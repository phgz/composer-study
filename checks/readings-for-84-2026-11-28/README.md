# Readings for composer-blend's piece 84 (28 November 2026)

Piece 84 is D, the tune made of the holes (`checks/untried-way2-2026-11-27.md`), drawn as Bach and Corelli, Duruflé and
Weinberg. These scripts read the scores behind the new parts of Bach's and Corelli's pages; `output.txt` is what they
printed. Duruflé's and Weinberg's readings are from sources only (no score of theirs is in the catalogue).

- `read84.py`: Bach's 22 dances for one instrument (BWV 1002 to 1013: courantes, gigues, bourrées; DCML), each line's even
  rhythm and its runs of two strands; Corelli's eight correnti and four gighe of op. 4 (DCML), the two violins at each
  onset, their rests, the first violin's leaps of a fourth or fifth.
- `schubler.py`: the six Schübler chorales BWV 645 to 650 (Mutopia): the chorale's part, its notes' length, its phrases,
  the share of the time it sounds, and the quick parts in its rests.
- `corelli_gavotta.py`: the Gavotta of op. 4 no. 5 (DCML), its rests bar by bar.

They read the notes as score-reader writes them (`score-reader notes ID -o tsv/<name>.tsv`, part, onset, dur, midi, bar,
beat in quarters) from a `tsv/` folder beside them: `bach_<movement>.tsv` for the dances, `corelli_<movement>.tsv`,
`schubler_<BWV>.tsv`, `corelli_op4n5_gavotta.tsv`. Run with `python3 -I`. The counting rules are each script's heading.
