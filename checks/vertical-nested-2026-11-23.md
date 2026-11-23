# The vertical view nested: a level heard as itself where it has heard much, as the level above where it has heard little

Written on 23 November 2026, on score-reader's catalogue version 25, after piece 64b (*Inside the Mazurka*, composer-blend) drew its inner voices from Weber's works for voices.

## Why

Piece 64b's inner voices were weakest, every time, on the Neapolitan. At its high point (bar 144: the bass on F, the lowered second of E minor, the tune on A), three rounds of alto proposals set D, D sharp, G sharp or B against the F chord.

The vertical view's counts say why:

| level | notes heard | over a bass on the lowered second | that bass with a third on top | its likeliest notes there |
|---|---|---|---|---|
| Weber's works for four voices or more (the unit) | 10,969 | 92 | 5 | B 31%, E flat 26%, A flat 10%, D 10% |
| all of Weber's works (the composer) | 11,403 | 97 | 4 | about the same |
| the catalogue | 17.1 million | 380,661 | 48,145 | A 29%, C 17%, F 15%, D 14% |

- The catalogue hears the F major chord. Weber's five notes hear something else: in his music that bass is a passing chromatic note, not the root of a chord.
- The levels' vertical views were joined by a plain geometric mean, one vote each. Weber's music is two of the three levels, so 5 notes outvoted 48,000.

## The change

`nested()`: the levels' vertical views as one distribution. The most general level is heard as before (its counts by escape method C, down to the bass's degree alone). Each more specific level's counts for the full context (the bass's degree and the interval to the top line) sit on the prediction of the level above as a prior worth `alpha` notes:

    p_level = (counts_level + alpha * p_above) / (notes_level + alpha)

A context a unit has heard 1,000 times is heard its way (with alpha 200, 83% its own). One it has heard 5 times is heard mostly as the catalogue hears it (2% its own).

A second order was tried: a specific level's counts for the bass's degree alone first, then for the full context. It did as well over all notes, and worse where contexts are rare (2.35 to 2.40 bits a note on them, against 2.26 to 2.27), so it is not used.

## Held out

Pitch, bits a note, lower is better. All lines with the vertical view weighed 0.5, inner lines (neither the highest nor the lowest of three or more) weighed 1, as before. "Rare": the notes whose full context the unit's level has heard fewer than 10 times.

**1. The standing test** (`checks/continuations-2026-11-22.md`): 12 units, 6 works each held out, 29,767 notes.

| | all lines | inner lines |
|---|---|---|
| the geometric mean (before) | 2.521 | 2.286 |
| nested, alpha 20 | 2.502 | 2.288 |
| nested, alpha 50 | 2.503 | 2.282 |
| nested, alpha 200 | 2.508 | 2.280 |
| nested, alpha 500 | 2.514 | 2.284 |
| nested, alpha 1,000 | 2.520 | 2.290 |

- The gain is small and widest where readings hold real voices: Corelli 1.950 to 1.886 (alpha 200), Bach's chorales 2.357 to 2.314.
- The keyboard units move by 0.005 or less (Beethoven, Chopin, Joplin, slightly worse).
- These units are large: only 48 of their notes fall in a rare context. This test cannot show what the change is for.

**2. Thin evidence:** the nine units with inner lines, each unit and its composer learnt from 4 of the unit's works only (as Weber's are thin), the same works held out. 24,439 notes; 2,859 in rare contexts.

| | all lines | inner lines | rare | rare, inner lines |
|---|---|---|---|---|
| the geometric mean (before) | 2.608 | 2.549 | 2.751 | 2.881 |
| nested, alpha 20 | 2.609 | 2.567 | 2.713 | 2.678 |
| nested, alpha 50 | 2.609 | 2.510 | 2.726 | 2.663 |
| nested, alpha 200 | 2.618 | 2.477 | 2.739 | 2.677 |
| nested, alpha 500 | 2.626 | 2.478 | 2.743 | 2.685 |
| nested, alpha 1,000 | 2.631 | 2.483 | 2.745 | 2.689 |

- Inner lines gain at alpha 200: Brahms's songs 3.49 to 3.19, Schubert's 2.33 to 2.10, Bach's chorales 2.65 to 2.53.
- **Corelli loses:** 2.13 to 2.33 over all lines. Four of his trio sonatas already teach a habit the catalogue does not have: his readings double the bass in two parts. Leaning on the catalogue unlearns it. A unit whose harmony is truly its own and thinly sampled pays for the change.

**3. Through Weber's ears:** every held-out work of the nine units heard with Weber's two levels (his works, his works for four voices or more) in place of the unit's and the composer's. Music that is not the unit's, as piece 64b's harmony was not Weber's. 24,439 notes; 1,326 in rare contexts.

| | all lines | inner lines | rare | rare, inner lines |
|---|---|---|---|---|
| the geometric mean (before) | 2.783 | 2.849 | 2.976 | 3.254 |
| nested, alpha 20 | 2.813 | 3.022 | 2.899 | 2.926 |
| nested, alpha 50 | 2.785 | 2.883 | 2.886 | 2.857 |
| nested, alpha 200 | 2.768 | 2.747 | 2.876 | 2.821 |
| nested, alpha 500 | 2.765 | 2.692 | 2.873 | 2.815 |
| nested, alpha 1,000 | 2.764 | 2.665 | 2.872 | 2.813 |

- Alpha 200 gains on every unit's inner lines: Brahms's songs 3.82 to 3.52, Haydn's quartets 2.78 to 2.66, Bach's chorales 2.80 to 2.67.
- **A light prior loses here:** alpha 20 does worse than the geometric mean on inner lines (3.02). Weber's two levels are nearly the same works, so nesting them counts his thin evidence twice. Only a heavier prior keeps that in check.
- **The heavier the prior, the better here,** because the music is not Weber's: the less of him, the better it is predicted. In tests 1 and 2, where the music is the unit's own, the gain stops at 200.

**Chosen:** alpha 200, the nested view the default (`Model(vmode='level', valpha=VALPHA)`). It is the best or nearly the best in tests 1 and 2, and takes most of test 3's gain. `vmode='mean'` keeps the geometric mean, to reproduce what was drawn before 23 November 2026.

## Piece 64b's Neapolitans, drawn again

For each four-bar segment whose bass reaches the Neapolitan, 100 continuations of the alto and of the tenor were drawn from the same context as when they were chosen, as proposals are drawn (`SAMPLE`: without the piece's own memory, the vertical view weighed 2). The two segments of variation 2's chain of sevenths are left out: their F is the root of F7, not the Neapolitan. Measured: the share of the samples' sounding time over the Neapolitan that is the chord's own notes (F, A, C in E minor; F flat, A flat, C flat in E flat major).

| segment | bars | voice | the geometric mean (before) | nested, alpha 50 | nested, alpha 200 |
|---|---|---|---|---|---|
| section 1 (the theme) | 6-9 | alto | 11% | 29% | 40% |
| section 1 (the theme) | 6-9 | tenor | 18% | 40% | 36% |
| section 1 (the theme) | 30-32 | alto | 18% | 38% | 44% |
| section 1 (the theme) | 30-32 | tenor | 45% | 78% | 80% |
| section 2 (variations 1-3) | 37-40 | alto | 48% | 77% | 78% |
| section 2 (variations 1-3) | 37-40 | tenor | 22% | 56% | 65% |
| section 2 (variations 1-3) | 45-48 | alto | 35% | 78% | 80% |
| section 2 (variations 1-3) | 45-48 | tenor | 41% | 83% | 84% |
| section 2 (variations 1-3) | 69-72 | alto | 27% | 78% | 81% |
| section 2 (variations 1-3) | 69-72 | tenor | 14% | 41% | 44% |
| section 3 (the slow pair, E flat) | 93-96 | alto | 14% | 30% | 45% |
| section 3 (the slow pair, E flat) | 93-96 | tenor | 14% | 35% | 32% |
| section 3 (the slow pair, E flat) | 101-104 | alto | 33% | 72% | 80% |
| section 3 (the slow pair, E flat) | 101-104 | tenor | 49% | 88% | 86% |
| section 4 (variations 6-8) | 109-112 | alto | 56% | 60% | 62% |
| section 4 (variations 6-8) | 109-112 | tenor | 24% | 49% | 52% |
| section 4 (variations 6-8) | 117-120 | alto | 57% | 59% | 58% |
| section 4 (variations 6-8) | 117-120 | tenor | 21% | 37% | 42% |
| section 4 (variations 6-8) | 141-144 | alto | 38% | 77% | 84% |
| section 4 (variations 6-8) | 141-144 | tenor | 21% | 70% | 74% |
| section 5 (the coda) | 153-156 | alto | 53% | 83% | 85% |
| section 5 (the coda) | 153-156 | tenor | 16% | 40% | 47% |
| section 5 (the coda) | 157-160 | alto | 13% | 37% | 39% |
| section 5 (the coda) | 157-160 | tenor | 21% | 40% | 54% |
| **all 24** | | | **30%** | **57%** | **61%** |

- **Every one of the 24 segments gains** at alpha 200. The smallest gain is where the Neapolitan stands on its fifth or third with the theme in the bass (bars 109-120, the alto: 56% to 62%, 57% to 58%). The old view already heard those positions.
- **At the high point** (bars 141-144), where three rounds of alto proposals were drawn: 38% to 84% (alto), 21% to 74% (tenor).
- **The rest of the time is not all wrong notes.** It includes passing notes, suspensions and the next chord's notes held over, which the chosen voices used too.

## Not checked

- **The vertical view's weight** was tuned with the geometric mean (0.5 for all lines, 1 for inner lines, 2 in sampling) and has not been tuned again with the nested view.
- **How proposals drawn this way sound:** piece 64b is finished and was not drawn again.
