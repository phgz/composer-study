"""The four tenor segments of piece 64b where the outside ears most prefer the proposal chosen over another: for each segment, each
ear's bits a note for each proposal, as z-scores within the segment, averaged over four ears (NotaGen-X, NotaGen's fine-tuned
checkpoint, AMT Large and Medium with the given notes on a second piano); the least liked proposal is the one with the highest
mean, the gap its mean less the chosen one's. Tenor segments only: their proposals were drawn, and scored, with the alto chosen for
the same bars, so that one sounds the same either way. One segment a section where it can, none next to another.
Writes worst64.json (for worst64.py). Run: python3 -I worst64_pick.py"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EARS = {'NotaGen-X': 'notagen64_scores.jsonl', 'NotaGen fine-tuned': 'notagen64_finetune_scores.jsonl',
        'AMT Large, two pianos': 'amt_large_two_pianos_scores.jsonl', 'AMT Medium, two pianos': 'amt_medium_two_pianos_scores.jsonl'}
meta = json.load(open(os.path.join(HERE, 'notes64.json')))
sc = {e: {x['id']: float(np.mean([b[0] for b in x['bits']])) for x in map(json.loads, open(os.path.join(HERE, f)))} for e, f in EARS.items()}
segs = {}
for p in meta['proposals']:
    if p['voice'] == 'tenor': segs.setdefault((p['section'], p['segment']), []).append(p)
choices = json.load(open(os.path.join(HERE, '..', '..', '..', 'composer-blend', 'pieces', '64b_inside_the_mazurka', 'choices64.json')))['voices']['tenor']
bars = {(s['section'], s['segment']): s['bars'] for s in choices}
rows = []
for key, ps in segs.items():
    if len(ps) < 3: continue
    z = np.mean([(lambda x: (x - x.mean()) / (x.std() + 1e-9))(np.array([sc[e][p['id']] for p in ps])) for e in EARS], 0)
    c = next(i for i, p in enumerate(ps) if p['chosen']); w = max((i for i in range(len(ps)) if i != c), key=lambda i: z[i])
    rows.append(dict(section=key[0], segment=key[1], bars=bars[key], chosen=ps[c]['k'], worst=ps[w]['k'], gap=round(float(z[w] - z[c]), 2),
                     bits={e: [round(sc[e][ps[c]['id']], 2), round(sc[e][ps[w]['id']], 2)] for e in EARS}, ours=[ps[c]['ours'], ps[w]['ours']]))
picked = []
for r in sorted(rows, key=lambda r: -r['gap']):
    if any(r['section'] == q['section'] for q in picked) or any(abs(r['bars'][0] - q['bars'][1]) <= 1 or abs(q['bars'][0] - r['bars'][1]) <= 1 for q in picked): continue
    picked.append(r)
    if len(picked) == 4: break
picked.sort(key=lambda r: r['bars'][0])
json.dump(picked, open(os.path.join(HERE, 'worst64.json'), 'w'), indent=1)
for r in picked: print(r)
