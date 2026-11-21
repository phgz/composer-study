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
