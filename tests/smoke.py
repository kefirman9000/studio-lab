"""Smoke test: every style renders (preview) and every exporter writes valid files.
   python -m tests.smoke          (quick)
   python -m tests.smoke --full   (also renders full-length audio for a few styles)
   python -m tests.smoke --shard 2/3   (every third genre, starting with the second - CI runs the shards in parallel)"""
import os
import sys
import shutil
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
    k, n = 1, 1
    if '--shard' in sys.argv:
        k, n = (int(x) for x in sys.argv[sys.argv.index('--shard') + 1].split('/'))
    out = tempfile.mkdtemp()
    try:
        _run(full, k, n, out)
    finally:
        shutil.rmtree(out, ignore_errors=True)          # previews of every genre add up to ~200 MB per run


def _run(full, k, n, out):
    t0 = time.time()
    for i, s in enumerate(STYLES):
        if i % n != k - 1:
            continue
        info = generate(dict(style=s, seed=7 + i), out, preview=True, log=lambda *a: None)
        assert -21 < info['loudness'] < -6 and info['peak'] <= -0.9, (s, info['loudness'], info['peak'])   # (quiet solo genres sit near -20)
        song = compose(Options(style=s, seed=7 + i))
        xml.dom.minidom.parse(write_lmms(os.path.join(out, s + '.mmp'), song))
        assert os.path.getsize(write_midi(os.path.join(out, s + '.mid'), song)) > 100
        print(f'ok  {s:<18} {info["key"]:<18} {info["bpm"]} bpm  {info["loudness"]} LUFS')
    names = list(STYLES)
    for i in range(6 if k == 1 else 0):
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
