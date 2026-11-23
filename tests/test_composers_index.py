"""The composers' pages and their index. Run: python3 -m pytest -q tests"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import composers_index as I


def test_every_technique_says_what_it_works_on():
    assert I.problems(I.pages()) == []


def test_every_technique_has_its_recipe_and_its_place():
    import re
    for f in os.listdir(I.PAGES):
        if f in ('README.md', 'INDEX.md') or not f.endswith('.md'): continue
        text = open(os.path.join(I.PAGES, f), encoding='utf-8').read()
        a = text.index('## Techniques\n'); b = text.index('\n## ', a + 1)
        for block in re.split(r'(?m)^(?=\d+\. )', text[a:b])[1:]:
            n = block.split('.', 1)[0]
            assert len(re.findall(r'(?m)^ {3,4}\*How:\*', block)) == 1, (f, n)
            assert len(re.findall(r'(?m)^ {3,4}\*Where:\*', block)) == 1, (f, n)


def test_the_index_is_up_to_date():
    current = open(I.INDEX, encoding='utf-8').read()
    assert current == I.render(I.pages()), 'run python3 -m study.composers_index'
