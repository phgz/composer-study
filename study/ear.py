"""The listener's ear: how surprising each note of a melodic line is to a listener, in bits (its information content, IC = -log2
of the probability the listener gave it), and how unsure the listener was just before it (the entropy of the prediction). After
IDyOM (Pearce 2005; Pearce and Wiggins 2006), as composer-blend's piece 44 built it (model44.py), here trained on score-reader's
whole catalogue.

The listener has two memories. The long-term one learnt a corpus (`Long`, from study/lines.py's works, each weighted); the
short-term one (`Short`) learns the piece itself as it goes, so that a motif heard twice is expected the third time. Each predicts
every next note from the notes before it with a variable-order Markov model (PPM: interpolated, escape method C, orders 0 to K,
order -1 uniform), in four views of the music at once:
  int    the interval from the note before (-20 to +20 semitones)      deg    the scale degree from the work's final (0-11)
  link   the interval and the degree together                           ioi    the ratio of this time-span to the one before
The pitch views are joined by a geometric mean over the 41 pitches within 20 semitones of the last note, and the two memories the
same way; rhythm (ioi) is predicted on its own, and a note's IC is the pitch IC plus the rhythm IC. A leap past 20 semitones is given
12 bits. The means are unweighted (`BIAS` 0). Piece 44 weighted each distribution by how sure it was (its relative entropy to the
power -1, IDyOM's bias 1): on the catalogue's held-out works that trusts the short-term memory most when it has heard least, and
a note costs 2.90 bits of pitch instead of 2.54 (200 held-out works; 22 November 2026). The short-term memory also hears the line's
first degree, which piece 44's did not.

The long-term memory holds weighted counts (a work weighs one at a shared level: TRAINING.md, section 4), scaled so that their sum
is the number of notes, so that escape method C sees counts of the size it was made for. It is kept as sorted arrays of
(context, symbol) codes, so that a corpus of millions of notes is learnt and asked in batches."""
import math
import numpy as np

LOG2 = math.log2
SPAN = 20
INT = np.arange(-SPAN, SPAN + 1)                                    # the 41 intervals, and the candidate pitches about the last note
A_INT, A_DEG, A_IOI = len(INT), 12, 13
A_LINK = A_INT * A_DEG
K_DEFAULT = 4


def ioi_symbol(prev_span, span):
    """log2 of the ratio of successive time-spans, in half steps, from 1/8 to 8: 13 symbols (index 0..12; 6 is 'the same')"""
    if prev_span <= 0 or span <= 0: return 6
    v = round(2 * LOG2(span / prev_span)) / 2
    return int(round((max(-3.0, min(3.0, v)) + 3) * 2))


def views(notes, final):
    """the four views of one line [(onset, dur, midi), ...] with its final: symbol arrays, aligned so that a view's j-th symbol is
    predicted from its symbols before j. int and link start at the second note, deg at the first, ioi at the third."""
    m = np.array([n[2] for n in notes], dtype=np.int64); on = np.array([n[0] for n in notes], dtype=float)
    iv = np.clip(np.diff(m), -SPAN, SPAN) + SPAN
    deg = (m - final) % 12
    link = iv * A_DEG + deg[1:]
    spans = np.diff(on)
    ioi = np.array([ioi_symbol(spans[i - 1], spans[i]) for i in range(1, len(spans))], dtype=np.int64)
    return dict(int=iv, deg=deg, link=link, ioi=ioi)


ALPHABET = dict(int=A_INT, deg=A_DEG, link=A_LINK, ioi=A_IOI)


def _codes(seq, A, k):
    """for each position j of seq, the code of its k symbols before (-1 where j < k)"""
    n = len(seq); out = np.full(n, -1, dtype=np.int64)
    if k == 0: out[:] = 0; return out
    if n <= k: return out
    c = np.zeros(n - k, dtype=np.int64)
    for j in range(k): c = c * A + seq[j:n - k + j]
    out[k:] = c
    return out


class Table:
    """one view's long-term memory: for each order k, the sorted (context, symbol) codes with their weighted counts, and for each
    context its total (N) and the number of symbols seen after it (T)"""

    def __init__(self, A, K):
        self.A, self.K = A, K; self.orders = []

    def learn(self, seqs, weights):
        """seqs: symbol arrays; weights: one weight a sequence (each of its symbols counts that much)"""
        A = self.A; kept = [(np.asarray(s, dtype=np.int64), w) for s, w in zip(seqs, weights) if len(s) and w > 0]
        self.orders = []
        for k in range(self.K + 1):                                         # one order at a time: the memory of one order's codes
            allc, allw = [], []
            for s, w in kept:
                ctx = _codes(s, A, k); ok = ctx >= 0
                if ok.any(): allc.append(ctx[ok] * A + s[ok]); allw.append(np.full(int(ok.sum()), w))
            if not allc: self.orders.append(None); continue
            pairs = np.concatenate(allc); ws = np.concatenate(allw); del allc, allw
            uniq, inv = np.unique(pairs, return_inverse=True); cnt = np.bincount(inv, weights=ws)
            ctx = uniq // A
            cu, starts = np.unique(ctx, return_index=True)
            N = np.add.reduceat(cnt, starts); T = np.diff(np.append(starts, len(uniq))).astype(float)
            self.orders.append(dict(pairs=uniq, cnt=cnt, ctx=cu, N=N, T=T))
        return self

    def predict(self, ctxs, wanted):
        """the probability of each wanted symbol: ctxs[k] the context code of each query at order k (-1: none), wanted an M x S array
        of symbols. The interpolated recursion is worked symbol by symbol, only for the wanted ones."""
        M, S = wanted.shape; p = np.full((M, S), 1.0 / self.A); alive = np.ones(M, dtype=bool)
        for k, o in enumerate(self.orders):
            if o is None: break
            c = ctxs[k]; need = alive & (c >= 0)
            alive &= c >= 0
            rows = np.nonzero(need)[0]
            if not len(rows): break
            loc = np.searchsorted(o['ctx'], c[rows]); loc_c = np.minimum(loc, len(o['ctx']) - 1)
            found = o['ctx'][loc_c] == c[rows]
            alive[rows[~found]] = False
            rows, ci = rows[found], loc_c[found]
            if not len(rows): break
            pair = c[rows][:, None] * self.A + wanted[rows]
            pl = np.minimum(np.searchsorted(o['pairs'], pair), len(o['pairs']) - 1)
            cnt = np.where(o['pairs'][pl] == pair, o['cnt'][pl], 0.0)
            N, T = o['N'][ci][:, None], o['T'][ci][:, None]
            p[rows] = (cnt + T * p[rows]) / (N + T)
        return p


class Short:
    """one view's short-term memory: learns one piece symbol by symbol (dense counts per context, for a short sequence)"""

    def __init__(self, A, K):
        self.A, self.K = A, K; self.c = [dict() for _ in range(K + 1)]; self.seq = []

    def dist(self):
        """the distribution over the next symbol, from the symbols heard so far"""
        p = np.full(self.A, 1.0 / self.A); n = len(self.seq)
        for k in range(min(self.K, n) + 1):
            e = self.c[k].get(tuple(self.seq[n - k:]) if k else ())
            if e is None: break
            cnt, N, T = e
            p = (cnt + T * p) / (N + T)
        return p

    def hear(self, x):
        n = len(self.seq)
        for k in range(min(self.K, n) + 1):
            key = tuple(self.seq[n - k:]) if k else ()
            e = self.c[k].get(key)
            if e is None: e = self.c[k][key] = [np.zeros(self.A), 0.0, 0.0]
            if e[0][x] == 0: e[2] += 1
            e[0][x] += 1; e[1] += 1
        self.seq.append(int(x))


def _entropy(p):
    q = p[p > 0]; return float(-(q * np.log2(q)).sum())


BIAS = 0.0                                                          # the weights' bias: 0, an unweighted geometric mean


def combine(dists, bias=None):
    """geometric mean of distributions over the same candidates, each weighted by its relative entropy ** -bias (bias 0: unweighted)"""
    bias = BIAS if bias is None else bias; hmax = LOG2(len(dists[0]))
    ws = [max(_entropy(d) / hmax, 1e-3) ** -bias for d in dists]
    logp = sum(w * np.log(np.maximum(d, 1e-12)) for w, d in zip(ws, dists)) / sum(ws)
    out = np.exp(logp - logp.max()); return out / out.sum()


class Long:
    """the long-term memory: the four views' tables, learnt from works (study/lines.py) with their weights"""

    def __init__(self, K=K_DEFAULT):
        self.K = K; self.tables = {v: Table(ALPHABET[v], max(0, K - 1) if v == 'link' else K) for v in ALPHABET}

    def learn(self, works, weight_of):
        """works: study.lines.Work; weight_of(work): its weight at this level (TRAINING.md, section 4). Each work's weight is spread
        over its notes, and the whole scaled so that the counts sum to the number of notes."""
        per = []; total_notes = 0; total_w = 0.0
        for w in works:
            n = sum(len(l) for l in w.lines.values()); wt = weight_of(w)
            if n == 0 or wt <= 0: continue
            per.append((w, wt / n)); total_notes += n; total_w += wt
        scale = total_notes / total_w if total_w else 1.0
        seqs = {v: [] for v in ALPHABET}; wts = {v: [] for v in ALPHABET}
        for w, x in per:
            for line in w.lines.values():
                vs = views(line, w.final)
                for v in ALPHABET: seqs[v].append(vs[v]); wts[v].append(x * scale)
        for v in ALPHABET: self.tables[v].learn(seqs[v], wts[v])
        self.notes = total_notes; self.works = len(per)
        return self

    def save(self, path, about=None):
        """the memory as one .npz file (every view's tables), with `about`: what it was trained on, as JSON"""
        import json
        arrays = {}
        for v, t in self.tables.items():
            for k, o in enumerate(t.orders):
                if o is None: continue
                for f, x in o.items(): arrays[f'{v}/{k}/{f}'] = x
        meta = dict(K=self.K, notes=getattr(self, 'notes', None), works=getattr(self, 'works', None), about=about or {})
        np.savez(path, __meta__=np.frombuffer(json.dumps(meta).encode('utf-8'), dtype=np.uint8), **arrays)

    @classmethod
    def load(cls, path):
        """a memory saved by save(); its `about` in .about"""
        import json
        z = np.load(path); meta = json.loads(bytes(z['__meta__']).decode('utf-8')); ltm = cls(meta['K'])
        for v, t in ltm.tables.items():
            t.orders = []
            for k in range(t.K + 1):
                key = f'{v}/{k}/pairs'
                t.orders.append({f: z[f'{v}/{k}/{f}'] for f in ('pairs', 'cnt', 'ctx', 'N', 'T')} if key in z.files else None)
        ltm.notes, ltm.works, ltm.about = meta['notes'], meta['works'], meta['about']
        return ltm

    def line(self, notes, final):
        """the long-term predictions for every note of a line: {view: M x S probabilities of the wanted symbols}, M = len(notes)-1"""
        vs = views(notes, final); n = len(notes); prev = np.array([x[2] for x in notes[:-1]], dtype=np.int64)
        cand = prev[:, None] + INT[None, :]                                # the 41 candidate pitches for notes 1..n-1
        degc = (cand - final) % 12
        out = {}
        for v in ('int', 'deg', 'link'):
            seq = vs[v]; T = self.tables[v]
            if v == 'deg':                                                  # deg predicts note j from degs[:j]; queries j = 1..n-1
                ctxs = [_codes(seq, T.A, k)[1:] for k in range(T.K + 1)]
                out[v] = T.predict(ctxs, np.tile(np.arange(A_DEG), (n - 1, 1)))
            elif v == 'int':
                ctxs = [_codes(seq, T.A, k) for k in range(T.K + 1)]
                out[v] = T.predict(ctxs, np.tile(np.arange(A_INT), (n - 1, 1)))
            else:
                ctxs = [_codes(seq, T.A, k) for k in range(T.K + 1)]
                out[v] = T.predict(ctxs, (INT[None, :] + SPAN) * A_DEG + degc)
        T = self.tables['ioi']; seq = vs['ioi']
        out['ioi'] = T.predict([_codes(seq, T.A, k) for k in range(T.K + 1)], np.tile(np.arange(A_IOI), (len(seq), 1))) if len(seq) else np.zeros((0, A_IOI))
        out['degc'] = degc
        return out, vs


def _pitch(pi, pd, pl, degc):
    """the three pitch views as distributions over the 41 candidates"""
    mult = np.bincount(degc, minlength=12)[degc]
    P_deg = pd[degc] / mult; P_deg = P_deg / P_deg.sum()
    P_link = pl / pl.sum()
    return combine([pi / pi.sum(), P_deg, P_link])


def listen(notes, final, ltm, stm_K=K_DEFAULT, short=True):
    """each note of one line, in order: (IC of its pitch, IC of its rhythm, entropy before it), the short-term memory learning as
    the line goes; the first note has no prediction (None). `short`: with the short-term memory (the piece learnt as it goes)."""
    if len(notes) < 2: return [None] * len(notes)
    L, vs = ltm.line(notes, final)
    stm = {v: Short(ALPHABET[v], stm_K if v != 'link' else max(2, stm_K - 1)) for v in ALPHABET}
    out = [None]; stm['deg'].hear(vs['deg'][0])
    for i in range(1, len(notes)):
        q = i - 1; degc = L['degc'][q]
        pl = _pitch(L['int'][q], L['deg'][q], L['link'][q], degc)
        if short and i >= 3:
            ps_int = stm['int'].dist(); ps_deg = stm['deg'].dist(); ps_link = stm['link'].dist()[(INT + SPAN) * A_DEG + degc]
            p = combine([pl, _pitch(ps_int, ps_deg, ps_link, degc)])
        else: p = pl
        r = None
        if i >= 2:
            r = L['ioi'][i - 2]; r = r / r.sum()
            if short and i >= 4: r = combine([r, stm['ioi'].dist()])
        step = notes[i][2] - notes[i - 1][2]
        ic_p = -LOG2(max(float(p[step + SPAN]), 1e-12)) if abs(step) <= SPAN else 12.0
        ic_r = -LOG2(max(float(r[vs['ioi'][i - 2]]), 1e-12)) if r is not None else 0.0
        out.append((ic_p, ic_r, _entropy(p) + (_entropy(r) if r is not None else 0.0)))
        stm['int'].hear(vs['int'][q]); stm['link'].hear(vs['link'][q]); stm['deg'].hear(vs['deg'][i])
        if i >= 2: stm['ioi'].hear(vs['ioi'][i - 2])
    return out
