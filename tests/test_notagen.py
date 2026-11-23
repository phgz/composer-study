"""NotaGen's notation, read and cut as NotaGen does. Run: python3 -m pytest -q tests"""
import os, sys
from fractions import Fraction as F
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import notagen as G

pytest.importorskip('abctoolkit')


def test_split_bars_as_notagen():
    line = '[r:0/3][V:1]c2 d2|[V:2]E4|\n'
    assert G.split_bars(line) == ['[r:0/3][V:1]c2 d2', '|[V:2]E4|\n']
    assert ''.join(G.split_bars('[r:1/2][V:1]c4|:[V:2]A4:|\n')) == '[r:1/2][V:1]c4|:[V:2]A4:|\n'


def test_patches_end_each_piece():
    pts, pieces = G.line_patches('[r:0/0][V:1]' + 'c' * 20 + '|[V:2]E|\n')     # 32 characters: two patches, no end mark
    assert pts[:2] == ['[r:0/0][V:1]cccc', 'c' * 16] and pts[2] == '|[V:2]E|\n' + chr(G.EOS) and pieces == [(0, 0), (2, 32)]
    pts, pieces = G.line_patches('[r:0/0][V:1]' + 'c' * 21 + '|[V:2]E|\n')     # 33: the third patch ends with the mark
    assert pts[2] == 'c' + chr(G.EOS) and pieces == [(0, 0), (3, 33)] and G.place(pieces, 34) == (3, 1)


def test_bar_accidentals_ties_tuplets_chords():
    v = G.Voice(G.key_signature('G'), F(1, 2), False)                                 # L:1/8, one sharp
    ns, d = v.bar('f2 =f2 f2 (3gab c\'2- ')
    assert [n[3] for n in ns] == [78, 77, 77, 79, 81, 83, 84] and d == F(5)              # the natural holds to the bar's end
    assert [n[2] for n in ns][3:6] == [F(3), F(10, 3), F(11, 3)]
    ns, _ = v.bar('c\'2 [CEG]2 z4')
    assert ns[0][4] and not ns[1][4] and ns[1][5] and ns[1][3] == 67                    # tied from the bar before; a chord's top


def test_octave_clef_sounds_below():
    assert G.sounding('treble-8 nm="Tenor"') == -12 and G.sounding('bass') == 0 and G.sounding('nm="x"') is None
    v = G.Voice({}, F(1, 2), False, G.sounding('treble-8'))
    assert [n[3] for n in v.bar('G2 c2')[0]] == [55, 60]


def test_windows_cover_and_overlap():
    ws = G.windows(10, [100] * 30, need=30)
    assert ws[0] == (0, 10, 0) and all(s < done for s, e, done in ws[1:]) and ws[-1][1] == 30
    assert all(10 + 100 * (e - s) + (1 if e == 30 else 0) <= 1024 for s, e, _ in ws)


def test_align_follows_order_not_time():
    abc = {'1.0': [(0, 0, 0, t, m, False) for t, m in enumerate([60, 62, 64, 65, 67])]}
    line = [(t + 9.0, 1, m) for t, m in enumerate([60, 62, 64, 65, 67])]
    v, (p, idx) = next(iter(G.align(abc, {'t1': line, 't2': [(0, 1, 40)] * 5}).items()))
    assert p == 't1' and idx == {i: i for i in range(5)}
