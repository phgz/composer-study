"""The glitch test, the comparison: how well each outside ear, and the four together, find the wrong notes planted by
prepare_glitch.py, among every note of the same copy.

  a note's bits     NotaGen: its pitch's characters and the end of the pitch (as before); a chord, its top note, is left out.
                    AMT: its pitch, given its onset and length, on any instrument (as before)
  together          the notes all four ears score (NotaGen's single notes, matched to AMT's by part, onset and pitch); each ear's
                    bits put on one scale within the copy (minus its mean, over its standard deviation), then averaged
  a planted note's place
                    the share of the copy's other notes at least as surprising to that ear (0: the most surprising of all)
  found at 2%       its place under 0.02: among the 2% of the copy's notes a reader would be shown first. Also 1% and 5%
  the rise          its bits in the copy, minus the bits of the note it replaced, in the copy as written
  intervals         95%, resampling works (each work's planted notes together); 64b is reported by itself, as the music the tool
                    is for (its three sets of sixteen, each in copies of its own; the interval from resampling notes, the sets being
                    one piece)

Also: the 25 notes of 64b as written that the four together find most surprising, for Claude to look at in the score.

Run: python3 compare_glitch.py     (reads glitch.json and the four score files beside it; writes compare_glitch.json)"""
import json, os, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EARS = [('NotaGen-X', 'glitch_notagen_x.jsonl', 'ng'), ('NotaGen fine-tuned', 'glitch_notagen_finetune.jsonl', 'ng'),
        ('AMT Large', 'glitch_amt_large.jsonl', 'amt'), ('AMT Medium', 'glitch_amt_medium.jsonl', 'amt')]
KINDS = {'semitone': 1, 'tone': 2}
BUDGETS = (0.01, 0.02, 0.05)
NAMES = 'C C# D Eb E F F# G G# A Bb B'.split()


def load(path):
    out = {}
    for line in open(path):
        x = json.loads(line); out[x['id']] = x['bits']
    return out


def keyed(scores, kind_of_ear, which, id_):
    """{note key: bits} for the notes this ear scores in one copy"""
    bits = scores[id_]; out = {}
    if kind_of_ear == 'ng':
        for (v, i, chord, key), b in zip(which['notagen'], bits):
            if chord or key is None: continue
            out.setdefault(tuple(key), b[0] + b[1])
    else:
        for key, b in zip(which['amt'], bits): out.setdefault(tuple(key), b[0])
    return out


def place(d, key, planted):
    """the share of the copy's other (unplanted) notes at least as surprising as `key`"""
    others = np.array([b for k, b in d.items() if k not in planted])
    return float(np.mean(others >= d[key]))


def together(ds):
    common = set.intersection(*(set(d) for d in ds))
    zs = []
    for d in ds:
        x = np.array([d[k] for k in common]); m, s = x.mean(), x.std() or 1.0
        zs.append({k: (d[k] - m) / s for k in common})
    return {k: float(np.mean([z[k] for z in zs])) for k in common}


def planted_keys(info, kind, is64):
    step = KINDS.get(kind, 0)
    if is64: return [((p['voice'], p['beat'], p['midi'] + p['sign'] * step), (p['voice'], p['beat'], p['midi'])) for p in info['planted']]
    return [((p['part'], p['onset'], p['midi'] + p['sign'] * step), (p['part'], p['onset'], p['midi'])) for p in info['planted']]


def main():
    meta = json.load(open(os.path.join(HERE, 'glitch.json')))
    have = [(n, f, k) for n, f, k in EARS if os.path.exists(os.path.join(HERE, f))]
    scores = {n: load(os.path.join(HERE, f)) for n, f, _ in have}
    m64 = meta['piece64']
    pieces = [(w, info, False) for w, info in meta['works'].items()] + \
             [(f'64b set {k}', dict(planted=x['planted'], copies={**x['copies'], 'as written': m64['as_written']}), True)
              for k, x in m64['sets'].items()]
    rows = []                                                              # (piece, kind, ear, place, rise)
    for name, info, is64 in pieces:
        for kind in KINDS:
            id_, id0 = f'{name} | {kind}', ('64b' if is64 else name) + ' | as written'
            ds = {n: keyed(scores[n], k, info['copies'][kind], id_) for n, _, k in have}
            d0 = {n: keyed(scores[n], k, info['copies']['as written'], id0) for n, _, k in have}
            if len(have) == len(EARS):
                ds['together'] = together([ds[n] for n, _, _ in have]); d0['together'] = together([d0[n] for n, _, _ in have])
            pk = planted_keys(info, kind, is64); planted = {a for a, _ in pk}
            for ear, d in ds.items():
                for new, old in pk:
                    if new not in d: continue
                    rows.append(dict(piece=name, kind=kind, ear=ear, place=place(d, new, planted),
                                     rise=d[new] - d0[ear][old] if old in d0[ear] else None))
    out = dict(ears=[n for n, _, _ in have] + (['together'] if len(have) == len(EARS) else []), results={})
    rnd = np.random.default_rng(0)
    for ear in out['ears']:
        for kind in KINDS:
            for where in ('works', '64b'):
                rs = [r for r in rows if r['ear'] == ear and r['kind'] == kind and (r['piece'].startswith('64b') == (where == '64b'))]
                if not rs: continue
                res = dict(n=len(rs), median_place=round(float(np.median([r['place'] for r in rs])), 4),
                           median_rise=round(float(np.median([r['rise'] for r in rs if r['rise'] is not None])), 2))
                for b in BUDGETS:
                    res[f'found at {b:.0%}'] = round(float(np.mean([r['place'] < b for r in rs])), 3)
                if True:                                                   # 95% interval: resampling works (64b: its notes)
                    by = {}
                    for r in rs: by.setdefault(r['piece'] if where == 'works' else len(by), []).append(r['place'] < 0.02)
                    ws = list(by); boots = []
                    for _ in range(2000):
                        pick = rnd.choice(len(ws), len(ws)); hits = [h for i in pick for h in by[ws[i]]]
                        boots.append(np.mean(hits))
                    res['found at 2%, 95% interval'] = [round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)]
                out['results'][f'{ear} | {kind} | {where}'] = res
    if len(have) == len(EARS):                                             # 64b as written: what the four together hear most
        id0 = '64b | as written'
        ds = {n: keyed(scores[n], k, m64['as_written'], id0) for n, _, k in have}
        t = together([ds[n] for n, _, _ in have])
        top = sorted(t, key=lambda k: -t[k])[:25]
        out['64b, most surprising as written'] = [dict(voice=k[0], bar=int(k[1] // 3) + 1, beat=round(k[1] % 3 + 1, 2),
                                                       pitch=NAMES[k[2] % 12] + str(k[2] // 12 - 1), together=round(t[k], 2),
                                                       **{n: round(ds[n][k], 2) for n, _, _ in have}) for k in top]
        out['64b, notes heard by all four'] = len(t)
    json.dump(out, open(os.path.join(HERE, 'compare_glitch.json'), 'w'), indent=1, ensure_ascii=False)
    for k, v in out['results'].items(): print(k, v)
    for x in out.get('64b, most surprising as written', []): print(x)


if __name__ == '__main__':
    main()
