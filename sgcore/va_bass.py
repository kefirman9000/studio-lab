"""Bass-music synths on the analog engine (1.59): the wobble, growl, reese / neuro, riddim, screech and hoover sounds of
dubstep, drum & bass and rave - plus the house organ stab.

What makes them sound like real synths instead of cheap digital ones:
  - every distortion stage runs at 4x the sample rate (no aliasing hash folding back down as metallic fizz);
  - the filters are the resonant 24 dB low-pass of va.vcf and real band-passes, moving smoothly through the note;
  - movement is tempo-synced (the LFO speed comes from the note's mod = beats per cycle) with proper LFO shapes;
  - the low end is split off: a clean, steady sine sub under a mid-bass that can be as nasty as it likes, high-passed
    so the two never phase against each other.
"""
import numpy as np
from scipy import signal

from .dsp import SR, mtof
from . import va

_RNG = np.random.default_rng(59)


def dist(x, drive=3.0, kind='tanh', os_=4):
    """Oversampled waveshaper: 'tanh' (warm), 'fold' (buzzy wavefolder), 'hard' (clipped, aggressive)."""
    x = np.asarray(x, float)
    up = signal.resample_poly(x, os_, 1, axis=-1)
    if kind == 'fold':
        y = np.sin(up * drive * 1.3)
    elif kind == 'hard':
        y = np.clip(up * drive, -1, 1)
        y = 1.5 * y - 0.5 * y ** 3
    else:
        y = np.tanh(up * drive) / np.tanh(drive)
    return signal.resample_poly(y, 1, os_, axis=-1)[..., :x.shape[-1]]


def _lfo(n, hz, shape='sine', phase=0.0):
    t = np.arange(n) / SR
    ph = (hz * t + phase) % 1.0
    if shape == 'saw':
        v = (1 - ph) ** 1.6
    elif shape == 'square':
        v = 0.5 + 0.5 * np.tanh(12 * np.sin(2 * np.pi * ph))
    elif shape == 'tri':
        v = 1 - np.abs(2 * ph - 1)
    else:
        v = 0.5 - 0.5 * np.cos(2 * np.pi * ph)
    k = max(1, int(0.002 * SR))
    return np.convolve(v, np.ones(k) / k, mode='same')


def _env(dur, a=0.003, d=0.08, s=1.0, r=0.04):
    return va.adsr(int(max(dur, 0.02) * SR), a, d, s, r)


def _bp(x, fc, q):
    """Band-pass with a moving centre (block-wise, state carried)."""
    n = x.shape[-1]
    fc = np.broadcast_to(np.asarray(fc, float), (n,))
    out = np.empty_like(x)
    chans = x if x.ndim == 2 else x[None, :]
    o = out if x.ndim == 2 else out[None, :]
    for c in range(chans.shape[0]):
        zi = np.zeros(2)
        for s in range(0, n, 96):
            e = min(n, s + 96)
            w = 2 * np.pi * float(np.clip(fc[s], 40, SR * 0.4)) / SR
            al = np.sin(w) / (2 * q)
            b = np.array([al, 0, -al]) / (1 + al)
            a = np.array([1, -2 * np.cos(w) / (1 + al), (1 - al) / (1 + al)])
            o[c, s:e], zi = signal.lfilter(b, a, chans[c, s:e], zi=zi)
    return out


def _sub(f, n, level=1.0):
    t = np.arange(n) / SR
    fs = f if f < 70 else f / 2
    return np.sin(2 * np.pi * fs * t) * level


def _split_hp(y, f):
    """High-pass the mid layer above its own fundamental (4th order) so only the sub carries the bottom."""
    fc = max(90.0, f * 1.6)
    b, a = signal.butter(4, fc / (SR / 2), 'high')
    return signal.lfilter(b, a, y, axis=-1)


def _rate(mod, p, default=0.5):
    beats = mod if isinstance(mod, (int, float)) and mod else default
    return 1.0 / (beats * p.get('spb', 0.43))


def wobble(m, dur, p, glide=None, mod=None):
    """Dubstep wobble: a unison saw + square stack through a resonant low-pass whose cutoff an LFO sweeps on an
    exponential curve (so it says 'wow'), a vowel band-pass following it, oversampled drive, over a clean sine sub."""
    f = float(mtof(m))
    env = _env(dur)
    n = len(env)
    fo = f if f > 55 else f * 2
    x = np.zeros((2, n))
    for k, c in enumerate((-9, -3, 3, 9)):
        s_ = va.saw(np.full(n, fo * 2 ** (c / 1200)), n, _RNG.random())
        x[k % 2] += s_
    sq = va.pulse(np.full(n, fo * 2), n, 0.1, 0.5) * 0.5
    x += sq
    x *= 0.4
    lfo = _lfo(n, _rate(mod, p), p.get('shape', 'sine'))
    top = p.get('cut', 2600)
    cut = 140 * (top / 140) ** lfo
    y = va.vcf(x, cut, res=p.get('res', 0.55), drive=1.6)
    y = y + 0.5 * _bp(y, 350 + 900 * lfo, 4.0)
    y = dist(y, 2.6 + float(p.get('grit', 1.2)))
    y = _split_hp(y, f) * 0.55
    return (y + _sub(f, n, p.get('sub', 0.85))) * env * 0.55


def growl(m, dur, p, glide=None, mod=None):
    """Growl: an FM pair (the modulator a fifth / octave up) whose index rises and falls with a synced LFO, through two
    moving vowel band-passes ('yoy' / 'ow' / 'ah') and an oversampled wavefolder - the talking mid-bass of brostep and
    neurofunk - with a clean sub underneath."""
    f = float(mtof(m))
    env = _env(dur, 0.004, 0.1, 1.0, 0.04)
    n = len(env)
    t = np.arange(n) / SR
    lfo = _lfo(n, _rate(mod, p), p.get('shape', 'sine'))
    fo = f if f > 55 else f * 2
    ph = 2 * np.pi * fo * t
    idx = 1.2 + 5.5 * lfo
    x = np.sin(ph + idx * np.sin(ph * p.get('ratio', 2.0))) + 0.35 * (va.saw(np.full(n, fo * 1.004), n) + va.saw(np.full(n, fo * 0.996), n, 0.4))
    x = dist(x, 2.2, 'fold')
    y = _bp(x, 260 + 640 * lfo, 5.0) + 0.8 * _bp(x, 800 + 1200 * lfo, 6.0) + 0.25 * x
    y = dist(y * 1.6, 2.2)
    y = np.vstack([y, np.roll(y, 25)])
    y = _split_hp(y, f) * 0.6
    return (y + _sub(f, n, p.get('sub', 0.8))) * env * 0.6


def reese(m, dur, p, glide=None, mod=None):
    """Reese / neuro bass: four saws a few cents apart whose detune slowly breathes, a resonant low-pass, an
    oversampled drive and a moving notch (the phaser-like 'movement' of DnB basslines), over a steady sine sub."""
    f = float(mtof(m))
    env = _env(dur, 0.01, 0.3, 0.9, 0.1)
    n = len(env)
    t = np.arange(n) / SR
    mv = p.get('move', 1.0)
    breathe = 1 + mv * 0.5 * np.sin(2 * np.pi * 0.21 * t + _RNG.random() * 6)
    x = np.zeros((2, n))
    for k, c in enumerate((-14, -5, 5, 14)):
        cents = c * breathe
        s_ = va.saw(f * 2 ** (cents / 1200), n, _RNG.random())
        x[0] += s_ * (0.8 if k < 2 else 0.5)
        x[1] += s_ * (0.5 if k < 2 else 0.8)
    x *= 0.4
    cut = p.get('cut', 900) * (1.0 + 0.6 * _lfo(n, 0.6 * mv + 0.05, 'sine'))
    y = va.vcf(x, cut, res=p.get('res', 0.25), drive=1.4)
    y = dist(y, p.get('drive', 2.4))
    notch_c = 500 + 1500 * _lfo(n, 0.33 * mv + 0.05, 'tri')
    y = y - 0.7 * _bp(y, notch_c, 2.5)                                   # the moving notch
    y = _split_hp(y, f) * 0.7
    return (y + _sub(f, n, 1.3) * 0.75) * env * 0.6


def neuro(m, dur, p, glide=None, mod=None):
    """Neuro bass: a reese core torn up - comb-like resonant band-passes sweeping on a synced LFO, a wavefolder and a
    hard clip, so every note snarls and shifts (neurofunk, tech DnB, jump-up)."""
    f = float(mtof(m))
    base = reese(m, dur, dict(p, drive=3.0, sub=0.0), glide, mod)
    n = base.shape[1]
    lfo = _lfo(n, _rate(mod, p, 0.25), p.get('shape', 'saw'))
    y = base - _sub(f, n, 1.3) * 0.75 * _env(dur, 0.01, 0.3, 0.9, 0.1)[:n]
    y = _bp(y, 400 + 2600 * lfo, 7.0) * 1.8 + 0.4 * y
    y = dist(y, 2.0, 'fold')
    y = dist(y, 1.6, 'hard') * 0.6
    y = _split_hp(y, f)
    return (y + _sub(f, n, 0.8) * _env(dur, 0.01, 0.3, 0.9, 0.1)[:n]) * 0.55


def riddim(m, dur, p, glide=None, mod=None):
    """Riddim: a hollow square / saw stack through a resonant band, chopped by a tempo-synced gate (mod = chop length in
    beats), oversampled drive, over a clean sub."""
    f = float(mtof(m))
    env = _env(dur, 0.002, 0.05, 1.0, 0.02)
    n = len(env)
    hz = _rate(mod, p, 1 / 3)
    t = np.arange(n) / SR
    gate = (np.sin(2 * np.pi * hz * t) > -0.2).astype(float)
    gate = np.convolve(gate, np.ones(64) / 64, mode='same')
    fo = f if f > 55 else f * 2
    x = va.pulse(np.full(n, fo), n, 0.0, 0.5) + 0.7 * va.saw(np.full(n, fo * 1.006), n) + 0.5 * va.pulse(np.full(n, fo * 2.003), n, 0.25, 0.3)
    y = va.vcf(x, p.get('cut', 900), res=0.5, drive=1.5) + 0.3 * x
    y = dist(y, 3.0)
    y = _split_hp(np.vstack([y, y]), f) * 0.5 * gate
    return (y + _sub(f, n, p.get('sub', 0.7))) * env


def screech(m, dur, p, glide=None, mod=None):
    """Brostep screech: a high FM tone with a sweeping resonant band and a whine up into the note, oversampled."""
    f = float(mtof(m)) * 2 ** p.get('octave', 1)
    env = _env(dur, 0.003, 0.08, 0.95, 0.03)
    n = len(env)
    t = np.arange(n) / SR
    bend = 2 ** ((-5 * np.exp(-t * 18)) / 12)
    lfo = _lfo(n, _rate(mod, p, 0.25))
    ph = 2 * np.pi * np.cumsum(f * bend) / SR
    x = np.sin(ph + (3.0 + 6.0 * lfo) * np.sin(ph * 3.01)) + 0.4 * va.saw(f * bend * 1.01, n)
    x = dist(x, 2.8)
    y = _bp(x, 900 + 2600 * lfo, 5.0) + 0.3 * x
    b, a = signal.butter(2, 300 / (SR / 2), 'high')
    y = dist(signal.lfilter(b, a, y) * 1.6, 1.8) * 0.35
    return np.vstack([y, np.roll(y, 40)]) * env


def hoover(m, dur, p, glide=None, mod=None):
    """Rave hoover: pulse-width-modulated saws, 7 voices wide, scooping down into the note, through a soft low-pass."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = va.adsr(gate, 0.01, 0.3, 0.85, 0.2)
    n = len(env)
    t = np.arange(n) / SR
    bend = 2 ** ((-5 * np.exp(-t * 18)) / 12)
    pwm = 0.5 + 0.35 * np.sin(2 * np.pi * 0.9 * t)
    L = np.zeros(n)
    R = np.zeros(n)
    for i, c in enumerate((-28, -16, -6, 0, 6, 16, 28)):
        fr = f * bend * 2 ** (c / 1200)
        s_ = va.saw(fr, n, _RNG.random()) + 0.6 * va.pulse(fr * 0.5, n, _RNG.random(), pwm)
        th = i / 6 * np.pi / 2
        L += s_ * np.cos(th)
        R += s_ * np.sin(th)
    y = va.vcf(np.vstack([L, R]) / 4.0, p.get('cut', 4500), 0.15, 1.2)
    return y * env * 0.45


def house_organ(m, dur, p, glide=None, mod=None):
    """The M1-style house organ stab: hollow, bright additive organ with a click, a quick decay and a short tail -
    90s house chords and basslines."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    n = gate + int(0.12 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for r, a in ((1, 1.0), (2, 0.8), (3, 0.55), (4, 0.4), (6, 0.25), (8, 0.18)):
        if f * r < 14000:
            y += a * np.sin(2 * np.pi * f * r * t + _RNG.random() * 6.28)
    y *= np.exp(-t * p.get('decay', 3.0)) * 0.6 + 0.4
    ck = int(0.003 * SR)
    y[:ck] += _RNG.standard_normal(ck) * 0.3 * np.linspace(1, 0, ck)
    env = np.ones(n)
    env[:int(0.002 * SR)] = np.linspace(0, 1, int(0.002 * SR))
    env[gate:] = np.exp(-np.arange(n - gate) / (0.04 * SR))
    y = dist(y * env * 0.4, 1.4)
    return np.vstack([y, np.roll(y, 30)]) * 0.5
