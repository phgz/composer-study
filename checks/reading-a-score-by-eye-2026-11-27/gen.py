"""Notes drawn at random (no tune, no harmony: nothing to guess from), as a picture at a chosen sharpness.
The truth goes to a file this session does not open; only score.py reads it.

    python3 gen.py NAME SEED BARS DPI [--systems N]
"""
import json, os, random, subprocess, sys
from music21 import clef, layout, meter, note, stream
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = 'CDEFGAB'
POOL = [f'{s}{o}' for o in (3, 4, 5, 6) for s in STEPS]
POOL = POOL[POOL.index('A3'):POOL.index('C6') + 1]          # 17 places, ledger lines both ways


def build(seed, bars, per_system):
    rng = random.Random(seed); part = stream.Part(); truth = []
    for b in range(bars):
        m = stream.Measure(number=b + 1)
        if b == 0: m.append(clef.TrebleClef()); m.append(meter.TimeSignature('4/4'))
        if b and b % per_system == 0: m.insert(0, layout.SystemLayout(isNew=True))
        row = [rng.choice(POOL) for _ in range(4)]
        for x in row: m.append(note.Note(x, quarterLength=1))
        truth.append(row); part.append(m)
    s = stream.Score(); s.append(part); return s, truth


def main():
    name, seed, bars, dpi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    per = int(sys.argv[sys.argv.index('--per') + 1]) if '--per' in sys.argv else bars
    s, truth = build(seed, bars, per)
    xml = os.path.join(HERE, name + '.musicxml'); s.write('musicxml', xml)
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen')
    trim = [] if '--page' in sys.argv else ['-T', '12']
    subprocess.run(['mscore3', '-r', str(dpi), *trim, '-o', os.path.join(HERE, name + '.png'), xml], env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    src = os.path.join(HERE, name + '-1.png'); im = Image.open(src).convert('RGBA')
    bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[3]); out = os.path.join(HERE, name + '.png'); bg.save(out); os.remove(src)
    json.dump(truth, open(os.path.join(HERE, name + '.truth.json'), 'w'))
    print(name, bg.size, f'{dpi} dpi, {bars} bars, {bars * 4} notes; between two staff lines: {dpi * 1.764 / 25.4:.1f} px')


main()
