"""The bracket test, the inputs: every piece Philip has rated a single mark, for AMT to hear note by note, keeping at each note how
surprised it was (the bits of the pitch) and how unsure it was beforehand (the entropy of its guess at the pitch).

  the pieces   the 30 of data/rated.json, and the 12 rated since (pieces 63 to 71, from CATALOGUE.md, 24 November 2026): 42.
               Pieces 63 on are read from their notes module's EV rows (study/pieces.py), the others as rated.py reads them
  the notes    every pitched part, a drum's part left out (by its name: bd, sd, snr, sn, cy, cym, crash, tam, tri, wb6, wb6q, gng,
               bng, hc); a pitch struck twice at once by two parts heard once (the longer kept); all on the piano, as in every
               AMT test so far, so AMT hears the notes and rhythms, not the orchestration
  AMT          every note, no given notes (the AUTOREGRESS flag), the times as the score or the render has them

Writes, beside this script: bracket_amt_inputs.jsonl (one input a section; id "<piece> | <section>"), bracket.json (the pieces,
ratings, sections and each scored note's onset in seconds).

Run: PYTHONPATH=<renderer>:<renderer>/tools:<renderer>/adapters python3 prepare_bracket.py <composer-blend> <folder of render.json
     files> <anticipation checkout>"""
import json, os, sys, warnings
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..'); sys.path.insert(0, ROOT)
from study import pieces as P, amt as A

DRUMS = {'bd', 'sd', 'snr', 'sn', 'cy', 'cym', 'crash', 'tam', 'tri', 'wb6', 'wb6q', 'gng', 'bng', 'hc'}
SINCE = [('63', 4.25, 'pieces/63_three_on_one_note/notes63.py'), ('64', 5, 'pieces/64_into_the_empty_bars/notes64.py'),
         ('64b', 4.5, 'pieces/64b_inside_the_mazurka/whole64.py'), ('65', 4.75, 'pieces/65_sung_the_third_time/notes65.py'),
         ('66', 4, 'pieces/66_said_by_one_then_by_all/notes66.py'), ('67', 4, 'pieces/67_one_bell_retuned/notes67.py'),
         ('68', 3.5, 'pieces/68_the_stone_and_the_storyteller/notes68.py'), ('68b', 4.5, 'pieces/68b_the_priest_and_the_voice/notes68b.py'),
         ('69', 3.5, 'pieces/69_one_tune_many_dances/notes69.py'), ('70', 4.25, 'pieces/70_the_walk_and_the_drone/notes70.py'),
         ('70b', 3.75, 'pieces/70b_the_march_and_the_dance/notes70b.py'), ('71', 5, 'pieces/71_the_fugue_and_the_keynote/notes71.py')]


def notes_of(parts):
    """the pitched parts' notes [(t, d, midi)], a pitch struck twice at once heard once"""
    best = {}
    for name, ns in parts.items():
        if str(name).split('.')[0] in DRUMS: continue
        for n in ns:
            t, d, m = float(n[0]), float(n[1]), int(round(float(n[2])))
            if d <= 0 or not 0 <= m < 128: continue
            k = (round(t, 2), m)
            if k not in best or d > best[k][1]: best[k] = (t, d, m)
    return sorted(best.values())


def main():
    blend, renders, aco = sys.argv[1:4]
    table = json.load(open(os.path.join(ROOT, 'data', 'rated.json')))['pieces']
    pieces = [dict(piece=x['piece'], rating=x['rating'], sources=[s for sec in x['sections'] for s in sec]) for x in table]
    pieces += [dict(piece=p, rating=r, sources=[s]) for p, r, s in SINCE]
    out, meta = [], []
    for x in pieces:
        secs = []
        for i, s in enumerate(x['sources']):
            path = os.path.join(renders, s) if s.endswith('.json') else os.path.join(blend, s)
            ns = notes_of(P.read(path))
            seq, where = A.sequence(ns, [], aco)
            order = sorted(range(len(ns)), key=lambda j: (ns[j][0], ns[j][2]))     # A.sequence's order, the same
            ws, pos = A.windows(seq, where, aco, alone=True)
            id_ = f"{x['piece']} | {i + 1}"
            out.append(dict(id=id_, windows=ws, notes=pos))
            secs.append(dict(id=id_, source=s, onsets=[round(ns[j][0], 3) for j in order]))
            print(f"{id_}: {len(ns)} notes, {len(ws)} windows, {ns[-1][0] + ns[-1][1]:.0f} s", flush=True)
        meta.append(dict(piece=x['piece'], rating=x['rating'], sections=secs))
    with open(os.path.join(HERE, 'bracket_amt_inputs.jsonl'), 'w') as f:
        for x in out: f.write(json.dumps(x) + '\n')
    json.dump(dict(pieces=meta), open(os.path.join(HERE, 'bracket.json'), 'w'))
    print(len(meta), 'pieces,', len(out), 'inputs')


if __name__ == '__main__':
    main()
