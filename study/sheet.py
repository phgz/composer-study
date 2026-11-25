"""Sheet music from a MusicXML file, drawn by MuseScore: to look at what NotaGen wrote (notagen_write.py --sheet), and later at
our own pieces once they are exported. Philip, 25 November 2026, on drawing NotaGen's proposals as sheet music without
ComfyUI_NotaGen (which does it with MuseScore after generating): "yes we can add it".

  python3 study/sheet.py FILE.xml [-o OUT_BASE] [--pdf] [--dpi 150] [--mscore PATH]

PNG: MuseScore writes one image a page, OUT_BASE-1.png, OUT_BASE-2.png, ...; --pdf writes OUT_BASE.pdf. OUT_BASE is the file's
own path without .xml unless -o says otherwise. MuseScore is looked for at --mscore, then on the PATH (mscore4portable,
MuseScore4, mscore4, mscore, musescore, then MuseScore 3's mscore3, musescore3), then where its Mac app installs it. On Linux
with no display it is run offscreen (Qt's own platform, not a virtual X server). The file is read by MuseScore as data;
nothing in it is run here. Tried on 25 November 2026 with MuseScore 3 on Linux, on the writer's Chopin of 23 November
(checks/notagen-writer-2026-11-23): three pages."""
import argparse, glob, os, re, shutil, subprocess, sys

NAMES = ('mscore4portable', 'MuseScore4', 'mscore4', 'mscore', 'musescore', 'mscore3', 'musescore3')
MAC_APPS = ('/Applications/MuseScore 4.app/Contents/MacOS/mscore', '/Applications/MuseScore 3.app/Contents/MacOS/mscore')


def find(explicit=None):
    """the MuseScore executable: the one named, else the first found; None if there is none"""
    if explicit: return explicit if os.path.isfile(explicit) and os.access(explicit, os.X_OK) else None
    for n in NAMES:
        p = shutil.which(n)
        if p: return p
    for p in MAC_APPS:
        if os.path.isfile(p) and os.access(p, os.X_OK): return p
    return None


def command(mscore, xml, target, dpi=None):
    return [mscore] + (['-r', str(int(dpi))] if dpi and target.endswith('.png') else []) + ['-o', target, xml]


def pages(out_base):
    """the page images MuseScore wrote for OUT_BASE, in page order"""
    found = glob.glob(glob.escape(out_base) + '-*.png')
    num = lambda p: int(re.search(r'-(\d+)\.png$', p).group(1)) if re.search(r'-(\d+)\.png$', p) else 0
    return sorted((p for p in found if re.search(r'-\d+\.png$', p)), key=num)


def draw(xml, out_base=None, pdf=False, dpi=150, mscore=None, timeout=300):
    """draw XML as sheet music; returns the files written"""
    exe = find(mscore)
    if not exe: raise FileNotFoundError('MuseScore not found: install it, or name it with --mscore')
    out_base = out_base or os.path.splitext(xml)[0]
    target = out_base + ('.pdf' if pdf else '.png')
    env = dict(os.environ)
    if sys.platform.startswith('linux') and not env.get('DISPLAY') and not env.get('WAYLAND_DISPLAY'):
        env.setdefault('QT_QPA_PLATFORM', 'offscreen')
    r = subprocess.run(command(exe, xml, target, None if pdf else dpi), env=env, capture_output=True, text=True, timeout=timeout)
    out = [target] if pdf and os.path.exists(target) else pages(out_base) if not pdf else []
    if not pdf and not out and os.path.exists(target): out = [target]          # a one-page score may come without a number
    if r.returncode or not out:
        raise RuntimeError(f'MuseScore wrote nothing (status {r.returncode}): {(r.stderr or r.stdout).strip()[-400:]}')
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('xml'); ap.add_argument('-o'); ap.add_argument('--pdf', action='store_true')
    ap.add_argument('--dpi', type=int, default=150); ap.add_argument('--mscore')
    a = ap.parse_args()
    for f in draw(a.xml, a.o, a.pdf, a.dpi, a.mscore): print(f)


if __name__ == '__main__':
    main()
