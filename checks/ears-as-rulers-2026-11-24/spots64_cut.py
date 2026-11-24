"""The clips of spots64.py, one file a place: the whole texture, then 3 seconds, then the inner voices alone, the same bars. Each clip
runs from 0.3 seconds before its first bar to 1.5 seconds after its last (the last notes' release); each part is brought to -20 LUFS
(lowered if it would peak above -1 dBFS), so the inner voices alone are louder than they are in the piece. Also writes where each
flagged moment falls, in seconds from the start of its file (and of the inner voices' part).

    python3 -I spots64_cut.py <folder holding whole/ and inner/ (spots64.py's two renders)> <out folder>"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SPOTS = [(4, 6), (20, 22), (28, 32), (61, 63), (111, 113)]
MOMENTS = {(4, 6): [(5, 1)], (20, 22): [(21, 2)], (28, 32): [(29, 2), (30, 1), (30, 2), (32, 1)], (61, 63): [(62, 1)],
           (111, 113): [(112, 1)]}                                          # (bar, beat) of each flagged moment


def main():
    src, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
    spec = json.load(open(os.path.join(HERE, '..', 'three-ears-64b-2026-11-23', 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    at = lambda bar, beat=1: float(np.interp((bar - 1) * 3 + beat - 1, xb, xt))
    audio = {}
    for k in ('whole', 'inner'):
        x, sr = sf.read(os.path.join(src, k, 'spots64.wav'), always_2d=True); audio[k] = x
    meter = pyln.Meter(sr); report = []
    for a, b in SPOTS:
        t0, t1 = at(a) - .3, at(b + 1) + 1.5; j0, j1 = int(t0 * sr), int(t1 * sr)
        parts, gains = [], {}
        for k in ('whole', 'inner'):
            c = audio[k][j0:j1]; gain = -20 - meter.integrated_loudness(c)
            peak = 20 * np.log10(np.abs(c).max() + 1e-12) + gain
            if peak > -1: gain -= peak + 1
            gains[k] = round(float(gain), 2); parts.append(c * 10 ** (gain / 20))
        gap = 3.0; y = np.concatenate([parts[0], np.zeros((int(gap * sr), 2)), parts[1]])
        name = f'64b_bars_{a}-{b}_flagged_inner_voices'
        wav = os.path.join(out, name + '.wav'); sf.write(wav, y, sr)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-b:a', '192k', os.path.join(out, name + '.mp3')], check=True)
        os.remove(wav)
        clip = t1 - t0
        report.append(dict(bars=[a, b], file=name + '.mp3', clip_seconds=round(clip, 2), inner_starts_at=round(clip + gap, 2), gain_db=gains,
                           moments=[dict(bar=bar, beat=beat, whole_at=round(at(bar, beat) - t0, 1),
                                         inner_at=round(at(bar, beat) - t0 + clip + gap, 1)) for bar, beat in MOMENTS[(a, b)]]))
    json.dump(report, open(os.path.join(out, 'spots64_cut.json'), 'w'), indent=1)
    for r in report: print(r)


if __name__ == '__main__':
    main()
