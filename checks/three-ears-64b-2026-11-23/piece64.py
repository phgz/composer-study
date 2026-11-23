"""Piece 64b (composer-blend, pieces/64b_inside_the_mazurka) as the three ears read it: its voices with their beats and the seconds
the renderer plays them at, and its piano score as MusicXML for NotaGen.

    voices(blend, renderer)    every note the renderer plays, with its voice: tune (with its octave doublings), alto, tenor, bass
    piano_xml(voices, path)    the four voices on a piano's two staves (tune and alto above, tenor and bass below), in 3/4, E minor
                               but E flat major in bars 89 to 104, each pitch spelt in its region's way"""
import os, sys
import numpy as np

METRE, BARS = 3, 160
FLATS = (85, 104)                                     # spelt with flats: the B flat of the bass from bar 85, then E flat major
EFLAT = (89, 104)                                     # E flat major's signature
SHARP_NAMES = 'C C# D D# E F F# G G# A A# B'.split(); FLAT_NAMES = 'C D- D E- E F G- G A- A B- B'.split()


def voices(blend, renderer):
    """{'notes': [(voice, beat, beats, MIDI, onset s, length s)], 'sec': beats -> seconds, 'module': notes64}, from the renderer's own
    build of the whole piece (notes64.build('all')), each note tagged with the voice whose list the build was reading"""
    piece = os.path.join(blend, 'pieces', '64b_inside_the_mazurka')
    for p in (renderer, os.path.join(renderer, 'adapters'), os.path.join(renderer, 'tools'), piece):
        if p not in sys.path: sys.path.insert(0, p)
    os.environ.setdefault('RENDERER_ROOT', renderer)
    import eng, notes64 as N
    cur, tags, cap = ['?'], [], {}

    class Tagged(list):
        def __init__(self, xs, name): super().__init__(xs); self.name = name
        def __iter__(self): cur[0] = self.name; return super().__iter__()

    inner0 = N.inner
    N.TUNE, N.BASS = Tagged(N.TUNE, 'tune'), Tagged(N.BASS, 'bass')
    N.inner = lambda: {v: Tagged(l, v) for v, l in inner0().items()}
    note0, finish0 = eng.Piece.note, eng.Piece.finish

    def note(self, key, b, db, m, L, *a, **k): tags.append(cur[0]); return note0(self, key, b, db, m, L, *a, **k)

    def finish(self, *a, **k): cap['ev'] = list(self.EV); r = finish0(self, *a, **k); cap['S'] = r[0]; return r
    eng.Piece.note, eng.Piece.finish = note, finish
    try: N.build('all')
    finally: eng.Piece.note, eng.Piece.finish, N.inner = note0, finish0, inner0
    ev = cap['ev']; S = cap['S']; played = S.parts[ev[0][0]]['notes']
    assert len(ev) == len(played) == len(tags)
    notes = [(v, float(b), float(db), int(m), float(t0), float(d)) for v, (_, b, db, m, _), (t0, d, _, _) in zip(tags, ev, played)]
    bs = sorted({(b, t) for _, b, _, _, t, _ in notes}); xb = np.array([b for b, _ in bs]); xt = np.array([t for _, t in bs])
    sec = lambda b: float(np.interp(b, xb, xt))
    return dict(notes=notes, sec=sec, module=N)


def seconds(notes, sec):
    """[(beat, beats, MIDI)] as [(onset s, length s, MIDI)], a note's length as the renderer plays it (.97 of its span from 0.45 s,
    .85 under)"""
    out = []
    for b, d, m in notes:
        t0, t1 = sec(b), sec(b + d); span = t1 - t0
        out.append((t0, span * (.97 if span >= .45 else .85), m))
    return out


def spelt(m, bar):
    names = FLAT_NAMES if FLATS[0] <= bar <= FLATS[1] else SHARP_NAMES
    return names[m % 12] + str(m // 12 - 1)


def piano_xml(vs, path):
    """vs {tune, alto, tenor, bass: [(beat, beats, MIDI)]} as a piano score in MusicXML. Notes at one onset in a voice are one chord
    (the doublings); a note is cut where its voice's next one begins"""
    import music21
    from music21 import stream, note, chord, meter, key, clef, layout
    parts = {}
    for name in ('tune', 'alto', 'tenor', 'bass'):
        by = {}
        for b, d, m in vs.get(name, []): by.setdefault(round(b, 6), []).append((d, m))
        p = stream.Part(); onsets = sorted(by)
        for i, b in enumerate(onsets):
            d = max(x for x, _ in by[b]); ms = sorted({m for _, m in by[b]})
            if i + 1 < len(onsets): d = min(d, onsets[i + 1] - b)
            d = min(d, BARS * METRE - b)
            bar = int(b // METRE) + 1
            el = chord.Chord([spelt(m, bar) for m in ms]) if len(ms) > 1 else note.Note(spelt(ms[0], bar))
            el.quarterLength = d; p.insert(b, el)
        p.insert(0, meter.TimeSignature('3/4'))
        p.insert(0, key.Key('e')); p.insert((EFLAT[0] - 1) * METRE, key.Key('E-')); p.insert(EFLAT[1] * METRE, key.Key('e'))
        p.makeRests(refStreamOrTimeRange=[0.0, float(BARS * METRE)], fillGaps=True, inPlace=True)
        p.makeMeasures(inPlace=True); p.makeTies(inPlace=True)
        parts[name] = p
    score = stream.Score(); staves = []
    for (up, down), cl, ids in ((('tune', 'alto'), clef.TrebleClef(), (1, 2)), (('tenor', 'bass'), clef.BassClef(), (3, 4))):
        ps = stream.PartStaff(); ps.partName = 'Piano'; ms_up = list(parts[up].getElementsByClass('Measure')); ms_dn = list(parts[down].getElementsByClass('Measure'))
        for i, (a, b) in enumerate(zip(ms_up, ms_dn)):
            m = stream.Measure(number=i + 1)
            if i == 0: m.insert(0, cl); m.insert(0, meter.TimeSignature('3/4'))
            for ks in a.getElementsByClass(key.KeySignature): m.insert(0, key.Key(ks.tonic.name, ks.mode))
            for vi, src in zip(ids, (a, b)):
                v = stream.Voice(id=str(vi))
                for el in src.notesAndRests: v.insert(el.offset, el)
                m.insert(0, v)
            ps.append(m)
        staves.append(ps); score.insert(0, ps)
    score.insert(0, layout.StaffGroup(staves, symbol='brace'))
    score.write('musicxml', fp=path)
    return path
