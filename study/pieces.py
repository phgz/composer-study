"""composer-blend's pieces as lines, for the ear: from a score's build() (run with the renderer on the path) or from the score a render
recorded (*.render.json, written by the shared renderer). Times are in seconds, as heard. Each pitched part is a line (its sounding
skyline, as study/lines.py); a part of fewer than 20 notes or a span under 4 semitones (a drum, a drone) is not a line."""
import contextlib, importlib.util, io, json, os, sys
from study import lines as L


def from_build(path):
    """{part name: notes [(t, d, midi, ...)]} from a score whose build() returns (Score, end) or a Score; or, for a notes module
    with no build() (pieces 63 on: notesNN.py), from its EV rows (part, seconds, length, midi, ...), as tools/events.py reads them"""
    path = os.path.abspath(path); d = os.path.dirname(path); sys.path.insert(0, d); cwd = os.getcwd(); os.chdir(d)
    try:
        spec = importlib.util.spec_from_file_location('piece_' + os.path.basename(path)[:-3], path); mod = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(mod)
            if not hasattr(mod, 'build') and hasattr(mod, 'EV'):
                out = {}
                for r in mod.EV: out.setdefault(str(r[0]), []).append((float(r[1]), float(r[2]), r[3]))
                return out
            r = mod.build()
        S = r[0] if isinstance(r, tuple) else r
        return {(k[-1] if isinstance(k, tuple) else str(k)): p['notes'] for k, p in S.parts.items()}
    finally: os.chdir(cwd); sys.path.remove(d)


def from_render(path):
    """{part name: notes} from the score a render recorded"""
    return {p['name']: p['notes'] for p in json.load(open(path, encoding='utf-8'))['score']['data']['parts']}


def read(path):
    return from_render(path) if path.endswith('.json') else from_build(path)


def lines_of(parts, min_notes=20, min_span=4):
    """{part: its sounding skyline [(t, d, midi)]}, pitched parts only"""
    out = {}
    for name, notes in parts.items():
        line = L.skyline([(float(n[0]), float(n[1]), int(round(float(n[2])))) for n in notes])
        if len(line) >= min_notes and max(n[2] for n in line) - min(n[2] for n in line) >= min_span: out[name] = line
    return out


def final_of(lines):
    """the keynote: the last note of the lowest line"""
    low = min(lines.values(), key=lambda l: sum(n[2] for n in l) / len(l)); return low[-1][2] % 12
