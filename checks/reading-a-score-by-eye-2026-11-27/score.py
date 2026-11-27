"""Compare a reading with the truth gen.py kept. A reading is one line a bar: `A4 C5 E4 G5`.

    python3 score.py NAME [FIRST_BAR]     reads NAME.read.txt (bars from FIRST_BAR on, 1 by default)
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = 'CDEFGAB'


def place(p): return STEPS.index(p[0]) + 7 * int(p[-1])


def main():
    name = sys.argv[1]; first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    truth = json.load(open(os.path.join(HERE, name.split('@')[0] + '.truth.json')))
    mine = [l.split() for l in open(os.path.join(HERE, name + '.read.txt')) if l.strip() and not l.startswith('#')]
    n = ok = near = 0; off = []
    for k, row in enumerate(mine):
        t = truth[first - 1 + k]
        assert len(row) == len(t), (name, first + k, row)
        for a, b in zip(row, t):
            n += 1; d = place(a) - place(b); ok += d == 0; near += abs(d) == 1
            if d: off.append(d)
    print(f'{name}: {ok} of {n} notes right ({ok / n:.0%}); one place off (line for space): {near}; further off: {n - ok - near}; misses, in places: {off}')


main()
