"""Sheet music by MuseScore (study/sheet.py): the plumbing, with a stand-in for MuseScore that writes what it would. Run:
python3 -m pytest -q tests"""
import os, stat, sys
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import sheet as S

FAKE = """#!/bin/sh
# a stand-in for MuseScore: -o TARGET XML; a PNG target becomes two numbered pages, as MuseScore writes them
while [ $# -gt 0 ]; do case "$1" in -o) T="$2"; shift 2;; -r) shift 2;; *) X="$1"; shift;; esac; done
[ -f "$X" ] || exit 3
case "$T" in *.png) B="${T%.png}"; echo p1 > "$B-1.png"; echo p2 > "$B-2.png"; echo p10 > "$B-10.png";; *) echo pdf > "$T";; esac
"""


def fake(tmp_path, name='mscore'):
    p = tmp_path / 'bin' / name; p.parent.mkdir(exist_ok=True); p.write_text(FAKE)
    p.chmod(p.stat().st_mode | stat.S_IXUSR); return str(p)


def test_command_asks_resolution_for_images_only():
    assert S.command('ms', 'a.xml', 'a.png', 150) == ['ms', '-r', '150', '-o', 'a.png', 'a.xml']
    assert S.command('ms', 'a.xml', 'a.pdf', 150) == ['ms', '-o', 'a.pdf', 'a.xml']


def test_find_named_and_on_path(tmp_path, monkeypatch):
    exe = fake(tmp_path)
    assert S.find(exe) == exe and S.find(str(tmp_path / 'none')) is None
    monkeypatch.setenv('PATH', str(tmp_path / 'bin'))
    assert S.find() == exe


def test_draw_pages_in_order_and_pdf(tmp_path):
    exe = fake(tmp_path); xml = tmp_path / 'tune.xml'; xml.write_text('<score-partwise/>')
    got = S.draw(str(xml), mscore=exe)
    assert [os.path.basename(p) for p in got] == ['tune-1.png', 'tune-2.png', 'tune-10.png']
    assert S.draw(str(xml), str(tmp_path / 'out' ), pdf=True, mscore=exe) == [str(tmp_path / 'out.pdf')]


def test_draw_says_when_nothing_was_written(tmp_path):
    exe = fake(tmp_path)
    with pytest.raises(RuntimeError): S.draw(str(tmp_path / 'missing.xml'), mscore=exe)
    with pytest.raises(FileNotFoundError): S.draw(str(tmp_path / 'x.xml'), mscore=str(tmp_path / 'nope'))
