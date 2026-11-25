"""The repair test, the choice among AMT's rewrites (repair_<model>_<seed>.json, sixteen: AMT Large and Medium, seeds 1 to 8), by a
rule written before any was made (24 November 2026), and the same count for 64b as written and for Claude's rewrite.

  AMT's notes     those it wrote inside the two places (bar 21; bars 29 to 32), brought back to beats through 64b's tempo map,
                  the alto those from middle C up, the tenor those below (as amt64.py did)
  faults          counted in bars 20 to 22 and 28 to 33 (a place, the bar before and the bar after):
                    - notes64.check(): a voice under the one below it, parallel fifths or octaves, a voice out of its range
                    - a struck second: an inner note begun while another voice sounds a semitone or a minor ninth from it
                    - a unison: the alto and the tenor on one pitch at once
                    - three inner notes or more at once
                    - a beat of a place where no inner note sounds
                    - an inner voice leaping more than an octave
                    - a false relation: an inner note a semitone from the other inner voice's note begun up to a beat before it
  the choice      the fewest faults; then the fewest of AMT's notes repeating a given note's pitch begun within a third of a second
                  (an echo of the tune or bass); then Large before Medium; then the lower seed

Writes repair_chosen.json (the chosen rewrite's voices, in beats) and repair_choice.json (every candidate's count).

Run: python3 -I choose_repair.py <composer-blend>"""
import glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    blend = sys.argv[1]
    sys.path.insert(0, os.path.join(blend, 'pieces', '64b_inside_the_mazurka')); sys.path.insert(0, HERE)
    import notes64 as N
    os.environ['VERSION'] = 'written'
    import repair64 as R
    spec = json.load(open(os.path.join(HERE, 'amt_repair.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    beat = lambda t: float(np.interp(t, xt, xb))
    bars = [b for a, z in R.CLIPS for b in range(a, z + 1)]

    def faults(iv):
        out = [x for x in N.check(iv) if any(f'bar {b} ' in x for b in bars)]
        parts = dict(tune=N.TUNE, alto=iv['alto'], tenor=iv['tenor'], bass=N.BASS)
        sounding = lambda l, t: [n[2] for n in l if n[0] <= t + 1e-6 < n[0] + n[1] - 1e-6]
        for v in ('alto', 'tenor'):
            for b, d, p in iv[v]:
                if int(b // 3) + 1 not in bars: continue
                for w, l in parts.items():
                    if w == v: continue
                    if any(abs(p - q) in (1, 13) for q in sounding(l, b)): out.append(f'bar {int(b // 3) + 1} beat {b % 3 + 1:g}: {v} struck a second from the {w}')
        for v, w in (('alto', 'tenor'), ('tenor', 'alto')):
            l = [n for n in iv[v] if int(n[0] // 3) + 1 in bars]
            for x, y in zip(l, l[1:]):
                if abs(y[2] - x[2]) > 12: out.append(f'bar {int(y[0] // 3) + 1} beat {y[0] % 3 + 1:g}: the {v} leaps more than an octave')
            for b, d, p in l:                                   # a false relation: the other voice a semitone off, within a beat
                if any(abs(b - c) <= 1 + 1e-6 and (p - q) % 12 in (1, 11) and abs(p - q) < 12 and (b, d, p) != (c, e, q)
                       for c, e, q in iv[w] if c <= b): out.append(f'bar {int(b // 3) + 1} beat {b % 3 + 1:g}: the {v} a semitone from the {w} within a beat')
        for t in sorted({n[0] for v in ('alto', 'tenor') for n in iv[v] if int(n[0] // 3) + 1 in bars}):
            a, te = sounding(iv['alto'], t), sounding(iv['tenor'], t)
            if set(a) & set(te): out.append(f'bar {int(t // 3) + 1} beat {t % 3 + 1:g}: unison')
            if len(a) + len(te) >= 3: out.append(f'bar {int(t // 3) + 1} beat {t % 3 + 1:g}: three inner notes')
        for s0, s1 in R.SPANS:
            for t in np.arange(s0, s1, 1.0):
                if not (sounding(iv['alto'], t) or sounding(iv['tenor'], t)): out.append(f'bar {int(t // 3) + 1} beat {t % 3 + 1:g}: no inner note')
        return out

    iv0 = R._inner0()
    report = dict(written=faults(iv0), claude=faults(R.rewritten(iv0, R.CLAUDE)), candidates=[])
    spans = spec['spans']; given = spec['given']
    for f in sorted(glob.glob(os.path.join(HERE, 'repair_*_*.json'))):
        if os.path.basename(f) in ('repair_chosen.json', 'repair_choice.json'): continue
        w = json.load(open(f)); model = 'large' if 'large' in w['model'] else 'medium'
        mine = [n for n in w['notes'] if any(s0 - 1e-6 <= n[0] < s1 - 1e-6 for s0, s1 in spans)]
        new = dict(alto=[], tenor=[])
        for t, d, p, instr in mine:
            b = beat(t); span = d / .97 if d / .97 >= .45 else d / .85
            new['alto' if p >= 60 else 'tenor'].append((round(b, 4), round(max(beat(t + span) - b, .05), 4), int(p)))
        echoes = sum(any(abs(t - g[0]) <= .33 and p == g[2] for g in given) for t, d, p, i in mine)
        fl = faults(R.rewritten(iv0, new))
        report['candidates'].append(dict(file=os.path.basename(f), model=model, seed=w['seed'], notes=len(mine), echoes=echoes,
                                         faults=fl, voices={v: sorted(l) for v, l in new.items()}))
    cs = sorted(report['candidates'], key=lambda c: (len(c['faults']), c['echoes'], c['model'] != 'large', c['seed']))
    print('as written:', len(report['written']), report['written'])
    print("Claude's:", len(report['claude']), report['claude'])
    if not cs: print('no candidates yet'); return
    chosen = cs[0]
    json.dump(dict(file=chosen['file'], model=chosen['model'], seed=chosen['seed'], faults=chosen['faults'], voices=chosen['voices']),
              open(os.path.join(HERE, 'repair_chosen.json'), 'w'), indent=1)
    json.dump(report, open(os.path.join(HERE, 'repair_choice.json'), 'w'), indent=1)
    for c in cs: print(c['file'], c['notes'], 'notes,', c['echoes'], 'echoes,', len(c['faults']), 'faults', c['faults'][:4])
    print('chosen:', chosen['file'])


if __name__ == '__main__':
    main()
