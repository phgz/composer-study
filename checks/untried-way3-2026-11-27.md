# A technique no composer has tried: the third way, a rule from outside music (27 November 2026)

**Why:** Philip's question, the third of the three ways (the first, `untried-2026-11-27.md`, gave piece 79, neutral "with potential"; the second, `untried-way2-2026-11-27.md`, gave D and E, left open). Philip, 27 November 2026, quoting how the way was offered: "A process from outside music. For example a rule from mathematics or programming that structures a piece, as canons and isorhythm once did, but one no source mentions. This is the most likely to be truly new and also the most likely to come out as a demonstration rather than music. Piece 75 showed that risk."

**What piece 79 adds to that risk.** Philip, of 79: "the focus was more on the technique than on the music itself, but it could be integrated elsewhere." So each candidate below says what the listener hears and how it can sit inside a piece whose tune stands by itself, not be the piece.

## Where to look: mathematics is taken, programming much less

- **Mathematics has been mined.** Tom Johnson's *Rational Melodies* (1982) explore "accumulation, counting, and isorhythm"; *Music for 88* (1988) "applied ideas of Eratosthenes, Euler, Mersenne and Blaise Pascal" (Wikipedia, "Tom Johnson (composer)"); his *Self-Similar Melodies* (1996) covers "finite and infinite automata, the paper-folding formula, self-replicating melodies" (the publisher's description). Add Xenakis's sieves, Nørgård's infinity series and change ringing, and a mathematical rule proposed here would most likely have a precedent.
- **Programming's rules turn up as hidden generators.** Backtracking search writes counterpoint or fills a constraint solver's music (Bemman and Meredith, ISMIR 2019; Varga, TU Delft 2024; a student paper on first-species counterpoint by depth-first search), but the search is not heard: only its answer is. Version control appears as a tool for composers working together (a Cardiff project on merging differences "while preserving musical semantics"; SHARP, version control in live coding, Creativity and Cognition 2024), not as a form. The candidates below make a rule from programming audible as the form. Philip is a software engineer; these are rules he knows from inside.

## Candidates

### F. The merge

- **The rule:** version control's three-way merge. Two versions made apart from one ancestor are reconciled by looking at what each changed: "The three-way merge looks for sections which are the same in only two of the three files" (Wikipedia, "Merge (version control)"). Where only one side changed a passage, its change is taken; where both changed the same passage differently, there is a conflict, which a person resolves.
- **What is heard:** a tune that stands by itself (the ancestor); a variation of it in one colour's manner, then another in the other colour's, made apart; then the merge, played: in the bars only one colour changed, its change; in the bars both changed, the conflict, both versions at once, until one gives way or a third resolves them. The two colours act on each other by the rule, and the listener who has heard the three can follow which side each bar came from.
- **The nearest found:** Hirata, Tojo and Hamanaka, "Algebraic Mozart by Tree Synthesis": new variations of Mozart's K. 265/300e made from existing ones by "join" and "meet" on their time-span trees (Lerdahl and Jackendoff's reduction), noting that in a join "two or more pitch events may occupy the same position on a score in a conflicting way" (the JAIST repository's abstract). Two variations combined, by an algebra on reductions, as research; not a three-way merge against the theme, and the conflict is resolved away, not heard.
- **Not found** in two searches (a three-way merge of variations as a musical form; the nearest, join and meet of variations).
- **What could go wrong:** the listener has to hold three versions in mind; the merged bars may sound like a medley of the two variations, and the conflicts like a mess.

### G. The search, heard

- **The rule:** depth-first search with backtracking. A tune is to be found that meets a rule (for example, reaching its last note without repeating an interval, or fitting another part's chords at every note); it is built a note at a time, and at a dead end the search goes back to the last choice it made and takes the next.
- **What is heard:** the search itself. Each attempt plays until it is stuck (a phrase stopping on a clash, or a held note with nowhere to go); then the music goes back to the last choice point, the passage up to there heard again, and goes on differently. A shallow dead end is a short return, a deep one a long return. At the end the tune that meets the rule, whole for the first time.
- **The nearest found:** first and second endings, the oldest form of going back and going on differently; backtracking as a hidden generator (above).
- **Not found** in two searches (a form made of a backtracking search the listener hears; returns and retries).
- **What could go wrong:** it is the most likely of the three to be a demonstration: a piece about failing, its returns tedious unless each failure is an event worth hearing.

### H. The deadlock

- **The rule:** Dijkstra's dining philosophers (1965): five sit at a round table, each pair of neighbours sharing a fork, and each needs both its forks to eat; if all take their left fork at once, none can go on: deadlock, "a system state in which no progress is possible" (EPFL Graph Search, on the problem). Its solutions (Wikipedia names a "resource hierarchy solution" among them) keep the jam from forming.
- **What is heard:** five players in a ring share five notes, each note between two neighbours; a player's phrase needs both its notes, and a note one player holds the next cannot play. The turn-taking around the ring comes from the rule; when all five take a note at once, the five notes are held together and nothing moves: the deadlock is a chord nobody chose, held, until one player gives its note back and the ring moves again. The composer chooses the five notes, so the deadlock chord can be the piece's arrival.
- **The nearest found:** the hocket (on the pages: Monk 12), one line divided among voices; nothing musical in a search for the dining philosophers in music.
- **Not found** in one search (the dining philosophers or deadlock as a rule for a piece).
- **What could go wrong:** the rule's states may be heard only as rests and held notes; the jam has to build so that the held chord is an event, not a stall.

## Claude's lean

F, for what 79 taught: its tune stands by itself (the ancestor), and the rule is how the two colours of a blend act on each other, which is what the project's pieces already do. G is the most likely to be new and to be a demonstration. H gives a single strong event (the deadlock chord) that a piece could be built toward.

## Sources

- Wikipedia, "Tom Johnson (composer)"; Two-Eighteen Press's description of *Self-Similar Melodies* (sheetmusicplus.com)
- Wikipedia, "Merge (version control)"
- Keiji Hirata, Satoshi Tojo and Masatoshi Hamanaka, "Algebraic Mozart by Tree Synthesis" (JAIST repository, hdl.handle.net/10119/12338): the abstract only
- Brian Bemman and David Meredith, "Backtracking search heuristics for solving the all-partition array problem", ISMIR 2019; Pál Patrik Varga, "Exhaustive Backtracking in Hierarchical Wave Function Collapse for Procedural Music Generation", TU Delft 2024; Rayhan Hanif Maulana Pradana, "Possible Voice Leadings Generation of First-Species Counterpoint with Depth-First Search and Backtracking" (ITB): the search excerpts only
- Cardiff University, a project description on version control for collaborative composition (pats.cs.cf.ac.uk), and Manesh, Bowman and Lee, "SHARP: Exploring Version Control Systems in Live Coding Music" (2024): the search excerpts only
- Wikipedia, "Dining philosophers problem"; LMU's notes on the problem (Dijkstra, 1965); EPFL Graph Search, "Dining philosophers problem": the search excerpt only
- composer-study's pages: Monk 12
