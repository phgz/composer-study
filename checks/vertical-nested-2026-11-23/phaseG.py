"""the vertical view nested, held out: pitch bits a note (all lines at vweight 0.5; inner lines at 1.0), and on notes whose context
the unit has heard rarely (fewer than 10 notes of the bass's degree and top interval), for the geometric mean (now) and nested"""
import sys, pickle, json, time
import numpy as np
sys.path.insert(0, '/home/claude/composer-study')
from study import continuations as C, lines as L
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
S = '/tmp/claude-0/-home-claude/669e17e8-ea5c-5071-9040-59c8c60ea523/scratchpad/cont/'
small = pickle.load(open(S + 'units.pickle', 'rb')); held = small['held']
ltm_all, v_all = C.load_all(S + 'all-v25.npz')
CFG = [('mean', None)] + [('level', a) for a in (5, 20, 50, 200)] + [('order', a) for a in (5, 20, 50, 200)]
VW = {'all': 0.5, 'inner': 1.0}
tot = {(c, k): [] for c in CFG for k in ('all', 'inner', 'rare', 'rare inner')}; per = {}
for u, ws in small['members'].items():
    test_ws = [w for w in ws if L.label_key(w) in held]
    lu, vu = C.level([w for w in ws if L.label_key(w) not in held]); lc, vc = C.level([w for w in small['composers'][u[0]] if L.label_key(w) not in held])
    lv = [('all', ltm_all, v_all), ('composer', lc, vc), ('unit', lu, vu)]
    res = {(c, k): [] for c in CFG for k in ('all', 'inner', 'rare', 'rare inner')}
    for w in test_ws:
        ls = sorted((l[:150] for l in C.counted(w).values() if len(l) >= 8), key=len, reverse=True)[:4]
        if not ls: continue
        means = [sum(n[2] for n in l) / len(l) for l in ls]; order = sorted(range(len(ls)), key=lambda i: means[i]); inner = set(order[1:-1]) if len(ls) >= 3 else set()
        for i, l in enumerate(ls):
            others = [x for j, x in enumerate(ls) if j != i]
            spans = C.around(l, others)
            rare = []
            for sp in spans[2:]:
                c1, c2 = C.vctx(sp, w.final); rare.append(sp is not None and c2 is not None and vu.c2[c2].sum() < 10)
            for c in CFG:
                for kind, vw in VW.items():
                    if kind == 'inner' and i not in inner: continue
                    m = C.Model(lv, vweight=vw, vmode=c[0], valpha=c[1])
                    h = [bp for bp, _ in m.hear(l, w.final, others)]
                    res[(c, kind)] += h
                    res[(c, 'rare' if kind == 'all' else 'rare inner')] += [x for x, r in zip(h, rare) if r]
    for k, v in res.items(): tot[k] += v
    per[u] = {f'{c[0]} {c[1]}': {k: (float(np.mean(res[(c, k)])) if res[(c, k)] else None, len(res[(c, k)])) for k in ('all', 'inner', 'rare', 'rare inner')} for c in CFG}
    log(u[0], u[1], ' | '.join(f"{c[0]} {c[1]}: {np.mean(res[(c, 'all')]):.3f}" for c in CFG),
        '|| rare', len(res[(CFG[0], 'rare')]), ' '.join(f"{np.mean(res[(c, 'rare')]):.2f}" for c in CFG if res[(c, 'rare')]))
summary = {f'{c[0]} {c[1]}': {k: (float(np.mean(tot[(c, k)])) if tot[(c, k)] else None, len(tot[(c, k)])) for k in ('all', 'inner', 'rare', 'rare inner')} for c in CFG}
for k, v in summary.items(): log('ALL', k, v)
json.dump(dict(summary=summary, units={' | '.join(map(str, u)): r for u, r in per.items()}), open(S + 'phaseG.json', 'w'), indent=1, ensure_ascii=False)
log('done')
