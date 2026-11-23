# Composers: how they work (read, not measured)

One page a composer, written by hand: what was read in the composer's scores by measurement, and what the sources say, as recipes an assistant can compose from. Asked by Philip on 22 November 2026 ("an encyclopedia that builds itself over time") and begun in composer-blend. Moved here on 23 November 2026, so that everything about a composer is in one place: Philip, "yes that's what I had in mind, and the tried section could stay here" (in composer-blend).

- **Beside `profiles/`, not part of it.** A profile is generated from score-reader's catalogue by `study/profiles.py` and is written again with each catalogue version; nothing in it is edited by hand. A page here is written by hand and never generated. The two share their file names: `profiles/john-cage.md` and `composers/john-cage.md` are the same composer (Cage has no profile, since none of his scores is in the catalogue).
- **What composer-blend made from a page** (the pieces, which techniques each took, and Philip's words on them) stays in composer-blend, at `reference/composers/<the same name>.md`. Each page links there. "Piece 64" on a page means composer-blend's piece 64.
- **A page grows** each time its composer is used: a new kind of piece means new reading and a new part of the page.

## What a page holds, in this order

1. **The header:**
   - the composer's name and dates;
   - when the page was begun;
   - **Scope so far:** which kinds of piece it covers (a composer in one kind of piece at one period is the unit), and whether a readable score is in score-reader's catalogue;
   - **Measured profile:** the link to `profiles/`, or why there is none;
   - the link to the pieces that used it.
2. **Techniques**, numbered, by kind of piece (a `###` heading for each kind when there are several). Numbers are never reused, so that a piece can cite them. Each technique gives:
   - a short bold name, then what it is;
   - *How:* a recipe an assistant can follow;
   - *Where:* where it can be heard, by work and bar;
   - at the end, where it comes from: **[score: the work]**, bold, for what was read in a score by measurement; [the source], plain, for what a source says.
3. **Walks through whole works:** what happens, in order, with what the score or the sources give of proportion and time. A list of techniques says what a composer does; a walk says when and for how long.
4. **Numbers:** forces, speeds, lengths, where the loud place sits.
5. **What he or she does not do.** A qualifier, when there is one, is the section's first line ("*In the Notturno.*").
6. **Samples in score-reader's catalogue:** for each technique that a work in the catalogue shows, the work's id, so that the notes can be looked at.
7. **Not checked:** what the writer believes from memory and did not find in a source read for the page. Nothing from memory goes in the sections above.
8. **Sources:** what was actually read, with links.

An empty section says "None yet." (or why it must stay empty), so that a gap shows.

## Rules

- **Research goes by the kind of piece being made** (Philip: "if we're to make a piano trio with Beethoven, then looking at analysis of his piano trios or chamber music in general is a good thing"). A new kind of piece means new reading and a new part of the page.
- **Start from the profile** where there is one: it measures the unit against its contemporaries, which a reading of one work cannot.
- **A piece takes a few techniques, not the list.** Some are picked for what the piece needs (or drawn, when Philip asks for a draw), and the piece names them by number. A long list is a store of possibilities, not a checklist. The sketch of 22 November used seven of Tavener's in a minute, and it sounded like an exercise to the one who wrote it.
- **A page comes from reading done for it.** A page written from memory gives the middle of what is said about a composer, which is what these pages exist to get away from. The writer's own sense of what it already knows is not evidence: on 22 November Claude named the mirror as something it could not have given from memory, and piece 1 had used it eleven days before.
- **Sources are put in the writer's own words.** No passage of a text and no line of a score in copyright is copied.
- **A technique is a recipe, not a guarantee:** whether it sounds like the composer is for Philip's ear.

## What the pages lack (23 November 2026)

- **The recipe form is complete** (23 November 2026; Philip: "we should do it now, otherwise it might drift again and get lost"). All 217 techniques give what they are, *How* and *Where*. A *How* is the writer's recipe from what the score or the source says; a *Where* names only what the score or the source names, and says so when it names no bar. Where a technique is not a technique (a composer's own words, a list of places), its *How* says so.
- **Empty sections:**
  - walks: Cage, Duruflé, Mendelssohn, Rodrigo, Rutter, Tavener, Tchaikovsky, Weinberg, Whitacre;
  - numbers: Tavener;
  - what he does not do: Mendelssohn, Mozart, Tavener, Tchaikovsky;
  - samples: Tchaikovsky (the catalogue holds none of his ballets).

  Composers with no score in the catalogue (Cage, Duruflé, Price, Rodrigo, Rutter, Tavener, Weinberg, Whitacre) cannot have samples or a profile.
