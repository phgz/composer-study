"""The flag tool's choice of NotaGen's prompt (study/flag_piece.py): the prompt under which NotaGen finds the piece least surprising,
both models averaged, single notes only; and its bits handed to the notes of the flag list they were matched to. Run:
python3 -m pytest -q tests"""
import json, os, sys
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import flag_piece as FP


def test_explicit_written_notes_keep_their_tempo_map_and_origin():
    from types import SimpleNamespace
    mod = SimpleNamespace(EXPORT={'notes':'written', 'clock':'performed', 'unit':.5, 'origin':2},
                          performed=lambda b: b*.5 if b<=6 else 3+(b-6)*.75)
    clock = FP.notation_clock(mod)
    assert [clock(q) for q in (0,2,3)] == [1,3,4.5]


def test_written_notes_without_a_clock_are_not_given_invented_times():
    from types import SimpleNamespace
    with pytest.raises(SystemExit,match='clock'):
        FP.notation_clock(SimpleNamespace(EXPORT={'notes':'written'}))


def test_spelling_uses_key_positions_in_the_original_units(monkeypatch):
    from types import SimpleNamespace
    mod = SimpleNamespace(
        EXPORT={'origin': 2, 'unit': .5, 'end': 12, 'keys': [(2, 0), (8, 1)],
                'notes': 'written', 'clock': 'sec'},
        sec=lambda u: 1 + (u - 2) * .25,
    )
    export = SimpleNamespace(load=lambda _: mod, clock=lambda m, end: lambda t: (t - 1) / .25,
                             spell=lambda midi, fifths, minor: str(fifths))
    monkeypatch.setattr(FP, 'exporter', lambda _: export)
    spell = FP.speller('piece.py')
    assert spell(mod.sec(7), 65) == '0'
    assert spell(mod.sec(8), 65) == '1'



def test_explicit_notes_keep_bar_locations_and_key_spellings(monkeypatch):
    from types import SimpleNamespace
    mod = SimpleNamespace(EXPORT={'notes':'written', 'unit':1, 'end':9,
                                  'keys':[(0,2,'minor'),(6,5)]}, sec=lambda b:b*.5)
    measures = [SimpleNamespace(number=i+1, getOffsetBySite=lambda p, q=i*3:q) for i in range(3)]
    part = SimpleNamespace(getElementsByClass=lambda _:measures)
    exp = SimpleNamespace(load=lambda _:mod, build=lambda _:SimpleNamespace(parts=[part]),
                          clock=lambda m,end:lambda t:t*2,
                          spell=lambda pitch,key,minor:f'{pitch}:{key}:{minor}')
    monkeypatch.setattr(FP,'exporter',lambda _:exp)
    assert FP.places('explicit.py',[0,1.49,1.5,2.99,3,4.49]) == [1,1,2,2,3,3]
    spell = FP.speller('explicit.py')
    assert spell(2.99,63) == '63:2:True'
    assert spell(3,63) == '63:5:False'
    del mod.sec
    assert FP.places('explicit.py',[1.5]) == [None]


def write(folder, name, rows):
    with open(os.path.join(folder, name), 'w') as f:
        for r in rows: f.write(json.dumps(r) + '\n')


def test_the_least_surprising_prompt_is_chosen_and_its_bits_go_to_the_matched_notes(tmp_path):
    notes = [dict(voice='1.0', chord=False, flag=4), dict(voice='1.0', chord=True, flag=None), dict(voice='2.0', chord=False, flag=None)]
    json.dump(dict(notes=notes), open(tmp_path / 'flag_notagen_notes.json', 'w'))
    write(tmp_path, 'flag_notagen_x.jsonl', [dict(id='A', bits=[[3, 0], [0, 0], [3, 0]]), dict(id='B', bits=[[1, 0], [9, 9], [2, 0]])])
    write(tmp_path, 'flag_notagen_finetune.jsonl', [dict(id='A', bits=[[2, 1], [0, 0], [2, 1]]), dict(id='B', bits=[[1, 1], [9, 9], [1, 0]])])
    ears, heard, rank = FP.notagen_choice(str(tmp_path))
    assert ears == ['x', 'finetune'] and rank[0][1] == 'B'                 # the chord's bits (9) do not count against B
    assert heard == {'x': {4: 1}, 'finetune': {4: 2}}                     # only the matched note, under B


def test_no_notagen_scores_no_choice(tmp_path):
    assert FP.notagen_choice(str(tmp_path)) == ([], {}, [])


def test_scores_from_another_preparation_are_refused(tmp_path):
    import pytest
    json.dump(dict(notes=[dict(voice='1.0', chord=False, flag=0)] * 3), open(tmp_path / 'flag_notagen_notes.json', 'w'))
    write(tmp_path, 'flag_notagen_x.jsonl', [dict(id='A', bits=[[1, 0]] * 4)])
    with pytest.raises(SystemExit): FP.notagen_choice(str(tmp_path))


def test_each_ear_ranks_on_its_own_after_the_first_two_seconds():
    notes = [(0.5, .5, 60, 'a'), (3.0, .5, 62, 'a'), (4.0, .5, 64, 'a'), (5.0, .5, 65, 'a')]
    r = FP.own_ranks(notes, range(4), [9.0, 1.0, float('nan'), 2.0])
    assert r == {3: 1, 1: 2}                                         # the first note too early, the third not heard


CO = os.environ.get('ANTICIPATION', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                                 'jthickstun', 'anticipation'))
needs_amt = pytest.mark.skipif(not os.path.isdir(os.path.join(CO, 'anticipation')), reason='no anticipation checkout')


def two_parts(folder, change=None, name='notes_t.py'):
    """a notes module: part a in halves of a second from 0 to 12 s, part b each second on C3, and at 5 s on a's C4 too"""
    ev = [('a', i / 2, .5, 60 + 2 * (i % 2)) for i in range(25)] + [('b', float(i), 1.0, 48) for i in range(13)] + [('b', 5.0, 1.0, 60)]
    if change: ev = [change(r) for r in ev]
    path = os.path.join(folder, name); open(path, 'w').write(f'EV = {ev!r}\n'); return path


def scores(inputs, high):
    """fake bits for every note of each input: about 1 with a little spread, `high` {(input id, note time): bits} where given"""
    import random
    rnd = random.Random(1); out = []
    for inp, times in inputs:
        out.append(dict(id=inp, bits=[[high.get((inp, t), 1 + rnd.random() / 4), 0, 0, 1 + rnd.random() / 4, 0] for t in times]))
    return out


@needs_amt
def test_each_part_is_prepared_by_itself_a_doubled_note_in_both(tmp_path):
    import argparse
    src = two_parts(str(tmp_path))
    FP.prepare(argparse.Namespace(source=src, checkout=CO, o=str(tmp_path)))
    notes = json.load(open(tmp_path / 'flag_notes.json'))['notes']
    assert len(notes) == 25 + 13                                       # the doubled C4 heard once in the whole
    FP.alone(argparse.Namespace(source=src, checkout=CO, folder=str(tmp_path)))
    lines = {d['id']: d for d in map(json.loads, open(tmp_path / 'flag_amt_alone_inputs.jsonl'))}
    assert sorted(lines) == ['a', 'b'] and len(lines['a']['index']) == 25 and len(lines['b']['index']) == 14
    both = set(lines['a']['index']) & set(lines['b']['index'])
    assert [notes[i][:3:2] for i in both] == [[5.0, 60]]
    moved = two_parts(str(tmp_path), lambda r: (r[0], r[1], r[2], 61) if r[1] == 6.0 and r[0] == 'a' else r, 'notes_u.py')
    with pytest.raises(SystemExit): FP.alone(argparse.Namespace(source=moved, checkout=CO, folder=str(tmp_path)))


@needs_amt
def test_a_place_surprising_only_with_the_rest_and_one_surprising_alone_too(tmp_path):
    import argparse
    src = two_parts(str(tmp_path))
    FP.prepare(argparse.Namespace(source=src, checkout=CO, o=str(tmp_path)))
    FP.alone(argparse.Namespace(source=src, checkout=CO, folder=str(tmp_path)))
    notes = json.load(open(tmp_path / 'flag_notes.json'))['notes']
    whole = [('piece', [n[0] for n in notes])]
    write(tmp_path, 'flag_amt_large.jsonl', scores(whole, {('piece', 6.0): 9.0, ('piece', 8.0): 9.0}))
    parts = [(d['id'], [notes[i][0] for i in d['index']]) for d in map(json.loads, open(tmp_path / 'flag_amt_alone_inputs.jsonl'))]
    write(tmp_path, 'flag_amt_alone_large.jsonl', scores(parts, {('a', 8.0): 9.0, ('b', 8.0): 9.0}))
    FP.together(argparse.Namespace(folder=str(tmp_path), top=2, odd=None))
    rows = [l.split(' | ') for l in open(tmp_path / 'TOGETHER.md') if l.startswith('| ') and 'note' in l]
    where = {r[1]: r[-1].strip(' |\n') for r in rows}
    assert where['0:06.0'] == 'with the rest' and where['0:08.0'] == 'alone too'


def test_the_first_note_of_each_onset():
    w = [[0, 10, 20, 11000, 30, 20, 11001, 30, 20, 11002]]          # three notes, the second and third at one onset
    assert FP.first_of_onset(w, [(0, 3), (0, 6), (0, 9)]) == [0, 1, 1]


@needs_amt
def test_places_above_a_fixed_bar_on_another_scoring_s_scale(tmp_path):
    import argparse
    ref, new = tmp_path / 'ref', tmp_path / 'new'
    for f in (ref, new):
        f.mkdir(); FP.prepare(argparse.Namespace(source=two_parts(str(tmp_path)), checkout=CO, o=str(f)))
    notes = json.load(open(ref / 'flag_notes.json'))['notes']
    whole = [('piece', [n[0] for n in notes])]
    write(ref, 'flag_amt_large.jsonl', scores(whole, {('piece', 6.0): 9.0}))
    row = scores(whole, {('piece', 6.0): 2.0})[0]                         # the place made less surprising than the bar
    row['expect'] = [[[[62, .5], [60, .3]], None] for _ in notes]
    write(new, 'flag_amt_large.jsonl', [row])
    FP.over(argparse.Namespace(folder=str(ref), bar=4.0, scale_from=None))
    assert '| 0:06.0 | note |' in open(ref / 'OVER-4.md').read()
    FP.over(argparse.Namespace(folder=str(new), bar=4.0, scale_from=str(ref)))
    assert '0 places' in open(new / 'OVER-4.md').read()
    FP.over(argparse.Namespace(folder=str(new), bar=-9.0, scale_from=str(ref)))
    assert 'D4 50%, C4 30%' in open(new / 'OVER--9.md').read()


@needs_amt
def test_flat_stretches_are_the_gaps_between_events_above_the_bar(tmp_path):
    import argparse
    ref, f = tmp_path / 'ref', tmp_path / 'f'
    for x in (ref, f): x.mkdir(); FP.prepare(argparse.Namespace(source=two_parts(str(tmp_path)), checkout=CO, o=str(x)))
    whole = [('piece', [n[0] for n in json.load(open(f / 'flag_notes.json'))['notes']])]
    write(ref, 'flag_amt_large.jsonl', scores(whole, {}))                # the scale: nothing stands out
    write(f, 'flag_amt_large.jsonl', scores(whole, {('piece', 4.0): 9.0, ('piece', 5.0): 9.0}))
    r = FP.flat_measures(str(f), str(ref), bar=3.0, gap=3.0)
    assert r['events'] == 2                                          # 4 s and 5 s; the notes run from 0 to 12 s
    assert [(round(a, 1), round(b, 1)) for a, b in r['stretches']] == [(5.0, 12.0)]   # 2 s to 4 s is under the gap
    assert abs(r['share'] - 7 / 10) < 1e-9 and r['longest'] == 7.0
    assert FP.pairs_ordered({'x': .6, 'y': .2, 'z': .6}, ['x'], ['y', 'z']) == 1.5


@needs_amt
def test_the_flags_are_written_for_the_walk_page_as_it_shows_them(tmp_path):
    """the page moved to phgz/listening-page (28 November 2026): flag_piece writes its flags.json"""
    import argparse
    src = two_parts(str(tmp_path))
    FP.prepare(argparse.Namespace(source=src, checkout=CO, o=str(tmp_path)))
    notes = json.load(open(tmp_path / 'flag_notes.json'))['notes']
    write(tmp_path, 'flag_amt_large.jsonl', scores([('piece', [n[0] for n in notes])], {('piece', 6.0): 9.0, ('piece', 8.0): 9.0}))
    out = tmp_path / 'flags.json'
    FP.layer(argparse.Namespace(folder=str(tmp_path), module=src, o=str(out), top=2))
    d = json.load(open(out))
    assert d['schema'] == 1 and d['ears'] == ['large'] and d['earNames']['large'] == 'AMT Large' and d['top'] == 2
    notes_ = [r for r in d['rows'] if r['kind'] == 'note']
    assert [r['t'] for r in notes_] == [6.0, 8.0] and sorted(r['rank'] for r in notes_) == [1, 2]
    assert set(d['rows'][0]) == {'t', 'bar', 'kind', 'rank', 'part', 'pitch', 'passage', 'ears'}
    assert [r['t'] for r in d['rows']] == sorted(r['t'] for r in d['rows']) and d['foot'].startswith(f"{len(d['rows'])} places")
