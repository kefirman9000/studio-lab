"""(2.3) Electronic genres play electronic basses.

Bass guitars, upright and acoustic basses (sampled or modelled) sound like a real player plucking strings - out of place
under a synth record. Every Electronic genre loses them from its bass rotation, and a genre whose own bass was one of
them gets a synth bass instead. Synth basses with a plucky filter envelope (saw bass, FM bass, SH-101 ...) stay: plucky
is fine, it just shouldn't sound like a real bass.

A few genres are built on a live / sampled bass player and keep it: electro swing (swing-band samples), krautrock (a band)
and future funk (chopped disco records with their slap bass).

Also: synthwave and electro use synth brass, not a real brass section, and tech house drops the acoustic piano.
Also (any category): a genre's own 2.0 rig guitar (metal guitar, jangle, dreadnought ...) leads its pool. Before, a
metal song that picked from its pool got the plain 'guitar', which upgrades to the generic rhythm guitar - never the
metal guitar the genre was written for.
Runs last, after every other pool step (see the end of compose.py)."""
from .styles import POOLS, STYLES

REAL_BASS = {'sf:fingerbass', 'sf:acbass', 'sf:pickbass', 'sf:slapbass', 'sf:contrabass', 'fingerbass', 'acbass', 'pickbass',
             'slapbass', 'ebass', 'ebass_dark', 'ebass_driven', 'ebass_bright', 'ebass_soft', 'upright', 'upright_dark',
             'upright_soft', 'contrabass', 'real:ebass', 'real:upright', 'tuba'}
KEEP_REAL = {'electro_swing', 'krautrock', 'future_funk'}
# synth bass that takes over when a genre's own bass was a real one (closest feel first)
# synth basses added where taking the bass guitars out left a rotation too short
REFILL = {'sunlit_electronica': ['dreambass', 'junobass', 'sinebass'], 'daydream_downtempo': ['junobass', 'sinebass'],
          'sunrise_chillwave': ['junobass', 'sinebass'], 'hazy_downtempo': ['junobass', 'dreambass']}
REPLACE = {'analog_arp_drive': 'moogbass', 'drill_space': 'fmbass', 'idm_jungle_theme': 'moogbass', 'sunrise_chillwave': 'moogbass'}
SWAPS = {
    'synthwave': {'chords': {'brass': 'synthbrass'}, 'lead': {'brass': 'synthbrass'}},
    'electro': {'chords': {'brass': 'synthbrass', 'brass_wide': 'synthbrass'}},
    'tech_house': {'chords': {'piano': None, 'piano_tape': None}},
}


# (2.4) the new instruments join the rotation of the genres they belong to: {sound: ({genre: roles}, roles-for-all)}
NEW_SOUNDS = {
    'tonewheel': (['gospel', 'modern_gospel', 'soul_ballad', 'motown', 'rnb', 'neo_soul', 'soul_jazz', 'jam_band', 'jam_rock_80s',
                   'blues', 'funk', 'reggae', 'ska', 'dub', 'smooth_funk', 'quiet_storm', 'slow_jam', 'jazz', 'jazz_rap', 'psych_pop'],
                  ('chords', 'pad', 'lead')),
    'rockorgan': (['rock', 'boogie_rock', 'boogie_blues_rock', 'jam_band', 'garage_rock', 'alt_rock_90s', 'doom_metal',
                   'celtic_punk'], ('chords', 'pad', 'lead')),
    'wahgtr': (['funk', 'disco', 'disco_funk', 'smooth_funk', 'electro_funk', 'g_funk', 'afrobeat', 'nu_disco', 'future_funk',
                'french_house', 'thai_funk', 'funk_150', 'new_jack_swing'], ('chords', 'arp')),
    'twelvestring': (['folk', 'folk_jam', 'indie_rock', 'psych_pop', 'jam_band', 'soft_rock', 'chamber_pop', 'shoegaze', 'post_rock',
                      'celtic_jig', 'celtic_reel', 'bedroom_pop'], ('chords', 'arp')),
    'lapsteel': (['blues', 'country', 'outlaw_country', 'western', 'western_swing', 'modern_country', 'boogie_blues_rock',
                  'desert_blues', 'exotica', 'surf_rock'], ('lead',)),
    'dobro': (['bluegrass', 'country', 'blues', 'folk_jam', 'outlaw_country', 'folk', 'country_waltz'], ('lead', 'arp')),
    'ukulele': (['tropical_house', 'pop', 'bedroom_pop', 'hopecore', 'hopecore_dreamy', 'exotica', 'reggae', 'folk', 'teen_pop',
                 'balearic_chill'], ('chords', 'arp')),
    'bouzouki': (['celtic_jig', 'celtic_reel', 'celtic_air', 'epic_celtic', 'folk', 'folk_jam'], ('chords', 'arp')),
    'dulcimer': (['celtic_jig', 'celtic_reel', 'celtic_air', 'epic_celtic', 'folk', 'fantasy_rpg', 'christmas_magic',
                  'storybook_score', 'festive_cinematic'], ('arp',)),
    'highlandpipes': (['celtic_jig', 'celtic_reel', 'epic_celtic', 'celtic_punk'], ('lead',)),
    'didgeridoo': (['fourth_world', 'field_ambient', 'new_age_chant', 'chant_downtempo', 'raga_fusion', 'ambient'], ('pad',)),
    'donk': (['bassline_140', 'uk_bounce_house', 'speed_garage', 'bass_house', 'uk_hardcore', 'rave_hardcore', 'hard_trance'], ('bass',)),
    'glitchchop': (['braindance', 'glitch_pop', 'glitch_future_bass', 'hyperpop', 'breakcore', 'idm_jungle_theme', 'wonky_beats'],
                   ('lead', 'arp')),
    'omnichord': (['sunrise_chillwave', 'bedroom_pop', 'lofi', 'hazy_downtempo', 'daydream_downtempo', 'sunlit_electronica',
                   'hopecore_dreamy', 'vaporwave', 'city_pop', 'dream_synthscape'], ('arp', 'chords')),
    'stylophone': (['synthpop', 'electro', 'krautrock', 'new_beat', 'post_punk', 'freestyle', 'italo_disco', 'chiptune'], ('lead', 'arp')),
    'toypiano': (['storybook_score', 'hauntology_lullaby', 'hauntology_melody', 'christmas_mischief', 'christmas_magic', 'bedroom_pop',
                  'musical_theatre', 'spooky_tv_theme'], ('lead', 'arp')),
}


def add_new_sounds():
    from .instruments import INSTRUMENTS
    for inst, (genres, roles) in NEW_SOUNDS.items():
        if inst not in INSTRUMENTS:
            continue
        for g in genres:
            st = STYLES.get(g)
            if not st or st.get('exact_pools'):
                continue
            pools = POOLS.setdefault(g, {})
            have = {t.get('layer') for t in st['tracks']}
            for r in roles:
                if r not in have:
                    continue
                lst = pools.get(r)
                if lst is None:
                    own = next((t['inst'] for t in st['tracks'] if t.get('layer') == r and t.get('name') == r), None)
                    if not own:
                        continue
                    lst = pools[r] = [own]
                if inst not in lst:
                    lst.append(inst)


def apply():
    add_new_sounds()
    from .instruments import INSTRUMENTS
    changed = []
    for g, st in STYLES.items():
        if st.get('category') != 'Electronic' or g in KEEP_REAL:
            continue
        pools = POOLS.setdefault(g, {})
        bpool = pools.get('bass')
        if bpool is not None:
            keep = [i for i in bpool if i not in REAL_BASS]
            if len(keep) != len(bpool):
                keep += [i for i in REFILL.get(g, []) if i not in keep]
                bpool[:] = keep
                changed.append(g)
        for t in st['tracks']:
            if t.get('layer') == 'bass' and t.get('inst') in REAL_BASS:
                new = REPLACE.get(g) or next((i for i in (bpool or []) if i in INSTRUMENTS), 'moogbass')
                t['inst'] = new
                t['p'] = {k: v for k, v in (t.get('p') or {}).items() if k in ('cut',)}
                if bpool is not None:
                    if new in bpool:
                        bpool.remove(new)
                    bpool.insert(0, new)                     # the genre's own sound leads its rotation
                if g not in changed:
                    changed.append(g)
        for pal in ((st.get('song_variations') or {}).get('palette') or []):   # per-song palettes carry their own bass
            if isinstance(pal, dict) and pal.get('bass') in REAL_BASS:
                pal['bass'] = REPLACE.get(g) or next((i for i in (bpool or []) if i in INSTRUMENTS), 'moogbass')
    for g, roles in SWAPS.items():
        for role, m in roles.items():
            lst = POOLS.get(g, {}).get(role)
            if not lst:
                continue
            out = []
            for i in lst:
                j = m.get(i, i) if i in m else i
                if j and j in INSTRUMENTS and j not in out:
                    out.append(j)
            lst[:] = out
            for t in STYLES[g]['tracks']:
                if t.get('layer') == role and t.get('inst') in m and m[t['inst']]:
                    t['inst'] = m[t['inst']]
    from .guitars2 import NEW as RIG
    from .styles import GTR_UPGRADE
    for g, st in STYLES.items():
        for t in st['tracks']:
            lst = POOLS.get(g, {}).get(t.get('layer'))
            inst = t.get('inst')
            if t.get('name') != t.get('layer') or not lst or inst not in RIG or lst[0] == inst:
                continue
            if inst in lst:
                lst.remove(inst)
            lst.insert(0, inst)
        own = {t.get('name'): t.get('inst') for t in st['tracks']}
        if own.get('chords') == 'metalgtr':              # metal: a pooled 'guitar' is the metal guitar, not a clean rhythm one
            for k in ('guitar', 'odguitar', 'sf:odguitar', 'sf:guitar'):
                GTR_UPGRADE.setdefault(g, {})[k] = 'metalgtr'
    return changed
