"""The critic on drafts: where a draft goes flat, before Philip listens.

The ear (study/ear.py, trained on the whole catalogue and saved by `--build`) hears each line of the draft with its short-term
memory, and a note is flat where the mean surprise of the 8 notes around it stays under what 95 in 100 such spans of real music
stay above: the threshold is measured on the catalogue's held-out works when the ear is built, and saved with it. Then:
  - the whole texture flat: the seconds where every line that sounds is flat, or nothing sounds, for 8 seconds or more;
  - a line flat for 30 seconds or more ("a layer whose surprise flatlines for 30 seconds is visible before you hear it");
  - each line's bits a note and the share of its time in a flat run.
A flat stretch is a fact about the notes, not a verdict: an ostinato, a drone, a stillness may be what the piece wants. Piece 44's
measure on the whole texture went against Philip's ratings on the pieces of the first pool, and not on those since (study/rated.py):
the critic shows where to look, it does not score the piece.

Usage:
  python3 -I study/critic.py --build <ready-read copy> --ear ear.npz [--works works.pickle]     train, measure the threshold, save
  PYTHONPATH=<renderer>:<renderer>/tools:<renderer>/adapters python3 study/critic.py --ear ear.npz <score.py | x.render.json> ..."""
import argparse, collections, os, pickle, random, sys, time
import numpy as np
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from study import ear as E, eras as R, lines as L, heldout as H, pieces as P

WINDOW, QUANTILE, TEXTURE, LONG = 8, 5, 8, 30


def rolling(x, w=WINDOW):
    """the mean of the w values around each (w//2 - 1 before, w//2 after; fewer at the ends)"""
    x = np.asarray(x, float); c = np.concatenate([[0.0], np.cumsum(x)]); n = len(x); i = np.arange(n)
    lo = np.maximum(0, i - (w // 2 - 1)); hi = np.minimum(n, i + w // 2 + 1)
    return (c[hi] - c[lo]) / (hi - lo)


def line_surprise(line, final, ltm):
    """(onsets of notes 1..n-1, their pitch IC)"""
    out = E.listen(line, final, ltm)
    return np.array([n[0] for n in line[1:]]), np.array([x[0] for x in out[1:]])


def build(ready, path, works=None, per_era=120, seed=24, log=print):
    works = works or L.read(ready); eras = R.table(); era = lambda w: (eras.get(w.composer) or {}).get('era', 'no period')
    train, held = H.split(works, seed); wt = H.weights(train, None)
    ltm = E.Long().learn(train, lambda w: wt[w.id]); log('the ear for the threshold, learnt on nine tenths')
    rnd = random.Random(seed + 1); by = collections.defaultdict(list)
    for w in held: by[era(w)].append(w)
    spans = collections.defaultdict(list)
    for e, ws in sorted(by.items()):
        for w in rnd.sample(ws, min(per_era, len(ws))):
            for line in sorted(w.lines.values(), key=len, reverse=True)[:4]:
                _, ic = line_surprise(line[:300], w.final, ltm)
                if len(ic) >= WINDOW: spans[e] += list(rolling(ic))
    allspans = [x for v in spans.values() for x in v]
    ref = dict(threshold=float(np.percentile(allspans, QUANTILE)), window=WINDOW, quantile=QUANTILE, spans=len(allspans),
               by_period={e: round(float(np.percentile(v, QUANTILE)), 3) for e, v in spans.items()})
    log(f'flat: under {ref["threshold"]:.2f} bits for {WINDOW} notes ({QUANTILE}% of {len(allspans)} spans of held-out music)')
    del ltm
    wt = H.weights(works, None); ltm = E.Long().learn(works, lambda w: wt[w.id]); log('the ear, learnt on every work')
    ltm.save(path, about=dict(L.record(ready), flat=ref)); log(f'saved: {path}')
    return ltm


def runs(mask, onsets, ends):
    """the [start, end] of each run of True"""
    out = []; i = 0; n = len(mask)
    while i < n:
        if not mask[i]: i += 1; continue
        j = i
        while j + 1 < n and mask[j + 1]: j += 1
        out.append((float(onsets[i]), float(ends[j]))); i = j + 1
    return out


def mmss(t): return f'{int(t // 60)}:{int(t % 60):02d}'


def judge(parts, ltm, threshold):
    """what the critic finds in a draft: {'lines': {part: dict(notes, bits, flat_share, long_runs)}, 'texture': [(start, end)], 'end'}"""
    lines = P.lines_of(parts)
    if not lines: return None
    final = P.final_of(lines); end = max(n[0] + n[1] for l in lines.values() for n in l)
    found = {}; flat_runs = {}
    for name, line in lines.items():
        on, ic = line_surprise(line, final, ltm)
        flat = rolling(ic) < threshold
        ends = np.array([n[0] + n[1] for n in line[1:]])
        rs = runs(flat, on, ends); flat_runs[name] = rs
        span = max(line[-1][0] + line[-1][1] - line[0][0], 1e-9)
        found[name] = dict(notes=len(line), bits=float(ic.mean()), flat_share=sum(b - a for a, b in rs) / span,
                           long_runs=[(a, b) for a, b in rs if b - a >= LONG])
    secs = np.arange(0, int(end) + 1); quiet = []
    for s in secs:                                                         # every line that sounds is flat there, or none sounds
        ok = True
        for name, line in lines.items():
            if any(s - 2 <= n[0] < s + 2 for n in line) and not any(a - 1e-9 <= s <= b for a, b in flat_runs[name]): ok = False; break
        quiet.append(ok)
    tex = [(a, b + 1) for a, b in runs(np.array(quiet), secs, secs) if b + 1 - a >= TEXTURE]
    return dict(lines=found, texture=tex, end=end)


def report(name, r, threshold):
    print(f'\n{name}: {mmss(r["end"])}, {len(r["lines"])} lines; flat = the 8 notes around a note under {threshold:.2f} bits a note')
    print('  the whole texture flat for 8 s or more: ' + (', '.join(f'{mmss(a)}-{mmss(b)} ({b - a:.0f} s)' for a, b in r['texture']) or 'none'))
    long = [(p, a, b) for p, d in r['lines'].items() for a, b in d['long_runs']]
    print(f'  a line flat for {LONG} s or more: ' + ('none' if not long else ''))
    for p, a, b in sorted(long, key=lambda x: x[1]): print(f'    {p:12s} {mmss(a)}-{mmss(b)} ({b - a:.0f} s)')
    for p, d in r['lines'].items(): print(f'  {p:12s} {d["notes"]:5d} notes  {d["bits"]:.2f} bits a note  flat {d["flat_share"]:4.0%} of its time')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ear', required=True); ap.add_argument('--build'); ap.add_argument('--works')
    ap.add_argument('pieces', nargs='*'); a = ap.parse_args()
    t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
    if a.build: build(a.build, a.ear, pickle.load(open(a.works, 'rb')) if a.works else None, log=log)
    if not a.pieces: return
    ltm = E.Long.load(a.ear); thr = ltm.about['flat']['threshold']
    print('the ear:', {k: v for k, v in ltm.about.items() if k != 'flat'})
    for p in a.pieces:
        try: r = judge(P.read(p), ltm, thr)
        except Exception as e: print(f'\n{p}: could not be read: {type(e).__name__}: {str(e)[:120]}'); continue
        if r is None: print(f'\n{p}: no pitched line'); continue
        report(os.path.relpath(p), r, thr)


if __name__ == '__main__': main()
