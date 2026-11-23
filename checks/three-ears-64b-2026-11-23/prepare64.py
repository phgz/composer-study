"""Three ears on piece 64b's inner voices, the inputs: NotaGen's (study/notagen.py) and AMT's (study/amt.py), for
  - the inner voices as chosen, the whole piece: each alto and tenor note, given the tune and the bass;
  - every proposal the continuations drew for 64b (composer-blend, pieces/64b_inside_the_mazurka/proposals), heard as it was drawn:
    the inner voices chosen before its four bars, the tune and the bass, and for a tenor the alto chosen for the same bars;
  - for AMT also the 29 held-out works of checks/notagen-ear-2026-11-23, the same inner notes (the outer lines given), at a quarter
    note of 90 a minute (its tokens are seconds; a span the reading plays twice, counted once, leaves no silence of more than four
    beats).
And AMT's writing input: the tune and the bass in seconds, bar 1's inner voices, the spans to write (bars 2 to 80, 89 to 160).

Writes beside this script: notagen_inputs.jsonl, amt_inputs.jsonl (for study/notagen_score.py and study/amt_score.py), amt_write.json
(for study/amt_write.py) and notes64.json (which note is which).

Run: python3 -I prepare64.py <composer-blend> <renderer-engine> <NotaGen checkout> <anticipation checkout> <scratch with cont/units.pickle>"""
import glob, json, os, pickle, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..'))
import piece64 as P
from study import notagen as G, amt as A, continuations as C, lines as L

BLEND, RENDERER, NG, ACO, SCR = sys.argv[1:6]
XML2ABC = os.path.join(NG, 'data', 'xml2abc.py')
PROMPT = ('Romantic', 'Chopin, Frederic', 'Keyboard')                 # NotaGen has no Weber; 64b is Chopin's and Rachmaninoff's mazurka
QUARTER_S = 60 / 90                                                   # the held-out works' tempo, for AMT
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)

v = P.voices(BLEND, RENDERER); N = v['module']; sec = v['sec']
beats = {}; secs = {}
for name, b, d, m, t, dd in v['notes']: beats.setdefault(name, []).append((b, d, m)); secs.setdefault(name, []).append((t, dd, m))
for name in beats: beats[name].sort(); secs[name].sort()
outer_s = secs['tune'] + secs['bass']
ng_in, amt_in, meta = [], [], dict(chosen={}, proposals=[], works=[])


def ng_scored(r, voice_num, keep):
    """NotaGen's notes in ABC voice `voice_num` that `keep(onset, MIDI)` picks: [(line, first, last character)], [(onset, MIDI)]"""
    out, which = [], []
    for k, a, b, t, midi, chord in r['notes'].get(f'{voice_num}.0', []):
        if not chord and keep(t, midi): out.append((k, a, b)); which.append((t, midi))
    return out, which


def ng_input(vs, id_, voice_num, keep):
    with tempfile.TemporaryDirectory() as tmp:
        r = G.prepare_xml(P.piano_xml(vs, os.path.join(tmp, 'p.musicxml')), PROMPT, XML2ABC)
    if isinstance(r, str): raise RuntimeError(f'{id_}: {r}')
    wanted, which = ng_scored(r, voice_num, keep)
    si = G.scoring_window_ending(r['meta'], r['body'], wanted)
    ng_in.append(dict(id=id_, unit='64b', prompt=list(PROMPT), windows=si['windows'], notes=si['notes']))
    return which


def amt_input(events, given, scored, id_):
    """AMT's input: `events` asked, `given` controls; `scored` the events (by index in `events`) whose bits are wanted"""
    order = sorted(range(len(events)), key=lambda i: (events[i][0], events[i][2]))
    rank = {i: r for r, i in enumerate(order)}
    seq, where = A.sequence(events, given, ACO)
    trip = [where[rank[i]] for i in scored]
    if id_ == '64b chosen' or id_.startswith('work '): ws, pos = A.windows(seq, trip, ACO)
    else: w, ps = A.window_ending(seq, trip, ACO); ws, pos = [w], [(0, p) for p in ps]
    amt_in.append(dict(id=id_, windows=ws, notes=pos))


# 1. the inner voices as chosen ---------------------------------------------------------------------------------------------------
inner_beats = {n: beats[n] for n in ('alto', 'tenor')}
for vn, voice in ((2, 'alto'), (3, 'tenor')):
    want = {(round(b, 6), m) for b, d, m in beats[voice]}
    which = ng_input(beats, f'64b chosen {voice}', vn, lambda t, m, want=want: (round(t, 6), m) in want)
    meta['chosen'][f'notagen {voice}'] = which
ev = secs['alto'] + secs['tenor']; tags = [('alto', b) for b, d, m in beats['alto']] + [('tenor', b) for b, d, m in beats['tenor']]
amt_input(ev, outer_s, list(range(len(ev))), '64b chosen')
meta['chosen']['amt'] = [(tg, b, m) for (tg, b), (t, d, m) in zip(tags, ev)]
log('chosen: NotaGen', {k: len(x) for k, x in meta['chosen'].items()})

# 2. every proposal, as it was drawn ------------------------------------------------------------------------------------------------
choices = json.load(open(os.path.join(BLEND, 'pieces/64b_inside_the_mazurka/choices64.json')))['voices']
chosen_k = {(s['section'], v_, s['segment']): s['chosen'] for v_ in choices for s in choices[v_]}
files = sorted(f for f in glob.glob(os.path.join(BLEND, 'pieces/64b_inside_the_mazurka/proposals/*-*-*.json')) if 'round' not in f)
for f in files:
    pf = json.load(open(f)); voice = pf['voice']; sec_, seg = pf['section'], pf['segment']
    s0, s1 = (pf['bars'][0] - 1) * P.METRE, pf['bars'][1] * P.METRE
    for k, prop in enumerate(pf['proposals']):
        notes = [tuple(n) for n in prop['notes']]; first = notes[0][0]

        def before(l, until, drawn_to=None):
            """a voice's chosen notes beginning before `until`, cut there; the last drawn out to `drawn_to`, as inner() draws it"""
            out = [(b, min(d, until - b), m) for b, d, m in l if b < until - 1e-6]
            if drawn_to is not None and out and not N.resting(out[-1][0] + out[-1][1], drawn_to):
                out[-1] = (out[-1][0], drawn_to - out[-1][0], out[-1][2])
            return out
        if voice == 'alto':
            vs = dict(tune=beats['tune'], bass=beats['bass'], alto=before(beats['alto'], first, first) + notes, tenor=before(beats['tenor'], s0))
            given_extra = []
        else:
            vs = dict(tune=beats['tune'], bass=beats['bass'], alto=before(beats['alto'], s1), tenor=before(beats['tenor'], first, first) + notes)
            given_extra = [n for n in vs['alto'] if n[0] >= s0 - 1e-6]                       # the alto of these bars, known in full
        id_ = f'64b {sec_}-{voice}-{seg} #{k}'
        want = {(round(b, 6), m) for b, d, m in notes}
        which = ng_input(vs, id_, 2 if voice == 'alto' else 3, lambda t, m, want=want: (round(t, 6), m) in want)
        alto_ev = [n for n in vs['alto'] if n[0] < s0 - 1e-6] if voice == 'tenor' else vs['alto']
        inner_ev = alto_ev + vs['tenor']                                                   # the proposal's notes come last in its voice
        end = len(alto_ev) if voice == 'alto' else len(inner_ev)
        scored = list(range(end - len(notes), end))
        assert [inner_ev[i] for i in scored] == notes
        ev = P.seconds(inner_ev, sec)
        amt_input(ev, outer_s + P.seconds(given_extra, sec), scored, id_)
        meta['proposals'].append(dict(id=id_, section=sec_, voice=voice, segment=seg, k=k, chosen=k == chosen_k[(sec_, voice, seg)],
                                      ours=prop['bits'], n=len(notes), notagen_notes=len(which), amt_notes=len(scored)))
    log(os.path.basename(f), len(pf['proposals']), 'proposals')

# 3. AMT on the 29 held-out works ---------------------------------------------------------------------------------------------------
ours = json.load(open(os.path.join(HERE, '..', 'notagen-ear-2026-11-23', 'ours.json')))['works']
small = pickle.load(open(os.path.join(SCR, 'cont/units.pickle'), 'rb'))
byid = {w.id: w for ws in small['members'].values() for w in ws}
for wid, o in ours.items():
    full = C.counted(byid[wid]); order = o['low_to_high']; inner = o['inner']
    if not inner: continue
    capped = {p: full[p][:150] for p in order}
    scored_keys = [(p, i) for p in inner for i in range(2, len(capped[p]))]
    t_end = max(capped[p][i][0] for p, i in scored_keys)
    asked = [(p, i, n) for p in inner for i, n in enumerate(full[p]) if n[0] <= t_end + 1e-6]
    given = [n for p in (order[0], order[-1]) for n in full[p] if n[0] <= t_end + 9]   # the outer lines, 6 seconds past the last
    spans = sorted((n[0], n[0] + n[1]) for n in [x[2] for x in asked] + given)        # silences of more than a bar where no line
    cuts, reach = [], spans[0][1]                                                       # sounds (a span played twice, counted once),
    for a, b in spans[1:]:                                                              # closed
        if a > reach + 4: cuts.append((reach, a - reach))
        reach = max(reach, b)
    shift = lambda t: t - sum(g for at, g in cuts if at < t - 1e-9)
    s_ = lambda n: (shift(n[0]) * QUARTER_S, max(n[1], .05) * QUARTER_S, n[2])
    ev = [s_(n) for _, _, n in asked]; keyidx = {(p, i): j for j, (p, i, _) in enumerate(asked)}
    want = {(n['part'], n['i']) for n in o['notes'] if n['inner']}
    scored = [keyidx[k] for k in scored_keys if k in want]
    amt_input(ev, [s_(n) for n in given], scored, f'work {wid}')
    meta['works'].append(dict(id=wid, unit=o['unit'], notes=[asked[j][:2] for j in scored], silences_closed=len(cuts)))
log('works:', len(meta['works']))

# 4. AMT writing 64b's inner voices ---------------------------------------------------------------------------------------------------
write = dict(given=outer_s, history=[n for n in secs['alto'] + secs['tenor'] if n[0] < sec(P.METRE) - 1e-6],
             spans=[[sec(P.METRE), sec(80 * P.METRE)], [sec(88 * P.METRE), sec(P.BARS * P.METRE)]],
             beats=[[b, sec(b)] for b in [x / 4 for x in range(0, P.BARS * P.METRE * 4 + 1)]])
json.dump(write, open(os.path.join(HERE, 'amt_write.json'), 'w'))
for name, rows in (('notagen_inputs.jsonl', ng_in), ('amt_inputs.jsonl', amt_in)):
    with open(os.path.join(HERE, name), 'w') as fh:
        for x in rows: fh.write(json.dumps(x) + '\n')
json.dump(meta, open(os.path.join(HERE, 'notes64.json'), 'w'), indent=1)
log('done:', len(ng_in), 'NotaGen inputs,', len(amt_in), 'AMT inputs')
