# Can Claude read a score from its picture? One small test (27 November 2026)

Philip, looking at the score on the walk page: "Can you transcribe a real piece score photo in this notation. How do current models work for the translation?"

**The test.** composer-blend's piece 80 was being written by another session; this session had not read its notes. Its score was drawn (`flag_piece.py score`, MuseScore) and the piano's first eight bars cut out of the page at 300 dots an inch, about what a good phone photo of a page gives. Claude read the picture and wrote down every note (beat, pitch, length), and `reading-a-score-by-eye-2026-11-27.py` compared the reading with the notes the picture was drawn from (piece 80's `notes80.py` as it stood that afternoon; the script holds the reading).

**The result.** 57 notes in those eight bars of the two piano staves; 57 read right in beat, pitch and length; none read that is not there.

**What it does not show.**
- It is an upper bound: clean computer engraving, two staves, quarter and eighth notes, eight bars, one try. A photo adds skew, shadow and blur; an old edition adds its own engraving; an orchestral page adds a dozen staves.
- At 150 dots an inch, with the whole system of thirteen staves in one picture, the same bars could not be read with confidence (bar 3's voices and the lower notes of the right hand were guesses), and that reading was not scored.
- The chords helped: one doubtful note (bar 2, the right hand's lower voice) was settled by the harmony of the left hand, which is reading, not seeing.
- Published tests of general vision models on whole pages report failure (the sources are in the reply of that day and not copied here); this one small success does not contradict them, since it is neither a page nor a benchmark.
