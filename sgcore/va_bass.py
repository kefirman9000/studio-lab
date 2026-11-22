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


LFO_MAX_HZ = 9.5                     # (2.10) the fastest a bass LFO may wobble (140 BPM 16ths still fit)


def sync_hz(beats, spb, cap=LFO_MAX_HZ):
    """(2.10) Tempo-synced LFO speed, kept musical: at drum & bass tempos a 1/6- or 1/4-beat LFO ran at 17-23 Hz - a
    buzz rather than a wobble. Too-fast rates are slowed by whole doublings (still in time with the beat) until they
    are at most ~9.5 wobbles a second (a 16th at 140 BPM)."""
    beats = float(beats) if beats else 0.5
    hz = 1.0 / (beats * float(spb))
    while hz > cap * 1.01:
        hz /= 2.0
    return hz


def _rate(mod, p, default=0.5):
    beats = mod if isinstance(mod, (int, float)) and not isinstance(mod, bool) and mod else default
    return sync_hz(beats, p.get('spb', 0.43), float(p.get('lfo_max', LFO_MAX_HZ)))


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


# (1.96) the reese's four saws start every note at the same phases (and the detune 'breathing' at the same point):
# random phases per note made fast reese lines jump between a different swirl on every 16th - a glitchy, stuttering sound
REESE_PH = (0.0, 0.31, 0.62, 0.87)


def reese_v2(m, dur, p, glide=None, mod=None):
    """(1.59-1.83 reese, kept as "reese_v2") Reese / neuro bass: four saws a few cents apart whose detune slowly breathes, a resonant low-pass, an
    oversampled drive and a moving notch (the phaser-like 'movement' of DnB basslines), over a steady sine sub."""
    f = float(mtof(m))
    env = _env(dur, 0.01, 0.3, 0.9, 0.1)
    n = len(env)
    t = np.arange(n) / SR
    mv = p.get('move', 1.0)
    breathe = 1 + mv * 0.5 * np.sin(2 * np.pi * 0.21 * t + 1.3)      # (1.96) fixed phases: every note starts alike
    x = np.zeros((2, n))
    for k, c in enumerate((-14, -5, 5, 14)):
        cents = c * breathe
        s_ = va.saw(f * 2 ** (cents / 1200), n, REESE_PH[k])
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



def reese(m, dur, p, glide=None, mod=None):
    """Reese bass (1.84): four saws a few cents apart whose detune slowly breathes. The saws are high-passed above the
    note BEFORE they are driven, so the drive only thickens the growl instead of the low fundamental modulating it (that
    intermodulation was the crackly 'clipping' sound of the old reese); a resonant low-pass, a moving notch for the
    phaser-like movement, and a steady sine sub at a level that leaves the master headroom."""
    f = float(mtof(m))
    env = _env(dur, 0.012, 0.3, 0.92, 0.1)
    n = len(env)
    t = np.arange(n) / SR
    mv = p.get('move', 1.0)
    breathe = 1 + mv * 0.5 * np.sin(2 * np.pi * 0.21 * t + 1.3)      # (1.96) fixed phases: every note starts alike
    x = np.zeros((2, n))
    for k, c in enumerate((-14, -5, 5, 14)):
        s_ = va.saw(f * 2 ** (c * breathe / 1200), n, REESE_PH[k])
        x[0] += s_ * (0.8 if k < 2 else 0.5)
        x[1] += s_ * (0.5 if k < 2 else 0.8)
    x = _split_hp(x * 0.4, f)                                              # mids only into the drive
    cut = p.get('cut', 900) * (1.0 + 0.6 * _lfo(n, 0.6 * mv + 0.05, 'sine'))
    y = va.vcf(x, np.maximum(cut, f * 2.2), res=p.get('res', 0.22), drive=1.2)
    y = dist(y * 1.4, p.get('drive', 1.7))
    notch_c = 500 + 1500 * _lfo(n, 0.33 * mv + 0.05, 'tri')
    y = y - 0.6 * _bp(y, notch_c, 2.5)
    y = _split_hp(y, f) * 0.8
    return (y + _sub(f, n, 0.72)) * env * 0.6

def neuro(m, dur, p, glide=None, mod=None):
    """Neuro bass: a reese core torn up - comb-like resonant band-passes sweeping on a synced LFO, a wavefolder and a
    hard clip, so every note snarls and shifts (neurofunk, tech DnB, jump-up)."""
    f = float(mtof(m))
    base = reese_v2(m, dur, dict(p, drive=3.0, sub=0.0), glide, mod)
    n = base.shape[1]
    lfo = _lfo(n, _rate(mod, p, 0.25), p.get('shape', 'saw'))
    y = base - _sub(f, n, 1.3) * 0.75 * _env(dur, 0.01, 0.3, 0.9, 0.1)[:n]
    y = _bp(y, 400 + 2600 * lfo, 7.0) * 1.8 + 0.4 * y
    y = dist(y, 2.0, 'fold')
    y = dist(y, 1.6, 'hard') * 0.6
    y = _split_hp(y, f)
    return (y + _sub(f, n, 0.8) * _env(dur, 0.01, 0.3, 0.9, 0.1)[:n]) * 0.55


GATE_RAMP = 132


def riddim(m, dur, p, glide=None, mod=None):
    """Riddim: a hollow square / saw stack through a resonant band, chopped by a tempo-synced gate (mod = chop length in
    beats), oversampled drive, over a clean sub."""
    f = float(mtof(m))
    env = _env(dur, 0.004, 0.05, 1.0, 0.035)
    n = len(env)
    hz = _rate(mod, p, 1 / 3)
    t = np.arange(n) / SR
    gate = (np.sin(2 * np.pi * hz * t) > -0.2).astype(float)
    gate = np.convolve(gate, np.ones(GATE_RAMP) / GATE_RAMP, mode='same')   # (1.96) 3 ms chop edges, not 1.5 ms clicks
    fo = f if f > 55 else f * 2
    x = va.pulse(np.full(n, fo), n, 0.0, 0.5) + 0.7 * va.saw(np.full(n, fo * 1.006), n) + 0.5 * va.pulse(np.full(n, fo * 2.003), n, 0.25, 0.3)
    y = va.vcf(x, p.get('cut', 900), res=0.5, drive=1.5) + 0.3 * x
    y = dist(y, 3.0)
    y = _split_hp(np.vstack([y, y]), f) * 0.5 * gate
    return (y + _sub(f, n, p.get('sub', 0.7))) * env


def screech(m, dur, p, glide=None, mod=None):
    """Brostep screech: a high FM tone with a sweeping resonant band and a whine up into the note, oversampled."""
    f = float(mtof(m)) * 2 ** p.get('octave', 1 if m < 55 else 0)     # an octave up only from the bass register
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


# ----------------------------------------------------------------------------- 1.62: more wobbles + techno voices
_VOWELS = np.array([[400, 800, 2600], [700, 1150, 2800], [550, 1700, 2500], [300, 2250, 3000]], float)   # o a e i


def _stack(fo, n, voices=4, cents=18, pulse=0.3):
    """Unison saws spread left / right + a square an octave up for bite -> (2, n)."""
    x = np.zeros((2, n))
    for k in range(voices):
        c = (k / max(1, voices - 1) - 0.5) * 2 * cents
        x[k % 2] += va.saw(np.full(n, fo * 2 ** (c / 1200)), n, _RNG.random())
    if pulse:
        x += va.pulse(np.full(n, fo * 2), n, 0.1, 0.5) * pulse
    return x * (1.6 / voices)


def _vowel(x, pos):
    """Talking filter: three formant band-passes gliding between the vowels o - a - e - i as `pos` goes 0 -> 1."""
    k = np.clip(np.asarray(pos, float), 0, 1) * (len(_VOWELS) - 1)
    i0 = np.minimum(k.astype(int), len(_VOWELS) - 2)
    fr = k - i0
    out = 0
    for j, (q, g) in enumerate(((6.0, 1.0), (9.0, 0.7), (11.0, 0.3))):
        fc = _VOWELS[i0, j] * (1 - fr) + _VOWELS[i0 + 1, j] * fr
        out = out + g * _bp(x, fc, q)
    return out


def dnb_wobble(m, dur, p, glide=None, mod=None):
    """DnB wobble: a reese-like pair of detuned saws (plus a little square) through a tighter resonant low-pass on a
    fast synced LFO (16ths by default), cleaner drive and more mids - rolling and hypnotic under fast breaks - with a
    clean mono sub."""
    f = float(mtof(m))
    env = _env(dur, 0.003, 0.1, 1.0, 0.03)
    n = len(env)
    fo = f if f > 55 else f * 2
    x = _stack(fo, n, 2, 14, 0.25)
    lfo = _lfo(n, _rate(mod, p, 0.25), p.get('shape', 'tri'))
    cut = 220 * (p.get('cut', 1900) / 220) ** (0.25 + 0.75 * lfo)
    y = va.vcf(x, cut, res=p.get('res', 0.45), drive=1.3)
    y = dist(y, 1.6 + 0.6 * float(p.get('grit', 1.0)))
    y = _split_hp(y, f) * 0.75 * (0.85 + 0.15 * lfo)
    return (y + _sub(f, n, p.get('sub', 0.75))) * env * 0.6


def vowel_wobble(m, dur, p, glide=None, mod=None):
    """Vocal wobble ('yoy'): a fat saw stack through formant filters that slide o -> a -> i with the synced LFO, so the
    bass talks, then clipped hard after the filter so the moving peaks scream - with a clean sub."""
    f = float(mtof(m))
    env = _env(dur)
    n = len(env)
    fo = f if f > 55 else f * 2
    x = _stack(fo, n, 4, 16, 0.4)
    lfo = _lfo(n, _rate(mod, p), p.get('shape', 'sine'))
    y = _vowel(x, lfo) * 2.2 + 0.15 * va.vcf(x, 200 + 1200 * lfo, 0.3)
    y = dist(y, 3.0 + float(p.get('grit', 1.0)), 'hard')
    y = _split_hp(y, f) * 0.45
    return (y + _sub(f, n, p.get('sub', 0.85))) * env * 0.55


def multi_wobble(m, dur, p, glide=None, mod=None):
    """Multiband wobble: the low-mids wobble on the beat's LFO through a resonant low-pass while the top band moves
    on its own faster LFO (a band-pass sweeping and pumping), each driven separately - a complex, layered drop bass."""
    f = float(mtof(m))
    env = _env(dur)
    n = len(env)
    fo = f if f > 55 else f * 2
    x = _stack(fo, n, 6, 20, 0.35)
    r = _rate(mod, p)
    lfo1 = _lfo(n, r, p.get('shape', 'sine'))
    lfo2 = _lfo(n, r * p.get('ratio', 2.0), 'tri', 0.25)
    low = va.vcf(x, 130 * (1400 / 130) ** lfo1, 0.5, 1.4)
    low = dist(low, 2.4)
    high = _bp(x, 1400 + 3200 * lfo2, 2.5) * (0.25 + 0.75 * lfo2)
    high = dist(high * 2, 2.0)
    y = np.asarray(low) + 0.7 * np.asarray(high)
    y = _split_hp(y, f) * 0.55
    return (y + _sub(f, n, p.get('sub', 0.85))) * env * 0.55


def table_wobble(m, dur, p, glide=None, mod=None):
    """Wavetable wobble: the oscillator morphs sine -> triangle -> saw -> square across the note on a slow LFO while
    the filter wobbles on the synced one, wavefolded and driven - an evolving, modern drop bass."""
    f = float(mtof(m))
    env = _env(dur)
    n = len(env)
    fo = f if f > 55 else f * 2
    t = np.arange(n) / SR
    r = _rate(mod, p)
    lfo = _lfo(n, r, p.get('shape', 'sine'))
    pos = 3 * _lfo(n, r / 4, 'tri', _RNG.random())
    out = np.zeros((2, n))
    for side, c in ((0, -7), (1, 7)):
        fr = fo * 2 ** (c / 1200)
        ph = 2 * np.pi * fr * t + _RNG.random() * 6.28
        sw = va.saw(np.full(n, fr), n, _RNG.random())
        waves = (np.sin(ph), 2 / np.pi * np.arcsin(np.sin(ph)), sw, np.sign(np.sin(ph)) * 0.8)
        for k, w in enumerate(waves):
            out[side] += w * np.clip(1 - np.abs(pos - k), 0, 1)
    out += va.pulse(np.full(n, fo * 2), n, 0.2, 0.5)[None, :] * 0.25
    y = va.vcf(out, 160 * (p.get('cut', 3000) / 160) ** lfo, 0.55, 1.5)
    y = dist(dist(y, 1.4, 'fold'), 2.2 + float(p.get('grit', 1.0)))
    y = _split_hp(y, f) * 0.5
    return (y + _sub(f, n, p.get('sub', 0.85))) * env * 0.55


def chop_wobble(m, dur, p, glide=None, mod=None):
    """Chop wobble: a falling saw-shaped LFO slams the filter open and lets it fall on every step ('wub - wub'), the
    volume gated with it, then bit-crushed - the hard, stuttering riddim / brostep wub."""
    f = float(mtof(m))
    env = _env(dur, 0.002, 0.05, 1.0, 0.02)
    n = len(env)
    fo = f if f > 55 else f * 2
    x = _stack(fo, n, 4, 12, 0.5)
    lfo = _lfo(n, _rate(mod, p), p.get('shape', 'saw'))
    y = va.vcf(x, 120 * (p.get('cut', 3200) / 120) ** lfo, 0.5, 1.8)
    y = dist(y, 3.0 + float(p.get('grit', 1.0)), 'hard')
    bits = 2 ** p.get('bits', 6)
    hold = int(p.get('crush', 3))
    y = np.round(y * bits) / bits
    if hold > 1:
        y = np.repeat(y[..., ::hold], hold, axis=-1)[..., :n]
    gate = 0.25 + 0.75 * np.clip(lfo * 1.6, 0, 1)
    y = _split_hp(y, f) * 0.5 * gate
    return (y + _sub(f, n, p.get('sub', 0.85)) * (0.6 + 0.4 * gate)) * env * 0.55


def rumble(m, dur, p, glide=None, mod=None):
    """Techno rumble: the dark, distorted low-end 'roar' between the kicks - a sine at the note with a band of
    low-passed noise around it, driven and filtered so only a growling sub-bass rumble remains (the track's sidechain
    makes it breathe against the kick)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    env = va.adsr(gate, 0.02, 0.4, 0.85, 0.12)
    n = len(env)
    t = np.arange(n) / SR
    nz = _bp(_RNG.standard_normal(n), np.full(n, f * 1.5), 2.0) * 1.8
    x = np.sin(2 * np.pi * f * t) + nz + 0.4 * np.sin(2 * np.pi * f * 2 * t)
    y = dist(x, 3.0)
    b, a = signal.butter(4, min(0.45, p.get('cut', 180) / (SR / 2)))
    y = signal.lfilter(b, a, y)
    return np.vstack([y, y]) * env * 0.5


def dub_stab(m, dur, p, glide=None, mod=None):
    """Dub-techno chord stab: detuned saws + a pulse through a band-limited, resonant filter that snaps shut in a
    tenth of a second - meant to be thrown into a long delay and reverb."""
    f = float(mtof(m))
    gate = int(min(max(dur, 0.05), 0.25) * SR)
    env = va.adsr(gate, 0.002, 0.12, 0.0, 0.08)
    n = len(env)
    t = np.arange(n) / SR
    x = _stack(f, n, 3, 10, 0.5)
    cut = 300 * (p.get('cut', 2600) / 300) ** np.exp(-t * 22)
    y = va.vcf(x, cut, 0.35, 1.2)
    b, a = signal.butter(2, [250 / (SR / 2), 3500 / (SR / 2)], 'band')
    return signal.lfilter(b, a, y, axis=-1) * env * 0.85


def techno_seq(m, dur, p, glide=None, mod=None):
    """Techno sequence: a pulse / saw blip through a resonant filter whose cutoff and decay wander from note to note
    (each step's filter is 'parameter-locked' a little differently), so a repeating line evolves hypnotically."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = va.adsr(gate, 0.002, p.get('d', 0.14), 0.15, 0.06)
    n = len(env)
    t = np.arange(n) / SR
    x = va.pulse(np.full(n, f), n, 0.0, 0.3) * 0.7 + va.saw(np.full(n, f * 1.003), n) * 0.5
    top = p.get('cut', 2400) * 2 ** _RNG.normal(0, 0.45)
    cut = 180 * (top / 180) ** np.exp(-t * _RNG.uniform(9, 22))
    y = va.vcf(x, cut, p.get('res', 0.55), 1.4)
    y = y * env * 0.75
    return np.vstack([y, y])


def dark_pad(m, dur, p, glide=None, mod=None):
    """Techno pad: dark and evolving - detuned saws and a breath of filtered noise under a low, resonant filter that a
    very slow LFO keeps moving, so it drones and morphs instead of shining."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = va.adsr(gate, p.get('a', 1.5), 2.0, 0.9, p.get('r', 2.0))
    n = len(env)
    t = np.arange(n) / SR
    x = _stack(f, n, 4, 14, 0.0) + 0.15 * _bp(_RNG.standard_normal((2, n)), np.full(n, f * 4), 1.5)
    cut = p.get('cut', 650) * 2 ** (1.2 * np.sin(2 * np.pi * 0.06 * t + _RNG.random() * 6.28))
    y = va.vcf(x, cut, 0.35, 1.1)
    return va.juno_chorus(y, 1, 0.3) * env * 1.2


def atmosphere(m, dur, p, glide=None, mod=None):
    """Texture / atmosphere: noise through resonant band-passes tuned to the note's harmonics, each slowly drifting,
    plus a faint sine - a tonal, breathing haze for breakdowns and deep techno."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = va.adsr(gate, p.get('a', 2.0), 2.0, 0.9, p.get('r', 2.5))
    n = len(env)
    t = np.arange(n) / SR
    nz = _RNG.standard_normal((2, n))
    y = np.zeros((2, n))
    for h, g in ((1, 0.6), (2, 1.0), (3, 0.7), (5, 0.45), (8, 0.25)):
        fc = f * h * 2 ** (0.08 * np.sin(2 * np.pi * (0.03 + 0.02 * h) * t + h))
        y += _bp(nz, fc, 40.0) * g
    y = y * 3.0 + 0.08 * np.sin(2 * np.pi * f * t)
    return y * env * 1.5


# ----------------------------------------------------------------------------- 1.69: more dubstep / bass-music basses
def _ott(y, amt=0.6, win=0.01):
    """Upward + downward 'OTT'-style squash: every moment pushed toward the same level (amt 0..1)."""
    k = max(16, int(win * SR))
    env = np.sqrt(np.convolve((y ** 2).mean(axis=0) if y.ndim == 2 else y ** 2, np.ones(k) / k, 'same')) + 1e-6
    tgt = float(np.percentile(env, 90))
    g = (tgt / env) ** amt
    g = np.minimum(g, 6.0)
    return y * g


def _stepped_lfo(n, hz, steps=(0.0, 0.66, 0.33, 1.0), glide=0.25):
    """A stepped LFO (the drawn 'wa-wa-oo-ee' curve): `steps` values per cycle, each step slewing into the next."""
    t = np.arange(n) / SR
    ph = (t * hz) % 1.0
    idx = np.minimum((ph * len(steps)).astype(int), len(steps) - 1)
    v = np.asarray(steps, float)[idx]
    k = max(1, int(glide / max(hz, 0.1) / len(steps) * SR))
    return np.convolve(v, np.ones(k) / k, 'same')


def dark_wobble(m, dur, p, glide=None, mod=None):
    """Smooth dark wobble (deep / dark dubstep): a rounded saw-and-triangle tone through a low, gently resonant 24 dB
    filter that a sine LFO sweeps only from very dark to warm - no fizz, no screech - over a heavy mono sub."""
    f = float(mtof(m))
    env = _env(dur, 0.01, 0.1, 1.0, 0.06)
    n = len(env)
    fo = f if f > 50 else f * 2
    x = _stack(fo, n, 2, 8, 0.0) * 0.6
    x = x + np.vstack([2 / np.pi * np.arcsin(np.sin(2 * np.pi * fo * np.arange(n) / SR))] * 2) * 0.5
    lfo = _lfo(n, _rate(mod, p, 1.0), p.get('shape', 'sine'))
    y = va.vcf(x, 70 * (p.get('cut', 700) / 70) ** lfo, 0.3, 1.2)
    y = dist(y, 1.3)
    y = _split_hp(y, f) * 0.8
    return (y + _sub(f, n, p.get('sub', 1.0))) * env * 0.55


def sub_wobble(m, dur, p, glide=None, mod=None):
    """Sub wobble ('sub wub'): a pure sine sub whose level and a whisper of 2nd harmonic swell on the LFO - the deep,
    felt-not-heard pressure of dark and deep dubstep."""
    f = float(mtof(m))
    env = _env(dur, 0.01, 0.1, 1.0, 0.08)
    n = len(env)
    t = np.arange(n) / SR
    fs = f if f < 70 else f / 2
    lfo = _lfo(n, _rate(mod, p, 1.0), p.get('shape', 'sine'))
    ph = 2 * np.pi * fs * t
    y = np.sin(ph) * (0.55 + 0.45 * lfo) + 0.12 * lfo * np.sin(2 * ph)
    y = np.tanh(y * 1.3)
    return np.vstack([y, y]) * env * 0.6


def fm_growl(m, dur, p, glide=None, mod=None):
    """FM growl (brostep / neuro): a pure sine carrier frequency-modulated by a sine and a square an octave and a
    twelfth up, the FM amount, a +-pitch bend and a moving formant band all driven by one synced LFO (so the sidebands
    'talk'), four detuned voices, multi-band distortion (the low-mids and the top crushed separately), an all-pass
    smear, an OTT squash and more saturation - with a clean sine sub split off underneath. Glides between notes."""
    f = float(mtof(m))
    env = _env(dur, 0.003, 0.08, 1.0, 0.04)
    n = len(env)
    t = np.arange(n) / SR
    fo = (f if f > 55 else f * 2)
    lfo = _lfo(n, _rate(mod, p, 0.5), p.get('shape', 'saw'))
    bend = 2 ** ((p.get('bend', 1.5) * (lfo - 0.5)) / 12)
    if glide is not None:
        g0 = float(mtof(glide)) / f
        bend = bend * (1 + (g0 - 1) * np.exp(-t / 0.05))
    idx = p.get('fm', 1.0) * (1.2 + 3.0 * lfo)
    L = np.zeros(n)
    R = np.zeros(n)
    for k, c in enumerate((-9, -3, 3, 9)):
        fr = fo * bend * 2 ** (c / 1200)
        ph = 2 * np.pi * np.cumsum(fr) / SR + _RNG.random()
        modu = np.sin(2 * ph) + 0.5 * np.sign(np.sin(3 * ph))
        v = np.sin(ph + idx * modu)
        if k % 2:
            R += v
        else:
            L += v
    x = np.vstack([L, R]) * 0.5
    form = _bp(x, 350 + 1600 * lfo, 3.5) * 1.6 + 0.4 * x
    lo = signal.lfilter(*signal.butter(2, 900 / (SR / 2)), form, axis=-1)
    hi = form - lo
    y = dist(lo, 3.0) * 0.7 + dist(hi * 1.5, 4.0, 'hard') * 0.5
    y = y + 0.6 * _bp(y, 1200 + 1800 * (1 - lfo), 1.2)       # the all-pass / phaser-ish smear
    y = _ott(y, 0.55)
    y = dist(y * 0.8, 1.8)
    y = _split_hp(y, f) * 0.42
    return (y + _sub(f, n, p.get('sub', 0.85))) * env * 0.6


def talk_growl(m, dur, p, glide=None, mod=None):
    """Talking growl: an FM / saw tone through a vowel filter that a stepped LFO walks 'wa - oo - ee - ow' (the drawn
    LFO curve of modern growls), the pitch bending with it, clipped hard after the formants - over a clean sub."""
    f = float(mtof(m))
    env = _env(dur, 0.003, 0.08, 1.0, 0.04)
    n = len(env)
    fo = f if f > 55 else f * 2
    rate = _rate(mod, p, 0.5)
    st = _stepped_lfo(n, rate, p.get('steps', (0.1, 0.85, 0.35, 1.0)))
    fr = fo * 2 ** ((st - 0.5) * p.get('bend', 2.0) / 12)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = np.sin(ph + (1.5 + 2.5 * st) * np.sin(2 * ph)) + 0.4 * va.saw(fr, n)
    x = np.vstack([x, np.roll(x, 30)])
    y = _vowel(x, st) * 2.4 + 0.2 * x
    y = dist(y, 3.5, 'hard')
    y = _split_hp(_ott(y, 0.5), f) * 0.42
    return (y + _sub(f, n, p.get('sub', 0.85))) * env * 0.6


def metal_bass(m, dur, p, glide=None, mod=None):
    """Metallic neuro bass: an FM tone through a resonant comb (a hollow, ringing metal tube tuned to the note) whose
    feedback moves with the LFO, then hard-clipped and OTT-squashed - the cold, mechanical neurofunk bass."""
    f = float(mtof(m))
    env = _env(dur, 0.003, 0.08, 1.0, 0.04)
    n = len(env)
    fo = f if f > 55 else f * 2
    t = np.arange(n) / SR
    lfo = _lfo(n, _rate(mod, p, 0.25), p.get('shape', 'square'))
    ph = 2 * np.pi * fo * t
    x = np.sin(ph + (2.0 + 3.0 * lfo) * np.sin(ph * 1.5)) + 0.3 * va.saw(np.full(n, fo * 1.003), n)
    d = max(2, int(round(SR / (fo * 2))))
    y = x.copy()
    for _ in range(3):                                   # a short comb with LFO-moved feedback
        y[d:] = y[d:] + (0.45 + 0.4 * lfo[d:]) * y[:-d]
    y = y / (np.abs(y).max() + 1e-9)
    y = dist(np.vstack([y, np.roll(y, 25)]) * 2.0, 3.0, 'hard')
    y = _split_hp(_ott(y, 0.5), f) * 0.42
    return (y + _sub(f, n, p.get('sub', 0.8))) * env * 0.6


def fuzz_bass(m, dur, p, glide=None, mod=None):
    """Fuzzy filter bass (the late-90s French / electro rubbery bass): one analog saw into a screaming 12 dB
    Sallen-Key-style low-pass and high-pass pair, the cutoff pushed by the envelope and wobbled slowly by hand, the
    resonance overdriven into a fuzzy 'quack', glide between notes."""
    f = float(mtof(m))
    env = _env(dur, 0.004, 0.2, 0.9, 0.05)
    n = len(env)
    t = np.arange(n) / SR
    fr = np.full(n, f) if glide is None else f + (float(mtof(glide)) - f) * np.exp(-t / 0.06)
    x = va.saw(fr * 2 ** (np.sin(2 * np.pi * 0.3 * t) * 4 / 1200), n)
    wob = 0.5 - 0.5 * np.cos(2 * np.pi * p.get('wob', 0.9) * t + _RNG.random() * 6.28)
    cut = p.get('cut', 420) * (1 + 2.2 * np.exp(-t / 0.15)) * (0.7 + 0.9 * wob)
    y = va.vcf(x, cut, p.get('res', 0.7), 2.2)
    y = dist(y * 1.8, 2.5)
    b, a = signal.butter(1, 45 / (SR / 2), 'high')
    y = signal.lfilter(b, a, y)
    y = y + 0.4 * np.sin(2 * np.pi * np.cumsum(fr) / SR)
    return np.vstack([y, y]) * env * 0.55
