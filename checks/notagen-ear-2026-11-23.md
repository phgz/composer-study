# NotaGen's ear beside ours (23 November 2026)

**The question:** how surprised is NotaGen by the real notes of held-out works, against the continuations' ear, note for note? Inner lines first, since that is where piece 64b used the ear. Lower is better.

**Status:** the inputs and our bits are ready, and the scripts for the machine that holds NotaGen's weights are written. NotaGen has not scored anything yet. The predictions below were written before it did.

## What NotaGen is

- **The model:** NotaGen (Wang et al., 2025; [github.com/ElectricAlexis/NotaGen](https://github.com/ElectricAlexis/NotaGen), MIT licence).
- **What it writes:** "interleaved ABC": three prompt lines (period, composer, instrumentation), the metadata, then one line a bar, each voice's bar in turn, top to bottom.
- **How it reads:** in patches of 16 characters. A patch-level GPT-2 (20 layers, 1280 wide, 1024 patches of context) reads the patches. A character-level GPT-2 (6 layers) predicts each next patch's characters.
- **The version used:** NotaGen-X, 516 million parameters.
  - Pre-trained on 1.6 million scores.
  - Fine-tuned on 8,948 classical pieces by 152 composers, without changing their keys.
  - Then reinforcement learning.

## The test (`notagen-ear-2026-11-23/`)

- **The works:** the standing test's held-out works (`vertical-nested-2026-11-23.md`), in the units NotaGen was fine-tuned on:
  - Bach's chorales;
  - Corelli's trio sonatas: DCML's notes, read from the kern collection's copy of the same movement, the alignment confirming it;
  - Vivaldi's trio sonatas;
  - Haydn's mature quartets;
  - Mozart's Vienna quartets.
- **29 works, 12,653 notes, 5,945 of them in inner lines.** One work is left out: Corelli op. 1 no. 6a, which has no kern copy.
- **Ours:** exactly as the standing test hears them.
  - The levels: the catalogue, the composer and the unit, the held-out works left out of each.
  - The vertical view nested at 200, weight 0.75.
  - Each work's four longest lines, their first 150 notes.
  - Each note's bits are the standing test's. Where every note of a work is compared, the work's sums are phaseK's exactly.
- **NotaGen's notation:** `study/notagen.py` follows NotaGen's own data scripts and its patch maker.
  - The pipeline:
    1. The source (kern or MusicXML).
    2. MusicXML from music21. For an OpenScore quartet, the movement's measures alone, where score-reader's `movements()` puts them.
    3. NotaGen's `xml2abc.py -d 8 -c 6 -x`.
    4. Its cleaning, and its rest reduction in the work's own key.
    5. The prompt lines first: for example "Baroque / Bach, Johann Sebastian / Choral", from its own prompt list.
  - **Checked against NotaGen's code:** on chorale 217 the patches are NotaGen's `Patchilizer.encode_train` output exactly, 118 of 118.
  - **The windows:** every work's scored notes fit one window of at most 1024 patches. Long works would get several, each beginning halfway through the one before, as NotaGen's stream mode does.
- **The notes compared:** each ABC voice is aligned to the line whose pitches it shares most, in order (the reading plays repeats; the ABC writes them once).
  - Almost every voice shares all its notes with its line. Mozart K. 589's cello shares 53%, and K. 575's 89%.
  - A chord counts as its top note (the line's skyline) and is not compared.
- **A note's bits under NotaGen:** the bits of its pitch's characters (accidental, letter, octave marks), plus those of the next character not being an octave mark (the pitch ends there).
- **The tests (`compare.py`):**
  - The difference is NotaGen minus ours, each work weighing one: a work's notes are not independent (`vertical-weight-2026-11-23.md`).
  - Its 95% interval comes from resampling works, and its p from flipping each work's sign.
  - It is given for inner lines, all lines, the top line, the bass, and inner notes with and without a written accidental.
  - Spearman's rho says whether the two ears find the same notes surprising.

## What is not alike

- **Against NotaGen:**
  - **The spelling:** it names the note (F sharp or G flat, and whether the accidental is written), so its bits pay for the spelling too. Ours predict the pitch alone.
  - **What it has heard of the bar:** it writes each bar's voices top to bottom. An inner voice is predicted after the top voice's whole bar, but before the same bar's bass. Ours hear what sounds at the note's onset, below and above, and nothing after it.
  - **Part names:** the kern works come to it through music21, so their part names ("Voice") are not those of its training files.
- **For NotaGen:** these works are standard repertoire, and its training may well hold them, most of all Bach's chorales. Ours were held out of every level that hears them.
- **So this is not a test of which ear generalises better:** it says how the two compare on this music. The cleaner test is music neither has seen, which is the third test planned: piece 64b's inner voices.

## Predictions, written before NotaGen scored any note (Claude's, not Philip's)

1. On inner lines, all units together, NotaGen is lower than ours by a clear margin, between 0.5 and 1.0 bits a note (ours: 2.32).
2. The gap is largest on Bach's chorales, where NotaGen falls under 1 bit a note.
3. NotaGen's advantage is smaller on inner notes written with an accidental than on those without, and smaller on the top line than on the bass.
4. The two ears agree on which inner notes are surprising, but only moderately: Spearman's rho between 0.3 and 0.5 over all inner notes.

## Ours, the half already measured

Pitch bits a note on the compared notes, each work weighing one:

| Unit | Works | Inner lines | All lines |
|---|---|---|---|
| Bach, chorales | 6 | 2.19 | 2.30 |
| Corelli, trio sonatas | 5 | 1.78 | 1.76 |
| Vivaldi, trio sonatas | 6 | 2.58 | 2.69 |
| Haydn, quartets | 6 | 2.31 | 2.45 |
| Mozart, quartets | 6 | 2.63 | 2.72 |
| **All** | **29** | **2.32** | **2.41** |

## Running it where the weights are (Philip's Mac)

1. **Set up.** Python 3.10 to 3.12; NotaGen pins transformers 4.40.0, which has no wheels for newer Pythons. Then a clone of NotaGen, for its own model code: the writer uses it, and the scorer's `--verify` checks against it.

   ```bash
   python3.12 -m venv ~/.venvs/notagen && source ~/.venvs/notagen/bin/activate
   pip install torch "transformers==4.40.0" "numpy<2" abctoolkit==0.0.6 samplings==0.1.7 pyparsing music21
   git clone https://github.com/ElectricAlexis/NotaGen ~/NotaGen
   ```

   `WEIGHTS` below is the downloaded `weights_notagenx_p_size_16_p_length_1024_p_layers_20_h_size_1280.pth` (6.2 GB). Loading it can take up to about 8 GB of memory for a moment, then about 2 GB.
2. **The writer test:** a piece from a prompt, with NotaGen's own sampling (top-k 9, top-p 0.9, temperature 1.2). The prompt must be one of NotaGen's `gradio/prompts.txt` lines.

   ```bash
   python study/notagen_write.py WEIGHTS ~/NotaGen "Romantic" "Chopin, Frederic" "Keyboard" -o ~/Music_LLM/notagen-out --seed 1
   ```

   - **Output:** the ABC as NotaGen wrote it, the full ABC, MusicXML (NotaGen's `abc2xml.py`) and MIDI.
   - **Where it runs:** on the Mac's GPU (MPS) when there is one.
3. **The ear test:** first the scorer, then the comparison.

   ```bash
   python study/notagen_score.py WEIGHTS checks/notagen-ear-2026-11-23/inputs.jsonl -o checks/notagen-ear-2026-11-23/scores.jsonl --verify ~/NotaGen
   python checks/notagen-ear-2026-11-23/compare.py
   ```

   - **`--verify`:** first checks, on one window, that the scorer's single pass gives the probabilities NotaGen's own `generate()` gives. If they differ by more than 0.01 bits, it stops without scoring.
   - **Health check:** the scorer prints NotaGen's bits a character over each window. A model that loaded wrongly gives about 7.
   - **`--trust-pickle`:** use it only if the weights will not read as plain tensors. It reads the file as NotaGen itself does, which runs any code the file holds, so only for the file from huggingface.co/ElectricAlexis/NotaGen.
   - **The results:** `scores.jsonl` and `compare.json` are committed here.
