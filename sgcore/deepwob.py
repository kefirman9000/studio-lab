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
    t = np.arange(n) / SR
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
