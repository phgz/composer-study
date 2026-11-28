"""Bach's six Schübler chorales (BWV 645-650): the chorale's part (the one with the fewest notes) against the running parts:
its notes' length, its phrases (runs of chorale notes broken by a rest of a bar or more) and how much of the time it is
silent while the others play. Run with python3 -I."""
import csv, statistics, sys
def notes(p):
    with open(p, newline='') as f: return [dict(part=x['part'], t=float(x['onset']), d=float(x['dur']), m=int(float(x['midi'])), bar=x['bar']) for x in csv.DictReader(f, delimiter='\t')]
for n in (645, 646, 647, 648, 649, 650):
    ns = notes(f'tsv/schubler_{n}.tsv'); parts = {}
    for x in ns: parts.setdefault(x['part'], []).append(x)
    seen, uniq = set(), {}
    for p, v in parts.items():
        key = tuple((x['t'], x['m']) for x in v)
        if key in seen: continue
        seen.add(key); uniq[p] = v
    ch = min((p for p in uniq if len(uniq[p]) >= 15), key=lambda p: len(uniq[p]))
    end = max(x['t'] + x['d'] for x in ns)
    bar = statistics.mode([b['t'] - a['t'] for a, b in zip(ns, ns[1:]) if False] or [4.0])
    c = sorted(uniq[ch], key=lambda x: x['t'])
    phrases = [[c[0]]]
    for a, b in zip(c, c[1:]):
        if b['t'] - (a['t'] + a['d']) >= 2.0: phrases.append([b])
        else: phrases[-1].append(b)
    sounding = sum(x['d'] for x in c)
    others = [x for p, v in uniq.items() if p != ch for x in v]
    print(f"BWV {n}: chorale in {ch} ({len(c)} notes, median {statistics.median(x['d'] for x in c):g} quarters), the others' median "
          f"{statistics.median(x['d'] for x in others):g} quarters; {len(phrases)} phrases of {', '.join(str(len(p)) for p in phrases)} notes; "
          f"the chorale sounds {sounding / end:.0%} of the {end:g} quarters; first entry at quarter {c[0]['t']:g} (bar {c[0]['bar']})")


def covered(intervals, end, step=0.25):
    """the share of the time, on a grid of sixteenths, in which some note of INTERVALS sounds"""
    k = 0; n = int(end / step)
    for g in range(n):
        t = g * step + 1e-6
        if any(a <= t < b for a, b in intervals): k += 1
    return k / n


print('While the chorale rests, the running parts:')
for n in (645, 646, 647, 648, 649, 650):
    ns = notes(f'tsv/schubler_{n}.tsv'); parts = {}
    for x in ns: parts.setdefault(x['part'], []).append(x)
    ch = min((p for p in parts if len(parts[p]) >= 15), key=lambda p: len(parts[p]))
    end = max(x['t'] + x['d'] for x in ns)
    chord = [(x['t'], x['t'] + x['d']) for x in parts[ch]]
    others = [(x['t'], x['t'] + x['d']) for p, v in parts.items() if p != ch for x in v]
    gaps = []; c = sorted(chord)
    for (a, b), (a2, b2) in zip(c, c[1:]):
        if a2 - b >= 2.0: gaps.append((b, a2))
    if c[0][0] > 0: gaps.insert(0, (0, c[0][0]))
    rest_time = sum(b - a for a, b in gaps)
    inside = sum(covered([(x, y) for x, y in others if x < b and y > a], b, 0.25) * 0 for a, b in gaps)
    k = 0; m = 0
    for a, b in gaps:
        g = a
        while g < b - 1e-9:
            m += 1; k += any(x <= g + 1e-6 < y for x, y in others); g += 0.25
    print(f"  BWV {n}: the chorale's rests (the opening included) {rest_time:g} quarters; the others sound in {k / m:.0%} of them; "
          f"over the whole piece the others sound {covered(others, end):.0%} of the time")
