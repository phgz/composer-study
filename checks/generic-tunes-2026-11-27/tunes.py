"""The generic-tune test of 27 November 2026 (../generic-tunes-2026-11-27.md): each piece's tune, as its notes module writes it, heard
by the catalogue's ear with no short-term memory; the mean bits a note (pitch and rhythm), and the baseline, the share of moves of
two semitones or less.

    python3 checks/generic-tunes-2026-11-27/tunes.py <composer-blend> <ear .npz>

The tunes are read from the modules' source (ast), not by running them: each is a literal, or (36) uses `t3`, one third of a beat."""
import ast, itertools, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import numpy as np
from study import ear as E

TUNES = {   # piece: (module, constant, the parts of it taken, in order)
    '36': ('36_the_note_that_moves/moves.py', 'TUNE_A', None),
    '64b': ('64b_inside_the_mazurka/notes64.py', 'A_TUNE', None),
    '66': ('66_said_by_one_then_by_all/notes66.py', 'TUNE', None),
    '67': ('67_one_bell_retuned/notes67.py', 'SONG', ['minor']),
    '68': ('68_the_stone_and_the_storyteller/notes68.py', 'TUNE', None),
    '68b': ('68b_the_priest_and_the_voice/notes68b.py', 'TUNE', ['a', "a'", 'b', 'c']),
    '69': ('69_one_tune_many_dances/notes69.py', 'TUNE', None),
    '72': ('72_the_tune_and_the_ride/notes72.py', 'TUNE', None),
    '74b': ('74b/notes74b.py', 'TUNE', None),
}
CLOSE_64B = ['E5 .5, D5 .5, C5 1, A4 1', 'G4 3']          # bars 7 and 8 of 64b's tune, written beside A_TUNE in its TUNE
G, L, SHOWN = ['36', '68', '69'], ['64b', '67', '68b', '72', '74b'], ['66']
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def midi(name):
    m = re.fullmatch(r'([A-G])([#b]*)(-?\d)', name)
    if not m: raise ValueError(name)
    return 12 * (int(m.group(3)) + 1) + STEP[m.group(1)] + m.group(2).count('#') - m.group(2).count('b')


def constant(path, name):
    for node in ast.parse(open(path, encoding='utf-8').read()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return eval(compile(ast.Expression(node.value), path, 'eval'), {'__builtins__': {'dict': dict}}, {'t3': 1 / 3})
    raise SystemExit(f'{path}: no {name}')


def tokens(text):
    """(pitch name or None for a rest, length) from 'A4/1 D5/2 | ...', 'A4:1.5 F#4 | ...' (no length: one) or 'B4 .5, C5 .5'"""
    out = []
    if ',' in text or re.search(r'[A-G][#b]*\d \.?\d', text):
        for t in text.split(','):
            n, d = t.split(); out.append((n, float(d)))
        return out
    for t in text.replace('|', ' ').split():
        n, _, d = t.replace(':', '/').partition('/')
        out.append((None if n == 'r' else n, float(d) if d else 1.0))
    return out


def notes_of(value):
    """[(onset, length, midi)] from any of the modules' ways of writing a tune"""
    seq = []
    def walk(v):
        if isinstance(v, str): seq.extend(tokens(v))
        elif isinstance(v, tuple) and len(v) == 2 and (v[0] is None or isinstance(v[0], (int, str))) and isinstance(v[1], (int, float)):
            seq.append(v)
        else:
            for x in v: walk(x)
    walk(value)
    out, t = [], 0.0
    for n, d in seq:
        if n is not None: out.append((t, d, n if isinstance(n, int) else midi(n)))
        t += d
    return out


def tune(blend, piece):
    module, name, keys = TUNES[piece]
    v = constant(os.path.join(blend, 'pieces', module), name)
    if keys: v = [v[k] for k in keys]
    if piece == '64b': v = list(v) + CLOSE_64B
    return notes_of(v)


def ordered(m, low, high):
    """pairs (one of LOW, one of HIGH) with the LOW one's measure lower; a tie counts half"""
    return sum(1. if m[a] < m[b] else .5 if m[a] == m[b] else 0. for a in low for b in high)


def main(blend, ear_path):
    ear = E.Long.load(ear_path)
    rows = {}
    for piece in G + L + SHOWN:
        ns = tune(blend, piece)
        heard = [r for r in E.listen(ns, ns[-1][2] % 12, ear, short=False) if r is not None]
        bits = float(np.mean([p + r for p, r, _ in heard])); pitch = float(np.mean([p for p, _, _ in heard]))
        moves = np.abs(np.diff([n[2] for n in ns])); plain = float(np.mean(moves <= 2))
        rows[piece] = dict(notes=len(ns), bits=bits, pitch=pitch, rhythm=bits - pitch, plain=plain)
    print('| piece | group | notes | bits a note | of which pitch | rhythm | moves of 2 semitones or less |')
    print('|---|---|---|---|---|---|---|')
    for p, r in rows.items():
        grp = 'G' if p in G else 'L' if p in L else 'shown'
        print(f"| {p} | {grp} | {r['notes']} | {r['bits']:.2f} | {r['pitch']:.2f} | {r['rhythm']:.2f} | {r['plain']:.0%} |")
    n = len(G) * len(L)
    a = ordered({p: r['bits'] for p, r in rows.items()}, G, L)
    b = ordered({p: -r['plain'] for p, r in rows.items()}, G, L)
    print(f'\nof the {n} pairs (one plain, forgettable or generic, one liked): the bits a note order {a:g} as predicted; '
          f'the baseline, more moves of two semitones or less, {b:g}')


if __name__ == '__main__':
    main(*sys.argv[1:3])
