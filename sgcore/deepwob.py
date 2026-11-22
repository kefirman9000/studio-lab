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
)


def register():
    from .instruments import GM_PROGRAM, INSTRUMENT_INFO, INSTRUMENTS, ROLE_CHOICES
    for name, fn, info, gm in NEW_290:
        INSTRUMENTS[name] = fn
        INSTRUMENT_INFO[name] = info
        GM_PROGRAM[name] = gm
        if name not in ROLE_CHOICES.setdefault('bass', []):
            ROLE_CHOICES['bass'].append(name)
