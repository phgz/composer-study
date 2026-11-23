"""Piece 64b's Neapolitans, sampled again: for each segment whose bass reaches the Neapolitan, NS (200) continuations of the alto and of
the tenor from the same context as when they were chosen, by the model as it was (the levels' vertical views joined by a geometric
mean) and nested; the share of their sounding time over the Neapolitan that is the chord's own notes"""
import sys, json, random, time
import numpy as np
sys.path.insert(0, '/home/claude/composer-study'); sys.path.insert(0, '/home/claude/composer-blend/pieces/64b_inside_the_mazurka')
from study import continuations as C, lines as L
import notes64 as N
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
S = '/tmp/claude-0/-home-claude/669e17e8-ea5c-5071-9040-59c8c60ea523/scratchpad/'
weber = L.read(S + 'ready25', composers=['Carl Maria von Weber']); unit = [w for w in weber if len(w.lines) >= 4]
levels = [('all',) + C.load_all(S + 'cont/all-v25-full.npz'), ('composer',) + C.level(weber), ('unit',) + C.level(unit)]
CFG = [('mean', None)] + [(m, a) for m, a in json.loads(sys.argv[1])] if len(sys.argv) > 1 else [('mean', None), ('level', 20)]
NS = int(sys.argv[2]) if len(sys.argv) > 2 else 200
iv = N.inner()
def neap(sec):                       # the Neapolitan's bass and chord tones: F in E minor, F flat in E flat major
    return (4, {4, 8, 11}) if sec == 3 else (5, {5, 9, 0})
out = {}
for sec, segs in N.SEGMENTS.items():
    bpc, tones = neap(sec)
    for k, (b0, b1) in enumerate(segs, 1):
        start, end = (b0 - 1) * N.METRE, b1 * N.METRE
        spans = [(o, o + d) for o, d, m in N.BASS if start <= o < end and m % 12 == bpc]
        spans += [(t0, t1) for t0, t1 in ((110 * 3 + 1, 111 * 3), (118 * 3 + 1, 119 * 3)) if start <= t0 < end]   # on its fifth, then its third
        if not spans: continue
        for voice in ('alto', 'tenor'):
            ctx = [n for n in iv[voice] if n[0] < start]
            gap = start - (ctx[-1][0] + ctx[-1][1])
            if gap > 1e-6: ctx = [(o + gap, d, m) for o, d, m in ctx]
            other = iv['tenor' if voice == 'alto' else 'alto']
            others = [N.TUNE, N.BASS, other]
            below, above = ([N.TUNE], [N.BASS]) if voice == 'alto' else ([iv['alto']], [N.BASS])
            res = {}
            for mode, a in CFG:
                m = C.Model(levels, **C.SAMPLE, vmode=mode, valpha=a); rnd = random.Random(sec * 1000 + k * 10 + (voice == 'tenor'))
                good = tot = 0.0
                for _ in range(NS):
                    ns, _ = C.sample(m, ctx, N.FINALS[sec], end - start, others=others, lo=N.RANGE[voice][0], hi=N.RANGE[voice][1], below=below,
                                     above=above, durations=C.durations_of(unit), grid=0.5, rnd=rnd)
                    for o, d, p in ns:
                        for s0, s1 in spans:
                            ov = max(0.0, min(o + d, s1) - max(o, s0))
                            tot += ov; good += ov * (p % 12 in tones)
                res[f'{mode} {a}'] = good / tot if tot else None
            out[f'{sec}-{voice}-{k} (bars {b0}-{b1})'] = res
            log(sec, voice, k, f'bars {b0}-{b1}', ' | '.join(f'{c}: {v:.0%}' for c, v in res.items() if v is not None))
keys = list(next(iter(out.values())).keys())
log('ALL', ' | '.join(f'{c}: {np.mean([r[c] for r in out.values() if r[c] is not None]):.0%}' for c in keys))
json.dump(out, open(S + 'cont/neapolitan64.json', 'w'), indent=1)
