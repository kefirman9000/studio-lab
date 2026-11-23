"""Sub-groups inside each genre tab, so 160+ genres are easy to browse: the style list shows these as headers.

Every genre belongs to exactly one group in GROUPS (its sound family, used by the engine) and one shelf in DISPLAY (how
the list is shown) - tests/features.py checks both. A genre added to styles.py without a shelf lands in 'More' at the
bottom of its tab until it is filed here.
"""

GROUPS = {
    'Electronic': [
        ('House & Disco', ['house', 'deep_house', 'tech_house', 'progressive_house', 'acid_house', 'afro_house', 'melodic_house',
                           'organic_house', 'sunny_melodic_house', 'emotive_deep_house', 'nineties_club_house', 'pop_house_90s', 'italo_disco', 'future_funk',
                           'eurodance', 'bigroom', 'bass_house', 'nu_disco', 'tokyo_deep_house', 'piano_house_90s', 'uk_bounce_house', 'outsider_house', 'garage_house', 'mallet_house', 'french_house', 'electro_swing', 'tropical_house', 'hi_nrg', 'brazilian_bass', 'progressive_journey']),
        ('Techno & Trance', ['techno', 'minimal', 'melodic_techno', 'euphoric_trance', 'euphoric_uk_techno', 'new_beat', 'trance', 'uplifting_trance', 'classic_vocal_trance', 'festival_techno',
                             'progressive_trance', 'club_trance_2000s', 'anthem_trance_2000', 'festival_psy', 'progressive_trance_2010s', 'vocal_trance_remix', 'electro_prog_trance', 'psytrance', 'progressive_psy', 'goa_trance', 'darkpsy', 'trance_pop_90s', 'hard_trance', 'uk_bass_130', 'uk_tribal_techno', 'hard_techno', 'dub_techno']),
        ('Dubstep, Garage & Bass', ['dubstep', 'switchup_bass', 'ethereal_wave', 'brostep', 'riddim', 'melodic_dubstep', 'chillstep', 'deep_dubstep', 'slow_wobble', 'dark_dubstep_classic', 'deep_dubstep_minimal',
                                    'deep_dubstep_rollers', 'deep_dubstep_rolling', 'steppy_halftime', 'sub_pressure_140', 'emotive_2step', 'rolling_atmos_bass', 'chipmunk_2step', 'glitch_future_bass', 'future_bass', 'ukgarage', 'future_garage', 'early_dubstep', 'bassline_140', 'grime', 'uk_funky', 'speed_garage', 'midtempo_bass']),
        ('Drum & Bass, Breaks & Hard', ['dnb', 'liquid_dnb', 'liquid_euphoric', 'liquid_dancefloor', 'anthem_dnb', 'neurofunk', 'neurofunk_lite', 'jump_up', 'jungle', 'breakcore', 'braindance', 'idm_jungle_theme', 'drill_space', 'rave_hardcore',
                                        'hardstyle', 'gabber', 'electro', 'funky_breaks', 'big_beat', 'uk_hardcore']),
        ('Hip-Hop, Trap & Phonk', ['trap', 'uk_drill', 'uk_road_rap', 'rage', 'plugg', 'melodic_club_rap', 'cloud_rap', 'luxury_rap', 'orchestral_hiphop',
                                   'jersey_club', 'phonk', 'memphis_phonk', 'house_phonk', 'brazilian_phonk', 'hard_trap', 'trap_metal', 'bass_warp_trap', 'bass_warp_fast', 'switchup_808', 'switchup_808_dj', 'switchup_808_hard', 'switchup_deathcore', 'dark_drill', 'switchup_mallets', 'screwed_slab', 'switch_trap', 'wonky_beats', 'warped_electronica', 'baltimore_club', 'witch_house', 'latin_trap', 'cinematic_trap']),
        ('Pop, R&B & Hopecore', ['synthpop', 'kpop', 'teen_pop', 'hyperpop', 'alt_rnb', 'hopecore', 'hopecore_dreamy', 'hopecore_breaks', 'club_pop', 'glitch_pop', 'freestyle', 'synth_rnb']),
        ('Afro, Latin & Caribbean', ['shangaan_electro', 'kuduro', 'neoperreo', 'afrobeats', 'amapiano', 'reggaeton', 'moombahton', 'dancehall', 'baile_funk', 'funk_150', 'gqom', 'afro_village_party', 'afro_village_synth', 'afro_wobble', 'bass_amapiano']),
        ('Chill, Lo-fi & Ambient', ['mallsoft', 'lofi', 'sunlit_electronica', 'daydream_downtempo', 'downtempo', 'balearic_chill', 'sunrise_chillwave', 'hazy_downtempo', 'analog_arp_drive', 'ambient', 'ambient_beat', 'dream_synthscape', 'vignette_synthscape', 'vaporwave', 'new_age_chant', 'chant_downtempo', 'midfi_synthfunk', 'trip_hop', 'spooky_tv_theme', 'berlin_school']),
        ('Footwork & Juke', ['footwork', 'footwork_soulful', 'footwork_dark', 'juke', 'juke_raw', 'juke_house']),
        ('Retro & Video Game', ['darksynth', 'synthwave', 'monster_synth', 'dark_synthwave', 'chiptune', 'ps1_game', 'darkwave_ebm', 'krautrock']),
        ('Hauntology', ['hauntology', 'hauntology_sunlit', 'hauntology_dark', 'hauntology_melody', 'hauntology_lullaby',
                        'hauntology_campfire', 'hauntology_cold']),
    ],
    'Classic': [
        ('Rock & Metal', ['rock', 'indie_rock', 'alt_rock_90s', 'grunge', 'punk', 'soft_rock', 'jam_band', 'jam_rock_80s', 'metal',
                          'symphonic_metal', 'lofi_rock', 'boogie_rock', 'boogie_blues_rock', 'nu_metal', 'cybergrind', 'slam', 'spooky_surf', 'monster_theme', 'monster_organ', 'surf_monster', 'surf_rock', 'shoegaze', 'post_rock', 'math_rock', 'pop_punk', 'doom_metal', 'stoner_raga', 'garage_rock', 'rockabilly', 'post_punk']),
        ('Pop & Indie', ['dream_pop', 'pop', 'bedroom_pop', 'velvet_pop', 'chamber_pop', 'city_pop', 'holiday', 'sophisti_pop', 'psych_pop', 'musical_theatre', 'anime_opening', 'shakuhachi_pop']),
        ('Funk & Disco', ['funk', 'disco', 'disco_funk', 'smooth_funk', 'electro_funk', 'afrobeat']),
        ('Soul, R&B & Gospel', ['motown', 'soul_ballad', 'gospel', 'modern_gospel', 'rnb', 'neo_soul', 'new_jack_swing', 'uk_rnb_swing', 'quiet_storm', 'slow_jam']),
        ('Hip-Hop', ['boombap', 'beat_tape_cinematic', 'jazz_rap', 'g_funk', 'smooth_90s_rap', 'soul_sample_rap', 'choir_rap', 'bay_rap', 'futuristic_bounce', 'jazz_hop']),
        ('Jazz', ['jazz', 'bebop', 'modal_jazz', 'soul_jazz', 'fusion', 'smooth_jazz', 'gypsy_jazz', 'ragtime', 'ethio_jazz', 'exotica', 'smooth_jazz_horns']),
        ('Swing & Big Band', ['swing', 'swing_tomtom', 'big_band_50s', 'western_swing', 'nola_brass']),
        ('Celtic', ['celtic_jig', 'celtic_reel', 'celtic_hornpipe', 'slip_jig', 'strathspey', 'celtic_polka', 'celtic_session', 'celtic_slow_air', 'celtic_punk', 'sea_shanty', 'highland_pipes', 'pipes_orchestra', 'breton_an_dro', 'galician_muineira', 'clarsach_air', 'celtic_new_age']),
        ('Country, Folk & Blues', ['country', 'modern_country', 'country_waltz', 'outlaw_country', 'western', 'bluegrass',
                                   'folk', 'blues', 'folk_jam']),
        ('Latin & Caribbean', ['bossa_nova', 'salsa', 'cumbia', 'tango', 'reggae', 'ska', 'soca', 'groovy_soca', 'dub', 'corridos_tumbados', 'bachata', 'merengue', 'samba', 'son_cubano', 'flamenco_rumba']),
        ('World', ['highlife', 'soukous', 'balkan_brass', 'raga_fusion', 'japanese_zen', 'bhangra', 'klezmer', 'gamelan', 'rai']),
        ('South Asian', ['qawwali', 'bollywood', 'ghazal']),
        ('Arabic', ['takht_maqam', 'raqs_sharqi', 'arab_pop', 'sufi_dhikr']),
        ('Psych & World Rock', ['anatolian_psych', 'thai_funk', 'chicha', 'desert_blues']),
        ('Hindu devotional', ['bhajan', 'sitar_bhajan', 'tabla_bhajan', 'kirtan', 'drum_kirtan', 'aarti', 'santoor_raga', 'jugalbandi', 'carnatic_kriti']),
    ],
    'Orchestral': [
        ('Film & Trailer', ['horror', 'wonder', 'cinematic_journey', 'cinematic_journey_low', 'cinematic', 'film_piano', 'adventure', 'tension',
                            'hybrid_trailer', 'festive_cinematic', 'storybook_score']),
        ('Epic', ['epic_orchestral', 'epic_battle', 'epic_choir', 'heroic_anthem', 'symphonic_finale']),
        ('Solo Piano', ['piano_miniature']),
        ('Ambient & Experimental', ['field_ambient', 'fourth_world']),
        ('Fantasy & Games', ['fantasy_rpg']),
        ('Christmas & Holiday', ['christmas_joyful', 'christmas_magic', 'christmas_mischief']),
        ('Classical Eras', ['gregorian_chant', 'baroque', 'baroque_organ', 'minuet', 'classical_period', 'waltz', 'romantic', 'impressionism', 'minimalism',
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


# ------------------------------------------------------------------------------------------------ (2.14.1) display groups
# How the genre list is shown: smaller, clearer shelves (techno apart from trance, psytrance on its own, phonk on its own,
# rock apart from metal ...), each ordered from the classic / best-known genre to its offshoots. GROUPS above stays the
# *sound family* the engine uses (drum voices, effects, risers, sound pools) - moving a genre here never changes its sound.
DISPLAY = {
    'Electronic': [
        ('House', ['house', 'deep_house', 'tech_house', 'progressive_house', 'progressive_journey', 'melodic_house', 'organic_house',
                   'sunny_melodic_house', 'emotive_deep_house', 'tokyo_deep_house', 'acid_house', 'bass_house', 'garage_house', 'mallet_house',
                   'outsider_house', 'tropical_house', 'bigroom', 'nineties_club_house', 'piano_house_90s', 'pop_house_90s', 'uk_bounce_house']),
        ('Disco, French & Nu-Disco', ['nu_disco', 'french_house', 'italo_disco', 'hi_nrg', 'eurodance', 'future_funk', 'midfi_synthfunk',
                                      'electro_swing']),
        ('Techno', ['techno', 'minimal', 'melodic_techno', 'dub_techno', 'hard_techno', 'festival_techno', 'euphoric_uk_techno',
                    'uk_tribal_techno', 'uk_bass_130', 'new_beat']),
        ('Trance', ['trance', 'uplifting_trance', 'euphoric_trance', 'progressive_trance', 'progressive_trance_2010s', 'classic_vocal_trance',
                    'vocal_trance_remix', 'club_trance_2000s', 'anthem_trance_2000', 'trance_pop_90s', 'electro_prog_trance', 'hard_trance']),
        ('Psytrance', ['psytrance', 'progressive_psy', 'goa_trance', 'festival_psy', 'darkpsy']),
        ('Dubstep', ['dubstep', 'brostep', 'riddim', 'melodic_dubstep', 'chillstep', 'early_dubstep', 'dark_dubstep_classic', 'deep_dubstep',
                     'deep_dubstep_minimal', 'deep_dubstep_rollers', 'deep_dubstep_rolling', 'slow_wobble', 'steppy_halftime', 'switchup_bass',
                     'midtempo_bass']),
        ('UK Garage, Grime & Bass', ['ukgarage', 'speed_garage', 'future_garage', 'emotive_2step', 'chipmunk_2step', 'bassline_140', 'grime',
                                     'uk_funky', 'sub_pressure_140', 'rolling_atmos_bass']),
        ('Future Bass & Wave', ['future_bass', 'glitch_future_bass', 'ethereal_wave']),
        ('Drum & Bass & Jungle', ['dnb', 'liquid_dnb', 'liquid_euphoric', 'liquid_dancefloor', 'anthem_dnb', 'jump_up', 'neurofunk',
                                  'neurofunk_lite', 'jungle', 'idm_jungle_theme', 'drill_space']),
        ('Breaks, Rave & Hard Dance', ['big_beat', 'funky_breaks', 'electro', 'rave_hardcore', 'uk_hardcore', 'hardstyle', 'gabber',
                                       'breakcore', 'braindance', 'warped_electronica']),
        ('Trap & Rap', ['trap', 'hard_trap', 'rage', 'plugg', 'cloud_rap', 'melodic_club_rap', 'luxury_rap', 'cinematic_trap',
                        'orchestral_hiphop', 'latin_trap', 'trap_metal', 'switch_trap', 'uk_drill', 'dark_drill', 'uk_road_rap', 'screwed_slab',
                        'wonky_beats', 'witch_house']),
        ('Phonk', ['phonk', 'memphis_phonk', 'house_phonk', 'brazilian_phonk']),
        ('808 Switch-ups & Bass Warp', ['switchup_808', 'switchup_808_dj', 'switchup_808_hard', 'switchup_mallets', 'switchup_deathcore',
                                       'bass_warp_trap', 'bass_warp_fast']),
        ('Club: Jersey, Baltimore, Footwork', ['jersey_club', 'baltimore_club', 'footwork', 'footwork_soulful', 'footwork_dark', 'juke',
                                               'juke_raw', 'juke_house']),
        ('Pop, R&B & Hopecore', ['synthpop', 'club_pop', 'teen_pop', 'kpop', 'hyperpop', 'glitch_pop', 'freestyle', 'alt_rnb', 'synth_rnb',
                                 'hopecore', 'hopecore_dreamy', 'hopecore_breaks']),
        ('Afro & Amapiano', ['afrobeats', 'amapiano', 'bass_amapiano', 'afro_house', 'afro_village_party', 'afro_village_synth', 'afro_wobble',
                             'gqom', 'kuduro', 'shangaan_electro']),
        ('Latin, Brazilian & Caribbean', ['reggaeton', 'neoperreo', 'moombahton', 'dancehall', 'baile_funk', 'funk_150', 'brazilian_bass']),
        ('Chill & Lo-fi', ['lofi', 'downtempo', 'trip_hop', 'hazy_downtempo', 'daydream_downtempo', 'chant_downtempo', 'balearic_chill',
                           'sunlit_electronica', 'sunrise_chillwave', 'vaporwave', 'mallsoft']),
        ('Ambient & Synthscapes', ['ambient', 'ambient_beat', 'new_age_chant', 'dream_synthscape', 'vignette_synthscape', 'analog_arp_drive',
                                   'berlin_school', 'krautrock']),
        ('Synthwave & Video Game', ['synthwave', 'dark_synthwave', 'darksynth', 'darkwave_ebm', 'monster_synth', 'spooky_tv_theme', 'chiptune',
                                    'ps1_game']),
        ('Hauntology', ['hauntology', 'hauntology_sunlit', 'hauntology_dark', 'hauntology_melody', 'hauntology_lullaby',
                        'hauntology_campfire', 'hauntology_cold']),
    ],
    'Classic': [
        ('Rock', ['rock', 'indie_rock', 'alt_rock_90s', 'grunge', 'soft_rock', 'lofi_rock', 'garage_rock', 'boogie_rock', 'boogie_blues_rock',
                  'jam_band', 'jam_rock_80s', 'shoegaze', 'post_rock', 'math_rock', 'stoner_raga']),
        ('Punk', ['punk', 'pop_punk', 'post_punk', 'celtic_punk']),
        ('Metal', ['metal', 'symphonic_metal', 'nu_metal', 'doom_metal', 'slam', 'cybergrind']),
        ('Surf, Rockabilly & Spooky', ['surf_rock', 'rockabilly', 'spooky_surf', 'surf_monster', 'monster_theme', 'monster_organ']),
        ('Pop & Indie', ['pop', 'dream_pop', 'bedroom_pop', 'velvet_pop', 'chamber_pop', 'psych_pop', 'sophisti_pop', 'city_pop',
                         'anime_opening', 'shakuhachi_pop', 'musical_theatre', 'holiday']),
        ('Soul, R&B & Gospel', ['motown', 'soul_ballad', 'rnb', 'neo_soul', 'new_jack_swing', 'uk_rnb_swing', 'quiet_storm', 'slow_jam',
                                'gospel', 'modern_gospel']),
        ('Funk & Disco', ['funk', 'smooth_funk', 'electro_funk', 'disco', 'disco_funk']),
        ('Hip-Hop', ['boombap', 'jazz_rap', 'jazz_hop', 'soul_sample_rap', 'smooth_90s_rap', 'g_funk', 'bay_rap', 'futuristic_bounce',
                     'choir_rap', 'beat_tape_cinematic']),
        ('Jazz', ['jazz', 'bebop', 'modal_jazz', 'soul_jazz', 'fusion', 'smooth_jazz', 'smooth_jazz_horns', 'gypsy_jazz', 'ragtime', 'exotica']),
        ('Swing & Big Band', ['swing', 'swing_tomtom', 'big_band_50s', 'western_swing', 'nola_brass']),
        ('Country, Folk & Blues', ['country', 'modern_country', 'outlaw_country', 'country_waltz', 'western', 'bluegrass', 'folk', 'folk_jam',
                                   'blues']),
        ('Celtic', ['celtic_jig', 'celtic_reel', 'celtic_hornpipe', 'slip_jig', 'strathspey', 'celtic_polka', 'celtic_session',
                    'celtic_slow_air', 'clarsach_air', 'sea_shanty', 'highland_pipes', 'pipes_orchestra', 'breton_an_dro', 'galician_muineira',
                    'celtic_new_age']),
        ('Latin', ['salsa', 'son_cubano', 'bossa_nova', 'samba', 'cumbia', 'bachata', 'merengue', 'tango', 'flamenco_rumba', 'corridos_tumbados', 'chicha']),
        ('Caribbean', ['reggae', 'dub', 'ska', 'soca', 'groovy_soca']),
        ('African', ['afrobeat', 'highlife', 'soukous', 'ethio_jazz', 'desert_blues']),
        ('Middle East, Balkan & Klezmer', ['arab_pop', 'raqs_sharqi', 'takht_maqam', 'sufi_dhikr', 'rai', 'balkan_brass', 'klezmer',
                                           'anatolian_psych']),
        ('South Asian', ['bollywood', 'bhangra', 'qawwali', 'ghazal', 'raga_fusion']),
        ('Indian Classical & Devotional', ['bhajan', 'sitar_bhajan', 'tabla_bhajan', 'kirtan', 'drum_kirtan', 'aarti', 'santoor_raga',
                                           'jugalbandi', 'carnatic_kriti']),
        ('East & Southeast Asian', ['japanese_zen', 'gamelan', 'thai_funk']),
    ],
    'Orchestral': [
        ('Film & Trailer', ['cinematic', 'cinematic_journey', 'cinematic_journey_low', 'film_piano', 'adventure', 'wonder', 'storybook_score',
                            'festive_cinematic', 'tension', 'horror', 'hybrid_trailer']),
        ('Epic', ['epic_orchestral', 'epic_battle', 'epic_choir', 'heroic_anthem', 'symphonic_finale']),
        ('Fantasy, Games & Holiday', ['fantasy_rpg', 'christmas_joyful', 'christmas_magic', 'christmas_mischief']),
        ('Classical Eras', ['gregorian_chant', 'baroque', 'baroque_organ', 'minuet', 'classical_period', 'waltz', 'romantic', 'impressionism',
                            'neoclassical', 'minimalism', 'chamber', 'orchestral']),
        ('Piano, Ambient & Experimental', ['piano_miniature', 'field_ambient', 'fourth_world']),
    ],
}
DISPLAY_OF = {sid: g for cat in DISPLAY.values() for g, ids in cat for sid in ids}


def display_group(style_id):
    return DISPLAY_OF.get(style_id, 'More')


def display_order(category):
    return [g for g, _ in DISPLAY.get(category, [])] + ['More']


def display_rank(style_id):
    for cat in DISPLAY.values():
        for gi, (g, ids) in enumerate(cat):
            if style_id in ids:
                return gi, ids.index(style_id)
    return 99, 0
