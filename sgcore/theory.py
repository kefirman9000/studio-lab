"""Music theory: scales, keys, chord voicings, rhythm patterns and the note event."""
import re


SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10], 'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10], 'harmonic_minor': [0, 2, 3, 5, 7, 8, 11], 'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'phrygian_dominant': [0, 1, 4, 5, 7, 8, 10],   # 'Spanish' / Hijaz: dramatic, exotic - phonk, dark electronic, metal
    'melodic_minor': [0, 2, 3, 5, 7, 9, 11],       # jazz minor: minor with a bright top - jazz, sophisticated electronic
}


NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


FLAT_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']


FLAT_ALIASES = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}


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


def color_fits(key, deg, color):
    """Does this colour really form that chord on this scale degree? (sus4 on vii is a tritone, add9 on iii a b9 ...)"""
    if color in (None, 'triad', '7'):
        return True
    r = key.deg(deg, 4)
    iv = lambda k: (key.deg(deg + k, 4) - r) % 12
    fifth_ok = iv(4) == 7
    if color == 'sus2':
        return iv(1) == 2 and fifth_ok
    if color == 'sus4':
        return iv(3) == 5 and fifth_ok
    if color in ('add9', '9', 'add9no3'):
        return iv(1) == 2 and fifth_ok                # a major 9th; a minor 9th grinds against the root
    if color == '6':
        return iv(5) == 9 and fifth_ok                # a major 6th; a minor 6th rubs against the 5th
    return True


def declutter(notes, key, deg, color=None):
    """No two chord notes a semitone apart: the colour note (7th / 9th / 6th) moves up an octave, where it rings open."""
    notes = sorted(notes)
    core = {key.deg(deg + k, 4) % 12 for k in ((0, 1, 4) if color == 'sus2' else (0, 3, 4) if color == 'sus4' else (0, 2, 4))}
    for _ in range(6):
        clash = next(((a, b) for a, b in zip(notes, notes[1:]) if b - a == 1), None)
        if not clash:
            break
        a, b = clash
        mover = b if b % 12 not in core else (a if a % 12 not in core else None)
        if mover is None:
            break
        notes.remove(mover)
        up = mover + 12
        notes = sorted(notes + [up if up <= max(notes + [mover]) + 12 else mover - 12])
    return notes


def voice_chord(key, deg, size, center, voicing='close', color=None):
    if color and not color_fits(key, deg, color):
        color = '7' if color == '9' and size >= 4 else None
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
    return declutter(notes, key, deg, color)


VOICINGS = ['close', 'open', 'drop2', 'rootless', 'power']


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
        c += 12 * sum(1 for a, b in zip(o, o[1:]) if b - a == 1)      # a semitone cluster sounds like two notes, not a chord
        mid = (o[0] + o[-1]) / 2
        c += 1.5 * max(0, abs(mid - center) - 5)
        if o[0] < center - 13 or o[-1] > center + 15:
            c += 60
        return c
    return min(opts, key=cost)


class Ev:
    __slots__ = ('track', 'beat', 'dur', 'midi', 'vel', 'glide', 'mod', 'strum', 'slide')

    def __init__(self, track, beat, dur, midi, vel, glide=None, mod=None, strum=0.0, slide=0.0):
        self.track, self.beat, self.dur, self.midi, self.vel, self.glide, self.mod = track, beat, dur, midi, vel, glide, mod
        self.strum = strum                       # beats after the chord's own position (strummed chords move as one)
        self.slide = slide                       # semitones the note slides up from (fiddle / steel / guitar / harmonica)


def chord_tones_deg(chord, lo, hi):
    out = []
    for k in range(-2, 4):
        for iv in (0, 2, 4):
            d = chord + 7 * k + iv
            if lo <= d <= hi:
                out.append(d)
    return out


# chord colours: scale-degree stacks above the root (0=root 2=3rd 4=5th 6=7th 8=9th, 1/3 = sus2/sus4, 5 = 6th)
COLORS = {'triad': [0, 2, 4], '7': [0, 2, 4, 6], 'add9': [0, 2, 4, 8], 'sus2': [0, 1, 4], 'sus4': [0, 3, 4],
          '9': [0, 2, 4, 6, 8], '6': [0, 2, 4, 5], 'add9no3': [0, 4, 8]}
