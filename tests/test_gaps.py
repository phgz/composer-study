"""The gap lists (study/gaps.py): which techniques a Tried line in composer-blend names, in each way the lines name them, and that
the real pages and Tried lines are all read. Run: python3 -m pytest -q tests"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import gaps as G

BLEND = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'composer-blend')


def test_numbers_read_lists_ranges_and_and():
    assert G.numbers('1 to 6, 8 to 16, 20, 21, 26 to 29, 33 and 35') == {1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 21, 26, 27, 28, 29, 33, 35}
    assert G.numbers('1, 2, 3, 5, 6, 8, 9 and 10') == {1, 2, 3, 5, 6, 8, 9, 10}
    assert G.numbers('3') == {3}


def page(tmp, slug, name, n):
    os.makedirs(tmp / 'pages', exist_ok=True)
    body = '\n\n'.join(f'{i}. **Technique {i}.** What it is.\n   *Works on:* melody.\n   *Why:* it does a thing. [A] *(an analysis)*' for i in range(1, n + 1))
    (tmp / 'pages' / f'{slug}.md').write_text(f'# {name} (1800-1900)\n\n## Techniques\n\n{body}\n\n## What he does not do\n\n*In this.*\n\n- Leap.\n\n## Sources\n')


def tried(tmp, slug, lines):
    os.makedirs(tmp / 'blend' / 'reference' / 'composers', exist_ok=True)
    (tmp / 'blend' / 'reference' / 'composers' / f'{slug}.md').write_text('# X\n\n## Tried\n\n' + '\n'.join('- ' + l for l in lines) + '\n\n## On these recordings\n')


def test_each_way_a_tried_line_names_its_techniques(tmp_path):
    page(tmp_path, 'anna-x', 'Anna X', 12)
    tried(tmp_path, 'anna-x', [
        '24 November 2026, piece 70, *A* (`pieces/70_a/`, two colours with B): 1, 2 and 5, fused with B on a thing. Philip: 4.',
        '22 November 2026, piece 65, *B*, a blend with C. It took 3, 4. Philip: 4.75.',
        '22 November 2026, a one-minute sketch in plain sound (`pieces/s/`): techniques 6 and 7. Philip: fine.',
        '22 November 2026, piece 61, *C* (`pieces/61_c/`): all but 1 to 10. Philip: good.',
        '24 November 2026, piece 69, *D* (`pieces/69_d/`, a blend): 8 and 9; 10 in part (the rest). Philip: 3.5, "Tune 1 to 12".',
        'Earlier, from memory and not from this page: pieces 14 and 40.',
        '23 November 2026, piece 67, two colours. Its page names the techniques it took. Philip: 4.'])
    os.makedirs(tmp_path / 'blend' / 'pieces' / '67_e', exist_ok=True)
    (tmp_path / 'blend' / 'pieces' / '67_e' / 'README.md').write_text(
        '# E\n\n## What was taken, by page and number\n\n**Anna X** (two of twelve):\n- 3, changed: this.\n- 4 and 12: that.\n\n'
        '**Borodin** (one):\n- 9: no.\n\n## Other\n')
    pages = G.read_pages(str(tmp_path / 'pages'))
    got, unread = G.read_tried(str(tmp_path / 'blend'), pages)
    assert unread == []
    by = {p: ns for p, ns, _ in got['anna-x']}
    assert by == {'70': [1, 2, 5], '65': [3, 4], 'sketch 22 November 2026': [6, 7], '61': [11, 12], '69': [8, 9, 10], '67': [3, 4, 12]}
    assert pages['anna-x']['does_not'] == [('In this.', 'Leap.')]
    assert pages['anna-x']['techniques'][1]['why'].startswith('it does a thing') and pages['anna-x']['techniques'][1]['speaker'] == 'an analysis'


def test_the_real_pages_and_tried_lines_are_all_read():
    if not os.path.isdir(BLEND): return                                    # composer-blend is not beside this checkout
    pages = G.read_pages()
    got, unread = G.read_tried(BLEND, pages)
    assert unread == []
    assert all(t['dims'] for p in pages.values() for t in p['techniques'].values())
