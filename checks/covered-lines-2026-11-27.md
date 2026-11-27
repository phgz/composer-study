# Covered lines: an orchestration check, written before it was run (27 November 2026)

**Why:** the last of the checks agreed on 25 November 2026 and never run, "an orchestration check" ("We can always try"). After three tests of a model's surprise against his verdicts failed (piece 44's M0, `flat-stretches-2026-11-27.md`, `generic-tunes-2026-11-27.md`), Claude proposed it only in a local form, on the rendered sound and not the notes: the places where the line meant to lead is covered by the rest, as flags to hear along, as AMT's are. Philip, 27 November 2026: "Let's do orchestration".

**What it is checked against.** His words name one covered line: 74b's last hymn, place 28 (4:08). Take 3: "The problem is the voice."; take 4: "I think the problem in the voice is in the how it drops from high to low."; take 5, where the voice no longer falls: "Now it sounds fine!" (composer-blend's `pieces/74b/README.md`). Takes 2 and 3 have the same voice notes there; the README measured the voice 6 to 10 dB under the band on its B4 and A4 in takes 3 and 4. Nothing else he has said names a line he could not hear. So this is a test the measure must pass before it is tried, not evidence that it works; the test that counts is the next one, below.

**The measure** (`study/covered.py`, from a render's own stems, `EXPORT_MIX_STEMS`):
- the foreground is the part or parts a window names (the pieces' `look` scripts write them for the renderer's `tools/check_balance.py`), the rest is every other stem;
- frames of 2048 samples (46 ms), every 1024; each frame's power spectrum, the two channels' powers averaged;
- the 24 critical bands (Zwicker's edges, 0 Hz to 15.5 kHz); the rest's energy in each band spread to the others, falling 25 dB a band below it and 10 dB a band above it (a sound masks higher pitches more than lower ones), summed, then 6 dB down: the masked threshold;
- the foreground is heard in a band where its energy is over that threshold; **its audible share** in a frame is the part of its energy in such bands;
- a frame is **covered** when the audible share is under 25%; a frame where the foreground is more than 40 dB under its loudest in the window is silence and not counted;
- a **covered stretch** is 0.5 s or more of covered frames (two frames or less between them bridged).
- Beside it, the renderer's kind of measure as a baseline: the foreground's broadband energy against the rest's, in the same frames; covered when 6 dB or more under, for the same 0.5 s.

**The test, before anything is measured:**
1. 74b, the voice, from 247.0 to 252.0 s (score time; the B4 and A4 of takes 2 to 4, the G sharp and A of take 5): **a covered stretch in takes 2, 3 and 4, and none in take 5.**
2. 74b take 5, the voice, from 240.6 to 247.4 s (its three A5s, which the README measured 13.7, 9.2 and 3.3 dB under the band by broadband medians, and which he did not complain of): **no covered stretch.**

If the measure gets both, it goes on to the real test. If not, it is not used. The baseline is scored on the same two: if it gets both too, the spectral measure adds nothing here.

3. **The real test, on a piece he has not heard:** its flags (every covered stretch of a leading line) given to him with the render, to hear along and tick. It is kept as a check if he hears at least half of them as covered or unclear; otherwise not. What it misses he can add as his own points, as on the walk pages.

**What it cannot see.** A line can be heard and still be wrong (74b's voice was also late and slid); a line can be covered on purpose; a masking model this simple is a rough ear (no level dependence, no temporal masking, the room taken as the stems give it).

## Result (27 November 2026, run on the stems of 74b's takes 2 to 5 on Philip's SSD, `rendered_pieces/74b/`)

```
python3 study/covered.py take-N/tune_and_hymn.render.json --map "/Volumes/Music Libraries/rendered_pieces=<the SSD here>" \
    --window "the fall:247.0:252.0:voice"            (and for take 5: --window "the three A5s:240.6:247.4:voice")
```

| | the fall, 247 to 252 s: audible share (median) | broadband, voice over the rest (median) | covered stretches | baseline (6 dB under) |
|---|---|---|---|---|
| take 2 | 93% | −6.6 dB | none | 4:08.0–4:08.7; 4:10.3–4:12.0 |
| take 3 | 94% | −6.6 dB | none | 4:08.0–4:08.7; 4:10.3–4:12.0 |
| take 4 | 93% | −7.4 dB | none | 4:07.1–4:08.6; 4:10.0–4:12.0 |
| take 5 | 99% | −4.0 dB | none | none |
| take 5, the three A5s, 240.6 to 247.4 s | 98% | −8.2 dB | none | 4:00.6–4:05.2 |

**The measure fails the first test:** it finds no covered stretch where he heard the problem (takes 2, 3 and 4). It gets the second right (take 5's A5s are not covered). It is not used, and the real test (3) is not run.

**The baseline gets the first and fails the second:** 6 dB under the band at the fall in takes 2 to 4 and not in take 5, but also under for four and a half seconds at take 5's A5s, which he did not complain of. Neither passes both.

**What the measure says instead, not adopted.** By its reckoning the voice stayed heard through its fall in takes 2 to 4 (93 to 94% of its energy over the threshold), though 6 to 7 dB under the band overall: high enough in pitch, away from where the band's energy was. His own words on take 4 put the problem in "how it drops from high to low", and the README's stems show it late and sliding. So the one place his words name may not have been a covered line at all. That reading came after the result, so the rule stands.

**It is not blind.** On take 5's last hymn (220 to 245 s) it finds the guitar, the cellos and the piano's accompaniment covered in places (eight, four and nine stretches), fewer than the baseline does. There is simply no covered line in his words to test it against.
