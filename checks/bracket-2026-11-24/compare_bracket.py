"""The bracket test, the comparison: do Philip's ratings of 42 pieces follow how surprising AMT finds them, not on a straight line
but in a bracket? Three tests, fixed before any score was made (24 November 2026), each against 10,000 shuffles of the ratings,
one-sided; a test passes under 0.05 / 3 (three tests).

  surprise S, uncertainty H   a note's pitch bits and the entropy of AMT's guess at its pitch (study/amt_score.py)
  1. the inverted U (Gold et al. 2019)   each piece's mean S, put on one scale across the pieces; the rating fitted to it and its
       square (least squares): the square's coefficient below 0 (liking highest in the middle). Its peak is reported, and whether
       it falls among the pieces
  2. surprise against uncertainty (Cheung et al. 2019)   the median S and median H of every note of every piece; a piece's share
       of notes either sure and surprised (H under its median, S over) or unsure and unsurprised (H over, S under); the higher
       the share, the higher the rating (Spearman)
  3. the bracket at every second   each second's mean S over the notes begun within two seconds of it (as rated.py's M0); the
       band from the 25th to the 75th percentile of every second of every piece; a piece's share of seconds in the band; the
       higher the share, the higher the rating (Spearman)
  also   the plain straight-line correlations of mean S and mean H with the ratings (Spearman), for the record

AMT Large is the ear the tests are decided on; AMT Medium is reported beside it.

Run: python3 compare_bracket.py     (reads bracket.json and bracket_amt_<large|medium>.jsonl beside it; writes compare_bracket.json)"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHUFFLES = 10000


def ranks(v):
    v = np.asarray(v, float); order = v.argsort(); r = np.empty(len(v)); r[order] = np.arange(len(v))
    for x in np.unique(v):
        k = v == x; r[k] = r[k].mean()
    return r


def spearman(x, y): return float(np.corrcoef(ranks(x), ranks(y))[0, 1])


def quad(s, y):
    """the coefficients (a, b, c) of y = a + b z + c z^2, z the standardized s"""
    z = (s - s.mean()) / s.std(); X = np.column_stack([np.ones_like(z), z, z * z])
    return np.linalg.lstsq(X, y, rcond=None)[0]


def per_piece(meta, scores):
    """{piece: dict(S=[...], H=[...], onsets=[...])} over all its sections"""
    out = {}
    for x in meta['pieces']:
        S, H, T = [], [], []
        for sec in x['sections']:
            b = scores[sec['id']]
            S += [n[0] for n in b]; H += [n[2] for n in b]; T.append((np.array(sec['onsets']), np.array([n[0] for n in b])))
        out[x['piece']] = dict(rating=x['rating'], S=np.array(S), H=np.array(H), T=T)
    return out


def seconds_means(T):
    out = []
    for t, s in T:
        for k in range(int(t.max()) + 1):
            w = (t >= k - 2) & (t < k + 2)
            if w.any(): out.append(float(s[w].mean()))
    return np.array(out)


def run(meta, scores, rnd):
    pp = per_piece(meta, scores); names = list(pp); y = np.array([pp[n]['rating'] for n in names], float)
    mS = np.array([pp[n]['S'].mean() for n in names]); mH = np.array([pp[n]['H'].mean() for n in names])
    res = dict(pieces=len(names), linear=dict(mean_S=round(spearman(mS, y), 3), mean_H=round(spearman(mH, y), 3)))
    # 1. the inverted U
    a, b, c = quad(mS, y); perm = np.array([quad(mS, rnd.permutation(y))[2] for _ in range(SHUFFLES)])
    peak = mS.mean() - b / (2 * c) * mS.std() if c != 0 else None
    res['1 inverted U'] = dict(c=round(float(c), 4), p=round(float(np.mean(perm <= c)), 4), peak_bits=round(float(peak), 3) if peak is not None else None,
                               pieces_range=[round(float(mS.min()), 3), round(float(mS.max()), 3)],
                               peak_among_pieces=bool(peak is not None and mS.min() <= peak <= mS.max()))
    # 2. surprise against uncertainty
    allS = np.concatenate([pp[n]['S'] for n in names]); allH = np.concatenate([pp[n]['H'] for n in names])
    ms, mh = np.median(allS), np.median(allH)
    q = np.array([float(np.mean(((pp[n]['H'] < mh) & (pp[n]['S'] > ms)) | ((pp[n]['H'] > mh) & (pp[n]['S'] < ms)))) for n in names])
    r2 = spearman(q, y); perm = np.array([spearman(q, rnd.permutation(y)) for _ in range(SHUFFLES)])
    res['2 surprise against uncertainty'] = dict(rho=round(r2, 3), p=round(float(np.mean(perm >= r2)), 4), median_S=round(float(ms), 3),
                                                 median_H=round(float(mh), 3), share_range=[round(float(q.min()), 3), round(float(q.max()), 3)])
    # 3. the bracket at every second
    secs = {n: seconds_means(pp[n]['T']) for n in names}; every = np.concatenate(list(secs.values()))
    lo, hi = np.percentile(every, 25), np.percentile(every, 75)
    share = np.array([float(np.mean((secs[n] >= lo) & (secs[n] <= hi))) for n in names])
    r3 = spearman(share, y); perm = np.array([spearman(share, rnd.permutation(y)) for _ in range(SHUFFLES)])
    res['3 bracket at every second'] = dict(rho=round(r3, 3), p=round(float(np.mean(perm >= r3)), 4), band_bits=[round(float(lo), 3), round(float(hi), 3)],
                                            share_range=[round(float(share.min()), 3), round(float(share.max()), 3)])
    res['passes (p < 0.0167)'] = [k for k in ('1 inverted U', '2 surprise against uncertainty', '3 bracket at every second') if res[k]['p'] < 0.05 / 3]
    res['by piece'] = [dict(piece=n, rating=float(pp[n]['rating']), mean_S=round(float(mS[i]), 3), mean_H=round(float(mH[i]), 3),
                            share_sure_surprised_or_unsure_unsurprised=round(float(q[i]), 3), share_seconds_in_band=round(float(share[i]), 3))
                       for i, n in enumerate(names)]
    return res


def main():
    meta = json.load(open(os.path.join(HERE, 'bracket.json'))); out = {}
    for ear in ('large', 'medium'):
        f = os.path.join(HERE, f'bracket_amt_{ear}.jsonl')
        if not os.path.exists(f): continue
        scores = {json.loads(l)['id']: json.loads(l)['bits'] for l in open(f)}
        out[f'AMT {ear.capitalize()}'] = run(meta, scores, np.random.default_rng(0))
    json.dump(out, open(os.path.join(HERE, 'compare_bracket.json'), 'w'), indent=1)
    for ear, r in out.items():
        print(ear, {k: v for k, v in r.items() if k != 'by piece'})


if __name__ == '__main__':
    main()
