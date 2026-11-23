"""the sampling weight of the vertical view, retuned with the nested view: inner voices drawn under the real outer voices of held-out
passages (twelve quarters after four real notes, 25 passages a unit, 6 samples each), against the real passages: bits a note (scored
as proposals are, SCORE), consonance with the other voices, notes, and the share falling in the real passages' 25-75% band"""
import sys, pickle, json, time, random, collections
import numpy as np
sys.path.insert(0, '/home/claude/composer-study')
from study import continuations as C, lines as L
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
S = '/tmp/claude-0/-home-claude/669e17e8-ea5c-5071-9040-59c8c60ea523/scratchpad/'
small = pickle.load(open(S + 'cont/units.pickle', 'rb')); held = small['held']
ltm_all, v_all = C.load_all(S + 'cont/all-v25.npz')
SCORE_VW = float(sys.argv[1]) if len(sys.argv) > 1 else C.SCORE['vweight']
SW = (1.0, 1.5, 2.0, 3.0, 4.0)
CONS = {0, 3, 4, 7, 8, 9}
def cons(line, others):
    sp = C.around(line, others); c = [all(((n[2] - x) % 12) in CONS for x in s_) for n, s_ in zip(line, sp) if s_]
    return float(np.mean(c)) if c else np.nan
units = [('Johann Sebastian Bach', 'chorale', 'voices', 'Leipzig'), ('Giovanni Pierluigi da Palestrina', 'motet', 'voices', 'all'),
         ('Wolfgang Amadeus Mozart', 'string quartet', 'string quartet', 'Vienna'), ('Johannes Brahms', 'song', 'voice and keyboard', 'middle')]
out = {}
for u in units:
    if u not in small['members']: log('missing', u); continue
    ws = small['members'][u]; train = [w for w in ws if L.label_key(w) not in held]
    lu, vu = C.level(train); lc, vc = C.level([w for w in small['composers'][u[0]] if L.label_key(w) not in held])
    lv = [('all', ltm_all, v_all), ('composer', lc, vc), ('unit', lu, vu)]
    score = C.Model(lv, short=True, vweight=SCORE_VW)
    durs = C.durations_of(train); real = []; res = collections.defaultdict(list); n_pass = 0
    for w in [w for w in ws if L.label_key(w) in held]:
        ls = [[n[:3] for n in l] for l in C.counted(w).values() if len(l) >= 16]
        if len(ls) < 3: continue
        ls.sort(key=lambda l: sum(n[2] for n in l) / len(l))
        for vi in range(1, len(ls) - 1):
            inner = ls[vi]; others = ls[:vi] + ls[vi + 1:]
            for s0 in range(0, len(inner) - 20, 30):
                if n_pass >= 25: break
                ctx = inner[s0:s0 + 4]; start = ctx[-1][0] + ctx[-1][1]; end = start + 12.0
                rl = [n for n in inner if start <= n[0] < end]
                if len(rl) < 6: continue
                n_pass += 1; lo, hi = min(n[2] for n in inner) - 2, max(n[2] for n in inner) + 2
                h = score.hear(ctx + rl, w.final, others)[len(ctx) - 2:]
                real.append((float(np.mean([a + (b or 0) for a, b in h])), cons(rl, others), len(rl)))
                for sw in SW:
                    m = C.Model(lv, short=False, vweight=sw); rnd = random.Random(s0)
                    for i in range(6):
                        ns, _ = C.sample(m, ctx, w.final, end - start, others=others, lo=lo, hi=hi, below=[ls[vi + 1]], above=[ls[vi - 1]], durations=durs, rnd=rnd)
                        if len(ns) < 2: continue
                        h = score.hear(ctx + ns, w.final, others)[len(ctx) - 2:]
                        res[sw].append((float(np.mean([a + (b or 0) for a, b in h])), cons(ns, others), len(ns)))
    R = np.nanmean(np.array(real), 0); q25, q75 = np.percentile([r[0] for r in real], [25, 75])
    log(u[0], u[1], f'real: bits {R[0]:.2f}, consonant {R[1]:.0%}, notes {R[2]:.1f} ({len(real)} passages)')
    out[' | '.join(u)] = dict(real=[float(x) for x in R], passages=len(real))
    for sw, g in res.items():
        G = np.array(g); inb = float(np.mean((G[:, 0] >= q25) & (G[:, 0] <= q75)))
        out[' | '.join(u)][str(sw)] = [float(np.nanmean(G[:, 0])), float(np.nanmean(G[:, 1])), float(np.nanmean(G[:, 2])), inb]
        log(f'   sampling weight {sw}: bits {np.nanmean(G[:,0]):.2f}, consonant {np.nanmean(G[:,1]):.0%}, notes {np.nanmean(G[:,2]):.1f}, in the real 25-75% band {inb:.0%}')
json.dump(out, open(S + f'cont/phaseJ_score{SCORE_VW:g}.json', 'w'), indent=1)
log('done')
