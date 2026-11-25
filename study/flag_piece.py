"""The outside ear's flags on a new piece, before Philip hears it: the notes AMT finds most surprising (a wrong-sounding note) and
the onsets it finds most surprising (a stumble in the rhythm), with their times, written down and kept from him; afterwards set
beside the moments he names. checks/ears-as-rulers-2026-11-24.md has the tests behind it and their limits: on planted wrong notes
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
            writes <folder>/FLAGS.md: the top notes by pitch surprise and the top onsets by onset surprise, each ear's bits put on
            one scale within the piece (minus its mean, over its standard deviation) and averaged over the ears that hear the note
            (NotaGen's two hear single notes only, under the prompt chosen); flags within a second of a higher one are folded into
            it. With NotaGen's scores, also its prompts ranked: whom NotaGen finds the piece closest to. Times are the notes' own: a score's seconds, or a render's as played (render.json). A render
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
    z = lambda x: (x - x.mean()) / (x.std() or 1)
    ng_ears, heard, rank = notagen_choice(folder)
    zs = [z(np.array([b[0] for b in bits[e]])) for e in ears]
    for e in ng_ears:                                                   # NotaGen's: on the notes it hears, nothing elsewhere
        idx = sorted(heard[e]); zz = np.full(len(notes), np.nan); zz[idx] = z(np.array([heard[e][i] for i in idx])); zs.append(zz)
    pitch = np.nanmean(np.vstack(zs), axis=0)
    onset_idx = [i for i in range(len(notes)) if first[i] and all(bits[e][i][3] is not None for e in ears)]
    onset = np.mean([z(np.array([bits[e][i][3] for i in onset_idx])) for e in ears], axis=0)

    def pick(order, score, key):
        out = []
        for i in order:
            if any(abs(notes[i][0] - notes[j][0]) < 1.0 for j, _ in out): continue
            out.append((i, score[key(i)]))
            if len(out) == top: break
        return out
    p = pick(sorted(range(len(notes)), key=lambda i: -pitch[i]), pitch, lambda i: i)
    k = {i: n for n, i in enumerate(onset_idx)}
    o = pick(sorted(onset_idx, key=lambda i: -onset[k[i]]), onset, lambda i: k[i])
    return meta, ears + [f'notagen_{e}' for e in ng_ears], notes, p, o, rank


def report(a):
    meta, ears, notes, p, o, rank = flags(a.folder, a.top)
    names = dict(large='AMT Large', medium='AMT Medium', notagen_x='NotaGen-X', notagen_finetune='NotaGen fine-tuned')
    nm = lambda m: NAMES[m % 12] + str(m // 12 - 1)
    lines = [f'# Flags (sealed: not for Philip before he has heard the piece)', '',
             f"From `{os.path.basename(meta['source'])}`: {', '.join(names[e] for e in ears)}. AMT hears every note, on the piano; "
             + ('NotaGen the written score, single notes only, under the prompt it finds the piece least surprising under (below). '
                if rank else '') +
             'Each ear\'s bits on one scale within the piece, averaged over the ears that hear the note; a flag within a second of '
             'a higher one is folded into it.', '',
             '## Notes (a wrong-sounding note)', '', '| | time | part | pitch | score |', '|---|---|---|---|---|']
    lines += [f'| {n + 1} | {mmss(notes[i][0])} | {notes[i][3]} | {nm(notes[i][2])} | {s:.2f} |' for n, (i, s) in enumerate(p)]
    lines += ['', '## Onsets (a stumble in the rhythm)', '', '| | time | part | pitch | score |', '|---|---|---|---|---|']
    lines += [f'| {n + 1} | {mmss(notes[i][0])} | {notes[i][3]} | {nm(notes[i][2])} | {s:.2f} |' for n, (i, s) in enumerate(o)]
    if rank:
        lines += ['', "## NotaGen's prompts (whom it finds the piece closest to)", '',
                  'Bits a single note, NotaGen-X and fine-tuned averaged; the flags above are read under the first.', '',
                  '| | prompt | bits a note |', '|---|---|---|']
        lines += [f"| {n + 1} | {pid.replace(' | ', ' / ')} | {b:.2f} |" for n, (b, pid) in enumerate(rank[:10])]
        lines += [f"| {len(rank)} (last) | {rank[-1][1].replace(' | ', ' / ')} | {rank[-1][0]:.2f} |"]
    open(os.path.join(a.folder, 'FLAGS.md'), 'w').write('\n'.join(lines) + '\n')
    print(f'FLAGS.md: {len(p)} notes, {len(o)} onsets')


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
