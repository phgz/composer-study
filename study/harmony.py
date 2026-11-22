"""The harmony of a unit, from the labels analysts wrote: a DCML corpus's (reviewed musicologists' labels, with cadences and phrases)
or When in Rome's (an analyst's Roman numerals, held against the notes by score-reader; no cadences). Nothing here is worked out
from the notes alone: a work with no labels has no harmony in its profile.

What is measured, each labelled work weighing one:
  chords a bar         how often the harmony changes: labelled chords a bar (consecutive labels of one chord counted once)
  tonic and dominant   the share of chords on I or V of the key they stand in (i and v in a minor key; not applied)
  sevenths             the share of seventh chords
  diminished sevenths  the share of fully diminished sevenths
  applied chords       the share of chords applied to another degree (V/V, viio7/ii)
  augmented sixths     the share of Italian, French and German sixths
  Neapolitan           the share of chords on the flattened second degree
  mixture              the share of chords borrowed from the other mode: in a major key iv, bIII, bVI, bVII and a diminished ii;
                       in a minor key the major tonic (the Neapolitan apart; DCML's numerals in minor stand on the natural minor,
                       so #vii and #vi, the leading-tone chords, are not borrowed)
  inversions           the share of chords over a bass that is not their root
  keys a 10 bars       how often the key changes (a label in another local key than the one before)
  away from home       the share of chords in a key other than the movement's own
  cadences a 10 bars   DCML's works only (When in Rome marks none); and of them the shares perfect, half, and deceptive or evaded
  changes              DCML's works only: the share of chords labelled with notes in place of theirs or added (V(4), vi(2):
                       suspensions, retardations, appoggiaturas the analysts heard as part of the harmony)
  non-chord tones      the share of the melody's notes that are not in the chord sounding at their onset (the chord's own
                       notes, from its root and kind: a note DCML writes into the label in parentheses is outside it)
  struck dissonance    of those, the share struck with the chord (an appoggiatura, an accented passing note), against those between
  resolved by step     of those, the share followed by a step to a note of the chord then sounding
  suspensions          the share of the melody's notes held into a chord they are not in, then falling a step to one of its notes
                       (a tied note is one note in the readings, so a suspension is held, not struck again)
Progressions: the chords as tokens in the key they stand in (V7, ii6, viio7/V, Ger, I64). One chord held while its seventh
enters or its bass moves (V then V7, I then I6) is one chord, written as the seventh if it has one; DCML's cadential six-four,
V(64), is written I64, as When in Rome writes it. The three-chord progressions a unit uses far more than the works it is set
against, with the bars where they stand.

The two analysts differ in places, so some measures are only compared within one analyst's labels (BY_ANALYST): where one
writes a change of key the other may write applied chords. Others depend on the forces (BY_FORCES: a chorale's melody against
a keyboard suite's), so they are compared only against works for the same forces."""
import bisect, collections, re
import numpy as np

SEVENTHS = {'Mm7', 'mm7', 'MM7', 'mM7', 'o7', '%7', '+7', '+M7'}
AUG6 = {'Ger', 'It', 'Fr'}
PC = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)
SUFFIX = {'M': '', 'm': '', 'o': 'o', '+': '+', 'Mm7': '7', 'mm7': '7', 'MM7': 'M7', 'mM7': 'mM7', 'o7': 'o7', '%7': 'ø7', '+7': '+7', '+M7': '+M7'}
FIG3 = {0: '', 1: '6', 2: '64'}
FIG7 = {0: '', 1: '65', 2: '43', 3: '42'}


def pc(name):
    """a note's name ('F#', 'Eb', 'Bbb') as a pitch class"""
    if not name: return None
    p = PC.get(name[0].upper())
    if p is None: return None
    return (p + name[1:].count('#') - name[1:].count('b') + 2 * name[1:].count('x')) % 12


def tones(label):
    """the pitch classes the label gives its chord, with any notes it names in parentheses (DCML's changes: V(4), vi(2))"""
    return {pc(t) for t in (label.get('tones') or '').split()} - {None}


SHAPES = {'M': (0, 4, 7), 'm': (0, 3, 7), 'o': (0, 3, 6), '+': (0, 4, 8), 'Mm7': (0, 4, 7, 10), 'mm7': (0, 3, 7, 10), 'MM7': (0, 4, 7, 11),
          'mM7': (0, 3, 7, 11), 'o7': (0, 3, 6, 9), '%7': (0, 3, 6, 10), '+7': (0, 4, 8, 10), '+M7': (0, 4, 8, 11)}


def chord_tones(label):
    """the chord's own pitch classes, from its root and kind: a suspension DCML writes into the label (V(4)) is not one of them,
    so the two corpora's notes outside the chord are counted alike"""
    r = pc(label.get('root')); sh = SHAPES.get(label.get('type'))
    if r is None or sh is None: return tones(label)                             # the augmented sixths: as labelled
    return {(r + i) % 12 for i in sh}


def minor(key):
    """whether a local key (a numeral against the movement's key: 'I', 'vi', 'bIII') is minor"""
    k = (key or 'I').lstrip('b#'); return k[:1].islower()


def borrowed(h):
    """whether a chord is borrowed from the other mode of the key it stands in"""
    if h['relativeroot']: return False
    n, t = h['numeral'], h['type']
    if minor(h['localkey']): return n == 'I' and t in ('M', 'Mm7')
    return n in ('iv', 'bIII', 'bVI', 'bVII') or (n == 'ii' and t in ('o', '%7', 'o7'))


def source(work):
    """who labelled the work: 'DCML' or 'When in Rome'"""
    return 'DCML' if (work.harmony or [{}])[0].get('by') == 'DCML' else 'When in Rome'


BY_ANALYST = {'keys a 10 bars', 'away from home', 'applied chords'}
BY_FORCES = {'chords a bar', 'non-chord tones', 'struck dissonance', 'resolved by step', 'suspensions'}


def chords(work):
    """the work's labels that name a chord, consecutive repeats of one chord in one key merged"""
    out = []
    for h in work.harmony or []:
        if not h.get('numeral') or not h.get('type') or h['numeral'].startswith('@'): continue
        key = (h['localkey'], h['numeral'], h['relativeroot'], h['type'], h['bass'], h.get('chord'))           # V(64) then V: two
        if out and out[-1][0] == key: continue
        out.append((key, h))
    return [h for _, h in out]


def token(h):
    """a chord as a token in the key it stands in: its numeral, its kind, its inversion, what it is applied to"""
    t = h['type']
    if t in AUG6: s = t
    else:
        suf, fig = SUFFIX.get(t, t), ''
        r, b = pc(h['root']), pc(h['bass'])
        if r is not None and b is not None and r != b:
            iv = (b - r) % 12; k = 1 if iv in (3, 4) else 2 if iv in (6, 7, 8) else 3 if iv in (9, 10, 11) else 0
            fig = (FIG7 if t in SEVENTHS else FIG3).get(k, '')
        if fig and t in SEVENTHS: suf = suf[:-1]                                # V65, not V765
        s = h['numeral'] + suf + fig
    return s + (f"/{h['relativeroot']}" if h['relativeroot'] else '')


def measure(work, melody):
    """a labelled work's harmony measures (dict), or None; `melody`: its melody [(onset, dur, midi, bar, beat), ...]"""
    hs = work.harmony or []; ch = chords(work)
    if len(ch) < 8: return None
    bars = [h['bar'] for h in hs if h.get('bar') is not None]
    nbars = max(1, (max(bars) - min(bars) + 1) if bars else 1)
    n = len(ch); share = lambda f: sum(1 for h in ch if f(h)) / n
    out = {'chords a bar': n / nbars,
           'tonic and dominant': share(lambda h: h['numeral'] in ('I', 'i', 'V', 'v') and not h['relativeroot']),
           'sevenths': share(lambda h: h['type'] in SEVENTHS), 'diminished sevenths': share(lambda h: h['type'] == 'o7'),
           'applied chords': share(lambda h: bool(h['relativeroot'])), 'augmented sixths': share(lambda h: h['type'] in AUG6),
           'Neapolitan': share(lambda h: h['numeral'] == 'bII' and not h['relativeroot']),
           'mixture': share(borrowed),
           'inversions': share(lambda h: pc(h['bass']) != pc(h['root']))}
    keys = [h['localkey'] for h in ch]
    out['keys a 10 bars'] = 10 * sum(1 for a, b in zip(keys, keys[1:]) if a != b) / nbars
    out['away from home'] = sum(1 for k in keys if k not in ('I', 'i')) / n
    if all(h.get('by') == 'DCML' for h in hs):
        cad = collections.Counter(h['cadence'].split('.')[0] for h in hs if h.get('cadence'))
        out['cadences a 10 bars'] = 10 * sum(cad.values()) / nbars
        tot = sum(cad.values())
        if tot: out['perfect cadences'] = cad['PAC'] / tot; out['half cadences'] = cad['HC'] / tot; out['deceptive or evaded'] = (cad['DC'] + cad['EC']) / tot
        out['changes'] = share(lambda h: '(' in (h.get('chord') or ''))
    labs = [h for h in hs if h.get('numeral') and h.get('type') and not h['numeral'].startswith('@')]; ons = [h['onset'] for h in labs]
    nct = struck = resolved = susp = 0; heard = 0
    for i, n_ in enumerate(melody):
        k = bisect.bisect_right(ons, n_[0] + 1e-6) - 1
        if k < 0: continue
        cs = chord_tones(labs[k])
        if not cs: continue
        heard += 1
        j = k + 1; end = n_[0] + n_[1]
        if j < len(ons) and ons[j] < end - 1e-3 and i + 1 < len(melody):         # a chord comes while it is held
            nx = melody[i + 1]; new = chord_tones(labs[j])
            if new and n_[2] % 12 not in new and 1 <= n_[2] - nx[2] <= 2 and nx[2] % 12 in new: susp += 1
        if n_[2] % 12 in cs: continue
        nct += 1
        if abs(labs[k]['onset'] - n_[0]) < 1e-3: struck += 1
        if i + 1 < len(melody):
            nx = melody[i + 1]; k2 = bisect.bisect_right(ons, nx[0] + 1e-6) - 1
            if 1 <= abs(nx[2] - n_[2]) <= 2 and k2 >= 0 and nx[2] % 12 in chord_tones(labs[k2]): resolved += 1
    if heard >= 20:
        out['non-chord tones'] = nct / heard; out['suspensions'] = susp / heard
        if nct >= 5: out['struck dissonance'] = struck / nct; out['resolved by step'] = resolved / nct
    return out


MEASURES = ('chords a bar', 'tonic and dominant', 'sevenths', 'diminished sevenths', 'applied chords', 'augmented sixths', 'Neapolitan', 'mixture',
            'inversions', 'keys a 10 bars', 'away from home', 'cadences a 10 bars', 'perfect cadences', 'half cadences', 'deceptive or evaded',
            'changes', 'non-chord tones', 'struck dissonance', 'resolved by step', 'suspensions')
SHARES = {m for m in MEASURES if m not in ('chords a bar', 'keys a 10 bars', 'cadences a 10 bars')}


def runs(work):
    """the work's chords as a progression hears them: [(local key, token, bar)], one chord held while its seventh enters or its
    bass moves counted once (as the seventh, if it has one), DCML's cadential six-four V(64) as I64"""
    out = []
    for h in chords(work):
        rel = f"/{h['relativeroot']}" if h['relativeroot'] else ''
        if '(64)' in (h.get('chord') or '') and h['numeral'] in ('V', 'v'):                      # V(64): the cadential six-four
            tok = ('i' if minor(h['relativeroot'] or h['localkey']) else 'I') + '64' + rel; num = 'cadential 64'   # not merged with a tonic
        else: num, tok = h['numeral'], token(h)
        key = (h['localkey'], num, h['relativeroot'])
        if out and out[-1][0] == key:
            if h['type'] in SEVENTHS and out[-1][3] not in SEVENTHS: out[-1] = (key, tok, out[-1][2], h['type'])
            continue
        out.append((key, tok, h.get('bar'), h['type']))
    return [(k[0], t, b) for k, t, b, _ in out]


def progressions(work):
    """{(token, token, token): [bar, ...]}: the work's three-chord progressions, in the keys they stand in"""
    r = runs(work); out = collections.defaultdict(list)
    for i in range(len(r) - 2):
        if r[i][0] == r[i + 1][0] == r[i + 2][0]: out[(r[i][1], r[i + 1][1], r[i + 2][1])].append(r[i][2])
    return out
