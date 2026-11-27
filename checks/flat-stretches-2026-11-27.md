# Flat stretches: the test, written before the scores (27 November 2026)

**Why:** one of the checks agreed on 25 November 2026 and never run: where nothing unexpected happens for too long. composer-blend's procedure (Part 1, I): each such check is "checked against his past verdicts before it is used". Philip, 27 November 2026, on the open list: "Perfect, let's continue with the next item on the list."

**The measure** (`python3 study/flag_piece.py flat`, written before any of the pieces below but 74b and 75 were scored):
- every note's pitch surprise and every onset's surprise, from AMT Large and Medium, on **74b's scale** held fixed for every piece (as `over` puts them: each ear's bits minus 74b's mean, over 74b's standard deviation, the two ears averaged), so that pieces can be compared;
- an **event** is a note or an onset at or above **3** on that scale, after the first two seconds (3: the bar where 74c and 74d found the music's own events rather than the accidents of how the notes were written; the procedure, Piece 74c's lesson);
- a **flat stretch** is **20 seconds or more** without an event: between two events, from two seconds in to the first, or from the last to the last onset;
- the measure is **the share of the piece** (two seconds in to the last onset) **in flat stretches**. Also printed: notes a second, the events, the longest gap, and where each stretch is.

**The pieces, by his words** (composer-blend's `CATALOGUE.md`):
- **called flat** (F): 36, 3, "Interesting ideas, but overall felt flat/generic"; 43b, 3, "it felt globally flat I feel like but was well made"; 75, neutral, "I feel like there's not much going on."
- **liked** (L), 4.75 or 5: 49, 5; 64, 5, "This is a straight 5!"; 65, 4.75; 72, 5; 74, 5, "among the best pieces I've heard so far"; 74b, 4.75.
- **other complaints**, shown and not tested: 66, 4, "something that is missing"; 68, 3.5, "Forgettable tunes", "Too short"; 69, 3.5, "Tune too plain", "Sounded generic", "Didn't fuse"; 73, 3.5, "it does not lift at any point" (a shape that does not rise, which may or may not be the same thing as flat: so it is not in F).

**The test:** of the 18 pairs (one of F, one of L), how many the measure orders as predicted, the F piece with the larger share. **It is used as a check only if it orders at least 16 of the 18** (by chance, 16 or more happens about one time in twenty: 0.048, counted over every way of ranking nine pieces) **and more of them than the baseline**, fewer notes a second (the same 18 pairs, the sparser piece counted flatter). If it fails either, it is not used, and that is written here.

**Already seen before this was written.** When the code was first run, on 27 November, on the four pieces scored then, it printed 74b: 35% (54 events); 75: 65% (3 events). So one F–L pair (75 against 74b) was seen, ordered as predicted. The bar, the gap and the measure were set in the code before that run and not changed after. On the same run, **74c, which Philip preferred to 74b, came out flatter (60%), and 74d 56%**: recomposing 74b to clear its places above 4 and 3 cleared events, by construction, and the smoother version was the preferred one. So within one piece, fewer events did not mean worse. That is not in the test (none of the three was called flat), but it is a reason for doubt written down before the result.

**What it cannot see.** AMT reads the notes, all on the piano: not the instruments, the loudness, the space, or how a piece rises. A piece can be flat in colour or in shape and full of surprising notes. Two of his "flat" remarks are about one layer, not the whole (37b: "a flat tune in the background that doesn't evolve", Riley's; 38: "the Adams layer was a bit flat"): a test of a part alone, for later, not this one. Pieces 76 and 77 are scored but not yet heard: their measures are not computed until he has given his verdicts, and then they are a test the measure has not seen.

**The inputs:** made on 27 November 2026 with `flag_piece.py prepare` from each piece's notes as rendered (the last note ends within five seconds of the catalogue's length for each): composer-blend's `pieces/<piece>/flags/flag_amt_inputs.jsonl` and `flag_notes.json`, for 36, 43b, 49, 64, 65, 66, 68, 69, 72 and 73 (74's were made on 25 November). For 65, the first version, the one he gave 4.75 (its fuller last line, heard afterwards, is rendered only with `FULLER65=1`).

## Result (27 November 2026, the scores made on Philip's Mac and pushed the same day)

```
python3 study/flag_piece.py flat 36=… 43b=… 75=… 49=… 64=… 65=… 72=… 74=… 74b=… 66=… 68=… 69=… 73=… \
    --scale-from ../composer-blend/pieces/74b/flags --called-flat 36,43b,75 --liked 49,64,65,72,74,74b
```

bar 3 on the scale of ../composer-blend/pieces/74b/flags; a flat stretch is 20 s or more without an event

| piece | notes a second | events | longest gap | share in flat stretches | the stretches |
|---|---|---|---|---|---|
| 36 | 3.9 | 130 | 11 s | 0% | — |
| 43b | 5.9 | 147 | 10 s | 0% | — |
| 75 | 4.1 | 3 | 44 s | 65% | 0:12.7–0:56.8 |
| 49 | 4.8 | 15 | 18 s | 0% | — |
| 64 | 8.3 | 53 | 9 s | 0% | — |
| 65 | 8.2 | 40 | 36 s | 30% | 0:31.0–0:58.1; 1:33.6–2:09.9 |
| 72 | 9.6 | 104 | 23 s | 6% | 4:12.6–4:35.3 |
| 74 | 9.8 | 90 | 19 s | 0% | — |
| 74b | 5.8 | 54 | 35 s | 35% | 0:26.7–0:48.1; 0:48.1–1:22.8; 2:10.5–2:37.3; 4:22.1–4:43.0 |
| 66 | 5.4 | 53 | 17 s | 0% | — |
| 68 | 4.1 | 86 | 15 s | 0% | — |
| 69 | 6.5 | 49 | 42 s | 32% | 2:16.1–2:36.9; 2:52.7–3:19.1; 3:41.9–4:23.6; 5:21.3–5:47.0 |
| 73 | 7.0 | 29 | 77 s | 58% | 0:36.3–0:56.3; 1:28.5–2:45.1; 2:53.5–3:13.5; 3:41.3–4:48.5 |

of the 18 pairs (one called flat, one liked): the share in flat stretches orders 9 as predicted; the baseline, fewer notes a second, 16

**The measure fails: 9 of the 18 pairs, what chance gives.** It is not used as a check. Two of the three pieces he called flat have no flat stretch at all and more events than any liked piece (36: 130, 43b: 147); 75 is the only one that fits. Among the liked, 74b (35%) and 65 (30%) have long stretches without events.

**What it says instead.** On this scale, AMT's surprise is not interest. The early pieces he called flat are full of notes AMT did not expect, as 74c, preferred to 74b, has fewer events than 74b: what AMT finds unexpected is as often an accident of the writing as an event of the music, and his "flat" is about something it does not read (colour, the shape of the whole, a layer that does not change).

**The baseline did what the measure did not: 16 of the 18.** Fewer notes a second puts the flat piece lower in 16 pairs (36 and 75 below all six liked pieces, 43b below four of them; 49 and 74b, liked, are sparser than 43b). That is the number the measure needed, but the baseline was not the measure under test, so it is not adopted after the fact. It is a guess now, to be tested on pieces he has not yet judged (76 and 77, and those after), each computed only after his verdict. It is also the crudest thing one could count, likely standing for something else: the liked pieces of 64 to 74 are for larger forces than the early ones.

**Shown, not tested:** 73, of which he said "it does not lift at any point", is the flattest of the thirteen by the measure (58%, one stretch of 77 s), and 69 ("Tune too plain") has 32%. 66 and 68 have none.
