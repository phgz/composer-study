# What training reads, and what it leaves out

The models here (the listener ear, the continuations) are trained on the notes of score-reader's catalogue. A work that can be drawn is not therefore a clean example of its composer: some readings are an editor's performance copy, not the score. These are the first things training filters on, before any count is made. Written on 21 November 2026, from what score-reader's catalogue version 9 reads; sections 1 to 3 brought to version 24 on 22 November 2026, which marks what they ask for.

Each model records the catalogue version and the score-reader commit it was trained on, and what it left out, so that a later catalogue shows which models to train again.

## 1. The score, not an editor's copy for playing

Many Mutopia works are read from the MIDI copy the editor wrote beside the printed score: a `\score` that only makes MIDI, or Mutopia's own MIDI file for a source that does not compile here. Such a copy can carry notes the composer did not write:
- **Doublings.** BWV 533's fugue, as read, holds 8% notes that are not in the printed score: the editor's copy doubles voices for an organ registration.
- **Ornaments played out.** A copy made with LilyPond's `\articulate` (Mendelssohn's Octet, Satie's *Enfantillages pittoresques*) plays trills and shortens notes.
- **Tracks out of step.** Beethoven's horn sonata: in the copy, the Rondo's right hand comes 1.005 quarters after the left hand and the horn. score-reader reads that movement as printed; others like it may not be known yet.

From catalogue version 24 each work says it (`midi_copy`, in the catalogue and in the ready-read copy's index), on 536 of Mutopia's readings:
- `a \score that only writes MIDI` (385 readings): the main file's closure holds a `\score` with `\midi` and no `\layout`, a copy only for MIDI;
- `a \score that only writes MIDI and \articulate` (24): the copy also plays the ornaments out and shortens the notes (`\articulate` alone, in a printed score, would be marked `\articulate`);
- `Mutopia's own MIDI file` (127): the source does not compile here;
- a movement read as printed by a judgment (`midi` with `printed`: the printed score, played alone) carries no mark: it is kept.

A work read from such a copy is left out of the counts by default. Where that leaves a narrow unit with too few notes, it may be kept with its notes weighted down, and the model says so.

## 2. Notes that are not the composer's

- IMSLP files marked `realized` (Pierre Gouin's organ files: the ornaments played out as notes). Left out of interval and rhythm counts.
- An organ file read with `registration` (16' copies removed) is kept; check a few against a typeset copy before trusting their bass.
- An editor's part already dropped by score-reader (`drop_parts`) stays out.
- Verovio's MIDI of kern files does not play ornaments out (checked for catalogue version 24): a trill, a mordent or a turn is its one written note. The kern readings hold the notes as written.
- CPDL's second archive (Palestrina and Landini, catalogue version 14) marks an edition that is transposed (`transposed`: a motet in high clefs written a fourth or fifth lower) or halves the note values (`halved`). Intervals, scale degrees and rhythm proportions are kept. Absolute pitch and register are not counted for a transposed work; a halved work's lengths are doubled before lengths are counted.

## 3. Repeats counted once

Some readings play the score's repeats and some do not, by how each source is read. From catalogue version 24 every reading of the ready-read copy says which (`repeats`):
- `played`: verovio plays a **kern file's repeats (1,507 of the 7,941 kern readings; 9.6% of the kern notes are a span heard again, 10.5% of the Polish Scores'), and an editor's copy for MIDI that unfolds them plays them (201 Mutopia readings);
- `as printed`: each written bar once, both endings in the order written (LilyPond's MIDI of a printed score, DCML, MusicXML, chant);
- `not known`: Mutopia's own MIDI files and IMSLP's (194).

Where a kern reading plays them, `heard_again` gives the spans that play bars already heard. For counts, a repeated span is counted once: the notes in `heard_again` are left out. A reading `played` with no spans (an editor's copy) or `not known` is already left out of the counts by section 1, or, for IMSLP's files, kept with its notes weighted down where its unit needs it, saying so. For the listener ear, which hears the piece as played, the repeats are kept: a span heard again is what the ear's memory of the piece predicts best, and the ear is judged on it as played.

## 4. Each work once, each composer in proportion

- A work held by two collections counts once (`replaces` in the catalogue). A movement kept from another collection (`also_in`) counts once too.
- The narrow units fall back to the composer, then the period, then everything, where a unit has little to go on. Those shared levels weigh by works: each work's counts are scaled to weigh one, whatever its length.
- No composer weighs more than a tenth of a shared level. Bach has 1,025 of the 2,022 Baroque works in version 14, half the level; held at a tenth, the fallbacks do not drift toward him. What a capped composer gives up is shared among the others by their works. Weighing each composer equally (the rule before 21 November 2026) would make one song of Ethel Smyth's weigh as much as Brahms's 137 works.
- No collection weighs more than a third of a shared level, as no composer weighs more than a tenth of one (Philip, 22 November 2026). The Polish Scores (score-reader's catalogue version 22: 5,949 works by 407 composers, most of them the church music of Polish archives of the 18th and 19th centuries) are by works 48% of the Classical level, 50% of the Romantic and 36% of 1890 to 1950; held at a third, those levels stay the periods' music and do not drift toward one region's archives. In version 22 the cap binds that collection only: the next largest share is the Josquin Research Project's 32% of Before 1600. The catalogue still reads every work, and a composer's own unit keeps all of them; only the shared levels are capped.
- Both caps hold at once: a composer's or a collection's weight is scaled down where it passes its cap, and what it gives up is shared among the others by their works, until neither cap is passed.
- The caps and the version they were applied to are recorded with each model.

## 4a. Who is counted

The shared levels count every composer before 1950 whose scores score-reader's pinned collections hold, drawn or not (Philip, 21 November 2026). That includes the sheet's Set aside composers and composers not on the sheet at all (most of OpenScore Lieder's 107, the Josquin Research Project's others, Mutopia's). A baseline made only of the canon's distinctive composers would make the distinctive look normal: Albinoni and Telemann are the background against which Vivaldi stands out. Their profiles may also show what a composer the sheet set aside for want of knowing her music has of her own.

Not counted: composers after 1950 (under copyright, nearly absent from open collections, and present elsewhere mostly as users' transcriptions and arrangements); anonymous and traditional pieces, which have no composer to weigh (they may enter the "everything" level later, saying so).

## 5. What may be trained on

- "Measure only" (works still under copyright, read but not reproduced): may be counted, for the ear and the profiles; not trained on for continuations without Philip's say.
- Collections whose licence forbids commercial use (ASAP: CC BY-NC-SA 4.0; some CPDL editions, CC BY-NC, named in each work's `licence`): a model trained on them inherits the question. Fine while the project is private; to be looked at before anything is published.
- The quotation check (score-reader `check`) filters every continuation, whatever it was trained on.
