"""The quote test, the comparison: how surprised each outside ear is by eight bars of a real mazurka put into piece 64b, against 64b's
own music, and whether it knows the very notes (their own key against a whole tone higher).

  a stretch's bits  the mean bits a note over its notes (NotaGen: single notes, a chord's top note left out; AMT: every note)
  the quote         its bars 3 to 8 (by the third bar, an ear that knows the piece has heard enough of it to know it)
  64b's own         every stretch of six bars of 64b as written (the glitch test's "64b | as written" scores), bars 1 to 6, 2 to 7,
                    ..., 155 to 160: where the quote's mean falls among them (the share of them less surprising than it)
  key               own key minus a tone higher, for each quote, in 64b and alone: below 0, the quote is less surprising in the key
                    it was written in, which only knowing the notes themselves explains

Run: python3 compare_quote.py      (reads quote.json, glitch.json and the score files beside it; writes compare_quote.json)"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EARS = [('NotaGen-X', 'notagen_x', 'ng'), ('NotaGen fine-tuned', 'notagen_finetune', 'ng'),
        ('AMT Large', 'amt_large', 'amt'), ('AMT Medium', 'amt_medium', 'amt')]
FROM = 6.0                                                                  # the quote's bars 3 to 8: from its seventh beat


def load(path):
    out = {}
    for line in open(path):
        x = json.loads(line); out[x['id']] = x['bits']
    return out


def note_bits(b, kind): return b[0] + b[1] if kind == 'ng' else b[0]


def own_stretches(glitch_scores, kind, which, bars=6):
    """the mean bits of each six-bar stretch of 64b as written"""
    bits = glitch_scores['64b | as written']; by_bar = {}
    if kind == 'ng':
        for (v, i, chord, key), b in zip(which['notagen'], bits):
            if chord or key is None: continue
            by_bar.setdefault(int(key[1] // 3) + 1, []).append(note_bits(b, kind))
    else:
        for key, b in zip(which['amt'], bits): by_bar.setdefault(int(key[1] // 3) + 1, []).append(note_bits(b, kind))
    out = []
    for k in range(1, 161 - bars + 1):
        xs = [x for j in range(k, k + bars) for x in by_bar.get(j, [])]
        if xs: out.append(float(np.mean(xs)))
    return out


def quote_mean(bits, notes, kind):
    """the mean bits of the quote's notes from its third bar"""
    if kind == 'ng':
        xs = [note_bits(b, kind) for (v, k, t, midi, chord), b in zip(notes, bits) if not chord and t >= FROM - 1e-6]
    else:
        xs = [note_bits(b, kind) for (t, d, m), b in zip(notes, bits) if t >= FROM - 1e-6]
    return float(np.mean(xs))


def main():
    meta = json.load(open(os.path.join(HERE, 'quote.json'))); g = json.load(open(os.path.join(HERE, 'glitch.json')))
    out = dict(results={}, by_quote=[])
    for ear, stem, kind in EARS:
        qf, gf = os.path.join(HERE, f'quote_{stem}.jsonl'), os.path.join(HERE, f'glitch_{stem}.jsonl')
        if not (os.path.exists(qf) and os.path.exists(gf)): continue
        qs, gs = load(qf), load(gf)
        own = np.array(own_stretches(gs, kind, g['piece64']['as_written']))
        rows = []
        for q in meta['quotes']:
            for where in ('in 64b', 'alone'):
                id_ = f"{q['title']} | {q['key']} | {where}"
                notes = (q['notagen_in_64b'] if where == 'in 64b' else q['notagen_alone']) if kind == 'ng' else q['amt']
                m = quote_mean(qs[id_], notes, kind)
                rows.append(dict(title=q['title'], family=q['family'], key=q['key'], where=where, bits=round(m, 3),
                                 below_64b=round(float(np.mean(own < m)), 3) if where == 'in 64b' else None))
        out['by_quote'] += [dict(ear=ear, **r) for r in rows]
        res = dict(own_64b=dict(median=round(float(np.median(own)), 3), p5=round(float(np.percentile(own, 5)), 3),
                                lowest=round(float(own.min()), 3), stretches=len(own)))
        for fam in ('Chopin', 'Polish'):
            for where in ('in 64b', 'alone'):
                ok = {r['title']: r['bits'] for r in rows if r['family'] == fam and r['where'] == where and r['key'] == 'own key'}
                up = {r['title']: r['bits'] for r in rows if r['family'] == fam and r['where'] == where and r['key'] == 'a tone higher'}
                diff = [ok[t] - up[t] for t in ok]
                r = dict(own_key=round(float(np.mean(list(ok.values()))), 3), tone_higher=round(float(np.mean(list(up.values()))), 3),
                         key_difference=round(float(np.mean(diff)), 3), lower_in_own_key=f'{sum(d < 0 for d in diff)} of {len(diff)}')
                if where == 'in 64b':
                    below = [x['below_64b'] for x in rows if x['family'] == fam and x['where'] == where and x['key'] == 'own key']
                    r['under_64b_5th_percentile'] = f"{sum(b < 0.05 for b in below)} of {len(below)}"
                res[f'{fam} | {where}'] = r
        out['results'][ear] = res
    json.dump(out, open(os.path.join(HERE, 'compare_quote.json'), 'w'), indent=1, ensure_ascii=False)
    for ear, res in out['results'].items():
        print(ear)
        for k, v in res.items(): print('  ', k, v)


if __name__ == '__main__':
    main()
