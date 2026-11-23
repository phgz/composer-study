"""A piece NotaGen wrote (its MusicXML, from study/notagen_write.py), played as written on the piano piece 64b was played on (the
Salamander grand): its notes, its tempo marks, its dynamics and hairpins, its fermatas, its pedal marks where it wrote any. Nothing
is added to it: no rubato, no voicing beyond the written dynamics, a little more weight on accents, staccato notes half their length.
Its pedal marks are read as a pianist would read them where the release is not written (read()).

    NOTAGEN_XML=<file.xml> python3 <composer-blend>/tools/run.py render notagen_piece.py"""
import os

XML = os.environ.get('NOTAGEN_XML', '')
BASE = 2.6                                                     # 64b's bass level: about mezzo-forte before the written dynamics
MARKS = dict(ppp=-1.8, pp=-1.3, p=-.7, mp=-.25, mf=.2, f=.7, ff=1.2, fff=1.6, sf=.6, sfz=.6, fz=.6, fp=.7)
DEFAULT_BPM = 96                                                # where the piece has no tempo mark at all


def directions(path):
    """the wedges and pedal marks of the MusicXML at their places, in quarters ([(beat, 'cresc'|'dim'|'stop'|'ped', number)]), walked
    from the file itself: music21 loses a hairpin that begins on a grace note, and a "Ped." that is never released"""
    import xml.etree.ElementTree as ET
    root = ET.parse(path).getroot(); out = []
    part = root.find('part'); divisions = 1; t = 0.0
    for m in part.iter('measure'):
        pos, longest = 0.0, 0.0
        for el in m:
            if el.tag == 'attributes' and el.find('divisions') is not None: divisions = int(el.find('divisions').text)
            elif el.tag == 'note':
                if el.find('grace') is None and el.find('chord') is None and el.find('duration') is not None:
                    pos += int(el.find('duration').text) / divisions
            elif el.tag == 'backup': pos -= int(el.find('duration').text) / divisions
            elif el.tag == 'forward': pos += int(el.find('duration').text) / divisions
            elif el.tag == 'direction':
                at = t + pos + (int(el.find('offset').text) / divisions if el.find('offset') is not None else 0)
                for w in el.iter('wedge'):
                    kind = {'crescendo': 'cresc', 'diminuendo': 'dim', 'stop': 'stop'}.get(w.get('type'))
                    if kind: out.append((at, kind, w.get('number', '1')))
                for pd in el.iter('pedal'):
                    if pd.get('type') == 'start': out.append((at, 'ped', None))
            longest = max(longest, pos)
        t += longest
    return out


def read(path):
    """[(beat, length, MIDI, level offset)], [(beat, quarter bpm)], dynamics [(beat, level, 'jump') or (beat, end, 'cresc'|'dim')],
    [beat of a fermata], [(beat, down)], end. NotaGen writes "Ped." without its release: from the first one, the pedal is changed
    on each beat of the metre (each dotted quarter in 6/8) where a note begins, to the end, as a pianist would play the marks"""
    import music21
    from music21 import dynamics, expressions, articulations, tempo, meter
    s = music21.converter.parse(path)
    notes, tempi, dyn, ferm, ped = [], [], [], [], []
    for mm in s.flatten().getElementsByClass(tempo.MetronomeMark):
        bpm = mm.getQuarterBPM()
        if bpm: tempi.append((float(mm.getOffsetInHierarchy(s)), float(bpm)))
    for part in s.parts:
        p = part.stripTies()
        for d in p.flatten().getElementsByClass(dynamics.Dynamic):
            if d.value in MARKS: dyn.append((float(d.getOffsetInHierarchy(p)), MARKS[d.value], 'jump'))
        for x in p.flatten().getElementsByClass(expressions.TextExpression):
            w = x.content.strip().rstrip('.').lower()
            if w in ('cresc', 'crescendo', 'dim', 'decresc', 'diminuendo'): dyn.append((float(x.getOffsetInHierarchy(p)), None, 'cresc' if w.startswith('cresc') else 'dim'))
        for n in p.flatten().notes:
            b = float(n.getOffsetInHierarchy(p)); ql = float(n.duration.quarterLength)
            grace = ql == 0
            if grace: ql = .12; b -= .12
            acc = .4 if any(isinstance(a, (articulations.Accent, articulations.StrongAccent)) for a in n.articulations) else 0
            if any(isinstance(a, (articulations.Staccato, articulations.Staccatissimo)) for a in n.articulations): ql *= .5
            if any(isinstance(e, expressions.Fermata) for e in n.expressions): ferm.append(b)
            for pt in n.pitches: notes.append((max(0.0, b), ql, pt.midi, acc - (.3 if grace else 0)))
    end = max(b + d for b, d, _, _ in notes)
    open_ = {}
    for at, kind, num in sorted(directions(path), key=lambda x: x[0]):
        if kind in ('cresc', 'dim'): open_[num] = (at, kind)
        elif kind == 'stop' and num in open_: b0, k = open_.pop(num); dyn.append((b0, at, k))
    start = min((at for at, kind, _ in directions(path) if kind == 'ped'), default=None)
    if start is not None:
        beat = float(s.flatten().getElementsByClass(meter.TimeSignature)[0].beatDuration.quarterLength)
        onsets = sorted({b for b, _, _, _ in notes})
        changes = [start + k * beat for k in range(int((end - start) / beat) + 1)
                   if any(start + k * beat - 1e-6 <= o < start + (k + 1) * beat - 1e-6 for o in onsets)]   # a beat where a note begins
        for a, b in zip(changes, changes[1:] + [end + 2]): ped += [(a, True), (b, False)]   # the last held into the silence
    return notes, sorted(set(tempi)), dyn, sorted(set(ferm)), ped, end


def curve(dyn):
    """the written dynamics as the engine's curve: a mark jumps; a hairpin (or "cresc.", "dim.") ramps from the level where it begins
    to the next mark, where that mark goes its way and comes within a beat of its end ("cresc." has no end: to the next mark), or
    else half a step up or down"""
    marks = sorted((b, v) for b, v, k in dyn if k == 'jump')
    pins = sorted((b0, b1, k) for b0, b1, k in dyn if k in ('cresc', 'dim'))
    out, level, i = [], 0.0, 0
    for b0, b1, k in pins:
        while i < len(marks) and marks[i][0] <= b0 + 1e-6: level = marks[i][1]; out.append((marks[i][0], level, 'jump')); i += 1
        if b1 is None: b1 = marks[i][0] if i < len(marks) else b0 + 3
        if i < len(marks) and marks[i][0] < b1 - 1e-6: continue           # a mark inside the hairpin: the marks say it
        up = k == 'cresc'
        nxt = next(((b, v) for b, v in marks[i:] if b <= b1 + 1), None)
        target = nxt[1] if nxt and (nxt[1] > level) == up and nxt[1] != level else level + (.5 if up else -.5)
        out += [(b0, level, 'jump'), (b1, target, 'ramp')]; level = target
    out += [(b, v, 'jump') for b, v in marks[i:]]
    return sorted(out, key=lambda x: x[0])


def build():
    from eng import Piece
    notes, tempi, dyn, ferm, ped, end = read(XML)
    p = Piece(); piano = p.part('piano', 'piano', 0, .5, True)
    for b, bpm in (tempi or [(0.0, DEFAULT_BPM)]): p.tempo(b, bpm)
    if tempi and tempi[0][0] > 0: p.tempo(0, tempi[0][1])
    for b, L, kind in curve(dyn): p.dyn(b, L, kind=kind)
    for b, d, m, acc in notes: p.note(piano, b, d, m, BASE + acc)
    for b in ferm: p.ferm(b, 1.0)
    for b, down in ped: p.pedal(piano, b + (.1 if down else -.05), down)
    S, END, T = p.finish(end, tail=3.5)
    return S, END


MAP = {'piano': lambda mm, d: ('piano_s', None)}
GAIN = {'piano': 1.0}
MASTERING = dict(mode='standard', target_lufs=-19.8)           # 64b's level, so that the two can be heard side by side
