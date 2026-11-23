"""paired differences between configurations, the held-out work as the unit: the per-note difference (sum over works / notes), its 95%
interval by bootstrap over works (10,000 resamples), the share of works that improve, and a sign-flip permutation p (two-sided)"""
import json, sys
import numpy as np
rows = json.load(open(sys.argv[1])); rng = np.random.default_rng(1)
COMP = [('the nesting, all lines', 'geo 0.5', 'nest 0.5', 'all'), ('the nesting, inner lines', 'geo 1', 'nest 1', 'inner'),
        ('the weight, all lines (0.5 to 0.75)', 'nest 0.5', 'nest 0.75', 'all'), ('the weight, inner lines (1 to 0.75)', 'nest 1', 'nest 0.75', 'inner'),
        ('old to new, all lines', 'geo 0.5', 'nest 0.75', 'all'), ('old to new, inner lines', 'geo 1', 'nest 0.75', 'inner')]
for test in ('standing', 'small', 'Weber'):
    R = [r for r in rows if r['test'] == test]
    print(f'\n{test}: {len(R)} works')
    for name, a, b, kind in COMP:
        k = (0, 1) if kind == 'all' else (2, 3)
        rs = [r for r in R if r[a][k[1]] > 0]
        if not rs: continue
        d = np.array([r[b][k[0]] - r[a][k[0]] for r in rs]); n = np.array([r[a][k[1]] for r in rs])   # summed bit difference, notes
        est = d.sum() / n.sum()
        idx = rng.integers(0, len(rs), size=(10000, len(rs))); boot = d[idx].sum(1) / n[idx].sum(1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        flips = rng.choice([-1, 1], size=(10000, len(rs))); perm = (flips * d).sum(1) / n.sum(); p = float(np.mean(np.abs(perm) >= abs(d.sum() / n.sum())))
        better = np.mean(d < 0)
        print(f'  {name:40s} {est:+.4f} bits a note  95% [{lo:+.4f}, {hi:+.4f}]  works better {better:4.0%} of {len(rs):3d}  p {p:.4f}')
