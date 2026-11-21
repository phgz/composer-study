"""The period of a work, by the table data/periods.json: the first period whose years hold the year a source states for the work
(score-reader's facts), else whose catalogue numbers or label hold it. None where no line holds it: the work's unit then falls back
to the composer. Every answer says how it was found."""
import json, os, re

TABLE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'periods.json')
SYSTEMS = ('op', 'K', 'D', 'BWV', 'S', 'Sz', 'Hob', 'Wq', 'HWV', 'RV', 'L', 'M')


def table(path=TABLE):
    with open(path, encoding='utf-8') as f: return json.load(f)['composers']


def _num(s):
    """'76/3' -> 76, '81b' -> (81, 'b'), 'I:45' -> ('I', 45)"""
    if ':' in s:
        g, n = s.split(':', 1); m = re.match(r'\d+', n); return (g, int(m.group())) if m else None
    m = re.match(r'(\d+)([a-z]?)', s)
    return (int(m.group(1)), m.group(2)) if m else None


def _holds(spec, key):
    """whether a period's numbers (ranges [a, b], numbers, '81b', 'I:45', ['I:82', 'I:92']) hold a work's number"""
    n = _num(key)
    if n is None: return False
    for x in spec:
        if isinstance(x, list):
            a, b = (_num(str(v)) for v in x)
            if isinstance(n[0], str):
                if a and b and a[0] == b[0] == n[0] and a[1] <= n[1] <= b[1]: return True
            elif a[0] <= n[0] <= b[0]: return True
        elif isinstance(x, str) and not x[0].isdigit():                    # 'I:45'
            if _num(x) == n: return True
        elif isinstance(x, str):                                           # '81b': exactly that number and letter
            if _num(x) == n: return True
        elif not isinstance(n[0], str) and n[0] == x and not n[1]: return True
    return False


def period_of(work, composers=None, year=None):
    """(period name, how) or (None, why not). `work` is a catalogue entry (its composer, keys, label); `year` the first year a
    source states for it (score-reader facts), if any."""
    composers = composers or table()
    entry = composers.get(work['composer'])
    if not entry: return None, 'the composer is not in the periods table'
    ps = entry['periods']
    if len(ps) == 1 and set(ps[0]) <= {'name', 'why'}: return ps[0]['name'], 'the composer has one period'
    if year is not None:
        for p in ps:
            if p.get('years') and p['years'][0] <= year <= p['years'][1]: return p['name'], f'its year, {year}'
    keys = work.get('keys') or []
    for p in ps:
        for system in SYSTEMS:
            if system in p:
                for k in keys:
                    if k.startswith(system + ' ') and _holds(p[system], k[len(system) + 1:]):
                        return p['name'], f'its number, {k}'
        if p.get('label') and re.search(p['label'], work.get('label', '')): return p['name'], 'its title'
    return None, 'no year stated, and no number or title the table places'
