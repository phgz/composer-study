"""Measurements for piece 81's reading (27 November 2026), from score-reader's ready-read copies (data; run with -I).
    python3 -I measure.py RACHMANINOFF_FOLDER MAHLER_FOLDER"""
import csv, collections, sys, os
N = 'C C# D Eb E F F# G Ab A Bb B'.split()
def nm(m): return N[m % 12] + str(m // 12 - 1)
def load(p):
    return [(r['part'], float(r['onset']), float(r['dur']), int(float(r['midi'])), int(float(r['bar'])), float(r['beat'])) for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t')]
def top(ns, part, b0, b1):
    by = {}
    for n in ns:
        if n[0] == part and b0 <= n[4] <= b1: by.setdefault(round(n[1], 3), []).append(n)
    return [max(v, key=lambda n: n[3]) for k, v in sorted(by.items())]
R, M = sys.argv[1:3]

print('RACHMANINOFF, Prelude op. 23 no. 4 (ASAP, a printed score): the tune as the right hand\'s top note, the file\'s bars 3 to 17')
ns = load(os.path.join(R, '0031', 'notes.tsv')); t = top(ns, 'p1', 3, 17)
bars = collections.OrderedDict()
for n in t: bars.setdefault(n[4], []).append(n)
print('  bars:', len(bars), '; beginning with a note of two beats or more:', sum(1 for b in bars.values() if b[0][2] >= 2 - 1e-6))
print('  bars ending in a turn of quick notes (two or more notes of half a beat or less in the last beat):', [k for k, b in bars.items() if sum(1 for n in b if n[5] >= 2 - 1e-6 and n[2] <= .5 + 1e-6) >= 2])
mv = [b[3] - a[3] for a, b in zip(t, t[1:])]
print('  moves:', len(mv), '; steps (1 or 2 half steps):', sum(1 for m in mv if abs(m) in (1, 2)), '; repeats:', mv.count(0), '; thirds:', sum(1 for m in mv if abs(m) in (3, 4)), '; fourths and fifths:', sum(1 for m in mv if abs(m) in (5, 7)), '; wider:', sum(1 for m in mv if abs(m) > 7))
longs = [n for n in t if n[2] >= 2 - 1e-6]; c = collections.Counter(nm(n[3]) for n in longs)
print('  long notes:', len(longs), c.most_common(4), '; span of the whole:', nm(min(n[3] for n in t)), 'to', nm(max(n[3] for n in t)))
print('  first eight bars span:', nm(min(n[3] for n in t if n[4] <= 10)), 'to', nm(max(n[3] for n in t if n[4] <= 10)))
print('  metre: beats in a bar by the notes of bar 3:', sum(n[2] for n in bars[3]))

print('RACHMANINOFF, Prelude op. 32 no. 5 (ASAP): the right hand\'s top note, the file\'s bars 2 to 6')
ns = load(os.path.join(R, '0034', 'notes.tsv')); t = [n for n in top(ns, 'p1', 2, 6) if n[2] >= .3]
mv = [b[3] - a[3] for a, b in zip(t, t[1:])]
print('  notes:', ' '.join(nm(n[3]) for n in t)); print('  moves:', len(mv), '; steps:', sum(1 for m in mv if abs(m) in (1, 2)), '; repeats:', mv.count(0), '; thirds:', sum(1 for m in mv if abs(m) in (3, 4)), '; wider:', sum(1 for m in mv if abs(m) > 4))

print('MAHLER, the voice in ten songs')
import json
idx = json.load(open(os.path.join(M, 'index.json'), encoding='utf-8')); ws = idx['works'] if isinstance(idx, dict) else idx
for w in ws:
    ns = load(os.path.join(M, w['folder'], 'notes.tsv')); parts = {r['part']: r['name'] for r in csv.DictReader(open(os.path.join(M, w['folder'], 'parts.tsv'), encoding='utf-8'), delimiter='\t')}
    vp = [p for p, n in parts.items() if 'oice' in n][0]; voice = sorted((n for n in ns if n[0] == vp), key=lambda n: n[1]); piano = [n for n in ns if n[0] != vp]
    # the figure: a half step down, the same note, a half step down, in even notes; then what
    found = []
    for i in range(len(voice) - 4):
        a, b, c, d, e = voice[i:i + 5]
        if (b[3] - a[3], c[3] - b[3], d[3] - c[3]) == (-1, 0, -1):
            gaps = [b[1] - a[1], c[1] - b[1], d[1] - c[1]]
            if max(gaps) <= 1.1 * min(gaps): found.append((a[4], nm(a[3]), e[3] - d[3]))
    # leaning: the voice's note is not among the notes the piano has sounding when it begins
    out = struck = step = 0
    for i, v in enumerate(voice):
        snd = {p[3] % 12 for p in piano if p[1] <= v[1] + 1e-6 and p[1] + p[2] > v[1] + 1e-6}
        if not snd or v[3] % 12 in snd: continue
        out += 1
        if any(abs(p[1] - v[1]) < 1e-6 for p in piano): struck += 1
        if i + 1 < len(voice) and abs(voice[i + 1][3] - v[3]) in (1, 2): step += 1
    print(f"  {w['label'][:62]:62s} voice notes {len(voice):3d}; not among the piano's notes {out:3d} ({out / len(voice):.0%}), struck with the piano {struck}, then by step {step}; the figure: {found}")

print('MAHLER, Nun will die Sonn\': the two bare lines before the voice (the piano\'s notes before the first sung note)')
ns = load(os.path.join(M, '0001', 'notes.tsv')); first = min(n[1] for n in ns if n[0] == 'staff1'); pn = sorted((n for n in ns if n[0] != 'staff1' and n[1] < first - 1e-6), key=lambda n: n[1])
times = sorted({n[1] for n in pn}); iv = collections.Counter(); motion = collections.Counter(); prev = None; counts = collections.Counter()
for x in times:
    snd = sorted({n[3] for n in pn if n[1] <= x + 1e-6 and n[1] + n[2] > x + 1e-6}); counts[len(snd)] += 1
    if len(snd) == 2:
        iv[(snd[1] - snd[0]) % 12] += 1
        if prev and len(prev) == 2:
            lo, hi = snd[0] - prev[0], snd[1] - prev[1]
            motion['oblique' if 0 in (lo, hi) and lo != hi else 'the same' if lo == hi == 0 else 'contrary' if lo * hi < 0 else 'parallel or similar'] += 1
    prev = snd
print('  moments:', len(times), '; notes sounding at each:', dict(counts), '; until beat', first)
print('  intervals between the two (half steps, octaves folded):', dict(sorted(iv.items())), '; thirds and sixths:', sum(iv[k] for k in (3, 4, 8, 9)), '; seconds, sevenths and the tritone:', sum(iv[k] for k in (1, 2, 6, 10, 11)), '; fourths, fifths, octaves:', sum(iv[k] for k in (0, 5, 7)))
print('  how they move from one moment to the next:', dict(motion)); lows = [n[3] for n in pn]; print('  from', nm(min(lows)), 'to', nm(max(lows)), '; widest distance between the two:', max((max(s) - min(s)) for s in [sorted({n[3] for n in pn if n[1] <= x + 1e-6 and n[1] + n[2] > x + 1e-6}) for x in times] if len(s) == 2))

print('RACHMANINOFF op. 23 no. 4 again, the file\'s bars 3 to 11 only (one note at a time in the right hand but for one moment)')
ns = load(os.path.join(R, '0031', 'notes.tsv')); t = top(ns, 'p1', 3, 11)
print('  right-hand notes in those bars:', sum(1 for n in ns if n[0] == 'p1' and 3 <= n[4] <= 11), '; top line:', len(t), ' '.join(f'{nm(n[3])}/{n[2]:g}' for n in t))
mv = [b[3] - a[3] for a, b in zip(t, t[1:])]
print('  moves:', len(mv), '; steps:', sum(1 for m in mv if abs(m) in (1, 2)), '; thirds:', sum(1 for m in mv if abs(m) in (3, 4)), '; fourths and fifths:', sum(1 for m in mv if abs(m) in (5, 7)), '; wider:', sum(1 for m in mv if abs(m) > 7), [m for m in mv if abs(m) > 2])
longs = [n for n in t if n[2] >= 2 - 1e-6]; print('  long notes:', len(longs), collections.Counter(nm(n[3]) for n in longs).most_common(), '; span', nm(min(n[3] for n in t)), nm(max(n[3] for n in t)))
ns1 = load(os.path.join(M, '0001', 'notes.tsv')); v = sorted((n for n in ns1 if n[0] == 'staff1'), key=lambda n: n[1])[0]
print('MAHLER Nun will die Sonn\': the first sung note is in bar', v[4], 'beat', v[5], '; bar lengths:', sorted({round(b - a, 2) for a, b in zip(sorted({n[1] - n[5] for n in ns1}), sorted({n[1] - n[5] for n in ns1})[1:])})[:4])
pn = [n for n in ns1 if n[0] != 'staff1']
for b in range(0, 12):
    xs = sorted({n[1] for n in pn if n[4] == b}); c = collections.Counter(len({m[3] for m in pn if m[1] <= x + 1e-6 and m[1] + m[2] > x + 1e-6}) for x in xs)
    print('   bar', b, 'notes sounding at each moment:', dict(c), '; voice sings:', any(n[0] == 'staff1' and n[4] == b for n in ns1))
