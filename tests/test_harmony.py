"""Harmony from the analysts' labels. Run: python3 -m pytest -q tests"""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import lines as L, profiles as P, harmony as HM

TONES = {('I', 'I'): 'C E G', ('I', 'V'): 'G B D', ('I', 'IV'): 'F A C', ('I', 'ii'): 'D F A', ('I', 'iv'): 'F Ab C', ('I', 'bVI'): 'Ab C Eb',
         ('i', 'i'): 'C Eb G', ('i', 'I'): 'C E G', ('i', 'V'): 'G B D', ('i', '#vii'): 'B D F', ('i', 'iv'): 'F Ab C'}
ROOT = {'I': 'C', 'V': 'G', 'IV': 'F', 'ii': 'D', 'iv': 'F', 'bVI': 'Ab', 'i': 'C', '#vii': 'B'}


def label(onset, numeral, key='I', type_='M', bass=None, rel='', cadence='', by='DCML', tones=None):
    root = ROOT[numeral]
    return dict(onset=float(onset), dur=2.0, bar=1 + int(onset) // 4, localkey=key, numeral=numeral, relativeroot=rel, type=type_,
                root=root, bass=bass or root, tones=tones or TONES[(key, numeral)], cadence=cadence, by=by)


def work(i, composer, labels, melody, collection='c'):
    line = [(t * 1.0, 1.0, m, 1 + t // 4, float(t % 4)) for t, m in enumerate(melody)]
    return L.Work(f'{composer}-{i}', composer, collection, 'dcml', f'{composer} work {i}', {'p': line}, 0, [], {}, len(line), len(line) * 1.0,
                  None, labels)


def test_tokens_name_the_chord_its_inversion_and_what_it_is_applied_to():
    assert HM.token(dict(type='Mm7', numeral='V', root='G', bass='B', relativeroot='')) == 'V65'
    assert HM.token(dict(type='M', numeral='I', root='C', bass='G', relativeroot='')) == 'I64'
    assert HM.token(dict(type='o7', numeral='vii', root='F#', bass='F#', relativeroot='V')) == 'viio7/V'
    assert HM.token(dict(type='Ger', numeral='Ger', root='Ab', bass='Ab', relativeroot='')) == 'Ger'


def test_repeated_labels_count_once_and_mixture_knows_the_mode():
    labs = [label(0, 'I'), label(1, 'I'), label(2, 'iv', type_='m'), label(4, 'bVI'), label(6, 'V'), label(8, 'I'),
            label(10, 'I', key='i', tones='C E G'), label(12, '#vii', key='i', type_='o'), label(14, 'i', key='i', type_='m'),
            label(16, 'V', key='i')]
    w = work(0, 'X', labs, [60] * 20)
    assert len(HM.chords(w)) == 9                                              # the second I merged
    m = HM.measure(w, w.lines['p'])
    assert abs(m['mixture'] - 3 / 9) < 1e-9                                    # iv and bVI in major, the major tonic in minor; not #vii
    assert abs(m['tonic and dominant'] - 6 / 9) < 1e-9
    assert abs(m['keys a 10 bars'] - 10 * 1 / 5) < 1e-9                        # one change of key in five bars


def test_non_chord_tones_struck_and_resolved():
    labs = [label(2 * k, 'V' if k % 2 else 'I') for k in range(16)]
    melody = [65, 64, 67, 69] * 8                                              # F struck with C major, down a step to E; A between, over G,
    w = work(0, 'X', labs, melody)                                             # then a leap to the next F
    m = HM.measure(w, w.lines['p'])
    assert m['non-chord tones'] == 0.5 and m['struck dissonance'] == 0.5 and m['resolved by step'] == 0.5


def test_a_note_held_into_a_chord_it_is_not_in_and_falling_a_step_is_a_suspension():
    labs = [label(4 * k, 'V' if k % 2 else 'I') for k in range(8)]
    melody = []                                                                # C held from beat 2 of a C chord into G, then down to B
    for k in range(4): melody += [(8 * k, 2, 64), (8 * k + 2, 3, 72), (8 * k + 5, 3, 71)]
    line = [(o * 1.0, d * 1.0, m, 1 + o // 4, float(o % 4)) for o, d, m in melody] + [(32.0 + t, 1.0, 67, 9, 0.0) for t in range(12)]
    w = work(0, 'X', labs, [60] * 24)._replace(lines={'p': line})
    m = HM.measure(w, line)
    assert abs(m['suspensions'] - 4 / len(line)) < 1e-9


def test_a_unit_whose_harmony_stands_apart_gets_its_progression_and_bars():
    rnd = random.Random(2); works = []
    seq_a = ['I', 'IV', 'I', 'V', 'I', 'iv', 'I', 'V']                         # the minor iv borrowed, again and again
    seq_b = ['I', 'ii', 'V', 'I', 'IV', 'V', 'I', 'V']
    for i in range(8):
        labs = [label(2 * k, n, type_='m' if n in ('iv', 'ii') else 'M') for k, n in enumerate(seq_a * 3)]
        works.append(work(i, 'Borrower', labs, [60 + rnd.choice([0, 4, 7]) for _ in range(48)]))
    for c in range(6):
        for i in range(8):
            labs = [label(2 * k, n, type_='m' if n in ('iv', 'ii') else 'M') for k, n in enumerate(seq_b * 3)]
            works.append(work(i, f'Other{c}', labs, [60 + rnd.choice([0, 4, 7]) for _ in range(48)], collection=f'c{c}'))
    facts = {w.id: dict(kind=['sonata'], forces='keyboard', year=None, keys=[]) for w in works}
    prof = P.build(works, facts, log=None)
    p = next(v for u, v in prof.items() if u[0] == 'Borrower')
    h = p['harmony']
    assert h['works'] == 8 and h['by'] == {'DCML': 8} and h['compared']['by'] == 'kind, forces, period'
    assert any(t['measure'] == 'mixture' and t['auc'] >= 0.75 for t in h['traits'])
    assert any('iv' in f['chords'] for f in h['progressions']) and h['progressions'][0]['at'][0]['bar'] is not None
    page = P.markdown(p)
    assert "**Harmony**, from the analysts' labels of 8 of its works (8 DCML's)" in page and 'chords from the other mode' in page
    assert 'the progression' in page


def test_a_work_without_labels_has_no_harmony():
    works = [work(i, 'Plain', None, [60, 62, 64, 65] * 6) for i in range(6)]
    facts = {w.id: dict(kind=['chorale'], forces='voices', year=None, keys=[]) for w in works}
    p = next(iter(P.build(works, facts, log=None).values()))
    assert 'harmony' not in p and '**Harmony**' not in P.markdown(p)


def test_a_suspension_dcml_writes_into_the_label_is_outside_the_chord():
    h = dict(root='A', type='m', tones='B C E', chord='vi(2)')                 # vi with 2 in place of its root
    assert HM.tones(h) == {11, 0, 4} and HM.chord_tones(h) == {9, 0, 4}
    assert HM.chord_tones(dict(root='Ab', type='Ger', tones='Ab C Eb F#')) == {8, 0, 3, 6}


def test_a_chord_held_while_its_seventh_enters_is_one_chord_and_dcmls_cadential_six_four_is_i64():
    labs = [label(0, 'I'), label(2, 'I', bass='E'), label(4, 'V', tones='C E G') | dict(chord='V(64)'), label(6, 'V'),
            label(8, 'V', type_='Mm7', tones='G B D F'), label(10, 'I'), label(12, 'IV'), label(14, 'V'), label(16, 'I')]
    toks = [t for _, t, _ in HM.runs(work(0, 'X', labs, [60] * 20))]
    assert toks == ['I', 'I64', 'V7', 'I', 'IV', 'V', 'I']
    assert ('I64', 'V7', 'I') in HM.progressions(work(0, 'X', labs, [60] * 20))
