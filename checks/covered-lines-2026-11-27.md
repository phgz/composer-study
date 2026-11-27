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

## Result

Not run yet.
