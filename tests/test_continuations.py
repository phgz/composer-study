"""Continuations. Run: python3 -m pytest -q tests"""
import os, sys, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import lines as L, ear as E, continuations as C


def work(i, notes, composer='X', lines=None):
    line = [(t * 0.5, 0.5, m, 1 + t // 8, (t % 8) * 0.5) for t, m in enumerate(notes)]
    return L.Work(f'{composer}-{i}', composer, 'c', 'kern', f'{composer} work {i}', lines or {'p': line}, 0, [], {}, len(line), len(line) * 0.5)


def corpus(n=12, seed=3):
    rnd = random.Random(seed); out = []
    for i in range(n):
        notes = [60]
        for _ in range(60): notes.append(max(48, min(84, notes[-1] + rnd.choice([-2, -1, 1, 2, 2, -3, 4]))))
        out.append(work(i, notes))
    return out


def test_one_level_hears_a_line_as_the_ear_does():
    ws = corpus(); ltm = E.Long().learn(ws, lambda w: 1.0)
    line = [(t * 0.5 + (0.25 if t % 3 == 0 else 0), 0.5, 60 + (t * 5) % 12) for t in range(30)]
    ear = E.listen(line, 0, ltm)
    mine = C.Model([('all', ltm, None)], vertical=False).hear(line, 0)
    for (bp, br), x in zip(mine, ear[2:]):
        assert abs(bp - x[0]) < 1e-9 and abs(br - x[1]) < 1e-9


def test_the_lowest_other_note_sounding_at_each_onset():
    line = [(0, 1, 72), (1, 1, 74), (2, 1, 76)]
    bass = [(0, 2, 48), (2, 1, 50)]; mid = [(0.5, 2, 45)]
    assert C.under(line, [bass, mid]) == [48, 45, 45]
    assert C.under(line, []) == [None, None, None]


def test_the_vertical_view_learns_what_sounds_over_the_bass():
    bass = [(t * 1.0, 1.0, 48 + (7 if t % 2 else 0), 1, 0.0) for t in range(16)]
    top = [(t * 1.0, 1.0, (64 if t % 2 == 0 else 71), 1, 0.0) for t in range(16)]     # a third over C, a third over G
    w = L.Work('v', 'X', 'c', 'kern', 'v', {'b': bass, 't': top}, 0, [], {}, 32, 16.0)
    v = C.Vertical().learn([w], lambda w: 1.0)
    assert v.dist(0).argmax() == 4 and v.dist(7).argmax() == 4                         # over the C, an E; over the G, a B
    assert v.dist(0)[C.BELOW] > v.dist(0)[1]                                           # the bass line itself is below the others
    assert v.dist(0, 0).argmax() == 4 and v.dist(4, 4 * 12).argmax() == C.BELOW         # order 2: over C alone, E; under E alone, below
    assert C.around([(0, 1, 60)], [[(0, 1, 48)], [(0, 1, 72)]]) == [(48, 72)]


def test_a_sample_keeps_its_range_its_length_and_the_lines_it_must_not_cross():
    ws = corpus(); lv = C.level(ws)
    m = C.Model([('all',) + lv])
    ctx = [(0, 0.5, 64), (0.5, 0.5, 65), (1.0, 0.5, 67), (1.5, 0.5, 65)]
    top = [(2.0, 8.0, 70)]; bass = [(2.0, 8.0, 55)]
    rnd = random.Random(1)
    for _ in range(20):
        notes, bits = C.sample(m, ctx, 0, 6.0, others=[top, bass], below=[top], above=[bass], rnd=rnd, durations=(0.5, 1.0))
        assert notes and all(55 < n[2] < 70 for n in notes) and abs(notes[-1][0] + notes[-1][1] - 8.0) < 1e-9
        assert len(bits) == len(notes) and all(b > 0 for b in bits)


def test_proposals_fall_in_the_band_and_leave_out_quotes():
    ws = corpus(); lv = [('all',) + C.level(ws)]
    ctx = [(0, 0.5, 64), (0.5, 0.5, 65), (1.0, 0.5, 67), (1.5, 0.5, 65)]
    got, info = C.propose(lv, ctx, 0, 4.0, n=60, keep=4, band=(1.0, 6.0), quotes=lambda ns: [], durations=(0.5,))
    assert got and all(1.0 <= b <= 6.0 for _, b, _ in got) and info['sampled'] == 60 and info['quoting'] == 0
    for notes, b, _ in got: assert abs(C.surprise(lv, ctx, notes, 0) - b) < 1e-9
    none, info = C.propose(lv, ctx, 0, 4.0, n=20, keep=4, band=(1.0, 6.0), quotes=lambda ns: ['a quote'], durations=(0.5,))
    assert none == [] and info['quoting'] == info['in_band']


def test_the_band_is_the_units_own_music_scored_as_proposals_are():
    ws = corpus(16); lv = [('all',) + C.level(ws[:12])]
    (lo, hi), vals = C.band(lv, ws[12:], length=6.0, step=10)
    assert vals and lo <= np.median(vals) <= hi


def test_no_parallel_fifths_or_octaves_with_a_line_that_moves():
    bass = [(0, 1, 48), (1, 1, 50)]                                                       # C then D
    assert C.parallels(55, [bass], 0, 1) == {9}                                           # G over C: not A over D
    assert C.parallels(52, [bass], 0, 1) == set()                                         # E over C: a third, free
    assert C.parallels(55, [[(0, 2, 48)]], 0, 1) == set()                                 # the bass holds: no parallel


def test_a_continuation_quotes_the_unit_at_eight_intervals():
    import pytest
    sr = os.environ.get('SCORE_READER', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'score-reader'))
    if not os.path.isdir(os.path.join(sr, 'score_reader')): pytest.skip('no score-reader checkout beside this one (SCORE_READER)')
    ws = corpus(4); q = C.quotes_against(ws, sr)
    line = [n[:3] for n in ws[0].lines['p'][10:22]]
    assert q(line) and not q(line[:8])                                                    # 11 intervals of a work; 7 are not a quote
