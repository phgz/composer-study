"""AMT's surprise at each prepared note (study/amt.py): for each input, its windows read by an Anticipatory Music Transformer, and for
each note the bits of its pitch, given its onset and its length: the model's probability of that pitch on any instrument, among the
note tokens (what AMT may write in a note's third token). Each note's scores: [the pitch's bits, the note token's own bits (the
pitch on its instrument), the entropy in bits of AMT's distribution over the 128 pitches there (on any instrument, the rest left
out): how unsure it was before it heard the pitch, the bits of its onset (among the onset tokens, given what came before: how
unexpected the moment it begins), the bits of its length (among the length tokens, given its onset)]. Runs where the weights are (a Mac's GPU through MPS, a CUDA GPU, or the
CPU): music-large-800k (780M parameters) or music-medium-800k (360M), each a folder with its config.json.

  python3 amt_score.py MODEL_FOLDER inputs.jsonl -o scores.jsonl [--device mps|cuda|cpu]

The health check is each input's bits a note token over every asked note in its windows: a model that loaded wrongly gives about
14 (one in 16,513). Needs torch and transformers."""
import argparse, json, math, time

TIME_OFFSET, DUR_OFFSET = 0, 10000                         # anticipation/vocab.py: the onset block (10 ms steps), the length block
NOTE_OFFSET, MAX_NOTE, MAX_INSTR = 11000, 16512, 129       # the note block, instrument x 128 + pitch
REST = NOTE_OFFSET + MAX_NOTE                              # its rest token, also allowed in a note's place
CONTROL_OFFSET = REST + 1


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('inputs'); ap.add_argument('-o', required=True)
    ap.add_argument('--device', default='auto'); a = ap.parse_args()
    import torch
    from transformers import AutoModelForCausalLM
    dev = a.device if a.device != 'auto' else ('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')
    t0 = time.time(); model = AutoModelForCausalLM.from_pretrained(a.model).to(dev).eval()
    assert model.config.vocab_size >= CONTROL_OFFSET + MAX_NOTE + 3, 'not an anticipatory music model'
    print(f'{a.model} on {dev} in {time.time() - t0:.0f} s', flush=True)
    ln2 = math.log(2)
    with open(a.o, 'w') as out:
        for line in open(a.inputs):
            w = json.loads(line); t1 = time.time(); lps = []; health = []; rhythm = {}
            asked = {}
            for k, (wi, pos) in enumerate(w['notes']): asked.setdefault(wi, []).append((k, pos))
            with torch.no_grad():
                for wi, toks in enumerate(w['windows']):
                    full = model(torch.tensor([toks], device=dev)).logits[0].float()
                    lp = torch.log_softmax(full[:, NOTE_OFFSET:REST + 1], dim=-1).cpu(); lps.append(lp)
                    for k, pos in asked.get(wi, []):                                    # its onset among the onset
                        t, d = toks[pos - 2], toks[pos - 1]; tb = db = None             # tokens, its length among the
                        if TIME_OFFSET <= t < DUR_OFFSET:                               # length tokens
                            tb = round(-float(torch.log_softmax(full[pos - 3, TIME_OFFSET:DUR_OFFSET], dim=-1)[t - TIME_OFFSET]) / ln2, 4)
                        if DUR_OFFSET <= d < NOTE_OFFSET:
                            db = round(-float(torch.log_softmax(full[pos - 2, DUR_OFFSET:NOTE_OFFSET], dim=-1)[d - DUR_OFFSET]) / ln2, 4)
                        rhythm[k] = (tb, db)
                    for pos in range(3, len(toks), 3):                                  # every asked note in the window
                        note = toks[pos] - NOTE_OFFSET
                        if 0 <= note < MAX_NOTE: health.append(-float(lp[pos - 1, note]) / ln2)
            bits = []
            for k, (wi, pos) in enumerate(w['notes']):
                tok = w['windows'][wi][pos]; note = tok - NOTE_OFFSET; assert 0 <= note < MAX_NOTE, (w['id'], pos)
                row = lps[wi][pos - 1]; pitch = note % 128
                pitch_lp = torch.logsumexp(row[pitch:MAX_NOTE:128], dim=0)                 # that pitch, on any instrument
                plp = torch.logsumexp(row[:MAX_NOTE].reshape(MAX_INSTR, 128), dim=0)       # every pitch, on any instrument,
                plp = plp - torch.logsumexp(plp, dim=0)                                    # among the pitches alone
                entropy = -float((plp.exp() * plp).sum()) / ln2                            # how unsure AMT was of the pitch
                bits.append([round(-float(pitch_lp) / ln2, 4), round(-float(row[note]) / ln2, 4), round(entropy, 4), *rhythm[k]])
            hc = sum(health) / len(health) if health else None
            out.write(json.dumps(dict(id=w['id'], bits=bits, per_note_token=round(hc, 4) if hc is not None else None)) + '\n'); out.flush()
            print(f"{w['id']}: {len(bits)} notes, {len(w['windows'])} window(s), {hc:.2f} bits a note token, "
                  f"{sum(b[0] for b in bits) / max(1, len(bits)):.2f} bits a pitch ({time.time() - t1:.1f} s)", flush=True)


if __name__ == '__main__':
    main()
