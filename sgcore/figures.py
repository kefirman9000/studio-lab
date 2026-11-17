"""Idiomatic figures written from patterns: metal riffs, classical variations, trap hats, 303 lines."""
from .theory import Ev, parse_rhythm


RIFF_OFF = {'p': 0, 'X': 0, 'x': 0, 'b': 1, 'm': 3, 'q': 5, 'f': 6, 'g': 7, 'n': 10, 'o': 12}


def gen_riff(pat, key, chord, lo=40):
    """A guitar riff bar from a 16-step pattern: 'p' palm-muted chug on the chord's root, 'X'/'x' a ringing power chord
    (accent / normal), and the metal riff notes off the root - 'b' b2, 'm' minor 3rd, 'q' 4th, 'f' tritone, 'g' 5th,
    'n' b7, 'o' octave. '-' holds, '.' rests. Returns (step, length, root midi, kind)."""
    root = key.deg(chord, 2) % 12
    r0 = lo + ((root - lo) % 12)
    out = []
    for step, l, c in parse_rhythm(pat):
        if c not in RIFF_OFF:
            continue
        out.append((step, l, r0 + RIFF_OFF[c], c))
    return out


def vary_melody(mel, how, key):
    """Classical variation technique on a phrase. 'dim' (diminution / ornamented variation): every note of a beat or
    longer is broken into running eighths that walk by scale step toward the next note, keeping the theme's pitches on
    the beats - the way a Baroque or Classical composer decorates the second time round."""
    if how != 'dim' or not mel:
        return mel
    pcs = sorted({(key.root + x) % 12 for x in key.scale})

    def step(m, d):
        m += d
        while m % 12 not in pcs:
            m += d
        return m
    out = []
    for i, (bt, du, m, v) in enumerate(mel):
        if du < 0.99:
            out.append((bt, du, m, v))
            continue
        nxt = mel[i + 1][2] if i + 1 < len(mel) else m
        n = int(du / 0.5)
        cur = m
        for k in range(n):
            out.append((bt + k * 0.5, 0.45, cur, v * (1.0 if k == 0 else 0.82)))
            left = n - k - 1
            if nxt > cur and left > 0:
                cur = step(cur, 1)
            elif nxt < cur and left > 0:
                cur = step(cur, -1)
            elif left > 0:                                  # same note next: a turn around it
                cur = step(cur, 1 if k % 2 == 0 else -1)
    return out


def gen_trap_hats(evs, beat0, rnd, energy, pitch_rolls=False):
    """Trap hats: 8ths with 16th doubles, accented downbeats, and short 16th / 32nd / triplet rolls that swell into the next
    hit. pitch_rolls: the rolls are also pitched up step by step (phonk / bass-warp hats)."""
    pos = 0.0
    while pos < 4 - 1e-9:
        r = rnd.random()
        if r < 0.08 + 0.12 * energy and pos <= 3.5:
            n = rnd.choice([3, 4, 6])
            for k in range(n):
                evs.append(Ev('chat', beat0 + pos + k * (0.5 / n), 0.1, None, 0.45 + 0.4 * k / n,
                              None, f'pt:{2 * k}' if pitch_rolls else None))
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
