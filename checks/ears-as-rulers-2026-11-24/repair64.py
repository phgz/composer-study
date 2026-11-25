"""Piece 64b at the two places Philip heard as wrong (bar 21; bars 29 to 32), in three versions, for listening side by side:

  VERSION=written   64b as written, untouched
  VERSION=claude    Claude's own rewrite of the inner voices there (CLAUDE below), by hand: two voices on the plan's chords, no
                    unison, no struck second, no false relation between them, no parallels, the section's last bar (32) a plain
                    E minor
  VERSION=amt       AMT's rewrite: the candidate choose_repair.py picked, by its rule, from AMT's sixteen (repair_chosen.json)

Everything else is 64b's own (the tune, the bass, the other inner notes, tempi, dynamics, pedal, performance draws). In both
rewrites an inner note that would sound on into a place is cut where the place begins, as AMT was given it; and a rewritten note
on a pitch an inner voice of 64b already strikes at that moment is left out (AMT, anticipating bar 33, wrote its first two notes
again a hair before the barline: one key cannot be struck twice at once). Only the notes that
begin from 4 seconds before a clip (bars 20 to 22; 28 to 33) to its end are rendered; repair64_cut.py cuts the clips.

    VERSION=... BLEND=<composer-blend> python3 <composer-blend>/tools/run.py --output-dir <folder> render repair64.py"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
THREE = os.path.join(HERE, '..', 'three-ears-64b-2026-11-23')
PIECE = os.path.join(os.environ.get('BLEND', os.path.join(HERE, '..', '..', '..', 'composer-blend')), 'pieces', '64b_inside_the_mazurka')
sys.path.insert(0, PIECE)
import notes64 as N, whole64 as W

MAP, GAIN, FINAL, METRE, MASTERING = W.MAP, W.GAIN, W.FINAL, W.METRE, W.MASTERING
PLACES = [(21, 21), (29, 32)]
CLIPS = [(20, 22), (28, 33)]
SPANS = [((a - 1) * 3.0, b * 3.0) for a, b in PLACES]
VERSION = os.environ.get('VERSION', 'written')
m = N.m
CLAUDE = dict(                                          # (beat from bar 1, beats, pitch)
    alto=[(60, 3.5, m('F#4')),                                                            # bar 21, held into 22 (a 9-8 over E)
          (84, 1, m('B3')), (85, 2, m('D4')), (87, 1, m('C4')), (88, 2, m('C#4')), (90, 3, m('C4')), (93, 3, m('E4'))],
    tenor=[(60, 2, m('D4')), (62, 1, m('B3')),
           (84, 3, m('G#3')), (87, 1, m('A3')), (88, 3, m('E3')), (91, 2, m('A3')), (93, 3, m('B3'))])


def amt_notes():
    """AMT's chosen rewrite, in beats, by voice (choose_repair.py)"""
    return {v: [tuple(n) for n in l] for v, l in json.load(open(os.path.join(HERE, 'repair_chosen.json')))['voices'].items()}


def rewritten(iv, new):
    """the inner voices with the places' notes taken out, a note sounding on into a place cut where it begins, and `new` put in"""
    out = {}
    for v, l in iv.items():
        kept = []
        for b, d, p in l:
            if any(s0 - 1e-6 <= b < s1 - 1e-6 for s0, s1 in SPANS): continue
            for s0, s1 in SPANS:
                if b < s0 - 1e-6 < b + d - 1e-6: d = s0 - b
            kept.append((b, d, p))
        out[v] = kept
    for v in out:                                       # a new note on a pitch the piece already strikes there is left out
        out[v] = sorted(out[v] + [n for n in new.get(v, []) if not any(abs(n[0] - k[0]) < .01 and n[2] == k[2] for w in out for k in out[w])])
    return out


_inner0 = N.inner
if VERSION == 'claude': N.inner = lambda: rewritten(_inner0(), CLAUDE)
elif VERSION == 'amt': N.inner = lambda: rewritten(_inner0(), amt_notes())


def seconds_of_bar(bar):
    spec = json.load(open(os.path.join(THREE, 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    return float(np.interp((bar - 1) * METRE, xb, xt))


def clips(): return [(seconds_of_bar(a), seconds_of_bar(b + 1)) for a, b in CLIPS]


def build():
    S, END = N.build('all'); ws = clips()
    for part in S.parts.values(): part['notes'] = [n for n in part['notes'] if any(t0 - 4 <= n[0] < t1 for t0, t1 in ws)]
    return S, END
