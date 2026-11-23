"""NotaGen's ear against ours, the inputs: each held-out work of the units NotaGen was fine-tuned on (study/notagen.py, UNITS), in
NotaGen's notation, with the places of the notes to score; and our bits for the same notes, as the standing test hears them (the
catalogue, composer and unit levels without the held-out works; the vertical view nested at 200, weight 0.75; each work's four
longest lines, their first 150 notes). Writes inputs.jsonl (for study/notagen_score.py) and ours.json beside this script.

Run: python3 -I prepare.py <score-reader checkout> <NotaGen checkout> <scratch folder with cont/units.pickle and cont/all-v25.npz>"""
import sys, os, json, pickle, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from study import continuations as C, lines as L, notagen as G
SR, NG, S = sys.argv[1:4]
HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time(); log = lambda *x: print(f'[{time.time() - t0:5.0f}s]', *x, flush=True)
small = pickle.load(open(os.path.join(S, 'cont/units.pickle'), 'rb')); held = small['held']
ltm_all, v_all = C.load_all(os.path.join(S, 'cont/all-v25.npz'))
CACHE = os.path.expanduser('/root/.cache/score-reader')
inputs, ours, skipped = [], {}, {}
for u, prompt in G.UNITS.items():
    ws = small['members'][u]; test_ws = sorted((w for w in ws if L.label_key(w) in held), key=lambda w: w.id)
    lu, vu = C.level([w for w in ws if L.label_key(w) not in held]); lc, vc = C.level([w for w in small['composers'][u[0]] if L.label_key(w) not in held])
    model = C.Model([('all', ltm_all, v_all), ('composer', lc, vc), ('unit', lu, vu)])
    for w in test_ws:
        r = G.prepare(w.id, prompt, CACHE, os.path.join(NG, 'data/xml2abc.py'), SR)
        if isinstance(r, str): skipped[w.id] = r; log('skipped', w.id, r); continue
        full = C.counted(w)
        top = sorted(((p, l[:150]) for p, l in full.items() if len(l) >= 8), key=lambda x: len(x[1]), reverse=True)[:4]
        parts = [p for p, _ in top]; ls = [l for _, l in top]
        means = [sum(n[2] for n in l) / len(l) for l in ls]; order = sorted(range(len(ls)), key=lambda i: means[i])
        inner = {parts[i] for i in order[1:-1]} if len(ls) >= 3 else set()
        bits = {}
        for i, (p, l) in enumerate(top):
            others = [x for j, x in enumerate(ls) if j != i]
            bits[p] = [bp for bp, _ in model.hear(l, w.final, others)]
        al = G.align(r['notes'], {p: full[p] for p in parts})
        notes, wanted = [], []
        for v, (p, idx) in al.items():
            for a, i in idx.items():
                k, c0, c1, t, midi, chord = r['notes'][v][a]
                if chord or not 2 <= i < len(dict(top)[p]): continue
                notes.append(dict(part=p, i=i, inner=p in inner, ours=bits[p][i - 2], voice=v, bar=k, onset=t, midi=midi))
                wanted.append((k, c0, c1))
        if not notes: skipped[w.id] = 'no notes aligned'; log('skipped', w.id, 'no notes aligned'); continue
        si = G.scoring_input(r['meta'], r['body'], wanted)
        shares = {v: round(len(idx) / max(1, min(400, len(r['notes'][v]))), 2) for v, (p, idx) in al.items()}
        inputs.append(dict(id=w.id, unit=' | '.join(u), prompt=list(prompt), windows=si['windows'], notes=si['notes']))
        ours[w.id] = dict(unit=' | '.join(u), voices={v: p for v, (p, _) in al.items()}, shares=shares, inner=sorted(inner),
                          low_to_high=[parts[i] for i in order],
                          bars=len(r['body']), windows=len(si['windows']), notes=notes)
        log(u[0], w.id, f"{len(notes)} notes ({sum(n['inner'] for n in notes)} inner), {len(si['windows'])} window(s),",
            'voices', {v: (p, shares[v]) for v, (p, _) in al.items()})
with open(os.path.join(HERE, 'inputs.jsonl'), 'w') as f:
    for x in inputs: f.write(json.dumps(x) + '\n')
json.dump(dict(works=ours, skipped=skipped), open(os.path.join(HERE, 'ours.json'), 'w'), indent=1, ensure_ascii=False)
log('done:', len(inputs), 'works,', sum(len(x['notes']) for x in inputs), 'notes;', len(skipped), 'skipped')
