"""Cinematic Journey - a through-composed orchestral score (the Orchestral tab's "ultimate" generator).

Unlike the pattern genres, every bar here is written for its place in a story:

    Tension     low celli & basses creeping in muted ostinatos, soft timpani rolls, icy notes at the bottom of the piano
    Sorrow      solo piano sings the theme over soft-vibrato string pads and gentle horn swells
    Resolve     violins & violas take the theme in long legato, spiccato ostinatos and rising runs drive forward,
                horns & trumpets in noble lines, trombones & tuba in weighty chords and short marcato statements
    Glory       full tutti: high violins, brass fanfares, thundering timpani & bass drum, cascading piano arpeggios,
                woodwind counter-melodies and high string "choir" harmonics
    Reflection  the piano alone again, fragile, over high shimmering strings and distant soft brass
    Resolution  full strings and warm low brass hold one long luminous chord that fades into silence

One theme (rhythm + contour) is invented per song and re-harmonised in every act, so the piece is recognisably about
one idea. Tempo follows the story (a tempo map with accelerando, allargando and a final ritardando, plus phrase
rubato), and dynamics run from near-silence to full fortissimo (section levels, note velocities - which choose the
soft / loud recordings of the real orchestra - and mod-wheel curves for orchestra plugins such as BBC SO).
"""
import math
import random

from .compose import Ev, Key

ACTS = [('tension', 'Tension', 16), ('sorrow', 'Sorrow', 16), ('resolve', 'Resolve', 16), ('battle', 'Battle', 8),
        ('glory', 'Glory', 16), ('reflection', 'Reflection', 8), ('resolution', 'Resolution', 8)]
ACT_IDS = [a[0] for a in ACTS]
HERO = ['tension', 'sorrow', 'resolve', 'glory', 'reflection', 'resolution']
DEFAULTS = dict(acts=HERO, piano=0.6, rubato=0.5, dynamics=0.75, ending='major', woodwinds=True, lift=True, choir=True,
                hybrid=False, glory_style='concert', lengths={}, preset='hero')
# one-click story arcs (the Journey card's presets); any setting you change afterwards wins
PRESETS = {
    'hero': dict(acts=HERO, ending='major'),
    'tragedy': dict(acts=['tension', 'sorrow', 'resolve', 'battle', 'reflection', 'resolution'], ending='minor', piano=0.7,
                    dynamics=0.85, lift=False, lengths={'reflection': 1.5}),
    'triumph': dict(acts=['tension', 'resolve', 'battle', 'glory', 'resolution'], ending='major', piano=0.4, dynamics=0.7,
                    glory_style='battle', lengths={'tension': 0.5, 'glory': 1.5}),
    'elegy': dict(acts=['sorrow', 'reflection', 'resolution'], ending='major', piano=0.95, dynamics=0.45, rubato=0.75,
                  choir=False, lengths={'sorrow': 1.5, 'reflection': 1.5}),
}
UNPITCHED = {'bdrum', 'cym', 'taiko', 'snare', 'anvil'}
# every player, for the Sound panel (track name -> label)
PLAYERS = [('piano', 'Solo piano'), ('vn1', 'Violins I (melody)'), ('vn_hi', 'High strings / harmonics'), ('va', 'Violas'),
           ('vc', 'Celli'), ('cb', 'Double basses'), ('pad', 'String section (sustain)'), ('trem', 'Strings tremolo'),
           ('spicc_lo', 'Low string ostinato'), ('spicc_hi', 'High string runs'), ('horns', 'French horns'), ('tpt', 'Trumpets'),
           ('tbn', 'Trombones (sustain)'), ('tbn_marc', 'Trombones (marcato hits)'), ('tuba', 'Tuba'), ('cbtbn', 'Contrabass trombone'),
           ('cbsn', 'Contrabassoon'), ('flute', 'Flute'), ('oboe', 'Oboe'), ('clar', 'Clarinet'), ('harp', 'Harp'),
           ('choir', 'Choir "aah"'), ('choir_oo', 'Choir "ooh"'), ('timp', 'Timpani'), ('sub', 'Hybrid sub boom')]

SC = [0, 2, 3, 5, 7, 8, 10]                     # natural minor; the V chord and a major ending raise notes as needed
QUAL = {'m': (0, 3, 7), 'M': (0, 4, 7), 'sus4': (0, 5, 7), 'sus2': (0, 2, 7)}

# one bar per chord: (semitones above the tonic, quality)
PROGS = {
    'tension': [[(0, 'm'), (0, 'm'), (8, 'M'), (8, 'M'), (5, 'm'), (5, 'm'), (7, 'M'), (7, 'M')],
                [(0, 'm'), (0, 'm'), (1, 'M'), (1, 'M'), (0, 'm'), (0, 'm'), (7, 'M'), (7, 'M')]],
    'sorrow': [[(0, 'm'), (8, 'M'), (3, 'M'), (10, 'M'), (5, 'm'), (0, 'm'), (5, 'm'), (7, 'M')],
               [(0, 'm'), (10, 'M'), (8, 'M'), (7, 'M'), (5, 'm'), (3, 'M'), (5, 'm'), (7, 'M')]],
    'resolve': [[(8, 'M'), (10, 'M'), (0, 'm'), (0, 'm'), (8, 'M'), (10, 'M'), (3, 'M'), (7, 'M')],
                [(0, 'm'), (8, 'M'), (3, 'M'), (10, 'M'), (5, 'm'), (8, 'M'), (10, 'M'), (7, 'M')]],
    'glory': [[(3, 'M'), (10, 'M'), (0, 'm'), (8, 'M'), (3, 'M'), (10, 'M'), (8, 'M'), (10, 'M')],
              [(8, 'M'), (10, 'M'), (3, 'M'), (0, 'm'), (8, 'M'), (10, 'M'), (3, 'M'), (3, 'M')]],
    'reflection': [[(0, 'm'), (8, 'M'), (5, 'm'), (0, 'm'), (8, 'M'), (3, 'M'), (5, 'm'), (7, 'sus4')]],
    'battle': [[(0, 'm'), (0, 'm'), (1, 'M'), (0, 'm'), (8, 'M'), (10, 'M'), (1, 'M'), (7, 'M')],
               [(0, 'm'), (8, 'M'), (1, 'M'), (7, 'M'), (0, 'm'), (8, 'M'), (10, 'M'), (7, 'M')]],
}
# (level dB at start, at end, tempo factor at start, at end)  - dB is scaled by the Dynamics setting
SHAPE = {'tension': (-17, -12, 0.93, 0.92), 'sorrow': (-12, -9.5, 0.96, 0.95), 'resolve': (-9, -3, 0.98, 1.05),
         'glory': (-1, 0, 1.07, 1.07), 'battle': (-4, -1.5, 1.12, 1.15), 'reflection': (-14, -15.5, 0.87, 0.82), 'resolution': (-8, -9, 0.84, 0.64)}

RH = [[(0, 2), (2, 1), (3, 1)], [(0, 1.5), (1.5, 0.5), (2, 2)], [(0, 3), (3, 1)], [(0, 1), (1, 1), (2, 2)],
      [(0, 2), (2, 2)], [(0, 1), (1, 0.5), (1.5, 0.5), (2, 2)], [(0, 2.5), (2.5, 0.5), (3, 1)]]


# ----------------------------------------------------------------------------- pitch helpers
def cpcs(ch, root):
    return {(root + ch[0] + i) % 12 for i in QUAL[ch[1]]}


def near(pc, target):
    return target + ((pc - target + 6) % 12) - 6


def chord_tone(ch, root, target):
    cands = [near(pc, target) for pc in cpcs(ch, root)]
    return min(cands, key=lambda m: (abs(m - target), m))


def step_midi(step, root, octave, ch):
    """Diatonic step (0 = tonic) -> MIDI, bent to fit the chord (raised leading tone on V, major third at the end)."""
    o, i = divmod(int(step), 7)
    m = 12 * (octave + 1) + root + 12 * o + SC[i]
    cp = cpcs(ch, root)
    if m % 12 not in cp and (m + 1) % 12 in cp and ((m + 1 - root) % 12) not in SC:
        m += 1
    return m


def scale_above(m, root, ch):
    cp = cpcs(ch, root)
    for k in range(1, 4):
        x = m + k
        if (x - root) % 12 in SC or x % 12 in cp:
            if not ((x - root) % 12 == 10 and (root + 11) % 12 in cp):
                return x
    return m + 2


def tones_between(ch, root, lo, hi):
    return [m for m in range(lo, hi + 1) if m % 12 in cpcs(ch, root)]


def spread(ch, root, lo, hi, n):
    """n chord tones spread evenly between lo and hi, the chord's root at the bottom."""
    allt = tones_between(ch, root, lo, hi)
    while len(allt) < n and hi < 127:                       # narrow range: reach a little higher
        hi += 4
        allt = tones_between(ch, root, lo, hi)
    r = (root + ch[0]) % 12
    ts = list(allt)
    while ts and ts[0] % 12 != r:
        ts = ts[1:]
    if len(ts) < n:
        ts = allt
    if len(ts) <= n:
        return ts
    idx = sorted({round(i * (len(ts) - 1) / (n - 1)) for i in range(n)})
    return [ts[i] for i in idx]


def gliss(S, track, beat, beats, ch, lo, hi, up=True, v0=0.35, v1=0.7):
    """Harp glissando: every scale note between lo and hi, spread evenly over `beats` starting at `beat`."""
    r = S.root
    cp = cpcs(ch, r)
    ms = [m for m in range(lo, hi + 1) if (m - r) % 12 in SC or m % 12 in cp]
    ms = [m for m in ms if not ((m - r) % 12 == 10 and (r + 11) % 12 in cp)]
    if not up:
        ms = ms[::-1]
    k_n = len(ms)
    for k, m in enumerate(ms):
        S.add(track, beat + beats * k / k_n, 1.2 if k == k_n - 1 else 0.5, m, _ramp(v0, v1, k / max(1, k_n - 1)))


def rip(S, track, beat, target, ch, vel=0.9, span=0.4):
    """Brass rip: a fast run up the scale into `target`, landing on `beat`."""
    ms = []
    m = target - 10
    while m < target:
        ms.append(m)
        m = scale_above(m, S.root, ch)
    for k, m in enumerate(ms):
        S.add(track, beat - span + span * k / len(ms), span / len(ms) * 1.3, m, _ramp(0.35, vel, k / max(1, len(ms) - 1)))


# ----------------------------------------------------------------------------- the theme
def make_theme(rng):
    """8 bars: rhythm + contour (diatonic steps above the tonic). Bars 5-6 echo bars 1-2; bar 7 holds the high point."""
    r = [rng.choice(RH) for _ in range(3)]
    rhythm = [r[0], r[1], r[2], rng.choice([[(0, 4)], [(0, 3), (3, 1)]]), r[0], r[1], rng.choice(RH), [(0, 4)]]
    j = rng.choice([0, 1])
    peak = rng.choice([8, 9])
    targets = [4, 5 + j, 7, 4 - j, 4, 6, peak, 1]
    notes = []
    for bar, rh in enumerate(rhythm):
        t0, t1 = targets[bar], targets[bar + 1] if bar + 1 < len(targets) else targets[bar]
        for (b, d) in rh:
            strong = b in (0, 2) and d >= 1 or b == 0
            step = t0 if b == 0 else round(t0 + (t1 - t0) * b / 4.0)
            app = strong and d >= 2 and bar in (1, 2, 5, 6) and rng.random() < 0.45
            notes.append((bar, b, d, step, strong, app))
    return notes


def realize(theme, prog, root, octave, bar0=0, bars=None, legato=0.0):
    """Theme notes over a progression -> [(beat, dur, midi, accent)]; strong notes land on chord tones."""
    out = []
    for (bar, b, d, step, strong, app) in theme:
        if bars is not None and bar >= bars:
            continue
        ch = prog[(bar0 + bar) % len(prog)]
        beat = (bar0 + bar) * 4 + b
        m = step_midi(step, root, octave, ch)
        if strong:
            m = chord_tone(ch, root, m)
        if app:                                          # the "sigh": a step above, leaning into the chord tone
            a = d * 0.4
            out.append((beat, a + legato, scale_above(m, root, ch), 1.0))
            out.append((beat + a, d - a + legato, m, 0.8))
        else:
            out.append((beat, d + legato, m, 1.0 if strong else 0.85))
    return out


# ----------------------------------------------------------------------------- the score
class Score:
    def __init__(self, root, rng):
        self.root, self.rng, self.evs = root, rng, []

    def add(self, track, beat, dur, midi, vel):
        if midi is None or dur <= 0:
            return
        self.evs.append(Ev(track, round(beat, 4), dur, int(midi), max(0.03, min(1.0, vel))))

    def hit(self, track, beat, vel):
        self.evs.append(Ev(track, round(beat, 4), 0.5, 36, max(0.03, min(1.0, vel))))


def _ramp(a, b, x):
    return a + (b - a) * max(0.0, min(1.0, x))


def act_tension(S, b0, n, prog, theme, cfg):
    r = S.root
    for bar in range(n):
        ch = prog[bar % len(prog)]
        x = bar / max(1, n - 1)
        beat = b0 + bar * 4
        if bar % 2 == 0:                                       # basses: a long, dark pedal
            m = 24 + (r + ch[0]) % 12
            S.add('cb', beat, 8.1, m + 12 if m < 28 else m, _ramp(0.3, 0.5, x))
        if bar >= 2:                                           # celli: muted, creeping ostinato
            creep = [0, 0, 1, 0, 3, 1, 0, -1] if ch[1] == 'm' else [0, 0, 1, 0, 4, 1, 0, -1]
            base = 36 + (r + ch[0]) % 12
            for k, c in enumerate(creep):
                S.add('vc', beat + k * 0.5, 0.48, base + c, _ramp(0.22, 0.42, x) * (1.15 if k % 4 == 0 else 1.0))
        if bar >= n // 2:                                      # violas join an octave up, quieter
            base = 48 + (r + ch[0]) % 12
            for k, c in enumerate([0, 0, 1, 0, 3, 1, 0, -1]):
                S.add('va', beat + k * 0.5, 0.48, base + c, _ramp(0.15, 0.3, x))
        if bar % 4 in (0, 3) or bar == n - 1:                  # soft timpani rolls swelling into the phrase
            m = near((r + (7 if ch[0] == 7 else 0)) % 12, 45)
            rl = 2 if bar % 4 == 0 else 4
            for k in range(int(rl / 0.125)):
                S.add('timp', beat + (4 - rl if bar % 4 == 3 else 0) + k * 0.125, 0.2, m,
                      0.1 + 0.25 * (k / (rl / 0.125)) * (0.6 + 0.4 * x))
        if bar % 2 == 1 or bar == 0:                           # icy notes at the very bottom of the piano
            pick = S.rng.choice(tones_between(ch, r, 21, 35) or [21 + r])
            b_ = S.rng.choice([0, 1, 2]) if bar else 0
            S.add('piano', beat + b_, 6, pick, 0.42 * cfg['piano_v'])
            if S.rng.random() < 0.4:
                S.add('piano', beat + b_ + 2.5, 4, pick + 12, 0.3 * cfg['piano_v'])
        if bar >= n // 2:                                      # measured tremolo, barely there
            for m in spread(ch, r, 55, 67, 2):
                S.add('trem', beat, 4.05, m, _ramp(0.12, 0.3, (bar - n // 2) / max(1, n // 2)))
        if bar >= n - 4:
            S.add('vn_hi', beat, 4.05, near((r + ch[0] + 7) % 12, 86), 0.18)
    # foreshadowing: the trombones hint at the theme, twice as slow, pianissimo
    start = n // 2
    span = n - start
    if span >= 4:
        aug = [prog[(start + 2 * k) % len(prog)] for k in range(8)]
        for (b, d, m, acc) in realize(theme, aug, r, 3, 0, max(1, span // 2), 0.0):
            S.add('tbn', b0 + start * 4 + b * 2, d * 2 + 0.1, m, 0.24 + 0.08 * acc)


def act_sorrow(S, b0, n, prog, theme, cfg):
    r = S.root
    for rep in range(max(1, n // 8)):
        bars = min(8, n - rep * 8)
        for (b, d, m, acc) in realize(theme, prog, r, 4, 0, bars, 0.05):
            v = (0.5 + 0.08 * (b / 4 % 8) / 7 + (0.06 if rep else 0)) * acc * cfg['piano_v']
            S.add('piano', b0 + rep * 32 + b, d, m, v)
            if rep and d >= 1.5 and acc >= 1.0:              # second time: octaves in the right hand
                S.add('piano', b0 + rep * 32 + b, d, m - 12, v * 0.7)
    for bar in range(n):
        ch = prog[bar % len(prog)]
        beat = b0 + bar * 4
        x = bar / max(1, n - 1)
        rt = 36 + (r + ch[0]) % 12
        lh = [rt, rt + 7, chord_tone(ch, r, rt + 16), rt + 12]       # left hand: open broken chord under the pedal
        for k, m in enumerate(lh):
            S.add('piano', beat + k, 4 - k + 0.2, m, (0.34 if k == 0 else 0.26) * cfg['piano_v'])
        for m in spread(ch, r, 48, 72, 4):                               # soft-vibrato string pad
            S.add('pad', beat, 4.08, m, _ramp(0.26, 0.38, x))
        S.add('cb', beat, 4.08, 28 + (r + ch[0] - 4) % 12, 0.32)
        if bar % 2 == 0 and bar > 0:                                     # gentle horn swells
            for m in spread(ch, r, 53, 65, 2)[-2:]:
                S.add('horns', beat, 7.5, m, _ramp(0.28, 0.42, x))
        if cfg['woodwinds'] and bar >= n - 4 and bar % 2 == 1:           # a clarinet sighs back at the piano
            S.add('clar', beat + 2, 2, chord_tone(ch, r, 62), 0.3)
        if bar == n - 1:                                                 # harp sweeps up into what comes next
            gliss(S, 'harp', beat + 3, 1, ch, 43, 84, True, 0.3, 0.6)


def _ostinato(S, track, beat, ch, r, lo, vel):
    rt = lo + (r + ch[0] - lo) % 12
    fifth = rt + 7
    for k, m in enumerate([rt, rt, fifth, rt, rt + 12, rt, fifth, rt, rt, rt, fifth, rt, rt + 12, fifth, rt + 12, fifth]):
        S.add(track, beat + k * 0.25, 0.2, m, vel * (1.18 if k % 4 == 0 else 0.92))


def _run(S, track, beat, beats, ch, r, lo, v0, v1):
    """Rising scalar run (16ths) into the next downbeat."""
    m = lo + (r + ch[0] - lo) % 12
    k_n = int(beats * 4)
    for k in range(k_n):
        S.add(track, beat + k * 0.25, 0.22, m, _ramp(v0, v1, k / max(1, k_n - 1)))
        m = scale_above(m, r, ch)


def act_resolve(S, b0, n, prog, theme, cfg):
    r = S.root
    for rep in range(max(1, n // 8)):
        bars = min(8, n - rep * 8)
        for (b, d, m, acc) in realize(theme, prog, r, 5, 0, bars, 0.12):
            x = (rep * 32 + b) / (n * 4)
            S.add('vn1', b0 + rep * 32 + b, d, m, _ramp(0.55, 0.85, x) * acc)
            S.add('va', b0 + rep * 32 + b, d, m - 12, _ramp(0.5, 0.75, x) * acc)
    if n >= 16:                                              # second time round the horns answer in canon, 2 bars behind
        sh = [prog[(k + 2) % len(prog)] for k in range(8)]
        for (b, d, m, acc) in realize(theme, sh, r, 4, 0, 6, 0.12):
            beat = b0 + 32 + 8 + b
            if beat < b0 + n * 4 - 1:
                S.add('horns', beat, d, m, 0.72 * acc)
    prev = None
    for bar in range(n):
        ch = prog[bar % len(prog)]
        beat = b0 + bar * 4
        x = bar / max(1, n - 1)
        _ostinato(S, 'spicc_lo', beat, ch, r, 36, _ramp(0.45, 0.8, x))
        if bar % 4 == 3:
            _run(S, 'spicc_hi', beat + 1, 3, ch, r, 55, 0.45, 0.9)
        for m in spread(ch, r, 52, 76, 4):
            S.add('pad', beat, 4.08, m, _ramp(0.4, 0.6, x))
        S.add('cb', beat, 4.08, 28 + (r + ch[0] - 4) % 12, _ramp(0.45, 0.75, x))
        hv = [chord_tone(ch, r, x) for x in prev] if prev else spread(ch, r, 55, 67, 2)
        prev = hv
        if bar < n // 2 or n < 16:
            for h in (0, 2):                                 # horns: noble, sustained
                for m in hv:
                    S.add('horns', beat + h, 2.05, m, _ramp(0.5, 0.78, x))
        elif cfg['choir']:
            for m in spread(ch, r, 55, 72, 3):               # the choir enters, softly, on "oo"
                S.add('choir_oo', beat, 4.08, m, _ramp(0.3, 0.55, x))
        if bar >= n // 2:
            y = (bar - n // 2) / max(1, n // 2 - 1)
            S.add('tpt', beat, 4.05, chord_tone(ch, r, 72), _ramp(0.5, 0.78, y))
            low = spread(ch, r, 38, 55, 3)
            if bar % 2 == 0:                                 # trombones & tuba: deep, weighty chords ...
                for m in low:
                    S.add('tbn', beat, 4.05, m, _ramp(0.55, 0.8, y))
            else:                                            # ... and short marcato statements
                for (o, d, v) in ((0, 0.5, 0.95), (0.75, 0.25, 0.8), (2, 1.4, 0.92)):
                    for m in low:
                        S.add('tbn_marc', beat + o, d, m, v)
            S.add('tuba', beat, 4.05, 24 + (r + ch[0] - 0) % 12 + (12 if (r + ch[0]) % 12 < 4 else 0), _ramp(0.55, 0.8, y))
            S.add('cbtbn', beat, 4.05, low_root(ch, r, 28), _ramp(0.45, 0.7, y))
        tm = near((r + ch[0]) % 12, 45)
        if bar < n - 1:
            S.add('timp', beat, 1.0, tm, _ramp(0.35, 0.6, x))
        else:                                                # the roll that throws the door open
            for k in range(32):
                S.add('timp', beat + k * 0.125, 0.2, tm, 0.25 + 0.6 * k / 31)


def low_root(ch, r, lo):
    return lo + (r + ch[0] - lo) % 12


def act_glory(S, b0, n, prog, theme, cfg):
    r = S.root
    mel = []
    for rep in range(max(1, n // 8)):
        bars = min(8, n - rep * 8)
        for (b, d, m, acc) in realize(theme, prog, r, 6, 0, bars, 0.1):
            beat = b0 + rep * 32 + b
            mel.append((beat, d, m))
            S.add('vn1', beat, d, m, 0.92 * acc)
            S.add('va', beat, d, m - 12, 0.85 * acc)
            S.add('vc', beat, d, m - 24, 0.85 * acc)
            S.add('horns', beat, d, m - 24, 0.88 * acc)
    for bar in range(n):
        ch = prog[bar % len(prog)]
        beat = b0 + bar * 4
        rt = (r + ch[0]) % 12
        _ostinato(S, 'spicc_lo', beat, ch, r, 36, 0.85)
        if bar % 4 == 3:
            _run(S, 'spicc_hi', beat + 2, 2, ch, r, 62, 0.6, 1.0)
        for m in spread(ch, r, 60, 84, 5):
            S.add('pad', beat, 4.08, m, 0.72)
        for m in spread(ch, r, 84, 96, 2):                   # high string harmonics, like a distant choir
            S.add('vn_hi', beat, 4.08, m, 0.32)
        five, top = chord_tone(ch, r, 72), chord_tone(ch, r, 79)
        for (o, d, m) in ((0, 1.5, five), (1.5, 0.5, five), (2, 0.33, five), (2.33, 0.33, five), (2.67, 0.33, five), (3, 1, top)):
            S.add('tpt', beat + o, d, m, 0.9 if o in (0, 3) else 0.78)   # blazing fanfare
        low = spread(ch, r, 38, 55, 3)
        fall = bar % 8 == 7 and bar < n - 1
        for m in low:
            S.add('tbn_marc', beat, 0.6, m, 0.98)            # sforzando ...
            S.add('tbn', beat + 0.6, 2.7 if fall else 3.45, m, 0.72)   # ... into a weighty sustain
        if fall:                                             # trombone fall at the end of the phrase
            top = max(low)
            for k in range(6):
                S.add('tbn', beat + 3.3 + k * 0.1, 0.14, top - 1 - k, 0.75 - 0.08 * k)
        if bar % 4 == 0 and bar > 0:                         # horn rip into the phrase
            cur = [m for (b, d, m) in mel if b <= beat < b + d]
            rip(S, 'horns', beat, (cur[0] - 24) if cur else chord_tone(ch, r, 65), ch)
        S.add('cbsn', beat, 4.05, low_root(ch, r, 22), 0.7)
        S.add('cbtbn', beat, 4.05, low_root(ch, r, 28), 0.85)
        if cfg['choir']:
            for m in spread(ch, r, 55, 79, 4):               # full choir, "aah"
                S.add('choir', beat, 4.08, m, 0.75)
        if cfg['hybrid'] and bar % 2 == 0:
            S.add('sub', beat, 2.0, low_root(ch, r, 24), 0.9)
        if cfg['glory_style'] == 'battle':
            percussion(S, beat, bar, n, 0.95)
        S.add('tuba', beat, 4.05, 24 + rt + (12 if rt < 4 else 0), 0.85)
        S.add('cb', beat, 4.05, 28 + (rt - 4) % 12, 0.85)
        # cascading piano arpeggios cut through the tutti
        arp = tones_between(ch, r, 52, 88)
        seq = arp[::-1] if bar % 2 == 0 else arp
        for k in range(16):
            m = seq[k % len(seq)]
            S.add('piano', beat + k * 0.25, 0.4, m, (0.82 if k % 4 == 0 else 0.68) * cfg['piano_v'])
        if cfg['woodwinds']:                                 # woodwind counter-melody, contrary to the theme
            for h in (0, 2):
                cur = [m for (b, d, m) in mel if b <= beat + h < b + d]
                mm = cur[0] if cur else 84
                tgt = 164 - mm
                c = chord_tone(ch, r, min(93, max(76, tgt)))
                S.add('flute', beat + h, 2.02, c, 0.62)
                S.add('oboe', beat + h, 2.02, c - 12, 0.55)
            for k in range(8):
                S.add('clar', beat + k * 0.5, 0.45, arp[(k * 2) % len(arp)] if arp else 60, 0.42)
        if bar == 0:                                         # harp glissando sweeping up out of the silence
            gliss(S, 'harp', beat, 1, ch, 48, 91, True, 0.5, 0.85)
        tm, t5 = near(rt, 45), near((rt + 7) % 12, 45)
        for (o, m, v) in ((0, tm, 0.98), (1.5, t5, 0.7), (2, tm, 0.88), (3.5, t5, 0.72)):
            S.add('timp', beat + o, 0.8, m, v)
        if bar % 4 == 3:
            for k in range(8):
                S.add('timp', beat + 3 + k * 0.125, 0.2, tm, 0.5 + 0.45 * k / 7)
        S.hit('bdrum', beat, 0.95)
        if bar % 2 == 1:
            S.hit('bdrum', beat + 2, 0.75)
        if bar % 8 == 0 or bar == n - 1:
            S.hit('cym', beat, 0.9)


TAIKO = ['X..x..x.X.x.x...', 'X.x.X..xX.x.Xxxx']


def percussion(S, beat, bar, n, v):
    """Trailer percussion ensemble: taiko patterns, snare rolls into each phrase, anvil on the backbeat."""
    pat = TAIKO[1] if bar % 4 == 3 else TAIKO[0]
    for k, c in enumerate(pat):
        if c != '.':
            S.hit('taiko', beat + k * 0.25, v * (1.0 if c == 'X' else 0.72))
    if bar % 2 == 1:
        S.hit('anvil', beat + 1, v * 0.7)
        S.hit('anvil', beat + 3, v * 0.75)
    if bar % 4 == 3 or bar == n - 1:
        for k in range(16):                                  # snare roll, crescendo
            S.hit('snare', beat + 2 + k * 0.125, v * (0.35 + 0.6 * k / 15))
    else:
        for o in (1, 3):
            S.hit('snare', beat + o, v * 0.55)


def act_battle(S, b0, n, prog, theme, cfg):
    r = S.root
    for (b, d, m, acc) in realize(theme, prog, r, 4, 0, min(n, 4), 0.05):      # the theme, now a battle cry
        for rep_ in range(max(1, n // 4)):
            if b0 + rep_ * 16 + b < b0 + n * 4:
                S.add('horns', b0 + rep_ * 16 + b, d, m, 0.85 * acc)
    for bar in range(n):
        ch = prog[bar % len(prog)]
        beat = b0 + bar * 4
        x = bar / max(1, n - 1)
        _ostinato(S, 'spicc_lo', beat, ch, r, 36, _ramp(0.8, 0.95, x))
        hi = spread(ch, r, 62, 79, 3)
        for k in range(16):
            S.add('spicc_hi', beat + k * 0.25, 0.2, hi[k % len(hi)] if k % 4 else hi[0], _ramp(0.6, 0.85, x))
        low = spread(ch, r, 38, 55, 3)
        for (o, v) in ((0, 0.98), (0.75, 0.8), (1.5, 0.9), (2.5, 0.85), (3, 0.92), (3.5, 0.85)):   # staccato brass
            for m in low:
                S.add('tbn_marc', beat + o, 0.25, m, v)
        for o in (1.5, 3.5):
            S.add('tpt', beat + o, 0.3, chord_tone(ch, r, 74), 0.85)
        S.add('tuba', beat, 1.5, low_root(ch, r, 28), 0.85)
        S.add('tuba', beat + 2, 1.5, low_root(ch, r, 28), 0.8)
        S.add('cbtbn', beat, 1.0, low_root(ch, r, 28), 0.85)
        S.add('cb', beat, 4.05, 28 + (r + ch[0] - 4) % 12, 0.8)
        tm = near((r + ch[0]) % 12, 45)
        for k in range(8):
            S.add('timp', beat + k * 0.5, 0.4, tm if k % 2 == 0 else near((r + ch[0] + 7) % 12, 45), 0.85 if k % 4 == 0 else 0.6)
        if cfg['choir']:
            for m in spread(ch, r, 50, 67, 3):
                S.add('choir_oo', beat, 4.08, m, 0.7)
        if cfg['hybrid']:
            S.add('sub', beat, 1.5, low_root(ch, r, 24), 0.9)
        percussion(S, beat, bar, n, 0.9)
        S.hit('bdrum', beat, 0.9)
        if bar % 4 == 0:
            S.hit('cym', beat, 0.8)


def act_reflection(S, b0, n, prog, theme, cfg):
    r = S.root
    gliss(S, 'harp', b0, 1.5, prog[0], 60, 91, False, 0.35, 0.18)        # a soft harp sweep down into the stillness
    frag = realize(theme, prog, r, 5, 0, min(4, n), 0.1)
    for (b, d, m, acc) in frag:
        S.add('piano', b0 + b, d, m, 0.4 * acc * cfg['piano_v'])
    if n > 4:
        for (b, d, m, acc) in realize(theme, prog, r, 5, 4, 2, 0.1):
            S.add('piano', b0 + b, d, m + 12, 0.32 * acc * cfg['piano_v'])
    for bar in range(n):
        ch = prog[bar % len(prog)]
        beat = b0 + bar * 4
        S.add('piano', beat, 4.5, 36 + (r + ch[0]) % 12, 0.26 * cfg['piano_v'])
        for m in spread(ch, r, 76, 91, 3):                   # soft, high, shimmering strings
            S.add('vn_hi', beat, 4.08, m, 0.22)
        if bar % 2 == 0:                                     # distant soft brass chords
            for m in spread(ch, r, 50, 64, 3):
                S.add('horns', beat + 0.5, 7, m, 0.24)


def act_resolution(S, b0, n, prog, theme, cfg):
    r = S.root
    final = (0, 'M' if cfg['ending'] == 'major' else 'm')
    path = [(5, 'm'), (8, 'M'), (10, 'sus4'), (10, 'M')]
    walk = path[-min(len(path), max(1, n - 4)):] if n > 4 else [(10, 'M')]
    hold = n - len(walk)
    prev_top = None
    for i, ch in enumerate(walk):
        beat = b0 + i * 4
        for m in spread(ch, r, 43, 79, 6):
            S.add('pad', beat, 4.1, m, 0.55)
        top = chord_tone(ch, r, prev_top or 79)
        prev_top = top
        S.add('vn1', beat, 4.1, top, 0.6)
        S.add('cb', beat, 4.1, 28 + (r + ch[0] - 4) % 12, 0.55)
        for m in spread(ch, r, 40, 55, 3):
            S.add('tbn', beat, 4.1, m, 0.5)
        S.add('tuba', beat, 4.1, 24 + (r + ch[0]) % 12 + (12 if (r + ch[0]) % 12 < 4 else 0), 0.5)
        for m in spread(ch, r, 53, 67, 2):
            S.add('horns', beat, 4.1, m, 0.48)
    beat = b0 + len(walk) * 4
    L = hold * 4 + 2
    for m in spread(final, r, 43, 84, 7):                    # the long, luminous last chord
        S.add('pad', beat, L, m, 0.6)
    S.add('vn1', beat, L, chord_tone(final, r, prev_top or 76), 0.58)
    S.add('vn_hi', beat, L, chord_tone(final, r, 88), 0.25)
    S.add('va', beat, L, chord_tone(final, r, 64), 0.5)
    S.add('vc', beat, L, 36 + r, 0.55)
    S.add('cb', beat, L, 28 + (r - 4) % 12, 0.55)
    for m in spread(final, r, 40, 55, 3):
        S.add('tbn', beat, L, m, 0.5)
    S.add('tuba', beat, L, 24 + r + (12 if r < 4 else 0), 0.48)
    for m in spread(final, r, 53, 67, 2):
        S.add('horns', beat, L, m, 0.45)
    S.add('piano', beat + 1, 8, chord_tone(final, r, 84), 0.3 * cfg['piano_v'])
    S.add('cbsn', beat, L, 22 + (r - 22) % 12, 0.4)
    if cfg['choir']:
        for m in spread(final, r, 55, 76, 4):                # the choir's last, held "oo"
            S.add('choir_oo', beat, L, m, 0.4)
    tm = near(r, 45)
    for k in range(int(min(L, 12) / 0.125)):                 # a whisper of timpani under it, dying away
        S.add('timp', beat + k * 0.125, 0.2, tm, 0.2 * (1 - k / (min(L, 12) / 0.125)))


WRITERS = {'tension': act_tension, 'sorrow': act_sorrow, 'resolve': act_resolve, 'battle': act_battle, 'glory': act_glory,
           'reflection': act_reflection, 'resolution': act_resolution}


def settings(opts):
    cfg = dict(DEFAULTS)
    user = getattr(opts, 'journey', None) or {}
    cfg.update(PRESETS.get(user.get('preset'), {}))
    cfg.update({k: v for k, v in user.items() if k in DEFAULTS})
    acts = [a for a in ACT_IDS if a in (cfg.get('acts') or HERO)] or HERO
    cfg['acts'] = acts
    for k in ('piano', 'rubato', 'dynamics'):
        try:
            cfg[k] = max(0.0, min(1.0, float(cfg[k])))
        except (TypeError, ValueError):
            cfg[k] = DEFAULTS[k]
    cfg['ending'] = 'minor' if cfg.get('ending') == 'minor' else 'major'
    cfg['woodwinds'] = bool(cfg.get('woodwinds', True))
    for k in ('lift', 'choir', 'hybrid'):
        cfg[k] = bool(cfg.get(k))
    cfg['glory_style'] = 'battle' if cfg.get('glory_style') == 'battle' else 'concert'
    ln = cfg.get('lengths') if isinstance(cfg.get('lengths'), dict) else {}
    cfg['lengths'] = {a: max(0.25, min(3.0, float(v))) for a, v in ln.items() if a in ACT_IDS and isinstance(v, (int, float))}
    cfg['piano_v'] = 0.55 + 0.6 * cfg['piano']
    return cfg


def compose_journey(st, opts, key, bpm, rng):
    """-> song dict (same shape as compose.compose) for the Cinematic Journey."""
    cfg = settings(opts)
    st['rubato'] = 0.15 + 0.85 * cfg['rubato']
    root = key.root
    key = Key(root, 'minor')
    S = Score(root, rng)
    theme = make_theme(random.Random(opts.seed * 131 + 7))
    scale = max(0.5, min(2.0, float(getattr(opts, 'length', 1.0) or 1.0)))
    dyn = 0.45 + 0.85 * cfg['dynamics']
    sections, fx, tempo, expr_pts = [], [], [], []
    bar = 0
    picks = {a: random.Random(f'{opts.seed}-{a}').randrange(len(PROGS.get(a, [[0]]))) for a in ACT_IDS}
    for i, act in enumerate(cfg['acts']):
        base = dict((a, b) for a, _, b in ACTS)[act]
        n = int(max(4, round(base * scale * cfg['lengths'].get(act, 1.0) / 4) * 4))
        if act in ('resolve', 'glory', 'sorrow'):
            n = max(8, int(round(n / 8) * 8))
        prog = PROGS[act][picks[act]] if act in PROGS else None
        mark = len(S.evs)
        WRITERS[act](S, bar * 4, n, prog, theme, cfg)
        lifted = 0
        if act == 'glory' and cfg['lift'] and n >= 8:          # the last half of the climax lifts a whole step
            half = (bar + n // 2) * 4
            for e in S.evs[mark:]:
                if e.beat >= half and e.track not in UNPITCHED:
                    e.midi += 2
            lifted = 2
        l0, l1, f0, f1 = SHAPE[act]
        lv0, lv1 = 10 ** (l0 * dyn / 20), 10 ** (l1 * dyn / 20)
        label = dict((a, l) for a, l, _ in ACTS)[act]
        o = {'level': lv0, 'level_to': lv1}
        if act == 'glory':
            o.update(drop=True, crash=True)
            fx.append(('impact', bar * 4, 0))
            if lifted:
                o['key_change_at'] = bar + n // 2
        if act == 'tension':
            o['filter_in'] = False
        sections.append(dict(name=label, bar=bar, bars=n, layers=sorted({'bass', 'pad', 'lead', 'chords', 'arp', 'kick', 'top'}),
                             opts=o, index=i, src=i, copy=False, act=act, key_change=lifted or None))
        b0 = bar * 4
        tempo.append((b0, bpm * f0))
        if act == 'glory':                                   # broaden into the last bars (allargando)
            tempo.append((b0 + (n - 2) * 4, bpm * f1))
            tempo.append((b0 + n * 4 - 0.01, bpm * 0.9))
        elif act in ('resolve', 'battle'):                   # drive forward, then one held breath before the climax
            tempo.append((b0 + (n - 1) * 4, bpm * f1))
            tempo.append((b0 + n * 4 - 0.01, bpm * 0.93))
        else:
            tempo.append((b0 + n * 4 - 0.01, bpm * f1))
        nxt = cfg['acts'][i + 1] if i + 1 < len(cfg['acts']) else None
        if nxt == 'glory':
            # suspended-cymbal roll swelling to the edge ... one beat of total silence ... then everything at once
            fx.append(('cymroll', b0 + (n - 2) * 4, 7))
            fx.append(('gap', b0 + n * 4 - 1, 1))
        elif nxt in ('resolve', 'battle', 'resolution'):
            fx.append(('cymroll', b0 + (n - 1) * 4, 4))      # a cymbal swell into the next act
            S.hit('cym', b0 + n * 4, 0.55 if nxt == 'resolution' else 0.75)
        expr_pts.append((b0, lv0))
        expr_pts.append((b0 + n * 4 - 0.5, lv1))
        bar += n
    last = sections[-1]
    if last.get('act') in ('resolution', 'reflection'):
        fade_bars = max(2, last['bars'] // 2)
        fx.append(('fade', (last['bar'] + last['bars'] - fade_bars) * 4, fade_bars * 4))
    total = bar + (2 if last.get('act') == 'resolution' else 0)
    tracks = {t['name'] for t in st['tracks']}
    evs = [e for e in S.evs if e.track in tracks and e.beat < total * 4]
    muted = set(opts.muted or [])
    if muted:
        layer = {t['name']: t['layer'] for t in st['tracks']}
        evs = [e for e in evs if layer.get(e.track) not in muted]
    # mod-wheel (CC1) dynamics for orchestra plugins: follows each act's level (crescendos and diminuendos)
    curve = []
    for (b, lv) in expr_pts:
        db = 20 * math.log10(max(lv, 1e-4))
        curve.append((b, int(max(12, min(127, 127 + db * 4.2)))))
    expr = {t: curve for t in tracks if not t.startswith(('bdrum', 'cym'))}
    roman = {(0, 'm'): 0, (8, 'M'): 5, (3, 'M'): 2, (10, 'M'): 6, (5, 'm'): 3, (7, 'M'): 4, (1, 'M'): 1}
    prog_main = [roman.get(c, 0) for c in PROGS['sorrow'][picks['sorrow']]][:4]
    prog_alt = [roman.get(c, 0) for c in PROGS['glory'][picks['glory']]][:4]
    sections[-1]['picardy'] = cfg['ending'] == 'major' and last.get('act') == 'resolution'
    return dict(style=opts.style, seed=opts.seed, bpm=bpm, key=key, events=evs, sections=sections, fx=fx, expr=expr,
                meter='4/4', harm_alts=0, total_bars=total, prog_main=prog_main, prog_alt=prog_alt, prog_verse=prog_main,
                chord_color='triad', modulate=False, st=st, opts=opts, user_opts=opts, vocal=[], energy=1.0,
                tempo_map=tempo, journey=dict(cfg, acts=cfg['acts'], theme_notes=len(theme)))
