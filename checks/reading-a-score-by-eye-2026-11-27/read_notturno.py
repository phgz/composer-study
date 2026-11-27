"""Borodin, String Quartet No. 2, third movement (Notturno), first page of the Belaieff miniature score (Leipzig, plate 1055;
IMSLP file 644692, PDF page 19, printed page 20), read by eye from the scan after a calque by code (calque_scan.py, zoom.py).

Read: the first, third and fourth of the page's five systems (bars 1 to 7, 15 to 21, 22 to 28). Written before the comparison
with the catalogue's copy was run, and not changed after.

Each part: {bar: [(beat, quarters, [pitches])]}, beats from 0, sounding names (the key's sharps written out).
A note tied over a barline is one note with its whole length, as the catalogue has it. Grace notes are kept apart.
"""
T = 1 / 3
SYNC = [(0, .5), (.5, 1), (1.5, 1), (2.5, .5)]            # the accompaniment's rhythm: eighth, quarter, quarter, eighth


def sync(*ps): return [(b, d, list(ps)) for b, d in SYNC]
def run(names, each=.5, start=0.0): return [(start + k * each, each, [p]) for k, p in enumerate(names.split())]
def held(*ps): return [(0, 3, list(ps))]


VIOLIN_1 = {
    24: [(1, 2, ['A6'])],
    25: run('G#6 F#6 G#6', T) + [(1, 2, ['E6'])],
    26: run('D6 E6 D6 E6', .25) + [(1, 2, ['F#6'])],
    27: [(0, 1, ['E6']), (1, .5, ['B5']), (2, 1.5, ['E6'])],                 # the last E tied into bar 28
    28: [(.5, .5, ['A#5']), (1, 1.5, ['F#6']), (2.5, .5, ['E6'])]}

VIOLIN_2 = {
    1: sync('C#4', 'E4'), 2: sync('B3', 'D4'), 3: sync('B3', 'D4'), 4: sync('B3', 'D4'), 5: sync('A#3'),
    6: [(0, .5, ['B3']), (.5, 1, ['B3']), (1.5, 1, ['D4']), (2.5, .5, ['D4'])], 7: sync('A3'),
    15: sync('D4'), 16: sync('C#4'), 17: sync('C#4'), 18: sync('B3'), 19: sync('B3'), 20: sync('A3'), 21: sync('A3'),
    22: sync('G#3', 'E4'), 23: [(0, .5, ['A3', 'E4'])],
    24: held('C#4', 'E4'), 25: held('D4', 'B4'), 26: held('D4', 'B4'), 27: held('D4', 'B4'), 28: held('E4', 'C#5')}

VIOLA = {
    1: sync('A3'), 2: sync('A3'), 3: sync('A3'), 4: sync('G#3', 'E4'), 5: sync('G3', 'C#4'), 6: sync('F#3'), 7: sync('F3'),
    15: sync('F#3'), 16: sync('E#3', 'B3'), 17: sync('E3'), 18: sync('D#3', 'A3'), 19: sync('D3'), 20: sync('E3', 'C#4'),
    21: [(0, .5, ['F3', 'D4']), (.5, 1, ['F3', 'D4']), (1.5, 1, ['D4']), (2.5, .5, ['D4'])],
    22: sync('D4'),
    23: run('C#4 E3 F#3 E3 F#3 E3'), 24: run('A3 E3 F#3 E3 F#3 E3'), 25: run('E3 E3 A3 G#3 F#3 E3'),
    26: run('F#3 F#3 B3 A3 G#3 A3'), 27: run('B3 B3 E4 F#4 E4 B3'), 28: run('A#3 C#4 A#3 B3 A#3 C#4')}

CELLO = {
    1: [(1, 2, ['A4'])],
    2: run('G#4 F#4 G#4', T) + [(1, 2, ['E4'])],
    3: run('D4 E4 D4 E4', .25) + [(1, 2, ['F#4'])],
    4: [(0, 1, ['E4']), (1, .5, ['B3']), (2, 1.5, ['E4'])],                  # the last E tied into bar 5
    5: [(.5, .5, ['A#3']), (1, 1.5, ['F#4']), (2.5, .5, ['E4'])],
    6: run('D4 C#4 D4', T) + [(1, 2, ['B3'])],
    7: run('B3 C#4 D4 C#4 B3', .5, .5),
    15: run('G#3 A3 B3 A3 G#3', .5, .5), 16: [(0, 1, ['C#4']), (1, 2, ['G#3'])],
    17: run('F#3 G#3 A3 G#3 F#3', .5, .5), 18: [(0, 1, ['B3']), (1, 2, ['F#3'])],
    19: run('F3 G3 A3 G3 F3', .5, .5), 20: [(0, 1, ['A3']), (1, 2, ['E3'])],
    21: [(0, 1, ['D3']), (1, 2, ['F2'])],
    22: [(0, 1, ['E2']), (1, 1, ['B2']), (2, 1, ['E2'])],
    23: held('A2'), 24: held('A2'), 25: held('A2'), 26: held('A2'), 27: held('G#2'), 28: held('G2')}

READ = {'p1': VIOLIN_1, 'p2': VIOLIN_2, 'p3': VIOLA, 'p4': CELLO}
BARS = list(range(1, 8)) + list(range(15, 29))
GRACES = {('p4', 2): 'G#4 A4', ('p4', 6): 'D4 E4', ('p4', 7): 'C#4 D4', ('p4', 15): 'A3 B3', ('p4', 17): 'G#3 A3',
          ('p4', 19): 'G3 A3', ('p1', 25): 'G#6 A6'}
# Where the picture did not decide by itself and something else did:
DOUBTS = {
    ('p2', 22): 'two notes or three in the chord: taken as two (G#3 and E4), the short lines between them read as ledger lines',
    ('p3', 4): 'the lower note G#3 or A3: taken as G#3, the gap between the heads and the chord (E with its seventh) agreeing',
    ('p3', 7): 'the natural read as on F (F natural), from the head\'s height against bar 6',
    ('p3', 21): 'the upper note D4 or C#4: taken as D4, a little higher than bar 20\'s, and the cello\'s D and F natural under it',
    ('p3', 25): 'the third eighth A3 or B3: taken as A3 from its height',
    ('p4', 1): 'the first note counted as three ledger lines and the space above: A4',
    'graces': 'which two small notes come before the main one was partly taken from the shape of bar 2\'s'}
