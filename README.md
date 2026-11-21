# composer-study

Measured studies of the composers in score-reader's catalogue, for composer-blend to compose with: profiles of narrow units (a composer in one kind of piece and one period), set against the other composers of the same kind and period, with pointers to the bars that show them; and, later, a listener's ear and continuations trained on the same notes.

- **`TRAINING.md`**: what training reads and what it leaves out (an editor's copy for playing is not the score).
- **`data/periods.json`**: each composer's periods, the second half of a unit (the kind comes from score-reader's `facts`). A work falls in the period whose years hold the year a source states for it, else whose catalogue numbers or title hold it; a work none holds belongs to no period, and its unit falls back to the composer. Each line gives its reason. Written on 21 November 2026 and left to stand: a period that sounds wrong in a piece is corrected here.
- **`study/periods.py`**: reads it (`period_of`). **`study/coverage.py <score-reader>/catalogue`**: how many works the numbers and titles place, composer by composer. Placing by year needs score-reader's facts and is not counted there.
- **`data/eras.json`**: each composer's shared period, the level a narrow unit falls back to after the composer and where the cap of a tenth is counted (`TRAINING.md`, section 4): the sheet's period where the sheet has the composer, else by the year of birth on the sheet's own boundaries. **`study/eras.py`** reads it (`era_of`).

Run the tests: `python3 -m pytest -q tests`.
