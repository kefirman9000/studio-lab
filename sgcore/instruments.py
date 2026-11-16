"""Built-in instruments: melodic synths, drum machine and FX - all synthesized from scratch."""
import numpy as np
from scipy import signal
from . import dsp
from .dsp import (SR, mtof, lp, hp, bp, eq, soft, noise, fade_out, adsr, saw, square, sine, tri,
                  filt_env, vibrato, svf_sweep)


def _rng():
    return dsp.get_rng()


def i_sawbass(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.003, p.get('d', 0.18), p.get('s', 0.6), 0.05)
    n = len(env)
    t = np.arange(n) / SR
    x = 0.7 * saw(f, n) + 0.6 * sine(f, n)
    y = filt_env(x, 160, p.get('cut', 2200), np.exp(-t * p.get('fdecay', 16)))
    return soft(y * env, 1.6)


def i_reese(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.01, 0.3, 0.9, 0.1)
    n = len(env)
    t = np.arange(n) / SR
    L = saw(f * 0.993, n) + saw(f * 1.004, n, 0.3)
    R = saw(f * 1.007, n, 0.6) + saw(f * 0.996, n, 0.1)
    wob = 0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t)
    cut = p.get('cut', 900)
    L = filt_env(L, cut * 0.5, cut * 1.6, wob)
    R = filt_env(R, cut * 0.5, cut * 1.6, 1 - wob)
    sub = sine(f, n) * 1.2
    out = np.vstack([soft(L * 0.5, 2.0) + sub, soft(R * 0.5, 2.0) + sub]) * env
    return out


def i_808(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    gate = int(dur * SR)
    n = gate + int(0.04 * SR)
    t = np.arange(n) / SR
    if glide is not None:
        f0 = float(mtof(glide))
        freq = f + (f0 - f) * np.exp(-t / 0.06)
    else:
        freq = np.full(n, f)
    y = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    amp = np.exp(-t * p.get('decay', 0.9)) * np.minimum(t / 0.002, 1)
    rel = np.ones(n)
    rel[gate:] = np.linspace(1, 0, n - gate)
    return soft(y * amp * rel, p.get('drive', 2.4))


def i_sinebass(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.006, 0.5, 0.75, 0.08)
    n = len(env)
    x = sine(f, n) + 0.12 * tri(f * 2, n)
    return lp(soft(x * env, 1.4), p.get('cut', 700))


def i_chipbass(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    gate = int(dur * SR)
    n = gate + int(0.02 * SR)
    x = np.round(tri(f, n) * 7.5) / 7.5
    e = np.ones(n)
    e[gate:] = np.linspace(1, 0, n - gate)
    return x * e


def i_supersaw(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.25), 0.6, 0.85, p.get('r', 0.6))
    n = len(env)
    cents = np.array([-20, -12, -5, 0, 5, 12, 20]) * p.get('detune', 1.0)
    L = np.zeros(n)
    R = np.zeros(n)
    for i, c in enumerate(cents):
        s = saw(f * 2 ** (c / 1200), n, _rng().random())
        th = (i / (len(cents) - 1)) * np.pi / 2
        L += s * np.cos(th)
        R += s * np.sin(th)
    out = lp(np.vstack([L, R]), p.get('cut', 3000))
    return out * env / len(cents) * 1.6


def i_warmpad(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 1.2), 1.0, 0.85, p.get('r', 2.0))
    n = len(env)
    a = saw(f * 2 ** (-7 / 1200), n, _rng().random()) + 0.5 * tri(f, n)
    b = saw(f * 2 ** (7 / 1200), n, _rng().random()) + 0.5 * tri(f * 1.001, n)
    out = lp(np.vstack([a, b]), p.get('cut', 1100))
    return out * env * 0.5


def i_stab(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.002, p.get('d', 0.22), p.get('s', 0.2), 0.08)
    n = len(env)
    t = np.arange(n) / SR
    x = saw(f * 1.003, n) + saw(f * 0.997, n, 0.5) + 0.4 * square(f, n)
    y = filt_env(x, 250, p.get('cut', 5000), np.exp(-t * p.get('fdecay', 20)))
    return y * env * 0.5


def i_pluck_saw(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.002, p.get('d', 0.3), p.get('s', 0.15), 0.12)
    n = len(env)
    t = np.arange(n) / SR
    x = saw(f, n) + 0.5 * square(f * 1.004, n)
    y = filt_env(x, 300, p.get('cut', 6000), np.exp(-t * p.get('fdecay', 14)))
    return y * env * 0.6


def i_epiano(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    gate = int(dur * SR)
    n = gate + int(0.35 * SR)
    t = np.arange(n) / SR
    idx = 1.4 * np.exp(-t * 4) + 0.25
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    if f * 14 < 16000:
        y += 0.12 * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t * 30)
    amp = np.exp(-t * p.get('decay', 1.1))
    amp[gate:] *= np.exp(-np.arange(n - gate) / (0.08 * SR))
    y *= amp * np.minimum(t / 0.002, 1)
    trem = 0.18 * np.sin(2 * np.pi * 4.2 * t)
    return np.vstack([y * (1 + trem), y * (1 - trem)]) * 0.6


def i_pluck(m, dur, p, glide=None, mod=None):
    """Karplus-Strong plucked string."""
    f = float(mtof(m))
    N = max(2, int(round(SR / f - 0.5)))
    f_real = SR / (N + 0.5)
    total = min(dur + p.get('r', 0.4), 4.0)
    n = int(total * SR)
    ratio = f / f_real
    n_gen = int(n * ratio) + 4
    exc = np.zeros(n_gen)
    burst = lp(_rng().uniform(-1, 1, N), p.get('bright', 5000))
    exc[:N] = burst
    damp = p.get('damp', 0.996)
    a = np.zeros(N + 2)
    a[0] = 1.0
    a[N] -= damp * 0.5
    a[N + 1] -= damp * 0.5
    y = signal.lfilter([1.0], a, exc)
    y = np.interp(np.arange(n) * ratio, np.arange(n_gen), y)
    gate = int(dur * SR)
    if gate < n:
        rel = int(0.12 * SR)
        e = np.ones(n)
        e[gate:gate + rel] = np.linspace(1, 0, len(e[gate:gate + rel]))
        e[gate + rel:] = 0
        y *= e
    return y


def i_bell(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    n = int((dur + p.get('ring', 1.4)) * SR)
    t = np.arange(n) / SR
    idx = p.get('index', 2.2) * np.exp(-t * 2.5)
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * p.get('ratio', 3.5) * t))
    y *= np.exp(-t * p.get('decay', 1.6)) * np.minimum(t / 0.002, 1)
    return fade_out(y, 0.05) * 0.7


def i_leadsaw(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.008, 0.3, 0.7, 0.18)
    n = len(env)
    t = np.arange(n) / SR
    fv = vibrato(f, n, cents=p.get('vib', 14))
    x = saw(fv * 2 ** (6 / 1200), n) + saw(fv * 2 ** (-6 / 1200), n, 0.4) + 0.4 * square(fv / 2, n)
    cut = p.get('cut', 5000)
    y = filt_env(x, cut * 0.35, cut, np.exp(-t * 5) * 0.6 + 0.4)
    return y * env * 0.4


def i_softlead(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.07, 0.5, 0.8, 0.5)
    n = len(env)
    fv = vibrato(f, n, rate=4.8, cents=10, delay=0.3)
    x = tri(fv, n) + 0.5 * sine(fv * 2, n) + 0.08 * saw(fv, n)
    return lp(x, p.get('cut', 3000)) * env * 0.6


def i_chip(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.002, p.get('d', 0.25), p.get('s', 0.6), 0.03)
    n = len(env)
    fv = vibrato(f, n, rate=6, cents=p.get('vib', 20), delay=0.15)
    x = square(fv, n, pw=p.get('pw', 0.5))
    frames = (np.floor(np.arange(n) / (SR / 60)) * (SR / 60)).astype(int)
    envq = np.round(env[np.minimum(frames, n - 1)] * 15) / 15
    return x * envq * 0.5




# =============================================================================
#  Drum machine
# =============================================================================

def _metallic(n, scale=1.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for fr in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0):
        out += np.sign(np.sin(2 * np.pi * fr * scale * t + _rng().random() * 6.28))
    return out / 6


def _chipnoise(n, rate):
    hold = max(1, int(SR / rate))
    v = _rng().choice([-1.0, 1.0], size=n // hold + 1)
    return np.repeat(v, hold)[:n]


def d_kick(p):
    n = int(p.get('len', 0.5) * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 48) + p.get('punch', 120) * np.exp(-t * p.get('sweep', 40))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * p.get('decay', 7))
    click = bp(noise(n), 1500, 7000) * np.exp(-t * 300) * p.get('click', 0.3)
    return fade_out(soft(body + click, p.get('drive', 1.6)), 0.02)


def d_snare(p):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    tf = p.get('tone', 185)
    tone = (np.sin(2 * np.pi * tf * t) * 0.6 + np.sin(2 * np.pi * tf * 1.8 * t) * 0.3) * np.exp(-t * 28)
    nz = bp(noise(n), 1200, 9000) * np.exp(-t * p.get('decay', 16))
    return fade_out(soft(tone * p.get('body', 0.7) + nz * p.get('snap', 0.9), 1.3), 0.02)


def d_clap(p):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    nz = bp(noise(n), 900, 4200)
    env = np.zeros(n)
    for k, o in enumerate((0.0, 0.009, 0.018, 0.027)):
        on = t >= o
        env[on] += np.exp(-(t[on] - o) * (220 if k < 3 else p.get('tail', 13)))
    return fade_out(nz * env, 0.02)


def d_chat(p):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = hp(0.6 * _metallic(n) + 0.5 * noise(n), 7000)
    return fade_out(x * np.exp(-t * p.get('decay', 70)), 0.01)


def d_ohat(p):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    x = hp(0.6 * _metallic(n) + 0.5 * noise(n), 6500)
    return fade_out(x * np.exp(-t * p.get('decay', 8)), 0.05)


def d_shaker(p):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    env = (1 - np.exp(-t * 250)) * np.exp(-t * 45)
    return fade_out(bp(noise(n), 4000, 13000) * env, 0.01)


def d_ride(p):
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    x = hp(0.7 * _metallic(n, 2.3) + 0.3 * noise(n), 5000)
    x += 0.15 * np.sin(2 * np.pi * 3150 * t) * np.exp(-t * 5)
    return fade_out(x * np.exp(-t * 3.5), 0.1)


def d_rim(p):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 120) + 0.5 * bp(noise(n), 2000, 6000) * np.exp(-t * 200)
    return fade_out(x, 0.01)


def d_crash(p):
    n = int(2.8 * SR)
    t = np.arange(n) / SR
    x = hp(noise(n), 3000) + 0.5 * hp(_metallic(n, 1.7), 5000)
    return fade_out(x * np.exp(-t * 1.5) * np.minimum(t / 0.003, 1), 0.2)


def d_chipkick(p):
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = 45 + 180 * np.exp(-t * 35)
    return square(f, n) * np.exp(-t * 18) * 0.8


def d_chipsnare(p):
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    return _chipnoise(n, 9000) * np.exp(-t * 20) * 0.7


def d_chiphat(p):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return _chipnoise(n, 30000) * np.exp(-t * 90) * 0.5




# =============================================================================
#  FX
# =============================================================================

def fx_riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    w = t / dur
    x = noise(n)
    y = bp(x, 200, 1000) * (1 - w) ** 2 + bp(x, 1000, 4500) * 2 * w * (1 - w) + hp(x, 4500) * w ** 2
    f = 120 * (10 ** (w * 1.1))
    y += 0.25 * lp(saw(f, n), 3500)
    return y * w ** 2.2


def fx_impact():
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    f = 30 + 70 * np.exp(-t * 3)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    y += 0.5 * lp(noise(n), 400) * np.exp(-t * 6)
    return fade_out(soft(y, 1.5), 0.2)


def fx_vinyl(n):
    crackle = np.zeros(n)
    hits = _rng().random(n) < 0.00035
    crackle[hits] = _rng().standard_normal(hits.sum()) * _rng().random(hits.sum())
    crackle = bp(crackle, 900, 7000) * 3
    hiss = lp(noise(n), 5000) * 0.04
    return crackle + hiss


def fx_texture(n):
    t = np.arange(n) / SR
    x = bp(noise(n), 250, 1800)
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * t / 17.0) * np.sin(2 * np.pi * t / 7.3 + 1)
    return x * swell




# =============================================================================
#  Additional instruments
# =============================================================================

def i_acid(m, dur, p, glide=None, mod=None):
    """TB-303 style: saw/square through a resonant low-pass with envelope, accent and slide."""
    f = float(mtof(m))
    gate = int(dur * SR)
    n = gate + int(0.03 * SR)
    t = np.arange(n) / SR
    if glide is not None:
        f0 = float(mtof(glide))
        freq = f + (f0 - f) * np.exp(-t / 0.045)
    else:
        freq = np.full(n, f)
    x = saw(freq, n) if p.get('wave', 'saw') == 'saw' else square(freq, n)
    acc = 1.0 if mod else 0.0
    base = p.get('cut', 380)
    envmod = p.get('envmod', 6.0) * (1.6 if acc else 1.0)
    cut = base * (1 + envmod * np.exp(-t * (14 if acc else 9)))
    y = svf_sweep(x, cut, q=p.get('res', 7.0) * (1.3 if acc else 1.0))
    amp = np.ones(n)
    if glide is None:
        amp *= np.minimum(t / 0.003, 1)
    amp[gate:] *= np.linspace(1, 0, n - gate)
    return soft(y * amp * (1.3 if acc else 0.9), 1.6) * 0.6


def i_wobble(m, dur, p, glide=None, mod=None):
    """Dubstep wobble: detuned saws through an LFO-swept resonant filter, clean sub underneath."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.005, 0.1, 1.0, 0.05)
    n = len(env)
    t = np.arange(n) / SR
    rate_beats = mod or 0.5
    hz = 1.0 / (rate_beats * p.get('spb', 0.43))
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * hz * t)
    x = saw(f * 1.004, n) + saw(f * 0.996, n, 0.3) + 0.6 * square(f * 2, n, 0.1)
    cut = 120 + p.get('cut', 2600) * lfo ** 1.5
    y = svf_sweep(x, cut, q=4.0)
    y = soft(y * 2.5, 2.0) * 0.5
    sub = sine(f / 2 if f > 70 else f, n) * 0.8
    return (y + sub) * env


def i_fmbass(m, dur, p, glide=None, mod=None):
    """Gritty FM bass for electro / big room / riddim."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.003, 0.25, 0.7, 0.06)
    n = len(env)
    t = np.arange(n) / SR
    idx = p.get('index', 3.0) * (0.4 + 0.6 * np.exp(-t * 6))
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * p.get('ratio', 1.0) * t))
    y = soft(y * p.get('drive', 2.5), 2.0)
    return lp(y, p.get('cut', 3500)) * env


def i_organ(m, dur, p, glide=None, mod=None):
    """Drawbar organ with key-click percussion and rotary-style stereo tremolo."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.004, 0.05, 1.0, 0.05)
    n = len(env)
    t = np.arange(n) / SR
    bars = p.get('bars', [(0.5, 0.6), (1, 1.0), (2, 0.7), (3, 0.4), (4, 0.35), (6, 0.15)])
    y = np.zeros(n)
    for ratio, amp in bars:
        if f * ratio < 15000:
            y += amp * np.sin(2 * np.pi * f * ratio * t + _rng().random() * 6.28)
    y += 0.35 * np.sin(2 * np.pi * f * 3 * t) * np.exp(-t * 12)
    y *= env * 0.25
    rot = 0.2 * np.sin(2 * np.pi * p.get('leslie', 5.8) * t)
    return np.vstack([y * (1 + rot), y * (1 - rot)])


def i_piano(m, dur, p, glide=None, mod=None):
    """Additive piano with stretched (inharmonic) partials, hammer noise and damper."""
    f = float(mtof(m))
    gate = int(dur * SR)
    ring = min(dur + 1.2, 5.0)
    n = int(ring * SR)
    t = np.arange(n) / SR
    B = 0.0004
    y = np.zeros(n)
    for k in range(1, 13):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > 16000:
            break
        y += (1.0 / k ** 1.15) * np.sin(2 * np.pi * fk * t) * np.exp(-t * (0.6 + 0.45 * k) * (f / 260) ** 0.4)
    y += 0.08 * bp(noise(n), 1000, 5000) * np.exp(-t * 60)
    damp = np.ones(n)
    if gate < n:
        damp[gate:] = np.exp(-np.arange(n - gate) / (0.09 * SR))
    y *= damp * np.minimum(t / 0.0015, 1) * 0.35
    pan = np.clip((m - 60) / 40, -0.6, 0.6)
    return np.vstack([y * (1 - pan * 0.5), y * (1 + pan * 0.5)])


def i_guitar(m, dur, p, glide=None, mod=None):
    """Plucked electric guitar (Karplus-Strong + pickup/cab filtering)."""
    y = i_pluck(m, dur, dict(bright=p.get('bright', 6500), damp=p.get('damp', 0.997), r=0.15))
    y = eq(y, 'peak', 2400, 1.0, 4.0)
    if p.get('dist'):
        y = lp(soft(y * p['dist'], 3.0), 4800)
    return y * 0.7


def i_brass(m, dur, p, glide=None, mod=None):
    """Synth brass section: detuned saws with a swelling filter."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.025, 0.25, 0.8, 0.15)
    n = len(env)
    t = np.arange(n) / SR
    fv = vibrato(f, n, rate=5.2, cents=8, delay=0.25)
    x = saw(fv * 1.003, n) + saw(fv * 0.997, n, 0.4) + 0.5 * saw(fv * 2.001, n, 0.7)
    fe = np.clip(t / 0.06, 0, 1) * (0.75 + 0.25 * np.exp(-t * 6))
    y = filt_env(x, 350, p.get('cut', 3800), fe)
    return y * env * 0.35


def i_strings(m, dur, p, glide=None, mod=None):
    """String ensemble: many detuned saws with vibrato and slow attack."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.35), 0.5, 0.9, p.get('r', 0.7))
    n = len(env)
    L = np.zeros(n)
    Rt = np.zeros(n)
    for i, c in enumerate((-14, -6, 0, 6, 14)):
        fv = vibrato(f * 2 ** (c / 1200), n, rate=4.5 + i * 0.37, cents=7, delay=0.1)
        s = saw(fv, n, _rng().random())
        th = i / 4 * np.pi / 2
        L += s * np.cos(th)
        Rt += s * np.sin(th)
    out = hp(lp(np.vstack([L, Rt]), p.get('cut', 3200)), 180)
    return out * env * 0.3


VOWELS = {'a': (800, 1150, 2900), 'o': (450, 800, 2830), 'e': (400, 1700, 2600),
          'i': (300, 2300, 3000), 'u': (325, 700, 2530)}


def i_vox(m, dur, p, glide=None, mod=None):
    """Synthetic vocal chop: pulse + breath through formant filters."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.012, 0.15, 0.75, 0.08)
    n = len(env)
    fv = vibrato(f, n, rate=5.5, cents=18, delay=0.15)
    src = saw(fv, n) + 0.15 * noise(n)
    vowel = p.get('vowel') or 'aoeiu'[int(m) % 5]
    f1, f2, f3 = VOWELS.get(vowel, VOWELS['a'])
    y = 1.0 * bp(src, f1 * 0.8, f1 * 1.2) + 0.6 * bp(src, f2 * 0.85, f2 * 1.15) + 0.3 * bp(src, f3 * 0.9, f3 * 1.1)
    return y * env * 1.4


def i_cowbell(m, dur, p, glide=None, mod=None):
    """Pitched 808-style cowbell (phonk melodies)."""
    f = float(mtof(m))
    n = int(min(dur + 0.4, 1.5) * SR)
    t = np.arange(n) / SR
    x = square(f, n) + square(f * 1.48, n, 0.3)
    y = bp(x, f * 0.9, f * 4) * (0.7 * np.exp(-t * 18) + 0.3 * np.exp(-t * 5))
    return fade_out(y, 0.03) * 0.6


def i_hoover(m, dur, p, glide=None, mod=None):
    """Rave 'hoover': detuned supersaw with a downward pitch scoop."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.01, 0.3, 0.85, 0.2)
    n = len(env)
    t = np.arange(n) / SR
    bend = 2 ** ((-5 * np.exp(-t * 18)) / 12)
    L = np.zeros(n)
    Rt = np.zeros(n)
    for i, c in enumerate((-25, -10, 0, 10, 25)):
        s = saw(f * bend * 2 ** (c / 1200), n, _rng().random()) + 0.5 * square(f * bend * 0.5 * 2 ** (c / 1200), n, pw=0.3)
        th = i / 4 * np.pi / 2
        L += s * np.cos(th)
        Rt += s * np.sin(th)
    out = lp(np.vstack([L, Rt]), p.get('cut', 4500))
    return out * env * 0.25


def i_supersaw_lead(m, dur, p, glide=None, mod=None):
    return i_supersaw(m, dur, dict(cut=p.get('cut', 7000), a=0.005, r=0.2, detune=p.get('detune', 1.3)))


INSTRUMENTS = {
    'sawbass': i_sawbass, 'reese': i_reese, '808': i_808, 'sinebass': i_sinebass, 'chipbass': i_chipbass,
    'acid': i_acid, 'wobble': i_wobble, 'fmbass': i_fmbass,
    'supersaw': i_supersaw, 'warmpad': i_warmpad, 'strings': i_strings,
    'stab': i_stab, 'pluck_saw': i_pluck_saw, 'epiano': i_epiano, 'piano': i_piano, 'organ': i_organ,
    'pluck': i_pluck, 'guitar': i_guitar, 'bell': i_bell, 'brass': i_brass, 'vox': i_vox, 'cowbell': i_cowbell,
    'leadsaw': i_leadsaw, 'softlead': i_softlead, 'chip': i_chip, 'hoover': i_hoover, 'supersaw_lead': i_supersaw_lead,
}

INSTRUMENT_INFO = {
    'sawbass': 'Saw bass (filter pluck)', 'reese': 'Reese bass (DnB growl)', '808': '808 sub (gliding)',
    'sinebass': 'Warm sine bass', 'chipbass': '8-bit triangle bass', 'acid': 'Acid 303 bass', 'wobble': 'Dubstep wobble bass',
    'fmbass': 'FM grit bass', 'supersaw': 'Supersaw chords', 'warmpad': 'Warm analog pad', 'strings': 'String ensemble',
    'stab': 'Chord stab', 'pluck_saw': 'Saw pluck', 'epiano': 'Electric piano (Rhodes)', 'piano': 'Acoustic piano',
    'organ': 'Drawbar organ', 'pluck': 'Plucked string', 'guitar': 'Electric guitar', 'bell': 'FM bell',
    'brass': 'Synth brass', 'vox': 'Vocal chop', 'cowbell': 'Pitched cowbell', 'leadsaw': 'Saw lead',
    'softlead': 'Soft flute-like lead', 'chip': '8-bit pulse', 'hoover': 'Rave hoover', 'supersaw_lead': 'Supersaw lead',
}

ROLE_CHOICES = {
    'bass': ['sawbass', 'reese', '808', 'sinebass', 'acid', 'wobble', 'fmbass', 'chipbass', 'pluck'],
    'chords': ['stab', 'supersaw', 'epiano', 'piano', 'organ', 'pluck', 'guitar', 'strings', 'brass', 'pluck_saw', 'warmpad', 'bell', 'chip'],
    'pad': ['supersaw', 'warmpad', 'strings', 'organ', 'vox'],
    'arp': ['pluck_saw', 'bell', 'pluck', 'chip', 'epiano', 'piano', 'acid', 'supersaw_lead'],
    'lead': ['leadsaw', 'supersaw_lead', 'pluck', 'bell', 'softlead', 'chip', 'hoover', 'vox', 'brass', 'piano', 'epiano', 'cowbell', 'acid', 'organ'],
}


# =============================================================================
#  Additional drums
# =============================================================================

def d_tom(p):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 110) * (1 + 0.5 * np.exp(-t * 20))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + 0.2 * bp(noise(n), 300, 3000) * np.exp(-t * 40)
    return fade_out(y, 0.05)


def d_cowbell808(p):
    return i_cowbell(81, 0.2, {})


def d_conga(p):
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 220) * (1 + 0.15 * np.exp(-t * 40))
    return fade_out(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14), 0.05)


DRUMS = {
    'kick': d_kick, 'snare': d_snare, 'clap': d_clap, 'chat': d_chat, 'ohat': d_ohat,
    'shaker': d_shaker, 'ride': d_ride, 'rim': d_rim, 'crash': d_crash,
    'chipkick': d_chipkick, 'chipsnare': d_chipsnare, 'chiphat': d_chiphat,
    'tom': d_tom, 'cowbell808': d_cowbell808, 'conga': d_conga,
}

# Drum kit presets: parameters for the synthesized kick/snare/hats
KITS = {
    'default': {},
    '808': dict(kick=dict(pitch=50, punch=90, decay=5, drive=1.6, len=0.9, click=0.15), snare=dict(tone=230, snap=1.1, body=0.5, decay=18),
                clap=dict(tail=11), chat=dict(decay=80), ohat=dict(decay=10)),
    '909': dict(kick=dict(pitch=50, punch=140, decay=8, drive=2.2, click=0.45), snare=dict(tone=190, snap=1.2, body=0.6, decay=14),
                chat=dict(decay=60), ohat=dict(decay=7)),
    'punchy': dict(kick=dict(pitch=54, punch=160, sweep=50, decay=9, drive=2.4, click=0.5), snare=dict(tone=200, snap=1.3, decay=15)),
    'hard': dict(kick=dict(pitch=55, punch=320, sweep=22, decay=3.5, drive=7.0, len=0.7, click=0.6), snare=dict(tone=210, snap=1.4, decay=13)),
    'soft': dict(kick=dict(pitch=50, punch=70, decay=9, drive=1.2, click=0.08), snare=dict(tone=170, snap=0.6, body=0.9, decay=22),
                 chat=dict(decay=90)),
    'acoustic': dict(kick=dict(pitch=58, punch=60, sweep=30, decay=11, drive=1.1, click=0.5), snare=dict(tone=195, snap=1.0, body=0.8, decay=11),
                     chat=dict(decay=45), ohat=dict(decay=5)),
}


# =============================================================================
#  Orchestral instruments
# =============================================================================

def i_violin(m, dur, p, glide=None, mod=None):
    """Solo bowed string: band-limited saw, bow attack, expressive vibrato, body resonances."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.08), 0.3, 0.9, 0.25)
    n = len(env)
    t = np.arange(n) / SR
    fv = vibrato(f, n, rate=5.6, cents=p.get('vib', 18), delay=0.18)
    x = saw(fv, n) + 0.05 * noise(n) * np.exp(-t * 20)
    y = eq(eq(lp(x, p.get('cut', 4500)), 'peak', 300, 1.2, 4), 'peak', 2800, 1.5, 3)
    return hp(y, 150) * env * 0.4


def i_choir(m, dur, p, glide=None, mod=None):
    """Choir 'aah/ooh': several detuned formant voices with slow attack."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.4), 0.5, 0.9, p.get('r', 0.9))
    n = len(env)
    f1, f2, f3 = VOWELS.get(p.get('vowel', 'a'), VOWELS['a'])
    L = np.zeros(n)
    Rt = np.zeros(n)
    for i, c in enumerate((-12, -4, 4, 12)):
        fv = vibrato(f * 2 ** (c / 1200), n, rate=4.8 + 0.4 * i, cents=10, delay=0.05)
        src = saw(fv, n, _rng().random()) + 0.08 * noise(n)
        v = bp(src, f1 * 0.8, f1 * 1.2) + 0.5 * bp(src, f2 * 0.85, f2 * 1.15) + 0.25 * bp(src, f3 * 0.9, f3 * 1.1)
        th = i / 3 * np.pi / 2
        L += v * np.cos(th)
        Rt += v * np.sin(th)
    return np.vstack([L, Rt]) * env * 0.8


def i_horn(m, dur, p, glide=None, mod=None):
    """French horn section: mellow brass, softer filter."""
    return i_brass(m, dur, dict(cut=p.get('cut', 1600)))


def i_harp(m, dur, p, glide=None, mod=None):
    return i_pluck(m, max(dur, 1.5), dict(bright=p.get('bright', 3500), damp=0.9985, r=1.0))


def i_pizz(m, dur, p, glide=None, mod=None):
    y = i_pluck(m, min(dur, 0.25), dict(bright=2200, damp=0.992, r=0.15))
    return eq(y, 'peak', 250, 1.0, 5)


def i_timpani(m, dur, p, glide=None, mod=None):
    """Tuned timpani hit (use with low notes)."""
    f = float(mtof(m))
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k, (r, a, d) in enumerate(((1.0, 1.0, 1.8), (1.5, 0.5, 2.5), (1.98, 0.3, 3.5), (2.44, 0.2, 4.5))):
        y += a * np.sin(2 * np.pi * f * r * t * (1 + 0.02 * np.exp(-t * 15))) * np.exp(-t * d)
    y += 0.4 * lp(noise(n), 900) * np.exp(-t * 30)
    return fade_out(y * np.minimum(t / 0.002, 1), 0.2) * 0.6


def i_celesta(m, dur, p, glide=None, mod=None):
    return i_bell(m, dur, dict(ratio=4.0, index=1.2, decay=2.5, ring=1.2))


def d_taiko(p):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 60) * (1 + 0.6 * np.exp(-t * 25))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    y += 0.6 * lp(noise(n), 1200) * np.exp(-t * 22)
    return fade_out(soft(y * 1.5, 1.4), 0.2)


def d_timp(p):
    return i_timpani(p.get('note', 41), 1.0, {})


INSTRUMENTS.update({'violin': i_violin, 'choir': i_choir, 'horn': i_horn, 'harp': i_harp, 'pizz': i_pizz,
                    'timpani': i_timpani, 'celesta': i_celesta})
INSTRUMENT_INFO.update({'violin': 'Solo violin / cello', 'choir': 'Choir (aah)', 'horn': 'French horns', 'harp': 'Harp',
                        'pizz': 'Pizzicato strings', 'timpani': 'Timpani (tuned)', 'celesta': 'Celesta'})
DRUMS.update({'taiko': d_taiko, 'timp': d_timp})
ROLE_CHOICES['bass'] += ['pizz', 'violin', 'piano', 'strings']
ROLE_CHOICES['chords'] += ['harp', 'choir', 'horn']
ROLE_CHOICES['pad'] += ['choir', 'horn']
ROLE_CHOICES['arp'] += ['harp', 'pizz', 'celesta', 'strings', 'violin']
ROLE_CHOICES['lead'] += ['violin', 'horn', 'celesta', 'choir', 'harp']

# General MIDI program for each instrument (used by MIDI / DAW export)
GM_PROGRAM = {
    'piano': 0, 'epiano': 4, 'celesta': 8, 'bell': 14, 'organ': 16, 'guitar': 29, 'pluck': 25,
    'sawbass': 38, 'reese': 39, '808': 38, 'sinebass': 38, 'chipbass': 38, 'acid': 38, 'wobble': 39, 'fmbass': 39,
    'violin': 40, 'strings': 48, 'pizz': 45, 'harp': 46, 'timpani': 47, 'choir': 52, 'vox': 54,
    'brass': 61, 'horn': 60, 'softlead': 73, 'leadsaw': 81, 'supersaw_lead': 81, 'hoover': 81, 'chip': 80,
    'supersaw': 90, 'warmpad': 89, 'stab': 62, 'pluck_saw': 84, 'cowbell': 113,
}


# =============================================================================
#  World / acoustic colours (v1.2)
# =============================================================================

def i_logdrum(m, dur, p, glide=None, mod=None):
    """Amapiano log drum: pitched, knocking sub with a fast pitch drop."""
    f = float(mtof(m))
    n = int((min(dur, 1.2) + 0.25) * SR)
    t = np.arange(n) / SR
    fr = f * (1 + 1.2 * np.exp(-t * 45))
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) + 0.35 * np.sin(4 * np.pi * np.cumsum(fr) / SR)
    y *= np.exp(-t * p.get('decay', 5.0)) * np.minimum(t / 0.001, 1)
    return lp(soft(y * 2.2, 2.0), 1500) * 0.8


def _modal(f, n, partials, strike=0.0):
    t = np.arange(n) / SR
    y = np.zeros(n)
    for r, a, d in partials:
        if f * r < 18000:
            y += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d)
    if strike:
        y += strike * bp(noise(n), 1500, 7000) * np.exp(-t * 300)
    return y * np.minimum(t / 0.0008, 1)


def i_marimba(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    n = int(1.2 * SR)
    return fade_out(_modal(f, n, [(1, 1.0, 5), (3.93, 0.35, 16), (9.9, 0.12, 35)], 0.15), 0.05) * 0.7


def i_kalimba(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    n = int(1.6 * SR)
    return fade_out(_modal(f, n, [(1, 1.0, 3.2), (1.003, 0.4, 3.0), (5.95, 0.25, 18), (2.0, 0.08, 8)], 0.08), 0.05) * 0.7


def i_steeldrum(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    n = int(1.4 * SR)
    return fade_out(_modal(f, n, [(1, 1.0, 3.5), (2, 0.7, 4.5), (3, 0.3, 6), (4.2, 0.15, 9), (5.1, 0.08, 12)], 0.05), 0.05) * 0.6


def i_sax(m, dur, p, glide=None, mod=None):
    """Breathy tenor-ish sax: pulse source, formants, breath, growl on attack."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.04, 0.3, 0.85, 0.12)
    n = len(env)
    t = np.arange(n) / SR
    fv = vibrato(f, n, rate=5.2, cents=14, delay=0.25) * (1 - 0.03 * np.exp(-t * 25))
    src = square(fv, n, pw=0.42) * 0.6 + saw(fv, n) * 0.4
    y = bp(src, 450, 1400) + 0.6 * bp(src, 1600, 3000) + 0.12 * bp(noise(n), 1500, 5000) * (0.4 + 0.6 * np.exp(-t * 12))
    return soft(y * env * 1.6, 1.4) * 0.5


def i_flute(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.06, 0.3, 0.85, 0.2)
    n = len(env)
    fv = vibrato(f, n, rate=5.0, cents=12, delay=0.2)
    y = sine(fv, n) + 0.12 * sine(fv * 2, n) + 0.05 * sine(fv * 3, n)
    y += 0.08 * bp(noise(n), f * 0.8, min(f * 3, 15000))
    return y * env * 0.6


def i_clav(m, dur, p, glide=None, mod=None):
    y = i_pluck(m, min(dur, 0.3), dict(bright=9000, damp=0.985, r=0.06))
    return eq(hp(y, 250), 'peak', 1800, 1.0, 6) * 0.8


def d_snap(p):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    y = bp(noise(n), 1200, 5000) * np.exp(-t * 90) + 0.5 * np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 200)
    return fade_out(y, 0.01)


def d_tamb(p):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    y = hp(_metallic(n, 3.1) + 0.6 * noise(n), 6000)
    env = np.exp(-t * 14) * (1 + 0.6 * np.sin(2 * np.pi * 28 * t))
    return fade_out(y * env, 0.03)


def d_woodblock(p):
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * p.get('pitch', 1050) * t) * np.exp(-t * 55) + 0.3 * np.sin(2 * np.pi * 2650 * t) * np.exp(-t * 90)
    return fade_out(y, 0.01)


INSTRUMENTS.update({'logdrum': i_logdrum, 'marimba': i_marimba, 'kalimba': i_kalimba, 'steeldrum': i_steeldrum,
                    'sax': i_sax, 'flute': i_flute, 'clav': i_clav})
INSTRUMENT_INFO.update({'logdrum': 'Log drum (amapiano)', 'marimba': 'Marimba', 'kalimba': 'Kalimba', 'steeldrum': 'Steel drum',
                        'sax': 'Saxophone', 'flute': 'Flute', 'clav': 'Clavinet'})
DRUMS.update({'snap': d_snap, 'tamb': d_tamb, 'woodblock': d_woodblock})
ROLE_CHOICES['bass'] += ['logdrum']
ROLE_CHOICES['chords'] += ['clav', 'marimba']
ROLE_CHOICES['arp'] += ['marimba', 'kalimba', 'steeldrum', 'clav']
ROLE_CHOICES['lead'] += ['sax', 'flute', 'steeldrum', 'marimba', 'kalimba']
GM_PROGRAM.update({'logdrum': 116, 'marimba': 12, 'kalimba': 108, 'steeldrum': 114, 'sax': 66, 'flute': 73, 'clav': 7})

# Per-genre-family sound pools: each song may swap in another instrument from these for variety
PALETTES = {
    'Electronic': {'chords': ['stab', 'supersaw', 'pluck_saw', 'epiano', 'organ', 'warmpad', 'vox', 'bell', 'marimba'],
                   'pad': ['supersaw', 'warmpad', 'strings', 'choir', 'vox'],
                   'arp': ['pluck_saw', 'bell', 'chip', 'pluck', 'marimba', 'kalimba', 'steeldrum', 'acid'],
                   'lead': ['leadsaw', 'supersaw_lead', 'pluck', 'bell', 'vox', 'hoover', 'chip', 'flute', 'sax', 'kalimba']},
    'Classic': {'chords': ['piano', 'epiano', 'organ', 'guitar', 'clav'], 'pad': ['strings', 'organ', 'warmpad', 'choir'],
                'arp': ['guitar', 'piano', 'marimba', 'clav', 'epiano'], 'lead': ['brass', 'sax', 'flute', 'guitar', 'piano', 'organ', 'leadsaw']},
    'Orchestral': {'chords': ['strings', 'harp', 'piano'], 'pad': ['choir', 'horn', 'strings'],
                   'arp': ['harp', 'pizz', 'celesta', 'piano', 'marimba'], 'lead': ['violin', 'horn', 'flute', 'celesta', 'choir', 'brass']},
}


# =============================================================================
#  More orchestra (v1.9): string articulations, solo cello, harpsichord, woodwinds, trailer braam, sleigh bells
# =============================================================================

def _string_section(f, n, cents=(-12, -5, 0, 5, 12), vib=7, rate=4.6):
    L = np.zeros(n)
    Rt = np.zeros(n)
    for i, c in enumerate(cents):
        fv = vibrato(f * 2 ** (c / 1200), n, rate=rate + i * 0.31, cents=vib, delay=0.08)
        s = saw(fv, n, _rng().random())
        th = i / max(1, len(cents) - 1) * np.pi / 2
        L += s * np.cos(th)
        Rt += s * np.sin(th)
    return np.vstack([L, Rt])


def i_spiccato(m, dur, p, glide=None, mod=None):
    """Short-bowed string section (spiccato / staccato): the driving ostinato of film and trailer music."""
    f = float(mtof(m))
    ln = min(dur, p.get('len', 0.22))
    n = int((ln + 0.18) * SR)
    t = np.arange(n) / SR
    x = _string_section(f, n, vib=3)
    bow = 0.06 * noise(n) * np.exp(-t * 60)
    env = np.minimum(t / 0.006, 1) * np.exp(-t * p.get('decay', 9.0))
    env[int(ln * SR):] *= np.exp(-np.arange(n - int(ln * SR)) / (0.04 * SR))
    y = hp(lp(x + bow, p.get('cut', 4200)), 160)
    y = eq(y, 'peak', 2500, 1.2, 3)
    return y * env * 0.42


def i_tremolo(m, dur, p, glide=None, mod=None):
    """Tremolo strings: fast repeated bow strokes - tension, suspense, shimmering beds."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.2), 0.4, 0.9, p.get('r', 0.6))
    n = len(env)
    t = np.arange(n) / SR
    rate = p.get('rate', 13.0)
    strokes = 0.55 + 0.45 * np.abs(np.sin(np.pi * rate * t + 0.3 * np.sin(2 * np.pi * 0.7 * t)))
    x = _string_section(f, n, vib=4)
    y = hp(lp(x, p.get('cut', 3600)), 170)
    return y * env * strokes * 0.3


def i_cello(m, dur, p, glide=None, mod=None):
    """Solo cello: darker, woodier bowed string with a slow, wide vibrato."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.12), 0.3, 0.92, 0.3)
    n = len(env)
    t = np.arange(n) / SR
    fv = vibrato(f, n, rate=5.0, cents=p.get('vib', 16), delay=0.22)
    x = saw(fv, n) + 0.3 * square(fv, n, pw=0.35) + 0.04 * noise(n) * np.exp(-t * 15)
    y = lp(x, p.get('cut', 2600))
    y = eq(eq(eq(y, 'peak', 220, 1.1, 5), 'peak', 600, 1.4, -3), 'peak', 1500, 1.2, 2)
    return hp(y, 55) * env * 0.42


def i_harpsichord(m, dur, p, glide=None, mod=None):
    """Harpsichord: two plucked strings (8' + 4' an octave up), quill snap, quick decay - baroque continuo."""
    a = i_pluck(m, max(dur, 0.6), dict(bright=p.get('bright', 9000), damp=0.9965, r=0.5))
    b = i_pluck(m + 12, max(dur, 0.6), dict(bright=10000, damp=0.995, r=0.4))
    n = max(len(a), len(b))
    y = np.zeros(n)
    y[:len(a)] += a
    y[:len(b)] += 0.45 * b
    y = eq(hp(y, 120), 'peak', 3000, 1.0, 4)
    return y * 0.8


def i_clarinet(m, dur, p, glide=None, mod=None):
    """Clarinet: hollow, odd-harmonic reed tone (warm, round woodwind lines)."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.05, 0.3, 0.88, 0.15)
    n = len(env)
    fv = vibrato(f, n, rate=4.8, cents=6, delay=0.35)
    x = square(fv, n) * 0.8 + 0.2 * sine(fv, n)
    y = lp(x, p.get('cut', min(3200, f * 7))) + 0.03 * bp(noise(n), 1200, 4000)
    return y * env * 0.45


def i_oboe(m, dur, p, glide=None, mod=None):
    """Oboe: nasal double-reed tone with a strong formant - pastoral and plaintive solos."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.04, 0.3, 0.88, 0.14)
    n = len(env)
    fv = vibrato(f, n, rate=5.4, cents=10, delay=0.25)
    x = square(fv, n, pw=0.22) * 0.7 + saw(fv, n) * 0.3
    y = bp(x, 700, 1600) + 0.6 * bp(x, 2400, 3600) + 0.25 * lp(x, 900)
    return y * env * 0.55


def i_braam(m, dur, p, glide=None, mod=None):
    """Trailer 'braam': a huge low brass blast - stacked saws, growl and distortion with a slow filter bloom."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.04, 1.2, 0.75, 1.2)
    n = len(env)
    t = np.arange(n) / SR
    growl = 1 + 0.004 * np.sin(2 * np.pi * 31 * t)
    x = sum(saw(f * growl * 2 ** (c / 1200), n, _rng().random()) for c in (-18, -7, 0, 7, 18)) / 5
    x += 0.6 * saw(f * 0.5, n) + 0.4 * saw(f * 1.5 * 2 ** (3 / 1200), n)
    fe = np.clip(t / 0.5, 0, 1) * (0.6 + 0.4 * np.exp(-t * 1.5))
    y = filt_env(x, 120, p.get('cut', 1800), fe)
    y = soft(eq(y, 'peak', 250, 0.9, 5) * 2.0, 2.5)
    return np.vstack([y, y]) * env * 0.4


def d_sleigh(p):
    """Sleigh bells: a shaken jingle (holiday music)."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    y = hp(_metallic(n, 4.3) + 0.7 * noise(n), 5500)
    env = np.exp(-t * 9) * (1 + 0.8 * np.sin(2 * np.pi * 22 * t) ** 2)
    return fade_out(y * env * 0.8, 0.04)


INSTRUMENTS.update({'spiccato': i_spiccato, 'tremolo': i_tremolo, 'cello': i_cello, 'harpsichord': i_harpsichord,
                    'clarinet': i_clarinet, 'oboe': i_oboe, 'braam': i_braam})
INSTRUMENT_INFO.update({'spiccato': 'Spiccato strings (short)', 'tremolo': 'Tremolo strings', 'cello': 'Solo cello',
                        'harpsichord': 'Harpsichord', 'clarinet': 'Clarinet', 'oboe': 'Oboe', 'braam': 'Trailer braam'})
DRUMS.update({'sleigh': d_sleigh})
ROLE_CHOICES['bass'] += ['cello', 'spiccato']
ROLE_CHOICES['chords'] += ['spiccato', 'tremolo', 'harpsichord']
ROLE_CHOICES['pad'] += ['tremolo', 'braam']
ROLE_CHOICES['arp'] += ['spiccato', 'harpsichord']
ROLE_CHOICES['lead'] += ['cello', 'clarinet', 'oboe', 'harpsichord']
GM_PROGRAM.update({'spiccato': 48, 'tremolo': 44, 'cello': 42, 'harpsichord': 6, 'clarinet': 71, 'oboe': 68, 'braam': 61})
PALETTES['Orchestral'] = {**PALETTES['Orchestral'],
                          'chords': PALETTES['Orchestral']['chords'] + ['spiccato', 'tremolo'],
                          'lead': PALETTES['Orchestral']['lead'] + ['cello', 'oboe', 'clarinet']}


# =============================================================================
#  Folk & latin colours (v1.10): accordion / bandoneon, banjo
# =============================================================================

def i_accordion(m, dur, p, glide=None, mod=None):
    """Accordion / bandoneon: free-reed tone, two reeds tuned slightly apart (the 'musette' shimmer) - cumbia, tango, folk."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.03, 0.2, 0.92, 0.12)
    n = len(env)
    wet = p.get('musette', 9)                                   # cents between the reeds
    x = sum(square(f * 2 ** (c / 1200), n, pw=0.38) * 0.5 + 0.5 * saw(f * 2 ** (c / 1200), n) for c in (-wet / 2, wet / 2))
    y = lp(x, p.get('cut', 3800)) + 0.35 * lp(square(f * 0.5, n, pw=0.4), 1200)
    y = eq(eq(y, 'peak', 1100, 1.0, 4), 'peak', 300, 1.0, -3)
    bellows = 1 + 0.04 * np.sin(2 * np.pi * 0.9 * np.arange(n) / SR)
    return hp(y, 90) * env * bellows * 0.3


def i_banjo(m, dur, p, glide=None, mod=None):
    """Banjo: bright, twangy plucked string with a quick drumhead decay - bluegrass rolls and country picking."""
    y = i_pluck(m, max(0.4, min(dur, 1.2)), dict(bright=p.get('bright', 11000), damp=0.993, r=0.15))
    n = len(y)
    t = np.arange(n) / SR
    y = eq(hp(y, 220), 'peak', 2800, 1.2, 6) * np.exp(-t * 3.2)
    return y * 1.1


INSTRUMENTS.update({'accordion': i_accordion, 'banjo': i_banjo})
INSTRUMENT_INFO.update({'accordion': 'Accordion / bandoneon', 'banjo': 'Banjo'})
ROLE_CHOICES['chords'] += ['accordion', 'banjo']
ROLE_CHOICES['arp'] += ['banjo', 'accordion']
ROLE_CHOICES['lead'] += ['accordion', 'banjo']
ROLE_CHOICES['pad'] += ['accordion']
GM_PROGRAM.update({'accordion': 21, 'banjo': 105})
