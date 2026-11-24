# The outside ears as rulers (24 November 2026)

**Why:** the three-ears test on piece 64b found the outside ears (NotaGen-X, NotaGen fine-tuned, AMT Large and Medium) agree with one another and prefer the inner voices Claude chose. Philip heard no clear winner between 64b's inner voices and AMT's. So he asked: if the inner voices are not where the models help, what could they do instead?

**Claude's answer:** these models measure how likely each note is, given what they have read. Asked to choose notes, they pull toward the middle, and Claude already leans their way: the chosen proposal was their favourite 2 to 2.5 times as often as chance. But the middle is useful as a ruler, to measure how far something sits from it. Four uses were proposed, and Philip is open to all four:

1. **Glitches:** a wrong note is far from every style, so the ears should flag it together.
2. **Flat stretches:** where nothing is unexpected for too long.
3. **Whose voice:** NotaGen takes a composer in its prompt; the prompt that finds a passage least surprising says whom it sounds like.
4. **Quotes:** a stretch a model finds nearly certain may be one it knows by heart.

**This run tests 1 and 4 on known material:** wrong notes planted on purpose, and real mazurkas put into 64b. Uses 2 and 3 come next, checked against Philip's verdicts on past pieces, once this says whether the ears measure anything useful.

**Status:** inputs made and checked; nothing scored yet. The predictions below were written before any model heard these inputs.

## 1. The glitch test (`ears-as-rulers-2026-11-24/prepare_glitch.py`, `compare_glitch.py`)

- **The music:**
  - **27 held-out works** from `notagen-ear-2026-11-23.md`: Bach chorales, Corelli and Vivaldi trio sonatas, Haydn and Mozart quartets.
    - Two are left out: Mozart's K. 575 and K. 589. In each, one moved note comes out of the ABC without the accidental its new pitch needs, so the copy would hold a second, unplanned change.
  - **Piece 64b:** the music the tool would be for.
- **The wrong notes:**
  - Single notes picked at random, seeded, an eighth or longer (no chord, tie or grace note), from the third bar to the third-last.
  - In the works: 2 to 8 a work, by length, at least 4 bars apart; 155 in all.
  - In 64b: three sets of 16, at least 6 bars apart, each set in copies of its own; 48 in all.
  - Each is moved up or down (at random), by a semitone in one copy and by a whole tone in another, spelt in its key's way.
- **Checked:** each copy's ABC differs from the original's at the planted notes, by the planted step, and nowhere else.
- **What the ears hear:** every note of each copy, and of the original.
  - **NotaGen:** each work's own prompt (64b: "Romantic / Chopin, Frederic / Keyboard"), a note's bits as before. A chord is its top note, left out of the comparison.
  - **AMT:** every note with no given notes. That is its plain sequence, flagged as AMT's own `generate()` flags one with no controls (`study/amt.py`, `alone=True`), all on the piano. The works are played at a quarter note of 90 a minute; 64b at the seconds the renderer plays it.
- **Together:** the notes all four ears score.
  - Each ear's bits are put on one scale within the copy, then averaged.
  - NotaGen's single notes match AMT's by part, onset and pitch: all of them in the works.
- **The measures:**
  - **A planted note's place:** the share of the copy's other notes at least as surprising to that ear (0 means the most surprising of all).
  - **Found at 2%:** among the 2% of a copy's notes a reader would be shown first; also given at 1% and 5%. In 64b, 2% is about 35 notes in five minutes.
  - **The rise:** a planted note's bits, minus those of the note it replaced.
  - **Intervals:** 95%, from resampling works (64b: its planted notes).
- **Also:** the 25 notes of 64b as written that the four ears together find most surprising. Claude looks at each in the score: an intended surprise, or a slip?

## 2. The quote test (`prepare_quote.py`, `compare_quote.py`)

- **The quotes:** eight bars of ten mazurkas, from the first whole bar the right hand plays in.
  - **Five by Chopin:** op. 7 no. 1, op. 17 no. 4, op. 24 no. 1, op. 33 no. 4 and op. 67 no. 4 (Chopin First Editions, kern). This is standard repertoire, which the ears' training may hold.
    - Op. 41 no. 2, 64b's own source, was the first choice. Music21 misreads its bar 8 in both editions, so op. 67 no. 4 replaces it.
  - **Five Polish mazurkas of the same century, little known:**
    - Statkowski, op. 27 no. 1. His op. 2 no. 1, the first choice, cannot be read by music21.
    - Stojowski, op. 8 no. 2.
    - Kątski, Mazur sielankowy op. 4.
    - Józef Stefani, Mazur in G no. 2.
    - Noskowski, Causeries op. 32.
    - All from Polish Scores, read for score-reader in 2026: less likely to be in the ears' training.
- **In 64b:** each quote replaces 64b's bars 41 to 48, every voice of them. Everything else is 64b's own, with the same prompt.
  - **NotaGen:** the quote's bars are the work's own ABC, its key written where each voice begins and 64b's E minor where each comes back.
    - Checked: the quote reads as it does alone, and 64b after it as it does without it.
  - **AMT:** the quote's notes at 64b's tempo for those bars.
- **Alone:** the same eight bars as a piece by themselves.
- **Two keys:**
  - **The work's own key**, and **a whole tone higher.**
  - Same notes, same style; only the key differs. A quote less surprising in its own key is one the ear knows note for note. Style alone does not explain that.
- **The measures:**
  - **A quote's bits:** the mean over its bars 3 to 8 (by then an ear that knows it has heard enough to know it).
  - **64b's own:** every six-bar stretch of 64b as written (the glitch test's scores). Where the quote falls among them is given as the share less surprising than it.
  - **The key difference:** own key minus a tone higher, in 64b and alone.

## Predictions, written before anything was scored (Claude's, not Philip's)

**The glitch test:**
1. **Real works, a semitone:** the four together find at least 60% of the planted notes at 2%.
2. **Real works, a whole tone:** fewer, at least 30% at 2%. A tone often lands on a note of the key, a wrong harmony rather than a wrong scale.
3. **64b:** less than on the real works, because 64b's own notes are already more surprising to these ears (2.7 to 3.3 bits a note in its inner voices, against about 1). A semitone 30% to 60% at 2%; a tone 15% to 40%.
4. **The best single ear:** NotaGen fine-tuned, on the real works. The four together within 5 points of it, and above the median single ear.
5. **The rise, real works, a semitone:** at least 4 bits a note (median) for both NotaGen checkpoints.

**The quote test:**
6. **NotaGen knows Chopin's notes:** for both checkpoints, alone, the Chopin quotes are less surprising in their own key in at least 4 of 5, by 0.3 bits a note or more on average. The Polish quotes are not: at most 3 of 5, and under 0.2 bits on average.
7. **AMT does not:** no key difference for either family, under 0.2 bits a note on average, and not 4 of 5.
8. **In 64b, NotaGen fine-tuned:** the Chopin quotes (own key) are less surprising than the Polish ones, by at least 0.3 bits a note on average.
9. **Low surprise alone does not mark a quote:** in 64b, the Chopin quotes fall under 64b's 5th percentile in at least 4 of 5, and so do the Polish ones in at least 3 of 5. Real music by anyone is less surprising to these ears than 64b. So only the key test tells a quote.

**What decides the uses (written now):**
- **Glitches:** worth running before each render if, on 64b, the four together find at least half the semitone errors at 2%. That is about 35 notes to look at in a five-minute piece. Below a quarter, dropped. Between, more planted notes before deciding.
- **Quotes:** worth keeping if prediction 6 holds for NotaGen fine-tuned. The check would then be: a stretch under the piece's 5th percentile, heard again a tone higher. A clear rise means the ear knows the notes.

## Running it where the weights are (Philip's Mac)

The same environment and paths as the three ears (`three-ears-64b-2026-11-23.md`): `WEIGHTS` is NotaGen-X, `FINETUNE` its fine-tuned checkpoint, and AMT's folders and checkout as before.

```bash
R=checks/ears-as-rulers-2026-11-24
for t in glitch quote; do
  python study/notagen_score.py WEIGHTS  $R/${t}_notagen_inputs.jsonl -o $R/${t}_notagen_x.jsonl --verify ~/NotaGen
  python study/notagen_score.py FINETUNE $R/${t}_notagen_inputs.jsonl -o $R/${t}_notagen_finetune.jsonl
  python study/amt_score.py ~/models/music-large-800k  $R/${t}_amt_inputs.jsonl -o $R/${t}_amt_large.jsonl
  python study/amt_score.py ~/models/music-medium-800k $R/${t}_amt_inputs.jsonl -o $R/${t}_amt_medium.jsonl
done
python $R/compare_glitch.py
python $R/compare_quote.py
```

- **Health:**
  - NotaGen's `--verify` should agree with its own `generate()` within 0.01 bits.
  - AMT's bits a note token should be well under 14 (about 14 is a model that loaded wrongly). These inputs use AMT's no-controls flag for the first time here, so the value is new: worth a look.
- **Size:** 88 NotaGen and 88 AMT inputs for the glitch test (whole works, up to 28 AMT windows each), 40 and 40 for the quotes.
- **The results:** commit the eight score files and the two `compare_*.json`.

## Changes to the library

- **`study/amt.py`:** `window()` and `windows()` take `alone=True` for a sequence with no given notes. It is flagged AUTOREGRESS, as AMT's own `generate()` flags one, instead of ANTICIPATE. Earlier inputs are unchanged.
- **`study/notagen.py`:** `prepare_lines()` reads NotaGen's lines as `prepare_abc()` does. `prepare_abc()` now calls it, and the quote test reads its spliced lines with it.
- **Tests:** one each (63 pass).
