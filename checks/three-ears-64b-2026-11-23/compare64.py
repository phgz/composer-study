"""Three ears on piece 64b's inner voices, the comparison (prepare64.py made the inputs; the Mac scored them):
  1. 64b's inner voices as chosen: each ear's pitch bits a note (NotaGen; AMT Large and Medium);
  2. the proposals: would each ear have chosen as we did? For each four bars, the rank of the proposal chosen among those drawn, by
     each ear's bits a note (1, the least surprising); its mean place from 0 (always the least surprising) to 1 (always the most),
     against chance (0.5), with a p from drawing each place at random; and how far the ears agree with one another (Spearman's rho
     between two ears over a segment's proposals, the median over segments);
  3. AMT's ear on the 29 held-out works beside ours and NotaGen's, on the same inner notes (checks/notagen-ear-2026-11-23).

Run: python3 -I compare64.py (beside notes64.json and the scores: notagen64_scores.jsonl, notagen64_finetune_scores.jsonl,
amt_large_scores.jsonl, amt_medium_scores.jsonl, those there); writes compare64.json"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EARS = {'NotaGen': 'notagen64_scores.jsonl', 'NotaGen fine-tuned': 'notagen64_finetune_scores.jsonl',
        'AMT Large': 'amt_large_scores.jsonl', 'AMT Medium': 'amt_medium_scores.jsonl',
        'AMT Large, two pianos': 'amt_large_two_pianos_scores.jsonl', 'AMT Medium, two pianos': 'amt_medium_two_pianos_scores.jsonl'}
                                                                                          # an ear without its scores is left out
meta = json.load(open(os.path.join(HERE, 'notes64.json')))
scores = {}
for ear, f in EARS.items():
    p = os.path.join(HERE, f)
    if os.path.exists(p): scores[ear] = {x['id']: x for x in map(json.loads, open(p))}
rnd = np.random.default_rng(0)


def ranks(x):
    x = np.asarray(x, float); r = np.empty(len(x)); r[np.argsort(x, kind='stable')] = np.arange(len(x))
    _, inv = np.unique(x, return_inverse=True); return (np.bincount(inv, r) / np.bincount(inv))[inv]


def rho(a, b):
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1]) if len(a) > 2 and np.std(a) > 0 and np.std(b) > 0 else None


def pitch_bits(ear, id_):
    return [b[0] for b in scores[ear][id_]['bits']]


res = dict(chosen={}, proposals={}, agreement={}, works={})

# 1 -------------------------------------------------------------------------------------------------------------------------------
for ear in scores:
    if ear.startswith('NotaGen'):
        a, t = pitch_bits(ear, '64b chosen alto'), pitch_bits(ear, '64b chosen tenor')
        res['chosen'][ear] = dict(alto=float(np.mean(a)), tenor=float(np.mean(t)), both=float(np.mean(a + t)), notes=len(a) + len(t))
    else:
        b = pitch_bits(ear, '64b chosen'); tags = [x[0] for x in meta['chosen']['amt']]
        res['chosen'][ear] = {v: float(np.mean([x for x, g in zip(b, tags) if g == v])) for v in ('alto', 'tenor')}
        res['chosen'][ear].update(both=float(np.mean(b)), notes=len(b),
                                  per_note_token=scores[ear]['64b chosen'].get('per_note_token'))

# 2 -------------------------------------------------------------------------------------------------------------------------------
segs = {}
for p in meta['proposals']: segs.setdefault((p['section'], p['voice'], p['segment']), []).append(p)
judges = ['ours'] + list(scores)
mean_bits = {}
for key, ps in segs.items():
    for p in ps:
        mean_bits[(p['id'], 'ours')] = p['ours']
        for ear in scores: mean_bits[(p['id'], ear)] = float(np.mean(pitch_bits(ear, p['id'])))
for j in judges:
    places, firsts, n_seg = [], 0, 0
    for key, ps in segs.items():
        if len(ps) < 2: continue
        x = [mean_bits[(p['id'], j)] for p in ps]; r = ranks(x); c = next(i for i, p in enumerate(ps) if p['chosen'])
        places.append(r[c] / (len(ps) - 1)); firsts += r[c] == 0; n_seg += 1
    sizes = [len(ps) for ps in segs.values() if len(ps) >= 2]
    sim = np.array([np.mean([rnd.integers(0, n) / (n - 1) for n in sizes]) for _ in range(20000)])
    m = float(np.mean(places))
    res['proposals'][j] = dict(segments=n_seg, mean_place=m, chosen_least_surprising=int(firsts),
                               chance_least_surprising=float(sum(1 / n for n in sizes)),
                               p=float((np.sum(np.abs(sim - .5) >= abs(m - .5)) + 1) / (len(sim) + 1)))
for i, a in enumerate(judges):
    for b in judges[i + 1:]:
        rs = [rho([mean_bits[(p['id'], a)] for p in ps], [mean_bits[(p['id'], b)] for p in ps]) for ps in segs.values()]
        rs = [x for x in rs if x is not None]
        res['agreement'][f'{a} / {b}'] = dict(median_rho=float(np.median(rs)), segments=len(rs))

# 3 -------------------------------------------------------------------------------------------------------------------------------
ear_dir = os.path.join(HERE, '..', 'notagen-ear-2026-11-23')
ours = json.load(open(os.path.join(ear_dir, 'ours.json')))['works']
ng = {x['id']: x for x in map(json.loads, open(os.path.join(ear_dir, 'scores.jsonl')))}
for ear in [e for e in scores if not e.startswith('NotaGen')]:
    per = []
    for w in meta['works']:
        o = ours[w['id']]; at = {(n['part'], n['i']): (n['ours'], b[0] + b[1]) for n, b in zip(o['notes'], ng[w['id']]['bits']) if n['inner']}
        trip = [(at[tuple(k)][0], at[tuple(k)][1], a) for k, a in zip(w['notes'], pitch_bits(ear, 'work ' + w['id']))]
        per.append((w['unit'].split(' | ')[0], np.mean([x[0] for x in trip]), np.mean([x[1] for x in trip]), np.mean([x[2] for x in trip]), len(trip)))
    d = np.array([a - o for _, o, _, a, _ in per])
    boots = [float(rnd.choice(d, len(d)).mean()) for _ in range(20000)]
    flips = np.abs((rnd.choice([-1, 1], (20000, len(d))) * d).mean(1))
    res['works'][ear] = dict(works=len(per), notes=int(sum(x[4] for x in per)), ours=float(np.mean([x[1] for x in per])),
                             notagen=float(np.mean([x[2] for x in per])), amt=float(np.mean([x[3] for x in per])),
                             amt_minus_ours=float(d.mean()), ci=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                             amt_lower=float((d < 0).mean()), p=float((np.sum(flips >= abs(d.mean())) + 1) / 20001),
                             units={u: dict(ours=float(np.mean([x[1] for x in per if x[0] == u])), notagen=float(np.mean([x[2] for x in per if x[0] == u])),
                                            amt=float(np.mean([x[3] for x in per if x[0] == u]))) for u in sorted({x[0] for x in per})})
json.dump(res, open(os.path.join(HERE, 'compare64.json'), 'w'), indent=1)

print('1. 64b inner voices as chosen, pitch bits a note:')
for ear, x in res['chosen'].items(): print(f"   {ear:11s} alto {x['alto']:.2f}  tenor {x['tenor']:.2f}  both {x['both']:.2f}  ({x['notes']} notes)")
print('2. would each ear have chosen as we did? place of the chosen proposal (0 least surprising, 0.5 chance, 1 most):')
for j, x in res['proposals'].items():
    print(f"   {j:11s} {x['mean_place']:.2f} over {x['segments']} segments, p {x['p']:.3f}; the chosen the least surprising in "
          f"{x['chosen_least_surprising']} (chance {x['chance_least_surprising']:.1f})")
print('   agreement between ears over a segment\'s proposals (median rho):', {k: round(v['median_rho'], 2) for k, v in res['agreement'].items()})
print('3. the 29 held-out works, inner lines, pitch bits a note (each work weighs one):')
for ear, x in res['works'].items():
    print(f"   {ear}: {x['amt']:.2f}, ours {x['ours']:.2f}, NotaGen {x['notagen']:.2f}; {ear} minus ours {x['amt_minus_ours']:+.2f} "
          f"[{x['ci'][0]:+.2f}, {x['ci'][1]:+.2f}], lower in {x['amt_lower']:.0%} of works, p {x['p']:.4f}")
    for u, y in x['units'].items(): print(f"      {u:26s} ours {y['ours']:.2f}  NotaGen {y['notagen']:.2f}  {ear} {y['amt']:.2f}")
