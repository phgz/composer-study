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

## Result

Not run yet: the scores are made on Philip's Mac.
