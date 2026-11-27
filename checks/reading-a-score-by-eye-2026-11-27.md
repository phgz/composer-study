# Can Claude read a score from its picture? One small test (27 November 2026)

Philip, looking at the score on the walk page: "Can you transcribe a real piece score photo in this notation. How do current models work for the translation?"

**The test.** composer-blend's piece 80 was being written by another session; this session had not read its notes. Its score was drawn (`flag_piece.py score`, MuseScore) and the piano's first eight bars cut out of the page at 300 dots an inch, about what a good phone photo of a page gives. Claude read the picture and wrote down every note (beat, pitch, length), and `reading-a-score-by-eye-2026-11-27/compare_piano_1_8.py` compared the reading with the notes the picture was drawn from (piece 80's `notes80.py` as it stood that afternoon; the script holds the reading).

**The result.** 57 notes in those eight bars of the two piano staves; 57 read right in beat, pitch and length; none read that is not there.

**What it does not show.**
- It is an upper bound: clean computer engraving, two staves, quarter and eighth notes, eight bars, one try. A photo adds skew, shadow and blur; an old edition adds its own engraving; an orchestral page adds a dozen staves.
- At 150 dots an inch, with the whole system of thirteen staves in one picture, the same bars could not be read with confidence (bar 3's voices and the lower notes of the right hand were guesses), and that reading was not scored.
- The chords helped: one doubtful note (bar 2, the right hand's lower voice) was settled by the harmony of the left hand, which is reading, not seeing.
- Published tests of general vision models on whole pages report failure (the sources are in the reply of that day and not copied here); this one small success does not contradict them, since it is neither a page nor a benchmark.

## The same afternoon: is it the eye or the music sense? And does a "calque" help?

Philip: "Can you 'copy (calquer)' the picture, like, you don't try to decipher it right away, you first take the score, then create an image of it, which you can read better. Or I don't know if what you miss is more semantic."

Everything is in `reading-a-score-by-eye-2026-11-27/`: the scripts, each reading as it was written before its comparison ran (`*.read.txt`, and the reading inside `compare_system3.py`), and the answers (`*.truth.json`, which this session did not open). One try each; no reading was changed after its score.

**The eye alone.** Notes drawn at random on one staff, A3 to C6, quarter notes, so that nothing can be guessed from a tune or a chord (`gen.py NAME SEED BARS DPI`; seeds 11 to 15). A different line at each size:

| between two staff lines | notes right of 24 |
|---|---|
| 20.8 px (300 dpi) | 24 |
| 10.4 px (150 dpi) | 24 |
| 6.9 px (100 dpi) | 24 |
| 5.0 px (72 dpi) | 23 |
| 3.5 px (50 dpi) | 16 |

**A photo, and its calque by code.** A page of such notes (seed 21) made to look like a phone photo by `photo.py degrade`: held at an angle, a lamp on one side, a shadow, slightly out of focus, grain, JPEG. Then `photo.py calque`, which reads no note: it finds the tilt from where the ink is, flattens the light, and cuts one line of music a picture.

| what was read | notes right |
|---|---|
| the photo seen whole, 6.9 px between staff lines (bars 1 to 12) | 33 of 48; 14 of the 15 misses one place off, a line taken for a space |
| a second photo (seed 22), one line cut at full size and nothing else (bars 7 to 12) | 20 of 24; the four misses all one place too high |
| the first photo after the calque by code, full size (bars 13 to 24) | 48 of 48 |

The same size drawn clean gave 24 of 24, so the photo's tilt, blur and light cost the eye about a third of the notes; enlarging alone gave back about half of that (on another page, so roughly), with the tilt still pulling every miss the same way; straightening and flattening gave back the rest.

**The eye with the music sense.** Piece 80's third system (bars 37 to 43), all thirteen staves in one picture, 150 dots an inch enlarged by half: 5.5 px of real detail between two staff lines, the kind of picture the first part of this file says "could not be read with confidence". Read once, five staves (`compare_system3.py`): **113 of 114 notes right** in beat, pitch and length (clarinet 62 of 63, violin I 19 of 19, violin II 16 of 16, viola 8 of 8, cello 8 of 8).

How it was read matters more than the count. The violin's tune was recognised from the piano's first bars; the lower strings were checked against the piano's left hand; and of the clarinet's 63 triplet notes the eye gave the contour, and the exact note was mostly chosen among the notes of each bar's chord. The one miss is of that kind: bar 41, sixth note, D5 drawn and E5 read, over an E in the bass. The chord's root was put where the score has its seventh: the likely note in place of the written one.

**What follows.**
- The doubt felt at this size was not a measure: the first part's unscored "could not be read" would probably have scored well. A reading is judged by a comparison, never by how sure it felt.
- What is missing in a poor picture is the eye (a line or the space beside it), not the meaning. A calque made by code gives the eye back.
- A calque made by the reader (redrawing the score) cannot help the reading, since it comes after it; it is a check: the redrawn score laid over the photo shows where the two differ.
- The music sense is what carries a small or crowded picture, and also what produces a wrong note nobody notices, because the wrong note is the plausible one. A composer's page is interested in exactly the notes that are not the plausible ones.

**What it does not show.** The photo is simulated, not a real one; the photo tests have quarter notes on one staff, no chords, no accidentals, no beams; piece 80's harmony is plain and its tune was already known; every count is one try on 24 to 114 notes.
