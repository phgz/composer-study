"""Profiles of narrow units. Run: python3 -m pytest -q tests"""
import os, sys, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import lines as L, profiles as P


def work(i, composer, notes, collection='c'):
    line = [(t * 0.5, 0.5, m, 1 + t // 8, (t % 8) * 0.5) for t, m in enumerate(notes)]
    return L.Work(f'{composer}-{i}', composer, collection, 'kern', f'{composer} work {i}', {'p': line}, 0, [], {}, len(line), len(line) * 0.5)


def test_measures_of_a_line():
    w = work(0, 'X', [60, 62, 64, 65, 67, 67, 60, 62, 64, 72, 71, 69])
    m = P.measure(w)
    assert abs(m['steps'] - 8 / 11) < 1e-9 and abs(m['repeats'] - 1 / 11) < 1e-9 and abs(m['leaps'] - 2 / 11) < 1e-9
    assert m['even'] == 1.0 and m['long-short'] == 0.0 and m['density'] == 2.0
    assert m['leap answered'] == 1.0                                            # down a fifth, then up a step; up a minor sixth, then
                                                                                # down a half step: both answered


def test_a_unit_that_turns_stands_apart_and_its_figure_is_found_with_its_bars():
    """one composer's works all turn about a note (up a step, down a step, down a half step) where the others' run in scales"""
    rnd = random.Random(1); facts = {}; works = []
    for i in range(8):
        notes = []
        for _ in range(10): b = 60 + rnd.choice([0, 2, 4, 5]); notes += [b, b + 2, b, b - 1]
        works.append(work(i, 'Turner', notes))
    for c in range(6):
        for i in range(8):
            start = 55 + rnd.randint(0, 10); works.append(work(i, f'Other{c}', [start + (k % 12) for k in range(40)], collection=f'c{c}'))
    for w in works: facts[w.id] = dict(kind=['mazurka'], forces='keyboard', year=None, keys=[])
    prof = P.build(works, facts, log=None)
    p = next(v for u, v in prof.items() if u[0] == 'Turner')
    assert p['compared']['by'] == 'kind, forces, period' or p['compared']['by'] == 'kind' or p['compared']['by'] == 'kind, period'
    assert any(t['measure'] == 'repeats' or t['measure'] == 'rising' or t['measure'] == 'steps' for t in p['traits'])
    f = p['figures'][0]; assert f['moves'] == [2, -2, -1] or [2, -2, -1] in [x['moves'] for x in p['figures']]
    assert f['at'] and f['at'][0]['bar'] is not None and len(f['at'][0]['notes'].split()) == 4
    assert '### Turner' in P.markdown(p)


def test_the_comparison_falls_back_and_says_so():
    works = [work(i, 'Lone', [60, 62, 64, 65] * 5) for i in range(6)]
    facts = {w.id: dict(kind=['chorale'], forces='voices', year=None, keys=[]) for w in works}
    p = next(iter(P.build(works, facts, log=None).values()))
    assert p['compared']['by'] is None and p['traits'] == [] and p['figures'] == []
    assert 'too few works by others' in P.markdown(p)


def test_in_a_song_the_melody_is_the_voice():
    voice = [(t * 1.0, 1.0, 64 + (t % 3), 1, 0.0) for t in range(20)]; piano = [(t * 0.5, 0.5, 76 + (t % 5), 1, 0.0) for t in range(40)]
    w = L.Work('s', 'X', 'c', 'musicxml', 'Lied', {'P1': voice, 'P2': piano}, 0, [], {}, 60, 20.0, {'P1': 'Singstimme', 'P2': 'Klavier'})
    assert P.top_line(w, 'voice and keyboard') is voice and P.top_line(w, 'keyboard') is piano and P.top_line(w._replace(names=None), 'voice and keyboard') is piano


def test_kinds_are_named_in_the_plural_when_others_are_counted():
    assert [P.plural(k) for k in ('mazurka', 'mass', 'symphony', 'variations', 'march', 'waltz', 'string quartet')] == \
        ['mazurkas', 'masses', 'symphonies', 'variations', 'marches', 'waltzes', 'string quartets']
