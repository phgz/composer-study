"""The research skill's package: only its listed files, reproducible, within Claude's upload limit. Run: python3 -m pytest -q tests"""
import hashlib, importlib.util, json, posixpath, re, subprocess, sys, tempfile, zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_skill', ROOT / 'tools' / 'package_skill.py')
builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)


def build(tmp, name='skill.zip'):
    out = Path(tmp) / name
    return out, builder.package(ROOT, out)


def test_the_package_holds_the_skill_and_its_two_documents_only():
    with tempfile.TemporaryDirectory() as tmp:
        out, report = build(tmp)
        again, _ = build(tmp, 'again.zip')
        assert out.read_bytes() == again.read_bytes()
        with zipfile.ZipFile(out) as z:
            names = set(z.namelist())
            expected = {f'{builder.SKILL}/{p}' for p in builder.SKILL_FILES}
            expected |= {f'{builder.SKILL}/references/repository/{p}' for p in builder.DOCUMENTS}
            expected.add(f'{builder.SKILL}/references/source.json')
            assert names == expected
            assert len(names) <= builder.MAX_FILES
            assert json.loads(z.read(f'{builder.SKILL}/references/source.json')) == report
            for item in report['files']:
                assert hashlib.sha256(z.read(item['archive'])).hexdigest() == item['sha256']


def test_relative_links_in_the_package_resolve_inside_it():
    with tempfile.TemporaryDirectory() as tmp:
        out, _ = build(tmp)
        with zipfile.ZipFile(out) as z:
            root = zipfile.Path(z); missing = []
            for name in z.namelist():
                if not name.endswith('.md'): continue
                for href in re.findall(r'\[[^\]\n]*\]\(([^)\s]+)\)', z.read(name).decode('utf-8')):
                    link = urlsplit(href)
                    if link.scheme or link.netloc or not link.path: continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(link.path)))
                    if not (root / target).exists(): missing.append(f'{name} -> {href}')
            assert missing == []


def test_a_package_over_the_upload_limit_is_refused_before_writing():
    limit = builder.MAX_FILES; builder.MAX_FILES = 3
    try:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'skill.zip'
            try:
                builder.package(ROOT, out); raised = False
            except ValueError:
                raised = True
            assert raised and not out.exists()
    finally:
        builder.MAX_FILES = limit


def test_an_existing_package_is_not_overwritten():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'skill.zip'; out.write_bytes(b'delivered')
        try:
            builder.package(ROOT, out); raised = False
        except FileExistsError:
            raised = True
        assert raised and out.read_bytes() == b'delivered'
