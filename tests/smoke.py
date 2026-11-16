"""Smoke test: every style renders (preview) and every exporter writes valid files.
   python -m tests.smoke          (quick)
   python -m tests.smoke --full   (also renders full-length audio for a few styles)"""
import os
import sys
import tempfile
import time
import xml.dom.minidom

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sgcore.api import generate
from sgcore import samplelibs as _sl  # noqa: E402
_sl.REAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_no_real_libs')   # same sounds as CI
from sgcore.compose import Options, compose, MOODS
from sgcore.exporters import write_lmms, write_midi
from sgcore.styles import STYLES


def main():
    full = '--full' in sys.argv
    out = tempfile.mkdtemp()
    t0 = time.time()
    for i, s in enumerate(STYLES):
        info = generate(dict(style=s, seed=7 + i), out, preview=True, log=lambda *a: None)
        assert -20 < info['loudness'] < -6 and info['peak'] <= -0.9, (s, info['loudness'], info['peak'])
        song = compose(Options(style=s, seed=7 + i))
        xml.dom.minidom.parse(write_lmms(os.path.join(out, s + '.mmp'), song))
        assert os.path.getsize(write_midi(os.path.join(out, s + '.mid'), song)) > 100
        print(f'ok  {s:<18} {info["key"]:<18} {info["bpm"]} bpm  {info["loudness"]} LUFS')
    names = list(STYLES)
    for i in range(6):
        o = dict(style=names[i * 5 % len(names)], blend=[names[(i * 7 + 3) % len(names)]], mood=list(MOODS)[i], seed=99 + i)
        info = generate(o, out, preview=True, log=lambda *a: None)
        print(f'ok  fusion {info["style"]:<30} mood={o["mood"]}')
    if full:
        for s in ('house', 'cinematic', 'jazz'):
            info = generate(dict(style=s, seed=3), out, outputs=('wav', 'midi', 'lmms', 'waveform'), log=lambda *a: None)
            assert os.path.exists(info['files']['waveform'])
            print(f'ok  full {s} {info["duration"]}')
    print(f'all good in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
