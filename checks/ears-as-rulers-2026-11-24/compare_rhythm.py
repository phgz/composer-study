"""The rhythm test, the comparison: how well AMT finds the stumbles planted by prepare_rhythm.py, by the bits of their onsets.

  an onset's bits   the bits of a note's onset token, given what came before (study/amt_score.py, its fourth number). Notes begun
                    together share an onset: the lowest is the one whose onset AMT had to guess, the others' cost next to nothing,
                    so the comparison is among the lowest notes of each onset (the first of each in AMT's order)
  a planted note    a note off: the moved note; a skip: the lowest note of the first onset after the sixteenth taken out. A moved
                    note that lands on another note's onset is not the first there, and is counted as it is (found or not)
  its place         the share of the copy's other onsets at least as surprising (0: the most surprising of all)
  found at 2%       its place under 0.02; also 1% and 5%
  the rise          its onset's bits in the copy, minus the same note's in the copy as written
  intervals         95%, resampling works (each work's stumbles together); in 64b, resampling its stumbles

Run: python3 compare_rhythm.py     (reads rhythm.json, rhythm_amt_inputs.jsonl and rhythm_amt_<large|medium>.jsonl beside it;
     writes compare_rhythm.json)"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGETS = (0.01, 0.02, 0.05)


def firsts(inp):
    """for each scored note (in order), whether it is the first of its onset: its onset token differs from the triplet's before"""
    out = []
    for wi, pos in inp['notes']:
        w = inp['windows'][wi]
        out.append(pos - 5 < 1 or w[pos - 2] != w[pos - 5])
    return out


def main():
    meta = json.load(open(os.path.join(HERE, 'rhythm.json')))
    inputs = {json.loads(l)['id']: json.loads(l) for l in open(os.path.join(HERE, 'rhythm_amt_inputs.jsonl'))}
    first = {k: firsts(v) for k, v in inputs.items()}
    pieces = [(w, m, f'{w} | as written', w) for w, m in meta['works'].items()]
    pieces += [(f'64b set {k}', meta['piece64'][k], '64b | as written', '64b') for k in ('1', '2', '3')]
    out = {}
    for ear in ('large', 'medium'):
        f = os.path.join(HERE, f'rhythm_amt_{ear}.jsonl')
        if not os.path.exists(f): continue
        scores = {json.loads(l)['id']: json.loads(l)['bits'] for l in open(f)}
        order0 = {'64b': meta['piece64']['as written']}
        order0.update({w: m['copies']['as written'] for w, m in meta['works'].items()})
        rows = []
        for name, m, id0, base in pieces:
            o0 = order0[base]; at0 = {i: k for k, i in enumerate(o0)}; b0 = scores[id0]
            for kind in ('a note off', 'a skip'):
                id_ = f'{name} | {kind}'; o = m['copies'][kind]; at = {i: k for k, i in enumerate(o)}; b = scores[id_]
                fs = first[id_]; planted = set(m[kind])
                others = np.array([b[k][3] for k, i in enumerate(o) if fs[k] and i not in planted and b[k][3] is not None])
                for i in m[kind]:
                    x = b[at[i]][3]
                    rows.append(dict(piece=name, where='64b' if base == '64b' else 'works', kind=kind, place=float(np.mean(others >= x)),
                                     rise=x - b0[at0[i]][3], first=fs[at[i]]))
        res = {}
        rnd = np.random.default_rng(0)
        for kind in ('a note off', 'a skip'):
            for where in ('works', '64b'):
                rs = [r for r in rows if r['kind'] == kind and r['where'] == where]
                x = dict(n=len(rs), median_place=round(float(np.median([r['place'] for r in rs])), 4),
                         median_rise=round(float(np.median([r['rise'] for r in rs])), 2),
                         first_of_their_onset=round(float(np.mean([r['first'] for r in rs])), 3))
                for bud in BUDGETS: x[f'found at {bud:.0%}'] = round(float(np.mean([r['place'] < bud for r in rs])), 3)
                by = {}
                for r in rs: by.setdefault(r['piece'] if where == 'works' else len(by), []).append(r['place'] < .02)
                ks = list(by); boots = [np.mean([h for j in rnd.choice(len(ks), len(ks)) for h in by[ks[j]]]) for _ in range(2000)]
                x['found at 2%, 95% interval'] = [round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)]
                res[f'{kind} | {where}'] = x
        out[f'AMT {ear.capitalize()}'] = res
    json.dump(out, open(os.path.join(HERE, 'compare_rhythm.json'), 'w'), indent=1)
    for ear, res in out.items():
        for k, v in res.items(): print(ear, k, v)


if __name__ == '__main__':
    main()
