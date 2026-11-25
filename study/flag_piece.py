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
            python study/amt_score.py ~/models/music-large-800k  <folder>/flag_amt_inputs.jsonl -o <folder>/flag_amt_large.jsonl
            python study/amt_score.py ~/models/music-medium-800k <folder>/flag_amt_inputs.jsonl -o <folder>/flag_amt_medium.jsonl
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
            Philip's named moments against the flags: which fall within two seconds of one, and of which"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from study import pieces as P, amt as A

DRUMS = {'bd', 'sd', 'snr', 'sn', 'cy', 'cym', 'crash', 'tam', 'tri', 'wb6', 'wb6q', 'gng', 'bng', 'hc',
         'g1', 'g2', 'g3', 'g4', 'g5', 'brk'}                     # piece 74's granite blocks and brake drum, struck at a nominal 60
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


def notagen(a):
    from fractions import Fraction
    from study import notagen as G
    notes = json.load(open(os.path.join(a.folder, 'flag_notes.json')))['notes']
    X = exporter(a.module); mod = X.load(a.module); E = mod.EXPORT
    if E.get('notes'): raise SystemExit('this piece gives its notes as written, with no clock to its seconds: not matched here')
    xml = os.path.join(a.folder, 'flag_notagen.musicxml'); X.build(mod).write('musicxml', fp=xml)
    prompts = [tuple(l.strip().split('_')) for l in open(os.path.join(a.notagen, 'gradio', 'prompts.txt')) if l.strip()]
    r = G.prepare_xml(xml, prompts[0], os.path.join(a.notagen, 'data', 'xml2abc.py'))
    if isinstance(r, str): raise SystemExit(f'NotaGen could not read the score: {r}')
    md = r['meta'][3:]                                                    # what follows the three prompt lines
    org, unit = Fraction(E.get('origin', 0)), Fraction(E.get('unit', 1))
    clock = getattr(mod, E.get('clock', 'sec'))
    seconds = lambda q: float(clock(float(org + Fraction(q).limit_denominator(4096) / unit)))
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


def flags(folder, top):
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
    zs = [z(np.array([b[0] for b in bits[e]])) for e in ears]
    for e in ng_ears:                                                   # NotaGen's: on the notes it hears, nothing elsewhere
        idx = sorted(heard[e]); zz = np.full(len(notes), np.nan); zz[idx] = z(np.array([heard[e][i] for i in idx])); zs.append(zz)
    pitch = np.nanmean(np.vstack(zs), axis=0)
    onset_idx = [i for i in range(len(notes)) if first[i] and all(bits[e][i][3] is not None for e in ears)]
    onset = np.mean([z(np.array([bits[e][i][3] for i in onset_idx])) for e in ears], axis=0)

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
    return meta, ears + [f'notagen_{e}' for e in ng_ears], notes, p, o, rank


def places(source, times):
    """for each time (the score's seconds): the bar it falls in, where the module declares its notation (composer-blend's
    tools/export.py), else None"""
    try:
        X = exporter(source); mod = X.load(source); E = mod.EXPORT
        if E.get('notes'): return [None] * len(times)
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
    for t, d, m, part in notes:
        near = [r for r in rows if abs(r[1] - t) < .02 and int(r[3]) == int(m)]
        hit = [r for r in near if r[0].rstrip('xp') in (part, part.rstrip('xp'))] or near
        out.append((hit[0][0] if hit else part, str(hit[0][6]) if hit and len(hit[0]) > 6 else ''))
    return out


def report(a):
    meta, ears, notes, p, o, rank = flags(a.folder, a.top)
    names = dict(large='AMT Large', medium='AMT Medium', notagen_x='NotaGen-X', notagen_finetune='NotaGen fine-tuned')
    nm = lambda m: NAMES[m % 12] + str(m // 12 - 1)
    rows = sorted([(notes[i][0], 'note', n + 1, i, sc) for n, (i, sc) in enumerate(p)] +
                  [(notes[i][0], 'rhythm', n + 1, i, sc) for n, (i, sc) in enumerate(o)])
    src = meta['source']
    bars = places(src, [r[0] for r in rows]) if src.endswith('.py') else [None] * len(rows)
    what = passages(src, [notes[r[3]] for r in rows]) if src.endswith('.py') else [(notes[r[3]][3], '') for r in rows]
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


def compare(a):
    meta, ears, notes, p, o, rank = flags(a.folder, a.top)
    sec = lambda s: int(s.split(':')[0]) * 60 + float(s.split(':')[1])
    for s in a.moments:
        t = sec(s)
        hit = [('note', n + 1, mmss(notes[i][0])) for n, (i, _) in enumerate(p) if abs(notes[i][0] - t) <= 2] + \
              [('onset', n + 1, mmss(notes[i][0])) for n, (i, _) in enumerate(o) if abs(notes[i][0] - t) <= 2]
        print(s, '->', hit or 'no flag within two seconds')


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    x = sub.add_parser('prepare'); x.add_argument('source'); x.add_argument('checkout'); x.add_argument('-o', required=True)
    x = sub.add_parser('notagen'); x.add_argument('module'); x.add_argument('notagen'); x.add_argument('folder')
    x = sub.add_parser('report'); x.add_argument('folder'); x.add_argument('--top', type=int, default=20)
    x = sub.add_parser('compare'); x.add_argument('folder'); x.add_argument('moments', nargs='+'); x.add_argument('--top', type=int, default=20)
    a = ap.parse_args(); dict(prepare=prepare, notagen=notagen, report=report, compare=compare)[a.cmd](a)


if __name__ == '__main__':
    main()
