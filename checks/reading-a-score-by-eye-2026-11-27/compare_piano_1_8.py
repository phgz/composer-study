"""A reading of a drawn score by eye (Claude's, from the picture alone) against the notes the picture was drawn from.
The reading: {staff: [bar: [(beat, quarters, [pitches])]]}; a note counts when its staff, bar, beat, pitch and length all agree."""
import os, sys
STUDY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLEND = os.environ.get('COMPOSER_BLEND_ROOT') or os.path.join(os.path.dirname(STUDY), 'composer-blend')
sys.argv = ['x']; sys.path.insert(0, STUDY)
from study import flag_piece as F
src = os.path.join(BLEND, 'pieces/80/notes80.py')      # as it stood on 27 November 2026 (composer-blend 3e202da)
X = F.exporter(src); mod = X.load(src); s = X.build(mod)
READ = {
 0: [  # piano, right hand, bars 1 to 8
  [(0, 1.5, ['E5']), (1.5, .5, ['C#5']), (2, 1, ['A5']), (0, 3, ['C#4', 'E4'])],
  [(0, 1, ['G#5']), (1, 1, ['F#5']), (2, 1, ['E5']), (0, 3, ['E4'])],
  [(0, .5, ['F#5']), (.5, .5, ['E5']), (1, 1, ['D5']), (0, 2, ['D4', 'F#4']), (2, 1, ['E4', 'B4'])],
  [(0, 2, ['C#5']), (0, 3, ['C#4', 'E4'])],
  [(0, 1.5, ['E5']), (1.5, .5, ['C#5']), (2, 1, ['A5']), (0, 3, ['C#4', 'E4'])],
  [(0, 1, ['G#5']), (1, 1, ['E5']), (2, 1, ['C#5']), (0, 3, ['C#4', 'E4'])],
  [(0, 1, ['D5']), (1, 1, ['B4']), (2, 1, ['G#4']), (0, 3, ['D4'])],
  [(0, 2, ['A4']), (0, 3, ['C#4', 'E4'])]],
 1: [  # piano, left hand
  [(0, 3, ['A2', 'A3'])], [(0, 3, ['E2', 'G#3', 'B3'])], [(0, 2, ['D3', 'A3']), (2, 1, ['E2', 'G#3', 'B3'])], [(0, 3, ['A2', 'A3'])],
  [(0, 3, ['A2', 'A3'])], [(0, 3, ['C#3', 'G#3'])], [(0, 3, ['E2', 'G#3', 'B3'])], [(0, 3, ['A2', 'A3'])]]}
total = hit = pitch_hit = 0; extra = 0; wrong = []
for k, bars in READ.items():
    part = s.parts[k]; ms = list(part.getElementsByClass('Measure'))
    for b, mine in enumerate(bars):
        truth = set()
        for n in ms[b].recurse().notes:
            off = float(n.getOffsetInHierarchy(ms[b]))
            for p in n.pitches: truth.add((round(off, 3), round(float(n.duration.quarterLength), 3), p.nameWithOctave.replace('-', 'b')))
        got = {(round(x, 3), round(d, 3), p) for x, d, ps in mine for p in ps}
        total += len(truth); hit += len(truth & got); extra += len(got - truth)
        pitch_hit += len({(x, p) for x, d, p in truth} & {(x, p) for x, d, p in got})
        if truth != got: wrong.append((part.partName, b + 1, sorted(truth - got), sorted(got - truth)))
print(f'{total} notes in the drawn score\'s piano part, bars 1 to 8; read right in beat, pitch and length: {hit} ({hit / total:.0%}); right in beat and pitch: {pitch_hit}; notes read that are not there: {extra}')
for w in wrong: print('   ', w)
