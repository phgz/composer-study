"""the vertical view's weight, retuned with the nested view (prior 200): pitch bits a note held out, all lines and inner lines, for
each weight; (1) the standing test, 12 units; (2) every unit with inner lines heard through Weber's levels"""
import sys, pickle, json, time
import numpy as np
sys.path.insert(0, '/home/claude/composer-study')
from study import continuations as C, lines as L
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
S = '/tmp/claude-0/-home-claude/669e17e8-ea5c-5071-9040-59c8c60ea523/scratchpad/'
small = pickle.load(open(S + 'cont/units.pickle', 'rb')); held = small['held']
ltm_all, v_all = C.load_all(S + 'cont/all-v25.npz')
weber = L.read(S + 'ready25', composers=['Carl Maria von Weber']); wunit = [w for w in weber if len(w.lines) >= 4]; W = (C.level(weber), C.level(wunit))
VW = (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)
out = {}
for test in ('standing', 'Weber'):
    tot = {(v, k): [] for v in VW for k in ('all', 'inner')}
    units = list(small['members']) if test == 'standing' else [u for u in small['members'] if u[2] != 'keyboard']
    for u in units:
        ws = small['members'][u]; test_ws = [w for w in ws if L.label_key(w) in held]
        if test == 'standing':
            lu, vu = C.level([w for w in ws if L.label_key(w) not in held]); lc, vc = C.level([w for w in small['composers'][u[0]] if L.label_key(w) not in held])
        else: (lc, vc), (lu, vu) = W
        lv = [('all', ltm_all, v_all), ('composer', lc, vc), ('unit', lu, vu)]
        res = {(v, k): [] for v in VW for k in ('all', 'inner')}
        for w in test_ws:
            ls = sorted((l[:150] for l in C.counted(w).values() if len(l) >= 8), key=len, reverse=True)[:4]
            if not ls: continue
            means = [sum(n[2] for n in l) / len(l) for l in ls]; order = sorted(range(len(ls)), key=lambda i: means[i]); inner = set(order[1:-1]) if len(ls) >= 3 else set()
            for i, l in enumerate(ls):
                if test == 'Weber' and i not in inner: continue
                others = [x for j, x in enumerate(ls) if j != i]
                for v in VW:
                    h = [bp for bp, _ in C.Model(lv, vweight=v, vertical=v > 0).hear(l, w.final, others)]
                    res[(v, 'all')] += h
                    if i in inner: res[(v, 'inner')] += h
        for k, x in res.items(): tot[k] += x
        log(test, u[0], u[1], ' | '.join(f"{v}: {np.mean(res[(v, 'all')]):.3f}" + (f" inner {np.mean(res[(v, 'inner')]):.3f}" if res[(v, 'inner')] else '') for v in VW))
    out[test] = {str(v): {k: (float(np.mean(tot[(v, k)])) if tot[(v, k)] else None, len(tot[(v, k)])) for k in ('all', 'inner')} for v in VW}
    for v in VW: log('ALL', test, v, out[test][str(v)])
json.dump(out, open(S + 'cont/phaseI.json', 'w'), indent=1)
log('done')
