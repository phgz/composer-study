# Readings for composer-blend's piece 82b (27 November 2026)

What was measured for the pages of Mendelssohn (16 to 18) and Dvořák (17 and 18), from score-reader's catalogue, version 25, with score-reader's `notes` and `harmony` written to TSV files and read by two short scripts (run with `python3 -I`; the scripts and their printed output follow). Glass and Still have no score in the catalogue.

## Dvořák, String Quartet no. 12, op. 96 (OpenScore), movements 1 and 2

Printed:

```
mvt 2 parts and note counts: {'p2': 636, 'p3': 919, 'p4': 339, 'p1': 467} bars 97
v1 bars 1-20 in D minor pentatonic (D F G A C): 100/125
p2: bars with notes 94; bar = the bar before (pitches and rhythm) 20; same rhythm 40
p3: bars with notes 97; bar = the bar before (pitches and rhythm) 28; same rhythm 78
p4: bars with notes 96; bar = the bar before (pitches and rhythm) 10; same rhythm 28
p2 bars 1-4: ['D4 F4 F4 F4 D4 F4 F4 F4', ...]  (the same in bars 1 to 4)
p3 bars 1-4: ['F3 A3 A3 D4 D4 A3 F3 A3 A3 D4 D4 A3', ...]  (the same in bars 1 to 4)
p4 bars 1-4: ['D3 D3', 'D3 D3', 'D3 D3', 'A3 D3 D3']
part with the longest mean note, bars counted: {'p4': 18, 'p1': 57, 'p3': 9, 'p2': 13}
cello bars with mean note >= 1.5 quarters: [18, 34, 42, 88, 95, 97]
mvt 1 parts and counts: {'p1': 1110, 'p2': 1228, 'p4': 757, 'p3': 1030} bars 178
viola bars 1-6: F3 A3 C4 D4 F4 D4 C4 A3 F3 G3 A3 C4 C3 D3 F3 D3 C3 D3 F3 D3 C3 F3 A3 C4 C4 A3 F3 (from bar 3)
viola bars 3-6 in F pentatonic: 27/27
p1 mvt1 bars 1-2: ['F5 A5 F5 A5', 'F5 A5 F5 A5']
p2 mvt1 bars 1-2: ['A4 C5 A4 C5 A4 C5', 'A4 C5 A4 C5']
```

"The bar before" compares each bar's notes (position in the bar, pitch, length) with the previous bar's.

## Mendelssohn, String Quartet no. 2, op. 13 (DCML), movements 1 and 4

Printed (the first violin's line: its highest note at each onset; bars as DCML counts them, the upbeat as bar 0):

```
intro, first violin, bars 0-19: C#4/0.5@0 F#4/2@1 E4/1@1 C#4/1@2 D4/1@2 E4/1.5@3 F#4/0.5@3 Ab4/0.5@3 B4/0.5@3 B4/1@4 ...
longest run of the same intervals: 21 intervals (22 notes), intro from bar 0, finale from bar 372 to 380
  intro : C#4 F#4 E4 C#4 D4 E4 F#4 Ab4 B4 B4 A4 C#5 F#5 E5 C#5 C#5 D5 D5 E5 A5 G5 F#5
  finale: C#4 F#4 E4 C#4 D4 E4 F#4 Ab4 B4 B4 A4 C#5 F#5 E5 C#5 C#5 D5 D5 E5 A5 G5 F#5
runs of 6+ intervals shared (finale bar, intro bar, length): [(372, 0, 21), (382, 13, 6)]
```

The annotators' labels of the first movement's bars 0 to 22 and the finale's bars 380 to 396 (key A, local key I in both): the introduction on A major's chords (I, IV, V and their applied chords) until the leading-tone chords of bars 19 to 22; the finale's last bars on I, IV, V, ii, ending I.
