"""The passages of excerpts64.py cut from the six unmastered renders (64b, AMT Large, AMT Medium; as made, and with the inner voices
brought out), one file a passage: the three versions as made, then the three with the inner voices brought out, in that order (64b,
Large, Medium), 1.5 seconds apart and 3 seconds between the two sets. Each clip runs from 0.3 seconds before its passage to 1.5
seconds after (the last notes' release).

The renderer scales each mix to its own loudest moment, so the six come back at different gains. They are put back on one scale
from stretches where they play the same notes: bars 2 to 5 (in every version 64b's own inner voices, the history AMT was given;
within a set, as made or brought out) and bars 89 to 92 (where neither AMT model wrote anything, so that its two renders are the
same). Then every clip of a passage gets the gain that brings 64b's clip as made to -20 LUFS, so that the tune and bass are as loud
in each; it is lowered for all six together if any would peak above -1 dBFS.

    python3 excerpts64_cut.py <folder holding ours_f0/ large_f0/ medium_f0/ ours_f1/ large_f1/ medium_f1/> <out folder>
    python3 excerpts64_cut.py --inner <folder holding ours_inner/ large_inner/ medium_inner/> <out folder>
        the inner voices alone (excerpts64.py, INNER=1), 64b, Large and Medium, one file a passage, put on one scale from bars 2 to 5
        (64b's own inner voices in all three); bars 89 to 92 left out, where AMT wrote nothing"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__))
PASSAGES = [(5, 9), (89, 92), (105, 112), (141, 148)]
VERSIONS = ['ours', 'large', 'medium']


def main():
    src, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
    spec = json.load(open(os.path.join(HERE, 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    at = lambda bar: float(np.interp((bar - 1) * 3, xb, xt))
    audio = {}
    for v in VERSIONS:
        for f in (0, 1):
            x, sr = sf.read(os.path.join(src, f'{v}_f{f}', 'excerpts64.wav'), always_2d=True); audio[(v, f)] = x
    meter = pyln.Meter(sr); report = []

    def fit(ref, other, t0, t1):
        """the gain that best brings `other` onto `ref` over [t0, t1] s, and how far apart they stay"""
        r = audio[ref][int(t0 * sr):int(t1 * sr)].ravel(); y = audio[other][int(t0 * sr):int(t1 * sr)].ravel()
        k = float(r @ y / (y @ y)); return k, float(np.sqrt(np.mean((r - k * y) ** 2) / np.mean(r ** 2)))
    A = (at(5) - 3.5, at(6) - .1)                                       # bars 2-5: rendered from 4 s before bar 5, the same in all
    B = (at(89) - 3.5, at(93))                                          # bars 89-92: no AMT notes, nor in the 4 s before
    k, fits = {('ours', 0): 1.0}, {}
    for (key, ref, oth, span) in [('large0', ('ours', 0), ('large', 0), A), ('medium0', ('ours', 0), ('medium', 0), A),
                                  ('large1', ('large', 0), ('large', 1), B), ('ours1', ('large', 1), ('ours', 1), A),
                                  ('medium1', ('ours', 1), ('medium', 1), A), ('medium1 via 89-92', ('medium', 0), ('medium', 1), B)]:
        g, res = fit(ref, oth, *span); fits[key] = dict(gain_db=round(20 * np.log10(g), 3), residual=round(res, 4))
        if key != 'medium1 via 89-92': k[oth] = k[ref] * g
    check = 20 * np.log10(k[('medium', 0)] * 10 ** (fits['medium1 via 89-92']['gain_db'] / 20) / k[('medium', 1)])
    print('the six on one scale (dB against 64b as made):', {f'{v} {f}': round(20 * np.log10(x), 2) for (v, f), x in k.items()},
          f'; the two routes to Medium brought out agree within {abs(check):.3f} dB')
    for a, b in PASSAGES:
        i0, i1 = int((at(a) - .3) * sr), int((at(b + 1) + 1.5) * sr)
        clips = {key: x[i0:i1] * k[key] for key, x in audio.items()}
        gain = -20 - meter.integrated_loudness(clips[('ours', 0)])
        peak = max(20 * np.log10(np.abs(c).max() + 1e-12) for c in clips.values()) + gain
        if peak > -1: gain -= peak + 1
        g = 10 ** (gain / 20); gap = np.zeros((int(1.5 * sr), 2)); between = np.zeros((int(3 * sr), 2))
        parts = []
        for f in (0, 1):
            for j, v in enumerate(VERSIONS):
                parts.append(clips[(v, f)] * g)
                if j < 2: parts.append(gap)
            if f == 0: parts.append(between)
        y = np.concatenate(parts)
        name = f'64b_bars_{a}-{b}_64b_Large_Medium'
        wav = os.path.join(out, name + '.wav'); sf.write(wav, y, sr)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-b:a', '192k', os.path.join(out, name + '.mp3')], check=True)
        os.remove(wav)
        report.append(dict(bars=[a, b], seconds=[round(at(a), 2), round(at(b + 1), 2)], clip_seconds=round((i1 - i0) / sr, 2),
                           gain_db=round(float(gain), 2), loudness={f'{v} {"forward" if f else "as made"}': round(float(meter.integrated_loudness(c * g)), 1)
                                                             for (v, f), c in clips.items()}))
    json.dump(dict(scale_db={f'{v} {f}': round(20 * np.log10(x), 3) for (v, f), x in k.items()}, fits=fits, routes_agree_db=round(abs(check), 4),
                   passages=report), open(os.path.join(out, 'excerpts64.json'), 'w'), indent=1)
    for r in report: print(r)


def inner():
    src, out = sys.argv[2:4]; os.makedirs(out, exist_ok=True)
    spec = json.load(open(os.path.join(HERE, 'amt_write.json')))
    xb = np.array([b for b, _ in spec['beats']]); xt = np.array([t for _, t in spec['beats']])
    at = lambda bar: float(np.interp((bar - 1) * 3, xb, xt))
    audio = {}
    for v in VERSIONS:
        x, sr = sf.read(os.path.join(src, f'{v}_inner', 'excerpts64.wav'), always_2d=True); audio[v] = x
    meter = pyln.Meter(sr); i0, i1 = int((at(5) - 3.5) * sr), int((at(6) - .1) * sr); r = audio['ours'][i0:i1].ravel()
    k, fits = {'ours': 1.0}, {}
    for v in VERSIONS[1:]:
        y = audio[v][i0:i1].ravel(); k[v] = float(r @ y / (y @ y))
        fits[v] = dict(gain_db=round(20 * np.log10(k[v]), 3), residual=round(float(np.sqrt(np.mean((r - k[v] * y) ** 2) / np.mean(r ** 2))), 4))
    print('on one scale:', fits)
    report = []
    for a, b in [p for p in PASSAGES if p != (89, 92)]:
        j0, j1 = int((at(a) - .3) * sr), int((at(b + 1) + 1.5) * sr)
        clips = {v: audio[v][j0:j1] * k[v] for v in VERSIONS}
        gain = -20 - meter.integrated_loudness(clips['ours'])
        peak = max(20 * np.log10(np.abs(c).max() + 1e-12) for c in clips.values()) + gain
        if peak > -1: gain -= peak + 1
        g = 10 ** (gain / 20); gap = np.zeros((int(1.5 * sr), 2))
        y = np.concatenate([clips['ours'] * g, gap, clips['large'] * g, gap, clips['medium'] * g])
        name = f'64b_bars_{a}-{b}_inner_voices_64b_Large_Medium'
        wav = os.path.join(out, name + '.wav'); sf.write(wav, y, sr)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-b:a', '192k', os.path.join(out, name + '.mp3')], check=True)
        os.remove(wav)
        report.append(dict(bars=[a, b], gain_db=round(float(gain), 2),
                           loudness={v: round(float(meter.integrated_loudness(c * g)), 1) for v, c in clips.items()}))
    json.dump(dict(scale=fits, passages=report), open(os.path.join(out, 'excerpts64_inner.json'), 'w'), indent=1)
    for x in report: print(x)


if __name__ == '__main__':
    inner() if sys.argv[1] == '--inner' else main()
