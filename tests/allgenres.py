"""(2.17) A check for every genre, derived from the genre's own rules (no audio rendering, ~1 minute).

    python -m tests.allgenres            # check every genre
    python -m tests.allgenres house trap # just these
    python -m tests.allgenres --update   # re-measure the baseline after an intended change (commit the json)

Per genre, two seeds, checked against the genre definition itself:
  - the song composes; the tempo is inside the genre's range; the key uses one of the genre's scales
  - notes in a playable range, sane velocities and timing; a song length between 25 s and 9 min
  - every part the song form brings in actually plays somewhere
  - the same seed gives exactly the same song (recipes / "Full song after its preview" depend on it)
  - each drum part follows the genre's written patterns about as closely as before (baseline below)
  - the chords stay in key about as much as before
The baseline (tests/allgenres_baseline.json) holds the measured pattern match / in-key numbers; a later change that
pulls a genre away from its own rules by more than the margin fails here, in every genre at once.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
BASE = os.path.join(ROOT, 'tests', 'allgenres_baseline.json')
SEEDS = (1, 2)
DRUM_MARGIN = 0.25            # pattern match may fall this much below the baseline (seed-to-seed spread is ~0.1)
KEY_MARGIN = 0.15


def _pattern_match(s, tr, pats, lay):
    on = {}
    for e in s['events']:
        if e.track == tr:
            on.setdefault(int(e.beat // 4), set()).add(e.beat % 4)
    scores = []
    for sec in s['sections']:
        if lay not in sec['layers'] or sec['opts'].get('fade'):
            continue
        for b in range(sec['bar'], sec['bar'] + sec['bars']):
            got, best = on.get(b, set()), 0.0
            for p in pats:
                if not p or not p.strip('.-'):
                    best = 1.0                    # a written rest bar
                    continue
                stp = 4.0 / len(p)
                want = [i * stp for i, c in enumerate(p) if c not in '.-']
                hit = sum(1 for w in want if any(abs(g - w) < stp * 0.5 for g in got))
                best = max(best, hit / len(want))
            scores.append(best)
    return sum(scores) / len(scores) if scores else None


def _sig(s):
    return [(e.track, round(e.beat, 4), round(e.dur, 4), e.midi, round(e.vel or 0, 3)) for e in s['events']]


def measure(style):
    from sgcore.compose import Options, compose
    from sgcore.styles import STYLES
    import math
    st = STYLES[style]
    errs, drums, inkey = [], {}, []
    for seed in SEEDS:
        try:
            s = compose(Options(style=style, seed=seed))
        except Exception as e:                       # noqa: BLE001 - reported per genre
            return style, dict(errors=['seed %d: compose failed: %r' % (seed, e)])
        tag = 'seed %d: ' % seed
        lo, hi = st['bpm']
        if not (lo - 0.5 <= s['bpm'] <= hi + 0.5):
            errs.append(tag + 'tempo %s outside %s-%s' % (s['bpm'], lo, hi))
        scales = s['st'].get('scales') or st.get('scales')      # the resolved rules (a 'modal' character trait swaps modes in)
        if scales and s['key'].scale_name not in scales:
            errs.append(tag + 'scale %s not one of %s' % (s['key'].scale_name, scales))
        secs = s['total_bars'] * 4 * 60.0 / s['bpm']
        if not (25 <= secs <= 540):
            errs.append(tag + 'length %.0f s' % secs)
        ev = s['events']
        if not ev:
            errs.append(tag + 'no notes')
            continue
        bad = [e for e in ev if not (math.isfinite(e.beat) and e.beat >= -0.01 and e.dur >= 0 and
                                     (e.vel is None or 0 <= e.vel <= 1.5) and (e.midi is None or 12 <= e.midi <= 120))]
        if bad:
            e = bad[0]
            errs.append(tag + '%d odd notes, e.g. %s beat %.2f midi %s vel %s' % (len(bad), e.track, e.beat, e.midi, e.vel))
        lay = {t['name']: t['layer'] for t in s['st']['tracks']}
        layers = set(lay.values())
        played = {lay.get(e.track) for e in ev}
        used = set()
        for sec in s['sections']:
            used |= set(sec['layers'])
        rests = lambda v: any(isinstance(p, str) and not p.strip('.-') for p in ([v] if isinstance(v, str) else (v or [])))
        dr = s['st'].get('drums') or {}
        may_rest = {x for x in layers if all(rests(dr.get(t)) or rests(s['st'].get('bass') if x == 'bass' else None)
                                             for t, l in lay.items() if l == x)}
        silent = sorted(x for x in used if x in layers and x not in played and x != 'fx' and x not in may_rest)
        if silent:
            errs.append(tag + 'parts brought in by the form never play: %s' % silent)
        if seed == SEEDS[0] and _sig(compose(Options(style=style, seed=seed))) != _sig(s):
            errs.append(tag + 'the same seed gave a different song')
        for tr, pats in (s['st'].get('drums') or {}).items():
            if isinstance(pats, str):
                pats = [pats]
            if not isinstance(pats, (list, tuple)) or tr not in lay:
                continue
            m = _pattern_match(s, tr, [p for p in pats if isinstance(p, str)], lay[tr])
            if m is not None:
                drums[tr] = min(drums.get(tr, 1.0), m)
        pcs = {(s['key'].root + x) % 12 for x in s['key'].scale}
        ch = [e.midi % 12 for e in ev if e.midi is not None and lay.get(e.track) in ('chords', 'pad')]
        if ch:
            inkey.append(sum(1 for p in ch if p in pcs) / len(ch))
    return style, dict(errors=errs, drums={k: round(v, 3) for k, v in drums.items()},
                       inkey=round(min(inkey), 3) if inkey else None)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    update = '--update' in sys.argv
    from sgcore import samplelibs as _sl
    _sl.REAL_DIR = os.path.join(ROOT, 'tests', '_no_real_libs')     # same sounds as CI
    from sgcore.styles import STYLES
    names = sorted(args or STYLES)
    for n in names:
        assert n in STYLES, 'unknown genre ' + n
    base = json.load(open(BASE)) if os.path.isfile(BASE) else {}
    with ProcessPoolExecutor(max(1, min(4, os.cpu_count() or 1))) as ex:
        res = dict(ex.map(measure, names, chunksize=4))
    fails = []
    for n in names:
        r = res[n]
        fails += ['%s: %s' % (n, e) for e in r['errors']]
        b = base.get(n)
        if b and not update:
            for tr, v in (b.get('drums') or {}).items():
                now = r['drums'].get(tr)
                if now is not None and now < v - DRUM_MARGIN:
                    fails.append('%s: the %s part follows its written patterns less (%.2f, was %.2f)' % (n, tr, now, v))
            if b.get('inkey') is not None and r['inkey'] is not None and r['inkey'] < b['inkey'] - KEY_MARGIN:
                fails.append('%s: chords in key %.2f (was %.2f)' % (n, r['inkey'], b['inkey']))
    missing = [n for n in names if n not in base]
    if update or (missing and not fails):
        for n in names:
            base[n] = dict(drums=res[n]['drums'], inkey=res[n]['inkey'])
        base = {k: base[k] for k in sorted(base) if k in STYLES}
        with open(BASE, 'w') as f:                       # one genre per line: small, readable diffs
            f.write('{\n' + ',\n'.join('%s: %s' % (json.dumps(k), json.dumps(base[k], sort_keys=True)) for k in base) + '\n}\n')
        print('baseline written for %d genres' % len(names))
    if not args:                                         # the docs say how many genres there are: keep them true
        import re
        n = len(STYLES)
        docs = {'README.md': r'(\d+) genres in three tabs', 'docs/GENRES.md': r'genres \((\d+)\)',
                'docs/GENRE_LIST.txt': r'ALL (\d+) GENRES'}
        for f, pat in docs.items():
            m = re.search(pat, open(os.path.join(ROOT, f), encoding='utf-8').read())
            if not m or int(m.group(1)) != n:
                fails.append('%s says %s genres, there are %d - run tools/genre_list.py, tools/genre_list_txt.py, '
                             'tools/genre_spec.py (and fix the README count)' % (f, m.group(1) if m else '?', n))
    if fails:
        print('\n'.join('FAIL ' + f for f in fails))
        sys.exit(1)
    print('ok  %d genres: tempo, scale, ranges, length, every part plays, same seed = same song, drum patterns, '
          'chords in key' % len(names))
    if missing and not update:
        print('note: %d genres had no baseline yet (now written): %s' % (len(missing), ', '.join(missing[:8])))


if __name__ == '__main__':
    main()
