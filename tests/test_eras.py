"""The shared periods. Run: python3 -m pytest -q tests"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import eras as E, periods as P


def test_every_composer_has_one_of_the_sheets_periods_and_its_reason():
    t = E.table()
    for name, e in t.items():
        assert e['era'] in E.ERAS and e['why'], name
    assert set(t) == set(P.table())                                       # the same composers as the periods table


def test_the_sheet_first_then_the_year_of_birth():
    assert E.era_of('Claudio Monteverdi') == ('Before 1600', "the sheet's period")
    assert E.era_of('Gustav Mahler')[0] == 'Romantic'                    # the sheet's, though born in 1860
    assert E.era_of('Muzio Clementi') == ('Classical', 'born 1752')
    assert E.era_of('Peter Warlock') == ('1890 to 1950', 'born 1894')
    assert E.era_of('Pierre de La Rue')[0] == 'Before 1600'
    assert E.era_of('Mr. Powlwheel')[0] == 'Baroque'                      # known only by Playford's book of 1685
    assert E.era_of('Nobody') == (None, 'not in data/eras.json')


def test_the_polish_scores_by_the_years_their_records_give():
    """catalogue version 22: a birth year or one about it; a composer known only as active, born about 30 years before; one known
    only by his death, about 50 years before it; one the collection gives no years is in neither table"""
    assert E.era_of('Stanisław Moniuszko') == ('Romantic', 'born 1819')
    assert E.era_of('Grzegorz Gerwazy Gorczycki') == ('Baroque', 'born about 1666')
    assert E.era_of('Wacław Raszek')[0] == 'Romantic' and E.era_of('Wacław Raszek')[1].startswith('active in 1848 (born about 1818')
    assert E.era_of('Marcin Mielczewski')[0] == 'Baroque'
    assert E.era_of('Karol Szymanowski') == ('1890 to 1950', "the sheet's period")
    assert E.era_of('Bauer')[0] is None and 'Bauer' not in P.table()


def test_a_composer_joined_in_score_reader_has_one_line():
    """catalogue version 23: the Polish Scores' Vanhal and Bortnjanskij are Mutopia's Wanhal and Bortniansky, named so in score-reader"""
    assert E.era_of('Johann Baptist Wanhal') == ('Classical', 'born 1739') and E.era_of('Johann Baptist Vanhal')[0] is None
    assert E.era_of('Dmitry Bortniansky') == ('Classical', 'born 1751') and 'Dmitrij Stepanovič Bortnjanskij' not in P.table()
