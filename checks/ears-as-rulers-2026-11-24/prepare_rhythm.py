"""The rhythm test, the inputs: stumbles planted in the 27 works of the glitch test and in piece 64b, for AMT to hear every note of
each (study/amt_score.py, which now keeps each note's onset bits: how unexpected the moment it begins, among the onset tokens).
Philip, on the glitches he has heard in the pieces: "mostly a wrong-sounding note or a stumble in the rhythm". The glitch test
covered the first; this, the second.

  two kinds of stumble, each in a copy of its own
    a note off   one note begun a sixteenth early or late (at random), its end where it was; every other note the work's
    a skip       a sixteenth of time taken out at one onset: every note from there on a sixteenth earlier, a note sounding across
                 it a sixteenth shorter; the first onset after it comes a sixteenth early
  where          picked at random (seeded by the work's id) among notes at least an eighth long, from the third bar to the third
                 last, at least four bars apart (64b: six); as many as the glitch test planted wrong notes (two to eight a work;
                 64b: sixteen, three sets, each in copies of its own)
  the sixteenth  a quarter of a beat: in the works, at a quarter note of 90 a minute (1/6 second); in 64b, a quarter of the beat at
                 that moment in its own tempo map
  AMT            every note, no given notes, on the piano, as in the glitch test

Writes beside this script: rhythm_amt_inputs.jsonl, rhythm.json (for each copy, each note's index in the work's own list, in
AMT's order; the planted notes). Ids: "<work> | as written", "<work> | a note off", "<work> | a skip"; "64b | as written",
"64b set <k> | a note off", ...

Run: python3 -I prepare_rhythm.py <score-reader checkout> <anticipation checkout> <composer-blend> <renderer-engine>"""
import json, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'checks', 'three-ears-64b-2026-11-23'))
import rulers as R
from study import amt as A

SR, ACO, BLEND, RENDERER = sys.argv[1:5]
CACHE = '/root/.cache/score-reader'
KINDS = ('a note off', 'a skip')
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
inputs, meta = [], dict(works={}, piece64={})


def record(notes, id_):
    """AMT's input for the notes [(t, d, midi, index)], and the indices in AMT's order (onset, then pitch)"""
    order = sorted(range(len(notes)), key=lambda i: (notes[i][0], notes[i][2]))
    seq, where = A.sequence([n[:3] for n in notes], [], ACO)
    ws, pos = A.windows(seq, where, ACO, alone=True)
    inputs.append(dict(id=id_, windows=ws, notes=pos))
    return [notes[i][3] for i in order]


def pick(cands, k, spacing, rnd):
    cands = list(cands); rnd.shuffle(cands); out = []
    for c in cands:
        if len(out) == k: break
        if all(abs(c[1] - o[1]) >= spacing for o in out): out.append(c)
    return sorted(out, key=lambda c: c[1])


def off(notes, picks, signs, six):
    """a note off: each pick (index, bar) begun a sixteenth early or late, its end kept"""
    out = [list(n) for n in notes]
    for (i, _), sg in zip(picks, signs):
        t, d = out[i][0], out[i][1]; s = six(t)
        out[i][0], out[i][1] = (t + s, d - s) if sg > 0 else (t - s, d + s)
    return [tuple(n) for n in out], [i for i, _ in picks]


def skip(notes, picks, six):
    """a skip: a sixteenth taken out at each pick's onset; the stumble is the lowest note of the first onset there"""
    out = [list(n) for n in notes]; firsts = []
    for i, _ in sorted(picks, key=lambda p: -notes[p[0]][0]):               # the latest first, so the earlier ones see the
        t0_ = notes[i][0]; s = six(t0_)                                       # piece's own times
        for n in out:
            if n[0] >= t0_ - 1e-6: n[0] -= s
            elif n[0] + n[1] > t0_ + 1e-6: n[1] = max(t0_ - n[0], n[1] - s)
    for i, _ in picks:
        t0_ = notes[i][0]; at = [j for j, n in enumerate(notes) if abs(n[0] - t0_) < 1e-6]
        firsts.append(min(at, key=lambda j: notes[j][2]))
    return [tuple(n) for n in out], firsts


def plant(notes, k, spacing, seed, six, bar_of):
    """the candidates (index, bar): notes at least an eighth long from the third bar to the third last"""
    last = max(bar_of(n[0]) for n in notes)
    cands = [(i, bar_of(n[0])) for i, n in enumerate(notes) if n[1] >= 2 * six(n[0]) - 1e-6 and 2 <= bar_of(n[0]) < last - 2]
    rnd = random.Random(seed); picks = pick(cands, k, spacing, rnd); signs = [rnd.choice((-1, 1)) for _ in picks]
    return picks, signs


# 1. the works --------------------------------------------------------------------------------------------------------------------
g = json.load(open(os.path.join(HERE, 'glitch.json')))
for wid, info in g['works'].items():
    s = R.stream_of(wid, CACHE, SR)
    notes = [(t, d, m, i) for i, (t, d, m, key) in enumerate(R.amt_notes(s))]
    bar_q = float(s.parts[0].getElementsByClass('Measure')[1].barDuration.quarterLength)
    six = lambda t: R.QUARTER_S / 4; bar_of = lambda t, b=bar_q: int(t / R.QUARTER_S // b)
    picks, signs = plant(notes, len(info['planted']), 4, f'{wid} rhythm', six, bar_of)
    m = dict(planted=[dict(note=i, bar=b + 1, sign=sg) for (i, b), sg in zip(picks, signs)], copies={})
    m['copies']['as written'] = record(notes, f'{wid} | as written')
    ns, which = off(notes, picks, signs, six); m['copies']['a note off'] = record(ns, f'{wid} | a note off'); m['a note off'] = which
    ns, which = skip(notes, picks, six); m['copies']['a skip'] = record(ns, f'{wid} | a skip'); m['a skip'] = which
    meta['works'][wid] = m
    log(wid, len(picks), 'planted,', len(notes), 'notes')

# 2. piece 64b ----------------------------------------------------------------------------------------------------------------------
import piece64 as P
v = P.voices(BLEND, RENDERER); sec = v['sec']
xb = None
notes = [(t, dd, m, i) for i, (name, b, db, m, t, dd) in enumerate(v['notes'])]
beat_at = {i: b for i, (name, b, db, m, t, dd) in enumerate(v['notes'])}
by_t = sorted((t, beat_at[i]) for t, dd, m, i in notes)
import numpy as np
tt = np.array([x for x, _ in by_t]); bb = np.array([y for _, y in by_t])
beat = lambda t: float(np.interp(t, tt, bb))
six = lambda t: sec(beat(t) + .25) - sec(beat(t)); bar_of = lambda t: int(beat(t) // P.METRE)
meta['piece64']['as written'] = record(notes, '64b | as written')
for k in range(1, 4):
    picks, signs = plant(notes, 16, 6, f'64b rhythm set {k}', six, bar_of)
    m = dict(planted=[dict(note=i, bar=b + 1, sign=sg) for (i, b), sg in zip(picks, signs)], copies={})
    ns, which = off(notes, picks, signs, six); m['copies']['a note off'] = record(ns, f'64b set {k} | a note off'); m['a note off'] = which
    ns, which = skip(notes, picks, six); m['copies']['a skip'] = record(ns, f'64b set {k} | a skip'); m['a skip'] = which
    meta['piece64'][str(k)] = m
    log(f'64b set {k}:', [b + 1 for _, b in picks])

with open(os.path.join(HERE, 'rhythm_amt_inputs.jsonl'), 'w') as f:
    for x in inputs: f.write(json.dumps(x) + '\n')
json.dump(meta, open(os.path.join(HERE, 'rhythm.json'), 'w'))
log('done:', len(inputs), 'AMT inputs')
