"""Genre traits: twelve high-level rule categories (arrangement, density, feel, melody, bass, drop, variation, culture,
texture, rhythm, harmony, energy curve) layered on top of the low-level genre rules.

Every genre gets a full set: inferred from its existing rules, with a few genres declared by hand. A song can override
any of them (Options.traits = {category: value}) or ask for a surprise ({'_surprise': True}): the same genre then makes
a meaningfully different track - hypnotic or evolving, sparse or dense, flat or full of contrasts.

The traits that map onto the generator steer it; 'culture' (and part of 'rhythm') only describe the genre.
"""
import random
from dataclasses import replace

CATEGORIES = {
    'arrangement': ('Arrangement', ['groove_locked', 'tension_release', 'atmospheric_drift', 'narrative', 'verse_chorus_pop',
                                    'hypnotic_minimal', 'switchup_heavy']),
    'density': ('Density', ['sparse', 'medium', 'dense', 'evolving']),
    'feel': ('Human feel', ['robotic', 'tight_swing', 'loose_human', 'drifting', 'live_drums']),
    'melody': ('Melodic behaviour', ['rhythmic_stabs', 'long_lyrical', 'call_and_response', 'minimal_motivic',
                                     'nostalgic_simple', 'virtuosic']),
    'bass': ('Bass personality', ['sub_only', 'rolling_groove', 'wobble_modulated', 'walking', '808_slide', 'melodic_bass']),
    'drop': ('Drop / payoff', ['sudden', 'long_build', 'groove_drop', 'emotional_swell', 'none']),
    'variation': ('Variation', ['low', 'sectional', 'progressive', 'switchup', 'theme_and_variations']),
    'culture': ('Context', ['uk_soundsystem', 'festival_mainstage', 'underground_club', 'bedroom_lofi', 'jazz_club',
                            'gospel_church', 'cinematic_score', 'nostalgic_memory', 'carnival', 'warehouse', 'radio_pop',
                            'concert_hall', 'street', 'folk_gathering']),
    'texture': ('Texture & space', ['dry_and_upfront', 'wet_and_spacious', 'tape_degraded', 'club_punchy', 'intimate_close',
                                    'massive_reverb', 'lofi_degraded']),
    'rhythm': ('Rhythmic feel', ['straight_16ths', 'swung_16ths', 'triplet_feel', 'half_time', 'double_time_sections',
                                 'syncopation_heavy', 'on_the_grid']),
    'harmony': ('Harmony', ['functional_tonal', 'modal', 'static_vamp', 'chromatic_colour', 'jazz_extensions',
                            'simple_pop_harmony']),
    'energy': ('Energy curve', ['flat_hypnotic', 'slow_build', 'peaks_and_valleys', 'continuous_climb', 'sudden_contrasts',
                                'emotional_arc']),
}
DESCRIPTIVE = {'culture'}                                  # describe the genre only
DESCRIPTIVE_VALUES = {'rhythm': {'half_time', 'double_time_sections', 'syncopation_heavy'}}
SURPRISE = ('density', 'energy', 'variation', 'drop', 'texture')   # what "surprise me" may change

# hand-declared genres (the rest are inferred); partial sets are filled in by inference
DECLARED = {
    'deep_dubstep': dict(arrangement='atmospheric_drift', density='sparse', feel='tight_swing', melody='minimal_motivic',
                         bass='sub_only', drop='sudden', variation='sectional', culture='uk_soundsystem',
                         texture='wet_and_spacious', rhythm='half_time', harmony='static_vamp', energy='peaks_and_valleys'),
    'deep_dubstep_minimal': dict(arrangement='atmospheric_drift', density='sparse', bass='sub_only', drop='sudden',
                                 culture='uk_soundsystem', rhythm='half_time', harmony='static_vamp'),
    'house': dict(arrangement='groove_locked', density='medium', feel='tight_swing', melody='rhythmic_stabs',
                  bass='rolling_groove', drop='groove_drop', variation='progressive', culture='underground_club',
                  texture='club_punchy', rhythm='swung_16ths', harmony='functional_tonal', energy='flat_hypnotic'),
    'jump_up': dict(arrangement='switchup_heavy', variation='switchup', bass='wobble_modulated', culture='uk_soundsystem'),
    'riddim': dict(arrangement='switchup_heavy', variation='switchup', bass='wobble_modulated'),
    'brostep': dict(arrangement='switchup_heavy', variation='switchup', bass='wobble_modulated', culture='festival_mainstage'),
    'modern_gospel': dict(arrangement='verse_chorus_pop', melody='call_and_response', culture='gospel_church',
                          energy='continuous_climb'),
    'gospel': dict(melody='call_and_response', culture='gospel_church', feel='live_drums'),
    'piano_miniature': dict(density='sparse', texture='intimate_close', drop='none', melody='nostalgic_simple'),
    'field_ambient': dict(density='sparse', drop='none', arrangement='atmospheric_drift'),
    'liquid_dnb': dict(melody='long_lyrical', drop='emotional_swell', bass='rolling_groove'),
    'hard_trance': dict(arrangement='tension_release', drop='long_build', culture='warehouse'),
    'bigroom': dict(arrangement='tension_release', drop='long_build', culture='festival_mainstage'),
    'bebop': dict(melody='virtuosic', culture='jazz_club', bass='walking'),
    'fusion': dict(melody='virtuosic'),
}

_GROUP_CULTURE = {
    'House & Disco': 'underground_club', 'Techno': 'warehouse', 'Trance': 'festival_mainstage',
    'Dubstep, Garage & Bass': 'uk_soundsystem', 'Drum & Bass, Breaks & Hard': 'uk_soundsystem',
    'Hauntology': 'nostalgic_memory', 'Chill, Lo-fi & Ambient': 'bedroom_lofi', 'Jazz': 'jazz_club',
    'Soul, R&B & Gospel': 'radio_pop', 'Latin & Caribbean': 'carnival', 'Hip-Hop': 'street', 'Hip-Hop, Trap & Phonk': 'street',
    'Pop, R&B & Hopecore': 'radio_pop', 'Pop & Indie': 'radio_pop', 'Classical Eras': 'concert_hall',
    'Solo Piano': 'concert_hall', 'Country & Folk': 'folk_gathering', 'Funk & Disco': 'underground_club',
}


def _group(name):
    try:
        from .genre_groups import group_of
        return group_of(name) or ''
    except Exception:
        return ''


def _has(name, *words):
    return any(w in name for w in words)


def infer(name, st):
    """A full trait set for a genre, read from its rules (declared values win)."""
    g = _group(name)
    form = st.get('form') if isinstance(st.get('form'), str) else 'custom'
    cat = st.get('category', '')
    m = st.get('master') or {}
    swing, human = float(st.get('swing', 0.5)), float(st.get('human', 0.0))
    melodic = [t for t in st.get('tracks', []) if t.get('layer') in ('chords', 'pad', 'arp', 'lead', 'bass')]
    drums = st.get('drums') or {}
    t = {}
    # arrangement
    if st.get('bass_switch') or _has(name, 'riddim', 'brostep', 'jump_up', 'switch_trap'):
        t['arrangement'] = 'switchup_heavy'
    elif cat == 'Orchestral' or st.get('composer') or form in ('epic', 'journey', 'toccata'):
        t['arrangement'] = 'narrative'
    elif _has(name, 'minimal', 'techno', 'dub_techno'):
        t['arrangement'] = 'hypnotic_minimal'
    elif form in ('edm', 'edm_b', 'trance', 'bigroom', 'hardstyle', 'trance_pop_90s') or _has(name, 'trance', 'bigroom'):
        t['arrangement'] = 'tension_release'
    elif form in ('ambient', 'deep_dubstep', 'lofi', 'liquid', 'halftime') or m.get('lofi'):
        t['arrangement'] = 'atmospheric_drift'
    elif form in ('groove', 'garage') or 'House' in g or 'Funk' in g:
        t['arrangement'] = 'groove_locked'
    else:
        t['arrangement'] = 'verse_chorus_pop'
    # density
    if not drums or len(melodic) <= 3 or form in ('ambient',):
        t['density'] = 'sparse'
    elif len(st.get('tracks', [])) >= 12:
        t['density'] = 'dense'
    else:
        t['density'] = 'medium'
    # human feel
    if float(m.get('wobble', 0) or 0) >= 2.0 or st.get('rubato'):
        t['feel'] = 'drifting'
    elif human < 0.002 and swing <= 0.51:
        t['feel'] = 'robotic'
    elif st.get('ghosts') and human >= 0.006:
        t['feel'] = 'live_drums'
    elif swing >= 0.56 or human >= 0.008:
        t['feel'] = 'loose_human'
    else:
        t['feel'] = 'tight_swing'
    # melody
    rh = ''.join(st.get('lead_rh') or [])
    holds = rh.count('-') / max(1, rh.count('x'))
    if _has(name, 'bebop', 'fusion', 'metal', 'shred'):
        t['melody'] = 'virtuosic'
    elif m.get('lofi') and float(m.get('wobble', 0) or 0) >= 2.5:
        t['melody'] = 'nostalgic_simple'
    elif float(st.get('repetition', 0) or 0) >= 0.85 or t['arrangement'] == 'hypnotic_minimal':
        t['melody'] = 'minimal_motivic'
    elif any(w in g for w in ('Jazz', 'Funk', 'Latin', 'Afro', 'Gospel')):
        t['melody'] = 'call_and_response'
    elif holds < 0.6:
        t['melody'] = 'rhythmic_stabs'
    else:
        t['melody'] = 'long_lyrical'
    # bass
    mode = st.get('bass_mode', 'pattern')
    binst = next((x['inst'] for x in st.get('tracks', []) if x.get('name') == 'bass'), '')
    if mode == '808':
        t['bass'] = '808_slide'
    elif mode == 'wobble' or st.get('bass_switch'):
        t['bass'] = 'wobble_modulated'
    elif mode == 'walk':
        t['bass'] = 'walking'
    elif binst == 'sinebass' and sum(p.count('R') for p in st.get('bass') or []) <= 4 * max(1, len(st.get('bass') or [])):
        t['bass'] = 'sub_only'
    elif _has(name, 'future_bass', 'melodic', 'progressive'):
        t['bass'] = 'melodic_bass'
    else:
        t['bass'] = 'rolling_groove'
    # drop / payoff
    try:
        from .arrange import GENRE_BUILD
        b = GENRE_BUILD.get(name) or {'Classic': 'lift', 'Orchestral': 'swell'}.get(cat, 'roll')
    except Exception:
        b = 'roll'
    if not drums or form == 'ambient':
        t['drop'] = 'none'
    elif st.get('plain_drops') or b in ('filter', 'hats', 'lift', 'pickup', 'claps', 'ride'):
        t['drop'] = 'groove_drop'
    elif b in ('pause', 'stutter', 'stops'):
        t['drop'] = 'sudden'
    elif b in ('swell', 'cymbal', 'march', 'tomgroove'):
        t['drop'] = 'emotional_swell'
    else:
        t['drop'] = 'long_build'
    # variation
    if t['arrangement'] == 'switchup_heavy':
        t['variation'] = 'switchup'
    elif cat == 'Orchestral' or 'Classical' in g or 'Jazz' in g:
        t['variation'] = 'theme_and_variations'
    elif float(st.get('repetition', 0) or 0) >= 0.9 or t['arrangement'] == 'hypnotic_minimal':
        t['variation'] = 'low'
    elif t['arrangement'] in ('tension_release', 'groove_locked'):
        t['variation'] = 'progressive'
    else:
        t['variation'] = 'sectional'
    # culture
    t['culture'] = _GROUP_CULTURE.get(g) or {'Orchestral': 'cinematic_score', 'Electronic': 'underground_club'}.get(cat, 'radio_pop')
    # texture
    rv = float(st.get('reverb', 2.0) or 2.0)
    if m.get('lofi'):
        t['texture'] = 'lofi_degraded' if float(m.get('air', 0) or 0) <= -2.5 else 'tape_degraded'
    elif rv >= 3.6:
        t['texture'] = 'massive_reverb'
    elif float(m.get('lufs', -10)) <= -15 or 'Piano' in g:
        t['texture'] = 'intimate_close'
    elif rv >= 2.6:
        t['texture'] = 'wet_and_spacious'
    elif float(m.get('lufs', -10)) >= -9.0 or m.get('drive'):
        t['texture'] = 'club_punchy'
    else:
        t['texture'] = 'dry_and_upfront'
    # rhythm
    sn = ''.join(drums.get('snare', [''])[:1]) if drums.get('snare') else ''
    if swing >= 0.62:
        t['rhythm'] = 'triplet_feel'
    elif sn.startswith('........X') or form == 'halftime':
        t['rhythm'] = 'half_time'
    elif swing >= 0.53:
        t['rhythm'] = 'swung_16ths'
    elif human < 0.001:
        t['rhythm'] = 'on_the_grid'
    else:
        t['rhythm'] = 'straight_16ths'
    # harmony
    scales = st.get('scales') or []
    progs = st.get('progs')
    plist = [p for v in progs.values() for p in v] if isinstance(progs, dict) else list(progs or [])
    static = plist and sum(len(set(p)) <= 2 for p in plist) >= max(1, len(plist) // 2)
    if static or int(st.get('chord_bars', 1)) >= 4:
        t['harmony'] = 'static_vamp'
    elif int(st.get('chord_size', 3)) >= 4 and ('Jazz' in g or 'Soul' in g or _has(name, 'jazz', 'neo_soul', 'bossa')):
        t['harmony'] = 'jazz_extensions'
    elif scales and scales[0] in ('dorian', 'mixolydian', 'lydian', 'phrygian'):
        t['harmony'] = 'modal'
    elif int(st.get('chord_size', 3)) == 3 and scales[:1] == ['major']:
        t['harmony'] = 'simple_pop_harmony'
    else:
        t['harmony'] = 'functional_tonal'
    # energy curve
    t['energy'] = {'groove_locked': 'flat_hypnotic', 'hypnotic_minimal': 'flat_hypnotic', 'tension_release': 'peaks_and_valleys',
                   'narrative': 'emotional_arc', 'atmospheric_drift': 'slow_build', 'switchup_heavy': 'sudden_contrasts'
                   }.get(t['arrangement'], 'peaks_and_valleys')
    t.update(DECLARED.get(name, {}))
    return t


def all_traits():
    from .styles import STYLES
    return {k: infer(k, s) for k, s in STYLES.items()}


def wanted(opts, name):
    """The trait overrides for this song (validated; a surprise picks some at random, seeded by the song)."""
    raw = dict(getattr(opts, 'traits', None) or {})
    out = {k: v for k, v in raw.items() if k in CATEGORIES and k not in DESCRIPTIVE and v in CATEGORIES[k][1]
           and v not in DESCRIPTIVE_VALUES.get(k, ())}
    if raw.get('_surprise'):
        rnd = random.Random(f'{opts.seed}-traits-{name}')
        for k in rnd.sample(SURPRISE, 2):
            if k not in out:
                out[k] = rnd.choice(CATEGORIES[k][1])
    return out


# ------------------------------------------------------------------------------------------------ steering the generator
def apply_opts(opts, name):
    """Traits that map onto the song-wide knobs (only where the user left a knob at its default)."""
    tr = wanted(opts, name)
    if not tr:
        return opts
    ch = {}
    rep = {'minimal_motivic': 0.9, 'nostalgic_simple': 0.8, 'rhythmic_stabs': 0.75, 'call_and_response': 0.6,
           'long_lyrical': 0.5, 'virtuosic': 0.3}.get(tr.get('melody'))
    rep = {'low': 0.92, 'switchup': 0.4, 'theme_and_variations': 0.65, 'progressive': 0.55}.get(tr.get('variation'), rep)
    if rep is not None and abs(float(getattr(opts, 'repetition', 0.5)) - 0.5) < 1e-9:
        ch['repetition'] = rep
    simp = {'minimal_motivic': 0.5, 'nostalgic_simple': 0.6, 'virtuosic': 0.0}.get(tr.get('melody'))
    if simp is not None and not float(getattr(opts, 'simplicity', 0) or 0):
        ch['simplicity'] = simp
    if tr.get('melody') == 'virtuosic' and abs(float(getattr(opts, 'complexity', 0.5)) - 0.5) < 1e-9:
        ch['complexity'] = 0.9
    if tr.get('harmony') == 'static_vamp' and not getattr(opts, 'chord_speed', None):
        ch['chord_speed'] = 'slow'
    if tr.get('harmony') == 'chromatic_colour' and not getattr(opts, 'chord_color', None):
        ch['chord_color'] = '9'
    elif tr.get('harmony') == 'jazz_extensions' and not getattr(opts, 'chord_color', None):
        ch['chord_color'] = random.Random(f'{opts.seed}-ext').choice(['7', '9', 'add9'])
    elif tr.get('harmony') == 'simple_pop_harmony' and not getattr(opts, 'chord_color', None):
        ch['chord_color'] = 'triad'
    if tr.get('drop') == 'none' and (getattr(opts, 'builds', 'auto') or 'auto') == 'auto':
        ch['builds'] = 'off'
    if tr.get('feel') == 'robotic' and not getattr(opts, 'groove', None):
        ch['groove'] = 'straight'
    return replace(opts, **ch) if ch else opts


FORM_FOR = {'groove_locked': 'groove', 'tension_release': 'edm', 'atmospheric_drift': 'deep_dubstep', 'narrative': 'epic',
            'verse_chorus_pop': 'song', 'hypnotic_minimal': 'groove', 'switchup_heavy': 'edm'}


def apply_style(st, opts, name):
    """Traits that change the genre's own rules for this song."""
    tr = wanted(opts, name)
    if not tr:
        return st
    st['traits_used'] = tr
    m = st['master'] = dict(st.get('master') or {})
    bass = next((t for t in st['tracks'] if t['name'] == 'bass'), None)
    # feel
    f = tr.get('feel')
    if f == 'robotic':
        st.update(swing=0.5, human=0.0)
    elif f == 'tight_swing':
        st.update(swing=min(0.58, max(0.54, st['swing'])), human=min(st['human'], 0.003))
    elif f == 'loose_human':
        st.update(swing=max(0.56, st['swing']), human=max(0.009, st['human']))
    elif f == 'drifting':
        st.update(human=max(0.012, st['human']))
        m['wobble'] = max(2.5, float(m.get('wobble', 0) or 0))
    elif f == 'live_drums':
        st.update(ghosts=True, fill=True, human=max(0.007, st['human']))
    r = tr.get('rhythm')
    if r == 'straight_16ths':
        st['swing'] = 0.5
    elif r == 'swung_16ths':
        st.update(swing=max(0.55, min(0.6, st['swing'])), swing_unit=16)
    elif r == 'triplet_feel':
        st['swing'] = 0.65
    elif r == 'on_the_grid':
        st.update(human=0.0)
    # bass
    b = tr.get('bass')
    if b == '808_slide':
        st['bass_mode'] = '808'
        if bass:
            bass['inst'] = '808'
    elif b == 'wobble_modulated':
        st['bass_mode'] = 'wobble'
        if bass and bass['inst'] not in ('wobble', 'riddim', 'growl'):
            bass['inst'] = 'wobble'
    elif b == 'walking':
        st['bass_mode'] = 'walk'
    elif b == 'sub_only':
        st['bass_mode'] = 'pattern'
        st['bass'] = ['R-------R-------', 'R---------------']
        if bass:
            bass['inst'] = 'sinebass'
    elif b == 'rolling_groove':
        st['bass_mode'] = 'pattern'
        if bass and bass['inst'] in ('808', 'wobble', 'riddim'):
            bass['inst'] = 'moogbass'
    elif b == 'melodic_bass':
        st['bass_mode'] = 'pattern'
        st['bass'] = ['R-..F-..O-..A-..', 'R-.R..F.O-..F...']
    # texture
    x = tr.get('texture')
    rv = float(st.get('reverb', 2.0) or 2.0)
    if x == 'dry_and_upfront':
        st['reverb'] = rv * 0.55
    elif x == 'wet_and_spacious':
        st['reverb'] = max(2.6, rv * 1.4)
    elif x == 'massive_reverb':
        st['reverb'] = max(3.8, rv * 1.9)
    elif x == 'intimate_close':
        st['reverb'] = rv * 0.7
        m['width'] = min(float(m.get('width', 1.0) or 1.0), 0.85)
    elif x == 'club_punchy':
        m['drive'] = max(0.15, float(m.get('drive', 0) or 0))
        st['sc_depth'] = max(0.35, float(st.get('sc_depth', 0) or 0))
    elif x in ('tape_degraded', 'lofi_degraded'):
        m['lofi'] = True
        m['wobble'] = max(2.5 if x == 'tape_degraded' else 1.5, float(m.get('wobble', 0) or 0))
        if x == 'lofi_degraded':
            m['air'] = min(-2.5, float(m.get('air', 0) or 0))
    # harmony
    h = tr.get('harmony')
    if h == 'jazz_extensions':
        st.update(chord_size=min(5, max(4, st['chord_size'] + 1)), voicing='open')
    elif h == 'simple_pop_harmony':
        st['chord_size'] = 3
    elif h == 'modal':
        modes = [s for s in st['scales'] if s in ('dorian', 'mixolydian', 'lydian', 'phrygian')]
        st['scales'] = modes or ['dorian', 'mixolydian']
    elif h == 'chromatic_colour':
        st['chord_size'] = max(4, st['chord_size'])
    # drop / payoff
    d = tr.get('drop')
    fam = {'sudden': ['pause', 'stops', 'drumless'], 'groove_drop': ['filter', 'hats', 'pickup'],
           'long_build': ['roll', 'filter', 'swell', 'lift'], 'emotional_swell': ['swell', 'cymbal', 'wash', 'lift']}.get(d)
    if fam:
        st['build_family'] = fam
        st['plain_drops'] = d in ('sudden', 'groove_drop')
    # arrangement / variation
    a = tr.get('arrangement')
    if a in FORM_FOR:
        from .styles import FORMS
        if FORM_FOR[a] in FORMS and not st.get('composer'):
            st['form'] = FORM_FOR[a]
            st.pop('forms', None)
            st['form_scale'] = 2 if st['bpm'][0] >= 160 else 1
    if (a == 'switchup_heavy' or tr.get('variation') == 'switchup') and bass and not st.get('bass_switch'):
        from .styles import POOLS
        alts = [i for i in (POOLS.get(name, {}).get('bass') or []) if not str(i).startswith('sf:')]
        pair = [bass['inst']] + [i for i in alts + ['growl', 'reese', 'fmbass'] if i != bass['inst']][:1]
        st['bass_switch'], st['switch_bars'] = pair, 2
    return st


def shape_form(form, opts, name):
    """Density, energy curve and long builds: which parts play in each section and the written dynamics."""
    tr = wanted(opts, name)
    if not tr or not form:
        return form
    n = len(form)
    out = []
    dens, curve = tr.get('density'), tr.get('energy')
    for i, (sname, bars, layers, o) in enumerate(form):
        layers, o = set(layers), dict(o)
        pos = i / max(1, n - 1)
        big = o.get('drop') or sname in ('drop', 'chorus', 'climax', 'peak')
        d = dens
        if dens == 'evolving':
            d = 'sparse' if pos < 0.4 else ('dense' if pos > 0.6 else 'medium')
        if d == 'sparse':
            thin = layers - {'arp'} - ({'pad'} if 'chords' in layers else set()) - (set() if big else {'lead'})
            layers = thin or layers
        elif d == 'dense' and (big or 'chords' in layers) and not o.get('build'):
            layers |= {'pad', 'arp'}
        if tr.get('drop') == 'long_build' and o.get('build'):
            bars = bars * 2
        if curve and not o.get('build') and o.get('level') is None and sname not in ('intro', 'outro'):
            lv = {'flat_hypnotic': 0.92,
                  'slow_build': 0.68 + 0.32 * min(1.0, pos / 0.7),
                  'peaks_and_valleys': 1.0 if big else 0.74,
                  'continuous_climb': 0.66 + 0.34 * pos,
                  'sudden_contrasts': 1.0 if big else 0.5,
                  'emotional_arc': 0.62 + 0.38 * (pos / 0.7 if pos <= 0.7 else max(0.0, 1 - (pos - 0.7) / 0.3 * 0.75)),
                  }.get(curve)
            if lv is not None:
                o['level'] = round(max(0.4, min(1.0, lv)), 3)
        out.append((sname, bars, layers, o))
    return out
