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
    groove: str = None            # None = genre feel | straight | dilla | laidback | afro | dembow | jazz | house | funk
    mood: str = None              # dark | happy | chill | epic | dreamy | aggressive | melancholic | energetic | mysterious | romantic

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
                'lofi': 'pentatonic', 'pop': 'pentatonic', 'disco': 'pentatonic', 'jazz': 'bebop', 'bossa_nova': 'bebop'}
GENRE_VOICING = {'jazz': 'rootless', 'bossa_nova': 'rootless', 'lofi': 'rootless', 'boombap': 'rootless', 'city_pop': 'drop2',
                 'deep_house': 'drop2', 'ukgarage': 'drop2', 'funk': 'drop2', 'disco': 'drop2', 'downtempo': 'drop2'}
GENRE_COLORS = {'jazz': ['7', '9', '9', '6'], 'bossa_nova': ['7', '9', '6'], 'lofi': ['7', '9', 'add9'], 'boombap': ['7', '9'],
                'city_pop': ['7', '9', 'add9'], 'deep_house': ['7', '9', 'add9'], 'ukgarage': ['7', '9'], 'funk': ['7', '9'],
                'blues': ['7'], 'downtempo': ['7', 'add9', '9']}


def fold(m, lo):
    while m < lo:
        m += 12
    while m >= lo + 12:
        m -= 12
    return m


def parse_rhythm(pat):
    out = []
    for i, c in enumerate(pat):
        if c not in '.-':
            l = 1
            j = i + 1
            while j < len(pat) and pat[j] == '-':
                l += 1
                j += 1
            out.append((i, l, c))
    return out


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
EXTRA_RHYTHMS = ['x.x.x.x.x-x-x---', 'x--x--x-x--x--x-', '..x.x.x...x.x...', 'x-.x-.x-x-x-....', 'x---x.x.x---x...',
                 '.x.x.x.x.x.x.x..', 'x-x-..x-x-..x-x-', 'x---..x-..x-x---', 'x.xx.xx.x.......', '....x-x-x-x-x---',
                 'x-----x-----x---', 'x.x...x.x...x.x.']


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


def apply_variety(st, opts, rnd):
    """Give every song its own palette: instrument swaps, tone tweaks, extra groove patterns, kit and arrangement."""
    v = max(0.0, min(1.0, float(opts.variety)))
    if v <= 0:
        return st
    fam = groove_family(st)
    ps = opts.part_seeds or {}
    PART_K = {'harmony': 1, 'melody': 2, 'drums': 3, 'bass': 4, 'chords': 5}

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
        bank = EXTRA_BASS.get(fam, EXTRA_BASS['other'])
        st['bass'] = list(st['bass']) + rb.sample(bank, min(len(bank), 1 + int(2 * v)))
    rc = r_for('chords')
    if st.get('voicing') != 'power' and rc.random() < 0.3 + 0.6 * v:
        bank = EXTRA_CHORD_RH.get(fam, EXTRA_CHORD_RH['other'])
        st['chord_rh'] = list(st['chord_rh']) + rc.sample(bank, min(len(bank), 1 + int(2 * v)))
    pal = PALETTES.get(st.get('category'), {})
    part_rng = {}
    chip_locked = st.get('name') == 'chiptune' and v < 0.85
    tracks = []
    for t in st['tracks']:
        t = dict(t, p=dict(t['p']))
        role = t['layer']
        rr = part_rng.setdefault(role, r_for({'bass': 'bass', 'lead': 'melody'}.get(role, 'chords')))
        if role in pal and role not in (opts.instruments or {}) and not chip_locked and rr.random() < 0.12 + 0.5 * v:
            choice = rr.choice(pal[role])
            if choice != t['inst']:
                t.update(inst=choice, p={}, db=None)
        for k in ('cut', 'bright'):
            if k in t['p']:
                t['p'][k] *= 2 ** (rr.uniform(-0.6, 0.6) * v)
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
        mapped = None if user_pick else ACOUSTIC_MAP.get(name, {}).get(t['layer'])
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
    apply_sampled(st, opts)
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


def gen_melody(key, prog, chord_bars, st, rnd, complexity):
    phrase_bars = 2 * len(prog) * chord_bars
    extra = rnd.sample(EXTRA_RHYTHMS, 3)
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
    d = prog[0] + rnd.choice([0, 2, 4])
    while d > hi:
        d -= 7
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
                d = motif[(src, i)]
            else:
                d += rnd.choices(steps, w)[0]
                if d > hi:
                    d = hi - (d - hi)
                if d < lo:
                    d = lo + (lo - d)
            strong = step % 4 == 0
            if strong and (reuse or rnd.random() < 0.8):
                d = min(ct, key=lambda x: (abs(x - d), x))
            if b8 < 2 and (bar < 8 or phrase_bars <= 8):
                motif[(b8, i)] = d
            last = (b8 == 7 and i == len(rh) - 1)
            ln = l
            if last:
                d = min([x for x in ct if (x - chord) % 7 == 0] or ct, key=lambda x: abs(x - d))
                ln = max(l, 16 - step)
            vel = (0.95 if strong else 0.78) * rnd.uniform(0.9, 1.05)
            if avoid and d % 7 in avoid and not (strong and d in ct):      # pentatonic: step off the avoid notes
                d = d + 1 if (d + 1) % 7 not in avoid and d + 1 <= hi else d - 1
            t = bar * 4 + step / 4
            midi = key.deg(d, st['lead_oct'])
            prev_end = notes[-1][0] + notes[-1][1] if notes else -1
            if lang == 'blues' and strong and d % 7 in (0, 2, 4) and lrnd.random() < (0.45 if d % 7 == 2 else 0.2) \
                    and t - 0.125 >= prev_end:                                # bluesy slide up into the note
                notes.append((t - 0.125, 0.11, midi - 1, vel * 0.7))
            elif lang == 'bebop' and strong and lrnd.random() < 0.25 + 0.35 * complexity and t - 0.25 >= prev_end:
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
    apply_sampled(st, opts)
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
    if sname in GENRE_COLORS:                       # genres whose harmony is defined by extended chords
        chord_color = random.Random(opts.seed * 31 + 7).choice(GENRE_COLORS[sname])
    if getattr(opts, 'chord_color', None) in COLORS:
        chord_color = opts.chord_color
    if st.get('voicing') != 'power' and sname in GENRE_VOICING:
        st['voicing'] = GENRE_VOICING[sname]
    if getattr(opts, 'voicing', None) in VOICINGS:
        st['voicing'] = opts.voicing
    st['melody_lang'] = opts.melody_style if getattr(opts, 'melody_style', None) in MELODY_STYLES else GENRE_MELODY.get(sname, 'diatonic')
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
                    for step in range(16):
                        if step not in used and rnd_d.random() < (energy - 0.7) * 1.6:
                            evs.append(Ev(dname, beat0 + step / 4, 0.25, None, 0.35))
                if st.get('ghosts') and dname in snares[:1]:
                    for step in range(16):
                        if step % 4 != 0 and step not in used and rnd_d.random() < 0.06 + 0.12 * energy:
                            evs.append(Ev(dname, beat0 + step / 4, 0.25, None, 0.28))
            if st.get('trap_hats') and 'top' in layers and 'chat' not in st['drums']:
                gen_trap_hats(evs, beat0, rnd_d, energy)
            if (st.get('fill') or energy > 0.6) and 'snare' in layers and b % 8 == 7 and snares and rnd_d.random() < 0.4 + 0.5 * energy:
                s = snares[0]
                for k, step in enumerate(rnd_d.choice([[13, 14, 15], [12, 13, 14, 15], [10, 13, 14, 15], [14, 15]])):
                    evs.append(Ev(s, beat0 + step / 4, 0.25, None, 0.55 + 0.1 * k))
            if opts_s.get('build') and snares:
                pb = b / max(1, nbars - 1)
                div = 1 if pb < 0.5 else (2 if pb < 0.75 else (4 if b < nbars - 1 else 8))
                for k in range(4 * div):
                    pos = k / div
                    if b == nbars - 1 and pos >= 3.5:
                        break
                    evs.append(Ev(snares[0], beat0 + pos, 0.25, None, 0.35 + 0.6 * (b + pos / 4) / nbars))
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
                            m = tgt + (1 if tgt <= root else -1) * (1 if rnd_b.random() < 0.5 else 2)
                        else:
                            m = root
                        evs.append(Ev('bass', beat0 + step / 4, l / 4 * gate, m, rnd_b.uniform(0.85, 1.0)))
            # ---------------- chords
            if 'chords' in layers and 'chords' in tracks and chord_pat and (b % cb == 0):
                col = chord_color if st.get('voicing', 'close') != 'power' and chord_size <= 4 else None
                if col and rnd_c.random() < 0.15:
                    col = rnd_c.choice(['sus4', 'sus2', col])
                notes = voice_chord(key, chord, chord_size, st.get('chord_center', 62), st.get('voicing', 'close'), col)
                for step, l, c in parse_rhythm(chord_pat):
                    dur = l / 4 * (cb if l == 16 else 1) * 0.95
                    if (opts_s.get('drop') or sname in BIG_SECTIONS) and notes and notes[-1] + 12 <= 96 and st.get('voicing') != 'power':
                        notes = notes + [notes[-1] + 12]               # choruses / drops open up: top note doubled
                    for i, m in enumerate(notes):
                        off = i * st.get('strum', 0.0)
                        evs.append(Ev('chords', beat0 + step / 4 + off, dur, m, rnd_c.uniform(0.75, 0.92)))
            # ---------------- pad
            if 'pad' in layers and 'pad' in tracks and (b % cb == 0):
                notes = voice_chord(key, chord, min(4, chord_size), st.get('chord_center', 62) - 2, pad_voicing,
                                    chord_color if chord_color in ('triad', '7', 'add9', 'sus2', '6') else None)
                for m in notes:
                    evs.append(Ev('pad', beat0, 4 * cb * 0.98, m, 0.8))
            # ---------------- arp
            if 'arp' in layers and 'arp' in tracks:
                tones = voice_chord(key, chord, 3, 12 * (arp['oct'] + 1) + 4)
                seq = tones + [tones[0] + 12]
                if arp['mode'] == 'updown':
                    seq = seq + seq[-2:0:-1]
                rate = arp['rate']
                for k in range(int(16 / rate)):
                    if arp.get('prob') and rnd_c.random() > arp['prob']:
                        continue
                    m = rnd_c.choice(seq) if arp['mode'] == 'random' else seq[k % len(seq)]
                    evs.append(Ev('arp', beat0 + k * rate / 4, rate / 4 * 0.8, m,
                                  (0.95 if k % 4 == 0 else 0.75) * rnd_c.uniform(0.9, 1.0)))
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
            fx.append(('riser', sec_start, nbars * 4))
            fx.append(('gap', sec_start + nbars * 4 - 0.5, 0.5))
            fx.append(('hpsweep', sec_start, nbars * 4))
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
    sname = '+'.join([opts.style] + [b for b in (opts.blend or []) if b != opts.style])
    song = dict(style=sname, seed=opts.seed, bpm=bpm, key=key, events=evs, sections=sections, fx=fx,
                total_bars=bar0, prog_main=prog_main, prog_alt=prog_alt, prog_verse=prog_verse, chord_color=chord_color,
                modulate=modulate, st=st, opts=opts, user_opts=user_opts, vocal=vocal,
                energy=energy)
    return song


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


BIG_SECTIONS = {'chorus', 'hook', 'climax', 'theme', 'drop'}
HIT_FORMS = {'song', 'song_b', 'jazz', 'orchestral', 'cinematic', 'trap', 'halftime', 'halftime_b', 'chip'}


def _track_of(tracks, layer):
    return next((n for n, t in tracks.items() if t['layer'] == layer), None)


VOCAL_SECTIONS = {'verse': (-2, 5), 'chorus': (1, 9), 'hook': (1, 9), 'drop': (1, 9), 'head': (0, 7), 'A': (0, 7),
                  'theme': (0, 8), 'climax': (2, 9)}
VOCAL_RHYTHMS = ['x.x.x.x-x-......', 'x-x-x.x.x---....', '..x.x.x.x-x-....', 'x.x.x-x.x.x-....', 'x---x.x.x-x-....',
                 '..x.x-x-x.x.x...', 'x.x.x.x.x.x-....', 'x-.xx-x-x---....']


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
                'funk': 'funk', 'disco': 'funk', 'city_pop': 'funk'}


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
        if cat == 'Classic' and opts.structure != 'loop':
            for name, pitch in (('tom_hi', 190), ('tom_mid', 140), ('tom_lo', 100)):
                if name not in tracks:
                    t = dict(name=name, layer='snare', inst='tom', pan={'tom_hi': 0.25, 'tom_mid': 0.0, 'tom_lo': -0.25}[name],
                             rev=0.12, dly=0.0, sc=0.0, db=-19, hp=None, drive=None, p={})
                    tracks[name] = t
                    st['tracks'].append(t)
                st.setdefault('drum_voice', {})[name] = {'pitch': pitch}
            n = beats * 4
            for k in range(n):
                name = 'tom_hi' if k < n / 3 else ('tom_mid' if k < 2 * n / 3 else 'tom_lo')
                if k % 2 == 0 or rnd.random() < 0.6:
                    evs.append(Ev(snare if k == 0 else name, start + k / 4, 0.25, None, 0.6 + 0.35 * k / n))
        else:
            n = beats * 4
            for k in range(n):
                evs.append(Ev(snare, start + k / 4, 0.25, None, 0.45 + 0.5 * k / n))


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
    if ch:
        for m in voice_chord(key, 0, chord_size, st.get('chord_center', 62), st.get('voicing', 'close'),
                             chord_color if chord_color in COLORS else None):
            evs.append(Ev(ch, end, ring, m + shift, 0.88))
    if pad:
        for m in voice_chord(key, 0, 3, st.get('chord_center', 62) - 2, 'open'):
            evs.append(Ev(pad, end, ring, m + shift, 0.7))
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
