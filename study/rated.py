"""Does the ear hear what Philip hears? Piece 44's measure M0 (composer-blend, pieces/44_mercy_twenty_one_times/test44.py), now
taken with the ear trained on score-reader's catalogue: the longest stretch, in seconds, over which the mean surprise of the notes
that begin in the four seconds around each second stays under 1.5 bits (a silence counts as unsurprising). Piece 44 found it going
against his ratings on 15 pieces (Spearman rho -0.54, with an ear trained on five composers).

WRITTEN BEFORE THE NEW PIECES WERE MEASURED (22 November 2026), and not changed after. The claim: on the 15 pieces rated since
(data/rated.json, `since`: True), M0 heard by the catalogue's ear goes against the ratings (rho < 0); p from 10,000 permutations
of the ratings, one-sided. 15 pieces show only a large effect: a measure that does not pass is not shown to be useless.

A piece's notes come from its score (composer-blend's `build()`, run with the renderer on the path) or from the score its render
recorded (`*.render.json`, written by the shared renderer). Each pitched part is a line: the highest note at each onset; a part of
fewer than 20 notes or a span under 4 semitones (a drum, a drone) is not a line. Times are in seconds, as heard.

Usage: PYTHONPATH=<renderer>:<renderer>/tools:<renderer>/adapters python3 study/rated.py <ready-read copy> <composer-blend>
       <folder of render.json files> [--ear ear.npz | --works works.pickle]"""
import argparse, json, os, pickle, random, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from study import ear as E, lines as L, heldout as H, pieces as P

TABLE = os.path.join(HERE, 'data', 'rated.json')


def from_build(path): return list(P.from_build(path).values())


def from_render(path): return list(P.from_render(path).values())


def lines_of(parts): return list(P.lines_of(dict(enumerate(parts))).values())


def m0(lines, ear):
    """the longest stretch (s) whose 4-second mean pitch surprise stays under 1.5 bits, and the mean bits a note"""
    end = max(n[0] for l in lines for n in l); low = min(lines, key=lambda l: np.mean([n[2] for n in l])); final = low[-1][2] % 12
    ons = []
    for l in lines:
        for n, r in zip(l[1:], E.listen(l, final, ear)[1:]): ons.append((n[0], r[0]))
    t = np.array([a for a, b in ons]); ic = np.array([b for a, b in ons]); run = best = 0
    for s in range(int(end) + 1):
        k = (t >= s - 2) & (t < s + 2)
        if not k.any() or ic[k].mean() < 1.5: run += 1; best = max(best, run)
        else: run = 0
    return best, float(ic.mean())


def spearman(x, y):
    """Spearman's rho, ties given their mean rank"""
    def ranks(v):
        v = np.asarray(v, float); order = np.argsort(v); r = np.empty(len(v)); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]: j += 1
            r[order[i:j + 1]] = (i + j) / 2; i = j + 1
        return r
    a, b = ranks(x), ranks(y); return float(np.corrcoef(a, b)[0, 1])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('ready'); ap.add_argument('blend'); ap.add_argument('renders'); ap.add_argument('--works'); ap.add_argument('--ear', help='an ear saved by study/critic.py --build')
    a = ap.parse_args()
    if a.ear: ear = E.Long.load(a.ear); print('trained on:', ear.about, flush=True)
    else:
        works = pickle.load(open(a.works, 'rb')) if a.works else L.read(a.ready)
        print('trained on:', L.record(a.ready), flush=True)
        w = H.weights(works, None); ear = E.Long().learn(works, lambda x: w[x.id])
    rows = []
    for e in json.load(open(TABLE, encoding='utf-8'))['pieces']:
        try:                                                               # a piece made in parts: each part heard on its own
            got = []
            for section in e['sections']:
                parts = []
                for src in section:
                    parts += from_build(os.path.join(a.blend, src)) if src.endswith('.py') else from_render(os.path.join(a.renders, src))
                lines = lines_of(parts); got.append((m0(lines, ear), sum(len(l) for l in lines)))
            best = max(g[0][0] for g in got); bits = sum(g[0][1] * g[1] for g in got) / sum(g[1] for g in got)
        except Exception as x:
            print(f'{e["piece"]:4s} could not be measured: {type(x).__name__}: {str(x)[:100]}'); continue
        rows.append((e['piece'], e['rating'], e['since'], best, bits))
        print(f'{e["piece"]:4s} {e["rating"]:4.2f}  M0 {best:4d} s  ({bits:.2f} bits a note)  {"since" if e["since"] else ""}', flush=True)
    rnd = random.Random(44)
    for name, sel in (('since (the claim)', [r for r in rows if r[2]]), ('the 15 of piece 44', [r for r in rows if not r[2]]), ('all', rows)):
        if len(sel) < 4: continue
        x = [r[3] for r in sel]; y = [r[1] for r in sel]; rho = spearman(x, y)
        perm = [spearman(x, rnd.sample(y, len(y))) for _ in range(10000)]
        p = float(np.mean([q <= rho for q in perm]))
        print(f'{name:20s} {len(sel):2d} pieces  rho {rho:+.2f}  one-sided permutation p {p:.3f}')


if __name__ == '__main__': main()
