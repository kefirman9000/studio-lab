"""Measure every genre the way the reference matcher measures a song, and save the results.

    python tools/genre_fingerprints.py            # genres not measured yet (--all: every genre, ~30 min)
    python tools/genre_fingerprints.py house trap # just these (merged into the file)

Writes sgcore/genre_fingerprints.json: per genre, the drum feel (kick / snare / hat on a 16-step bar, four on the
floor, backbeat, half-time, kick density, 16th hats), how percussive it is, and its tonal balance - measured from a
rendered preview, so a reference song is compared with how each genre actually sounds.
"""
import json
import os
import shutil
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, 'sgcore', 'genre_fingerprints.json')


def one(style, seeds=(11,)):
    import numpy as np
    from scipy.io import wavfile
    from sgcore.api import generate
    from sgcore.genrematch import fingerprint
    prints = []
    d = tempfile.mkdtemp()
    try:
        for sd in seeds:
            info = generate(dict(style=style, seed=sd), d, preview=True, outputs=['wav'], log=lambda *a: None)
            sr, x = wavfile.read(info['files']['wav'])
            x = x.astype(np.float32)
            x = x.mean(axis=1) if x.ndim == 2 else x
            from scipy import signal
            x = signal.resample_poly(x, 1, 2) if sr == 44100 else x
            prints.append(fingerprint(x, 22050, info['bpm']))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return style, prints


def main():
    from sgcore.styles import STYLES
    try:
        with open(OUT) as f:
            data = json.load(f)
    except Exception:
        data = {}
    names = [a for a in sys.argv[1:] if not a.startswith('-')] or \
        [s for s, st in STYLES.items() if not st.get('composer') and ('--all' in sys.argv or s not in data)]
    with ProcessPoolExecutor(max_workers=int(os.environ.get('JOBS', '3'))) as ex:
        for i, (style, prints) in enumerate(ex.map(one, names)):
            data[style] = prints
            print(f'{i + 1}/{len(names)} {style}', flush=True)
            if i % 10 == 9:
                with open(OUT, 'w') as f:
                    json.dump(data, f, separators=(',', ':'))
    data = {k: data[k] for k in sorted(data) if k in STYLES}
    with open(OUT, 'w') as f:
        json.dump(data, f, separators=(',', ':'))
    print(f'saved {len(data)} genres -> {OUT}')


if __name__ == '__main__':
    main()
