"""The outside ear's flags on a new piece: the notes AMT finds most surprising (a wrong-sounding note) and the onsets it finds most
surprising (a stumble in the rhythm), with their times and bars, in the order they come, for Philip to listen along. Philip, 25
November 2026: "In fact, instead of hiding the FLAGS, I'd prefer to listen along the specific flagged parts and tell how it sounds
to me. That's a better way in my opinion to operate." (Until then the list was kept from him and his own rough times set beside
it afterwards: `compare` still does that.) checks/ears-as-rulers-2026-11-24.md has the tests behind it and their limits: on planted wrong notes
in 64b, AMT Large and Medium together found 46% among the 2% they flag (the four ears together, NotaGen's two with them, 52%).
NotaGen joins them where the piece declares its notation (composer-blend's tools/export.py): it reads the written score.

  prepare   python3 study/flag_piece.py prepare <score .py | render.json> <anticipation checkout> -o <folder>
            every pitched part (a drum's part left out by its name), a pitch struck twice at once heard once, all on the piano,
            no given notes; writes <folder>/flag_amt_inputs.jsonl and flag_notes.json
  score     on the Mac, where the weights are:
            python study/amt_score.py "/Volumes/Music Libraries/models/music-large-800k"  <folder>/flag_amt_inputs.jsonl -o <folder>/flag_amt_large.jsonl
            python study/amt_score.py "/Volumes/Music Libraries/models/music-medium-800k" <folder>/flag_amt_inputs.jsonl -o <folder>/flag_amt_medium.jsonl
  notagen   python3 study/flag_piece.py notagen <notes module> <NotaGen checkout> <folder>      (after prepare)
            the piece exported as a score (composer-blend's tools/export.py, from the module's EXPORT), read as NotaGen reads a
            score, once under each of NotaGen's 112 prompts (its gradio/prompts.txt: period, composer, instrumentation): none of
            ours is among them, so the piece is read under all, and the one under which NotaGen finds it least surprising
            (fewest bits a note, NotaGen-X and the fine-tuned model averaged) is the one its flags are taken from (Philip,
            25 November 2026: "Sure, we can do that"). Each of NotaGen's notes is matched to the note of flag_notes.json it is
            (same pitch, within a quarter of a second); a note in a chord is not scored, as in the tests. Writes
            <folder>/flag_notagen_inputs.jsonl, flag_notagen_notes.json and the score it read (flag_notagen.musicxml)
            on the Mac:
            python study/notagen_score.py FINETUNE <folder>/flag_notagen_inputs.jsonl -o <folder>/flag_notagen_finetune.jsonl
            python study/notagen_score.py WEIGHTS  <folder>/flag_notagen_inputs.jsonl -o <folder>/flag_notagen_x.jsonl --verify ~/NotaGen
  report    python3 study/flag_piece.py report <folder> [--top 20]
            writes <folder>/FLAGS.md: the flagged places in the order they come (time, bar where the piece declares its
            notation, part, pitch, the passage it belongs to), from the top notes by pitch surprise and the top onsets by
            onset surprise, each ear's bits put on
            one scale within the piece (minus its mean, over its standard deviation) and averaged over the ears that hear the note
            (NotaGen's two hear single notes only, under the prompt chosen); flags within a second of a higher one are folded into
            it; nothing in the first two seconds, where the ears have heard nothing yet. With NotaGen's scores, also its
            prompts ranked: whom NotaGen finds the piece closest to. Times are the notes' own: a score's seconds, or a render's as played (render.json). A render
            may start with a short lead-in, so compare by the music, not to the hundredth
  compare   python3 study/flag_piece.py compare <folder> 1:23 2:45 ...
            Philip's named moments against the flags: which fall within two seconds of one, and of which
  layer     python3 study/flag_piece.py layer <folder> --module <notes module> -o <listening folder>/flags.json [--top 20]
            the flagged places as the walk page shows them (phgz/listening-page; the page moved there on 28 November 2026,
            Philip: "I feel like the listening-UI should be a project on its own"): in time order, each with its time,
            bar, kind, rank within its kind, part and pitch as the score names and spells them, passage, and each model's
            own rank of its note or onset (Philip: "In the UI, could we specify when it's which model exactly flagged a
            place."). Then name it in the listening folder (composer-blend's tools/listening.py --flags flags.json) and
            build the page there. The page, the score drawn, each instrument alone and the spots changed between two
            takes are listening-page's (its README)
  alone     python3 study/flag_piece.py alone <score as heard> <anticipation checkout> <folder>      (after prepare)
            each part by itself, for AMT: <folder>/flag_amt_alone_inputs.jsonl, one input a part, scored on the Mac as the
            piece is (flag_amt_alone_large.jsonl, flag_amt_alone_medium.jsonl). Philip, 25 November 2026: "if I listen to an
            instrument alone, then the sequence makes sense, but if I listen to the whole in context with the rest, then it's
            true it may sound weird. So on its layer its fine, but it's the interaction with the rest that is needs tuning."
  over      python3 study/flag_piece.py over <folder> [--bar 4] [--scale-from <reference folder>]
            the places above a fixed bar, on a reference scoring's scale held fixed: <folder>/OVER-<bar>.md (74c: 74b
            recomposed until nothing is above the bar)
  flat      python3 study/flag_piece.py flat 36=<folder> 75=<folder> ... --scale-from <reference folder> [--bar 3] [--gap 20]
                [--called-flat 36,43b,75 --liked 49,64,65,72,74,74b]
            flat stretches: where nothing unexpected happens for too long (agreed 25 November 2026). An event is a note or an onset
            at or above the bar on the reference's scale (as `over`), after the first two seconds; a flat stretch, a gap of GAP
            seconds or more without one. A line a piece: notes a second, events, the longest gap, the share of the piece in flat
            stretches and where they are; with the two groups, how many of their pairs the share orders as predicted, against
            fewer notes a second (checks/flat-stretches-2026-11-27.md: the test, written before the scores)
  together  python3 study/flag_piece.py together <folder> [--odd 1,28,34,39]
            each flagged place with everything and with its own part alone: <folder>/TOGETHER.md; with --odd, where the places
            heard as wrong stand among the rest"""
import argparse, collections, json, math, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from study import pieces as P, amt as A

DRUMS = {'bd', 'sd', 'snr', 'sn', 'cy', 'cym', 'crash', 'tam', 'tri', 'wb6', 'wb6q', 'gng', 'bng', 'hc',
         'g1', 'g2', 'g3', 'g4', 'g5', 'brk',                     # piece 74's granite blocks and brake drum, struck at a nominal 60
         'fa', 'fb', 'st'}                                        # piece 75's feet: recorded gestures, their midi a bank's key
NAMES = 'C C# D Eb E F F# G G# A Bb B'.split()
EARS = ('large', 'medium')


def pitched(parts):
    best = {}
    for name, ns in parts.items():
        if str(name).split('.')[0] in DRUMS: continue
        for n in ns:
            t, d, m = float(n[0]), float(n[1]), int(round(float(n[2])))
            if d <= 0 or not 0 <= m < 128: continue
            k = (round(t, 2), m)
            if k not in best or d > best[k][1]: best[k] = (t, d, m, str(name))
    return sorted(best.values(), key=lambda n: (n[0], n[2]))


def prepare(a):
    os.makedirs(a.o, exist_ok=True)
    notes = pitched(P.read(a.source))
    seq, where = A.sequence([n[:3] for n in notes], [], a.checkout)
    ws, pos = A.windows(seq, where, a.checkout, alone=True)
    with open(os.path.join(a.o, 'flag_amt_inputs.jsonl'), 'w') as f: f.write(json.dumps(dict(id='piece', windows=ws, notes=pos)) + '\n')
    json.dump(dict(source=os.path.abspath(a.source), notes=notes), open(os.path.join(a.o, 'flag_notes.json'), 'w'))
    print(f'{len(notes)} notes, {len(ws)} windows; now score it on the Mac (see this script)')


def key(t, m): return (round(float(t), 2), int(m))


def alone(a):
    """each part by itself, for AMT, so that each note is heard twice: with everything (`prepare`) and with its own part alone
    (Philip, 25 November 2026: "if I listen to an instrument alone, then the sequence makes sense, but if I listen to the whole in
    context with the rest, then it's true it may sound weird"). One input a part: its notes as `prepare` makes the piece's (on
    the piano, no controls given), and `index`, each note's place in the flag list. A note two parts play at once is in both.
    SOURCE is the score as it was heard; its onsets and pitches must be the flag list's, though a note may since have moved to
    another part (74b's string chords were set the right way up after its flags were made)"""
    notes = json.load(open(os.path.join(a.folder, 'flag_notes.json')))['notes']
    at = {key(n[0], n[2]): i for i, n in enumerate(notes)}
    parts = {str(name): own for name, ns in P.read(a.source).items() if (own := pitched({name: ns}))}
    heard = {key(n[0], n[2]) for own in parts.values() for n in own}
    if heard != set(at):
        raise SystemExit(f'{a.source}: {len(heard - set(at))} of its notes are not in the flag list, and {len(set(at) - heard)} '
                         'of the list are not in it: not the score the flags were made from')
    with open(os.path.join(a.folder, 'flag_amt_alone_inputs.jsonl'), 'w') as f:
        for name, own in sorted(parts.items()):
            seq, where = A.sequence([n[:3] for n in own], [], a.checkout)
            ws, pos = A.windows(seq, where, a.checkout, alone=True)
            f.write(json.dumps(dict(id=name, windows=ws, notes=pos, index=[at[key(n[0], n[2])] for n in own])) + '\n')
            print(f'{name}: {len(own)} notes, {len(ws)} window(s)')
    print(f'{sum(len(o) for o in parts.values())} notes in {len(parts)} parts (the list has {len(notes)}); now score it on the Mac')


def exporter(module):
    """composer-blend's tools/export.py, found above the notes module"""
    import importlib.util
    d = os.path.dirname(os.path.abspath(module))
    while d != os.path.dirname(d) and not os.path.exists(os.path.join(d, 'tools', 'export.py')): d = os.path.dirname(d)
    path = os.path.join(d, 'tools', 'export.py')
    if not os.path.exists(path): raise SystemExit('composer-blend\'s tools/export.py is not above this module')
    spec = importlib.util.spec_from_file_location('blend_export', path); X = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(X)
    return X


def notation_clock(mod):
    """Written quarters to performance seconds, also for explicitly written notes.

    An explicit note list supplies pitches and durations, not a missing clock.
    Require the module's declared mapping rather than assuming a fixed tempo.
    """
    from fractions import Fraction
    E = mod.EXPORT
    clock = getattr(mod, E.get('clock', 'sec'), None)
    if not callable(clock):
        raise SystemExit('the written score has no callable clock to performance seconds')
    org, unit = Fraction(E.get('origin', 0)), Fraction(E.get('unit', 1))
    if unit <= 0:
        raise SystemExit('the written score needs a positive quarter-note unit')
    return lambda q: float(clock(float(org + Fraction(q).limit_denominator(4096) / unit)))


def notagen(a):
    from fractions import Fraction
    from study import notagen as G
    notes = json.load(open(os.path.join(a.folder, 'flag_notes.json')))['notes']
    X = exporter(a.module); mod = X.load(a.module); E = mod.EXPORT
    seconds = notation_clock(mod)
    xml = os.path.join(a.folder, 'flag_notagen.musicxml'); X.build(mod).write('musicxml', fp=xml)
    prompts = [tuple(l.strip().split('_')) for l in open(os.path.join(a.notagen, 'gradio', 'prompts.txt')) if l.strip()]
    r = G.prepare_xml(xml, prompts[0], os.path.join(a.notagen, 'data', 'xml2abc.py'))
    if isinstance(r, str): raise SystemExit(f'NotaGen could not read the score: {r}')
    md = r['meta'][3:]                                                    # what follows the three prompt lines
    wanted, which = [], []
    for v in sorted(r['notes']):
        for i, (k, a_, b_, t, midi, chord) in enumerate(r['notes'][v]):
            wanted.append((k, a_, b_))
            which.append(dict(voice=v, chord=bool(chord), quarter=float(t), midi=int(midi), time=round(seconds(t), 3), flag=None))
    by_pitch = {}
    for j, n in enumerate(notes): by_pitch.setdefault(int(n[2]), []).append(j)
    pairs = sorted((abs(notes[j][0] - w['time']), wi, j) for wi, w in enumerate(which) if not w['chord']
                   for j in by_pitch.get(w['midi'], ()) if abs(notes[j][0] - w['time']) <= .25)
    used = set()
    for _, wi, j in pairs:
        if which[wi]['flag'] is None and j not in used: which[wi]['flag'] = j; used.add(j)
    with open(os.path.join(a.folder, 'flag_notagen_inputs.jsonl'), 'w') as f:
        for p in prompts:
            si = G.scoring_input([f'%{x}\n' for x in p] + md, r['body'], wanted)
            f.write(json.dumps(dict(id=' | '.join(p), prompt=list(p), windows=si['windows'], notes=si['notes'])) + '\n')
    json.dump(dict(score=os.path.basename(xml), prompts=[' | '.join(p) for p in prompts], notes=which),
              open(os.path.join(a.folder, 'flag_notagen_notes.json'), 'w'))
    single = sum(not w['chord'] for w in which)
    print(f"{len(which)} notes in NotaGen's reading, {single} single, {len(used)} matched to the {len(notes)} of flag_notes.json; "
          f"{len(si['windows'])} window(s) under each of {len(prompts)} prompts; now score it on the Mac (see this script)")


def notagen_choice(folder):
    """NotaGen's scores, if there are any: (ears, {flag note: bits} for each ear under the chosen prompt, ranking of the prompts)"""
    ears = [e for e in ('x', 'finetune') if os.path.exists(os.path.join(folder, f'flag_notagen_{e}.jsonl'))]
    if not ears: return [], {}, []
    which = json.load(open(os.path.join(folder, 'flag_notagen_notes.json')))['notes']
    scores = {e: {json.loads(l)['id']: json.loads(l)['bits'] for l in open(os.path.join(folder, f'flag_notagen_{e}.jsonl'))}
              for e in ears}
    ids = sorted(set.intersection(*(set(scores[e]) for e in ears)))
    for e in ears:                                                  # scores made from another preparation do not fit it
        off = {len(b) for b in scores[e].values()} - {len(which)}
        if off: raise SystemExit(f'flag_notagen_{e}.jsonl has {sorted(off)} notes a record, flag_notagen_notes.json {len(which)}: '
                                 'the scores were made from another preparation (prepare again, or restore the one scored)')
    mean = lambda e, pid: sum(b[0] + b[1] for w, b in zip(which, scores[e][pid]) if not w['chord']) / max(1, sum(not w['chord'] for w in which))
    rank = sorted((sum(mean(e, pid) for e in ears) / len(ears), pid) for pid in ids)
    chosen = rank[0][1]
    heard = {e: {w['flag']: b[0] + b[1] for w, b in zip(which, scores[e][chosen]) if w['flag'] is not None} for e in ears}
    return ears, heard, rank


def mmss(t): return f'{int(t // 60)}:{t % 60:04.1f}'


def surprise(folder):
    """each ear's surprise, on one scale within the piece (its bits minus their mean, over their standard deviation): (meta, the
    notes, {ear: per note, nan where the ear does not hear it}, the indices of the notes that begin an onset, {AMT ear: per
    onset}, NotaGen's prompts ranked)"""
    import numpy as np
    meta = json.load(open(os.path.join(folder, 'flag_notes.json'))); notes = meta['notes']
    inp = json.loads(open(os.path.join(folder, 'flag_amt_inputs.jsonl')).readline())
    first = [pos - 5 < 1 or inp['windows'][wi][pos - 2] != inp['windows'][wi][pos - 5] for wi, pos in inp['notes']]
    ears = [e for e in EARS if os.path.exists(os.path.join(folder, f'flag_amt_{e}.jsonl'))]
    if not ears: raise SystemExit('no scores yet')
    bits = {e: json.loads(open(os.path.join(folder, f'flag_amt_{e}.jsonl')).readline())['bits'] for e in ears}
    for e in ears:
        if len(bits[e]) != len(notes): raise SystemExit(f'flag_amt_{e}.jsonl has {len(bits[e])} notes, flag_notes.json {len(notes)}')
    z = lambda x: (x - x.mean()) / (x.std() or 1)
    ng_ears, heard, rank = notagen_choice(folder)
    pz = {e: z(np.array([b[0] for b in bits[e]])) for e in ears}
    for e in ng_ears:                                                   # NotaGen's: on the notes it hears, nothing elsewhere
        idx = sorted(heard[e]); zz = np.full(len(notes), np.nan); zz[idx] = z(np.array([heard[e][i] for i in idx])); pz[f'notagen_{e}'] = zz
    onset_idx = [i for i in range(len(notes)) if first[i] and all(bits[e][i][3] is not None for e in ears)]
    oz = {e: z(np.array([bits[e][i][3] for i in onset_idx])) for e in ears}
    return meta, notes, pz, onset_idx, oz, rank


def raw_bits(folder):
    """each AMT ear's bits as scored, not rescaled: (notes, {ear: pitch bits per note}, the indices of the notes that begin an
    onset, {ear: onset bits per such note})"""
    import numpy as np
    notes = json.load(open(os.path.join(folder, 'flag_notes.json')))['notes']
    inp = json.loads(open(os.path.join(folder, 'flag_amt_inputs.jsonl')).readline())
    first = [pos - 5 < 1 or inp['windows'][wi][pos - 2] != inp['windows'][wi][pos - 5] for wi, pos in inp['notes']]
    ears = [e for e in EARS if os.path.exists(os.path.join(folder, f'flag_amt_{e}.jsonl'))]
    if not ears: raise SystemExit(f'{folder}: no scores yet')
    bits = {e: json.loads(open(os.path.join(folder, f'flag_amt_{e}.jsonl')).readline())['bits'] for e in ears}
    for e in ears:
        if len(bits[e]) != len(notes): raise SystemExit(f'{folder}: flag_amt_{e}.jsonl has {len(bits[e])} notes, flag_notes.json {len(notes)}')
    onset_idx = [i for i in range(len(notes)) if first[i] and all(bits[e][i][3] is not None for e in ears)]
    return (notes, {e: np.array([b[0] for b in bits[e]]) for e in ears}, onset_idx,
            {e: np.array([bits[e][i][3] for i in onset_idx]) for e in ears})


def over(a):
    """the places above a fixed bar: each AMT ear's bits put on the scale of a reference scoring held fixed (its mean and
    standard deviation; by default the folder's own), averaged over the ears both have, and every note (and every onset) above
    the bar after the first two seconds, one a second as the flags take them. For a piece recomposed until nothing is left above
    the bar (74c: 74b's scale, the bar 4, then 3; Philip, 25 November 2026). Writes <folder>/OVER-<bar>.md"""
    import numpy as np
    notes, pb, onset_idx, ob = raw_bits(a.folder)
    _, rpb, _, rob = raw_bits(a.scale_from or a.folder)
    ears = [e for e in pb if e in rpb]
    z = lambda x, ref: (x - ref.mean()) / (ref.std() or 1)
    pitch = np.mean([z(pb[e], rpb[e]) for e in ears], axis=0)
    onset = dict(zip(onset_idx, np.mean([z(ob[e], rob[e]) for e in ears], axis=0)))
    start = min(n[0] for n in notes)

    def above(idx, score):
        out = []
        for i in sorted(idx, key=lambda i: -score(i)):
            if score(i) < a.bar: break
            if notes[i][0] < start + 2.0 or any(abs(notes[i][0] - notes[j][0]) < 1.0 for j in out): continue
            out.append(i)
        return out
    rows = [(i, 'note', float(pitch[i])) for i in above(range(len(notes)), lambda i: pitch[i])]
    rows += [(i, 'rhythm', float(onset[i])) for i in above(onset_idx, lambda i: onset[i])]
    rows.sort(key=lambda r: notes[r[0]][0])
    meta = json.load(open(os.path.join(a.folder, 'flag_notes.json')))
    where = passages(meta.get('source', ''), [notes[r[0]] for r in rows])
    nm = lambda m: NAMES[m % 12] + str(m // 12 - 1)
    exp = {}
    for e in ears:
        got = json.loads(open(os.path.join(a.folder, f'flag_amt_{e}.jsonl')).readline()).get('expect')
        if got: exp[e] = got

    def expected(i, kind):
        """what the ears expected there, their probabilities averaged: the three likeliest"""
        if not exp: return ''
        pool = collections.defaultdict(float)
        for e, got in exp.items():
            for v, p in (got[i][0] if kind == 'note' else got[i][1] or []): pool[v] += p / len(exp)
        top = sorted(pool.items(), key=lambda x: -x[1])[:3]
        if kind == 'note': return ', '.join(f'{nm(int(v))} {p:.0%}' for v, p in top)
        return ', '.join(f'{v:+.2f} s {p:.0%}' for v, p in top)
    ref = os.path.relpath(a.scale_from, a.folder) if a.scale_from else 'this folder'
    lines = [f'# Above {a.bar:g}, on the scale of {ref}', '',
             f"{', '.join(EAR_NAMES[e] for e in ears)}; each note's surprise (or its onset's, **rhythm**) on the reference's scale, "
             f'averaged over the ears; one place a second, as the flags take them, after the first two seconds. **AMT expected**: '
             'where it was scored with --expect, its likeliest pitches there (a note) or onsets (a rhythm, in seconds from the note\'s '
             'own: negative, earlier), the ears\' probabilities averaged.', '',
             '| time | flag | pitch | part | passage | surprise | AMT expected |', '|---|---|---|---|---|---|---|']
    for (i, kind, s), (part, passage) in zip(rows, where):
        lines.append(f'| {mmss(notes[i][0])} | {kind} | {nm(notes[i][2])} | {part} | {passage} | {s:.1f} | {expected(i, kind)} |')
    n_note = sum(r[1] == 'note' for r in rows)
    lines += ['', f'{len(rows)} places: {n_note} notes, {len(rows) - n_note} onsets.']
    open(os.path.join(a.folder, f'OVER-{a.bar:g}.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[4:]))


def flat_measures(folder, ref, bar, gap):
    """one piece's flat stretches: every note (pitch) and onset (rhythm) on the reference scoring's scale, the ears averaged,
    as `over` puts them; an event is one at or above the bar, after the first two seconds; a flat stretch is a gap of at least
    GAP seconds between two events, or between the start (two seconds in) and the first, or between the last and the last onset.
    Returns notes a second, the events, the longest gap, the share of the piece (two seconds in to the last onset) in flat
    stretches, and the stretches themselves"""
    import numpy as np
    notes, pb, onset_idx, ob = raw_bits(folder)
    _, rpb, _, rob = raw_bits(ref)
    ears = [e for e in pb if e in rpb]
    z = lambda x, r: (x - r.mean()) / (r.std() or 1)
    pitch = np.mean([z(pb[e], rpb[e]) for e in ears], axis=0)
    onset = np.mean([z(ob[e], rob[e]) for e in ears], axis=0)
    start, last = min(n[0] for n in notes), max(n[0] for n in notes)
    t0 = start + 2.0
    times = sorted({notes[i][0] for i in range(len(notes)) if pitch[i] >= bar and notes[i][0] >= t0} |
                   {notes[i][0] for i, s in zip(onset_idx, onset) if s >= bar and notes[i][0] >= t0})
    edges = [t0] + times + [last]
    gaps = [(a, b) for a, b in zip(edges, edges[1:]) if b - a >= gap]
    span = last - t0
    return dict(density=len(notes) / (last - start), events=len(times), longest=max(b - a for a, b in zip(edges, edges[1:])),
                share=sum(b - a for a, b in gaps) / span, stretches=gaps, span=span)


def pairs_ordered(m, high, low):
    """of the pairs (one of HIGH, one of LOW), how many have the HIGH one's measure higher (a tie counts half)"""
    return sum(1.0 if m[h] > m[l] else .5 if m[h] == m[l] else 0. for h in high for l in low)


def flat(a):
    """flat stretches across pieces, and the test of 27 November 2026 (composer-study checks/flat-stretches-2026-11-27.md):
    each LABEL=FOLDER a line, then, with --called-flat and --liked, how many of the pairs (one he called flat, one he liked) the
    measure orders as predicted (the flat one flatter), against the baseline of fewer notes a second"""
    pieces = dict(x.split('=', 1) for x in a.pieces)
    m = {k: flat_measures(f, a.scale_from, a.bar, a.gap) for k, f in pieces.items()}
    print(f'bar {a.bar:g} on the scale of {a.scale_from}; a flat stretch is {a.gap:g} s or more without an event\n')
    print('| piece | notes a second | events | longest gap | share in flat stretches | the stretches |')
    print('|---|---|---|---|---|---|')
    for k, r in m.items():
        st = '; '.join(f'{mmss(x)}–{mmss(y)}' for x, y in r['stretches']) or '—'
        print(f"| {k} | {r['density']:.1f} | {r['events']} | {r['longest']:.0f} s | {r['share']:.0%} | {st} |")
    if a.called_flat and a.liked:
        F, L = a.called_flat.split(','), a.liked.split(',')
        n = len(F) * len(L)
        share = pairs_ordered({k: r['share'] for k, r in m.items()}, F, L)
        sparse = pairs_ordered({k: -r['density'] for k, r in m.items()}, F, L)
        print(f'\nof the {n} pairs (one called flat, one liked): the share in flat stretches orders {share:g} as predicted; '
              f'the baseline, fewer notes a second, {sparse:g}')


def own_ranks(notes, idx, scores):
    """{note index: its rank by one ear's scores (1 the most surprising)}, among the notes after the first two seconds that the
    ear hears"""
    start = min(n[0] for n in notes)
    keep = [(i, s) for i, s in zip(idx, scores) if notes[i][0] >= start + 2.0 and s == s]
    return {i: n + 1 for n, (i, s) in enumerate(sorted(keep, key=lambda x: -x[1]))}


def flags(folder, top):
    import numpy as np
    meta, notes, pz, onset_idx, oz, rank = surprise(folder)
    pitch = np.nanmean(np.vstack(list(pz.values())), axis=0)
    onset = np.mean(list(oz.values()), axis=0)

    start = min(n[0] for n in notes)

    def pick(order, score, key):
        out = []
        for i in order:
            if notes[i][0] < start + 2.0: continue                     # the first two seconds: the ears have heard nothing
            if any(abs(notes[i][0] - notes[j][0]) < 1.0 for j, _ in out): continue   # yet to be surprised against
            out.append((i, score[key(i)]))
            if len(out) == top: break
        return out
    p = pick(sorted(range(len(notes)), key=lambda i: -pitch[i]), pitch, lambda i: i)
    k = {i: n for n, i in enumerate(onset_idx)}
    o = pick(sorted(onset_idx, key=lambda i: -onset[k[i]]), onset, lambda i: k[i])
    return meta, list(pz), notes, p, o, rank


def places(source, times):
    """for each time (the score's seconds): the bar it falls in, where the module declares its notation (composer-blend's
    tools/export.py), else None"""
    try:
        X = exporter(source); mod = X.load(source); E = mod.EXPORT
        notation_clock(mod)                                              # explicit notes may still declare a usable clock
        from fractions import Fraction
        s = X.build(mod); part = s.parts[0]; unit = Fraction(E['unit']).limit_denominator(16)
        starts = [(float(m.getOffsetBySite(part)), m.number) for m in part.getElementsByClass('Measure')]
        beat = X.clock(mod, E['end'])
        out = []
        for t in times:
            qq = beat(t) * float(unit)
            out.append(max((o, n) for o, n in starts if o <= qq + 1e-6)[1] if qq >= 0 else 1)
        return out
    except (SystemExit, Exception): return [None] * len(times)


def passages(source, notes):
    """for each flagged note (seconds, length, midi, part): (the part that plays it now, the passage its row of the module's EV
    names), the row found by part, time and pitch, or by time and pitch alone where the module has since moved the note to
    another part (74b's chords set the right way up after its flags were scored)"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('piece_for_flags', source); mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, os.path.dirname(source)); spec.loader.exec_module(mod)
        rows = mod.EV
    except Exception: return [(n[3], '') for n in notes]
    out = []
    same = lambda r, part: r[0].rstrip('xp') in (part, part.rstrip('xp'))
    for t, d, m, part in notes:
        near = [r for r in rows if abs(r[1] - t) < .02 and int(r[3]) == int(m)]
        hit = [r for r in near if same(r, part)] or near
        if not hit:                                                     # the note since changed: the passage its part is in then
            there = sorted((r for r in rows if abs(r[1] - t) < 1.0 and same(r, part)), key=lambda r: abs(r[1] - t))
            out.append((part, str(there[0][6]) if there and len(there[0]) > 6 else '')); continue
        out.append((hit[0][0], str(hit[0][6]) if len(hit[0]) > 6 else ''))
    return out


def listing(folder, top, source=None):
    """the flagged places in time order, as FLAGS.md lists them: (meta, ears, NotaGen's prompts ranked, the notes, rows), each row
    a dict: t, kind ('note' or 'rhythm'), rank within its kind, i (the note's index), score, bar, part (the module's), passage,
    and ears: each ear's own rank of that note (or onset), None where the ear does not hear it"""
    meta, ears, notes, p, o, rank = flags(folder, top)
    _, _, pz, onset_idx, oz, _ = surprise(folder)
    own = dict(note={e: own_ranks(notes, range(len(notes)), s) for e, s in pz.items()},
               rhythm={e: own_ranks(notes, onset_idx, s) for e, s in oz.items()})
    rows = sorted([(notes[i][0], 'note', n + 1, i, sc) for n, (i, sc) in enumerate(p)] +
                  [(notes[i][0], 'rhythm', n + 1, i, sc) for n, (i, sc) in enumerate(o)])
    src = source or meta['source']
    bars = places(src, [r[0] for r in rows]) if src.endswith('.py') else [None] * len(rows)
    what = passages(src, [notes[r[3]] for r in rows]) if src.endswith('.py') else [(notes[r[3]][3], '') for r in rows]
    out = [dict(t=float(t), kind=kind, rank=rk, i=i, score=float(sc), bar=b, part=pt, passage=w,
                ears={e: r.get(i) for e, r in own[kind].items()})
           for (t, kind, rk, i, sc), b, (pt, w) in zip(rows, bars, what)]
    return meta, ears, rank, notes, out


EAR_NAMES = dict(large='AMT Large', medium='AMT Medium', notagen_x='NotaGen-X', notagen_finetune='NotaGen fine-tuned')


def report(a):
    meta, ears, rank, notes, listed = listing(a.folder, a.top)
    src = meta['source']
    names = EAR_NAMES
    nm = lambda m: NAMES[m % 12] + str(m // 12 - 1)
    rows = [(r['t'], r['kind'], r['rank'], r['i'], r['score']) for r in listed]
    bars = [r['bar'] for r in listed]; what = [(r['part'], r['passage']) for r in listed]
    p = [r for r in listed if r['kind'] == 'note']; o = [r for r in listed if r['kind'] == 'rhythm']
    lines = ['# Flags: the places to listen to', '',
             f"From `{os.path.basename(src)}`: {', '.join(names[e] for e in ears)}. AMT hears every note, on the piano; "
             + ('NotaGen the written score, single notes only, under the prompt it finds the piece least surprising under (below). '
                if rank else '') +
             'Each ear\'s bits on one scale within the piece, averaged over the ears that hear the note; a flag within a second of '
             'a higher one is folded into it. **note**: a note the ears find most surprising (a wrong-sounding note?); '
             '**rhythm**: an onset AMT finds most surprising (a stumble?). The rank is within its kind (1 the most surprising); '
             "the times are the score's, which the render keeps.", '',
             '| time | bar | flag | rank | part | pitch | passage | score |', '|---|---|---|---|---|---|---|---|']
    lines += [f"| {mmss(t)} | {b if b is not None else ''} | {kind} | {rk} | {pt} | {nm(notes[i][2])} | {w} | {sc:.2f} |"
              for (t, kind, rk, i, sc), b, (pt, w) in zip(rows, bars, what)]
    if rank:
        lines += ['', "## NotaGen's prompts (whom it finds the piece closest to)", '',
                  'Bits a single note, NotaGen-X and fine-tuned averaged; the note flags are read under the first.', '',
                  '| | prompt | bits a note |', '|---|---|---|']
        lines += [f"| {n + 1} | {pid.replace(' | ', ' / ')} | {b:.2f} |" for n, (b, pid) in enumerate(rank[:10])]
        lines += [f"| {len(rank)} (last) | {rank[-1][1].replace(' | ', ' / ')} | {rank[-1][0]:.2f} |"]
    open(os.path.join(a.folder, 'FLAGS.md'), 'w').write('\n'.join(lines) + '\n')
    print(f'FLAGS.md: {len(p)} notes, {len(o)} onsets, {len(rows)} places')


def display(source):
    """part -> its name in the score (the module's EXPORT names; of a keyboard's two staves, the hand), else the part"""
    try:
        X = exporter(source); E = X.load(source).EXPORT
    except (SystemExit, Exception): return lambda p: p
    names, hand = E.get('names', {}), {}
    for group, members in E.get('groups', []):
        if len(members) == 2:
            kb = any(w in group.lower() for w in ('piano', 'organ', 'harpsichord', 'celesta', 'harp'))
            hand.update(zip(members, ('right hand', 'left hand') if kb else ('upper staff', 'lower staff')))
    return lambda p: (names.get(p) or names.get(p.rstrip('xp')) or p) + (f', {hand[p]}' if p in hand else '')


def speller(source):
    """(seconds, midi) -> the pitch as the score spells it there (the key the module's EXPORT gives at that time), else by NAMES"""
    plain = lambda m: NAMES[m % 12][0] + NAMES[m % 12][1:].replace('b', '♭').replace('#', '♯') + str(m // 12 - 1)
    try:
        X = exporter(source); mod = X.load(source); E = mod.EXPORT
        keys = sorted(E.get('keys', []), key=lambda k: k[0])
        if not keys: return lambda t, m: plain(m)
        notation_clock(mod)
        beat = X.clock(mod, E['end'])
    except (SystemExit, Exception): return lambda t, m: plain(m)
    def f(t, m):
        u = E.get('origin', 0) + beat(t); k = [x for x in keys if x[0] <= u + 1e-6] or keys[:1]; k = k[-1]
        return X.spell(int(m), k[1], len(k) > 2 and k[2] == 'minor').replace('#', '♯').replace('-', '♭')
    return f


def layer(a):
    """the flagged places as listening-page's walk page shows them: flags.json (its README, "A listening folder")"""
    meta, ears, rank, notes, rows = listing(a.folder, a.top, a.module)
    name, spell = display(a.module), speller(a.module)
    out = [dict(t=round(r['t'], 3), bar=r['bar'], kind=r['kind'], rank=r['rank'], part=name(r['part']),
                pitch=spell(r['t'], notes[r['i']][2]), passage=r['passage'], ears=r['ears']) for r in rows]
    foot = (f"{len(rows)} places from {', '.join(ears)}, ranked within each kind, 1 the most surprising; "
            'nothing in the first two seconds.')
    with open(a.o, 'w', encoding='utf-8') as f:
        json.dump(dict(schema=1, source=os.path.abspath(a.module), ears=ears, earNames=EAR_NAMES, top=a.top, foot=foot,
                       rows=out), f, ensure_ascii=False, indent=1)
    print(f"{a.o}: {len(out)} places ({sum(r['kind'] == 'note' for r in out)} notes, {sum(r['kind'] == 'rhythm' for r in out)} "
          f"onsets) from {', '.join(EAR_NAMES.get(e, e) for e in ears)}")


def compare(a):
    meta, ears, notes, p, o, rank = flags(a.folder, a.top)
    sec = lambda s: int(s.split(':')[0]) * 60 + float(s.split(':')[1])
    for s in a.moments:
        t = sec(s)
        hit = [('note', n + 1, mmss(notes[i][0])) for n, (i, _) in enumerate(p) if abs(notes[i][0] - t) <= 2] + \
              [('onset', n + 1, mmss(notes[i][0])) for n, (i, _) in enumerate(o) if abs(notes[i][0] - t) <= 2]
        print(s, '->', hit or 'no flag within two seconds')


WITH_REST, ALONE_TOO = 1.0, 2.0        # a part's surprise alone, on its scale within the piece: under 1 the line makes sense by
                                        # itself and the place is surprising only with the rest; 2 or more, the line itself is


def first_of_onset(windows, pos):
    """for each scored note, the index (in the same list) of the first note that shares its onset token"""
    out = []
    for k, (wi, p) in enumerate(pos):
        out.append(k if not out or p - 5 < 1 or windows[wi][p - 2] != windows[wi][p - 5] else out[-1])
    return out


def alone_surprise(folder, notes):
    """the AMT ears' surprise at each note with its own part alone: {(part, note index): z} for the pitches and for the onsets
    (each note given its onset's, the onset's first note in that part), each ear's bits on one scale over all the parts, then
    averaged over the ears. A part's first two seconds are left out (nothing of it heard yet), as the flags leave out the
    piece's"""
    import numpy as np
    inputs = [json.loads(l) for l in open(os.path.join(folder, 'flag_amt_alone_inputs.jsonl'))]
    path = lambda e: os.path.join(folder, f'flag_amt_alone_{e}.jsonl')
    ears = [e for e in EARS if os.path.exists(path(e))]
    if not ears: raise SystemExit('no scores of the parts alone yet')
    pitch, onset = {}, {}
    for e in ears:
        got = {d['id']: d['bits'] for d in map(json.loads, open(path(e)))}
        p, o, of = {}, {}, {}
        for inp in inputs:
            b = got.get(inp['id'])
            if b is None or len(b) != len(inp['index']): raise SystemExit(f"{path(e)}: {inp['id']} is not the prepared part")
            first = first_of_onset(inp['windows'], inp['notes']); t0 = min(notes[i][0] for i in inp['index'])
            for k, i in enumerate(inp['index']):
                if notes[i][0] < t0 + 2.0: continue
                p[(inp['id'], i)] = b[k][0]
                if b[first[k]][3] is not None: of[(inp['id'], i)] = (inp['id'], inp['index'][first[k]])
                if first[k] == k and b[k][3] is not None: o[(inp['id'], i)] = b[k][3]
        for got_, into, src in ((p, pitch, None), (o, onset, of)):
            x = np.array(list(got_.values())); z = dict(zip(got_, (x - x.mean()) / (x.std() or 1)))
            for k in (src or z):
                v = z.get(src[k]) if src else z[k]
                if v is not None: into.setdefault(k, []).append(v)
    mean = lambda d: {k: float(np.mean(v)) for k, v in d.items() if len(v) == len(ears)}
    return ears, mean(pitch), mean(onset)


def together(a):
    """each flagged place heard with everything and with its own part alone: the AMT ears' surprise both ways, and where it
    falls. Writes TOGETHER.md; with --odd (the places a listener heard as wrong, by their numbers in time order), how those
    places stand among the rest: by their surprise alone (the lowest first) and by how much more surprising they are with
    everything than alone (the most first), each with the share of every set of as many places that ranks as low or lower"""
    import numpy as np
    from itertools import combinations
    meta, _, _, notes, listed = listing(a.folder, a.top)
    _, _, pz, onset_idx, oz, _ = surprise(a.folder)
    ears, lp, lo = alone_surprise(a.folder, notes)
    k = {i: n for n, i in enumerate(onset_idx)}
    parts_of = {}
    for (part, i) in lp: parts_of.setdefault(i, []).append(part)
    nm = lambda m: NAMES[m % 12] + str(m // 12 - 1)
    rows = []
    for n, r in enumerate(listed):
        i = r['i']
        whole = float(np.mean([pz[e][i] for e in ears])) if r['kind'] == 'note' else float(np.mean([oz[e][k[i]] for e in ears]))
        each = {p: (lp if r['kind'] == 'note' else lo).get((p, i)) for p in sorted(parts_of.get(i, []))}
        each = {p: v for p, v in each.items() if v is not None}
        lone = max(each.values()) if each else float('nan')
        where = ('' if lone != lone else 'with the rest' if lone < WITH_REST else 'alone too' if lone >= ALONE_TOO else 'between')
        rows.append(dict(place=n + 1, t=r['t'], kind=r['kind'], pitch=nm(notes[i][2]), whole=whole, each=each, alone=lone,
                         gap=whole - lone, where=where))
    lines = ['# Each flag with everything, and with its own part alone', '',
             f"From `flag_amt_alone_*.jsonl` ({', '.join(EAR_NAMES[e] for e in ears)}): each part's notes read by themselves, as the "
             "flags read the whole piece (every note on the piano). The surprise of a place's note (or, for **rhythm**, its onset) "
             "on one scale within the piece, both ways: **with everything** as the flags have it, **alone** in each part that plays "
             "it (a part's first two seconds have no number). A place is **with the rest** where every part that plays its note "
             f"makes sense alone (under {WITH_REST:g}): what is surprising is how the part meets the others. **Alone too** where "
             f"one part is surprising by itself ({ALONE_TOO:g} or more): the line itself. Places numbered in time order, as on the "
             'walk page.', '',
             '| place | time | flag | pitch | with everything | alone, by part | where |', '|---|---|---|---|---|---|---|']
    for r in rows:
        each = ', '.join(f'{p} {v:.1f}' for p, v in sorted(r['each'].items(), key=lambda x: -x[1])) or 'none'
        lines.append(f"| {r['place']} | {mmss(r['t'])} | {r['kind']} | {r['pitch']} | {r['whole']:.1f} | {each} | {r['where']} |")
    counts = collections.Counter(r['where'] for r in rows)
    lines += ['', ', '.join(f'{v} {w or "with no number alone"}' for w, v in counts.most_common()) + '.']
    if a.odd:
        odd = [int(x) for x in a.odd.split(',')]
        ok = [r for r in rows if r['alone'] == r['alone']]
        lines += ['', f"## The places heard as wrong ({', '.join(map(str, odd))})", '']
        for name, score, low in (('alone', 'alone', True), ('with everything less alone', 'gap', False)):
            order = sorted(ok, key=lambda r: r[score] if low else -r[score]); rank = {r['place']: n + 1 for n, r in enumerate(order)}
            mine = [rank[p] for p in odd if p in rank]; total = sum(mine)
            share = sum(1 for c in combinations(range(1, len(ok) + 1), len(mine)) if sum(c) <= total) / math.comb(len(ok), len(mine))
            lines.append(f"- By {name} ({'the lowest' if low else 'the most'} first), of {len(ok)} places: ranks "
                         f"{', '.join(f'{p}: {rank[p]}' for p in odd if p in rank)}; "
                         f"of every set of {len(mine)} places, {share:.1%} rank as near the first or nearer, added up.")
    open(os.path.join(a.folder, 'TOGETHER.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[4:]))


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    x = sub.add_parser('prepare'); x.add_argument('source'); x.add_argument('checkout'); x.add_argument('-o', required=True)
    x = sub.add_parser('over'); x.add_argument('folder'); x.add_argument('--bar', type=float, default=4.0)
    x.add_argument('--scale-from', help='a scored flags folder whose scale is held fixed (by default the folder itself)')
    x = sub.add_parser('alone'); x.add_argument('source'); x.add_argument('checkout'); x.add_argument('folder')
    x = sub.add_parser('together'); x.add_argument('folder'); x.add_argument('--top', type=int, default=20)
    x.add_argument('--odd', help='the places heard as wrong, by their numbers: 1,28,34,39')
    x = sub.add_parser('notagen'); x.add_argument('module'); x.add_argument('notagen'); x.add_argument('folder')
    x = sub.add_parser('report'); x.add_argument('folder'); x.add_argument('--top', type=int, default=20)
    x = sub.add_parser('compare'); x.add_argument('folder'); x.add_argument('moments', nargs='+'); x.add_argument('--top', type=int, default=20)
    x = sub.add_parser('flat'); x.add_argument('pieces', nargs='+', help='LABEL=a scored flags folder')
    x.add_argument('--scale-from', required=True, help='a scored flags folder whose scale is held fixed for every piece')
    x.add_argument('--bar', type=float, default=3.0); x.add_argument('--gap', type=float, default=20.0)
    x.add_argument('--called-flat', dest='called_flat'); x.add_argument('--liked')
    x = sub.add_parser('layer'); x.add_argument('folder'); x.add_argument('--module', required=True); x.add_argument('-o', required=True)
    x.add_argument('--top', type=int, default=20)
    a = ap.parse_args(); dict(prepare=prepare, over=over, alone=alone, together=together, notagen=notagen, report=report, compare=compare, layer=layer, flat=flat)[a.cmd](a)


if __name__ == '__main__':
    main()
