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
