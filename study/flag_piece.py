"""The outside ear's flags on a new piece, before Philip hears it: the notes AMT finds most surprising (a wrong-sounding note) and
the onsets it finds most surprising (a stumble in the rhythm), with their times, written down and kept from him; afterwards set
beside the moments he names. checks/ears-as-rulers-2026-11-24.md has the tests behind it and their limits: on planted wrong notes
in 64b, AMT Large and Medium together found 46% among the 2% they flag (the four ears together, NotaGen's two with them, 52%).
NotaGen is not used here yet: it reads a written score, and pieces are not exported to one yet.

  prepare   python3 study/flag_piece.py prepare <score .py | render.json> <anticipation checkout> -o <folder>
            every pitched part (a drum's part left out by its name), a pitch struck twice at once heard once, all on the piano,
            no given notes; writes <folder>/flag_amt_inputs.jsonl and flag_notes.json
  score     on the Mac, where the weights are:
            python study/amt_score.py ~/models/music-large-800k  <folder>/flag_amt_inputs.jsonl -o <folder>/flag_amt_large.jsonl
            python study/amt_score.py ~/models/music-medium-800k <folder>/flag_amt_inputs.jsonl -o <folder>/flag_amt_medium.jsonl
  report    python3 study/flag_piece.py report <folder> [--top 20]
            writes <folder>/FLAGS.md: the top notes by pitch surprise and the top onsets by onset surprise, each ear's bits put on
            one scale within the piece (minus its mean, over its standard deviation) and averaged; flags within a second of a higher
            one are folded into it. Times are the notes' own: a score's seconds, or a render's as played (render.json). A render
            may start with a short lead-in, so compare by the music, not to the hundredth
  compare   python3 study/flag_piece.py compare <folder> 1:23 2:45 ...
            Philip's named moments against the flags: which fall within two seconds of one, and of which"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from study import pieces as P, amt as A

DRUMS = {'bd', 'sd', 'snr', 'sn', 'cy', 'cym', 'crash', 'tam', 'tri', 'wb6', 'wb6q', 'gng', 'bng', 'hc'}
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
    pitch = np.mean([z(np.array([b[0] for b in bits[e]])) for e in ears], axis=0)
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
    return meta, ears, notes, p, o


def report(a):
    meta, ears, notes, p, o = flags(a.folder, a.top)
    nm = lambda m: NAMES[m % 12] + str(m // 12 - 1)
    lines = [f'# Flags (sealed: not for Philip before he has heard the piece)', '',
             f"From `{os.path.basename(meta['source'])}`, AMT {' and '.join(e.capitalize() for e in ears)}, every note on the piano. "
             'Each ear\'s bits on one scale within the piece, averaged; a flag within a second of a higher one is folded into it.', '',
             '## Notes (a wrong-sounding note)', '', '| | time | part | pitch | score |', '|---|---|---|---|---|']
    lines += [f'| {n + 1} | {mmss(notes[i][0])} | {notes[i][3]} | {nm(notes[i][2])} | {s:.2f} |' for n, (i, s) in enumerate(p)]
    lines += ['', '## Onsets (a stumble in the rhythm)', '', '| | time | part | pitch | score |', '|---|---|---|---|---|']
    lines += [f'| {n + 1} | {mmss(notes[i][0])} | {notes[i][3]} | {nm(notes[i][2])} | {s:.2f} |' for n, (i, s) in enumerate(o)]
    open(os.path.join(a.folder, 'FLAGS.md'), 'w').write('\n'.join(lines) + '\n')
    print(f'FLAGS.md: {len(p)} notes, {len(o)} onsets')


def compare(a):
    meta, ears, notes, p, o = flags(a.folder, a.top)
    sec = lambda s: int(s.split(':')[0]) * 60 + float(s.split(':')[1])
    for s in a.moments:
        t = sec(s)
        hit = [('note', n + 1, mmss(notes[i][0])) for n, (i, _) in enumerate(p) if abs(notes[i][0] - t) <= 2] + \
              [('onset', n + 1, mmss(notes[i][0])) for n, (i, _) in enumerate(o) if abs(notes[i][0] - t) <= 2]
        print(s, '->', hit or 'no flag within two seconds')


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    x = sub.add_parser('prepare'); x.add_argument('source'); x.add_argument('checkout'); x.add_argument('-o', required=True)
    x = sub.add_parser('report'); x.add_argument('folder'); x.add_argument('--top', type=int, default=20)
    x = sub.add_parser('compare'); x.add_argument('folder'); x.add_argument('moments', nargs='+'); x.add_argument('--top', type=int, default=20)
    a = ap.parse_args(); dict(prepare=prepare, report=report, compare=compare)[a.cmd](a)


if __name__ == '__main__':
    main()
