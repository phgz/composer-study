"""The works of score-reader's ready-read copy as melodic lines, by the rules of TRAINING.md, for the listener's ear and the counts.

Each part of a reading (a staff, a voice in kern; a track in MIDI) becomes one line, its sounding skyline: at each onset its highest
note, and not a note that begins under a higher note of the part still sounding (an inner voice moving under a held melody note),
so that a staff that sounds chords and voices gives the line a listener follows in it. Against the top note at each onset, the
skyline is a little more predictable in four periods and the same before 1600 (held-out works, 22 November 2026). A work's final is the last note of its lowest
line (its keynote for the scale degrees). A line keeps its notes as the reading plays them; `heard_again` (catalogue version 24)
says which spans repeat bars already heard, so that counts can leave them out (`once`) while the ear hears the piece as played.

What is left out (TRAINING.md, sections 1 and 2): a reading from an editor's copy for MIDI (`midi_copy`), IMSLP's organ files
with their ornaments played out (`realized`), a work that could not be read, a line of fewer than 8 notes.

Weights (TRAINING.md, section 4; `capped`): each work weighs one at a shared level, whatever its length; no composer weighs more
than a tenth of a level and no collection more than a third, what a capped one gives up shared among the others by their works.

Only plain numbers are read from the copy (its TSV and JSON files); nothing in it is run."""
import collections, csv, io, json, os, re, tarfile

LEFT_OUT = ('midi_copy', 'realized')

Work = collections.namedtuple('Work', 'id composer collection kind label lines final heard_again flags')


def skyline(notes, eps=1e-3):
    """[(onset, dur, midi), ...] -> its sounding skyline: the highest note at each onset, less a note that begins while a higher
    note already kept still sounds"""
    top = {}
    for on, du, m in notes:
        on = round(float(on), 6)
        if on not in top or m > top[on][1]: top[on] = (float(du), int(m))
    out = []
    for on, (du, m) in sorted(top.items()):
        if out and m < out[-1][2] and out[-1][0] + out[-1][1] > on + eps: continue
        out.append((on, du, m))
    return out


def _lines(rows):
    """notes.tsv rows -> {part: its sounding skyline}"""
    by = collections.defaultdict(list)
    for r in rows: by[r['part']].append((float(r['onset']), float(r['dur']), int(r['midi'])))
    return {p: skyline(ns) for p, ns in by.items()}


def read(ready_dir, composers=None, min_notes=8, keep=()):
    """the works of the copy as Work, composer by composer, by the rules above. `composers`: only these; `keep`: keep the works
    with these flags too (e.g. {'midi_copy'}, to look at them)"""
    top = json.load(open(os.path.join(ready_dir, 'index.json'), encoding='utf-8'))['composers']
    keep = set(keep); out = []
    for composer, v in sorted(top.items()):
        if composers is not None and composer not in composers: continue
        slug = v['file'][:-len('.tar.gz')]; path = os.path.join(ready_dir, v['file'])
        if not os.path.exists(path): continue
        with tarfile.open(path) as t:
            try: listing = json.loads(t.extractfile(f'{slug}/index.json').read())
            except KeyError: continue
            for e in listing:
                if e.get('error') or 'notes.tsv' not in e.get('files', []): continue
                flags = {k: e[k] for k in LEFT_OUT if e.get(k)}
                if any(k not in keep for k in flags): continue
                rows = csv.DictReader(io.StringIO(t.extractfile(f'{slug}/{e["folder"]}/notes.tsv').read().decode('utf-8')), delimiter='\t')
                lines = {p: l for p, l in _lines(rows).items() if len(l) >= min_notes}
                if not lines: continue
                low = min(lines.values(), key=lambda l: sum(m for _, _, m in l) / len(l))
                out.append(Work(e['id'], composer, e['collection'], e['kind'], e['label'], lines, low[-1][2] % 12,
                                [tuple(x) for x in e.get('heard_again', [])], dict(flags, repeats=e.get('repeats'))))
    return out


def once(line, heard_again):
    """a line without the notes that begin in a span heard again: each bar counted once (TRAINING.md, section 3)"""
    if not heard_again: return line
    return [n for n in line if not any(a <= n[0] < b for a, b in heard_again)]


def capped(base, caps):
    """weights for items, from `base` (item -> weight), such that within each partition of `caps` ([(group_of, cap)], group_of:
    item -> group) no group's share of the whole passes its cap. A group over its cap is scaled down to it, what it gives up shared
    among the others in proportion to their weights, partition after partition, until no cap is passed. A cap that cannot be met
    (fewer groups than 1/cap) is not applied."""
    w = dict(base)
    usable = [(g, c) for g, c in caps if len({g(i) for i in w}) * c >= 1.0]
    for _ in range(500):
        moved = False
        for group_of, cap in usable:
            tot = sum(w.values()); by = collections.Counter()
            for i, x in w.items(): by[group_of(i)] += x
            over = {g for g, x in by.items() if x > cap * tot * (1 + 1e-9)}
            if not over or cap * len(over) >= 1.0: continue
            rest = sum(x for g, x in by.items() if g not in over)
            target = cap * rest / (1 - cap * len(over))                    # each capped group's total, the others' unchanged
            for i in w:
                if group_of(i) in over: w[i] *= target / by[group_of(i)]
            moved = True
        if not moved: break
    return w


def label_key(work):
    """copies of one work (the same composer and label, but for the source named in the last brackets: an archive and shelfmark,
    a collection) share a key, so that a copy is never held out apart from its twin"""
    return (work.composer, re.sub(r'\s*\([^()]*\)\s*$', '', work.label).strip().lower())


def record(ready_dir):
    """what a model was trained on, for it to say (TRAINING.md): the copy's catalogue version and score-reader commit, and the rules"""
    top = json.load(open(os.path.join(ready_dir, 'index.json'), encoding='utf-8'))
    return dict(catalogue_version=top.get('catalogue_version'), score_reader=top.get('code'), left_out=list(LEFT_OUT),
                line='sounding skyline', weights='a work weighs one; a composer at most a tenth, a collection at most a third')
