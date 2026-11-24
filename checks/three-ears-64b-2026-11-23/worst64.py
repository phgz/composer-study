"""Piece 64b's tenor as chosen, against the proposal the outside ears like least, in the four segments of worst64.json: each heard
from the bar before it to its end, everything else 64b's own (the alto chosen for the same bars, which both tenors were drawn
against; the tune, bass, tempi, dynamics, pedal and performance draws). In the least liked version, the tenor's note before the
segment is drawn out to the proposal's first note, as inner() draws it.

  VARIANT=chosen|worst   which tenor
  INNER=1                the inner voices alone (alto and tenor), at their levels in the piece, with 64b's pedal

Only the notes that begin from 4 seconds before a clip to its end are rendered; worst64_cut.py cuts the clips.

    VARIANT=worst [INNER=1] BLEND=<composer-blend> python3 <composer-blend>/tools/run.py render worst64.py"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(os.environ.get('BLEND', os.path.join(HERE, '..', '..', '..', 'composer-blend')), 'pieces', '64b_inside_the_mazurka')
sys.path.insert(0, PIECE)
import notes64 as N, whole64 as W
import eng

MAP, GAIN, FINAL, METRE, MASTERING = W.MAP, W.GAIN, W.FINAL, W.METRE, W.MASTERING
VARIANT = os.environ.get('VARIANT', 'chosen'); INNER = os.environ.get('INNER') == '1'
SEL = json.load(open(os.path.join(HERE, 'worst64.json')))
_cur, _tags = ['?'], []


class Tagged(list):
    """a voice's notes, telling the build which voice it is reading (each note the build plays is tagged with it)"""
    def __init__(self, xs, name): super().__init__(xs); self.name = name
    def __iter__(self): _cur[0] = self.name; return super().__iter__()


_inner0 = N.inner


def inner():
    iv = _inner0()
    if VARIANT == 'worst':
        ten = list(iv['tenor'])
        for s in SEL:
            s0, s1 = (s['bars'][0] - 1) * METRE, s['bars'][1] * METRE
            prop = json.load(open(os.path.join(PIECE, 'proposals', f"{s['section']}-tenor-{s['segment']}.json")))['proposals'][s['worst']]
            notes = [tuple(n) for n in prop['notes']]; first = notes[0][0]
            before = [n for n in ten if n[0] < s0 - 1e-6]; after = [n for n in ten if n[0] >= s1 - 1e-6]
            if before and not N.resting(before[-1][0], first):
                before[-1] = (before[-1][0], first - before[-1][0], before[-1][2])
            ten = before + notes + after
        iv = dict(iv, tenor=ten)
    return {v: Tagged(l, v) for v, l in iv.items()}


N.inner = inner
N.TUNE, N.BASS = Tagged(N.TUNE, 'tune'), Tagged(N.BASS, 'bass')
_note0 = eng.Piece.note


def _note(self, key, b, db, m, L, *a, **k): _tags.append(_cur[0]); return _note0(self, key, b, db, m, L, *a, **k)
eng.Piece.note = _note


def seconds_of_bar(bar):
    spec = json.load(open(os.path.join(HERE, 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    return float(np.interp((bar - 1) * METRE, xb, xt))


def clips():
    """each segment's clip, in seconds: from the bar before it to its end"""
    return [(seconds_of_bar(s['bars'][0] - 1), seconds_of_bar(s['bars'][1] + 1)) for s in SEL]


def build():
    _tags.clear(); S, END = N.build('all')
    ws = clips()
    for part in S.parts.values():
        assert len(part['notes']) == len(_tags)
        part['notes'] = [n for n, tag in zip(part['notes'], _tags) if any(t0 - 4 <= n[0] < t1 for t0, t1 in ws)
                         and (not INNER or tag in ('alto', 'tenor'))]
    return S, END
