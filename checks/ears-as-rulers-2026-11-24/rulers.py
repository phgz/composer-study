"""The outside ears as rulers, the shared pieces: a work as music21 reads it, its notes as lines and as AMT's notes, a copy with some
notes moved (the planted wrong notes), and the check that the copy's ABC differs from the original's at those notes and nowhere else.

    stream_of(work_id, cache, score_reader)   the work's score (one movement where the file holds several), as notagen.standard_abc
    lines_of(score)                           {part index: [(onset, length, MIDI, element index)]}: each part's notes in order, a chord
                                              as its top note, tied continuations and grace notes left out (as NotaGen's ABC reads them)
    amt_notes(score)                          [(onset s, length s, MIDI, (part, onset, MIDI))]: every note, ties joined, a quarter at 90
    moved(score, picks)                       a copy with each pick [(part, element index, semitones)] moved, spelt in its key's way
    abc_of(score, prompt, xml2abc)            the score in NotaGen's notation (notagen.prepare_xml)
    differences(r0, r1)                       {(voice, ABC index): (MIDI before, after)} where two preparations differ, or a reason"""
import copy, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..'))
from study import notagen as G

QUARTER_S = 60 / 90


def stream_of(work_id, cache, score_reader):
    import music21
    src, mv = G.source(work_id, cache)
    if not src: raise FileNotFoundError(work_id)
    s = music21.converter.parse(src)
    if mv:
        if score_reader not in sys.path: sys.path.insert(0, score_reader)
        from score_reader import notes as N
        starts = [i for i, _ in N.movements(src)]
        i0 = starts[mv - 1]; i1 = starts[mv] if mv < len(starts) else len(s.parts[0].getElementsByClass('Measure'))
        s = s.measures(i0, i1, indicesNotNumbers=True)
    return s


def elements(score):
    """[(part index, [note or chord, in order])]"""
    return [(pi, list(p.recurse().notes)) for pi, p in enumerate(score.parts)]


def lines_of(score):
    out = {}
    for pi, els in elements(score):
        line = []
        for ei, el in enumerate(els):
            if el.duration.isGrace or (el.tie is not None and el.tie.type in ('stop', 'continue')): continue
            ps = [el.pitch] if el.isNote else list(el.pitches)
            if not ps: continue
            line.append((float(el.getOffsetInHierarchy(score)), float(el.quarterLength), max(p.midi for p in ps), ei))
        out[pi] = line
    return out


def amt_notes(score, quarter_s=QUARTER_S):
    out = []
    for pi, p in enumerate(score.parts):
        for el in p.flatten().stripTies().notes:
            if el.duration.isGrace: continue
            ps = [el.pitch] if el.isNote else list(el.pitches)
            t = float(el.offset); d = max(float(el.quarterLength), .05)
            for q in ps: out.append((t * quarter_s, d * quarter_s, q.midi, (pi, round(t, 4), q.midi)))
    return out


def spelt(midi, sharps):
    """a pitch for `midi`, spelt with sharps in a sharp key, flats in a flat key (music21's own choice for C major's)"""
    import music21
    p = music21.pitch.Pitch(); p.midi = midi
    if p.accidental is not None and p.accidental.alter != 0 and ((sharps < 0 < p.accidental.alter) or (sharps > 0 > p.accidental.alter)):
        p = p.getEnharmonic()
    return p


def eligible(score, first_bar=3, last_bars=2, shortest=0.5):
    """notes a wrong note may be planted on: [(part, element index, bar index)], single notes (no chord, tie or grace note) at least
    an eighth long, from the third bar to the third last"""
    import music21
    nbars = len(score.parts[0].getElementsByClass('Measure')); out = []
    for pi, els in elements(score):
        index = {id(m): i for i, m in enumerate(score.parts[pi].getElementsByClass('Measure'))}
        for ei, el in enumerate(els):
            if not el.isNote or el.duration.isGrace or el.tie is not None or el.quarterLength < shortest: continue
            m = el.getContextByClass(music21.stream.Measure)
            bar = index.get(id(m), -1) if m is not None else -1
            if first_bar - 1 <= bar < nbars - last_bars: out.append((pi, ei, bar))
    return out


def moved(score, picks):
    """a copy of the score with each pick (part, element index, semitones) moved"""
    import music21
    s = copy.deepcopy(score); els = dict(elements(s))
    for pi, ei, semis in picks:
        el = els[pi][ei]; ks = el.getContextByClass(music21.key.KeySignature)
        el.pitch = spelt(el.pitch.midi + semis, ks.sharps if ks is not None else 0)
    return s


def abc_of(score, prompt, xml2abc):
    with tempfile.TemporaryDirectory() as tmp:
        xml = os.path.join(tmp, 'work.musicxml'); score.write('musicxml', fp=xml)
        return G.prepare_xml(xml, prompt, xml2abc)


def differences(r0, r1):
    if sorted(r0['notes']) != sorted(r1['notes']): return 'other voices'
    out = {}
    for v, a in r0['notes'].items():
        b = r1['notes'][v]
        if len(a) != len(b): return f'voice {v}: {len(a)} notes against {len(b)}'
        for i, (x, y) in enumerate(zip(a, b)):
            if (x[0], round(x[3], 4), x[5]) != (y[0], round(y[3], 4), y[5]): return f'voice {v}, note {i}: moved in time'
            if x[4] != y[4]: out[(v, i)] = (x[4], y[4])
    return out
