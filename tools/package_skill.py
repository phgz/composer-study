"""Build a portable skill ZIP from an explicit list of tracked public files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

SKILL = "music-llm-study"
REPOSITORY = "https://github.com/phgz/composer-study"
# The two documents that hold the layout and the rules. The pages themselves change often and are read
# from the checkout or from GitHub, not from a dated copy.
DOCUMENTS = ["README.md", "composers/README.md"]
SKILL_FILES = ("SKILL.md", "references/platforms.md", "agents/openai.yaml")
MAX_FILES = 200  # Claude's skill upload refuses a ZIP of more files


def git(repo, *args):
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], stderr=subprocess.PIPE
    ).decode().strip()


def package(repo, output, *, skill=SKILL, documents=DOCUMENTS):
    repo = Path(repo).resolve()
    output = Path(output).expanduser()
    prefix = Path(".agents/skills") / skill
    sources = [(prefix / p, f"{skill}/{p}") for p in SKILL_FILES]
    sources += [(Path(p), f"{skill}/references/repository/{p}") for p in documents]
    if len(sources) + 1 > MAX_FILES:
        raise ValueError(f"The package would hold {len(sources) + 1} files; Claude's upload accepts {MAX_FILES}.")
    payload = {}
    records = []
    for relative, destination in sources:
        path = repo / relative
        if not path.is_file() or path.is_symlink() or path.resolve() != path:
            raise ValueError(f"Expected a regular in-repository source: {relative}")
        git(repo, "ls-files", "--error-unmatch", "--", relative.as_posix())
        data = path.read_bytes()
        payload[destination] = data
        records.append({
            "source": relative.as_posix(),
            "archive": destination,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })
    revision = git(repo, "rev-parse", "HEAD")
    modified = bool(git(repo, "status", "--porcelain", "--untracked-files=no",
                        "--", *(str(p) for p, _ in sources)))
    manifest = {
        "schema": 1, "skill": skill, "repository": REPOSITORY,
        "revision": revision, "included_sources_modified": modified,
        "files": records,
        "note": "Documentation snapshot; prefer the current accessible checkout.",
    }
    payload[f"{skill}/references/source.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode()
    # Exclusive creation protects previously delivered installation packages.
    # No filesystem walk: samples, presets, captures, and unrelated files are excluded.
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(payload.items()):
                item = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                item.compress_type = zipfile.ZIP_DEFLATED
                item.external_attr = 0o100644 << 16
                archive.writestr(item, data)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New ZIP filename; existing files are not overwritten")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    manifest = package(repo, args.output)
    print(f"{args.output}: {manifest['skill']}, {len(manifest['files'])} source files, "
          f"revision {manifest['revision'][:12]}"
          + (" (modified sources)" if manifest["included_sources_modified"] else ""))


if __name__ == "__main__":
    main()
