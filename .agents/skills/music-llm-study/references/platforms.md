# Where the study runs

The instructions are shared by Claude and GPT-based assistants. They grant no
filesystem access and install nothing.

- **A cloud session** can hold checkouts of composer-study, score-reader and
  composer-blend in its own workspace, fetch web sources, and run score-reader there.
  score-reader's data folder lives outside every repository.
- **A session linked to Philip's Mac** can also read the folders he connected. His
  Mac keeps a ready-read copy of the catalogue; check its version in its
  `index.json` before relying on it. Say which place a command ran in.
- **Without a checkout**, read the pages and the profiles on GitHub
  (`phgz/composer-study`) and prepare the change as text for a pull request. Never
  write a page from memory or from this package's dated copies.

Philip's terminal on his Mac runs fish (Philip, 27 November 2026). A command he
types himself is written for fish: `set F value`, not `F=value`; a loop is
`for x in a b ... end`; `VAR=value command` works (fish 3.1 and later). AMT's
weights are on his Music Libraries SSD, `/Volumes/Music Libraries/models/`.

A generated ZIP is a snapshot of two documents, identified by
`references/source.json`. Updating GitHub does not update an uploaded skill:
rebuild and replace it when this skill or those documents change.
