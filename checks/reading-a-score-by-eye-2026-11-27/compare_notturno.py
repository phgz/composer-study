"""Compare read_notturno.py with the catalogue's copy of the movement (score-reader's ready-read sample: OpenScore's edition).

    python3 -I compare_notturno.py /path/to/alexander-borodin/0007

The catalogue's copy is data: it is read as text, nothing in it is run.
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read_notturno as R

STEP = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi(p):
    acc = p.count('#') - p.count('b'); return 12 * (int(p[-1]) + 1) + STEP[p[0]] + acc


def name(m): return f'{NAMES[m % 12]}{m // 12 - 1}'


def main():
    folder = sys.argv[1]; PART = dict(p1='violin I', p2='violin II', p3='viola', p4='cello')
    rows = list(csv.DictReader(open(os.path.join(folder, 'notes.tsv')), delimiter='\t'))
    T = {}
    for r in rows:
        b = int(r['bar'])
        if b in R.BARS: T.setdefault((r['part'], b), set()).add((round(float(r['beat']), 2), int(r['midi']), round(float(r['dur']), 2)))
    tot = hit = pitch = extra = 0; per = {}; misses = []
    for part in ('p1', 'p2', 'p3', 'p4'):
        for b in R.BARS:
            truth = T.get((part, b), set())
            mine = {(round(x, 2), midi(p), round(d, 2)) for x, d, ps in R.READ[part].get(b, []) for p in ps}
            t2 = {(x, m) for x, m, d in truth}; m2 = {(x, m) for x, m, d in mine}
            a = per.setdefault(part, [0, 0, 0, 0]); a[0] += len(truth); a[1] += len(truth & mine); a[2] += len(t2 & m2); a[3] += len(mine - truth)
            if truth != mine:
                misses.append((PART[part], b, sorted((x, name(m), d) for x, m, d in truth - mine), sorted((x, name(m), d) for x, m, d in mine - truth)))
    for part, (n, h, p, e) in per.items():
        print(f'{PART[part]:10s} {n:3d} notes in the catalogue; read right in beat, pitch and length: {h:3d}; in beat and pitch: {p:3d}; read but not there: {e}')
        tot += n; hit += h; pitch += p; extra += e
    print(f'all four   {tot:3d} notes; right in beat, pitch and length: {hit} ({hit / tot:.1%}); in beat and pitch: {pitch} ({pitch / tot:.1%}); read but not there: {extra}')
    print(f'bars read: {len(R.BARS)} (1 to 7, 15 to 28); bars with any difference: {len({(p, b) for p, b, _, _ in misses})}')
    for p, b, t, m in misses: print(f'   {p}, bar {b}: the catalogue has {t}; read {m}')
    det = list(csv.DictReader(open(os.path.join(folder, 'detail.tsv')), delimiter='\t')); G = {}
    for r in det:
        if r.get('grace') and int(r['bar']) in R.BARS: G.setdefault((r['part'], int(r['bar'])), []).append(int(r['midi']))
    keys = sorted(set(G) | set(R.GRACES)); ok = 0
    for k in keys:
        mine = [midi(p) for p in R.GRACES.get(k, '').split()]; same = mine == G.get(k, []); ok += same
        if not same: print(f'   grace notes, {PART[k[0]]} bar {k[1]}: the catalogue has {[name(m) for m in G.get(k, [])]}; read {[name(m) for m in mine]}')
    print(f'grace-note groups: {ok} of {len(keys)} the same')


main()
