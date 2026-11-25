"""The glitch test, the inputs: wrong notes planted in the 29 held-out works of checks/notagen-ear-2026-11-23 and in piece 64b, for
NotaGen (study/notagen_score.py) and AMT (study/amt_score.py) to hear every note of each, as written and with the wrong notes.

  the wrong notes   in each work, notes picked at random (seeded by the work's id) among single notes at least an eighth long (no
                    chord, tie or grace note), from the third bar to the third last, at least four bars apart (64b: six), in any part;
                    two to eight a work by its length (one for each 60 notes). In 64b (the music the tool would be for), three sets
                    of sixteen, each set in copies of its own: forty-eight. Each is moved up or down (at random) by a semitone in
                    one copy, by a whole tone in another, spelt in its key's way. Every other note is the work's.
  checked           each copy's ABC differs from the work's at the planted notes, by the planted step, and nowhere else; a work
                    where it does not is left out (Mozart's K. 575 and K. 589: in each, one moved note is written without the
                    accidental its new pitch needs, even when music21 is told to show it)
  NotaGen           every note of every voice (a chord as its top note, as before), the work's own prompt (64b: "Romantic / Chopin,
                    Frederic / Keyboard", as in the three ears)
  AMT               every note (each note of a chord), no given notes: its sequence without controls, flagged as such (AUTOREGRESS),
                    as AMT's own generate() makes it; all on the piano; the works at a quarter note of 90 a minute, 64b in the seconds
                    the renderer plays it at, its doublings included

Writes beside this script: glitch_notagen_inputs.jsonl, glitch_amt_inputs.jsonl, glitch.json (which note is which, and the planted
notes). Ids: "<work> | as written", "<work> | semitone", "<work> | tone"; "64b | as written", "64b set <1-3> | semitone", ...

Run: python3 -I prepare_glitch.py <score-reader checkout> <NotaGen checkout> <anticipation checkout> <composer-blend> <renderer-engine>"""
import json, os, random, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'checks', 'three-ears-64b-2026-11-23'))
import rulers as R
from study import notagen as G, amt as A

SR, NG, ACO, BLEND, RENDERER = sys.argv[1:6]
CACHE = '/root/.cache/score-reader'
XML2ABC = os.path.join(NG, 'data', 'xml2abc.py')
KINDS = (('semitone', 1), ('tone', 2))
PROMPT64 = ('Romantic', 'Chopin, Frederic', 'Keyboard')
VOICE64 = dict(tune='1.0', alto='2.0', tenor='3.0', bass='4.0')
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
ng_in, amt_in, meta = [], [], dict(works={}, skipped={})


def pick(cands, k, spacing, rnd):
    """up to k candidates (part, element, bar) at least `spacing` bars apart, in a seeded random order"""
    cands = list(cands); rnd.shuffle(cands); out = []
    for c in cands:
        if len(out) == k: break
        if all(abs(c[2] - o[2]) >= spacing for o in out): out.append(c)
    return sorted(out, key=lambda c: (c[2], c[0]))


def ng_record(r, id_, prompt, key_of):
    """NotaGen's input for every note of r, and each note's [voice, index, chord, key]"""
    wanted, which = [], []
    for v in sorted(r['notes']):
        for i, (k, a, b, t, midi, chord) in enumerate(r['notes'][v]):
            wanted.append((k, a, b)); which.append([v, i, chord, key_of(v, i, t, midi)])
    si = G.scoring_input(r['meta'], r['body'], wanted)
    ng_in.append(dict(id=id_, prompt=list(prompt), windows=si['windows'], notes=si['notes']))
    return which


def amt_record(notes, id_):
    """AMT's input for every note [(onset s, length s, MIDI, key)], heard alone; each note's key in scoring order"""
    ev = [n[:3] for n in notes]
    order = sorted(range(len(ev)), key=lambda i: (ev[i][0], ev[i][2])); rank = {i: r for r, i in enumerate(order)}
    seq, where = A.sequence(ev, [], ACO)
    trip = [where[rank[i]] for i in range(len(ev))]
    ws, pos = A.windows(seq, trip, ACO, alone=True)
    amt_in.append(dict(id=id_, windows=ws, notes=pos))
    return [list(n[3]) for n in notes]


# 1. the 29 held-out works --------------------------------------------------------------------------------------------------------
ours = json.load(open(os.path.join(ROOT, 'checks', 'notagen-ear-2026-11-23', 'ours.json')))['works']
prompts = {' | '.join(u): p for u, p in G.UNITS.items()}
for wid, o in ours.items():
    prompt = prompts[o['unit']]
    s = R.stream_of(wid, CACHE, SR); lines = R.lines_of(s)
    r0 = R.abc_of(s, prompt, XML2ABC)
    if isinstance(r0, str): meta['skipped'][wid] = r0; log('skipped', wid, r0); continue
    al = G.align(r0["notes"], lines, cap=10 ** 6)
    key_line = {}                                                             # (voice, ABC index) -> (part, onset, MIDI)
    for v, (p, idx) in al.items():
        for a, i in idx.items(): n = lines[p][i]; key_line[(v, a)] = [p, round(n[0], 4), n[2]]
    aligned_parts = {p for p, _ in al.values()}
    n_notes = sum(len(l) for p, l in lines.items() if p in aligned_parts)
    k = max(2, min(8, n_notes // 60)); rnd = random.Random(wid)
    cands = [c for c in R.eligible(s) if c[0] in aligned_parts]
    picks = pick(cands, k, 4, rnd); signs = [rnd.choice((-1, 1)) for _ in picks]
    elx = dict(R.elements(s))
    planted = []
    for (pi, ei, bar), sg in zip(picks, signs):
        el = elx[pi][ei]; planted.append(dict(part=pi, element=ei, bar=bar + 1, onset=round(float(el.getOffsetInHierarchy(s)), 4),
                                              midi=el.pitch.midi, sign=sg))
    copies = {'as written': (s, r0)}
    ok = True
    for kind, step in KINDS:
        s1 = R.moved(s, [(p['part'], p['element'], p['sign'] * step) for p in planted]); r1 = R.abc_of(s1, prompt, XML2ABC)
        d = R.differences(r0, r1) if not isinstance(r1, str) else r1
        want = {}
        for p in planted:
            hit = [va for va, key in key_line.items() if key == [p['part'], p['onset'], p['midi']]]
            if len(hit) == 1: want[hit[0]] = (p['midi'], p['midi'] + p['sign'] * step)
        if isinstance(d, str) or d != want or len(want) != len(planted):
            meta['skipped'][wid] = f'{kind}: the copy differs elsewhere ({d if isinstance(d, str) else sorted(set(d) ^ set(want))})'
            log('skipped', wid, meta['skipped'][wid]); ok = False; break
        copies[kind] = (s1, r1)
    if not ok: continue
    for kind, (sc, r) in copies.items():
        step = dict(KINDS).get(kind, 0)
        moved_keys = {(p['part'], p['onset'], p['midi']): p['midi'] + p['sign'] * step for p in planted}

        def key_of(v, i, t, midi, moved_keys=moved_keys):
            key = key_line.get((v, i))
            if key is None: return None
            return [key[0], key[1], moved_keys.get(tuple(key), key[2])]
        which_ng = ng_record(r, f'{wid} | {kind}', prompt, key_of)
        which_amt = amt_record(R.amt_notes(sc), f'{wid} | {kind}')
        meta['works'].setdefault(wid, dict(unit=o['unit'], prompt=list(prompt), planted=planted, copies={}))
        meta['works'][wid]['copies'][kind] = dict(notagen=which_ng, amt=which_amt)
    log(wid, f'{len(planted)} planted, {n_notes} notes in aligned lines,', f"{len(ng_in[-1]['windows'])} NotaGen window(s),",
        f"{len(amt_in[-1]['windows'])} AMT window(s)")

# 2. piece 64b ----------------------------------------------------------------------------------------------------------------------
import piece64 as P
v = P.voices(BLEND, RENDERER)
notes = [list(n) for n in v['notes']]                                        # [voice, beat, beats, MIDI, onset s, length s]
at = {}
for j, (name, b, d, m, t, dd) in enumerate(notes): at.setdefault((name, round(b, 4)), []).append(j)
cands = [(name, j, int(b // P.METRE)) for j, (name, b, d, m, t, dd) in enumerate(notes)
         if len(at[(name, round(b, 4))]) == 1 and d >= .5 and 2 <= int(b // P.METRE) < P.BARS - 2]
SETS = 3                                                                     # three sets of sixteen, each its own copies


def copy64(planted, step):
    ns = [list(n) for n in notes]
    for p in planted: ns[p['note']][3] = p['midi'] + p['sign'] * step
    vs = {}
    for name, b, d, m, t, dd in ns: vs.setdefault(name, []).append((b, d, m))
    with tempfile.TemporaryDirectory() as tmp:
        r = G.prepare_xml(P.piano_xml({k: sorted(x) for k, x in vs.items()}, os.path.join(tmp, 'p.musicxml')), PROMPT64, XML2ABC)
    if isinstance(r, str): raise RuntimeError(r)
    return ns, r


name_of = {x: k for k, x in VOICE64.items()}
unmatched = [0]


def records64(ns, r, id_):
    have = {(name, round(b, 4), m) for name, b, d, m, t, dd in ns}

    def key_of(vv, i, t, midi):
        key = (name_of.get(vv), round(t, 4), midi)
        if key not in have: unmatched[0] += 1; return None
        return list(key)
    return dict(notagen=ng_record(r, id_, PROMPT64, key_of),
                amt=amt_record([(t, dd, m, (name, round(b, 4), m)) for name, b, d, m, t, dd in ns], id_))


ns0, r0 = copy64([], 0)
meta['piece64'] = dict(prompt=list(PROMPT64), as_written=records64(ns0, r0, '64b | as written'), sets={})
for k in range(1, SETS + 1):
    rnd = random.Random(f'64b set {k}'); picks = pick(cands, 16, 6, rnd); signs = [rnd.choice((-1, 1)) for _ in picks]
    planted = [dict(voice=name, note=j, bar=bar + 1, beat=round(notes[j][1], 4), midi=notes[j][3], sign=sg)
               for (name, j, bar), sg in zip(picks, signs)]
    meta['piece64']['sets'][str(k)] = dict(planted=planted, copies={})
    for kind, step in KINDS:
        ns1, r1 = copy64(planted, step); d = R.differences(r0, r1)
        if isinstance(d, str): raise RuntimeError(f'64b {kind}: {d}')
        got = {(name_of[vv], round(r0['notes'][vv][i][3], 4), a, b) for (vv, i), (a, b) in d.items()}
        want = {(p['voice'], p['beat'], p['midi'], p['midi'] + p['sign'] * step) for p in planted}
        if got != want: raise RuntimeError(f'64b {kind}: the copy differs elsewhere ({sorted(got ^ want)})')
        meta['piece64']['sets'][str(k)]['copies'][kind] = records64(ns1, r1, f'64b set {k} | {kind}')
    log(f'64b set {k}:', [(p['voice'], p['bar']) for p in planted])
log('64b:', SETS, 'sets of 16 planted,', len(notes), 'notes;', unmatched[0], "NotaGen notes not matched to 64b's own")

with open(os.path.join(HERE, 'glitch_notagen_inputs.jsonl'), 'w') as f:
    for x in ng_in: f.write(json.dumps(x) + '\n')
with open(os.path.join(HERE, 'glitch_amt_inputs.jsonl'), 'w') as f:
    for x in amt_in: f.write(json.dumps(x) + '\n')
json.dump(meta, open(os.path.join(HERE, 'glitch.json'), 'w'))
log('done:', len(meta['works']), 'works and 64b,', len(ng_in), 'NotaGen inputs,', len(amt_in), 'AMT inputs;', len(meta['skipped']), 'skipped')
