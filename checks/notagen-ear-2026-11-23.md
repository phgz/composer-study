# NotaGen's ear beside ours (23 November 2026)

**The question:** how surprised is NotaGen by the real notes of held-out works, against the continuations' ear, note for note? Inner lines first, since that is where piece 64b used the ear. Lower is better.

**Status:** run on 23 November 2026, on Philip's Mac. On inner lines NotaGen is far less surprised than ours: 1.16 bits a note against 2.32, lower in 28 of 29 works. Its training may hold these works, so this says how the two ears compare on this music, not which generalises better. The predictions below were written before it scored any note; two of the four held only in part, and one missed.

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

## NotaGen's half, and the difference

Run on 23 November 2026 on Philip's Mac (Apple M2, its GPU through MPS), with Python 3.11.15, torch 2.15.0, transformers 4.40.0 and NotaGen at 4553cd7.
- **The weights:** their SHA-256 is the one huggingface.co lists (`3df0bc38…`). They read as plain tensors, so `--trust-pickle` was not needed.
- **`--verify`:** the largest difference from NotaGen's own `generate()` was 3.5e-05 bits, against a limit of 0.01.
- **Health:** NotaGen's bits a character were 0.17 to 0.75 over the works, median 0.35. A model that loaded wrongly gives about 7.
- **The windows:** every work fitted one, and each took under 9 seconds.

Pitch bits a note on the compared notes, each work weighing one. The difference is NotaGen minus ours, with its 95% interval. Every p is under 0.001:

| Which notes | Notes | Ours | NotaGen | NotaGen minus ours | Works where NotaGen is lower |
|---|---|---|---|---|---|
| **Inner lines** | 5,945 | 2.32 | 1.16 | **-1.16** [-1.34, -0.96] | 28 of 29 |
| All lines | 12,653 | 2.41 | 1.19 | -1.22 [-1.41, -1.02] | 28 of 29 |
| Top line | 3,405 | 2.39 | 1.65 | -0.74 [-1.03, -0.42] | 25 of 29 |
| Bass | 3,303 | 2.58 | 0.76 | -1.82 [-2.10, -1.54] | 28 of 29 |
| Inner, written without an accidental | 5,513 | 2.16 | 1.11 | -1.05 [-1.22, -0.85] | 28 of 29 |
| Inner, written with an accidental | 432 | 4.71 | 1.82 | -2.89 [-3.56, -2.24] | 28 of 29 |

Inner lines by unit:

| Unit | Works | Ours | NotaGen | NotaGen minus ours | Works where NotaGen is lower |
|---|---|---|---|---|---|
| Bach, chorales | 6 | 2.19 | 0.70 | -1.49 [-1.83, -1.05] | 6 of 6 |
| Corelli, trio sonatas | 5 | 1.78 | 0.53 | -1.25 [-1.26, -1.23] | 5 of 5 |
| Vivaldi, trio sonatas | 6 | 2.58 | 1.73 | -0.85 [-1.34, -0.35] | 5 of 6 |
| Haydn, quartets | 6 | 2.31 | 1.63 | -0.69 [-0.89, -0.46] | 6 of 6 |
| Mozart, quartets | 6 | 2.63 | 1.10 | -1.53 [-1.68, -1.38] | 6 of 6 |

The rest is in `notagen-ear-2026-11-23/compare.json`, including each test unit by unit.

- **NotaGen is far ahead, almost everywhere.**
  - On inner lines it gives the real note 2.2 times the probability ours gives, on average (a geometric mean).
  - The one work where it is not lower is Vivaldi op. 1 no. 7's fourth movement: 2.56 against 2.38, on 49 notes.
  - Corelli's interval is narrow because his five works differ by almost the same amount, -1.22 to -1.26.
- **The advantage grows with how much of the bar NotaGen has already read.** This fits "What it has heard of the bar" above, but does not prove it.
  - It is smallest on the top line (-0.74), which NotaGen writes first in each bar.
  - It is larger on inner lines (-1.16), which come after the top voice's bar.
  - It is largest on the bass (-1.82), which comes after every other voice's bar.
  - On the top line it is no better than ours on Haydn's quartets (2.41 against 2.41), and lower in only 3 of Vivaldi's 6 works.
- **The notes written with an accidental:** these are the sharps, flats and naturals the ABC writes. Ours finds them very surprising (4.71 bits a note), NotaGen much less (1.82), even though NotaGen pays for their spelling.
- **The chorales:** over all lines, NotaGen hears four of the six at 0.22 to 0.33 bits a note. That means it puts 80% to 86% of its probability on the real note, on average. This is close to recall, and fits its training holding them.
- **Work by work (a reading after the results, not a test), the gap is uneven:**
  - Some works NotaGen seems to know by heart: chorale 161's inner voices cost it 0.14 bits a note, chorale 366's top line 0.02, Vivaldi's op. 1 no. 12 (inner) 0.25.
  - On others its top line is worse than ours: Haydn op. 50 no. 1, iii (4.67 against 2.77), and the fourth movements of Vivaldi's op. 1 nos. 6, 7 and 9.
  - So the gap mixes three things: memory of these works, the order of writing, and a larger model with a longer memory of the piece. This test cannot separate them; music neither has seen can.
- **Unit by unit,** each sign-flip p is as low as its number of works allows when every work goes the same way: about 0.03 with 6 works, 0.06 with 5.
- **Agreement:** Spearman's rho is 0.47 over all inner notes (the median within a work is 0.42; `compare.py` now gives tied values their average rank, where the first run's 0.40 hung on how the sort broke ties). So the two ears find the same notes surprising, but only moderately.

## The predictions against it

1. **Missed.** The gap is larger than predicted: 1.16 bits a note, with an interval of 0.96 to 1.34, all above the predicted 0.5 to 1.0.
2. **Held in part.** NotaGen is under 1 bit a note on Bach's chorales (0.70 on inner lines). But on inner lines the gap on Mozart's quartets is as large (-1.53, against Bach's -1.49). Over all lines, Bach's gap is the largest (-1.72).
3. **Held in part.** The advantage is smaller on the top line than on the bass (-0.74 against -1.82), as predicted. But on inner notes written with an accidental it is larger, not smaller: -2.89 against -1.05.
4. **Held.** Rho is 0.47, within the predicted 0.3 to 0.5.

## The writer test

`study/notagen_write.py` with the prompt Romantic / Chopin, Frederic / Keyboard and seed 1 wrote its piece in 137 seconds. The files are in `notagen-writer-2026-11-23/`: the ABC as NotaGen wrote it, the full ABC, the MusicXML and the MIDI.
- **The piece:** an Andante in 6/8, marked pianissimo, 45 bars after an upbeat.
- **Its key:** F sharp minor under A major's key signature. It ends with a fermata on the tonic chord, after the dominant.
- **Its shape:** the opening phrase comes back, nearly the same, at bar 9.
- **Played** as written on the Salamander grand, at 64b's loudness: `notagen-writer-2026-11-23.md`. Philip has not heard it yet.

## Not checked

- **Whether NotaGen's training holds these works.** Its fine-tuning list was not read here.
- **Music neither ear has heard:** piece 64b's inner voices, the third test planned.

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
