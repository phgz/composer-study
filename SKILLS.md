# Assistant skills

This repository owns the **music-llm-study** skill, for research on composers.
Its maintained source is [SKILL.md](.agents/skills/music-llm-study/SKILL.md).
Claude and GPT-based assistants use the same instructions. The project's other
skills stay in their own repositories: music-llm-compose in `phgz/composer-blend`,
music-llm-render in `phgz/renderer-engine`.

## GPT / Codex

Inside this checkout, Codex discovers the skill under
`.agents/skills/music-llm-study/`; the root `AGENTS.md` points to it. For use
outside the checkout, link that folder into the host's personal skill location
rather than copying it.

## Claude Desktop / Cowork

From this checkout, with Python 3.10 or newer:

```sh
python3 tools/package_skill.py --output /absolute/path/music-llm-study.zip
```

The ZIP holds the skill folder and a dated copy of `README.md` and
`composers/README.md` (the layout and the rules). The pages themselves are not in
it: they change often, and are read from the checkout or from GitHub.
`references/source.json` records the revision and checksums and flags modified
sources. The builder takes only its explicit list of tracked files, refuses
symlinks, never overwrites an existing ZIP, and refuses a package over 200 files
(Claude's upload limit). Commit the intended changes before building.

In Claude, use **Customize → Skills → + Create skill → Upload a skill**, select the
ZIP and enable it, beside music-llm-compose and music-llm-render. Replace it after
the skill or those two documents change: a GitHub update does not refresh it.
