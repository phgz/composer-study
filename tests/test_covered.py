"""study/covered.py: a line under a louder sound in its own band is covered; the same line far above a louder sound is heard."""
import numpy as np
from study import covered as C

RATE = 44100


def tone(hz, amp, sec=1.0): t = np.arange(int(sec * RATE)) / RATE; return amp * np.sin(2 * np.pi * hz * t)


def noise(lo, hi, amp, sec=1.0, seed=1):
    x = np.random.default_rng(seed).standard_normal(int(sec * RATE)); X = np.fft.rfft(x); hz = np.fft.rfftfreq(len(x), 1 / RATE)
    X[(hz < lo) | (hz > hi)] = 0; y = np.fft.irfft(X, len(x)); return amp * y / np.abs(y).max()


def test_a_line_in_the_rests_own_band_and_quieter_is_covered():
    share, over, sounding = C.shares(C.bands(tone(1000, .05), RATE), C.bands(noise(800, 1300, 1.0), RATE))
    assert sounding.all() and np.median(share) < C.SHARE


def test_a_line_far_above_a_louder_low_sound_is_heard_though_quieter_overall():
    share, over, sounding = C.shares(C.bands(tone(4000, .05), RATE), C.bands(tone(150, 1.0), RATE))
    assert np.median(share) > .9 and np.median(over) < -20             # what the broadband baseline would call covered


def test_stretches_bridge_short_gaps_and_keep_only_long_runs():
    t = np.arange(40) * .1
    f = np.zeros(40, bool); f[2:8] = True; f[9:12] = True; f[20:23] = True
    assert [tuple(round(x, 6) for x in s) for s in C.stretches(f, t, least=.5, bridge=1)] == [(.2, 1.2)]
