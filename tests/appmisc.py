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
    print('all good')


def test_journey():
    import numpy as np
    from sgcore import samplelibs
    samplelibs.REAL_DIR = '_no_real_libs'
    from sgcore.compose import compose, Options, tempo_seconds, section_window
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
