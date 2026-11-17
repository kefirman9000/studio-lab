"""Checks that the genre-specific writing and sound features actually happen (fast: mostly composition, tiny renders).
   python -m tests.features"""
import ast
import os
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from sgcore import samplelibs as _sl  # noqa: E402
_sl.REAL_DIR = os.path.join(ROOT, 'tests', '_no_real_libs')       # same sounds as CI
from sgcore.compose import Options, compose  # noqa: E402
from sgcore.figures import gen_riff, vary_melody  # noqa: E402
from sgcore.theory import Key  # noqa: E402
from sgcore.dsp import SR  # noqa: E402


def song(style, seed=1, **kw):
    return compose(Options(style=style, seed=seed, **kw))


def in_section(e, s):
    return s['bar'] * 4 <= e.beat < (s['bar'] + s['bars']) * 4


def test_metal_riffs():
    k = Key(4, 'minor')
    r = gen_riff('pp.pp.ppX-pp.pp.', k, 0, 38)
    assert [c for _, _, _, c in r].count('p') == 10 and r[6][3] == 'X'
    assert all(38 <= m < 50 for _, _, m, _ in r) and len({m for _, _, m, _ in r}) == 1     # chugs + chord on the root
    for st in ('metal', 'punk'):
        s = None
        for seed in range(1, 6):                       # riffs live in the verses; find a song that has one
            s = song(st, seed)
            pm = [e for e in s['events'] if e.track == 'chords' and e.mod == 'pm']
            if pm:
                break
        assert pm, st
        assert all(e.dur <= 0.3 for e in pm), st                                        # palm mutes are choked
        assert any(t['name'] == 'chords' and t.get('amp', 0) >= 24 for t in s['st']['tracks']), st   # high-gain amp
    print('ok  metal / punk: palm-muted riffs, power chords, high-gain amp')


def test_tuned_hard_kicks():
    for st in ('hardstyle', 'gabber', 'psytrance'):
        for seed in (1, 2, 3):
            s = song(st, seed)
            f = s['st']['kitparams']['kick']['pitch']
            m = 69 + 12 * np.log2(f / 440.0)
            assert abs(m - round(m)) < 0.01 and round(m) % 12 == s['key'].root % 12, (st, f, s['key'].root)
            assert 28 <= round(m) <= 39
    assert song('hardstyle')['st']['kitparams']['kick'].get('tail') == 1.0
    assert song('gabber')['st']['kitparams']['kick'].get('tail') == 2.0
    print('ok  hard dance kicks tuned to the key (hardstyle, gabber, psytrance)')


def test_classical_forms():
    k = Key(0, 'major')
    theme = [(0, 2, 60, 1.0), (2, 1, 64, 1.0), (3, 1, 67, 1.0)]
    d = vary_melody(theme, 'dim', k)
    assert len(d) > len(theme) and [n for b, _, n, _ in d if b in (0, 2, 3)] == [60, 64, 67]   # theme kept on the beats
    assert all((n % 12) in (0, 2, 4, 5, 7, 9, 11) for _, _, n, _ in d)                     # ornaments stay in the key
    forms = set()
    for st, want in (('baroque', {'binary', 'prelude'}), ('classical_period', {'theme_var', 'sonata'}),
                     ('romantic', {'lyric', 'cinematic'}), ('impressionism', {'arch', 'orchestral'})):
        got = {song(st, seed)['st']['form'] for seed in range(1, 9)}
        assert got <= want and len(got) == 2, (st, got)
        forms |= got
    tv = next(s for s in (song('classical_period', seed) for seed in range(1, 9)) if s['st']['form'] == 'theme_var')
    tonic = tv['key'].root % 12
    for sec in tv['sections']:
        lead = [e for e in tv['events'] if e.track == 'lead' and in_section(e, sec)]
        if sec['opts'].get('var') == 'bass':                       # the theme moved to the bass, the top rests
            assert not lead, sec['name']
        elif sec['opts'].get('cad') and lead:                      # the melody comes home on the tonic
            assert max(lead, key=lambda e: e.beat).midi % 12 == tonic, sec['name']
    mn = song('minuet')
    assert mn['st']['form'] == 'minuet' and [s['name'] for s in mn['sections']].count('trio') == 1
    print('ok  classical forms: binary, prelude, theme & variations, sonata, lyric, arch, minuet; cadences')


def test_latin_figures():
    s = song('salsa', 2)
    arp = [e for e in s['events'] if e.track == 'arp']
    assert arp
    by_beat = {}
    for e in arp:
        by_beat.setdefault(round(e.beat, 4), []).append(e.midi)
    assert all(len(v) == 2 and abs(v[0] - v[1]) == 12 for v in by_beat.values())     # montuno: octaves
    af = song('afrobeats', 1)
    assert any(t['name'] == 'arp' and t['inst'] == 'guitar' for t in af['st']['tracks'])
    print('ok  salsa piano montuno in octaves, afrobeats guitar')


def test_dsp_effects():
    from sgcore.render import leslie, metal_amp
    from sgcore.dsp import dub_delay, make_spring_ir
    t = np.arange(SR) / SR
    x = np.vstack([np.sin(2 * np.pi * 1000 * t)] * 2).astype(np.float32) * 0.5
    y = leslie(x, 6.5)
    env = np.abs(y[0][SR // 4:])
    blocks = env[:len(env) // 400 * 400].reshape(-1, 400).max(axis=1)
    assert blocks.max() / blocks.min() > 1.2                              # the rotor swirl modulates the level
    assert np.max(np.abs(y)) <= np.max(np.abs(x)) + 1e-6
    g = metal_amp(x * 0.1, 32)
    assert g.shape == x.shape and np.all(np.isfinite(g))
    imp = np.zeros((2, SR * 2))
    imp[:, 0] = 1.0
    d = dub_delay(imp, 0.3)
    taps = [float(np.max(np.abs(d[:, int(k * 0.3 * SR) - 50:int(k * 0.3 * SR) + 400]))) for k in (1, 2, 3)]
    assert taps[0] > taps[1] > taps[2] > 0                               # repeats that decay
    ir = make_spring_ir(1.8)
    assert ir.shape[0] == 2 and np.all(np.isfinite(ir))
    print('ok  Leslie, high-gain amp, dub delay, spring reverb')


def test_section_loop():
    from sgcore.api import generate, wrap_loop
    x = np.ones((2, SR * 3), dtype=np.float32) * 0.1
    y = wrap_loop(x, 2.0)
    assert y.shape[-1] == 2 * SR and np.allclose(y[:, :SR], 0.2) and np.allclose(y[:, SR:], 0.1)   # tail folded onto the start
    out = tempfile.mkdtemp()
    info = generate(dict(style='house', seed=3), out, section=1, loop=True, log=lambda *a: None)
    s = song('house', 3)
    bars = min(s['sections'][1]['bars'], 8)
    assert abs(info['loop_seconds'] - bars * 4 * 60.0 / s['bpm']) < 0.002, (info['loop_seconds'], bars, s['bpm'])
    print('ok  seamless section loop (exact length, tail wrapped)')


def test_styles_self_contained():
    """Every genre is defined in one place: no statements patching a genre after its style() call."""
    path = os.path.join(ROOT, 'sgcore', 'styles.py')
    tree = ast.parse(open(path).read())
    bad = []
    for n in tree.body:
        tgts = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, ast.AugAssign) else []
        for t in tgts:
            if not isinstance(t, (ast.Subscript, ast.Attribute)):
                continue                                   # plain 'STYLES = {}' is fine
            while isinstance(t, (ast.Subscript, ast.Attribute)):
                t = t.value
            if isinstance(t, ast.Name) and t.id in ('STYLES', 'POOLS', 'LABELS'):
                bad.append(n.lineno)
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute):
            r = n.value.func.value
            while isinstance(r, (ast.Subscript, ast.Attribute)):
                r = r.value
            if isinstance(r, ast.Name) and r.id in ('STYLES', 'POOLS', 'LABELS'):
                bad.append(n.lineno)
    assert not bad, f'styles.py patches genres after their definition at lines {bad} - edit the style() call instead'
    from sgcore.styles import STYLES, POOLS, LABELS
    assert set(POOLS) <= set(STYLES) and set(LABELS) <= set(STYLES)
    print('ok  styles.py: every genre defined in one place')


def test_contrabassoon_role():
    from sgcore.vstrigs import _user_sounds
    sounds = [dict(name='BBC contrabassoon', ok=1), dict(name='BBC bassoon', ok=1)]
    assert _user_sounds('bassoon', sounds)[0][0]['name'] == 'BBC bassoon'
    assert _user_sounds('contrabassoon', sounds)[0][0]['name'] == 'BBC contrabassoon'
    from sgcore.styles import STYLES
    cb = next(t for t in STYLES['cinematic_journey']['tracks'] if t['name'] == 'cbsn')
    assert cb.get('rig_role') == 'contrabassoon'
    print('ok  bassoon and contrabassoon parts pick their own saved sounds')


def test_drum_kits():
    from sgcore import drumkits
    from sgcore.instruments import KITS
    for e in drumkits.KIT_MENU:                          # every kit's synth preset exists
        assert e[3] in KITS or e[3] == 'acoustic', e
    d = song('dnb', 2)
    tr = {t['name']: t for t in d['st']['tracks']}
    assert d['st']['kit_id'] == 'dnb_rollers' and tr['lkick'].get('synth') and tr['kick'].get('hp')     # layered two-step
    assert d['st']['kick_track'] == 'lkick' and any(e.track == 'lsnare' for e in d['events'])
    for k, st in (('jungle_raw', 'jungle'), ('neuro', 'neurofunk'), ('liquid', 'liquid_dnb')):
        assert song(st, 1)['st']['kit_id'] == k, st
    for k in ('cr78', '707', 'dmx', 'unruly', 'big80s'):
        assert song('pop', 1, kit=k)['st']['kit_id'] == k
    from sgcore.render import crush, tame_transient
    x = np.sin(np.linspace(0, 200, 4000)).astype(np.float32)
    assert crush(x, 8, 22050).shape == x.shape
    spike = np.r_[np.ones(10), np.full(8000, 0.02)].astype(np.float32)
    assert tame_transient(spike, 13, 6).shape == spike.shape
    print('ok  drum kits: DnB layered two-step, new machines, real kits, snare swaps')


def test_new_genres():
    from sgcore.styles import STYLES
    from sgcore.instruments import INSTRUMENTS, DRUMS
    for i in ('mandolin', 'tinwhistle', 'pipes', 'drone', 'sitar', 'tanpura', 'koto', 'whine', 'talkbox'):
        y = INSTRUMENTS[i](64, 0.8, {}, 60, None)
        assert np.all(np.isfinite(y)) and np.max(np.abs(y)) > 0.01, i
    for d in ('bodhran', 'timbale', 'tabla', 'bayan'):
        assert np.max(np.abs(DRUMS[d]({}))) > 0.01, d
    names = ('deep_dubstep_rollers', 'sunny_melodic_house', 'bedroom_pop', 'electro_funk', 'ambient_beat', 'ps1_game', 'soca',
             'raga_fusion', 'japanese_zen', 'alt_rock_90s', 'nineties_club_house', 'hopecore', 'hopecore_dreamy', 'jam_rock_80s')
    for n in names:
        assert n in STYLES, n
    bg = song('bluegrass', 2)
    trk = {e.track for e in bg['events']}
    assert {'solo_banjo', 'solo_mando', 'gtr'} <= trk, trk                     # breaks go round the band; guitar boom-chick
    assert any(e.track == 'chords' for e in bg['events'])
    f = song('funk', 2)
    horns = [e for e in f['events'] if e.track == 'horns']
    assert horns and all(e.dur <= 0.23 for e in horns)                         # horn stabs on the accents only
    j = song('celtic_jig', 1)
    assert j['st']['form'] == 'jig' and [s_['name'] for s_ in j['sections']][:4] == ['A', 'A', 'B', 'B']
    pads = {e.midi % 12 for e in j['events'] if e.track == 'pad'}
    assert pads == {j['key'].root % 12}                                         # the pipes drone on the tonic
    g = song('g_funk', 2)
    assert sum(1 for e in g['events'] if e.track == 'lead' and e.glide is not None) > 10   # the whine glides
    a = song('ambient', 2)
    arp = sorted(e.beat for e in a['events'] if e.track.startswith('arp'))
    assert arp
    print('ok  new instruments, reference genres, bluegrass breaks, funk horns, jig form + drone, G-funk glide')


def main():
    test_metal_riffs()
    test_tuned_hard_kicks()
    test_classical_forms()
    test_latin_figures()
    test_dsp_effects()
    test_section_loop()
    test_styles_self_contained()
    test_contrabassoon_role()
    test_drum_kits()
    test_new_genres()
    print('all good')


if __name__ == '__main__':
    main()
