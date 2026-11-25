"""The flag tool's choice of NotaGen's prompt (study/flag_piece.py): the prompt under which NotaGen finds the piece least surprising,
both models averaged, single notes only; and its bits handed to the notes of the flag list they were matched to. Run:
python3 -m pytest -q tests"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import flag_piece as FP


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


def test_two_takes_differ_where_their_notes_do():
    before = {'gtr': [(110.8, .35, 68, 38), (111.13, .35, 68, 35)], 'ca': [(262.02, .37, 69, 76), (262.43, .32, 67, 71)],
              'vn2': [(196.14, 2.05, 73, 28), (200.0, 1.0, 69, 30)], 'pno': [(5.82, 1.6, 64, 40), (7.96, 1.6, 64, 40)]}
    after = {'gtr': [(110.8, .35, 66, 38), (111.13, .35, 66, 35)], 'ca': [(262.2, .37, 69, 76), (262.61, .32, 67, 71)],
             'vn2': [(196.14, 2.05, 71, 28), (200.0, 1.0, 69, 30)], 'pno': [(5.82, 1.6, 66, 40), (7.96, 1.6, 66, 40)]}
    spots = FP.changed(before, after)
    assert [round(s[0][0], 2) for s in spots] == [5.82, 110.8, 196.14, 262.02]      # 5.82 and 7.96 one spot; 200.0 unchanged
    assert {e[2] for e in spots[3]} == {'time'} and {e[2] for e in spots[1]} == {'pitch'}
    assert FP.describe(spots[1]) == 'gtr: G#4 → F#4 (2 notes)'
    assert FP.describe(spots[3]) == 'ca: A4, G4 0.18 s later'
    assert FP.changed(before, before) == []


def test_a_note_only_one_take_has_is_added_or_dropped():
    spots = FP.changed({'fl': [(1.0, .5, 72, 60)]}, {'fl': [(1.0, .5, 72, 60), (40.0, .5, 74, 60)], 'cl': [(41.0, 1, 60, 50)]})
    assert len(spots) == 1 and FP.describe(spots[0]) == 'fl: adds D5; cl: adds C4'


def test_section_names_as_the_timeline_shows_them():
    assert FP.short("03 concerto 1: the guitar alone, then the tune on the cor angla") == 'Concerto 1'
    assert FP.short('08 the last hymn: the tune loud by everyone') == 'Last hymn'
    assert FP.short('Beklemmt: F major, then D minor') == 'Beklemmt'
