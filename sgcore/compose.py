"""Composition: harmony, melody, bass, drums and arrangement -> a list of note events."""
import math
import random
import re
from dataclasses import dataclass, field, asdict

from .styles import STYLES, FORMS, FORM_VARIANTS
from .instruments import KITS, INSTRUMENTS, PALETTES

SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10], 'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10], 'harmonic_minor': [0, 2, 3, 5, 7, 8, 11], 'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
}
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FLAT_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
FLAT_ALIASES = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
VEL = {'X': 1.0, 'x': 0.78, 'o': 0.5}
LAYERS = ['kick', 'snare', 'top', 'bass', 'chords', 'pad', 'arp', 'lead', 'fx']
MELODIC_ROLES = ['bass', 'chords', 'pad', 'arp', 'lead']
SECTION_ENERGY = {'intro': 0.72, 'verse': 0.85, 'drop': 1.0, 'break': 0.68, 'outro': 0.8, 'hook': 1.0, 'A': 0.9,
                  'B': 1.0, 'C': 0.75, 'chorus': 1.0, 'bridge': 0.8, 'head': 0.95, 'solo': 0.9, 'rise': 0.8,
                  'theme': 0.95, 'calm': 0.65, 'climax': 1.0, 'loop': 1.0}


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
    blend: list = field(default_factory=list)          # extra styles to fuse with the main style
    blend_parts: dict = field(default_factory=dict)    # part -> style  (groove, bass, harmony, melody, form, mix)
    part_seeds: dict = field(default_factory=dict)     # re-roll one part: harmony, melody, drums, bass, chords
    variety: float = 0.5          # 0..1 how adventurous each song's sound palette, grooves and arrangement get
    user_drums: bool = False      # use the drum samples you loaded instead of the built-in kit
    sections: list = None         # section editor: [{src, copy, bars, seeds{part:int}, vary:int, mute:[layers]}]
    engine: str = 'auto'          # auto | sampled | synth  (sampled = real recorded instruments when the library is installed)
    vst_rig: bool = False         # play parts through genre-matched plugins (sgcore.vstrigs) when they're installed
    melody_style: str = None      # None = genre default | diatonic | pentatonic | blues | bebop
    voicing: str = None           # None = genre default | close | open | drop2 | rootless | power
    chord_color: str = None       # None = varies per song | triad | 7 | add9 | 9 | 6 | sus2 | sus4
    part_levels: dict = field(default_factory=dict)   # layer -> dB offset (-12..+6), e.g. {'lead': -3}
    part_fx: dict = field(default_factory=dict)       # layer -> effect plugin name (e.g. {'lead': 'ValhallaSupermassive'})
    ending: str = 'auto'          # auto | hit (final chord + crash) | fade
    vocal_guide: bool = False     # also play the vocal guide melody (it is always in the MIDI export)
    bass_rhythm: str = None       # None = style | kick (bass plays with the kick drum)
    lead_style: str = None        # None = genre | hook | arp | riff | ostinato | bell | call | chops
    build_style: str = None       # None = genre | roll | triplet | kick_roll | filter | stutter | pause | lift | swell
    groove: str = None            # None = genre feel | straight | dilla | laidback | afro | dembow | jazz | house | funk
    mood: str = None              # dark | happy | chill | epic | dreamy | aggressive | melancholic | energetic | mysterious | romantic
    counter: str = None           # None = genre decides | on | off  (a second line answering the lead: celli, horns, flute ...)
    layering: str = None          # None = genre + variety decide | off | more  (parts doubled by a second instrument)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**known)


class Key:
    def __init__(self, root, scale):
        self.root = root
        self.scale_name = scale
        self.scale = SCALES[scale]

    def deg(self, d, octave):
        o, i = divmod(int(d), 7)
        return 12 * (octave + 1) + self.root + 12 * o + self.scale[i]

    def name(self):
        n = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'][self.root]
        return f"{n} {self.scale_name.replace('_', ' ')}"

    def chord_ok(self, d):
        third = (self.deg(d + 2, 4) - self.deg(d, 4)) % 12
        fifth = (self.deg(d + 4, 4) - self.deg(d, 4)) % 12
        return third in (3, 4) and fifth == 7

    def roman(self, prog):
        out = []
        for d in prog:
            r = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][d % 7]
            third = (self.deg(d + 2, 4) - self.deg(d, 4)) % 12
            fifth = (self.deg(d + 4, 4) - self.deg(d, 4)) % 12
            out.append((r if third == 4 else r.lower()) + ('°' if fifth == 6 else ''))
        return '-'.join(out)


ROMAN = {'i': 0, 'ii': 1, 'iii': 2, 'iv': 3, 'v': 4, 'vi': 5, 'vii': 6}


def parse_progression(text):
    if not text:
        return None
    parts = [p for p in re.split(r'[\s,\-–>|]+', text.strip()) if p]
    out = []
    for p in parts:
        q = p.lower() if p.isdigit() else p.lower().rstrip('°o+7m')   # "7" is degree 7; "V7" is chord V
        if q.isdigit() and 1 <= int(q) <= 7:
            out.append(int(q) - 1)
        elif q in ROMAN:
            out.append(ROMAN[q])
        else:
            raise ValueError(f'Cannot read chord "{p}" - use numbers 1-7 or roman numerals like i, IV, vi')
    return out or None


def parse_key(text):
    t = text.strip()
    minor = t.endswith('m') and not t.lower().endswith('maj')
    r = (t[:-1] if minor else t).strip()
    r = r[0].upper() + r[1:]
    r = FLAT_ALIASES.get(r, r)
    if r not in NOTE_NAMES:
        raise ValueError(f'Unknown key {text!r} (examples: C, F#m, Ebm, A)')
    return NOTE_NAMES.index(r), minor


def voice_chord(key, deg, size, center, voicing='close', color=None):
    if voicing == 'power':
        root = key.deg(deg, 4) % 12
        lo = center - 6
        r = lo + ((root - lo) % 12)
        return [r, r + 7, r + 12]
    offs = COLORS[color] if color in COLORS else [2 * i for i in range(size)]
    if voicing == 'rootless':                       # jazz piano: the bass has the root, hands play 3-5-7-9
        offs = [o for o in offs if o != 0]
        for extra in (6, 8):
            if len(offs) < 3 and extra not in offs:
                offs.append(extra)
    pcs = [key.deg(deg + o, 4) % 12 for o in offs]
    lo = center - 6
    notes = sorted(lo + ((pc - lo) % 12) for pc in pcs)
    if voicing == 'open' and len(notes) >= 3:      # spread: second-lowest note up an octave
        notes = sorted([notes[0]] + [notes[1] + 12] + notes[2:])
    elif voicing == 'drop2' and len(notes) >= 4:   # second-highest note dropped an octave (guitar / keys soul voicing)
        top = notes[-4:]
        notes = sorted(notes[:-4] + [top[2] - 12, top[0], top[1], top[3]])
    return notes


VOICINGS = ['close', 'open', 'drop2', 'rootless', 'power']
MELODY_STYLES = ['diatonic', 'pentatonic', 'blues', 'bebop']
# how each genre's lead player phrases, and how its keyboard player voices chords (styles not listed: diatonic / style's own)
GENRE_MELODY = {'blues': 'blues', 'rock': 'blues', 'funk': 'blues', 'boombap': 'blues', 'phonk': 'blues', 'metal': 'pentatonic',
                'folk': 'pentatonic', 'afrobeats': 'pentatonic', 'amapiano': 'pentatonic', 'reggae': 'pentatonic',
                'lofi': 'pentatonic', 'pop': 'pentatonic', 'disco': 'pentatonic', 'jazz': 'bebop', 'bossa_nova': 'bebop',
                'western': 'pentatonic', 'chamber_pop': 'pentatonic', 'fantasy_rpg': 'pentatonic',
                'gospel': 'blues', 'rnb': 'pentatonic', 'motown': 'pentatonic', 'country': 'pentatonic', 'bluegrass': 'pentatonic',
                'swing': 'bebop', 'punk': 'pentatonic', 'indie_rock': 'pentatonic', 'kpop': 'pentatonic', 'soul_ballad': 'pentatonic',
                'dancehall': 'pentatonic', 'afro_house': 'pentatonic', 'jersey_club': 'pentatonic', 'baile_funk': 'pentatonic',
                'celtic_jig': 'diatonic', 'waltz': 'diatonic', 'tango': 'diatonic', 'salsa': 'diatonic', 'cumbia': 'diatonic'}
GENRE_VOICING = {'jazz': 'rootless', 'bossa_nova': 'rootless', 'lofi': 'rootless', 'boombap': 'rootless', 'city_pop': 'drop2',
                 'deep_house': 'drop2', 'ukgarage': 'drop2', 'funk': 'drop2', 'disco': 'drop2', 'downtempo': 'drop2',
                 'neoclassical': 'open', 'chamber': 'open', 'fantasy_rpg': 'open', 'cinematic': 'open', 'orchestral': 'open',
                 'swing': 'drop2', 'gospel': 'open', 'rnb': 'drop2', 'waltz': 'open', 'tango': 'close'}
GENRE_COLORS = {'jazz': ['7', '9', '9', '6'], 'bossa_nova': ['7', '9', '6'], 'lofi': ['7', '9', 'add9'], 'boombap': ['7', '9'],
                'city_pop': ['7', '9', 'add9'], 'deep_house': ['7', '9', 'add9'], 'ukgarage': ['7', '9'], 'funk': ['7', '9'],
                'blues': ['7'], 'downtempo': ['7', 'add9', '9'], 'neoclassical': ['triad', 'add9', 'add9', 'sus2'],
                'baroque': ['triad'], 'chamber': ['triad', 'triad', '7'], 'holiday': ['triad', '6', '7', 'add9'],
                'western': ['triad', 'triad', 'sus4'], 'hybrid_trailer': ['triad', 'triad', 'add9no3'],
                'symphonic_metal': ['triad'], 'fantasy_rpg': ['triad', 'add9', 'sus2'],
                'gospel': ['7', '9', '6', '7'], 'rnb': ['7', '9', '9', 'add9'], 'swing': ['6', '7', '9'], 'motown': ['triad', '7'],
                'country': ['triad'], 'bluegrass': ['triad'], 'tango': ['triad', '7'], 'salsa': ['triad', '7', '6'],
                'kpop': ['triad', 'add9', '7'], 'afro_house': ['7', '9', 'triad'], 'melodic_techno': ['triad', 'sus2', 'add9no3'],
                'soul_ballad': ['triad', '7', '6'], 'waltz': ['triad'], 'celtic_jig': ['triad', 'sus2'], 'ska': ['triad', '7'],
                'cumbia': ['triad'], 'dancehall': ['triad', '7'], 'punk': ['triad'], 'indie_rock': ['triad', 'add9', 'sus2']}


def fold(m, lo):
    while m < lo:
        m += 12
    while m >= lo + 12:
        m -= 12
    return m


def parse_rhythm(pat):
    """'x-..X...' -> [(step, length, char)] in 16ths of a bar. 12-step patterns (triple / compound meters: 3/4, 6/8,
    12/8) are scaled onto the same bar, so a step is a third of a beat there."""
    out = []
    k = 16 / len(pat) if len(pat) == 12 else 1
    for i, c in enumerate(pat):
        if c not in '.-':
            l = 1
            j = i + 1
            while j < len(pat) and pat[j] == '-':
                l += 1
                j += 1
            out.append((i * k if k != 1 else i, l * k if k != 1 else l, c))
    return out


def grid_of(st):
    """Steps per bar: 16 (straight 4/4) or 12 (3/4, 6/8, 12/8 - see styles 'meter')."""
    return 12 if st.get('meter') else 16


def grid_steps(st):
    g = grid_of(st)
    return [i * 16 / g for i in range(g)] if g != 16 else list(range(16))


def lead_voicing(notes, prev, center, inversions=True):
    """Voice leading: of the chord's inversions / octave shifts, the one closest to the previous chord (each voice moves
    as little as possible), kept near the part's register - how a pianist or string section moves between chords."""
    if not prev or not notes:
        return notes
    base = sorted(notes)
    opts = []
    inv = base
    for _ in range(len(base) if inversions else 1):
        opts.append(inv)
        inv = sorted(inv[1:] + [inv[0] + 12])
    opts = [[x + sh for x in o] for o in opts for sh in (-12, 0, 12)]

    def cost(o):
        c = sum(min(abs(x - q) for q in prev) for x in o) + 0.5 * sum(min(abs(q - x) for x in o) for q in prev)
        mid = (o[0] + o[-1]) / 2
        c += 1.5 * max(0, abs(mid - center) - 5)
        if o[0] < center - 13 or o[-1] > center + 15:
            c += 60
        return c
    return min(opts, key=cost)


class Ev:
    __slots__ = ('track', 'beat', 'dur', 'midi', 'vel', 'glide', 'mod')

    def __init__(self, track, beat, dur, midi, vel, glide=None, mod=None):
        self.track, self.beat, self.dur, self.midi, self.vel, self.glide, self.mod = track, beat, dur, midi, vel, glide, mod


def chord_tones_deg(chord, lo, hi):
    out = []
    for k in range(-2, 4):
        for iv in (0, 2, 4):
            d = chord + 7 * k + iv
            if lo <= d <= hi:
                out.append(d)
    return out


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
}

# chord colours: scale-degree stacks above the root (0=root 2=3rd 4=5th 6=7th 8=9th, 1/3 = sus2/sus4, 5 = 6th)
COLORS = {'triad': [0, 2, 4], '7': [0, 2, 4, 6], 'add9': [0, 2, 4, 8], 'sus2': [0, 1, 4], 'sus4': [0, 3, 4],
          '9': [0, 2, 4, 6, 8], '6': [0, 2, 4, 5], 'add9no3': [0, 4, 8]}
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
        free = role not in (opts.instruments or {}) and not t.get('user_pick') and not chip_locked
        if free and pool and rr.random() < 0.3 + 0.55 * v:
            # the genre's own pool: its signature sound stays the likeliest, the others are all authentic alternatives
            w = [2.0 if i == 0 else 1.0 for i in range(len(pool))]
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
        if t['dly'] or (role in ('lead', 'arp') and rnd.random() < 0.3 * v):
            t['dly'] = max(t['dly'], 0.2) * rnd.uniform(0.7, 1.3)
        tracks.append(t)
    st['tracks'] = tracks
    if not opts.kit and st.get('category') != 'Orchestral' and rd.random() < 0.35 * v:
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
        mapped = None if (user_pick or t.get('pooled')) else ACOUSTIC_MAP.get(name, {}).get(t['layer'])
        if mapped:
            target = mapped
        elif inst in sfm.ACOUSTIC and (cat in ('Orchestral', 'Classic') or engine == 'sampled' or inst in sfm.ELECTRONIC_SWAP):
            target = inst
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
        new = opts.instruments.get(t['layer']) if t['layer'] in MELODIC_ROLES else None
        if isinstance(new, str) and new.startswith(('vstp:', 'vstd:', 'vstq:')):
            new = _installed_vst(new, opts)             # a plugin picked in the Sound dropdown -> playable sound
        if new and (new in INSTRUMENTS or new.startswith(('user:', 'vst:', 'sf:'))) and new != t['inst']:
            t['fallback'] = t['inst']
            t['user_pick'] = True
            t['inst'] = new
            t['p'] = {}
            t['db'] = None
        tracks.append(t)
    st['tracks'] = tracks
    kit = dict(KITS.get(opts.kit or st['kit'], {}))
    if not opts.kit:
        for k, v in st.get('kit_override', {}).items():
            kit[k] = {**kit.get(k, {}), **v}
    st['kitparams'] = kit
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
    **{k: 'syncopated' for k in ('funk', 'disco', 'afrobeats', 'amapiano', 'reggaeton', 'moombahton', 'reggae', 'ukgarage', 'house',
                                 'deep_house', 'tech_house', 'city_pop', 'bossa_nova')},
    **{k: 'sparse' for k in ('ambient', 'downtempo', 'lofi', 'vaporwave', 'jazz', 'cinematic', 'orchestral', 'film_piano',
                             'adventure', 'tension', 'boombap', 'neoclassical', 'western', 'hybrid_trailer')},
    **{k: 'sung' for k in ('chamber', 'fantasy_rpg', 'holiday', 'chamber_pop', 'symphonic_metal', 'gospel', 'rnb', 'motown',
                           'country', 'kpop', 'indie_rock', 'punk', 'cumbia', 'ska', 'dancehall')},
    **{k: 'busy' for k in ('bluegrass', 'salsa', 'swing', 'melodic_techno', 'baile_funk', 'jersey_club', 'afro_house')},
    'baroque': 'busy', 'orchestral_hiphop': 'busy', 'tango': 'sparse',
}


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


def gen_trap_hats(evs, beat0, rnd, energy):
    pos = 0.0
    while pos < 4 - 1e-9:
        r = rnd.random()
        if r < 0.08 + 0.12 * energy and pos <= 3.5:
            n = rnd.choice([3, 4, 6])
            for k in range(n):
                evs.append(Ev('chat', beat0 + pos + k * (0.5 / n), 0.1, None, 0.45 + 0.4 * k / n))
            pos += 0.5
            continue
        if r < 0.32:
            evs.append(Ev('chat', beat0 + pos, 0.1, None, 0.8))
            evs.append(Ev('chat', beat0 + pos + 0.25, 0.1, None, 0.55))
        else:
            evs.append(Ev('chat', beat0 + pos, 0.1, None, 0.85 if pos % 1 == 0 else 0.65))
        pos += 0.5


def gen_acid_pattern(key, rnd, energy, bars=2):
    """A looping 303 line in scale degrees relative to the chord root: (step, deg_offset, octave, accent, slide)."""
    steps = []
    dens = 0.5 + 0.35 * energy
    for s in range(16 * bars):
        if s == 0 or rnd.random() < dens:
            off = rnd.choices([0, 0, 0, 2, 4, 6, -1, 3], k=1)[0]
            octv = rnd.choices([0, 1, -1], [6, 2, 1])[0]
            steps.append((s, off, octv, rnd.random() < 0.3, rnd.random() < 0.2 and s > 0))
    return steps


def compose(opts):
    user_opts = opts
    opts, mood = apply_mood(opts)
    ps = opts.part_seeds or {}

    def prng(part, k):
        return random.Random(ps.get(part) if ps.get(part) is not None else opts.seed * 1009 + k)
    rnd = prng('harmony', 1)          # key, tempo, progression
    rnd_m = prng('melody', 2)         # lead melody
    rnd_d = prng('drums', 3)          # drum patterns, fills, hats
    rnd_b = prng('bass', 4)           # bass lines
    rnd_c = prng('chords', 5)         # chord rhythms, arps, voicing choices
    st = resolve_style(opts, random.Random(opts.seed * 7 + 3), mood)
    st = apply_variety(st, opts, random.Random(opts.seed * 7919 + 17))
    add_counter_track(st, opts)
    add_layer_tracks(st, opts)
    apply_sampled(st, opts)
    by_name = {t['name']: t for t in st['tracks']}
    st['tracks'] = [t for t in st['tracks'] if not (t.get('double_of') and by_name.get(t['double_of'], {}).get('inst') == t['inst'])]
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
            alt = [s for s in scales if (s in ('minor', 'dorian', 'phrygian', 'harmonic_minor')) == minor]
            scale = alt[0] if alt else scale
    else:
        root = rnd.randrange(12)
        if not opts.scale and mood and mood.get('scales'):
            pref = [x for x in mood['scales'] if x in scales] or mood['scales']
            scale = rnd.choice(pref)
        else:
            scale = opts.scale or rnd.choice(scales)
    key = Key(root, scale)
    # ---- harmony
    progs = st.get('progs') or {scale: GENERIC_PROGS.get(scale, GENERIC_PROGS['major'])}
    if isinstance(progs, dict):
        progs = progs.get(scale) or GENERIC_PROGS.get(scale) or next(iter(progs.values()))
    elif scale not in st['scales']:
        progs = GENERIC_PROGS.get(scale, progs)
    custom = parse_progression(opts.progression)
    progs = [p for p in progs if all(key.chord_ok(d) for d in p)] or [[0, 3, 4, 0]]
    bank = [p for p in GENERIC_PROGS.get(scale, []) if all(key.chord_ok(d) for d in p)]
    pool = [p for p in progs] * 2 + [p for p in bank if p not in progs]
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
    g = getattr(opts, 'groove', None)
    st['groove'] = None if g == 'straight' else (g if g in GROOVES else STYLE_GROOVE.get(sname))
    pad_voicing = rnd.choice(['close', 'close', 'open'])
    modulate = rnd.random() < 0.22 and st.get('form') in ('edm', 'song', 'trap', 'chip', 'halftime')
    cb = st['chord_bars']
    chord_size = st['chord_size'] + (1 if cx > 0.72 else 0) - (1 if cx < 0.28 and st['chord_size'] > 3 else 0)
    chord_size = max(3, min(5, chord_size))
    mel_main, ph_bars = gen_melody(key, prog_main, cb, st, rnd_m, cx)
    mel_alt, ph_alt = gen_melody(key, prog_alt, cb, st, rnd_m, cx)
    mel_verse, ph_verse = gen_melody(key, prog_verse, cb, st, rnd_m, cx)
    acid_pat = gen_acid_pattern(key, rnd_b, energy)

    tracks = {t['name']: t for t in st['tracks']}
    muted = set(opts.muted or [])
    # ---- form
    form = list(FORMS[st['form']]) if isinstance(st['form'], str) else list(st['form'])
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
    for si, ed in enumerate(edits):
        src = int(ed['src'])
        uid = f"{src}:{int(ed.get('copy', 0))}"
        sname, nbars, layers, opts_s = base_form[src]
        if ed.get('bars') and not opts_s.get('build'):
            nbars = max(2, min(64, int(ed['bars'])))
        rnd_d, rnd_b, rnd_c = sec_rng('drums', uid, ed), sec_rng('bass', uid, ed), sec_rng('chords', uid, ed)
        layers = set(layers) - muted - set(ed.get('mute') or [])
        if energy > 0.75 and opts_s.get('drop'):
            layers |= {'arp'} - muted
        if energy < 0.25:
            layers -= {'arp'} if sname not in ('drop', 'chorus', 'hook', 'climax') else set()
        is_verse = sname in ('verse', 'A', 'rise', 'head') and not opts_s.get('drop')
        prog = prog_alt if opts_s.get('alt') else (prog_verse if is_verse else prog_main)
        mel, ph = (mel_alt, ph_alt) if opts_s.get('alt') else ((mel_verse, ph_verse) if is_verse else (mel_main, ph_bars))
        if (ed.get('seeds') or {}).get('melody') is not None:
            mel, ph = gen_melody(key, prog, cb, st, random.Random(f"{ed['seeds']['melody']}-melody-edit"), cx)
        if opts_s.get('build'):
            bs = st.get('build_style', 'roll')
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
        chord_pat = rnd_c.choice(st['chord_rh'])
        prev_bass = None
        for b in range(nbars):
            bar = bar0 + b
            beat0 = bar * 4
            chord = prog[(b // cb) % len(prog)]
            nxt = prog[((b + 1) // cb) % len(prog)]
            last_of_4 = (b % 4 == 3)
            # ---------------- drums
            for dname, pats in st['drums'].items():
                if dname not in tracks or tracks[dname]['layer'] not in layers:
                    continue
                pat = pchoice[dname]
                if dname == kick_name and last_of_4 and len(pats) > 1 and rnd_d.random() < 0.2 + 0.3 * energy:
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
            if st.get('trap_hats') and not st.get('meter') and 'top' in layers and 'chat' not in st['drums']:
                gen_trap_hats(evs, beat0, rnd_d, energy)
            if (st.get('fill') or energy > 0.6) and 'snare' in layers and b % 8 == 7 and snares and rnd_d.random() < 0.4 + 0.5 * energy:
                s = snares[0]
                fills = [[13, 14, 15], [12, 13, 14, 15], [10, 13, 14, 15], [14, 15]] if G == 16 else \
                    [[x * 4 / 3 for x in f] for f in ([9, 10, 11], [8, 9, 10, 11], [10, 11])]
                for k, step in enumerate(rnd_d.choice(fills)):
                    evs.append(Ev(s, beat0 + step / 4, 0.25, None, 0.55 + 0.1 * k))
            if opts_s.get('build'):
                add_build_drums(evs, st, tracks, snares, kick_name, b, nbars, beat0, rnd_d)
            # ---------------- bass
            if 'bass' in layers and 'bass' in tracks:
                lo = st['bass_lo']
                root = fold(key.deg(chord, 2), lo)
                mode = st['bass_mode']
                inst = tracks['bass']['inst']
                if inst == '808' and mode == 'pattern':
                    mode = '808'
                elif inst == 'acid' and mode == 'pattern':
                    mode = 'acid'
                elif inst == 'wobble' and mode == 'pattern':
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
                        ln = rnd_b.choice([8, 4, 4, 2, 16]) if pos % 4 == 0 else 2
                        ln = min(ln, 16 - pos)
                        if rnd_b.random() < 0.12 and pos > 0:
                            pos += ln
                            continue
                        rate = rnd_b.choice([1, 0.5, 0.5, 0.25, 1 / 3, 1 / 6]) if energy > 0.3 else rnd_b.choice([1, 0.5])
                        m = rnd_b.choice([root, root, root + 12, fold(key.deg(chord + 4, 2), lo)])
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
                        if c == 'O':
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
            if b % cb == 0 and sname_style in COLOR_HARMONY and nxt != chord and st.get('voicing') != 'power':
                third = (key.deg(chord + 2, 4) - key.deg(chord, 4)) % 12
                pc3 = key.deg(chord + 2, 4) % 12
                pcol = 0.12 + 0.3 * cx
                if (chord - nxt) % 7 == 4 and third == 3 and rnd_hc.random() < pcol + (0.35 if nxt == 0 else 0):
                    harm_alts.append((beat0, beat0 + 4 * cb, pc3, (pc3 + 1) % 12))      # V/x: its 3rd goes up
                elif key.scale_name == 'major' and chord == 3 and nxt == 0 and third == 4 and rnd_hc.random() < pcol:
                    harm_alts.append((beat0, beat0 + 4 * cb, pc3, (pc3 - 1) % 12))      # borrowed minor iv
            # ---------------- chords
            bar_col = chord_color
            if b % cb == 0 and chord_color not in ('sus2', 'sus4', 'add9no3') and rnd_c.random() < 0.15 \
                    and not (opts_s.get('drop') or sname in BIG_SECTIONS):
                bar_col = rnd_c.choice(['sus4', 'sus2', chord_color])   # a sus colour now and then (chords + pad agree)
            if 'chords' in layers and 'chords' in tracks and chord_pat and (b % cb == 0):
                col = bar_col if st.get('voicing', 'close') != 'power' and chord_size <= 4 else None
                notes = voice_chord(key, chord, chord_size, st.get('chord_center', 62), st.get('voicing', 'close'), col)
                if st.get('voicing', 'close') in ('close', 'open'):
                    notes = lead_voicing(notes, vl_prev.get('chords'), st.get('chord_center', 62),
                                         st.get('voicing', 'close') == 'close')
                vl_prev['chords'] = notes
                if (opts_s.get('drop') or sname in BIG_SECTIONS) and notes and notes[-1] + 12 <= 96 and st.get('voicing') != 'power':
                    notes = notes + [notes[-1] + 12]                   # choruses / drops open up: top note doubled (once)
                for step, l, c in parse_rhythm(chord_pat):
                    dur = l / 4 * (cb if l == 16 else 1) * 0.95
                    for i, m in enumerate(notes):
                        off = i * st.get('strum', 0.0)
                        evs.append(Ev('chords', beat0 + step / 4 + off, dur, m, rnd_c.uniform(0.75, 0.92)))
            # ---------------- pad
            if 'pad' in layers and 'pad' in tracks and (b % cb == 0):
                notes = voice_chord(key, chord, min(4, chord_size), st.get('chord_center', 62) - 2, pad_voicing,
                                    bar_col if bar_col in ('triad', '7', 'add9', 'sus2', 'sus4', '6', 'add9no3') else None)
                notes = lead_voicing(notes, vl_prev.get('pad'), st.get('chord_center', 62) - 2, pad_voicing == 'close')
                vl_prev['pad'] = notes
                for m in notes:
                    evs.append(Ev('pad', beat0, 4 * cb * 0.98, m, 0.8))
            # ---------------- arp
            if 'arp' in layers and 'arp' in tracks:
                acol = bar_col if bar_col in ('sus2', 'sus4', 'add9no3') else None   # arps follow a sus chord
                tones = voice_chord(key, chord, 3, 12 * (arp['oct'] + 1) + 4, 'close', acol)
                seq = tones + [tones[0] + 12]
                if arp['mode'] == 'updown':
                    seq = seq + seq[-2:0:-1]
                rate = arp['rate']
                u = 16 / G                                       # a grid step in 16ths (4/3 in triple meters)
                for k in range(int(G / rate)):
                    if arp.get('prob') and rnd_c.random() > arp['prob']:
                        continue
                    m = rnd_c.choice(seq) if arp['mode'] == 'random' else seq[k % len(seq)]
                    evs.append(Ev('arp', beat0 + k * rate * u / 4, rate * u / 4 * 0.8, m,
                                  (0.95 if (k % 4 == 0 if G == 16 else (k * rate) % 3 == 0) else 0.75) * rnd_c.uniform(0.9, 1.0)))
        # ---------------- lead
        if 'lead' in layers and 'lead' in tracks:
            soft_lead = 0.75 if sname in ('break', 'bridge', 'C', 'calm') else 1.0
            reps = int(math.ceil(nbars / ph))
            for r in range(reps):
                for (bt, du, m, v) in mel:
                    beat = sec_start + r * ph * 4 + bt
                    if beat < sec_start + nbars * 4 - 0.01:
                        if opts_s.get('build') and beat >= sec_start + nbars * 4 - 2:
                            continue
                        evs.append(Ev('lead', beat, du, m, v * soft_lead))
        if opts_s.get('build'):
            add_build_fx(fx, st.get('build_style', 'roll'), sec_start, nbars)
        if opts_s.get('drop'):
            fx.append(('crash', sec_start, 0))
            fx.append(('impact', sec_start, 0))
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
    lock_bass_to_kick(evs, tracks, st)
    add_transitions(sections, evs, fx, tracks, st, opts)
    bar0 = apply_ending(sections, evs, fx, tracks, st, opts, key, chord_size, chord_color, bar0)
    shape_dynamics(evs, tracks, sections, st)
    evs += double_layers(evs, tracks)
    in_evs = {id(e) for e in evs}
    st['tuned_notes'] = fix_clashes(evs + [v for v in vocal if id(v) not in in_evs], {**tracks, 'vocal': tracks.get('vocal') or
                                    dict(layer='lead')}, key, st, sections)
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
    'hybrid_trailer', 'orchestral_hiphop', 'gospel', 'rnb', 'motown', 'swing', 'country', 'tango', 'salsa', 'kpop', 'ska',
    'indie_rock', 'bluegrass'}
# how often the bass steps into the next chord on the last beat (styles with a moving, song-like bass)
BASS_PASS = {'pop': 0.35, 'folk': 0.5, 'holiday': 0.5, 'western': 0.45, 'chamber_pop': 0.45, 'baroque': 0.6, 'chamber': 0.55,
             'neoclassical': 0.3, 'orchestral': 0.4, 'film_piano': 0.3, 'fantasy_rpg': 0.4, 'adventure': 0.3, 'reggae': 0.3,
             'rock': 0.25, 'disco': 0.2, 'city_pop': 0.3, 'soul_ballad': 0.5, 'celtic_jig': 0.4, 'waltz': 0.45, 'bossa_nova': 0.35,
             'synthpop': 0.2, 'eurodance': 0.15, 'downtempo': 0.25, 'lofi': 0.25, 'boombap': 0.2, 'symphonic_metal': 0.2,
             'country': 0.5, 'bluegrass': 0.6, 'motown': 0.4, 'gospel': 0.4, 'ska': 0.3, 'tango': 0.3, 'indie_rock': 0.3,
             'cumbia': 0.25, 'kpop': 0.2}
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
    'country': ['violin', 'softlead', 'guitar'], 'swing': ['brass', 'clarinet'], 'tango': ['cello', 'violin', 'accordion'],
    'kpop': ['strings', 'pluck', 'bell'], 'rnb': ['strings', 'guitar'], 'bluegrass': ['banjo', 'guitar'], 'salsa': ['flute', 'violin'],
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
NO_LAYER = {'808', 'logdrum', 'wobble', 'acid', 'sinebass', 'chipbass'}


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
        if role in (opts.instruments or {}) and want != 'more':
            continue
        part = {'bass': 'bass', 'lead': 'melody', 'arp': 'melody'}.get(role, 'chords')
        sd = ps.get(part) if ps.get(part) is not None else opts.seed * 1009 + PART_K[part]
        r = random.Random(f'{sd}-{role}-layer')
        owner = fusion.get({'bass': 'bass', 'chords': 'harmony', 'pad': 'harmony'}.get(role, 'melody'), opts.style)
        if role == 'bass':
            if cat != 'Electronic' or t['inst'] in NO_LAYER or r.random() > odds:
                continue
            inst, octv = 'sinebass', 0                       # the classic sub layer under a mid bass
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


def double_layers(evs, tracks):
    """The layer tracks play exactly the notes of the part they double (after tuning and dynamics)."""
    out = []
    for name, t in tracks.items():
        src = t.get('double_of')
        if not src:
            continue
        o = t.get('octave', 0)
        for e in evs:
            if e.track == src and e.midi is not None:
                m = e.midi + o
                if not 28 <= m <= 100:
                    m = e.midi
                out.append(Ev(name, e.beat, e.dur, m, e.vel * 0.9, None if e.glide is None else e.glide + (m - e.midi), e.mod))
    return out


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


BUILD_STYLES = ['roll', 'triplet', 'kick_roll', 'filter', 'stutter', 'pause', 'lift', 'swell']
GENRE_BUILD = {'trance': 'roll', 'bigroom': 'roll', 'progressive_house': 'roll', 'electro': 'roll', 'eurodance': 'roll',
               'moombahton': 'roll', 'dnb': 'roll', 'jungle': 'stutter', 'hardstyle': 'kick_roll', 'future_bass': 'triplet',
               'hyperpop': 'triplet', 'dubstep': 'stutter', 'breakcore': 'stutter', 'house': 'filter', 'deep_house': 'filter',
               'tech_house': 'filter', 'techno': 'filter', 'minimal': 'filter', 'acid_house': 'filter', 'psytrance': 'filter',
               'ukgarage': 'pause', 'amapiano': 'pause', 'afrobeats': 'pause', 'reggaeton': 'pause', 'synthwave': 'lift',
               'synthpop': 'lift', 'chiptune': 'lift', 'orchestral_hiphop': 'pause', 'hybrid_trailer': 'swell',
               'symphonic_metal': 'roll', 'kpop': 'lift', 'melodic_techno': 'filter', 'afro_house': 'filter',
               'jersey_club': 'pause', 'baile_funk': 'stutter', 'punk': 'roll', 'waltz': 'swell', 'celtic_jig': 'swell',
               'soul_ballad': 'swell'}
BIG_SECTIONS = {'chorus', 'hook', 'climax', 'theme', 'drop'}
HIT_FORMS = {'song', 'song_b', 'jazz', 'orchestral', 'cinematic', 'trap', 'halftime', 'halftime_b', 'chip', 'trailer'}


def _track_of(tracks, layer):
    return next((n for n, t in tracks.items() if t['layer'] == layer), None)


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
STYLE_GROOVE = {'boombap': 'dilla', 'lofi': 'dilla', 'phonk': 'dilla', 'reggae': 'laidback', 'downtempo': 'laidback',
                'afrobeats': 'afro', 'amapiano': 'afro', 'reggaeton': 'dembow', 'moombahton': 'dembow', 'jazz': 'jazz',
                'house': 'house', 'deep_house': 'house', 'tech_house': 'house', 'ukgarage': 'house',
                'funk': 'funk', 'disco': 'funk', 'city_pop': 'funk', 'rnb': 'laidback', 'gospel': 'laidback',
                'swing': 'jazz', 'afro_house': 'afro', 'dancehall': 'dembow', 'cumbia': 'afro'}


def add_build_drums(evs, st, tracks, snares, kick, b, nbars, beat0, rnd):
    """The build-up's drums, in the genre's idiom."""
    bs = st.get('build_style', 'roll')
    last = b == nbars - 1
    pb = b / max(1, nbars - 1)
    snare = snares[0] if snares else None

    def roll(track, divs):
        div = divs[0] if pb < 0.5 else (divs[1] if pb < 0.75 else (divs[2] if not last else divs[3]))
        for k in range(int(4 * div)):
            pos = k / div
            if last and pos >= 3.5:
                break
            evs.append(Ev(track, beat0 + pos, 0.25, None, 0.35 + 0.6 * (b + pos / 4) / nbars))
    if bs == 'roll' and snare:
        roll(snare, (1, 2, 4, 8))
    elif bs == 'triplet' and snare:
        roll(snare, (1, 1.5, 3, 6))                     # triplet subdivisions
    elif bs == 'kick_roll' and kick in tracks:
        roll(kick, (1, 2, 4, 4))
    elif bs == 'stutter' and snare:
        if b >= nbars - 2:                              # chopped, stuttering last two bars
            for k in range(16 if not last else 12):
                if rnd.random() < 0.85:
                    evs.append(Ev(snare, beat0 + k / 4, 0.12, None, 0.5 + 0.4 * k / 16))
        else:
            for pos in (1, 3):
                evs.append(Ev(snare, beat0 + pos, 0.25, None, 0.7))
    elif bs == 'filter' and last and snare and rnd.random() < 0.6:
        for k in range(4):                              # a little clap/snare push into the drop
            evs.append(Ev(snare, beat0 + 2 + k / 2, 0.25, None, 0.5 + 0.12 * k))
    elif bs == 'lift' and last and snare:
        for k in range(8):
            evs.append(Ev(snare, beat0 + k / 2, 0.25, None, 0.4 + 0.07 * k))
        for k in range(4):
            evs.append(Ev(snare, beat0 + 3 + k / 4, 0.25, None, 0.85))
    elif bs == 'swell' and snare and b >= nbars - 2:
        g = grid_of(st)
        for k in range(g if not last else g - 2):
            evs.append(Ev(snare, beat0 + 4 * k / g, 0.25, None, 0.25 + 0.6 * ((b - nbars + 2) * g + k) / (2 * g)))
    if bs in ('filter', 'kick_roll', 'lift') and last:   # kick drops out on the final beat
        evs[:] = [e for e in evs if not (e.track == kick and e.beat >= beat0 + 3)]


def add_build_fx(fx, bs, start, nbars):
    end = start + nbars * 4
    if bs in ('roll', 'triplet', 'kick_roll', 'stutter'):
        fx.append(('riser', start, nbars * 4))
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('gap', end - (1.0 if bs == 'stutter' else 0.5), 1.0 if bs == 'stutter' else 0.5))
    elif bs == 'filter':                                # long filter, short riser, kick-out
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('riser', end - 8, 8))
        fx.append(('gap', end - 1, 1))
    elif bs == 'pause':                                 # the band drops out, a swell, straight back in
        fx.append(('swell', end - 4, 4))
        fx.append(('gap', end - 0.5, 0.5))
    elif bs == 'lift':
        fx.append(('swell', end - 4, 4))
    elif bs == 'swell':
        fx.append(('riser', start, nbars * 4))
        fx.append(('swell', end - 4, 4))


def add_transitions(sections, evs, fx, tracks, st, opts):
    """A fill and a reverse-cymbal swell into every bigger section (chorus, drop, climax), in the genre's idiom:
    tom fills for band styles, snare fills for electronic ones."""
    from .instruments import DRUMS
    rnd = random.Random(opts.seed * 13 + 5)
    cat = st.get('category')
    snare = next((s for s in st.get('snare_tracks', []) if s in tracks), None)
    for cur, nxt in zip(sections, sections[1:]):
        bigger = nxt['opts'].get('drop') or nxt['name'] in BIG_SECTIONS
        if not bigger or cur['opts'].get('build'):
            continue
        end = (cur['bar'] + cur['bars']) * 4
        fx.append(('swell', end - 4, 4))
        if 'snare' not in cur['layers'] or not snare or rnd.random() > 0.55 + 0.45 * opts.energy:
            continue
        beats = 2 if cat == 'Classic' else rnd.choice([1, 1, 2])
        start = end - beats
        drum_names = {n for n, t in tracks.items() if t['inst'] in DRUMS and t['layer'] in ('snare', 'top')}
        evs[:] = [e for e in evs if not (e.track in drum_names and start <= e.beat < end)]
        sub = 4 if grid_of(st) == 16 else 3                 # 16ths, or triplet 8ths in 3/4, 6/8, 12/8
        if cat == 'Classic' and opts.structure != 'loop':
            for name, pitch in (('tom_hi', 190), ('tom_mid', 140), ('tom_lo', 100)):
                if name not in tracks:
                    t = dict(name=name, layer='snare', inst='tom', pan={'tom_hi': 0.25, 'tom_mid': 0.0, 'tom_lo': -0.25}[name],
                             rev=0.12, dly=0.0, sc=0.0, db=-19, hp=None, drive=None, p={})
                    tracks[name] = t
                    st['tracks'].append(t)
                st.setdefault('drum_voice', {})[name] = {'pitch': pitch}
            n = beats * sub
            for k in range(n):
                name = 'tom_hi' if k < n / 3 else ('tom_mid' if k < 2 * n / 3 else 'tom_lo')
                if k % 2 == 0 or rnd.random() < 0.6:
                    evs.append(Ev(snare if k == 0 else name, start + k / sub, 0.25, None, 0.6 + 0.35 * k / n))
        else:
            n = beats * sub
            for k in range(n):
                evs.append(Ev(snare, start + k / sub, 0.25, None, 0.45 + 0.5 * k / n))


def apply_ending(sections, evs, fx, tracks, st, opts, key, chord_size, chord_color, total_bars):
    """End on a final chord hit with crash (bands, film, hip-hop) instead of fading out; club mixes keep their fade."""
    mode = getattr(opts, 'ending', 'auto') or 'auto'
    form = st.get('form') if isinstance(st.get('form'), str) else ''
    if mode == 'auto':
        mode = 'hit' if (form in HIT_FORMS and opts.structure not in ('club', 'loop')) else 'fade'
    if mode != 'hit' or opts.structure == 'loop' or not sections:
        return total_bars
    last = sections[-1]
    fx[:] = [f for f in fx if not (f[0] == 'fade' and f[1] >= last['bar'] * 4)]
    end = total_bars * 4
    shift = next((s_['key_change'] for s_ in sections if s_.get('key_change')), 0)
    ring = 6.0
    ch, pad, bass = _track_of(tracks, 'chords'), _track_of(tracks, 'pad'), _track_of(tracks, 'bass')
    third = (key.deg(2, 4) - key.deg(0, 4)) % 12
    pic = None                                     # Picardy third: a minor-key piece ends on a major chord
    if third == 3 and st.get('category') in ('Orchestral', 'Classic') and st.get('voicing') != 'power' \
            and random.Random(opts.seed * 17 + 3).random() < 0.35:
        pic = key.deg(2, 4) % 12
    lift = lambda m: m + 1 if pic is not None and m % 12 == pic else m
    if ch:
        for m in voice_chord(key, 0, chord_size, st.get('chord_center', 62), st.get('voicing', 'close'),
                             chord_color if chord_color in COLORS else None):
            evs.append(Ev(ch, end, ring, lift(m) + shift, 0.88))
    if pad:
        for m in voice_chord(key, 0, 3, st.get('chord_center', 62) - 2, 'open'):
            evs.append(Ev(pad, end, ring, lift(m) + shift, 0.7))
    if pic is not None:
        last['picardy'] = True
    if bass:
        evs.append(Ev(bass, end, ring - 1, fold(key.deg(0, 2), st['bass_lo']) + shift, 0.9))
    kick = st.get('kick_track', 'kick')
    if kick in tracks:
        evs.append(Ev(kick, end, 0.25, None, 1.0))
    fx.append(('crash', end, 0))
    if st.get('category') == 'Orchestral' or form == 'cinematic':
        fx.append(('impact', end, 0))
    last['ending'] = 'hit'
    return total_bars + 1                          # the hit rings out into the render's tail


def section_window(song, index, preroll_bars=2, max_bars=20):
    """Excerpt containing one section (plus a short lead-in) - for auditioning edits."""
    sec = song['sections'][index]
    b0 = max(0, sec['bar'] - preroll_bars)
    b1 = min(song['total_bars'], sec['bar'] + min(sec['bars'], max_bars))
    return _window(song, b0, b1, fade=True)


def loop_window(song, bars=8):
    """Clean loop from the start of the most energetic section, no fades (sample packs)."""
    best = max(song['sections'], key=lambda s: len(s['layers']) + (3 if s['opts'].get('drop') else 0))
    b0 = best['bar']
    return _window(song, b0, min(song['total_bars'], b0 + bars), fade=False, keep_fx=False)


def _window(song, b0, b1, fade=True, keep_fx=True):
    beat0, beat1 = b0 * 4, b1 * 4
    evs = [Ev(e.track, e.beat - beat0, min(e.dur, beat1 - e.beat), e.midi, e.vel, e.glide, e.mod)
           for e in song['events'] if beat0 <= e.beat < beat1]
    fx = []
    for kind, b, d in song['fx']:
        if not keep_fx:
            continue
        if kind in ('crash', 'impact') and beat0 <= b < beat1:
            fx.append((kind, b - beat0, d))
        if kind in ('riser', 'hpsweep', 'gap', 'lpsweep') and b < beat1 and b + d > beat0:
            nb = max(b, beat0)
            fx.append((kind, nb - beat0, min(b + d, beat1) - nb))
    if fade:
        fx.append(('fade', beat1 - beat0 - 4, 4))
    secs = []
    for s in song['sections']:
        s0, s1 = max(s['bar'], b0), min(s['bar'] + s['bars'], b1)
        if s1 > s0:
            secs.append(dict(s, bar=s0 - b0, bars=s1 - s0))
    pv = dict(song)
    pv.update(events=evs, fx=fx, sections=secs, total_bars=b1 - b0, preview_of=(b0, b1))
    return pv


def preview_window(song, target_sec=26.0):
    """Cut a short excerpt around the most energetic section (for quick auditioning)."""
    spb = 60.0 / song['bpm']
    bar_sec = 4 * spb
    nbars = int(max(8, min(16, round(target_sec / bar_sec / 4) * 4)))
    best = None
    for s in song['sections']:
        score = len(s['layers']) + (3 if s['opts'].get('drop') else 0) + (1 if s['name'] in ('chorus', 'hook', 'climax', 'B', 'head', 'theme', 'loop') else 0)
        if best is None or score > best[0]:
            best = (score, s)
    sec = best[1]
    b0 = max(0, sec['bar'] - (2 if sec['bar'] >= 2 else 0))
    b1 = min(song['total_bars'], b0 + nbars)
    beat0, beat1 = b0 * 4, b1 * 4
    evs = []
    for e in song['events']:
        if beat0 <= e.beat < beat1:
            evs.append(Ev(e.track, e.beat - beat0, min(e.dur, beat1 - e.beat), e.midi, e.vel, e.glide, e.mod))
    fx = []
    for kind, b, d in song['fx']:
        if kind in ('crash', 'impact') and beat0 <= b < beat1:
            fx.append((kind, b - beat0, d))
        if kind in ('riser', 'hpsweep', 'gap') and b < beat1 and b + d > beat0:
            nb = max(b, beat0)
            fx.append((kind, nb - beat0, min(b + d, beat1) - nb))
    fx.append(('fade', beat1 - beat0 - 4, 4))
    secs = []
    for s in song['sections']:
        s0, s1 = max(s['bar'], b0), min(s['bar'] + s['bars'], b1)
        if s1 > s0:
            secs.append(dict(s, bar=s0 - b0, bars=s1 - s0))
    pv = dict(song)
    pv.update(events=evs, fx=fx, sections=secs, total_bars=b1 - b0, preview_of=(b0, b1))
    return pv
