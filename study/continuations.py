"""Continuations: a line carried on in a narrow unit's manner (a composer in one kind of piece and one period), proposed for a draft
to choose from. The model is the listener's ear (study/ear.py) learnt at several levels at once, and one view more for a line that
sounds with others:

  levels     the unit's works, the composer's, and the whole catalogue's (the saved ear), each a variable-order Markov model (PPM)
             of the line's intervals, degrees and rhythm; their predictions joined by a geometric mean (ear.combine), with the piece's
             own short-term memory, so that a figure the line has made is expected again
  vertical   where other lines sound, the note's pitch class above the lowest of them (or "below it"), given the degree of that bass:
             the unit's harmony as its lines meet, learnt from its works' lines (each part's sounding skyline), at the same levels

For counts, a span the reading plays again is counted once (TRAINING.md, section 3); editors' copies for MIDI and realized files are
left out (section 1), as study/lines.py reads them.

A continuation is sampled note by note: a pitch among the 41 within 20 semitones of the last, kept in a range and between the lines
it must not cross; a time-span from the rhythm view, snapped to the durations the unit uses. Of many samples, the ones proposed are
those whose surprise (bits a note, under the same model) falls within what the unit's own music has, measured on its works held out:
not the most likely, which is what the critic calls flat, and not noise. Each one is checked against the unit's works for quotation
(score-reader's rule: no more than three intervals in a row with their rhythm), and a quoting sample is not proposed."""
import bisect, collections, copy, heapq, math, random
import numpy as np
from study import ear as E, lines as L

LOG2 = math.log2
SPAN, INT, A_INT, A_DEG, A_IOI, A_LINK = E.SPAN, E.INT, E.A_INT, E.A_DEG, E.A_IOI, E.A_LINK
BELOW, ALONE = 12, 13                                           # the vertical view's two symbols beside the 12 pitch classes
A_V, C_V = 14, 13                                               # its alphabet; its contexts (the bass's degree, or none)


# --- the lines a model learns from -------------------------------------------------------------------------------------------

def counted(work):
    """a work's lines with each span played again counted once"""
    return {p: L.once(l, work.heard_again) for p, l in work.lines.items()}


def around(line, others, eps=1e-3):
    """for each note of `line`, the lowest and the highest pitch of `others` (lines) sounding at its onset: (low, high), or None"""
    ev = sorted((n[0], n[0] + n[1], n[2]) for o in others for n in o if n[1] > 0)
    out = []; lo = []; hi = []; i = 0
    for n in line:
        t = n[0] + eps
        while i < len(ev) and ev[i][0] <= t:
            heapq.heappush(lo, (ev[i][2], ev[i][1])); heapq.heappush(hi, (-ev[i][2], ev[i][1])); i += 1
        while lo and lo[0][1] <= t: heapq.heappop(lo)                     # an ended note is dropped when it is the lowest
        while hi and hi[0][1] <= t: heapq.heappop(hi)                     # or the highest
        out.append((lo[0][0], -hi[0][0]) if lo else None)
    return out


def under(line, others): return [x[0] if x else None for x in around(line, others)]


def sounding_at(t, lines, eps=1e-3):
    """(low, high) of the lines' notes sounding at time t, or None"""
    ps = [n[2] for l in lines for n in l if n[0] <= t + eps < n[0] + n[1]]
    return (min(ps), max(ps)) if ps else None


def vctx(span, final):
    """the vertical view's contexts for a note with `span` (low, high) of the others: (the bass's degree, and that with the interval
    from the bass to the highest other), or (12, None) where nothing else sounds"""
    if span is None: return 12, None
    b, t = span; return (b - final) % 12, ((b - final) % 12) * 12 + (t - b) % 12


def vsym(m, span):
    """the vertical view's symbol for a note `m` sounding with `span`: its pitch class above the bass, BELOW it, or ALONE"""
    if span is None: return ALONE
    return BELOW if m < span[0] else (m - span[0]) % 12


class Vertical:
    """the vertical view's counts: the symbol given the bass's degree and the interval from the bass to the highest other line
    (order 2), given the bass's degree (order 1), and alone (order 0), interpolated by escape method C"""

    def __init__(self): self.c = np.zeros((C_V, A_V)); self.c2 = np.zeros((C_V * 12, A_V))

    def learn(self, works, weight_of):
        for w in works:
            ls = [l for l in counted(w).values() if len(l) >= 2]
            if len(ls) < 2: continue
            n = sum(len(l) for l in ls); x = weight_of(w) / n if n else 0
            if x <= 0: continue
            for k, l in enumerate(ls):
                for m, sp in zip(l, around(l, ls[:k] + ls[k + 1:])):
                    c1, c2 = vctx(sp, w.final); s = vsym(m[2], sp); self.c[c1, s] += x
                    if c2 is not None: self.c2[c2, s] += x
        return self

    def scaled(self, notes):
        """the counts scaled to sum to `notes`, so that escape method C sees counts of the size it was made for (ear.Long)"""
        tot = self.c.sum(); v = Vertical(); f = notes / tot if tot else 1.0; v.c = self.c * f; v.c2 = self.c2 * f; return v

    def dist(self, c1, c2=None):
        c0 = self.c.sum(0); N0, T0 = c0.sum(), (c0 > 0).sum()
        p = (c0 + T0 / A_V) / (N0 + T0) if N0 else np.full(A_V, 1 / A_V)
        for row in (self.c[c1], self.c2[c2] if c2 is not None else None):
            if row is None: break
            N, T = row.sum(), (row > 0).sum()
            if not N: break
            p = (row + T * p) / (N + T)
        return p


def over_candidates(pv, last, span):
    """a vertical distribution as one over the 41 candidate pitches about `last`"""
    if span is None: return np.full(A_INT, 1 / A_INT)
    cand = last + INT; sym = np.where(cand < span[0], BELOW, (cand - span[0]) % 12)
    mult = np.bincount(sym, minlength=A_V)[sym]; p = pv[sym] / mult; return p / p.sum()


# --- the ear's prediction of the next note, one note at a time ---------------------------------------------------------------

def _ctx(seq, j, k, A):
    if k == 0: return 0
    if j - k < 0: return -1
    c = 0
    for s in seq[j - k:j]: c = c * A + int(s)
    return c


def next_long(ltm, notes, final):
    """the long-term memory's distributions for the note after `notes` (2 or more): pitch over the 41 candidates about the last note,
    and rhythm over the 13 time-span ratios of its span to the one before"""
    dummy = list(notes) + [(notes[-1][0] + 1.0, 1.0, notes[-1][2])]
    vs = E.views(dummy, final); n = len(notes); last = notes[-1][2]
    degc = (last + INT - final) % 12
    out = {}
    for v, seq, j, wanted in (('int', vs['int'], n - 1, np.arange(A_INT)), ('deg', vs['deg'], n, np.arange(A_DEG)),
                              ('link', vs['link'], n - 1, (INT + SPAN) * A_DEG + degc)):
        T = ltm.tables[v]; out[v] = T.predict([np.array([_ctx(seq, j, k, T.A)]) for k in range(T.K + 1)], wanted[None, :])[0]
    p = E._pitch(out['int'], out['deg'], out['link'], degc)
    r = None
    if n >= 2:
        T = ltm.tables['ioi']; seq = vs['ioi']; j = n - 2
        r = T.predict([np.array([_ctx(seq, j, k, T.A)]) for k in range(T.K + 1)], np.arange(A_IOI)[None, :])[0]; r = r / r.sum()
    return p, r, degc


class Memory:
    """the piece's short-term memory of one line (ear.Short in each view), heard note by note"""

    def __init__(self, final, K=E.K_DEFAULT):
        self.final = final; self.notes = []
        self.s = {v: E.Short(E.ALPHABET[v], K if v != 'link' else max(2, K - 1)) for v in E.ALPHABET}

    def hear(self, note):
        ns = self.notes; ns.append(note); i = len(ns) - 1
        d = (note[2] - self.final) % 12
        if i == 0: self.s['deg'].hear(d); return
        iv = int(np.clip(note[2] - ns[-2][2], -SPAN, SPAN) + SPAN)
        self.s['int'].hear(iv); self.s['link'].hear(iv * A_DEG + d); self.s['deg'].hear(d)
        if i >= 2: self.s['ioi'].hear(E.ioi_symbol(ns[-2][0] - ns[-3][0], note[0] - ns[-2][0]))

    def dists(self, degc):
        n = len(self.notes)
        p = E._pitch(self.s['int'].dist(), self.s['deg'].dist(), self.s['link'].dist()[(INT + SPAN) * A_DEG + degc], degc) if n >= 3 else None
        r = self.s['ioi'].dist() if n >= 4 else None
        return p, r


# --- the model ---------------------------------------------------------------------------------------------------------------

VWEIGHT = 0.5                                                   # the vertical view's exponent in the product (held out: see test)


class Model:
    """a unit's continuations: `levels` [(name, ear.Long, Vertical)], most general first; `bias` the geometric mean's
    (ear.combine); `vertical` whether the vertical view is heard; `short` whether the piece's own memory is"""

    def __init__(self, levels, bias=0.0, vertical=True, short=True, vweight=VWEIGHT):
        self.levels, self.bias, self.vertical, self.short, self.vweight = levels, bias, vertical, short, vweight

    def predict(self, notes, final, span=None, mem=None):
        """pitch (41 candidates about the last note) and rhythm (13 ratios, or None) for the note after `notes`; `span`: the lowest
        and highest other pitches sounding where it will start (None: none, or not known); `mem`: the line's Memory"""
        ps, rs, degc = [], [], None
        for _, ltm, _ in self.levels:
            p, r, degc = next_long(ltm, notes, final); ps.append(p)
            if r is not None: rs.append(r)
        p = E.combine(ps, self.bias) if len(ps) > 1 else ps[0]
        r = (E.combine(rs, self.bias) if len(rs) > 1 else rs[0]) if rs else None
        if self.short and mem is not None:
            sp, sr = mem.dists(degc)
            if sp is not None: p = E.combine([p, sp])
            if sr is not None and r is not None: r = E.combine([r, sr])
        if self.vertical and span is not None:                            # the levels' vertical views joined first, then with the line
            c1, c2 = vctx(span, final)
            pv = [over_candidates(v.dist(c1, c2), notes[-1][2], span) for _, _, v in self.levels if v is not None]
            if pv:                                                         # a product of the two, the vertical view raised to vweight
                q = p * (E.combine(pv, self.bias) if len(pv) > 1 else pv[0]) ** self.vweight; p = q / q.sum()
        return p, r

    def hear(self, line, final, others=()):
        """each note of a line, after the first two: (bits of its pitch, bits of its rhythm or None), the line's memory learning as it
        goes; `others`: the lines sounding with it (for the vertical view)"""
        spans = around(line, others) if others else [None] * len(line)
        mem = Memory(final); out = []
        for i, n in enumerate(line):
            if i >= 2:
                p, r = self.predict(line[:i], final, spans[i], mem)
                step = n[2] - line[i - 1][2]
                bp = -LOG2(max(float(p[step + SPAN]), 1e-12)) if abs(step) <= SPAN else 12.0
                br = None
                if r is not None: br = -LOG2(max(float(r[E.ioi_symbol(line[i - 1][0] - line[i - 2][0], n[0] - line[i - 1][0])]), 1e-12))
                out.append((bp, br))
            mem.hear(n)
        return out


def level(works, weight_of=lambda w: 1.0, K=E.K_DEFAULT, measure_only=False):
    """one level of a Model from works: (ear.Long, Vertical), the lines counted with each span played again once. A work still
    under copyright somewhere (`measure_only`) is left out unless Philip says otherwise (TRAINING.md, section 5)"""
    once = [w._replace(lines=counted(w)) for w in works if measure_only or not (w.flags or {}).get('measure_only')]
    ltm = E.Long(K).learn(once, weight_of)
    v = Vertical().learn(once, weight_of).scaled(ltm.notes or 1)
    return ltm, v


# --- sampling ----------------------------------------------------------------------------------------------------------------

DURATIONS = (0.25, 1 / 3, 0.5, 2 / 3, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0)


def durations_of(works, top=10):
    """the time-spans (in quarters) a unit's lines use most, to snap a sampled span to"""
    c = collections.Counter()
    for w in works:
        for l in w.lines.values():
            for a, b in zip(l, l[1:]):
                d = round(b[0] - a[0], 3)
                if d > 0: c[d] += 1
    return sorted(d for d, _ in c.most_common(top)) or list(DURATIONS)


def snap(span, allowed): return min(allowed, key=lambda d: abs(math.log(d / span)))


def parallels(prev, others, t0, t1):
    """the pitch classes a line moving from `prev` (at t0) to a note at t1 may not take: those that would make parallel fifths or
    octaves (or unisons) with another line that moves too"""
    bad = set()
    for o in others:
        a = sounding_at(t0, [o]); b = sounding_at(t1, [o])
        if not a or not b or a[1] == b[1]: continue                       # the other line's (top) note at each time; it must move
        iv = (prev - a[1]) % 12
        if iv in (0, 7): bad.add((b[1] + iv) % 12)
    return bad


def sample(model, context, final, length, others=(), lo=None, hi=None, below=None, above=None, durations=DURATIONS,
           rnd=None, temperature=1.0, grid=None, no_parallels=True):
    """one continuation of `context` (a line [(onset, dur, midi)], 3 notes or more) for `length` quarters: [(onset, dur, midi)] and
    the bits of each note (pitch + rhythm). `others`: lines sounding with it (the vertical view's bass); `lo`, `hi`: its range;
    `below`/`above`: lines it must stay under / over (an inner voice between the melody and the bass); `grid`: onsets must fall on
    multiples of it (in quarters), where given; `no_parallels`: no parallel fifths or octaves with the other lines"""
    rnd = rnd or random.Random(); mem = Memory(final)
    for n in context: mem.hear(n)
    line = [tuple(n[:3]) for n in context]; start = line[-1][0] + line[-1][1]; end = start + length
    out, bits, tries = [], [], 0
    while tries < 1000:
        tries += 1
        p, r = model.predict(line, final, None, mem)
        prev = line[-1][0] - line[-2][0]
        if r is not None:
            q = r ** (1 / temperature); q /= q.sum(); s = int(rnd.choices(range(A_IOI), weights=q)[0])
            span = snap(prev * 2 ** ((s - 6) / 2), durations); br = -LOG2(float(r[s]))
        else: span, br = prev, 0.0
        t = max(line[-1][0] + span, start)                                 # the context's last note is not cut short
        if grid: t = round(t / grid) * grid; span = t - line[-1][0]
        if span <= 0: continue
        if t >= end - 1e-6: break
        p, _ = model.predict(line, final, sounding_at(t, others) if others else None, mem)
        cand = line[-1][2] + INT; ok = np.ones(A_INT, dtype=bool)
        if lo is not None: ok &= cand >= lo
        if hi is not None: ok &= cand <= hi
        if below: ub = sounding_at(t, below); ok &= cand < ub[0] if ub else ok
        if above: lb = sounding_at(t, above); ok &= cand > lb[1] if lb else ok
        if no_parallels and others:
            bad = parallels(line[-1][2], others, line[-1][0], t)
            if bad: ok &= ~np.isin(cand % 12, list(bad)) | (cand == line[-1][2])
        if not ok.any(): ok[:] = True
        q = np.where(ok, p, 0) ** (1 / temperature); q /= q.sum()
        k = int(rnd.choices(range(A_INT), weights=q)[0]); m = int(cand[k])
        bits.append(-LOG2(float(p[k] / p[ok].sum())) + br)
        last = line[-1]; line[-1] = (last[0], t - last[0], last[2])             # the note before lasts until this one
        if out: out[-1] = line[-1]
        note = (t, 1.0, m); line.append(note); out.append(note); mem.hear(note)
    if out: out[-1] = (out[-1][0], end - out[-1][0], out[-1][2])
    return out, bits


SAMPLE = dict(short=False, vweight=2.0)                        # how a continuation is drawn (held out: see README)
SCORE = dict(short=True, vweight=1.0)                          # how its surprise is measured, as the unit's own music's is


def surprise(levels, context, notes, final, others=()):
    """bits a note (pitch and rhythm) of `notes` after `context`, under the scoring model (the piece's own memory heard)"""
    h = Model(levels, **SCORE).hear(list(context) + list(notes), final, others)[max(0, len(context) - 2):]
    return float(np.mean([a + (b or 0.0) for a, b in h])) if h else None


def band(levels, works, length=12.0, ctx=4, step=30, min_notes=6):
    """the surprise of the unit's own music, held out: its works' passages of `length` quarters after `ctx` notes, every line with
    the others sounding, scored as proposals are; (25th, 75th percentile) and the values. `levels` must not have learnt `works`."""
    vals = []
    for w in works:
        ls = [[n[:3] for n in l] for l in counted(w).values() if len(l) >= 16]
        for i, l in enumerate(ls):
            others = ls[:i] + ls[i + 1:]
            for s0 in range(0, len(l) - 20, step):
                c = l[s0:s0 + ctx]; start = c[-1][0] + c[-1][1]; real = [n for n in l if start <= n[0] < start + length]
                if len(real) >= min_notes: vals.append(surprise(levels, c, real, w.final, others))
    vals = [v for v in vals if v is not None]
    return (float(np.percentile(vals, 25)), float(np.percentile(vals, 75))) if vals else None, vals


QUOTE_UNIT, QUOTE_DRAWN = 8, 4                                # Philip, 22 November 2026: a continuation quotes the unit it learnt
                                                               # from at 8 intervals in a row with their rhythm; the works a piece
                                                               # draws on, at 4 (score-reader's rule, pieces 45 on)


def quotes_against(works, score_reader, n=QUOTE_UNIT):
    """a check for propose(): the chains of `n` intervals with their rhythm that a continuation shares with `works`, by
    score-reader's quote module (`score_reader`: a checkout's folder)"""
    import sys
    if score_reader not in sys.path: sys.path.insert(0, score_reader)
    from score_reader import quote as Q
    idx = Q.index([[(p, x[0], x[1], x[2]) for p, l in w.lines.items() for x in l] for w in works], n=n)
    return lambda notes: Q.check([('line', x[0], x[1], x[2]) for x in notes], idx, n=n)


def propose(levels, context, final, length, n=200, keep=5, band=None, quotes=None, seed=0, **kw):
    """`keep` continuations of `context`, of the `n` sampled (SAMPLE: without the piece's own memory, which loops a line on itself,
    and with the vertical view weighed double), whose surprise under SCORE falls in `band` (lo, hi), most different from one another;
    any that `quotes` (a function: notes -> quoted chains) finds quoting is left out. [(notes, bits a note, why)], and counts"""
    rnd = random.Random(seed); pool = []; m = Model(levels, **SAMPLE); others = kw.get('others', ())
    for i in range(n):
        notes, _ = sample(m, context, final, length, rnd=rnd, **kw)
        if len(notes) < 2: continue
        pool.append((notes, surprise(levels, context, notes, final, others)))
    inband = [x for x in pool if x[1] is not None and (band is None or band[0] <= x[1] <= band[1])]
    quoting = [x for x in inband if quotes and quotes(list(context[-4:]) + x[0])]
    free = [x for x in inband if not any(x is q for q in quoting)]
    chosen = []
    for x in sorted(free, key=lambda x: abs(x[1] - (sum(band) / 2 if band else x[1]))):
        sig = tuple(m_ for _, _, m_ in x[0][:8])
        if all(sum(a != b for a, b in zip(sig, tuple(m_ for _, _, m_ in c[0][:8]))) >= 3 for c in chosen): chosen.append(x)
        if len(chosen) == keep: break
    return [(notes, b, f'{b:.2f} bits a note') for notes, b in chosen], dict(sampled=len(pool), in_band=len(inband), quoting=len(quoting))


# --- held out: does the unit's model expect the unit's music better than the ear? ----------------------------------------------

TEST_UNITS = (('Johann Sebastian Bach', 'chorale', 'voices', 'Leipzig'), ('Giovanni Pierluigi da Palestrina', 'motet', 'voices', 'all'),
              ('Josquin Des Prez', 'mass', 'voices', 'all'), ('Arcangelo Corelli', 'trio sonata', 'chamber', 'all'),
              ('Antonio Vivaldi', 'trio sonata', 'chamber', 'all'), ('Franz Joseph Haydn', 'string quartet', 'string quartet', 'mature'),
              ('Wolfgang Amadeus Mozart', 'string quartet', 'string quartet', 'Vienna'), ('Ludwig van Beethoven', 'sonata', 'keyboard', 'early'),
              ('Franz Schubert', 'song', 'voice and keyboard', 'late'), ('Johannes Brahms', 'song', 'voice and keyboard', 'middle'),
              ('Frédéric Chopin', 'dance', 'keyboard', 'Paris'), ('Scott Joplin', 'rag', 'keyboard', 'all'))


def split_units(works, facts, units=TEST_UNITS, per_unit=6, seed=25):
    """the test units' works, and `per_unit` of each held out (a work held out with its twins, lines.label_key)"""
    from study import periods as PD, profiles as P
    periods = PD.table(); members = collections.defaultdict(list)
    for w in works:
        for u in P.units_of(w, facts, periods):
            if u in units: members[u].append(w)
    rnd = random.Random(seed); held = set()
    for u in units:
        keys = sorted({L.label_key(w) for w in members[u]}); rnd.shuffle(keys); held |= set(keys[:per_unit])
    return dict(members), held


def build_all(works, held, path, log=print):
    """the catalogue's level without the held-out works: its ear (.npz) and vertical counts (.vertical.npy), counted once"""
    from study import heldout as H
    train = [w for w in works if L.label_key(w) not in held]
    wt = H.weights(train, None)
    ltm, v = level(train, lambda w: wt[w.id])
    ltm.save(path, about=dict(L_record='catalogue level for continuations, held out: %d works' % len(held), held=sorted(map(str, held))))
    np.savez(path.replace('.npz', '.vertical.npz'), c=v.c, c2=v.c2); log(f'catalogue level: {ltm.works} works, {ltm.notes} notes')
    return ltm, v


def load_all(path):
    z = np.load(path.replace('.npz', '.vertical.npz')); v = Vertical(); v.c, v.c2 = z['c'], z['c2']; return E.Long.load(path), v


def test(members, held, all_level, composer_works, max_notes=200, max_lines=4, log=print):
    """bits a note of each held-out work's lines, by model; the inner lines (neither the highest nor the lowest of three or more)
    apart. {unit: {model: [pitch, rhythm, notes, inner pitch, inner notes]}}, and for the whole model, each unit's surprise over
    8 notes (pitch and rhythm, bits a note) at its 10th, 25th, 50th, 75th and 90th percentiles: the band proposals are kept in"""
    ltm_all, v_all = all_level; out = {}; bands = {}
    for u, ws in members.items():
        test_ws = [w for w in ws if L.label_key(w) in held]; train_u = [w for w in ws if L.label_key(w) not in held]
        train_c = [w for w in composer_works[u[0]] if L.label_key(w) not in held]
        lu, vu = level(train_u); lc, vc = level(train_c)
        models = {'the ear (catalogue)': Model([('all', ltm_all, None)], vertical=False),
                  '+ composer': Model([('all', ltm_all, None), ('composer', lc, None)], vertical=False),
                  '+ composer + unit': Model([('all', ltm_all, None), ('composer', lc, None), ('unit', lu, None)], vertical=False),
                  '+ composer + unit, bias 1': Model([('all', ltm_all, None), ('composer', lc, None), ('unit', lu, None)], bias=1.0, vertical=False),
                  '+ composer + unit + vertical': Model([('all', ltm_all, v_all), ('composer', lc, vc), ('unit', lu, vu)])}
        res = {k: [[], [], [], []] for k in models}; windows = []
        for w in test_ws:
            ls = sorted((l[:max_notes] for l in counted(w).values() if len(l) >= 8), key=len, reverse=True)[:max_lines]
            if not ls: continue
            means = [sum(n[2] for n in l) / len(l) for l in ls]; order = sorted(range(len(ls)), key=lambda i: means[i])
            inner = set(order[1:-1]) if len(ls) >= 3 else set()
            for k, m in models.items():
                for i, l in enumerate(ls):
                    others = [x for j, x in enumerate(ls) if j != i]
                    heard = m.hear(l, w.final, others)
                    if k == '+ composer + unit + vertical':
                        b = [bp + (br or 0.0) for bp, br in heard]
                        windows += [float(np.mean(b[j:j + 8])) for j in range(0, len(b) - 7)]
                    for bp, br in heard:
                        res[k][0].append(bp)
                        if br is not None: res[k][1].append(br)
                        if i in inner: res[k][2].append(bp)
                        res[k][3].append(1)
        out[u] = {k: [float(np.mean(r[0])) if r[0] else None, float(np.mean(r[1])) if r[1] else None, len(r[0]),
                      float(np.mean(r[2])) if r[2] else None, len(r[2])] for k, r in res.items()}
        if windows: bands[u] = [float(x) for x in np.percentile(windows, [10, 25, 50, 75, 90])]
        log(u, len(test_ws), 'held out;', ' | '.join(f"{k}: {v[0]:.2f}/{v[1]:.2f}" + (f" inner {v[3]:.2f}" if v[3] else '') for k, v in out[u].items() if v[0]))
    return out, bands
