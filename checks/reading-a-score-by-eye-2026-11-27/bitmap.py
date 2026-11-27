"""Parsing the page as a pure black-and-white bitmap, by code alone: a first, naive try.

It turns the scan black and white, finds the staves and the barlines, keeps only the blobs as big as a filled notehead,
and gives each one a staff, a bar and a height on the staff (so a letter name and octave, without sharps or naturals).
Open noteheads (half notes), grace notes, accidentals and rhythm are not attempted.

    python3 -I bitmap.py PAGE.jpg /path/to/catalogue/0007 FIRST_BAR
"""
import collections, csv, os, sys, time
import cv2, numpy as np
from scipy.signal import find_peaks

LETTERS = 'CDEFGAB'
BOTTOM = dict(p1=2 + 7 * 4, p2=2 + 7 * 4, p3=3 + 7 * 3, p4=4 + 7 * 2)        # the bottom line: E4 (treble), F3 (alto), G2 (bass)
PARTS = ['p1', 'p2', 'p3', 'p4']; NAME = dict(p1='violin I', p2='violin II', p3='viola', p4='cello')


def step_name(i): return f'{LETTERS[i % 7]}{i // 7}'


def parse(path):
    g = cv2.imread(path, cv2.IMREAD_GRAYSCALE).astype(np.float32); h, w = g.shape
    bg = cv2.GaussianBlur(cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((41, 41), np.uint8)), (0, 0), 20)
    bw = ((g / np.maximum(bg, 1)) < .62).astype(np.uint8)                       # pure black and white: 1 is ink
    runs = cv2.morphologyEx(bw, cv2.MORPH_OPEN, np.ones((1, 60), np.uint8)).sum(1).astype(np.float32)
    pk, _ = find_peaks(np.convolve(runs, np.ones(3), 'same'), height=.30 * w, distance=5); ys = [float(y) for y in pk]
    space = float(np.median(np.diff(ys))); groups = [[ys[0]]]
    for y, d in zip(ys[1:], np.diff(ys)):
        if d < 1.6 * space: groups[-1].append(y)
        else: groups.append([y])
    staves = []
    for st in groups:
        if len(st) == 5: staves.append(st)
        elif len(st) > 5: staves.append(min((st[i:i + 5] for i in range(len(st) - 4)), key=lambda v: float(np.abs(np.diff(v) - space).sum())))
    systems = [staves[i:i + 4] for i in range(0, len(staves), 4)]
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(round(1.05 * space)) | 1, int(round(.78 * space)) | 1))
    heads = cv2.morphologyEx(bw, cv2.MORPH_OPEN, k)                               # only what is as fat as a filled notehead survives
    n, lab, stats, cent = cv2.connectedComponentsWithStats(heads, connectivity=8)
    found = collections.Counter(); bars_ok = []; blobs = 0
    for si, sy in enumerate(systems):
        top, bot = int(sy[0][0]), int(sy[-1][-1])
        col = bw[top:bot + 1].sum(0); xs = np.where(col >= .90 * (bot - top + 1))[0]; lines = []      # a barline: ink from the top staff to the bottom one
        for x in xs:
            if lines and x - lines[-1][-1] <= 1.2 * space: lines[-1].append(x)                       # the bracket and the first line count as one
            else: lines.append([x])
        bx = [float(np.mean(l)) for l in lines]; bars_ok.append(len(bx) - 1)
        y_lo = (systems[si - 1][-1][-1] + sy[0][0]) / 2 if si else 0; y_hi = (sy[-1][-1] + systems[si + 1][0][0]) / 2 if si + 1 < len(systems) else h
        for i in range(1, n):
            x, y, bwid, bh, area = stats[i]; cx, cy = cent[i]
            if not (y_lo <= cy < y_hi) or len(bx) < 2 or not (bx[0] < cx < bx[-1]): continue
            if bwid < .7 * space or bwid > 2.6 * space or bh < .55 * space or area < .35 * space * space: continue
            bar = int(np.searchsorted(bx, cx)) - 1
            if si == 0 and bar == 0 and cx < bx[0] + 10.5 * space: continue          # the clefs, key and metre at the start of the movement
            if si > 0 and bar == 0 and cx < bx[0] + 6.5 * space: continue            # the clefs and key at the start of a line
            blobs += 1; k_heads = max(1, int(round(bh / space)))                  # a tall blob is a chord of stacked heads
            for j in range(k_heads):
                yc = y + bh * (j + .5) / k_heads
                part = min(range(4), key=lambda q: 0 if sy[q][0] <= yc <= sy[q][-1] else min(abs(yc - sy[q][0]), abs(yc - sy[q][-1])))
                st = BOTTOM[PARTS[part]] + int(round((sy[part][-1] - yc) / (space / 2)))
                found[(PARTS[part], si * 7 + bar, step_name(st))] += 1
    return found, bars_ok, blobs, space


def truth(folder, first, last):
    T = collections.Counter(); opened = 0
    for r in csv.DictReader(open(os.path.join(folder, 'detail.tsv')), delimiter='\t'):
        if r['grace']: continue
        b, beat, dur = int(r['bar']), float(r['beat']), float(r['dur']); step = ''.join(c for c in r['name'] if c not in '#b-')
        pieces = []                                                               # a note tied over the barline is a head in each bar
        while beat + dur > 3 + 1e-6: pieces.append((b, 3 - beat)); dur -= 3 - beat; b += 1; beat = 0
        pieces.append((b, dur))
        for bb, d in pieces:
            if not first <= bb <= last: continue
            if d >= 2 - 1e-6: opened += 1                                         # a half note or longer: an open head, not attempted
            else: T[(r['part'], bb - first, step)] += 1
    return T, opened


def main():
    page, folder, first = sys.argv[1], sys.argv[2], int(sys.argv[3]); t0 = time.perf_counter()
    found, bars_ok, blobs, space = parse(page); dt = time.perf_counter() - t0
    T, opened = truth(folder, first, first + 7 * len(bars_ok) - 1)
    print(f'parsed in {dt:.2f} s; bars found on each line: {bars_ok}; blobs kept as noteheads: {blobs}; heads after splitting chords: {sum(found.values())}')
    print(f'filled noteheads on the page, by the catalogue: {sum(T.values())} (and {opened} open ones, not attempted)')
    hit = sum((found & T).values()); print(f'found at the right staff, bar and height: {hit} of {sum(T.values())} ({hit / sum(T.values()):.0%}); found but not in the catalogue: {sum((found - T).values())}; missed: {sum((T - found).values())}')
    for p in PARTS:
        tp = collections.Counter({k: v for k, v in T.items() if k[0] == p}); fp = collections.Counter({k: v for k, v in found.items() if k[0] == p})
        print(f'   {NAME[p]:10s} right {sum((fp & tp).values()):3d} of {sum(tp.values()):3d}; found but not there {sum((fp - tp).values()):3d}')
    if '--show' in sys.argv:
        for k, v in sorted((found - T).items()): print('   extra', k, v)
        for k, v in sorted((T - found).items()): print('   missed', k, v)


main()
