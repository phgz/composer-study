"""NotaGen's ear against ours, the comparison: for the same notes of the held-out works, NotaGen's bits (scores.jsonl, from
study/notagen_score.py) and ours (ours.json, from prepare.py). Lower is better. Each work weighs one in the tests: the notes of a work
are not independent (checks/vertical-weight-2026-11-23.md, signif.py), so the difference is a work's mean, tested by flipping each
work's sign (permutation) and by resampling works (bootstrap).

Run: python3 -I compare.py [scores.jsonl]  (beside ours.json and inputs.jsonl; writes compare.json)"""
import json, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ours = json.load(open(os.path.join(HERE, 'ours.json')))['works']
scores = {x['id']: x for x in map(json.loads, open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'scores.jsonl')))}
inputs = {x['id']: x for x in map(json.loads, open(os.path.join(HERE, 'inputs.jsonl')))}


def spelled(wid):
    """for each note, whether its pitch is written with an accidental (NotaGen pays for the spelling there)"""
    w = inputs[wid]; flats = [''.join(p.ljust(16, chr(0)) for p in ws) for ws in w['windows']]
    return [flats[wi][a] in '^_=' for wi, a, b in w['notes']]


def role(o, n):
    order = o['low_to_high']
    return 'inner' if n['inner'] else 'top' if n['part'] == order[-1] else 'bass' if n['part'] == order[0] else 'other'


rows = []                                                             # one a note
for wid, o in ours.items():
    if wid not in scores: continue
    s = scores[wid]['bits']; acc = spelled(wid)
    assert len(s) == len(o['notes']) == len(acc), wid
    for n, (chars, stop), a in zip(o['notes'], s, acc):
        rows.append(dict(work=wid, unit=o['unit'].split(' | ')[0], role=role(o, n), ours=n['ours'], ng=chars + stop, ng_chars=chars, acc=a))


def by_work(sel):
    """{work: (mean ours, mean NotaGen, notes)} over the notes `sel` keeps"""
    out = {}
    for r in rows:
        if sel(r): out.setdefault(r['work'], []).append((r['ours'], r['ng']))
    return {w: (float(np.mean([a for a, _ in v])), float(np.mean([b for _, b in v])), len(v)) for w, v in out.items()}


def test(bw, n=20000, seed=0):
    """NotaGen minus ours, a work's mean each: the mean over works, its 95% bootstrap interval, the share of works where NotaGen is
    lower, and the two-sided sign-flip p"""
    d = np.array([b - a for a, b, _ in bw.values()])
    if len(d) == 0: return None
    rnd = np.random.default_rng(seed)
    boots = [float(rnd.choice(d, len(d)).mean()) for _ in range(n)]
    flips = np.abs((rnd.choice([-1, 1], (n, len(d))) * d).mean(1))
    return dict(works=len(d), notes=sum(k for _, _, k in bw.values()), ours=float(np.mean([a for a, _, _ in bw.values()])),
                notagen=float(np.mean([b for _, b, _ in bw.values()])), diff=float(d.mean()),
                ci=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                notagen_lower=float((d < 0).mean()), p=float((np.sum(flips >= abs(d.mean())) + 1) / (n + 1)))


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b)); return float(np.corrcoef(ra, rb)[0, 1])


units = sorted({r['unit'] for r in rows})
res = dict(health={w: scores[w].get('per_char') for w in ours if w in scores}, tests={})
for name, sel in [('inner lines', lambda r: r['role'] == 'inner'), ('all lines', lambda r: True),
                  ('top line', lambda r: r['role'] == 'top'), ('bass line', lambda r: r['role'] == 'bass'),
                  ('inner, written without accidental', lambda r: r['role'] == 'inner' and not r['acc']),
                  ('inner, written with accidental', lambda r: r['role'] == 'inner' and r['acc'])]:
    res['tests'][name] = {'all units': test(by_work(sel))}
    for u in units: res['tests'][name][u] = test(by_work(lambda r, u=u: sel(r) and r['unit'] == u))
inner = [r for r in rows if r['role'] == 'inner']
res['agreement'] = dict(inner_notes_spearman=spearman([r['ours'] for r in inner], [r['ng'] for r in inner]),
                        per_work_median=float(np.median([spearman([r['ours'] for r in inner if r['work'] == w], [r['ng'] for r in inner if r['work'] == w])
                                                         for w in {r['work'] for r in inner}])))
json.dump(res, open(os.path.join(HERE, 'compare.json'), 'w'), indent=1, ensure_ascii=False)

print(f"{len(rows)} notes in {len({r['work'] for r in rows})} works; NotaGen's bits a character over the windows, "
      f"median {np.median([v for v in res['health'].values() if v is not None]):.3f}")
for name, t in res['tests'].items():
    print(f'\n{name}: pitch bits a note (each work weighs one); NotaGen minus ours, 95% interval, works where NotaGen is lower, p')
    for u, x in t.items():
        if x: print(f"  {u:28s} {x['works']:3d} works {x['notes']:6d} notes   ours {x['ours']:.2f}   NotaGen {x['notagen']:.2f}   "
                    f"{x['diff']:+.2f} [{x['ci'][0]:+.2f}, {x['ci'][1]:+.2f}]   {x['notagen_lower']:.0%}   p {x['p']:.4f}")
print(f"\ndo they hear the same notes as surprising? Spearman's rho, inner notes: {res['agreement']['inner_notes_spearman']:.2f} "
      f"(median within a work {res['agreement']['per_work_median']:.2f})")
