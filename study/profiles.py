"""Profiles of narrow units: a composer in one kind of piece and one period, measured from the notes and set against the other
composers of the same kind and period, with pointers to the bars that show each trait.

A unit's works: a work belongs to a unit for each kind score-reader's facts give it (a gavotte of a suite is in 'suite',
'gavotte' and 'dance'), in the period data/periods.json gives it (by its year, its number or its title; a work none places is in
the composer's unit for the kind across his periods, 'any period'). A unit is profiled when it holds at least 3 works; its traits and figures are sought when it holds 5.

What is measured, each work weighing one (the mean of its works):
  the melody: in a work for a voice and accompaniment, the voice, where the reading names its parts; else the top line (the line
  with the highest mean pitch); its sounding skyline:
    steps          the share of its moves of one or two semitones
    repeats        the share of repeated notes
    leaps          the share of moves of a fourth or more
    move           the mean size of a move, in semitones (repeated notes left out)
    rising         the share of moves that rise
    leap answered  the share of leaps followed by a step the other way
    range          the span of its middle 90%, in semitones
    register       its median pitch
    even           the share of notes whose time-span is the one before's
    long-short     the share of notes whose time-span is three times the one before's, or a third of it (dotted figures)
    rhythm variety the entropy of its time-span ratios, in bits
    surprise       the listener's ear (study/ear.py, saved by study/critic.py), its first 300 notes: bits a note of pitch, of rhythm.
                   The ear learnt the whole catalogue, these works too: what it measures is how closely a melody keeps to the
                   ways of the catalogue and of itself, not how new it was in its day
  the texture:
    density        notes a quarter, every note of the reading
    lines          its pitched lines

Set against: the works of the other composers of the same kind, for the same forces, in the same shared period (data/eras.json);
where they are fewer than 20, those of the kind in the period for any forces, then those of the kind in any period, then the works
for the same forces in the period, of any kind; the comparison says which. The others' works weigh as at a shared level (a
composer at most a tenth, a collection at most a third). A measure is a trait where a work of the unit stands above a work of the
others 75 times in 100 or more, or 25 or fewer (with 5 works of the unit and 20 of the others at least). Range, register and
density are set only against works for the same forces; the number of lines, which follows how an edition lays out its staves, is
shown and not set against anything.

Figures: the four-note figures of the top line, each its three moves and the rhythm of its notes (each time-span against the one
before: much shorter, shorter, as long, longer, much longer), counted in the unit (a figure at most three times a work) and in the
works it is set against (weighted as above); a figure the unit uses far more than they do (a z-score of its log-odds over 3, with
an informative prior: Monroe, Colaresi and Quinn 2008), 5 times at least and in two of its works, is one of its figures, with the
bars where it stands."""
import collections, math, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from study import ear as E, periods as PD, eras as R, harmony as HM

MIN_WORKS = 3
NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def name(m): return NAMES[int(m) % 12] + str(int(m) // 12 - 1)


VOICE = re.compile(r'(?i)voice|voix|voce|singstimme|gesang|canto|soprano|sopran|mezzo|contralto|\balto\b|tenor|baritone?|bariton|basso\b(?! continuo)|bass voice')
SUNG = ('voice and keyboard', 'voice and lute', 'voice and instruments', 'voice and orchestra')


def top_line(work, forces=None):
    """the melody: in a work for a voice and accompaniment, the voice (its part named so); else the line with the highest mean pitch"""
    if forces in SUNG and work.names:
        sung = [l for p, l in work.lines.items() if VOICE.search(work.names.get(p) or '')]
        if sung: return max(sung, key=lambda l: sum(n[2] for n in l) / len(l))
    return max(work.lines.values(), key=lambda l: sum(n[2] for n in l) / len(l))


def measure(work, ear=None, max_notes=300, forces=None):
    """one work's measures (dict); `ear`: a saved study.ear.Long, for the surprise"""
    top = top_line(work, forces); m = np.array([n[2] for n in top]); on = np.array([n[0] for n in top])
    iv = np.diff(m); moves = iv[iv != 0]; out = {}
    if len(iv) < 8: return None
    out['steps'] = float(np.mean((np.abs(iv) >= 1) & (np.abs(iv) <= 2))); out['repeats'] = float(np.mean(iv == 0))
    out['leaps'] = float(np.mean(np.abs(iv) >= 5)); out['move'] = float(np.mean(np.abs(moves))) if len(moves) else 0.0
    out['rising'] = float(np.mean(moves > 0)) if len(moves) else 0.5
    lp = [i for i in range(len(iv) - 1) if abs(iv[i]) >= 5]
    out['leap answered'] = float(np.mean([np.sign(iv[i + 1]) == -np.sign(iv[i]) and 1 <= abs(iv[i + 1]) <= 2 for i in lp])) if lp else None
    out['range'] = float(np.percentile(m, 95) - np.percentile(m, 5)); out['register'] = float(np.median(m))
    span = np.diff(on); ok = (span[:-1] > 0) & (span[1:] > 0); r = span[1:][ok] / span[:-1][ok]
    if len(r):
        out['even'] = float(np.mean(np.abs(np.log2(r)) < 0.05))
        out['long-short'] = float(np.mean(np.abs(np.abs(np.log2(r)) - math.log2(3)) < 0.1))
        sym = np.clip(np.round(2 * np.log2(r)) / 2, -3, 3); _, c = np.unique(sym, return_counts=True); p = c / c.sum()
        out['rhythm variety'] = float(-(p * np.log2(p)).sum())
    out['density'] = work.notes / work.length if work.length else None; out['lines'] = len(work.lines)
    if ear is not None:
        x = E.listen([n[:3] for n in top[:max_notes]], work.final, ear)[1:]
        out['surprise, pitch'] = float(np.mean([a[0] for a in x])); out['surprise, rhythm'] = float(np.mean([a[1] for a in x]))
    return out


MEASURES = ('steps', 'repeats', 'leaps', 'move', 'rising', 'leap answered', 'range', 'register', 'even', 'long-short', 'rhythm variety',
            'surprise, pitch', 'surprise, rhythm', 'density', 'lines')


RHYTHM = {-2: 'much shorter', -1: 'shorter', 0: 'as long', 1: 'longer', 2: 'much longer'}


def _ratio(a, b):
    """the time-span b against the one before, a: -2 (half or less), -1, 0 (the same), 1, 2 (twice or more)"""
    if a <= 0 or b <= 0: return 0
    r = math.log2(b / a)
    return 0 if abs(r) < 0.05 else (2 if r >= 0.95 else 1) if r > 0 else (-2 if r <= -0.95 else -1)


def figures(work, forces=None):
    """the melody's four-note figures, each a tuple of its three moves and the three time-spans' ratios to the span before:
    {figure: [(bar, onset, index), ...]}"""
    top = top_line(work, forces); out = collections.defaultdict(list)
    for i in range(1, len(top) - 3):
        moves = tuple(int(top[i + k + 1][2] - top[i + k][2]) for k in range(3))
        if any(abs(x) > 12 for x in moves): continue
        spans = [top[i + k][0] - top[i + k - 1][0] for k in range(4)]
        rhythm = tuple(_ratio(spans[k], spans[k + 1]) for k in range(3))
        out[moves + rhythm].append((top[i][3], top[i][0], i))
    return out


def units_of(work, facts, periods):
    """the units (composer, kind, forces, period) a work belongs to: one for each kind its facts give it"""
    f = facts.get(work.id) or {}
    kinds = f.get('kind') or []
    if not kinds: return []
    year = (f.get('year') or [None])[0]
    period, _ = PD.period_of(dict(composer=work.composer, keys=f.get('keys') or [], label=work.label), periods, year=year)
    return [(work.composer, k, f.get('forces'), period or 'any period') for k in kinds]


def log_odds(unit, rest, a0=1000.0):
    """z-scores of the log-odds ratio of each figure in the unit against the rest (Monroe, Colaresi and Quinn 2008), with an
    informative Dirichlet prior of total weight a0 spread by the pooled frequencies"""
    keys = set(unit) | set(rest); nu = sum(unit.values()); nr = sum(rest.values())
    T = nu + nr; out = {}
    for k in keys:
        yu, yr = unit.get(k, 0), rest.get(k, 0); a = a0 * (yu + yr) / T
        if a <= 0: continue
        d = math.log((yu + a) / max(nu + a0 - yu - a, 1e-9)) - math.log((yr + a) / max(nr + a0 - yr - a, 1e-9))
        out[k] = d / math.sqrt(1 / (yu + a) + 1 / (yr + a))
    return out


def auc(xs, ys, wy):
    """how often a work of the unit stands above a work of the others (weighted by the others' weights): 1 always, 0.5 as often as
    not, 0 never"""
    ys = np.asarray(ys, float); wy = np.asarray(wy, float); tot = wy.sum(); out = []
    for x in xs: out.append((wy[ys < x].sum() + 0.5 * wy[ys == x].sum()) / tot)
    return float(np.mean(out))


MIN_TRAIT, MIN_REST, AUC_CUT = 5, 20, 0.75
BY_FORCES = ('register', 'density', 'range')                                # set against works for the same forces only
INFO = ('lines',)                                                           # how an edition lays out its staves, not a trait


def build(works, facts, surprise=None, log=print):
    """every unit with MIN_WORKS works: {unit: profile}. `surprise`: {work id: (pitch, rhythm, notes)}, from the saved ear"""
    from study import lines as L
    periods = PD.table(); eras = R.table()
    era = lambda c: (eras.get(c) or {}).get('era')
    per_work, figs, members, by_id, per_harm, progs = {}, {}, collections.defaultdict(list), {}, {}, {}
    marked = HM.cadence_collections(works)
    for k, w in enumerate(works):
        us = units_of(w, facts, periods)
        if not us: continue
        forces = (facts.get(w.id) or {}).get('forces')
        mw = measure(w, forces=forces)
        if mw is None: continue
        if surprise and w.id in surprise: mw['surprise, pitch'], mw['surprise, rhythm'] = surprise[w.id][:2]
        per_work[w.id] = mw; figs[w.id] = figures(w, forces); by_id[w.id] = w
        if w.harmony:                                                      # the analysts' labels: the harmony
            hm = HM.measure(w, top_line(w, forces), cadences=w.collection in marked)
            if hm is not None: per_harm[w.id] = hm; progs[w.id] = HM.progressions(w)
        for u in us: members[u].append(w)
        if log and k % 4000 == 0: log(f'  {k} of {len(works)} works measured')
    units = {u: ws for u, ws in members.items() if len(ws) >= MIN_WORKS}
    pool = collections.defaultdict(set)                                       # the works of every composer by (kind, forces, era), (kind, era), kind
    for u, ws in members.items():
        for w in ws:
            pool[('kind, forces, period', u[1], u[2], era(u[0]))].add(w.id); pool[('kind, period', u[1], era(u[0]))].add(w.id); pool[('kind', u[1])].add(w.id)
    for u, ws in members.items():
        for w in ws: pool[('forces, period', u[2], era(u[0]))].add(w.id)
    def rest_of(u):
        for key in (('kind, forces, period', u[1], u[2], era(u[0])), ('kind, period', u[1], era(u[0])), ('kind', u[1]), ('forces, period', u[2], era(u[0]))):
            if u[2] is None and key[0] in ('kind, forces, period', 'forces, period'): continue
            ids = [i for i in pool[key] if by_id[i].composer != u[0]]
            if len(ids) >= MIN_REST: return key, ids
        return None, []
    work_counts = {i: collections.Counter({f: min(len(v), 3) for f, v in figs[i].items()}) for i in per_work}
    hpool = collections.defaultdict(set)                                      # the labelled works, by (kind, forces, era), (forces, era), era
    for u, ws in members.items():
        for w in ws:
            if w.id in per_harm:
                hpool[('kind, forces, period', u[1], u[2], era(u[0]))].add(w.id); hpool[('forces, period', u[2], era(u[0]))].add(w.id); hpool[('period', era(u[0]))].add(w.id)
    out = {}
    for u, ws in units.items():
        key, rest = rest_of(u)
        wt = L.capped({i: 1.0 for i in rest}, [(lambda i: by_id[i].composer, 0.1), (lambda i: by_id[i].collection, 1 / 3)]) if rest else {}
        values = {}; traits = []; same_forces = key is not None and key[0] in ('kind, forces, period', 'forces, period')
        for m in MEASURES:
            xs = [per_work[w.id][m] for w in ws if per_work[w.id].get(m) is not None]
            if not xs: continue
            values[m] = float(np.mean(xs))
            ys = [(per_work[i][m], wt[i]) for i in rest if per_work[i].get(m) is not None]
            if len(xs) < MIN_TRAIT or len(ys) < MIN_REST or m in INFO or (m in BY_FORCES and not same_forces): continue
            a = auc(xs, [y for y, _ in ys], [w_ for _, w_ in ys])
            if a >= AUC_CUT or a <= 1 - AUC_CUT:
                tot = sum(w_ for _, w_ in ys)
                traits.append(dict(measure=m, value=values[m], others=float(sum(y * w_ for y, w_ in ys) / tot), auc=a))
        fig_out = []
        if rest and len(ws) >= MIN_TRAIT:
            mine = collections.Counter(); where = collections.defaultdict(list)
            for w in ws:
                mine.update(work_counts[w.id])
                for f, occ in figs[w.id].items(): where[f].append((w, occ))
            others = collections.Counter(); scale = len(rest) / sum(wt.values())
            for i in rest:
                for f, c in work_counts[i].items(): others[f] += c * wt[i] * scale
            z = log_odds(mine, others)
            good = sorted(((s, f) for f, s in z.items() if s > 3 and len(where[f]) >= 2 and mine[f] >= 5), reverse=True)
            for s, f in good[:6]:
                pts = []
                for w, occ in sorted(where[f], key=lambda x: -len(x[1]))[:3]:
                    bar, onset, i = occ[0]; line = top_line(w, u[2])
                    pts.append(dict(work=w.id, label=w.label, bar=bar, notes=' '.join(name(n[2]) for n in line[i:i + 4])))
                fig_out.append(dict(moves=list(f[:3]), rhythm=list(f[3:]), z=round(s, 1), works=len(where[f]),
                                    per_1000=round(1000 * mine[f] / max(1, sum(mine.values())), 1),
                                    others_per_1000=round(1000 * others.get(f, 0) / max(1, sum(others.values())), 1), at=pts))
        out[u] = dict(composer=u[0], kind=u[1], forces=u[2], period=u[2 + 1], era=era(u[0]), works=len(ws), values=values, traits=traits,
                      figures=fig_out, compared=dict(by=key[0] if key else None, works=len(rest), composers=len({by_id[i].composer for i in rest})))
        h = harmony_of(u, ws, per_harm, progs, hpool, by_id, era, L)
        if h: out[u]['harmony'] = h
    return out


def harmony_of(u, ws, per_harm, progs, hpool, by_id, era, L):
    """a unit's harmony, from its labelled works (3 or more): the measures, the traits against other composers' labelled works
    (of the kind for the forces in the period; else for the forces in the period; else in the period), its progressions"""
    mine = [w for w in ws if w.id in per_harm]
    if len(mine) < MIN_WORKS: return None
    by = collections.Counter(HM.source(w) for w in mine); main = by.most_common(1)[0][0]
    key, rest = None, []
    for k in (('kind, forces, period', u[1], u[2], era(u[0])), ('forces, period', u[2], era(u[0])), ('period', era(u[0]))):
        ids = [i for i in hpool.get(k, ()) if by_id[i].composer != u[0]]
        if len(ids) >= MIN_REST: key, rest = k, ids; break
    wt = L.capped({i: 1.0 for i in rest}, [(lambda i: by_id[i].composer, 0.1), (lambda i: by_id[i].collection, 1 / 3)]) if rest else {}
    values, traits = {}, []; same_forces = key is not None and key[0] != 'period'
    for m in HM.MEASURES:
        xs = [per_harm[w.id][m] for w in mine if per_harm[w.id].get(m) is not None]
        if not xs: continue
        values[m] = float(np.mean(xs))
        if m in HM.BY_FORCES and not same_forces: continue                   # a chorale's melody is not set against a suite's
        if m in HM.BY_ANALYST:                                               # one analyst's keys against the same analyst's
            xs = [per_harm[w.id][m] for w in mine if per_harm[w.id].get(m) is not None and HM.source(w) == main]
            ys = [(per_harm[i][m], wt[i]) for i in rest if per_harm[i].get(m) is not None and HM.source(by_id[i]) == main]
        else: ys = [(per_harm[i][m], wt[i]) for i in rest if per_harm[i].get(m) is not None]
        if len(xs) < MIN_TRAIT or len(ys) < MIN_REST: continue
        a = auc(xs, [y for y, _ in ys], [w_ for _, w_ in ys])
        if a >= AUC_CUT or a <= 1 - AUC_CUT:
            tot = sum(w_ for _, w_ in ys); traits.append(dict(measure=m, value=values[m], others=float(sum(y * w_ for y, w_ in ys) / tot), auc=a))
    found = []; same = [i for i in rest if HM.source(by_id[i]) == main]
    prest = same if len(same) >= MIN_REST else rest                          # progressions against the same analyst's, where enough
    if prest and len(mine) >= MIN_TRAIT:
        pwt = L.capped({i: 1.0 for i in prest}, [(lambda i: by_id[i].composer, 0.1), (lambda i: by_id[i].collection, 1 / 3)])
        cnt = lambda i: collections.Counter({f: min(len(v), 3) for f, v in progs[i].items()})
        have = collections.Counter(); where = collections.defaultdict(list)
        for w in mine:
            have.update(cnt(w.id))
            for f, bars in progs[w.id].items(): where[f].append((w, bars))
        others = collections.Counter(); scale = len(prest) / sum(pwt.values())
        for i in prest:
            for f, c in cnt(i).items(): others[f] += c * pwt[i] * scale
        z = log_odds(have, others)
        good = sorted(((s, f) for f, s in z.items() if s > 3 and len(where[f]) >= 2 and have[f] >= 5), reverse=True)
        for s, f in good[:6]:
            found.append(dict(chords=list(f), z=round(s, 1), works=len(where[f]), per_1000=round(1000 * have[f] / max(1, sum(have.values())), 1),
                              others_per_1000=round(1000 * others.get(f, 0) / max(1, sum(others.values())), 1),
                              at=[dict(work=w.id, label=w.label, bar=bars[0]) for w, bars in sorted(where[f], key=lambda x: -len(x[1]))[:3]]))
    return dict(works=len(mine), by=dict(by), values=values, traits=traits, progressions=found,
                compared=dict(by=key[0] if key else None, works=len(rest), composers=len({by_id[i].composer for i in rest}),
                              progressions_by=main if prest is same else 'both', progressions_works=len(prest) if found or prest else 0))


MOVE = {0: 'same', 1: 'up a half step', -1: 'down a half step', 2: 'up a step', -2: 'down a step', 3: 'up a minor third', -3: 'down a minor third',
        4: 'up a major third', -4: 'down a major third', 5: 'up a fourth', -5: 'down a fourth', 7: 'up a fifth', -7: 'down a fifth'}
WORDS = {'steps': 'moves by step', 'repeats': 'repeated notes', 'leaps': 'leaps of a fourth or more', 'move': 'mean move (semitones)',
         'rising': 'moves that rise', 'leap answered': 'leaps answered by a step back', 'range': 'range of the melody (semitones)',
         'register': 'register of the melody', 'even': 'even rhythm (a note as long as the one before)', 'long-short': 'dotted figures (3:1)',
         'rhythm variety': 'rhythmic variety (bits)', 'surprise, pitch': "the ear's surprise, pitch (bits a note)",
         'surprise, rhythm': "the ear's surprise, rhythm (bits a note)", 'density': 'notes a quarter (texture)', 'lines': 'lines (texture)'}
SHARES = ('steps', 'repeats', 'leaps', 'rising', 'leap answered', 'even', 'long-short')


def fmt(m, x):
    if x is None: return '-'
    if m in SHARES: return f'{x:.0%}'
    if m == 'register': return name(round(x))
    return f'{x:.2f}' if m in ('move', 'rhythm variety', 'surprise, pitch', 'surprise, rhythm', 'density') else f'{x:.1f}'


def markdown(p):
    """a profile as Markdown, for a person"""
    what = f"{p['kind']}" + (f" ({p['forces']})" if p['forces'] else '')
    c = p['compared']
    against = {'kind, forces, period': f"other composers' {what} of the {p['era']} period", 'kind, period': f"other composers' {p['kind']} of the {p['era']} period, for any forces (too few for these forces: range, register and density not compared)",
               'kind': f"other composers' {p['kind']}, of any period and forces (range, register and density not compared)",
               'forces, period': f"other composers' works for {p['forces']} of the {p['era']} period, of any kind (too few {p['kind']})"}.get(c['by'], 'nothing: too few works by others to set it against')
    s = [f"### {p['composer']}: {what}, {p['period']}", '', f"{p['works']} works; set against {c['works']} works by {c['composers']} composers: {against}.", '']
    if p['traits']:
        s.append('**Where it stands apart** (how often one of its works stands above one of the others\': 75 times in 100 or more, or 25 or fewer):')
        for t in sorted(p['traits'], key=lambda t: -abs(t['auc'] - 0.5)):
            s.append(f"- {WORDS[t['measure']]}: {fmt(t['measure'], t['value'])}, against {fmt(t['measure'], t['others'])} ({t['auc'] * 100:.0f} in 100)")
    elif p['works'] < MIN_TRAIT: s.append(f"**Where it stands apart:** not asked (fewer than {MIN_TRAIT} works).")
    else: s.append('**Where it stands apart:** nowhere that clearly.')
    s += ['', '**Its figures** (four-note figures of the melody, with their rhythm, used far more than by the others; where they stand):']
    for f in p['figures']:
        moves = ', '.join(MOVE.get(x, f"{'up' if x > 0 else 'down'} {abs(x)}") for x in f['moves'])
        rh = ', '.join(RHYTHM[x] for x in f['rhythm'])
        at = '; '.join(f"{a['label']}, bar {a['bar']} ({a['notes']})" for a in f['at'])
        s.append(f"- {moves} ({rh}): {f['per_1000']} in 1,000 figures, against {f['others_per_1000']}, in {f['works']} works. At: {at}")
    if not p['figures']: s.append('- none stands out' if p['works'] >= MIN_TRAIT else '- not asked')
    s += ['', '**All measures:** ' + '; '.join(f"{WORDS[m]} {fmt(m, p['values'][m])}" for m in MEASURES if p['values'].get(m) is not None), '']
    h = p.get('harmony')
    if h:
        src = ' and '.join(f"{n} {k}'s" if k == 'DCML' else f"{n} When in Rome's" for k, n in h['by'].items())
        hc = h['compared']; ag = {'kind, forces, period': f"other composers' labelled {what} of the {p['era']} period",
                                  'forces, period': f"other composers' labelled works for {p['forces']} of the {p['era']} period, of any kind",
                                  'period': f"other composers' labelled works of the {p['era']} period"}.get(hc['by'], 'nothing: too few labelled works by others')
        note = (' Being for other forces, they are not compared for how often the chords change, nor for the melody against the chords.'
                if hc['by'] == 'period' else '')
        s += [f"**Harmony**, from the analysts' labels of {h['works']} of its works ({src}); set against {hc['works']} works by {hc['composers']} composers: {ag}."
              f" Changes of key and applied chords are compared within one analyst's labels.{note}", '']
        for t in sorted(h['traits'], key=lambda t: -abs(t['auc'] - 0.5)):
            s.append(f"- {HWORDS[t['measure']]}: {hfmt(t['measure'], t['value'])}, against {hfmt(t['measure'], t['others'])} ({t['auc'] * 100:.0f} in 100)")
        if not h['traits']: s.append('- where it stands apart: ' + ('nowhere that clearly' if h['works'] >= MIN_TRAIT else f'not asked (fewer than {MIN_TRAIT} labelled works)'))
        if h['progressions']:
            pb = hc.get('progressions_by'); s.append(f"- its progressions, against {hc.get('progressions_works')} of those works"
                                                     + (f", labelled by {'DCML' if pb == 'DCML' else 'When in Rome'} too:" if pb != 'both' else ', by either analyst:'))
        for f in h['progressions']:
            at = '; '.join(f"{a['label']}, bar {a['bar']}" for a in f['at'])
            s.append(f"- the progression {' – '.join(f['chords'])}: {f['per_1000']} in 1,000, against {f['others_per_1000']}, in {f['works']} works. At: {at}")
        s += ['', '*All its harmony:* ' + '; '.join(f"{HWORDS[m]} {hfmt(m, h['values'][m])}" for m in HM.MEASURES if h['values'].get(m) is not None), '']
    return '\n'.join(s)


HWORDS = {'chords a bar': 'chords a bar', 'tonic and dominant': 'chords on I or V', 'sevenths': 'seventh chords', 'diminished sevenths': 'diminished sevenths',
          'applied chords': 'applied chords (V/V and the like)', 'augmented sixths': 'augmented sixths', 'Neapolitan': 'Neapolitan chords', 'mixture': 'chords from the other mode',
          'inversions': 'chords over a bass not their root', 'keys a 10 bars': 'changes of key a 10 bars', 'away from home': 'chords away from the home key',
          'cadences a 10 bars': 'cadences a 10 bars (DCML)', 'perfect cadences': 'of its cadences, perfect', 'half cadences': 'of its cadences, half',
          'deceptive or evaded': 'of its cadences, deceptive or evaded', 'non-chord tones': "melody notes outside the chord",
          'changes': "chords labelled with a note in place of one of theirs, or added (V(4)), DCML", 'struck dissonance': 'of those, struck with the chord (appoggiaturas)', 'resolved by step': 'of those, resolved by a step',
          'suspensions': 'melody notes held into a chord they are not in, then falling a step (suspensions)'}


def hfmt(m, x): return f'{x:.0%}' if m in HM.SHARES else f'{x:.2f}'


def slug(composer):
    import unicodedata, re
    t = composer.replace('ł', 'l').replace('Ł', 'L').replace('ø', 'o').replace('đ', 'd')
    t = ''.join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c)).lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def write(profiles, out_dir, about):
    """one Markdown page and one JSON file a composer, and an index"""
    import json, os
    os.makedirs(out_dir, exist_ok=True); by = collections.defaultdict(list)
    for u, p in profiles.items(): by[p['composer']].append(p)
    order = lambda p: (p['kind'], str(p['forces']), p['period'])
    for c, ps in by.items():
        ps.sort(key=order)
        with open(os.path.join(out_dir, slug(c) + '.md'), 'w', encoding='utf-8') as f:
            f.write(f"# {c}\n\n{len(ps)} units, from score-reader's catalogue version {about.get('catalogue_version')} "
                    f"({about.get('score_reader')}). How they are measured: composer-study, `study/profiles.py`.\n\n" + '\n'.join(markdown(p) for p in ps))
        with open(os.path.join(out_dir, slug(c) + '.json'), 'w', encoding='utf-8') as f: json.dump(ps, f, indent=1, ensure_ascii=False)
    index = dict(about=about, composers={c: dict(file=slug(c) + '.md', units=[f"{p['kind']}{' (' + p['forces'] + ')' if p['forces'] else ''}, {p['period']}: {p['works']} works"
                                                                                  + (f", {p['harmony']['works']} labelled" if p.get('harmony') else '') for p in ps])
                                          for c, ps in sorted(by.items())})
    with open(os.path.join(out_dir, 'index.json'), 'w', encoding='utf-8') as f: json.dump(index, f, indent=1, ensure_ascii=False)


def main():
    import argparse, json, os, pickle, sys
    from study import lines as L
    ap = argparse.ArgumentParser(); ap.add_argument('ready'); ap.add_argument('--facts', help="facts.json; the ready-read copy's own by default"); ap.add_argument('--surprise')
    ap.add_argument('--works'); ap.add_argument('-o', required=True); a = ap.parse_args()
    works = pickle.load(open(a.works, 'rb')) if a.works else L.read(a.ready)
    path = a.facts or os.path.join(a.ready, 'facts.json')                     # the copy's own facts (catalogue version 25), else a checkout's
    facts = json.load(open(path, encoding='utf-8')); facts = facts.get('works', facts); surprise = json.load(open(a.surprise)) if a.surprise else None
    prof = build(works, facts, surprise, log=print)
    write(prof, a.o, dict(L.record(a.ready), surprise=bool(surprise)))
    print(len(prof), 'units of', len({p['composer'] for p in prof.values()}), 'composers written to', a.o)


if __name__ == '__main__': main()
