"""How many of each composer's works the periods table places, from a score-reader catalogue folder (numbers and titles only; a
work placed by its stated year is not counted here). Run: python3 -I study/coverage.py <score-reader>/catalogue"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import periods as P


def main(cat):
    t = P.table(); rows = []
    for f in sorted(glob.glob(os.path.join(cat, '*.json'))):
        if os.path.basename(f) in ('index.json', 'compile_status.json'): continue
        d = json.load(open(f, encoding='utf-8')); c = collections.Counter()
        for w in d['works']: c[P.period_of(w, t)[0]] += 1
        missing = d['composer'] not in t
        rows.append((d['composer'], len(d['works']), dict(c), missing))
    for name, n, c, missing in rows:
        if len(c) > 1 or missing or None in c:
            print(f'{name[:30]:30} {n:5}  ' + ('NOT IN THE TABLE' if missing else ', '.join(f'{k or "(none)"} {v}' for k, v in sorted(c.items(), key=lambda x: str(x[0])))))
    print(f'{sum(1 for r in rows if not r[3])} of {len(rows)} composers in the table')


if __name__ == '__main__':
    main(sys.argv[1])
