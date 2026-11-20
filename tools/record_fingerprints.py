"""Fingerprint real reference records for the genre matcher (1.87).

    python tools/record_fingerprints.py mapping.tsv          # add / replace these records
    python tools/record_fingerprints.py mapping.tsv --eval   # also report how well the matcher places each record

mapping.tsv: one record per line, "<genre id><TAB><audio file>". Each record is measured exactly the way a reference
song is measured in the app (drum feel on a 16-step bar, tonal balance, how percussive it is), at the tempo reading
that fits its genre (half / double / x1.5 tempo detections are common), and saved to sgcore/record_fingerprints.json.
The matcher compares a reference with these records as well as with rendered previews of each genre, so a real
record is placed next to the records its genre was modelled on, not only next to how the app renders the genre.
Only the measurements are stored - no audio, no titles.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, 'sgcore', 'record_fingerprints.json')
SR = 22050


def load(path, seconds=180):
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-t', str(seconds), '-i', path, '-f', 'f32le', '-ac', '1',
                          '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<f4').astype(np.float64)


def fit_bpm(bpm, lo, hi):
    """The reading of a detected tempo that falls in the genre's range (or lands nearest to it)."""
    cands = [bpm * r for r in (1.0, 2.0, 0.5, 1.5, 2 / 3, 3.0, 4 / 3, 0.75)]
    return min(cands, key=lambda b: (max(0, lo - b, b - hi), abs(b - bpm)))


def measure(genre, path):
    from sgcore.analysis import analyze
    from sgcore.genrematch import fingerprint
    from sgcore.styles import STYLES
    x = load(path)
    a = analyze(x, SR)
    lo, hi = STYLES[genre]['bpm']
    b = fit_bpm(float(a['bpm']), lo, hi)
    fp = fingerprint(x, SR, b)
    fp['src'] = 'record'
    fp['id'] = hashlib.sha1(os.path.basename(path).encode()).hexdigest()[:10]
    return fp


def main():
    from sgcore.styles import STYLES
    pairs = []
    for line in open(sys.argv[1], encoding='utf-8'):
        if '\t' in line and not line.startswith('#'):
            g, p = line.rstrip('\n').split('\t', 1)
            if g in STYLES and os.path.exists(p):
                pairs.append((g, p))
            else:
                print('skipped', g, os.path.basename(p))
    try:
        data = json.load(open(OUT))
    except Exception:
        data = {}
    for i, (g, p) in enumerate(pairs):
        fp = measure(g, p)
        lst = [x for x in data.get(g, []) if x.get('id') != fp['id']]
        data[g] = lst + [fp]
        print(f'{i + 1}/{len(pairs)} {g} bpm {fp["bpm"]}', flush=True)
    with open(OUT, 'w') as f:
        json.dump({k: data[k] for k in sorted(data)}, f, separators=(',', ':'))
    print(f'saved {sum(len(v) for v in data.values())} records for {len(data)} genres -> {OUT}')
    if '--eval' in sys.argv:
        evaluate(pairs)


def evaluate(pairs):
    """Leave-one-out: each record is placed with its own fingerprint removed."""
    from sgcore import genrematch
    from sgcore.analysis import analyze
    from sgcore.styles import STYLES, LABELS
    from sgcore.genre_groups import group_of
    top1 = top3 = fam3 = 0
    for g, p in pairs:
        x = load(p, 150)
        res = analyze(x, SR)
        genrematch.analyze_reference(x, SR, res)
        own = hashlib.sha1(os.path.basename(p).encode()).hexdigest()[:10]
        genrematch.EXCLUDE = {own}
        gs = [s['id'] for s in genrematch.suggest(res, STYLES, LABELS, top=3)]
        genrematch.EXCLUDE = set()
        top1 += gs[:1] == [g]
        top3 += g in gs
        fam3 += any(group_of(s) == group_of(g) for s in gs)
        print(f'  {g:24s} -> {", ".join(gs)}')
    n = max(1, len(pairs))
    print(f'right genre first: {top1}/{n}   in the top 3: {top3}/{n}   right family in the top 3: {fam3}/{n}')


if __name__ == '__main__':
    if '--eval-only' in sys.argv:
        pairs = [tuple(line.rstrip('\n').split('\t', 1)) for line in open(sys.argv[1], encoding='utf-8') if '\t' in line]
        evaluate([(g, p) for g, p in pairs if os.path.exists(p)])
    else:
        main()
