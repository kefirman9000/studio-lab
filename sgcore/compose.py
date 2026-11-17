"""Composition: harmony, melody, bass, drums and arrangement -> a list of note events."""
import math
import random
from dataclasses import dataclass, field, asdict, replace

from .styles import STYLES, FORMS, FORM_VARIANTS
from .instruments import KITS, INSTRUMENTS, PALETTES
from .theory import (Key, parse_progression, parse_key, color_fits, declutter, voice_chord, VOICINGS, fold, parse_rhythm,
                     grid_of, grid_steps, lead_voicing, Ev, chord_tones_deg, COLORS)
from .figures import gen_riff, vary_melody, gen_trap_hats, gen_acid_pattern
from .arrange import (BIG_SECTIONS, _track_of, BUILD_STYLES, FX_SOUNDS, build_sequence, GENRE_BUILD, add_build_drums, add_build_fx,
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
    kit: str = None               # drum kit preset
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
    variety: float = 0.5          # 0..1 how adventurous each song's sound palette, grooves and arrangement get
    user_drums: bool = False      # use the drum samples you loaded instead of the built-in kit
    sections: list = None         # section editor: [{src, copy, bars, seeds{part:int}, vary:int, mute:[layers]}]
    engine: str = 'auto'          # auto | sampled | synth  (sampled = real recorded instruments when the library is installed)
    vst_rig: bool = False         # play parts through genre-matched plugins (sgcore.vstrigs) when they're installed
    orch_plugin: bool = False     # orchestral parts on your orchestra plugin (BBC SO / LABS) instead of the free real orchestra
    melody_style: str = None      # None = genre default | diatonic | pentatonic | blues | bebop
    voicing: str = None           # None = genre default | close | open | drop2 | rootless | power
    chord_color: str = None       # None = varies per song | triad | 7 | add9 | 9 | 6 | sus2 | sus4
    traits: dict = None           # genre-trait overrides {category: value} (see sgcore/traits.py); {'_surprise': True} = random
    part_levels: dict = field(default_factory=dict)   # layer -> dB offset (-12..+6), e.g. {'lead': -3}
    part_fx: dict = field(default_factory=dict)       # layer -> effect plugin name (e.g. {'lead': 'ValhallaSupermassive'})
    ending: str = 'auto'          # auto | hit (final chord + crash) | fade
    vocal_guide: bool = False     # also play the vocal guide melody (it is always in the MIDI export)
    bass_rhythm: str = None       # None = style | kick (bass plays with the kick drum)
    lead_style: str = None        # None = genre | hook | arp | riff | ostinato | bell | call | chops
    build_style: str = None       # None = genre (varies per song) | roll | triplet | kick_roll | filter | stutter | pause | lift | swell | hats | claps | toms | halftime | drumless | pickup | ride | march | tomgroove | pulse | stops | tapestop | cymbal | wash | none
    builds: str = 'auto'          # build-ups into big sections: auto | subtle (natural, no EDM ramps) | off
    transition_fx: str = 'auto'   # risers, reverse cymbals, impacts, tape stops ...: auto | fewer | fills (drum fills only) | off
    groove: str = None            # None = genre feel | straight | dilla | laidback | afro | dembow | jazz | house | funk
    mood: str = None              # dark | happy | chill | epic | dreamy | aggressive | melancholic | energetic | mysterious | romantic
    counter: str = None           # None = genre decides | on | off  (a second line answering the lead: celli, horns, flute ...)
    layering: str = None          # None = genre + variety decide | off | more  (parts doubled by a second instrument)
    simplicity: float = 0.0       # 0..1 strip it back: triads, fewer & longer notes, held chords, no extras
    repetition: float = 0.5       # 0..1 how much the melody repeats its opening idea (catchy loop <-> developing line)
    melody_range: float = 0.5     # 0..1 narrow (a few notes) <-> wide (big leaps)
    chord_speed: str = None       # None = style | slow (chords last twice as long) | fast (change twice as often)
    rotation: str = 'auto'        # instrument rotation between sections: auto | off | some | lots
    avoid: dict = field(default_factory=dict)          # role -> instruments your recent songs used (picked less often)
    title: str = None             # song name (front of every exported file name); None = an invented name that fits the song
    journey: dict = None          # Cinematic Journey settings: acts, piano, rubato, dynamics, ending, woodwinds (see journey.py)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**known)


MELODY_STYLES = ['diatonic', 'pentatonic', 'blues', 'bebop']
# how each genre's lead player phrases, and how its keyboard player voices chords (styles not listed: diatonic / style's own)
GENRE_MELODY = {'riddim': 'diatonic', 'chillstep': 'diatonic', 'jazz_rap': 'blues', 'cloud_rap': 'pentatonic', 'slow_jam': 'pentatonic', 'smooth_jazz': 'pentatonic', 'smooth_funk': 'blues', 'quiet_storm': 'pentatonic', 'modern_country': 'pentatonic', 'country_waltz': 'pentatonic', 'outlaw_country': 'pentatonic', 'western_swing': 'pentatonic', 'g_funk': 'pentatonic', 'neo_soul': 'pentatonic', 'new_jack_swing': 'pentatonic', 'alt_rnb': 'pentatonic', 'rage': 'diatonic', 'plugg': 'pentatonic', 'hauntology_sunlit': 'diatonic', 'hauntology_dark': 'diatonic', 'epic_orchestral': 'diatonic', 'epic_battle': 'diatonic', 'epic_choir': 'diatonic', 'heroic_anthem': 'diatonic', 'symphonic_finale': 'diatonic', 'bebop': 'bebop', 'soul_jazz': 'blues', 'modal_jazz': 'diatonic', 'fusion': 'pentatonic', 'future_funk': 'pentatonic', 'italo_disco': 'diatonic', 'classical_period': 'diatonic', 'romantic': 'diatonic', 'impressionism': 'pentatonic', 'minimalism': 'diatonic', 'brazilian_phonk': 'blues', 'deep_dubstep': 'diatonic', 'deep_dubstep_minimal': 'diatonic', 'progressive_trance': 'diatonic', 'organic_house': 'diatonic', 'disco_funk': 'pentatonic', 'blues': 'blues', 'rock': 'blues', 'funk': 'blues', 'boombap': 'blues', 'phonk': 'blues', 'metal': 'pentatonic',
                'folk': 'pentatonic', 'afrobeats': 'pentatonic', 'amapiano': 'pentatonic', 'reggae': 'pentatonic',
                'lofi': 'pentatonic', 'pop': 'pentatonic', 'disco': 'pentatonic', 'jazz': 'bebop', 'bossa_nova': 'bebop',
                'western': 'pentatonic', 'chamber_pop': 'pentatonic', 'fantasy_rpg': 'pentatonic',
                'gospel': 'blues', 'rnb': 'pentatonic', 'motown': 'pentatonic', 'country': 'pentatonic', 'bluegrass': 'pentatonic',
                'swing': 'bebop', 'punk': 'pentatonic', 'indie_rock': 'pentatonic', 'kpop': 'pentatonic', 'soul_ballad': 'pentatonic',
                'dancehall': 'pentatonic', 'afro_house': 'pentatonic', 'jersey_club': 'pentatonic', 'baile_funk': 'pentatonic',
                'hauntology': 'pentatonic', 'braindance': 'diatonic', 'liquid_dnb': 'pentatonic', 'melodic_dubstep': 'diatonic', 'jam_band': 'blues', 'soft_rock': 'pentatonic',
                'teen_pop': 'pentatonic', 'luxury_rap': 'diatonic', 'uplifting_trance': 'diatonic', 'melodic_house': 'pentatonic',
                'celtic_jig': 'diatonic', 'waltz': 'diatonic', 'tango': 'diatonic', 'salsa': 'diatonic', 'cumbia': 'diatonic'}
GENRE_VOICING = {'bebop': 'rootless', 'soul_jazz': 'rootless', 'modal_jazz': 'open', 'fusion': 'drop2', 'impressionism': 'open', 'romantic': 'open', 'jazz': 'rootless', 'bossa_nova': 'rootless', 'lofi': 'rootless', 'boombap': 'rootless', 'city_pop': 'drop2',
                 'deep_house': 'drop2', 'ukgarage': 'drop2', 'funk': 'drop2', 'disco': 'drop2', 'downtempo': 'drop2',
                 'neoclassical': 'open', 'chamber': 'open', 'fantasy_rpg': 'open', 'cinematic': 'open', 'orchestral': 'open',
                 'swing': 'drop2', 'gospel': 'open', 'rnb': 'drop2', 'waltz': 'open', 'tango': 'close'}
GENRE_COLORS = {'jazz_rap': ['9', '7', '9', '6'], 'cloud_rap': ['add9', 'sus2', 'triad'], 'slow_jam': ['9', '7', 'add9'], 'smooth_jazz': ['add9', '9', '7', 'sus2'], 'smooth_funk': ['9', '7'], 'quiet_storm': ['9', '7', 'add9'], 'modern_country': ['triad', 'add9', 'sus2'], 'country_waltz': ['triad'], 'outlaw_country': ['triad', '7'], 'western_swing': ['6', '7', '9', '6'], 'g_funk': ['7', '9', 'triad'], 'neo_soul': ['9', '7', '9', 'add9'], 'new_jack_swing': ['7', '9', 'triad'], 'alt_rnb': ['7', 'add9', '9'], 'rage': ['triad'], 'plugg': ['add9', 'triad', '7'], 'hauntology_sunlit': ['add9', 'triad', 'sus2', '7'], 'hauntology_dark': ['triad', 'sus2', 'add9'], 'epic_orchestral': ['triad', 'sus4'], 'epic_battle': ['triad'], 'epic_choir': ['triad'], 'heroic_anthem': ['triad', 'sus4', 'add9'], 'symphonic_finale': ['triad', '7'], 'bebop': ['9', '7', '6'], 'modal_jazz': ['9', 'sus4', '7'], 'soul_jazz': ['7', '9'], 'fusion': ['9', 'add9', '7'], 'future_funk': ['7', '9'], 'italo_disco': ['triad', 'add9'], 'new_beat': ['triad'], 'gabber': ['triad'], 'rave_hardcore': ['triad', '7'], 'classical_period': ['triad'], 'romantic': ['7', 'triad', 'add9'], 'impressionism': ['add9', '9', 'sus2'], 'minimalism': ['triad', 'add9'], 'deep_dubstep': ['triad'], 'deep_dubstep_minimal': ['triad'], 'progressive_trance': ['triad', 'sus2', 'add9'], 'organic_house': ['add9', 'triad', 'sus2'], 'disco_funk': ['7', '9', 'triad'], 'jazz': ['7', '9', '9', '6'], 'bossa_nova': ['7', '9', '6'], 'lofi': ['7', '9', 'add9'], 'boombap': ['7', '9'],
                'city_pop': ['7', '9', 'add9'], 'deep_house': ['7', '9', 'add9'], 'ukgarage': ['7', '9'], 'funk': ['7', '9'],
                'blues': ['7'], 'downtempo': ['7', 'add9', '9'], 'neoclassical': ['triad', 'add9', 'add9', 'sus2'],
                'baroque': ['triad'], 'chamber': ['triad', 'triad', '7'], 'holiday': ['triad', '6', '7', 'add9'],
                'western': ['triad', 'triad', 'sus4'], 'hybrid_trailer': ['triad', 'triad', 'add9no3'],
                'symphonic_metal': ['triad'], 'fantasy_rpg': ['triad', 'add9', 'sus2'],
                'gospel': ['7', '9', '6', '7'], 'rnb': ['7', '9', '9', 'add9'], 'swing': ['6', '7', '9'], 'motown': ['triad', '7'],
                'country': ['triad'], 'bluegrass': ['triad'], 'tango': ['triad', '7'], 'salsa': ['triad', '7', '6'],
                'kpop': ['triad', 'add9', '7'], 'afro_house': ['7', '9', 'triad'], 'melodic_techno': ['triad', 'sus2', 'add9no3'],
                'soul_ballad': ['triad', '7', '6'], 'waltz': ['triad'], 'celtic_jig': ['triad', 'sus2'], 'ska': ['triad', '7'],
                'cumbia': ['triad'], 'dancehall': ['triad', '7'], 'hauntology': ['add9', '7', 'triad', 'sus2'],
                'braindance': ['add9', 'sus2', '7', 'add9no3'], 'liquid_dnb': ['7', '9', 'add9'], 'neurofunk': ['triad', 'add9no3'],
                'melodic_dubstep': ['triad', 'add9', 'sus2'], 'brostep': ['triad'], 'memphis_phonk': ['triad'], 'phonk': ['triad'], 'house_phonk': ['triad'], 'brazilian_phonk': ['triad'], 'jam_band': ['triad', '7', 'sus4'],
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


def groove_family(st):
    kicks = st['drums'].get(st.get('kick_track', 'kick'), [])
    if any(k == FOURX for k in kicks):
        return 'four'
    snares = sum((st['drums'].get(n, []) for n in st.get('snare_tracks', [])), [])
    if snares and all(p.find('X') == 8 or p.strip('.') == '' for p in snares):
        return 'half'
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
    for name in drums:
        bank = EXTRA_DRUMS.get(fam, {}).get(name, [])
        if bank and rd.random() < 0.3 + 0.6 * v:
            drums[name] += rd.sample(bank, min(len(bank), 1 + int(2 * v)))
    st['drums'] = drums
    rb = r_for('bass')
    if st.get('bass_mode') == 'pattern' and rb.random() < 0.3 + 0.6 * v:
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
            part_rng[role] = random.Random(f'{sd}-{role}-{owner}-variety')
        rr = part_rng[role]
        free = role not in (opts.instruments or {}) and not t.get('user_pick') and not chip_locked and not t.get('double_of') \
            and (t['name'] == role or st.get('composer') or t.get('switch_of'))     # a genre's named extra parts keep their sound
        keep_sig = owner in SIGNATURE_STRICT                  # rap / R&B: the genre's own sound is the usual one
        if free and pool and rr.random() < ((0.2 + 0.3 * v) if keep_sig else (0.55 + 0.4 * v)):
            # the genre's own pool: its signature sound a little likelier, every other one an authentic alternative;
            # instruments your last songs in this genre used are picked less often, so the next one sounds fresh
            recent = set((getattr(opts, 'avoid', None) or {}).get(role, []))
            w = [(1.4 if i == 0 else 1.0) * (0.25 if x in recent else 1.0) for i, x in enumerate(pool)]
            choice = rr.choices(pool, w)[0]
            if choice != t['inst']:
                t.update(inst=choice, p={}, db=None, pooled=True)
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
    st['delay_beats'] = rnd.choice([0.75, 0.75, 0.5, 1.5]) if rnd.random() < 0.4 * v else st['delay_beats']
    return st


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
    kit_id = drumkits.effective(opts, groove_of, st)
    preset = drumkits.configure(st, kit_id, groove_of, opts) if kit_id else st['kit']
    kit = dict(KITS.get(preset, {}))
    if not kit_id:
        for k, v in st.get('kit_override', {}).items():
            kit[k] = {**kit.get(k, {}), **v}
    if st.get('kick_shape') and not getattr(opts, 'kit', None):    # the genre's own kick, whatever drum preset it sits on
        kit['kick'] = {**kit.get('kick', {}), **st['kick_shape']}
    st['kitparams'] = kit
    drumkits.install_break(st, st['tracks'])
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
    """Octaves to move the lead by so it sits where the genre's lead lives, whatever the key: around E5-E6 for a
    sung-style or synth lead (a little higher for trap bells and trance arps), and always clear above the chords so the
    melody isn't buried. Riff leads (rock, metal, funk, blues) already place themselves low and are left alone."""
    if not mel or (st.get('lead_device') == 'riff' and not st.get('lead_lo')):
        return 0
    mean = sum(m for _, _, m, _ in mel) / len(mel)
    if st.get('lead_lo'):                               # genres whose lead lives lower (phonk cowbells sit around A3-A4)
        lo = st['lead_lo']
    else:
        lo = max(12 * (st.get('lead_oct', 5) + 1) + 1, st.get('chord_center', 62) + 8)
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


def gen_melody(key, prog, chord_bars, st, rnd, complexity):
    from .leads import GENERATORS
    dev = st.get('lead_device', 'hook')
    if dev in GENERATORS:                              # genre lead device (arpeggio, riff, ostinato, bell, call, chops)
        return GENERATORS[dev](key, prog, chord_bars, st, rnd, complexity)
    phrase_bars = 2 * len(prog) * chord_bars
    fam = PHRASE_FAMILY.get(st.get('name'), 'sparse' if st.get('category') == 'Orchestral' else 'sung')
    if st.get('meter'):
        fam = 'triple'
    extra = rnd.sample(PHRASE_BANKS[fam], 3)
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
    plan8 = [rr[i] for i in rnd.choice(PHRASE_PLANS)]
    lo, hi = -3, 10
    d = prog[0] + rnd.choice([0, 2, 4, 4, 7])
    while d > hi:
        d -= 7
    contour = rnd.choice(['arch', 'rise', 'fall', 'wave', 'valley', 'arch'])   # the phrase's overall shape
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
            if reuse and (src, i) in motif:
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


def hold_slow_chords(evs, tracks, st, bpm=120):
    """A slow-attack pad (warm pad, string section, choir) can't play short chord stabs: the notes never reach full
    volume, then ring out after the beat as a smear of late, off-beat notes. On such a sound the chord is held from the
    beat it starts on until it changes, as a keyboard player would on a pad patch."""
    spb = 60.0 / max(40.0, float(bpm or 120))
    for name, t in tracks.items():
        if t.get('layer') not in ('chords', 'pad') or attack_of(t) < 0.3:
            continue
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
                                       and attack_of(tracks[e.track]) >= 0.3)]


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
        add_counter_track(st, opts)
        add_layer_tracks(st, opts)
        add_bass_switch_tracks(st)
        add_section_switch_tracks(st, opts, random.Random(f'{opts.seed}-rotation-{opts.style}'))
    debell(st, opts)
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
        root = rnd.randrange(12)
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
    colors = {'Electronic': ['triad', 'triad', '7', 'add9', 'sus2', 'add9no3', '6'],
              'Classic': ['triad', '7', '7', 'add9', '6', '9', 'sus4'], 'Orchestral': ['triad', 'triad', 'add9', 'sus4', '6']}
    chord_color = rnd.choice(colors.get(st.get('category'), ['triad']))
    if cx > 0.72 and chord_color == 'triad':
        chord_color = rnd.choice(['7', 'add9', '9'])
    sname = st.get('name') or opts.style
    sname_style = sname
    if sname in GENRE_COLORS:                       # genres whose harmony is defined by extended chords
        chord_color = random.Random(opts.seed * 31 + 7).choice(GENRE_COLORS[sname])
    if getattr(opts, 'chord_color', None) in COLORS:
        chord_color = opts.chord_color
    if st.get('voicing') != 'power' and sname in GENRE_VOICING:
        st['voicing'] = GENRE_VOICING[sname]
    if getattr(opts, 'voicing', None) in VOICINGS:
        st['voicing'] = opts.voicing
    st['melody_lang'] = opts.melody_style if getattr(opts, 'melody_style', None) in MELODY_STYLES else GENRE_MELODY.get(sname, 'diatonic')
    from .leads import pick_device
    st['lead_device'] = pick_device(sname, opts.seed, getattr(opts, 'lead_style', None))
    if st.get('meter'):
        st['lead_device'] = 'hook'                     # the device figures are 16th-note based
    bsel = getattr(opts, 'build_style', None)
    st['build_style'] = bsel if bsel in BUILD_STYLES else GENRE_BUILD.get(sname) or \
        {'Classic': 'lift', 'Orchestral': 'swell'}.get(st.get('category'), 'roll')
    st['build_home'] = st['build_style']
    st['build_seq'] = build_sequence(st['build_style'], bool(bsel in BUILD_STYLES), random.Random(f'{opts.seed}-build-{sname}'),
                                     amount=getattr(opts, 'builds', 'auto') or 'auto', family=st.get('build_family'))
    g = getattr(opts, 'groove', None)
    st['groove'] = None if g == 'straight' else (g if g in GROOVES else STYLE_GROOVE.get(sname))
    pad_voicing = rnd.choice(['close', 'close', 'open'])
    modulate = rnd.random() < {'teen_pop': 0.75, 'gospel': 0.35, 'soul_ballad': 0.35, 'smooth_jazz': 0.7}.get(st.get('name'), 0.22) \
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
    mel_main, ph_bars = gen_melody(key, prog_main, cb, st, rnd_m, cx)
    mel_alt, ph_alt = gen_melody(key, prog_alt, cb, st, rnd_m, cx)
    mel_verse, ph_verse = gen_melody(key, prog_verse, cb, st, rnd_m, cx)
    mel_main, mel_alt, mel_verse = [shape_melody(x, p_, key, opts, random.Random(opts.seed * 53 + i_))
                                    for i_, (x, p_) in enumerate(((mel_main, ph_bars), (mel_alt, ph_alt), (mel_verse, ph_verse)))]
    lead_k = lead_octave_shift(mel_main, st)            # same register in every key (not an octave higher in B than in C)
    mel_main, mel_alt, mel_verse = [[(a, b, m + lead_octave_shift(x, st), v) for a, b, m, v in x] for x in (mel_main, mel_alt, mel_verse)]
    st['lead_shift'] = lead_k
    acid_pat = gen_acid_pattern(key, rnd_b, energy)

    tracks = {t['name']: t for t in st['tracks']}
    muted = set(opts.muted or [])
    # ---- form
    if st.get('forms') and isinstance(st['form'], str) and getattr(opts, 'structure', 'auto') in (None, '', 'auto'):
        st['form'] = random.Random(opts.seed * 31 + 7).choice(st['forms'])     # classical genres: one of their forms
    form = list(FORMS[st['form']]) if isinstance(st['form'], str) else list(st['form'])
    form = _traits.shape_form(form, opts, opts.style)
    if opts.structure == 'loop':
        form = [('loop', 16, set(l for l in ['kick', 'snare', 'top', 'bass', 'chords', 'pad', 'arp', 'lead', 'fx']), {})]
    elif opts.structure == 'club':
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
    scale_len = float(opts.length) * st.get('form_scale', 1)
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
    arp_base = arp
    base_form = []
    for (sname, nbars, layers, opts_s) in form:
        if not opts_s.get('build') and opts.structure != 'loop':
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
        is_verse = sname in ('verse', 'A', 'rise', 'head') and not opts_s.get('drop')
        prog = prog_alt if opts_s.get('alt') else (prog_verse if is_verse else prog_main)
        mel, ph = (mel_alt, ph_alt) if opts_s.get('alt') else ((mel_verse, ph_verse) if is_verse else (mel_main, ph_bars))
        if (ed.get('seeds') or {}).get('melody') is not None:
            mel, ph = gen_melody(key, prog, cb, st, random.Random(f"{ed['seeds']['melody']}-melody-edit"), cx)
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
        pchoice = {name: rnd_d.choice(pats) for name, pats in st['drums'].items()}
        bass_pat = rnd_b.choice(st['bass'])
        chord_pat = opts_s.get('chord_rh') or rnd_c.choice(st['chord_rh'])     # a section can have its own (tango ending)
        riff_pat = None
        if st.get('riffs') and st.get('voicing') == 'power' and S < 0.6:     # metal / punk: verses are riffs
            big = opts_s.get('drop') or sname in BIG_SECTIONS
            if not big or rnd_c.random() < st.get('riff_chorus', 0.3):
                riff_pat = rnd_c.choice(st['riffs'])
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
                if slices is not None:                      # a break: its 4-bar pattern, straight or chopped
                    pat = drumkits.bar_pattern(st, dname, slices) or pat
                elif dname == kick_name and last_of_4 and len(pats) > 1 and rnd_d.random() < 0.2 + 0.3 * energy:
                    pat = rnd_d.choice(pats)
                hits = parse_rhythm(pat)
                used = {s for s, l, c in hits}
                for step, l, c in hits:
                    v = VEL.get(c, 0.8) * rnd_d.uniform(1 - 0.1 * opts.humanize, 1 + 0.05 * opts.humanize)
                    evs.append(Ev(dname, beat0 + step / 4, 0.25, None, v))
                if dname in ('chat', 'shaker') and energy > 0.7:
                    for step in GS:
                        if step not in used and rnd_d.random() < (energy - 0.7) * 1.6:
                            evs.append(Ev(dname, beat0 + step / 4, 0.25, None, 0.35))
                if st.get('ghosts') and dname in snares[:1]:
                    for step in GS:
                        if step % 4 != 0 and step not in used and rnd_d.random() < 0.06 + 0.12 * energy:
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
                gen_trap_hats(evs, beat0, rnd_d, energy)
            if (st.get('fill') or energy > 0.6) and 'snare' in layers and b % 8 == 7 and snares and rnd_d.random() < (0.4 + 0.5 * energy) * (1 - S):
                s = snares[0]
                fills = [[13, 14, 15], [12, 13, 14, 15], [10, 13, 14, 15], [14, 15]] if G == 16 else \
                    [[x * 4 / 3 for x in f] for f in ([9, 10, 11], [8, 9, 10, 11], [10, 11])]
                for k, step in enumerate(rnd_d.choice(fills)):
                    evs.append(Ev(s, beat0 + step / 4, 0.25, None, 0.55 + 0.1 * k))
            if opts_s.get('build'):
                add_build_drums(evs, st, tracks, snares, kick_name, b, nbars, beat0, rnd_d)
            riff = gen_riff(riff_pat, key, chord, st.get('riff_lo', 40)) if riff_pat else None
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
                if inst == '808' and mode == 'pattern':
                    mode = '808'
                elif inst == 'acid' and mode == 'pattern':
                    mode = 'acid'
                elif inst in ('wobble', 'riddim') and mode == 'pattern':
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
                        if r < 0.15:
                            m = root + 12
                        elif r < 0.25:
                            m = fold(key.deg(chord + 4, 2), lo)
                        glide = prev_bass if (prev_bass is not None and prev_bass != m and rnd_b.random() < 0.45) else None
                        evs.append(Ev('bass', beat0 + s / 4, (e - s) / 4 * 0.95, m, 1.0, glide))
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
                    while pos < 16:
                        ln = rnd_b.choice(st.get('wobble_lens') or [8, 4, 4, 2, 16]) if pos % 4 == 0 else 2
                        ln = min(ln, 16 - pos)
                        if rnd_b.random() < 0.12 and pos > 0:
                            pos += ln
                            continue
                        rates = (opts_s.get('alt') and st.get('wobble_rates_alt')) or st.get('wobble_rates') or \
                            ([2, 1, 1, 0.5, 0.5, 1 / 3] if energy > 0.3 else [2, 1])   # half-bar / beat / 8th wubs; 16ths are a genre's own choice   # A / B drop switch-up
                        rate = rnd_b.choice(rates)
                        m = rnd_b.choice([root, root, root + 12] if st.get('pedal_sub') else
                                         [root, root, root + 12, fold(key.deg(chord + 4, 2), lo)])
                        evs.append(Ev('bass', beat0 + pos / 4, ln / 4 * 0.97, m, 1.0, None, rate))
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
                    for q, m in enumerate(notes):
                        evs.append(Ev('bass', beat0 + q, 0.92, m, 0.95 if q == 0 else 0.82))
                else:
                    gate = st.get('bass_gate', 0.92)
                    for step, l, c in parse_rhythm(bass_pat):
                        if S >= 0.6 and c in 'OFA':                 # simple: the bass stays on the root
                            m = root
                        elif c == 'O':
                            m = root + 12
                        elif c == 'F':
                            m = fold(key.deg(chord + 4, 2), lo)
                        elif c == 'A':
                            tgt = fold(key.deg(nxt, 2), lo)
                            if rnd_b.random() < 0.4:                     # a step into the next chord - now and then
                                m = tgt + (1 if tgt <= root else -1) * (1 if rnd_b.random() < 0.5 else 2)
                            else:
                                m = rnd_b.choice([fold(key.deg(chord + 4, 2), lo), root + 12, root])
                        else:
                            m = root
                        evs.append(Ev('bass', beat0 + step / 4, l / 4 * gate, m, rnd_b.uniform(0.85, 1.0)))
                    pp = BASS_PASS.get(sname_style, 0.0)
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
                pcol = 0.12 + 0.3 * cx
                if (chord - nxt) % 7 == 4 and third == 3 and rnd_hc.random() < pcol + (0.35 if nxt == 0 else 0):
                    harm_alts.append((beat0, beat0 + 4 * cb, pc3, (pc3 + 1) % 12))      # V/x: its 3rd goes up
                elif key.scale_name == 'major' and chord == 3 and nxt == 0 and third == 4 and rnd_hc.random() < pcol:
                    harm_alts.append((beat0, beat0 + 4 * cb, pc3, (pc3 - 1) % 12))      # borrowed minor iv
            # ---------------- chords
            bar_col = chord_color
            if b % cb == 0 and chord_color not in ('sus2', 'sus4', 'add9no3') and rnd_c.random() < 0.15 * (1 - S) \
                    and not (opts_s.get('drop') or sname in BIG_SECTIONS):
                bar_col = rnd_c.choice(['sus4', 'sus2', chord_color])   # a sus colour now and then (chords + pad agree)
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
                col = bar_col if st.get('voicing', 'close') != 'power' and chord_size <= 4 else None
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
                if arp['mode'] == 'updown':
                    seq = seq + seq[-2:0:-1]
                elif arp['mode'] == 'roll':                      # Scruggs banjo roll: thumb-index-middle with the high drone string
                    drone = 12 * (arp['oct'] + 1) + 7 + ((key.root - 7) % 12)
                    if drone <= tones[-1]:
                        drone += 12
                    seq = [tones[1], tones[2] if len(tones) > 2 else tones[0] + 12, drone, tones[0], tones[2] if len(tones) > 2 else tones[1],
                           drone, tones[1], drone]
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
                for k in range(0 if arp.get('rh') else int(G / rate)):
                    if arp.get('prob') and rnd_c.random() > arp['prob']:
                        continue
                    m = rnd_c.choice(seq) if arp['mode'] == 'random' else seq[k % len(seq)]
                    evs.append(Ev('arp', beat0 + k * rate * u / 4, rate * u / 4 * 0.8, m,
                                  (0.95 if (k % 4 == 0 if G == 16 else (k * rate) % 3 == 0) else 0.75) * rnd_c.uniform(0.9, 1.0)))
        # ---------------- lead
        if 'lead' in layers and 'lead' in tracks:
            soft_lead = 0.75 if sname in ('break', 'bridge', 'C', 'calm') else 1.0
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
    if getattr(opts, 'vocal_guide', False) and vocal:
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
        fx[:] = [f for f in fx if f[0] not in FX_SOUNDS or f[0] == 'crash']
    bar0 = apply_ending(sections, evs, fx, tracks, st, opts, key, chord_size, chord_color, bar0)
    hold_slow_chords(evs, tracks, st, bpm)
    shape_dynamics(evs, tracks, sections, st)
    in_evs = {id(e) for e in evs}
    st['tuned_notes'] = fix_clashes(evs + [v for v in vocal if id(v) not in in_evs], {**tracks, 'vocal': tracks.get('vocal') or
                                    dict(layer='lead')}, key, st, sections)
    if st.get('slides'):                                 # country: notes slide up into place (steel / fiddle / Telecaster)
        add_slides(evs, tracks, st, key, random.Random(opts.seed * 41 + 3))
    if st.get('lead_glide'):                             # G-funk / talk-box: the lead slides from note to note
        prev = None
        for e in sorted((e for e in evs if e.track == 'lead' and e.midi is not None), key=lambda e: e.beat):
            if prev is not None and e.beat - (prev.beat + prev.dur) < 0.3 and e.midi != prev.midi and e.glide is None:
                e.glide = prev.midi
            prev = e
    if st.get('solos'):                                  # bluegrass / synthwave: instruments take turns at the solos
        rotate_solos(evs, tracks, sections, st)
    if st.get('g_run'):
        add_g_runs(evs, tracks, sections, key)
    if st.get('eno_loops'):
        eno_loops(evs, st['eno_loops'], bar0 * 4)
    if any(t.get('chops') for t in tracks.values()):
        chop_samples(evs, tracks, random.Random(opts.seed * 53 + 1))
    evs += double_layers(evs, tracks)                    # layers copy the tuned notes
    switch_sections(evs, tracks, sections)                # verses / choruses / breaks on different instruments
    switch_basses(evs, tracks, sections, st)              # brostep / neuro: several bass timbres trade bars in the drop
    for name, t in tracks.items():                       # any part of this song, picked by its own name in the editor
        pick = (opts.instruments or {}).get(name)
        if not pick or t.get('user_pick') or (name == t['layer'] and not st.get('composer')):
            continue
        if pick == 'off':
            t['off'] = True
        elif t['layer'] in MELODIC_ROLES and isinstance(pick, str) and (pick in INSTRUMENTS or pick.startswith(('user:', 'vst:', 'sf:', 'real:'))):
            t['fallback'], t['inst'], t['user_pick'] = t['inst'], pick, True
    hold_slow_chords(evs, tracks, st, bpm)               # again: switched / re-picked parts may now be on a pad sound
    off = {n for n, t in tracks.items() if t.get('off')} if not st.get('composer') else set()
    if off:                                              # extra parts switched off in the Sound panel
        evs = [e for e in evs if e.track not in off]
    if muted:                                            # parts you switched off: everything else stays note-for-note
        evs = [e for e in evs if tracks.get(e.track, {}).get('layer') not in muted]
    sname ='+'.join([opts.style] + [b for b in (opts.blend or []) if b != opts.style])
    expr = expression_curves(evs, tracks, sections, fx, bar0)
    song = dict(style=sname, seed=opts.seed, bpm=bpm, key=key, events=evs, sections=sections, fx=fx, expr=expr,
                meter=st.get('meter') or '4/4', harm_alts=len(harm_alts),
                total_bars=bar0, prog_main=prog_main, prog_alt=prog_alt, prog_verse=prog_verse, chord_color=chord_color,
                modulate=modulate, st=st, opts=opts, user_opts=user_opts, vocal=vocal,
                energy=energy)
    return song


# ----------------------------------------------------------------------------- 1.10: harmony colour, bass, counter, dynamics
# styles whose harmony uses secondary dominants and borrowed chords (modal / riff genres keep their own sound)
COLOR_HARMONY = {
    'pop', 'jazz', 'bossa_nova', 'city_pop', 'disco', 'folk', 'holiday', 'western', 'chamber_pop', 'soul_ballad', 'celtic_jig',
    'cinematic', 'orchestral', 'film_piano', 'adventure', 'tension', 'neoclassical', 'chamber', 'baroque', 'fantasy_rpg',
    'waltz', 'synthpop', 'eurodance', 'future_bass', 'progressive_house', 'trance', 'downtempo', 'vaporwave', 'lofi', 'boombap',
    'hybrid_trailer', 'orchestral_hiphop', 'teen_pop', 'soft_rock', 'luxury_rap', 'uplifting_trance', 'gospel', 'rnb', 'motown', 'swing', 'country', 'tango', 'salsa', 'kpop', 'ska',
    'indie_rock', 'bluegrass'}
# how often the bass steps into the next chord on the last beat (styles with a moving, song-like bass)
BASS_PASS = {'pop': 0.35, 'folk': 0.5, 'holiday': 0.5, 'western': 0.45, 'chamber_pop': 0.45, 'baroque': 0.6, 'chamber': 0.55,
             'neoclassical': 0.3, 'orchestral': 0.4, 'film_piano': 0.3, 'fantasy_rpg': 0.4, 'adventure': 0.3, 'reggae': 0.3,
             'rock': 0.25, 'disco': 0.2, 'city_pop': 0.3, 'soul_ballad': 0.5, 'celtic_jig': 0.4, 'waltz': 0.45, 'bossa_nova': 0.35,
             'synthpop': 0.2, 'eurodance': 0.15, 'downtempo': 0.25, 'lofi': 0.25, 'boombap': 0.2, 'symphonic_metal': 0.2,
             'country': 0.5, 'bluegrass': 0.6, 'motown': 0.4, 'gospel': 0.4, 'ska': 0.3, 'tango': 0.3, 'indie_rock': 0.3,
             'cumbia': 0.25, 'kpop': 0.2, 'jam_band': 0.5, 'soft_rock': 0.4, 'teen_pop': 0.2}
# genres that get a counter-melody (when the genre decides): the instruments that play it, likeliest first
COUNTER_STYLES = {
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
    q = 1 / 3 if st.get('meter') else 0.5               # counter rhythm grid: 8ths, or triplet 8ths
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
NO_LAYER = {'808', 'logdrum', 'wobble', 'acid', 'sinebass', 'chipbass', 'riddim', 'screech'}


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
        if mine.get(role) == t['inst']:
            continue
        if bell_allowed(name, t['inst']):
            # even where they fit, a bell / mallet that isn't the genre's own sound for this part is an occasional colour
            if t['inst'] not in BELLS | MALLETS or (role, t['inst']) in own or rnd.random() < 0.35:
                continue
        # replaced by the genre's own sound for this part when it has one (not a generic category synth)
        from .styles import POOLS as _P
        mine_ = [] if name == 'hauntology' else [i for (l, i) in own if l == role and bell_allowed(name, i)]   # (Hauntology: unchanged)
        mine_ += [] if name == 'hauntology' else [i for i in _P.get(name, {}).get(role, []) if i not in BELLS | MALLETS]
        t['inst'] = mine_[0] if mine_ else bell_swap(name, role, t['inst'])


def add_layer_tracks(st, opts):
    """Some parts get a second instrument from the genre's own pool, playing the same notes (in unison or an octave
    apart): a supersaw lead with a pluck on top, violins doubled by a flute an octave up or celli an octave down, a
    saw bass with a sub under it, piano chords with a string pad inside them. Which parts, and with what, changes
    from song to song."""
    from .styles import POOLS
    want = getattr(opts, 'layering', None)
    if want == 'off' or st.get('name') == 'chiptune':
        return
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
            continue                                     # one soloist (Kenny G's sax isn't doubled)
        if role in (opts.instruments or {}) and want != 'more':
            continue
        part = {'bass': 'bass', 'lead': 'melody', 'arp': 'melody'}.get(role, 'chords')
        sd = ps.get(part) if ps.get(part) is not None else opts.seed * 1009 + PART_K[part]
        r = random.Random(f'{sd}-{role}-layer')
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
            inst = r.choice(pool)
            octv = 12 if inst in OCT_UP and role in ('lead', 'arp') else (-12 if inst in OCT_DOWN and role == 'lead' else 0)
        picks += 1
        base_db = t['db'] if t.get('db') is not None else {'bass': -15, 'chords': -21, 'pad': -23, 'arp': -25, 'lead': -19}[role]
        st['tracks'].append(dict(name=t['name'] + '_layer', layer=role, inst=inst, pan=-(t.get('pan') or 0) * 0.6,
                                 rev=t.get('rev') or 0.0, dly=t.get('dly') or 0.0, sc=t.get('sc') or 0.0,
                                 db=base_db - (4 if role == 'bass' else 6), hp=None, drive=None, p={},
                                 double_of=t['name'], octave=octv))


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
                out.append(Ev(name, e.beat, min(e.dur, max_d) if max_d else e.dur, m, e.vel * 0.9,
                              None if e.glide is None else e.glide + (m - e.midi), e.mod))
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


def inst_family(inst):
    """Instrument family of a sound name ('sf:' / 'real:' prefixes ignored); unknown sounds are their own family."""
    base = str(inst).split(':', 1)[-1]
    for fam, names in INST_FAMILIES.items():
        if base in names:
            return fam
    for fam, names in INST_FAMILIES.items():          # e.g. 'cowbell_808' -> no; 'piano_soft' -> keys
        if any(base.startswith(n) for n in names if len(n) > 3):
            return fam
    return base


def add_section_switch_tracks(st, opts, rnd):
    """Instrument rotation: verses, choruses and breaks play a part on different instruments from the genre's own pool
    (e.g. Rhodes verse, piano chorus, guitar bridge). The main instrument keeps the big sections."""
    from .styles import POOLS
    mode = getattr(opts, 'rotation', 'auto') or 'auto'
    if mode == 'off' or opts.structure == 'loop' or (st.get('no_rotation') and mode == 'auto'):
        return                                           # ensemble genres keep each instrument on its own part
    v = float(getattr(opts, 'variety', 0.5))
    n_roles = {'some': 1, 'lots': 3}.get(mode, 1 if v < 0.45 else (2 if v < 0.8 else 3))
    if mode == 'auto' and random.Random(f'{opts.seed}-rot-on').random() > 0.35 + 0.6 * v:
        return
    pal = PALETTES.get(st.get('category'), {})
    recent = getattr(opts, 'avoid', None) or {}
    cands = []
    for role in ('lead', 'chords', 'pad', 'arp'):
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
        for k in range(2 if (mode == 'lots' or rnd.random() < 0.4) and len(alts) >= 2 else 1):
            c = rnd.choices(alts, w)[0]
            i = alts.index(c)
            alts, w = alts[:i] + alts[i + 1:], w[:i] + w[i + 1:]
            picks.append(c)
            if not alts:
                break
        for k, inst in enumerate(picks):
            st['tracks'].append(dict(main, name=f'{role}_sw{k + 1}', inst=inst, p={}, db=None, pooled=True,
                                     switch_of=role, groups=('A',) if (k == 0 and len(picks) > 1) else (('A', 'C') if k == 0 else ('C',))))


def switch_sections(evs, tracks, sections):
    alts = {}
    for n, t in tracks.items():
        if t.get('switch_of') in ('lead', 'chords', 'pad', 'arp'):
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
                                 sc=main.get('sc') or 0.0, db=main.get('db'), hp=None, drive=None,
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
}
STYLE_GROOVE = {'jazz_rap': 'dilla', 'slow_jam': 'laidback', 'smooth_jazz': 'laidback', 'quiet_storm': 'laidback', 'smooth_funk': 'funk', 'neo_soul': 'dilla', 'g_funk': 'laidback', 'hauntology_sunlit': 'dilla', 'hauntology_dark': 'laidback', 'disco_funk': 'funk', 'organic_house': 'house', 'boombap': 'dilla', 'lofi': 'dilla', 'phonk': 'dilla', 'reggae': 'laidback', 'downtempo': 'laidback',
                'afrobeats': 'afro', 'amapiano': 'afro', 'reggaeton': 'dembow', 'moombahton': 'dembow', 'jazz': 'jazz',
                'house': 'house', 'deep_house': 'house', 'tech_house': 'house', 'ukgarage': 'house',
                'funk': 'funk', 'disco': 'funk', 'city_pop': 'funk', 'rnb': 'laidback', 'gospel': 'laidback',
                'swing': 'jazz', 'afro_house': 'afro', 'dancehall': 'dembow', 'cumbia': 'afro', 'hauntology': 'dilla'}


