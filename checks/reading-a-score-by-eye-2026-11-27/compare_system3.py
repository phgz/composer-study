"""Piece 80's third system (bars 37 to 43), read by eye from one picture of all thirteen staves (150 dots an inch,
5.5 pixels between two staff lines before enlarging), against the notes it was drawn from.
A reading: {staff: [bar: [(beat, quarters, [pitches])]]}. Written before the comparison was run; not changed after."""
import os, sys
STUDY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLEND = os.environ.get('COMPOSER_BLEND_ROOT') or os.path.join(os.path.dirname(STUDY), 'composer-blend')
sys.argv = ['x']; sys.path.insert(0, STUDY)
from study import flag_piece as F
src = os.path.join(BLEND, 'pieces/80/notes80.py')      # as it stood on 27 November 2026 (composer-blend 3e202da)
X = F.exporter(src); mod = X.load(src); s = X.build(mod)
FIRST = 37
T = 1 / 3


def trip(*groups):
    """Nine triplet eighths: three groups of three."""
    out = []
    for g, names in enumerate(groups):
        for k, p in enumerate(names.split()): out.append((g + k * T, T, [p]))
    return out


def held(*ps): return [(0, 3, list(ps))]


READ = {
 7: [  # clarinet: the contour seen, the exact notes mostly chosen among each bar's chord
  trip('D6 A5 F#5', 'D5 F#5 A5', 'E6 B5 G#5'), trip('E6 C#6 A5', 'E5 C#5 E5', 'A5 C#6 E6'), trip('C#6 A5 E5', 'C#5 E5 A5', 'C#6 E6 C#6'),
  trip('G#5 E5 C#5', 'E5 G#5 C#6', 'E6 C#6 G#5'), trip('G#5 B5 D6', 'B5 G#5 E5', 'G#5 B5 D6'), trip('C#5 E5 A5', 'C#6 E6 C#6', 'A5 E5 C#5'),
  trip('C#6 A5 F#5', 'C#5 F#5 A5', 'C#6 A5 F#5')],
 9: [  # violin I: the tune of bars 3 to 9, recognised
  [(0, .5, ['F#5']), (.5, .5, ['E5']), (1, 1, ['D5']), (2, 1, ['B4'])], [(0, 2, ['C#5'])], [(0, 1.5, ['E5']), (1.5, .5, ['C#5']), (2, 1, ['A5'])],
  [(0, 1, ['G#5']), (1, 1, ['E5']), (2, 1, ['C#5'])], [(0, 1, ['D5']), (1, 1, ['B4']), (2, 1, ['G#4'])], [(0, 2, ['A4'])],
  [(0, 1, ['F#5']), (1, .5, ['F#5']), (1.5, .5, ['G#5']), (2, 1, ['A5'])]],
 10: [[(0, 2, ['D4', 'F#4']), (2, 1, ['B3', 'E4'])], held('C#4', 'E4'), held('C#4', 'E4'), held('C#4', 'E4'), held('B3', 'D4'), held('C#4', 'E4'), held('C#4', 'F#4')],
 11: [[(0, 2, ['A3']), (2, 1, ['G#3'])], held('A3'), held('A3'), held('G#3'), held('G#3'), held('A3'), held('A3')],
 12: [[(0, 2, ['D3']), (2, 1, ['E2'])], held('A2'), held('A2'), held('C#3'), held('E2'), held('A2'), held('F#2')]}
allt = allh = 0
for k, bars in READ.items():
    part = s.parts[k]; ms = list(part.getElementsByClass('Measure')); total = hit = ph = extra = 0; wrong = []
    for b, mine in enumerate(bars):
        truth = set()
        for n in ms[FIRST - 1 + b].recurse().notes:
            off = float(n.getOffsetInHierarchy(ms[FIRST - 1 + b]))
            for p in n.pitches: truth.add((round(off, 2), round(float(n.duration.quarterLength), 2), p.nameWithOctave.replace('-', 'b')))
        got = {(round(x, 2), round(d, 2), p) for x, d, ps in mine for p in ps}
        total += len(truth); hit += len(truth & got); extra += len(got - truth)
        ph += len({(x, p) for x, d, p in truth} & {(x, p) for x, d, p in got})
        if truth != got: wrong.append((FIRST + b, len(truth - got)))
    allt += total; allh += hit
    print(f'{part.partName:18s} {total:3d} notes; right in beat, pitch and length: {hit:3d} ({hit / total:.0%}); in beat and pitch: {ph:3d}; read but not there: {extra}; bars with misses (bar, notes missed): {wrong}')
print(f'all five staves: {allh} of {allt} ({allh / allt:.0%})')
