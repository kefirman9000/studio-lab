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


def test_builds_and_transitions():
    from sgcore.arrange import BUILD_STYLES, FX_SOUNDS, build_sequence, NATURAL_BUILDS
    import random
    for bs in BUILD_STYLES:                                  # every build style composes
        for st_ in ('house', 'rock'):
            song(st_, 2, build_style=bs)
    for st_ in ('trance', 'pop', 'dnb'):
        off = song(st_, 3, builds='off', transition_fx='off')
        assert not [f for f in off['fx'] if f[0] in ('riser', 'swell', 'wash', 'cymroll', 'tapestop', 'hpsweep', 'downlift')]
        assert set(off['st'].get('builds_used', [])) <= {'none'}
        fills = song(st_, 3, transition_fx='fills')
        last = max(s_['bar'] for s_ in fills['sections']) * 4
        assert not [f for f in fills['fx'] if f[0] in FX_SOUNDS and f[1] < last]
    seq = build_sequence('roll', False, random.Random(1), n=4, amount='subtle')
    assert all(b in NATURAL_BUILDS for b in seq) and all(a != b for a, b in zip(seq, seq[1:]))
    seq = build_sequence('roll', False, random.Random(4), n=4)
    assert len(set(seq)) == 4                                # each build in a song is a different one
    kinds = set()
    for seed in range(8):
        kinds |= {f[0] for f in song('house', seed)['fx']}
    assert len({'wash', 'cymroll', 'tapestop', 'swell', 'riser', 'downlift'} & kinds) >= 3   # varied lead-ins
    print('ok  build-ups: off / subtle / 23 styles; transition FX: fewer / fills / off; varied lead-ins')


def test_amen_and_groups():
    from sgcore import drumkits
    from sgcore.styles import STYLES
    from sgcore.genre_groups import GROUP_OF, GROUPS
    import random
    st = {'break_chop': 0.6, 'break_seq': drumkits.BREAKS['amen']['drums']}
    roles = drumkits._slice_roles(st['break_seq'])
    rnd = random.Random(3)
    for bar in range(200):
        m = drumkits.chop_map(st, bar, rnd, 0.9, bar % 8 + 1)
        assert len(m) == 4 and all(sl in roles for sl in m)
    j = song('jungle', 5)
    mods = {e.mod for e in j['events'] if e.track in ('snare', 'kick') and e.mod}
    assert mods and any(str(m).startswith('pt:') for m in mods)       # snare rushes / edits on phrase ends
    from sgcore.render import drum_mod
    x = np.random.randn(8000).astype(np.float32)
    r = drum_mod(x, 'rev')
    assert r[0] == 0 and r[-1] == x[0] and len(drum_mod(x, 'pt:12')) < len(x)      # fades in, ends on the hit
    assert set(GROUP_OF) == set(STYLES)                       # every genre is filed in exactly one group
    assert sum(len(ids) for cat in GROUPS.values() for _, ids in cat) == len(STYLES)
    for cat, gs in GROUPS.items():
        assert all(STYLES[k]['category'] == cat for _, ids in gs for k in ids)
    p = song('piano_miniature', 2, variety=0.95)
    assert {t['layer'] for t in p['st']['tracks']} == {'bass', 'arp', 'lead'} and not [f for f in p['fx'] if f[0] != 'fade']
    assert all('piano' in t['inst'] for t in p['st']['tracks'])
    print('ok  amen: backbeat-aware chops, phrase-end edits; genre groups; solo piano miniature')


def test_no_console_windows():
    """Every helper program (ffmpeg, the plugin worker, git, Defender ...) starts hidden on Windows."""
    import re
    for fn in sorted(os.listdir(os.path.join(ROOT, 'sgcore'))):
        if not fn.endswith('.py') or fn in ('proc.py',):
            continue
        src = open(os.path.join(ROOT, 'sgcore', fn), encoding='utf-8').read()
        for m in re.finditer(r'subprocess\.run\(', src):
            k, depth = m.end(), 1
            while depth:
                depth += (src[k] == '(') - (src[k] == ')')
                k += 1
            call = src[m.start():k]
            assert 'NOWIN' in call or 'creationflags' in call or "'hdiutil'" in call or "'pkgutil'" in call, (fn, call[:80])
    print('ok  helper programs run without console windows on Windows')


def test_editor_and_sounds():
    """Every sound in a song is listed and can be changed / switched off by name; slow pads never play smeared stabs;
    a past project opens from any of its files."""
    from sgcore.api import _tracks
    from sgcore.compose import attack_of
    from sgcore import app
    s = song('future_bass', 1, variety=0.6)
    tr = _tracks(s)
    ids = {t['id'] for t in tr}
    assert {'kick', 'bass', 'chords', 'lead'} <= ids and any(t['id'].endswith('_sw1') for t in tr)
    sw = next(t['id'] for t in tr if t['id'].endswith('_sw1'))
    s2 = song('future_bass', 1, variety=0.6, instruments={sw: 'off'})
    assert not [e for e in s2['events'] if e.track == sw]
    for st_ in ('melodic_techno', 'ukgarage', 'disco_funk', 'future_garage'):
        x = song(st_, 1, variety=0.6)
        for t in x['st']['tracks']:
            if t['layer'] in ('chords', 'pad') and attack_of(t) >= 0.3:
                assert all(abs(e.beat - round(e.beat)) < 1e-6 for e in x['events'] if e.track == t['name']), (st_, t['name'])
    assert app.project_base('Night_house_C-minor_124bpm_seed5_PLUGIN_GUIDE.txt') == 'Night_house_C-minor_124bpm_seed5'
    assert app.project_base(r'C:\\songs\\Night_house_seed5.mp3') == 'Night_house_seed5'
    tmp = tempfile.mkdtemp()
    old = app.out_dir
    app.out_dir = lambda: tmp
    try:
        import json
        with open(os.path.join(tmp, 'Night_house_seed5_settings.json'), 'w') as f:
            json.dump(dict(options=dict(style='house', seed=5), info=dict(style='house', seed=5, sections=[])), f)
        open(os.path.join(tmp, 'Night_house_seed5.mp3'), 'wb').close()
        p = app.open_project('Night_house_seed5.mp3')
        assert p['found'] and p['options']['style'] == 'house' and p['urls'].get('mp3')
        p = app.open_project('elsewhere.json', dict(options=dict(style='trap', seed=3)))
        assert not p['found'] and p['options']['style'] == 'trap'
        try:
            app.open_project('missing.wav')
            raise AssertionError('should fail')
        except ValueError:
            pass
    finally:
        app.out_dir = old
    print('ok  editor: every sound listed + changeable by name, held pad chords, open a past project from any file')


def test_reference_genres():
    """The reference-built genres follow their records' structures."""
    from sgcore.styles import STYLES
    new = ['bass_house', 'club_pop', 'future_garage', 'glitch_pop', 'uk_bass_130', 'nu_disco', 'lofi_rock', 'new_age_chant',
           'smooth_90s_rap', 'sophisti_pop', 'early_dubstep', 'folk_jam', 'garage_house', 'hard_trap', 'wonky_beats',
           'field_ambient', 'trance_pop_90s', 'bay_rap', 'bassline_140', 'midfi_synthfunk', 'piano_house_90s',
           'futuristic_bounce', 'soul_sample_rap', 'tokyo_deep_house', 'psych_pop', 'boogie_rock', 'grime', 'spooky_surf',
           'nu_metal', 'switch_trap', 'mallet_house', 'hard_trance']
    for g in new:
        assert g in STYLES, g
        x = song(g, 3)
        lo, hi = STYLES[g]['bpm']
        assert lo <= x['bpm'] <= hi and x['events'], g
    d = song('deep_dubstep', 2)
    intro = [s_ for s_ in d['sections'] if s_['name'] == 'intro']
    assert all('kick' not in s_['layers'] for s_ in intro)                         # no kick before the first drop
    assert not [f for f in d['fx'] if f[0] in ('riser', 'impact', 'downlift')]
    h = song('hard_trap', 2)
    assert sum(1 for s_ in h['sections'] if s_['name'] == 'break' and 'kick' not in s_['layers']) >= 4   # 4-bar drop-outs
    t = song('switch_trap', 2)
    stops = [s_ for s_ in t['sections'] if s_['name'] == 'stop']
    assert len(stops) == 2 and not [e for e in t['events'] for s_ in stops if in_section(e, s_)]    # dead silence
    print('ok  32 reference genres; deep dubstep / hard trap / beat-switch structures')


def test_sound_choices():
    """Every genre part offers several idiomatic sounds (its own first); genre-defining ones (808, log drum, solo piano) stay."""
    from sgcore.styles import STYLES, POOLS
    thin = []
    for k, st in STYLES.items():
        if st.get('composer'):
            continue
        main = {t['layer']: t['inst'] for t in st['tracks'] if t['name'] == t['layer']}
        for r, inst in main.items():
            if r not in ('bass', 'chords', 'pad', 'arp', 'lead') or inst.startswith(('real:', 'vst:')):
                continue
            pool = (POOLS.get(k) or {}).get(r) or [inst]
            assert pool[0] == inst, (k, r)
            if len(pool) < 3 and inst not in ('808', 'logdrum', 'piano', 'chipbass', 'chip', 'tanpura', 'koto', 'sinebass', 'upright',
                                              'cello', 'contrabass', 'organ', 'ebass', 'mandolin', 'guitar', 'choir',
                                              'sitar', 'harmonium', 'santoor', 'veena', 'gamelan', 'saz', 'phin', 'khaen', 'tres', 'oud', 'shakuhachi'):
                thin.append((k, r, pool))
    assert len(thin) <= 6, thin
    print('ok  every genre part has idiomatic alternative sounds (re-roll / suggestions)')


def test_traits_and_review():
    """v1.43: genre traits (12 rule categories) on every genre, steering per song; review fixes."""
    import re
    import numpy as np
    from sgcore.compose import Options, compose
    from sgcore.styles import STYLES
    from sgcore.traits import CATEGORIES, all_traits, infer
    from sgcore.instruments import INSTRUMENTS
    from sgcore.dsp import SR
    T = all_traits()
    assert set(T) == set(STYLES)
    for k, tr in T.items():
        for c, (_, vals) in CATEGORIES.items():
            assert tr[c] in vals, (k, c, tr[c])
    assert infer('deep_dubstep', STYLES['deep_dubstep'])['bass'] == 'sub_only'
    # no traits -> identical song; a trait changes it, and the genre's own rules stay untouched
    a = compose(Options(style='house', seed=4))
    b = compose(Options(style='house', seed=4, traits={}))
    assert [(e.track, e.beat, e.midi) for e in a['events']] == [(e.track, e.beat, e.midi) for e in b['events']]
    c = compose(Options(style='house', seed=4, traits={'bass': '808_slide', 'feel': 'robotic', 'energy': 'sudden_contrasts'}))
    assert c['st']['bass_mode'] == '808' and c['st']['swing'] == 0.5
    assert STYLES['house']['bass_mode'] != '808'
    lv = [x['opts'].get('level') for x in c['sections'] if x['name'] in ('break', 'drop')]
    assert 0.5 in lv and 1.0 in lv, lv
    sp = compose(Options(style='house', seed=4, traits={'density': 'sparse'}))
    assert not any(e.track == 'arp' for e in sp['events'])
    s1 = compose(Options(style='trap', seed=9, traits={'_surprise': True}))
    assert len(s1['st'].get('traits_used') or {}) == 2
    # moog bass: sustained by default (filter stays open), the plucked one is its own sound
    def bright(name, at):
        y = INSTRUMENTS[name](36, 1.0, {'cut': 600})
        y = y if y.ndim == 1 else y[0]
        seg = y[int(at * SR):int(at * SR) + 4096] * np.hanning(4096)
        spec = np.abs(np.fft.rfft(seg))
        return float((spec * np.fft.rfftfreq(4096, 1 / SR)).sum() / spec.sum())
    assert bright('moogbass', 0.8) > 1.8 * bright('moogpluck', 0.8)
    assert any(t['inst'] == 'moogpluck' for t in STYLES['g_funk']['tracks'])
    # review additions + no artist / band names in genre descriptions or labels
    for g in ('jump_up', 'dark_synthwave', 'modern_gospel', 'neurofunk_lite'):
        assert g in STYLES and not any(t['inst'] == 'vox' for t in STYLES[g]['tracks']), g
    names = r'Boards of Canada|Kenny G|Skrillex|Excision|Rusko|Weeknd|Dilla|Nujabes|Blackmill|Patsy Cline|Bob Wills|Johnny Cash|Teddy Riley'
    from sgcore.styles import label
    for k, st in STYLES.items():
        assert not re.search(names, st['desc'] + ' ' + str(label(k))), k
    assert STYLES['hauntology']['bpm'] == (78, 96)                   # the original hauntology is left as it was
    assert any(t['name'] == 'texture' for t in STYLES['hauntology_sunlit']['tracks'])
    print('ok  genre traits on every genre + per-song overrides, sustained vs plucked moog bass, review genres, no artist names')


def test_rotation_keeps_genre_sound():
    """v1.43.1: instrument rotation never replaces the genre's own part everywhere, and only swaps within a family."""
    from collections import Counter
    from sgcore.compose import Options, compose, inst_family
    for g, sd in (('lofi', 898228), ('jazz', 203796), ('house', 503576), ('spooky_surf', 640674)):
        for v in (0.5, 0.9):
            s = compose(Options(style=g, seed=sd, variety=v))
            used = Counter(e.track for e in s['events'])
            for t in s['st']['tracks']:
                if t.get('switch_of') in ('lead', 'chords', 'pad', 'arp') and used.get(t['name']):
                    main = next(x for x in s['st']['tracks'] if x['name'] == t['switch_of'])
                    assert used.get(main['name']), (g, v, main['name'], 'never plays')
                    assert inst_family(t['inst']) == inst_family(main['inst']), (g, t['name'], t['inst'], main['inst'])
    print('ok  instrument rotation: the genre sound keeps its sections, swaps stay in the same family')


def test_surf_and_monster_theme():
    """v1.43.2: surf rock in a normal (not double) time feel; the monster TV theme's chromatic riff; bass fallbacks."""
    from sgcore.compose import Options, compose
    from sgcore.styles import STYLES
    from sgcore import soundfont as sfm
    assert STYLES['surf_rock']['bpm'][1] <= 160
    assert not any('xxxxxxxx' in p for p in STYLES['surf_rock']['lead_rh'])
    for sd in (1, 2, 3):
        s = compose(Options(style='monster_theme', seed=sd, variety=0.9))
        b = [e.midi for e in s['events'] if e.track == 'bass']
        steps = {y - x for x, y in zip(b, b[1:])}
        assert {1, -1} <= steps, sd                                   # the half-step crawl is always there
        assert any(e.track == 'riff' for e in s['events'])          # doubled by the twang guitar
        assert not any(t.get('switch_of') for t in s['st']['tracks'])
    for sd in (1, 2, 3):                                            # organ & brass version: same riff, organ + horns up front
        s = compose(Options(style='monster_organ', seed=sd, variety=0.9))
        ins = {t['name']: t['inst'] for t in s['st']['tracks']}
        assert ins['pad'] == 'organ' and ins['arp'] == 'organ' and ins['riff'] == 'twang', ins
        assert ins['chords'] in ('brass', 'sf:trumpetsection', 'synthbrass') and ins['bass'] in ('ebass', 'sf:pickbass', 'sf:fingerbass')
        b = [e.midi for e in s['events'] if e.track == 'bass']
        assert {1, -1} <= {y - x for x, y in zip(b, b[1:])}
        n = {k: sum(e.track == k for e in s['events']) for k in ('pad', 'chords', 'arp', 'lead', 'riff')}
        assert all(n.values()) and n['arp'] >= 120, n                # a busy organ break
    assert sfm.fallback_for('pickbass') == 'pickbass' and sfm.fallback_for('fingerbass') == 'ebass'
    print('ok  surf rock feel, monster TV theme riff, pick / finger bass fall back to a bass (not a synth pluck)')


def test_hindu_devotional():
    """v1.52: bhajan, kirtan, aarti, santoor raga - raga phrasing (a climb to a held peak, a fall home), hand drums and
    hand-drum fills (no rock toms), no EDM effects, the kirtan speeding up, its call answered by the group."""
    from sgcore.compose import Options, compose
    from sgcore.instruments import INSTRUMENTS, DRUMS
    for nm in ('harmonium', 'santoor'):
        assert nm in INSTRUMENTS
    for nm in ('manjira', 'dholak', 'dholak_ta'):
        assert nm in DRUMS
    for g, want in (('bhajan', {'harmonium', 'tanpura'}), ('kirtan', {'harmonium', 'tanpura', 'choir'}),
                    ('aarti', {'harmonium', 'tubular'}), ('santoor_raga', {'santoor', 'tanpura'})):
        for sd in (1, 2):
            s = compose(Options(style=g, seed=sd, energy=0.9))
            ins = {t['inst'] for t in s['st']['tracks']}
            assert want <= ins, (g, ins)
            assert s['st']['lead_device'] == 'raga'
            assert not any(e.track.startswith('tom') for e in s['events']), g
            assert not any(f[0] in ('impact', 'riser', 'swell', 'crash') for f in s['fx']), (g, s['fx'])
            lead = sorted((e for e in s['events'] if e.track == 'lead'), key=lambda e: e.beat)
            longest = max(lead, key=lambda e: e.dur)
            assert longest.dur >= 1.3                                         # held peaks / resting notes
            assert any(e.slide or e.bend for e in lead)                        # meend
    tm = compose(Options(style='kirtan', seed=3))['tempo_map']
    assert tm[-1][1] > tm[0][1] * 1.8                                          # starts slow, ends ecstatic
    k = compose(Options(style='kirtan', seed=3))
    lead = sorted((e.beat, e.midi) for e in k['events'] if e.track == 'lead')
    mids = [m for _, m in lead]
    assert any(mids[i:i + 6] == mids[j:j + 6] for i in range(0, 30) for j in range(i + 6, i + 30))   # the group answers
    for sd in (1, 2, 3):                                                      # stoner rock with Indian instruments
        s = compose(Options(style='stoner_raga', seed=sd, variety=0.9))
        ins = {t['layer']: t['inst'] for t in s['st']['tracks'] if t['layer'] in ('lead', 'pad', 'chords')}
        assert ins == {'lead': 'sitar', 'pad': 'tanpura', 'chords': ins['chords']} and 'guitar' in ins['chords'], ins
        assert {'tabla', 'bayan', 'kick', 'snare'} <= {e.track for e in s['events']}
    drum_layers = {'kick', 'snare', 'top'}
    for g, opener in (('sitar_bhajan', 'sitar'), ('jugalbandi', 'sitar'), ('tabla_bhajan', 'drums'), ('drum_kirtan', 'drums')):
        for sd in (1, 2):                                                     # drum- or sitar-led openings, no violin
            s = compose(Options(style=g, seed=sd, variety=0.9))
            first = s['sections'][0]
            tr = {t['name']: t for t in s['st']['tracks']}
            used = {tr[e.track]['layer'] for e in s['events'] if e.beat < first['bars'] * 4}
            if opener == 'sitar':
                assert used == {'lead', 'pad'} and tr['lead']['inst'] == 'sitar', (g, used)
            else:
                assert used <= drum_layers and len({e.track for e in s['events'] if e.beat < first['bars'] * 4}) >= 4, (g, used)
            assert tr['lead']['inst'] == 'sitar' and not any(t['inst'] in ('violin', 'violins') for t in s['st']['tracks'])
            assert not any(e.track.startswith('tom') for e in s['events'])
    print('ok  Hindu devotional: raga phrasing + meend, hand drums & fills, no EDM fx, kirtan accelerando, call & response')


def test_world_and_rock_genres_153():
    """v1.53: 19 more genres - each with its defining sounds, its own drums, and the right feel."""
    from sgcore.compose import Options, compose
    want = {'qawwali': {'harmonium', 'choir'}, 'bollywood': {'dholak'}, 'carnatic_kriti': {'tanpura'}, 'ghazal': {'sitar', 'harmonium'},
            'anatolian_psych': {'guitar'}, 'ethio_jazz': set(), 'thai_funk': set(), 'chicha': set(),
            'desert_blues': set(), 'exotica': set(), 'garage_rock': {'guitar'}, 'rockabilly': set(),
            'krautrock': set(), 'post_punk': set(), 'flamenco_rumba': set(), 'klezmer': set(), 'gamelan': {'gamelan'},
            'rai': set(), 'son_cubano': set()}  # (defining parts only - the rest may roll alternatives)
    drums = {'qawwali': {'tabla', 'claps'}, 'carnatic_kriti': {'mridangam', 'mridangam_lo'}, 'anatolian_psych': {'darbuka'},
             'thai_funk': {'ching'}, 'chicha': {'timbale', 'guiro'}, 'flamenco_rumba': {'cajon', 'palmas'},
             'gamelan': {'gong', 'kendang'}, 'rai': {'darbuka', 'darbuka_tek'}, 'son_cubano': {'clave', 'bongo'},
             'garage_rock': {'tamb'}, 'exotica': {'conga', 'bongo'}}
    hand = {'qawwali', 'bollywood', 'carnatic_kriti', 'ghazal', 'flamenco_rumba', 'gamelan', 'rai', 'son_cubano'}
    for g, insts in want.items():
        for sd in (1, 2):
            s = compose(Options(style=g, seed=sd))
            ins = {t['inst'] for t in s['st']['tracks']}
            if ins & {'cleanguitar', 'odguitar', 'distguitar', 'sf:cleanguitar', 'sf:odguitar', 'sf:distguitar'}:
                ins.add('guitar')                                          # (any electric guitar amp)
            used = {e.track for e in s['events']}
            assert insts <= ins, (g, ins)
            assert drums.get(g, set()) <= used, (g, used)
            assert any(e.track == 'lead' for e in s['events']), g
            if g in hand:
                assert not any(x.startswith('tom') for x in used), g
    assert compose(Options(style='qawwali', seed=1))['tempo_map'][-1][1] > compose(Options(style='qawwali', seed=1))['bpm'] * 1.3
    k = compose(Options(style='klezmer', seed=2))
    assert k['tempo_map'][0][1] == k['bpm'] * 0.5 and k['tempo_map'][-1][1] == k['bpm']          # slow doina, then the dance
    gm = compose(Options(style='gamelan', seed=1))
    assert gm['key'].scale_name == 'pelog'
    sl = [t['inst'] for s_ in (1, 2, 3) for t in compose(Options(style='ghazal', seed=s_))['st']['tracks'] if t['name'] == 'lead']
    assert set(sl) == {'sitar'}
    print('ok  19 world / rock genres: defining sounds, own drums, qawwali speeds up, klezmer doina -> dance, gamelan pelog')


def test_sung_vocals():
    """v1.54: sung vocals on the song's melody - in tune, every voice, lyrics turned into syllables; genres without a
    guide melody sing the lead line."""
    import numpy as np
    from sgcore.compose import Options, compose
    from sgcore.render import Renderer
    from sgcore.daisy import syllables, sing_part
    assert syllables('Oh my love') == ['oU', 'm aI', 'l V v'] and syllables('la la') == ['l a', 'l a']
    notes = [(i * 0.6, 0.5, m) for i, m in enumerate([60, 64, 67, 72])]
    for v in ('female', 'male', 'choir', 'robot'):
        y = sing_part(notes, 'aah', v, seed=1)
        assert y.shape[0] == 2 and np.isfinite(y).all() and np.abs(y).max() > 0.5, v
    y = sing_part(notes, 'aah', 'female', seed=1)[0]
    for s0, d, m in notes:                                       # every note on pitch
        seg = y[int((s0 + 0.15) * 44100):int((s0 + 0.4) * 44100)]
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, 'full')[len(seg) - 1:]
        lag = 44 + int(np.argmax(ac[44:630]))
        assert abs(69 + 12 * np.log2(44100 / lag / 440) - m) < 0.5, m
    for style in ('pop', 'bhajan'):                              # bhajan: no guide sections - the singer takes the melody
        song = compose(Options(style=style, seed=4, vocals='lyrics', voice='choir', lyrics='hare krishna hare rama'))
        tr = {t['name']: t for t in song['st']['tracks']}
        assert tr['vocal']['inst'] == 'sung' and tr['vocal']['p']['voice'] == 'choir'
        voc = [e for e in song['events'] if e.track == 'vocal']
        assert len(voc) > 20 and all(48 <= e.midi <= 84 for e in voc)
        r = Renderer(song, log=lambda *a: None)
        buf = r.render_track(tr['vocal'], voc[:12])
        assert np.abs(buf).max() > 0.05
    assert not any(t['name'] == 'vocal' for t in compose(Options(style='pop', seed=4))['st']['tracks'])
    print('ok  sung vocals: in tune, 4 voices, lyrics -> syllables, melody fallback for genres without a guide')


def test_reference_genre_match():
    """v1.54: a reference song gets genre suggestions - a rendered house song and a rendered surf song each find their
    own genre family near the top (drum feel, tempo, key and sound)."""
    import tempfile
    import shutil
    import numpy as np
    from scipy.io import wavfile
    from scipy import signal
    from sgcore.api import generate
    from sgcore.analysis import analyze
    from sgcore.styles import STYLES, LABELS
    from sgcore import genrematch as gm
    fam = {'house': {'house', 'deep_house', 'tech_house', 'progressive_house', 'nineties_club_house', 'garage_house', 'piano_house_90s',
                     'disco', 'nu_disco', 'french_house', 'minimal', 'bass_house', 'pop_house_90s', 'melodic_house', 'organic_house',
                     'sunny_melodic_house', 'tokyo_deep_house', 'mallet_house', 'italo_disco', 'afro_house', 'acid_house', 'techno',
                     'eurodance', 'bigroom', 'melodic_techno'},
           'trap': {'trap', 'uk_drill', 'phonk', 'memphis_phonk', 'plugg', 'rage', 'cloud_rap', 'luxury_rap', 'latin_trap', 'bass_warp_trap',
                    'switch_trap', 'hard_trap', 'orchestral_hiphop', 'drill', 'brazilian_phonk', 'house_phonk', 'witch_house'}}
    d = tempfile.mkdtemp()
    try:
        for style in ('house', 'trap'):
            info = generate(dict(style=style, seed=77), d, preview=True, outputs=['wav'], log=lambda *a: None)
            sr, x = wavfile.read(info['files']['wav'])
            x = signal.resample_poly(x.astype(np.float32).mean(axis=1), 1, 2)
            a = analyze(x, 22050)
            gm.analyze_reference(x, 22050, a)
            top = [g['id'] for g in gm.suggest(a, STYLES, LABELS, top=6)]
            assert set(top) & fam[style], (style, top)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    fp = gm.fingerprints()
    missing = [s for s, st in STYLES.items() if not st.get('composer') and s not in fp]
    assert not missing, f'no fingerprint for {missing[:8]} - run python tools/genre_fingerprints.py'
    print('ok  reference -> genre suggestions (house and trap find their families); every genre has a fingerprint')


def test_shakuhachi_genres():
    """v1.54: the 80s sampled shakuhachi - it scoops up into the note; it leads 80s adult pop and answers the horns in
    smooth jazz."""
    import numpy as np
    from sgcore.compose import Options, compose
    from sgcore.instruments import INSTRUMENTS
    y = INSTRUMENTS['shakuhachi'](72, 1.2, {})[0]

    def f0(seg):
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, 'full')[len(seg) - 1:]
        return 44100 / (29 + int(np.argmax(ac[29:220])))
    start, held = (69 + 12 * np.log2(f0(y[int(t * 44100):int(t * 44100) + 2048]) / 440) for t in (0.01, 0.5))
    assert start < 71.6 and abs(held - 72) < 0.4, (start, held)                 # meri: starts flat, settles in tune
    for sd in (1, 2, 3):
        p = compose(Options(style='shakuhachi_pop', seed=sd))
        assert {t['name']: t['inst'] for t in p['st']['tracks']}['lead'] == 'shakuhachi' and p['st'].get('gated_snare')
        j = compose(Options(style='smooth_jazz_horns', seed=sd))
        assert sum(e.track == 'horns' for e in j['events']) > 20 and any(e.track == 'arp' for e in j['events'])
    print('ok  shakuhachi: meri scoop; 80s gated pop lead; smooth jazz horns + shakuhachi answers')


def test_meend_gamak():
    """v1.54: Indian ornaments - meend pulls from the previous note, gamak shakes up to the note above; only bendable
    instruments; the Bends setting scales them; previews keep them."""
    from sgcore.compose import Options, compose
    from sgcore.render import bend_curve
    from sgcore.windows import preview_window
    def count(o):
        s = compose(Options(**o))
        lead = [e for e in s['events'] if e.track == 'lead' and e.midi is not None]
        return s, sum(1 for e in lead if e.bend), len(lead)
    s, n, tot = count(dict(style='sitar_bhajan', seed=3))
    assert n > tot * 0.15, (n, tot)
    kinds = {o[0] for e in s['events'] if e.track == 'lead' and e.bend for o in e.bend}
    assert {'meend', 'gamak'} <= kinds, kinds
    assert count(dict(style='sitar_bhajan', seed=3, bends='more'))[1] > n > count(dict(style='sitar_bhajan', seed=3, bends='subtle'))[1]
    assert count(dict(style='sitar_bhajan', seed=3, bends='off'))[1] == 0
    assert count(dict(style='house', seed=3))[1] == 0                               # not every genre
    assert not any(e.bend for e in s['events'] if e.track == 'chords')               # harmonium can't bend
    assert any(e.bend for e in preview_window(s)['events'])                          # previews keep the ornaments
    c = bend_curve([('meend', -3.0, 0.5), ('gamak', 2.0, 5.5)], 44100, 1.0)
    assert c[0] < -2.9 and abs(c[int(0.5 * 44100)]) < 2.1 and c[int(0.4 * 44100):].max() > 1.5
    print('ok  meend / gamak / andolan: on sitar & co, scaled by Bends, kept in previews')


def test_v144_drums_layers_new_genres():
    """v1.44: editor drum swaps / kick off, no hit+swell layer flams, liquid DnB + boogie genres, UI parts panel."""
    from sgcore.compose import Options, compose, attack_class
    s = compose(Options(style='house', seed=4, instruments={'clap': 'rim', 'chat': 'shaker', 'kick': 'off'}))
    tr = {t['name']: t for t in s['st']['tracks']}
    assert tr['clap']['inst'] == 'rim' and tr['chat']['inst'] == 'shaker' and not any(e.track == 'kick' for e in s['events'])
    for g in ('breakcore', 'dnb', 'pop', 'trance'):
        for sd in range(1, 8):
            s = compose(Options(style=g, seed=sd, variety=0.9))
            tr = {t['name']: t for t in s['st']['tracks']}
            for t in s['st']['tracks']:
                if t.get('double_of') and t['layer'] in ('chords', 'arp'):
                    assert attack_class(t['inst']) == attack_class(tr[t['double_of']]['inst']), (g, sd, t['inst'])
    for g in ('liquid_euphoric', 'liquid_dancefloor'):
        s = compose(Options(style=g, seed=3))
        bars = sum(x['bars'] for x in s['sections'])
        assert 200 <= bars <= 240 and 174 <= s['bpm'] <= 176, (g, bars)
        assert not any(e.track.startswith('bass') for e in s['events'] if e.beat < s['sections'][1]['bar'] * 4)   # no bass in the intro
    s = compose(Options(style='boogie_blues_rock', seed=1))
    b = [e.midi for e in sorted((e for e in s['events'] if e.track == 'bass'), key=lambda e: e.beat)][:8]
    assert [x - b[0] for x in b] == [0, 0, 4, 4, 7, 7, 9, 9], b                 # the boogie riff climbs root-3-5-6
    assert s['key'].root in (4, 7, 9, 2)
    ui = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sgcore', 'ui.html'), encoding='utf-8').read()
    assert ui.index('<summary>Basics</summary>') > ui.index('<summary>Mix &amp; master</summary>')
    assert 'volHtml(r)' in ui and 'id="levels"' not in ui and 'id="edKit"' in ui
    print('ok  editor drum swaps, no flam layers, liquid DnB x2, boogie riff + keys, unified parts panel')


def test_bass_warp_trap():
    """v1.44.1: bass-warp trap - warped 808 notes (dives, rises, wobbles, growls), slides, switch-up sections where the
    808 jumps up with no sub, and the warps really bend the pitch."""
    import numpy as np
    from collections import Counter
    from sgcore.compose import Options, compose
    from sgcore.instruments import INSTRUMENTS
    from sgcore.dsp import SR
    s = compose(Options(style='bass_warp_trap', seed=3))
    b = [e for e in s['events'] if e.track in ('bass', 'bass_hi')]
    kinds = Counter(str(e.mod).split(':')[0] for e in b if e.mod)
    assert {'dive', 'rise', 'wob', 'growl'} <= set(kinds), kinds
    assert sum(e.glide is not None for e in b) > 10
    for x in s['sections']:
        notes = [e.midi for e in b if x['bar'] * 4 <= e.beat < (x['bar'] + x['bars']) * 4]
        if x['opts'].get('bass_up') and notes:
            assert min(notes) >= 40, (x['name'], min(notes))
    def f0(y, a, b_):
        seg = y[int(a * SR):int(b_ * SR)]
        z = np.where(np.diff(np.signbit(seg)))[0]
        return SR / (2 * np.mean(np.diff(z))) if len(z) > 4 else 0
    y = INSTRUMENTS['808'](33, 1.0, {}, None, 'dive')
    assert f0(y, 0.85, 0.98) < 0.8 * f0(y, 0.05, 0.3)                # the dive really falls
    y = INSTRUMENTS['808'](33, 1.0, {}, None, 'rise')
    assert f0(y, 0.85, 0.98) > 1.3 * f0(y, 0.05, 0.3)
    f = compose(Options(style='bass_warp_fast', seed=3))
    assert 155 <= f['bpm'] <= 165
    for x in f['sections']:
        if x['opts'].get('bass_mod') == 'growl':
            bn = [e for e in f['events'] if e.track == 'bass' and x['bar'] * 4 <= e.beat < (x['bar'] + x['bars']) * 4]
            assert bn and all(e.mod == 'growl' for e in bn)          # the long distorted-808 stretch
    assert any(e.track == 'bass_grit' for e in f['events'])                 # parallel driven 808 layer
    assert any(e.track == 'chat' and str(e.mod).startswith('pt:') for e in f['events'])   # pitched hat rolls
    assert not any(e.track.endswith('_layer') for e in f['events'])
    for x in (s, f):                                                      # the 808 stays low; raised / leaping notes
        b8 = [e for e in x['events'] if e.track == 'bass']                 # go to a mid-bass (reese / growl / FM)
        hb = [e for e in x['events'] if e.track == 'bass_hi']
        assert b8 and hb and max(e.midi for e in b8) < 38 and 38 <= min(e.midi for e in hb) and max(e.midi for e in hb) <= 52
        assert next(t for t in x['st']['tracks'] if t['name'] == 'bass_hi')['inst'] in ('midbass', 'reese')
        assert not any(e.track == 'bass_grit' and e.midi >= 38 for e in x['events'])
    print('ok  bass-warp trap (+ fast): warped 808s, slides, 808-up / growl switch-ups, parallel grit, pitched hat rolls')


def test_switchup_808():
    """v1.56: switch-up 808 - the 808 switches up nearly every bar (grinds, leaps, rolls, gaps, stops, folds ...), never
    repeats the bar before for long, keeps leaps as leaps in the raised no-sub sections, and the fold mod buzzes."""
    import numpy as np
    from sgcore.compose import Options, compose
    from sgcore.instruments import INSTRUMENTS
    from sgcore.styles import STYLES
    assert 155 <= STYLES['switchup_808']['bpm'][0] and STYLES['switchup_808']['bass_lo'] <= 24
    for seed in (3, 11):
        s = compose(Options(style='switchup_808', seed=seed))
        b = [e for e in s['events'] if e.track in ('bass', 'bass_hi')]
        sig = {}
        for e in b:
            sig.setdefault(int(e.beat // 4), []).append((round(e.beat % 4, 2), e.midi, e.mod))
        bars = sorted(sig)
        same = sum(sig[a] == sig[c] for a, c in zip(bars, bars[1:]))
        assert same <= 2, same                                        # no two bars alike (nearly)
        assert len({tuple(v) for v in sig.values()}) > 0.6 * len(bars)
        assert any(e.mod == 'fold' for e in b) and any(e.mod == 'dive' for e in b)
        assert max(e.midi for e in b) - min(e.midi for e in b) >= 20  # octave leaps
        semis = sorted({e.midi - e.glide for e in b if e.glide is not None})
        assert 1 in semis or -1 in semis                              # root / flat-2nd grind
    y = INSTRUMENTS['808'](28, 1.0, {}, None, 'fold')
    c = INSTRUMENTS['808'](28, 1.0, {}, None, None)
    def hi(z):
        sp = np.abs(np.fft.rfft(z))
        return sp[200:].sum() / sp.sum()
    assert hi(y) > 2 * hi(c)                                          # folded = buzzing harmonics
    m = compose(Options(style='switchup_mallets', seed=3))
    a = sorted(e.beat for e in m['events'] if e.track == 'arp')
    step = float(np.median([d for d in np.diff(a) if d > 0])) * 60 / m['bpm']
    assert step < 0.07 and any(e.track == 'arp_hi' for e in m['events'])     # 32nd-note mallet arps, doubled up high
    by = {}
    for e in m['events']:
        if e.track == 'arp':
            by.setdefault(int(e.beat), []).append(e)
    rolls = sum(len(set(x.midi for x in v)) == 1 and len(v) >= 6 for v in by.values())
    trills = sum(len(set(x.midi for x in v)) == 2 for v in by.values())
    beats = range(min(by), max(by))
    rests = sum(1 for k in beats if len(by.get(k, [])) <= 1)
    assert rolls > 10 and trills > 5 and rests > 5, (rolls, trills, rests)   # mallet figures, not one long arpeggio
    assert all(min(x.beat for x in v) == k for k, v in by.items())          # every figure starts on its beat
    assert m['st']['delay_beats'] in (0.5, 1.0)
    h = compose(Options(style='switchup_808_hard', seed=3))
    from sgcore.styles import STYLES as _S
    k = _S['switchup_808_hard']['kit_override']['kick']
    assert k['drive'] >= 4 and k['punch'] >= 200 and _S['switchup_808_hard']['sc_depth'] >= 0.8   # punchy, ducking kicks
    assert sum(e.track == 'kick' for e in h['events']) > sum(e.track == 'kick' for e in s['events'])
    assert compose(Options(style='shadow_808', seed=3))['style'] == 'switchup_808'              # old name still opens
    print('ok  switch-up 808: bar-by-bar 808 switch-ups (grind, leap, roll, gap, stop, fold), no repeated bars')


def test_tanpura_on_the_beat():
    """v1.56: the tanpura plucks one string per grid beat (Pa, Sa, Sa, low Sa) as its own note, so in the genres that
    speed up (jugalbandi 75 -> 109 BPM) it follows the tempo map instead of drifting on a fixed clock."""
    from sgcore.compose import Options, compose
    for g, seed in (('jugalbandi', 920581), ('kirtan', 3), ('santoor_raga', 5)):
        s = compose(Options(style=g, seed=seed))
        names = {e.track for e in s['events'] if e.mod and str(e.mod).startswith('str:')}
        tp = [e for e in s['events'] if e.track in names]
        assert tp, g
        for e in tp:
            assert abs(e.beat - round(e.beat)) < 1e-6 and str(e.mod).startswith('str:'), (g, e.beat, e.mod)
            assert int(str(e.mod)[4:]) == (int(round(e.beat)) // (1 if e.dur < 1.5 else 2)) % 4
    print('ok  tanpura: one string per beat on the grid, following the tempo map')


def test_arabic_maqam():
    """v1.56: Arabic genres - maqam quarter tones on the melody only (Bayati / Rast / Saba), the darbuka / riq / bendir
    rhythms, a taqsim (melody alone over the drone) to open, the Sufi dhikr speeding up, and the new sounds."""
    import numpy as np
    from sgcore.compose import Options, compose
    from sgcore.theory import Key, MAQAM_QUARTER
    from sgcore.render import bend_curve
    from sgcore.instruments import INSTRUMENTS, DRUMS
    assert {'qanun', 'ney'} <= set(INSTRUMENTS) and {'riq', 'bendir', 'bendir_tek'} <= set(DRUMS)
    assert abs(bend_curve([('shift', -0.5)], 100, 1.0).mean() + 0.5) < 1e-9
    seen = set()
    for g in ('takht_maqam', 'raqs_sharqi', 'arab_pop', 'sufi_dhikr'):
        for seed in range(1, 7):
            s = compose(Options(style=g, seed=seed))
            tr = {t['name']: t for t in s['st']['tracks']}
            k = s['key']
            q = MAQAM_QUARTER.get(k.scale_name)
            shifted = [e for e in s['events'] if e.bend and any(b[0] == 'shift' for b in e.bend)]
            assert all(tr[e.track]['layer'] in ('lead', 'arp') or e.track == 'vocal' for e in shifted)
            if q:
                seen.add(k.scale_name)
                assert shifted, (g, seed, k.scale_name)
                pcs = {(k.root + k.scale[d]) % 12 for d in q}
                assert all(e.midi % 12 in pcs for e in shifted)
            else:
                assert not shifted
            if g in ('takht_maqam', 'sufi_dhikr'):
                first = s['sections'][0]
                assert not {'kick', 'snare'} & set(first['layers'])          # the taqsim / ney opening: no drums
    assert seen & {'bayati', 'rast', 'saba'}
    d = compose(Options(style='sufi_dhikr', seed=2))
    assert d['tempo_map'][-1][1] > 1.6 * d['tempo_map'][0][1]                # the dhikr whirls faster and faster
    assert any(e.track == 'bendir' for e in d['events'])
    assert any(e.track == 'riq' for e in compose(Options(style='raqs_sharqi', seed=2))['events'])
    assert Key(0, 'hijaz').scale == [0, 1, 4, 5, 7, 8, 10]
    y = INSTRUMENTS['qanun'](67, 1.5, {}, None, None)
    assert np.isfinite(y).all() and np.abs(y).max() > 0.01
    print('ok  Arabic maqam: quarter tones on the melody, taqsim openings, darbuka / riq / bendir, dhikr accelerando')


def test_voice_sample_chops():
    """v1.56: a voice sample of yours chopped into the song - screwed in phonk / DJ genres (pitched down, caught
    twice), stuttered in club genres, a one-shot or a phrase elsewhere, or played as the melody; the slices render."""
    import tempfile
    import numpy as np
    from sgcore import usersounds
    from sgcore.compose import Options, compose, vox_use_for
    from sgcore.dsp import SR
    old = usersounds.ROOT
    usersounds.ROOT = tempfile.mkdtemp()
    try:
        t = np.arange(int(1.6 * SR)) / SR
        word = np.sin(2 * np.pi * 220 * t) * (np.sin(2 * np.pi * 2.5 * t) > 0)      # three 'syllables'
        name = usersounds.save('vocal', 'bounce it', word.astype(np.float32), 60, 'phrase')
        assert usersounds.listing()['vocal'] == [name] and usersounds.vocal_type(name) == 'phrase'
        L, vt, root, ons = usersounds.vocal_info(name)
        assert 1.2 < L < 1.7 and len(ons) >= 3, (L, ons)
        assert vox_use_for('switchup_808', 'Electronic', 'phrase') == 'screwed'
        assert vox_use_for('jersey_club', 'Electronic', 'phrase') == 'stutter'
        assert vox_use_for('jazz', 'Classic', 'phrase') == 'adlib' and vox_use_for('jazz', 'Classic', 'note') == 'melody'
        for g, use in (('switchup_808_dj', 'auto'), ('uk_bounce_house', 'auto'), ('jazz', 'auto'), ('trap', 'melody'),
                       ('lofi', 'phrase')):
            s = compose(Options(style=g, seed=5, vox_sample=name, vox_use=use))
            v = [e for e in s['events'] if e.track == 'voxsample']
            assert v and any(x['name'] == 'voxsample' for x in s['st']['tracks']), (g, use)
            if g == 'switchup_808_dj':
                assert all(e.midi < 60 for e in v)                          # screwed: pitched down
            if g == 'uk_bounce_house':
                assert len(v) > 40 and min(e.dur for e in v) < 0.3           # stutter chops
        y = usersounds.vocal_slice(name, 'vx:0.000:0.400:0', -4, 2.0)
        assert abs(len(y) / SR - 0.4 * 2 ** (4 / 12)) < 0.02                 # screwed = slower and lower
        assert len(usersounds.vocal_slice(name, 'vx:0.000:0.400:1', 7, 2.0)) < 0.4 * SR
        s = compose(Options(style='switchup_808', seed=5, vox_sample='not there'))
        assert not any(e.track == 'voxsample' for e in s['events'])
    finally:
        usersounds.ROOT = old
    print('ok  voice samples: screwed / stutter / ad-lib / phrase / melody chops, tape-style pitch')


def test_dj_effects():
    """v1.56: DJ edits - pitched hat moves (climb, dive, swoop, octave, rolls), down / up-tuned lead notes, fake DJ
    slowdowns before drops; and 808s driven hard no longer fizz on high notes."""
    import numpy as np
    from collections import Counter
    from sgcore.compose import Options, compose
    from sgcore.render import drum_mod, dj_slow
    from sgcore.instruments import INSTRUMENTS
    from sgcore.dsp import SR
    s = compose(Options(style='switchup_808_dj', seed=4))
    mods = Counter(str(e.mod).split(':')[0] for e in s['events'] if e.track in ('chat', 'ohat') and e.mod)
    assert mods['pt'] > 10 and mods['sw'] > 0, mods
    assert any(e.bend and any(b[0] in ('fall', 'shift', 'meend') for b in e.bend) for e in s['events'] if e.track == 'lead')
    assert any(f[0] == 'djslow' for f in s['fx'])
    for seed in (1, 2, 3):                                                  # chopped & screwed: the same DJ edits, slower
        c = compose(Options(style='screwed_slab', seed=seed))
        assert c['bpm'] <= 72 and any(f[0] == 'djslow' for f in c['fx'])
        assert any(str(e.mod).startswith(('pt:', 'sw:')) for e in c['events'] if e.track == 'chat')
        assert c['st'].get('switchups') and c['st']['master']['vintage_lp'] <= 5000   # dark: low end, not high end
    x = np.sin(2 * np.pi * 440 * np.arange(SR) / SR).astype(np.float32)
    assert drum_mod(x, 'sw:0:-12').shape[-1] == x.shape[-1] - 1 or drum_mod(x, 'sw:0:-12').shape[-1] > 0.6 * SR
    buf = np.vstack([x, x]).copy()
    dj_slow(buf, 0, SR)
    z = buf[0, int(0.8 * SR):int(0.95 * SR)]
    zc = np.sum(np.diff(np.signbit(z))) / 0.15 / 2
    assert zc < 0.6 * 440, zc                                               # pitch sinks towards the end
    def fizz(m):
        y = INSTRUMENTS['808'](m, 0.6, dict(drive=8.0, decay=0.3), None, 'growl')
        sp = np.abs(np.fft.rfft(y[:int(0.5 * SR)])) ** 2
        f = np.fft.rfftfreq(int(0.5 * SR), 1 / SR)
        return sp[f > 5000].sum() / sp.sum()
    assert fizz(58) < 1e-3, fizz(58)
    print('ok  DJ edits: pitched hats, tuned leads, slowdowns before drops; no fizz on driven high 808 notes')


def test_idm_drill():
    """v1.56.5: IDM jungle theme + drill & bass (from the user's references and notes): an intro on the synths alone,
    breaks resequenced so no two drum bars repeat (flams, stutters, reversed / re-pitched hits, ghost fills), long calm
    melody notes over them, a melodic bass guitar, a key change in the theme genre."""
    from sgcore.compose import Options, compose
    for g in ('idm_jungle_theme', 'drill_space'):
        s = compose(Options(style=g, seed=1))
        first = s['sections'][0]
        assert not {'kick', 'snare', 'bass'} & set(first['layers'])          # the moody synth intro
        sig = {}
        for e in s['events']:
            if e.track in ('kick', 'snare', 'chat'):
                sig.setdefault(int(e.beat // 4), []).append((e.track, round(e.beat % 4, 3), str(e.mod)))
        assert len({tuple(sorted(v)) for v in sig.values()}) >= 0.95 * len(sig)   # the break never loops
        mods = [str(e.mod) for e in s['events'] if e.track in ('kick', 'snare') and e.mod]
        assert any(m == 'rev' for m in mods) and any(m.startswith('pt:') for m in mods) and mods.count('cut') > 50
        lead = [e.dur for e in s['events'] if e.track == 'lead']
        assert lead and sorted(lead)[len(lead) // 2] >= 1.0                  # calm, long melody notes over the chaos
        assert next(t for t in s['st']['tracks'] if t['name'] == 'bass')['inst'] in ('sf:fingerbass', 'ebass', 'fmbass', 'moogbass', 'sinebass')
    t = compose(Options(style='idm_jungle_theme', seed=1))
    assert any(x.get('key_change') for x in t['sections'])
    print('ok  IDM jungle theme / drill & bass: synth intro, resequenced breaks, calm melody, key change')


def test_math_rock_meters():
    """v1.56.6: math rock - bars of 7/8, 3/4 and 5/8 between the 4/4 ones (cut short and played faster, so each 16th
    keeps its length), a tapping guitar looping 5-8 note cells across the bar lines; and the reference-batch genres."""
    from sgcore.compose import Options, compose
    from sgcore.windows import tempo_seconds
    s = compose(Options(style='math_rock', seed=2))
    m = s.get('meters') or {}
    assert m and set(m.values()) <= {14, 12, 10} and 14 in m.values()
    tm, bpm = s['tempo_map'], s['bpm']
    b7 = next(b for b, n in m.items() if n == 14)
    dur = tempo_seconds(tm, b7 * 4 + 4) - tempo_seconds(tm, b7 * 4)
    assert abs(dur - 3.5 * 60 / bpm) < 0.01, dur                      # a 7/8 bar lasts 3.5 beats
    b4 = next(b for b in range(s['total_bars']) if b not in m)
    assert abs(tempo_seconds(tm, b4 * 4 + 4) - tempo_seconds(tm, b4 * 4) - 4 * 60 / bpm) < 0.01
    for e in s['events']:
        if int(e.beat // 4) in m:
            assert e.beat < int(e.beat // 4) * 4 + 4
    tap = sorted((e.beat, e.midi) for e in s['events'] if e.track == 'arp')
    assert tap and max(n for _, n in tap) - min(n for _, n in tap) >= 19   # two hands, two octaves wide
    for g in ('rolling_atmos_bass', 'beat_tape_cinematic', 'uk_tribal_techno', 'steppy_halftime', 'balearic_chill'):
        x = compose(Options(style=g, seed=1))
        assert x['events'] and x['st']['bpm'][0] <= x['bpm'] <= x['st']['bpm'][1] + 2
    for g in ('sunrise_chillwave', 'hazy_downtempo', 'analog_arp_drive', 'velvet_pop', 'emotive_2step', 'sub_pressure_140'):
        x = compose(Options(style=g, seed=1))
        assert x['events'] and x['st']['master'].get('air', 0) <= 0.6
    sun = {t['name']: t for t in compose(Options(style='sunrise_chillwave', seed=3))['st']['tracks']}
    assert sun['chords'].get('chorus') and sun['pad'].get('chorus') and sun['pad'].get('sc')   # chorus guitar, breathing pads
    print('ok  math rock: real odd bars (7/8, 3/4, 5/8), tapped loops across the bar line; five reference-batch genres')


def test_va_synth():
    """v1.57: the built-in analog synth - band-limited oscillators (no aliasing hash), a resonant moving filter, unison
    spread across the stereo field, and the rebuilt classic sounds (old ones still there as *_v1)."""
    import numpy as np
    from sgcore import va
    from sgcore.compose import Options, compose
    from sgcore.dsp import SR
    from sgcore.instruments import INSTRUMENTS, ROLE_CHOICES
    x = va.saw(np.full(SR, 3520.0), SR)
    sp = np.abs(np.fft.rfft(x * np.hanning(SR))) ** 2
    f = np.fft.rfftfreq(SR, 1 / SR)
    harm = np.abs(f / 3520.0 - np.round(f / 3520.0)) * 3520.0 < 4
    assert sp[~harm & (f > 200)].sum() / sp.sum() < 0.01                  # PolyBLEP: aliasing stays tiny
    n = SR
    noise = np.random.default_rng(1).standard_normal(n)
    y = va.vcf(noise, 1000.0, res=0.9)
    sy = np.abs(np.fft.rfft(y)) ** 2
    fy = np.fft.rfftfreq(n, 1 / SR)
    band = lambda a, b: sy[(fy > a) & (fy < b)].mean()
    assert band(900, 1100) > 3 * band(300, 500) and band(900, 1100) > 30 * band(4000, 6000)   # resonant 24 dB low-pass
    v = va.voice(57, 1.0, {}, unison=5, detune=20, spread=1.0)
    assert v.shape[0] == 2 and np.abs(v[0] - v[1]).mean() > 0.05            # unison voices spread in stereo
    for k in ('warmpad', 'polysynth', 'supersaw', 'leadsaw', 'softlead', 'pluck_saw', 'stab', 'sawbass', 'moogbass', 'epiano'):
        a = np.asarray(INSTRUMENTS[k](60, 0.5, {}, None, None))
        assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.5, k
        assert k + '_v1' in INSTRUMENTS
    assert 'warmpad_v1' in ROLE_CHOICES['pad']
    for k in ('organ', 'synthbrass', 'synclead', 'mellotron', 'mellotron_flute', 'dxbell', 'vocalpad'):      # 1.58
        a = np.asarray(INSTRUMENTS[k](60, 0.8, {}, None, None))
        assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.5, k
    assert 'synclead' in ROLE_CHOICES['lead'] and 'vocalpad' in ROLE_CHOICES['pad'] and 'mellotron' in ROLE_CHOICES['chords']
    for k in ('trancepad', 'rollbass', 'superpluck', 'neuro', 'houseorgan', 'wobble', 'growl', 'reese', 'riddim',
              'screech', 'hoover', 'supersaw_lead'):                                                  # 1.59
        a = np.asarray(INSTRUMENTS[k](40 if k in ('rollbass', 'neuro', 'wobble', 'growl', 'reese', 'riddim') else 64, 0.8,
                                      {'spb': 0.43}, None, 0.5 if k in ('wobble', 'growl', 'neuro', 'riddim', 'screech') else None))
        assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.6, (k, np.abs(a).max())
    from sgcore.va_bass import dist
    xx = np.sin(2 * np.pi * 3000 * np.arange(SR) / SR)
    yy = dist(xx, 8.0)
    sp3 = np.abs(np.fft.rfft(yy)) ** 2
    f3 = np.fft.rfftfreq(SR, 1 / SR)
    harm3 = np.abs(f3 / 3000.0 - np.round(f3 / 3000.0)) * 3000.0 < 3
    assert sp3[~harm3].sum() / sp3.sum() < 1e-3                             # oversampled drive: no aliased fizz
    jp = va.jp_supersaw(440.0, SR // 2)
    assert jp.shape == (2, SR // 2) and np.abs(jp[0] - jp[1]).mean() > 0.05   # seven saws spread wide
    from sgcore.styles import STYLES as _S2
    tr = {t['name']: t['inst'] for t in _S2['trance']['tracks']}
    assert tr['bass'] == 'rollbass' and tr['pad'] == 'trancepad'
    dry = np.asarray(INSTRUMENTS['organ'](60, 0.5, {'leslie': 0.0}))
    assert np.allclose(dry[0], dry[1])                                     # the track's own rotary effect takes over
    s = va.sync_saw(220.0, np.linspace(1.5, 4.0, SR), SR)
    sp2 = np.abs(np.fft.rfft(s[: SR // 4])) ** 2
    f2 = np.fft.rfftfreq(SR // 4, 1 / SR)
    assert sp2[f2 > 12000].sum() / sp2.sum() < 0.01                        # oversampled sync: no fizz
    for k in ('junopad', 'junopoly', 'junobass', 'jupiterpad', 'obstab', 'moog_lead', 'hypersaw', 'dxbass', 'acid'):   # 1.60
        a = np.asarray(INSTRUMENTS[k](40 if k in ('junobass', 'dxbass', 'acid') else 64, 0.8, {}, None, None))
        assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.3, (k, np.abs(a).max())
    assert 'acid_v1' in INSTRUMENTS and 'acid_v1' in ROLE_CHOICES['bass']
    plain = np.asarray(INSTRUMENTS['acid'](40, 0.3, {}, None, 0))
    accent = np.asarray(INSTRUMENTS['acid'](40, 0.3, {}, None, 1))
    assert np.sqrt((accent ** 2).mean()) > np.sqrt((plain ** 2).mean()) * 1.1          # 303 accent: louder, brighter
    slid = np.asarray(INSTRUMENTS['acid'](43, 0.3, {}, 40, 0))
    assert np.abs(slid[:40]).max() > np.abs(plain[:40]).max()                         # a slide has no new attack
    jc = va.juno_chorus(np.sin(2 * np.pi * 220 * np.arange(SR) / SR), 2)
    assert jc.shape == (2, SR) and np.abs(jc[0] - jc[1]).mean() > 0.02               # BBD chorus: L and R move apart
    y18 = va.vcf18(np.random.default_rng(1).standard_normal(SR), 500.0, 0.3)
    sp18 = np.abs(np.fft.rfft(y18)) ** 2
    f18 = np.fft.rfftfreq(SR, 1 / SR)
    assert sp18[(f18 > 3000) & (f18 < 6000)].mean() < sp18[(f18 > 100) & (f18 < 400)].mean() * 1e-3
    for k in ('ebass', 'pickbass', 'slapbass', 'fretless', 'upright', 'sinebass', 'sawbass'):          # 1.61 basses
        for mm in (28, 40, 52):
            a = np.asarray(INSTRUMENTS[k](mm, 0.5, {}, None, None))
            assert np.isfinite(a).all() and 0.05 < np.abs(a).max() < 1.2, (k, mm, np.abs(a).max())
        assert k + '_v1' in INSTRUMENTS or k in ('pickbass', 'slapbass', 'fretless')
    from sgcore.dsp import mtof as _mt
    for fq in (41.2, 98.0):                                                  # the waveguide string is in tune
        ws = va.string(fq, SR, np.random.default_rng(0).standard_normal(int(SR / fq)), t60=3)[SR // 4:]
        wsp = np.abs(np.fft.rfft((ws - ws.mean()) * np.hanning(len(ws))))
        wf = np.fft.rfftfreq(len(ws), 1 / SR)
        band = (wf > fq * 0.8) & (wf < fq * 1.2)
        assert abs(wf[band][np.argmax(wsp[band])] - fq) < 2.0
    eb = np.asarray(INSTRUMENTS['ebass'](40, 1.0, {}, None, None))
    assert np.abs(eb[int(0.9 * SR):int(1.0 * SR)]).max() > 0.05 * np.abs(eb).max()   # a bass note sustains
    assert np.abs(eb[-200:]).max() < 0.02                                    # and is muted at the end
    from sgcore.soundfont import fallback_for
    assert fallback_for('slapbass') == 'slapbass' and fallback_for('pickbass') == 'pickbass'
    _ = _mt
    for k in ('dnbwob', 'vowelwob', 'multiwob', 'tablewob', 'chopwob', 'rumble', 'dubstab', 'technoseq', 'darkpad', 'atmos',
              'emolead'):                                                                           # 1.62
        a = np.asarray(INSTRUMENTS[k](40 if k in ('dnbwob', 'vowelwob', 'multiwob', 'tablewob', 'chopwob', 'rumble') else 62,
                                      0.8, {'spb': 0.43}, None, 0.5 if 'wob' in k else None))
        assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.6, (k, np.abs(a).max())
    ju = compose(Options(style='jump_up', seed=1))
    rates = {e.mod for e in ju['events'] if e.track == 'bass' and e.midi is not None}
    assert ju['st']['tracks'] and min(r for r in rates if isinstance(r, (int, float))) <= 0.5   # DnB wobble: fast LFO
    tf = compose(Options(style='trance', seed=1))
    assert tf['st'].get('rev_hp') and tf['st'].get('rev_predelay')                 # trance hall: pre-delay, high-passed
    from sgcore.render import auto_lp                                                   # 1.63: filter arc
    nz = np.random.default_rng(2).standard_normal((2, SR))
    cutc = np.geomspace(500, 20000, SR)
    fl = auto_lp(nz, cutc)
    hi1 = lambda z: float(np.mean(np.abs(np.diff(z[0]))))
    assert hi1(fl[:, :SR // 4]) < 0.3 * hi1(nz[:, :SR // 4]) and hi1(fl[:, -SR // 8:]) > 0.5 * hi1(nz[:, -SR // 8:])
    assert np.array_equal(auto_lp(nz, np.full(SR, 20000.0)), nz)
    from sgcore.styles import STYLES as _S3
    assert all(_S3[g].get('filter_arc') and _S3[g].get('sc_arc') for g in ('trance', 'techno', 'progressive_trance'))
    for k in ('vocalchop', 'fbchord', 'lofikeys'):                                       # 1.64
        a = np.asarray(INSTRUMENTS[k](64, 0.6, {'spb': 0.43}, None, None))
        assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.3, (k, np.abs(a).max())
    lv = [float(np.sqrt(np.mean(np.asarray(INSTRUMENTS['vocalchop'](mm, 0.3, {})) ** 2))) for mm in range(60, 70)]
    assert max(lv) < min(lv) * 1.2                                                        # every vowel the same level
    for k in ('rhodes', 'acguitar', 'nylon', 'hardlead', 'steelguitar'):                     # 1.65
        a = np.asarray(INSTRUMENTS[k](55, 0.6, {}, None, None))
        assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.3, (k, np.abs(a).max())
    from sgcore.soundfont import fallback_for as _fb
    assert _fb('nylon') == 'nylon' and _fb('steelguitar') == 'steelguitar' and 'acguitar_v1' in INSTRUMENTS
    for k in ('strings', 'piano', 'guitar', 'cleanguitar', 'odguitar', 'distguitar', 'sax', 'sopsax', 'flute'):   # 1.66
        for mm in (48, 64, 76):
            a = np.asarray(INSTRUMENTS[k](mm, 0.6, {}, None, None))
            assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.3, (k, mm, np.abs(a).max())
        assert k + '_v1' in INSTRUMENTS or k in ('cleanguitar', 'odguitar', 'distguitar', 'sopsax')
    pl = [float(np.sqrt(np.mean(np.asarray(INSTRUMENTS['piano'](mm, 1.0, {}))[:, :SR // 3] ** 2))) for mm in (36, 60, 84)]
    assert max(pl) < 1.6 * min(pl)                                             # an even keyboard
    from sgcore.render import track_fx
    zz = np.random.default_rng(3).standard_normal((2, SR)) * 0.2
    for fxk, fxv in (('phaser', 0.6), ('flanger', 0.5), ('trem', {'rate': 0.25, 'depth': 0.5}), ('wah', 0.6), ('crush', 0.5)):
        yy = track_fx(zz, {fxk: fxv}, 0.5)
        assert yy.shape == zz.shape and np.isfinite(yy).all() and not np.allclose(yy, zz), fxk
    for k in ('marimba', 'celesta', 'glock', 'kalimba', 'choir', 'brass', 'harp', 'pizz', 'clav', 'mutedgtr', 'twang'):   # 1.67
        for mm in (48, 72):
            a = np.asarray(INSTRUMENTS[k](mm, 0.6, {}, None, None))
            assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.3, (k, mm, np.abs(a).max())
    for k in ('m1piano', 'samplerstab', 'techbass', 'bhbass', 'psybass', 'psylead'):          # 1.68
        a = np.asarray(INSTRUMENTS[k](48 if 'bass' in k else 67, 0.4, {}, None, None))
        assert np.isfinite(a).all() and 0.02 < np.abs(a).max() < 1.3, (k, np.abs(a).max())
    from sgcore.styles import POOLS as _P4
    assert all(len(_P4[g][r]) >= 6 for g in ('dnb', 'house', 'techno', 'dubstep') for r in ('chords', 'pad', 'arp', 'lead'))
    assert _P4['trap']['bass'] == ['808']                                    # a genre's defining part keeps its own list
    tm = compose(Options(style='trap_metal', seed=1))
    assert tm['st']['master']['lufs'] >= -7 and tm['st']['voicing'] == 'power' and tm['key'].scale_name in ('phrygian_dominant', 'phrygian', 'harmonic_minor')
    assert any(e.track == 'chords_r' for e in tm['events'])                 # double-tracked guitars
    print('ok  built-in analog synth: band-limited, resonant moving filter, stereo unison; classic sounds kept')


def test_christmas_orchestral():
    """v1.45: Christmas film-score orchestra - joyful 3/4 carol with a last-chorus key change, mischief 4/4 chase."""
    from sgcore.compose import Options, compose
    j = compose(Options(style='christmas_joyful', seed=3))
    assert j['st'].get('meter') == '3/4'
    assert any(x.get('key_change') for x in j['sections'])                 # the lift into the last chorus
    lv = [x['opts'].get('level') for x in j['sections'] if x['opts'].get('level') is not None]
    assert lv[0] < 0.4 and max(lv) >= 0.95                                   # hushed start, full-orchestra finish
    assert {'glock', 'sleigh', 'horns'} <= {e.track for e in j['events']}
    m = compose(Options(style='christmas_mischief', seed=3))
    assert 128 <= m['bpm'] <= 154 and 3 in m['key'].scale             # a minor third: minor / harmonic minor
    sneak = next(x for x in m['sections'] if x['name'] == 'sneak')
    assert sneak['opts']['level'] < 0.5 and 'kick' not in sneak['layers']
    print('ok  Christmas orchestral: joyful 3/4 carol + key change, mischief chase with a sneaky break')


def test_octaves_and_ranges():
    """v1.46: every melodic part is kept in its instrument's sweet spot, and each part can be moved by octaves."""
    from sgcore.compose import Options, compose, INST_RANGE
    def med(s, n):
        m = sorted(e.midi for e in s['events'] if e.track == n and e.midi is not None)
        return m[len(m) // 2] if m else None
    s = compose(Options(style='swing', seed=773040))                       # the squealing big-band lead
    inst = s['st']['tracks'][[t['name'] for t in s['st']['tracks']].index('lead')]['inst'].split(':')[-1]
    lo, hi = INST_RANGE[inst]
    assert lo <= med(s, 'lead') <= hi, (inst, med(s, 'lead'))
    a = compose(Options(style='swing', seed=773040, octaves={'lead': -1, 'chords': 1}))
    assert med(a, 'lead') == med(s, 'lead') - 12 and med(a, 'chords') == med(s, 'chords') + 12
    assert med(a, 'bass') == med(s, 'bass')                                   # other parts untouched
    m = compose(Options(style='christmas_magic', seed=4))
    assert {'flute', 'vibes', 'bass_cb'} <= {e.track for e in m['events']} and m['harm_alts'] >= 1
    ui = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sgcore', 'ui.html'), encoding='utf-8').read()
    assert 'octHtml(r,' in ui and 'data-edoct' in ui
    print('ok  instrument sweet-spot registers, per-part octave choices (panel + editor), magical Christmas genre')


def test_lead_runs_and_ebass():
    """v1.47: liquid DnB leads sweep up into long notes with 16th-note arpeggio runs; the electric bass sustains."""
    import numpy as np
    from sgcore.compose import Options, compose
    from sgcore.instruments import INSTRUMENTS
    s = compose(Options(style='liquid_euphoric', seed=2))
    lead = sorted((e for e in s['events'] if e.track == 'lead' and e.midi is not None), key=lambda e: e.beat)
    runs = 0
    for i in range(len(lead) - 3):
        a, b, c, d = lead[i:i + 4]
        if all(abs(y.beat - x.beat - 0.25) < 1e-6 and y.midi > x.midi for x, y in ((a, b), (b, c), (c, d))):
            runs += 1
    assert runs >= 3, runs
    y = INSTRUMENTS['ebass'](36, 1.5, {})
    q = len(y) // 4
    r = [float(np.sqrt(np.mean(y[k * q:(k + 1) * q] ** 2))) for k in range(4)]
    assert r[3] > 0.7 * r[0], r                                  # holds, not a decaying pluck
    print('ok  lead run-ups into long notes (liquid DnB), sustained electric bass')


def test_drum_style_vs_sounds_and_orchestra_detection():
    """Drum sounds never change drum patterns; drum style can be a break or another genre's beat; user-picked sounds
    play every section; orchestra plugin states are recognised."""
    import struct
    from sgcore import orchscan
    from sgcore.styles import STYLES
    for style in ('jungle', 'house', 'boombap', 'salsa'):
        base = compose(Options(style=style, seed=5))['st']['drums']
        for kit in ('909', 'studio', 'amen', 'linn', 'brushes'):
            assert compose(Options(style=style, seed=5, kit=kit, drum_pattern='genre'))['st']['drums'] == base, (style, kit)
    assert compose(Options(style='house', seed=5, kit='amen'))['st'].get('break') == 'amen'        # old saved settings
    assert compose(Options(style='house', seed=5, drum_pattern='break:think'))['st'].get('break') == 'think'
    assert compose(Options(style='jungle', seed=5, drum_pattern='programmed'))['st'].get('break') is None
    st = compose(Options(style='house', seed=5, drum_pattern='style:reggaeton', kit='909'))['st']
    assert st.get('borrowed_drums') == 'reggaeton' and st['drums']['snare'] == STYLES['reggaeton']['drums']['snare']
    assert compose(Options(style='house', seed=5, drum_pattern='style:waltz'))['st'].get('borrowed_drums') is None  # 3/4
    vc2 = lambda x: b'VC2!' + struct.pack('<I', len(x) + 1) + x.encode() + b'\0'
    info = orchscan.identify(vc2('<s instrumentName="Celli" articulationText="Pizzicato"/>'))
    assert info['instrument'] == 'Celli' and 'pizzicato' in orchscan.sound_name('BBC', info)
    assert orchscan.identify(b'nothing to see') is None
    print('ok  drum style / drum sounds / orchestra detection')


def test_drummer_percussion_and_beat_feels():
    """Drummer settings change only the playing; percussion sets replace the genre's; every genre's beat has a feel."""
    from collections import Counter
    from sgcore import drummer
    from sgcore.styles import STYLES

    def hits(**kw):
        return Counter(e.track for e in compose(Options(style='funk', seed=4, **kw))['events'])
    base = hits()
    assert hits(drum_ghosts='more')['snare'] > base['snare'] and hits(drum_ghosts='off')['snare'] < base['snare']
    assert hits(hat_density='sparse')['chat'] < base['chat'] < hits(hat_density='busy')['chat']
    assert hits(drum_fills='more')['snare'] > hits(drum_fills='none')['snare']
    st = compose(Options(style='house', seed=4, percussion='latin'))['st']
    assert {'pc_conga', 'pc_guiro', 'pc_bell'} <= set(st['drums']) and 'conga' not in st['drums'] and st.get('real_cowbell')
    assert not {k for k in compose(Options(style='afro_house', seed=4, percussion='off'))['st']['drums']} & {'conga', 'shaker', 'woodblock'}
    assert not any(k.startswith('pc_') for k in compose(Options(style='waltz', seed=4, percussion='latin'))['st']['drums'])
    feels = {k: drummer.beat_feel(k) for k in STYLES}
    assert feels['house'] == 'four-on-the-floor' and feels['trap'] == 'half-time' and feels['reggaeton'] == 'dembow / clave'
    assert feels['jungle'] == 'breakbeat' and feels['waltz'] == '3/4' and feels['chamber'] == 'no drums'
    print('ok  drummer settings, percussion sets, beat feels')


def test_new_genres_and_daisy():
    """1.51: 40 new genres compose with their own grooves; the Daisy Bell computer voice sings in tune."""
    import numpy as np
    from sgcore import daisy
    from sgcore.compose import OWN_GROOVE
    from sgcore.styles import STYLES
    for g in ('french_house', 'trip_hop', 'footwork', 'juke', 'footwork_soulful', 'footwork_dark', 'hard_techno', 'afrobeat',
              'dub', 'corridos_tumbados', 'samba', 'gypsy_jazz', 'ragtime', 'bhangra', 'anime_opening'):
        assert g in STYLES, g
    for seed in (1, 2, 3):                                   # footwork keeps its triplet-feel kicks (no generic patterns)
        ks = {round(e.beat % 4, 2) for e in compose(Options(style='footwork', seed=seed))['events'] if e.track == 'kick'}
        assert 0.75 in ks or 1.5 in ks, ks
    rk = [round(e.beat % 4, 2) for e in compose(Options(style='reggae', seed=2))['events'] if e.track == 'kick']
    assert 'reggae' in OWN_GROOVE and rk.count(2.0) > 0.8 * len(rk), rk     # the one-drop: kick on beat 3 (build-ups aside)
    assert sum(b for _, _, b in daisy.MELODY) == 99 and len(daisy.CHORDS) == 33
    y = daisy.sing([(0.0, 0.6, 69, 'd aI'), (0.6, 0.6, 76, 'z i')])
    seg = y[int(0.3 * SR):int(0.55 * SR)]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    harm = f[np.argmax(spec * (f < 1000))]
    assert abs(harm / 440.0 - round(harm / 440.0)) < 0.05, harm   # the sung 'Dai' sits on A440 (or a harmonic of it)
    print('ok  40 new genres, protected grooves, Daisy Bell computer voice')


def test_storage_cleanup():
    """Old previews go; unkept songs older than the limit are trimmed to MIDI + settings (or deleted); kept songs and
    files that aren't Studio Lab projects are never touched."""
    import json
    import time as _t
    from sgcore import storage
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, 'previews'))
    old = _t.time() - 30 * 86400

    def song(base, kept=False, age=old):
        with open(os.path.join(d, base + '_settings.json'), 'w') as f:
            json.dump({'options': {'style': 'house'}, 'kept': kept}, f)
        for ext in ('.mp3', '.wav', '.mid'):
            open(os.path.join(d, base + ext), 'wb').write(b'x' * 1000)
        os.makedirs(os.path.join(d, base + '_stems'))
        open(os.path.join(d, base + '_stems', 'drums.wav'), 'wb').write(b'x' * 5000)
        for p in os.listdir(d):
            if p.startswith(base):
                os.utime(os.path.join(d, p), (age, age))
    song('Old_one'); song('Kept_one', kept=True); song('New_one', age=_t.time())
    open(os.path.join(d, 'my_own_track.wav'), 'wb').write(b'x' * 100)
    pv = os.path.join(d, 'previews', 'p.mp3'); open(pv, 'wb').write(b'x'); os.utime(pv, (old, old))
    r = storage.clean(d, storage.policy({}))
    assert r['previews'] == 1 and r['trimmed'] == 1 and r['deleted'] == 0, r
    left = set(os.listdir(d))
    assert {'Old_one_settings.json', 'Old_one.mid'} <= left and not {'Old_one.mp3', 'Old_one.wav', 'Old_one_stems'} & left
    assert {'Kept_one.mp3', 'Kept_one_stems', 'New_one.mp3', 'my_own_track.wav'} <= left
    assert storage.is_trimmed(d, 'Old_one') and not storage.is_trimmed(d, 'Kept_one')
    storage.set_kept(d, 'Kept_one', False)
    os.utime(os.path.join(d, 'Kept_one_settings.json'), (old, old))
    r = storage.clean(d, storage.policy({'storage': {'mode': 'delete', 'days': 7}}))
    assert r['deleted'] == 2 and not any(f.startswith(('Kept_one', 'Old_one')) for f in os.listdir(d)), os.listdir(d)
    assert 'my_own_track.wav' in os.listdir(d) and storage.policy({'storage': {'mode': 'bogus', 'days': 0}}) == {'mode': 'midi', 'days': 1}
    print('ok  storage clean-up: previews, trimmed / deleted / kept songs, other files untouched')


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
    test_builds_and_transitions()
    test_amen_and_groups()
    test_no_console_windows()
    test_editor_and_sounds()
    test_reference_genres()
    test_sound_choices()
    test_traits_and_review()
    test_rotation_keeps_genre_sound()
    test_surf_and_monster_theme()
    test_hindu_devotional()
    test_world_and_rock_genres_153()
    test_sung_vocals()
    test_reference_genre_match()
    test_meend_gamak()
    test_shakuhachi_genres()
    test_switchup_808()
    test_tanpura_on_the_beat()
    test_arabic_maqam()
    test_voice_sample_chops()
    test_dj_effects()
    test_idm_drill()
    test_math_rock_meters()
    test_va_synth()
    test_v144_drums_layers_new_genres()
    test_bass_warp_trap()
    test_christmas_orchestral()
    test_octaves_and_ranges()
    test_lead_runs_and_ebass()
    test_drum_style_vs_sounds_and_orchestra_detection()
    test_drummer_percussion_and_beat_feels()
    test_new_genres_and_daisy()
    test_storage_cleanup()
    print('all good')


if __name__ == '__main__':
    main()
