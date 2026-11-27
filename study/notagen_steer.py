"""Steering NotaGen-X toward a composer without training it: Composer Vector (Jiang and Xu, 2025, arXiv 2604.03333; their code,
github.com/JiangXunyi/Composer-Vector, was read, not run). A composer's vector is the mean, over some of the composer's works, of
the patch-level decoder's last hidden state at each work's last patch; while NotaGen writes (or reads), the state h of each patch,
from which its character decoder writes the next patch, becomes h + alpha * v, scaled back to h's length. The paper takes the vector
from its decoder's last block and adds it after the final layer norm; here it is taken where it is added. The test of 27 November
2026: checks/composer-vector-2026-11-27.md.

  prepare  python3 study/notagen_steer.py prepare NOTAGEN_CHECKOUT "Baroque|Handel, George Frideric|Vocal-Orchestral" \\
               -o inputs.jsonl --root COLLECTION_DIR PATH ...           (anywhere: each work in NotaGen's notation, under the prompt)
  vector   python3 study/notagen_steer.py vector WEIGHTS.pth inputs.jsonl --ids split.json:strozzi_vector -o vector.json   (the Mac)
  score    python3 study/notagen_steer.py score WEIGHTS.pth inputs.jsonl --vector vector.json --alpha 0 0.1 0.3 0.5 -o scores.jsonl
  test     python3 study/notagen_steer.py test scores.jsonl split.json

Writing with the vector: study/notagen_write.py --vector vector.json --alpha 0.3 (the same steering, on the newest patch only).
Weights are read as study/notagen_score.py reads them (plain tensors; --trust-pickle only for NotaGen's own file)."""
import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))


def steer(h, v, alpha):
    """h (..., width) moved by alpha * v and scaled back to its own length; alpha 0 leaves it as it is"""
    if not alpha: return h
    s = h + alpha * v
    return s * (h.norm(dim=-1, keepdim=True) / s.norm(dim=-1, keepdim=True).clamp_min(1e-12))


def prepare(a):
    from study import notagen as N
    prompt = a.prompt.split('|')
    xml2abc = os.path.join(a.checkout, 'data', 'xml2abc.py')
    with open(a.o, 'w') as out:
        for path in a.paths:
            src = os.path.join(a.root, path) if a.root else path; via = 'xml2abc'
            r = N.prepare_xml(src, prompt, xml2abc)
            if isinstance(r, str):                                          # some files only NotaGen's converter cannot read:
                first = r; r = again(src, prompt, xml2abc); via = 'music21, then xml2abc'   # music21 writes them out again first
                if isinstance(r, str): print(f'{path}: {first}; through music21: {r}'); continue
            wanted = [(k, x, y) for v in r['notes'].values() for k, x, y, t, m, chord in v if not chord]
            if not wanted: print(f'{path}: no single notes'); continue
            si = N.scoring_input(r['meta'], r['body'], wanted)
            out.write(json.dumps(dict(id=path, prompt=prompt, via=via, windows=si['windows'])) + '\n')
            print(f"{path}: {len(r['body'])} bars, {len(si['windows'])} window(s), via {via}")


def again(src, prompt, xml2abc):
    """the file read by music21 and written out as plain MusicXML, then prepared as NotaGen's converter reads it"""
    import tempfile
    from study import notagen as N
    try:
        import music21
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, 'work.musicxml'); music21.converter.parse(src).write('musicxml', fp=out)
            return N.prepare_xml(out, prompt, xml2abc)
    except Exception as e: return f'{type(e).__name__}: {e}'[:200]


def model_on(weights, trust, device):
    import torch
    from study import notagen_score as S
    dev = device if device != 'auto' else ('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')
    return S.load(weights, trust).to(dev).eval(), dev


def encode(model, patches, device):
    """the patch-level decoder's last hidden state for each patch of one window: (n, width), and the window as ids"""
    import torch
    from study.notagen_score import PATCH
    ids = [[ord(c) for c in p] + [0] * (PATCH - len(p)) for p in patches]
    x = torch.tensor(ids, dtype=torch.long, device=device); pl = model.patch_level_decoder
    oh = torch.nn.functional.one_hot(x, num_classes=128).to(torch.float32).reshape(1, len(ids), PATCH * 128)
    return pl.base(inputs_embeds=pl.patch_embedding(oh)).last_hidden_state[0], x


def bits(model, enc, x, chunk=256):
    """bits a character of a window, every character after the first patch read from the (steered) states before it"""
    import torch
    from study.notagen_score import PATCH
    cb = model.char_level_decoder.base; wte = cb.transformer.wte.weight; n = len(x); total, count = 0.0, 0
    for a in range(1, n, chunk):
        b = min(n, a + chunk); tgt = x[a:b]
        inp = torch.cat([enc[a - 1:b - 1].unsqueeze(1), torch.nn.functional.embedding(tgt, wte)], dim=1)
        lp = torch.log_softmax(cb(inputs_embeds=inp).logits[:, :PATCH, :].float(), dim=-1)
        got = lp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1); real = tgt > 0
        total += -float(got[real].sum()) / math.log(2); count += int(real.sum())
    return total, count


def vector(a):
    import torch
    split, key = a.ids.split(':')
    ids = set(json.load(open(split))[key])
    model, dev = model_on(a.weights, a.trust_pickle, a.device)
    states, used = [], []
    with torch.no_grad():
        for line in open(a.inputs):
            w = json.loads(line)
            if w['id'] not in ids: continue
            enc, _ = encode(model, w['windows'][-1], dev)                    # the last window: its last patch ends the piece
            states.append(enc[-1].float().cpu()); used.append(w['id'])
    missing = sorted(ids - set(used))                                       # works NotaGen's converter could not read
    if not used: sys.exit(f'none of the works is in {a.inputs}')
    if missing: print(f'not in {a.inputs}, so not in the vector: {missing}')
    v = torch.stack(states).mean(0)
    json.dump(dict(works=used, missing=missing, prompt=w['prompt'], norm=float(v.norm()), vector=[round(float(x), 6) for x in v]),
              open(a.o, 'w'))
    print(f'{len(used)} works; the vector\'s length {float(v.norm()):.2f}, a state\'s {float(torch.stack(states).norm(dim=-1).mean()):.2f} on average')


def score(a):
    import torch
    model, dev = model_on(a.weights, a.trust_pickle, a.device)
    v = torch.tensor(json.load(open(a.vector))['vector'], dtype=torch.float32, device=dev)
    with open(a.o, 'w') as out, torch.no_grad():
        for line in open(a.inputs):
            w = json.loads(line); t0 = time.time(); row = dict(id=w['id'], bits={})
            encs = [encode(model, pts, dev) for pts in w['windows']]
            for alpha in a.alpha:
                tb = tc = 0
                for enc, x in encs:
                    b, c = bits(model, steer(enc, v, alpha), x); tb += b; tc += c
                row['bits'][f'{alpha:g}'] = round(tb / tc, 5)
            out.write(json.dumps(row) + '\n'); out.flush()
            print(f"{w['id']}: " + ', '.join(f'alpha {k} {b:.4f}' for k, b in row['bits'].items()) + f' bits a character ({time.time() - t0:.0f} s)', flush=True)


def test(a):
    """the test of checks/composer-vector-2026-11-27.md, at alpha 0.3: the held-out works' saving, and the control's"""
    rows = {json.loads(l)['id']: json.loads(l)['bits'] for l in open(a.scores)}
    sp = json.load(open(a.split)); held, ctrl = sp['strozzi_held_out'], sp['caccini_control']
    for alpha in sorted({k for r in rows.values() for k in r} - {'0'}, key=float):
        sh = [rows[i]['0'] - rows[i][alpha] for i in held if i in rows]
        sc = [rows[i]['0'] - rows[i][alpha] for i in ctrl if i in rows]
        mean = lambda x: sum(x) / len(x) if x else float('nan')
        print(f'alpha {alpha}: Strozzi held out, {sum(s > 0 for s in sh)} of {len(sh)} cheaper, mean saving {mean(sh):+.4f} bits a '
              f'character; Caccini, {sum(s > 0 for s in sc)} of {len(sc)} cheaper, mean saving {mean(sc):+.4f}')
    sh = [rows[i]['0'] - rows[i]['0.3'] for i in held if i in rows]; sc = [rows[i]['0'] - rows[i]['0.3'] for i in ctrl if i in rows]
    one, two = sum(s > 0 for s in sh) >= 6, (sum(sh) / len(sh)) > (sum(sc) / len(sc))
    print(f"\nat alpha 0.3: 1. six or more of the eight cheaper: {'yes' if one else 'no'}; 2. their saving larger than Caccini's: "
          f"{'yes' if two else 'no'}. {'Passes: write with it, for him to hear.' if one and two else 'Fails: not used.'}")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    x = sub.add_parser('prepare'); x.add_argument('checkout'); x.add_argument('prompt'); x.add_argument('-o', required=True)
    x.add_argument('--root'); x.add_argument('paths', nargs='+')
    for name in ('vector', 'score'):
        x = sub.add_parser(name); x.add_argument('weights'); x.add_argument('inputs'); x.add_argument('-o', required=True)
        x.add_argument('--device', default='auto'); x.add_argument('--trust-pickle', action='store_true')
        if name == 'vector': x.add_argument('--ids', required=True, help='FILE:KEY, a JSON file and the key of its list of work ids')
        else: x.add_argument('--vector', required=True); x.add_argument('--alpha', type=float, nargs='+', default=[0, .1, .3, .5])
    x = sub.add_parser('test'); x.add_argument('scores'); x.add_argument('split')
    a = ap.parse_args(); dict(prepare=prepare, vector=vector, score=score, test=test)[a.cmd](a)


if __name__ == '__main__':
    main()
