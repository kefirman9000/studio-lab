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
                                              'cello', 'contrabass', 'organ', 'ebass', 'mandolin', 'guitar', 'choir'):
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
    assert sfm.fallback_for('pickbass') == 'ebass' and sfm.fallback_for('fingerbass') == 'ebass'
    print('ok  surf rock feel, monster TV theme riff, pick / finger bass fall back to a bass (not a synth pluck)')


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
    b = [e for e in s['events'] if e.track == 'bass']
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
    print('ok  bass-warp trap (+ fast): warped 808s, slides, 808-up / growl switch-ups, parallel grit, pitched hat rolls')


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
    test_v144_drums_layers_new_genres()
    test_bass_warp_trap()
    test_christmas_orchestral()
    test_octaves_and_ranges()
    print('all good')


if __name__ == '__main__':
    main()
