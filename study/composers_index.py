"""The index of the composers' pages: every technique of every page in `composers/`, by what it works on, so that two
composers can be set side by side on one dimension (where they might meet) without reading both pages end to end.

The index is written from the pages and is not edited by hand. Run after changing a page:
    python3 -m study.composers_index            # writes composers/INDEX.md
    python3 -m study.composers_index --check    # says whether composers/INDEX.md is up to date (exit 1 if not)
"""
import argparse, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, 'composers')
INDEX = os.path.join(PAGES, 'INDEX.md')
# What a technique can work on. "background" is for an entry that is not a technique: the composer's words, a list of works.
DIMENSIONS = ('melody', 'harmony', 'rhythm', 'texture', 'form', 'loudness', 'colour', 'background')
MEANING = {
    'melody': 'the tune: its notes, steps and leaps, its range',
    'harmony': 'chords, modes and keys, the bass under them',
    'rhythm': 'note values, metre, accents, speed',
    'texture': 'how many lines, who has the tune, who accompanies and how',
    'form': 'sections, their order and length, returns, beginnings and endings',
    'loudness': 'levels, swells, where the loud place is',
    'colour': 'instruments and voices, register, the way of playing',
    'background': 'not a technique: what the composer said, where the works are',
}


def pages(folder=PAGES):
    """(slug, composer, [(number, name, [dimensions], kind)]) for every page, kind being the ### heading it stands under"""
    out = []
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.md') or f in ('README.md', 'INDEX.md'): continue
        text = open(os.path.join(folder, f), encoding='utf-8').read()
        composer = re.match(r'# (.+?)(?: \(|$)', text).group(1)
        a = text.index('## Techniques\n'); b = text.index('\n## ', a + 1)
        kind = None; items = []
        for block in re.split(r'(?m)^(?=\d+\. |### )', text[a:b])[1:]:
            if block.startswith('### '):
                kind = block[4:].split('\n', 1)[0].strip(); continue
            number = int(block.split('.', 1)[0])
            first = block.split('\n', 1)[0]
            m = re.match(r'\d+\. \*\*(.+?)\*\*', first) or re.match(r'\d+\. \*(.+?)\*', first)
            name = re.sub(r'[*]', '', m.group(1)).strip().rstrip('.:,') if m else first[:60]
            w = re.search(r'(?m)^ {3,4}\*Works on:\* (.+?)\.?\s*$', block)
            dims = [d.strip() for d in w.group(1).split(',')] if w else []
            items.append((number, name, dims, kind))
        out.append((f[:-3], composer, items))
    return out


def problems(found):
    """what is wrong with the tags: a technique with none, or with a word that is not a dimension"""
    bad = []
    for slug, _, items in found:
        for number, name, dims, _ in items:
            if not dims: bad.append(f'{slug} {number}: no "Works on" line')
            for d in dims:
                if d not in DIMENSIONS: bad.append(f'{slug} {number}: "{d}" is not one of {", ".join(DIMENSIONS)}')
    return bad


def render(found):
    lines = ['# Index of the composers\' pages, by what each technique works on', '',
             'Written by `study/composers_index.py` from the pages\' "Works on" lines; do not edit it by hand. '
             'A technique can work on more than one thing and is listed under each. To look for where two composers '
             'might meet, read their rows under the same heading. The numbers are the pages\' own.', '']
    counts = {d: sum(1 for _, _, items in found for _, _, dims, _ in items if d in dims) for d in DIMENSIONS}
    lines += [' · '.join(f'[{d}](#{d}) ({counts[d]})' for d in DIMENSIONS), '']
    for d in DIMENSIONS:
        lines += [f'## {d}', '', f'*{MEANING[d]}*', '']
        for slug, composer, items in found:
            mine = [(n, name, kind) for n, name, dims, kind in items if d in dims]
            if not mine: continue
            refs = '; '.join(f'{n}. {name}' + (f' ({kind})' if kind else '') for n, name, kind in mine)
            lines.append(f'- **[{composer}]({slug}.md):** {refs}')
        lines.append('')
    return '\n'.join(lines).rstrip('\n') + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--check', action='store_true', help='say whether composers/INDEX.md is up to date; write nothing')
    a = ap.parse_args(argv)
    found = pages(); bad = problems(found)
    if bad:
        print('\n'.join(bad)); return 1
    text = render(found)
    if a.check:
        current = open(INDEX, encoding='utf-8').read() if os.path.exists(INDEX) else ''
        if current != text:
            print('composers/INDEX.md is out of date: run python3 -m study.composers_index'); return 1
        print('composers/INDEX.md is up to date'); return 0
    with open(INDEX, 'w', encoding='utf-8') as f: f.write(text)
    print(f'composers/INDEX.md: {sum(len(i) for _, _, i in found)} techniques of {len(found)} composers'); return 0


if __name__ == '__main__':
    sys.exit(main())
