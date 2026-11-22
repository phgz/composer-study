"""Is the ear any good? It is trained on nine tenths of the catalogue's works and listens to the tenth held back, line by line; a
copy of a work is held out with its twin (lines.label_key). The measure: the information content (bits) of each note's pitch and
rhythm, the lower the better: an ear that expects the notes a composer writes gives them high probability.

Ears compared, each trained on the same nine tenths:
  catalogue     every work, each weighing one, a composer held to a tenth and a collection to a third (TRAINING.md, section 4)
  by notes      every work, each note weighing one (a long work weighs by its length; no caps)
  five          the five composers of piece 44's listener ear, from the catalogue's readings: Bach's chorales, Corelli's trio
                sonatas (DCML), Mendelssohn's quartets (DCML), Beethoven's quartets (DCML, ABC) and Mozart's quartets (kern)
  order 0       the catalogue's ear with no context at all: how often each interval, degree and rhythm comes (a floor to beat)
The held-out works are drawn period by period (TRAINING.md's shared levels), so that each period is heard, not only the largest.

Usage: python3 -I study/heldout.py <ready-read copy> [--works works.pickle] [--per-era 120] [--seed 24]"""
import argparse, collections, os, pickle, random, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import ear as E, eras as R, lines as L

FIVE = ('kern/bach-chorales', 'dcml/corelli', 'dcml/mendelssohn_quartets', 'dcml/ABC', 'kern/mozart-quartets')


def split(works, seed, share=0.1):
    keys = sorted({L.label_key(w) for w in works}); rnd = random.Random(seed); rnd.shuffle(keys)
    held = set(keys[:int(len(keys) * share)])
    return [w for w in works if L.label_key(w) not in held], [w for w in works if L.label_key(w) in held]


def weights(works, eras):
    base = {w.id: 1.0 for w in works}; comp = {w.id: w.composer for w in works}; col = {w.id: w.collection for w in works}
    return L.capped(base, [(comp.get, 0.1), (col.get, 1 / 3)])


def hear(work, ltm, short=True, max_lines=4, max_notes=300):
    ps, rs = [], []
    for line in sorted(work.lines.values(), key=len, reverse=True)[:max_lines]:
        for x in E.listen(line[:max_notes], work.final, ltm, short=short)[1:]:
            ps.append(x[0]); rs.append(x[1])
    return ps, rs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('ready'); ap.add_argument('--works'); ap.add_argument('--per-era', type=int, default=120)
    ap.add_argument('--seed', type=int, default=24); a = ap.parse_args()
    t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:6.0f}s]', *x, flush=True)
    works = pickle.load(open(a.works, 'rb')) if a.works else L.read(a.ready)
    print('trained on:', L.record(a.ready), flush=True)
    eras = R.table(); era = lambda w: (eras.get(w.composer) or {}).get('era', 'no period')
    train, held = split(works, a.seed)
    log(f'{len(works)} works: {len(train)} to learn from, {len(held)} held out')
    w_cat = weights(train, eras)
    ears = {}
    ears['catalogue'] = E.Long().learn(train, lambda w: w_cat[w.id]); log('catalogue ear learnt')
    ears['by notes'] = E.Long().learn(train, lambda w: sum(len(l) for l in w.lines.values())); log('by-notes ear learnt')
    five = [w for w in train if w.collection in FIVE]
    ears['five'] = E.Long().learn(five, lambda w: 1.0); log(f'five-composer ear learnt ({len(five)} works)')
    ears['order 0'] = E.Long(K=0).learn(train, lambda w: w_cat[w.id]); log('order-0 ear learnt')
    rnd = random.Random(a.seed + 1); by_era = collections.defaultdict(list)
    for w in held: by_era[era(w)].append(w)
    sample = {e: rnd.sample(ws, min(a.per_era, len(ws))) for e, ws in sorted(by_era.items())}
    rows = []
    for name, ltm in ears.items():
        for short in ((True, False) if name == 'catalogue' else (True,)):
            for e, ws in sample.items():
                P, Rh = [], []
                for w in ws:
                    p, r = hear(w, ltm, short=short); P += p; Rh += r
                rows.append((name + ('' if short else ', no short-term memory'), e, len(ws), len(P), float(np.mean(P)), float(np.mean(Rh)), float(np.mean(np.array(P) > 6)), float(np.mean(np.array(P) < 1))))
            log(f'{name}{"" if short else " (no short-term memory)"}: heard')
    print(f'\n{"ear":38s} {"period":14s} works  notes   pitch  rhythm  jolts  obvious')
    for r in rows: print(f'{r[0]:38s} {r[1]:14s} {r[2]:5d} {r[3]:6d}  {r[4]:5.2f}  {r[5]:5.2f}   {r[6]:5.1%}  {r[7]:5.1%}')
    tot = collections.defaultdict(lambda: [0, 0.0, 0.0])
    for r in rows: t = tot[r[0]]; t[0] += r[3]; t[1] += r[4] * r[3]; t[2] += r[5] * r[3]
    print('\nall periods, by notes heard:')
    for k, (n, p, q) in tot.items(): print(f'  {k:38s} {n:7d} notes  pitch {p / n:5.2f}  rhythm {q / n:5.2f}  bits a note')


if __name__ == '__main__': main()
