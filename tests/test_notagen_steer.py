"""study/notagen_steer.py: the steering keeps each state's length and moves it toward the vector; the test reads the split."""
import json
import pytest

from study import notagen_steer as T


def test_steering_keeps_the_length_and_turns_toward_the_vector():
    torch = pytest.importorskip('torch')
    h = torch.tensor([[3.0, 0.0], [0.0, 2.0]]); v = torch.tensor([0.0, 1.0])
    s = T.steer(h, v, .5)
    assert torch.allclose(s.norm(dim=-1), h.norm(dim=-1))
    cos = lambda a, b: float(a @ b / (a.norm() * b.norm()))
    assert cos(s[0], v) > cos(h[0], v) and torch.allclose(s[1], h[1])        # the second already points along it
    assert T.steer(h, v, 0) is h


def test_the_test_counts_the_held_out_and_the_control(tmp_path, capsys):
    split = dict(strozzi_vector=['v'], strozzi_held_out=[f's{i}' for i in range(8)], caccini_control=['c0', 'c1'])
    rows = [dict(id=f's{i}', bits={'0': 2.0, '0.3': 1.9 if i < 6 else 2.1}) for i in range(8)]
    rows += [dict(id='c0', bits={'0': 2.0, '0.3': 1.99}), dict(id='c1', bits={'0': 2.0, '0.3': 2.0})]
    (tmp_path / 'split.json').write_text(json.dumps(split)); (tmp_path / 's.jsonl').write_text('\n'.join(map(json.dumps, rows)))
    T.test(type('A', (), dict(scores=str(tmp_path / 's.jsonl'), split=str(tmp_path / 'split.json')))())
    out = capsys.readouterr().out
    assert '6 of 8 cheaper' in out and 'Passes' in out
