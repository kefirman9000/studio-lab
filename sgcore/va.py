"""The built-in analog synth (1.57): one virtual-analog voice that the classic synth sounds are built from.

    oscillators   band-limited saw / pulse (PolyBLEP), a sub-oscillator an octave down, noise; pulse-width
                  modulation; up to 9 unison voices spread in pitch and across the stereo field, each starting at
                  a random phase (like a real poly synth's free-running oscillators); slow analog pitch drift
    filter        a resonant 24 dB/oct low-pass (two state-variable stages, the first one resonant), driven into
                  soft saturation, with its own envelope (attack / decay / sustain) and key tracking
    amp           ADSR envelope; velocity
    character     a gentle tanh drive, and the Juno-style stereo chorus in render.chorus for the pads

Everything is vectorised NumPy except the filter, which runs in short blocks with its state carried over, so the
cutoff can move smoothly through a note (a pluck closing, a pad slowly opening).
"""
import numpy as np
from scipy import signal

from .dsp import SR, mtof

_RNG = np.random.default_rng(57)


def _blep(t, dt):
    """PolyBLEP residual for a phase t in [0, 1) advancing dt per sample."""
    out = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    out[m] = x + x - x * x - 1.0
    m2 = t > 1.0 - dt
    x = (t[m2] - 1.0) / dt[m2]
    out[m2] = x * x + x + x + 1.0
    return out


def _phase(freq, n, ph0):
    dt = np.broadcast_to(np.asarray(freq, float) / SR, (n,)).copy()
    ph = (ph0 + np.concatenate([[0.0], np.cumsum(dt[:-1])])) % 1.0
    return ph, np.clip(dt, 1e-6, 0.5)


def saw(freq, n, ph0=0.0):
    p, dt = _phase(freq, n, ph0)
    return 2.0 * p - 1.0 - _blep(p, dt)


def pulse(freq, n, ph0=0.0, pw=0.5):
    p, dt = _phase(freq, n, ph0)
    pw = np.broadcast_to(np.asarray(pw, float), (n,))
    s = np.where(p < pw, 1.0, -1.0)
    s += _blep(p, dt)
    s -= _blep((p + 1.0 - pw) % 1.0, dt)
    return s


def adsr(n_gate, a, d, s, r, curve=4.0):
    """Analog-style envelope: a slightly curved attack, exponential decay and release. Length gate + release."""
    a, d, r = max(1, int(a * SR)), max(1, int(d * SR)), max(1, int(r * SR))
    g = max(1, int(n_gate))
    t = np.arange(g, dtype=float)
    att = 1.0 - np.exp(-curve * np.minimum(t / a, 1.0)) / 1.0
    att = att / (1.0 - np.exp(-curve))
    dec = s + (1.0 - s) * np.exp(-np.maximum(t - a, 0.0) * 5.0 / d)
    env = np.where(t < a, att, dec)
    last = env[-1]
    rel = last * np.exp(-np.arange(r, dtype=float) * 5.0 / r)
    return np.concatenate([env, rel])


def _biquad_lp(fc, q):
    w = 2 * np.pi * fc / SR
    al = np.sin(w) / (2 * q)
    cw = np.cos(w)
    b = np.array([(1 - cw) / 2, 1 - cw, (1 - cw) / 2]) / (1 + al)
    a = np.array([1.0, -2 * cw / (1 + al), (1 - al) / (1 + al)])
    return b, a


def vcf(x, cut, res=0.2, drive=1.2, block=96):
    """Resonant 24 dB/oct low-pass with a moving cutoff `cut` (Hz, array or number). res 0..1 (self-oscillation ~1).
    Driven into soft saturation before the filter, like an analog VCF's input stage."""
    x = np.tanh(np.asarray(x, float) * drive) / np.tanh(drive)
    n = x.shape[-1]
    cut = np.broadcast_to(np.asarray(cut, float), (n,))
    q1 = 0.55 + 6.0 * float(res) ** 1.6
    chans = x if x.ndim == 2 else x[None, :]
    out = np.empty_like(chans)
    for c in range(chans.shape[0]):
        z1, z2 = np.zeros(2), np.zeros(2)
        for s in range(0, n, block):
            e = min(n, s + block)
            fc = float(np.clip(cut[s], 25.0, SR * 0.42))
            b1, a1 = _biquad_lp(fc, q1)
            b2, a2 = _biquad_lp(fc, 0.54)
            y, z1 = signal.lfilter(b1, a1, chans[c, s:e], zi=z1)
            out[c, s:e], z2 = signal.lfilter(b2, a2, y, zi=z2)
    out *= 1.0 / (1.0 + 0.35 * float(res))                  # resonance thins the body: make up a little level
    return out if x.ndim == 2 else out[0]


def voice(m, dur, p, glide=None, *, saw_mix=1.0, pulse_mix=0.0, sub=0.0, noise=0.0, pw=0.5, pwm=0.0, pwm_rate=0.6,
          unison=1, detune=12.0, spread=0.6, drift=3.0, cut=2000.0, res=0.2, fenv=0.0, fa=0.003, fd=0.3, fs=0.0,
          keytrack=0.5, amp=(0.005, 0.3, 0.8, 0.3), drive=1.2, vib=0.0, vib_rate=5.2, vib_delay=0.25, slide=0.06,
          octave=0, hp=0.0, stereo=True):
    """One synth note -> stereo array. Every knob has the meaning it has on a hardware poly synth; `p` (the track's
    params) can override cut / a / d / s / r / res / detune / fd / fenv like the old instruments did."""
    a_, d_, s_, r_ = amp
    a_, d_, s_, r_ = p.get('a', a_), p.get('d', d_), p.get('s', s_), p.get('r', r_)
    cut = p.get('cut', cut)
    res = p.get('res', res)
    detune = detune * p.get('detune', 1.0)
    fd = p.get('fdecay_s', fd)
    fenv = p.get('fenv', fenv)
    gate = int(max(dur, 0.01) * SR)
    env = adsr(gate, a_, d_, s_, r_)
    n = len(env)
    t = np.arange(n) / SR
    f = float(mtof(m + 12 * octave))
    fr = np.full(n, f)
    if glide is not None:
        f0 = float(mtof(glide + 12 * octave))
        fr = f + (f0 - f) * np.exp(-t / max(0.005, slide))
    if vib:
        dep = np.clip((t - vib_delay) / 0.35, 0, 1) * vib
        fr = fr * 2 ** (dep * np.sin(2 * np.pi * vib_rate * t) / 1200)
    if drift:
        wob = np.sin(2 * np.pi * (0.13 + 0.07 * _RNG.random()) * t + _RNG.random() * 6.28)
        fr = fr * 2 ** (drift * wob / 1200)
    nv = max(1, int(unison))
    L = np.zeros(n)
    R = np.zeros(n)
    pwv = pw + pwm * 0.45 * np.sin(2 * np.pi * pwm_rate * t) if pwm else pw
    for k in range(nv):
        off = 0.0 if nv == 1 else (k / (nv - 1) - 0.5) * 2.0       # -1 .. 1
        cents = off * detune
        fk = fr * 2 ** (cents / 1200)
        ph = _RNG.random()
        osc = saw(fk, n, ph) * saw_mix if saw_mix else np.zeros(n)
        if pulse_mix:
            osc = osc + pulse(fk, n, (ph + 0.37) % 1.0, pwv) * pulse_mix
        pan = 0.5 + 0.5 * off * spread if (stereo and nv > 1) else 0.5
        L += osc * np.cos(pan * np.pi / 2)
        R += osc * np.sin(pan * np.pi / 2)
    g = 1.0 / np.sqrt(nv)
    L *= g * np.sqrt(2)
    R *= g * np.sqrt(2)
    if sub:
        so = pulse(fr / 2, n, 0.0, 0.5) * sub
        L += so
        R += so
    if noise:
        nz = _RNG.standard_normal(n) * noise * 0.3
        L += nz
        R += nz
    # filter: cutoff = base (key-tracked) + envelope amount (in octaves)
    kt = (f / 261.6) ** keytrack
    fe = adsr(gate, fa, fd, fs, max(0.05, r_)) if fenv else np.zeros(n)
    cutoff = np.clip(cut * kt * 2 ** (fenv * fe[:n]), 25.0, SR * 0.42)
    y = vcf(np.vstack([L, R]), cutoff, res, drive)
    if hp:
        bh, ah = signal.butter(2, hp / (SR / 2), 'high')
        y = signal.lfilter(bh, ah, y, axis=-1)
    y = y * env
    return y.astype(np.float64)


def fm_epiano(m, dur, p, glide=None):
    """DX7-style electric piano (the classic 'E.PIANO 1' structure): two operator pairs - a 1:1 pair for the warm body
    and a 1:14 pair for the bright 'tine' bark that rings only in the attack; harder notes bark more; a little detune
    between the pairs for the chorus-y shimmer, and a slow tremolo."""
    vel = p.get('vel', 0.8)
    f = float(mtof(m))
    dur_ = max(dur, 0.05)
    n = int((min(dur_, 6.0) + p.get('r', 0.6)) * SR)
    t = np.arange(n) / SR
    decay = p.get('decay', 1.1) * (0.7 + 0.6 * (f / 440.0) ** 0.3)
    body_i = (1.4 + 1.6 * vel) * np.exp(-t * 2.2)
    body = np.sin(2 * np.pi * f * t + body_i * np.sin(2 * np.pi * f * t))
    tine_i = (2.2 + 3.0 * vel) * np.exp(-t * 18.0)
    tine = np.sin(2 * np.pi * f * 1.003 * t + tine_i * np.sin(2 * np.pi * f * 14.0 * t))
    y = (body * np.exp(-t * decay) + 0.45 * tine * np.exp(-t * (decay * 1.8 + 1.5)))
    gate = int(dur_ * SR)
    if gate < n:
        y[gate:] *= np.exp(-np.arange(n - gate) / (0.08 * SR))
    y *= np.minimum(t / 0.0015, 1)
    trem = 0.1 * np.sin(2 * np.pi * p.get('trem', 4.5) * t)
    return np.vstack([y * (1 + trem), y * (1 - trem)]) * 0.5


def fm_bell(m, dur, p, glide=None):
    """FM bell / glock: inharmonic 1 : 3.5 pair plus a 1 : 1.414 shimmer, a bright strike and a long ring."""
    f = float(mtof(m))
    n = int((dur + p.get('ring', 1.6)) * SR)
    t = np.arange(n) / SR
    i1 = p.get('index', 2.4) * np.exp(-t * 2.2)
    y = np.sin(2 * np.pi * f * t + i1 * np.sin(2 * np.pi * f * p.get('ratio', 3.5) * t))
    y += 0.35 * np.sin(2 * np.pi * f * 2.0 * t + 1.2 * np.exp(-t * 4) * np.sin(2 * np.pi * f * 1.414 * t)) * np.exp(-t * 2.5)
    y *= np.exp(-t * p.get('decay', 1.5)) * np.minimum(t / 0.0015, 1)
    k = min(n, int(0.05 * SR))
    y[-k:] *= np.linspace(1, 0, k)
    return np.vstack([y, np.roll(y, 60)]) * 0.55
