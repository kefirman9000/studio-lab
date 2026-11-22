"""(2.9.0) Deep dubstep basses: slow, simple wobbles that carry a whole track on their own.

Modelled on how deep, dark 140 dubstep basses behave (measured from reference drops):
  - the sub does most of the work (about 80 % of the energy under 150 Hz): a clean, steady sine, never wobbled;
  - the wobble lives in the low mids (150 Hz - 1.5 kHz, dark: the spectral centre sits around 900 Hz), high-passed off
    the sub so the two never fight;
  - the movement is SLOW: one sweep per bar, per half bar or per beat, sometimes a dotted 1/8 - and often a single
    sweep that opens across the whole note ('yooowww');
  - lots of space: phrases stop, the sub carries on alone.
Every LFO speed comes from the note's `mod` (beats per cycle), so the composer sets the rhythm of the wobble.
"""
import numpy as np
from scipy import signal

from . import va
from .dsp import SR, mtof
from .va_bass import _env, _lfo, _rate, _sub, dist

_RNG = np.random.default_rng(909)


def _mid_hp(y, f, lo=110.0):
    fc = max(lo, f * 1.8)
    return signal.sosfilt(signal.butter(4, fc / (SR / 2), 'high', output='sos'), y, axis=-1)


def _clean_sub(f, n, level, a=0.008):
    """A pure, steady sine sub on the fundamental (one octave down if the note is high), faded in and out so it never
    clicks, with no DC."""
    s = _sub(f, n, level)
    k = int(a * SR)
    if 0 < k < n:
        s[:k] *= np.sin(np.linspace(0, np.pi / 2, k)) ** 2
    return s


def _stack(fo, n, det=(-8, 8), sq=0.5):
    x = np.zeros((2, n))
    for k, c in enumerate(det):
        x[k % 2] += va.saw(np.full(n, fo * 2 ** (c / 1200)), n, _RNG.random())
    x += sq * va.pulse(np.full(n, fo), n, 0.1, 0.5)
    return x * 0.5


def _shape_for(m, mod):
    """Pick the LFO shape from the note itself, so the same phrase always says the same thing: mostly a smooth 'wow',
    sometimes a rising sweep ('yoww') or a slow triangle."""
    return ('sine', 'sine', 'rise', 'tri')[(int(m) * 7 + int(round((mod or 1) * 4))) % 4]


def _lfo_shape(n, hz, shape):
    if shape == 'rise':                                     # opens up across each cycle, then snaps shut
        t = np.arange(n) / SR
        v = ((hz * t) % 1.0) ** 1.4
        k = max(1, int(0.006 * SR))
        return np.convolve(v, np.ones(k) / k, mode='same')
    return _lfo(n, hz, shape)


def slowwob(m, dur, p, glide=None, mod=None):
    """Slow deep wobble: two saws and a square through a dark resonant low-pass that an LFO sweeps once per bar, half
    bar or beat (set by the composer) - a fat, round 'wowww' over a clean sine sub. Dark and simple."""
    f = float(mtof(m))
    env = _env(dur, a=0.006, d=0.1, s=1.0, r=0.06)
    n = len(env)
    fo = f if f > 50 else f * 2
    x = _stack(fo, n)
    lfo = _lfo_shape(n, _rate(mod, p, 2.0), p.get('shape') or _shape_for(m, mod))
    cut = 110 * (p.get('cut', 1500) / 110) ** lfo
    y = va.vcf(x, cut, res=p.get('res', 0.5), drive=1.3)
    y = dist(y, 1.6 + float(p.get('grit', 0.4)))
    y = _mid_hp(y, f) * 1.25
    return (y + _clean_sub(f, n, p.get('sub', 0.75))) * env * 0.55


def yoiwob(m, dur, p, glide=None, mod=None):
    """Talking 'yoi' wobble: a buzzy stack through vowel formants that morph oo -> ah -> oo with a slow LFO, so the bass
    seems to say 'yowww' - the vocal wub of deep dubstep."""
    f = float(mtof(m))
    env = _env(dur, a=0.006, d=0.1, s=1.0, r=0.06)
    n = len(env)
    fo = f if f > 50 else f * 2
    x = dist(_stack(fo, n, (-6, 6), 0.7), 2.2)
    lfo = _lfo_shape(n, _rate(mod, p, 2.0), p.get('shape') or _shape_for(m, mod))
    # formants: 'oo' (300, 800) -> 'ah' (750, 1250)
    f1 = 300 + 450 * lfo
    f2 = 800 + 450 * lfo
    y = np.zeros_like(x)
    for fc, q, g in ((f1, 5.0, 1.0), (f2, 6.0, 0.7)):
        y += g * _bp_moving(x, fc, q)
    y = y + 0.25 * va.vcf(x, 180 * (1400 / 180) ** lfo, res=0.3, drive=1.0)
    y = _mid_hp(y, f) * 1.8
    return (y + _clean_sub(f, n, p.get('sub', 0.75))) * env * 0.5


def sweepwob(m, dur, p, glide=None, mod=None):
    """One long sweep per note: the filter opens slowly across the whole note and closes at its end - the patient
    half-bar / bar 'yooooowww' that rises out of the sub."""
    f = float(mtof(m))
    env = _env(dur, a=0.006, d=0.1, s=1.0, r=0.08)
    n = len(env)
    gate = max(1, int(max(dur, 0.02) * SR))
    fo = f if f > 50 else f * 2
    x = _stack(fo, n, (-10, 10), 0.4)
    t = np.arange(n) / SR
    up = np.clip(t / (gate / SR), 0, 1) ** 1.8
    lfo = up * (0.85 + 0.15 * _lfo(n, _rate(mod, p, 1.0), 'sine'))   # a little life on the way up
    cut = 100 * (p.get('cut', 1800) / 100) ** lfo
    y = va.vcf(x, cut, res=p.get('res', 0.6), drive=1.3)
    y = dist(y, 1.8)
    y = _mid_hp(y, f) * 1.25
    return (y + _clean_sub(f, n, p.get('sub', 0.75))) * env * 0.55


def reesewob(m, dur, p, glide=None, mod=None):
    """Slow dark reese wobble: wide detuned saws whose phasing rolls slowly, through a low-pass that breathes with the
    LFO - a menacing, rolling growl rather than a 'wow'."""
    f = float(mtof(m))
    env = _env(dur, a=0.01, d=0.1, s=1.0, r=0.08)
    n = len(env)
    fo = f if f > 50 else f * 2
    x = np.zeros((2, n))
    for k, c in enumerate((-22, -9, 9, 22)):
        x[k % 2] += va.saw(np.full(n, fo * 2 ** (c / 1200)), n, _RNG.random())
    x *= 0.4
    lfo = _lfo(n, _rate(mod, p, 2.0), 'sine')
    cut = 180 * (p.get('cut', 1200) / 180) ** (0.25 + 0.75 * lfo)
    y = va.vcf(x, cut, res=0.35, drive=1.4)
    y = dist(y, 2.0)
    y = _mid_hp(y, f) * 1.25
    return (y + _clean_sub(f, n, p.get('sub', 0.75))) * env * 0.55


def deepsub(m, dur, p, glide=None, mod=None):
    """Deep dubstep sub: a pure sine on the fundamental with a soft start and end and just a touch of warmth - the
    steady floor that the wobbles sit on, or the only bass in the quiet parts."""
    f = float(mtof(m))
    fs = f if f < 80 else f / 2
    env = _env(dur, a=0.01, d=0.05, s=1.0, r=0.07)
    n = len(env)
    t = np.arange(n) / SR
    fr = np.full(n, fs) if glide is None else fs + (float(mtof(glide)) * (fs / f) - fs) * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.sin(ph)
    s = np.tanh(1.3 * s) / np.tanh(1.3)                     # symmetric: warm, no DC
    return np.vstack([s, s]) * env * 0.6


def sleepersub(m, dur, p, glide=None, mod=None):
    """'Sleeper' sub: a pure sine sub whose pitch slowly bends a semitone or so up and down (the LFO speed comes from
    the composer), dropping in from just above the note - the sub itself wobbles, felt more than heard."""
    f = float(mtof(m))
    fs = f if f < 80 else f / 2
    env = _env(dur, a=0.01, d=0.05, s=1.0, r=0.08)
    n = len(env)
    t = np.arange(n) / SR
    depth = float(p.get('bend', 1.0))                           # semitones
    lfo = np.sin(2 * np.pi * _rate(mod, p, 1.33) * t - np.pi / 2)  # starts low in its swing
    st_ = depth * 0.6 * lfo + 1.0 * np.exp(-t / 0.06)          # ...after a short drop from a semitone above
    if (int(m) * 5 + int(round((mod or 1) * 3))) % 3 == 0 and dur > 0.6:
        # (2.9.1) every third phrase the sub arcs instead: up about a tritone across the note's middle and back down
        u = np.clip(t / max(dur, 0.1), 0, 1)
        st_ = 6.0 * np.sin(np.pi * u) ** 1.5 + 0.8 * np.exp(-t / 0.06)
    fr = fs * 2 ** (st_ / 12)
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR)
    s = np.tanh(1.4 * s) / np.tanh(1.4)
    return np.vstack([s, s]) * env * 0.6


def brightwob(m, dur, p, glide=None, mod=None):
    """Grimy bright wobble: a hard-driven saw / square stack through a resonant low-pass and a moving comb, opening
    much higher than the deep wobbles - a dirtier, more forward 'wow-wow' at a dotted / triplet bounce."""
    f = float(mtof(m))
    env = _env(dur, a=0.004, d=0.08, s=1.0, r=0.05)
    n = len(env)
    fo = f if f > 50 else f * 2
    x = _stack(fo, n, (-12, 12), 0.8)
    lfo = _lfo_shape(n, _rate(mod, p, 2 / 3), p.get('shape') or 'sine')
    cut = 150 * (p.get('cut', 4500) / 150) ** lfo
    y = va.vcf(x, cut, res=p.get('res', 0.65), drive=1.6)
    y = dist(y, 4.0, 'hard')
    d = (1 / (300 + 900 * lfo)) * SR                         # a comb that moves with the filter: metallic grit
    idx = np.clip(np.arange(n) - d, 0, n - 1).astype(int)
    y = y + 0.4 * y[:, idx]
    y = _mid_hp(y, f) * 0.9
    return (y + _clean_sub(f, n, p.get('sub', 0.7))) * env * 0.33


def tearwob(m, dur, p, glide=None, mod=None):
    """Tearout / riddim riff bass: a clipped, nasal mid-bass that chops in tight 8ths, triplets or 16ths (the LFO is
    a hard gate on the filter and the formant), all in the 300 Hz - 4 kHz band, with a plain sub under it."""
    f = float(mtof(m))
    env = _env(dur, a=0.002, d=0.05, s=1.0, r=0.03)
    n = len(env)
    fo = f if f > 50 else f * 2
    x = _stack(fo, n, (-5, 5), 1.0)
    lfo = _lfo_shape(n, _rate(mod, p, 1 / 3), 'square')
    cut = 250 * (p.get('cut', 3500) / 250) ** lfo
    y = va.vcf(x, cut, res=0.7, drive=2.0)
    y = y + 0.8 * _bp_moving(y, 500 + 1300 * lfo, 4.0)
    y = dist(y, 6.0, 'hard')
    y = _mid_hp(y, f, 250.0) * 0.8
    return (y + _clean_sub(f, n, p.get('sub', 0.6))) * env * 0.36


# ---- (2.9.2) learned from a deep-dark-dubstep sample pack: subs that dive, MS-10 zaps, pitch-wobbling growls, and the
#      slow, dark swelling atmospheres and fluttering pads that sit behind them ----

def divesub(m, dur, p, glide=None, mod=None):
    """Diving sub: a warm sine sub whose pitch moves across the note - a long dive down an octave, a slow sag of a
    semitone or two, or a dive that comes back up (each phrase picks one from its note, so a riff stays consistent)."""
    f = float(mtof(m))
    fs = f if f < 80 else f / 2
    env = _env(dur, a=0.01, d=0.05, s=1.0, r=0.08)
    n = len(env)
    t = np.arange(n) / SR
    u = np.clip(t / max(dur, 0.1), 0, 1)
    kind = p.get('dive') or ('octave', 'sag', 'sag', 'return')[(int(m) * 3 + int(round((mod or 1) * 2))) % 4]
    if kind == 'octave':
        st_ = -12.0 * u ** 1.6
    elif kind == 'return':
        st_ = -7.0 * np.sin(np.pi * u) ** 1.2
    else:
        st_ = -1.5 * u
    fr = fs * 2 ** (st_ / 12)
    s_ = np.sin(2 * np.pi * np.cumsum(fr) / SR)
    s_ = np.tanh(1.5 * s_) / np.tanh(1.5)
    return np.vstack([s_, s_]) * env * 0.6


def ms10zap(m, dur, p, glide=None, mod=None):
    """Monophonic analog 'zap' bass (a small Korg-style mono synth): a saw that starts two octaves up and dives down
    to the note over a couple of seconds through a resonant low-pass that closes as it falls - bright and buzzy at the
    top, a plain sub at the bottom."""
    f = float(mtof(m))
    env = _env(dur, a=0.003, d=0.1, s=1.0, r=0.1)
    n = len(env)
    t = np.arange(n) / SR
    drop = float(p.get('zap', 24.0))
    tau = max(0.25, min(dur, 3.0) * 0.35)
    fr = f * 2 ** (drop * np.exp(-t / tau) / 12)
    x = va.saw(fr, n, _RNG.random())
    cut = 120 + 4000 * np.exp(-t / (tau * 0.8))
    y = va.vcf(np.vstack([x, x]), cut, res=0.55, drive=1.4)
    y = dist(y, 1.6)
    return y * env * 0.5


def pitchgrowl(m, dur, p, glide=None, mod=None):
    """Pitch-wobbling growl: a mid-bass (500 Hz - 3 kHz) whose pitch bends a semitone up and down with the LFO while
    a formant band-pass follows it - a moaning, alive mid-range over a clean sub."""
    f = float(mtof(m))
    env = _env(dur, a=0.02, d=0.1, s=1.0, r=0.08)
    n = len(env)
    lfo = _lfo(n, _rate(mod, p, 2.0), 'sine')
    fo = (f if f > 50 else f * 2) * 2 * 2 ** ((lfo - 0.5) * 2.0 / 12)
    x = np.zeros((2, n))
    for k, c in enumerate((-9, 9)):
        x[k] += va.saw(fo * 2 ** (c / 1200), n, _RNG.random())
    x = dist(x * 0.6, 2.4)
    y = _bp_moving(x, 700 + 1100 * lfo, 3.0) * 1.6 + 0.3 * va.vcf(x, 300 + 2000 * lfo, res=0.3, drive=1.0)
    y = _mid_hp(y, f, 300.0)
    return (y + _clean_sub(f, n, p.get('sub', 0.75))) * env * 0.45


def dddpad(m, dur, p, glide=None, mod=None):
    """Dark atmosphere: a wide, detuned saw drone with a breath of filtered noise, swelling in over seconds and kept
    under 1.5 kHz, drifting very slowly - the cold air behind a deep dubstep track."""
    f = float(mtof(m))
    gate = int(max(dur, 0.5) * SR)
    env = va.adsr(gate, float(p.get('a', min(4.0, max(0.8, dur * 0.4)))), 1.0, 0.95, float(p.get('r', 2.5)))
    n = len(env)
    t = np.arange(n) / SR
    x = np.zeros((2, n))
    for k, c in enumerate((-14, -5, 5, 14)):
        fr = f * 2 ** ((c + 3 * np.sin(2 * np.pi * (0.05 + 0.02 * k) * t + k)) / 1200)
        x[k % 2] += va.saw(fr, n, _RNG.random()) * 0.35
    x += 0.04 * np.vstack([_RNG.standard_normal(n), _RNG.standard_normal(n)])
    cut = float(p.get('cut', 1300)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * t))
    y = va.vcf(x, cut, res=0.2, drive=1.0)
    y = signal.sosfilt(signal.butter(2, 140 / (SR / 2), 'high', output='sos'), y, axis=-1)
    return y * env * 0.45


def virusflutter(m, dur, p, glide=None, mod=None):
    """Fluttering virtual-analog pad: a hollow mid-range chord tone that swells in and shimmers with a fast (about 10 Hz)
    flutter of its level and filter - glassy and uneasy, made for the space between drops."""
    f = float(mtof(m))
    gate = int(max(dur, 0.3) * SR)
    env = va.adsr(gate, float(p.get('a', min(3.0, max(0.5, dur * 0.35)))), 1.0, 0.9, float(p.get('r', 1.5)))
    n = len(env)
    t = np.arange(n) / SR
    x = np.vstack([va.pulse(np.full(n, f * 2 ** (-6 / 1200)), n, 0.1, 0.35) + 0.5 * va.saw(np.full(n, f * 2), n, 0.2),
                   va.pulse(np.full(n, f * 2 ** (6 / 1200)), n, 0.6, 0.35) + 0.5 * va.saw(np.full(n, f * 2), n, 0.7)])
    fl = 0.5 + 0.5 * np.sin(2 * np.pi * float(p.get('flutter', 10.0)) * t)
    y = va.vcf(x * 0.5, 900 + 1400 * fl, res=0.35, drive=1.0) * (0.75 + 0.25 * fl)
    y = signal.sosfilt(signal.butter(2, 400 / (SR / 2), 'high', output='sos'), y, axis=-1)
    return y * env * 0.4


def _bp_moving(x, fc, q):
    """Band-pass with a moving centre (block-wise, state carried) - two channels."""
    n = x.shape[-1]
    out = np.empty_like(x)
    for c in range(x.shape[0]):
        zi = np.zeros(2)
        for s in range(0, n, 64):
            e = min(n, s + 64)
            w = 2 * np.pi * float(np.clip(fc[s], 40, SR * 0.4)) / SR
            al = np.sin(w) / (2 * q)
            b = np.array([al, 0.0, -al]) / (1 + al)
            a = np.array([1.0, -2 * np.cos(w) / (1 + al), (1 - al) / (1 + al)])
            out[c, s:e], zi = signal.lfilter(b, a, x[c, s:e], zi=zi)
    return out


NEW_290 = (
    ('slowwob', slowwob, 'Slow deep wobble (one sweep per bar / half bar / beat)', 38),
    ('yoiwob', yoiwob, 'Talking "yoi" wobble (vowel oo-ah-oo)', 38),
    ('sweepwob', sweepwob, 'Rising sweep wobble (opens across each note)', 38),
    ('reesewob', reesewob, 'Slow dark reese wobble (rolling growl)', 38),
    ('deepsub', deepsub, 'Deep dubstep sine sub (clean, steady)', 38),
    ('sleepersub', sleepersub, "'Sleeper' sub (the sub's pitch slowly bends)", 38),
    ('brightwob', brightwob, 'Grimy bright wobble (dotted / triplet bounce)', 38),
    ('tearwob', tearwob, 'Tearout / riddim riff bass (tight chops)', 38),
    ('divesub', divesub, 'Diving sub (dives an octave, sags, or dives and returns)', 38),
    ('ms10zap', ms10zap, 'Mono analog zap bass (dives from two octaves up)', 38),
    ('pitchgrowl', pitchgrowl, 'Pitch-wobbling mid growl', 38),
    ('dddpad', dddpad, 'Dark swelling atmosphere (deep dubstep)', 89, ('pad',)),
    ('virusflutter', virusflutter, 'Fluttering hollow pad (fast shimmer)', 89, ('pad', 'chords')),
)


def register():
    from .instruments import GM_PROGRAM, INSTRUMENT_INFO, INSTRUMENTS, ROLE_CHOICES
    for name, fn, info, gm, *roles in NEW_290:
        INSTRUMENTS[name] = fn
        INSTRUMENT_INFO[name] = info
        GM_PROGRAM[name] = gm
        for role in (roles[0] if roles else ('bass',)):
            if name not in ROLE_CHOICES.setdefault(role, []):
                ROLE_CHOICES[role].append(name)


# ---- (2.10) generative-modular sounds: warbly, slightly unstable, alive ----

def _drift(n, cents, rate, seed):
    """A slow, wandering pitch drift in cents (a modular oscillator that won't sit still)."""
    rng = np.random.default_rng(seed)
    k = max(2, int(n / SR * rate) + 2)
    pts = rng.standard_normal(k) * cents
    x = np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)
    return x


def modularpad(m, dur, p, glide=None, mod=None):
    """Modular pad: two slightly detuned oscillators (a soft saw and a wavefolded triangle) that each drift on their
    own by 10-20 cents, a low-pass that breathes slowly, a long swell - celestial but never quite stable."""
    f = float(mtof(m))
    gate = int(max(dur, 0.4) * SR)
    env = va.adsr(gate, float(p.get('a', min(2.5, max(0.6, dur * 0.3)))), 1.0, 0.95, float(p.get('r', 2.0)))
    n = len(env)
    t = np.arange(n) / SR
    out = np.zeros((2, n))
    for c in range(2):
        dr = _drift(n, 9.0, 0.6, int(m) * 13 + c)
        fr = f * 2 ** ((dr + (-6 if c == 0 else 6)) / 1200)
        ph = np.cumsum(fr) / SR % 1.0
        tri = 4 * np.abs(ph - 0.5) - 1
        fold = np.sin(np.pi * tri * (1.2 + 0.6 * np.sin(2 * np.pi * 0.09 * t + c)))
        sw = va.saw(fr, n, _RNG.random())
        out[c] = 0.55 * fold + 0.45 * sw
    cut = float(p.get('cut', 2200)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.06 * t))
    y = va.vcf(out * 0.6, cut, res=0.25, drive=1.0)
    y = signal.sosfilt(signal.butter(2, 160 / (SR / 2), 'high', output='sos'), y, axis=-1)
    return y * env * 0.5


def modularlead(m, dur, p, glide=None, mod=None):
    """Soaring modular lead: a warm pulse-and-saw voice that glides between notes, drifts in pitch, and opens up as it
    holds - big and singing once the track opens, a little wobbly like a patch left running."""
    f = float(mtof(m))
    gate = int(max(dur, 0.06) * SR)
    env = va.adsr(gate, 0.04, 0.3, 0.85, float(p.get('r', 0.8)))
    n = len(env)
    t = np.arange(n) / SR
    fr = np.full(n, f) if glide is None else f + (float(mtof(glide)) - f) * np.exp(-t / 0.09)
    dr = _drift(n, 7.0, 1.2, int(m) * 7 + 3)
    vib = np.clip((t - 0.35) / 0.5, 0, 1) * 10 * np.sin(2 * np.pi * 4.6 * t)
    fr = fr * 2 ** ((dr + vib) / 1200)
    x = np.vstack([va.saw(fr * 2 ** (-5 / 1200), n, 0.1) + 0.5 * va.pulse(fr, n, 0.3, 0.4),
                   va.saw(fr * 2 ** (5 / 1200), n, 0.6) + 0.5 * va.pulse(fr, n, 0.8, 0.4)])
    cut = 700 + (float(p.get('cut', 3200)) - 700) * (1 - np.exp(-t / 0.6))
    y = va.vcf(x * 0.45, cut, res=0.3, drive=1.2)
    y = signal.sosfilt(signal.butter(2, 220 / (SR / 2), 'high', output='sos'), y, axis=-1)
    return y * env * 0.5


def modularseq(m, dur, p, glide=None, mod=None):
    """Generative modular blip: a short, round, slightly detuned pluck with a random-ish filter and tiny pitch wobble -
    for the patch-generated sequences that run underneath."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.35), 0.03) * SR)
    env = va.adsr(gate, 0.002, 0.22, 0.0, 0.2)
    n = len(env)
    t = np.arange(n) / SR
    seed = int(m) * 31 + int(dur * 1000)
    fr = f * 2 ** (_drift(n, 6.0, 3.0, seed) / 1200)
    ph = np.cumsum(fr) / SR % 1.0
    x = np.sin(np.pi * (4 * np.abs(ph - 0.5) - 1) * 1.8)
    top = 900 + 2600 * np.random.default_rng(seed).random()
    y = va.vcf(np.vstack([x, x]) * 0.6, 200 + top * np.exp(-t / 0.08), res=0.4, drive=1.1)
    return y * env * 0.5


NEW_210 = (('modularpad', modularpad, 'Modular pad (warbly, drifting, celestial)', 89, ('pad', 'chords')),
           ('modularlead', modularlead, 'Soaring modular lead (gliding, drifting)', 81, ('lead',)),
           ('modularseq', modularseq, 'Generative modular blip (patch sequences)', 81, ('arp',)))
NEW_290 = NEW_290 + NEW_210


# ---- (2.12.1) deep "bass amapiano" log drums: the log drum as the song's bass and lead - saturated, sustained by
# heavy upward compression instead of knocking and dying, a resonant low-pass closing on each note, and a talking pitch
# movement / slide between notes ----

def _log_body(m, dur, p, glide, talk, mod):
    from .dsp import svf_sweep
    f = float(mtof(m))
    while f < 55:
        f *= 2                                                         # it sits above the sub, 55-110 Hz
    f0 = float(mtof(glide)) if glide is not None else f * 1.6
    while glide is not None and f0 < 55:
        f0 *= 2
    gate = max(0.08, float(dur))
    n = int((gate + 0.09) * SR)
    t = np.arange(n) / SR
    fr = f + (f0 - f) * np.exp(-t * (18 if glide is not None else 34))      # drops in from above / slides from the note before
    if talk:                                                           # the "talking" log: a synced bend up and back
        lfo = _lfo(n, _rate(mod, p, 1.0), 'sine')
        fr = fr * 2 ** ((talk * (lfo - 0.5) * 2) / 12)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    body = np.sin(ph) + 0.45 * np.tanh(3 * np.sin(ph)) + 0.25 * np.sin(2 * ph)
    cut = 140 + 1500 * np.exp(-t * 16)                                 # resonant low-pass closing to ~100-150 Hz
    if talk:
        cut = cut + 500 * _lfo(n, _rate(mod, p, 1.0), 'sine') * np.exp(-t * 2)
    y = svf_sweep(body, cut, q=2.2) + 0.55 * np.sin(ph)
    y += signal.lfilter(*signal.butter(2, [700 / (SR / 2), 2400 / (SR / 2)], 'band'), np.random.default_rng(int(m)).standard_normal(n)) \
        * np.exp(-t * 170) * 0.35                                      # the woody knock on top
    # upward compression: the knock stays, the body holds up for the whole note instead of dying away
    env = (0.62 + 0.38 * np.exp(-t * 14)) * np.exp(-t * float(p.get('decay', 0.9))) * np.minimum(t / 0.0015, 1)
    g = int(gate * SR)
    if g < n:
        env[g:] *= np.exp(-np.arange(n - g) / (0.035 * SR))
    y = np.tanh(y * env * float(p.get('drive', 1.3))) * 0.7            # soft saturation
    y = signal.lfilter(*signal.butter(1, 22 / (SR / 2), 'high'), y)    # no DC thump
    return np.vstack([y, y])                                           # mono low end


def logdrum_deep(m, dur, p, glide=None, mod=None):
    """Deep log drum (bass amapiano): saturated and sustained, a resonant low-pass closing on every note, slides."""
    return _log_body(m, dur, p, glide, 0.0, mod)


def logdrum_talk(m, dur, p, glide=None, mod=None):
    """Talking log drum: the deep log with a synced pitch bend and filter wah - it 'speaks' on long notes."""
    return _log_body(m, dur, p, glide, float(p.get('talk', 1.2)), mod)


NEW_2121 = (('logdrum_deep', logdrum_deep, 'Deep log drum (bass amapiano: saturated, sustained, sliding)', 117),
            ('logdrum_talk', logdrum_talk, 'Talking log drum (pitch bend + wah)', 117))
NEW_290 = NEW_290 + NEW_2121


# ---- (2.12.1) more bass-amapiano sounds, from the user's notes: a near-sine log drum with a strong pitch scoop, and
# the "alive" detuned-saw pad / stab - a 7-voice supersaw kept soft and filtered, its cutoff breathing on a slow LFO,
# a tiny pitch warble and a little scoop into each note ----

def logdrum_sine(m, dur, p, glide=None, mod=None):
    """Sine log drum: an almost pure sine with a strong pitch scoop from above (or a slide from the note before), a
    little random drift in pitch and level so it feels alive, saturated so it stays thick - the defining sound."""
    f = float(mtof(m))
    while f < 55:
        f *= 2
    f0 = float(mtof(glide)) if glide is not None else f * 2.0
    while glide is not None and f0 < 55:
        f0 *= 2
    gate = max(0.08, float(dur))
    n = int((gate + 0.08) * SR)
    t = np.arange(n) / SR
    drift = 2 ** (_drift(n, 6.0, 3.0, int(m) * 7 + 1) / 1200)            # a few cents of wander
    fr = (f + (f0 - f) * np.exp(-t * (16 if glide is not None else 28))) * drift
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph) + 0.12 * np.sin(2 * ph) * np.exp(-t * 6)
    env = (0.7 + 0.3 * np.exp(-t * 10)) * np.exp(-t * float(p.get('decay', 1.1))) * np.minimum(t / 0.0012, 1)
    env *= 1 + 0.04 * np.sin(2 * np.pi * 4.3 * t)                         # slight level movement
    g = int(gate * SR)
    if g < n:
        env[g:] *= np.exp(-np.arange(n - g) / (0.03 * SR))
    y = np.tanh(y * env * float(p.get('drive', 1.8))) * 0.75             # saturation: thick, present
    y = signal.lfilter(*signal.butter(1, 22 / (SR / 2), 'high'), y)
    return np.vstack([y, y])


def _amasaw(m, dur, p, mod, stab):
    from .dsp import svf_sweep
    f = float(mtof(m))
    gate = max(0.05, float(dur))
    a, r = (0.003, 0.18) if stab else (float(p.get('a', 0.35)), float(p.get('r', 1.0)))
    env = va.adsr(int(gate * SR), a, 0.25 if stab else 0.6, 0.0 if stab else 0.85, r)
    n = len(env)
    t = np.arange(n) / SR
    scoop = 2 ** ((-45 * np.exp(-t * 18)) / 1200)                         # scoops up into the note
    warble = 2 ** ((5 * np.sin(2 * np.pi * 0.45 * t + m)) / 1200)         # tiny pitch drift
    out = np.zeros((2, n))
    rng = np.random.default_rng(int(m) * 13 + (1 if stab else 0))
    for k, c in enumerate((-17, -11, -5, 0, 5, 11, 17)):                  # 7 detuned saws, spread across the stereo
        x = va.saw(f * scoop * warble * 2 ** (c / 1200), n, rng.random())
        pan = (k - 3) / 3 * 0.7
        out[0] += x * (1 - pan) * 0.5
        out[1] += x * (1 + pan) * 0.5
    lfo_hz = _rate(mod, p, 4.0) if mod else float(p.get('lfo', 0.35))      # slow breathing: 0.1-2 Hz
    lfo = _lfo(n, min(2.0, max(0.1, lfo_hz)), 'tri')
    if stab:
        cut = 500 + 2600 * np.exp(-t * 22) + 400 * lfo                     # a quick filter envelope on the stab
    else:
        cut = float(p.get('cut', 1300)) * (0.55 + 0.9 * lfo)
    for ch in range(2):
        out[ch] = svf_sweep(out[ch], cut, q=1.1)
    out = signal.lfilter(*signal.butter(2, 180 / (SR / 2), 'high'), out, axis=1)   # sits above the log drum
    return np.tanh(out * env * 0.55) * 0.5


def amapad_saw(m, dur, p, glide=None, mod=None):
    """Breathing supersaw pad: 7 detuned saws, soft and low-passed, cutoff moving on a slow LFO, a little pitch scoop
    and warble - the alive, slightly unstable amapiano pad."""
    return _amasaw(m, dur, p, mod, False)


def amastab_saw(m, dur, p, glide=None, mod=None):
    """Scooping supersaw stab: the same saw stack as a short chord stab with a pitch scoop and a quick filter snap."""
    return _amasaw(m, dur, p, mod, True)


NEW_2121B = (('logdrum_sine', logdrum_sine, 'Sine log drum (pitch scoop, saturated, alive)', 117),
             ('amapad_saw', amapad_saw, 'Breathing supersaw pad (slow LFO filter, pitch warble)', 90, ('pad', 'chords')),
             ('amastab_saw', amastab_saw, 'Scooping supersaw stab (pitch scoop + filter snap)', 90, ('chords',)))
NEW_290 = NEW_290 + NEW_2121B
