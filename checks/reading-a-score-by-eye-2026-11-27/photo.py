"""A clean page of random notes made to look like a phone photo, and the "calque" of that photo by code alone.

    python3 photo.py degrade NAME        NAME.png (300 dpi, clean) -> NAME.photo.jpg (full size) and NAME.seen.jpg (a third of it)
    python3 photo.py calque NAME         NAME.photo.jpg -> NAME.line-K.png: straightened, light flattened, one line a picture

Nothing here reads a note: the calque finds the page's tilt and its lines from where the ink is.
"""
import os, sys
import cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))


def degrade(name):
    im = cv2.imread(os.path.join(HERE, name + '.png')); h, w = im.shape[:2]; rng = np.random.default_rng(7)
    pad = 160; im = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255, 255, 255)); h, w = im.shape[:2]
    paper = np.array([222, 238, 244], np.float32) / 255                       # bgr: a cream page
    f = im.astype(np.float32) / 255 * paper
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])                         # held at an angle: tilt and keystone
    dst = np.float32([[.030 * w, .050 * h], [.985 * w, .0 * h], [w, .93 * h], [.0 * w, .995 * h]])
    M = cv2.getPerspectiveTransform(src, dst); f = cv2.warpPerspective(f, M, (w, h), borderValue=tuple(float(x) for x in paper * .8))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    light = 1.0 - .38 * (xx / w) - .12 * (yy / h)                              # the lamp is on the left
    shadow = 1 - .30 * np.exp(-(((xx - .62 * w) / (.20 * w)) ** 2 + ((yy - .55 * h) / (.45 * h)) ** 2))   # a hand's shadow
    f = f * (light * shadow)[..., None]
    f = cv2.GaussianBlur(f, (0, 0), 2.4)                                        # not quite in focus
    f = f + rng.normal(0, .022, f.shape).astype(np.float32)                     # sensor grain
    out = np.clip(f * 255, 0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(HERE, name + '.photo.jpg'), out, [cv2.IMWRITE_JPEG_QUALITY, 60])
    full = cv2.imread(os.path.join(HERE, name + '.photo.jpg'))
    small = cv2.resize(full, (w // 3, h // 3), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(HERE, name + '.seen.jpg'), small, [cv2.IMWRITE_JPEG_QUALITY, 80])
    print('photo', full.shape[1::-1], '| as seen whole', small.shape[1::-1], f'| between two staff lines there: about {20.8 / 3:.1f} px')


def calque(name):
    im = cv2.imread(os.path.join(HERE, name + '.photo.jpg')); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    bg = cv2.GaussianBlur(cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((61, 61), np.uint8)), (0, 0), 25)   # the paper without its ink
    flat = np.clip(g / np.maximum(bg, 1), 0, 1)                                 # the light flattened
    ink = (flat < .80).astype(np.float32); small = cv2.resize(ink, None, fx=.25, fy=.25, interpolation=cv2.INTER_AREA)
    best = (0, 0); hs, ws = small.shape
    for a in np.arange(-6, 6.01, .1):                                           # the tilt: the angle at which the rows of ink are sharpest
        R = cv2.getRotationMatrix2D((ws / 2, hs / 2), a, 1); p = cv2.warpAffine(small, R, (ws, hs)).sum(1); v = float(((p[1:] - p[:-1]) ** 2).sum())
        if v > best[0]: best = (v, a)
    a = best[1]; h, w = flat.shape; R = cv2.getRotationMatrix2D((w / 2, h / 2), a, 1)
    up = cv2.warpAffine(flat, R, (w, h), borderValue=1.0, flags=cv2.INTER_CUBIC)
    rows = (up < .80).sum(1).astype(np.float32); rows = np.convolve(rows, np.ones(41) / 41, 'same'); on = rows > rows.max() * .10
    bands = []; k = 0
    while k < h:
        if on[k]:
            j = k
            while j < h and on[j]: j += 1
            if j - k > 60: bands.append((k, j))
            k = j
        else: k += 1
    merged = []
    for b in bands:                                                              # ledger notes above a line can split a band
        if merged and b[0] - merged[-1][1] < 50: merged[-1] = (merged[-1][0], b[1])
        else: merged.append(b)
    print(f'tilt found: {a:+.1f} degrees; lines of music found: {len(merged)}')
    for n, (y0, y1) in enumerate(merged, 1):
        cols = (up[y0:y1] < .80).sum(0); xs = np.where(cols > 0)[0]; x0, x1 = max(0, xs[0] - 30), min(w, xs[-1] + 30)
        c = up[max(0, y0 - 45):min(h, y1 + 45), x0:x1]; c = np.clip((c - .25) / .60, 0, 1)   # ink dark, paper white
        cv2.imwrite(os.path.join(HERE, f'{name}.line-{n}.png'), (c * 255).astype(np.uint8)); print('  line', n, c.shape[1::-1])


{'degrade': degrade, 'calque': calque}[sys.argv[1]](sys.argv[2])
