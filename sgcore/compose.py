"""Composition: harmony, melody, bass, drums and arrangement -> a list of note events."""
import math
import random
from dataclasses import dataclass, field, asdict, replace

from .styles import STYLES, FORMS, FORM_VARIANTS
from .instruments import KITS, INSTRUMENTS, PALETTES, DRUMS, INSTRUMENT_INFO, ROLE_CHOICES
from .theory import (Key, parse_progression, parse_key, color_fits, declutter, voice_chord, VOICINGS, fold, parse_rhythm,
                     grid_of, grid_steps, lead_voicing, Ev, chord_tones_deg, COLORS)
from . import drummer
from .figures import gen_riff, vary_melody, gen_trap_hats, gen_acid_pattern
from .arrange import (BIG_SECTIONS, _track_of, BUILD_STYLES, FX_SOUNDS, build_sequence, add_build_drums, add_build_fx,
                      add_transitions, apply_ending)

VEL = {'X': 1.0, 'x': 0.78, 'o': 0.5}
LAYERS = ['kick', 'snare', 'top', 'bass', 'chords', 'pad', 'arp', 'lead', 'fx']
MELODIC_ROLES = ['bass', 'chords', 'pad', 'arp', 'lead']
SECTION_ENERGY = {'intro': 0.72, 'verse': 0.85, 'drop': 1.0, 'break': 0.68, 'outro': 0.8, 'hook': 1.0, 'A': 0.9,
                  'B': 1.0, 'C': 0.75, 'chorus': 1.0, 'bridge': 0.8, 'head': 0.95, 'solo': 0.9, 'rise': 0.8,
                  'theme': 0.95, 'calm': 0.65, 'climax': 1.0, 'loop': 1.0,
                  'var': 0.95, 'dev': 0.97, 'coda': 0.85, 'trio': 0.8}


@dataclass
class Options:
    """Every customization knob. None = use the style's default."""
    style: str = 'house'
    seed: int = 1
    bpm: int = None
    key: str = None               # 'C', 'F#', 'Bb' ...
    scale: str = None             # 'major', 'minor', 'dorian', ... or None (style picks)
    progression: str = None       # e.g. 'i-VI-III-VII' or '1-6-3-7'
    length: float = 1.0           # 0.5 = short ... 2.0 = extended
    structure: str = 'auto'       # auto | club (long DJ intro/outro) | radio (shorter) | loop (16-bar loop)
    energy: float = 0.5           # 0..1 drum density, fills, contrast
    complexity: float = 0.5       # 0..1 melody density, chord extensions, arp speed
    swing: float = None           # 0.5 (straight) .. 0.75
    humanize: float = 1.0         # 0..2 timing/velocity looseness multiplier
    instruments: dict = field(default_factory=dict)   # role -> instrument name
    kit: str = None               # drum sounds: kit / machine / sampled-break kit (never changes the patterns)
    drum_fills: str = None        # drummer: None = genre | none | fewer | more
    drum_ghosts: str = None       # drummer: None = genre | off | more
    hat_density: str = None       # drummer: None = genre | sparse | busy
    percussion: str = None        # None = genre's own | off | a set from drummer.PERC_SETS (shakers, latin, afro ...)
    drum_pattern: str = None      # drum style: None/'genre' = genre's beat | 'programmed' | 'break:<kit id>' | 'style:<genre id>'
    muted: list = field(default_factory=list)          # layers to remove
    sidechain: float = None       # 0..1 pumping depth
    sc_release: float = None      # beats
    reverb: float = 1.0           # send multiplier 0..2
    reverb_size: float = None     # seconds
    delay: float = 1.0            # send multiplier 0..2
    brightness: float = 0.0       # -1 (dark) .. +1 (bright)
    width: float = 1.0            # stereo width 0..2
    bass_boost: float = 0.0       # dB
    drive: float = 0.0            # master saturation 0..1
    loudness: float = None        # target LUFS
    lofi: bool = None             # force tape/vinyl master on/off
    vinyl: bool = None            # vinyl crackle: only True turns it on (None / False = off)
    blend: list = field(default_factory=list)          # extra styles to fuse with the main style
    blend_parts: dict = field(default_factory=dict)    # part -> style  (groove, bass, harmony, melody, form, mix)
    part_seeds: dict = field(default_factory=dict)     # re-roll one part: harmony, melody, drums, bass, chords
    midi_parts: dict = None       # (1.87) parts imported from a MIDI file {'lead'|'chords'|'bass': [[beat, len, midi, vel]], 'root': pc}
    favorites: list = None        # (1.87) your favourite sounds: picked more often when a genre chooses sounds
    lanes: dict = None            # (1.87) editor lanes {'filter'|'reverb'|'pan': {track: [[beat, value], ...]}}
    melody_check: str = 'auto'    # (1.85) write a few hooks, keep the strongest | off
    evolve: str = 'auto'          # (1.85) later drops develop (octave climb, bass pushes, stutters, half-time) | off
    call_response: str = 'auto'   # (1.85) a second sound answers the lead in the hooks: auto | on | off
    bar_variation: str = 'auto'   # (1.85) small changes in the 4th / 8th bar of phrases | off
    section_dynamics: str = 'auto'   # (1.90) layers saved for the drops, bare breakdowns, harder first downbeats | off
    genre_fills: str = 'auto'     # (1.90) DnB rewinds, dubstep drop stops with a shout, trance pitch-rising rolls | off
    polymeter: str = 'auto'       # (1.93) techno sequences looping in 3 / 5 / 6 / 7 steps against 4/4 | on | off
    phrase_evolution: str = 'auto'   # (1.94) club genres: long sections change every 8-16 bars | off
    drop_space: str = 'auto'      # (1.95.1) dubstep drops: no held pad, chords thinned to accents (the bass owns the mids) | off
    variety: float = 0.5          # 0..1 how adventurous each song's sound palette, grooves and arrangement get
    user_drums: bool = False      # use the drum samples you loaded instead of the built-in kit
    sections: list = None         # section editor: [{src, copy, bars, seeds{part:int}, vary:int, mute:[layers]}]
    engine: str = 'auto'          # auto | sampled | synth  (sampled = real recorded instruments when the library is installed)
    vst_rig: bool = False         # play parts through genre-matched plugins (sgcore.vstrigs) when they're installed
    orch_plugin: bool = False     # orchestral parts on your orchestra plugin (BBC SO / LABS) instead of the free real orchestra
    melody_style: str = None      # None = genre default | diatonic | pentatonic | blues | bebop
    voicing: str = None           # None = genre default | close | open | drop2 | rootless | power
    chord_color: str = None       # None = varies per song | triad | 7 | add9 | 9 | 6 | sus2 | sus4
    octaves: dict = None          # part (role like 'lead' or a track name) -> octaves up (+) / down (-)
    traits: dict = None           # genre-trait overrides {category: value} (see sgcore/traits.py); {'_surprise': True} = random
    part_levels: dict = field(default_factory=dict)   # layer -> dB offset (-12..+6), e.g. {'lead': -3}
    master_preset: str = None     # None = genre | streaming | radio | club | vinyl (vinyl-safe) | film (stem, no squeeze)
    ref_tone: list = None         # tonal balance of a reference song (9 bands, dB) - the master is steered toward it
    ref_tone_quiet: list = None   # (1.86) ... and of its quiet part (breakdown), for the song's quiet sections
    production_pass: object = 'auto'  # after the master: read the mix check, fix what it finds, master again: auto (full songs) | True | False
    sound_seed: int = None        # 🎲 Re-roll sounds: re-picks every sound (layers, section sounds, drum voices), same notes
    automation: dict = field(default_factory=dict)    # song editor volume lines: track id -> [[beat, dB], ...] (dB <= -60 = silent)
    note_edits: dict = None       # song editor note edits: {'del': [[track, beat, midi]], 'add': [[track, beat, dur, midi, vel]]}
    track_levels: dict = field(default_factory=dict)  # one sound (track id: 'lkick', 'pad_sw2', 'x1' ...) -> dB offset (-24..+9)
    part_fx: dict = field(default_factory=dict)       # layer -> effect plugin name (e.g. {'lead': 'ValhallaSupermassive'})
    part_effects: dict = field(default_factory=dict)  # part -> built-in effect preset (sgcore.part_effects; 'none' = dry)
    drum_voices: dict = field(default_factory=dict)   # drum voice (kick / snare / clap / hats) -> drum machine id, locked
    extra_parts: list = None      # extra instruments: [{inst, follows (lead/counter/chords/pad/arp/bass), octave, db, pan}]
    ending: str = 'auto'          # auto | hit (final chord + crash) | fade
    vocal_guide: bool = False     # also play the vocal guide melody (it is always in the MIDI export)
    skip_intro: bool = False      # start the song on its first main section (no intro)
    bends: str = None             # meend / gamak on sitar, veena, bansuri ...: 'off', 'subtle', 'more' (None = genre default)
    vocals: str = None            # sung vocals on the vocal melody: 'ooh', 'aah' or 'lyrics' (None = no singing)
    voice: str = 'female'         # the singer: 'female', 'male', 'choir' or 'robot'
    lyrics: str = ''              # words for vocals='lyrics' (simple English spelling; repeats if the song is longer)
    vox_sample: str = None        # one of your voice samples (My samples) to chop into the song (None = none)
    vox_use: str = 'auto'         # auto (genre decides) | screwed | stutter | adlib | phrase | melody
    vox_pitch: str = 'auto'       # auto | down (screwed) | natural | up (chipmunk)
    vox_amount: str = 'normal'    # few | normal | lots
    bass_rhythm: str = None       # None = style | kick (bass plays with the kick drum)
    lead_style: str = None        # None = genre | hook | arp | riff | ostinato | bell | call | chops
    build_style: str = None       # None = genre (varies per song) | roll | triplet | kick_roll | filter | stutter | pause | lift | swell | hats | claps | toms | halftime | drumless | pickup | ride | march | tomgroove | pulse | stops | tapestop | cymbal | wash | none
    builds: str = 'auto'          # build-ups into big sections: auto | subtle (natural, no EDM ramps) | off
    transition_fx: str = 'auto'   # risers, reverse cymbals, impacts, tape stops ...: auto | fewer | fills (drum fills only) | off
    groove: str = None            # None = genre feel | straight | dilla | laidback | afro | dembow | jazz | house | funk
    mood: str = None              # dark | happy | chill | epic | dreamy | aggressive | melancholic | energetic | mysterious | romantic
    counter: str = None           # None = genre decides | on | off  (a second line answering the lead: celli, horns, flute ...)
    hook_first: str = None        # None / off | on  (the verse melody is built from the chorus hook)
    layering: str = None          # None = genre + variety decide | off | more  (parts doubled by a second instrument)
    simplicity: float = 0.0       # 0..1 strip it back: triads, fewer & longer notes, held chords, no extras
    repetition: float = 0.5       # 0..1 how much the melody repeats its opening idea (catchy loop <-> developing line)
    melody_range: float = 0.5     # 0..1 narrow (a few notes) <-> wide (big leaps)
    chord_speed: str = None       # None = style | slow (chords last twice as long) | fast (change twice as often)
    synth_character: str = 'analog'   # analog (velocity shapes the tone, every note its own take, ladder filter) | classic (before 1.77)
    motif: str = 'song'           # song (verse / chorus / alt melodies grow from one motif) | free (each written on its own)
    rotation: str = 'auto'        # instrument rotation between sections: auto | off | some | lots
    avoid: dict = field(default_factory=dict)          # role -> instruments your recent songs used (picked less often)
    title: str = None             # song name (front of every exported file name); None = an invented name that fits the song
    journey: dict = None          # Cinematic Journey settings: acts, piano, rubato, dynamics, ending, woodwinds (see journey.py)
    energy_curve: list = None     # (2.0) your drawn energy across the song: 8-32 values 0..1 (None = the genre's own shape)
    ornaments: float = None       # (2.4.4) Celtic / pipe ornaments: 0 none, 0.25 light, 0.5 traditional, 0.75 heavy, 1 virtuoso

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**known)


MELODY_STYLES = ['diatonic', 'pentatonic', 'blues', 'bebop']
# how each genre's lead player phrases, and how its keyboard player voices chords (styles not listed: diatonic / style's own)
GENRE_MELODY = {'smooth_jazz_horns': 'pentatonic', 'shakuhachi_pop': 'pentatonic', 'ethio_jazz': 'pentatonic', 'thai_funk': 'pentatonic', 'desert_blues': 'pentatonic', 'chicha': 'diatonic', 'garage_rock': 'blues', 'rockabilly': 'blues', 'exotica': 'diatonic', 'riddim': 'diatonic', 'chillstep': 'diatonic', 'jazz_rap': 'blues', 'cloud_rap': 'pentatonic', 'slow_jam': 'pentatonic', 'smooth_jazz': 'pentatonic', 'smooth_funk': 'blues', 'quiet_storm': 'pentatonic', 'modern_country': 'pentatonic', 'country_waltz': 'pentatonic', 'outlaw_country': 'pentatonic', 'western_swing': 'pentatonic', 'g_funk': 'pentatonic', 'neo_soul': 'pentatonic', 'new_jack_swing': 'pentatonic', 'alt_rnb': 'pentatonic', 'rage': 'diatonic', 'plugg': 'pentatonic', 'hauntology_sunlit': 'diatonic', 'hauntology_dark': 'diatonic', 'epic_orchestral': 'diatonic', 'epic_battle': 'diatonic', 'epic_choir': 'diatonic', 'heroic_anthem': 'diatonic', 'symphonic_finale': 'diatonic', 'bebop': 'bebop', 'soul_jazz': 'blues', 'modal_jazz': 'diatonic', 'fusion': 'pentatonic', 'future_funk': 'pentatonic', 'italo_disco': 'diatonic', 'classical_period': 'diatonic', 'romantic': 'diatonic', 'impressionism': 'pentatonic', 'minimalism': 'diatonic', 'brazilian_phonk': 'blues', 'deep_dubstep': 'diatonic', 'deep_dubstep_minimal': 'diatonic', 'progressive_trance': 'diatonic', 'organic_house': 'diatonic', 'disco_funk': 'pentatonic', 'blues': 'blues', 'rock': 'blues', 'funk': 'blues', 'boombap': 'blues', 'phonk': 'blues', 'metal': 'pentatonic',
                'folk': 'pentatonic', 'afrobeats': 'pentatonic', 'amapiano': 'pentatonic', 'reggae': 'pentatonic',
                'lofi': 'pentatonic', 'pop': 'pentatonic', 'disco': 'pentatonic', 'jazz': 'bebop', 'bossa_nova': 'bebop',
                'western': 'pentatonic', 'chamber_pop': 'pentatonic', 'fantasy_rpg': 'pentatonic',
                'gospel': 'blues', 'rnb': 'pentatonic', 'motown': 'pentatonic', 'country': 'pentatonic', 'bluegrass': 'pentatonic',
                'swing': 'bebop', 'punk': 'pentatonic', 'indie_rock': 'pentatonic', 'kpop': 'pentatonic', 'soul_ballad': 'pentatonic',
                'dancehall': 'pentatonic', 'afro_house': 'pentatonic', 'jersey_club': 'pentatonic', 'baile_funk': 'pentatonic',
                'hauntology': 'pentatonic', 'braindance': 'diatonic', 'liquid_dnb': 'pentatonic', 'melodic_dubstep': 'diatonic', 'jam_band': 'pentatonic', 'soft_rock': 'pentatonic',
                'teen_pop': 'pentatonic', 'luxury_rap': 'diatonic', 'uplifting_trance': 'diatonic', 'melodic_house': 'pentatonic',
                'celtic_jig': 'diatonic', 'waltz': 'diatonic', 'tango': 'diatonic', 'salsa': 'diatonic', 'cumbia': 'diatonic'}
# house / techno keyboard voicings, one picked per song (deep house's minor 9 / 11 chords in drop-2, the quartal
# 'Detroit' stab built in fourths, open triads ...)
# per-sound timing in house (swing added on the off-beat 16ths, then milliseconds early / late): the hats and shakers
# swing harder than the kick, the shaker is pushed ahead, rims and congas sit a little back, the clap a hair late
MODULAR_GENRES = {'techno': 1.0, 'hard_techno': 0.9, 'minimal': 1.0, 'dub_techno': 0.7, 'melodic_techno': 0.6, 'uk_tribal_techno': 0.8,
                  'berlin_school': 0.6, 'acid_house': 0.5, 'tech_house': 0.5}
TECHNO_RUMBLE = {'techno': 0.8, 'hard_techno': 1.0, 'dub_techno': 0.6, 'melodic_techno': 0.45, 'uk_tribal_techno': 0.6, 'minimal': 0.3}
HOUSE_FEEL = {'chat': (0.05, 0.0), 'ohat': (0.0, 3.0), 'shaker': (0.07, -5.0), 'rim': (0.04, 7.0), 'conga': (0.05, 4.0),
              'bongo': (0.05, 3.0), 'clap': (0.0, 4.0), 'tamb': (0.06, -3.0), 'perc': (0.04, 5.0)}
HOUSE_FEEL_GENRES = {'house', 'deep_house', 'tech_house', 'melodic_house', 'organic_house', 'sunny_melodic_house',
                     'emotive_deep_house', 'garage_house', 'tokyo_deep_house', 'nineties_club_house', 'piano_house_90s',
                     'afro_house', 'uk_funky', 'outsider_house', 'french_house', 'nu_disco', 'mallet_house', 'pop_house_90s'}
HOUSE_VOICINGS = {'deep_house': ['drop2', 'drop2', 'fourths', 'open'], 'tech_house': ['fourths', 'drop2', 'close'],
                  'house': ['close', 'drop2', 'open'], 'melodic_house': ['open', 'drop2'], 'garage_house': ['drop2', 'close'],
                  'tokyo_deep_house': ['drop2', 'fourths'], 'dub_techno': ['fourths', 'fourths', 'drop2'],
                  'minimal': ['fourths', 'close'], 'techno': ['fourths', 'close', 'close'], 'nineties_club_house': ['close', 'drop2'],
                  'emotive_deep_house': ['open', 'drop2'], 'organic_house': ['open', 'drop2'], 'uk_funky': ['drop2', 'fourths'],
                  'afro_house': ['drop2', 'open'], 'outsider_house': ['fourths', 'drop2'], 'french_house': ['close', 'drop2']}
GENRE_VOICING = {'jazz_hop': 'rootless', 'storybook_score': 'open', 'bebop': 'rootless', 'soul_jazz': 'rootless', 'modal_jazz': 'open', 'fusion': 'drop2', 'impressionism': 'open', 'romantic': 'open', 'jazz': 'rootless', 'bossa_nova': 'rootless', 'lofi': 'rootless', 'boombap': 'rootless', 'city_pop': 'drop2',
                 'deep_house': 'drop2', 'ukgarage': 'drop2', 'funk': 'drop2', 'disco': 'drop2', 'downtempo': 'drop2',
                 'neoclassical': 'open', 'chamber': 'open', 'fantasy_rpg': 'open', 'cinematic': 'open', 'orchestral': 'open',
                 'swing': 'drop2', 'gospel': 'open', 'rnb': 'drop2', 'waltz': 'open', 'tango': 'close'}
GENRE_COLORS_HOUSE = {'deep_house': ['9', 'm11', '9', '7'], 'tech_house': ['m11', '7', 'triad'], 'tokyo_deep_house': ['9', 'm11', '7'],
                      'garage_house': ['9', '7'], 'house': ['7', '9', 'triad', 'triad'], 'uk_funky': ['m11', '9'],
                      'outsider_house': ['m11', '9', '7'], 'dub_techno': ['m11', '7', 'triad']}
GENRE_COLORS = {'jazz_hop': ['9', '7', '9', 'add9'], 'celtic_jig': ['triad', 'sus2', 'triad', 'sus4'], 'slip_jig': ['triad', 'sus2', 'triad'], 'celtic_hornpipe': ['triad', 'sus4', 'triad'], 'strathspey': ['triad', 'sus4'], 'celtic_polka': ['triad'], 'celtic_session': ['triad', 'sus2', 'triad', 'sus4'], 'celtic_reel': ['triad', 'sus2', 'triad', 'sus4'], 'celtic_slow_air': ['sus2', 'add9', 'triad'], 'celtic_new_age': ['add9', 'sus2', 'triad'], 'sea_shanty': ['triad'], 'dream_pop': ['7', 'add9', '7', 'sus2'], 'mallsoft': ['7', '9', '7', '6'], 'highlife': ['triad', '6', 'triad'], 'soukous': ['triad', '6'], 'wonder': ['add9', 'triad', 'sus2'], 'euphoric_trance': ['triad', 'triad', 'sus2', 'add9'], 'storybook_score': ['triad', 'add9', '7'], 'synth_rnb': ['triad', 'add9', '7'], 'cinematic_trap': ['triad'], 'ethereal_wave': ['7', 'add9', '7', 'triad'], 'sunlit_electronica': ['7', 'add9', '7', 'sus2'], 'daydream_downtempo': ['7', 'add9', '7', 'sus2'], 'dream_synthscape': ['9', '7', '9', 'add9'], 'festive_cinematic': ['7', 'add9', '7', 'triad'], 'jazz_rap': ['9', '7', '9', '6'], 'cloud_rap': ['add9', 'sus2', 'triad'], 'slow_jam': ['9', '7', 'add9'], 'smooth_jazz': ['add9', '9', '7', 'sus2'], 'smooth_funk': ['9', '7'], 'quiet_storm': ['9', '7', 'add9'], 'modern_country': ['triad', 'add9', 'sus2'], 'country_waltz': ['triad'], 'outlaw_country': ['triad', '7'], 'western_swing': ['6', '7', '9', '6'], 'g_funk': ['7', '9', 'triad'], 'neo_soul': ['9', '7', '9', 'add9'], 'new_jack_swing': ['7', '9', 'triad'], 'alt_rnb': ['7', 'add9', '9'], 'rage': ['triad'], 'plugg': ['add9', 'triad', '7'], 'hauntology_sunlit': ['add9', 'triad', 'sus2', '7'], 'hauntology_dark': ['triad', 'sus2', 'add9'], 'epic_orchestral': ['triad', 'sus4'], 'epic_battle': ['triad'], 'epic_choir': ['triad'], 'heroic_anthem': ['triad', 'sus4', 'add9'], 'symphonic_finale': ['triad', '7'], 'bebop': ['9', '7', '6'], 'modal_jazz': ['9', 'sus4', '7'], 'soul_jazz': ['7', '9'], 'fusion': ['9', 'add9', '7'], 'future_funk': ['7', '9'], 'italo_disco': ['triad', 'add9'], 'new_beat': ['triad'], 'gabber': ['triad'], 'rave_hardcore': ['triad', '7'], 'classical_period': ['triad'], 'romantic': ['7', 'triad', 'add9'], 'impressionism': ['add9', '9', 'sus2'], 'minimalism': ['triad', 'add9'], 'deep_dubstep': ['triad'], 'deep_dubstep_minimal': ['triad'], 'progressive_trance': ['triad', 'sus2', 'add9'], 'organic_house': ['add9', 'triad', 'sus2'], 'disco_funk': ['7', '9', 'triad'], 'jazz': ['7', '9', '9', '6'], 'bossa_nova': ['7', '9', '6'], 'lofi': ['7', '9', 'add9'], 'boombap': ['7', '9'],
                'city_pop': ['7', '9', 'add9'], 'deep_house': ['7', '9', 'add9'], 'ukgarage': ['7', '9'], 'funk': ['7', '9'],
                'blues': ['7'], 'downtempo': ['7', 'add9', '9'], 'neoclassical': ['triad', 'add9', 'add9', 'sus2'],
                'baroque': ['triad'], 'chamber': ['triad', 'triad', '7'], 'holiday': ['triad', '6', '7', 'add9'],
                'western': ['triad', 'triad', 'sus4'], 'hybrid_trailer': ['triad', 'triad', 'add9no3'],
                'symphonic_metal': ['triad'], 'fantasy_rpg': ['triad', 'add9', 'sus2'],
                'gospel': ['7', '9', '6', '7'], 'rnb': ['7', '9', '9', 'add9'], 'swing': ['6', '7', '9'], 'motown': ['triad', '7'],
                'country': ['triad'], 'bluegrass': ['triad'], 'tango': ['triad', '7'], 'salsa': ['triad', '7', '6'],
                'kpop': ['triad', 'add9', '7'], 'afro_house': ['7', '9', 'triad'], 'melodic_techno': ['triad', 'sus2', 'add9no3'],
                'soul_ballad': ['triad', '7', '6'], 'waltz': ['triad'], 'ska': ['triad', '7'],
                'cumbia': ['triad'], 'dancehall': ['triad', '7'], 'hauntology': ['add9', '7', 'triad', 'sus2'],
                'braindance': ['add9', 'sus2', '7', 'add9no3'], 'liquid_dnb': ['7', '9', 'add9'], 'neurofunk': ['triad', 'add9no3'],
                'melodic_dubstep': ['triad', 'add9', 'sus2'], 'brostep': ['triad'], 'memphis_phonk': ['triad'], 'switchup_808': ['add9', 'add9', 'triad'], 'switchup_808_dj': ['add9', 'add9', 'triad'], 'switchup_808_hard': ['triad', 'add9'], 'idm_jungle_theme': ['add9', '7', 'triad'], 'math_rock': ['add9', '7', 'add9', 'sus2'], 'sunrise_chillwave': ['add9', 'sus2', '7', 'add9'], 'hazy_downtempo': ['add9', '7', 'sus2'], 'analog_arp_drive': ['add9', 'sus2', 'triad'], 'velvet_pop': ['7', 'add9', '9'], 'drill_space': ['9', '7', 'add9'], 'switchup_mallets': ['add9', 'triad'], 'phonk': ['triad'], 'house_phonk': ['triad'], 'brazilian_phonk': ['triad'], 'jam_band': ['triad', '7', 'sus4'],
                'soft_rock': ['triad', 'add9', '7', 'sus2'], 'teen_pop': ['triad', 'add9', '7'], 'luxury_rap': ['7', 'add9', '9', 'triad'],
                'uplifting_trance': ['triad', 'add9', 'sus2'], 'melodic_house': ['add9', '7', 'triad', 'sus2'], 'punk': ['triad'], 'indie_rock': ['triad', 'add9', 'sus2']}


FUSION_PARTS = {
    'groove': ['bpm', 'swing', 'swing_unit', 'human', 'drums', 'snare_tracks', 'kit', 'kit_override', 'kick_track',
               'trap_hats', 'ghosts', 'fill', 'sc_depth', 'sc_release'],
    'bass': ['bass', 'bass_mode', 'bass_lo', 'bass_gate'],
    'harmony': ['scales', 'progs', 'chord_size', 'chord_bars', 'chord_rh', 'chord_center', 'strum', 'voicing'],
    'melody': ['lead_rh', 'lead_oct', 'arp'],
    'form': ['form', 'form_scale'],
    'mix': ['reverb', 'delay_beats', 'master'],
}
PART_LAYERS = {'groove': ('kick', 'snare', 'top'), 'bass': ('bass',), 'harmony': ('chords', 'pad'),
               'melody': ('lead', 'arp'), 'mix': ('fx',), 'form': ()}
PART_LABELS = {'groove': 'Drums & groove', 'bass': 'Bassline', 'harmony': 'Chords & pads', 'melody': 'Lead & arps',
               'form': 'Arrangement', 'mix': 'Mix & space'}

MOODS = {
    'dark': dict(scales=['minor', 'phrygian', 'harmonic_minor'], brightness=-0.4, reverb=0.3, energy=0.05),
    'happy': dict(scales=['major', 'lydian', 'mixolydian'], brightness=0.3, energy=0.15),
    'chill': dict(tempo=0.88, energy=-0.25, swing=0.04, reverb=0.3, brightness=-0.2, sidechain=-0.3),
    'epic': dict(scales=['minor', 'harmonic_minor'], reverb=0.5, energy=0.25, inst={'pad': 'choir'}),
    'dreamy': dict(scales=['major', 'lydian'], reverb=0.8, delay=0.5, brightness=-0.1, inst={'pad': 'warmpad', 'arp': 'bell'}),
    'aggressive': dict(scales=['phrygian', 'minor'], energy=0.35, drive=0.4, brightness=0.2, tempo=1.04, sidechain=0.15),
    'melancholic': dict(scales=['minor', 'dorian'], energy=-0.15, brightness=-0.25, inst={'lead': 'piano'}),
    'energetic': dict(energy=0.3, tempo=1.06, complexity=0.1),
    'mysterious': dict(scales=['phrygian', 'harmonic_minor', 'dorian'], reverb=0.4, brightness=-0.3, complexity=0.1),
    'romantic': dict(scales=['major'], energy=-0.1, inst={'pad': 'strings', 'lead': 'violin'}),
}

GENERIC_PROGS = {
    'major': [[0, 4, 5, 3], [0, 5, 3, 4], [3, 4, 0, 0], [5, 3, 0, 4], [0, 3, 4, 3], [0, 2, 3, 4], [0, 5, 1, 4],
              [3, 0, 4, 5], [0, 4, 3, 4], [0, 3, 5, 4], [1, 4, 0, 0], [0, 2, 5, 3], [5, 4, 3, 4], [0, 4, 5, 2, 3, 0, 3, 4],
              [0, 5, 3, 4, 0, 5, 1, 4], [3, 4], [0, 3], [5, 3, 0], [0, 4, 1, 3], [3, 2, 1, 0], [0, 0, 3, 3, 5, 5, 4, 4],
              [0, 1, 3, 4], [5, 1, 4, 0]],
    'minor': [[0, 5, 2, 6], [0, 3, 4, 0], [0, 6, 5, 6], [0, 5, 3, 4], [0, 3, 6, 2], [0, 6, 5, 4], [5, 6, 0, 0],
              [0, 2, 6, 5], [0, 3, 0, 4], [5, 2, 6, 0], [0, 4, 5, 6], [3, 4, 0, 0], [0, 5], [0, 6], [0, 3, 6],
              [0, 5, 2, 6, 3, 0, 4, 4], [0, 0, 5, 5, 3, 3, 4, 6], [5, 3, 0, 6], [0, 6, 3, 5], [3, 6, 2, 5],
              [0, 2, 3, 4], [0, 3, 5, 6]],
    'dorian': [[0, 3, 0, 3], [0, 3, 6, 4], [0, 6, 3, 0], [0, 2, 3, 0], [0, 3, 6, 2], [0, 4, 3, 0], [0, 1, 3, 0], [3, 4, 0, 0],
               [0, 6, 2, 3], [0, 3]],
    'phrygian': [[0, 1, 0, 1], [0, 1, 6, 0], [0, 0, 1, 0], [0, 5, 1, 0], [0, 6, 5, 1], [0, 3, 1, 0], [0, 1, 5, 6], [0, 1]],
    'harmonic_minor': [[0, 5, 3, 4], [0, 3, 4, 0], [0, 5, 4, 0], [0, 3, 5, 4], [5, 3, 4, 0], [0, 4]],
    'mixolydian': [[0, 6, 3, 0], [0, 0, 3, 0], [0, 6, 0, 3], [0, 4, 6, 3], [0, 6, 5, 6], [0, 3, 6, 0], [0, 6]],
    'lydian': [[0, 1, 0, 1], [0, 1, 4, 0], [0, 1, 5, 4], [0, 4, 1, 0], [0, 1, 2, 1], [0, 1]],
    'phrygian_dominant': [[0, 1, 0, 1], [0, 3, 1, 0], [0, 6, 1, 0], [0, 1, 6, 0], [0, 0, 3, 1], [0, 1]],
    'melodic_minor': [[0, 3, 4, 0], [0, 1, 4, 0], [0, 3, 0, 4], [1, 4, 0, 0], [0, 4]],
}

PHRASE_PLANS = [[0, 1, 0, 1, 0, 1, 2, 3], [0, 1, 0, 2, 0, 1, 0, 3], [0, 0, 1, 1, 0, 0, 2, 3], [0, 1, 2, 3, 0, 1, 2, 3],
                [0, 1, 0, 1, 2, 3, 2, 3], [0, 1, 2, 1, 0, 1, 2, 3]]



def is_808(inst):
    """An 808 of any flavour (808, its distorted / long / punchy variants, drill 808, wobble 808)."""
    inst = str(inst or '')
    return inst.startswith('808') or inst in ('drill808', 'wob808')

def apply_mood(opts):
    """Return a copy of the options with the mood's adjustments folded in."""
    if not opts.mood or opts.mood not in MOODS:
        return opts, None
    m = MOODS[opts.mood]
    o = Options.from_dict(opts.to_dict())
    o.energy = min(1.0, max(0.0, o.energy + m.get('energy', 0)))
    o.complexity = min(1.0, max(0.0, o.complexity + m.get('complexity', 0)))
    o.brightness = min(1.0, max(-1.0, o.brightness + m.get('brightness', 0)))
    o.reverb = o.reverb + m.get('reverb', 0)
    o.delay = o.delay + m.get('delay', 0)
    o.drive = min(1.0, o.drive + m.get('drive', 0))
    o.instruments = {**m.get('inst', {}), **(o.instruments or {})}
    return o, m


def fuse_styles(opts, rnd):
    """Build one style recipe out of several: each musical part comes from one of the chosen styles."""
    names = [opts.style] + [b for b in (opts.blend or []) if b in STYLES and b != opts.style]
    base = STYLES[opts.style]
    if len(names) == 1 and not opts.blend_parts:
        return dict(base), {p: opts.style for p in FUSION_PARTS}
    parts = list(FUSION_PARTS)
    assign = {p: s for p, s in (opts.blend_parts or {}).items() if s in STYLES and p in FUSION_PARTS}
    free = [p for p in parts if p not in assign]
    rnd.shuffle(free)
    # make sure every chosen style contributes at least one part
    pool = [n for n in names if n not in assign.values()]
    for p in free:
        assign[p] = pool.pop(0) if pool else rnd.choice(names)
    # an auto-picked groove should come from a style that actually has drums
    if 'groove' in free and not STYLES[assign['groove']]['drums']:
        drummy = [n for n in names if STYLES[n]['drums']]
        if drummy:
            d = rnd.choice(drummy)
            other = next((p for p in free if assign[p] == d), None)
            if other:
                assign[other] = assign['groove']
            assign['groove'] = d
    st = dict(base)
    for part, src in assign.items():
        for k in FUSION_PARTS[part]:
            if k in STYLES[src]:
                st[k] = STYLES[src][k]
    # tracks: take each layer's tracks from the style that owns that part
    owner = {}
    for part, layers in PART_LAYERS.items():
        for l in layers:
            owner[l] = assign.get(part, opts.style)
    tracks = []
    for layer in ['kick', 'snare', 'top', 'bass', 'chords', 'pad', 'arp', 'lead', 'fx']:
        src = owner.get(layer, opts.style)
        cand = [t for t in STYLES[src]['tracks'] if t['layer'] == layer]
        if not cand:
            for n in names:
                cand = [t for t in STYLES[n]['tracks'] if t['layer'] == layer]
                if cand:
                    break
        tracks += cand
    # the drum patterns must refer to drum tracks that exist
    names_in = {t['name'] for t in tracks}
    st['drums'] = {k: v for k, v in st['drums'].items() if k in names_in}
    st['snare_tracks'] = [s for s in st['snare_tracks'] if s in names_in]
    if st.get('kick_track', 'kick') not in names_in:
        st['kick_track'] = next((t['name'] for t in tracks if t['layer'] == 'kick'), 'kick')
    st['tracks'] = tracks
    st['category'] = base['category']
    return st, assign


# ----------------------------------------------------------------------------- variety banks (per groove family)
FOURX = 'X...X...X...X...'
EXTRA_DRUMS = {
    'four': {'chat': ['x.x.x.x.x.x.x.x.', '.x.x.x.x.x.x.x.x', 'xxx.xxx.xxx.xxx.', 'x.xxx.xxx.xxx.xx', 'oxoxoxoxoxoxoxox'],
             'ohat': ['..x...x...x...x.', '..x...x...x.x.x.', '..X...X...X...x.'],
             'clap': ['....X.......X...', '....X.......X..x', '....X..x....X...'],
             'shaker': ['xoxoxoxoxoxoxoxo', 'o.o.o.o.o.o.o.o.', '.o.o.o.o.o.o.o.o'],
             'rim': ['...x..x....x..x.', '..x.....x.x.....'], 'snare': ['....X.......X...', '....X.......X..x']},
    'half': {'kick': ['X.....X...X.....', 'X......X..X..X..', 'X..X......X.....', 'X.....X.X.....X.', 'X.......X.X.....'],
             'snare': ['........X.......', '........X......x'], 'clap': ['........X.......'], 'ohat': ['..............x.', '......x.......x.']},
    'break': {'kick': ['X.........X.....', 'X.X.......X.....', 'X.........XX....', 'X.....X...X.....'],
              'snare': ['....X.......X...', '....X..x....X...', '....X.......X.x.'], 'chat': ['x.x.x.x.x.x.x.x.', 'x.xxx.x.x.xxx.x.']},
    'other': {'kick': ['X.......X.......', 'X.....x.X.......', 'X.......X.x.....', 'X..x....X.......'],
              'chat': ['x.x.x.x.x.x.x.x.', 'xxxxxxxxxxxxxxxx', 'x.xxx.xxx.xxx.xx'], 'snare': ['....X.......X...', '....X.......X..x']},
}
EXTRA_BASS = {
    'four': ['..R...R...R...R.', '.RR..RR..RR..RR.', 'R..R..R..R..R.R.', '..R.R...R.R...R.', '..RO..R...RO..R.', 'R.....R.R.....R.'],
    'break': ['R-------R-------', 'R-----R---R-----', 'R---R-------R---'],
    'other': ['R.......R...R...', 'R...R...R...R...', 'R-..R-..R...A...', 'R.....R...F.....'],
}
EXTRA_CHORD_RH = {
    'four': ['..x...x.x...x..x', '...x..x....x..x.', 'x..x..x...x..x..', 'x---------------', '.x.x..x..x.x..x.', 'x.......x.......'],
    'half': ['x---------------', 'x-------x-------', 'x.xx.x.xx.x.xx.x', 'x--x--x-x--x--x-'],
    'break': ['x---------------', 'x-------x-------', '......x.........'],
    'other': ['x---------------', 'x-------x-------', 'x---x---x---x---', 'x-.x-.x-x-.x-.x-'],
}


# genres whose drum pattern IS the genre (a one-drop, dembow, clave, tumbao, footwork's triplet kicks ...): the variety
# pass never mixes the generic extra drum patterns into them - a reggae song with a kick on 1 and 3 isn't reggae
OWN_GROOVE = {'reggae', 'dub', 'ska', 'reggaeton', 'dancehall', 'moombahton', 'soca', 'groovy_soca', 'salsa', 'cumbia',
              'bossa_nova', 'samba', 'bachata', 'merengue', 'baile_funk', 'funk_150', 'brazilian_phonk', 'afrobeat', 'afrobeats',
              'amapiano', 'gqom', 'uk_funky', 'bhangra', 'raga_fusion', 'bhajan', 'kirtan', 'aarti', 'santoor_raga', 'sitar_bhajan', 'tabla_bhajan', 'drum_kirtan', 'jugalbandi', 'qawwali', 'carnatic_kriti', 'ghazal', 'bollywood', 'klezmer', 'gamelan', 'rai', 'takht_maqam', 'raqs_sharqi', 'arab_pop', 'sufi_dhikr', 'son_cubano', 'flamenco_rumba', 'chicha', 'krautrock', 'rockabilly', 'footwork', 'footwork_soulful', 'footwork_dark', 'juke', 'juke_raw', 'juke_house',
              'baltimore_club', 'jersey_club', 'uk_drill', 'ukgarage', 'speed_garage', 'freestyle', 'electro', 'nola_brass',
              'tango', 'celtic_jig', 'swing_tomtom', 'western_swing', 'country', 'outlaw_country', 'surf_rock'}


def groove_family(st):
    def first_hit(p):                                  # (1.95) soft hits ('x') count too: a clap written 'x' on the 3rd beat
        return next((i for i, c in enumerate(p) if c in 'Xx'), -1)   # used to make a half-time genre look 'other'
    snares = sum((st['drums'].get(n, []) for n in st.get('snare_tracks', [])), [])
    if snares and all(first_hit(p) == 8 or p.strip('.') == '' for p in snares):
        return 'half'                                  # (1.95) checked first: a steppers kick (one on every beat) under a
    kicks = st['drums'].get(st.get('kick_track', 'kick'), [])   # snare on the 3 is still half-time dubstep, not house
    if any(k == FOURX for k in kicks):
        return 'four'
    if max(st['bpm']) >= 160:
        return 'break'
    return 'other'


# synth tone controls (their built-in defaults) that get a per-song twist, so one instrument isn't one preset
TONE_DEFAULTS = {'sawbass': dict(cut=2200), 'supersaw': dict(cut=3000, detune=1.0), 'stab': dict(cut=5000),
                 'pluck_saw': dict(cut=6000), 'leadsaw': dict(cut=5000), 'warmpad': dict(cut=1100), 'strings': dict(cut=3200),
                 'pluck': dict(bright=5000), 'supersaw_lead': dict(cut=7000, detune=1.3), 'hoover': dict(cut=4500),
                 'reese': dict(cut=900), 'softlead': dict(cut=3000), 'violin': dict(cut=4500), 'cello': dict(cut=2600),
                 'spiccato': dict(cut=4200), 'tremolo': dict(cut=3600), 'brass': dict(cut=3800), 'horn': dict(cut=1600)}


PART_K = {'harmony': 1, 'melody': 2, 'drums': 3, 'bass': 4, 'chords': 5}


def _layout_seed(opts):
    """(2.6) The per-song arrangement variant follows a locked part: a part locked from another song keeps that song's
    section layout, so the locked drums / bass / chords land where they did (before, a re-roll re-arranged the song
    around them and moved them). Part seeds are seed * 1009 + PART_K, so the source song's seed comes back exactly."""
    ps = getattr(opts, 'part_seeds', None) or {}
    for part in sorted(ps, key=lambda k: PART_K.get(k, 99)):
        v, k = ps.get(part), PART_K.get(part)
        if v is not None and k is not None and (int(v) - k) % 1009 == 0:
            return (int(v) - k) // 1009
    return opts.seed


def _snd(opts):
    """The sound re-roll (🎲 Re-roll sounds): a new sound_seed re-picks the sounds - main parts, layers, the sounds that
    take over in other sections, the drum-machine voices - while every note stays the same."""
    sd = getattr(opts, 'sound_seed', None)
    return f'-snd{int(sd)}' if sd else ''


def apply_variety(st, opts, rnd):
    """Give every song its own palette: instrument swaps, tone tweaks, extra groove patterns, kit and arrangement."""
    v = max(0.0, min(1.0, float(opts.variety)))
    if v <= 0:
        return st
    fam = groove_family(st) if not st.get('meter') else 'meter'
    ps = opts.part_seeds or {}

    def r_for(part):                                  # each part's palette comes from its own seed, so a locked part
        sd = ps.get(part) if ps.get(part) is not None else opts.seed * 1009 + PART_K[part]   # sounds the same in any song
        return random.Random(f'{sd}-variety')
    drums = {k: list(p) for k, p in st['drums'].items()}
    rd = r_for('drums')
    own = (st.get('name') or opts.style) in OWN_GROOVE
    for name in drums:
        bank = [] if own else EXTRA_DRUMS.get(fam, {}).get(name, [])
        if bank and rd.random() < 0.3 + 0.6 * v:
            drums[name] += rd.sample(bank, min(len(bank), 1 + int(2 * v)))
    st['drums'] = drums
    rb = r_for('bass')
    if st.get('bass_mode') == 'pattern' and not st.get('riff_locked') and rb.random() < 0.3 + 0.6 * v:
        bank = EXTRA_BASS.get(fam, [] if fam == 'meter' else EXTRA_BASS['other'])
        st['bass'] = list(st['bass']) + rb.sample(bank, min(len(bank), 1 + int(2 * v)))
    rc = r_for('chords')
    if st.get('voicing') != 'power' and rc.random() < 0.3 + 0.6 * v:
        bank = EXTRA_CHORD_RH.get(fam, [] if fam == 'meter' else EXTRA_CHORD_RH['other'])
        st['chord_rh'] = list(st['chord_rh']) + rc.sample(bank, min(len(bank), 1 + int(2 * v)))
    from .styles import POOLS
    pal = PALETTES.get(st.get('category'), {})
    fusion = st.get('fusion') or {}
    part_rng = {}
    chip_locked = st.get('name') == 'chiptune' and v < 0.85
    tracks = []
    for t in st['tracks']:
        t = dict(t, p=dict(t['p']))
        role = t['layer']
        part = {'bass': 'bass', 'lead': 'melody', 'arp': 'melody'}.get(role, 'chords')
        owner = fusion.get({'bass': 'bass', 'chords': 'harmony', 'pad': 'harmony'}.get(role, 'melody'), opts.style)
        pool = POOLS.get(owner, {}).get(role)
        if role not in part_rng:                      # seeded per part + genre, so genres don't all pick alike
            sd = ps.get(part) if ps.get(part) is not None else opts.seed * 1009 + PART_K[part]
            part_rng[role] = random.Random(f'{sd}-{role}-{owner}-variety' + _snd(opts))
        rr = part_rng[role]
        free = role not in (opts.instruments or {}) and not t.get('user_pick') and not chip_locked and not t.get('double_of') \
            and (t['name'] == role or st.get('composer') or t.get('switch_of'))     # a genre's named extra parts keep their sound
        keep_sig = owner in SIGNATURE_STRICT and role in SIGNATURE_ROLES.get(owner, ('bass', 'lead'))
        # (rap / R&B / trance ...: the genre's defining part - its bass, its lead - usually keeps its own sound, but the
        # supporting parts (arps, pads, chords) vary freely, so the arp before every drop isn't the same pluck)
        club = st.get('category') == 'Electronic' and not chip_locked
        # (electronic genres' pools hold only genre-proper synths, so their songs rotate through all of them - the
        # defining bass / lead still keeps its sound more often than the supporting parts)
        p_pool = ((0.5 + 0.35 * v) if club else (0.2 + 0.3 * v)) if keep_sig else ((0.75 + 0.25 * v) if club else (0.55 + 0.4 * v))
        if keep_sig and pool:                         # the defining part rotates only among sounds its own check accepts
            from .fitness import SIGNATURE as _SIG
            sg = _SIG.get(owner)
            if sg and sg[0] == role:
                pool = [x for x in pool if x in sg[1]] or pool
        if free and pool and rr.random() < p_pool:
            # the genre's own pool: its signature sound a little likelier, every other one an authentic alternative;
            # instruments your last songs in this genre used are picked less often, so the next one sounds fresh
            recent = set((getattr(opts, 'avoid', None) or {}).get(role, []))
            favs = set(getattr(opts, 'favorites', None) or ())
            w = [(1.4 if i == 0 and not club else 1.0) * (0.25 if x in recent else 1.0) * (2.5 if x in favs else 1.0)
                 for i, x in enumerate(pool)]
            choice = rr.choices(pool, w)[0]
            choice = _GTR_UP.get(opts.style, {}).get(choice, choice)     # (2.0) the rig guitars play the old guitar picks
            if choice != t['inst']:                   # (the genre's level for this part stays: every part is levelled to it)
                t.update(inst=choice, p={}, pooled=True)
        elif free and not pool and role in pal and rr.random() < 0.12 + 0.5 * v:
            choice = rr.choice(pal[role])
            if choice != t['inst']:
                t.update(inst=choice, p={}, db=None, pooled=True)
        for k, dv in TONE_DEFAULTS.get(t['inst'], {}).items():   # each song gets its own take on the patch
            t['p'].setdefault(k, dv)
        for k in ('cut', 'bright'):
            if k in t['p']:
                t['p'][k] *= 2 ** (rr.uniform(-0.6, 0.6) * v)
        if 'detune' in t['p']:
            t['p']['detune'] *= rr.uniform(1 - 0.35 * v, 1 + 0.35 * v)
        if 'res' in t['p']:
            t['p']['res'] *= rr.uniform(1 - 0.2 * v, 1 + 0.15 * v)
        if t['rev']:
            t['rev'] *= rnd.uniform(1 - 0.4 * v, 1 + 0.4 * v)
        dry_cowbell = role == 'lead' and t['inst'].startswith('cowbell')     # the phonk cowbell stays dry: no added echo
        if not dry_cowbell and (t['dly'] or (role in ('lead', 'arp') and rnd.random() < 0.3 * v)):
            t['dly'] = max(t['dly'], 0.2) * rnd.uniform(0.7, 1.3)
        tracks.append(t)
    st['tracks'] = tracks
    if not opts.kit and not st.get('kit_id') and st.get('category') != 'Orchestral' and not st.get('kit_override') \
            and not st.get('kick_shape') and rd.random() < 0.35 * v:      # genres with a designed kit keep it
        kit = dict(KITS[rd.choice(['808', '909', 'punchy', 'soft', 'default'])])
        st['kitparams'] = kit
    elif st.get('kitparams', {}).get('kick'):
        k = dict(st['kitparams']['kick'])
        k['pitch'] = k.get('pitch', 48) * 2 ** (rd.uniform(-2, 2) * v / 12)
        k['decay'] = k.get('decay', 7) * rd.uniform(1 - 0.25 * v, 1 + 0.25 * v)
        st['kitparams'] = dict(st['kitparams'], kick=k)
    if isinstance(st['form'], str) and st['form'] in FORM_VARIANTS and opts.structure == 'auto' and rnd.random() < 0.55 * v:
        st['form'] = rnd.choice(FORM_VARIANTS[st['form']])
    if not (st.get('arp') or {}).get('beat_lock'):       # beat-locked arps keep their echoes on the beat
        st['delay_beats'] = rnd.choice([0.75, 0.75, 0.5, 1.5]) if rnd.random() < 0.4 * v else st['delay_beats']
    return st


DRUM_STATE_KEYS = ('snare_tracks', 'kick_track', 'trap_hats', 'ghosts', 'fill')


def borrow_drums(st, opts):
    """Drum style 'style:<genre>': play that genre's drum patterns (and the drum parts they need) while every sound
    choice - the kit, percussion samples, tempo and swing - stays this song's. Only the patterns move."""
    dp = getattr(opts, 'drum_pattern', None) or ''
    if not dp.startswith('style:'):
        return
    src = STYLES.get(dp[6:])
    if not src or not src.get('drums') or (src.get('meter') or '4/4') != (st.get('meter') or '4/4'):
        return                                           # a 3/4 beat can't drive a 4/4 song (or the reverse)
    keep = [t for t in st['tracks'] if t['layer'] not in ('kick', 'snare', 'top') or t.get('user_pick')
            and t['name'] in src['drums']]
    have = {t['name'] for t in keep}
    for t in src['tracks']:
        if t['layer'] in ('kick', 'snare', 'top') and t['name'] in src['drums'] and t['name'] not in have:
            keep.append(dict(t, p=dict(t.get('p') or {})))
            have.add(t['name'])
    st['tracks'] = keep
    st['drums'] = {k: list(v) for k, v in src['drums'].items() if k in have}
    for k in DRUM_STATE_KEYS:
        if k in src:
            st[k] = src[k]
    st['snare_tracks'] = [x for x in st.get('snare_tracks') or [] if x in have] or \
        [t['name'] for t in keep if t['layer'] == 'snare'][:1]
    if st.get('kick_track', 'kick') not in have:
        st['kick_track'] = next((t['name'] for t in keep if t['layer'] == 'kick'), 'kick')
    st['borrowed_drums'] = dp[6:]


def apply_sampled(st, opts):
    """Swap synthesised stand-ins for real recorded instruments (if the sound library is installed)."""
    from . import soundfont as sfm
    from .styles import ACOUSTIC_MAP, ACOUSTIC_KIT, POWER_CHORDS, GENTLE_MASTER
    name, cat = opts.style, st.get('category')
    if name in POWER_CHORDS:
        st['voicing'] = 'power'
    if cat == 'Orchestral' or name in GENTLE_MASTER:
        st['master'] = {**st['master'], 'gentle': True}
    engine = getattr(opts, 'engine', 'auto') or 'auto'
    on = engine != 'synth' and sfm.installed()
    if getattr(opts, 'vst_rig', False) and engine != 'synth':
        from . import vsthost, vstrigs
        if vsthost.available():
            try:
                vstrigs.assign(st, opts)
            except Exception as e:                             # a broken plugin folder must never stop a song
                st['rig_error'] = str(e)
    for t in st['tracks']:
        inst = t['inst']
        if inst.startswith('sf:'):
            if not on:                                         # library missing / synth engine: use a stand-in
                t['inst'] = sfm.fallback_for(inst[3:])
            elif not t.get('fallback'):
                t['fallback'] = sfm.fallback_for(inst[3:])
            continue
        if not on or inst.startswith(('user:', 'vst:')) or t['layer'] not in MELODIC_ROLES:
            continue
        if inst in _GTR20:                                     # (2.0) the played, double-tracked rig guitars beat GM samples
            continue
        user_pick = bool(t.get('fallback'))
        mapped = None if (user_pick or t.get('pooled') or t.get('keep_inst')) else ACOUSTIC_MAP.get(name, {}).get(t['layer'])
        if mapped:
            target = mapped
        elif (inst in sfm.ACOUSTIC or inst in sfm.SF_ALIAS) and (cat in ('Orchestral', 'Classic') or engine == 'sampled'
                                                                  or inst in sfm.ELECTRONIC_SWAP):
            target = sfm.SF_ALIAS.get(inst, inst)
            if target != inst:
                t['orch_name'] = inst                          # the real orchestra still plays the exact section
        else:
            continue
        t['fallback'] = t.get('fallback') or inst
        t['inst'] = 'sf:' + target
    if on and not getattr(opts, 'user_drums', False):
        kit = ACOUSTIC_KIT.get(name) or ('orchestra' if cat == 'Orchestral' else None)
        if opts.kit == 'acoustic':
            kit = kit or 'acoustic'
        elif opts.kit:
            kit = None
        if kit:
            st['sampled_kit'] = kit
    if engine != 'synth':
        apply_real(st, opts)


def apply_real(st, opts):
    """Real multi-sampled libraries (orchestra, percussion, acoustic kits - see samplelibs) beat the General MIDI bank."""
    from . import samplelibs as sl
    from .styles import ACOUSTIC_KIT
    try:
        any_lib = any(sl.installed(x) for x in sl.LIB_ORDER)
    except Exception:
        any_lib = False
    if not any_lib:
        return
    for t in st['tracks']:
        inst = t['inst']
        if t['layer'] not in MELODIC_ROLES or inst.startswith(('user:', 'vst:', 'real:')):
            continue
        base = t.get('orch_name') or (inst[3:] if inst.startswith('sf:') else inst)
        orig_base = base
        style_ = st.get('name') or opts.style
        if base == 'piano' and style_ in sl.UPRIGHT_STYLES and sl.plays('upright_piano'):
            base = 'upright_piano'                         # lo-fi / vintage styles: a worn upright, not a concert grand
        elif base == 'organ' and (style_ in sl.PIPE_ORGAN_STYLES or st.get('category') == 'Orchestral') and sl.plays('pipeorgan'):
            base = 'pipeorgan'                             # church / film organ, not a Hammond
        elif base in ('tenorsax', 'altosax'):
            base = 'sax'
        if base in sl.ORCH and sl.plays(base):
            from . import soundfont as sfm
            t['fallback'] = t.get('fallback') or (orig_base if orig_base in INSTRUMENTS else sfm.fallback_for(orig_base))
            t['real_from'] = inst
            if base in ('guitar', 'mutedgtr') and (t.get('p') or {}).get('dist'):
                t['amp'] = float(t['p']['dist'])           # the synth's distortion becomes an amp on the real guitar
            t['inst'] = 'real:' + base
    if getattr(opts, 'user_drums', False):
        return
    name = opts.style
    if any(sl.installed(x) for x in sl.KIT_LIBS):
        if st.get('kit_id'):                               # a chosen / genre kit says which mic, if any
            mic = st.get('want_real_kit')
            if mic and not sl.has(mic + ':kick'):
                mic = 'studio' if sl.has('studio:kick') else None
            if mic:
                st['real_kit'] = mic
        elif opts.kit in (None, '', 'acoustic'):
            acoustic = st.get('sampled_kit') not in (None, 'orchestra') or ACOUSTIC_KIT.get(name) or st.get('kit') == 'acoustic' \
                or opts.kit == 'acoustic'
            if name in sl.LOFI_KIT_STYLES:
                st['real_kit'] = 'lofi'
            elif acoustic:
                st['real_kit'] = 'studio'
    if sl.installed('percussion'):
        st['real_perc'] = True
    if 'orch_note' in st:                                  # re-check now that parts may play the real orchestra
        from . import vstrigs
        try:
            st['orch_note'] = vstrigs.orchestra_note(st, vstrigs.plugins_on_disk(), st.get('category'), {})
        except Exception:
            pass


def _installed_vst(choice, opts):
    """'vstp:<patch>' (a genre patch of an installed plugin) or 'vstd:<plugin name>' (its default sound) -> 'vst:<id>'."""
    try:
        from . import vsthost, vstrigs
        if not vsthost.available():
            return None
        kind, ident = choice.split(':', 1)
        if kind == 'vstp' and ident in vstrigs.PATCHES:
            path = vstrigs.player_path(vstrigs.PATCHES[ident]['player'])
            return 'vst:' + vstrigs.ensure_sound(ident, path, vstrigs.STYLE_TONE.get(opts.style, 0.0)) if path else None
        if kind == 'vstd':
            return 'vst:' + vstrigs.ensure_plain_sound(ident) if vstrigs.plugin_by_name(ident) else None
        if kind == 'vstq':
            sid = vsthost.ensure_preset_sound(ident)
            return 'vst:' + sid if sid else None
    except Exception:
        return None
    return None


def resolve_style(opts, rnd=None, mood=None):
    """Fuse styles if requested, then apply instrument / kit / mute / mix / mood overrides."""
    rnd = rnd or random.Random(opts.seed)
    st, assign = fuse_styles(opts, rnd)
    st['fusion'] = assign
    st['mood'] = mood
    if mood:
        if mood.get('swing'):
            st['swing'] = min(0.72, st['swing'] + mood['swing'])
        if mood.get('sidechain') and st['sc_depth'] > 0:
            st['sc_depth'] = min(1.0, max(0.0, st['sc_depth'] + mood['sidechain']))
    tracks = []
    for t in st['tracks']:
        t = dict(t)
        t['p'] = dict(t['p'])
        if st.get('composer') or t['name'] != t['layer']:   # scores and a genre's extra parts: each has its own pick
            new = opts.instruments.get(t['name']) if t['layer'] in MELODIC_ROLES else None
        else:
            new = opts.instruments.get(t['layer']) if t['layer'] in MELODIC_ROLES else None
        if new == 'off':                                 # a player / extra part switched off in the Sound panel
            t['off'] = True
            new = None
        if isinstance(new, str) and new.startswith(('vstp:', 'vstd:', 'vstq:')):
            new = _installed_vst(new, opts)             # a plugin picked in the Sound dropdown -> playable sound
        if new and (new in INSTRUMENTS or new.startswith(('user:', 'vst:', 'sf:', 'real:'))) and new != t['inst']:
            t['fallback'] = t['inst']
            t['user_pick'] = True
            t['inst'] = new
            t['p'] = {}
            t['db'] = None
        tracks.append(t)
    st['tracks'] = tracks
    from . import drumkits
    groove_of = (st.get('fusion') or {}).get('groove') or st.get('name') or opts.style
    borrow_drums(st, opts)                               # drum style: another genre's beat on this genre's sounds
    kit_id = drumkits.effective(opts, groove_of, st)
    pattern_id = drumkits.pattern_of(opts, groove_of)
    preset = drumkits.configure(st, kit_id, groove_of, opts, pattern_id) if (kit_id or pattern_id) else st['kit']
    if not kit_id:
        preset = st['kit']
        from .pool_variety import KIT_ALTS              # (2.5.2) some genres pick one of several fitting kits per song
        alts = KIT_ALTS.get(st.get('name') or opts.style)
        if alts and preset in alts and not st.get('kit_override'):
            import random as _random
            ks = (opts.sound_seed if opts.sound_seed is not None else opts.seed) or 0
            preset = _random.Random(ks * 7919 + 17).choice([a_ for a_ in alts if a_ in KITS] or [preset])
    kit = dict(KITS.get(preset, {}))
    if not kit_id:
        for k, v in st.get('kit_override', {}).items():
            kit[k] = {**kit.get(k, {}), **v}
    if not kit_id and not getattr(opts, 'kit', None):    # (2.9.4) dubstep genres: one of several dubstep kits per song
        from .pool_variety import DUB_KITS, DUB_KITS_FOR
        ch = DUB_KITS_FOR.get(st.get('name') or opts.style)
        if ch:
            import random as _random
            ks = (opts.sound_seed if opts.sound_seed is not None else opts.seed) or 0
            pick = _random.Random(ks * 104729 + 3).choice(ch)
            st['dub_kit'] = pick
            for k, v in (DUB_KITS.get(pick) or {}).items():
                kit[k] = {**kit.get(k, {}), **v}
    if st.get('kick_shape') and not getattr(opts, 'kit', None):    # the genre's own kick, whatever drum preset it sits on
        kit['kick'] = {**kit.get('kick', {}), **st['kick_shape']}
    st['kitparams'] = kit
    st['drum_picks'] = drumkits.pick_voices(st, opts, kit_id, preset, groove_of)   # each song: its own kick / snare / clap / hats
    drumkits.install_break(st, st['tracks'])
    drummer.apply_percussion(st, opts)                   # percussion picked on its own (or switched off)
    if opts.swing is not None:
        st['swing'] = opts.swing
    st['human'] = st['human'] * opts.humanize
    if opts.sidechain is not None:
        st['sc_depth'] = opts.sidechain
        if opts.sidechain > 0:
            for t in st['tracks']:
                if t['layer'] in ('bass', 'chords', 'pad', 'arp') and not t['sc']:
                    t['sc'] = 0.8
    if opts.sc_release is not None:
        st['sc_release'] = opts.sc_release
    if opts.reverb_size:
        st['reverb'] = opts.reverb_size
    m = dict(st['master'])
    if opts.loudness is not None:
        m['lufs'] = opts.loudness
    m['air'] = m.get('air', 1.5) + 3.0 * opts.brightness
    m['low'] = m.get('low', 1.0) + opts.bass_boost
    mp = getattr(opts, 'master_preset', None)
    if mp:                                               # mastering targets (Mix & master)
        m.update(MASTER_PRESETS.get(mp, {}))
    rt = getattr(opts, 'ref_tone', None)
    if isinstance(rt, (list, tuple)) and len(rt) == 9:     # match a reference song's tonal balance
        m['tone'] = [float(v) for v in rt]
        rq = getattr(opts, 'ref_tone_quiet', None)
        if isinstance(rq, (list, tuple)) and len(rq) == 9:
            m['tone_quiet'] = [float(v) for v in rq]
    m['genre_width'] = float(st['master'].get('width', 1.0))     # the genre's own width (it used to be overwritten)
    m['width'] = opts.width
    m['drive'] = opts.drive
    if opts.lofi is not None:
        m['lofi'] = opts.lofi
    st['master'] = m
    vin = getattr(opts, 'vinyl', None)
    if vin is not True:                                  # crackle only when you switch it on (no genre turns it on by itself)
        st['tracks'] = [t for t in st['tracks'] if t['inst'] != 'vinyl']
    elif vin is True and not any(t['inst'] == 'vinyl' for t in st['tracks']):
        st['tracks'] = st['tracks'] + [dict(name='vinyl', layer='fx', inst='vinyl', pan=0.0, rev=0.0, dly=0.0, sc=0.0, db=-36,
                                            hp=None, drive=None, p={})]
    return st


# extra lead rhythms per phrasing family (was one shared bank, which put the same 16th-note pairs into every genre)
PHRASE_BANKS = {
    'sung': ['x-x-x-x-x---....', 'x---x-x-x-------', '..x-x-x-x---x---', 'x-.x-.x-x-------', 'x-x-x---x---x---',
             'x---x---x-x-x---', '....x-x-x-x-x---', 'x-----x-x-x-....', 'x-x-x-x---------', '..x-x---x-x-x---'],
    'syncopated': ['..x..x..x..x....', '.x.x..x...x.x...', 'x..x..x.x.......', '..x.x..x..x.....', 'x..x...x..x.x...',
                   '...x..x...x..x..', 'x.x..x..x.x.....', '..x...x.x..x....'],
    'sparse': ['x-------x---x---', 'x-----x-x-------', 'x---------------', 'x-----x---------', '....x-------x---',
               'x---x-------....', 'x-------....x---'],
    'busy': ['x.x.x.x.x-x-x---', 'x.xx.xx.x.......', 'xx.x.x..x.x.xx..', 'x.x.xx.x.x.x....', '.x.x.x.x.x.x.x..',
             'x-x-..x-x-..x-x-'],
    'triple': ['x-xx-xx-xx-x', 'x--x--x-----', 'x-xx-x-----.', 'x-----x-xx-x', 'xxx-x-x-----', 'x--x-xx-----',
               'x-x-x-x-----', 'x-----x--x--'],
}
PHRASE_FAMILY = {
    **{k: 'busy' for k in ('psytrance', 'dnb', 'jungle', 'breakcore', 'hyperpop', 'chiptune', 'trap', 'phonk', 'uk_drill', 'hardstyle')},
    **{k: 'syncopated' for k in ('future_funk', 'fusion', 'disco_funk', 'funk', 'disco', 'afrobeats', 'amapiano', 'reggaeton', 'moombahton', 'reggae', 'ukgarage', 'house',
                                 'deep_house', 'tech_house', 'city_pop', 'bossa_nova')},
    **{k: 'sparse' for k in ('deep_dubstep', 'deep_dubstep_minimal', 'ambient', 'downtempo', 'lofi', 'vaporwave', 'jazz', 'cinematic', 'orchestral', 'film_piano',
                             'adventure', 'tension', 'boombap', 'neoclassical', 'western', 'hybrid_trailer')},
    **{k: 'sung' for k in ('smooth_jazz', 'quiet_storm', 'modern_country', 'country_waltz', 'outlaw_country', 'western_swing',
                           'chamber', 'fantasy_rpg', 'holiday', 'chamber_pop', 'symphonic_metal', 'gospel', 'rnb', 'motown',
                           'country', 'kpop', 'indie_rock', 'punk', 'cumbia', 'ska', 'dancehall')},
    **{k: 'busy' for k in ('bluegrass', 'salsa', 'swing', 'melodic_techno', 'baile_funk', 'jersey_club', 'afro_house', 'braindance')},
    'hauntology_sunlit': 'sparse', 'hauntology_dark': 'sparse', 'neo_soul': 'sung', 'alt_rnb': 'sung', 'g_funk': 'sung', 'plugg': 'sung',
    'hauntology': 'sparse', 'brostep': 'sparse', 'neurofunk': 'sparse', 'melodic_dubstep': 'sung', 'liquid_dnb': 'sung', 'jam_band': 'busy', 'soft_rock': 'sung', 'teen_pop': 'sung', 'luxury_rap': 'sparse',
    'baroque': 'busy', 'orchestral_hiphop': 'busy', 'tango': 'sparse',
}


def lead_octave_shift(mel, st):
    """Octaves to move the lead by so it sits where the genre's lead lives, whatever the key: around G4-G5 for a
    sung-style or synth lead (a little higher for trap bells and trance arps), and always clear above the chords so the
    melody isn't buried. Riff leads (rock, metal, funk, blues) already place themselves low and are left alone."""
    if not mel or (st.get('lead_device') == 'riff' and not st.get('lead_lo')):
        return 0
    mean = sum(m for _, _, m, _ in mel) / len(mel)
    if st.get('lead_lo'):                               # genres whose lead lives lower (phonk cowbells sit around A3-A4)
        lo = st['lead_lo']
    else:
        lo = max(12 * (st.get('lead_oct', 5) + 1) - 6, st.get('chord_center', 62) + 4)   # mean ~G4-G5 (oct 5)
        lo += {'bell': 3, 'arp': 2}.get(st.get('lead_device'), 0)
    k = 0
    while mean + k >= lo + 12:
        k -= 12
    while mean + k < lo:
        k += 12
    return k


def _snap(key, m):
    """Nearest note of the key."""
    pcs = {(key.root + x) % 12 for x in key.scale}
    for d in (0, 1, -1, 2, -2):
        if (m + d) % 12 in pcs:
            return m + d
    return m


def shape_melody(notes, phrase_bars, key, opts, rnd):
    """Repetition (repeat the opening idea vs keep developing), melody range, and simplicity (fewer, longer notes)."""
    if not notes:
        return notes
    R = max(0.0, min(1.0, float(getattr(opts, 'repetition', 0.5))))
    W = max(0.0, min(1.0, float(getattr(opts, 'melody_range', 0.5))))
    S = max(0.0, min(1.0, float(getattr(opts, 'simplicity', 0) or 0)))
    notes = sorted(notes)
    blk = 8                                                  # beats in a 2-bar idea
    nblk = int(phrase_bars * 4 // blk)
    if R > 0.6 and nblk >= 3:                                # catchy: the opening 2 bars come back
        first = [n for n in notes if n[0] < blk]
        copy_to = [k for k in range(1, nblk - 1) if R > 0.85 or k % 2 == 0]
        out = [n for n in notes if int(n[0] // blk) not in copy_to]
        for k in copy_to:
            out += [(b + k * blk, d, m, v) for b, d, m, v in first]
        notes = sorted(out)
    elif R < 0.35:                                           # developing: later ideas drift away from the first
        amt = (0.35 - R) / 0.35
        notes = [(b, d, _snap(key, m + rnd.choice([-2, -1, 1, 2])) if b >= blk and rnd.random() < 0.35 * amt else m, v)
                 for b, d, m, v in notes]
    if abs(W - 0.5) > 0.05:                                  # narrow <-> wide, kept in key
        f = 0.45 + 1.1 * W
        ms = sorted(m for _, _, m, _ in notes)
        mid = ms[len(ms) // 2]
        notes = [(b, d, _snap(key, int(round(mid + (m - mid) * f))), v) for b, d, m, v in notes]
    if S > 0:                                                # simple: drop off-beat notes, hold the rest longer
        kept = []
        for n in notes:
            b = n[0]
            on_beat = abs(b - round(b)) < 1e-6
            if not on_beat and rnd.random() < 0.75 * S and kept:
                continue
            kept.append(n)
        out = []
        for i, (b, d, m, v) in enumerate(kept):
            nxt = kept[i + 1][0] if i + 1 < len(kept) else b + d
            out.append((b, max(d, min(nxt - b, 2.0) * 0.92 * S + d * (1 - S)), m, v))
        notes = out
    return notes


def _thin_cell(rh, rnd):
    """A verse version of a rhythm cell: the off-beat notes thinned out, the kept notes held a little longer."""
    keep = [n for n in rh if n[0] % 4 == 0 or rnd.random() < 0.45]
    if len(keep) < 2:
        keep = list(rh[:2])
    out = []
    for i, (step, l, c) in enumerate(keep):
        nxt = keep[i + 1][0] if i + 1 < len(keep) else 16
        out.append((step, max(l, min(nxt - step, l * 2)), c))
    return out


def theme_device(notes, role, rnd):
    """Lead devices (arps, riffs, ostinatos ...) share the song's idea by replaying the main figure's seed on the
    other sections' chords; the verse version drops some of the off-beat notes."""
    if role != 'verse':
        return notes
    return [n for n in notes if abs(n[0] * 4 - round(n[0] * 4)) > 1e-6 or round(n[0] * 4) % 4 == 0 or rnd.random() < 0.6]


def derive_verse(hook, ph_hook, prog_v, cb, key, rnd):
    """Hook-first writing: the verse melody is the chorus hook's rhythm and contour, sung lower (down a third) and a
    little sparser, re-fitted to the verse chords - so the chorus lands as the payoff of an idea you've already heard."""
    ph = 2 * len(prog_v) * cb
    L = ph * 4
    scale = {(key.root + iv) % 12 for iv in key.scale}
    down = rnd.choice([3, 4, 3, 5])
    thin = rnd.uniform(0.1, 0.3)

    def snap(m, pcs):
        return min((m + k for k in range(-5, 6) if (m + k) % 12 in pcs), key=lambda x: (abs(x - m), x))
    out = []
    reps = int(math.ceil(L / max(1, ph_hook * 4)))
    for r in range(reps):
        for (bt, du, m, v) in hook:
            t = bt + r * ph_hook * 4
            if t >= L - 0.01:
                break
            strong = abs(t - round(t)) < 0.01
            if not strong and du <= 0.5 and rnd.random() < thin:
                continue
            chord = prog_v[(int(t // 4) // cb) % len(prog_v)]
            ct = {key.deg(chord + i, 4) % 12 for i in (0, 2, 4)}
            m2 = snap(m - down, ct if strong else scale)
            out.append((t, min(du, L - t), m2, v * 0.92))
    if out:                                                    # end the verse phrase open (3rd / 5th), not on the root
        t, du, m, v = out[-1]
        chord = prog_v[(int(t // 4) // cb) % len(prog_v)]
        open_ = {key.deg(chord + i, 4) % 12 for i in (2, 4)}
        out[-1] = (t, du, snap(m, open_), v)
    return out, ph


def gen_melody(key, prog, chord_bars, st, rnd, complexity, theme=None, role='main'):
    """theme: a dict shared by the song's melodies (main first, then alt / verse). The main melody writes its opening
    two-bar motif into it - rhythm cells and the notes relative to the first chord - and the alt and verse melodies
    are built from that motif (moved to their own chords; the alt one inverted or sequenced, the verse one lower and
    sparser), so a song has one tune in different shapes instead of three unrelated ones. theme=None: the old way."""
    from .leads import GENERATORS
    dev = st.get('lead_device', 'hook')
    if dev in GENERATORS:                              # genre lead device (arpeggio, riff, ostinato, bell, call, chops)
        if theme is None:
            return GENERATORS[dev](key, prog, chord_bars, st, rnd, complexity)
        if 'dev_seed' not in theme:
            theme['dev_seed'] = rnd.random()
        notes, pb = GENERATORS[dev](key, prog, chord_bars, st, random.Random(theme['dev_seed']), complexity)
        return theme_device(notes, role, random.Random(theme['dev_seed'] + 1)), pb
    phrase_bars = 2 * len(prog) * chord_bars
    fam = PHRASE_FAMILY.get(st.get('name'), 'sparse' if st.get('category') == 'Orchestral' else 'sung')
    if st.get('meter'):
        fam = 'triple'
    extra = [] if st.get('meter') == '9/8' else rnd.sample(PHRASE_BANKS[fam], 3)   # (the stock phrases are 12-step)
    rhs = sorted((parse_rhythm(r) for r in list(st['lead_rh']) + extra), key=len)
    if complexity < 0.35:
        pool = rhs[:max(2, len(rhs) // 2 + 1)]
    elif complexity > 0.65:
        pool = rhs[len(rhs) // 2 - 1:] if len(rhs) > 2 else rhs
    else:
        pool = rhs
    idx = list(range(len(pool)))
    rnd.shuffle(idx)
    rr = [pool[idx[i % len(idx)]] for i in range(4)]
    plan = rnd.choice(PHRASE_PLANS)
    lo, hi = -3, 10
    d = prog[0] + rnd.choice([0, 2, 4, 4, 7])
    while d > hi:
        d -= 7
    contour = rnd.choice(['arch', 'rise', 'fall', 'wave', 'valley', 'arch'])   # the phrase's overall shape
    given = None                                     # (b8, i) -> degree: the song's motif, placed on this melody's chords
    if theme is not None and theme.get('cells'):
        cells = theme['cells']
        if role == 'verse':
            cells = [_thin_cell(c, rnd) for c in cells]
        rr[plan[0]], rr[plan[1]] = cells[0], cells[1] if plan[1] != plan[0] else cells[0]
        shift = prog[0] - theme['root']
        shift -= 7 * round(shift / 7) if abs(shift) > 3 else 0         # nearest copy of the new chord root
        mode = 'lower' if role == 'verse' else rnd.choice(['sequence', 'invert', 'sequence', 'same'])
        deg = {tuple(int(x) for x in k_.split(',')): v for k_, v in theme['deg'].items()}   # (JSON-safe keys)
        first = deg.get((0, 0), prog[0])
        given = {}
        for k_, v in deg.items():
            if mode == 'invert':
                v = first - (v - first)              # the motif turned upside down around its first note
            elif mode == 'lower':
                v -= 2                               # the verse sits a little lower than the chorus
            elif mode == 'sequence':
                v += rnd.choice([1, 2, -1]) if k_ == (0, 0) else 0
            given[k_] = max(lo, min(hi, v + shift))
        if role == 'verse':
            contour = rnd.choice(['rise', 'valley', 'wave'])          # verses climb toward the chorus
    plan8 = [rr[i] for i in plan]
    shape = {'arch': lambda x: 0.3 + 0.6 * math.sin(math.pi * x), 'rise': lambda x: 0.2 + 0.7 * x, 'fall': lambda x: 0.85 - 0.6 * x,
             'wave': lambda x: 0.5 + 0.3 * math.sin(4 * math.pi * x), 'valley': lambda x: 0.8 - 0.6 * math.sin(math.pi * x)}[contour]
    seq_shift = rnd.choice([0, 1, 2, 2, -1, 3])          # bars 3-4 restate bars 1-2 a step or two higher (a sequence)
    prev = None
    motif = {}
    notes = []
    lang = st.get('melody_lang') or 'diatonic'
    lrnd = random.Random(hash(tuple(rnd.getstate()[1][:6])) ^ phrase_bars) if lang != 'diatonic' else None
    major3 = (key.scale[2] - key.scale[0]) % 12 == 4
    avoid = ({3, 6} if major3 else {1, 5}) if lang in ('pentatonic', 'blues') else set()
    steps = [-2, -1, -1, 1, 1, 2, 0, 3, -3]
    w = [1, 3, 3, 3, 3, 1, 1, 0.5, 0.5]
    for bar in range(phrase_bars):
        chord = prog[(bar // chord_bars) % len(prog)]
        ct = chord_tones_deg(chord, lo, hi)
        b8 = (bar // max(1, phrase_bars // 8)) % 8 if phrase_bars > 8 else bar % 8
        rh = plan8[b8]
        reuse = b8 in (2, 3, 4, 5)
        src = b8 % 2
        for i, (step, l, c) in enumerate(rh):
            if given is not None and b8 < 2 and (bar < 8 or phrase_bars <= 8) and (b8, i) in given:
                d = given[(b8, i)]                         # the song's motif, on this melody's chords
            elif reuse and (src, i) in motif:
                d = motif[(src, i)] + (seq_shift if b8 in (2, 3) else 0)
            else:
                d += rnd.choices(steps, w)[0]
                target = lo + (hi - lo) * shape((bar + step / 16) / phrase_bars)
                if abs(d - target) > 2 and rnd.random() < 0.45:   # follow the contour
                    d += 1 if target > d else -1
                if d > hi:
                    d = hi - (d - hi)
                if d < lo:
                    d = lo + (lo - d)
            strong = step % 4 == 0
            if strong and (reuse or rnd.random() < 0.8):
                d = min(ct, key=lambda x: (abs(x - d), x))
                if d == prev and len(ct) > 1 and rnd.random() < 0.65:   # don't hammer the same note
                    d = min((x for x in ct if x != prev), key=lambda x: abs(x - d))
            if b8 < 2 and (bar < 8 or phrase_bars <= 8):
                motif[(b8, i)] = d
            last = (b8 == 7 and i == len(rh) - 1)
            half = (b8 == 3 and i == len(rh) - 1)
            ln = l
            if fam in ('sung', 'sparse', 'triple') and b8 in (1, 3, 5) and i == len(rh) - 1 and step + l >= 13:
                ln = (12 - step) if step <= 10 else min(l, 2)     # a breath (about a beat) before the next phrase
            if last:
                d = min([x for x in ct if (x - chord) % 7 == 0] or ct, key=lambda x: abs(x - d))
                ln = max(l, 16 - step)
            elif half:                                      # mid-phrase: leave it open on the 3rd or 5th
                d = min([x for x in ct if (x - chord) % 7 in (2, 4)] or ct, key=lambda x: abs(x - d))
            prev = d
            vel = (0.95 if strong else 0.78) * rnd.uniform(0.9, 1.05)
            if avoid and d % 7 in avoid and not (strong and d in ct):      # pentatonic: step off the avoid notes
                d = d + 1 if (d + 1) % 7 not in avoid and d + 1 <= hi else d - 1
            t = bar * 4 + step / 4
            midi = key.deg(d, st['lead_oct'])
            prev_end = notes[-1][0] + notes[-1][1] if notes else -1
            if lang == 'blues' and strong and d % 7 in (0, 2, 4) and lrnd.random() < (0.45 if d % 7 == 2 else 0.2) \
                    and t - 0.125 >= prev_end:                                # bluesy slide up into the note
                notes.append((t - 0.125, 0.11, midi - 1, vel * 0.7))
            elif lang == 'bebop' and strong and lrnd.random() < 0.12 + 0.2 * complexity and t - 0.25 >= prev_end:
                notes.append((t - 0.25, 0.22, midi - 1, vel * 0.8))          # chromatic approach from below
            notes.append((t, ln / 4 * 0.92, midi, vel))
    if theme is not None and not theme.get('cells') and role == 'main':
        theme.update(cells=[[list(n) for n in plan8[0]], [list(n) for n in plan8[1]]], root=prog[0],
                     deg={f'{a},{b}': v for (a, b), v in motif.items()})
    return notes, phrase_bars


def apply_simplicity(opts):
    """Simplicity strips a song back: fewer notes, plain triads, no counter-melody / doubling, (later) held chords."""
    S = max(0.0, min(1.0, float(getattr(opts, 'simplicity', 0) or 0)))
    if S <= 0:
        return opts
    ch = dict(complexity=float(opts.complexity) * (1 - 0.75 * S))
    if S >= 0.4:
        if not opts.chord_color:
            ch['chord_color'] = 'triad'
        if not opts.counter:
            ch['counter'] = 'off'
    if S >= 0.5 and not opts.layering:
        ch['layering'] = 'off'
    if S >= 0.75 and 'arp' not in (opts.muted or []):
        ch['muted'] = list(opts.muted or []) + ['arp']
    return replace(opts, **ch)


def style_knob_defaults(opts):
    """Some genres are simpler / more repetitive by nature; their defaults apply while your knobs are untouched."""
    sd = STYLES.get(opts.style, {})
    ch = {}
    if sd.get('repetition') is not None and abs(float(opts.repetition) - 0.5) < 1e-9:
        ch['repetition'] = sd['repetition']
    if sd.get('simplicity') and not opts.simplicity:
        ch['simplicity'] = sd['simplicity']
    return replace(opts, **ch) if ch else opts


# synth / soundfont pads that swell in slowly (recorded string sections switch to spiccato for short notes, so they're fine)
SLOW_ATTACK = {'warmpad': 1.2, 'glasspad': 0.6, 'strings': 0.35, 'choir': 0.4, 'sf:slowstrings': 0.5, 'sf:choir': 0.4,
               'real:choir': 0.4}


def attack_of(t):
    a = (t.get('p') or {}).get('a')
    if a is not None:
        return float(a)
    inst = t.get('inst') or ''
    return SLOW_ATTACK.get(inst, 0.0)


ARP_FIGURES = ('up', 'down', 'updown', 'converge', 'pinky', 'octaves', 'motif', 'random')
ARP_GATES = ('xxxxxxxxxxxxxxxx', 'x.xxx.xxx.xxx.xx', 'xx.xx.xx.xx.x.x.', 'x.x.xx.xx.x.xx.x', 'xxx.xxx.xxx.xx.x',
             'x.xx.x.xx.xx.x.x', 'xx.x.xx.xx.x.xx.')


def vary_arp(arp, rnd, electronic=True):
    """Each song gets its own arpeggio instead of the genre's one figure every time: the genre's own figure stays the
    most likely, but the order of the notes (up, down, up-down, outside-in, a pedal note, octaves, a little fixed motif,
    random), the range (one or two octaves), the speed (one step faster or slower) and, on 16ths, a gate rhythm with
    rests are all picked per song (bands and orchestras: only the note order). Written figures (montuno, Alberti, rolls, mallets, taps, beat-locked) are left alone."""
    a = dict(arp)
    if a.get('rh') or a.get('beat_lock') or a.get('mode') not in ('up', 'down', 'updown', 'random'):
        return a
    if rnd.random() < 0.7:
        a['mode'] = rnd.choice([m for m in ARP_FIGURES if m != arp['mode']])
        if a['mode'] == 'motif':
            ln = rnd.choice([3, 4, 5, 6])                          # 3 or 5 over 16ths: a figure that drifts over the beat
            a['motif'] = tuple(rnd.randrange(4) for _ in range(ln))
        if a['mode'] == 'pinky':
            a['pedal'] = rnd.choice(['low', 'low', 'high'])
    if rnd.random() < 0.3 and a['mode'] not in ('octaves',):
        a['span'] = 2
    if not electronic:                                     # band / orchestral parts: the order of notes only
        return a
    r = rnd.random()
    if r < 0.2:
        a['rate'] = max(0.5, a['rate'] / 2)
    elif r < 0.4:
        a['rate'] = min(4, a['rate'] * 2)
    if a['rate'] <= 1 and rnd.random() < 0.55:
        a['gate_rh'] = rnd.choice(ARP_GATES[1:])
    return a


def hold_slow_chords(evs, tracks, st, bpm=120):
    """A slow-attack pad (warm pad, string section, choir) can't play short chord stabs: the notes never reach full
    volume, then ring out after the beat as a smear of late, off-beat notes. On such a sound the chord is held from the
    beat it starts on until it changes, as a keyboard player would on a pad patch."""
    spb = 60.0 / max(40.0, float(bpm or 120))
    for name, t in tracks.items():
        if t.get('layer') not in ('chords', 'pad') or attack_of(t) < 0.3 or t.get('double_of'):
            continue                                             # (a layer keeps exactly the notes of the part it doubles)
        mine = sorted((e for e in evs if e.track == name and e.midi is not None), key=lambda e: e.beat)
        if not mine or sum(e.dur for e in mine) / len(mine) * spb >= attack_of(t) * 1.5:
            continue                                             # already long notes: nothing to do
        clusters = []
        for e in mine:
            if clusters and abs(clusters[-1][0] - e.beat) < 0.06:
                clusters[-1][1].append(e)
            else:
                clusters.append([e.beat, [e]])
        spans, k = [], 0
        while k < len(clusters):
            b0, notes = clusters[k]
            pset = frozenset(e.midi for e in notes)
            j = k + 1
            end = max(e.beat + e.dur for e in notes)
            while j < len(clusters) and frozenset(e.midi for e in clusters[j][1]) == pset and clusters[j][0] - end < 2.01:
                end = max(e.beat + e.dur for e in clusters[j][1])
                j += 1
            for c in clusters[k + 1:j]:
                for e in c[1]:
                    e.midi = None                                # merged into the held chord
            spans.append([b0, end, notes])
            k = j
        prev = None
        for i, (b0, end, notes) in enumerate(spans):
            start = float(int(b0 + 1e-6))
            if prev is not None and start <= prev[0] + 1e-6:
                start = b0
            nxt = spans[i + 1][0] if i + 1 < len(spans) else end + 0.5
            stop = min(nxt, end + 0.5)
            for e in notes:
                e.beat, e.dur, e.strum = start, max(0.25, stop - start - 0.02), 0.0
            if prev is not None:
                for e in prev[1]:
                    e.dur = max(0.25, min(e.dur, start - e.beat - 0.02))
            prev = (start, notes)
    evs[:] = [e for e in evs if not (e.midi is None and tracks.get(e.track, {}).get('layer') in ('chords', 'pad')
                                       and attack_of(tracks[e.track]) >= 0.3 and not tracks[e.track].get('double_of'))]


def compose(opts):
    from . import drumkits  # noqa: F401  (break patterns)
    from .styles import STYLE_ALIASES
    if opts.style in STYLE_ALIASES or any(b in STYLE_ALIASES for b in (opts.blend or [])):
        opts = replace(opts, style=STYLE_ALIASES.get(opts.style, opts.style),
                       blend=[STYLE_ALIASES.get(b, b) for b in (opts.blend or [])])
    _J = ('cinematic_journey', 'cinematic_journey_low')
    if opts.style in _J and opts.blend:                     # a through-composed score doesn't blend
        opts = replace(opts, blend=[], blend_parts={})
    elif any(b in _J for b in (opts.blend or [])):
        opts = replace(opts, blend=[b for b in opts.blend if b not in _J])
    user_opts = opts
    from . import traits as _traits
    opts = _traits.apply_opts(opts, opts.style)
    opts = style_knob_defaults(opts)
    opts = apply_simplicity(opts)
    opts, mood = apply_mood(opts)
    S = max(0.0, min(1.0, float(getattr(opts, 'simplicity', 0) or 0)))
    ps = opts.part_seeds or {}

    def prng(part, k):
        return random.Random(ps.get(part) if ps.get(part) is not None else opts.seed * 1009 + k)
    rnd = prng('harmony', 1)          # key, tempo, progression
    rnd_m = prng('melody', 2)         # lead melody
    rnd_d = prng('drums', 3)          # drum patterns, fills, hats
    rnd_b = prng('bass', 4)           # bass lines
    rnd_c = prng('chords', 5)         # chord rhythms, arps, voicing choices
    st = resolve_style(opts, random.Random(opts.seed * 7 + 3), mood)
    st = _traits.apply_style(st, opts, opts.style)
    if not st.get('composer'):                           # through-composed scores keep their exact orchestration
        st = apply_variety(st, opts, random.Random(opts.seed * 7919 + 17))
        from .evolve import song_variations
        song_variations(st, opts)                        # (1.92.3) genres that vary their palette / figures per song
        add_counter_track(st, opts)
        add_layer_tracks(st, opts)
        add_bass_switch_tracks(st)
        add_section_switch_tracks(st, opts, random.Random(f'{opts.seed}-rotation-{opts.style}' + _snd(opts)))
    add_extra_parts(st, opts)                            # your extra instruments (Parts panel > + Add instrument)
    debell(st, opts)
    chords_t = next((t for t in st['tracks'] if t['name'] == 'chords'), None)
    if chords_t and attack_class(chords_t['inst']) == 'hit':      # a pad under struck chords swells in, never a late 2nd hit
        for t in st['tracks']:
            if t['layer'] == 'pad' and not t.get('user_pick') and float((t.get('p') or {}).get('a', 0) or 0) < 0.35:
                t['p'] = dict(t.get('p') or {}, a=0.35)
    apply_sampled(st, opts)
    from . import fxrig
    fxrig.plan(st, opts.style, bool(getattr(opts, 'vst_rig', False)))
    by_name = {t['name']: t for t in st['tracks']}
    st['tracks'] = [t for t in st['tracks'] if not (t.get('double_of') and not t.get('keep_inst')
                                                    and by_name.get(t['double_of'], {}).get('inst') == t['inst'])]
    energy = float(opts.energy)
    cx = float(opts.complexity)
    bpm = opts.bpm or rnd.randint(*st['bpm'])
    if not opts.bpm and mood and mood.get('tempo'):
        bpm = int(max(55, min(200, round(bpm * mood['tempo']))))
    # ---- key & scale
    scales = st['scales']
    if opts.key:
        root, minor = parse_key(opts.key)
        scale = opts.scale or ('minor' if minor else 'major')
        if not opts.scale and scale not in scales:
            alt = [s for s in scales if (s in ('minor', 'dorian', 'phrygian', 'harmonic_minor', 'melodic_minor')) == minor]
            scale = alt[0] if alt else scale
    else:
        root = rnd.choice(st['roots']) if st.get('roots') else rnd.randrange(12)   # open-tuning genres: E, G, A, D
        if not opts.scale and mood and mood.get('scales'):
            pref = [x for x in mood['scales'] if x in scales] or mood['scales']
            scale = rnd.choice(pref)
        else:
            scale = opts.scale or rnd.choice(scales)
    key = Key(root, scale)
    if st.get('tune_kick') and (st.get('kitparams') or {}).get('kick') is not None:
        km = 28 + ((root - 28) % 12)                     # hard dance / psy: the kick's tail is tuned to the key (41-78 Hz)
        st['kitparams'] = dict(st['kitparams'], kick=dict(st['kitparams']['kick'], pitch=round(440.0 * 2 ** ((km - 69) / 12), 2)))
    if st.get('composer') == 'journey':
        from .journey import compose_journey
        return compose_journey(st, opts, key, bpm, random.Random(opts.seed * 977 + 11))
    # ---- harmony
    progs = st.get('progs') or {scale: GENERIC_PROGS.get(scale, GENERIC_PROGS['major'])}
    if isinstance(progs, dict):
        progs = progs.get(scale) or GENERIC_PROGS.get(scale) or next(iter(progs.values()))
    elif scale not in st['scales']:
        progs = GENERIC_PROGS.get(scale, progs)
    custom = parse_progression(opts.progression)
    progs = [p for p in progs if all(key.chord_ok(d) for d in p)] or [[0, 3, 4, 0]]
    bank = [p for p in GENERIC_PROGS.get(scale, []) if all(key.chord_ok(d) for d in p)]
    pool = [p for p in progs] * 2 + ([] if st.get('own_progs') else [p for p in bank if p not in progs])
    picks = []
    for _ in range(40):
        p = rnd.choice(pool)
        if p not in picks:
            picks.append(p)
        if len(picks) == 3:
            break
    while len(picks) < 3:
        picks.append(picks[-1])
    prog_main = custom or picks[0]
    prog_verse = custom or (picks[1] if rnd.random() < 0.6 else picks[0])
    prog_alt = custom or picks[2]
    sp = st.get('section_progs') or {}                  # a genre that pins its sections' harmony (TV-theme forms)
    if sp and not custom:
        ok = lambda p_: p_ if p_ and all(key.chord_ok(d) for d in p_) else None
        prog_main = ok(sp.get('main')) or prog_main
        prog_verse = ok(sp.get('verse')) or prog_verse
        prog_alt = ok(sp.get('alt')) or prog_alt
    colors = {'Electronic': ['triad', 'triad', '7', 'add9', 'sus2', 'add9no3', '6'],
              'Classic': ['triad', '7', '7', 'add9', '6', '9', 'sus4'], 'Orchestral': ['triad', 'triad', 'add9', 'sus4', '6']}
    chord_color = rnd.choice(colors.get(st.get('category'), ['triad']))
    if cx > 0.72 and chord_color == 'triad':
        chord_color = rnd.choice(['7', 'add9', '9'])
    sname = st.get('name') or opts.style
    sname_style = sname
    if sname in GENRE_COLORS and sname not in GENRE_COLORS_HOUSE:   # genres whose harmony is defined by extended chords
        chord_color = random.Random(opts.seed * 31 + 7).choice(GENRE_COLORS[sname])
    elif sname in GENRE_COLORS_HOUSE:               # house: 7ths, 9ths and the minor 11th of deep house
        chord_color = random.Random(f'{opts.seed}-{sname}-house-color').choice(GENRE_COLORS_HOUSE[sname])
    if getattr(opts, 'chord_color', None) in COLORS:
        chord_color = opts.chord_color
    if st.get('voicing') != 'power' and sname in GENRE_VOICING:
        st['voicing'] = GENRE_VOICING[sname]
    if st.get('voicing') != 'power' and sname in HOUSE_VOICINGS:
        rv = random.Random(f'{opts.seed}-{sname}-house-voicing')    # each song its own keyboard player: 9ths and
        st['voicing'] = rv.choice(HOUSE_VOICINGS[sname])           # 11ths in drop-2, quartal stabs, open triads
    if getattr(opts, 'voicing', None) in VOICINGS:
        st['voicing'] = opts.voicing
    st['melody_lang'] = opts.melody_style if getattr(opts, 'melody_style', None) in MELODY_STYLES else GENRE_MELODY.get(sname, 'diatonic')
    from .leads import pick_device
    _ms = (opts.part_seeds or {}).get('melody')       # a kept melody keeps its lead device too
    st['lead_device'] = pick_device(sname, opts.seed if _ms is None else _ms, getattr(opts, 'lead_style', None))
    if st.get('meter'):
        st['lead_device'] = 'hook'                     # the device figures are 16th-note based
    bsel = getattr(opts, 'build_style', None)
    from .arrange import default_build, DROPOUT, DROPOUT_FAMILY
    st['build_style'] = bsel if bsel in BUILD_STYLES else default_build(sname, st)
    st['build_home'] = st['build_style']
    fam = DROPOUT_FAMILY if (sname in DROPOUT and not st.get('build_family')) else st.get('build_family')
    st['build_seq'] = build_sequence(st['build_style'], bool(bsel in BUILD_STYLES), random.Random(f'{opts.seed}-build-{sname}'),
                                     amount=getattr(opts, 'builds', 'auto') or 'auto', family=fam)
    g = getattr(opts, 'groove', None)
    st['groove'] = None if g == 'straight' else (g if g in GROOVES else STYLE_GROOVE.get(sname))
    if st.get('category') == 'Electronic' and 'hat_choke' not in st and 'ohat' in st.get('drums', {}) and 'chat' in st.get('drums', {}):
        st['hat_choke'] = True                           # drum-machine hats: the closed hat chokes the open one
    if sname in TECHNO_RUMBLE and 'kick_rumble' not in st:
        st['kick_rumble'] = TECHNO_RUMBLE[sname]
    if sname in HOUSE_FEEL_GENRES and g != 'straight' and not st.get('meter'):
        st['track_feel'] = {k: v for k, v in HOUSE_FEEL.items() if k != 'kick'}
    pad_voicing = rnd.choice(['close', 'close', 'open'])
    modulate = bool(st.get('key_change')) or rnd.random() < {'teen_pop': 0.75, 'gospel': 0.35, 'soul_ballad': 0.35, 'smooth_jazz': 0.7}.get(st.get('name'), 0.22) \
        and st.get('form') in ('edm', 'song', 'trap', 'chip', 'halftime', 'song_b')   # (teen pop: the last-chorus key change)
    cb = st['chord_bars']
    if getattr(opts, 'chord_speed', None) == 'slow':
        cb = min(4, cb * 2)
    elif getattr(opts, 'chord_speed', None) == 'fast' and cb >= 2:
        cb = cb // 2
    elif st.get('slow_chords') and not getattr(opts, 'chord_speed', None) and rnd.random() < st['slow_chords']:
        cb = min(4, cb * 2)                             # long progressive / cinematic songs: now and then 2 bars per chord
    st['chord_bars'] = cb
    chord_size = st['chord_size'] + (1 if cx > 0.72 else 0) - (1 if cx < 0.28 and st['chord_size'] > 3 else 0)
    chord_size = max(3, min(5, chord_size))
    from .theory import MAQAM_QUARTER
    theme = {} if (getattr(opts, 'motif', 'song') or 'song') != 'free' and key.scale_name not in MAQAM_QUARTER else None
    # (one tune for the whole song; maqam melodies stay free - modal, taqsim-like lines that keep finding the half-flat notes)
    if (getattr(opts, 'melody_check', 'auto') or 'auto') != 'off' and not st.get('composer'):
        # (1.85) the melody check: a few hooks are written and the strongest kept; the rest of the song is unchanged
        import copy as _copy
        from .evolve import score_hook
        th0 = _copy.deepcopy(theme)
        mel_main, ph_bars = gen_melody(key, prog_main, cb, st, rnd_m, cx, theme, 'main')
        after = rnd_m.getstate()
        best = (score_hook(mel_main, key, 4 * ph_bars if ph_bars else 8), mel_main, ph_bars, theme)
        for k_ in range(1, 4):
            th_ = _copy.deepcopy(th0)
            msd = ps.get('melody') if ps.get('melody') is not None else opts.seed * 1009 + 2
            cand = gen_melody(key, prog_main, cb, st, random.Random(f'{msd}-hook{k_}'), cx, th_, 'main')
            sc = score_hook(cand[0], key, 4 * cand[1] if cand[1] else 8)
            if sc > best[0] + 0.04:
                best = (sc, cand[0], cand[1], th_)
        _, mel_main, ph_bars, theme = best
        rnd_m.setstate(after)
        st['hook_score'] = round(best[0], 3)
    else:
        mel_main, ph_bars = gen_melody(key, prog_main, cb, st, rnd_m, cx, theme, 'main')
    mel_alt, ph_alt = gen_melody(key, prog_alt, cb, st, rnd_m, cx, theme, 'alt')
    mel_verse, ph_verse = gen_melody(key, prog_verse, cb, st, rnd_m, cx, theme, 'verse')
    st['_motif'] = theme
    mel_main, mel_alt, mel_verse = [shape_melody(x, p_, key, opts, random.Random(opts.seed * 53 + i_))
                                    for i_, (x, p_) in enumerate(((mel_main, ph_bars), (mel_alt, ph_alt), (mel_verse, ph_verse)))]
    lead_k = lead_octave_shift(mel_main, st)            # same register in every key (not an octave higher in B than in C)
    mel_main, mel_alt, mel_verse = [[(a, b, m + lead_octave_shift(x, st), v) for a, b, m, v in x] for x in (mel_main, mel_alt, mel_verse)]
    if getattr(opts, 'hook_first', None) == 'on' and mel_main and not st.get('meter'):
        # hook-first writing: the verse is the chorus hook's rhythm and contour, sung lower, on the verse chords
        mel_verse, ph_verse = derive_verse(mel_main, ph_bars, prog_verse, cb, key, random.Random(opts.seed * 71 + 5))
        st['hook_first'] = True
    st['lead_shift'] = lead_k
    acid_pat = gen_acid_pattern(key, rnd_b, energy)

    tracks = {t['name']: t for t in st['tracks']}
    muted = set(opts.muted or [])
    # ---- form
    if st.get('forms') and isinstance(st['form'], str) and getattr(opts, 'structure', 'auto') in (None, '', 'auto'):
        _ch = random.Random(opts.seed * 31 + 7).choice(st['forms'])        # classical genres: one of their forms
        if not (st.get('forms_variants') and _ch == st['forms'][0]):          # (1.91) club genres: one of their layouts
            st['form'] = _ch
    if st.get('form_gen') and getattr(opts, 'structure', 'auto') in (None, '', 'auto', 'club', 'radio'):
        from . import grind as _grind                       # (1.96) metal: every song's layout written fresh,
        st['form'] = _grind.make_form(st['form_gen'], opts.seed, opts.style)   # every breakdown a new one
    from .styles import ABS_FORMS, CLUB_FORM
    if opts.structure == 'club' and CLUB_FORM.get(st.get('name') or opts.style):      # (1.91) Extended / club: the
        st['form'] = CLUB_FORM[st.get('name') or opts.style]                          # record-shaped layout
    form_abs = isinstance(st['form'], str) and st['form'] in ABS_FORMS
    form = list(FORMS[st['form']]) if isinstance(st['form'], str) else list(st['form'])
    if (getattr(opts, 'structure', 'auto') or 'auto') == 'auto' and not form_abs and not st.get('exact_form') \
            and not st.get('form_gen') and not st.get('composer') and len(st.get('forms') or []) < 2 \
            and st.get('category') != 'Orchestral' and not st.get('meter_form'):
        from .layouts import vary_layout                 # (2.4) the genre's layout, reshaped for this song
        form, st['layout_moves'] = vary_layout(form, st, _layout_seed(opts), {t['layer'] for t in st['tracks']})
    form = _traits.shape_form(form, opts, opts.style)
    if opts.structure == 'loop':
        form = [('loop', 16, set(l for l in ['kick', 'snare', 'top', 'bass', 'chords', 'pad', 'arp', 'lead', 'fx']), {})]
    elif opts.structure == 'club' and not form_abs:
        form = [(n, b * 2 if n in ('intro', 'outro') else b, l, o) for (n, b, l, o) in form]
    elif opts.structure == 'radio':
        seen_break = False
        f2 = []
        for (n, b, l, o) in form:
            if n in ('break', 'bridge', 'calm', 'C', 'solo') and not seen_break:
                seen_break = True
                f2.append((n, max(4, b // 2), l, o))
            else:
                f2.append((n, b, l, o))
        form = f2
    if opts.energy_curve and opts.structure != 'loop':
        form = apply_energy_curve(form, opts.energy_curve, st)
    scale_len = float(opts.length) * (1 if form_abs else st.get('form_scale', 1))
    if opts.structure == 'radio':
        scale_len *= 0.8

    evs = []
    sections = []
    fx = []
    bar0 = 0
    kick_name = st.get('kick_track', 'kick')
    snares = [s for s in st['snare_tracks'] if s in tracks]
    arp = dict(st['arp'])
    if cx > 0.78:
        arp['rate'] = max(0.5, arp['rate'] / 2)
    elif cx < 0.22:
        arp['rate'] = min(4, arp['rate'] * 2)
    arp_base = arp if grid_of(st) != 16 else \
        vary_arp(arp, random.Random(f"{opts.seed}-{st.get('name')}-arp-figure"), st.get('category') == 'Electronic')   # every song its own figure
    base_form = []
    if getattr(opts, 'skip_intro', False) and len(form) > 2:   # start straight on the groove: no intro section(s)
        while len(form) > 2 and form[0][0] in INTRO_NAMES:
            form = form[1:]
    for (sname, nbars, layers, opts_s) in form:
        if not opts_s.get('build') and opts.structure != 'loop':
            if st.get('form_gen'):                                  # (1.96) written layouts keep their 1- and 2-bar parts
                nbars = max(1, int(round(nbars * scale_len)))
            elif (st.get('name') or opts.style) in CLUB_COHERENT:     # (1.94) club records live on the 8-bar grid
                nbars = max(8, int(round(nbars * scale_len / 8)) * 8)
            else:
                nbars = max(4, int(round(nbars * scale_len / 4)) * 4)
        base_form.append((sname, nbars, layers, opts_s))
    edits = opts.sections or [dict(src=i, copy=0) for i in range(len(base_form))]
    edits = [e for e in edits if 0 <= int(e.get('src', -1)) < len(base_form)] or [dict(src=i, copy=0) for i in range(len(base_form))]
    vl_prev = {}                          # last chord / pad voicing, for voice leading
    _ps = lambda part, k: ps.get(part) if ps.get(part) is not None else opts.seed * 1009 + k
    rnd_hc = random.Random(f"{_ps('harmony', 1)}-colour")   # own streams (following part locks): colour chords and
    rnd_bp = random.Random(f"{_ps('bass', 4)}-passing")     # passing notes never reshuffle the rest of the song
    harm_alts = []                        # (start, end, pc, new_pc): secondary dominants, borrowed chords
    G = grid_of(st)
    GS = grid_steps(st)
    if st.get('meter'):
        st['groove'] = None
        st['swing'] = 0.5
        st['trap_hats'] = False
    base_seed = {k: (ps.get(k) if ps.get(k) is not None else opts.seed * 1009 + n) for n, k in
                 ((3, 'drums'), (4, 'bass'), (5, 'chords'), (2, 'melody'))}

    def sec_rng(part, uid, ed):
        sd = (ed.get('seeds') or {})
        if sd.get(part) is not None:
            return random.Random(f"{sd[part]}-{part}-edit")
        return random.Random(f"{base_seed[part]}-{part}-{uid}")
    variations = []
    n_builds = 0
    for si, ed in enumerate(edits):
        src = int(ed['src'])
        uid = f"{src}:{int(ed.get('copy', 0))}"
        sname, nbars, layers, opts_s = base_form[src]
        if ed.get('bars') and not opts_s.get('build'):
            nbars = max(2, min(64, int(ed['bars'])))
        rnd_d, rnd_b, rnd_c = sec_rng('drums', uid, ed), sec_rng('bass', uid, ed), sec_rng('chords', uid, ed)
        arp = dict(arp_base, **opts_s['arp']) if opts_s.get('arp') else arp_base      # a variation's own figuration
        var = opts_s.get('var')
        layers = set(layers) - set(ed.get('mute') or [])   # (switched-off parts are removed at the end: same take)
        if energy > 0.75 and opts_s.get('drop'):
            layers |= {'arp'}
        if energy < 0.25:
            layers -= {'arp'} if sname not in ('drop', 'chorus', 'hook', 'climax') else set()
        if opts_s.get('build') and 'arp' in layers and not ed.get('keep_layers'):
            rb_ = random.Random(f'{opts.seed}-{sname}-{si}-build-parts')   # builds aren't all "the arp, rising":
            if rb_.random() < 0.45 and layers & {'chords', 'pad', 'lead'}:   # some ride the chords / pad / a lead
                layers = layers - {'arp'}                                    # teaser instead
                if rb_.random() < 0.4 and 'lead' in tracks:
                    layers = layers | {'lead'}
        is_verse = sname in ('verse', 'A', 'rise', 'head') and not opts_s.get('drop')
        hook_verse = bool(st.get('hook_first') and is_verse and 'lead' in tracks and 'lead' not in layers
                          and not ed.get('keep_layers'))
        if hook_verse:                                   # hook-first: the verse sings the hook idea, low and soft
            layers = layers | {'lead'}
        prog = prog_alt if opts_s.get('alt') else (prog_verse if is_verse else prog_main)
        mel, ph = (mel_alt, ph_alt) if opts_s.get('alt') else ((mel_verse, ph_verse) if is_verse else (mel_main, ph_bars))
        if (ed.get('seeds') or {}).get('melody') is not None:
            mel, ph = gen_melody(key, prog, cb, st, random.Random(f"{ed['seeds']['melody']}-melody-edit"), cx,
                                 st.get('_motif') if ed.get('vary') is not None else None, 'alt')
            mel = [(a, b_, m + lead_k, v) for a, b_, m, v in mel]
        if opts_s.get('build'):
            seq = st.get('build_seq') or [st.get('build_style', 'roll')]
            st['build_style'] = bs = seq[min(n_builds, len(seq) - 1)]
            n_builds += 1
            st.setdefault('builds_used', []).append(bs)
            if bs in ('hats', 'claps', 'toms', 'drumless', 'halftime', 'tomgroove', 'march'):   # their own drums (or none)
                layers -= {'kick', 'snare', 'top'}
            elif bs == 'pulse':
                layers -= {'snare', 'top'}
            if bs in ('filter', 'kick_roll'):
                layers |= {'kick', 'snare', 'top'} if bs == 'filter' else {'kick'}
            elif bs == 'pause':
                layers -= {'kick', 'snare', 'bass'}
            elif bs == 'lift':
                layers |= {'kick', 'snare'}
        sec_start = bar0 * 4
        sections.append(dict(name=sname, bar=bar0, bars=nbars, layers=sorted(layers), opts=opts_s, src=src, prog=list(prog),
                             copy=int(ed.get('copy', 0)), index=si, edited=bool(ed.get('seeds') or ed.get('vary') or ed.get('mute') or ed.get('bars'))))
        if ed.get('vary') is not None:
            variations.append((sec_start, sec_start + nbars * 4, int(ed['vary'])))
        sec_dr = opts_s.get('drums') or {}                # a section can bring its own beat (metal: blast / breakdown)
        pchoice = {name: rnd_d.choice(sec_dr.get(name) or pats) for name, pats in st['drums'].items()}
        bass_pat = rnd_b.choice(st['bass'])
        chord_pat = opts_s.get('chord_rh') or rnd_c.choice(st['chord_rh'])     # a section can have its own (tango ending)
        riff_pat = None
        if st.get('riffs') and st.get('voicing') == 'power' and S < 0.6:     # metal / punk: verses are riffs
            big = opts_s.get('drop') or sname in BIG_SECTIONS
            if not big or rnd_c.random() < st.get('riff_chorus', 0.3):
                riff_pat = rnd_c.choice(st['riffs'])
        if opts_s.get('riffs') and S < 0.6:                # a section's own riffs (a breakdown's chug pattern)
            riff_pat = rnd_c.choice(opts_s['riffs'])
            if opts_s.get('kick_riff') and kick_name in pchoice:   # breakdown: the kick hits with every chug
                L = max(16, len(riff_pat) // 16 * 16)              # (1.96: over a 2- or 4-bar phrase)
                pchoice[kick_name] = ''.join('X' if c not in '.-' else '.' for c in riff_pat[:L]).ljust(L, '.')
        prev_bass = None
        for b in range(nbars):
            bar = bar0 + b
            beat0 = bar * 4
            chord = prog[(b // cb) % len(prog)]
            nxt = prog[((b + 1) // cb) % len(prog)]
            if opts_s.get('cad') and b >= nbars - 2:             # a written-out perfect cadence closes the section: V - I
                chord, nxt = (4, 0) if b == nbars - 2 else (0, 0)
            last_of_4 = (b % 4 == 3)
            # ---------------- drums
            slices = drumkits.chop_map(st, bar, rnd_d, energy, b) if st.get('break_seq') else None
            for dname, pats in st['drums'].items():
                if dname not in tracks or tracks[dname]['layer'] not in layers:
                    continue
                pat = pchoice[dname]
                if G == 16 and len(pat) > 16 and len(pat) % 16 == 0:    # (1.96) a 2- / 4-bar phrase: this bar's part
                    k_ = len(pat) // 16
                    pat = pat[(b % k_) * 16:(b % k_ + 1) * 16]
                if slices is not None:                      # a break: its 4-bar pattern, straight or chopped
                    pat = drumkits.bar_pattern(st, dname, slices) or pat
                elif dname == kick_name and last_of_4 and len(pats) > 1 and not sec_dr and rnd_d.random() < 0.2 + 0.3 * energy:
                    pat = rnd_d.choice(pats)
                hits = drummer.hat_hits(opts, dname, parse_rhythm(pat))
                used = {s for s, l, c in hits}
                for step, l, c in hits:
                    v = VEL.get(c, 0.8) * rnd_d.uniform(1 - 0.1 * opts.humanize, 1 + 0.05 * opts.humanize)
                    evs.append(Ev(dname, beat0 + step / 4, 0.25, None, v))
                hx = drummer.hat_extra(opts, dname, energy)
                if hx > 0:
                    for step in GS:
                        if step not in used and rnd_d.random() < hx:
                            evs.append(Ev(dname, beat0 + step / 4, 0.25, None, 0.35))
                gr = drummer.ghost_rate(opts, st, energy) if dname in snares[:1] else 0.0
                if gr > 0:
                    for step in GS:
                        if step % 4 != 0 and step not in used and rnd_d.random() < gr:
                            evs.append(Ev(dname, beat0 + step / 4, 0.25, None, 0.28))
            if slices is not None and 'snare' in layers and st.get('break_chop'):
                edit = drumkits.break_edits(st, rnd_d, energy, b, nbars)
                if edit:                                    # a jungle edit on the phrase's last beat(s)
                    frm, hits = edit
                    brk = set(st['break_seq']) | {'lsnare', 'lkick'}
                    evs[:] = [e for e in evs if not (e.track in brk and beat0 + frm <= e.beat < beat0 + 4 and e.track != 'ride')]
                    for pos, dn, v, mod in hits:
                        if dn in tracks:
                            evs.append(Ev(dn, beat0 + pos, 0.25, None, v, mod=mod))
            if st.get('comp_snare') and 'snare' in layers and snares and snares[0] in tracks:
                # jazz comping: sparse, irregular snare accents on off-beats, the odd kick "bomb"
                for step in (2, 6, 7, 10, 11, 14, 15):
                    if rnd_d.random() < 0.10 + 0.12 * energy:
                        evs.append(Ev(snares[0], beat0 + step / 4, 0.25, None, rnd_d.uniform(0.3, 0.6)))
                if kick_name in tracks and rnd_d.random() < 0.12 * energy:
                    evs.append(Ev(kick_name, beat0 + rnd_d.choice((1.5, 2.5, 3.5)), 0.25, None, 0.75))
            if st.get('trap_hats') and not st.get('meter') and 'top' in layers and 'chat' not in st['drums']:
                gen_trap_hats(evs, beat0, rnd_d, energy, bool(st.get('pitch_rolls')))
            if 'snare' in layers and snares and drummer.fill_ok(opts, st, b, nbars, energy, S, rnd_d):
                s = snares[0]
                fills = [[13, 14, 15], [12, 13, 14, 15], [10, 13, 14, 15], [14, 15]] if G == 16 else \
                    [[x * 4 / 3 for x in f] for f in ([9, 10, 11], [8, 9, 10, 11], [10, 11])]
                for k, step in enumerate(rnd_d.choice(fills)):
                    evs.append(Ev(s, beat0 + step / 4, 0.25, None, 0.55 + 0.1 * k))
            if opts_s.get('build'):
                add_build_drums(evs, st, tracks, snares, kick_name, b, nbars, beat0, rnd_d)
            bar_riff = riff_pat
            if riff_pat and G == 16 and len(riff_pat) > 16 and len(riff_pat) % 16 == 0:
                k_ = len(riff_pat) // 16
                bar_riff = riff_pat[(b % k_) * 16:(b % k_ + 1) * 16]
            riff = gen_riff(bar_riff, key, chord, st.get('riff_lo', 40)) if bar_riff else None
            # ---------------- bass
            if 'bass' in layers and 'bass' in tracks and riff:      # the bass doubles the guitar riff an octave down
                for step, l, m, c in riff:
                    m = fold(m - 12, st['bass_lo'])
                    evs.append(Ev('bass', beat0 + step / 4, (0.4 if c == 'p' else l / 4 * 0.92), m, 0.9 if c == 'p' else 1.0))
            elif 'bass' in layers and 'bass' in tracks and not (var == 'bass' and 'lead' in layers):
                lo = st['bass_lo']
                root = fold(key.deg(chord, 2), lo)
                mode = st['bass_mode']
                inst = tracks['bass']['inst']
                if is_808(inst) and mode == 'pattern':
                    mode = '808'
                elif inst == 'acid' and mode == 'pattern':
                    mode = 'acid'
                elif inst in ('wobble', 'riddim', 'dnbwob', 'vowelwob', 'multiwob', 'tablewob', 'chopwob', 'darkwob', 'subwob', 'fmgrowl', 'talkgrowl', 'metalbass',
                              'slowwob', 'yoiwob', 'sweepwob', 'reesewob', 'sleepersub', 'brightwob', 'tearwob', 'divesub', 'pitchgrowl') and mode == 'pattern':
                    mode = 'wobble'
                if getattr(opts, 'bass_rhythm', None) == 'kick' and mode not in ('walk', '808'):
                    mode = 'kick'
                if mode == 'kick':                               # bass locked to the kick drum (no 808 slides)
                    kpat = pchoice.get(kick_name) or (st['drums'].get(kick_name) or ['X...X...X...X...'])[0]
                    hits = [s_ for s_, l, c in parse_rhythm(kpat)] or [0, 8]
                    for i, s_ in enumerate(hits):
                        e_ = hits[i + 1] if i + 1 < len(hits) else 16
                        m = root + (12 if rnd_b.random() < 0.1 else 0)
                        evs.append(Ev('bass', beat0 + s_ / 4, min(e_ - s_, 8) / 4 * 0.85, m, 0.95))
                    prev_bass = root
                elif mode == '808':
                    kpat = pchoice.get(kick_name) or (st['drums'].get(kick_name) or ['X.....X...X.....'])[0]
                    hits = [s for s, l, c in parse_rhythm(kpat)]
                    for i, s in enumerate(hits):
                        e = hits[i + 1] if i + 1 < len(hits) else 16
                        m = root
                        r = rnd_b.random()
                        o8, f8 = st.get('oct808', 0.15), st.get('fifth808', 0.10)   # how often the 808 jumps an octave / to the 5th
                        if r < o8:
                            m = root + 12
                        elif r < o8 + f8:
                            m = fold(key.deg(chord + 4, 2), lo)
                        glide = prev_bass if (prev_bass is not None and prev_bass != m and rnd_b.random() < st.get('glide808', 0.45)) else None
                        warp = None
                        wp = float(st.get('warp_808') or 0)
                        if wp and (e - s) >= st.get('warp_min', 4) and is_808(tracks.get('bass', {}).get('inst', '')) and rnd_b.random() < wp:     # held notes get warped: dives, rises, wobbles, growls
                            warp = rnd_b.choice(['dive', 'dive', 'rise', f'wob:{rnd_b.choice([3, 4, 5, 6, 8])}',
                                                 f'wob:{rnd_b.choice([3, 4, 5, 6, 8])}', 'growl'])
                        evs.append(Ev('bass', beat0 + s / 4, (e - s) / 4 * 0.95, m, 1.0, glide, warp))
                        prev_bass = m
                elif mode == 'acid':
                    half = (b % 2) * 16
                    pat = [x for x in acid_pat if half <= x[0] < half + 16]
                    for i, (s, off, octv, acc, slide) in enumerate(pat):
                        s -= half
                        e = pat[i + 1][0] - half if i + 1 < len(pat) else 16
                        m = key.deg(chord + off, 2) + 12 * octv
                        while m < lo:
                            m += 12
                        legato = i + 1 < len(pat) and pat[i + 1][4]
                        dur = (e - s) / 4 * (1.02 if legato else 0.5)
                        evs.append(Ev('bass', beat0 + s / 4, dur, m, 1.0 if acc else 0.8,
                                      prev_bass if slide else None, 1 if acc else 0))
                        prev_bass = m
                elif mode == 'wobble':
                    pos = 0
                    last_wob = None                              # (2.9.1) (pitch, end step) of the note before
                    while pos < 16:
                        ln = rnd_b.choice(st.get('wobble_lens') or [8, 4, 4, 2, 16]) if pos % 4 == 0 else 2
                        ln = min(ln, 16 - pos)
                        if rnd_b.random() < st.get('wobble_rest', 0.12) and pos > 0:   # (2.9.0) space: the sub alone
                            pos += ln
                            continue
                        rates = (opts_s.get('alt') and st.get('wobble_rates_alt')) or st.get('wobble_rates') or \
                            (([0.25, 0.5, 0.25, 1 / 3, 1 / 6] if energy > 0.3 else [0.5, 0.25]) if (inst in ('dnbwob', 'metalbass') or (st.get('bpm') or (0, 0))[0] >= 160) else
                             [2, 1, 1, 0.5, 0.5, 1 / 3] if energy > 0.3 else [2, 1])   # half-bar / beat / 8th wubs; 16ths are a genre's own choice   # A / B drop switch-up
                        rate = rnd_b.choice(rates)
                        m = rnd_b.choice([root, root, root + 12] if st.get('pedal_sub') else
                                         [root, root, root + 12, fold(key.deg(chord + 4, 2), lo)])
                        ev_ = Ev('bass', beat0 + pos / 4, ln / 4 * 0.97, m, 1.0, None, rate)
                        # (2.9.1) some wobble notes glide in from the note before (straight on from it, no gap)
                        if last_wob and last_wob[1] == pos and 0 < abs(last_wob[0] - m) <= 12 and \
                                rnd_b.random() < st.get('wobble_glide', 0.35):
                            ev_.slide = float(m - last_wob[0])
                        evs.append(ev_)
                        last_wob = (m, pos + ln)
                        pos += ln
                elif mode == 'walk':
                    tgt = fold(key.deg(nxt, 2), lo)
                    cur = root
                    notes = [cur]
                    for q in range(1, 3):
                        cand = [fold(key.deg(chord + i, 2), lo) for i in (2, 4, 1, 3, 5)]
                        cand += [c + 12 for c in cand if c + 12 < lo + 17]
                        cur = min(cand, key=lambda c: abs(c - (cur + (tgt - cur) * 0.5)) + rnd_b.random() * 4)
                        notes.append(cur)
                    notes.append(tgt + rnd_b.choice([-1, 1]))
                    skips = st.get('walk_skips', 0.2) if S < 0.6 else 0
                    for q, m in enumerate(notes):
                        evs.append(Ev('bass', beat0 + q, 0.92, m, 0.95 if q == 0 else 0.82))
                        if q and rnd_b.random() < skips:             # big-band "skip": a triplet ghost pickup into the beat
                            evs[-1].dur = 0.6
                            evs.append(Ev('bass', beat0 + q - 1 / 3, 0.28, notes[q - 1], 0.55))
                else:
                    gate = st.get('bass_gate', 0.92)
                    bp_ = st['bass'][b % len(st['bass'])] if st.get('bass_cycle') else bass_pat   # boogie: up one bar, down the next
                    for step, l, c in parse_rhythm(bp_):
                        if S >= 0.6 and c in 'OFA':                 # simple: the bass stays on the root
                            m = root
                        elif c == 'O':
                            m = root + 12
                        elif c == 'F':
                            m = fold(key.deg(chord + 4, 2), lo)
                        elif c in '3567':                           # boogie chord tones: major 3rd, 5th, 6th, flat 7th
                            m = root + {'3': 4, '5': 7, '6': 9, '7': 10}[c]
                        elif c == 'u':                              # chromatic upper neighbour (a half step up)
                            m = root + 1
                        elif c == 'd':                              # chromatic lower neighbour (a half step down)
                            m = root - 1
                        elif c == 'A':
                            tgt = fold(key.deg(nxt, 2), lo)
                            if rnd_b.random() < 0.4:                     # a step into the next chord - now and then
                                m = tgt + (1 if tgt <= root else -1) * (1 if rnd_b.random() < 0.5 else 2)
                            else:
                                m = rnd_b.choice([fold(key.deg(chord + 4, 2), lo), root + 12, root])
                        else:
                            m = root
                        evs.append(Ev('bass', beat0 + step / 4, l / 4 * gate, m, rnd_b.uniform(0.85, 1.0)))
                    pp = bass_pass(sname_style, st)
                    if pp and nxt != chord and b % cb == cb - 1 and rnd_bp.random() < pp:
                        tgt = fold(key.deg(nxt, 2), lo)        # a scale step leading into the next chord's root
                        side = -1 if tgt >= root else 1
                        m = tgt + (key.deg(nxt + side, 2) - key.deg(nxt, 2))
                        mine = [e for e in evs[-12:] if e.track == 'bass' and beat0 <= e.beat < beat0 + 4]
                        late = [e for e in mine if e.beat >= beat0 + 2.5]
                        if late:
                            late[-1].midi = m
                        elif mine and mine[-1].beat + mine[-1].dur > beat0 + 3:
                            mine[-1].dur = beat0 + 3 - mine[-1].beat
                            evs.append(Ev('bass', beat0 + 3, 0.9 * gate, m, 0.82))
            # ---------------- harmonic colour: secondary dominants and borrowed chords (Classic / Orchestral / pop)
            if b % cb == 0 and sname_style in COLOR_HARMONY and nxt != chord and st.get('voicing') != 'power' and S < 0.3:
                third = (key.deg(chord + 2, 4) - key.deg(chord, 4)) % 12
                pc3 = key.deg(chord + 2, 4) % 12
                pcol = 0.12 + 0.3 * cx + float(st.get('colour_boost') or 0)   # film-score genres colour more
                if (chord - nxt) % 7 == 4 and third == 3 and rnd_hc.random() < pcol + (0.35 if nxt == 0 else 0):
                    harm_alts.append((beat0, beat0 + 4 * cb, pc3, (pc3 + 1) % 12))      # V/x: its 3rd goes up
                elif key.scale_name == 'major' and chord == 3 and nxt == 0 and third == 4 and rnd_hc.random() < pcol:
                    harm_alts.append((beat0, beat0 + 4 * cb, pc3, (pc3 - 1) % 12))      # borrowed minor iv
            # ---------------- chords
            bar_col = chord_color
            if b % cb == 0 and chord_color not in ('sus2', 'sus4', 'add9no3') and rnd_c.random() < 0.15 * (1 - S) \
                    and not (opts_s.get('drop') or sname in BIG_SECTIONS):
                bar_col = rnd_c.choice(['sus4', 'sus2', chord_color])   # a sus colour now and then (chords + pad agree)
            if chord in (st.get('sus_degrees') or ()) and color_fits(key, chord, 'sus4'):
                bar_col = 'sus4'                              # (1.91) the genre voices this chord suspended (V sus4)
            if 'chords' in layers and 'chords' in tracks and riff:
                for step, l, m, c in riff:
                    if c == 'p':                                  # palm-muted chug: root + fifth, choked short
                        for i, n_ in enumerate((m, m + 7)):
                            evs.append(Ev('chords', beat0 + step / 4, min(l, 2) / 4 * 0.6, n_, rnd_c.uniform(0.72, 0.82), mod='pm'))
                    else:
                        for i, n_ in enumerate((m, m + 7, m + 12)):
                            evs.append(Ev('chords', beat0 + step / 4, l / 4 * 0.95, n_, 0.95 if c != 'x' else 0.85,
                                          strum=i * 0.008))
            elif 'chords' in layers and 'chords' in tracks and chord_pat and (b % cb == 0):
                col = bar_col if st.get('voicing', 'close') != 'power' and (chord_size <= 4 or (bar_col == 'sus4' and st.get('sus_degrees'))) else None
                notes = voice_chord(key, chord, chord_size, st.get('chord_center', 62), st.get('voicing', 'close'), col)
                if st.get('voicing', 'close') in ('close', 'open'):
                    notes = lead_voicing(notes, vl_prev.get('chords'), st.get('chord_center', 62),
                                         st.get('voicing', 'close') == 'close')
                    notes = declutter(notes, key, chord, col if col and color_fits(key, chord, col) else None)
                vl_prev['chords'] = notes
                if (opts_s.get('drop') or sname in BIG_SECTIONS) and notes and notes[-1] + 12 <= 96 and st.get('voicing') != 'power':
                    notes = notes + [notes[-1] + 12]                   # choruses / drops open up: top note doubled (once)
                hits = parse_rhythm(chord_pat)
                if S >= 0.5 and hits:                            # simple: one held chord instead of a rhythm
                    hits = [(hits[0][0], 16, hits[0][2])]
                for step, l, c in hits:
                    dur = l / 4 * (cb if l == 16 else 1) * 0.95
                    for i, m in enumerate(notes):
                        vel = rnd_c.uniform(0.95, 1.0) if c == 'X' else rnd_c.uniform(0.75, 0.92)     # 'X' = an accent
                        evs.append(Ev('chords', beat0 + step / 4, dur, m, vel, strum=i * st.get('strum', 0.0),
                                      mod='acc' if c == 'X' else None))
            # ---------------- pad
            if 'pad' in layers and 'pad' in tracks and (b % cb == 0):
                notes = voice_chord(key, chord, min(4, chord_size), st.get('chord_center', 62) - 2, pad_voicing,
                                    bar_col if bar_col in ('triad', '7', 'add9', 'sus2', 'sus4', '6', 'add9no3') else None)
                notes = lead_voicing(notes, vl_prev.get('pad'), st.get('chord_center', 62) - 2, pad_voicing == 'close')
                pcol = bar_col if bar_col in ('sus2', 'sus4') and color_fits(key, chord, bar_col) else None
                notes = declutter(notes, key, chord, pcol)
                vl_prev['pad'] = notes
                if st.get('pad_drone'):                         # pipes / tanpura: one long tonic, whatever the chords do
                    c0 = st.get('chord_center', 62) - 12
                    notes = [c0 + ((key.root - c0) % 12)]
                for m in notes:
                    evs.append(Ev('pad', beat0, 4 * cb * 0.98, m, 0.8))
            # ---------------- arp
            if 'arp' in layers and 'arp' in tracks:
                acol = bar_col if bar_col in ('sus2', 'sus4', 'add9no3') else None   # arps follow a sus chord
                tones = voice_chord(key, chord, 3, 12 * (arp['oct'] + 1) + 4, 'close', acol)
                seq = tones + [tones[0] + 12]
                if arp.get('span') == 2:                         # over two octaves
                    seq = tones + [x + 12 for x in tones] + [tones[0] + 24]
                if arp['mode'] == 'updown':
                    seq = seq + seq[-2:0:-1]
                elif arp['mode'] == 'down':
                    seq = seq[::-1]
                elif arp['mode'] == 'converge':                  # outside in: low, high, next low, next high ...
                    lo_i, hi_i, cv = 0, len(seq) - 1, []
                    while lo_i <= hi_i:
                        cv.append(seq[lo_i])
                        if hi_i != lo_i:
                            cv.append(seq[hi_i])
                        lo_i, hi_i = lo_i + 1, hi_i - 1
                    seq = cv
                elif arp['mode'] == 'pinky':                     # a pedal note under (or over) each chord tone in turn
                    ped = seq[0] if arp.get('pedal', 'low') == 'low' else seq[-1]
                    seq = [x for t_ in seq if t_ != ped for x in (ped, t_)] or seq
                elif arp['mode'] == 'octaves':                   # each chord tone and its octave
                    seq = [x for t_ in tones for x in (t_, t_ + 12)]
                elif arp['mode'] == 'motif':                     # a fixed little order of the chord tones, repeated:
                    seq = [seq[i % len(seq)] for i in arp.get('motif') or (0, 2, 1, 3)]   # hypnotic, its own per song
                elif arp['mode'] == 'roll':                      # Scruggs banjo roll: thumb-index-middle with the high drone string
                    drone = 12 * (arp['oct'] + 1) + 7 + ((key.root - 7) % 12)
                    if drone <= tones[-1]:
                        drone += 12
                    seq = [tones[1], tones[2] if len(tones) > 2 else tones[0] + 12, drone, tones[0], tones[2] if len(tones) > 2 else tones[1],
                           drone, tones[1], drone]
                elif arp['mode'] == 'cascade':                   # hopecore: a two-octave ripple up the chord and back down
                    two = tones + [t + 12 for t in tones] + [tones[0] + 24]
                    seq = two + two[-2:0:-1]
                elif arp['mode'] == 'alberti':                   # Classical-era accompaniment: low - high - middle - high
                    lo_, mid_, hi_ = tones[0] - 12, tones[1] - 12 if len(tones) > 2 else tones[0] - 5, tones[-1] - 12
                    seq = [lo_, hi_, mid_, hi_]
                rate = arp['rate']
                u = 16 / G                                       # a grid step in 16ths (4/3 in triple meters)
                if arp.get('rh'):                                # a written figure: montuno, highlife guitar, guajeo...
                    rh = arp['rh'] if isinstance(arp['rh'], str) else arp['rh'][b % len(arp['rh'])]
                    if arp['mode'] == 'montuno':                 # salsa piano: chord tones in octaves, anticipating the clave
                        seq = [tones[0], tones[1], tones[2], tones[1]] if len(tones) > 2 else seq
                    for k, (step, l, c) in enumerate(parse_rhythm(rh)):
                        m = rnd_c.choice(seq) if arp['mode'] == 'random' else seq[k % len(seq)]
                        acc = c == 'X'
                        vel = (0.95 if acc else 0.78) * rnd_c.uniform(0.92, 1.0)
                        evs.append(Ev('arp', beat0 + step * u / 4, max(0.2, l * u / 4 * 0.85), m, vel))
                        if arp['mode'] == 'montuno':
                            evs.append(Ev('arp', beat0 + step * u / 4, max(0.2, l * u / 4 * 0.85), m - 12, vel * 0.85))
                if arp['mode'] == 'tap':                         # math rock: tapped loops drifting over the bar line
                    evs += tap_bar(key, tones, beat0, b, si, st.setdefault('_tap', {}), rnd_c,
                                   0.85 if not (opts_s.get('drop') or sname in BIG_SECTIONS) else 1.0)
                    continue
                if arp['mode'] == 'mallet':                      # mallet figures (rolls, trills, hops, runs, rests)
                    big = bool(opts_s.get('drop') or sname in BIG_SECTIONS)
                    evs += mallet_bar(key, tones, beat0, b, sname, si, big, rate, arp.get('rest', 0.18),
                                      st.setdefault('_mallet', {}), rnd_c)
                    continue
                per_beat = max(1, int(round(4 / rate))) if arp.get('beat_lock') else 0
                for k in range(0 if arp.get('rh') else int(G / rate)):
                    if per_beat:                                 # locked to the beat: every beat starts the figure again
                        j, bt = k % per_beat, k // per_beat      # from the bottom (up on one beat, down the next), the
                        run = seq[:per_beat] if len(seq) >= per_beat else (seq * per_beat)[:per_beat]
                        m = run[j] if bt % 2 == 0 else run[per_beat - 1 - j]
                        vel = (1.0 if j == 0 else 0.86 if j * 2 == per_beat else 0.72 if j % 2 == 0 else 0.6)
                        evs.append(Ev('arp', beat0 + k * rate * u / 4, rate * u / 4 * 0.8, m, vel * rnd_c.uniform(0.96, 1.0)))
                        continue                                 # downbeat accented, the off-beat half a step down
                    if arp.get('prob') and rnd_c.random() > arp['prob']:
                        continue
                    gmask = arp.get('gate_rh')
                    if gmask and gmask[int(round(k * rate * u)) % len(gmask)] == '.':   # the song's own gate rhythm
                        continue
                    m = rnd_c.choice(seq) if arp['mode'] == 'random' else seq[k % len(seq)]
                    evs.append(Ev('arp', beat0 + k * rate * u / 4, rate * u / 4 * 0.8, m,
                                  (0.95 if (k % 4 == 0 if G == 16 else (k * rate) % 3 == 0) else 0.75) * rnd_c.uniform(0.9, 1.0)))
        # ---------------- lead
        if 'lead' in layers and 'lead' in tracks:
            soft_lead = 0.75 if sname in ('break', 'bridge', 'C', 'calm') else (0.8 if hook_verse else 1.0)
            reps = int(math.ceil(nbars / ph))
            src_mel = vary_melody(mel, var, key) if var in ('dim', 'aug') else mel
            n0 = len(evs)
            for r in range(reps):
                for (bt, du, m, v) in src_mel:
                    beat = sec_start + r * ph * 4 + bt
                    if beat < sec_start + nbars * 4 - 0.01:
                        if opts_s.get('build') and beat >= sec_start + nbars * 4 - 2:
                            continue
                        evs.append(Ev('lead', beat, du, m, v * soft_lead))
            new = [e for e in evs[n0:] if e.track == 'lead']
            if var == 'bass' and 'bass' in tracks and new:      # the theme sinks to the celli / basses; the top rests
                lo = st['bass_lo']
                for e in new:
                    e.track = 'bass'
                    e.midi = e.midi - 24
                    while e.midi < lo:
                        e.midi += 12
                    while e.midi > lo + 22:
                        e.midi -= 12
            elif var == 'oct':                                  # tutti statement: the theme doubled an octave down
                evs.extend(Ev('lead', e.beat, e.dur, e.midi - 12, e.vel * 0.8) for e in new)
            if opts_s.get('cad') and new:                       # the melody comes home on the tonic and holds
                last = max(new, key=lambda e: e.beat)
                tonic = [m for m in range(last.midi - 7, last.midi + 8) if (m - key.root) % 12 == 0]
                if tonic:
                    last.midi = min(tonic, key=lambda m: abs(m - last.midi))
                    last.dur = max(last.dur, sec_start + nbars * 4 - last.beat - 0.1)
        if opts_s.get('build'):
            add_build_fx(fx, st.get('build_style', 'roll'), sec_start, nbars,
                         riser=st.get('build_home') not in ('lift', 'swell', 'pause') and st.get('category') == 'Electronic'
                         and (getattr(opts, 'builds', 'auto') or 'auto') == 'auto',
                         rnd=random.Random(f'{opts.seed}-bfx-{sec_start}'))
        if opts_s.get('drop') and (getattr(opts, 'transition_fx', 'auto') or 'auto') in ('auto', 'fewer'):
            if rnd_d.random() < (0.35 if getattr(opts, 'transition_fx', 'auto') == 'fewer' else 0.6):
                fx.append(('impact', sec_start, 0))
            elif rnd_d.random() < 0.4:
                fx.append(('downlift', sec_start, 4))
        if opts_s.get('drop'):
            fx.append(('crash', sec_start, 0))
        if opts_s.get('crash'):
            fx.append(('crash', sec_start, 0))
        if opts_s.get('filter_in'):
            fx.append(('lpsweep', sec_start, nbars * 4))
        if opts_s.get('fade'):
            fx.append(('fade', sec_start, nbars * 4))
        bar0 += nbars

    if 'counter' in tracks:
        evs += gen_counter(evs, key, sections, cb, st, prng('melody', 2 + 90))
    apply_harm_alts(evs, tracks, harm_alts)
    for (b0, b1, vs) in variations:
        evs = apply_variation(evs, b0, b1, vs, key, st, tracks)
    evs += gen_vocal(key, sections, cb, st, random.Random(opts.seed * 7 + 41))
    if modulate:
        big = [s_ for s_ in sections if s_['opts'].get('drop') or s_['name'] in ('chorus', 'hook')]
        if len(big) >= 2:
            last = big[-1]
            k0, k1 = last['bar'] * 4, (last['bar'] + last['bars']) * 4
            outro_end = sections[-1]['bar'] * 4 + sections[-1]['bars'] * 4 if sections[-1]['opts'].get('fade') else k1
            from .instruments import DRUMS as _D
            shift = rnd.choice([1, 2])
            for e in evs:
                if k0 <= e.beat < outro_end and e.midi is not None and tracks.get(e.track, {}).get('inst') not in _D:
                    e.midi += shift
                    if e.glide is not None:
                        e.glide += shift
            last['key_change'] = shift
    vocal = [e for e in evs if e.track == 'vocal']
    sung = getattr(opts, 'vocals', None) in ('ooh', 'aah', 'lyrics')
    if sung and not vocal:                               # genres without verse / chorus names: the singer takes the melody
        lead = sorted((e for e in evs if e.track == 'lead' and e.midi is not None), key=lambda e: e.beat)
        if lead:
            mid = sorted(e.midi for e in lead)[len(lead) // 2]
            shift = 12 * round((66 - mid) / 12)          # into a comfortable singing range around F4
            vocal = [Ev('vocal', e.beat, e.dur, e.midi + shift, e.vel) for e in lead]
            evs += vocal
    if sung and vocal:
        t = dict(name='vocal', layer='lead', inst='sung', pan=0.0, rev=0.35, dly=0.12, sc=0.0, db=-15, hp=120, drive=None,
                 p=dict(style=opts.vocals, voice=getattr(opts, 'voice', 'female') or 'female', lyrics=getattr(opts, 'lyrics', '') or ''))
        st['tracks'].append(t)
        tracks['vocal'] = t
    elif getattr(opts, 'vocal_guide', False) and vocal:
        t = dict(name='vocal', layer='lead', inst='vox', pan=0.0, rev=0.3, dly=0.15, sc=0.0, db=-20, hp=None, drive=None, p={})
        st['tracks'].append(t)
        tracks['vocal'] = t
    else:
        evs[:] = [e for e in evs if e.track != 'vocal']
    if S > 0:
        from .instruments import DRUMS as _DR
        rs = random.Random(opts.seed * 61 + 5)
        def busy(e):
            t = tracks.get(e.track, {})
            if t.get('inst') not in _DR:
                return False
            if e.vel < 0.6 and rs.random() < S:                       # ghost notes
                return True
            q = e.beat * 4                                             # 16th-note hats / shakers -> 8ths
            return t.get('layer') == 'top' and abs(q - round(q)) < 1e-6 and int(round(q)) % 2 == 1 and rs.random() < S
        evs[:] = [e for e in evs if not busy(e)]
    lock_bass_to_kick(evs, tracks, st)
    if st.get('bass_mode') == '808':                     # 808s live in the sub register (E1 ... A2), slides included
        for e in evs:
            if tracks.get(e.track, {}).get('layer') == 'bass' and e.midi is not None and e.midi > 45:
                e.midi -= 12
                if e.glide is not None:
                    e.glide -= 12
    add_transitions(sections, evs, fx, tracks, st, opts)
    if (getattr(opts, 'transition_fx', 'auto') or 'auto') in ('fills', 'off'):   # no risers / cymbal swells / impacts
        fx[:] = [f for f in fx if f[0] not in FX_SOUNDS]
    elif st.get('plain_drops'):                          # the genre's drops just land: no risers, swells or impacts
        keep = {'crash'} | set(st.get('keep_fx') or [])     # (bass-warp keeps its tape stops)
        fx[:] = [f for f in fx if f[0] not in FX_SOUNDS or f[0] in keep]
    bar0 = apply_ending(sections, evs, fx, tracks, st, opts, key, chord_size, chord_color, bar0)
    if st.get('no_fx_sounds'):                          # surf / TV-theme bands: no cymbal FX, swells or sweeps at all
        fx[:] = [f for f in fx if f[0] not in FX_SOUNDS and f[0] not in ('lpsweep', 'hpsweep')]
    elif natural_band(st):                               # live bands: a crash on the downbeat, never studio swells / sweeps
        fx[:] = [f for f in fx if (f[0] not in FX_SOUNDS or f[0] == 'crash') and f[0] not in ('lpsweep', 'hpsweep')]
    hold_slow_chords(evs, tracks, st, bpm)
    legato_bass(evs, tracks)
    sync_drones(evs, tracks, bpm)
    shape_dynamics(evs, tracks, sections, st)
    in_evs = {id(e) for e in evs}
    st['tuned_notes'] = fix_clashes(evs + [v for v in vocal if id(v) not in in_evs], {**tracks, 'vocal': tracks.get('vocal') or
                                    dict(layer='lead')}, key, st, sections)
    if st.get('slides'):                                 # country: notes slide up into place (steel / fiddle / Telecaster)
        add_slides(evs, tracks, st, key, random.Random(opts.seed * 41 + 3))
    orn = ornament_amount(st, opts)
    if orn > 0:                                          # Indian music: meend, gamak and andolan on bendable instruments
        add_ornaments(evs, tracks, key, orn, random.Random(opts.seed * 43 + 7))
    maqam_quarters(evs, tracks, key)                     # Arabic maqamat: half-flat notes a quarter tone down
    if st.get('lead_glide'):                             # G-funk / talk-box: the lead slides from note to note
        prev = None
        for e in sorted((e for e in evs if e.track == 'lead' and e.midi is not None), key=lambda e: e.beat):
            if prev is not None and e.beat - (prev.beat + prev.dur) < 0.3 and e.midi != prev.midi and e.glide is None:
                e.glide = prev.midi
            prev = e
    if st.get('bass_glide'):                             # (1.97) wave / trap: the held 808 slides into its next note
        rg = random.Random(opts.seed * 47 + 5)
        prev = None
        for e in sorted((e for e in evs if e.track == 'bass' and e.midi is not None), key=lambda e: e.beat):
            if prev is not None and e.beat - (prev.beat + prev.dur) < 0.3 and e.midi != prev.midi and e.glide is None \
                    and rg.random() < float(st['bass_glide']):
                e.glide = prev.midi
            prev = e
    if st.get('solos'):                                  # bluegrass / synthwave: instruments take turns at the solos
        rotate_solos(evs, tracks, sections, st)
    if st.get('g_run'):
        add_g_runs(evs, tracks, sections, key)
    if st.get('eno_loops'):
        eno_loops(evs, st['eno_loops'], bar0 * 4)
    if st.get('lead_runs'):                              # liquid DnB: 16th-note arpeggio run-ups into long lead notes
        add_lead_runs(evs, key, st['lead_runs'], random.Random(opts.seed * 61 + 7))
    if any(t.get('chops') for t in tracks.values()):
        chop_samples(evs, tracks, random.Random(opts.seed * 53 + 1))
    if st.get('switchups'):                              # switch-up 808: no two bars of the 808 alike
        bar_switchups(evs, tracks, sections, st, random.Random(opts.seed * 67 + 5))
    if getattr(opts, 'midi_parts', None):               # (1.87) your MIDI file's melody / chords / bass, in this song
        import_midi_parts(evs, sections, st, opts, key, tracks)
    from . import evolve as _ev                          # (1.85) songs that develop instead of looping (before the
    from .styles import POOLS as POOLS_                  # layers copy the notes, so a doubled lead climbs with it)
    st['evolved'] = _ev.evolve_drops(evs, sections, st, opts, tracks)
    if (st.get('name') or opts.style) in CLUB_COHERENT and (st.get('name') or opts.style) not in CLUB_TRANCE \
            and getattr(opts, 'call_response', 'auto') == 'auto':
        st['no_answer'] = True                           # (1.94) house / techno: no second sound answering the hook
    _ans = None if st.get('no_answer') else _ev.call_response(evs, sections, st, opts, tracks,
                             [x for r_ in ('lead', 'arp') for x in (POOLS_.get(opts.style, {}).get(r_) or [])])
    if _ans:
        tracks['answer'] = _ans
        st['tracks'].append(_ans)
    st['bar_variations'] = _ev.bar_variation(evs, sections, st, opts)
    st['extra_arps'] = _ev.extra_arps(evs, sections, st, opts, tracks)   # (1.91) background arpeggio layers
    st['bass_stutters'] = _ev.bass_stutter(evs, st)      # (1.92.2) long bass notes enter with a triplet stutter
    st['polymeter_len'] = _ev.polymeter(evs, sections, st, opts, tracks)   # (1.93) techno: 3 / 5 / 7-step loops against 4/4
    st['phrase_moves'] = _ev.phrase_evolution(evs, sections, st, opts, tracks, CLUB_COHERENT, CLUB_TRANCE)   # (1.94)
    st['drop_space'] = _ev.drop_space(evs, sections, st, opts, tracks, CLUB_DUBSTEP - {'melodic_dubstep', 'chillstep'})   # (1.95.1)
    evs += double_layers(evs, tracks)                    # layers copy the tuned notes
    switch_sections(evs, tracks, sections)                # verses / choruses / breaks on different instruments
    _sw = _ev.structure_moves(evs, sections, st, opts, tracks, POOLS_.get(opts.style, {}).get('bass') or [], fx)
    if _sw:                                               # (1.91) layered intros / outros, switch-up drops
        tracks[_sw['name']] = _sw
        st['tracks'].append(_sw)
    st['dyn_moves'] = _ev.section_dynamics(evs, sections, st, opts, tracks)   # (1.90) real section dynamics
    st['fills'] = _ev.genre_fills(evs, fx, sections, st, opts, tracks, opts.seed)   # (1.90) rewinds / stops / rolls
    if not st.get('composer'):
        fit_registers(evs, tracks)                        # each part in its instrument's sweet spot
    apply_octaves(evs, tracks, getattr(opts, 'octaves', None))
    for sec in sections:                                  # bass-warp switch-ups: the 808 jumps up, the sub drops out
        bm = sec['opts'].get('bass_mod')                     # ... or a whole section of distorted, growling 808
        if bm and str(tracks.get('bass', {}).get('inst', '')).startswith('808'):
            b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
            for e in evs:
                if b0 <= e.beat < b1 and e.track == 'bass' and not (st.get('switchups') and e.mod):
                    e.mod = bm
        up = int(sec['opts'].get('bass_up') or 0)              # target MIDI note (e.g. 40 = E2)
        if up:
            b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
            st.setdefault('_up_ranges', []).append((b0, b1))
            ins = [e for e in evs if b0 <= e.beat < b1 and tracks.get(e.track, {}).get('layer') == 'bass' and e.midi is not None]
            k0 = 12 * max(0, -((min(e.midi for e in ins) - up) // 12)) if ins and st.get('switchups') else None
            for e in ins:                                    # (switch-up genres move the whole section, so leaps stay leaps)
                k = k0 if k0 is not None else 12 * max(0, -((e.midi - up) // 12))   # up whole octaves until it reaches the target register
                e.midi += k
                if e.glide is not None:
                    e.glide += k
    if st.get('hi_bass'):                                # the 808 stays down low; when it leaps up / is raised it hands
        hand_up_bass(evs, tracks, st, opts)              # those notes to a mid-bass (reese / growl / FM) - no squeaky 808
    for e in evs:                                        # a high 808 sounds far louder than a low one at the same level
        t = tracks.get(e.track, {})                      # (the ear is much more sensitive at 100-200 Hz than at 40 Hz):
        if t.get('layer') == 'bass' and is_808(t.get('inst', '')) and e.midi is not None and e.midi > 33:
            e.vel *= 10 ** (-min(9.0, 0.45 * (e.midi - 33)) / 20)   # notes leaping up or raised to E2+ are turned down
    switch_basses(evs, tracks, sections, st)              # brostep / neuro: several bass timbres trade bars in the drop
    if st.get('celtic_orn'):                             # (2.4.1) Celtic ornaments: cuts / taps / rolls, pipe gracenotes
        from .celtic import ornament_pass
        if getattr(opts, 'ornaments', None) is not None:
            st['_orn_amount'] = opts.ornaments
        ornament_pass(evs, tracks, sections, st, bpm, opts.seed, tonic=key.root)
    if st.get('euphoric'):                               # (2.3) euphoric trance: chord-aware lead harmony, piano breakdown
        from .trance2 import euphoric_pass
        euphoric_pass(evs, tracks, sections, st)
    if st.get('scene_switch'):                           # (2.1) switch-up bass: one rhythm, a new scene every section
        from .switchup import scene_switch
        scene_switch(evs, tracks, sections, st, opts.seed)
    if st.get('granular'):                               # IDM / drill & bass: the break resequenced hit by hit, every bar
        granular_breaks(evs, tracks, sections, float(st['granular']), random.Random(opts.seed * 97 + 5))
    _gname = st.get('name') or opts.style
    if st.get('modular') or _gname in MODULAR_GENRES:
        modular_drums(evs, tracks, sections, float(st.get('modular') or MODULAR_GENRES[_gname]),
                      random.Random(f'{opts.seed}-{_gname}-modular'))
    if st.get('calm_lead'):                              # ... and the melody sits and breathes over it: long notes only
        calm = float(st['calm_lead'])
        for name in [n for n, t in tracks.items() if t.get('layer') == 'lead' and n != 'vocal' and not t.get('double_of')]:
            ln = sorted((e for e in evs if e.track == name and e.midi is not None), key=lambda e: e.beat)
            keep, last = [], None
            for e in ln:
                if last is None or e.beat - last.beat >= calm or e.beat // 4 != last.beat // 4 and e.beat % 4 == 0:
                    keep.append(e)
                    last = e
            kid = {id(e) for e in keep}
            evs[:] = [e for e in evs if not (e.track == name and e.midi is not None and id(e) not in kid)]
            for a, nx in zip(keep, keep[1:] + [None]):
                gap = (nx.beat - a.beat) if nx is not None else 4.0
                a.dur = max(a.dur, min(4.0, gap) * 0.95)
    _late = fix_clashes(evs, tracks, key, st, sections)  # (2.8) late stages (calm leads, answers, extra arps, layer
    if _late:                                            # copies) can land held notes on a rub - tune those too
        st['tuned_notes'] = (st.get('tuned_notes') or 0) + _late
    if st.get('dj_fx'):                                  # DJ edits: pitched hat moves, down / up-tuned lead notes, slowdowns
        dj_effects(evs, fx, tracks, sections, float(st['dj_fx']), random.Random(opts.seed * 73 + 11), st.get('dj_slow'))
    if st.get('chopped'):                                # chopped & screwed: the DJ catches a beat twice
        screw_chops(evs, sections, float(st['chopped']), random.Random(opts.seed * 71 + 9))
    if getattr(opts, 'vox_sample', None):                # your voice sample, chopped into the song
        voice_sample_part(evs, tracks, st, sections, opts, bpm, random.Random(opts.seed * 79 + 13))
    for name, t in tracks.items():                       # any part of this song, picked by its own name in the editor
        pick = (opts.instruments or {}).get(name)
        is_drum = t['layer'] in ('kick', 'snare', 'top')
        if not pick or t.get('user_pick') or (name == t['layer'] and not st.get('composer') and not is_drum):
            continue
        if pick == 'off':
            t['off'] = True
        elif is_drum and pick in DRUMS:                   # a different drum sound for this drum part (editor)
            t['inst'], t['user_pick'] = pick, True
        elif t['layer'] in MELODIC_ROLES and isinstance(pick, str) and (pick in INSTRUMENTS or pick.startswith(('user:', 'vst:', 'sf:', 'real:'))):
            t['fallback'], t['inst'], t['user_pick'] = t['inst'], pick, True
    before = {n: sum(1 for e in evs if e.track == n) for n in tracks}
    hold_slow_chords(evs, tracks, st, bpm)               # again: switched / re-picked parts may now be on a pad sound
    held = {n for n in tracks if sum(1 for e in evs if e.track == n) != before[n]}
    relayer = {n for n, t in tracks.items() if t.get('double_of') in held}
    if relayer:                                          # a held part's layers follow it again
        evs[:] = [e for e in evs if e.track not in relayer]
        evs += [e for e in double_layers(evs, {n: tracks[n] for n in relayer})]
    off = {n for n, t in tracks.items() if t.get('off')} if not st.get('composer') else set()
    if off:                                              # extra parts switched off in the Sound panel
        evs = [e for e in evs if e.track not in off]
    if muted:                                            # parts you switched off: everything else stays note-for-note
        evs = [e for e in evs if tracks.get(e.track, {}).get('layer') not in muted]
    if getattr(opts, 'note_edits', None):                 # your note edits (song editor > Notes & volume)
        evs = apply_note_edits(evs, opts.note_edits, tracks)
    bar_steps = cut_meters(evs, fx, sections, st, random.Random(opts.seed * 101 + 7)) if st.get('cut_meters') else None
    sname ='+'.join([opts.style] + [b for b in (opts.blend or []) if b != opts.style])
    expr = expression_curves(evs, tracks, sections, fx, bar0)
    try:                                                 # effects on the parts: the genre's picks and yours
        from . import part_effects as _pfx
        picked_fx = _pfx.apply(st, tracks, opts, opts.style)
    except Exception:
        picked_fx = {}
    song = dict(style=sname, seed=opts.seed, bpm=bpm, key=key, events=evs, sections=sections, fx=fx, expr=expr,
                part_effects=picked_fx, drum_picks=st.get('drum_picks') or {},
                meter=st.get('meter') or '4/4', harm_alts=len(harm_alts),
                total_bars=bar0, prog_main=prog_main, prog_alt=prog_alt, prog_verse=prog_verse, chord_color=chord_color,
                modulate=modulate, st=st, opts=opts, user_opts=user_opts, vocal=vocal,
                energy=energy)
    if (st.get('sec_tempo') or any((sec.get('opts') or {}).get('tempo', 1.0) != 1.0 for sec in sections)) and bar0 > 0:
        tm = []                                          # tempo steps by section (klezmer: a slow, free doina, then the
        for sec in sections:                             # dance; metal: half-time slams and double-time blasts)
            f = (sec.get('opts') or {}).get('tempo') or (st.get('sec_tempo') or {}).get(sec['name'], 1.0)
            tm += [(sec['bar'] * 4.0, bpm * f), ((sec['bar'] + sec['bars']) * 4.0 - 0.01, bpm * f)]
        song['tempo_map'] = tm
    elif bar_steps:                                      # odd meters: a 7/8 bar is a 4/4 bar cut short and played faster
        tm = []
        for b in range(bar0):
            f = 16.0 / bar_steps.get(b, 16)
            tm += [(b * 4.0, bpm * f), (b * 4.0 + 3.999, bpm * f)]
        song['tempo_map'] = tm
        song['meters'] = {b: n for b, n in bar_steps.items() if n != 16}
    elif st.get('accel') and bar0 > 0:                     # kirtan: starts slow and speeds up chant by chant (a laya build)
        f0, f1 = st['accel']
        tm = [(sec['bar'] * 4.0, bpm * (f0 + (f1 - f0) * (sec['bar'] / bar0) ** 1.4)) for sec in sections]
        tm.append((bar0 * 4.0, bpm * f1))
        song['tempo_map'] = tm
    return song


# ----------------------------------------------------------------------------- 1.10: harmony colour, bass, counter, dynamics
# styles whose harmony uses secondary dominants and borrowed chords (modal / riff genres keep their own sound)
COLOR_HARMONY = {
    'pop', 'jazz', 'bossa_nova', 'city_pop', 'disco', 'folk', 'holiday', 'western', 'chamber_pop', 'soul_ballad', 'celtic_jig',
    'cinematic', 'orchestral', 'film_piano', 'adventure', 'tension', 'neoclassical', 'chamber', 'baroque', 'fantasy_rpg',
    'waltz', 'synthpop', 'eurodance', 'future_bass', 'progressive_house', 'trance', 'downtempo', 'vaporwave', 'lofi', 'boombap',
    'hybrid_trailer', 'orchestral_hiphop', 'teen_pop', 'soft_rock', 'luxury_rap', 'uplifting_trance', 'gospel', 'rnb', 'motown', 'swing', 'country', 'tango', 'salsa', 'kpop', 'ska',
    'indie_rock', 'bluegrass', 'christmas_joyful', 'christmas_mischief', 'christmas_magic'}
# how often the bass steps into the next chord on the last beat (styles with a moving, song-like bass)
BASS_PASS = {'math_rock': 0.45, 'idm_jungle_theme': 0.5, 'drill_space': 0.6, 'pop': 0.35, 'folk': 0.5, 'holiday': 0.5, 'western': 0.45, 'chamber_pop': 0.45, 'baroque': 0.6, 'chamber': 0.55,
             'neoclassical': 0.3, 'orchestral': 0.4, 'film_piano': 0.3, 'fantasy_rpg': 0.4, 'adventure': 0.3, 'reggae': 0.3,
             'rock': 0.25, 'disco': 0.2, 'city_pop': 0.3, 'soul_ballad': 0.5, 'celtic_jig': 0.4, 'waltz': 0.45, 'bossa_nova': 0.35,
             'synthpop': 0.2, 'eurodance': 0.15, 'downtempo': 0.25, 'lofi': 0.25, 'boombap': 0.2, 'symphonic_metal': 0.2,
             'country': 0.5, 'bluegrass': 0.6, 'motown': 0.4, 'gospel': 0.4, 'ska': 0.3, 'tango': 0.3, 'indie_rock': 0.3,
             'cumbia': 0.25, 'kpop': 0.2, 'jam_band': 0.5, 'soft_rock': 0.4, 'teen_pop': 0.2}
def import_midi_parts(evs, sections, st, opts, key, tracks):
    """Replace a part's notes with the ones imported from a MIDI file, wherever the part plays: the imported phrase is
    repeated through each section, moved into the song's key (by the nearest interval) and, for the bass, into the
    genre's bass register."""
    mp = opts.midi_parts or {}
    shift = ((key.root - int(mp.get('root', key.root))) + 6) % 12 - 6
    for role in ('lead', 'chords', 'bass'):
        notes = mp.get(role)
        if not notes or role not in tracks:
            continue
        end = max(float(n[0]) + float(n[1]) for n in notes)
        P = max(4.0, math.ceil(end / 4 - 1e-6) * 4.0)          # whole bars
        lo = st.get('bass_lo', 28)
        for x in sections:
            a, b = x['bar'] * 4, (x['bar'] + x['bars']) * 4
            mine = [e for e in evs if e.track == role and a <= e.beat < b]
            if not mine:
                continue
            for e in mine:
                evs.remove(e)
            t = a
            while t < b:
                for nb, nl, nm, nv in notes:
                    if t + nb < b:
                        m = int(nm) + shift
                        if role == 'bass':
                            while m < lo:
                                m += 12
                            while m > lo + 19:
                                m -= 12
                        evs.append(Ev(role, t + float(nb), min(float(nl), b - (t + float(nb))), m, float(nv)))
                t += P


BASS_PASS_GROUP = {'House & Disco': 0.25, 'Funk, Soul & Disco': 0.4, 'Drum & Bass, Breaks & Hard': 0.15,
                   'Techno & Trance': 0.08, 'Pop, R&B & Hopecore': 0.2, 'Chill, Lo-fi & Ambient': 0.2}


def bass_pass(style, st):
    """(1.85) How often the bass steps into the next chord's root: the genre's own value, else its family's (808s,
    acid lines and riff basses keep their written line)."""
    if style in BASS_PASS:
        return BASS_PASS[style]
    if is_808(next((t['inst'] for t in st.get('tracks', []) if t['name'] == 'bass'), '')) or st.get('riff_locked'):
        return 0.0
    from .genre_groups import group_of
    return BASS_PASS_GROUP.get(group_of(style), 0.0)


# genres that get a counter-melody (when the genre decides): the instruments that play it, likeliest first
COUNTER_STYLES = {
    'festive_cinematic': ['horn', 'cello', 'clarinet'],
    'orchestral': ['cello', 'horn', 'clarinet', 'flute'], 'cinematic': ['horn', 'cello', 'strings'],
    'film_piano': ['cello', 'violin', 'oboe'], 'adventure': ['horn', 'strings', 'cello'], 'tension': ['cello', 'clarinet'],
    'neoclassical': ['cello', 'violin'], 'chamber': ['cello', 'sf:viola', 'violin'], 'baroque': ['oboe', 'violin', 'flute'],
    'fantasy_rpg': ['clarinet', 'oboe', 'horn', 'cello'], 'hybrid_trailer': ['horn', 'cello'], 'waltz': ['cello', 'clarinet', 'horn'],
    'chamber_pop': ['cello', 'horn', 'flute', 'strings'], 'holiday': ['clarinet', 'strings', 'flute', 'horn'],
    'western': ['cello', 'strings', 'flute'], 'folk': ['violin', 'flute', 'cello'], 'pop': ['strings', 'cello', 'pluck'],
    'soul_ballad': ['strings', 'organ', 'sax'], 'celtic_jig': ['flute', 'violin'], 'symphonic_metal': ['strings', 'choir'],
    'orchestral_hiphop': ['cello', 'horn'], 'city_pop': ['brass', 'strings'], 'disco': ['strings'], 'jazz': ['sax', 'brass'],
    'bossa_nova': ['flute', 'strings'], 'gospel': ['organ', 'choir'], 'motown': ['strings', 'brass'],
    'country': ['pedalsteel', 'violin', 'twang', 'harmonica'], 'modern_country': ['pedalsteel', 'twang'], 'country_waltz': ['pedalsteel', 'violin'],
    'outlaw_country': ['harmonica', 'twang'], 'western_swing': ['pedalsteel', 'violin'],
    'smooth_jazz': ['strings', 'acguitar'], 'smooth_funk': ['brass', 'vibes'], 'quiet_storm': ['acguitar', 'strings'], 'swing': ['brass', 'clarinet'], 'tango': ['cello', 'violin', 'accordion'],
    'kpop': ['strings', 'pluck', 'bell'], 'teen_pop': ['strings', 'pluck', 'vox'], 'luxury_rap': ['horn', 'strings', 'choir'],
    'soft_rock': ['organ', 'epiano', 'guitar'], 'jam_band': ['organ', 'piano'], 'uplifting_trance': ['pluck_saw', 'strings'], 'rnb': ['strings', 'guitar'], 'bluegrass': ['banjo', 'guitar'], 'salsa': ['flute', 'violin'],
}


# mastering presets: settings laid over the genre's master
MASTER_PRESETS = {
    'streaming': dict(lufs=-14.0),
    'balanced': dict(lufs=-10.0),
    'club': dict(lufs=-8.0, max_gr=4.0),
    'radio': dict(lufs=-9.0, glue_thresh=-16.0, clip=1.0, max_gr=4.0),        # dense and even, for small speakers
    'vinyl': dict(lufs=-12.0, air=-1.5, clip=0.0, max_gr=2.0, width=0.85, dyn_eq=1.0),   # mono-safe, gentle highs
    'film': dict(lufs=-18.0, gentle=True, clip=0.0, max_gr=1.0, integrated=True),        # a stem for picture: no squeeze
}


def apply_note_edits(evs, edits, tracks):
    """Your edits from the song editor's note timeline, applied on top of the composed song (so a re-render with the
    same settings keeps them): edits = {'del': [[track, beat, midi], ...], 'add': [[track, beat, dur, midi, vel], ...]}.
    A deleted note is matched by its track, start (to 1/1000 of a beat) and pitch (drum hits: pitch null)."""
    from .theory import Ev
    gone = set()
    for d in (edits.get('del') or []):
        try:
            gone.add((str(d[0]), round(float(d[1]), 3), None if d[2] is None else int(d[2])))
        except (TypeError, ValueError, IndexError):
            continue
    out = [e for e in evs if (e.track, round(float(e.beat), 3), None if e.midi is None else int(e.midi)) not in gone]
    for a in (edits.get('add') or []):
        try:
            tr, beat, dur, midi, vel = str(a[0]), float(a[1]), float(a[2]), a[3], float(a[4])
        except (TypeError, ValueError, IndexError):
            continue
        if tr not in tracks or beat < 0 or not (0.01 <= dur <= 64):
            continue
        out.append(Ev(tr, beat, dur, None if midi is None else max(0, min(127, int(midi))), max(0.05, min(1.0, vel))))
    out.sort(key=lambda e: e.beat)
    return out


SUB_BASSES = ('808', '808dist', '808long', '808punch', 'sinebass', 'deepsub', 'sleepersub', 'divesub', 'logdrum', 'chipbass', 'deepbass', 'splitbass', 'rumble', 'subwob')

EXTRA_FOLLOWS = ('lead', 'counter', 'chords', 'pad', 'arp', 'bass')


def add_extra_parts(st, opts):
    """Extra instruments on top of the genre's parts - a celesta and glockenspiel doubling the melody an octave or two
    up, horns on the counter-melody, a choir on the chords, pizzicato on the bass: the way an orchestrator thickens a
    line. Each one plays exactly the notes of the part it follows (octave-shifted), at its own level and pan.
    'counter' adds the counter-melody itself when the song doesn't have one."""
    from .instruments import INSTRUMENTS
    ex = list(getattr(opts, 'extra_parts', None) or [])[:8]
    if not ex:
        return
    names = {t['name'] for t in st['tracks']}
    for i, x in enumerate(ex):
        if not isinstance(x, dict):
            continue
        inst, f = x.get('inst'), x.get('follows', 'lead')
        if not inst or f not in EXTRA_FOLLOWS or not (inst in INSTRUMENTS or str(inst).startswith(('sf:', 'real:', 'vst:'))):
            continue
        lead = next((t for t in st['tracks'] if t['name'] == 'lead'), None)
        if f == 'counter' and 'counter' not in names:
            if not lead:
                continue
            st['tracks'].append(dict(name='counter', layer='lead', inst=inst, pan=-0.3 if (lead.get('pan') or 0) >= 0 else 0.3,
                                     rev=max(0.3, lead.get('rev') or 0), dly=0.1, sc=0.0, db=-24 + float(x.get('db', 0) or 0),
                                     hp=None, drive=None, p={}, counter=True, user_pick=True, extra=True))
            names.add('counter')
            continue
        src = next((t for t in st['tracks'] if t['name'] == f), None) or \
            next((t for t in st['tracks'] if t['layer'] == f and not t.get('double_of')), None)
        if not src:
            continue
        name = f'extra{i + 1}'
        st['tracks'].append(dict(name=name, layer=src['layer'], inst=inst,
                                 pan=float(x.get('pan', (-0.35 if i % 2 else 0.35))), rev=max(0.3, src.get('rev') or 0),
                                 dly=src.get('dly') or 0.0, sc=src.get('sc') or 0.0,
                                 db=(src.get('db') if src.get('db') is not None else -22) + float(x.get('db', -4) or 0),
                                 hp=None, drive=None, p={}, double_of=src['name'], octave=int(x.get('octave', 0) or 0),
                                 user_pick=True, extra=True))
        names.add(name)


def add_counter_track(st, opts):
    """A second melodic line that answers the lead (celli under violins, horns answering strings ...)."""
    want = getattr(opts, 'counter', None)
    name = st.get('name')
    pool = COUNTER_STYLES.get(name) or (['cello', 'horn', 'strings'] if st.get('category') == 'Orchestral' else ['strings', 'flute'])
    r = random.Random(opts.seed * 53 + 11)
    if want == 'off' or not any(t['layer'] == 'lead' for t in st['tracks']):
        return
    if want != 'on' and not (name in COUNTER_STYLES and r.random() < 0.6):
        return
    inst = r.choices(pool, [2.0] + [1.0] * (len(pool) - 1))[0]
    lead = next(t for t in st['tracks'] if t['layer'] == 'lead')
    st['tracks'].append(dict(name='counter', layer='lead', inst=inst, pan=-0.3 if (lead.get('pan') or 0) >= 0 else 0.3,
                             rev=max(0.3, lead.get('rev') or 0), dly=0.1, sc=0.0, db=-24, hp=None, drive=None, p={}, counter=True))


def gen_counter(evs, key, sections, cb, st, rnd):
    """Fill the lead's gaps with short answering phrases (chord tones, an octave down), and sometimes sing a third or
    sixth under its long notes. It is quieter than the lead and never plays over the lead's busy passages."""
    lead = sorted((e for e in evs if e.track == 'lead' and e.midi is not None), key=lambda e: e.beat)
    if len(lead) < 2:
        return []
    pcs = sorted({(key.root + iv) % 12 for iv in key.scale})
    out = []
    q = (4 / 9 if st.get('meter') == '9/8' else 1 / 3) if st.get('meter') else 0.5   # counter grid: 8ths / triplet 8ths
    snap = lambda x: math.ceil(x / q - 1e-6) * q

    def chord_at(beat):
        for sec in sections:
            if sec['bar'] * 4 <= beat < (sec['bar'] + sec['bars']) * 4 and sec.get('prog'):
                b = int(beat // 4) - sec['bar']
                return sec['prog'][(b // max(1, cb)) % len(sec['prog'])]
        return 0

    def tones(beat, near):
        c = chord_at(beat)
        cand = [key.deg(c + iv, o) for iv in (0, 2, 4) for o in (3, 4, 5)]
        cand = [m for m in cand if 50 <= m <= 79]
        return sorted(cand, key=lambda m: abs(m - near))
    prev = lead[0].midi - 12
    for a, b in zip(lead, lead[1:]):
        g0 = a.beat + a.dur
        gap = b.beat - g0
        if 0.75 <= gap <= 8:
            n = 1 if gap < 2 else rnd.choice([2, 2, 3])
            step = snap(min(1.0, max(q, (gap - 0.25) / n)))
            t0 = snap(g0 + 0.1)
            target = b.midi - 12
            for k in range(n):
                t = t0 + k * step
                if t + 0.25 > b.beat:
                    break
                near = prev + (target - prev) * (k + 1) / (n + 1)
                tt = tones(t, near) or [near]
                m = tt[0] if rnd.random() < 0.8 or len(tt) < 2 else tt[1]
                out.append(Ev('counter', t, max(0.3, step * 0.9), m, 0.62 + 0.08 * rnd.random()))
                prev = m
        if a.dur >= 1.5 and a.beat + a.dur >= b.beat - 0.3 and rnd.random() < 0.7:
            # the lead holds: the counter moves underneath in its second half, leading toward the lead's next note
            n = 2 if a.dur >= 3 else 1
            for k in range(n):
                t = snap(a.beat + a.dur * (0.5 + 0.22 * k))
                if t + 0.4 > b.beat:
                    break
                near = prev + (b.midi - 12 - prev) * (k + 1) / (n + 1)
                tt = tones(t, near) or [near]
                m = tt[0] if tt[0] != prev or len(tt) < 2 else tt[1]
                out.append(Ev('counter', t, min(1.0, b.beat - t) * 0.9, m, 0.6))
                prev = m
        elif a.dur >= 2.0 and rnd.random() < 0.45 and a.midi % 12 in pcs:
            i = pcs.index(a.midi % 12)
            c = chord_at(a.beat)
            cpcs = {key.deg(c + iv, 4) % 12 for iv in (0, 2, 4)}
            for down in (2, 5):                                # a third, else a sixth below - if it's a chord tone
                pc = pcs[(i - down) % len(pcs)]
                if pc in cpcs:
                    m = a.midi - ((a.midi % 12 - pc) % 12 or 12)
                    if 50 <= m:
                        out.append(Ev('counter', a.beat, a.dur, m, 0.55))
                    break
    return out


def apply_harm_alts(evs, tracks, alts):
    """Secondary dominants / borrowed chords: the altered chord tone changes in every harmony part (chords, pad, arp,
    bass, counter); held melody notes follow through fix_clashes."""
    if not alts:
        return
    for e in evs:
        t = tracks.get(e.track)
        if e.midi is None or not t or (t['layer'] not in ('chords', 'pad', 'arp', 'bass') and e.track != 'counter'):
            continue
        for b0, b1, pc, new in alts:
            if b0 <= e.beat < b1 and e.midi % 12 == pc:
                e.midi += (new - pc + 6) % 12 - 6
                break


def _is_real(t):
    inst = t.get('inst', '')
    return inst.startswith(('sf:', 'vst:'))


def shape_dynamics(evs, tracks, sections, st):
    """Play softer in quiet sections and harder in big ones - in the notes themselves, not only the fader. Sampled
    instruments and plugins change tone with how hard they are played (softer strings sound darker and warmer).
    Phrases also lean forward to their third bar and relax after. Built-in synths keep their levels."""
    from .instruments import DRUMS
    secs = [(s_['bar'] * 4, (s_['bar'] + s_['bars']) * 4, s_) for s_ in sections]
    for e in evs:
        t = tracks.get(e.track)
        if e.midi is None or not t or t['inst'] in DRUMS or not _is_real(t):
            continue
        sec = next((x for x in secs if x[0] <= e.beat < x[1]), None)
        if not sec:
            continue
        b0, b1, s_ = sec
        en = SECTION_ENERGY.get(s_['name'], 0.9)
        f = 0.74 + 0.26 * max(0.0, min(1.0, (en - 0.62) / 0.38))
        if s_['opts'].get('build'):
            f = 0.78 + 0.22 * (e.beat - b0) / max(1, b1 - b0)
        pos = ((e.beat - b0) % 16) / 16
        arc = 1 + 0.07 * math.sin(math.pi * min(1.0, pos / 0.75))
        e.vel = max(0.2, min(1.0, e.vel * f * arc))
    sv = st.get('sec_vel')
    if sv:                                               # film-score dynamics: a whole section played softer / louder
        for i, (b0, b1, s_) in enumerate(secs):          # (every part, synths and drums too) - the pp opening that
            g = float(sv[min(i, len(sv) - 1)])           # grows to the tutti, the 10-15 dB a film cue spans
            if abs(g - 1.0) < 1e-6:
                continue
            for e in evs:
                if b0 <= e.beat < b1:
                    e.vel = max(0.06, min(1.0, e.vel * g))


EXPRESSIVE = {'strings', 'violin', 'cello', 'viola', 'contrabass', 'slowstrings', 'tremolo', 'spiccato', 'horn', 'brass', 'trumpet',
              'trombone', 'tuba', 'braam', 'choir', 'vox', 'flute', 'clarinet', 'oboe', 'bassoon', 'piccolo', 'sax', 'tenorsax'}


def base_inst(t):
    inst = t.get('rig_from') or (t.get('fallback') if t.get('inst', '').startswith('vst:') else None) or t.get('inst', '')
    return inst[3:] if inst.startswith('sf:') else inst


def expression_curves(evs, tracks, sections, fx, total_bars):
    """Mod-wheel (CC1) dynamics curves for bowed, blown and sung parts: each long note swells and relaxes, quiet
    sections sit lower, builds rise, fades fall. Orchestra plugins (BBC Symphony Orchestra, LABS ...) use CC1 for
    dynamics; the curves go to your saved plugin sounds and into the MIDI export. -> {track: [(beat, value 0..127)]}"""
    out = {}
    end = total_bars * 4
    fades = [(b, b + d) for k, b, d in fx if k == 'fade']
    for name, t in tracks.items():
        if base_inst(t) not in EXPRESSIVE:
            continue
        notes = sorted((e for e in evs if e.track == name and e.midi is not None), key=lambda e: e.beat)
        if not notes:
            continue
        longs = [e for e in notes if e.dur >= 1.5]
        pts, last, li = [], None, 0
        beat = 0.0
        while beat <= end + 2:
            sec = next((s_ for s_ in sections if s_['bar'] * 4 <= beat < (s_['bar'] + s_['bars']) * 4), None)
            en = SECTION_ENERGY.get(sec['name'], 0.9) if sec else 0.85
            v = 52 + 58 * max(0.0, min(1.0, (en - 0.6) / 0.4))
            if sec and sec['opts'].get('build'):
                v = 60 + 50 * (beat - sec['bar'] * 4) / max(1, sec['bars'] * 4)
            while li < len(longs) and longs[li].beat + longs[li].dur < beat:
                li += 1
            cur = next((e for e in longs[li:li + 6] if e.beat <= beat < e.beat + e.dur), None)
            if cur:
                x = (beat - cur.beat) / cur.dur
                v += 16 * math.sin(math.pi * min(1.0, x * 1.15)) - 8
            for f0, f1 in fades:
                if beat >= f0:
                    v *= max(0.25, 1 - (beat - f0) / max(1, f1 - f0) * 0.75)
            v = int(max(18, min(124, round(v))))
            if last is None or abs(v - last) >= 2:
                pts.append((round(beat, 3), v))
                last = v
            beat += 0.25
        out[name] = pts
    return out


# ----------------------------------------------------------------------------- layered parts (two instruments, one part)
LAYER_ODDS = {'Electronic': 0.5, 'Classic': 0.3, 'Orchestral': 0.45}
OCT_UP = {'bell', 'celesta', 'flute', 'sf:piccolo', 'pluck', 'chip', 'marimba', 'kalimba', 'harp', 'glock', 'steeldrum', 'pizz'}
OCT_DOWN = {'cello', 'sf:contrabass', 'sf:bassoon', 'sf:trombone', 'sf:tuba', 'horn'}
NO_LAYER = {'808', 'logdrum', 'wobble', 'acid', 'sinebass', 'chipbass', 'riddim', 'screech', 'dnbwob', 'vowelwob',
            'multiwob', 'tablewob', 'chopwob', 'rumble', 'darkwob', 'subwob', 'fmgrowl', 'talkgrowl', 'metalbass', 'fuzzbass',
            'slowwob', 'yoiwob', 'sweepwob', 'reesewob', 'deepsub', 'sleepersub', 'brightwob', 'tearwob', 'divesub', 'ms10zap', 'pitchgrowl'}


def debell(st, opts):
    """Last check on every song: no bell / mallet sound in a genre where it isn't idiomatic (rotation, layering, moods
    and palettes all end up here) - unless you picked it yourself."""
    from .styles import bell_allowed, bell_swap, BELLS, MALLETS, STYLES
    name = st.get('name') or opts.style
    mine = opts.instruments or {}
    own = {(t['layer'], t['inst']) for t in STYLES.get(name, {}).get('tracks', [])}
    rnd = random.Random(f'{opts.seed}-bells-{name}')
    for t in st['tracks']:
        role = t['layer']
        if role not in ('arp', 'lead', 'chords', 'pad') or t['inst'].startswith(('vst:', 'user:', 'real:')):
            continue
        if mine.get(role) == t['inst'] or t.get('extra'):     # your picks and your extra instruments stay
            continue
        if bell_allowed(name, t['inst']):
            # even where they fit, a bell / mallet that isn't the genre's own sound for this part is an occasional colour
            if t['inst'] not in BELLS | MALLETS or (role, t['inst']) in own or rnd.random() < 0.35:
                continue
        # replaced by the genre's own sound for this part when it has one (not a generic category synth)
        from .styles import POOLS as _P
        mine_ = [] if name == 'hauntology' else [i for (l, i) in own if l == role and bell_allowed(name, i)]   # (Hauntology: unchanged)
        mine_ += [] if name == 'hauntology' else [i for i in _P.get(name, {}).get(role, []) if i not in BELLS | MALLETS]
        mine_ = list(dict.fromkeys(mine_))        # any of the genre's own non-bell sounds, not always the first one
        t['inst'] = rnd.choice(mine_) if mine_ else bell_swap(name, role, t['inst'])
    if name in CLUB_COHERENT and not mine:             # (1.95.1) a swap above can leave a doubled part on a sound of another
        by = {t['name']: t for t in st['tracks']}         # kind (a bell layer on what became a pluck): drop that layer
        st['tracks'][:] = [t for t in st['tracks'] if not (t.get('double_of') and t['layer'] != 'bass'
                                                            and not (name in CLUB_TRANCE and t['layer'] == 'lead')
                                                            and t['double_of'] in by
                                                            and (sound_kind(t['inst']) != sound_kind(by[t['double_of']]['inst'])
                                                                 or inst_family(t['inst']) != inst_family(by[t['double_of']]['inst'])))]


SWELL_SOUNDS = {'warmpad', 'glasspad', 'strings', 'slowstrings', 'choir', 'solina', 'supersaw', 'tremolo', 'violins', 'violas',
                'drone', 'talkbox', 'brass', 'horn', 'trombone', 'violin', 'pedalsteel', 'bandoneon', 'accordion', 'cello',
                'viola', 'synthbrass', 'braam', 'harmonica', 'flute', 'oboe', 'clarinet', 'sax', 'vox', 'organ'}


def attack_class(inst):
    """'swell' for sounds that fade / bow / blow in, 'hit' for struck or plucked ones. Layering a hit with a swell on the
    same chord makes a flam: the struck note on the beat, then the swell peaking a 16th later (a '1-2' instead of a 1)."""
    base = str(inst).split(':', 1)[-1]
    return 'swell' if base in SWELL_SOUNDS or base.startswith(('slow', 'pad')) else 'hit'


def add_layer_tracks(st, opts):
    """Some parts get a second instrument from the genre's own pool, playing the same notes (in unison or an octave
    apart): a supersaw lead with a pluck on top, violins doubled by a flute an octave up or celli an octave down, a
    saw bass with a sub under it, piano chords with a string pad inside them. Which parts, and with what, changes
    from song to song."""
    from .styles import POOLS
    want = getattr(opts, 'layering', None)
    if want == 'off' or st.get('name') == 'chiptune' or (st.get('no_layers') and want != 'on') \
            or ((st.get('name') or opts.style) in SPARSE_DUBSTEP and want != 'on'):   # (1.95) sparse dubstep: no doubles
        return                                           # (a genre whose doubling is written in keeps its line-up)
    v = max(0.0, min(1.0, float(opts.variety)))
    cat = st.get('category')
    fusion = st.get('fusion') or {}
    ps = opts.part_seeds or {}
    odds = LAYER_ODDS.get(cat, 0.3) * (0.35 + 0.9 * v) * (1.6 if want == 'more' else 1.0)
    picks = 0
    for t in list(st['tracks']):
        role = t['layer']
        if role not in ('lead', 'chords', 'pad', 'arp', 'bass') or t.get('counter') or t.get('double_of'):
            continue
        if role == 'lead' and st.get('solo_lead') and want != 'more':
            continue                                     # one soloist (a smooth-jazz sax isn't doubled)
        if role in (opts.instruments or {}) and want != 'more':
            continue
        part = {'bass': 'bass', 'lead': 'melody', 'arp': 'melody'}.get(role, 'chords')
        sd = ps.get(part) if ps.get(part) is not None else opts.seed * 1009 + PART_K[part]
        r = random.Random(f'{sd}-{role}-layer' + _snd(opts))
        owner = fusion.get({'bass': 'bass', 'chords': 'harmony', 'pad': 'harmony'}.get(role, 'melody'), opts.style)
        if role == 'bass':
            forced = st.get('sub_layer') and t['inst'] not in ('808', 'sinebass', 'logdrum', 'chipbass') and want != 'off'
            if forced and t['inst'] == 'wobble':
                t['p'] = dict(t['p'], sub=0.0)                # the separate clean sub takes over the low end
            if not forced and (cat != 'Electronic' or t['inst'] in NO_LAYER or r.random() > odds):
                continue
            inst, octv = 'sinebass', 0                       # the classic sub layer under a mid bass
            if forced:
                picks -= 1                                   # the genre's own sub doesn't count as a 'layer'
        else:
            pool = [i for i in (POOLS.get(owner, {}).get(role) or PALETTES.get(cat, {}).get(role) or []) if i != t['inst']]
            if not pool or r.random() > odds or picks >= (3 if want == 'more' else 2):
                continue
            if role in ('chords', 'arp'):                    # no swells doubling struck chords (and the reverse): flams
                pool = [i for i in pool if attack_class(i) == attack_class(t['inst'])]
                if not pool:
                    continue
            _g = st.get('name') or opts.style
            if _g in CLUB_COHERENT and not (_g in CLUB_TRANCE and role == 'lead'):   # (1.94) club records double a part
                pool = [i for i in pool if inst_family(i) == inst_family(t['inst']) and sound_kind(i) == sound_kind(t['inst'])]
                if not pool:                                                        # (trance leads: saw + pluck is the idiom)
                    continue
            inst = r.choice(pool)
            octv = 12 if inst in OCT_UP and role in ('lead', 'arp') else (-12 if inst in OCT_DOWN and role == 'lead' else 0)
        picks += 1
        layer_hp = None
        if role == 'bass':
            # (1.80 / 1.82) only ONE sound owns the sub: two basses on the same notes (a reese's own sub + a sine, a
            # growl + a saw ...) beat against each other and spike into the limiter - the 'clipping bass'. A sub-type
            # sound (sine, 808, deep bass) takes the bottom; otherwise the main bass keeps it and the layer is cut.
            if inst in SUB_BASSES and t['inst'] not in SUB_BASSES:
                t['hp'] = max(float(t.get('hp') or 0), 95.0)
            else:
                layer_hp = 110.0
        base_db = t['db'] if t.get('db') is not None else {'bass': -15, 'chords': -21, 'pad': -23, 'arp': -25, 'lead': -19}[role]
        st['tracks'].append(dict(name=t['name'] + '_layer', layer=role, inst=inst, pan=-(t.get('pan') or 0) * 0.6,
                                 rev=t.get('rev') or 0.0, dly=t.get('dly') or 0.0, sc=t.get('sc') or 0.0,
                                 db=base_db - (4 if role == 'bass' else 6), hp=layer_hp if role == 'bass' else None,
                                 drive=None, p={}, double_of=t['name'], octave=octv))


def add_slides(evs, tracks, st, key, rnd):
    """Real slides into the melody's longer notes: the note itself starts a whole step (or half step) low and glides up
    into pitch, the way a fiddle, pedal steel, Telecaster or harmonica bends into a note - the most recognisable country
    inflection. Works on recorded instruments too (the renderer bends the recording)."""
    p = float(st.get('slides') or 0)
    scale = {(key.root + x) % 12 for x in key.scale}
    for e in evs:
        t = tracks.get(e.track, {})
        if t.get('layer') != 'lead' or e.midi is None or e.dur < 0.5 or rnd.random() > p:
            continue
        if abs(e.beat * 2 - round(e.beat * 2)) > 1e-6:      # on the beat or the off-beat 8th only
            continue
        e.slide = 2.0 if (e.midi - 2) % 12 in scale else 1.0
        if rnd.random() < 0.25:
            e.slide = 1.0                                   # a quick half-step bend now and then


BENDABLE = {'sitar', 'veena', 'saz', 'oud', 'ney', 'flute', 'violin', 'phin', 'sf:sitar', 'sf:violin', 'sf:flute', 'sf:shehnai',
            'sf:fiddle', 'shehnai', 'real:violin', 'real:flute'}


def ornament_amount(st, opts):
    """How much meend / gamak: the genre's own amount (raga-phrased genres have it), scaled by the Bends setting."""
    base = st.get('ornament')
    if base is None:
        base = 0.75 if st.get('lead_device') == 'raga' else 0.0
    b = getattr(opts, 'bends', None)
    if b == 'off':
        return 0.0
    if b == 'subtle':
        return base * 0.5
    if b == 'more':
        return min(1.0, max(base, 0.5) * 1.6)
    return base


def add_ornaments(evs, tracks, key, amt, rnd):
    """Indian ornaments on instruments that can bend (sitar, veena, saz, oud, bansuri, violin, shehnai):
    meend - a slow pull from the previous note into this one (up to 5 semitones, up or down);
    gamak - shaking up to the next note above and back, on held notes (mostly the phrase's peak);
    andolan - a slow sway on very long notes; a 'fall' that pulls the end of a note towards a lower next note.
    Keyboards and hammered instruments (harmonium, santoor) can't bend, so they're left alone."""
    scale = sorted({(key.root + x) % 12 for x in key.scale})

    def above(m):                                        # semitones up to the next scale note
        for k in (1, 2, 3):
            if (m + k) % 12 in scale:
                return k
        return 2

    def below(m):                                        # semitones down to the next scale note
        for k in (1, 2, 3):
            if (m - k) % 12 in scale:
                return k
        return 2
    for name, t in tracks.items():
        if t.get('layer') not in ('lead', 'arp') or t.get('inst') not in BENDABLE:
            continue
        notes = sorted((e for e in evs if e.track == name and e.midi is not None), key=lambda e: e.beat)
        for i, e in enumerate(notes):
            if e.dur < 0.45:
                continue
            prev = notes[i - 1] if i and e.beat - (notes[i - 1].beat + notes[i - 1].dur) < 0.6 else None
            nxt = notes[i + 1] if i + 1 < len(notes) and notes[i + 1].beat - (e.beat + e.dur) < 0.6 else None
            bend = []
            diff = (prev.midi - e.midi) if prev is not None else 0
            if prev is not None and 1 <= abs(diff) <= 5 and rnd.random() < (0.85 if e.dur >= 0.9 else 0.3) * amt:
                bend.append(('meend', float(diff), rnd.uniform(0.35, 0.6)))
            elif e.dur >= 0.9 and rnd.random() < 0.4 * amt:
                # a pull into the note from the scale note below (mostly) or above - always a note of the raga, never a
                # chromatic one (before 1.72 the 'below' start was worked out from 3 semitones down and often missed the
                # scale, so the glide started on an out-of-key pitch)
                bend.append(('meend', -float(below(e.midi)) if rnd.random() < 0.7 else float(above(e.midi)), rnd.uniform(0.3, 0.5)))
            peak = (prev is None or prev.midi <= e.midi) and (nxt is None or nxt.midi <= e.midi)
            if e.dur >= 0.9 and rnd.random() < (0.75 if peak else 0.35) * amt:
                bend.append(('gamak', float(above(e.midi)), rnd.uniform(4.8, 6.4)))
            elif e.dur >= 1.8 and rnd.random() < 0.5 * amt:
                bend.append(('andolan', rnd.uniform(0.25, 0.45)))
            if nxt is not None and e.dur >= 0.75 and -4 <= nxt.midi - e.midi <= -1 and rnd.random() < 0.3 * amt:
                bend.append(('fall', float(nxt.midi - e.midi)))
            if bend:
                e.bend = bend
                e.slide = 0.0                            # the meend replaces the quick slide


def maqam_quarters(evs, tracks, key):
    """Maqam Bayati, Rast and Saba have notes between the piano keys (a quarter tone flat). The melody parts - lead, arp
    and the sung voice - bend those notes down a quarter tone; chords and drones stay on the 12-tone notes."""
    from .theory import MAQAM_QUARTER
    q = MAQAM_QUARTER.get(key.scale_name)
    if not q:
        return
    pcs = {(key.root + key.scale[d]) % 12: v for d, v in q.items()}

    def real(m):                                         # where a note actually sounds in this maqam
        return m + pcs.get(int(round(m)) % 12, 0.0)
    for e in evs:
        t = tracks.get(e.track, {})
        if e.midi is None or (t.get('layer') not in ('lead', 'arp', 'chords', 'pad', 'bass') and e.track != 'vocal'):
            continue
        # every pitched part plays the maqam's real notes (since 1.72): before, only the melody bent its half-flat notes
        # and the chords / pads / bass kept the 12-tone note right under it - a quarter-tone clash on every Rast chord
        v = pcs.get(e.midi % 12, 0.0)
        new = [('shift', v)] if v else []
        for b in (e.bend or []):
            if b[0] == 'shift':
                continue
            if b[0] in ('meend', 'gamak', 'fall'):       # ornaments aim at real maqam notes, not the piano key beside them
                tgt = e.midi + float(b[1])
                b = (b[0], real(tgt) - real(e.midi)) + tuple(b[2:])
            new.append(b)
        if new or e.bend:
            e.bend = new or None


def sync_drones(evs, tracks, bpm):
    """The tanpura plucks its four strings in time with the song (one per beat, every other beat when it's fast).
    Each pluck is its own note on the beat grid, so it follows the tempo map too: the genres that speed up (jugalbandi,
    kirtan, qawwali ...) used to leave the tanpura on a fixed clock, drifting against the tabla like a bass player
    doing their own thing."""
    every = 2 if 60.0 / max(40, bpm) < 0.55 else 1          # beats per pluck
    names = {n for n, t in tracks.items() if t.get('inst') == 'tanpura'}
    if not names:
        return
    out = []
    for e in evs:
        if e.track not in names or e.midi is None:
            out.append(e)
            continue
        k = int(-(-e.beat // every))                          # first grid beat inside the note
        while k * every < e.beat + e.dur - 1e-6:
            out.append(e.copy(beat=float(k * every), dur=float(every), mod=f'str:{k % 4}', glide=None))
            k += 1
    evs[:] = out


SUSTAINED_BASS = {'reese', 'growl', 'wobble', 'hoover', 'sinebass', 'moogbass', 'drone', 'tanpura', 'dnbwob', 'vowelwob',
                  'multiwob', 'tablewob', 'chopwob', 'rumble', 'darkwob', 'subwob', 'fmgrowl', 'talkgrowl', 'metalbass', 'fuzzbass',
                  'slowwob', 'yoiwob', 'sweepwob', 'reesewob', 'deepsub', 'sleepersub', 'brightwob', 'tearwob', 'divesub', 'ms10zap', 'pitchgrowl'}


def legato_bass(evs, tracks):
    """Held basses (reese, growl, sub ...) roll on instead of choking and restarting on every note: a repeated note of
    the same pitch is tied into the one before it, and short gaps close up, so the bass only changes where the pitch
    changes. (Re-struck reese notes every beat dipped 3-6 dB each time - the bass sounded like it kept breaking.)"""
    for name, t in tracks.items():
        if t.get('layer') != 'bass' or t.get('inst') not in SUSTAINED_BASS:
            continue
        notes = sorted((e for e in evs if e.track == name and e.midi is not None), key=lambda e: e.beat)
        drop = set()
        prev = None
        for e in notes:
            if prev is not None:
                gap = e.beat - (prev.beat + prev.dur)
                if -1e-6 <= gap < 0.2:
                    if e.midi == prev.midi and e.glide is None and not e.mod and prev.dur + gap + e.dur <= 16:
                        prev.dur = e.beat + e.dur - prev.beat           # tie it on
                        drop.add(id(e))
                        continue
                    prev.dur = e.beat - prev.beat                       # close the gap up to the next note
            prev = e
        if drop:
            evs[:] = [e for e in evs if id(e) not in drop]


INTRO_NAMES = {'intro', 'alap', 'alapana', 'buka', 'invocation', 'doina', 'bells', 'drums'}   # (only leading ones are skipped)


def rotate_solos(evs, tracks, sections, st):
    """Solo sections pass the melody round the band, like a bluegrass jam or an 80s sax / guitar break: each 'solo'
    section is played by the next instrument in st['solos'] (track names); everywhere else the lead keeps the tune."""
    order = [n for n in st['solos'] if n in tracks]
    if not order:
        return
    k = 0
    for sec in sections:
        if sec['name'] not in ('solo', 'break_solo'):
            continue
        to = order[k % len(order)]
        k += 1
        b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
        for e in evs:
            if e.track == 'lead' and b0 <= e.beat < b1:
                e.track = to


def add_g_runs(evs, tracks, sections, key):
    """The bluegrass guitar 'G run': at the end of each section the rhythm guitar walks up from below into the tonic."""
    trk = 'gtr' if 'gtr' in tracks else ('chords' if 'chords' in tracks else None)
    if not trk:
        return
    t0 = 40 + ((key.root - 40) % 12)
    for sec in sections:
        if 'chords' not in sec['layers'] or sec['bars'] < 4:
            continue
        end = (sec['bar'] + sec['bars']) * 4
        run = [t0 - 5, t0 - 3, t0 - 2, t0 - 1]
        for i, m in enumerate(run):
            evs.append(Ev(trk, end - 2 + i * 0.5, 0.45, m, 0.85))


def add_lead_runs(evs, key, prob, rnd, track='lead'):
    """Liquid-DnB lead hook: a fast 16th-note arpeggio sweeps up (in the key, climbing in thirds) into a long held lead
    note that follows a gap - the run fills the space before the note instead of the lead just appearing."""
    lead = sorted((e for e in evs if e.track == track and e.midi is not None), key=lambda e: e.beat)
    starts = [e.beat for e in lead]
    pcs = {(key.root + i) % 12 for i in key.scale}
    for i, e in enumerate(lead):
        if e.dur < 0.9 or e.beat < 2 or rnd.random() >= prob:
            continue
        prev_on = starts[i - 1] if i else -99
        if e.beat - prev_on < 1.5:
            continue
        below = [m for m in range(e.midi - 1, e.midi - 24, -1) if m % 12 in pcs]
        run = below[1::2][:7][::-1]                      # every other scale note: thirds, low to high
        n = len(run)
        for j, m in enumerate(run):
            b = e.beat - (n - j) * 0.25
            if b > prev_on + 0.25:
                evs.append(Ev(track, b, 0.22, m, round(min(1.0, e.vel * (0.6 + 0.35 * j / max(1, n - 1))), 3)))


def eno_loops(evs, loops, total_beats):
    """Brian Eno's tape loops (Music for Airports): each part repeats its own phrase on its own cycle length, so the parts
    drift against each other and the music never lines up the same way twice."""
    for name, period in loops.items():
        mine = sorted((e for e in evs if e.track == name), key=lambda e: e.beat)
        if not mine:
            continue
        start = mine[0].beat
        cell = [e for e in mine if e.beat < start + period]
        evs[:] = [e for e in evs if e.track != name]
        t = start
        while t < total_beats - 1:
            for e in cell:
                b = t + (e.beat - start)
                if b < total_beats - 1:
                    evs.append(Ev(name, b, e.dur, e.midi, e.vel, e.glide, e.mod))
            t += period


def chop_samples(evs, tracks, rnd):
    """Lo-fi / boom-bap: chords played like a chopped record - long chords are re-triggered in sampler slices
    (the attack comes back each time, slightly uneven), the way an MPC chop of a sampled Rhodes sounds."""
    out = []
    for e in evs:
        t = tracks.get(e.track, {})
        if not t.get('chops') or e.midi is None or e.dur < 1.4:
            out.append(e)
            continue
        cuts = rnd.choice(((0, 1.5, 2.5), (0, 0.75, 1.5, 2.5), (0, 2, 2.75), (0, 1, 1.75, 3)))
        cuts = [c for c in cuts if c < e.dur - 0.2]
        for i, c in enumerate(cuts):
            nxt = cuts[i + 1] if i + 1 < len(cuts) else e.dur
            out.append(Ev(e.track, e.beat + c, max(0.2, nxt - c - 0.05), e.midi, e.vel * (1.0 if i == 0 else 0.88), e.glide, e.mod))
    evs[:] = out


def double_layers(evs, tracks):
    """The layer tracks play exactly the notes of the part they double (after tuning and dynamics)."""
    out = []
    for name, t in tracks.items():
        src = t.get('double_of')
        if not src:
            continue
        o = t.get('octave', 0)
        acc_only, max_d = t.get('accents'), t.get('max_dur')
        for e in evs:
            if e.track == src and e.midi is not None and (not acc_only or e.mod == 'acc'):   # accents: horn stabs
                m = e.midi + o
                if not 28 <= m <= 100:
                    m = e.midi
                out.append(e.copy(track=name, dur=min(e.dur, max_d) if max_d else e.dur, midi=m, vel=e.vel * 0.9,
                                  glide=None if e.glide is None else e.glide + (m - e.midi)))
    return out


SECTION_GROUPS = {'B': {'chorus', 'hook', 'drop', 'climax', 'theme', 'main', 'loop', 'B', 'head', 'refrain'},
                  'C': {'break', 'bridge', 'calm', 'outro', 'C', 'breakdown', 'interlude', 'solo'}}


def section_group(sec):
    """A = verses / intros, B = choruses / drops, C = breaks / bridges / outros."""
    if sec['opts'].get('drop') or sec['name'] in SECTION_GROUPS['B']:
        return 'B'
    if sec['name'] in SECTION_GROUPS['C'] or sec['opts'].get('fade'):
        return 'C'
    return 'A'


# genres whose lead sound is the genre - rotation only uses their own pool
# rap, hip-hop and R&B genres: their signature sounds are swapped for alternatives far less often
SIGNATURE_ROLES = {'house': ('bass', 'chords'), 'deep_house': ('bass', 'chords'), 'tech_house': ('bass',), 'techno': ('bass',),
                   'melodic_techno': ('bass',), 'acid_house': ('bass',), 'psytrance': ('bass',), 'smooth_jazz': ('lead', 'chords'),
                   'lofi': ('chords',), 'boombap': ('bass', 'chords')}
SIGNATURE_STRICT = {'trap', 'boombap', 'rnb', 'lofi', 'uk_drill', 'luxury_rap', 'g_funk', 'neo_soul', 'new_jack_swing', 'alt_rnb',
                    'rage', 'plugg', 'hauntology_sunlit', 'hauntology_dark', 'memphis_phonk', 'orchestral_hiphop', 'jersey_club',
                    'country', 'modern_country', 'country_waltz', 'outlaw_country', 'western_swing', 'bluegrass',
                    'smooth_jazz', 'smooth_funk', 'quiet_storm', 'jazz_rap', 'cloud_rap', 'slow_jam',
                    'house', 'deep_house', 'tech_house', 'progressive_house', 'melodic_house', 'acid_house', 'trance',
                    'uplifting_trance', 'progressive_trance', 'psytrance', 'techno', 'melodic_techno', 'bigroom',
                    'dubstep', 'brostep', 'melodic_dubstep', 'deep_dubstep', 'deep_dubstep_minimal', 'riddim', 'chillstep'}
SIGNATURE_SOUNDS = {'trap', 'boombap', 'rnb', 'lofi', 'uk_drill', 'luxury_rap', 'g_funk', 'neo_soul', 'new_jack_swing', 'alt_rnb',
                    'rage', 'plugg', 'hauntology_sunlit', 'hauntology_dark', 'phonk', 'house_phonk', 'memphis_phonk', 'brazilian_phonk', 'metal', 'punk', 'symphonic_metal', 'rock',
                    'epic_orchestral', 'epic_battle', 'epic_choir', 'heroic_anthem', 'symphonic_finale'}


INST_FAMILIES = {
    'keys': {'piano', 'epiano', 'wurli', 'm1piano', 'organ', 'clav', 'fmpiano', 'upright_piano', 'harpsichord', 'grand', 'rhodes'},
    'guitar': {'guitar', 'acguitar', 'nylon', 'twang', 'mutedgtr', 'cleanguitar', 'distgtr', 'overdrive', 'jazzguitar', 'steelgtr',
               'banjo', 'mandolin', 'sitar', 'koto', 'oud', 'pedalsteel'},
    'synth': {'leadsaw', 'softlead', 'supersaw_lead', 'supersaw', 'polysynth', 'hoover', 'pluck', 'pluck_saw', 'chip', 'stab',
              'synthbrass', 'acid', 'screech', 'square_lead', 'vox', 'saw_lead'},
    'pad': {'warmpad', 'glasspad', 'solina', 'strings', 'slowstrings', 'choir', 'tremolo', 'violins', 'violas'},
    'winds': {'sax', 'tenorsax', 'altosax', 'flute', 'clarinet', 'oboe', 'brass', 'trumpet', 'mutedtrumpet', 'trombone', 'horn',
              'trumpetsection', 'piccolo', 'bassoon', 'harmonica', 'panflute', 'shakuhachi', 'violin', 'fiddle', 'cello'},
    'mallets': {'vibes', 'bell', 'celesta', 'marimba', 'kalimba', 'musicbox', 'steeldrum', 'xylophone', 'glock', 'tubular'},
}


NATURAL_GROUPS = {'Rock & Metal', 'Jazz', 'Swing & Big Band', 'Funk & Disco', 'Latin & Caribbean', 'Country, Folk & Blues',
                  'Soul, R&B & Gospel', 'World', 'Pop & Indie'}
STUDIO_FX = {'electro_funk', 'soca', 'groovy_soca', 'new_jack_swing', 'rnb', 'pop', 'bedroom_pop', 'modern_gospel', 'slow_jam',
             'city_pop', 'modern_country'}


def natural_band(st):
    """A live-band genre: transitions are the band's own (fills, stops, a crash) - no reverse cymbals, risers or sweeps."""
    name = st.get('name')
    if st.get('category') != 'Classic' or name in STUDIO_FX or st.get('studio_fx'):
        return False
    try:
        from .genre_groups import group_of
        return group_of(name) in NATURAL_GROUPS
    except Exception:
        return False


# where each melodic instrument sounds best: the middle of a part is kept inside this window (MIDI notes), else the
# part moves by whole octaves (a brass lead squealing around A5 drops to A4; a flute line down in the mud goes up)
INST_RANGE = {
    'piano': (40, 91), 'm1piano': (45, 88), 'epiano': (45, 84), 'wurli': (45, 84), 'organ': (43, 79), 'clav': (48, 79),
    'harpsichord': (45, 84), 'guitar': (45, 84), 'acguitar': (45, 81), 'nylon': (45, 81), 'twang': (40, 79),
    'mutedgtr': (40, 67), 'cleanguitar': (45, 84), 'jazzguitar': (45, 81), 'odguitar': (40, 84), 'distguitar': (40, 84),
    'sax': (50, 80), 'tenorsax': (46, 72), 'altosax': (53, 78), 'sopranosax': (58, 84), 'sopsax': (58, 84),
    'brass': (52, 77), 'trumpet': (55, 79), 'mutedtrumpet': (55, 79), 'trumpetsection': (55, 79), 'trombone': (40, 67),
    'horn': (43, 70), 'tuba': (28, 53), 'synthbrass': (50, 79),
    'flute': (62, 89), 'piccolo': (74, 98), 'clarinet': (52, 82), 'oboe': (60, 84), 'bassoon': (36, 63),
    'violin': (57, 88), 'viola': (50, 77), 'cello': (38, 69), 'contrabass': (28, 55),
    'harmonica': (55, 81), 'accordion': (50, 79), 'vox': (52, 79), 'choir': (48, 76),
    'celesta': (64, 100), 'bell': (64, 96), 'vibes': (55, 86), 'marimba': (48, 84), 'kalimba': (60, 86), 'harp': (40, 91),
    'leadsaw': (52, 84), 'softlead': (55, 84), 'supersaw_lead': (55, 86), 'pluck': (52, 86), 'pluck_saw': (52, 86),
    'chip': (55, 91), 'hoover': (48, 79), 'stab': (48, 84), 'qanun': (55, 88), 'ney': (55, 84), 'oud': (43, 74),
}


def fit_registers(evs, tracks):
    """Keep every melodic part (lead, arp, chords, pad) in its instrument's comfortable register: if the middle of the
    part sits above / below the instrument's window, the whole part moves by octaves (the melody keeps its shape)."""
    by = {}
    for e in evs:
        t = tracks.get(e.track)
        if t and t.get('layer') in ('lead', 'arp', 'chords', 'pad') and e.midi is not None:
            by.setdefault(e.track, []).append(e)
    for name, es in by.items():
        rng = INST_RANGE.get(str(tracks[name].get('inst', '')).split(':', 1)[-1])
        if not rng:
            continue
        mid = sorted(e.midi for e in es)[len(es) // 2]
        k = 0
        while mid + k > rng[1] and k > -36:
            k -= 12
        while mid + k < rng[0] and k < 36:
            k += 12
        if k:
            for e in es:
                e.midi += k
                if e.glide is not None:
                    e.glide += k


def apply_octaves(evs, tracks, octs):
    """Your octave choices: {'lead': -1, 'chords': 1, 'pad_sw1': -1 ...} - a part name wins over its role."""
    if not octs:
        return
    for e in evs:
        t = tracks.get(e.track)
        if not t or e.midi is None or t.get('layer') in ('kick', 'snare', 'top', 'fx'):
            continue
        k = octs.get(e.track, octs.get(t.get('layer'), 0))
        try:
            k = max(-3, min(3, int(k)))
        except (TypeError, ValueError):
            k = 0
        if k:
            e.midi += 12 * k
            if e.glide is not None:
                e.glide += 12 * k


def inst_family(inst):
    """Instrument family of a sound name ('sf:' / 'real:' prefixes ignored); unknown sounds are their own family."""
    base = str(inst).split(':', 1)[-1]
    for fam, names in INST_FAMILIES.items():
        if base in names:
            return fam
    for fam, names in INST_FAMILIES.items():          # e.g. 'cowbell_808' -> no; 'piano_soft' -> keys
        if any(base.startswith(n) for n in names if len(n) > 3):
            return fam
    return _auto_family(base)


def _auto_family(base):
    """(1.88) A built-in sound without a listed family gets one from its description, so the synths added over time
    (pads, plucks, stabs, bells, keys) rotate with their kin mid-song instead of each being a family of one. Sampled /
    recorded / plugin sounds and anything unknown stay their own family."""
    if base not in INSTRUMENTS or base in DRUMS:
        return base
    info = (INSTRUMENT_INFO.get(base) or '').lower()
    roles = {r for r, lst in ROLE_CHOICES.items() if base in lst}
    if roles == {'bass'} or ('bass' in roles and 'bass' in info.split('(')[0]):
        return 'bass'
    if 'pad' in base or ' pad' in ' ' + info.split('(')[0]:
        return 'pad'
    if any(w in info for w in ('bell', 'music box', 'glock', 'kalimba', 'marimba', 'mallet', 'vibraphone')):
        return 'mallets'
    if any(w in info for w in ('piano', 'e-piano', 'keys', 'organ', 'clav', 'rhodes', 'wurli')):
        return 'keys'
    if any(w in info for w in ('guitar', 'sitar', 'koto', 'banjo', 'harp ', 'oud', 'lute')):
        return base                                  # (acoustic-like plucked strings keep their own character)
    return 'synth'


def sound_kind(inst):
    """(1.94) A finer kind than the instrument family, for doubling: vocal, pluck, stab, pad, bell or other - a vocal chop
    isn't doubled by a pluck, a pad isn't doubled by a stab."""
    n = str(inst).lower()
    for kind, words in (('vocal', ('vox', 'vocal', 'choir', 'formant', 'vowel', 'hum', 'talk')),
                        ('bell', ('bell', 'chime', 'glock', 'celesta', 'kalimba', 'marimba')),
                        ('pluck', ('pluck', 'harp', 'pizz', 'seq', 'bleep')),
                        ('stab', ('stab', 'chord', 'horn', 'hit')),
                        ('pad', ('pad', 'string', 'solina', 'air', 'wash'))):
        if any(w in n for w in words):
            return kind
    return 'other'


CLUB_COHERENT = {'house', 'deep_house', 'tech_house', 'progressive_house', 'acid_house', 'melodic_house', 'organic_house',
                 'garage_house', 'piano_house_90s', 'nineties_club_house', 'emotive_deep_house', 'tokyo_deep_house',
                 'sunny_melodic_house', 'bass_house', 'french_house', 'afro_house',
                 'trance', 'uplifting_trance', 'progressive_trance', 'classic_vocal_trance', 'club_trance_2000s',
                 'progressive_trance_2010s', 'vocal_trance_remix', 'hard_trance', 'trance_pop_90s', 'electro_prog_trance',
                 'techno', 'minimal', 'melodic_techno', 'hard_techno', 'dub_techno', 'uk_tribal_techno', 'festival_techno'}
CLUB_DUBSTEP = {'dubstep', 'brostep', 'riddim', 'melodic_dubstep', 'deep_dubstep', 'deep_dubstep_minimal', 'deep_dubstep_rollers',
                'deep_dubstep_rolling', 'early_dubstep', 'dark_dubstep_classic', 'chillstep'}
SPARSE_DUBSTEP = {'deep_dubstep', 'deep_dubstep_minimal', 'deep_dubstep_rollers', 'deep_dubstep_rolling', 'early_dubstep',
                  'dark_dubstep_classic'}
CLUB_COHERENT = CLUB_COHERENT | CLUB_DUBSTEP             # (1.95) dubstep keeps the same discipline
CLUB_TRANCE = {g for g in CLUB_COHERENT if 'trance' in g} | {'melodic_dubstep', 'chillstep'}   # (styles where an answering sound is idiomatic)


def add_section_switch_tracks(st, opts, rnd):
    """Instrument rotation: verses, choruses and breaks play a part on different instruments from the genre's own pool
    (e.g. Rhodes verse, piano chorus, guitar bridge). The main instrument keeps the big sections."""
    from .styles import POOLS
    mode = getattr(opts, 'rotation', 'auto') or 'auto'
    if mode == 'off' or opts.structure == 'loop' or (st.get('no_rotation') and mode == 'auto'):
        return                                           # ensemble genres keep each instrument on its own part
    v = float(getattr(opts, 'variety', 0.5))
    n_roles = {'some': 1, 'lots': 3}.get(mode, 1 if v < 0.45 else (2 if v < 0.8 else 3))
    club = (st.get('name') or opts.style) in CLUB_COHERENT and mode == 'auto'
    if (st.get('name') or opts.style) in SPARSE_DUBSTEP and mode == 'auto':
        return                                           # (1.95) deep / early dubstep: a few sounds, kept all the way
    if club:                                             # (1.94) a club record keeps one sound per part all song; only a
        n_roles = 1                                      # breakdown may move its chords / pad to another sound
    if mode == 'auto' and random.Random(f'{opts.seed}-rot-on').random() > 0.35 + 0.6 * v:
        return
    pal = PALETTES.get(st.get('category'), {})
    recent = getattr(opts, 'avoid', None) or {}
    cands = []
    for role in (('chords', 'pad') if club else ('lead', 'chords', 'pad', 'arp')):
        if role == 'lead' and (st.get('name') or opts.style) in SIGNATURE_STRICT and mode == 'auto':
            continue                                     # rap / R&B: the hook sound stays the hook sound
        main = next((t for t in st['tracks'] if t['layer'] == role and t['name'] == role), None)
        if not main or role in (opts.instruments or {}) or main.get('user_pick') or str(main['inst']).startswith(('vst:', 'user:')):
            continue
        pool = list(POOLS.get(st.get('name') or opts.style, {}).get(role) or [])
        if len(set(pool)) == 1:                         # the genre has exactly one sound for this part (phonk cowbell)
            continue
        if len(pool) < 3 and (st.get('name') or opts.style) not in SIGNATURE_SOUNDS | SIGNATURE_STRICT:
            pool += [x for x in pal.get(role, []) if x not in pool][:2]
        alts = [x for x in dict.fromkeys(pool) if x != main['inst'] and x in INSTRUMENTS or (isinstance(x, str) and x.startswith('sf:') and x != main['inst'])]
        if mode != 'lots':                               # mid-song swaps stay in the same family (keys <-> keys, horns <-> winds)
            fam = inst_family(main['inst'])
            alts = [x for x in alts if inst_family(x) == fam]
        if alts:
            cands.append((role, main, alts))
    rnd.shuffle(cands)
    for role, main, alts in cands[:n_roles]:
        w = [0.3 if x in recent.get(role, []) else 1.0 for x in alts]
        picks = []
        for k in range(2 if (mode == 'lots' or rnd.random() < 0.4) and len(alts) >= 2 and not club else 1):
            c = rnd.choices(alts, w)[0]
            i = alts.index(c)
            alts, w = alts[:i] + alts[i + 1:], w[:i] + w[i + 1:]
            picks.append(c)
            if not alts:
                break
        for k, inst in enumerate(picks):
            grp = ('C',) if club else (('A',) if (k == 0 and len(picks) > 1) else (('A', 'C') if k == 0 else ('C',)))
            st['tracks'].append(dict(main, name=f'{role}_sw{k + 1}', inst=inst, p={}, db=None, pooled=True,
                                     switch_of=role, groups=grp))


def switch_sections(evs, tracks, sections):
    alts = {}
    for n, t in tracks.items():
        if t.get('switch_of') in ('lead', 'chords', 'pad', 'arp'):
            if (tracks.get(t['switch_of']) or {}).get('user_pick'):
                continue                                  # you picked this part's sound: it plays every section
            for g in t.get('groups', ()):
                alts.setdefault(t['switch_of'], {})[g] = n
    if not alts:
        return
    spans = [(s_['bar'] * 4, (s_['bar'] + s_['bars']) * 4, section_group(s_)) for s_ in sections]
    notes = {}                                            # where each rotated part actually plays: {role: {group: notes}}
    for e in evs:
        if e.track in alts:
            g = next((g for b0, b1, g in spans if b0 <= e.beat < b1), None)
            if g:
                notes.setdefault(e.track, {})[g] = notes.get(e.track, {}).get(g, 0) + 1
    for role, to in alts.items():                         # the genre's own instrument always keeps its biggest sections
        have = notes.get(role, {})
        if have and set(have) <= set(to):
            to.pop(max(have, key=have.get), None)
    for e in evs:
        to = alts.get(e.track)
        if not to:
            continue
        g = next((g for b0, b1, g in spans if b0 <= e.beat < b1), None)
        if g in to:
            e.track = to[g]


def add_bass_switch_tracks(st):
    """Styles with 'bass_switch': extra bass voices (each a different timbre) that take over bars of the drop."""
    names = st.get('bass_switch') or []
    main = next((t for t in st['tracks'] if t['name'] == 'bass'), None)
    if not names or not main:
        return
    spare = [i for i in ('growl', 'wobble', 'fmbass', 'reese', 'screech') if i != main['inst'] and i not in names]
    names = [n if n != main['inst'] else spare.pop(0) for n in names]   # every voice a different timbre
    for i, inst in enumerate(names):
        st['tracks'].append(dict(name=f'bass_{"bcd"[i]}', layer='bass', inst=inst, pan=0.0, rev=0.0, dly=0.0,
                                 sc=main.get('sc') or 0.0, db=st.get('switch_db', main.get('db')), hp=None, drive=None,
                                 p={'sub': 0.0} if inst == 'wobble' else {}, switch_of='bass'))


def switch_basses(evs, tracks, sections, st):
    """In drops and climaxes, hand bars of the bass line to the other bass voices in a call-and-response order
    (main, B, main, C ...), so the drop moves between growls, wobbles and FM stabs instead of looping one sound.
    The clean sub layer was copied from the whole line first, so the low end stays continuous."""
    voices = [n for n, t in tracks.items() if t.get('switch_of') == 'bass']
    if not voices:
        return
    order = ['bass', voices[0], 'bass', voices[-1]] if len(voices) > 1 else ['bass', voices[0]]
    per = st.get('switch_bars', 1)
    for s_ in sections:
        if not (s_['opts'].get('drop') or s_['name'] in BIG_SECTIONS):
            continue
        b0, b1 = s_['bar'] * 4, (s_['bar'] + s_['bars']) * 4
        for e in evs:
            if e.track == 'bass' and b0 <= e.beat < b1:
                e.track = order[int((e.beat - b0) // (4 * per)) % len(order)]


HAT_INSTS = {'chat', 'ohat', 'chiphat', 'shaker', 'tamb', 'ride'}


def dj_effects(evs, fx, tracks, sections, amount, rnd, slow=None):
    """DJ-style edits (from the user's reference): bars where the hats climb or dive in pitch, swoop down inside each
    hit or drop an octave; lead notes that are down-tuned or up-tuned (the end of a note diving an octave, a note
    pulled up a fifth, a phrase played a whole tone flat); and a fake DJ slowdown - the record dragged by hand - in the
    bar before some of the drops."""
    hats = {n for n, t in tracks.items() if t.get('layer') == 'top' and t.get('inst') in HAT_INSTS}
    leads = {n for n, t in tracks.items() if t.get('layer') in ('lead', 'arp') and not t.get('no_dj')}
    for sec in sections:
        for b in range(sec['bars']):
            b0 = (sec['bar'] + b) * 4
            if hats and rnd.random() < 0.45 * amount:
                bar_h = sorted((e for e in evs if e.track in hats and b0 <= e.beat < b0 + 4), key=lambda e: e.beat)
                mv = rnd.choice(['climb', 'dive', 'swoop', 'octave', 'roll'])
                if mv == 'roll':                            # a pitched 16th / 32nd roll into the next bar, diving or climbing
                    name = next(iter(sorted(hats)))
                    evs[:] = [e for e in evs if not (e.track in hats and b0 + 3 <= e.beat < b0 + 4)]   # (1.83: only this
                    #                         bar's last beat - it used to delete every hat to the end of the song)
                    step = rnd.choice([0.25, 0.125])
                    k_n = int(1 / step)
                    d = rnd.choice([-1, 1])
                    for k in range(k_n):
                        evs.append(Ev(name, b0 + 3 + k * step, step * 0.8, None, 0.55 + 0.4 * k / k_n, None, f'pt:{d * k * (12 // k_n + 1)}'))
                else:
                    for i, e in enumerate(bar_h):
                        x = (e.beat - b0) / 4
                        if mv == 'climb':
                            e.mod = f'pt:{round(10 * x)}'
                        elif mv == 'dive':
                            e.mod = f'pt:{-round(12 * x)}'
                        elif mv == 'swoop':
                            e.mod = f'sw:0:{rnd.choice([-5, -7, -12])}'
                        else:
                            e.mod = 'pt:-12'
            if leads and rnd.random() < 0.3 * amount:
                bar_l = [e for e in evs if e.track in leads and b0 <= e.beat < b0 + 4 and e.midi is not None]
                if bar_l:
                    mv = rnd.choice(['downtune', 'uptune', 'flat', 'scoop'])
                    for e in bar_l:
                        if mv == 'flat':                    # the whole bar a whole tone flat - a pitched-down phrase
                            e.bend = [('shift', -2.0)] + list(e.bend or [])
                    if mv != 'flat':
                        e = max(bar_l, key=lambda e: e.dur)
                        if mv == 'downtune':
                            e.bend = list(e.bend or []) + [('fall', -12.0)]
                        elif mv == 'uptune':
                            e.bend = list(e.bend or []) + [('fall', 7.0)]
                        else:
                            e.bend = [('meend', -12.0, 0.5)] + list(e.bend or [])
        if (sec['opts'].get('drop') or sec['name'] in ('drop', 'grind')) and sec['bar'] > 0 and rnd.random() < (0.6 * amount if slow is None else slow):
            beg = sec['bar'] * 4 - rnd.choice([4, 2])
            fx[:] = [f for f in fx if not (f[0] == 'tapestop' and beg - 2 <= f[1] < sec['bar'] * 4)]
            fx.append(('djslow', beg, sec['bar'] * 4 - beg))


VOX_SCREW = {'switchup_808', 'switchup_808_dj', 'switchup_808_hard', 'switchup_mallets', 'trap_metal', 'screwed_slab', 'memphis_phonk', 'phonk', 'house_phonk', 'brazilian_phonk',
             'bass_warp_trap', 'bass_warp_fast', 'switch_trap', 'witch_house', 'cloud_rap', 'hard_trap', 'trap', 'plugg', 'rage',
             'uk_drill', 'wonky_beats', 'trip_hop', 'vaporwave', 'outsider_house'}
VOX_STUTTER = {'jersey_club', 'juke', 'juke_raw', 'juke_house', 'footwork', 'footwork_soulful', 'footwork_dark', 'baltimore_club',
               'bass_house', 'uk_bounce_house', 'chipmunk_2step', 'glitch_future_bass', 'future_bass', 'baile_funk', 'hyperpop',
               'speed_garage', 'uk_funky', 'gqom', 'breakcore', 'jungle', 'big_beat', 'ukgarage', 'bassline_140', 'grime',
               'funk_150', 'tech_house', 'house', 'garage_house', 'brostep', 'riddim', 'dubstep', 'jump_up', 'hardstyle'}
VOX_USES = ('screwed', 'stutter', 'adlib', 'phrase', 'melody')


def vox_use_for(style, category, vtype, use='auto'):
    """How a voice sample is used: your choice, else the genre's (screwed for phonk / switch-up 808 / Houston, stutter
    chops for club music), else what kind of sample it is (a sung note plays the melody, a quote opens the breaks)."""
    if use in VOX_USES:
        return use
    if vtype == 'note':
        return 'melody'
    if style in VOX_SCREW:
        return 'screwed'
    if style in VOX_STUTTER:
        return 'stutter' if vtype != 'speech' else 'phrase'
    if vtype == 'speech':
        return 'phrase'
    return 'stutter' if category == 'Electronic' and vtype == 'phrase' else 'adlib'


def voice_sample_part(evs, tracks, st, sections, opts, bpm, rnd):
    """Chop a short voice sample into the song. Uses: screwed (slowed and pitched down, the DJ catching words twice and
    letting the line drag out), stutter (rhythmic chops of its syllables - b-b-bounce it - and rolls into the drops),
    adlib (the whole sample as a one-shot on drops and turnarounds), phrase (the whole line, untouched, in the intro,
    the breaks and the outro) and melody (its first syllable played as an instrument on the lead's notes)."""
    from .usersounds import vocal_info
    name = opts.vox_sample
    info = vocal_info(name)
    if not info:
        return
    L, vtype, root, ons = info
    use = vox_use_for(st.get('name'), st.get('category'), vtype, getattr(opts, 'vox_use', 'auto'))
    pitch = getattr(opts, 'vox_pitch', 'auto') or 'auto'
    if pitch == 'auto':
        pitch = 'down' if use == 'screwed' else 'up' if st.get('name') == 'chipmunk_2step' else 'natural'
    base = {'down': -4, 'natural': 0, 'up': 6}.get(pitch, 0)
    dens = {'few': 0.5, 'normal': 1.0, 'lots': 1.8}.get(getattr(opts, 'vox_amount', 'normal'), 1.0)
    spb = 60.0 / bpm
    sl = [(a, (ons[i + 1] if i + 1 < len(ons) else L) - a) for i, a in enumerate(ons)] or [(0.0, L)]
    out = []

    def hit(beat, k=None, semis=None, rev=False, whole=False, cap=None):
        a, ln = (0.0, L) if whole else sl[(k or 0) % len(sl)]
        sm = base if semis is None else semis
        slow = 2 ** (-sm / 12)                           # tape-style: lower = longer
        beats = ln * slow / spb
        if cap is not None:
            beats = min(beats, cap)
        out.append(Ev('voxsample', beat, max(0.06, beats), 60 + int(round(sm)), 0.95, None,
                      f'vx:{a:.3f}:{ln:.3f}:{1 if rev else 0}'))

    mains = [x for x in sections if x['opts'].get('drop') or x['name'] in ('drop', 'chorus', 'hook', 'grind', 'leap', 'dance',
                                                                             'main', 'B', 'climax')]
    if not mains:                                        # songs without drops: the sections with the full beat
        mains = [x for x in sections[1:] if 'kick' in x['layers']] or sections[1:] or sections
    quiet = [x for x in sections if x not in mains]
    if use == 'phrase':
        for x in sections:
            if x is sections[0] or x['name'] in ('break', 'breakdown', 'bridge', 'outro', 'intro', 'taqsim', 'interlude') \
                    or (dens > 1.2 and x in mains):
                hit(x['bar'] * 4 + (4 if x['bars'] > 4 else 0), whole=True)
    elif use == 'adlib':
        for x in sections:
            if x in mains or rnd.random() < 0.3 * dens:
                hit(x['bar'] * 4, whole=True)
            every = max(4, int(8 / dens))
            for b in range(every - 1, x['bars'], every):
                if x in mains and rnd.random() < 0.8:
                    hit((x['bar'] + b) * 4 + 3, whole=True, rev=rnd.random() < 0.2,
                        semis=base + (rnd.choice([0, 0, -5, 7]) if rnd.random() < 0.3 else 0))
    elif use == 'screwed':
        first = sections[0]
        hit(first['bar'] * 4 + min(4, first['bars'] * 2), k=0, cap=1.0)       # the DJ catches the first word ...
        hit(first['bar'] * 4 + min(4, first['bars'] * 2) + 1, whole=True)     # ... and lets the whole line drag out
        for x in sections:
            every = max(4, int(8 / dens))
            for b in range(every - 1 if x in mains else every + 3, x['bars'], every):
                b0 = (x['bar'] + b) * 4
                mv = rnd.choice(['catch', 'drag', 'deep', 'echo'])
                if mv == 'catch':                        # "I-I-I'm ..."
                    hit(b0, k=0, cap=0.5)
                    hit(b0 + 0.5, k=0, cap=0.5)
                    hit(b0 + 1, whole=True, cap=3.0)
                elif mv == 'drag':
                    hit(b0 + 2, whole=True, semis=base - 2, cap=6.0)
                elif mv == 'deep':
                    hit(b0, k=len(sl) - 1, semis=base - 5, cap=4.0)
                else:                                    # the last word caught three times, sinking
                    for i in range(3):
                        hit(b0 + 2 + i * 0.5, k=len(sl) - 1, semis=base - i, cap=0.5)
        for x in mains:
            if x['bar'] > 0:
                hit(x['bar'] * 4 - 2, k=0, semis=base - 3, cap=2.0)          # a deep word into each drop
    elif use == 'stutter':
        pats = [[(0, 0, 3), (3, 0, 3), (6, 1, 2), (8, 0, 2), (10, 0, 2), (12, 2, 4)],
                [(0, 0, 2), (2, 0, 2), (4, 1, 4), (8, 0, 1), (9, 0, 1), (10, 0, 2), (12, 1, 2), (14, 2, 2)],
                [(0, 0, 4), (6, 0, 2), (8, 1, 2), (11, 0, 1), (12, 0, 1), (13, 0, 1), (14, 2, 2)]]
        for x in mains:
            pat = rnd.choice(pats)
            on_every = 1 if dens > 1.2 else 2 if dens > 0.7 else 4
            for b in range(0, x['bars'], on_every):
                b0 = (x['bar'] + b) * 4
                p = pat if b % 4 != 3 else rnd.choice(pats)
                for step, k, ln in p:
                    hit(b0 + step / 4, k=k, cap=ln / 4)
            if x['bar'] > 0:                             # a roll into the drop, rising
                for i in range(8):
                    hit(x['bar'] * 4 - 2 + i * 0.25, k=0, semis=base + i, cap=0.22)
        for x in quiet[:1]:
            hit(x['bar'] * 4 + 4, whole=True)
    elif use == 'melody':
        lead = sorted((e for e in evs if tracks.get(e.track, {}).get('layer') == 'lead' and e.midi is not None
                       and e.track != 'vocal'), key=lambda e: e.beat)
        ok = {id(x) for x in mains} if mains else {id(x) for x in sections}
        spans = [(x['bar'] * 4, (x['bar'] + x['bars']) * 4) for x in sections if id(x) in ok]
        for e in lead:
            if any(a <= e.beat < z for a, z in spans):
                m = e.midi
                while m - root > 12:
                    m -= 12
                while m - root < -12:
                    m += 12
                hit(e.beat, k=0, semis=m - root, cap=e.dur)
    if not out:
        return
    t = dict(name='voxsample', layer='lead', inst='voxsample', pan=0.0, rev=0.3 if use != 'screwed' else 0.45,
             dly=0.15 if use in ('screwed', 'adlib') else 0.05, sc=0.2, db=-15, hp=90, drive=None, p=dict(sample=name))
    st['tracks'].append(t)
    tracks['voxsample'] = t
    evs += out


def hand_up_bass(evs, tracks, st, opts):
    """Bass-warp / switch-up 808 genres: an 808 played up around D2 and above stops sounding like an 808 (thin, loud,
    squeaky). Those notes - the octave leaps, the raised switch-ups, breaks and outros - go to a second, mid-range bass
    instead (a reese, growl or FM bass, distorted like the reference's no-sub sections); the 808 keeps the low notes."""
    cfg = st['hi_bass'] if isinstance(st['hi_bass'], dict) else {}
    at = int(cfg.get('at', 38))
    main = tracks.get('bass')
    if not main or not is_808(main.get('inst', '')):
        return
    doubles = {n for n, t in tracks.items() if t.get('double_of') == 'bass'}
    hi = [e for e in evs if e.track == 'bass' and e.midi is not None and e.midi >= at]
    if cfg.get('only_marked'):                           # (1.83) only in the sections that ask for it (drill's wobble)
        rng_ = st.get('_up_ranges') or []
        hi = [e for e in hi if any(a <= e.beat < b for a, b in rng_)]
    if not hi:
        return
    pool = cfg.get('pool') or ['midbass', 'reese']
    inst = (opts.instruments or {}).get('bass_hi') or random.Random(opts.seed * 83 + 3).choice(pool)
    t = dict(name='bass_hi', layer='bass', inst=inst, pan=0.0, rev=0.1, dly=0.0, sc=0.5, db=float(cfg.get('db', -17)),
             hp=70, drive=None, p=dict(cfg.get('p') or {'cut': 1600}))
    st['tracks'].append(t)
    tracks['bass_hi'] = t
    gone = {(round(e.beat, 4)) for e in hi}
    for e in hi:
        e.track, e.glide, e.mod = 'bass_hi', None, None
        while e.midi > int(cfg.get('top', 52)):          # a mid-bass, not a lead: never above E3
            e.midi -= 12
        e.vel = min(1.0, e.vel)
    evs[:] = [e for e in evs if not (e.track in doubles and e.midi is not None and e.midi >= at and round(e.beat, 4) in gone)]
    if st.get('switchups'):                              # moving / folding notes can make two bars alike again
        rnd = random.Random(opts.seed * 89 + 1)
        bars = {}
        for e in evs:
            if e.track in ('bass', 'bass_hi') and e.midi is not None:
                bars.setdefault(int(e.beat // 4), []).append(e)
        prev = None
        for b in sorted(bars):
            sig = sorted((round(e.beat % 4, 2), e.midi, str(e.mod)) for e in bars[b])
            if sig == prev:
                es = sorted(bars[b], key=lambda e: e.beat)
                if len(es) > 1 and rnd.random() < 0.5:   # a gap at the end of the bar ...
                    evs.remove(es[-1])
                else:                                    # ... or one note an octave away
                    e = rnd.choice(es)
                    e.midi += 12 if e.midi + 12 <= 52 else -12
                sig = None
            prev = sig


MALLET_CELLS = ('roll', 'roll', 'trill', 'trill', 'hop', 'run', 'octave', 'rest')


def mallet_bar(key, tones, beat0, b, sname, si, big, rate, rest, memo, rnd):
    """One bar of mallet playing, modelled on the user's mallet reference - not a straight arpeggio: each beat is a
    cell, all on the beat - a roll (one note struck again and again, the mallet tremolo), a trill with its neighbour,
    a hop between two chord tones, a short run up to a note then a roll on it, an octave bounce, or a rest. A bar's
    four cells are a motif that repeats for two bars with small changes, and a new one comes every four bars; the
    note it sits on moves between chord tones like a melody. Quiet sections leave more rests."""
    from .theory import Ev
    per = max(2, int(round(4 / rate)))                    # strokes per beat (8 = 32nd notes)
    step = rate / 4
    sc = sorted({(key.root + x) % 12 for x in key.scale})
    tones = sorted(tones)

    def nb(m, d):                                         # the scale neighbour above (d=1) or below (d=-1)
        k = m + d
        while k % 12 not in sc:
            k += d
        return k
    mkey = (si, b // 4)
    if mkey not in memo:                                  # a new motif every four bars
        cells = []
        for j in range(4):
            c = rnd.choice(MALLET_CELLS)
            if c != 'rest' and rnd.random() < (rest if big else rest * 2.2):
                c = 'rest'
            cells.append(c)
        if cells.count('rest') > 2 or cells[0] == 'rest' and rnd.random() < 0.6:
            cells[0] = 'roll'
        memo[mkey] = dict(cells=cells, tone=rnd.randrange(len(tones)))
    mot = memo[mkey]
    cells = list(mot['cells'])
    if b % 2 == 1:                                        # the answering bar: one cell changes
        j = rnd.randrange(4)
        cells[j] = rnd.choice(MALLET_CELLS)
    ti = mot['tone']
    out = []
    for j, c in enumerate(cells):
        if j and rnd.random() < 0.45:                     # the held note walks to a neighbouring chord tone
            ti = max(0, min(len(tones) - 1, ti + rnd.choice([-1, 1])))
        m = tones[ti]
        t0 = beat0 + j
        seq = []
        if c == 'roll':
            seq = [m] * per
        elif c == 'trill':
            o = nb(m, rnd.choice([1, -1]))
            seq = [m if k % 2 == 0 else o for k in range(per)]
        elif c == 'hop':
            o = tones[(ti + 1) % len(tones)] if ti + 1 < len(tones) else m + 7
            half = per // 2
            seq = [m] * half + [o] * (per - half) if rnd.random() < 0.5 else [m if k % 2 == 0 else o for k in range(per)]
        elif c == 'run':
            r = [m]
            while len(r) < per // 2:
                r.insert(0, nb(r[0], -1))
            seq = r + [m] * (per - len(r))
        elif c == 'octave':
            seq = [m if k % 2 == 0 else m + 12 for k in range(per)]
        else:                                             # rest: the beat stays empty (sometimes one stroke)
            if rnd.random() < 0.3:
                out.append(Ev('arp', t0, step * 0.8, m, 0.75))
            continue
        for k, n in enumerate(seq):
            v = 1.0 if k == 0 else (0.8 if k * 2 == per else 0.62 + 0.08 * (k % 2))
            out.append(Ev('arp', t0 + k * step, step * 0.8, n, v * rnd.uniform(0.95, 1.0)))
    return out


def modular_drums(evs, tracks, sections, amount, rnd):
    """Modular-style sequencing for techno (and its relatives): the hats and percussion aren't a fixed loop any more.
    - probability: off-beat hat hits only play some of the time (each song its own odds), so the line breathes;
    - ratchets: now and then a hat hit rolls into 2-4 quick repeats inside its 16th;
    - polymeter: one percussion part loops every 3, 5 or 7 sixteenths, drifting against the 4/4 bar and only meeting
      it again after several bars;
    - parameter locks: a few steps of each loop are always accented (or ghosted), the same steps every bar.
    Kicks, claps and snares are left exactly where they are."""
    big = [s for s in sections if s['name'] not in ('intro', 'outro')]
    if not big:
        return
    inside = lambda b: any(s['bar'] * 4 <= b < (s['bar'] + s['bars']) * 4 for s in big)
    hats = [n for n, t in tracks.items() if t.get('layer') == 'top' and n in ('chat', 'ohat', 'shaker', 'ride', 'hat2', 'perc')]
    odds = {n: rnd.uniform(0.7, 0.92) for n in hats}
    locks = {n: {rnd.randrange(16): rnd.choice([1.25, 1.2, 0.55]) for _ in range(2)} for n in hats}
    out, drop = [], set()
    for i, e in enumerate(evs):
        if e.track not in odds or e.midi is not None or not inside(e.beat):
            continue
        step = int(round(e.beat * 4)) % 16
        if step in locks[e.track]:
            e.vel = min(1.2, e.vel * locks[e.track][step])
        if step % 4 != 0 and rnd.random() > odds[e.track] ** (1 + amount * 0.5):
            drop.add(i)
            continue
        if e.track == 'chat' and rnd.random() < 0.05 * amount:     # ratchet
            k = rnd.choice([2, 3, 4])
            drop.add(i)
            for j in range(k):
                out.append(e.copy(beat=e.beat + j * 0.25 / k, dur=0.25 / k, vel=e.vel * (1.0 - 0.12 * j)))
    evs[:] = [e for i, e in enumerate(evs) if i not in drop] + out
    perc = next((n for n in ('rim', 'perc', 'tom', 'conga', 'cowbell808') if n in tracks), None)
    if perc and amount >= 0.5:                                  # the polymetric loop
        L = rnd.choice([3, 5, 7, 5])
        hits = sorted(rnd.sample(range(L), max(1, L // 3)))
        evs[:] = [e for e in evs if not (e.track == perc and inside(e.beat))]
        for s in big:
            if s['opts'].get('build') and rnd.random() < 0.5:
                continue
            for k in range(s['bars'] * 16):
                if (k % L) in hits:
                    b = s['bar'] * 4 + k / 4
                    evs.append(Ev(perc, b, 0.25, None, (0.85 if k % L == hits[0] else 0.62) * rnd.uniform(0.92, 1.0)))


def granular_breaks(evs, tracks, sections, amount, rnd):
    """Drill & bass / IDM drum programming (from the user's notes on the genre): the break is treated as single hits
    and resequenced, so no two bars are the same - flams (a hit doubled a hair later), micro-stutters (a hit split into
    a 32nd / 48th burst), reversed and re-pitched single hits, kicks and snares swapping places, and quiet ghost hits
    filling the gaps between the main accents. The melody on top is left alone to sit and breathe."""
    from .theory import Ev
    kicks = {n for n, t in tracks.items() if t.get('layer') == 'kick'}
    snares = {n for n, t in tracks.items() if t.get('layer') == 'snare'}
    hats = {n for n, t in tracks.items() if t.get('layer') == 'top'}
    if not (kicks and snares):
        return
    sn = sorted(snares)[0]
    kk = sorted(kicks)[0]
    for sec in sections:
        if not ({'kick', 'snare'} & set(sec['layers'])):
            continue
        dens = amount * (1.0 if sec['opts'].get('drop') else 0.7)
        for b in range(sec['bars']):
            b0 = (sec['bar'] + b) * 4
            bar_d = [e for e in evs if (e.track in kicks or e.track in snares) and b0 <= e.beat < b0 + 4]
            if not bar_d:
                continue
            taken = {round((e.beat - b0) * 8) for e in bar_d}
            ops = rnd.sample(['flam', 'stutter', 'reverse', 'pitch', 'swap', 'ghosts', 'ghosts', 'stutter'],
                             k=max(1, min(5, int(round(1 + 4 * dens * rnd.random())))))
            for op in ops:
                e = rnd.choice(bar_d)
                if op == 'flam':                          # the same hit again ~1/64 note later, softer
                    evs.append(e.copy(beat=e.beat + 0.0625, vel=e.vel * 0.7))
                elif op == 'stutter' and e.beat + 0.25 < b0 + 4:
                    k = rnd.choice([3, 4, 6])
                    sp = rnd.choice([0.125, 1 / 12, 0.0625])
                    for i in range(1, k):
                        evs.append(e.copy(beat=e.beat + i * sp, vel=e.vel * (0.85 - 0.08 * i), mod='cut'))
                elif op == 'reverse' and e.track in snares:
                    e.mod = 'rev'
                elif op == 'pitch':
                    e.mod = f'pt:{rnd.choice([-7, -5, -3, 3, 5, 7, 12])}'
                elif op == 'swap':                        # kick <-> snare interchange
                    e.track = sn if e.track in kicks else kk
                    e.mod = None
                elif op == 'ghosts':                      # quiet hits filling the gaps between the accents
                    for _ in range(rnd.randint(2, 5)):
                        q = rnd.randrange(32)
                        if q // 4 in taken or q in taken:
                            continue
                        evs.append(Ev(sn, b0 + q / 8, 0.1, None, rnd.uniform(0.18, 0.35), None, 'cut'))
            if hats and rnd.random() < 0.35 * dens:       # a hat ratchet somewhere in the bar
                h = sorted(hats)[0]
                t0 = b0 + rnd.randrange(8) / 2
                for i in range(rnd.choice([4, 6, 8])):
                    evs.append(Ev(h, t0 + i / 16, 0.05, None, 0.3 + 0.05 * i, None, None))


METER_NAMES = {16: '4/4', 15: '15/16', 14: '7/8', 13: '13/16', 12: '3/4', 11: '11/16', 10: '5/8', 9: '9/16'}


def cut_meters(evs, fx, sections, st, rnd):
    """Odd time signatures (math rock): some bars are cut short - a 7/8 bar keeps the first 14 sixteenths of the bar,
    a 3/4 (6/8) bar the first 12, a 5/8 bar the first 10 - and the bar is then played that much faster, so every 16th
    keeps its length and the bar really is shorter. Each section cycles through a meter pattern (e.g. 4/4, 4/4, 4/4,
    7/8 or 7/8 all the way, or 3/4 + 7/8), from its own 'meters' or picked from the genre's list. Intros, breaks and
    outros mostly stay in 4/4, so the odd bars land in the riffs. Returns {bar: sixteenths} for the tempo map."""
    cycles = st['cut_meters'] if isinstance(st['cut_meters'], (list, tuple)) else [[16, 16, 16, 14]]
    steps = {}
    for sec in sections:
        cyc = sec['opts'].get('meters')
        if cyc is None:
            calm = sec['name'] in ('intro', 'outro') or sec['opts'].get('fade')
            cyc = [16] if calm and rnd.random() < 0.7 else list(rnd.choice(cycles))
        for b in range(sec['bars']):
            steps[sec['bar'] + b] = int(cyc[b % len(cyc)])
    cut = {b: n for b, n in steps.items() if n < 16}
    if not cut:
        return steps
    keep = []
    for e in evs:
        b = int(e.beat // 4)
        n = cut.get(b)
        if n is None:
            keep.append(e)
            continue
        b0 = b * 4
        pos = (e.beat - b0) * 4                              # in sixteenths
        if pos >= n - 1e-6:
            continue                                         # the cut-off end of the bar
        f = 16.0 / n
        e.beat = b0 + pos * f / 4
        e.dur = min(e.dur * f, b0 + 4 - e.beat) if e.beat + e.dur * f > b0 + 4 else e.dur * f
        keep.append(e)
    evs[:] = keep
    out = []
    for kind, b_, d in fx:
        n = cut.get(int(b_ // 4))
        if n is not None:
            pos = (b_ - int(b_ // 4) * 4) * 4
            if pos >= n:
                pos = n - 1
            b_ = int(b_ // 4) * 4 + pos * (16.0 / n) / 4
        out.append((kind, b_, d))
    fx[:] = out
    return steps


def tap_bar(key, tones, beat0, b, si, memo, rnd, vel=1.0):
    """Math-rock two-hand tapping: a cell of 5, 6 or 7 sixteenths (fretting hand low - root and fifth - tapping hand high
    - the 9th, the 3rd, the octave and above, two octaves wide) repeating straight through the bar lines, so it drifts
    against the 4/4 (or odd) bar like an interlocking loop. A new cell every few bars; the chord under it re-voices it."""
    from .theory import Ev
    st_ = memo.setdefault(('tap', si), dict(cell=None, at=0, k=0))
    if st_['cell'] is None or b % 4 == 0 and rnd.random() < 0.5:
        L = rnd.choice([5, 6, 7, 6, 7, 8])
        shape = rnd.choice(['updown', 'leap', 'pedal'])
        st_['cell'] = (L, shape)
    L, shape = st_['cell']
    t = sorted(tones)
    root = t[0] - 12
    sc = sorted({(key.root + x) % 12 for x in key.scale})
    nine = t[0] + 2 if (t[0] + 2) % 12 in sc else t[0] + 1
    hi = [t[1] + 12, nine + 12, t[0] + 24, t[2] + 12 if len(t) > 2 else t[1] + 19]
    lo = [root, root + 7, t[0]]
    if shape == 'updown':
        cell = lo[:2] + hi[:3] + hi[1:2] + lo[2:]
    elif shape == 'leap':
        cell = [lo[0], hi[0], lo[1], hi[2], hi[1], lo[2], hi[3]]
    else:
        cell = [lo[0], hi[1], hi[0], lo[0], hi[2], hi[1], hi[0], lo[1]]
    cell = cell[:L] + [cell[k % len(cell)] for k in range(max(0, L - len(cell)))]
    out = []
    for q in range(16):
        k = st_['k']
        n = cell[k % L]
        acc = k % L == 0
        out.append(Ev('arp', beat0 + q / 4, 0.5 if n >= t[0] + 12 else 0.4, n,
                      (1.0 if acc else 0.72 + 0.1 * (n < t[0])) * vel * rnd.uniform(0.94, 1.0)))
        st_['k'] += 1
    return out


def screw_chops(evs, sections, amount, rnd):
    """Chopped & screwed: in some bars the DJ pulls the record back and plays a beat (or two) again - everything in
    that beat is repeated straight after itself, replacing what would have come next. Never in the first bar of a
    section, so every section still starts clean."""
    for sec in sections:
        for b in range(1, sec['bars']):
            if rnd.random() >= amount:
                continue
            ln = rnd.choice([1, 1, 2])
            k = rnd.choice([0, 2] if ln == 2 else [0, 1, 2])
            b0 = (sec['bar'] + b) * 4 + k
            src = [e for e in evs if b0 <= e.beat < b0 + ln]
            if not src:
                continue
            evs[:] = [e for e in evs if not (b0 + ln <= e.beat < b0 + 2 * ln)]
            for e in src:
                evs.append(e.copy(beat=e.beat + ln, dur=min(e.dur, b0 + 2 * ln - e.beat - ln)))


SWITCH_MOVES = ('grind', 'leap', 'roll', 'gap', 'stop', 'dive', 'wob', 'fold', 'chop', 'rise', 'plain')


def bar_switchups(evs, tracks, sections, st, rnd):
    """Shadow-808 switch-ups (from the user's reference): every bar of the 808 does something different from the bar
    before - grinding root / flat-2nd 8ths, leaping one or two octaves up, a 16th roll, a sudden gap or a full stop
    (drums out), a dive, a wobble, a folded / distorted bar, chopped stabs, a rise - and the last bar of each 4-bar
    phrase leaves space. Runs before the layers copy the bass, so the grit layer follows every move."""
    cfg = st['switchups'] if isinstance(st['switchups'], dict) else {}
    moves = list(cfg.get('moves') or SWITCH_MOVES)
    weights = cfg.get('weights') or {}
    bass_names = {n for n, t in tracks.items() if t.get('layer') == 'bass' and not t.get('double_of')}
    drums = {n for n, t in tracks.items() if t.get('layer') in ('kick', 'snare', 'top')}
    prev = prev_sig = None
    for sec in sections:
        if 'bass' not in sec['layers'] or sec['opts'].get('fade'):
            continue
        for b in range(sec['bars']):
            b0 = (sec['bar'] + b) * 4
            bar_b = [e for e in evs if e.track in bass_names and b0 <= e.beat < b0 + 4 and e.midi is not None]
            if not bar_b:
                continue
            last = b % 4 == 3
            mvs = sec['opts'].get('moves') or moves
            pool = [m for m in (('gap', 'stop', 'dive', 'roll') if last else mvs) if m != prev] or ['plain']
            w = [float(weights.get(m, 1.0)) for m in pool]
            mv = rnd.choices(pool, w)[0]
            prev = mv
            bar_b.sort(key=lambda e: e.beat)
            root = min(e.midi for e in bar_b)
            name = bar_b[0].track
            if mv == 'grind':                               # root and flat 2nd, 8th notes, grinding against each other
                for e in bar_b:
                    evs.remove(e)
                start = 1 if rnd.random() < 0.3 else 0
                for k in range(start, 8):
                    m = root + (1 if k % 2 else 0)
                    evs.append(Ev(name, b0 + k * 0.5, 0.48, m, 0.92 if k % 2 else 1.0, root if k % 2 else None))
            elif mv == 'leap':                              # notes leap an octave or two up and slide back down
                for i, e in enumerate(bar_b):
                    if i % 2 == 1 or rnd.random() < 0.35:
                        old = e.midi
                        e.midi = min(e.midi + rnd.choice([12, 24, 24]), 50)
                        e.glide = old
            elif mv == 'roll':                              # the last beat (or two) turns into a 16th roll
                n = rnd.choice([4, 8])
                t0 = b0 + 4 - n * 0.25
                for e in bar_b:
                    if e.beat >= t0:
                        evs.remove(e)
                    elif e.beat + e.dur > t0:
                        e.dur = t0 - e.beat
                m = bar_b[-1].midi
                for k in range(n):
                    evs.append(Ev(name, t0 + k * 0.25, 0.22, m + (12 if k == n - 1 and rnd.random() < 0.5 else 0), 0.85 + 0.15 * (k % 2)))
            elif mv in ('gap', 'stop'):                     # space: the 808 (and drums) cut out for the end of the bar
                cut = b0 + (rnd.choice([2, 3]) if mv == 'gap' else 1)
                for e in bar_b:
                    if e.beat >= cut:
                        evs.remove(e)
                    elif e.beat + e.dur > cut:
                        e.dur = cut - e.beat
                if mv == 'stop':
                    bar_b[0].mod = 'dive'
                dz = cut if mv == 'stop' else b0 + 3.5
                evs[:] = [e for e in evs if not (e.track in drums and dz <= e.beat < b0 + 4)]
            elif mv == 'dive':
                bar_b[-1].mod = 'dive'
                bar_b[-1].dur = max(bar_b[-1].dur, b0 + 4 - bar_b[-1].beat - 0.05)
            elif mv == 'rise':
                bar_b[-1].mod = 'rise'
            elif mv == 'wob':
                r = rnd.choice([3, 4, 6, 8])
                for e in bar_b:
                    e.mod = f'wob:{r}'
            elif mv == 'fold':                              # folded, distorted 808 - more mid, less clean sub
                for e in bar_b:
                    e.mod = 'fold'
            elif mv == 'chop':                              # gated 8th / 16th stabs of the same notes
                g = rnd.choice([0.5, 0.25])
                for e in bar_b:
                    evs.remove(e)
                    k = 0
                    while k * g < e.dur - 0.05:
                        if not (k % 3 == 2 and g == 0.25):
                            evs.append(e.copy(beat=e.beat + k * g, dur=g * 0.6, glide=None, mod=None))
                        k += 1
            now = sorted((round(e.beat - b0, 2), e.midi, e.mod) for e in evs if e.track in bass_names and b0 <= e.beat < b0 + 4)
            if now and now == prev_sig:                     # still the same as the bar before: one note leaps an octave
                es = [e for e in evs if e.track in bass_names and b0 <= e.beat < b0 + 4]
                e = rnd.choice(es)
                e.glide, e.midi = e.midi, e.midi + 12
                now = None
            prev_sig = now


CLASH_LAYERS = ('lead', 'arp')


def fix_clashes(evs, tracks, key, st, sections):
    """Keep held melody notes in tune with the harmony under them.

    A lead / arp / vocal note that is held (or sits on the beat) a semitone away from a chord, pad or held bass note
    that is sounding at the same moment - and isn't itself one of those notes - moves to the nearest note that fits:
    a chord tone first, otherwise a scale note that doesn't rub. Short passing notes, slides and bebop approach
    notes are left alone (that's what makes them passing notes), and so are the blue notes in blues-flavoured genres."""
    import bisect
    harm = []
    for e in evs:
        t = tracks.get(e.track)
        if e.midi is None or not t:
            continue
        lay = t['layer']
        if lay in ('chords', 'pad') or (lay == 'bass' and e.dur >= 0.75):
            harm.append((e.beat, e.beat + e.dur, e.midi % 12))
    if not harm:
        return 0
    harm.sort()
    starts = [h[0] for h in harm]
    maxdur = max(h[1] - h[0] for h in harm)

    def sounding(t):
        i = bisect.bisect_right(starts, t)
        out = set()
        j = i - 1
        while j >= 0 and starts[j] >= t - maxdur:
            if harm[j][1] > t:
                out.add(harm[j][2])
            j -= 1
        return out
    shift_at = []                                         # key changes move the scale too
    for s in sections:
        if s.get('key_change'):
            shift_at.append((s['bar'] * 4, s['key_change']))
    base_pcs = {(key.root + iv) % 12 for iv in key.scale}
    blue = {(key.root + 3) % 12, (key.root + 10) % 12} if st.get('melody_lang') == 'blues' else set()

    def scale_at(t):
        sh = sum(k for b, k in shift_at if t >= b)
        return {(p + sh) % 12 for p in base_pcs}, {(p + sh) % 12 for p in blue}
    short = 0.3 if st.get('melody_lang') == 'bebop' else 0.2   # bebop approach notes are 0.22 beats on purpose
    fixed = 0
    for e in evs:
        t = tracks.get(e.track)
        if e.midi is None or not t or not (t['layer'] in CLASH_LAYERS or e.track == 'vocal'):
            continue
        on_beat = abs(e.beat - round(e.beat)) < 0.01
        if e.dur < short and not (on_beat and e.dur >= 0.2):
            continue
        snd = sounding(e.beat + 0.01)
        if e.dur >= 1.0:
            snd |= sounding(e.beat + e.dur * 0.5)
        pc = e.midi % 12
        if not snd or pc in snd:
            continue
        rubs = lambda p: any((p - q) % 12 in (1, 11) for q in snd)
        scl, bl = scale_at(e.beat)
        if not rubs(pc) or pc in bl:
            continue
        best = None
        for mv in (-1, 1, -2, 2, -3, 3):
            p = (pc + mv) % 12
            if rubs(p):
                continue
            score = (0 if p in snd else 1 if p in scl else 3) + abs(mv) * 0.4
            if best is None or score < best[0]:
                best = (score, mv)
        if best is None:
            continue
        e.midi += best[1]
        if e.glide is not None:
            e.glide += best[1]
        fixed += 1
    return fixed


def apply_variation(evs, b0, b1, seed, key, st, tracks):
    """Subtle variation of one section: a few drum hits moved/added, bass octave flips, melody notes nudged by a scale step."""
    r = random.Random(seed)
    from .instruments import DRUMS
    pcs = sorted({(key.root + iv) % 12 for iv in key.scale})
    out = []
    added = []
    for e in evs:
        if not (b0 <= e.beat < b1):
            out.append(e)
            continue
        t = tracks.get(e.track)
        layer = t['layer'] if t else ''
        if t and t['inst'] in DRUMS:
            if layer == 'top' and e.vel < 0.9 and r.random() < 0.12:
                continue
            if layer in ('top', 'snare') and r.random() < 0.08:
                added.append(Ev(e.track, e.beat + r.choice([0.25, 0.5, -0.25]), e.dur, None, e.vel * 0.55))
            out.append(e)
        elif layer == 'bass' and e.midi is not None and r.random() < 0.18:
            m = e.midi + (12 if e.midi < st['bass_lo'] + 10 else -12)
            out.append(Ev(e.track, e.beat, e.dur, m, e.vel, e.glide, e.mod))
        elif layer in ('lead', 'arp') and e.midi is not None and r.random() < 0.28:
            d = r.choice([-1, 1])
            m = e.midi + d
            while m % 12 not in pcs:
                m += d
            out.append(Ev(e.track, e.beat, e.dur, m, e.vel, e.glide, e.mod))
        elif layer == 'chords' and e.midi is not None and r.random() < 0.12:
            out.append(Ev(e.track, e.beat, e.dur, e.midi + r.choice([-12, 12]), e.vel, e.glide, e.mod))
        else:
            out.append(e)
    return out + [a for a in added if b0 <= a.beat < b1]


VOCAL_SECTIONS = {'verse': (-2, 5), 'chorus': (1, 9), 'hook': (1, 9), 'drop': (1, 9), 'head': (0, 7), 'A': (0, 7),
                  'theme': (0, 8), 'climax': (2, 9)}
VOCAL_RHYTHMS = ['x.x.x.x-x-......', 'x-x-x.x.x---....', '..x.x.x.x-x-....', 'x.x.x-x.x.x-....', 'x---x.x.x-x-....',
                 '..x.x-x-x.x.x...', 'x.x.x.x.x.x-....', 'x-.xx-x-x---....']


VOCAL_TRIPLE = ['x-xx-xx-x---', 'x--x--x-x---', 'x-xx-x-xx---', 'xx-x--x--x--', 'x-xx-xx-xx--']
VOCAL_TRIPLE_END = ['x-xx-x------', 'x--x--x-----', 'x-----x-----', 'x-xx--x-----']


def gen_vocal(key, sections, chord_bars, st, rnd):
    """A singable guide melody: verses low, choruses higher; 2-bar phrases with a breath; the chorus melody repeats."""
    out, memory = [], {}
    for sec in sections:
        rng = VOCAL_SECTIONS.get(sec['name'])
        if not rng or not sec.get('prog'):
            continue
        lo, hi = rng
        kind = 'chorus' if rng[0] >= 1 else sec['name']
        if kind not in memory:
            phrase = []
            d = rnd.randint(lo + 1, min(hi, lo + 4))
            for bar in range(4):                             # a 4-bar idea (two 2-bar phrases), repeated over the section
                prog = sec['prog']
                chord = prog[(bar // max(1, chord_bars)) % len(prog)]
                ct = [x for x in chord_tones_deg(chord, lo, hi)]
                if st.get('meter'):
                    pat = parse_rhythm(rnd.choice(VOCAL_TRIPLE if bar % 2 == 0 else VOCAL_TRIPLE_END))
                else:
                    pat = parse_rhythm(rnd.choice(VOCAL_RHYTHMS)) if bar % 2 == 0 else \
                        parse_rhythm(rnd.choice(['x-x-x---........', 'x.x.x-x-x-------', 'x-x-x-x---------', 'x---x---x-------']))
                for i, (step, ln, c) in enumerate(pat):
                    d += rnd.choices([-2, -1, 0, 1, 2], [1, 4, 2, 4, 1])[0]
                    d = max(lo, min(hi, d))
                    if step % 4 == 0 and ct:
                        d = min(ct, key=lambda x: (abs(x - d), x))
                    end = bar % 2 == 1 and i == len(pat) - 1
                    if end and ct:
                        d = min(ct, key=lambda x: abs(x - d))
                    phrase.append((bar * 4 + step / 4, ln / 4 * 0.9, d, 0.85 if step % 4 == 0 else 0.72))
            memory[kind] = phrase
        phrase = memory[kind]
        start = sec['bar'] * 4
        for rep in range(0, sec['bars'], 4):
            for (bt, du, d, v) in phrase:
                b = start + rep * 4 + bt
                if b < start + sec['bars'] * 4 - 0.01:
                    out.append(Ev('vocal', b, du, key.deg(d, 4), v))
    return out


def lock_bass_to_kick(evs, tracks, st):
    """Electronic styles: a bass note that lands a hair before/after a kick is moved onto it, so the low end hits as one."""
    if st.get('category') != 'Electronic':
        return
    kick = st.get('kick_track', 'kick')
    kicks = sorted(e.beat for e in evs if e.track == kick)
    if not kicks:
        return
    import bisect
    bass = _track_of({t['name']: t for t in st['tracks']}, 'bass')
    for e in evs:
        if e.track != bass or e.midi is None:
            continue
        i = bisect.bisect_left(kicks, e.beat)
        near = min((kicks[j] for j in (i - 1, i) if 0 <= j < len(kicks)), key=lambda k: abs(k - e.beat))
        if 1e-6 < abs(near - e.beat) <= 0.13:
            e.dur += e.beat - near
            e.beat = near


ENERGY_ORDER = ['pad', 'chords', 'fx', 'lead', 'top', 'bass', 'arp', 'snare', 'kick']


def apply_energy_curve(form, curve, st):
    """(2.0) Arrange the song to the energy curve you drew. Each section reads the curve at its own place in the song:
         < 0.22  just the harmony: pads / chords (and FX) - an intro, a breakdown, an ending
         < 0.45  no kick or snare: harmony, hats, bass - a build or a breather
         < 0.70  the section as the genre wrote it
         >= 0.70 the full groove: kick, snare, hats and bass all in;  >= 0.85 everything the genre has
    A dip in the middle of a long drop becomes a breakdown, a slow rise becomes a slow build - the genre's parts, your
    shape. Sections keep their names, lengths and music; only who plays changes."""
    try:
        c = [min(1.0, max(0.0, float(v))) for v in curve][:64]
    except (TypeError, ValueError):
        return form
    if len(c) < 2:
        return form
    have = {t.get('layer') for t in st.get('tracks', [])}
    total = sum(max(1, int(b)) for (_, b, _, _) in form) or 1
    out, pos = [], 0
    for (n, b, layers, o) in form:
        mid = (pos + b / 2) / total
        pos += b
        x = mid * (len(c) - 1)
        i = int(x)
        e = c[i] + (c[min(i + 1, len(c) - 1)] - c[i]) * (x - i)
        lay = set(layers)
        if e < 0.22:
            new = {l for l in lay if l in ('pad', 'chords', 'fx')} or ({'pad', 'chords', 'lead'} & have) or lay
        elif e < 0.45:
            new = (lay - {'kick', 'snare'}) | ({'top', 'bass'} & have)
            if not new & {'pad', 'chords'}:
                new |= {'pad', 'chords'} & have
        elif e < 0.70:
            new = lay
        else:
            new = lay | ({'kick', 'snare', 'top', 'bass'} & have)
            if e >= 0.85:
                new |= {'chords', 'arp', 'lead', 'pad'} & have
        out.append((n, b, new, dict(o, energy=round(e, 2))))
    return out


# per-genre timing feel: offsets in fractions of a 16th note, for each of the 16 steps of a bar, per part
GROOVES = {
    'dilla': {'snare': [0, 0, 0, 0, .22, 0, 0, 0, 0, 0, 0, 0, .22, 0, 0, 0], 'top': [0, .14] * 8, 'bass': [.1] * 16,
              'chords': [.08] * 16},
    'laidback': {'snare': [0, 0, 0, 0, .14, 0, 0, 0, 0, 0, 0, 0, .14, 0, 0, 0], 'chords': [.1] * 16, 'top': [0, .06] * 8},
    'afro': {'top': [0, .14, 0, -.04] * 4, 'snare': [0, 0, 0, .1] * 4, 'bass': [0, .06] * 8},
    'dembow': {'snare': [0, 0, 0, -.06, 0, 0, -.06, 0, 0, 0, 0, -.06, 0, 0, -.06, 0]},
    'jazz': {'top': [-.06] * 16, 'bass': [-.03] * 16, 'snare': [.1] * 16, 'chords': [.05] * 16},
    'house': {'top': [0, 0, .07, 0] * 4, 'chords': [0, 0, .04, 0] * 4},
    'funk': {'top': [0, -.05] * 8, 'bass': [-.02] * 16, 'snare': [0, .06] * 8},
    # (2.0) the classic feels producers reach for, as offsets of a 16th (MPC swing % = how late the off-16ths land)
    'mpc54': {'top': [0, .08] * 8, 'snare': [0, .08] * 8, 'kick': [0, .08] * 8, 'bass': [0, .08] * 8, 'chords': [0, .08] * 8},
    'mpc58': {'top': [0, .16] * 8, 'snare': [0, .16] * 8, 'kick': [0, .16] * 8, 'bass': [0, .16] * 8, 'chords': [0, .16] * 8},
    'mpc62': {'top': [0, .24] * 8, 'snare': [0, .24] * 8, 'kick': [0, .24] * 8, 'bass': [0, .24] * 8, 'chords': [0, .24] * 8},
    'boombap': {'top': [0, .2] * 8, 'snare': [0, 0, 0, 0, .16, 0, 0, 0, 0, 0, 0, 0, .16, 0, 0, 0], 'kick': [0, .12] * 8,
                'bass': [.05] * 16},
    'drunk': {'top': [.04, .3, -.06, .22] * 4, 'snare': [0, 0, 0, 0, .3, 0, 0, 0, 0, 0, 0, 0, .26, 0, 0, 0], 'kick': [-.05, .1] * 8,
              'bass': [.14] * 16, 'chords': [.12] * 16},
    'ukg': {'top': [0, .32] * 8, 'kick': [0, .32] * 8, 'snare': [0, .1] * 8, 'bass': [0, .32] * 8},
    'techno_shuffle': {'top': [0, .12, -.04, .12] * 4, 'kick': [0] * 16, 'snare': [-.02] * 16},
    'trap_tight': {'top': [-.03] * 16, 'snare': [.04] * 16},
    'drill': {'top': [0, .1, 0, -.04] * 4, 'snare': [.08] * 16, 'kick': [0, .06] * 8},
    'dnb_roll': {'snare': [-.06] * 16, 'top': [0, .05] * 8},
}
STYLE_GROOVE = {'jazz_hop': 'dilla', 'jazz_rap': 'dilla', 'slow_jam': 'laidback', 'smooth_jazz': 'laidback', 'quiet_storm': 'laidback', 'smooth_funk': 'funk', 'neo_soul': 'dilla', 'g_funk': 'laidback', 'hauntology_sunlit': 'dilla', 'hauntology_dark': 'laidback', 'disco_funk': 'funk', 'organic_house': 'house', 'boombap': 'boombap', 'lofi': 'dilla', 'phonk': 'dilla', 'reggae': 'laidback', 'downtempo': 'laidback',
                'afrobeats': 'afro', 'amapiano': 'afro', 'reggaeton': 'dembow', 'moombahton': 'dembow', 'jazz': 'jazz',
                'house': 'house', 'deep_house': 'house', 'tech_house': 'house', 'ukgarage': 'house',
                'funk': 'funk', 'disco': 'funk', 'city_pop': 'funk', 'rnb': 'laidback', 'gospel': 'laidback',
                'swing': 'jazz', 'afro_house': 'afro', 'dancehall': 'dembow', 'cumbia': 'afro', 'hauntology': 'dilla',
                # (2.0) the classic feels as genre defaults
                'trap': 'trap_tight', 'hard_trap': 'trap_tight', 'uk_drill': 'drill', 'dark_drill': 'drill', 'techno': 'techno_shuffle',
                'minimal': 'techno_shuffle', 'hypnotic_techno': 'techno_shuffle', 'dnb': 'dnb_roll', 'neurofunk': 'dnb_roll',
                'soul_sample_rap': 'boombap', 'smooth_90s_rap': 'boombap', 'speed_garage': 'ukg', 'bassline_140': 'ukg'}




from .guitars2 import NEW as _GTR20  # noqa: E402
from .styles import GTR_UPGRADE as _GTR_UP  # noqa: E402
from .pool_variety import widen as _widen_pools  # noqa: E402  (needs SIGNATURE_STRICT above)
_widen_pools()
from .styles import _offer_genre_sounds  # noqa: E402
_offer_genre_sounds()
from .electro_sounds import apply as _electronic_basses  # noqa: E402  (last pool step)
_electronic_basses()
