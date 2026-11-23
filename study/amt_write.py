"""AMT writing between given notes: an Anticipatory Music Transformer fills the spans of a piece around the notes given it (the
controls, which it reads 5 seconds ahead), after the notes given as history, with AMT's own generate() (its sample.py, from a
checkout). For piece 64b: the inner voices, between its tune and its bass (checks/three-ears-64b-2026-11-23/amt_write.json).

  python3 amt_write.py MODEL_FOLDER ANTICIPATION_CHECKOUT INPUT.json -o OUT.json [--seed 1] [--top-p 0.98] [--device mps]

INPUT: {"given": [[onset s, length s, MIDI]], "history": [[...]], "spans": [[from s, to s], ...]}. Each span is written after
everything before it, AMT's own notes included. OUT: {"notes": [[onset s, length s, MIDI, instrument]], ...}, the notes AMT wrote
(the history left out), with the seed, nucleus and model. top-p 0.98 is the README's. Needs torch, transformers, the checkout."""
import argparse, json, os, sys, time


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('checkout'); ap.add_argument('input')
    ap.add_argument('-o', required=True); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--top-p', type=float, default=.98)
    ap.add_argument('--device', default='auto'); a = ap.parse_args()
    sys.path.insert(0, a.checkout); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import torch
    from transformers import AutoModelForCausalLM
    from anticipation.sample import generate
    from anticipation import ops
    from anticipation.vocab import TIME_OFFSET, DUR_OFFSET, NOTE_OFFSET
    import amt as A
    dev = a.device if a.device != 'auto' else ('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')
    model = AutoModelForCausalLM.from_pretrained(a.model).to(dev).eval()
    spec = json.load(open(a.input)); torch.manual_seed(a.seed)
    controls = A.tokens(spec['given'], a.checkout, control=True); events = A.tokens(spec['history'], a.checkout)
    t0 = time.time()
    for s0, s1 in spec['spans']:
        events = generate(model, s0, s1, inputs=events, controls=controls, top_p=a.top_p)
        print(f'{s0:.1f} s to {s1:.1f} s written ({time.time() - t0:.0f} s)', flush=True)
    start = spec['spans'][0][0]; out = []
    for t, d, n in zip(events[0::3], events[1::3], events[2::3]):
        t_s = (t - TIME_OFFSET) / 100
        if t_s < start - 1e-9: continue
        note = n - NOTE_OFFSET; out.append([round(t_s, 2), round((d - DUR_OFFSET) / 100, 2), note % 128, note // 128])
    json.dump(dict(model=os.path.basename(os.path.normpath(a.model)), seed=a.seed, top_p=a.top_p, spans=spec['spans'], notes=out,
                   seconds=round(time.time() - t0, 1)), open(a.o, 'w'))
    print(f'{len(out)} notes written to {a.o}', flush=True)


if __name__ == '__main__':
    main()
