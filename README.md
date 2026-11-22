# composer-study

Measured studies of the composers in score-reader's catalogue, for composer-blend to compose with: profiles of narrow units (a composer in one kind of piece and one period), set against the other composers of the same kind and period, with pointers to the bars that show them; a listener's ear trained on the same notes (below); and, later, continuations.

- **`TRAINING.md`**: what training reads and what it leaves out (an editor's copy for playing is not the score).
- **`data/periods.json`**: each composer's periods, the second half of a unit (the kind comes from score-reader's `facts`). A work falls in the period whose years hold the year a source states for it, else whose catalogue numbers or title hold it; a work none holds belongs to no period, and its unit falls back to the composer. Each line gives its reason. Written on 21 November 2026 and left to stand: a period that sounds wrong in a piece is corrected here.
- **`study/periods.py`**: reads it (`period_of`). **`study/coverage.py <score-reader>/catalogue`**: how many works the numbers and titles place, composer by composer. Placing by year needs score-reader's facts and is not counted there.
- **`data/eras.json`**: each composer's shared period, the level a narrow unit falls back to after the composer and where the caps are counted (a composer's tenth, a collection's third: `TRAINING.md`, section 4): the sheet's period where the sheet has the composer, else by the year of birth on the sheet's own boundaries. **`study/eras.py`** reads it (`era_of`).

## The listener's ear

- **`study/lines.py`**: the works of score-reader's ready-read copy as melodic lines, by `TRAINING.md`.
  - **Lines:** each part becomes a line, its sounding skyline: the highest note at each onset, but not a note that begins under a higher note still sounding.
  - **Left out:** the editor's copies for MIDI (`midi_copy`) and IMSLP's organ files with their ornaments played out (`realized`).
  - **Weights:** each work weighs one; a composer is held to a tenth of a level and a collection to a third (`capped`).
  - **Repeats:** they are kept as played. `once` leaves out the spans heard again, for counts.
  - Copies of one work share a key (`label_key`), so a held-out work is never learnt through its twin.
  - Catalogue version 24 gives 14,039 works and 18.2 million notes in lines.
- **`study/ear.py`**: the listener's ear, piece 44's model (composer-blend, `pieces/44_mercy_twenty_one_times/model44.py`) moved here and trained on the whole catalogue.
  - **How it predicts:** a variable-order model (PPM, escape method C, orders 0 to 4) predicts each note in four views: interval, scale degree from the final, the two together, and the ratio of successive time-spans.
  - **Two memories:** a long-term memory of the corpus, and a short-term memory that learns the piece as it goes.
  - **Speed:** the long-term memory is kept as sorted arrays, so the whole catalogue is learnt in about 80 seconds.
  - **Two changes from piece 44, each measured on held-out works:**
    - The views and the memories are joined by unweighted geometric means. Piece 44 weighted each by its certainty, which trusts the short-term memory most when it has heard least: on 200 held-out works, 2.90 bits of pitch a note, against 2.54.
    - The line is the sounding skyline rather than the top note at each onset: a little better in four periods, the same before 1600.
- **`study/heldout.py`**: trains on nine tenths of the works and listens to the tenth held back, 120 works a period. Lower is better. On catalogue version 24, 402,539 notes held out:

  | Ear | Pitch, bits a note | Rhythm, bits a note |
  |---|---|---|
  | the catalogue (a work weighs one, caps) | 2.58 | 1.51 |
  | the catalogue, no short-term memory | 2.93 | 1.55 |
  | the catalogue, a note weighs one, no caps | 2.59 | 1.52 |
  | piece 44's five composers (Bach's chorales, Corelli, Mendelssohn, Beethoven and Mozart quartets) | 2.66 | 1.57 |
  | no context (order 0), with the short-term memory | 2.83 | 1.72 |

  - **What the catalogue adds:** over piece 44's five composers, most after 1890 (2.93 against 3.10) and in the Romantic period (2.54 against 2.66). Before 1600 it adds almost nothing, and there the short-term memory doesn't help either.
  - **The caps cost no accuracy** (2.58 against 2.59). What they change is whose idiom counts as normal.
  - **The short-term memory matters more than the corpus:** without it the catalogue's ear is worse than no context with it.
- **`study/rated.py`** and **`data/rated.json`**: piece 44's measure M0 against Philip's ratings, heard by this ear. M0 is the longest stretch in which the 4-second mean surprise stays under 1.5 bits.
  - **The claim, written before measuring:** on the 15 pieces rated since piece 44's test, M0 goes against the ratings.
  - **Result:** rho −0.01, one-sided p 0.49. **The claim does not pass.**
  - **Piece 44's own 15 pieces:** this ear finds what piece 44 found there, rho −0.63 (p 0.008). All 30 together: −0.29 (p 0.062).
  - **Reading:** the long flat stretches that marked the generic pieces of the first pool are mostly gone from the pieces made since. Ten of the 15 have no stretch longer than 4 seconds, and the longest (29 s) is the stillness of piece 52b, rated 4.5.
  - What separates those ratings is not melodic surprise. The ear can still show where a draft goes flat, but it does not predict Philip's verdict.

## The critic on drafts

- **`study/critic.py`**: where a draft goes flat, before Philip listens.
  - **The ear:** `--build` trains it on every work and saves it, about 75 MB, in about 4 minutes. A check then takes seconds.
  - **What "flat" means:** a note is flat where the 8 notes around it average less surprise than 95 in 100 such spans of real music. The threshold is measured on the catalogue's held-out works when the ear is built: 0.56 bits a note on version 24.
  - **What it names:**
    - the seconds where the whole texture is flat (every line that sounds is flat, or nothing sounds) for 8 s or more;
    - a line flat for 30 s or more;
    - each line's bits a note, and the share of its time spent flat.
  - **What it doesn't do:** score the piece. A flat stretch can be what the piece wants: an ostinato, a pulse, a stillness.
  - It reads a score's `build()` or a `*.render.json`, through `study/pieces.py`.
- **`checks/critic-2026-11-22.md`**: the critic against Philip's words, with what it should find written down before it ran.
  - **The test:** the one layer he called flat, Riley's in piece 37b ("a flat tune in the background that doesn't evolve").
  - **Found as expected:** Riley's pulse is flat from 0:02 to 2:49 in 37 and 37b, and the cello's melody isn't.
  - **The controls:** in 27, 29 and 49 (rated 5) and 46 (4.75), nothing is flat for 30 s, and the texture never for 8 s.
  - **What the check can't say:** a pulse of one note is the easiest thing to call flat, so this shows the critic sees what Philip heard, not that it would catch subtler cases.

Run the tests: `python3 -m pytest -q tests`.
