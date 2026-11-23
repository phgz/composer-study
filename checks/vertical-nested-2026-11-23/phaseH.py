"""the vertical view nested, where the unit's evidence is thin: (small) each unit and its composer learnt from 4 of the unit's works
only; (Weber) the held-out works of every unit with inner lines heard through Weber's levels (his works, his works for four voices
or more), as piece 64b's inner voices were drawn. Pitch bits a note: all lines (vertical weight 0.5), inner lines (1.0), and the
notes whose context the specific level has heard fewer than 10 times"""
import sys, pickle, json, time, random
import numpy as np
sys.path.insert(0, '/home/claude/composer-study')
from study import continuations as C, lines as L
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
S = '/tmp/claude-0/-home-claude/669e17e8-ea5c-5071-9040-59c8c60ea523/scratchpad/'
small = pickle.load(open(S + 'cont/units.pickle', 'rb')); held = small['held']
ltm_all, v_all = C.load_all(S + 'cont/all-v25.npz')
weber = L.read(S + 'ready25', composers=['Carl Maria von Weber']); wunit = [w for w in weber if len(w.lines) >= 4]
W = (C.level(weber), C.level(wunit))
CFG = [('mean', None), ('level', 20), ('level', 50), ('level', 200)]
VOICES = [u for u in small['members'] if u[2] != 'keyboard']
out = {}
for test in ('small', 'Weber'):
    tot = {(c, k): [] for c in CFG for k in ('all', 'inner', 'rare', 'rare inner')}
    for u in VOICES:
        ws = small['members'][u]; test_ws = [w for w in ws if L.label_key(w) in held]
        if test == 'small':
            train = sorted((w for w in ws if L.label_key(w) not in held), key=lambda w: w.id); random.Random(7).shuffle(train)
            (lc, vc) = (lu, vu) = C.level(train[:4])
        else: (lc, vc), (lu, vu) = W
        lv = [('all', ltm_all, v_all), ('composer', lc, vc), ('unit', lu, vu)]
        res = {(c, k): [] for c in CFG for k in ('all', 'inner', 'rare', 'rare inner')}
        for w in test_ws:
            ls = sorted((l[:150] for l in C.counted(w).values() if len(l) >= 8), key=len, reverse=True)[:4]
            if not ls: continue
            means = [sum(n[2] for n in l) / len(l) for l in ls]; order = sorted(range(len(ls)), key=lambda i: means[i]); inner = set(order[1:-1]) if len(ls) >= 3 else set()
            for i, l in enumerate(ls):
                others = [x for j, x in enumerate(ls) if j != i]; spans = C.around(l, others)
                rare = [sp is not None and C.vctx(sp, w.final)[1] is not None and vu.c2[C.vctx(sp, w.final)[1]].sum() < 10 for sp in spans[2:]]
                for c in CFG:
                    for kind, vw in (('all', .5), ('inner', 1.0)):
                        if kind == 'inner' and i not in inner: continue
                        h = [bp for bp, _ in C.Model(lv, vweight=vw, vmode=c[0], valpha=c[1]).hear(l, w.final, others)]
                        res[(c, kind)] += h; res[(c, 'rare' if kind == 'all' else 'rare inner')] += [x for x, r in zip(h, rare) if r]
        for k, v in res.items(): tot[k] += v
        log(test, u[0], u[1], ' | '.join(f"{c[0]} {c[1]}: {np.mean(res[(c, 'all')]):.3f}" + (f" inner {np.mean(res[(c, 'inner')]):.3f}" if res[(c, 'inner')] else '') for c in CFG),
            '|| rare', len(res[(CFG[0], 'rare')]), ' '.join(f"{np.mean(res[(c, 'rare')]):.2f}" for c in CFG if res[(c, 'rare')]))
    out[test] = {f'{c[0]} {c[1]}': {k: (float(np.mean(tot[(c, k)])) if tot[(c, k)] else None, len(tot[(c, k)])) for k in ('all', 'inner', 'rare', 'rare inner')} for c in CFG}
    for k, v in out[test].items(): log('ALL', test, k, v)
json.dump(out, open(S + 'cont/phaseH.json', 'w'), indent=1)
log('done')
