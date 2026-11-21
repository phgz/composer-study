"""Each composer's shared period, by the table data/eras.json: the level a narrow unit falls back to after the composer, and where
the cap of a tenth is counted (TRAINING.md, section 4). Every answer says how it was found."""
import json, os

TABLE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'eras.json')
ERAS = ('Before 1600', 'Baroque', 'Classical', 'Romantic', '1890 to 1950')


def table(path=TABLE):
    with open(path, encoding='utf-8') as f: return json.load(f)['composers']


def era_of(composer, eras=None):
    """(era, why), or (None, why) for a composer the table does not hold"""
    e = (eras or table()).get(composer)
    return (e['era'], e['why']) if e else (None, 'not in data/eras.json')
