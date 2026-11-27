"""What has not been made yet: the three places composer-blend's procedure names for a gap (Part 1, I), read from the
composers' pages here and from what composer-blend's pieces took of them. Philip, 23 November 2026: "I'd be curious to try
to see, once we have enough samples of composer reference, try to pattern what have not been made yet and experiment with
that." Re-run it as pages are added; the reading of what it lists is written by hand, in checks/.

    python3 -m study.gaps --blend ../composer-blend                  # the report, as Markdown, on stdout
    python3 -m study.gaps --blend ../composer-blend --json gaps.json # the same, as data

What it lists (for reading, not a verdict):
  1. What few techniques work on: the count for each dimension, and how often two dimensions meet in one technique.
  2. What no piece has taken: each page's techniques that no "Tried" line in composer-blend names. A Tried line names its
     numbers itself, or says that the piece's page names them ("Its page names the techniques it took"); then the piece's
     "What was taken" section is read. Lines about pieces made before the page, or not from it, are left out.
  3. The purposes: every *Why* line, by dimension, with who is speaking, so that a purpose reached one way only can be found.
  4. What the composers do not do: every page's list.
"""
import argparse, collections, glob, itertools, json, os, re, sys

from study.composers_index import DIMENSIONS, PAGES

TECHNIQUES = ('melody', 'harmony', 'rhythm', 'texture', 'form', 'loudness', 'colour')      # background is not a technique
NUMS = r'\d+(?:(?:,\s*(?:and\s+)?|\s+and\s+|\s+to\s+|\s*[-–]\s*)\d+)*'


def numbers(text):
    """'1 to 6, 8 to 16, 20 and 35' -> {1..6, 8..16, 20, 35}"""
    out = set()
    for part in re.split(r',\s*(?:and\s+)?|\s+and\s+', text.strip()):
        m = re.match(r'(\d+)(?:\s+to\s+|\s*[-–]\s*)(\d+)$', part.strip())
        if m: out |= set(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.strip().isdigit(): out.add(int(part))
    return out


def section(text, title):
    """the body of a '## ' section whose heading starts with title, or ''"""
    m = re.search(r'(?m)^## ' + re.escape(title) + r'.*\n', text)
    if not m: return ''
    n = re.search(r'(?m)^## ', text[m.end():])
    return text[m.end():m.end() + n.start()] if n else text[m.end():]


def read_pages(folder=PAGES):
    """{slug: {composer, techniques: {n: {name, dims, kind, why, speaker}}, does_not: [(qualifier, line)]}}"""
    out = {}
    for path in sorted(glob.glob(os.path.join(folder, '*.md'))):
        slug = os.path.basename(path)[:-3]
        if slug in ('README', 'INDEX'): continue
        text = open(path, encoding='utf-8').read()
        composer = re.match(r'# (.+?)(?: \(|$)', text).group(1)
        techs, kind = {}, None
        for block in re.split(r'(?m)^(?=\d+\. |### )', section(text, 'Techniques'))[1:]:
            if block.startswith('### '):
                kind = block[4:].split('\n', 1)[0].strip(); continue
            n = int(block.split('.', 1)[0]); first = block.split('\n', 1)[0]
            m = re.match(r'\d+\. \*\*(.+?)\*\*', first) or re.match(r'\d+\. \*(.+?)\*', first)
            name = re.sub(r'[*]', '', m.group(1)).strip().rstrip('.:,') if m else first[:60]
            w = re.search(r'(?m)^ {3,4}\*Works on:\* (.+?)\.?\s*$', block)
            why = re.search(r'(?ms)^ {3,4}\*Why:\* (.+?)(?=^ {3,4}\*[A-Z][a-z]+:\*|\Z)', block)
            why_text = ' '.join(why.group(1).split()) if why else ''
            speaker = re.findall(r'\*\(([^)]+)\)\*', why_text)
            techs[n] = dict(name=name, kind=kind, dims=[d.strip() for d in w.group(1).split(',')] if w else [],
                            why=re.sub(r'\s*\*\([^)]+\)\*\s*$', '', why_text), speaker=speaker[-1] if speaker else '')
        does_not, qualifier = [], ''
        body = section(text, 'What he does not do') or section(text, 'What she does not do') or section(text, 'What they do not do')
        for line in body.splitlines():
            if re.match(r'^\*[^*].*\*\s*$', line.strip()): qualifier = line.strip().strip('*')
            elif line.startswith('- '): does_not.append((qualifier, line[2:].strip()))
        out[slug] = dict(composer=composer, techniques=techs, does_not=does_not)
    return out


def taken_from_piece_page(blend, piece, composer, slug):
    """the numbers a piece's own page lists for one composer, under 'What was taken'"""
    folder = sorted(glob.glob(os.path.join(blend, 'pieces', f'{piece}_*')))
    if not folder or not os.path.exists(os.path.join(folder[0], 'README.md')): return None
    text = open(os.path.join(folder[0], 'README.md'), encoding='utf-8').read()
    body = section(text, 'What was taken')
    if not body: return None
    last = composer.split()[-1]
    heads = list(re.finditer(r'(?m)^\*\*([^*]+)\*\*', body))
    mine = [h for h in heads if last in h.group(1)]
    if mine:                                                               # a list under the composer's name
        h = mine[0]; nxt = [g.start() for g in heads if g.start() > h.start()]
        chunk = body[h.end():nxt[0] if nxt else len(body)]
        got = set()
        for m in re.finditer(r'(?m)^- (' + NUMS + r')', chunk): got |= numbers(m.group(1))
        return got
    got = set()                                                            # one composer: numbers in brackets
    for m in re.finditer(r'\((' + NUMS + r')\)', body.split('Left out')[0]): got |= numbers(m.group(1))
    return got or None


def read_tried(blend, pages):
    """{slug: [(piece, {numbers}, line)]}, and the lines that could not be read"""
    out, unread = collections.defaultdict(list), []
    for slug, page in pages.items():
        path = os.path.join(blend, 'reference', 'composers', slug + '.md')
        if not os.path.exists(path): continue
        for line in section(open(path, encoding='utf-8').read(), 'Tried').splitlines():
            if not line.startswith('- '): continue
            entry = line[2:]
            if re.match(r'(Earlier|What was already)', entry) or 'not from this page' in entry: continue
            piece = re.search(r'piece (\d+[a-z]?)', entry)
            piece = piece.group(1) if piece else ('sketch ' + entry.split(',')[0] if 'sketch' in entry else '?')
            head = entry.split('Philip:')[0]
            if 'page names the techniques' in head:
                got = taken_from_piece_page(blend, piece, page['composer'], slug)
            else:
                m = re.search(r'all but (' + NUMS + r')', head)
                if m: got = set(page['techniques']) - numbers(m.group(1))
                else:
                    m = re.search(r'(?:\):\s*(?:techniques\s+)?|techniques\s+|took\s+)(' + NUMS + r')', head)
                    got = numbers(m.group(1)) if m else None
                    more = re.search(r';\s*(' + NUMS + r') in part', head)
                    if got is not None and more: got |= numbers(more.group(1))
            if got is None: unread.append((slug, entry[:120])); continue
            out[slug].append((piece, sorted(got), entry))
    return out, unread


def report(pages, tried, unread):
    lines = ['# What has not been made yet: the lists', '',
             f'{len(pages)} pages, {sum(len(p["techniques"]) for p in pages.values())} numbered entries. Written by '
             '`study/gaps.py`; the reading of them is in `checks/`.', '']
    techs = [(s, n, t) for s, p in pages.items() for n, t in p['techniques'].items() if 'background' not in t['dims'] or len(t['dims']) > 1]
    # 1. what few techniques work on
    lines += ['## 1. What the techniques work on', '']
    count = collections.Counter(d for _, _, t in techs for d in t['dims'] if d in TECHNIQUES)
    lines += ['| | ' + ' | '.join(TECHNIQUES) + ' |', '|---|' + '---:|' * len(TECHNIQUES)]
    pair = collections.Counter(frozenset(c) for _, _, t in techs for c in itertools.combinations(sorted(set(t['dims']) & set(TECHNIQUES)), 2))
    for a in TECHNIQUES:
        lines.append(f'| **{a}** ({count[a]}) | ' + ' | '.join('' if a == b else str(pair[frozenset((a, b))]) for b in TECHNIQUES) + ' |')
    alone = collections.Counter(t['dims'][0] for _, _, t in techs if len(set(t['dims']) & set(TECHNIQUES)) == 1 and t['dims'][0] in TECHNIQUES)
    lines += ['', 'A dimension\'s total, and in each cell the techniques tagged with both. Tagged with one dimension only: '
              + ', '.join(f'{d} {alone[d]}' for d in TECHNIQUES) + '.', '']
    # 2. what no piece has taken
    lines += ['## 2. What no piece has taken', '']
    for slug, page in pages.items():
        got = set(n for _, ns, _ in tried.get(slug, []) for n in ns)
        left = [n for n, t in page['techniques'].items() if n not in got and set(t['dims']) & set(TECHNIQUES)]
        pieces = ', '.join(sorted({p for p, _, _ in tried.get(slug, [])})) or 'none from this page'
        lines.append(f'- **{page["composer"]}** ({len(left)} of {len(page["techniques"])} not taken; pieces: {pieces}): '
                     + ('; '.join(f'{n}. {page["techniques"][n]["name"]} [{", ".join(page["techniques"][n]["dims"])}]' for n in left) or 'all taken'))
    if unread:
        lines += ['', 'Tried lines whose numbers could not be read (counted as taking nothing):', '']
        lines += [f'- {s}: {e}' for s, e in unread]
    # 3. the purposes
    lines += ['', '## 3. The purposes (*Why*), by dimension', '']
    for d in TECHNIQUES:
        mine = [(s, n, t) for s, n, t in techs if d in t['dims'] and t['why']]
        lines += [f'### {d} ({len(mine)} with a *Why*, of {count[d]})', '']
        lines += [f'- {pages[s]["composer"]} {n}, {t["name"]}: {t["why"]}' + (f' *({t["speaker"]})*' if t['speaker'] else '') for s, n, t in mine]
        lines.append('')
    # 4. what they do not do
    lines += ['## 4. What the composers do not do', '']
    for slug, page in pages.items():
        for q, l in page['does_not']:
            lines.append(f'- **{page["composer"]}**' + (f' ({q})' if q else '') + f': {l}')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--blend', required=True, help="composer-blend's checkout (its reference/composers/ and pieces/)")
    ap.add_argument('--json', help='also write the lists as data')
    a = ap.parse_args(argv)
    pages = read_pages(); tried, unread = read_tried(a.blend, pages)
    sys.stdout.write(report(pages, tried, unread))
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(dict(pages=pages, tried={s: [(p, ns) for p, ns, _ in v] for s, v in tried.items()},
                           unread=unread), f, indent=1, ensure_ascii=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())
