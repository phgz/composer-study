# composer-study

Measured studies of the composers in score-reader's catalogue, for composer-blend to compose with: profiles of narrow units (a composer in one kind of piece and one period), set against the other composers of the same kind and period, with pointers to the bars that show them; a listener's ear trained on the same notes (below); and continuations, ways to carry a line on in a unit's manner.

- **`TRAINING.md`**: what training reads and what it leaves out (an editor's copy for playing is not the score).
- **`data/periods.json`**: each composer's periods, the second half of a unit (the kind comes from score-reader's `facts`). A work falls in the period whose years hold the year a source states for it, else whose catalogue numbers or title hold it; a work none holds belongs to no period, and its unit falls back to the composer. Each line gives its reason. Written on 21 November 2026 and left to stand: a period that sounds wrong in a piece is corrected here.
- **`study/periods.py`**: reads it (`period_of`). **`study/coverage.py <score-reader>/catalogue`**: how many works the numbers and titles place, composer by composer. Placing by year needs score-reader's facts and is not counted there.
- **`data/eras.json`**: each composer's shared period, the level a narrow unit falls back to after the composer and where the caps are counted (a composer's tenth, a collection's third: `TRAINING.md`, section 4): the sheet's period where the sheet has the composer, else by the year of birth on the sheet's own boundaries. **`study/eras.py`** reads it (`era_of`).

## Research on composers: the skill

`.agents/skills/music-llm-study/` is the skill for researching a composer: writing or extending a page in `composers/`, reading scores through score-reader and sources, checking what a source says. `AGENTS.md` routes tasks; `SKILLS.md` says how to package the skill for Claude (`tools/package_skill.py`).

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

## Profiles of narrow units

A narrow unit is a composer in one kind of piece and one period: Chopin's mazurkas of his Paris years, Beethoven's late piano sonatas.

- **`study/profiles.py <ready-read copy> [--surprise s.json] -o profiles`**: the profiles.
  - **The facts** (each work's kinds, forces, years and catalogue numbers) come from the copy's own `facts.json` (catalogue version 25 on). For an older copy, `study/facts.py <score-reader> <ready-read copy> -o facts.json` writes them from a score-reader checkout, passed with `--facts`.
  - **Who is in a unit:** a work belongs to a unit for each kind its facts give it, for its forces, in the period `data/periods.json` gives it. A work no period holds counts in the composer's "any period".
  - **What is measured,** each work weighing one: the melody's moves, range, register and rhythm; the ear's surprise; the texture's density.
    - The melody is the voice in a work for a voice and accompaniment, where the reading names its parts; elsewhere it is the top line.
  - **Its harmony,** where 3 or more of its works carry the analysts' labels (`study/harmony.py`): DCML's corpora (reviewed labels, with cadences) or When in Rome's Roman numerals (no cadences). Each page says how many of the unit's works are labelled, and by whom. Nothing is worked out from the notes alone: a unit without labels has no harmony.
    - **What is measured:** how often the chords and the keys change; the share of chords on the tonic and the dominant, of sevenths and diminished sevenths, of applied chords, augmented sixths, Neapolitans, chords borrowed from the other mode, and inversions; how far the music goes from home; where DCML marks them, how often cadences come and which kinds (some of its corpora mark none: the ABC, Winterreise, Koželuch's sonatas, Mendelssohn's quartets and more); and the melody's notes outside the chord, whether they are struck with it, and whether they resolve by step.
    - **Set against** other composers' labelled works of the same kind, forces and period; where those are fewer than 20, the same forces and period; then the period. Labels are fewer than notes, so the comparison widens more often than the melody's.
      - Where it widens to the period alone, the measures that depend on the forces (how often the chords change, the melody against the chords) are not compared: a chorale's soprano is not set against a keyboard suite's top line.
      - Changes of key and applied chords are compared within one analyst's labels: where When in Rome writes a new key, DCML may write applied chords in the old one.
    - **Its progressions:** three chords in one key, as Roman numerals (V65, viio7/V, Ger), that the unit uses far more than the works it is set against, with the bars where they stand. They are set against the same analyst's labels where there are 20 such works.
      - One chord held while its seventh enters or its bass moves (V then V7) is one chord, written as the seventh. DCML's cadential six-four, V(64), is written I64, as When in Rome writes it.
      - The melody's notes outside the chord are measured against the chord's own notes, from its root and kind. A suspension DCML writes into the label (V(4)) is outside it, as it is in When in Rome's.
  - **Who it is set against:** the other composers' works of the same kind, for the same forces, in the same shared period. Where those are fewer than 20, the comparison widens step by step and says so. The others are weighted as at a shared level: a composer at most a tenth, a collection at most a third.
  - **A trait:** a measure where a work of the unit stands above a work of the others 75 times in 100 or more, or 25 or fewer.
  - **Its figures:** four-note figures of the melody, with their rhythm, that the unit uses far more than the others, each with the bars where it stands.
- **`profiles/`**: the profiles of catalogue version 25, one Markdown page and one JSON file a composer, with `index.json`.
- **Known limits:**
  - About a quarter of the works have no kind in score-reader's facts, and are in no unit.
  - The ear's surprise comes from an ear that learnt these works too. A composer the catalogue holds much of is better known to it, so read surprise against composers of the same size.
  - Harmony is measured only where analysts labelled it: 1,868 works by 57 composers, most of them by a few: J. S. Bach (522), Beethoven, Corelli, Couperin, Scarlatti, Grieg, C. P. E. Bach, Mozart, Chopin. Harmony inferred from the notes, for the rest, is not done; it would need its accuracy measured against these labels first, and marking as inferred.
  - Analysts differ: DCML's and When in Rome's labels follow different conventions in places (how a cadential six-four is named, how long a key lasts), so a unit labelled by one is set partly against works labelled by the other.

## Composers' pages (read, not measured)

- **`composers/`**: one page a composer, written by hand from scores read by measurement and from sources: numbered techniques as recipes, walks through whole works, numbers, what the composer does not do, samples in the catalogue, sources. Moved from composer-blend on 23 November 2026, so that everything about a composer is in one place; what composer-blend made from each page stays there.
- A page and a profile share their file name. The profile is generated; the page never is. `composers/README.md` gives the layout and the rules.
- **`composers/INDEX.md`**: every technique of every page under what it works on (melody, harmony, rhythm, texture, form, loudness, colour), to find where two composers might meet. Written by `python3 -m study.composers_index`; a test keeps it in step with the pages.
- **`study/gaps.py`** (`python3 -m study.gaps --blend ../composer-blend`): what has not been made yet, from the pages and from composer-blend's "Tried" lines: what few techniques work on, the techniques no piece has taken, every *Why* by dimension, what the composers do not do. Lists for reading, not a verdict; run again as pages are added. The first reading of them is `checks/gaps-2026-11-25.md`.

## Continuations

`study/continuations.py` proposes ways to carry a line on in a narrow unit's manner, for a draft to choose from: most often an inner voice under a melody and over a bass that are already written.

- **The model:** the listener's ear learnt at three levels at once (the unit's works, the composer's, the whole catalogue's), their predictions joined, and one view more.
  - **The vertical view:** where other lines sound, the note's pitch class above the lowest of them, given that bass's degree and the interval from it to the highest other line. It is the unit's harmony as its lines meet, learnt from its works' lines.
  - Spans a reading plays again are counted once, and editors' copies for MIDI are left out (TRAINING.md, sections 1 and 3).
- **Held out** (`checks/continuations-2026-11-22.md`): 12 units, 6 works each held out, the catalogue level learnt without them (version 25: 13,951 works). Bits a note of pitch, lower is better:

  | | all lines | inner lines |
  |---|---|---|
  | the ear alone (the catalogue) | 2.80 | 2.73 |
  | + the composer's works | 2.73 | 2.66 |
  | + the unit's works | 2.72 | 2.65 |
  | + the vertical view | 2.52 | 2.29 |

  - Rhythm moves less: 1.50 to 1.48 bits a note.
  - The gain is largest where the readings hold real voices: Corelli's trio sonatas 2.84 to 1.95, Bach's chorales 2.86 to 2.36, Palestrina's motets 2.69 to 2.34.
  - It is smallest for keyboard music: Beethoven's early sonatas 2.94 to 2.91, Chopin's Paris dances 2.87 to 2.82. The readings give each hand as one line (its top notes), so there are no inner voices to learn from.
  - The vertical view enters as a product, raised to a weight. A plain geometric mean with the line's prediction made the line worse (2.90); weighed 0.5 it helps everywhere, and weighed 1 it helps inner lines most (2.29 against 2.33).
  - **The levels' vertical views are nested** (since 23 November 2026, `checks/vertical-nested-2026-11-23.md`). Each specific level's counts sit on the prediction of the level above as a prior worth 200 notes. A unit is heard its own way where it has heard much, and mostly as the catalogue hears it where it has heard little.
    - Before, the levels voted equally. Weber's works for voices hold 5 notes over a bass on the lowered second with a third on top, the catalogue 48,000, and his two levels outvoted the catalogue: piece 64b's inner voices set B and E flat against its Neapolitans.
    - Held out, nested: the standing test 2.52 to 2.51 bits a note (inner lines 2.29 to 2.28).
    - Units learnt from 4 works: inner lines 2.55 to 2.48.
    - Every unit heard through Weber's levels: inner lines 2.85 to 2.75.
    - Over piece 64b's Neapolitans, the samples' time on the chord's own notes: 30% to 61%, every one of 24 segments gaining.
    - Corelli, thinly sampled, loses: his readings' doubled bass is a habit the catalogue does not have.
  - **The vertical view's weight, retuned with the nested view** (`checks/vertical-weight-2026-11-23.md`): 0.75 for hearing and for scoring proposals, in place of 0.5 and 1. Held out: all lines 2.49 bits a note, inner lines 2.27 (2.52 and 2.29 with the geometric mean). Drawing proposals keeps 2.
- **Sampling:** a continuation is drawn note by note, within a range and between the lines it must not cross, its time-spans snapped to the durations the unit uses most.
  - It is drawn without the piece's own memory. With it, a line loops on itself: its samples were far less surprising than the unit's real inner voices (2.4 to 2.7 bits a note against 4.2 to 4.4, Bach's chorales and Mozart's quartets), and less consonant.
  - Without it, and with the vertical view weighed double: 3.6 to 4.4 bits a note against the real 4.2 to 4.8; consonant with the outer voices 61% to 70% of the time, against the real 63% to 71%.
  - No parallel fifths or octaves with a line that moves too: they came 3 to 5 times in 100 notes in Bach's and Palestrina's samples, where their own inner voices have almost none.
- **What is proposed:** of many samples, the ones whose surprise (measured with the piece's own memory, as the unit's music is) falls between the 25th and 75th percentiles of the unit's own held-out passages, most different from one another. Neither the most likely, which the critic would call flat, nor noise.
- **Quotation:** each proposal can be checked against the unit's works with score-reader's rule (no more than three intervals in a row with their rhythm). Counted that way, the composers' own held-out passages quote their other works 84% to 100% of the time, and the proposals 59% to 91%. At eight intervals, the real passages 6% to 44%, the proposals 0% to 29%. So, as Philip decided: against the unit, a quote is eight intervals in a row with their rhythm (`quotes_against`); against the works a piece draws on, four, as for any line.

## NotaGen beside the ear

NotaGen (Wang et al., 2025; MIT licence) is a 516-million-parameter model that writes classical scores in ABC notation from a prompt (period, composer, instrumentation). Its weights are not kept here; the scripts that need them run where they are.

- **`study/notagen.py`**: works in NotaGen's notation, made as its own data scripts make them, and cut into patches as its training cuts them; each note's place in the text; each ABC voice aligned to the reading's line.
- **`study/notagen_score.py`** (needs torch and the weights): NotaGen's bits for each prepared note, in one pass a window, checked against NotaGen's own `generate()` with `--verify`.
- **`study/notagen_write.py`** (needs torch, the weights and a NotaGen checkout): a piece from a prompt, with NotaGen's own model and sampling, as ABC, MusicXML and MIDI; with `--sheet`, the sheet music too.
- **`study/sheet.py`** (needs MuseScore): a MusicXML file drawn as sheet music by MuseScore, a PNG a page (or one PDF).
- **`checks/notagen-ear-2026-11-23.md`**: NotaGen's surprise against ours on the same 12,653 notes of 29 held-out works (Bach's chorales, Corelli's and Vivaldi's trio sonatas, Haydn's and Mozart's quartets). On inner lines NotaGen is lower than ours, 1.16 bits a note against 2.32, in 28 of 29 works; its fine-tuned checkpoint, before reinforcement learning, 0.78 (`compare_scores_finetune.json`, from `checks/three-ears-64b-2026-11-23.md`). Its training may hold these works, so this compares the two ears on this music, not how well each generalises. The predictions were written before NotaGen scored; one held, two held in part, one missed.
- **`checks/notagen-writer-2026-11-23/`**: the writer's first piece (Romantic / Chopin, Frederic / Keyboard, seed 1), as ABC, MusicXML and MIDI, and played as written on the Salamander grand (`checks/notagen-writer-2026-11-23.md`).

The Anticipatory Music Transformer (Thickstun, Hall, Donahue and Liang, 2023; Apache 2.0) reads and writes notes in seconds, not scores. Some notes can be given to it ahead of time, so that what it writes knows where they are going: the outer voices, while it hears or writes the inner ones.
- **`study/amt.py`**: notes as AMT's tokens, the given ones interleaved as its training interleaves them (its own code, from a checkout), in windows of 1023 tokens.
- **`study/amt_score.py`** (needs torch and a model): AMT's bits for each prepared note's pitch, given its onset and length.
- **`study/amt_write.py`** (needs torch, a model and the checkout): AMT writing between given notes, with its own `generate()`.
- **`checks/three-ears-64b-2026-11-23.md`**: NotaGen's and AMT's surprise at piece 64b's inner voices, given its tune and bass; whether they would have chosen the proposals we chose; AMT's ear on the 29 held-out works; and AMT writing 64b's inner voices (`amt64.py` plays them). The predictions were written before anything ran.
  - **Our choices:** every outside ear (two NotaGen checkpoints, two AMT models, each AMT with the given notes on the piano or on a second piano) prefers the proposals we chose: mean place 0.29 to 0.31, where 0.5 is chance. They agree with one another (rho 0.37 to 0.94), and ours agrees with none of them. What they hear, and the choices heard, is the harmony as the lines meet.
  - **The held-out works' inner lines:** AMT 0.90 to 1.19 bits a note, NotaGen-X 1.16, NotaGen's fine-tuned checkpoint 0.78, ours 2.32.
  - **64b's own inner voices:** 2.70 to 3.34 to every outside ear; heard by none before.
  - **AMT's writing:** given the tune and bass on a second piano and five bars of history, it writes a part: Large a whole accompaniment (4 notes a second, F1 to B6), Medium 64b's density but with a third of its notes echoing the tune and bass.

Run the tests: `python3 -m pytest -q tests`.
