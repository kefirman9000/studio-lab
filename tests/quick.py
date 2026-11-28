"""The quick checks (a few minutes): run first on every push, so most mistakes show up before the long test run.

Imports, the 2.30 features (best of several seeds, family tone targets, cutdowns, seamless loop, release folder, A/B
picks) and one short render per family of genres.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np  # noqa: E402

from sgcore import dsp  # noqa: E402
from sgcore.compose import Options, compose  # noqa: E402


def test_pick_best():
    from sgcore.polish import pick_best_seed, song_score
    s1, sc1, tried = pick_best_seed({'style': 'house'}, 4242, k=5, budget=30)
    s2, _, _ = pick_best_seed({'style': 'house'}, 4242, k=5, budget=30)
    assert s1 == s2, 'the same rolled seed must pick the same song'
    assert tried[0][0] == 4242 and len(tried) == 5 and sc1 == max(x[1] for x in tried)
    assert song_score(compose(Options(style='house', seed=s1))) == sc1   # the picked seed replays as itself
    print('ok  best of several: deterministic, keeps the top score, the seed replays')


def test_family_tone():
    from sgcore.render import family_tone
    from sgcore.styles import STYLES
    assert family_tone('trance') is None                  # has its own record-measured target
    ft = family_tone('house')
    assert ft and len(ft) == 9 and abs(sum(ft)) < 0.1, ft
    assert family_tone('bluegrass') is None               # its family has no measured records
    n = sum(1 for k in STYLES if family_tone(k))
    assert n >= 80, n
    print(f'ok  family tone targets for {n} genres without records of their own')


def test_release_exports():
    from sgcore.render import Renderer, master, _trim
    from sgcore import release
    dsp.seed_rng(7)
    song = compose(Options(style='house', seed=7))
    r = Renderer(song, log=lambda *a: None)
    mix = r.render(None)
    _trim()
    out = master(mix, dict(song['st']['master']), log=lambda *a: None)
    bar = r._bt(4)
    cuts = release.cutdowns(out, song, r)
    assert sorted(cuts) == [15, 30, 60], sorted(cuts)
    for L, x in cuts.items():
        d = x.shape[-1] / dsp.SR
        assert L - 2 * bar - 0.1 <= d <= L + 0.01, (L, d)
        assert float(np.sqrt(np.mean(x[:, -500:] ** 2))) < 1e-3, 'a cutdown must end in silence'
    lp = release.seamless_loop(out, song, r)
    assert abs(lp.shape[-1] - int(round(r._bt(song['total_bars'] * 4) * dsp.SR))) <= 1
    seam = np.concatenate([lp[:, -64:], lp[:, :64]], axis=1)
    assert np.abs(np.diff(seam, axis=1)).max() < 0.5, 'loop seam clicks'
    d = tempfile.mkdtemp()
    try:
        from sgcore.api import generate
        os.environ['STUDIOLAB_NO_FFMPEG'] = '1'
        info = generate({'style': 'lofi', 'seed': 3}, d, outputs=('wav', 'release'), log=lambda *a: None)
        rf = info['files']['release']
        meta = json.load(open(os.path.join(rf, 'release.json')))
        assert meta['bpm'] == info['bpm'] and meta['loudness_lufs'] is not None and meta['cutdowns'], meta
        for f in meta['files'].values():
            assert os.path.exists(os.path.join(rf, f.rstrip('/'))), f
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print('ok  cutdowns 60 / 30 / 15 s, seamless loop, release folder + release.json')


def test_ab_picks():
    from sgcore import app
    d = tempfile.mkdtemp()
    old = app.AB_PICKS
    try:
        app.AB_PICKS = os.path.join(d, 'ab_picks.jsonl')
        for i in range(4):
            app.save_ab_pick(dict(t=i, winner={'style': 'house', 'energy': 0.8}, loser={'style': 'house', 'energy': 0.3},
                                  winner_sounds={'lead': 'saw'}, loser_sounds={'lead': 'pluck'}), keep=3)
        picks = app.load_ab_picks()
        assert [p['t'] for p in picks] == [1, 2, 3]
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
        import ab_report
        rep = ab_report.report(picks)
        assert '3 A/B picks' in rep and 'lead: saw  +3' in rep and 'lead: pluck  -3' in rep, rep
    finally:
        app.AB_PICKS = old
        shutil.rmtree(d, ignore_errors=True)
    print('ok  A/B picks saved, capped and reported')


def test_one_per_family():
    for st in ('house', 'trance', 'rock', 'jazz', 'trap', 'celtic_reel'):
        song = compose(Options(style=st, seed=11))
        assert song['events'] and song['sections'], st
    print('ok  compose one genre per family')


def main():
    test_one_per_family()
    test_pick_best()
    test_family_tone()
    test_ab_picks()
    test_release_exports()
    print('all good')


if __name__ == '__main__':
    main()
