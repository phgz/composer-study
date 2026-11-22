# Continuations held out: do they expect a unit's music better than the ear, and do their samples sound like it?

Written on 22 November 2026, on score-reader's catalogue version 25 (d37df33), read from the ready-read copy.

## The test

- **Twelve units,** from five centuries and of several textures: Bach's chorales (Leipzig), Palestrina's motets, Josquin's masses, Corelli's and Vivaldi's trio sonatas, Haydn's quartets (mature) and Mozart's (Vienna), Beethoven's early sonatas, Schubert's late songs and Brahms's middle songs, Chopin's Paris dances, Joplin's rags.
- **Six works of each held out** (72; a work with its twins). The catalogue level was learnt without them: 13,951 works, 17.1 million notes, weighted as the ear is. The unit's and the composer's levels were learnt without them too.
- **What is heard:** each held-out work's four longest lines, 150 notes each at most, each with the others sounding (29,767 notes). Inner lines are neither the highest nor the lowest of three or more (10,992 notes).

## Prediction: bits a note of pitch, lower is better

| Unit | the ear | + composer and unit | + the vertical view (0.5) | inner lines: the ear | inner lines: + all (1.0) |
|---|---|---|---|---|---|
| Bach, chorales | 2.86 | 2.67 | 2.36 | 2.99 | 2.22 |
| Palestrina, motets | 2.69 | 2.56 | 2.34 | 2.60 | 2.17 |
| Josquin, masses | 2.45 | 2.30 | 2.15 | 2.41 | 2.06 |
| Corelli, trio sonatas | 2.84 | 2.63 | 1.95 | 2.83 | 1.80 |
| Vivaldi, trio sonatas | 2.95 | 2.92 | 2.70 | 3.14 | 2.64 |
| Haydn, quartets (mature) | 2.66 | 2.61 | 2.45 | 2.64 | 2.33 |
| Mozart, quartets (Vienna) | 2.95 | 2.91 | 2.75 | 2.96 | 2.65 |
| Schubert, songs (late) | 2.21 | 2.20 | 2.09 | 2.05 | 1.91 |
| Brahms, songs (middle) | 3.23 | 3.26 | 3.08 | 3.27 | 2.97 |
| Beethoven, sonatas (early) | 2.94 | 2.94 | 2.91 | | |
| Chopin, dances (Paris) | 2.87 | 2.85 | 2.82 | | |
| Joplin, rags | 3.22 | 3.12 | 3.08 | | |
| **All** | **2.80** | **2.72** | **2.52** | **2.73** | **2.29** |

- The ear here is the catalogue's alone, with the piece's own memory, as `study/heldout.py` measures it.
- The vertical view's weight: 0.5 is best over all lines (2.52; 0 gives 2.72, 0.25 2.59, 1 2.53); 1 is best for inner lines (2.29; 0.5 gives 2.33).
- The first form of the view (the bass's degree alone, joined to the line's prediction by a plain geometric mean) made things worse, 2.90. A geometric mean of two equal predictions halves the sharper one. The product with a weight does not.
- **Rhythm** changes little: 1.50 bits a note with the ear, 1.48 with the composer and the unit.
- **Keyboard music** gains least, because the readings give each hand as one line (its top notes): there are no inner voices to learn the vertical view from.

## Sampling: inner voices drawn under the real outer voices

Twelve quarters after four real notes, between the real lines above and below, 25 passages a unit, 6 samples each. Each sample was scored as the real passage was (pitch and rhythm, with the piece's own memory, vertical weight 1).

| Unit | real: bits a note | real: consonant with the outer voices | sampled with the piece's memory | without it | without it, vertical ×2 |
|---|---|---|---|---|---|
| Bach, chorales | 4.24 | 71% | 2.71, 57% | 3.85, 63% | 3.55, 69% |
| Palestrina, motets | 4.75 | 67% | 4.20, 63% | 4.85, 61% | 4.36, 70% |
| Mozart, quartets | 4.44 | 63% | 2.42, 45% | 4.31, 54% | 4.05, 61% |

- **With the piece's own memory, a line loops on itself.** One Bach sample alternated E and C for four bars at 0.27 bits a note. That is the flatness the critic names.
- **Kept:** drawn without the piece's memory, vertical weighed double, temperature 1. Of these samples, 30% (Bach), 45% (Palestrina) and 63% (Mozart) fall within the middle half of the real passages' surprise.
- **Parallel fifths and octaves** with a line that moves too came 3 times in 100 notes in Bach's sampled inner voices and 5 in Palestrina's, where their real voices have none or almost none (0 and 0.6). They are now forbidden in sampling (`no_parallels`, on by default): 0 and 1.6 in 100 after. Mozart's real inner voices have 2.3; his samples 0.3. (Corelli's readings double the bass in two parts, so this count means nothing for him.)
- **Still unlike the real voices:** Mozart's sampled inner voices move more often than his (23 notes in twelve quarters against 17.5), and Palestrina's less (5.1 against 7.1).

## Quotation

Counted with score-reader's rule against the unit's own works (the samples drawn as proposals are):

| Unit | proposals: 4 intervals | 5 | 6 | 8 | the real held-out passages: 4 | 5 | 6 | 8 |
|---|---|---|---|---|---|---|---|---|
| Bach, chorales | 83% | 57% | 38% | 6% | 100% | 89% | 50% | 6% |
| Palestrina, motets | 59% | 25% | 6% | 0% | 100% | 64% | 48% | 12% |
| Mozart, quartets | 91% | 73% | 59% | 29% | 84% | 76% | 56% | 28% |
| Corelli, trio sonatas | 81% | 47% | 23% | 3% | 100% | 88% | 80% | 44% |

Against a whole unit, four intervals with their rhythm is a composer's idiom, not a quotation: his own passages "quote" his other works more often than the proposals do. The rule was made for the few works a piece draws on (pieces 45 on). Philip's decision (22 November 2026): against the unit, a quote is eight intervals in a row with their rhythm; against the works a piece draws on, four.
