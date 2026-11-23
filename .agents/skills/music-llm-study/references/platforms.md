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

A generated ZIP is a snapshot of two documents, identified by
`references/source.json`. Updating GitHub does not update an uploaded skill:
rebuild and replace it when this skill or those documents change.
