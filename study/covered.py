"""Covered lines: where the line meant to lead is covered by the rest, from a render's own stems (the orchestration check of
27 November 2026; checks/covered-lines-2026-11-27.md has the test, written before it was run, and its result).

    python3 study/covered.py <render.json> <windows.json> [--map "/Volumes/Music Libraries/rendered_pieces=<here>"] [--from S --to E]
    python3 study/covered.py <render.json> --window "the voice:247:252:voice" [...]

WINDOWS is a JSON list of {name, start, end, foreground: [parts]} (the pieces' `look` scripts write them for the renderer's
tools/check_balance.py --sections). The render must have been made with EXPORT_MIX_STEMS (its render.json lists mix_stem:<part>).
--map rewrites the start of the stems' paths, for a render read on another machine than it was made on.

For each window: the foreground (its parts summed) against the rest (every other stem), frame by frame (2048 samples, every 1024;
the two channels' powers averaged). In each of the 24 critical bands the rest's energy is spread to the others (25 dB a band
down, 10 dB a band up), summed and lowered 6 dB: the masked threshold. The foreground's audible share in a frame is the part of
its energy in bands where it is over the threshold; a frame is covered under 25%, and is silence (not counted) where the
foreground is more than 40 dB under its loudest in the window. A covered stretch: 0.5 s or more of covered frames, two frames or
less between them bridged. The baseline, the renderer's kind of measure: the foreground's broadband energy 6 dB or more under the
rest's, for the same 0.5 s. A rough ear: no level dependence, no masking in time, the room as the stems carry it."""
import argparse, json, os, sys
import numpy as np

EDGES = np.array([0, 100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270, 1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400, 5300,
                  6400, 7700, 9500, 12000, 15500], dtype=float)
N, HOP = 2048, 1024
DOWN, UP, OFFSET = 25.0, 10.0, 6.0                                    # dB a band below / above the masker; the threshold's offset
SHARE, SILENT, LEAST, BRIDGE, UNDER = .25, 40.0, .5, 2, 6.0


def spreading(n=len(EDGES) - 1):
    """S[j, i]: how much of band i's energy masks band j"""
    i = np.arange(n)
    d = i[None, :] - i[:, None]                                       # masker band minus masked band
    return np.where(d > 0, 10 ** (-DOWN * d / 10), 10 ** (UP * d / 10))  # j below i: falls DOWN a band; j above: falls UP a band


def bands(x, rate):
    """[frames, 24] band energies of a stereo (or mono) signal"""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1: x = x[:, None]
    frames = 1 + max(0, (len(x) - N) // HOP)
    w = np.hanning(N); hz = np.fft.rfftfreq(N, 1 / rate)
    which = np.searchsorted(EDGES, hz, side='right') - 1
    keep = (which >= 0) & (which < len(EDGES) - 1)
    out = np.zeros((frames, len(EDGES) - 1))
    for k in range(frames):
        seg = x[k * HOP:k * HOP + N]
        if len(seg) < N: seg = np.pad(seg, ((0, N - len(seg)), (0, 0)))
        p = np.mean(np.abs(np.fft.rfft(seg * w[:, None], axis=0)) ** 2, axis=1)
        out[k] = np.bincount(which[keep], weights=p[keep], minlength=len(EDGES) - 1)
    return out


def shares(fg, rest):
    """per frame: the foreground's audible share, its broadband level over the rest's (dB), and whether it is sounding"""
    thr = rest @ spreading().T * 10 ** (-OFFSET / 10)
    total = fg.sum(axis=1)
    share = np.where(total > 0, (fg * (fg > thr)).sum(axis=1) / np.maximum(total, 1e-30), 1.0)
    over = 10 * np.log10(np.maximum(total, 1e-30) / np.maximum(rest.sum(axis=1), 1e-30))
    sounding = total > total.max() * 10 ** (-SILENT / 10) if total.max() > 0 else np.zeros(len(total), bool)
    return share, over, sounding


def stretches(flags, times, least=LEAST, bridge=BRIDGE):
    """[(start, end)] of runs of True, gaps of `bridge` frames or less bridged, `least` seconds or more"""
    out, run, gap = [], None, 0
    for k, f in enumerate(flags):
        if f:
            if run is None: run = [k, k]
            else: run[1] = k
            gap = 0
        elif run is not None:
            gap += 1
            if gap > bridge: out.append(run); run, gap = None, 0
    if run is not None: out.append(run)
    step = times[1] - times[0] if len(times) > 1 else 0
    return [(float(times[a]), float(times[b] + step)) for a, b in out if times[b] + step - times[a] >= least]


def stems(render, remap=None):
    d = json.load(open(render)); rate = None; paths = {}
    for k, v in d['outputs'].items():
        if not k.startswith('mix_stem:'): continue
        p = v['path']
        if remap:
            a, b = remap.split('=', 1)
            if p.startswith(a): p = b + p[len(a):]
        paths[v['part']] = p; rate = v.get('sample_rate', rate)
    if not paths: raise SystemExit(f'{render}: no mix stems (render with EXPORT_MIX_STEMS)')
    return paths, int(rate or 44100)


def window(paths, rate, start, end, foreground):
    import soundfile as sf
    missing = [p for p in foreground if p not in paths]
    if missing: raise SystemExit(f'no stem for {missing}')
    a, b = int(start * rate), int(end * rate); fg = rest = None
    for part, path in paths.items():
        with sf.SoundFile(path) as f:
            f.seek(a); x = f.read(b - a, dtype='float64', always_2d=True)
        if part in foreground: fg = x if fg is None else fg + x
        else: rest = x if rest is None else rest + x
    if rest is None: rest = np.zeros_like(fg)
    F, R = bands(fg, rate), bands(rest, rate)
    times = start + (np.arange(len(F)) * HOP + N / 2) / rate
    share, over, sounding = shares(F, R)
    covered = stretches((share < SHARE) & sounding, times)
    under = stretches((over <= -UNDER) & sounding, times)
    return dict(times=times, share=share, over=over, sounding=sounding, covered=covered, under=under)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('render'); ap.add_argument('windows', nargs='?')
    ap.add_argument('--window', action='append', default=[], help='NAME:START:END:part,part')
    ap.add_argument('--map'); ap.add_argument('--from', dest='t0', type=float); ap.add_argument('--to', dest='t1', type=float)
    a = ap.parse_args()
    W = json.load(open(a.windows)) if a.windows else []
    for w in a.window:
        n, s, e, parts = w.rsplit(':', 3); W.append(dict(name=n, start=float(s), end=float(e), foreground=parts.split(',')))
    if a.t0 is not None: W = [w for w in W if w['end'] > a.t0]
    if a.t1 is not None: W = [w for w in W if w['start'] < a.t1]
    paths, rate = stems(a.render, a.map)
    for w in W:
        r = window(paths, rate, w['start'], w['end'], w['foreground'])
        s = r['share'][r['sounding']]; o = r['over'][r['sounding']]
        mm = lambda t: (lambda r: f'{int(r // 60)}:{r % 60:04.1f}')(round(t, 1))
        print(f"{w['name']} ({mm(w['start'])}–{mm(w['end'])}, {'+'.join(w['foreground'])}): audible share median "
              f"{np.median(s):.0%}" + (f", over the rest {np.median(o):+.1f} dB" if len(o) else ''))
        print('   covered: ' + ('; '.join(f'{mm(x)}–{mm(y)}' for x, y in r['covered']) or 'none'))
        print('   baseline, 6 dB under: ' + ('; '.join(f'{mm(x)}–{mm(y)}' for x, y in r['under']) or 'none'))


if __name__ == '__main__':
    main()
