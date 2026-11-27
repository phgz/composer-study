"""The calque of a scanned page by code alone: straighten it, flatten its paper, find its staves from their lines,
and cut one system a picture. It reads no note.

    python3 -I calque_scan.py PAGE.jpg OUT_PREFIX [--zoom 1.33] [--staves-per-system 4]
"""
import sys
import cv2, numpy as np


def main():
    src, out = sys.argv[1], sys.argv[2]
    zoom = float(sys.argv[sys.argv.index('--zoom') + 1]) if '--zoom' in sys.argv else 1.33
    per = int(sys.argv[sys.argv.index('--staves-per-system') + 1]) if '--staves-per-system' in sys.argv else 4
    g = cv2.imread(src, cv2.IMREAD_GRAYSCALE).astype(np.float32); h, w = g.shape
    bg = cv2.GaussianBlur(cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((41, 41), np.uint8)), (0, 0), 20)
    flat = np.clip(g / np.maximum(bg, 1), 0, 1)
    ink = (flat < .62).astype(np.float32); small = cv2.resize(ink, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA); hs, ws = small.shape
    best = (0, 0)
    for a in np.arange(-3, 3.01, .05):
        R = cv2.getRotationMatrix2D((ws / 2, hs / 2), a, 1); p = cv2.warpAffine(small, R, (ws, hs)).sum(1); v = float(((p[1:] - p[:-1]) ** 2).sum())
        if v > best[0]: best = (v, a)
    a = best[1]; R = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1)
    up = cv2.warpAffine(flat, R, (w, h), borderValue=1.0, flags=cv2.INTER_CUBIC); ink = up < .62
    # staff lines: rows where ink runs sideways for long stretches (a line may wander a pixel across the page)
    from scipy.signal import find_peaks
    runs = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, 60), np.uint8)).sum(1).astype(np.float32)
    runs = np.convolve(runs, np.ones(3), 'same'); pk, _ = find_peaks(runs, height=.30 * w, distance=5)
    ys = [float(y) for y in pk]
    gaps = np.diff(ys); space = float(np.median(gaps)); staves = []; cur = [ys[0]]
    for y, d in zip(ys[1:], gaps):
        if d < 1.6 * space: cur.append(y)
        else: staves.append(cur); cur = [y]
    staves.append(cur)
    good = []
    for st in staves:                                   # a beam or a hairpin beside a staff can add a sixth "line": keep the most even five
        if len(st) == 5: good.append(st)
        elif len(st) > 5:
            wins = [st[i:i + 5] for i in range(len(st) - 4)]; good.append(min(wins, key=lambda v: float(np.abs(np.diff(v) - space).sum())))
    print(f'tilt {a:+.2f} degrees; lines found {len(ys)}; staves of five lines {len(good)} of {len(staves)}; between two staff lines {space:.1f} px')
    systems = [good[i:i + per] for i in range(0, len(good), per)]
    cols = np.where(ink[int(good[0][0]):int(good[-1][-1])].sum(0) > 0)[0]; x0, x1 = max(0, cols[0] - 12), min(w, cols[-1] + 12)
    cuts = []
    for k, sy in enumerate(systems):
        top = sy[0][0]; bot = sy[-1][-1]
        above = systems[k - 1][-1][-1] if k else top - 14 * space
        below = systems[k + 1][0][0] if k + 1 < len(systems) else bot + 9 * space
        y0 = int(max(0, above + .30 * (top - above))); y1 = int(min(h, bot + .45 * (below - bot)))
        cuts.append((y0, y1))
    for k, ((y0, y1), sy) in enumerate(zip(cuts, systems), 1):
        c = np.clip((up[y0:y1, x0:x1] - .15) / .75, 0, 1); c = cv2.resize(c, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(f'{out}.system-{k}.png', (np.clip(c, 0, 1) * 255).astype(np.uint8))
        print(f'  system {k}: rows {y0} to {y1}, picture {c.shape[1]} x {c.shape[0]}; staves\' top lines at', [round((s[0] - y0) * zoom) for s in sy], 'bottom lines at', [round((s[-1] - y0) * zoom) for s in sy])
    np.save(out + '.geometry.npy', np.array([a, space, x0, x1, zoom] + [v for c in cuts for v in c], dtype=np.float64))


main()
