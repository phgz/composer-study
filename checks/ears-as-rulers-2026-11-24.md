# The outside ears as rulers (24 November 2026)

**Why:** the three-ears test on piece 64b found the outside ears (NotaGen-X, NotaGen fine-tuned, AMT Large and Medium) agree with one another and prefer the inner voices Claude chose. Philip heard no clear winner between 64b's inner voices and AMT's. So he asked: if the inner voices are not where the models help, what could they do instead?

**Claude's answer:** these models measure how likely each note is, given what they have read. Asked to choose notes, they pull toward the middle, and Claude already leans their way: the chosen proposal was their favourite 2 to 2.5 times as often as chance. But the middle is useful as a ruler, to measure how far something sits from it. Four uses were proposed, and Philip is open to all four:

1. **Glitches:** a wrong note is far from every style, so the ears should flag it together.
2. **Flat stretches:** where nothing is unexpected for too long.
3. **Whose voice:** NotaGen takes a composer in its prompt; the prompt that finds a passage least surprising says whom it sounds like.
4. **Quotes:** a stretch a model finds nearly certain may be one it knows by heart.

**This run tests 1 and 4 on known material:** wrong notes planted on purpose, and real mazurkas put into 64b. Uses 2 and 3 come next, checked against Philip's verdicts on past pieces, once this says whether the ears measure anything useful.

**Status:** scored on Philip's Mac on 24 November; results at the end. The predictions were written before any model heard these inputs.

- **Wrong notes:** the four ears together catch half of the wrong notes planted in 64b (52%), just over the bar set for keeping the check. Of the 25 notes they flag in 64b as written, 10 sit at six places where Claude, reading the score, finds the inner voices weak.
- **Quotes:** the quote check fails. NotaGen shows no sign of knowing Chopin's mazurkas note for note. AMT shows a little, too little to single out a quote.

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

## Results (scored on Philip's Mac, 24 November)

**Health:**
- NotaGen-X's `--verify` agreed with its own `generate()` within 3.5e-05 bits (glitch inputs) and 1.4e-05 (quotes).
- AMT with no given notes, the first time: 0.80 to 2.33 bits a note token (Large).
- AMT Large's first glitch run stopped at 51 of 88 inputs when the Mac's disk filled; it was scored again in full.

### The glitch test

**Found at 2%** (the four together with their 95% intervals):

| Ear | Works, semitone | Works, tone | 64b, semitone | 64b, tone |
|---|---|---|---|---|
| NotaGen-X | 81% | 80% | 35% | 29% |
| NotaGen fine-tuned | 85% | 84% | 29% | 23% |
| AMT Large | 80% | 76% | 40% | 31% |
| AMT Medium | 77% | 74% | 44% | 29% |
| **The four together** | **92%** [87, 96] | **88%** [80, 95] | **52%** [38, 67] | **42%** [27, 54] |

**The median rise** (a semitone): 18.6, 12.6, 10.8 and 9.9 bits on the works; 8.7, 5.6, 4.9 and 5.4 in 64b.

**The predictions:**
1. Real works, a semitone, at least 60%: **held** (92%).
2. Real works, a whole tone, at least 30% and fewer than a semitone: **held in the letter** (88%). The reason given was wrong: a whole tone is found almost as often as a semitone, not much less often.
3. 64b: a semitone 30% to 60%: **held** (52%). A tone 15% to 40%: **missed** (42%, above).
4. Best single ear NotaGen fine-tuned, the four together within 5 points of it: **held**, and better than predicted. The four together beat every single ear, by 7 points on the works. In 64b, no single ear reaches half (29% to 44%), and the ranking turns over: AMT Medium is best and NotaGen fine-tuned worst.
5. The rise at least 4 bits: **held** (18.6 and 12.6).

**The decision, by the rule written beforehand:** at least half the semitone errors in 64b: 52%, so the check is worth running before each render. It is at the edge. The interval runs from 38% to 67%, and half of the wrong notes still get past it.

### What the four flag in 64b as written

These are the 25 notes the four together find most surprising. Claude looked at each in the score; these are judgments from the score, not from listening.

- **8 are in the parts Claude wrote by hand, and meant:**
  - Bar 3: the tune's D sharp, after an opening (E7, then A minor) that sounds like A minor.
  - Bars 6 and 34: the tune's leaps.
  - Bar 7: the bass to C.
  - Bars 82 and 84: the intermezzo's flourishes.
  - Bar 105, twice: E flat major to E minor at once.
- **10 sit at six places where the inner voices (the model's proposals Claude chose) look weak:**
  - Bar 5, beat 1: alto and tenor in unison on G sharp 3. That is the leading tone of the coming A minor, doubled, with the alto at the bottom of its range.
  - Bar 21, beat 2: the tenor's D sharp 4 a semitone under the alto's E4, struck together. The tune's C sharp 5 above them is flagged too.
  - Bars 29 and 30:
    - The tenor's F sharp, G, G sharp against the alto's G sharp.
    - Then the tenor on C3, its lowest note, a third above the bass.
    - The alto leaps a tenth to C sharp 5, then drops an octave as the tune arrives on that same C sharp 5.
  - Bar 32, beat 1: section 1 arrives on E minor with A sharp and D in the inner voices.
  - Bar 62, beat 1: the tenor's B natural where the plan has F7, so the chord heard is B half-diminished over F.
  - Bar 112, beat 1: the tenor's C sharp in a tonic bar (E minor over G).
- **7 are colours Claude would defend:**
  - Bar 4: the tenor's G sharp just after the tune's G, a false relation Chopin uses.
  - Bar 9: C sharp as E7's thirteenth.
  - Bar 53: a 4-3 suspension.
  - Bar 54: B flat in three voices.
  - Bar 76: an added sixth.
  - Bar 100: the alto dropping an octave.
  - Bar 160: a C sharp neighbour in the last bar.

The flags fall unevenly: the inner voices are about half of 64b's notes, but 16 of the 25 flags.

Whether these spots sound wrong is Philip's to say. Piece 64b was rated 4.5 with all of them in it.

### The quote test

**Own key minus a tone higher**, bits a note; negative means less surprising in the key the work was written in. In brackets: how many of the five quotes are lower in their own key.

| Ear | Chopin, alone | Polish, alone | Chopin, in 64b | Polish, in 64b |
|---|---|---|---|---|
| NotaGen-X | +0.53 (1 of 5) | -0.43 (3 of 5) | +0.15 (0 of 5) | +0.01 (1 of 5) |
| NotaGen fine-tuned | +0.02 (2 of 5) | -0.15 (4 of 5) | +0.06 (1 of 5) | -0.15 (5 of 5) |
| AMT Large | -0.16 (5 of 5) | -0.02 (3 of 5) | -0.13 (5 of 5) | -0.04 (3 of 5) |
| AMT Medium | -0.21 (5 of 5) | -0.02 (2 of 5) | -0.18 (5 of 5) | -0.00 (2 of 5) |

**The predictions:**

6. NotaGen knows Chopin's notes: **failed.** Neither checkpoint does, as far as this test can see. One limit: NotaGen reads notation. If its training held these works in another edition's ABC, the memory would not carry over character for character.
7. AMT does not: **failed.** AMT is the one that does, a little. Every Chopin quote is less surprising in its own key, for both models, alone and in 64b. The Polish ones are not.
8. In 64b, Chopin at least 0.3 bits a note below the Polish quotes (NotaGen fine-tuned): **failed** (2.41 against 2.65: 0.23, in the predicted direction).
9. The quotes under 64b's 5th percentile: **failed.**
   - None of the ten falls there for NotaGen; one or two of five do for AMT.
   - Dropped into 64b, a real mazurka is about as surprising as 64b's own stretches.
   - A fairer comparison, opening against opening: 64b's bars 3 to 8, heard from its start, are more surprising than the mazurkas' bars 3 to 8 alone. NotaGen fine-tuned: 3.26 bits a note against 2.77 (Chopin) and 2.43 (Polish). AMT: 3.4 against 1.4 to 1.6.
   - 64b's later stretches only look ordinary because its theme keeps coming back.
   - NotaGen-X's scores for the eight bars alone (6.7 to 7.5 bits a note) are far above the fine-tuned checkpoint's, as if it does not know what to do with so short a piece. Its quote numbers are set aside.

**The decision:** prediction 6 failed, so the quote check is dropped. AMT's sign is real but small (0.13 to 0.21 bits a note), and two Polish quotes show as much in 64b (Kątski -0.11, Noskowski -0.15, AMT Large). It cannot single out a quote.

This also corrects a claim Claude made to Philip, that these models "know a lot of works nearly by heart". For these mazurkas, NotaGen does not, and AMT barely does.

### Listening: the six places (`spots64.py`, `spots64_cut.py`, `spots64/`)

Five files, one for each place (bars 29 and 30 share a file with bar 32). Each plays 64b as written from the bar before to the bar after: the whole texture, then 3 seconds of silence, then the inner voices alone. Each part is brought to -20 LUFS, so the inner voices alone are louder than they are in the piece. The flagged moments, in seconds from the start of each file:

- `64b_bars_4-6`: bar 5, beat 1, at 1.8 (inner voices alone: 11.1).
- `64b_bars_20-22`: bar 21, beat 2, at 2.3 (11.6).
- `64b_bars_28-32`:
  - Bar 29, beat 2, at 2.3 (14.8).
  - Bar 30, beats 1 and 2, at 3.3 and 3.8 (15.8 and 16.3).
  - Bar 32, beat 1, at 6.3 (18.8).
- `64b_bars_61-63`: bar 62, beat 1, at 1.4 (9.4).
- `64b_bars_111-113`: bar 112, beat 1, at 1.5 (9.8).

**Philip's hearing (24 November), his words:** "I'd flag 20-22, 28-32. 61-63, 111-113 I'm uncertain". He did not flag bars 4 to 6. Asked whether he heard bars 21 and 29 to 32 as wrong in the whole texture or only with the inner voices alone: "I'd say in the whole texture."

- **The tally:** of the five files, Philip flags two (bar 21; bars 29, 30 and 32), is unsure of two (bars 62 and 112), and does not flag one (bar 5).
- **The pipeline:** the models flagged 25 notes, Claude picked out six places from them, and Philip hears two of those as wrong. He knew which moments Claude thought weak when he listened. He still left one unflagged and was unsure of two, so he was not simply agreeing.
- **Where the heard places rank** among the notes the four together find most surprising in 64b as written (of 1315):
  - Bar 21: 17th (the tune) and 19th (the tenor).
  - Bar 29: 13th.
  - Bar 30: 3rd, 5th and 25th.
  - Bar 32: 15th.
  - The unsure places: 16th and 21st. Bar 5, not flagged: 7th.
- **Two ears instead of four** (from the same scores):

| Ears | Found at 2% in 64b, a semitone | A tone | Where the heard places rank |
|---|---|---|---|
| All four | 52% | 42% | 3rd to 25th |
| AMT Large and Medium | 46% | 33% | bar 30: 1st and 3rd; bar 21's tune: 14th; the rest 59th to 309th (of 1745 notes) |
| NotaGen-X and fine-tuned | 29% | 27% | 3rd to 50th |

  - AMT alone needs only the notes the renderer plays, so it can hear any piece, in any instruments. NotaGen needs the piece written out as a score.
  - With AMT alone, both heard places would still be among the first 35 flagged (bar 30; bar 21 through its tune), but bars 29 and 32 would not.

### Next

- **The glitch check:** kept, at the edge.
  - It needs the Mac, where the weights are: the four ears over a new piece, then the 25 most surprising notes listed for Claude to look at.
  - First, whether the six weak spots in 64b sound wrong to Philip. If they do not, a list that only Claude finds wanting is not worth a Mac run per piece.
- **Uses 2 and 3:** flat stretches, and whose voice a passage sounds like, checked against Philip's verdicts on past pieces.

## The repair test (`prepare_repair.py`, `choose_repair.py`, `repair64.py`, `repair64_cut.py`)

**Why:** the first of the further uses Philip agreed to: "That would be interesting". When the check flags a slip, let AMT rewrite just those bars. For a slip, the pull to the middle is what is wanted. The line held: the models for correctness (voice-leading, spacing), never for character.

**The places:** the two Philip heard as wrong in the whole texture, bar 21 and bars 29 to 32. Three versions, each named when heard:

- **As written:** 64b untouched.
- **Claude's rewrite, by hand** (`repair64.py`, CLAUDE):
  - Bar 21: the alto holds F sharp 4, a 9-8 over bar 22's E. The tenor plays D4, then B3. No more D sharp under E.
  - Bars 29 to 32: two plain voices on the plan's chords (E7; A minor, then A sharp diminished; C, then F; E minor). The section ends on a plain E minor (E2, B3, E4, G4).
- **AMT's rewrite:**
  - AMT gets the tune and the bass of the whole piece on the bright piano ("two pianos"). It also gets the inner voices everywhere else: those before a place as played, those after as notes it knows are coming.
  - It writes the inner voices of the two places with its own `generate()`: AMT Large and Medium, seeds 1 to 8, sixteen candidates.
- **In both rewrites,** an inner note that would sound on into a place is cut where the place begins, as AMT was given it.

**The choice among AMT's sixteen, by a rule written before any was made** (`choose_repair.py`): the fewest faults in the place, the bar before and the bar after. Ties go to the fewest echoes of the tune or the bass, then Large, then the lower seed. The faults counted:

- `notes64.check()`: voices crossing, parallel fifths or octaves, a voice out of its range.
- An inner note struck a semitone or a minor ninth from another voice.
- A unison between the inner voices.
- Three inner notes at once.
- A beat of a place with no inner note.
- An inner voice leaping more than an octave.
- A false relation between the inner voices within a beat.

**The same count for the other two:**
- **As written:** 9 faults (the struck second in bar 21; the alto's leap of a tenth in bar 30; the false relations in bars 21, 29 and 30).
- **Claude's rewrite:** 0, after one change. Its first draft had a false relation in bar 30 (C in the alto, C sharp in the tenor a beat later). The alto now takes the chromatic step itself.
- **What the rule misses:** bar 32's blurred arrival, which Philip heard among bars 28 to 32. It is not among its faults.

**Running it on the Mac:**

```bash
R=checks/ears-as-rulers-2026-11-24
for m in large medium; do for s in 1 2 3 4 5 6 7 8; do
  python study/amt_write.py ~/models/music-$m-800k ~/anticipation $R/amt_repair.json -o $R/repair_${m}_$s.json --seed $s --given-program 1
done; done
```

Use AMT's checkout path as for the earlier writing. Commit the sixteen `repair_*.json`. Claude then runs `choose_repair.py`, renders the three versions and cuts the two clips (`repair64_cut.py`).

**What AMT wrote** (on Philip's Mac, 24 November): 13 to 25 notes in each candidate, all inside the two places.

| Version | Faults by the rule |
|---|---|
| 64b as written | 9 |
| Claude's rewrite | 0 |
| AMT's sixteen | 7 to 16 |

- **Only one AMT candidate has fewer faults than as written:** Medium seed 7, with 7.
- **The most common faults:**
  - Three inner notes at once: AMT does not keep to two voices.
  - Parallel octaves or fifths with the tune.
  - Struck seconds.
  - At the end of bars 29 to 32, AMT writes bar 33's first notes again, a hair before the barline. It is anticipating the notes it was told are coming. These count as unisons.
- **The hypothesis does not hold here.** "For a slip, the average is the right fix" is not borne out by AMT's writing, at least in this setup. It does not repair the voice-leading; it rewrites the bars about as roughly as the original.

**The chosen rewrite** (`repair_chosen.json`, Medium seed 7):
- **Bar 21:** the tenor alone (F sharp 3, then B3), the alto silent.
- **Bars 29 to 32:**
  - Alto: E4, D4 | C sharp 4, E4, E4 | E4, A4 | E4.
  - Tenor: G sharp 3, B3 | G3, G3 | G3, A3, B3.
  - At bar 30's downbeat, the alto's C sharp turns the plan's A minor into A major.
- **Left out of the render:** its two repeated notes at bar 33, as duplicates of 64b's own.

**Listening** (`repair64/`): two files, each 64b as written, then Claude's rewrite, then AMT's, 1.5 seconds apart, at one level.
- `64b_bars_20-22_as_written_then_Claude_then_AMT.mp3`: the three start at 0, 7.8 and 15.6 seconds.
- `64b_bars_28-33_as_written_then_Claude_then_AMT.mp3`: at 0, 12.3 and 24.6 seconds.

**Philip's hearing (24 November), his words:** "They sound... similar".

- **One more of the same:** this is the third time a change to 64b's inner voices has made little difference to his ear.
  - 64b's against AMT's: "I can't say there is a clear winner honestly".
  - Now as written, Claude's rewrite and AMT's, where Claude's has none of the faults he heard.
- **What it suggests:** in this piano texture, the inner voices sit under what he listens to. A place can sound a little off without a cleaner version sounding clearly better. So a check that fixes inner-voice slips changes little of what he hears in this texture. The tune, the bass, the form and other textures are not tested by this.
- **What would tell more:** whether the four ears find the moments Philip himself named in past pieces. For example, "2:46 sounds out of place" in piece 34, and the two ornamented spots that "sounded strange" in "Said Again".

## The rhythm test (`prepare_rhythm.py`, `compare_rhythm.py`)

**Why:** Philip, asked what the glitches he has heard in the pieces were like: "mostly a wrong-sounding note or a stumble in the rhythm". The glitch test covered wrong notes. This covers stumbles, by a new measure: the bits of each note's onset. `study/amt_score.py` now keeps it as a fourth number for each note, and the bits of its length as a fifth.

**The records hold almost none of his own named moments to check against.**
- The one named moment there is "2:46 sounds out of place" in piece 34: a stroke on gongs. The bracket test's drum list leaves gongs out, and AMT hears every part on a piano.
- Piece 38's "glitches" came from the player inside the app, not from the file.
- "Said Again" (the practice round) and the cross-genre morphs are not in these repositories.
- So the test is planted again, and then forward: see below.

**The stumbles:** two kinds, each in copies of their own, in the 27 works of the glitch test and in 64b. They are picked as the wrong notes were: notes an eighth or longer, spaced, as many per work, and in 64b three sets of sixteen.
- **A note off:** one note begun a sixteenth early or late, its end kept.
- **A skip:** a sixteenth of time taken out at one onset. Every note from there on comes a sixteenth early, and a note sounding across it is a sixteenth shorter.
- **The sixteenth:** a sixth of a second in the works (a quarter note at 90). In 64b, a quarter of the beat at that moment in its tempo map.

**The measure:**
- **What counts as the stumble:** the onset bits of the moved note, or of the first onset after the skip (its lowest note).
- **The comparison:** the lowest note of every other onset in the copy. The other notes of a chord cost next to nothing.
- **Found at 2%:** as in the glitch test.

**Predictions, written before anything was scored (Claude's):**
1. **Works, a note off:** AMT Large finds at least 50% at 2%.
2. **Works, a skip:** at least 60% at 2%. A skip moves the whole pulse, and AMT hears the beat.
3. **64b:** fewer than the works for both kinds; a note off 20% to 50%, a skip 30% to 60%. 64b's tempo changes make every onset a little less certain.
4. **AMT Medium:** within 10 points of Large.

**What decides it (written now):** the rhythm check is kept if, in 64b, AMT Large finds at least half of either kind at 2%.

**Then forward, on the next new piece:**
- Before Philip hears it, the four ears (notes) and AMT (onsets) list its most surprising moments.
- The list is written into the piece's folder and not shown to him.
- He listens as he always does. When a note or a stumble sounds wrong, he says roughly when.
- Afterwards, his moments are set beside the list. This is not a blind test: he hears the piece as usual and nothing is hidden from him except the list.

- **Philip, asked whether he would give rough times when something sounds off:** "Sure".
- **The tool:** `study/flag_piece.py`, with three steps: prepare, here; score, on the Mac; report into the piece's folder as `flags/FLAGS.md`. A fourth step, `compare`, sets his times beside the list.
- **The rule:** composer-blend's PROCEDURE (section F, its PR #96).
- **For now, AMT only:** NotaGen reads a written score, and no exporter has been written yet.

**Running it on the Mac:** `study/amt_score.py` has changed again; pull the branch first.

```bash
R=checks/ears-as-rulers-2026-11-24
python study/amt_score.py ~/models/music-large-800k  $R/rhythm_amt_inputs.jsonl -o $R/rhythm_amt_large.jsonl
python study/amt_score.py ~/models/music-medium-800k $R/rhythm_amt_inputs.jsonl -o $R/rhythm_amt_medium.jsonl
python $R/compare_rhythm.py
```

There are 88 inputs, about 98,000 notes. Commit the two score files and `compare_rhythm.json`.

### The rhythm test's results (scored on Philip's Mac, 24 November)

**Health:** AMT Large scored 0.80 to 2.30 bits a note token (median 1.35), and 0.20 onset bits a note on average.

**Found at 2%** (95% intervals; the comparison is every other onset of the copy):

| | Works, a note off | Works, a skip | 64b, a note off | 64b, a skip |
|---|---|---|---|---|
| AMT Large | 79% [72, 87] | 71% [59, 83] | 98% [94, 100] | 92% [83, 98] |
| AMT Medium | 82% | 71% | 100% | 96% |

**The median rise:** 8 to 12 bits.
- **Where the misses come from:** in the works, 14% of the moved notes landed on another note's onset. AMT's onset bits cannot single those out; they are most of the notes off it missed.
- **What that means:** a note begun with another voice, a sixteenth from its own place, is a stumble to a listener following that line, not to the onset measure.

**The predictions:**
1. Works, a note off, at least 50%: **held** (79%).
2. Works, a skip, at least 60%: **held** (71%), but fewer than a note off, not more as reasoned.
3. 64b, fewer than the works: **failed**, the other way. 64b's are found almost all (98%, 92%).
   - 64b's mazurka keeps a steady three-beat bar, and its tempo map moves slowly. So a note a sixteenth off its grid stands out more there than in the works' quicker, denser counterpoint.
   - The reason given (64b's tempo changes making every onset less certain) was wrong for this piece.
4. Medium within 10 points of Large: **held**.

**The decision, by the rule written beforehand:** kept. In 64b, AMT Large finds at least half of either kind (98%, 92%).

**The limit:** these stumbles were planted in notes timed exactly. A render's own timing (rubato, a performance's small irregularities) is not, and it will compete with any real stumble. The forward test on the next piece is where that shows.

