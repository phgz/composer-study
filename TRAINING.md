# What training reads, and what it leaves out

The models here (the listener ear, the continuations) are trained on the notes of score-reader's catalogue. A work that can be drawn is not therefore a clean example of its composer: some readings are an editor's performance copy, not the score. These are the first things training filters on, before any count is made. Written on 21 November 2026, from what score-reader's catalogue version 9 reads.

Each model records the catalogue version and the score-reader commit it was trained on, and what it left out, so that a later catalogue shows which models to train again.

## 1. The score, not an editor's copy for playing

Many Mutopia works are read from the MIDI copy the editor wrote beside the printed score: a `\score` that only makes MIDI, or Mutopia's own MIDI file for a source that does not compile here. Such a copy can carry notes the composer did not write:
- **Doublings.** BWV 533's fugue, as read, holds 8% notes that are not in the printed score: the editor's copy doubles voices for an organ registration.
- **Ornaments played out.** A copy made with LilyPond's `\articulate` (Mendelssohn's Octet, Satie's *Enfantillages pittoresques*) plays trills and shortens notes.
- **Tracks out of step.** Beethoven's horn sonata: in the copy, the Rondo's right hand comes 1.005 quarters after the left hand and the horn. score-reader reads that movement as printed; others like it may not be known yet.

score-reader's status already says how each entry is read: compiled, or Mutopia's own MIDI. It does not yet say whether the file compiled is the printed score or a copy made only for MIDI. Until a work carries that (a field for score-reader to add), training finds it here:
- a main file whose closure holds a `\score` with `\midi` and no `\layout` (a copy only for MIDI);
- `\articulate` anywhere in the closure;
- Mutopia's own MIDI;
- a `midi` judgment with `printed` (the printed score, played alone: kept).

A work read from such a copy is left out of the counts by default. Where that leaves a narrow unit with too few notes, it may be kept with its notes weighted down, and the model says so.

## 2. Notes that are not the composer's

- IMSLP files marked `realized` (Pierre Gouin's organ files: the ornaments played out as notes). Left out of interval and rhythm counts.
- An organ file read with `registration` (16' copies removed) is kept; check a few against a typeset copy before trusting their bass.
- An editor's part already dropped by score-reader (`drop_parts`) stays out.
- Verovio's MIDI of kern files: whether it plays ornaments out is to be checked before training on kern.
- CPDL's second archive (Palestrina and Landini, catalogue version 11) marks an edition that is transposed (`transposed`: a motet in high clefs written a fourth or fifth lower) or halves the note values (`halved`). Intervals, scale degrees and rhythm proportions are kept. Absolute pitch and register are not counted for a transposed work; a halved work's lengths are doubled before lengths are counted.

## 3. Repeats counted once

An editor's copy for MIDI writes its repeats out, so repeated sections count twice. For counts, a repeated span is counted once; for the listener ear, which hears the piece as played, it may be kept, saying so.

## 4. Each work once, each composer in proportion

- A work held by two collections counts once (`replaces` in the catalogue). A movement kept from another collection (`also_in`) counts once too.
- Bach has 1,025 works in version 9, Hildegard 5. The narrow units fall back to the composer, then the period, then everything, where a unit has little to go on. Those shared levels weigh composers equally, or every fallback drifts toward Bach.

## 5. What may be trained on

- "Measure only" (works still under copyright, read but not reproduced): may be counted, for the ear and the profiles; not trained on for continuations without Philip's say.
- Collections whose licence forbids commercial use (ASAP: CC BY-NC-SA 4.0; some CPDL editions, CC BY-NC, named in each work's `licence`): a model trained on them inherits the question. Fine while the project is private; to be looked at before anything is published.
- The quotation check (score-reader `check`) filters every continuation, whatever it was trained on.
