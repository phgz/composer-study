# The vertical view's weight, retuned with the nested view

Written on 23 November 2026, after the vertical view was nested (`checks/vertical-nested-2026-11-23.md`, prior 200 notes). The weights had been tuned with the geometric mean:
- 0.5 for all lines (`VWEIGHT`);
- 1 for scoring proposals and the unit's own music (`SCORE`);
- 2 for drawing proposals (`SAMPLE`).

The nested view is more reliable where a unit has heard little, so its weights were measured again.

## The weight for hearing: VWEIGHT and SCORE

Pitch, bits a note held out, lower is better; nested, prior 200.

| weight | the standing test: all lines | inner lines | through Weber's levels: inner lines |
|---|---|---|---|
| 0 (no vertical view) | 2.719 | 2.645 | 2.919 |
| 0.25 | 2.578 | 2.431 | 2.725 |
| 0.5 | 2.508 | 2.313 | **2.648** |
| **0.75** | **2.492** | **2.267** | 2.662 |
| 1 | 2.523 | 2.280 | 2.747 |
| 1.5 | 2.704 | 2.436 | 3.079 |
| 2 | 3.023 | 2.725 | 3.557 |

- **The standing test** (12 units, 29,767 notes; inner lines 10,992): 0.75 is best for all lines and for inner lines.
  - For inner lines, 7 of 9 units are best at 0.75, Vivaldi and Bach at 1.
  - The keyboard units (no inner lines) are best at 0.5, by 0.012 bits a note or less.
- **Through Weber's levels** (every unit's inner lines heard with Weber's two levels, music that is not his): 0.5 is best, 0.75 within 0.014. Where the vertical view comes from another style, it is trusted a little less.
- **Chosen: 0.75 for both** (`VWEIGHT`, and `SCORE` now uses it). Against the geometric mean with its old weights, the standing test moves from 2.521 to 2.492 bits a note over all lines, and from 2.286 to 2.267 over inner lines.

## The weight for drawing: SAMPLE

Inner voices drawn under the real outer voices of held-out passages: twelve quarters after four real notes, 25 passages a unit (18 for Bach's chorales), 6 samples each. They are compared with the real passages for:
- consonance with the other voices;
- surprise, scored as proposals are;
- the share falling in the real passages' 25-75% band of surprise, the band proposals are kept in.

Consonance with the other voices:

| | Bach, chorales | Palestrina, motets | Mozart, quartets | Brahms, songs |
|---|---|---|---|---|
| the real inner voices | 71% | 67% | 63% | 63% |
| weight 1 | 62% | 61% | 52% | 58% |
| 1.5 | 65% | 63% | 58% | 62% |
| **2** | 68% | 66% | 59% | 64% |
| 3 | 70% | 68% | 63% | 68% |
| 4 | 72% | 69% | 64% | 69% |

The share falling in the real passages' band, scored as proposals now are (`SCORE`, weight 0.75):

| | Bach, chorales | Palestrina, motets | Mozart, quartets | Brahms, songs | all four |
|---|---|---|---|---|---|
| weight 1 | 38% | 59% | 68% | 23% | 47% |
| 1.5 | 44% | 57% | 66% | 27% | 49% |
| **2** | 37% | 53% | 69% | 25% | 46% |
| 3 | 37% | 51% | 72% | 23% | 46% |
| 4 | 39% | 52% | 69% | 25% | 46% |

Scored as before (weight 1), the same picture: 45% to 46% at weights 1, 1.5, 2 and 4; 43% at 3.

- **Consonance** comes closest to the real voices at 2 or 3: on average 2.3 points away at 2, 1.8 at 3. Bach and Mozart are closer at 3, Brahms at 2, Palestrina the same at both. At 1 the samples are too dissonant by 5 to 11 points, at 1.5 by 1 to 6.
- **The band** barely moves with the weight (46% to 49%, within what 108 to 150 samples a unit can tell apart).
- **Surprise:** the heavier the weight, the less surprising the samples, and they are less surprising than the real voices at every weight. The gap is small for Palestrina (4.43 at 2, against 4.70) and wide for Brahms (4.20 against 5.17).
- **Kept: 2.** Nothing here asks for a change: 3 matches the real consonance a little better, 2 keeps a little more surprise, and the band cannot tell them apart.

## Not checked

- **How proposals drawn this way sound.**
- **The sampled voices' rhythm:** in Mozart's quartets and Brahms's songs they move half again as often as the real ones (about 26 notes in twelve quarters against 17.5), at every weight. That is the rhythm view's doing, not the vertical view's, and is not touched here.
