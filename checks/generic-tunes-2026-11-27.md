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

## Result

Not run yet.
