# NotaGen writing (23 November 2026)

**The test:** what NotaGen writes from a prompt, heard as it wrote it.

- **The run:** written on Philip's Mac (M2) with `study/notagen_write.py`.
  - Prompt: Romantic / Chopin, Frederic / Keyboard; seed 1.
  - NotaGen's own sampling: top-k 9, top-p 0.9, temperature 1.2.
  - 137 seconds.
- **The files** (`notagen-writer-2026-11-23/`): the ABC as NotaGen wrote it, the full ABC, MusicXML (NotaGen's `abc2xml.py`) and MIDI.
- **The piece:** 45 bars and an upbeat in 6/8, Andante, quarter = 92.
  - Key: F sharp minor, under a signature of three sharps.
  - It opens pianissimo with a falling semiquaver run over staccato left-hand chords. Its marks run from pp to f.
  - It ends on a held F sharp minor chord.
- **Played** (`notagen_piece.py`, the renderer, Salamander grand) on the piano piece 64b was played on, at 64b's loudness (−19.8 LUFS): 1 minute 36 seconds.
  - **What is played:** its notes, tempo, dynamics, hairpins (and a written "cresc."), accents, staccatos and fermata, as written. Nothing is added: no rubato, no voicing.
  - **The pedal:** NotaGen writes "Ped." four times and never its release. From the first, the pedal is changed on each dotted quarter where a note begins, to the end. That is a pianist's reading of the marks, not NotaGen's.
