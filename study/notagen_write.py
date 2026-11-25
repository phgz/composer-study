"""NotaGen writing: one piece from a prompt (period, composer, instrumentation, as NotaGen's gradio/prompts.txt lists them), with
NotaGen's own model and sampling (its inference/utils.py from a checkout; top-k 9, top-p 0.9, temperature 1.2, its config's,
unless --temperature, --top-p or --top-k change them, as piece 74 raised the temperature to move its tunes off the expected), on a
Mac's GPU (MPS), a CUDA GPU or the CPU. Its generation loop and its rest_unreduce are NotaGen's (gradio/inference.py and
inference/inference.py, MIT licence, Copyright (c) 2025 ElectricAlexis), here with a seed, a time limit, the stream step's misnamed
variable put right (context_tunebody_liness), and a voice list for files without %%score.

  python3 notagen_write.py WEIGHTS.pth NOTAGEN_CHECKOUT "Classical" "Mozart, Wolfgang Amadeus" "Chamber" -o OUT [--seed 1]
      [--temperature 1.4] [--top-p 0.9] [--top-k 9]

Writes OUT/<name>.abc (as NotaGen wrote it), OUT/<name>.full.abc (every voice in every bar, X:1 first, the prompt lines left
out: NotaGen's own output form), OUT/<name>.xml (its abc2xml.py) and OUT/<name>.mid (music21, where installed)."""
import argparse, os, re, subprocess, sys, time


def rest_unreduce(abc_lines, Barline_regexPattern, calculate_bartext_duration):
    """NotaGen's: the voices left out of a bar (all rests) put back, as rests of the bar's usual length"""
    tunebody_index = next(i for i, l in enumerate(abc_lines) if '[V:' in l)
    metadata_lines = abc_lines[:tunebody_index]; tunebody_lines = abc_lines[tunebody_index:]
    part_symbol_list, voice_group_list, existed_voices = [], [], []
    for line in metadata_lines:
        if line.startswith('%%score'):
            for m in re.findall(r'\((.*?)\)', line): voice_group_list.append(m.split())
            existed_voices = [item for sublist in voice_group_list for item in sublist]
        if line.startswith('V:'):
            symbol = line.split()[0]; part_symbol_list.append(symbol)
            if symbol[2:] not in existed_voices: voice_group_list.append([symbol[2:]])
    z_symbol_list, x_symbol_list = [], []
    for g in voice_group_list:
        z_symbol_list.append('V:' + g[0]); x_symbol_list += ['V:' + v for v in g[1:]]
    part_symbol_list.sort(key=lambda x: int(x[2:]))
    out = []; ref_dur = None; right_barline = '|'
    for i, line in enumerate(tunebody_lines):
        line = re.sub(r'^\[r:[^\]]*\]', '', line)
        bars = {f'V:{m[0]}': m[1] for m in re.findall(r'\[V:(\d+)\](.*?)(?=\[V:|$)', line)}
        durs = {}
        for symbol, bartext in bars.items():
            right_barline = ''.join(re.split(Barline_regexPattern, bartext)[-2:])
            try: d = calculate_bartext_duration(bartext[:-len(right_barline)])
            except Exception: d = None
            if d is not None: durs[d] = durs.get(d, 0) + 1
        if durs: ref_dur = max(durs, key=durs.get)
        prefix = line.split('[V:')[0] if i == 0 else ''
        new = ''
        for symbol in part_symbol_list:
            if symbol in bars: text = bars[symbol]
            else: text = prefix + ('x' if symbol in x_symbol_list else 'z') + str(ref_dur) + right_barline
            new += '[' + symbol + ']' + text
        out.append(new + '\n')
    return metadata_lines + out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('weights'); ap.add_argument('checkout'); ap.add_argument('period'); ap.add_argument('composer'); ap.add_argument('instrumentation')
    ap.add_argument('-o', required=True); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--device', default='auto')
    ap.add_argument('--minutes', type=float, default=30.0); ap.add_argument('--tries', type=int, default=3)
    ap.add_argument('--trust-pickle', action='store_true')
    ap.add_argument('--temperature', type=float); ap.add_argument('--top-p', type=float); ap.add_argument('--top-k', type=int)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.checkout, 'inference'))
    import numpy as np, torch
    import utils as U, config as K                                  # NotaGen's inference/utils.py and config.py
    TEMP = a.temperature if a.temperature is not None else K.TEMPERATURE
    TOPP = a.top_p if a.top_p is not None else K.TOP_P; TOPK = a.top_k if a.top_k is not None else K.TOP_K
    from transformers import GPT2Config
    from abctoolkit.utils import Barline_regexPattern
    from abctoolkit.duration import calculate_bartext_duration
    dev = torch.device(a.device if a.device != 'auto' else ('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu'))
    pc = GPT2Config(num_hidden_layers=K.PATCH_NUM_LAYERS, max_length=K.PATCH_LENGTH, max_position_embeddings=K.PATCH_LENGTH,
                    n_embd=K.HIDDEN_SIZE, num_attention_heads=K.HIDDEN_SIZE // 64, vocab_size=1)
    cc = GPT2Config(num_hidden_layers=K.CHAR_NUM_LAYERS, max_length=K.PATCH_SIZE + 1, max_position_embeddings=K.PATCH_SIZE + 1,
                    hidden_size=K.HIDDEN_SIZE, num_attention_heads=K.HIDDEN_SIZE // 64, vocab_size=128)
    model = U.NotaGenLMHeadModel(encoder_config=pc, decoder_config=cc)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from notagen_score import checkpoint
    sd = checkpoint(a.weights, a.trust_pickle); model.load_state_dict(sd, strict=False); del sd
    model = model.to(dev).eval(); pz = U.Patchilizer()
    np.random.seed(a.seed); torch.manual_seed(a.seed)
    prompt = ['%' + a.period + '\n', '%' + a.composer + '\n', '%' + a.instrumentation + '\n']
    print(f'NotaGen-X on {dev}, seed {a.seed}, temperature {TEMP}, top-p {TOPP}, top-k {TOPK}:', ' / '.join(p.strip('%\n') for p in prompt), flush=True)
    for attempt in range(a.tries):
        t0 = time.time(); bos = [pz.bos_token_id] * (K.PATCH_SIZE - 1) + [pz.eos_token_id]
        pp = [[ord(c) for c in p] + [pz.special_token_id] * (K.PATCH_SIZE - len(p)) for p in pz.patchilize_metadata(prompt)]
        inp = torch.tensor([bos] + pp, device=dev).reshape(1, -1)
        text = list(''.join(prompt)); meta_chars, body_chars = [], []; in_body = False; ended = failed = False
        with torch.inference_mode():
            while True:
                patch = model.generate(inp.unsqueeze(0), top_k=TOPK, top_p=TOPP, temperature=TEMP)
                if not in_body and pz.decode([patch]).startswith('[r:'):         # the body begins with [r:0/
                    in_body = True
                    r0 = torch.tensor([ord(c) for c in '[r:0/']).unsqueeze(0).to(dev)
                    patch = [ord(c) for c in '[r:0/'] + model.generate(torch.concat([inp, r0], axis=-1).unsqueeze(0), top_k=TOPK, top_p=TOPP, temperature=TEMP)
                if patch[0] == pz.bos_token_id and patch[1] == pz.eos_token_id: ended = True; break
                for ch in pz.decode([patch]):
                    text.append(ch); (body_chars if in_body else meta_chars).append(ch)
                over = False
                for j in range(len(patch)):
                    if over: patch[j] = pz.special_token_id
                    if patch[j] == pz.eos_token_id: over = True
                inp = torch.cat([inp, torch.tensor([patch], device=dev)], dim=1)
                if len(text) > 102400 or time.time() - t0 > a.minutes * 60: failed = True; break
                if inp.shape[1] >= K.PATCH_LENGTH * K.PATCH_SIZE and not ended:      # stream: keep the metadata and the last half
                    body = ''.join(body_chars)
                    if '\n' not in body: failed = True; break
                    ls = body.split('\n'); ls = [l + '\n' for l in ls[:-1]] + ([ls[-1]] if ls[-1] else [])
                    keep = ls[-(len(ls) // 2):]
                    ids = pz.encode_generate(''.join(meta_chars) + ''.join(keep))
                    inp = torch.tensor([[c for p in ids for c in p]], device=dev).reshape(1, -1)
                    body_chars = list(''.join(keep))
                    print(f'  ... {len(text)} characters, {time.time() - t0:.0f} s', flush=True)
        if failed: print(f'attempt {attempt + 1} failed after {time.time() - t0:.0f} s', flush=True); continue
        os.makedirs(a.o, exist_ok=True)
        name = time.strftime('%Y%m%d-%H%M%S') + '_' + re.sub(r'[^A-Za-z0-9]+', '-', f'{a.composer}_{a.instrumentation}').strip('-') + f'_seed{a.seed}_t{TEMP:g}'
        abc = ''.join(text); open(os.path.join(a.o, name + '.abc'), 'w').write(abc)
        lines = [l + '\n' for l in abc.split('\n') if l]
        full = [l for l in rest_unreduce(lines, Barline_regexPattern, calculate_bartext_duration) if not (l.startswith('%') and not l.startswith('%%'))]
        fpath = os.path.join(a.o, name + '.full.abc'); open(fpath, 'w').write('X:1\n' + ''.join(full))
        xml = subprocess.run([sys.executable, '-I', os.path.join(a.checkout, 'data', 'abc2xml.py'), fpath], capture_output=True, text=True).stdout
        if xml.strip():
            xpath = os.path.join(a.o, name + '.xml'); open(xpath, 'w').write(xml)
            try:
                import music21; music21.converter.parse(xpath).write('midi', fp=os.path.join(a.o, name + '.mid'))
            except Exception as e: print('no MIDI:', type(e).__name__, str(e)[:200])
        else: print('abc2xml wrote nothing')
        print(f'written in {time.time() - t0:.0f} s: {os.path.join(a.o, name)}.*', flush=True)
        return
    sys.exit('no piece written')


if __name__ == '__main__':
    main()
