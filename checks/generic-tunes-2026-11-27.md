# Generic tunes: the test, written before it was run (27 November 2026)

**Why:** one of the checks agreed on 25 November 2026 and never run, "a generic-tune check" ("We can always try"); like each of them, "checked against his past verdicts before it is used" (composer-blend's procedure, Part 1, I). Philip, 27 November 2026, choosing it before the check of whose voice a passage sounds like: "Generic-tune check first".

**The measure** (`checks/generic-tunes-2026-11-27/tunes.py`): a tune is generic when it moves the way the music everyone knows moves. So: how surprising each of its notes is to **the catalogue's ear** (`study/ear.py`, the long-term memory learnt from score-reader's catalogue, version 24: `ear-v24.npz`) **with no short-term memory**, so that a tune is not made less surprising by repeating itself; pitch and rhythm together, in bits, **the mean over its notes**. A low mean is a tune made of the corpus's commonest moves. The keynote the ear needs is the tune's last note.

**The tunes:** each piece's tune as its notes module writes it, one statement, before any variation or accompaniment, so that no choice of part is needed:
- 36: `TUNE_A` (`moves.py`), the theme as first stated;
- 64b: `A_TUNE`, with the two bars that close its first eight (bars 1 to 8, `notes64.py`);
- 66: `TUNE`; 67: `SONG['minor']`, as first sung; 68: `TUNE` (its two phrases); 68b: `TUNE` (a, a', b, c, in that order); 69: `TUNE` (sixteen bars); 72: `TUNE` (the major, first); 74b: `TUNE` (NotaGen's, bars 1 to 15).

**The pieces, by his words** (composer-blend's `CATALOGUE.md`):
- **plain, forgettable or generic** (G): 36, 3, "Interesting ideas, but overall felt flat/generic"; 68, 3.5, "Forgettable tunes"; 69, 3.5, "Tune too plain", "Sounded generic".
- **liked, the tune or the piece** (L): 64b, 4.5, "The theme hold"; 67, 4, "This is much original than anything I've heard on Suno"; 68b, 4.5, "Very interesting piece!" (68's four composers written again); 72, 5; 74b, 4.75.
- **shown, not tested:** 66, 4, "there is something that is missing from making it a 5! Can't pinpoint what exactly."

**The test:** of the 15 pairs (one of G, one of L), how many the measure orders as predicted, the G tune with the lower mean. **It is used as a check only if it orders at least 14 of the 15** (by chance, 14 or more happens 3.6% of the time, counted over every way of ranking eight tunes) **and more of them than the baseline**: the share of the tune's moves that repeat a note or move by a step (two semitones or less), more counted as plainer. If it fails either, it is not used, and that is written here.

**What it cannot see, written before the result.**
- Three tunes against five: only a large difference would show.
- Two of the three G verdicts may not be about the tune: 36's "flat/generic" is about the whole piece; 69's "Sounded generic" may be about its harmony or its scoring, though "Tune too plain" is about the tune.
- The corpus is classical music before 1950. A tune in another manner (72's blue notes, Gershwin's) is less expected there for that reason alone, which counts it less generic: that may be right for his ear or not.
- The flat-stretch test of the same day (`checks/flat-stretches-2026-11-27.md`) and piece 44's measure M0 (the README, `study/rated.py`) found that a model's surprise did not follow his verdicts. This is the same kind of measure, on another question.

## Result (27 November 2026)

```
python3 checks/generic-tunes-2026-11-27/tunes.py ../composer-blend ear-v24.npz
```

| piece | group | notes | bits a note | of which pitch | rhythm | moves of 2 semitones or less |
|---|---|---|---|---|---|---|
| 36 | G | 27 | 5.59 | 4.06 | 1.54 | 50% |
| 68 | G | 27 | 5.06 | 2.95 | 2.12 | 73% |
| 69 | G | 46 | 4.41 | 2.72 | 1.69 | 53% |
| 64b | L | 30 | 5.31 | 3.92 | 1.39 | 55% |
| 67 | L | 29 | 5.00 | 2.42 | 2.57 | 82% |
| 68b | L | 38 | 3.70 | 2.16 | 1.54 | 89% |
| 72 | L | 55 | 5.01 | 3.34 | 1.66 | 57% |
| 74b | L | 47 | 4.32 | 2.94 | 1.38 | 67% |
| 66 | shown | 22 | 4.28 | 2.49 | 1.79 | 71% |

of the 15 pairs (one plain, forgettable or generic, one liked): the bits a note order 4 as predicted; the baseline, more moves of two semitones or less, 3

**The measure fails: 4 of the 15 pairs**, fewer than chance gives on average (7.5). The baseline fails too (3). Neither is used.

**What it shows, not adopted.** The order is nearly the reverse of the prediction: the tunes he liked are, if anything, the more expected ones to the catalogue's ear. 68b's tune, the most expected of the eight (3.70 bits) and the most by step (89% of its moves), belongs to the piece he liked after 68, whose tunes were "Forgettable" (5.06). 36's, the least expected (5.59), is in the piece he called "flat/generic". So what he calls generic or forgettable is not a tune made of the corpus's commonest moves. What it is, this test does not say: the harmony under it, the scoring, how it returns, whether it has one turn to remember it by. A guess drawn from a failed test would be a guess fitted to it, so none is written as a rule.

**With the flat-stretch test of the same day and piece 44's M0:** three tests of a model's surprise against his verdicts, each written before it was run, none passed. What the models' surprise has been good for is local: the flags heard along a piece (74b's four odd places were all among them; 74c, recomposed where AMT was most surprised, was preferred). Measuring a whole piece or a whole tune by it has not followed his ear.
