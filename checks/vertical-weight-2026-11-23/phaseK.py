"""per-work bits for the configurations compared today, so that differences can be tested with the work as the unit (notes of one
work are not independent): sums and counts of pitch bits, all lines and inner lines, for each held-out work, in three tests"""
import sys, pickle, json, time, random
import numpy as np
sys.path.insert(0, '/home/claude/composer-study')
from study import continuations as C, lines as L
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
S = '/tmp/claude-0/-home-claude/669e17e8-ea5c-5071-9040-59c8c60ea523/scratchpad/'
small = pickle.load(open(S + 'cont/units.pickle', 'rb')); held = small['held']
ltm_all, v_all = C.load_all(S + 'cont/all-v25.npz')
weber = L.read(S + 'ready25', composers=['Carl Maria von Weber']); wunit = [w for w in weber if len(w.lines) >= 4]; W = (C.level(weber), C.level(wunit))
CFG = {'geo 0.5': ('mean', None, 0.5), 'geo 1': ('mean', None, 1.0), 'nest 0.5': ('level', 200, 0.5), 'nest 0.75': ('level', 200, 0.75), 'nest 1': ('level', 200, 1.0)}
rows = []
for test in ('standing', 'small', 'Weber'):
    units = list(small['members']) if test == 'standing' else [u for u in small['members'] if u[2] != 'keyboard']
    for u in units:
        ws = small['members'][u]; test_ws = [w for w in ws if L.label_key(w) in held]
        if test == 'standing':
            lu, vu = C.level([w for w in ws if L.label_key(w) not in held]); lc, vc = C.level([w for w in small['composers'][u[0]] if L.label_key(w) not in held])
        elif test == 'small':
            train = sorted((w for w in ws if L.label_key(w) not in held), key=lambda w: w.id); random.Random(7).shuffle(train); (lc, vc) = (lu, vu) = C.level(train[:4])
        else: (lc, vc), (lu, vu) = W
        lv = [('all', ltm_all, v_all), ('composer', lc, vc), ('unit', lu, vu)]
        for w in test_ws:
            ls = sorted((l[:150] for l in C.counted(w).values() if len(l) >= 8), key=len, reverse=True)[:4]
            if not ls: continue
            means = [sum(n[2] for n in l) / len(l) for l in ls]; order = sorted(range(len(ls)), key=lambda i: means[i]); inner = set(order[1:-1]) if len(ls) >= 3 else set()
            row = dict(test=test, unit=' | '.join(u), work=w.id, label=L.label_key(w) if isinstance(L.label_key(w), str) else str(L.label_key(w)))
            for name, (mode, a, vw) in CFG.items():
                m = C.Model(lv, vweight=vw, vmode=mode, valpha=a); sa = na = si = ni = 0.0
                for i, l in enumerate(ls):
                    if test == 'Weber' and i not in inner: continue
                    h = [bp for bp, _ in m.hear(l, w.final, [x for j, x in enumerate(ls) if j != i])]
                    sa += sum(h); na += len(h)
                    if i in inner: si += sum(h); ni += len(h)
                row[name] = [sa, na, si, ni]
            rows.append(row)
        log(test, u[0], u[1], len(test_ws), 'works')
json.dump(rows, open(S + 'cont/phaseK.json', 'w'))
log('done')
