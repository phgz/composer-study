"""Readings for piece 84 (D, the tune made of the holes): Bach's solo dances and Corelli's op. 4 correnti and gighe, from
score-reader's notes (part, onset, dur, midi, bar, beat; quarters). Run with python3 -I. Data only: nothing here is imported
from a score.

Bach, the line that holds two: a run of at least six notes in which every move is a leap of a fourth or more, the leaps
alternating up and down, and each of the two strands (every other note) moves by a step or less (2 semitones) or stays:
the ear can gather every other note into a line of its own. A pedal run: one of the two strands keeps one pitch.

Corelli, the two violins: at each onset of either violin, which of the two begins a note there; and the violins' rests
inside the movement (a beat with no note sounding in that violin, after its first note and before its last)."""
import collections, csv, glob, os, sys

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tsv')


def notes(path):
    with open(path, newline='') as f:
        r = csv.DictReader(f, delimiter='\t')
        return [dict(part=x['part'], t=float(x['onset']), d=float(x['dur']), m=int(float(x['midi'])), bar=x['bar'], beat=x['beat'])
                for x in r]


def line(ns):
    """one note an onset, the highest where a chord is struck"""
    by = {}
    for n in ns:
        if n['t'] not in by or n['m'] > by[n['t']]['m']: by[n['t']] = n
    return [by[t] for t in sorted(by)]


def strand_runs(ln, least=6):
    """runs of two strands: (start index, length, pedal?)"""
    out, i = [], 0
    mv = [ln[k + 1]['m'] - ln[k]['m'] for k in range(len(ln) - 1)]
    while i < len(mv):
        j = i
        while j < len(mv) and abs(mv[j]) >= 5 and (j == i or (mv[j] > 0) != (mv[j - 1] > 0)):
            if j - i >= 1 and abs(ln[j + 1]['m'] - ln[j - 1]['m']) > 2: break
            j += 1
        n = j - i + 1
        if n >= least:
            a = {ln[k]['m'] for k in range(i, j + 1, 2)}; b = {ln[k]['m'] for k in range(i + 1, j + 1, 2)}
            out.append((i, n, len(a) == 1 or len(b) == 1))
        i = max(j, i + 1)
    return out


def bach():
    rows, kinds = [], collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for p in sorted(glob.glob(os.path.join(D, 'bach_*.tsv'))):
        ln = line(notes(p)); runs = strand_runs(ln)
        inrun = sum(n for _, n, _ in runs); ped = sum(n for _, n, pd in runs if pd)
        even = sum(1 for a, b in zip(ln, ln[1:]) if abs(a['d'] - b['d']) < 1e-6)
        name = os.path.basename(p)[5:-4]
        kind = 'courante' if 'our' in name or 'orr' in name else 'gigue' if 'Gi' in name else 'bourree'
        k = kinds[kind]; k[0] += len(ln); k[1] += inrun; k[2] += ped; k[3] += even; k[4] += 1
        longest = max(runs, key=lambda r: r[1]) if runs else None
        rows.append((name, len(ln), inrun, ped, even / max(1, len(ln) - 1),
                     (ln[longest[0]]['bar'], longest[1], 'pedal' if longest[2] else 'two moving') if longest else None))
    print('Bach, solo dances: notes, in two-strand runs (of which one strand a pedal), even rhythm, the longest run (bar, notes)')
    for r in rows: print(f"  {r[0]:28s} {r[1]:4d} notes  {r[2]:4d} in runs ({r[2] / r[1]:.0%}; pedal {r[3]})  even {r[4]:.0%}  longest {r[5]}")
    for kind, (n, i, pd, ev, w) in kinds.items():
        print(f"  {kind}: {w} movements, {n} notes, {i / n:.1%} in two-strand runs ({pd / n:.1%} with a pedal strand), even {ev / (n - w):.0%}")
    n = sum(k[0] for k in kinds.values()); i = sum(k[1] for k in kinds.values()); pd = sum(k[2] for k in kinds.values())
    print(f"  all: {n} notes, {i / n:.1%} in two-strand runs, {pd / n:.1%} with a pedal strand")


def corelli():
    print('Corelli, op. 4: the violins at each onset (v1 alone, v2 alone, both), and the beats each violin rests within the movement')
    tot = collections.Counter(); rest = collections.Counter(); beats = collections.Counter()
    for p in sorted(glob.glob(os.path.join(D, 'corelli_*.tsv'))):
        ns = notes(p); v = {s: [n for n in ns if n['part'] == s] for s in ('staff1', 'staff2')}
        on = {s: {round(n['t'], 4) for n in v[s]} for s in v}
        c = collections.Counter('both' if t in on['staff1'] and t in on['staff2'] else 'v1' if t in on['staff1'] else 'v2'
                                for t in on['staff1'] | on['staff2'])
        tot.update(c)
        name = os.path.basename(p)[8:-4]; out = []
        for s in v:
            first, last = min(n['t'] for n in v[s]), max(n['t'] + n['d'] for n in v[s])
            grid = [first + k for k in range(int(last - first))]
            silent = sum(1 for g in grid if not any(n['t'] <= g + 1e-6 < n['t'] + n['d'] for n in v[s]))
            rest[s] += silent; beats[s] += len(grid); out.append(f"{s} rests {silent} of {len(grid)} beats")
        ln = line(v['staff1']); mv = [b['m'] - a['m'] for a, b in zip(ln, ln[1:])]
        fourths = sum(1 for x in mv if abs(x) in (5, 7)); runs = strand_runs(ln, least=4)
        print(f"  {name}: onsets {dict(c)}; {'; '.join(out)}; v1 leaps of a 4th or 5th {fourths / len(mv):.0%}, "
              f"two-strand runs of 4+ notes in v1: {len(runs)} ({sum(r[1] for r in runs)} notes)")
    n = sum(tot.values())
    print(f"  all: onsets v1 alone {tot['v1'] / n:.0%}, v2 alone {tot['v2'] / n:.0%}, both {tot['both'] / n:.0%}; "
          f"rests: v1 {rest['staff1'] / beats['staff1']:.0%} of its beats, v2 {rest['staff2'] / beats['staff2']:.0%}")


if __name__ == '__main__':
    bach(); corelli()
