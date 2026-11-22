"""The listener's ear and the lines it hears. Run: python3 -m pytest -q tests"""
import os, sys, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import ear as E, lines as L


def work(i, notes, composer='X', collection='c', final=0):
    return L.Work(f'w{i}', composer, collection, 'kern', f'W{i}', {'p': notes}, final, [], {})


def scale(n, start=60, step=0.5):
    up = [0, 2, 4, 5, 7, 9, 11, 12]; ms = [start + up[i % 8] + 12 * (i // 8) for i in range(n)]
    return [(i * step, step, m) for i, m in enumerate(ms)]


def test_a_note_heard_often_is_expected_and_a_leap_is_not():
    ltm = E.Long().learn([work(i, scale(40)) for i in range(20)], lambda w: 1.0)
    ic = [x[0] for x in E.listen(scale(24), 0, ltm)[1:]]
    assert np.mean(ic) < 1.0                                                  # the scale it learnt: well under a bit a note
    odd = scale(12) + [(6.0, 0.5, 90)]
    assert E.listen(odd, 0, ltm)[-1][0] > 6                                    # a leap of 18 semitones never heard: a jolt
    far = scale(12) + [(6.0, 0.5, 110)]
    assert E.listen(far, 0, ltm)[-1][0] == 12.0                                # past 20 semitones: 12 bits


def test_the_short_term_memory_learns_the_piece():
    rnd = random.Random(3)
    corpus = [work(i, [(t * 0.5, 0.5, 60 + rnd.randint(-7, 7)) for t in range(60)]) for i in range(10)]
    ltm = E.Long().learn(corpus, lambda w: 1.0)
    motif = [62, 65, 60, 67, 59]; notes = [(t * 0.5, 0.5, motif[t % 5]) for t in range(40)]
    with_stm = [x[0] for x in E.listen(notes, 0, ltm)[1:]]; without = [x[0] for x in E.listen(notes, 0, ltm, short=False)[1:]]
    assert np.mean(with_stm[-10:]) < 0.5 * np.mean(without[-10:])              # the fifth time round, the motif is expected


def test_weights_count_as_notes_and_a_heavier_work_teaches_more():
    a = work(1, [(t, 1.0, 60 + (t % 2) * 2) for t in range(40)])               # C D C D ...
    b = work(2, [(t, 1.0, 60 + (t % 2) * 4) for t in range(40)])               # C E C E ...
    probe = [(0.0, 1.0, 60), (1.0, 1.0, 62), (2.0, 1.0, 60), (3.0, 1.0, 62)]
    even = E.Long().learn([a, b], lambda w: 1.0); more_b = E.Long().learn([a, b], lambda w: 9.0 if w.id == 'w2' else 1.0)
    assert E.listen(probe, 0, more_b, short=False)[-1][0] > E.listen(probe, 0, even, short=False)[-1][0]
    t = even.tables['int']; assert abs(sum(t.orders[0]['N']) - 78) < 1e-6    # the counts sum to the intervals learnt (2 x 39)


def test_caps_hold_a_composer_to_a_tenth_and_a_collection_to_a_third():
    ids = [f'big{i}' for i in range(50)] + [f's{j}-{i}' for j in range(12) for i in range(2)]
    comp = {i: i.split('-')[0] if i.startswith('s') else 'Big' for i in ids}
    col = {i: 'one' if i.startswith('big') or i.startswith('s0') else f'col{i[1:].split("-")[0]}' for i in ids}
    w = L.capped({i: 1.0 for i in ids}, [(comp.get, 0.1), (col.get, 1 / 3)])
    tot = sum(w.values())
    assert sum(x for i, x in w.items() if comp[i] == 'Big') <= 0.1 * tot + 1e-9
    assert sum(x for i, x in w.items() if col[i] == 'one') <= tot / 3 + 1e-9
    assert abs(w['s5-0'] - w['s7-1']) < 1e-9                                  # the others share what is given up by their works


def test_counts_take_a_span_heard_again_once_and_copies_share_a_key():
    line = [(float(t), 1.0, 60 + t) for t in range(10)]
    assert [n[0] for n in L.once(line, [(4.0, 8.0)])] == [0.0, 1.0, 2.0, 3.0, 8.0, 9.0]
    a = L.Work('a', 'Józef Stefani', 'k', 'kern', 'Mazur (PL-Wn 123, kern)', {}, 0, [], {})
    b = L.Work('b', 'Józef Stefani', 'k', 'kern', 'Mazur (PL-Kk 9, kern)', {}, 0, [], {})
    assert L.label_key(a) == L.label_key(b)


def test_ioi_symbols_and_views_line_up():
    assert E.ioi_symbol(1.0, 1.0) == 6 and E.ioi_symbol(1.0, 2.0) == 8 and E.ioi_symbol(2.0, 1.0) == 4 and E.ioi_symbol(1.0, 100.0) == 12
    v = E.views([(0.0, 1, 60), (1.0, 1, 62), (3.0, 1, 59)], 0)
    assert list(v['int']) == [22, 17] and list(v['deg']) == [0, 2, 11] and list(v['ioi']) == [8]
    assert list(v['link']) == [22 * 12 + 2, 17 * 12 + 11]


def test_the_line_is_the_sounding_skyline():
    """the top note at each onset, less a note that begins under a higher note still sounding: an inner voice moving under a held
    melody note is not the line"""
    notes = [(0.0, 2.0, 72), (0.0, 1.0, 60), (1.0, 1.0, 62), (2.0, 1.0, 74), (2.0, 1.0, 55), (3.0, 1.0, 76)]
    assert L.skyline(notes) == [(0.0, 2.0, 72), (2.0, 1.0, 74), (3.0, 1.0, 76)]
    assert L.skyline([(0.0, 1.0, 72), (1.0, 1.0, 60)]) == [(0.0, 1.0, 72), (1.0, 1.0, 60)]       # the melody ended: the next is heard


def test_the_memories_are_joined_unweighted_by_default():
    a = np.array([0.7, 0.2, 0.1]); b = np.array([0.1, 0.2, 0.7])
    g = E.combine([a, b]); assert abs(g[0] - g[2]) < 1e-12                     # bias 0: neither is trusted more
    sure = np.array([0.98, 0.01, 0.01]); assert E.combine([sure, b], bias=1.0)[0] > E.combine([sure, b])[0]
