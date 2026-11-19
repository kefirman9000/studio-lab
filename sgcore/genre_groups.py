"""Sub-groups inside each genre tab, so 160+ genres are easy to browse: the style list shows these as headers.

Every genre belongs to exactly one group (tests/features.py checks it). A genre added to styles.py without a group
lands in 'More' at the bottom of its tab until it is filed here.
"""

GROUPS = {
    'Electronic': [
        ('House & Disco', ['house', 'deep_house', 'tech_house', 'progressive_house', 'acid_house', 'afro_house', 'melodic_house',
                           'organic_house', 'sunny_melodic_house', 'emotive_deep_house', 'nineties_club_house', 'pop_house_90s', 'italo_disco', 'future_funk',
                           'eurodance', 'bigroom', 'bass_house', 'nu_disco', 'tokyo_deep_house', 'piano_house_90s', 'uk_bounce_house', 'outsider_house', 'garage_house', 'mallet_house', 'french_house', 'electro_swing', 'tropical_house', 'hi_nrg', 'brazilian_bass']),
        ('Techno & Trance', ['techno', 'minimal', 'melodic_techno', 'new_beat', 'trance', 'uplifting_trance',
                             'progressive_trance', 'club_trance_2000s', 'festival_psy', 'progressive_trance_2010s', 'vocal_trance_remix', 'electro_prog_trance', 'psytrance', 'progressive_psy', 'goa_trance', 'darkpsy', 'trance_pop_90s', 'hard_trance', 'uk_bass_130', 'uk_tribal_techno', 'hard_techno', 'dub_techno']),
        ('Dubstep, Garage & Bass', ['dubstep', 'brostep', 'riddim', 'melodic_dubstep', 'chillstep', 'deep_dubstep', 'deep_dubstep_minimal',
                                    'deep_dubstep_rollers', 'deep_dubstep_rolling', 'steppy_halftime', 'sub_pressure_140', 'emotive_2step', 'rolling_atmos_bass', 'chipmunk_2step', 'glitch_future_bass', 'future_bass', 'ukgarage', 'future_garage', 'early_dubstep', 'bassline_140', 'grime', 'uk_funky', 'speed_garage', 'midtempo_bass']),
        ('Drum & Bass, Breaks & Hard', ['dnb', 'liquid_dnb', 'liquid_euphoric', 'liquid_dancefloor', 'anthem_dnb', 'neurofunk', 'neurofunk_lite', 'jump_up', 'jungle', 'breakcore', 'braindance', 'idm_jungle_theme', 'drill_space', 'rave_hardcore',
                                        'hardstyle', 'gabber', 'electro', 'funky_breaks', 'big_beat', 'uk_hardcore']),
        ('Hip-Hop, Trap & Phonk', ['trap', 'uk_drill', 'uk_road_rap', 'rage', 'plugg', 'cloud_rap', 'luxury_rap', 'orchestral_hiphop',
                                   'jersey_club', 'phonk', 'memphis_phonk', 'house_phonk', 'brazilian_phonk', 'hard_trap', 'trap_metal', 'bass_warp_trap', 'bass_warp_fast', 'switchup_808', 'switchup_808_dj', 'switchup_808_hard', 'switchup_deathcore', 'switchup_mallets', 'screwed_slab', 'switch_trap', 'wonky_beats', 'baltimore_club', 'witch_house', 'latin_trap']),
        ('Pop, R&B & Hopecore', ['synthpop', 'kpop', 'teen_pop', 'hyperpop', 'alt_rnb', 'hopecore', 'hopecore_dreamy', 'hopecore_breaks', 'club_pop', 'glitch_pop', 'freestyle']),
        ('Afro, Latin & Caribbean', ['afrobeats', 'amapiano', 'reggaeton', 'moombahton', 'dancehall', 'baile_funk', 'funk_150', 'gqom']),
        ('Chill, Lo-fi & Ambient', ['lofi', 'downtempo', 'balearic_chill', 'sunrise_chillwave', 'hazy_downtempo', 'analog_arp_drive', 'ambient', 'ambient_beat', 'vaporwave', 'new_age_chant', 'chant_downtempo', 'midfi_synthfunk', 'trip_hop', 'spooky_tv_theme', 'berlin_school']),
        ('Footwork & Juke', ['footwork', 'footwork_soulful', 'footwork_dark', 'juke', 'juke_raw', 'juke_house']),
        ('Retro & Video Game', ['synthwave', 'dark_synthwave', 'chiptune', 'ps1_game', 'darkwave_ebm', 'krautrock']),
        ('Hauntology', ['hauntology', 'hauntology_sunlit', 'hauntology_dark', 'hauntology_melody', 'hauntology_lullaby',
                        'hauntology_campfire', 'hauntology_cold']),
    ],
    'Classic': [
        ('Rock & Metal', ['rock', 'indie_rock', 'alt_rock_90s', 'punk', 'soft_rock', 'jam_band', 'jam_rock_80s', 'metal',
                          'symphonic_metal', 'lofi_rock', 'boogie_rock', 'boogie_blues_rock', 'nu_metal', 'cybergrind', 'spooky_surf', 'monster_theme', 'monster_organ', 'surf_rock', 'shoegaze', 'post_rock', 'math_rock', 'pop_punk', 'doom_metal', 'stoner_raga', 'garage_rock', 'rockabilly', 'post_punk']),
        ('Pop & Indie', ['pop', 'bedroom_pop', 'velvet_pop', 'chamber_pop', 'city_pop', 'holiday', 'sophisti_pop', 'psych_pop', 'musical_theatre', 'anime_opening', 'shakuhachi_pop']),
        ('Funk & Disco', ['funk', 'disco', 'disco_funk', 'smooth_funk', 'electro_funk', 'afrobeat']),
        ('Soul, R&B & Gospel', ['motown', 'soul_ballad', 'gospel', 'modern_gospel', 'rnb', 'neo_soul', 'new_jack_swing', 'uk_rnb_swing', 'quiet_storm', 'slow_jam']),
        ('Hip-Hop', ['boombap', 'beat_tape_cinematic', 'jazz_rap', 'g_funk', 'smooth_90s_rap', 'soul_sample_rap', 'bay_rap', 'futuristic_bounce']),
        ('Jazz', ['jazz', 'bebop', 'modal_jazz', 'soul_jazz', 'fusion', 'smooth_jazz', 'gypsy_jazz', 'ragtime', 'ethio_jazz', 'exotica', 'smooth_jazz_horns']),
        ('Swing & Big Band', ['swing', 'swing_tomtom', 'big_band_50s', 'western_swing', 'nola_brass']),
        ('Country, Folk & Blues', ['country', 'modern_country', 'country_waltz', 'outlaw_country', 'western', 'bluegrass',
                                   'folk', 'celtic_jig', 'blues', 'folk_jam']),
        ('Latin & Caribbean', ['bossa_nova', 'salsa', 'cumbia', 'tango', 'reggae', 'ska', 'soca', 'groovy_soca', 'dub', 'corridos_tumbados', 'bachata', 'merengue', 'samba', 'son_cubano', 'flamenco_rumba']),
        ('World', ['raga_fusion', 'japanese_zen', 'bhangra', 'klezmer', 'gamelan', 'rai']),
        ('South Asian', ['qawwali', 'bollywood', 'ghazal']),
        ('Arabic', ['takht_maqam', 'raqs_sharqi', 'arab_pop', 'sufi_dhikr']),
        ('Psych & World Rock', ['anatolian_psych', 'thai_funk', 'chicha', 'desert_blues']),
        ('Hindu devotional', ['bhajan', 'sitar_bhajan', 'tabla_bhajan', 'kirtan', 'drum_kirtan', 'aarti', 'santoor_raga', 'jugalbandi', 'carnatic_kriti']),
    ],
    'Orchestral': [
        ('Film & Trailer', ['cinematic_journey', 'cinematic_journey_low', 'cinematic', 'film_piano', 'adventure', 'tension',
                            'hybrid_trailer', 'festive_cinematic']),
        ('Epic', ['epic_orchestral', 'epic_battle', 'epic_choir', 'heroic_anthem', 'symphonic_finale']),
        ('Solo Piano', ['piano_miniature']),
        ('Ambient & Experimental', ['field_ambient', 'fourth_world']),
        ('Fantasy & Games', ['fantasy_rpg']),
        ('Christmas & Holiday', ['christmas_joyful', 'christmas_magic', 'christmas_mischief']),
        ('Classical Eras', ['baroque', 'baroque_organ', 'minuet', 'classical_period', 'waltz', 'romantic', 'impressionism', 'minimalism',
                            'neoclassical', 'chamber', 'orchestral']),
    ],
}

GROUP_OF = {sid: g for cat in GROUPS.values() for g, ids in cat for sid in ids}


def group_of(style_id):
    return GROUP_OF.get(style_id, 'More')


def order(category):
    """The group names of a tab, in display order (plus 'More' for anything not filed yet)."""
    return [g for g, _ in GROUPS.get(category, [])] + ['More']


def rank(style_id):
    """Sort key: group position, then the genre's position inside its group."""
    for cat in GROUPS.values():
        for gi, (g, ids) in enumerate(cat):
            if style_id in ids:
                return gi, ids.index(style_id)
    return 99, 0
