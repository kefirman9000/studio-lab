"""Problem report (redaction, sections) and the app-window helpers - no network, no GUI."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sgcore import diagnostics, appwindow  # noqa: E402


def main():
    home = os.path.expanduser('~')
    t = diagnostics.redact(f'{home}/x a@b.com ' + 'ab' * 32 + ' key=ABCDEFGHIJKLMNOPQRSTUV')
    assert home not in t and 'a@b.com' not in t and 'ab' * 32 not in t and 'ABCDEFGHIJKLMNOP' not in t, t
    jobs = {'j1': dict(status='error', error='boom', started=1.0, items=[{'options': {'style': 'trance', 'seed': 3}}], results=[],
                       log=['Traceback (most recent call last): ...']),
            'j2': dict(status='done', started=2.0, items=[], results=[{'warnings': ['lead: plugin failed']}], log=[])}
    r = diagnostics.build(jobs, 'it broke')
    for want in ('STUDIO LAB PROBLEM REPORT', 'it broke', '=== Versions', '=== Sound libraries', '=== Plugins',
                 'ERROR: boom', 'trance seed 3', 'warning: lead: plugin failed', '=== Recent log'):
        assert want in r, want
    appwindow.find_browser()                     # never raises, whatever is installed
    from sgcore import fxrig
    assert fxrig.reverb_kind('orchestral', 'Orchestral') == 'hall' and fxrig.reverb_kind('trance', 'Electronic') == 'hall'
    assert fxrig.reverb_kind('rock', 'Classic') == 'room' and fxrig.reverb_kind('pop', 'Classic') == 'plate'
    for k in ('hall', 'plate', 'room'):
        prm = fxrig.reverb_params(k, 3.0)
        assert prm['dry_level'] == 0.0 and 0.1 <= prm['decay_s'] <= 10.0
    st = {'category': 'Classic', 'reverb': 2.0}
    assert fxrig.run_reverb(st, None) is None    # no plugin planned -> built-in reverb
    print('ok  problem report + redaction, app window helpers')
    sm = diagnostics.summary(jobs, 'it broke')
    assert sm.startswith('```') and 'TECHNICAL SUMMARY' in sm and 'boom' in sm and '"style": "trance"' in sm and 'lead: plugin failed' in sm
    assert home not in sm and len(sm) < 13000
    assert diagnostics.synth_params().startswith('```')
    print('ok  technical summary, synth parameter list')
    test_journey()
    test_mp3_without_ffmpeg()
    test_ui_sound_menus()
    test_remembered_prefs()
    print('all good')


def test_remembered_prefs():
    """1.56: the theme and other app settings, and the window size, are kept in settings.json (the page's own storage is
    lost when the app starts on another port or the window keeps no storage), and come back on the next launch."""
    import json
    import tempfile
    from sgcore import app, appwindow, updater
    ui = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sgcore', 'ui.html')).read()
    assert ui.index("'__SL_UIPREFS__'") < ui.index('state={closed:')           # restored before anything reads it
    old_s, old_r = app.SETTINGS, updater.ROOT
    d = tempfile.mkdtemp()
    app.SETTINGS = os.path.join(d, 'settings.json')
    updater.ROOT = d
    try:
        app.save_settings({'ui_prefs': {'sl_theme': '{"main":"#000000"}'}, 'window_geom': {'w': 1200, 'h': 800, 'x': 30, 'y': 40}})
        assert json.load(open(app.SETTINGS))['ui_prefs']['sl_theme'].startswith('{')
        assert appwindow.last_geometry() == (1200, 800, (30, 40))
        app.save_settings({'window_geom': {'w': 5, 'h': 5}})
        assert appwindow.last_geometry()[:2] == (1440, 920)                      # nonsense sizes fall back
    finally:
        app.SETTINGS, updater.ROOT = old_s, old_r
    print('ok  theme / settings and window size remembered across launches')


def test_ui_sound_menus():
    """A part's sound menu must be the one that saves your pick (1.51.5 moved the octave menu in front of it, and the
    pick silently went to the octave menu - songs kept reverting to the genre's sounds)."""
    ui = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sgcore', 'ui.html')).read()
    assert "querySelector(':scope > select:not(.fxsel):not(.octsel)').onchange=e=>{ if(e.target.value) state.instruments[r]" in ui
    assert "w.querySelector('select').onchange=e=>{ if(e.target.value) state.instruments" not in ui
    import re
    from collections import Counter
    ids = Counter(re.findall(r'\sid="([^"$]+)"', ui[:ui.index('<script>')]))
    dup = [k for k, v in ids.items() if v > 1]
    assert not dup, f'duplicate element ids in ui.html: {dup}'              # (#prog was both a box and the progress bar)
    assert ui.index('id="voxCard"') < ui.index('<summary>Parts') and 'id="voxQuickUp"' in ui     # voice samples: own card, easy to find
    assert '<details class="card dropzone" open id="voxCard">' in ui and "vc.addEventListener('drop'" in ui   # drop a clip on it
    assert '_styleAnchor' in ui and 'd.dataset.id=s.id' in ui                                 # clicked genre row stays put
    assert "it took too long" in ui and "hubOpenTab('overview')" in ui                     # the sounds hub always opens
    import ast as _ast                                                                      # no endpoint shadows STYLES
    _src = open(os.path.join(os.path.dirname(__file__), '..', 'sgcore', 'app.py')).read()
    for _fn in _ast.walk(_ast.parse(_src)):
        if isinstance(_fn, _ast.FunctionDef) and _fn.name == '_post':
            assert not any(isinstance(x, _ast.ImportFrom) and any((a.asname or a.name) == 'STYLES' for a in x.names)
                           for x in _ast.walk(_fn)), 'a local STYLES import in _post breaks the other endpoints'
    assert 'id="fontSel"' in ui and "applyFont()" in ui and 'id="denseSel"' in ui and ".st.alt{" in ui   # font menu, compact striped list
    print('ok  part sound menus save your pick; no duplicate element ids')


def test_mp3_without_ffmpeg():
    """The installer bundles lameenc, so MP3 export works with no ffmpeg installed."""
    import shutil
    import sys
    import tempfile
    import types
    import numpy as np
    from sgcore import dsp
    calls = {}

    class Enc:
        def set_bit_rate(self, k): calls['kbps'] = k
        def set_in_sample_rate(self, r): calls['sr'] = r
        def set_channels(self, c): calls['ch'] = c
        def set_quality(self, q): pass
        def encode(self, pcm): calls['n'] = len(pcm); return b'\xff\xfb' + b'\0' * 10
        def flush(self): return b''
    fake = types.ModuleType('lameenc')
    fake.Encoder = Enc
    old_which, old_mod = shutil.which, sys.modules.get('lameenc')
    shutil.which = lambda *a, **k: None
    sys.modules['lameenc'] = fake
    d = tempfile.mkdtemp()
    try:
        assert dsp.mp3_encoder() == 'lameenc'
        from sgcore import api
        assert api.have_ffmpeg()
        wav = os.path.join(d, 'a.wav')
        dsp.write_wav(wav, np.zeros((2, 4410)))
        mp3 = dsp.write_mp3(wav, os.path.join(d, 'a.mp3'), 320, dict(title='Tést', genre='house', artist='Studio Lab'))
        data = open(mp3, 'rb').read()
        assert data.startswith(b'ID3\x04') and b'TIT2' in data and 'Tést'.encode() in data and b'\xff\xfb' in data
        assert calls == dict(kbps=320, sr=dsp.SR, ch=2, n=4410 * 4)
    finally:
        shutil.which = old_which
        if old_mod is None:
            sys.modules.pop('lameenc', None)
        else:
            sys.modules['lameenc'] = old_mod
        shutil.rmtree(d, ignore_errors=True)
    print('ok  MP3 export without ffmpeg (lameenc, ID3 tags)')


def test_journey():
    import numpy as np
    from sgcore import samplelibs
    samplelibs.REAL_DIR = '_no_real_libs'
    from sgcore.compose import compose, Options
    from sgcore.windows import tempo_seconds, section_window
    from sgcore.api import describe, trim_tail, trim_lead_in
    from sgcore.dsp import SR
    tm = [(0, 60.0), (8, 60.0), (16, 120.0)]
    assert abs(tempo_seconds(tm, 8) - 8.0) < 1e-6 and 8 + 4 < tempo_seconds(tm, 16) < 16         # ramps integrate
    s = compose(Options(style='cinematic_journey', seed=5))
    names = [x['name'] for x in s['sections']]
    assert names == ['Tension', 'Sorrow', 'Resolve', 'Glory', 'Reflection', 'Resolution'], names
    lv = {x['name']: x['opts']['level'] for x in s['sections']}
    assert lv['Glory'] > lv['Resolve'] > lv['Sorrow'] > lv['Tension'] and lv['Reflection'] < lv['Sorrow']   # dynamic arc
    bpms = [v for _, v in s['tempo_map']]
    assert min(bpms) < 0.75 * s['bpm'] and max(bpms) > 1.03 * s['bpm']          # ritardando ... accelerando
    tracks = {e.track for e in s['events']}
    for t in ('piano', 'vn1', 'va', 'vc', 'cb', 'horns', 'tpt', 'tbn', 'tuba', 'timp', 'spicc_lo', 'flute'):
        assert t in tracks, t
    sec = {x['name']: (x['bar'] * 4, (x['bar'] + x['bars']) * 4) for x in s['sections']}
    lo = [e.midi for e in s['events'] if e.track == 'piano' and sec['Tension'][0] <= e.beat < sec['Tension'][1]]
    assert lo and max(lo) <= 47                                                   # icy notes at the bottom of the piano
    assert not [e for e in s['events'] if e.track == 'tpt' and e.beat < sec['Resolve'][0]]   # trumpets wait for the resolve
    last = [e for e in s['events'] if e.track == 'pad' and e.beat >= sec['Resolution'][0]]
    fin = max(last, key=lambda e: e.beat)
    assert fin.dur >= 12 and {(m - s['key'].root) % 12 for m in [e.midi for e in last if e.beat == fin.beat]} >= {0, 4, 7}
    d = describe(s)
    assert 180 < d['seconds'] < 330 and d['tempo_range'][0] < d['tempo_range'][1]
    g = next(x for x in s['sections'] if x['name'] == 'Glory')
    assert g.get('key_change') == 2 and ('gap', g['bar'] * 4 - 1, 1) in s['fx']                  # lift + grand pause
    assert any(k == 'cymroll' for k, _, _ in s['fx'])
    for t in ('choir', 'choir_oo', 'harp', 'cbsn', 'cbtbn', 'tbn_marc'):
        assert t in tracks, t
    hi = [e for e in s['events'] if e.track == 'vn1' and e.beat >= (g['bar'] + g['bars'] // 2) * 4 and e.beat < (g['bar'] + g['bars']) * 4]
    assert hi
    tri = compose(Options(style='cinematic_journey', seed=5, journey={'preset': 'triumph'}))
    assert [x['name'] for x in tri['sections']] == ['Tension', 'Resolve', 'Battle', 'Glory', 'Resolution']
    tb = {e.track for e in tri['events']}
    assert {'taiko', 'snare', 'anvil'} <= tb
    tg = compose(Options(style='cinematic_journey', seed=5, journey={'preset': 'tragedy'}))
    assert 'Glory' not in [x['name'] for x in tg['sections']] and not tg['sections'][-1].get('picardy')
    el = compose(Options(style='cinematic_journey', seed=5, journey={'preset': 'elegy', 'piano': 0.2}))
    assert [x['name'] for x in el['sections']] == ['Sorrow', 'Reflection', 'Resolution'] and 'choir_oo' not in {e.track for e in el['events']}
    lo_ = compose(Options(style='cinematic_journey_low', seed=5))
    lt = {e.track for e in lo_['events']}
    assert 'vc_mel' in lt and 'bsn' in lt and not lt & {'vn_hi', 'flute', 'oboe'}
    hi_n = lambda song: sum(e.midi >= 72 for e in song['events'] if e.track not in ('bdrum', 'cym', 'taiko', 'snare', 'anvil'))
    assert hi_n(lo_) < 0.6 * hi_n(s) and max(e.midi for e in lo_['events']) <= 79                 # darker, lower
    m = compose(Options(style='cinematic_journey', seed=5, journey={'acts': ['sorrow', 'glory'], 'ending': 'minor'}))
    assert [x['name'] for x in m['sections']] == ['Sorrow', 'Glory']
    b = compose(Options(style='cinematic_journey', seed=5, blend=['trance']))
    assert b.get('tempo_map') and b['style'] == 'cinematic_journey'                  # never blended
    w = section_window(s, 3)
    assert w['tempo_map'][0][0] == 0.0 and w['tempo_map'][-1][0] > 0
    x = np.zeros((2, SR * 12))
    x[:, SR * 4:SR * 6] = 0.4
    y, cut = trim_lead_in(x)
    y, tail = trim_tail(y)
    assert abs(cut - 3.0) < 0.1 and 3.3 < tail < 3.7, (cut, tail)
    print('ok  cinematic journey: acts, dynamics, tempo map, ending, window; lead-in / tail trim')


if __name__ == '__main__':
    main()
