"""The periods table and its reading. Run: python3 -m pytest -q tests"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import periods as P


def w(composer, keys=(), label=''):
    return dict(composer=composer, keys=list(keys), label=label)


def test_numbers_place_a_work_and_the_exceptions_come_first():
    assert P.period_of(w('Ludwig van Beethoven', ['op 31/2']))[0] == 'early'
    assert P.period_of(w('Ludwig van Beethoven', ['op 81b']))[0] == 'early'          # the sextet of 1795, published late
    assert P.period_of(w('Ludwig van Beethoven', ['op 81a']))[0] == 'middle'
    assert P.period_of(w('Ludwig van Beethoven', ['op 103']))[0] == 'early'
    assert P.period_of(w('Ludwig van Beethoven', ['op 111']))[0] == 'late'
    assert P.period_of(w('Franz Joseph Haydn', ['Hob I:45']))[0] == 'Sturm und Drang'
    assert P.period_of(w('Franz Joseph Haydn', ['Hob I:94']))[0] == 'London and late'
    assert P.period_of(w('Franz Joseph Haydn', ['op 76/3', 'Hob III:77']))[0] == 'London and late'


def test_a_stated_year_comes_before_the_number():
    name, how = P.period_of(w('Ludwig van Beethoven', ['op 1/1']), year=1820)
    assert name == 'late' and '1820' in how


def test_titles_and_composers_of_one_period():
    assert P.period_of(w('Claudio Monteverdi', label='Il quarto libro de madrigali, no. 3: Sfogava con le stelle (DCML)'))[0] == 'seconda pratica'
    assert P.period_of(w('Erik Satie', label='Gymnopédie no. 1'))[0] == 'all'
    assert P.period_of(w('Franz Schubert', label='Ständchen'))[0] is None       # no number, no year: the unit falls back to the composer


def test_every_line_has_its_reason():
    for name, entry in P.table().items():
        assert entry.get('source'), name
        for p in entry['periods']:
            assert p.get('name') and p.get('why'), (name, p)
            if p.get('years'): assert p['years'][0] <= p['years'][1], (name, p)


def test_a_version_named_in_the_title():
    assert P.period_of(w('Franz Liszt', ['S 270'], 'sonetti di Petrarca, S.270b, Pace non trovo (OpenScore)'))[0] == 'late'
    assert P.period_of(w('Claudio Monteverdi', label='Beatus vir (SV 268) (Mutopia)'))[0] == 'Venice'
    assert P.period_of(w('Claudio Monteverdi', label='Dixit Dominus (SV 206) (Mutopia)'))[0] is None
