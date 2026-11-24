"""NotaGen as an ear, beside the continuations' ear: held-out works put in NotaGen's notation, so that its surprise at each real note
can be measured (on a machine that holds its weights: study/notagen_score.py) and set against ours, note for note.

NotaGen (Wang et al., 2025; github.com/ElectricAlexis/NotaGen, MIT) writes "interleaved ABC": a few metadata lines, then one line a
bar, each voice's bar in turn ("[V:1]... |[V:2]... |"). It reads the text as patches of 16 characters (each line cut where the bars
are, each piece of it cut in 16s) and predicts each patch's characters one at a time. Its fine-tuning puts three lines first,
"%period", "%composer", "%instrumentation". This module follows its data scripts (data/1_batch_xml2abc.py, data/2_data_preprocess.py)
and its Patchilizer (inference/utils.py, encode_train, stream mode), so that the characters measured are those it was trained on:

  prepare   a work's source (kern, MusicXML) -> MusicXML (music21; one movement of a file that holds several, where score-reader's
            movements() puts it) -> standard ABC (NotaGen's xml2abc.py, "-d 8 -c 6 -x") -> NotaGen's cleaning, then its rest
            reduction in the work's own key (NotaGen-X was fine-tuned without changing keys) -> the prompt lines first -> windows of at
            most 1024 patches, as its stream mode cuts them (a window begins at a bar, with the metadata; each bar keeps its
            "[r:i/j]"); and each note's place in a window: the characters of its pitch (accidental, letter, octave marks)
  align     each ABC voice to the work's line (lines.py's reading) whose pitches it shares most, in order (the reading plays repeats,
            the ABC writes them once), so that each note has a line and an index in it

A note's bits under NotaGen are those of its pitch's characters, and of the character after them not being an octave mark (the pitch
ends there). What is not alike, and leans against NotaGen: it names the note (F sharp or G flat, and whether the accidental is
written), so its bits pay for the spelling too; and it writes a bar's voices top to bottom, so an inner voice is predicted before the
same bar's bass, but after the top voice's whole bar. Ours hears what sounds at the note's onset, below and above. And for it: these
works are standard repertoire, and its training (1.6 million scores, then 8,948 classical pieces) may well hold them; ours were held
out of every level that hears them."""
import difflib, os, re, subprocess, sys, tempfile
from fractions import Fraction as F

PATCH_SIZE, PATCH_LENGTH = 16, 1024                             # NotaGen-X (inference/config.py)
BOS, EOS = 1, 2
DELIMITERS = ["|:", "::", ":|", "[|", "||", "|]", "|"]
SPLIT_RE = '(' + '|'.join(map(re.escape, DELIMITERS)) + ')'

UNITS = {('Johann Sebastian Bach', 'chorale', 'voices', 'Leipzig'): ('Baroque', 'Bach, Johann Sebastian', 'Choral'),
         ('Arcangelo Corelli', 'trio sonata', 'chamber', 'all'): ('Baroque', 'Corelli, Arcangelo', 'Chamber'),
         ('Antonio Vivaldi', 'trio sonata', 'chamber', 'all'): ('Baroque', 'Vivaldi, Antonio', 'Chamber'),
         ('Franz Joseph Haydn', 'string quartet', 'string quartet', 'mature'): ('Classical', 'Haydn, Joseph', 'Chamber'),
         ('Wolfgang Amadeus Mozart', 'string quartet', 'string quartet', 'Vienna'): ('Classical', 'Mozart, Wolfgang Amadeus', 'Chamber')}


# --- the source, as NotaGen's data scripts make it -------------------------------------------------------------------------------

def source(work_id, cache):
    """(path, movement or None) of a work's source among score-reader's collections. DCML's Corelli has no score: the same movement
    in the kern collection (op04n02a -> op4/op4n2-01.krn), which the alignment then has to confirm"""
    coll, rest = work_id.split(':', 1); path, _, mv = rest.partition('#')
    if coll == 'dcml/corelli':
        m = re.search(r'op0?(\d+)n0?(\d+)([a-z])', path)
        if not m: return None, None
        coll, path = 'kern/corelli', f'op{m[1]}/op{m[1]}n{m[2]}-{ord(m[3]) - 96:02d}.krn'
    root = os.path.join(cache, 'collections', coll.replace('/', '__'))
    for cand in (os.path.join(root, path), os.path.join(root, 'scores', path), os.path.join(root, 'kern', path)):
        if os.path.isfile(cand): return cand, int(mv) if mv else None
    found = [os.path.join(d, os.path.basename(path)) for d, _, fs in os.walk(root) if os.path.basename(path) in fs]
    return (found[0], int(mv) if mv else None) if len(found) == 1 else (None, None)


def standard_abc(src, movement, xml2abc, score_reader):
    """the source as standard ABC: MusicXML from music21 (the movement's measures alone, where the file holds several), then NotaGen's
    own xml2abc.py with its options"""
    import music21
    s = music21.converter.parse(src)
    if movement:
        if score_reader not in sys.path: sys.path.insert(0, score_reader)
        from score_reader import notes as N
        starts = [i for i, _ in N.movements(src)]
        i0 = starts[movement - 1]; i1 = starts[movement] if movement < len(starts) else len(s.parts[0].getElementsByClass('Measure'))
        s = s.measures(i0, i1, indicesNotNumbers=True)
    with tempfile.TemporaryDirectory() as tmp:
        xml = os.path.join(tmp, 'work.musicxml'); s.write('musicxml', fp=xml)
        out = subprocess.run([sys.executable, '-I', xml2abc, '-d', '8', '-c', '6', '-x', xml], capture_output=True, text=True, timeout=600)
    return out.stdout


def notagen_lines(abc_text):
    """NotaGen's cleaning (data/2_data_preprocess.py, line for line) and its rest reduction, in the work's own key: (metadata lines,
    one line a bar with the voices that are not all rest)"""
    from abctoolkit.utils import (remove_information_field, remove_bar_no_annotations, Quote_re, Barlines, extract_metadata_and_parts,
                                  extract_global_and_local_metadata, extract_barline_and_bartext_dict)
    from abctoolkit.convert import unidecode_abc_lines
    from abctoolkit.transpose import transpose_an_abc_text, Mode2Key
    from abctoolkit.check import check_alignment_unrotated
    lines = [l + '\n' for l in abc_text.split('\n') if l.strip()]
    lines = unidecode_abc_lines(lines)
    lines = remove_information_field(abc_lines=lines, info_fields=['X:', 'T:', 'C:', 'W:', 'w:', 'Z:', '%%MIDI'])
    lines = remove_bar_no_annotations(lines)
    for i, line in enumerate(lines):
        if not (re.search(r'^[A-Za-z]:', line) or line.startswith('%')) and r'\"' in line: lines[i] = line.replace(r'\"', '')
    for i, line in enumerate(lines):
        for q in re.findall(Quote_re, line):
            if any(b in q for b in Barlines): line = line.replace(q, ''); lines[i] = line
    _, equal, _ = check_alignment_unrotated(lines)
    if not equal: raise ValueError('voices with unequal numbers of bars')       # NotaGen leaves such a file out
    for i, line in enumerate(lines):
        for match in re.findall(r'"[^"]*"', line):
            if match == '""': line = line.replace(match, '')
            if match[1] in ['^', '_']:
                sub = re.sub(r'([^a-zA-Z0-9])\1+', r'\1', match)
                line = line.replace(match, sub if len(sub) <= 40 else '')
        lines[i] = line
    md, _ = extract_metadata_and_parts(lines)
    g, _ = extract_global_and_local_metadata(md)
    key = g['K'][0] if g['K'][0] != 'none' else 'C'
    t = [x + '\n' for x in transpose_an_abc_text(lines, Mode2Key[key]).split('\n') if x]
    md2, prefix, left, bars, right = extract_barline_and_bartext_dict(t)
    body = []
    for i in range(len(bars['V:1'])):
        line = ''
        for sym in prefix:
            if any(c.isalpha() and c not in 'ZzXx' for c in bars[sym][i]):
                line += '[' + sym + ']' + (prefix[sym] + left[sym][0] + bars[sym][0] + right[sym][0] if i == 0 else bars[sym][i] + right[sym][i])
        body.append(line + '\n')
    return md2, body


# --- NotaGen's patches (its Patchilizer: encode_train, stream mode) --------------------------------------------------------------

def split_bars(line):
    """Patchilizer.split_bars for one line: the first voice's bar, then each barline with the next voice's bar, the last barline
    and the newline joined to the last"""
    parts = list(filter(None, re.split(SPLIT_RE, line)))
    if len(parts) == 1: return parts
    if parts[0] in DELIMITERS: bars = [parts[i] + parts[i + 1] for i in range(0, len(parts), 2)]
    else: bars = [parts[0]] + [parts[i] + parts[i + 1] for i in range(1, len(parts), 2)]
    if 'V' not in bars[-1]: bars[-2] += bars[-1]; bars = bars[:-1]
    return bars


def split_patches(s):
    if len(s) % PATCH_SIZE: s = s + chr(EOS)
    return [s[i:i + PATCH_SIZE] for i in range(0, len(s), PATCH_SIZE)]


def line_patches(line):
    """a tagged line's patches, and its pieces' (first patch, first character) within it"""
    out, pieces, pos = [], [], 0
    for b in split_bars(line):
        pieces.append((len(out), pos)); out += split_patches(b); pos += len(b)
    return out, pieces


def place(pieces, offset):
    """(patch, position) within a line's patches of the character at `offset` in the line"""
    j = max(i for i, (_, s) in enumerate(pieces) if s <= offset)
    first, start = pieces[j]; d = offset - start
    return first + d // PATCH_SIZE, d % PATCH_SIZE


def windows(head, sizes, need, limit=PATCH_LENGTH):
    """windows over the body lines as stream mode reads them: [(first line, line after the last, first line scored here)], each at
    most `limit` patches with the `head` patches of metadata (and the end patch where it reaches the end), covering lines [0, need).
    Each window after the first begins halfway through the one before (NotaGen's own stream generation keeps half), so that each
    line scored has at least half a window before it, or the piece's start"""
    out, s, done = [], 0, 0
    while done < need:
        e, total = s, head
        while e < len(sizes) and total + sizes[e] + (1 if e + 1 == len(sizes) else 0) <= limit: total += sizes[e]; e += 1
        if e <= done: raise ValueError('a bar longer than a window')
        out.append((s, e, done)); done = e
        s = max(s + 1, (s + e) // 2)
    return out


# --- the notes of an ABC bar -----------------------------------------------------------------------------------------------------

SHARPS, FLATS = 'FCGDAEB', 'BEADGCF'
FIFTHS = {'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6, 'C#': 7, 'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5,
          'Gb': -6, 'Cb': -7}
LETTER = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)
NOTE_RE = re.compile(r"(\^\^|\^|__|_|=)?([A-Ga-g])([,']*)")
LEN_RE = re.compile(r'(\d*)(/*)(\d*)')
CLEF_RE = re.compile(r'(?:^|\s|clef=)(treble|bass|alto|tenor|soprano|mezzosoprano|baritone|[CFG][1-5]?)([+-](?:8|15))?(?=\s|$)')


def sounding(field):
    """semitones from written to sounding pitch that a voice or key field sets (xml2abc writes an octave clef's notes as printed,
    with '-8' after the clef; a transposing instrument with 'transpose='), or None where the field names no clef"""
    m = CLEF_RE.search(field); t = re.search(r'transpose=(-?\d+)', field)
    if not m and not t: return None
    octv = {'-8': -12, '+8': 12, '-15': -24, '+15': 24}.get(m.group(2) if m else None, 0)
    return octv + (int(t.group(1)) if t else 0)


def key_signature(k):
    """{letter: alteration} for an ABC key field ('G', 'Am', 'Bbmin', 'Ddor', 'none'; clef words after it ignored)"""
    from abctoolkit.transpose import Mode2Key
    k = k.split()[0] if (k or '').strip() else 'C'
    if k in ('none', 'Hp', 'HP'): return {}
    f = FIFTHS.get(Mode2Key.get(k, Mode2Key.get(k.replace('min', 'm'), k)), 0)
    return {c: 1 for c in SHARPS[:f]} if f > 0 else {c: -1 for c in FLATS[:-f]}


def length(s, unit):
    """an ABC length ('', '2', '/2', '/', '3/2', '//') times the unit, in quarters"""
    m = LEN_RE.fullmatch(s); num = int(m.group(1)) if m.group(1) else 1
    if not m.group(2): return unit * num
    return unit * F(num, int(m.group(3)) if m.group(3) else 2 ** len(m.group(2)))


class Voice:
    """an ABC voice read bar by bar: its key signature, unit length and a tie from the bar before carried over"""

    def __init__(self, sig, unit, compound, shift=0): self.sig, self.unit, self.compound, self.shift, self.tied = sig, unit, compound, shift, False

    def bar(self, text):
        """the bar's notes: [(first character, last character of the pitch, onset in quarters, MIDI, tied from before, chord, layer)],
        and its length. A chord is its highest note (the line's skyline); grace notes, decorations, annotations are passed over;
        "&" begins a layer over the bar (its notes are another layer's)"""
        acc = {}; out = []; t = F(0); i = 0; n = len(text); tup = None; layer = 0; longest = F(0); broken = [F(1)]

        def step(d):
            nonlocal tup
            if tup: d *= tup[0]; tup[1] -= 1; tup = tup if tup[1] > 0 else None
            d *= broken[0]; broken[0] = F(1)
            return d

        def rhythm(d, at):
            """a broken rhythm after a note ('>' dots it and halves the next, '>>' double-dots it, '<' the other way): (its length,
            where the text goes on)"""
            m = re.match(r'(>+|<+)', text[at:])
            if not m: return d, at
            k = len(m.group(1)); short = F(1, 2 ** k)
            if m.group(1)[0] == '>': broken[0] = short; return d * (2 - short), at + k
            broken[0] = 2 - short; return d * short, at + k

        def pitch(m):
            a, letter, octs = m.groups()
            base = 60 + LETTER[letter.upper()] + (12 if letter.islower() else 0) + 12 * octs.count("'") - 12 * octs.count(',')
            name = (letter.upper(), base)
            if a: acc[name] = {'^^': 2, '^': 1, '__': -2, '_': -1, '=': 0}[a]
            return base + acc.get(name, self.sig.get(letter.upper(), 0)) + self.shift

        while i < n:
            c = text[i]
            if c in '"!+{':
                j = text.find({'{': '}'}.get(c, c), i + 1); i = (j + 1) if j >= 0 else n; continue
            if c == '[' and re.match(r'\[[A-Za-z]:', text[i:i + 3]):                  # an inline field: [K:..], [L:..], [M:..]
                j = text.find(']', i); field = text[i + 1:j]
                if field.startswith('K:'):
                    self.sig = key_signature(field[2:].strip()); acc = {}
                    sh = sounding(' '.join(field[2:].split()[1:]))
                    if sh is not None: self.shift = sh
                if field.startswith('L:'): a, b = field[2:].strip().split('/'); self.unit = F(4 * int(a), int(b))
                if field.startswith('M:'): self.compound = field[2:].strip().split('/')[0] in ('6', '9', '12')
                i = j + 1; continue
            if c == '&':
                longest = max(longest, t); t = F(0); layer += 1; i += 1; continue
            if c == '(' and i + 1 < n and text[i + 1].isdigit():                     # a tuplet: (p, (p:q, (p:q:r
                m = re.match(r'\((\d+)(?::(\d*))?(?::(\d*))?', text[i:]); p = int(m.group(1))
                q = int(m.group(2)) if m.group(2) else (3 if p in (2, 4, 8) else 2 if p in (3, 6) else (3 if self.compound else 2))
                tup = [F(q, p), int(m.group(3)) if m.group(3) else p]; i += len(m.group(0)); continue
            if c == '[':                                                               # a chord: its length is its first note's
                j = text.find(']', i); inner = text[i + 1:j]
                ms = list(NOTE_RE.finditer(inner)); ps = [pitch(m) for m in ms]
                first = LEN_RE.match(inner, ms[0].end()).group(0) if ms else ''
                after = LEN_RE.match(text, j + 1).group(0)
                d = step(length(first, self.unit) * (length(after, F(1)) if after else 1))
                if ps:
                    top = max(range(len(ps)), key=lambda k: ps[k])
                    out.append((i + 1 + ms[top].start(), i + 1 + ms[top].end() - 1, t, ps[top], self.tied, True, layer))
                i = j + 1 + len(after); self.tied = i < n and text[i] == '-'
                d, i = rhythm(d, i + self.tied) if re.match(r'[<>]', text[i + self.tied:i + self.tied + 1]) else (d, i)
                t += d; continue
            if c in 'zxZX':
                m = re.match(r'[zxZX]' + LEN_RE.pattern, text[i:])
                i += len(m.group(0)); self.tied = False
                if c in 'zx': d, i = rhythm(step(length(m.group(0)[1:], self.unit)), i); t += d
                continue
            m = NOTE_RE.match(text, i)
            if m:
                mm = pitch(m); dur = LEN_RE.match(text, m.end()).group(0)
                out.append((i, m.end() - 1, t, mm, self.tied, False, layer))
                i = m.end() + len(dur); self.tied = i < n and text[i] == '-'; d = step(length(dur, self.unit))
                d, i = rhythm(d, i + self.tied) if re.match(r'[<>]', text[i + self.tied:i + self.tied + 1]) else (d, i)
                t += d; continue
            i += 1
        return out, max(longest, t)


# --- a work prepared -------------------------------------------------------------------------------------------------------------

def prepare(work_id, prompt, cache, xml2abc, score_reader):
    """a work in NotaGen's notation: {'meta', 'body', 'notes': {voice: [(line, first char, last char, onset, MIDI, chord)]}} with the
    characters' offsets in the line as tagged ("[r:i/j]" first), or a reason it could not be"""
    src, mv = source(work_id, cache)
    if not src: return 'no source'
    try: std = standard_abc(src, mv, xml2abc, score_reader)
    except Exception as e: return f'conversion: {type(e).__name__}: {e}'[:200]
    return prepare_abc(std, prompt)


def prepare_xml(xml, prompt, xml2abc):
    """a MusicXML file of our own (a piece of the repertoire) in NotaGen's notation, as prepare() makes a work's"""
    out = subprocess.run([sys.executable, '-I', xml2abc, '-d', '8', '-c', '6', '-x', xml], capture_output=True, text=True, timeout=600)
    return prepare_abc(out.stdout, prompt)


def prepare_abc(std, prompt):
    """standard ABC (xml2abc's) in NotaGen's notation: as prepare(), or a reason it could not be"""
    if 'V:' not in std: return 'xml2abc wrote no voices'
    try: md, body = notagen_lines(std)
    except Exception as e: return f'cleaning: {type(e).__name__}: {e}'[:200]
    return prepare_lines([f'%{p}\n' for p in prompt] + md, body)


def prepare_lines(meta, body):
    """the notes of NotaGen's lines (its metadata, prompt lines first, and one line a bar), as prepare_abc() reads them: also for
    lines put together here, such as a piece with another's bars in it"""
    md = [l for l in meta if not l.startswith('%')]
    head = {}
    for l in md:
        if re.match(r'[LMK]:', l): head.setdefault(l[0], l[2:].strip())
    unit = F(4) * F(head.get('L', '1/8')); compound = head.get('M', '4/4').split('/')[0] in ('6', '9', '12')
    sig = key_signature(head.get('K', 'C'))
    shifts = {l.split()[0][2:]: sounding(' '.join(l.split()[1:])) or 0 for l in md if l.startswith('V:') and l.split()}
    nb = len(body); voices = {}; notes = {}; start = F(0)
    for k, line in enumerate(body):
        tag = f'[r:{k}/{nb - k - 1}]'; length_k = F(0)
        for m in re.finditer(r'\[V:(\d+)\](.*?)(?=\[V:|$)', line.rstrip('\n')):
            v = voices.setdefault(m.group(1), Voice(sig, unit, compound, shifts.get(m.group(1), 0)))
            ns, d = v.bar(m.group(2)); length_k = max(length_k, d)
            for a, b, t, midi, tied, chord, layer in ns:
                if tied: continue
                notes.setdefault(f'{m.group(1)}.{layer}', []).append((k, len(tag) + m.start(2) + a, len(tag) + m.start(2) + b,
                                                                     float(start + t), midi, chord))
        start += length_k
    return dict(meta=meta, body=body, notes=notes)


def align(abc_notes, lines, cap=400):
    """each ABC voice's line: {voice: (part, {ABC note index: index in the line})}, the line the one whose pitches it shares most in
    order (the first `cap` notes of each); a line goes to the voice that shares most with it, and a voice sharing fewer than half
    its notes with any is left out"""
    scores = []
    for v, ns in abc_notes.items():
        a = [n[4] for n in ns[:cap]]
        for p, l in lines.items():
            sm = difflib.SequenceMatcher(None, a, [n[2] for n in l[:cap]], autojunk=False)
            blocks = sm.get_matching_blocks(); hit = sum(b.size for b in blocks)
            scores.append((hit, v, p, blocks, len(a)))
    out, used = {}, set()
    for hit, v, p, blocks, na in sorted(scores, key=lambda x: -x[0]):
        if v in out or p in used or hit < 0.5 * na: continue
        out[v] = (p, {b.a + j: b.b + j for b in blocks for j in range(b.size)}); used.add(p)
    return out


def tagged(body):
    nb = len(body); return [f'[r:{k}/{nb - k - 1}]' + l for k, l in enumerate(body)]


def scoring_input(meta, body, wanted):
    """the windows for the notes `wanted` [(line, first char, last char)]: {'windows': [[patch, ...]], 'notes': [(window, first,
    last character, as indices into the window's patches read as one string of 16-character patches)]}"""
    head = [chr(BOS) * (PATCH_SIZE - 1) + chr(EOS)] + [p for l in meta for p in split_patches(l)]
    lines = [line_patches(l) for l in tagged(body)]
    need = max(k for k, _, _ in wanted) + 1
    ws = windows(len(head), [len(p) for p, _ in lines], need)
    out_w, where = [], {}
    for wi, (s, e, done) in enumerate(ws):
        pts = list(head); first = {}
        for k in range(s, e): first[k] = len(pts); pts += lines[k][0]
        if e == len(body): pts.append(chr(BOS) + chr(EOS) * (PATCH_SIZE - 1))
        out_w.append(pts)
        for k in range(done, e): where[k] = (wi, first[k])
    notes = []
    for k, a, b in wanted:
        wi, f = where[k]; pa, qa = place(lines[k][1], a); pb, qb = place(lines[k][1], b)
        notes.append((wi, (f + pa) * PATCH_SIZE + qa, (f + pb) * PATCH_SIZE + qb))
    return dict(windows=out_w, notes=notes)


def scoring_window_ending(meta, body, wanted):
    """one window for the notes `wanted` [(line, first char, last char)], ending with the line of the last and reaching back as far
    as 1024 patches allow: {'windows': [patches], 'notes': [(0, first, last character)]}"""
    head = [chr(BOS) * (PATCH_SIZE - 1) + chr(EOS)] + [p for l in meta for p in split_patches(l)]
    lines = [line_patches(l) for l in tagged(body)]
    e = max(k for k, _, _ in wanted) + 1; s = e; total = len(head) + (1 if e == len(body) else 0)
    while s > 0 and total + len(lines[s - 1][0]) <= PATCH_LENGTH: s -= 1; total += len(lines[s][0])
    if min(k for k, _, _ in wanted) < s: raise ValueError('the notes do not fit one window')
    pts = list(head); first = {}
    for k in range(s, e): first[k] = len(pts); pts += lines[k][0]
    if e == len(body): pts.append(chr(BOS) + chr(EOS) * (PATCH_SIZE - 1))
    notes = []
    for k, a, b in wanted:
        pa, qa = place(lines[k][1], a); pb, qb = place(lines[k][1], b)
        notes.append((0, (first[k] + pa) * PATCH_SIZE + qa, (first[k] + pb) * PATCH_SIZE + qb))
    return dict(windows=[pts], notes=notes)
