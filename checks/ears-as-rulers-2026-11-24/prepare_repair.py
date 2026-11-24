"""The repair test, AMT's input: piece 64b with the inner voices of the two places Philip heard as wrong (bar 21; bars 29 to 32)
taken out, for AMT to write them again knowing everything around them (study/amt_write.py, AMT's own generate()).

  given      the tune and the bass, every note of the piece (their doublings included), as the earlier writing gave them, on the
             bright piano (--given-program 1: "two pianos", the setup in which AMT writes a part of its own)
  history    the inner voices everywhere else, before the places and after them. AMT's generate() reads those before a place as
             what has been played, and those after as notes it knows are coming (it anticipates them, five seconds ahead)
  spans      bar 21, and bars 29 to 32, in seconds. An inner note that would sound on into a place is cut where the place begins,
             here and in Claude's own rewrite, so that both rewrites start a place from the same silence (64b as written is heard
             untouched)
  beats      64b's tempo map (beat, second), to bring AMT's notes back to beats

Writes amt_repair.json beside this script. On the Mac, eight seeds of each model:

    for m in large medium; do for s in 1 2 3 4 5 6 7 8; do
      python study/amt_write.py ~/models/music-$m-800k ~/anticipation $R/amt_repair.json -o $R/repair_${m}_$s.json --seed $s --given-program 1
    done; done

Run: python3 -I prepare_repair.py <composer-blend> <renderer-engine>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); THREE = os.path.join(HERE, '..', 'three-ears-64b-2026-11-23')
sys.path.insert(0, THREE)
import piece64 as P

PLACES = [(21, 21), (29, 32)]                                                  # bars, first and last


def main():
    blend, renderer = sys.argv[1:3]
    v = P.voices(blend, renderer); sec = v['sec']
    spans_b = [((a - 1) * P.METRE, b * P.METRE) for a, b in PLACES]
    lists = {}
    for name, b, db, m, t, dd in v['notes']: lists.setdefault(name, []).append((b, db, m))
    inner = []
    for name in ('alto', 'tenor'):
        for b, db, m in lists[name]:
            if any(s0 - 1e-6 <= b < s1 - 1e-6 for s0, s1 in spans_b): continue
            for s0, s1 in spans_b:
                if b < s0 - 1e-6 < b + db - 1e-6: db = s0 - b                       # cut where a place begins
            inner.append((b, db, m))
    given = P.seconds(sorted(lists['tune'] + lists['bass']), sec)
    spec = json.load(open(os.path.join(THREE, 'amt_write.json')))
    out = dict(given=given, history=P.seconds(sorted(inner), sec), spans=[[sec(s0), sec(s1)] for s0, s1 in spans_b],
               beats=spec['beats'], places=PLACES)
    json.dump(out, open(os.path.join(HERE, 'amt_repair.json'), 'w'))
    print(f"{len(given)} given notes, {len(out['history'])} inner notes around the places; spans {[[round(a, 2), round(b, 2)] for a, b in out['spans']]}")


if __name__ == '__main__':
    main()
