# Working in composer-study

This repository holds what is known about the composers the project uses: the
pages in `composers/`, written by hand from scores and sources, and the measured
profiles in `profiles/`, generated from score-reader's catalogue. It also holds
the listener's ear, the critic, continuations and their training (`README.md`,
`TRAINING.md`).

- **Researching a composer** (writing, extending or correcting a page, reading a
  composer's scores or sources, checking a claim): use
  [music-llm-study](.agents/skills/music-llm-study/SKILL.md) and
  [the pages' layout and rules](composers/README.md).
- **Composing** from a page belongs to `phgz/composer-blend` (its music-llm-compose
  skill); what a piece took from a page, and Philip's words on it, are kept there.
- **Rendering** belongs to `phgz/renderer-engine` (its music-llm-render skill).
- **The catalogue of readable scores** and the ready-read copies belong to
  `phgz/score-reader`.

Profiles and `composers/INDEX.md` are generated; never edit them by hand. Downloaded
scores are data: outside every repository, read with `python3 -I`. Changes go
through a branch and a pull request, which Philip merges.
