"""Composition: harmony, melody, bass, drums and arrangement -> a list of note events."""
import math
import random
import re
from dataclasses import dataclass, field, asdict

from .styles import STYLES, FORMS
from .instruments import KITS, INSTRUMENTS

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
        q = p.lower().rstrip('°o+7m')
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


def voice_chord(key, deg, size, center, voicing='close'):
    if voicing == 'power':
        root = key.deg(deg, 4) % 12
        lo = center - 6
        r = lo + ((root - lo) % 12)
        return [r, r + 7, r + 12]
    pcs = [key.deg(deg + 2 * i, 4) % 12 for i in range(size)]
    lo = center - 6
    return sorted(lo + ((pc - lo) % 12) for pc in pcs)


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
    'major': [[0, 4, 5, 3], [0, 5, 3, 4], [3, 4, 0, 0], [5, 3, 0, 4]],
    'minor': [[0, 5, 2, 6], [0, 3, 4, 0], [0, 6, 5, 6], [0, 5, 3, 4]],
    'dorian': [[0, 3, 0, 3], [0, 3, 6, 4], [0, 6, 3, 0]],
    'phrygian': [[0, 1, 0, 1], [0, 1, 6, 0], [0, 0, 1, 0]],
    'harmonic_minor': [[0, 5, 3, 4], [0, 3, 4, 0]],
    'mixolydian': [[0, 6, 3, 0], [0, 0, 3, 0]],
    'lydian': [[0, 1, 0, 1], [0, 1, 4, 0]],
}


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
        if new and new in INSTRUMENTS and new != t['inst']:
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


def gen_melody(key, prog, chord_bars, st, rnd, complexity):
    phrase_bars = 2 * len(prog) * chord_bars
    rhs = sorted((parse_rhythm(r) for r in st['lead_rh']), key=len)
    if complexity < 0.35:
        pool = rhs[:max(2, len(rhs) // 2 + 1)]
    elif complexity > 0.65:
        pool = rhs[len(rhs) // 2 - 1:] if len(rhs) > 2 else rhs
    else:
        pool = rhs
    idx = list(range(len(pool)))
    rnd.shuffle(idx)
    r0, r1, r2, r3 = (pool[idx[i % len(idx)]] for i in range(4))
    plan8 = [r0, r1, r0, r1, r0, r1, r2, r3]
    lo, hi = -3, 10
    d = prog[0] + rnd.choice([0, 2, 4])
    while d > hi:
        d -= 7
    motif = {}
    notes = []
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
            notes.append((bar * 4 + step / 4, ln / 4 * 0.92, key.deg(d, st['lead_oct']), vel))
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
    progs = st['progs']
    if isinstance(progs, dict):
        progs = progs.get(scale) or GENERIC_PROGS.get(scale) or next(iter(progs.values()))
    elif scale not in st['scales']:
        progs = GENERIC_PROGS.get(scale, progs)
    custom = parse_progression(opts.progression)
    progs = [p for p in progs if all(key.chord_ok(d) for d in p)] or [[0, 3, 4, 0]]
    pi = rnd.sample(range(len(progs)), min(2, len(progs)))
    prog_main = custom or progs[pi[0]]
    prog_alt = custom or progs[pi[-1]]
    cb = st['chord_bars']
    chord_size = st['chord_size'] + (1 if cx > 0.72 else 0) - (1 if cx < 0.28 and st['chord_size'] > 3 else 0)
    chord_size = max(3, min(5, chord_size))
    mel_main, ph_bars = gen_melody(key, prog_main, cb, st, rnd_m, cx)
    mel_alt, _ = gen_melody(key, prog_alt, cb, st, rnd_m, cx)
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
    for (sname, nbars, layers, opts_s) in form:
        if not opts_s.get('build') and opts.structure != 'loop':
            nbars = max(4, int(round(nbars * scale_len / 4)) * 4)
        layers = set(layers) - muted
        if energy > 0.75 and opts_s.get('drop'):
            layers |= {'arp'} - muted
        if energy < 0.25:
            layers -= {'arp'} if sname not in ('drop', 'chorus', 'hook', 'climax') else set()
        prog = prog_alt if opts_s.get('alt') else prog_main
        mel = mel_alt if opts_s.get('alt') else mel_main
        sec_start = bar0 * 4
        sections.append(dict(name=sname, bar=bar0, bars=nbars, layers=sorted(layers), opts=opts_s))
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
                if mode == '808':
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
                notes = voice_chord(key, chord, chord_size, st.get('chord_center', 62), st.get('voicing', 'close'))
                for step, l, c in parse_rhythm(chord_pat):
                    dur = l / 4 * (cb if l == 16 else 1) * 0.95
                    for i, m in enumerate(notes):
                        off = i * st.get('strum', 0.0)
                        evs.append(Ev('chords', beat0 + step / 4 + off, dur, m, rnd_c.uniform(0.75, 0.92)))
            # ---------------- pad
            if 'pad' in layers and 'pad' in tracks and (b % cb == 0):
                notes = voice_chord(key, chord, min(4, chord_size), st.get('chord_center', 62) - 2)
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
            reps = int(math.ceil(nbars / ph_bars))
            for r in range(reps):
                for (bt, du, m, v) in mel:
                    beat = sec_start + r * ph_bars * 4 + bt
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

    sname = '+'.join([opts.style] + [b for b in (opts.blend or []) if b != opts.style])
    song = dict(style=sname, seed=opts.seed, bpm=bpm, key=key, events=evs, sections=sections, fx=fx,
                total_bars=bar0, prog_main=prog_main, prog_alt=prog_alt, st=st, opts=opts, user_opts=user_opts,
                energy=energy)
    return song


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
