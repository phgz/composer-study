"""The repair test's clips: for each place (bars 20 to 22; 28 to 33), 64b as written, then Claude's rewrite, then AMT's, 1.5 seconds
apart. Each clip runs from 0.3 seconds before its first bar to 1.5 seconds after its last. The renderer scales each render to its own
loudest moment, so the three are put on one scale from the bar before each place, where they play the same notes; then the clip as
written is brought to -20 LUFS and the others get the same gain (lowered for all three if one would peak above -1 dBFS).

    python3 -I repair64_cut.py <folder holding written/ claude/ amt/ (repair64.py's three renders)> <out folder>"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = [(20, 22), (28, 33)]
VERSIONS = ['written', 'claude', 'amt']


def main():
    src, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
    spec = json.load(open(os.path.join(HERE, '..', 'three-ears-64b-2026-11-23', 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    at = lambda bar: float(np.interp((bar - 1) * 3, xb, xt))
    audio = {}
    for v in VERSIONS:
        x, sr = sf.read(os.path.join(src, v, 'repair64.wav'), always_2d=True); audio[v] = x
    meter = pyln.Meter(sr); report = []
    for a, b in CLIPS:
        same = slice(int((at(a) - .1) * sr), int((at(a + 1) - .05) * sr))        # the bar before the place: the same notes
        k = {'written': 1.0}; fits = {}
        for v in VERSIONS[1:]:
            r = audio['written'][same].ravel(); y = audio[v][same].ravel(); k[v] = float(r @ y / (y @ y))
            fits[v] = dict(gain_db=round(20 * np.log10(k[v]), 3), residual=round(float(np.sqrt(np.mean((r - k[v] * y) ** 2) / np.mean(r ** 2))), 4))
        j0, j1 = int((at(a) - .3) * sr), int((at(b + 1) + 1.5) * sr)
        clips = {v: audio[v][j0:j1] * k[v] for v in VERSIONS}
        gain = -20 - meter.integrated_loudness(clips['written'])
        peak = max(20 * np.log10(np.abs(c).max() + 1e-12) for c in clips.values()) + gain
        if peak > -1: gain -= peak + 1
        g = 10 ** (gain / 20); gap = np.zeros((int(1.5 * sr), 2)); parts = []
        for i, v in enumerate(VERSIONS):
            parts.append(clips[v] * g)
            if i < len(VERSIONS) - 1: parts.append(gap)
        name = f'64b_bars_{a}-{b}_as_written_then_Claude_then_AMT'
        wav = os.path.join(out, name + '.wav'); sf.write(wav, np.concatenate(parts), sr)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-b:a', '192k', os.path.join(out, name + '.mp3')], check=True)
        os.remove(wav)
        clip = (j1 - j0) / sr
        report.append(dict(bars=[a, b], file=name + '.mp3', clip_seconds=round(clip, 2), starts=[round(i * (clip + 1.5), 2) for i in range(3)],
                           gain_db=round(float(gain), 2), fits=fits))
    json.dump(report, open(os.path.join(out, 'repair64_cut.json'), 'w'), indent=1)
    for r in report: print(r)


if __name__ == '__main__':
    main()
