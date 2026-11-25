"""Piece 64b as written, the places where the four outside ears flag inner voices Claude finds weak (ears-as-rulers-2026-11-24.md),
for Philip to hear whether they sound wrong. Each clip runs from the bar before the place to the bar after; everything is 64b's own
(its notes, tempi, dynamics, pedal and performance draws).

  SPOTS      bars 4-6      bar 5, beat 1: alto and tenor in unison on G sharp 3 (the leading tone of A minor, doubled)
             bars 20-22    bar 21, beat 2: the tenor's D sharp 4 struck a semitone under the alto's E4
             bars 28-32    bars 29-30: the tenor's F sharp - G - G sharp against the alto's G sharp, then the tenor on C3 a third
                           above the bass, the alto leaping a tenth to C sharp 5 as the tune arrives there; bar 32, beat 1: section
                           1 arrives on E minor with A sharp and D in the inner voices
             bars 61-63    bar 62, beat 1: the tenor's B natural where the plan has F7
             bars 111-113  bar 112, beat 1: the tenor's C sharp in a tonic bar
  INNER=1    the inner voices alone (alto and tenor), with 64b's pedal

Only the notes that begin from 4 seconds before a clip to its end are rendered; spots64_cut.py cuts the clips.

    [INNER=1] BLEND=<composer-blend> python3 <composer-blend>/tools/run.py render spots64.py --output-dir <folder>"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
THREE = os.path.join(HERE, '..', 'three-ears-64b-2026-11-23')
PIECE = os.path.join(os.environ.get('BLEND', os.path.join(HERE, '..', '..', '..', 'composer-blend')), 'pieces', '64b_inside_the_mazurka')
sys.path.insert(0, PIECE)
import notes64 as N, whole64 as W
import eng

MAP, GAIN, FINAL, METRE, MASTERING = W.MAP, W.GAIN, W.FINAL, W.METRE, W.MASTERING
SPOTS = [(4, 6), (20, 22), (28, 32), (61, 63), (111, 113)]
INNER = os.environ.get('INNER') == '1'
_cur, _tags = ['?'], []


class Tagged(list):
    """a voice's notes, telling the build which voice it is reading (each note the build plays is tagged with it)"""
    def __init__(self, xs, name): super().__init__(xs); self.name = name
    def __iter__(self): _cur[0] = self.name; return super().__iter__()


_inner0 = N.inner
N.inner = lambda: {v: Tagged(l, v) for v, l in _inner0().items()}
N.TUNE, N.BASS = Tagged(N.TUNE, 'tune'), Tagged(N.BASS, 'bass')
_note0 = eng.Piece.note


def _note(self, key, b, db, m, L, *a, **k): _tags.append(_cur[0]); return _note0(self, key, b, db, m, L, *a, **k)
eng.Piece.note = _note


def seconds_of_bar(bar):
    spec = json.load(open(os.path.join(THREE, 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    return float(np.interp((bar - 1) * METRE, xb, xt))


def clips(): return [(seconds_of_bar(a), seconds_of_bar(b + 1)) for a, b in SPOTS]


def build():
    _tags.clear(); S, END = N.build('all')
    ws = clips()
    for part in S.parts.values():
        assert len(part['notes']) == len(_tags)
        part['notes'] = [n for n, tag in zip(part['notes'], _tags) if any(t0 - 4 <= n[0] < t1 for t0, t1 in ws)
                         and (not INNER or tag in ('alto', 'tenor'))]
    return S, END
