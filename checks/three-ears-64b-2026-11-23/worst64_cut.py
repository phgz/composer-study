"""The four segments of worst64.py cut into one file each: the whole texture with the tenor chosen, then with the tenor the outside
ears like least, 1.5 seconds apart; 3 seconds; then the inner voices alone, the same two. Each clip runs from 0.3 seconds before
the bar before its segment to 1.5 seconds after the segment (the last notes' release). The two renders of each kind are put on one
scale from the stretches before each segment, where they play the same notes; then the chosen clip, whole or inner, is brought to
-20 LUFS and the other gets the same gain, lowered for both if either would peak above -1 dBFS.

    python3 -I worst64_cut.py <folder holding chosen_inner0/ worst_inner0/ chosen_inner1/ worst_inner1/> <out folder>"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
    sel = json.load(open(os.path.join(HERE, 'worst64.json')))
    spec = json.load(open(os.path.join(HERE, 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    at = lambda bar: float(np.interp((bar - 1) * 3, xb, xt))
    audio = {}
    for v in ('chosen', 'worst'):
        for i in (0, 1):
            x, sr = sf.read(os.path.join(src, f'{v}_inner{i}', 'worst64.wav'), always_2d=True); audio[(v, i)] = x
    meter = pyln.Meter(sr); scale, report = {}, []
    for i in (0, 1):
        idx = np.concatenate([np.arange(int((at(s['bars'][0] - 1) - 3.5) * sr), int((at(s['bars'][0]) - .05) * sr)) for s in sel])
        r = audio[('chosen', i)][idx].ravel(); y = audio[('worst', i)][idx].ravel(); k = float(r @ y / (y @ y))
        scale[i] = dict(gain_db=round(20 * np.log10(k), 3), residual=round(float(np.sqrt(np.mean((r - k * y) ** 2) / np.mean(r ** 2))), 4))
        audio[('worst', i)] = audio[('worst', i)] * k
    for s in sel:
        a, b = s['bars']; j0, j1 = int((at(a - 1) - .3) * sr), int((at(b + 1) + 1.5) * sr)
        parts, gains = [], {}
        for i in (0, 1):
            c, w = audio[('chosen', i)][j0:j1], audio[('worst', i)][j0:j1]
            gain = -20 - meter.integrated_loudness(c)
            peak = max(20 * np.log10(np.abs(x).max() + 1e-12) for x in (c, w)) + gain
            if peak > -1: gain -= peak + 1
            g = 10 ** (gain / 20); gains['whole' if i == 0 else 'inner voices'] = round(float(gain), 2)
            parts += [c * g, np.zeros((int(1.5 * sr), 2)), w * g] + ([np.zeros((int(3 * sr), 2))] if i == 0 else [])
        name = f'64b_bars_{a}-{b}_tenor_chosen_then_least_liked'
        wav = os.path.join(out, name + '.wav'); sf.write(wav, np.concatenate(parts), sr)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-b:a', '192k', os.path.join(out, name + '.mp3')], check=True)
        os.remove(wav); report.append(dict(bars=[a, b], gain_db=gains))
    json.dump(dict(scale={'whole' if i == 0 else 'inner voices': v for i, v in scale.items()}, segments=report),
              open(os.path.join(out, 'worst64_cut.json'), 'w'), indent=1)
    print(scale); [print(r) for r in report]


if __name__ == '__main__':
    main()
