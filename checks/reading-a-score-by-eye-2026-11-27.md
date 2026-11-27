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

## The same evening: a real library scan

Philip: "Well why not use the PDFs from the online libraries?" He downloaded Borodin's String Quartet No. 2 from IMSLP (file 644692; 37 pages, each a grey picture of 1465 by 2094 at 300 dots an inch; M. P. Belaieff, Leipzig, plate 1055 at the foot of the page) and attached it. The PDF was kept outside every repository and read as data; it is not copied here.

**What was read.** The first page of the third movement, the Notturno (PDF page 19, printed page 20): five systems of seven bars. `calque_scan.py` straightened it (tilt found: 0.00 degrees), flattened the paper, found 20 staves of 20 from their lines (10.0 px between two staff lines) and cut one system a picture; `zoom.py` enlarged bands of a system 2.2 to 3.3 times. Thirteen pictures were looked at: the page, three systems, nine closer looks. Three of the five systems were read by eye, bars 1 to 7, 15 to 21 and 22 to 28: the opening, the chromatic stretch, and the place where the first violin takes the tune. The reading is `read_notturno.py`, written before the comparison and not changed after (it lists the six places where the picture did not decide alone).

**The result** (`compare_notturno.py`, against score-reader's copy of the movement, OpenScore's edition, ready-read sample 0007): **283 of 283 notes right** in beat, pitch and length, none read that is not there; the seven groups of grace notes the same. The comparison was checked by planting two wrong notes in a copy: it reported both.

**What the count is worth.**
- The 283 notes are about 129 separate decisions (a part, a bar, a pitch): 210 of them are the second violin's and the viola's accompaniment, which repeats one chord four times a bar. The tune and the bass are 73 notes.
- It was not blind. The Notturno is among the best-known quartet movements, and this session had read this very copy of it that morning for piece 81's reading. The notes were no longer before it after the conversation was compacted, but the tune's shape was in its summary, and any reader of music half knows it.
- Six places were settled by something other than the picture (the chord, the cello under it, a neighbouring bar): all six came out right. The music is tonal and regular, which is where music sense agrees with the score. A chromatic or irregular page would test the other case.
- The closer looks were chosen by the reader, bar by bar. A pipeline would have to choose them by itself.
- Two of the page's five systems (bars 8 to 14, 29 to 35; the page holds 480 notes) were not read.
- The scan is a good one: straight, 300 dots an inch, clean plates. A worse scan is untested.

**Cost.** Heavier than was said beforehand ("about the size of what I already did today"): the page holds four times the notes of the afternoon's system, and three fifths of it took thirteen pictures and the longest stretch of reading of the day.

## And the page as a pure black-and-white bitmap, parsed by code

Philip: "Is first putting the image in pure black and white only and then parse the bitmap more efficiently?"

A first, naive try, `bitmap.py` (about a hundred lines): the scan made black and white, staves and barlines found from long runs of ink, only blobs as fat as a filled notehead kept, each given a staff, a bar and a height on the staff. No open noteheads (half notes), no grace notes, no sharps or naturals, no rhythm. Run on the whole Notturno page against the catalogue's copy, after one fix to the barlines:

- 0.13 s for the page;
- 333 of the 429 filled noteheads found at the right staff, bar and height (78%): cello 59 of 65, violin I 32 of 36, viola 179 of 200, violin II 63 of 128;
- 165 heads found that are not in the catalogue (letters of the title and tempo, chords of two notes a third apart split at the wrong heights), 96 missed; one line of the five still has a barline wrong (6 bars found for 7).

So it is cheaper by several orders, and the heights it measures are a measurement, with no expectation in them. What it lacks is everything that is not a height: which blob is a note at all, which notes are one chord, sharps, lengths. Not tested: whether a pure black-and-white picture helps or hurts the eye of the model (its calque kept the greys on purpose, since the grey edge of a notehead is part of what tells a line from a space at small sizes).

## Where it was left

Philip, the same evening: "if it's too costly, let's drop it and focus on composition instead." Nothing was built on these tests and nothing depends on them. What stays usable: when a piece needs a work the catalogue lacks, one page of a clean library scan can be read by eye after the calque by code, at about the cost of the Notturno page above, and the reading says where the picture did not decide alone.
