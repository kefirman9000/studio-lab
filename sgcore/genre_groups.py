"""Sub-groups inside each genre tab, so 160+ genres are easy to browse: the style list shows these as headers.

Every genre belongs to exactly one group (tests/features.py checks it). A genre added to styles.py without a group
lands in 'More' at the bottom of its tab until it is filed here.
"""

GROUPS = {
    'Electronic': [
        ('House & Disco', ['house', 'deep_house', 'tech_house', 'progressive_house', 'acid_house', 'afro_house', 'melodic_house',
                           'organic_house', 'sunny_melodic_house', 'nineties_club_house', 'italo_disco', 'future_funk',
                           'eurodance', 'bigroom', 'bass_house', 'nu_disco', 'tokyo_deep_house', 'piano_house_90s', 'garage_house', 'mallet_house']),
        ('Techno & Trance', ['techno', 'minimal', 'melodic_techno', 'new_beat', 'trance', 'uplifting_trance',
                             'progressive_trance', 'psytrance', 'trance_pop_90s', 'hard_trance', 'uk_bass_130']),
        ('Dubstep, Garage & Bass', ['dubstep', 'brostep', 'riddim', 'melodic_dubstep', 'chillstep', 'deep_dubstep', 'deep_dubstep_minimal',
                                    'deep_dubstep_rollers', 'future_bass', 'ukgarage', 'future_garage', 'early_dubstep', 'bassline_140', 'grime']),
        ('Drum & Bass, Breaks & Hard', ['dnb', 'liquid_dnb', 'neurofunk', 'jungle', 'breakcore', 'braindance', 'rave_hardcore',
                                        'hardstyle', 'gabber', 'electro', 'funky_breaks']),
        ('Hip-Hop, Trap & Phonk', ['trap', 'uk_drill', 'uk_road_rap', 'rage', 'plugg', 'cloud_rap', 'luxury_rap', 'orchestral_hiphop',
                                   'jersey_club', 'phonk', 'memphis_phonk', 'house_phonk', 'brazilian_phonk', 'hard_trap', 'switch_trap', 'wonky_beats']),
        ('Pop, R&B & Hopecore', ['synthpop', 'kpop', 'teen_pop', 'hyperpop', 'alt_rnb', 'hopecore', 'hopecore_dreamy', 'club_pop', 'glitch_pop']),
        ('Afro, Latin & Caribbean', ['afrobeats', 'amapiano', 'reggaeton', 'moombahton', 'dancehall', 'baile_funk', 'funk_150']),
        ('Chill, Lo-fi & Ambient', ['lofi', 'downtempo', 'ambient', 'ambient_beat', 'vaporwave', 'new_age_chant', 'midfi_synthfunk']),
        ('Retro & Video Game', ['synthwave', 'chiptune', 'ps1_game']),
        ('Hauntology', ['hauntology', 'hauntology_sunlit', 'hauntology_dark', 'hauntology_melody', 'hauntology_lullaby',
                        'hauntology_campfire', 'hauntology_cold']),
    ],
    'Classic': [
        ('Rock & Metal', ['rock', 'indie_rock', 'alt_rock_90s', 'punk', 'soft_rock', 'jam_band', 'jam_rock_80s', 'metal',
                          'symphonic_metal', 'lofi_rock', 'boogie_rock', 'nu_metal', 'spooky_surf']),
        ('Pop & Indie', ['pop', 'bedroom_pop', 'chamber_pop', 'city_pop', 'holiday', 'sophisti_pop', 'psych_pop']),
        ('Funk & Disco', ['funk', 'disco', 'disco_funk', 'smooth_funk', 'electro_funk']),
        ('Soul, R&B & Gospel', ['motown', 'soul_ballad', 'gospel', 'rnb', 'neo_soul', 'new_jack_swing', 'quiet_storm', 'slow_jam']),
        ('Hip-Hop', ['boombap', 'jazz_rap', 'g_funk', 'smooth_90s_rap', 'soul_sample_rap', 'bay_rap', 'futuristic_bounce']),
        ('Jazz', ['jazz', 'bebop', 'modal_jazz', 'soul_jazz', 'fusion', 'smooth_jazz']),
        ('Swing & Big Band', ['swing', 'swing_tomtom', 'big_band_50s', 'western_swing']),
        ('Country, Folk & Blues', ['country', 'modern_country', 'country_waltz', 'outlaw_country', 'western', 'bluegrass',
                                   'folk', 'celtic_jig', 'blues', 'folk_jam']),
        ('Latin & Caribbean', ['bossa_nova', 'salsa', 'cumbia', 'tango', 'reggae', 'ska', 'soca']),
        ('World', ['raga_fusion', 'japanese_zen']),
    ],
    'Orchestral': [
        ('Film & Trailer', ['cinematic_journey', 'cinematic_journey_low', 'cinematic', 'film_piano', 'adventure', 'tension',
                            'hybrid_trailer']),
        ('Epic', ['epic_orchestral', 'epic_battle', 'epic_choir', 'heroic_anthem', 'symphonic_finale']),
        ('Solo Piano', ['piano_miniature']),
        ('Ambient & Experimental', ['field_ambient']),
        ('Fantasy & Games', ['fantasy_rpg']),
        ('Classical Eras', ['baroque', 'minuet', 'classical_period', 'waltz', 'romantic', 'impressionism', 'minimalism',
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
