"""The quote test, the inputs: the first eight bars of ten real mazurkas put in place of piece 64b's bars 41 to 48, for NotaGen and
AMT to hear: five by Chopin (standard repertoire, which their training may hold) and five by Polish composers of his century whose
mazurkas are little known (Polish Scores, read for score-reader in 2026; less likely in their training). Each in its own key and a
whole tone higher, so that what a model knows of the very notes (in its key) can be told from what it knows of the style.

  the quotes        eight bars of each work as written, from the first whole bar its right hand plays in (a pickup bar and an
                    introduction for the left hand alone left out): every voice, the left hand's voices on
                    64b's lower staff, the right hand's on its upper; its key written where it begins ([K:...] in each of its voices)
                    and 64b's E minor written where each voice comes back. In NotaGen's ABC the quote's bars are the work's own, as
                    NotaGen's pipeline writes them for the work alone; an inline clef change in them is left out (it moves no pitch),
                    and so is a tie out of their last bar.
                    Checked: the quote's notes read as they do alone, and 64b's after it as they do without it
  64b around them   everything before bar 41 and after bar 48 as written, a note that would sound into bar 41 cut there; the same
                    prompt as before ("Romantic / Chopin, Frederic / Keyboard")
  AMT               the quote's notes at 64b's tempo for those bars (its beats through 64b's tempo map), on the piano, with 64b's
                    notes around them, no given notes
  alone             the same eight bars as a piece by themselves, both keys: what each ear makes of them with no 64b around them

The notes scored are the quote's. The comparison is the rest of 64b, as written (the glitch test's "64b | as written").

Writes beside this script: quote_notagen_inputs.jsonl, quote_amt_inputs.jsonl, quote.json. Ids: "<work> | <key> | in 64b" and
"<work> | <key> | alone", <key> "own key" or "a tone higher".

Run: python3 -I prepare_quote.py <score-reader cache> <NotaGen checkout> <anticipation checkout> <composer-blend> <renderer-engine>"""
import json, os, re, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'checks', 'three-ears-64b-2026-11-23'))
from study import notagen as G, amt as A

CACHE, NG, ACO, BLEND, RENDERER = sys.argv[1:6]
XML2ABC = os.path.join(NG, 'data', 'xml2abc.py')
PROMPT64 = ('Romantic', 'Chopin, Frederic', 'Keyboard')
AT, BARS = 41, 8                                                       # 64b's bars 41 to 48
C = 'kern__chopin-first-editions/kern/'; PL = 'kern__polish-scores/'
SOURCES = [('Chopin', 'Chopin, Mazurka op. 7 no. 1', C + '007-1-KI-001.krn'),
           ('Chopin', 'Chopin, Mazurka op. 17 no. 4', C + '017-1-BH-004.krn'),
           ('Chopin', 'Chopin, Mazurka op. 24 no. 1', C + '024-1d-W-001.krn'),
           ('Chopin', 'Chopin, Mazurka op. 33 no. 4', C + '033-1-BH-004.krn'),
           ('Chopin', 'Chopin, Mazurka op. 67 no. 4', C + '067-1-Sam-004.krn'),   # op. 41 no. 2, 64b's source: music21 misreads its bar 8
           ('Polish', 'Statkowski, Mazur op. 27 no. 1', PL + 'pl-wtm/kern/pl-wtm--a-19-143_statkowski-roman--mazur-op-27-no-1.krn'),   # op. 2 no. 1: music21 cannot read it
           ('Polish', 'Stojowski, Mazurka op. 8 no. 2', PL + 'pl-wtm/kern/pl-wtm--1936-fp-6535_stojowski-zygmunt--mazurka-op-8-no-2.krn'),
           ('Polish', 'Kątski, Mazur sielankowy op. 4', PL + 'pl-wn/kern/pl-wn--mus-iii-72-689-cim_katski-apolinary--mazur-sielankowy-op-4.krn'),
           ('Polish', 'Józef Stefani, Mazur G no. 2', PL + 'pl-wtm/kern/pl-wtm--r-1345_stefani-jozef--mazur-g-nr-2.krn'),
           ('Polish', 'Noskowski, Mazurka (Causeries op. 32)', PL + 'pl-wtm/kern/pl-wtm--r-116-n--001-002_noskowski-zygmunt--causeries-op-32-mazurka.krn')]
KEYS = (('own key', None), ('a tone higher', 'M2'))
CLEF_ONLY = re.compile(r'\[K:\s*(?:clef=)?(?:treble|bass|alto|tenor|soprano|mezzosoprano|baritone)[^\]]*\]')
SEG = re.compile(r'\[V:(\d+)\](.*?)(?=\[V:|$)')
TIE_OUT = re.compile(r'-(?=[\s|:\]]*$)')
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)


def quote_of(path, shift):
    """(the eight bars' score, their ABC in NotaGen's notation, their notes [(beat, beats, MIDI)] from the first bar's start)"""
    import music21
    s = music21.converter.parse(os.path.join(CACHE, 'collections', path))
    if shift: s = s.transpose(shift)
    ms = list(s.parts[0].getElementsByClass('Measure'))
    full = ms[0].barDuration.quarterLength
    i0 = 1 if ms[0].duration.quarterLength < full - 1e-6 else 0             # a pickup bar left out
    while not list(ms[i0].recurse().notes): i0 += 1                          # from the first bar the right hand plays in
    q = s.measures(i0, i0 + BARS, indicesNotNumbers=True)                    # the end left out
    for p in q.parts:
        for m in p.getElementsByClass('Measure'):
            if abs(m.duration.quarterLength - full) > 1e-6: raise RuntimeError(f'{path}: bar {m.number} misread ({m.duration.quarterLength})')
    with tempfile.TemporaryDirectory() as tmp:
        xml = os.path.join(tmp, 'q.musicxml'); q.write('musicxml', fp=xml); r = G.prepare_xml(xml, PROMPT64, XML2ABC)
    if isinstance(r, str): raise RuntimeError(f'{path}: {r}')
    if len(r['body']) != BARS: raise RuntimeError(f'{path}: {len(r["body"])} bars')
    start = min(float(m.getOffsetInHierarchy(q)) for m in q.parts[0].getElementsByClass('Measure'))
    notes = []
    for p in q.parts:
        for el in p.flatten().stripTies().notes:
            if el.duration.isGrace: continue
            for x in ([el.pitch] if el.isNote else el.pitches): notes.append((float(el.offset) - start, float(el.quarterLength), x.midi))
    return q, r, notes


def remap(r):
    """the quote's ABC voices onto 64b's: the upper staff's voices to 1 and 2, the lower's to 4 (one) or 3 and 4 (two)"""
    clefs = [(l.split()[0][2:], 'bass' if re.search(r'\bbass\b|\bF[34]?\b', l) else 'treble') for l in r['meta'] if l.startswith('V:')]
    up = [v for v, c in clefs if c == 'treble']; down = [v for v, c in clefs if c == 'bass']
    if len(up) > 2 or len(down) > 2 or not up or not down: raise RuntimeError(f'voices {clefs}')
    return {**dict(zip(up, ['1', '2'])), **dict(zip(down, ['4'] if len(down) == 1 else ['3', '4']))}


def splice(body64, rq, qkey, back):
    """64b's body with bars AT.. replaced by the quote's, the keys written where they change"""
    vmap = remap(rq); out = list(body64[:AT - 1]); in_quote = set()
    for j, line in enumerate(rq['body']):
        segs = sorted(((vmap[v], CLEF_ONLY.sub('', t)) for v, t in SEG.findall(line.rstrip('\n'))), key=lambda x: int(x[0]))
        if any('[K:' in t for _, t in segs): raise RuntimeError('a key change in the quote')
        segs = [(v, t if v in in_quote else f'[K:{qkey}]' + t) for v, t in segs]   # each voice told the key where it first plays
        if j == len(rq['body']) - 1: segs = [(v, TIE_OUT.sub('', t)) for v, t in segs]  # no tie out of the quote into 64b
        in_quote |= {v for v, _ in segs}
        out.append(''.join(f'[V:{v}]{t}' for v, t in segs) + '\n')
    for line in body64[AT - 1 + BARS:]:
        segs = SEG.findall(line.rstrip('\n'))
        if in_quote & {v for v, _ in segs}:
            segs = [(v, f'[K:{back}]' + t if v in in_quote else t) for v, t in segs]; in_quote -= {v for v, _ in segs}
            line = ''.join(f'[V:{v}]{t}' for v, t in segs) + '\n'
        out.append(line)
    if in_quote: raise RuntimeError(f'voices {in_quote} never come back')
    return out


def head_key(meta): return next(l[2:].strip() for l in meta if l.startswith('K:'))


# 64b, its bars 41 to 48 emptied --------------------------------------------------------------------------------------------------
import piece64 as P
v = P.voices(BLEND, RENDERER); sec = v['sec']
b0, b1 = (AT - 1) * P.METRE, (AT - 1 + BARS) * P.METRE
kept = []
for name, b, d, m, t, dd in v['notes']:
    if b0 - 1e-6 <= b < b1 - 1e-6: continue
    if b < b0 - 1e-6 and b + d > b0 + 1e-6: d = b0 - b; dd = min(dd, sec(b0) - t)
    kept.append((name, b, d, m, t, dd))
vs = {}
for name, b, d, m, t, dd in kept: vs.setdefault(name, []).append((b, d, m))
with tempfile.TemporaryDirectory() as tmp:
    r64 = G.prepare_xml(P.piano_xml({k: sorted(x) for k, x in vs.items()}, os.path.join(tmp, 'p.musicxml')), PROMPT64, XML2ABC)
if isinstance(r64, str): raise RuntimeError(r64)
assert all(not SEG.findall(l) for l in r64['body'][AT - 1:AT - 1 + BARS]), "64b's bars 41 to 48 are not empty"
back = head_key(r64['meta'])
log("64b's ABC:", len(r64['body']), 'bars, its key', back)

ng_in, amt_in, meta = [], [], dict(at=[AT, AT + BARS - 1], prompt=list(PROMPT64), quotes=[])
for family, title, path in SOURCES:
    for kname, shift in KEYS:
        q, rq, qnotes = quote_of(path, shift); qkey = head_key(rq['meta'])
        # NotaGen, in 64b: the spliced body read as NotaGen reads a work (prepare_abc's note reading, on the spliced lines)
        body = splice(r64['body'], rq, qkey, back)
        rs = G.prepare_lines(r64['meta'], body)
        vmap = remap(rq)                                                    # checked: the quote's notes read as they read alone,
        for qv, ns in rq['notes'].items():                                  # 64b's after it as they read without the quote
            got = [n[4] for n in rs['notes'].get(vmap[qv.split('.')[0]] + '.' + qv.split('.')[1], []) if AT - 1 <= n[0] < AT - 1 + BARS]
            if got != [n[4] for n in ns]: raise RuntimeError(f'{title} {kname}: voice {qv} reads otherwise in 64b')
        for vv, ns in r64['notes'].items():
            if [n[4] for n in ns if n[0] >= AT - 1 + BARS] != [n[4] for n in rs['notes'][vv] if n[0] >= AT - 1 + BARS]:
                raise RuntimeError(f'{title} {kname}: 64b reads otherwise after the quote, voice {vv}')
        wanted = [(k, a, b) for vv in sorted(rs['notes']) for (k, a, b, t, midi, chord) in rs['notes'][vv] if AT - 1 <= k < AT - 1 + BARS]
        which = [[vv, k, round(t - b0, 4), midi, chord] for vv in sorted(rs['notes']) for (k, a, b, t, midi, chord) in rs['notes'][vv]
                 if AT - 1 <= k < AT - 1 + BARS]
        si = G.scoring_input(rs['meta'], rs['body'], wanted)
        ng_in.append(dict(id=f'{title} | {kname} | in 64b', prompt=list(PROMPT64), windows=si['windows'], notes=si['notes']))
        # NotaGen, alone
        wa = [(k, a, b) for vv in sorted(rq['notes']) for (k, a, b, t, midi, chord) in rq['notes'][vv]]
        which_alone = [[vv, k, round(t, 4), midi, chord] for vv in sorted(rq['notes']) for (k, a, b, t, midi, chord) in rq['notes'][vv]]
        sa = G.scoring_input(rq['meta'], rq['body'], wa)
        ng_in.append(dict(id=f'{title} | {kname} | alone', prompt=list(PROMPT64), windows=sa['windows'], notes=sa['notes']))
        # AMT, in 64b and alone
        qs = P.seconds([(b0 + x, d, m) for x, d, m in qnotes], sec)
        ev = [(t, dd, m) for name, b, d, m, t, dd in kept] + qs
        scored = list(range(len(kept), len(ev)))
        order = sorted(range(len(ev)), key=lambda i: (ev[i][0], ev[i][2])); rank = {i: k for k, i in enumerate(order)}
        seq, where = A.sequence(ev, [], ACO); trip = [where[rank[i]] for i in scored]
        ws, pos = A.windows(seq, trip, ACO, alone=True)
        amt_in.append(dict(id=f'{title} | {kname} | in 64b', windows=ws, notes=pos))
        alone = P.seconds(qnotes, lambda x: sec(b0 + x) - sec(b0))
        order = sorted(range(len(alone)), key=lambda i: (alone[i][0], alone[i][2])); rank = {i: k for k, i in enumerate(order)}
        seq, where = A.sequence(alone, [], ACO)
        ws, pos = A.windows(seq, [where[rank[i]] for i in range(len(alone))], ACO, alone=True)
        amt_in.append(dict(id=f'{title} | {kname} | alone', windows=ws, notes=pos))
        meta['quotes'].append(dict(family=family, title=title, path=path, key=kname, abc_key=qkey,
                                   notagen_in_64b=which, notagen_alone=which_alone,
                                   amt=[[round(x, 4), round(d, 4), m] for x, d, m in qnotes]))
        log(title, '|', kname, f'({qkey}):', len(which), 'NotaGen notes,', len(qnotes), 'AMT notes')

with open(os.path.join(HERE, 'quote_notagen_inputs.jsonl'), 'w') as f:
    for x in ng_in: f.write(json.dumps(x) + '\n')
with open(os.path.join(HERE, 'quote_amt_inputs.jsonl'), 'w') as f:
    for x in amt_in: f.write(json.dumps(x) + '\n')
json.dump(meta, open(os.path.join(HERE, 'quote.json'), 'w'))
log('done:', len(ng_in), 'NotaGen inputs,', len(amt_in), 'AMT inputs')
