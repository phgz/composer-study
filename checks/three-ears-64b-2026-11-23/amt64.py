"""Piece 64b with the inner voices AMT wrote between its tune and its bass (study/amt_write.py), played as 64b is played: the same
tune, bass, doublings, tempi, dynamics and pedal (composer-blend's notes64.build('all')), AMT's notes in place of the alto and the
tenor (those from middle C up at the alto's level, those below at the tenor's; the bars given to AMT as history are 64b's own),
each brought back from seconds to beats through 64b's own tempo map (the writing's input), its length as written where the renderer
would shorten it.

    AMT64=<amt_*_write.json> BLEND=<composer-blend> python3 <composer-blend>/tools/run.py render amt64.py"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(os.environ.get('BLEND', os.path.join(HERE, '..', '..', '..', 'composer-blend')), 'pieces', '64b_inside_the_mazurka')
sys.path.insert(0, PIECE)
import notes64 as N, whole64 as W

MAP, GAIN, FINAL, METRE, MASTERING = W.MAP, W.GAIN, W.FINAL, W.METRE, W.MASTERING


def amt_inner():
    wrote = json.load(open(os.environ['AMT64'])); spec = json.load(open(os.path.join(HERE, wrote.get('input', 'amt_write.json'))))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    beat = lambda t: float(np.interp(t, xt, xb))
    out = dict(alto=[], tenor=[])
    for t, d, m, instr in wrote['notes'] + [[t, d, m, 0] for t, d, m in spec['history']]:      # the history AMT was given
        b = beat(t); span = d / .97 if d / .97 >= .45 else d / .85             # the renderer plays .97 (or .85) of a note's span
        out['alto' if m >= 60 else 'tenor'].append((b, max(beat(t + span) - b, .05), int(m)))
    return {v: sorted(l) for v, l in out.items()}


if os.environ.get('AMT64'): N.inner = amt_inner                         # without AMT64, 64b as made


def build(): return N.build('all')
