"""NotaGen's surprise at each prepared note (study/notagen.py): for each work of an inputs file, its windows read by NotaGen-X, and for
each note the bits of its pitch's characters, and of the character after them not being an octave mark. Runs where the weights are
(about 6.2 GB on disk, 2.1 GB in memory): on a Mac's GPU (MPS), a CUDA GPU, or the CPU.

The model is NotaGen's (inference/utils.py, MIT): a patch-level GPT-2 (20 layers, 1280 wide, 1024 patches) reads each patch of 16
characters as one vector; a character-level GPT-2 (6 layers) predicts the next patch's characters, the first from the patch-level
output alone, each after from it and the characters before. Built here from transformers' GPT-2 with NotaGen's names, so its saved
weights load as they are; the forward pass is its training pass (NotaGenLMHeadModel.forward), every patch scored at once.

  python3 notagen_score.py WEIGHTS.pth inputs.jsonl -o scores.jsonl [--device mps|cuda|cpu] [--verify NOTAGEN_CHECKOUT]

--verify also loads NotaGen's own classes from a checkout (its inference/utils.py) and checks, on the first window, that its
generate() gives the same probabilities as this pass. Needs: torch, transformers (NotaGen pins 4.40.0); --verify also samplings."""
import argparse, json, math, sys, time

PATCH, WIDTH = 16, 1280


def build():
    import torch
    from transformers import GPT2Config, GPT2Model, GPT2LMHeadModel
    pc = GPT2Config(num_hidden_layers=20, max_position_embeddings=1024, n_embd=WIDTH, num_attention_heads=WIDTH // 64, vocab_size=1)
    cc = GPT2Config(num_hidden_layers=6, max_position_embeddings=PATCH + 1, hidden_size=WIDTH, num_attention_heads=WIDTH // 64, vocab_size=128)

    class PatchLevel(torch.nn.Module):
        def __init__(self):
            super().__init__(); self.patch_embedding = torch.nn.Linear(PATCH * 128, WIDTH); self.base = GPT2Model(pc)

    class CharLevel(torch.nn.Module):
        def __init__(self): super().__init__(); self.base = GPT2LMHeadModel(cc)

    class NotaGen(torch.nn.Module):
        def __init__(self): super().__init__(); self.patch_level_decoder = PatchLevel(); self.char_level_decoder = CharLevel()

    return NotaGen()


def checkpoint(path, trust_pickle=False):
    """the saved weights ({name: tensor}), read as plain tensors (mapped from the file where it allows); --trust-pickle reads the file
    as NotaGen itself does, which runs whatever code the file holds: only for the file from huggingface.co/ElectricAlexis/NotaGen"""
    import torch
    err = None
    for kw in (dict(mmap=True), {}):
        try: ck = torch.load(path, map_location='cpu', weights_only=not trust_pickle, **kw); break
        except Exception as e: err = e
    else:
        sys.exit(f'could not read the weights as plain tensors ({type(err).__name__}: {str(err)[:300]}). If the file is the one '
                 'downloaded from huggingface.co/ElectricAlexis/NotaGen, --trust-pickle reads it as NotaGen itself does')
    return ck['model'] if isinstance(ck, dict) and 'model' in ck else ck


def load(path, trust_pickle=False):
    sd = checkpoint(path, trust_pickle)
    model = build(); missing, unexpected = model.load_state_dict(sd, strict=False)
    buffers = ('.attn.bias', '.attn.masked_bias')
    bad = [k for k in missing if not k.endswith(buffers)] + [k for k in unexpected if not k.endswith(buffers)]
    if bad: sys.exit(f'the weights do not fit NotaGen-X: {bad[:8]}')
    del sd
    return model


def window(model, patches, device, chunk=256):
    """log2 p of each character of each patch after the first ([n][16], row 0 unused), and p of an octave mark ("," or "'") at each
    position"""
    import torch
    ids = [[ord(c) for c in p] + [0] * (PATCH - len(p)) for p in patches]
    x = torch.tensor(ids, dtype=torch.long, device=device); n = len(ids)
    pl = model.patch_level_decoder; cb = model.char_level_decoder.base
    with torch.no_grad():
        oh = torch.nn.functional.one_hot(x, num_classes=128).to(torch.float32).reshape(1, n, PATCH * 128)
        enc = pl.base(inputs_embeds=pl.patch_embedding(oh)).last_hidden_state[0]                 # (n, width): patch i's reading
        lp2 = torch.zeros((n, PATCH)); octv = torch.zeros((n, PATCH))
        wte = cb.transformer.wte.weight
        for a in range(1, n, chunk):
            b = min(n, a + chunk); tgt = x[a:b]
            inp = torch.cat([enc[a - 1:b - 1].unsqueeze(1), torch.nn.functional.embedding(tgt, wte)], dim=1)   # (m, 17, width)
            lp = torch.log_softmax(cb(inputs_embeds=inp).logits[:, :PATCH, :].float(), dim=-1)    # position t predicts character t
            lp2[a:b] = (lp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1) / math.log(2)).cpu()
            p = lp.exp(); octv[a:b] = (p[..., ord(',')] + p[..., ord("'")]).cpu()
    return lp2, octv, x.cpu()


def verify(model, checkout, patches, device):
    """NotaGen's own generate() on a few patches of a window: the largest difference from this pass's probabilities"""
    import os, torch, random
    sys.path.insert(0, os.path.join(checkout, 'inference'))
    from transformers import GPT2Config
    import utils as U                                                     # NotaGen's inference/utils.py (its config.py beside it)
    pc = GPT2Config(num_hidden_layers=20, max_length=1024, max_position_embeddings=1024, n_embd=WIDTH, num_attention_heads=WIDTH // 64, vocab_size=1)
    cc = GPT2Config(num_hidden_layers=6, max_length=PATCH + 1, max_position_embeddings=PATCH + 1, hidden_size=WIDTH, num_attention_heads=WIDTH // 64, vocab_size=128)
    theirs = U.NotaGenLMHeadModel(encoder_config=pc, decoder_config=cc)
    theirs.load_state_dict(model.state_dict(), strict=False); theirs = theirs.to(device).eval()
    lp2, _, x = window(model, patches, device)
    worst = 0.0; rnd = random.Random(0)
    with torch.no_grad():
        enc = theirs.patch_level_decoder(x.to(device).unsqueeze(0))['last_hidden_state'][0]
        for i in rnd.sample(range(1, len(patches)), min(6, len(patches) - 1)):
            for t in range(PATCH):
                c = int(x[i, t])
                if c == 0: break
                toks = torch.tensor([1] + [int(v) for v in x[i, :t]], device=device)
                prob = theirs.char_level_decoder.generate(enc[i - 1], toks)[c].item()
                worst = max(worst, abs(math.log2(max(prob, 1e-12)) - float(lp2[i, t])))
    del theirs
    return worst


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('weights'); ap.add_argument('inputs'); ap.add_argument('-o', required=True)
    ap.add_argument('--device', default='auto'); ap.add_argument('--verify'); ap.add_argument('--trust-pickle', action='store_true')
    a = ap.parse_args()
    import torch
    dev = a.device if a.device != 'auto' else ('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')
    t0 = time.time(); model = load(a.weights, a.trust_pickle).to(dev).eval()
    print(f'NotaGen-X loaded on {dev} in {time.time() - t0:.0f} s', flush=True)
    works = [json.loads(l) for l in open(a.inputs)]
    if a.verify:
        worst = verify(model, a.verify, works[0]['windows'][0], dev)
        print(f"verify: largest difference from NotaGen's own generate(): {worst:.2e} bits", flush=True)
        if worst > 0.01: sys.exit('this pass does not give the probabilities NotaGen gives: nothing scored')
    with open(a.o, 'w') as out:
        for w in works:
            t1 = time.time(); got = [window(model, pts, dev) for pts in w['windows']]
            bits = []
            for wi, f0, f1 in w['notes']:
                lp2, octv, x = got[wi]
                chars = -sum(float(lp2[f // PATCH, f % PATCH]) for f in range(f0, f1 + 1))
                nxt = f1 + 1; stop = -math.log2(max(1.0 - float(octv[nxt // PATCH, nxt % PATCH]), 1e-12))
                bits.append([round(chars, 4), round(stop, 4)])
            real = [(lp2[1:][x[1:] > 0]) for lp2, _, x in got]                           # every character read, padding apart
            per_char = -float(torch.cat(real).mean()) if real else None
            out.write(json.dumps(dict(id=w['id'], bits=bits, per_char=round(per_char, 4))) + '\n'); out.flush()
            print(f"{w['id']}: {len(bits)} notes, {len(w['windows'])} window(s), {per_char:.3f} bits a character, "
                  f"{sum(b[0] + b[1] for b in bits) / len(bits):.2f} bits a note ({time.time() - t1:.1f} s)", flush=True)


if __name__ == '__main__':
    main()
