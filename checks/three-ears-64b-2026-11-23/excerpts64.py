"""Four passages of piece 64b, in its three versions, for listening side by side: 64b as made, and with the notes AMT Large or AMT
Medium wrote between its tune and bass (amt64.py). Everything else is 64b's own: the same tune, bass, tempi, dynamics, pedal and
performance draws (each note's are keyed by its beat), so that the tune and bass sound the same in all three.

  PASSAGES   bars 5-9      the theme's close: VI, the Neapolitan (bar 7), the tonic; AMT's first bars after its five of history
             bars 89-92    E flat major after the intermezzo, where both AMT models wrote nothing
             bars 105-112  section 4, the theme in the bass, the Neapolitan sixth at bar 111
             bars 141-148  the high point: the Neapolitan held at bar 144, the tune's A at the top
  FORWARD=1  the inner voices brought out, a step louder (level +1, as a pianist voices them), the rest unchanged

Only the notes that begin in a passage, or up to 4 seconds before it, are rendered; excerpts64_cut.py cuts the passages from the
unmastered mix and gives every clip of a passage the same gain.

    VERSION=ours|large|medium [FORWARD=1] BLEND=<composer-blend> python3 <composer-blend>/tools/run.py render excerpts64.py"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PASSAGES = [(5, 9), (89, 92), (105, 112), (141, 148)]
VERSION = os.environ.get('VERSION', 'ours'); FORWARD = os.environ.get('FORWARD') == '1'
WRITINGS = dict(large='amt_large_write_long_given1.json', medium='amt_medium_write_long_given1.json')
if VERSION != 'ours': os.environ['AMT64'] = os.path.join(HERE, WRITINGS[VERSION])
else: os.environ.pop('AMT64', None)
import amt64 as A                                                       # 64b's notes64, with AMT's notes when AMT64 is set
N = A.N
MAP, GAIN, FINAL, METRE = A.MAP, A.GAIN, A.FINAL, A.METRE
MASTERING = A.MASTERING
LEVEL0 = dict(N.LEVEL)                                                  # 64b's levels, so that each build starts from them


def seconds_of_bar(bar):
    spec = json.load(open(os.path.join(HERE, 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    return float(np.interp((bar - 1) * METRE, xb, xt))


def windows():
    return [(seconds_of_bar(a), seconds_of_bar(b + 1)) for a, b in PASSAGES]


def build():
    N.LEVEL.update(LEVEL0)
    if FORWARD:
        for v in ('alto', 'tenor'): N.LEVEL[v] = LEVEL0[v] + 1.0
    S, END = N.build('all')
    ws = windows()
    for part in S.parts.values():
        part['notes'] = [n for n in part['notes'] if any(t0 - 4 <= n[0] < t1 for t0, t1 in ws)]
    return S, END
