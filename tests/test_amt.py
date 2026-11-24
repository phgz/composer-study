"""AMT's tokens, made with its own code. Run: python3 -m pytest -q tests (needs a checkout of github.com/jthickstun/anticipation:
ANTICIPATION=<path>, or beside this repository's parent as jthickstun/anticipation)"""
import os, random, sys
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import amt as A

CO = os.environ.get('ANTICIPATION', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                                 'jthickstun', 'anticipation'))
pytestmark = pytest.mark.skipif(not os.path.isdir(os.path.join(CO, 'anticipation')), reason='no anticipation checkout')


def test_tokens():
    ops, V, C = A.anticipation(CO)
    assert A.tokens([(0.5, 12.0, 60)], CO) == [V.TIME_OFFSET + 50, V.DUR_OFFSET + C.MAX_DUR - 1, V.NOTE_OFFSET + 60]
    assert A.tokens([(1.0, .25, 64), (1.0, .25, 55)], CO)[2::3] == [V.NOTE_OFFSET + 55, V.NOTE_OFFSET + 64]   # lower first
    assert A.tokens([(0.0, 1.0, 60)], CO, control=True)[0] == V.ATIME_OFFSET


def test_given_notes_come_five_seconds_ahead():
    ops, V, C = A.anticipation(CO)
    asked = [(t * .5, .5, 60 + t % 5) for t in range(40)]; given = [(10.0, 1.0, 40)]
    seq, where = A.sequence(asked, given, CO)
    trip = [seq[i:i + 3] for i in range(0, len(seq), 3)]
    c = next(i for i, x in enumerate(trip) if x[2] >= V.CONTROL_OFFSET)
    before = [x[0] - V.TIME_OFFSET for x in trip[:c] if x[2] < V.REST]
    assert before[-1] >= 500 and all(x[0] - V.TIME_OFFSET >= 500 for x in trip[c + 1:] if x[2] < V.REST)   # after the event at 5 s
    assert [trip[k][2] - V.NOTE_OFFSET for k in where] == [m for _, _, m in sorted(asked, key=lambda n: (n[0], n[2]))]


def test_windows_place_each_note_once():
    ops, V, C = A.anticipation(CO)
    rnd = random.Random(1)
    asked = [(t * .25, .25, rnd.randint(55, 70)) for t in range(600)]; given = [(t * 1.0, 1.0, rnd.randint(36, 48)) for t in range(150)]
    seq, where = A.sequence(asked, given, CO)
    ws, pos = A.windows(seq, where, CO)
    assert len(ws) > 1 and all(len(w) <= 1024 for w in ws) and len(pos) == len(asked)
    order = sorted(asked, key=lambda n: (n[0], n[2]))
    assert [ws[w][p] - V.NOTE_OFFSET for w, p in pos] == [m for _, _, m in order]
    assert all(ops.min_time(w[1:], seconds=False) == 0 for w in ws)
    w, ps = A.window_ending(seq, where[-10:], CO)
    assert len(w) <= 1024 and [w[p] - V.NOTE_OFFSET for p in ps] == [m for _, _, m in order[-10:]]
