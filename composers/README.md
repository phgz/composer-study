# Composers: how they work (read, not measured)

One page a composer, written by hand: what was read in the composer's scores by measurement, and what the sources say, as recipes an assistant can compose from. Asked by Philip on 22 November 2026 ("an encyclopedia that builds itself over time") and begun in composer-blend. Moved here on 23 November 2026, so that everything about a composer is in one place: Philip, "yes that's what I had in mind, and the tried section could stay here" (in composer-blend).

- **Beside `profiles/`, not part of it.** A profile is generated from score-reader's catalogue by `study/profiles.py` and is written again with each catalogue version; nothing in it is edited by hand. A page here is written by hand and never generated. The two share their file names: `profiles/john-cage.md` and `composers/john-cage.md` are the same composer (Cage has no profile, since none of his scores is in the catalogue).
- **What composer-blend made from a page** (the pieces, which techniques each took, and Philip's words on them) stays in composer-blend, at `reference/composers/<the same name>.md`. Each page links there. "Piece 64" on a page means composer-blend's piece 64.
- **A page grows** each time its composer is used: a new kind of piece means new reading and a new part of the page. A composer drawn again gets new reading before the piece is composed, even when the page seems enough (Philip, 24 November 2026).

## What a page holds, in this order

1. **The header:**
   - the composer's name and dates;
   - when the page was begun;
   - **Scope so far:** which kinds of piece it covers (a composer in one kind of piece at one period is the unit), and whether a readable score is in score-reader's catalogue;
   - **Measured profile:** the link to `profiles/`, or why there is none;
   - the link to the pieces that used it.
2. **Techniques**, numbered, by kind of piece (a `###` heading for each kind when there are several). Numbers are never reused, so that a piece can cite them. Each technique gives:
   - a short bold name, then what it is;
   - *Works on:* one or more of melody, harmony, rhythm, texture, form, loudness, colour (or background, for an entry that is not a technique), which is how the index finds it;
   - *Why:* only where a source says it or a score shows it: what the technique does in the composer's music (what it holds still, what it makes the other parts do, where it leads), or the composer's own stated reason. It ends with its own mark, as *Where* does, and then, in italics, who is speaking: *(his words)* or *(her words)*, the composer's own; *(an analysis)*, a writer reasoning from the notes or the life; *(from the score)*, what the reading of the score shows; *(a listener)*, someone (a player too) saying how it comes across. Two voices are named when the line holds both, the main one first. Which counts most depends on the question: for what the composer aimed at, the composer's words; for what it does in the notes, an analysis or the score, the only ones that can be checked against the notes; for how it comes across, a listener, which is evidence of an effect and not the composer's reason. Where neither a source nor a score gives one, there is no *Why*: a guess at a composer's purpose is what these pages keep out. A *How* without a *Why* is the case that came out as film music in composer-blend's piece 65 (Duruflé's close, from one sentence and no score): the chords were his, what they were for was not on the page;
   - *How:* a recipe an assistant can follow;
   - *Where:* where it can be heard, by work and bar;
   - at the end, where it comes from: **[score: the work]**, bold, for what was read in a score by measurement; [the source], plain, for what a source says.
3. **Walks through whole works:** what happens, in order, with what the score or the sources give of proportion and time. A list of techniques says what a composer does; a walk says when and for how long.
4. **Numbers:** forces, speeds, lengths, where the loud place sits.
5. **What he or she does not do.** A qualifier, when there is one, is the section's first line ("*In the Notturno.*").
6. **Too well known to borrow:** the composer's themes and figures that a listener recognises at once, from sources that say they are famous. A piece does not take them as techniques, even moved to another key (composer-blend's piece 67 first took Rachmaninoff's three-note toll from his best-known prelude).
7. **Samples in score-reader's catalogue:** for each technique that a work in the catalogue shows, the work's id, so that the notes can be looked at.
8. **Not checked:** what the writer believes from memory and did not find in a source read for the page. Nothing from memory goes in the sections above.
9. **Sources:** what was actually read, with links.

An empty section says "None yet." (or why it must stay empty), so that a gap shows.

**The index.** `INDEX.md` lists every technique of every page under what it works on, so that two composers can be read side by side on one dimension. It is written by `python3 -m study.composers_index` from the "Works on" lines and is never edited by hand; a test fails when a technique has no such line or the index is out of date.

## Rules

- **Research goes by the kind of piece being made** (Philip: "if we're to make a piano trio with Beethoven, then looking at analysis of his piano trios or chamber music in general is a good thing"). A new kind of piece means new reading and a new part of the page.
- **Start from the profile** where there is one: it measures the unit against its contemporaries, which a reading of one work cannot.
- **A piece takes a few techniques, not the list.** Some are picked for what the piece needs (or drawn, when Philip asks for a draw), and the piece names them by number. A long list is a store of possibilities, not a checklist. The sketch of 22 November used seven of Tavener's in a minute, and it sounded like an exercise to the one who wrote it.
- **A page comes from reading done for it.** A page written from memory gives the middle of what is said about a composer, which is what these pages exist to get away from. The writer's own sense of what it already knows is not evidence: on 22 November Claude named the mirror as something it could not have given from memory, and piece 1 had used it eleven days before.
- **Sources are put in the writer's own words.** No passage of a text and no line of a score in copyright is copied.
- **A technique is a recipe, not a guarantee:** whether it sounds like the composer is for Philip's ear.
- **A *Why* says what the notes or the source show, not how it sounds.** From a score: what the device does to the other notes (every chord of the hymn sits on the same bass; the tune never moves while the strings do), measured. From a source: what it says the device is for, in the writer's words. Neither is a promise of an effect on a listener.

## What the pages lack (23 November 2026)

- **The recipe form is complete** (23 November 2026; Philip: "we should do it now, otherwise it might drift again and get lost"). All 217 techniques of that day, and the 61 added for composer-blend's piece 68 (Tavener's 12 to 22, and the new pages of Rimsky-Korsakov, Glière and Desplat), give what they are, *How* and *Where*. A *How* is the writer's recipe from what the score or the source says; a *Where* names only what the score or the source names, and says so when it names no bar. Where a technique is not a technique (a composer's own words, a list of places), its *How* says so.
- **A *Why* on 145 of the 278 techniques** (23 November 2026; Philip agreed to it as an optional line, from a source or a score only). The figures that follow are for the first 101, on the 217 techniques before piece 68's pages. Every source cited by a technique was read again for it, as far as the pages could be fetched (the long theses only in their first part). 92 come from sources, 9 from the scores. By voice (23 November 2026): 13 hold the composer's own words, 79 an analysis, 9 the score, 7 a listener. The rest have none because the source describes and does not say what for, or the score shows nothing beyond the *How*; a background entry never has one. Fewest on the pages written mostly from scores (Rameau 2 of 16, Mozart 3 of 10, Borodin 3 of 10, Dvořák 3 of 11, Mendelssohn 3 of 8): a score shows what the notes do, rarely what for.
- **Empty sections:**
  - walks: Cage, Desplat, Duruflé, Mendelssohn, Rodrigo, Rutter, Tchaikovsky, Weinberg, Whitacre;
  - numbers: Tavener;
  - what he does not do: Glière, Mendelssohn, Mozart, Tchaikovsky;
  - samples: Tchaikovsky (the catalogue holds none of his ballets).

  Composers with no score in the catalogue (Cage, Desplat, Duruflé, Glière, Price, Rodrigo, Rutter, Tavener, Weinberg, Whitacre) cannot have samples or a profile. Rimsky-Korsakov's few readable works (piano pieces, an aria) are not of the kind his page covers.
