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
    if p.get('reverse'):                                # hardstyle reverse bass: swells up after the kick, cut dead at the end
        n_ = int(max(0.02, dur) * SR)
        env = (np.linspace(0, 1, n_) ** 2.2).astype(np.float32)
        env[-int(0.006 * SR):] *= np.linspace(1, 0, int(0.006 * SR))
    else:
        env = adsr(dur * SR, p.get('a', 0.003), p.get('d', 0.18), p.get('s', 0.6), 0.05)
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
    mv = p.get('move', 1.0)                       # the reese 'moves': its detune slowly widens and narrows (DnB)
    d = 1 + (0.006 + 0.004 * mv * np.sin(2 * np.pi * 0.23 * t + 1.0))
    L = saw(f / d, n) + saw(f * (1 + (d - 1) * 0.6), n, 0.3)
    R = saw(f * d, n, 0.6) + saw(f / (1 + (d - 1) * 0.6), n, 0.1)
    wob = 0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t)
    cut = p.get('cut', 900)
    L = filt_env(L, cut * 0.5, cut * 1.6, wob)
    R = filt_env(R, cut * 0.5, cut * 1.6, 1 - wob)
    sub = sine(f, n) * 1.2
    out = np.vstack([soft(L * 0.5, 2.0) + sub, soft(R * 0.5, 2.0) + sub]) * env
    return out


def i_808(m, dur, p, glide=None, mod=None):
    """Trap 808: a sine with a long tail and drive, sliding from the previous note. `mod` warps one note (bass-warp
    genres): 'dive' (falls up to an octave as it ends), 'rise' (shoots up an octave), 'wob:<Hz>' (a 2-3 semitone pitch
    wobble), 'growl' (extra drive + square grit)."""
    f = float(mtof(m))
    gate = int(dur * SR)
    n = gate + int(0.04 * SR)
    t = np.arange(n) / SR
    if glide is not None:
        f0 = float(mtof(glide))
        freq = f + (f0 - f) * np.exp(-t / p.get('slide', 0.09))      # the classic trap 808 slide
    else:
        freq = np.full(n, f)
    w = str(mod) if isinstance(mod, str) else ''
    if w == 'dive' or w == 'rise':
        start = 0.45 * gate / SR
        k = np.clip((t - start) / max(0.05, dur - start), 0, 1) ** 1.6
        freq = freq * 2 ** ((-12 if w == 'dive' else 12) * k / 12)
    elif w.startswith('wob'):
        rate = float(w.split(':')[1]) if ':' in w else 5.0
        depth = min(1.0, t[-1] / 0.25) * 2.5                       # semitones, easing in after the attack
        freq = freq * 2 ** (depth * np.sin(2 * np.pi * rate * t) * np.minimum(t / 0.15, 1) / 12)
    y = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    if w == 'growl':
        y = y + 0.35 * np.sign(y) * np.abs(y) ** 0.5
    amp = np.exp(-t * p.get('decay', 0.9)) * np.minimum(t / 0.002, 1)
    rel = np.ones(n)
    rel[gate:] = np.linspace(1, 0, n - gate)
    return soft(y * amp * rel, p.get('drive', 2.4) * (1.8 if w == 'growl' else 1.0))


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
    # JP-8000-style supersaw: seven saws spread wide (the outer ones furthest), the centre voice a little louder,
    # bright, and high-passed so the low end stays clean for the bass
    cents = np.array([-38, -22, -9, 0, 9, 22, 38]) * p.get('detune', 1.0)
    gains = np.array([0.8, 0.9, 1.0, 1.25, 1.0, 0.9, 0.8])
    L = np.zeros(n)
    R = np.zeros(n)
    for i, (c, g) in enumerate(zip(cents, gains)):
        s = saw(f * 2 ** (c / 1200), n, _rng().random()) * g
        th = (i / (len(cents) - 1)) * np.pi / 2
        L += s * np.cos(th)
        R += s * np.sin(th)
    out = hp(lp(np.vstack([L, R]), p.get('cut', 3000) * 1.6), 140)
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


def d_hardkick(p):
    """Hard dance kick (hardstyle / gabber / hardcore): a clicky punch on top of a long pitched body that is driven into
    heavy, asymmetric distortion so it 'screams' - the tail carries a note (tuned to the key by the composer), then a
    band-pass shapes the distortion into the mid-range bite. tail 1 = hardstyle, 2 = gabber (shorter, squarer, nastier)."""
    tail = p.get('tail', 1.0)
    n = int(p.get('len', 0.5) * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 52)
    f = f0 + p.get('punch', 300) * np.exp(-t * p.get('sweep', 26)) + f0 * 0.6 * np.exp(-t * 6)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.exp(-t * p.get('decay', 3.5)) * np.clip((p.get('len', 0.5) - t) / 0.04, 0, 1)
    drv = p.get('drive', 10.0)
    x = body * env
    dist = np.tanh(x * drv + 0.25 * tail) - np.tanh(0.25 * tail)                # asymmetric: even harmonics, 'rawness'
    if tail >= 2:
        dist = np.sign(dist) * np.abs(dist) ** 0.5                             # gabber: clipped nearly square
    bite = bp(dist, 250, 2400) * (0.6 + 0.3 * tail)
    sub = lp(dist, 140)
    click = bp(noise(n), 1800, 8000) * np.exp(-t * 260) * p.get('click', 0.6)
    y = sub * 1.1 + bite + click + 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 20)
    return fade_out(soft(y, 1.4), 0.02)


def d_kick(p):
    if p.get('tail'):
        return d_hardkick(p)
    n = int(p.get('len', 0.5) * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 48) + p.get('punch', 120) * np.exp(-t * p.get('sweep', 40))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * p.get('decay', 7))
    click = bp(noise(n), 1500, 7000) * np.exp(-t * 300) * p.get('click', 0.3)
    return fade_out(soft(body + click, p.get('drive', 1.6)), 0.02)


def d_snare(p):
    """Snare: a pitched shell tone + band-passed wire noise. Optional: crack (a hard stick transient - the crisp DnB
    snare), nlo / nhi (the wire band), tdecay (how long the shell rings), drive (a squashed, distorted neuro snare)."""
    n = int(p.get('len', 0.35) * SR)
    t = np.arange(n) / SR
    tf = p.get('tone', 185)
    tone = (np.sin(2 * np.pi * tf * t) * 0.6 + np.sin(2 * np.pi * tf * 1.8 * t) * 0.3) * np.exp(-t * p.get('tdecay', 28))
    nz = bp(noise(n), p.get('nlo', 1200), p.get('nhi', 9000)) * np.exp(-t * p.get('decay', 16))
    y = tone * p.get('body', 0.7) + nz * p.get('snap', 0.9)
    if p.get('crack'):
        y += p['crack'] * hp(noise(n), 2500) * np.exp(-t * 600)
    return fade_out(soft(y, p.get('drive', 1.3)), 0.02)


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
    x = hp(p.get('metal', 0.6) * _metallic(n) + 0.5 * noise(n), p.get('hp', 7000))
    return fade_out(x * np.exp(-t * p.get('decay', 70)), 0.01)


def d_ohat(p):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    x = hp(p.get('metal', 0.6) * _metallic(n) + 0.5 * noise(n), p.get('hp', 6500))
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
    """Dubstep wobble ("wub"): a fat unison saw + square stack with a touch of FM grit, through a resonant low-pass whose
    cutoff an LFO sweeps exponentially (closed - open - closed, so each cycle says "wow"), plus a vowel formant that
    follows it, then driven hard. The wobble lives above ~110 Hz; a clean, steady sine sub sits underneath so the low
    end never pumps. mod = beats per LFO cycle (0.5 = 8ths, 0.25 = 16ths, 1/3 = triplets, 2 = slow half-bar swells).
    p: cut (top of the sweep, Hz), sub (sub level), shape ('sine' | 'saw' | 'square' | 'tri'), res, grit."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.004, 0.08, 1.0, 0.04)
    n = len(env)
    t = np.arange(n) / SR
    rate_beats = mod if isinstance(mod, (int, float)) and mod else 0.5
    hz = 1.0 / (rate_beats * p.get('spb', 0.43))
    ph = (hz * t) % 1.0
    shape = p.get('shape', 'sine')
    if shape == 'saw':                                   # snaps open, closes slowly: "WAAow"
        lfo = (1 - ph) ** 1.6
    elif shape == 'square':                              # choppy on / off "wob wob"
        lfo = 0.5 + 0.5 * np.tanh(12 * np.sin(2 * np.pi * ph))
    elif shape == 'tri':
        lfo = 1 - np.abs(2 * ph - 1)
    else:                                                # smooth "wow"
        lfo = 0.5 - 0.5 * np.cos(2 * np.pi * ph)
    lfo = uniform_smooth(lfo, int(0.002 * SR))
    fo = f if f > 55 else f * 2                          # the mid layer speaks an octave up from very low roots
    x = (saw(fo * 1.0045, n) + saw(fo * 0.9955, n, 0.37) + 0.8 * saw(fo, n, 0.71)) / 2.4
    x += 0.55 * square(fo * 2, n, 0.13)
    grit = float(p.get('grit', 1.2))
    x += 0.25 * np.sin(2 * np.pi * fo * t + grit * np.sin(2 * np.pi * fo * 2 * t))
    top = float(p.get('cut', 2600))
    cut = 110.0 * (max(top, 200.0) / 110.0) ** lfo       # exponential sweep: even "vowel" movement to the ear
    y = svf_sweep(x, cut, q=float(p.get('res', 5.0)))
    y += 0.6 * svf_sweep(x, 350 + 1100 * lfo, q=6.0, mode='bandpass')   # 'oo' -> 'ah' formant riding the filter
    y = soft(y * 3.0, 2.2) * 0.5
    y = hp(hp(y, 120), 120)                              # 4th-order: the wobble keeps out of the sub's way
    sub = sine(f / 2 if f > 70 else f, n) * p.get('sub', 0.8)
    return (y + sub) * env


def uniform_smooth(x, k):
    if k <= 1:
        return x
    return np.convolve(x, np.ones(k) / k, mode='same')


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
    """Plucked electric guitar (Karplus-Strong + pickup/cab filtering). mod 'pm' = palm-muted (choked, dark, thumpy)."""
    if mod == 'pm':
        y = i_pluck(m, min(dur, 0.16), dict(bright=1600, damp=0.97, r=0.05))
        return eq(y, 'peak', 160, 1.0, 5.0) * 0.8
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
    """Pitched 808-style cowbell (phonk melodies). The classic sound: the 808's two square oscillators a fifth-ish apart
    (ratio 1.48) through a band-pass, a fast attack decay into a shorter ring, and light saturation for punch."""
    f = float(mtof(m))
    p = p or {}
    ring = float(p.get('ring', 5.0))                    # lower = longer tail
    n = int(min(dur + (0.4 if ring >= 4 else 1.0), 2.2) * SR)
    t = np.arange(n) / SR
    x = square(f, n) + square(f * 1.48, n, 0.3)
    if p.get('chorus'):                                 # a second, slightly detuned cowbell for width
        x = x + 0.6 * (square(f * 1.006, n, 0.1) + square(f * 1.48 * 1.006, n, 0.4))
    y = bp(x, f * 0.9, f * 4) * (0.7 * np.exp(-t * float(p.get('attack_decay', 18))) + 0.3 * np.exp(-t * ring))
    if p.get('sat', 1.6) and not p.get('drive'):        # light saturation: punchy, still clearly a cowbell
        k = float(p.get('sat', 1.6))
        y = soft(y / (np.max(np.abs(y)) + 1e-9) * k, 1.0) / soft(np.array([k]), 1.0)[0]
    if p.get('drive'):                       # phonk: overdriven until it cuts like a synth lead, ring held up by the clipping
        d = float(p['drive'])
        y = soft(y / (np.max(np.abs(y)) + 1e-9) * d, 1.0) / soft(np.array([d]), 1.0)[0]
        y = eq(lp(y, 6500), 'peak', 1600, 1.0, 4)
    if p.get('crush'):                       # light bit / sample-rate reduction for the "broken" lo-fi edge
        c = float(p['crush'])
        bits = 2 ** (12 - 6 * c)
        y = np.round(y * bits) / bits
        hold = max(1, int(1 + 5 * c))
        y = np.repeat(y[::hold], hold)[:len(y)]
    return fade_out(y, 0.03) * 0.6


def i_cowbell_808(m, dur, p, glide=None, mod=None):
    """Raw 808 cowbell: dry, short and clean - straight off the drum machine."""
    return i_cowbell(m, dur, dict(p or {}, sat=0.0, ring=9.0, attack_decay=22))


def i_cowbell_long(m, dur, p, glide=None, mod=None):
    """Long-ringing cowbell with a slight chorus - the sustained drift-phonk lead."""
    return i_cowbell(m, dur, dict(p or {}, ring=2.2, chorus=True, sat=2.2))


def i_cowbell_dist(m, dur, p, glide=None, mod=None):
    """Overdriven cowbell that cuts like a synth lead."""
    return i_cowbell(m, dur, dict(p or {}, drive=5.0, ring=3.5))


def i_cowbell_crushed(m, dur, p, glide=None, mod=None):
    """Distorted and bit-crushed - the broken, lo-fi cowbell."""
    return i_cowbell(m, dur, dict(p or {}, drive=6.0, crush=0.35, ring=3.5))


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
    """The trance lead: 9 detuned saws spread across the stereo field, an octave-down saw for body, a filter that opens on
    every note, delayed vibrato on long notes and a high-pass so it sits above the chords."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.004, 0.25, 0.85, p.get('r', 0.25))
    n = len(env)
    t = np.arange(n) / SR
    vib = 1 + 0.0035 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.3) / 0.35, 0, 1)
    cents = np.array([-34, -22, -12, -5, 0, 5, 12, 22, 34]) * p.get('detune', 1.0)
    L = np.zeros(n)
    R = np.zeros(n)
    for i, c in enumerate(cents):
        ph = np.cumsum(f * 2 ** (c / 1200) * vib / SR) + _rng().random()
        s_ = 2 * (ph % 1.0) - 1
        th = (i / (len(cents) - 1)) * np.pi / 2
        L += s_ * np.cos(th)
        R += s_ * np.sin(th)
    sub = 2 * ((np.cumsum(f / 2 * vib / SR)) % 1.0) - 1
    x = np.vstack([L, R]) / len(cents) * 1.7 + 0.35 * sub
    fenv = 0.55 + 0.45 * np.exp(-t * 6)
    y = filt_env(x, 900, p.get('cut', 9000), fenv)
    y = hp(y, 180)
    return y * env * 1.1


INSTRUMENTS = {
    'sawbass': i_sawbass, 'reese': i_reese, '808': i_808, 'sinebass': i_sinebass, 'chipbass': i_chipbass,
    'acid': i_acid, 'wobble': i_wobble, 'fmbass': i_fmbass,
    'supersaw': i_supersaw, 'warmpad': i_warmpad, 'strings': i_strings,
    'stab': i_stab, 'pluck_saw': i_pluck_saw, 'epiano': i_epiano, 'piano': i_piano, 'organ': i_organ,
    'pluck': i_pluck, 'guitar': i_guitar, 'bell': i_bell, 'brass': i_brass, 'vox': i_vox, 'cowbell': i_cowbell, 'cowbell_808': i_cowbell_808,
    'cowbell_long': i_cowbell_long, 'cowbell_dist': i_cowbell_dist, 'cowbell_crushed': i_cowbell_crushed,
    'leadsaw': i_leadsaw, 'softlead': i_softlead, 'chip': i_chip, 'hoover': i_hoover, 'supersaw_lead': i_supersaw_lead,
}

INSTRUMENT_INFO = {
    'sawbass': 'Saw bass (filter pluck)', 'reese': 'Reese bass (DnB growl)', '808': '808 sub (gliding)',
    'sinebass': 'Warm sine bass', 'chipbass': '8-bit triangle bass', 'acid': 'Acid 303 bass', 'wobble': 'Dubstep wobble bass',
    'fmbass': 'FM grit bass', 'supersaw': 'Supersaw chords', 'warmpad': 'Warm analog pad', 'strings': 'String ensemble',
    'stab': 'Chord stab', 'pluck_saw': 'Saw pluck', 'epiano': 'Electric piano (Rhodes)', 'piano': 'Acoustic piano',
    'organ': 'Drawbar organ', 'pluck': 'Plucked string', 'guitar': 'Electric guitar', 'bell': 'FM bell',
    'brass': 'Synth brass', 'vox': 'Vocal chop', 'cowbell': 'Pitched cowbell (classic phonk)', 'cowbell_808': 'Pitched cowbell - raw 808',
    'cowbell_long': 'Pitched cowbell - long ring', 'cowbell_dist': 'Pitched cowbell - distorted', 'cowbell_crushed': 'Pitched cowbell - crushed', 'leadsaw': 'Saw lead',
    'softlead': 'Soft flute-like lead', 'chip': '8-bit pulse', 'hoover': 'Rave hoover', 'supersaw_lead': 'Supersaw lead',
}

ROLE_CHOICES = {
    'bass': ['sawbass', 'reese', '808', 'sinebass', 'acid', 'wobble', 'fmbass', 'chipbass', 'pluck'],
    'chords': ['stab', 'supersaw', 'epiano', 'piano', 'organ', 'pluck', 'guitar', 'strings', 'brass', 'pluck_saw', 'warmpad', 'bell', 'chip'],
    'pad': ['supersaw', 'warmpad', 'strings', 'organ', 'vox'],
    'arp': ['pluck_saw', 'bell', 'pluck', 'chip', 'epiano', 'piano', 'acid', 'supersaw_lead'],
    'lead': ['leadsaw', 'supersaw_lead', 'pluck', 'bell', 'softlead', 'chip', 'hoover', 'vox', 'brass', 'piano', 'epiano', 'cowbell', 'cowbell_808', 'cowbell_long', 'cowbell_dist', 'cowbell_crushed', 'acid', 'organ'],
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
    # trance: a tight, rolling 909 kick with a long tail, crisp clap, airy open hats
    'trance': dict(kick=dict(pitch=48, punch=170, sweep=40, decay=6.5, drive=2.6, len=0.55, click=0.55), snare=dict(tone=200, snap=1.3, decay=16),
                   clap=dict(tail=9), chat=dict(decay=70), ohat=dict(decay=5)),
    # techno: harder, darker 909 with drive
    'techno': dict(kick=dict(pitch=46, punch=150, sweep=34, decay=5.5, drive=3.6, len=0.6, click=0.4), snare=dict(tone=180, snap=1.1, decay=15),
                   chat=dict(decay=95), ohat=dict(decay=9)),
    # 80s LinnDrum-style: round kick, big snare with a fat body (the gated-reverb era)
    'linn': dict(kick=dict(pitch=56, punch=80, sweep=28, decay=10, drive=1.3, click=0.35), snare=dict(tone=210, snap=1.0, body=1.2, decay=7),
                 clap=dict(tail=6), chat=dict(decay=55), ohat=dict(decay=6)),
    # drum & bass: a tight, short, clicky kick that leaves room for the sub, and the crisp, cracking layered snare
    'dnb': dict(kick=dict(pitch=52, punch=190, sweep=70, decay=14, drive=2.2, len=0.32, click=0.75),
                snare=dict(tone=245, snap=1.5, body=0.8, decay=17, tdecay=40, nlo=1800, nhi=11000, crack=0.7, len=0.28),
                chat=dict(decay=95, hp=8500), ohat=dict(decay=9, hp=7500)),
    # neurofunk: harder kick, a compressed, distorted snare with a longer noisy tail
    'neuro': dict(kick=dict(pitch=50, punch=230, sweep=60, decay=11, drive=3.5, len=0.34, click=0.8),
                  snare=dict(tone=220, snap=1.8, body=0.9, decay=11, tdecay=30, nlo=1500, nhi=10000, crack=0.9, drive=3.0, len=0.32),
                  chat=dict(decay=110, hp=9000), ohat=dict(decay=10, hp=8000)),
    # liquid: rounder kick, a softer snare with more shell
    'liquid': dict(kick=dict(pitch=50, punch=140, sweep=50, decay=10, drive=1.6, len=0.4, click=0.45),
                   snare=dict(tone=210, snap=1.1, body=1.0, decay=16, tdecay=26, nlo=1400, nhi=9500, crack=0.35),
                   chat=dict(decay=80, hp=8000), ohat=dict(decay=8)),
    # Roland CR-78 (late-70s preset rhythm box): soft round kick, thin tinny snare, short metallic 'tss' hats
    'cr78': dict(kick=dict(pitch=62, punch=35, sweep=40, decay=15, drive=1.1, len=0.3, click=0.05),
                 snare=dict(tone=330, snap=0.55, body=0.5, decay=26, tdecay=45, nlo=2500, nhi=8000, len=0.22),
                 chat=dict(decay=140, hp=9000, metal=0.9), ohat=dict(decay=14, hp=8500, metal=0.9)),
    # Roland TR-606 (Drumatix): small, snappy, bright - acid & electro
    '606': dict(kick=dict(pitch=58, punch=70, sweep=45, decay=13, drive=1.4, len=0.35, click=0.3),
                snare=dict(tone=260, snap=1.3, body=0.4, decay=22, nlo=2000, nhi=10000, len=0.25),
                chat=dict(decay=120, hp=8500, metal=0.8), ohat=dict(decay=11, hp=8000, metal=0.8)),
    # Roland TR-707 (mid-80s sample-based): punchy 'digital' kick and snare, 6-bit hats
    '707': dict(kick=dict(pitch=54, punch=110, sweep=38, decay=11, drive=1.8, len=0.45, click=0.4, bits=8, srate=25000),
                snare=dict(tone=205, snap=1.35, body=0.75, decay=12, crack=0.3, bits=8, srate=25000),
                clap=dict(tail=10, bits=8, srate=25000), chat=dict(decay=75, bits=6, srate=25000),
                ohat=dict(decay=7, bits=6, srate=25000)),
    # Oberheim DMX (early-80s hip hop, Run-DMC, electro-funk): fat 8-bit kick and snare
    'dmx': dict(kick=dict(pitch=52, punch=95, sweep=30, decay=8, drive=2.0, len=0.6, click=0.35, bits=8, srate=24000),
                snare=dict(tone=190, snap=1.2, body=1.1, decay=10, tdecay=22, bits=8, srate=24000),
                clap=dict(tail=9, bits=8, srate=24000), chat=dict(decay=70, bits=8, srate=24000),
                ohat=dict(decay=6, bits=8, srate=24000)),
    # distorted phonk 808: clipped long kick, crunchy snare
    'phonk808': dict(kick=dict(pitch=48, punch=100, decay=4, drive=4.5, len=0.9, click=0.3),
                     snare=dict(tone=240, snap=1.4, body=0.6, decay=15, drive=2.6, bits=10, srate=22050),
                     clap=dict(tail=11), chat=dict(decay=85, bits=10, srate=22050), ohat=dict(decay=9)),
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
    'supersaw': 90, 'warmpad': 89, 'stab': 62, 'pluck_saw': 84, 'cowbell': 113, 'cowbell_808': 113, 'cowbell_long': 113, 'cowbell_dist': 113, 'cowbell_crushed': 113,
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


# =============================================================================
#  v1.11: classic synths and missing band instruments
# =============================================================================

def i_polysynth(m, dur, p, glide=None, mod=None):
    """Juno-style poly synth: one saw + sub pulse through a warm low-pass, with the famous lush chorus. 80s pop chords,
    synthwave, city pop, house stabs."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.006), p.get('d', 0.35), p.get('s', 0.7), p.get('r', 0.35))
    n = len(env)
    t = np.arange(n) / SR
    x = saw(f, n, _rng().random()) + 0.55 * square(f * 0.5, n, pw=0.5) + 0.03 * noise(n)
    fe = np.exp(-t / max(0.05, p.get('fdecay', 0.4)))
    y = filt_env(x, p.get('cut', 1800) * 0.45, p.get('cut', 1800) * 1.6, fe)
    y = hp(y, 70)
    d1 = int(0.0045 * SR + 0.0016 * SR * np.sin(2 * np.pi * 0.5 * t).mean())   # chorus: two delayed, modulated copies
    lfo = 0.0016 * SR * np.sin(2 * np.pi * 0.513 * t)
    idx = np.arange(n)
    L = y + 0.7 * np.interp(idx - (d1 + lfo), idx, y, left=0)
    Rt = y + 0.7 * np.interp(idx - (d1 - lfo), idx, y, left=0)
    return np.vstack([L, Rt]) * env * 0.32


def i_synthbrass(m, dur, p, glide=None, mod=None):
    """Prophet / OB-style synth brass: two detuned saws, a filter that blooms open on every note - 80s anthems, synthwave."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.05), 0.4, 0.8, 0.25)
    n = len(env)
    t = np.arange(n) / SR
    x = saw(f * 2 ** (-7 / 1200), n, _rng().random()) + saw(f * 2 ** (7 / 1200), n, _rng().random()) + 0.4 * saw(f * 0.5, n)
    fe = np.clip(t / 0.08, 0, 1) * (0.55 + 0.45 * np.exp(-t * 3))
    y = filt_env(x, 300, p.get('cut', 3200), fe)
    y = eq(hp(y, 90), 'peak', 1200, 1.0, 3)
    return np.vstack([y, y]) * env * 0.3


def i_moogbass(m, dur, p, glide=None, mod=None):
    """Moog-style bass, sustained: fat saw + square through a 24 dB ladder-ish filter that opens on the attack and then
    SETTLES half-open, so a held note stays round and full (house, synthwave, liquid, pop, electronic). The plucked,
    snap-shut version is 'moogpluck' (funk / disco / G-funk)."""
    if p.get('pluck'):
        return i_moogpluck(m, dur, p, glide, mod)
    f = float(mtof(m))
    gate = dur * SR
    env = adsr(gate, p.get('a', 0.004), p.get('d', 0.35), p.get('s', 0.88), p.get('r', 0.08))
    n = len(env)
    t = np.arange(n) / SR
    x = saw(f, n) + 0.8 * square(f * 2 ** (-4 / 1200), n, pw=0.5) + 0.6 * square(f * 0.5, n)
    sus = p.get('fsus', 0.55)                          # where the filter settles (0 = closed, 1 = fully open)
    fe = sus + (1 - sus) * np.exp(-t / p.get('fd', 0.3))
    cut = p.get('cut', 500)
    y = filt_env(x, cut * 0.8, cut * 3.5, fe)
    y = lp(y, cut * 5)
    y = soft(y * 1.5, 1.3)
    return hp(y, 30) * env * 0.5


def i_moogpluck(m, dur, p, glide=None, mod=None):
    """Plucked Moog bass: the filter snaps shut in ~0.1 s and the level drops - the bouncy funk / disco / G-funk bass."""
    f = float(mtof(m))
    gate = dur * SR
    env = adsr(gate, 0.002, p.get('d', 0.25), p.get('s', 0.7), 0.06)
    n = len(env)
    t = np.arange(n) / SR
    x = saw(f, n) + 0.8 * square(f * 2 ** (-4 / 1200), n, pw=0.5) + 0.5 * square(f * 0.5, n)
    fe = np.exp(-t / 0.12)
    y = filt_env(x, p.get('cut', 500) * 0.6, p.get('cut', 500) * 4.5, fe)
    y = lp(y, p.get('cut', 500) * 5)
    y = soft(y * 1.6, 1.4)
    return hp(y, 30) * env * 0.55


def i_glasspad(m, dur, p, glide=None, mod=None):
    """Glass pad: bell-like FM partials over a soft sine bed, slow shimmer - ambient, future bass, melodic techno."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.6), 0.8, 0.85, p.get('r', 1.4))
    n = len(env)
    t = np.arange(n) / SR
    mod_ = np.sin(2 * np.pi * f * 3.5 * t) * (1.2 + 0.6 * np.sin(2 * np.pi * 0.21 * t))
    a = np.sin(2 * np.pi * f * t + mod_ * 0.6)
    b = np.sin(2 * np.pi * f * 2 ** (6 / 1200) * 2 * t + 0.4 * np.sin(2 * np.pi * f * 5 * t))
    bed = sine(f, n) * 0.6
    L = 0.5 * a + 0.25 * b + bed
    Rt = 0.5 * np.roll(a, 300) + 0.25 * np.roll(b, 170) + bed
    return lp(np.vstack([L, Rt]), p.get('cut', 7000)) * env * 0.22


def i_solina(m, dur, p, glide=None, mod=None):
    """String machine (Solina / ARP): buzzy divide-down strings with a deep ensemble chorus - disco, 70s/80s, synthwave."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.12), 0.3, 0.95, p.get('r', 0.5))
    n = len(env)
    t = np.arange(n) / SR
    x = saw(f, n) + 0.5 * saw(f * 2, n)
    y = eq(bp(x, 300, 5000), 'peak', 2200, 0.8, 3)
    voices = []
    for k, (rate, dep) in enumerate(((0.63, 0.0016), (5.7, 0.00014), (0.91, 0.0011))):   # ~6 cents of ensemble wobble
        dly = (0.006 + dep * np.sin(2 * np.pi * rate * t + k)) * SR
        idx = np.arange(n)
        voices.append(np.interp(idx - dly, idx, y, left=0))
    L = voices[0] + 0.6 * voices[1]
    Rt = voices[2] + 0.6 * voices[1]
    return np.vstack([L, Rt]) * env * 0.22


def i_wurli(m, dur, p, glide=None, mod=None):
    """Wurlitzer electric piano: reedy, a little barky when played hard, with amp tremolo - soul, R&B, lo-fi, indie."""
    f = float(mtof(m))
    gate = int(dur * SR)
    n = gate + int(0.3 * SR)
    t = np.arange(n) / SR
    idx = 0.9 * np.exp(-t * 6) + 0.35
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 2 * t)) + 0.25 * np.sin(2 * np.pi * f * 3 * t) * np.exp(-t * 8)
    y = soft(y * 1.4, 1.2)
    amp = np.exp(-t * p.get('decay', 1.4))
    amp[gate:] *= np.exp(-np.arange(n - gate) / (0.07 * SR))
    y *= amp * np.minimum(t / 0.003, 1)
    trem = 0.22 * np.sin(2 * np.pi * p.get('trem', 5.5) * t)
    return lp(np.vstack([y * (1 + trem), y * (1 - trem)]), 4500) * 0.55


def i_vibes(m, dur, p, glide=None, mod=None):
    """Vibraphone: metal bars with motor tremolo and a long ring - jazz, bossa, lo-fi, cool lounge."""
    f = float(mtof(m))
    n = int((max(dur, 0.5) + 2.0) * SR)
    t = np.arange(n) / SR
    y = sine(f, n) * np.exp(-t * 1.1) + 0.3 * sine(f * 4, n) * np.exp(-t * 6) + 0.1 * sine(f * 10, n) * np.exp(-t * 18)
    y *= np.minimum(t / 0.002, 1)
    damp = int((dur + 0.6) * SR)                      # the pedal lets go a little after the note
    if damp < n:
        y[damp:] *= np.exp(-np.arange(n - damp) / (0.25 * SR))
    motor = 1 + p.get('motor', 0.28) * np.sin(2 * np.pi * 5.0 * t)
    return np.vstack([y * motor, y * (2 - motor)]) * 0.45


def i_upright(m, dur, p, glide=None, mod=None):
    """Upright (double) bass: a woody pluck with a soft thump and quick body decay - jazz, swing, bluegrass, folk."""
    y = i_pluck(m, max(0.3, min(dur, 2.0)), dict(bright=p.get('bright', 900), damp=0.995, r=0.12))
    n = len(y)
    t = np.arange(n) / SR
    f = float(mtof(m))
    thump = 0.6 * sine(f, n) * np.exp(-t * 7) * np.minimum(t / 0.004, 1)
    y = y + thump
    y = eq(eq(y, 'peak', 110, 1.0, 4), 'peak', 700, 1.2, 2.5)
    return lp(hp(y, 35), 3000) * 1.1


def i_mutedgtr(m, dur, p, glide=None, mod=None):
    """Palm-muted electric guitar: short, percussive 'chk' notes - funk, afrobeats, disco, highlife."""
    y = i_pluck(m, 0.25, dict(bright=p.get('bright', 4000), damp=0.95, r=0.04))
    n = len(y)
    t = np.arange(n) / SR
    y = eq(hp(y, 180), 'peak', 2500, 1.2, 4) * np.exp(-t * 14)
    return y * 1.4


def i_harmonica(m, dur, p, glide=None, mod=None):
    """Harmonica: breathy free reed with bends into the note - blues, country, folk."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.03, 0.2, 0.9, 0.12)
    n = len(env)
    t = np.arange(n) / SR
    bend = 2 ** ((-60 * np.exp(-t * 18)) / 1200)                # a small scoop up into the pitch
    fv = vibrato(f, n, rate=5.2, cents=p.get('vib', 12), delay=0.3) * bend
    x = square(fv, n, pw=0.3) * 0.6 + saw(fv, n) * 0.4
    y = bp(x, 400, 4000) + 0.12 * bp(noise(n), 1500, 5000)
    y = eq(y, 'peak', 1700, 1.4, 5)
    return y * env * 0.4


def i_trumpet(m, dur, p, glide=None, mod=None):
    """Solo trumpet: bright, brassy and singing, with a lip attack and late vibrato - jazz, salsa, ska, mariachi, western."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.025, 0.15, 0.85, 0.12)
    n = len(env)
    t = np.arange(n) / SR
    fv = vibrato(f, n, rate=5.6, cents=p.get('vib', 14), delay=0.35) * 2 ** ((-30 * np.exp(-t * 30)) / 1200)
    x = saw(fv, n)
    bright = np.clip(t / 0.06, 0, 1) * (0.7 + 0.3 * np.exp(-t * 2))
    y = filt_env(x, 600, p.get('cut', 5200), bright)
    y = eq(eq(y, 'peak', 1400, 1.0, 5), 'peak', 3000, 1.5, 3)
    return hp(y, 160) * env * 0.4


def i_pedalsteel(m, dur, p, glide=None, mod=None):
    """Pedal steel guitar: sweet, sustained notes that swell in with the volume pedal and slide up into pitch - country."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.18), 0.5, 0.85, 0.6)
    n = len(env)
    t = np.arange(n) / SR
    slide = 2 ** ((-150 * np.exp(-t * 9)) / 1200)                # the steel bar sliding up into the note
    fv = vibrato(f, n, rate=4.6, cents=8, delay=0.5) * slide
    x = saw(fv, n) * 0.5 + 0.5 * sine(fv, n) + 0.25 * sine(fv * 2, n)
    y = lp(x, p.get('cut', 3000))
    y = eq(y, 'peak', 900, 1.0, 2)
    return np.vstack([y, np.roll(y, 220)]) * env * 0.35


INSTRUMENTS.update({'polysynth': i_polysynth, 'synthbrass': i_synthbrass, 'moogbass': i_moogbass, 'moogpluck': i_moogpluck, 'glasspad': i_glasspad,
                    'solina': i_solina, 'wurli': i_wurli, 'vibes': i_vibes, 'upright': i_upright, 'mutedgtr': i_mutedgtr,
                    'harmonica': i_harmonica, 'trumpet': i_trumpet, 'pedalsteel': i_pedalsteel})
INSTRUMENT_INFO.update({'polysynth': 'Juno-style poly synth', 'synthbrass': 'Synth brass (Prophet / OB)', 'moogbass': 'Moog-style bass (sustained)', 'moogpluck': 'Moog-style bass (plucked, funk)',
                        'glasspad': 'Glass pad', 'solina': 'String machine (Solina)', 'wurli': 'Wurlitzer electric piano',
                        'vibes': 'Vibraphone', 'upright': 'Upright bass', 'mutedgtr': 'Palm-muted guitar', 'harmonica': 'Harmonica',
                        'trumpet': 'Trumpet', 'pedalsteel': 'Pedal steel guitar'})
ROLE_CHOICES['bass'] += ['moogbass', 'moogpluck', 'upright']
ROLE_CHOICES['chords'] += ['polysynth', 'synthbrass', 'wurli', 'solina', 'vibes', 'mutedgtr']
ROLE_CHOICES['pad'] += ['glasspad', 'solina', 'polysynth', 'synthbrass', 'pedalsteel']
ROLE_CHOICES['arp'] += ['polysynth', 'vibes', 'mutedgtr', 'wurli']
ROLE_CHOICES['lead'] += ['synthbrass', 'polysynth', 'vibes', 'harmonica', 'trumpet', 'pedalsteel', 'wurli']
GM_PROGRAM.update({'polysynth': 90, 'synthbrass': 62, 'moogbass': 39, 'moogpluck': 38, 'glasspad': 92, 'solina': 50, 'wurli': 4, 'vibes': 11,
                   'upright': 32, 'mutedgtr': 28, 'harmonica': 22, 'trumpet': 56, 'pedalsteel': 26})


def i_phonkbell(m, dur, p, glide=None, mod=None):
    """Phonk cowbell: two 808 cowbells tuned a little apart (the detuned, sour sound) driven into heavy distortion,
    with a ring that's long enough to carry a melody - the signature of drift phonk."""
    f = float(mtof(m))
    n = int(min(dur + 0.5, 1.8) * SR)
    t = np.arange(n) / SR
    det = 2 ** (p.get('detune', 22) / 1200)
    x = (square(f, n) + square(f * 1.48, n, 0.3)) + 0.8 * (square(f * det, n, 0.1) + square(f * 1.48 * det, n, 0.6))
    y = bp(x, f * 0.85, f * 5) * (0.65 * np.exp(-t * 11) + 0.35 * np.exp(-t * 3.2))
    y = soft(y * p.get('drive', 4.0), 2.2)                          # crushed and saturated
    y = eq(lp(y, 7000), 'peak', 1400, 1.0, 3)
    return np.vstack([y, np.roll(y, 90)]) * fade_out(np.ones(n), 0.03) * 0.42


INSTRUMENTS['phonkbell'] = i_phonkbell
INSTRUMENT_INFO['phonkbell'] = 'Phonk cowbell (detuned, distorted)'
ROLE_CHOICES['lead'] += ['phonkbell']
ROLE_CHOICES['arp'] += ['phonkbell']
GM_PROGRAM['phonkbell'] = 113



def i_growl(m, dur, p, glide=None, mod=None):
    """Growl bass: FM-modulated saw through moving vowel formants (yoy / ow / ah) and heavy distortion - the talking,
    snarling mid-bass of brostep and neurofunk. Movement is synced to the beat (mod = cycle length in beats)."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.004, 0.1, 1.0, 0.04)
    n = len(env)
    t = np.arange(n) / SR
    hz = 1.0 / ((mod if isinstance(mod, (int, float)) and mod else 0.5) * p.get('spb', 0.43))
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * hz * t)
    idx = 1.5 + 5.0 * lfo                                      # FM depth swells with the LFO
    ph = 2 * np.pi * np.cumsum(np.full(n, f)) / SR
    x = np.sin(ph + idx * np.sin(ph * 2.0)) + 0.3 * (saw(f * 1.003, n) + saw(f * 0.997, n, 0.4))
    x = soft(x * 2.2, 1.8)
    f1 = 300 + 500 * lfo                                       # vowel: 'oo' -> 'ah'
    f2 = 900 + 900 * lfo
    y = svf_sweep(x, f1, q=6.0) + 0.8 * svf_sweep(x, f2, q=7.0) + 0.25 * x
    y = soft(hp(y, 90) * 2.5, 2.2) * 0.45
    return y * env

INSTRUMENTS['growl'] = i_growl
INSTRUMENT_INFO['growl'] = 'Growl bass (FM + formant)'
ROLE_CHOICES['bass'] += ['growl']
GM_PROGRAM['growl'] = 39


# ---------------------------------------------------------------- orchestral sections (synth fallbacks)
# When the real orchestra library (or the user's orchestra plugin) is installed these names are played by
# the matching recorded section; otherwise these synth voices stand in.
def i_violins(m, dur, p, glide=None, mod=None):
    """1st violin section: bright string ensemble with expressive vibrato."""
    return i_strings(m, dur, dict(a=p.get('a', 0.18), r=p.get('r', 0.6), cut=p.get('cut', 5200)))


def i_violas(m, dur, p, glide=None, mod=None):
    return i_strings(m, dur, dict(a=p.get('a', 0.25), r=p.get('r', 0.6), cut=p.get('cut', 2800)))


def i_contrabass(m, dur, p, glide=None, mod=None):
    """Double basses: dark bowed low strings with a little sub weight."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.12), 0.3, 0.9, 0.35)
    n = len(env)
    fv = vibrato(f, n, rate=4.6, cents=6, delay=0.25)
    x = saw(fv, n) + 0.6 * saw(fv * 1.004, n, 0.3) + 0.5 * np.sin(2 * np.pi * np.cumsum(fv) / SR)
    y = eq(lp(x, p.get('cut', 1300)), 'peak', 110, 1.0, 4)
    return hp(y, 30) * env * 0.42


def i_trombone(m, dur, p, glide=None, mod=None):
    return i_brass(m, dur, dict(cut=p.get('cut', 2200)))


def i_tuba(m, dur, p, glide=None, mod=None):
    y = i_brass(m, dur, dict(cut=p.get('cut', 900)))
    return eq(y, 'peak', 90, 1.0, 5)


def i_bassoon(m, dur, p, glide=None, mod=None):
    return i_clarinet(m, dur, dict(p, cut=p.get('cut', 1600)))


def i_tubular(m, dur, p, glide=None, mod=None):
    return i_bell(m, max(dur, 2.5), dict(p))


INSTRUMENTS.update({'violins': i_violins, 'violas': i_violas, 'contrabass': i_contrabass, 'trombone': i_trombone,
                    'tuba': i_tuba, 'bassoon': i_bassoon, 'tubular': i_tubular})
INSTRUMENT_INFO.update({'violins': 'Violins (section)', 'violas': 'Violas (section)', 'contrabass': 'Double basses',
                        'trombone': 'Trombones', 'tuba': 'Tuba', 'bassoon': 'Bassoon', 'tubular': 'Tubular bells'})
ROLE_CHOICES['bass'] += ['contrabass', 'tuba']
ROLE_CHOICES['lead'] += ['violins', 'violas', 'trombone']
ROLE_CHOICES['pad'] += ['violins', 'violas', 'trombone']
ROLE_CHOICES['arp'] += ['violins']
GM_PROGRAM.update({'violins': 40, 'violas': 41, 'contrabass': 43, 'trombone': 57, 'tuba': 58, 'bassoon': 70, 'tubular': 14})


def d_anvil(p):
    """Trailer anvil / metal hit: bright inharmonic partials with a hard strike."""
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in ((1180, 1.0, 9), (1960, 0.7, 11), (2745, 0.55, 13), (3620, 0.4, 16), (5130, 0.3, 20)):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)
    y += 0.5 * hp(noise(n), 3000) * np.exp(-t * 60)
    return fade_out(y * 0.5, 0.1)


DRUMS['anvil'] = d_anvil



def i_twang(m, dur, p, glide=None, mod=None):
    """Telecaster twang: a bright bridge-pickup pluck with a snappy attack, a little amp grit and spring-reverb sparkle -
    the chicken-pickin' country lead guitar. p['trem'] (picks per second): tremolo picking - the note re-picked fast for
    its whole length, the surf-guitar rumble (alternate picks slightly softer)."""
    rate = float(p.get('trem') or 0)
    if rate > 0 and dur > 1.5 / rate:
        step = int(SR / rate)
        n = int(dur * SR) + int(0.25 * SR)
        y = np.zeros(n)
        pick = i_pluck(m, 2.2 / rate, dict(bright=p.get('bright', 7000), damp=p.get('damp', 0.99), r=0.05))
        pick = pick if pick.ndim == 1 else pick.mean(axis=0)
        for k, i in enumerate(range(0, int(dur * SR), step)):
            seg = pick[:n - i] * (1.0 if k % 2 == 0 else 0.8)
            y[i:i + len(seg)] *= 0.35                       # the new pick damps the ringing one
            y[i:i + len(seg)] += seg
        y = eq(eq(y, 'peak', 2600, 1.2, 5), 'peak', 180, 1.0, -2)
        return soft(y * 2.0, 1.6) * 0.42
    y = i_pluck(m, min(dur, 1.6), dict(bright=p.get('bright', 9000), damp=p.get('damp', 0.993), r=0.18))
    y = eq(eq(y, 'peak', 2600, 1.2, 6), 'peak', 180, 1.0, -4)
    return soft(y * 2.2, 1.6) * 0.45


INSTRUMENTS['twang'] = i_twang
INSTRUMENT_INFO['twang'] = 'Telecaster twang guitar (country)'
ROLE_CHOICES['lead'] += ['twang']
ROLE_CHOICES['arp'] += ['twang']
GM_PROGRAM['twang'] = 27


INSTRUMENTS['acguitar'] = INSTRUMENTS['guitar']        # synth stand-in until the real guitar library is installed
INSTRUMENT_INFO['acguitar'] = 'Acoustic guitar'
for _r in ('chords', 'arp', 'lead'):
    ROLE_CHOICES[_r] += ['acguitar']
GM_PROGRAM['acguitar'] = 25


INSTRUMENTS['sopsax'] = INSTRUMENTS['sax']             # synth stand-in until a recorded sax is installed
INSTRUMENT_INFO['sopsax'] = 'Soprano sax'
ROLE_CHOICES['lead'] += ['sopsax']
GM_PROGRAM['sopsax'] = 64



def i_ebass(m, dur, p, glide=None, mod=None):
    """Electric (finger) bass: a short pick/finger transient on top of a sustained round body that holds for the
    whole note, like a real P/J bass - it no longer dies away like a plucked string on long notes."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.004, p.get('d', 0.35), p.get('s', 0.62), 0.07)
    n = len(env)
    t = np.arange(n) / SR
    body = 0.85 * sine(f, n) + 0.28 * sine(2 * f, n) + 0.22 * saw(f, n)
    body = filt_env(body, 380, p.get('bright', 1400), np.exp(-t * 7))
    att = i_pluck(m, min(dur, 0.25), dict(bright=p.get('bright', 1400) * 1.4, damp=0.99, r=0.05))
    k = min(len(att), n)
    y = body * env
    y[:k] += 0.3 * att[:k] * np.exp(-t[:k] * 18)
    return eq(lp(hp(soft(y, 1.2), 32), 3200), 'peak', 90, 1.0, 3) * 0.32


INSTRUMENTS['ebass'] = i_ebass
INSTRUMENT_INFO['ebass'] = 'Electric bass'
ROLE_CHOICES['bass'] += ['ebass']
GM_PROGRAM['ebass'] = 33



def i_organbass(m, dur, p, glide=None, mod=None):
    """The house organ bass (Korg M1 "Organ 2" style, Robin S / Crystal Waters / 90s NYC house): bright organ partials
    with a hard key click that die away quickly, so each note is a punchy, rounded 'bonk' in the bass register."""
    f = float(mtof(m))
    n = int((min(dur, 1.2) + 0.08) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for ratio, amp, dk in ((1, 1.0, 3.0), (2, 0.75, 5.0), (3, 0.45, 7.0), (4, 0.3, 9.0), (6, 0.12, 12.0)):
        if f * ratio < 12000:
            y += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dk * p.get('decay', 1.0))
    y += 0.25 * hp(noise(n), 2500) * np.exp(-t * 180)                      # key click
    gate = np.ones(n)
    g = int(dur * SR)
    if g < n:
        gate[g:] = np.exp(-np.arange(n - g) / (0.03 * SR))
    y = soft(lp(y * gate, 3500) * 1.4, 1.3)
    return np.vstack([y, y]) * 0.42 * np.minimum(t / 0.002, 1)


INSTRUMENTS['organbass'] = i_organbass
INSTRUMENT_INFO['organbass'] = 'House organ bass (M1-style)'
ROLE_CHOICES['bass'] += ['organbass']
GM_PROGRAM['organbass'] = 16



def i_screech(m, dur, p, glide=None, mod=None):
    """Brostep screech (Skrillex "Scary Monsters" style): a high, harsh FM tone with a sweeping notch / formant and a
    pitch bend that whines up at the start - played an octave or two above the growls."""
    f = float(mtof(m)) * 2 ** p.get('octave', 1)
    env = adsr(dur * SR, 0.003, 0.08, 0.95, 0.03)
    n = len(env)
    t = np.arange(n) / SR
    bend = 2 ** ((-5 * np.exp(-t * 18)) / 12)                     # whines up into the note
    hz = 1.0 / ((mod if isinstance(mod, (int, float)) and mod else 0.25) * p.get('spb', 0.43))
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * hz * t)
    ph = 2 * np.pi * np.cumsum(f * bend) / SR
    x = np.sin(ph + (3.0 + 6.0 * lfo) * np.sin(ph * 3.01)) + 0.4 * saw(f * 1.01, n)
    y = svf_sweep(soft(x * 3.0, 2.5), 900 + 2600 * lfo, q=5.0) + 0.3 * x
    y = soft(hp(y, 300) * 2.0, 2.0) * 0.35
    return y * env


def i_riddim(m, dur, p, glide=None, mod=None):
    """Riddim bass: a hollow square / saw stack through a band-pass that is chopped on and off by a hard, tempo-synced
    gate (mod = chop length in beats) - the minimal, repetitive, triplet-chopped mid bass of riddim - plus a clean sub."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.002, 0.05, 1.0, 0.02)
    n = len(env)
    t = np.arange(n) / SR
    hz = 1.0 / ((mod if isinstance(mod, (int, float)) and mod else 1 / 3) * p.get('spb', 0.43))
    gate = (np.sin(2 * np.pi * hz * t) > -0.2).astype(np.float64)
    gate = np.convolve(gate, np.ones(64) / 64, mode='same')       # click-free chops
    x = square(f, n, 0.0) + 0.7 * saw(f * 1.006, n) + 0.5 * square(f * 2.003, n, 0.25)
    y = svf_sweep(x, np.full(n, p.get('cut', 750)), q=3.5) + 0.35 * x
    y = soft(y * 2.8, 2.4) * 0.45 * gate
    sub = sine(f / 2 if f > 70 else f, n) * p.get('sub', 0.7)
    return (y + sub) * env


INSTRUMENTS.update({'screech': i_screech, 'riddim': i_riddim})
INSTRUMENT_INFO.update({'screech': 'Screech bass (brostep)', 'riddim': 'Riddim bass (chopped)'})
ROLE_CHOICES['bass'] += ['screech', 'riddim']
GM_PROGRAM.update({'screech': 81, 'riddim': 39})



# =============================================================================
#  v1.36: M1 house piano, folk & latin instruments rebuilt, tuned log drum
# =============================================================================

def i_m1piano(m, dur, p, glide=None, mod=None):
    """Korg M1 'Piano 16'' - the bright, glassy, slightly hollow house piano (Crystal Waters, Robin S, every 90s piano
    house record): a hard hammer 'ding', upper partials that die fast, a short looped sustain and a big 3 kHz presence."""
    f = float(mtof(m))
    ring = min(dur + 0.5, 3.0)
    n = int(ring * SR)
    t = np.arange(n) / SR
    amps = (1.0, 0.85, 0.5, 0.55, 0.3, 0.32, 0.16, 0.14, 0.1, 0.08, 0.06)
    y = np.zeros(n)
    for k, a in enumerate(amps, 1):
        fk = k * f * (1 + 0.0003 * k * k)
        if fk > 15000:
            break
        dk = 2.2 + 1.4 * k
        y += a * np.sin(2 * np.pi * fk * t + k) * (np.exp(-t * dk) * 0.8 + 0.2 * np.exp(-t * 0.9))   # the looped tail
    y += 0.12 * bp(noise(n), 2000, 7000) * np.exp(-t * 90)                    # hammer
    g = int(dur * SR)
    if g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.07 * SR))
    y = eq(eq(hp(y, 160), 'peak', 3100, 0.9, 5.0), 'highshelf', 7500, 0.7, 3.0)
    y = soft(y * 0.9, 1.2) * np.minimum(t / 0.001, 1) * 0.32
    return np.vstack([y, np.roll(y, 90)])


def i_accordion2(m, dur, p, glide=None, mod=None):
    """Accordion with three reeds - one in tune, one sharp and one flat (the 'wet' musette tuning of cumbia, vallenato
    and French musette), narrow-pulse reed buzz, a bellows push at the attack and a little air."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.025, 0.15, 0.9, 0.1)
    n = len(env)
    t = np.arange(n) / SR
    wet = p.get('musette', 12)
    x = np.zeros(n)
    for c, a in ((0.0, 1.0), (wet, 0.8), (-wet * 0.9, 0.8)):
        fc = f * 2 ** (c / 1200)
        x += a * (square(fc, n, pw=0.22) * 0.55 + saw(fc, n) * 0.45)
    x += 0.4 * square(f * 0.5, n, pw=0.3)                                     # the bassoon reed an octave down
    y = lp(x, p.get('cut', 4200))
    y = eq(eq(y, 'peak', 1250, 1.2, 5.0), 'peak', 2900, 2.0, 3.0)
    y += 0.03 * bp(noise(n), 800, 4000) * np.exp(-t * 6)                       # air at the bellows push
    push = 1 + 0.25 * np.exp(-t * 9) + 0.035 * np.sin(2 * np.pi * 0.7 * t)
    y = hp(y, 110) * env * push * 0.2
    return np.vstack([y, np.roll(y, 160)])


def i_bandoneon(m, dur, p, glide=None, mod=None):
    """Bandoneon (tango): two reeds an octave apart, dry (no musette beating), dark and reedy with a breathy, slightly
    plaintive attack - Piazzolla's instrument."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.05, 0.25, 0.85, 0.15)
    n = len(env)
    t = np.arange(n) / SR
    fv = vibrato(f, n, rate=5.2, cents=4, delay=0.5)
    x = square(fv, n, pw=0.33) * 0.6 + saw(fv, n) * 0.4 + 0.55 * square(fv * 0.5, n, pw=0.4)
    y = lp(x, p.get('cut', 2700))
    y = eq(eq(y, 'peak', 700, 1.0, 4.0), 'peak', 1600, 1.4, 2.0)
    y += 0.05 * bp(noise(n), 500, 2500) * np.exp(-t * 8)
    y = hp(y, 100) * env * (1 + 0.2 * np.exp(-t * 6)) * 0.24
    return np.vstack([y, np.roll(y, 110)])


def i_banjo2(m, dur, p, glide=None, mod=None):
    """5-string banjo: a steel string plucked with a metal fingerpick (sharp click, very bright), ringing through a
    drum-head bridge - nasal resonances around 400 Hz, 1.2 kHz and 3 kHz, short sustain, plenty of 'plunk'."""
    y = i_pluck(m, max(0.35, min(dur, 1.0)), dict(bright=p.get('bright', 12000), damp=0.991, r=0.12))
    n = len(y)
    t = np.arange(n) / SR
    head = bp(y, 300, 520) * 1.2 + bp(y, 1000, 1500) * 1.4 + bp(y, 2600, 3600) * 1.8 + y * 0.5
    click = hp(noise(n), 3000) * np.exp(-t * 400) * 0.25
    out = (hp(head, 180) + click) * np.exp(-t * 3.6)
    return out * 0.9


def i_pedalsteel2(m, dur, p, glide=None, mod=None):
    """Pedal steel: the volume pedal swells each note in, the bar slides up into pitch (and the pedals bend the
    neighbouring strings), with the glassy single-coil pickup and the sweet slow shimmer of a steel tone."""
    f = float(mtof(m))
    env = adsr(dur * SR, p.get('a', 0.22), 0.6, 0.9, 0.7)
    n = len(env)
    t = np.arange(n) / SR
    up = p.get('slide', -120 if (int(m) % 3) else -200)
    fv = f * 2 ** ((up * np.exp(-t * 7)) / 1200) * 2 ** ((5 * np.sin(2 * np.pi * 5.0 * t) * np.clip(t - 0.6, 0, 1)) / 1200)
    ph = 2 * np.pi * np.cumsum(fv) / SR
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.15 * np.sin(4 * ph) + 0.08 * np.sin(5 * ph)
    y = eq(eq(x, 'peak', 2300, 1.5, 4.0), 'peak', 200, 1.0, -3.0)
    y = soft(y * 0.8, 1.2) * env * 0.3
    return np.vstack([y, np.roll(y, 300)])


def i_logdrum2(m, dur, p, glide=None, mod=None):
    """Amapiano log drum (the MDU / Kabza 'yanos' log): a tuned, hollow knock - sine + soft square body that drops in
    pitch from above, a woody click, a filter that closes as it rings and a little drive; glides between notes."""
    f = float(mtof(m))
    if f < 55:
        f *= 2                                                               # it lives above the sub, around 55-110 Hz
    n = int((min(dur, 1.0) + 0.3) * SR)
    t = np.arange(n) / SR
    f_start = float(mtof(glide)) * (2 if float(mtof(glide)) < 55 else 1) if glide is not None else f * 1.9
    fr = f + (f_start - f) * np.exp(-t * (40 if glide is None else 22))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    body = np.sin(ph) + 0.35 * np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** 0.6 + 0.3 * np.sin(2 * ph) * np.exp(-t * 9)
    knock = bp(noise(n), 600, 2200) * np.exp(-t * 160) * 0.5
    y = svf_sweep(body, 300 + 2600 * np.exp(-t * 14), q=1.4) + 0.5 * np.sin(ph) + knock
    y *= np.exp(-t * p.get('decay', 4.0)) * np.minimum(t / 0.0015, 1)
    g = int(dur * SR)
    if g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.05 * SR))
    y = soft(y * 1.8, 1.8) * 0.6
    return np.vstack([y, y])


INSTRUMENTS.update({'m1piano': i_m1piano, 'accordion': i_accordion2, 'bandoneon': i_bandoneon, 'banjo': i_banjo2,
                    'pedalsteel': i_pedalsteel2, 'logdrum': i_logdrum2})
INSTRUMENT_INFO.update({'m1piano': 'House piano (M1-style)', 'bandoneon': 'Bandoneon (tango)'})
ROLE_CHOICES['chords'] += ['m1piano', 'bandoneon']
ROLE_CHOICES['lead'] += ['m1piano', 'bandoneon']
ROLE_CHOICES['arp'] += ['m1piano']
ROLE_CHOICES['pad'] += ['bandoneon']
GM_PROGRAM.update({'m1piano': 1, 'bandoneon': 23})



# =============================================================================
#  v1.38: folk & world instruments - mandolin, tin whistle, uilleann pipes, sitar, koto, tanpura; bodhrán, timbales, tabla
# =============================================================================

def i_mandolin(m, dur, p, glide=None, mod=None):
    """Mandolin: paired steel courses (two strings a few cents apart) picked hard - bright, short, metallic. Long notes are
    played the mandolin way, tremolo-picked; mod 'chop' = the bluegrass chop (a choked, percussive chord stroke)."""
    if mod == 'chop':
        y = i_pluck(m, 0.06, dict(bright=3500, damp=0.95, r=0.03))
        y = y + 0.4 * bp(noise(len(y)), 1500, 6000) * np.exp(-np.arange(len(y)) / SR * 90)
        return hp(y, 250) * 0.8
    pp = dict(bright=p.get('bright', 9000), damp=0.994, r=0.15)
    if dur > 0.6:                                         # tremolo picking: ~13 strokes a second
        step = 1 / 13.0
        n = int((dur + 0.15) * SR)
        y = np.zeros(n)
        k = 0
        while k * step < dur:
            s = int(k * step * SR)
            hit = i_pluck(m + (0.04 if k % 2 else 0.0), step + 0.05, dict(pp, r=0.05)) * (0.85 + 0.15 * (k % 2 == 0))
            y[s:s + len(hit)] += hit[:n - s]
            k += 1
    else:
        y = i_pluck(m, dur, pp) + 0.8 * i_pluck(m + 0.07, dur, pp)
    y = eq(eq(hp(y, 200), 'peak', 1100, 1.2, 4.0), 'peak', 3200, 1.5, 3.0)
    return np.vstack([y, np.roll(y, 70)]) * 0.5


def i_tinwhistle(m, dur, p, glide=None, mod=None):
    """Tin whistle / penny whistle: an almost pure tone with a breathy chiff at the start, light, late vibrato and a
    quick 'cut' (a grace note from above) on accented notes - the Irish ornament."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.02, 0.1, 0.9, 0.06)
    n = len(env)
    t = np.arange(n) / SR
    fv = vibrato(f, n, rate=5.8, cents=10, delay=0.35)
    cut = np.where(t < 0.035, 2 ** (3 / 12), 1.0) if p.get('cut', True) and dur > 0.2 else 1.0
    ph = 2 * np.pi * np.cumsum(fv * cut) / SR
    x = np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    breath = bp(noise(n), f * 1.5, min(f * 6, 16000)) * (0.25 * np.exp(-t * 30) + 0.04)
    return (x + breath) * env * 0.3


def i_pipes(m, dur, p, glide=None, mod=None):
    """Uilleann pipes chanter: a sweet, reedy double-reed tone (narrow pulse through nasal formants), bellows-blown so the
    notes join smoothly, with a soft, constant drone a couple of octaves down unless p drone=0."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.03, 0.1, 0.95, 0.08)
    n = len(env)
    t = np.arange(n) / SR
    fv = f * 2 ** ((3 * np.sin(2 * np.pi * 4.5 * t)) / 1200)
    x = square(fv, n, pw=0.18) * 0.6 + saw(fv, n) * 0.4
    y = eq(eq(eq(lp(x, 5000), 'peak', 1300, 2.0, 7.0), 'peak', 2600, 2.5, 5.0), 'peak', 400, 1.0, -4.0)
    if p.get('drone', 0.0):
        y += p['drone'] * lp(saw(f / 4, n) + 0.6 * saw(f / 4 * 1.5, n), 1200)
    return hp(y, 150) * env * 0.22


def i_drone(m, dur, p, glide=None, mod=None):
    """Bagpipe / pipe drones: tonic and fifth, buzzy reeds, never stopping (use long notes)."""
    f = float(mtof(m))
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    x = sum(a * (square(f * r * 2 ** (c / 1200), n, pw=0.3) * 0.5 + saw(f * r * 2 ** (c / 1200), n) * 0.5)
            for r, a, c in ((1.0, 1.0, 0), (1.0, 0.7, 4), (1.5, 0.5, -3), (0.5, 0.6, 2)))
    env = np.minimum(t / 0.3, 1) * np.clip((dur + 0.3 - t) / 0.3, 0, 1)
    y = eq(lp(x, 2200), 'peak', 900, 1.5, 4.0) * env * 0.1
    return np.vstack([y, np.roll(y, 200)])


def _jawari(y, amount):
    """The sitar / tanpura bridge: the string grazes a curved bridge, so its tone 'buzzes' - a level-dependent clip that
    brightens as the note decays (jawari)."""
    env = np.abs(signal.lfilter([0.002], [1, -0.998], np.abs(y))) + 1e-4
    return y + amount * np.tanh(y / (env * 0.6)) * env


def i_sitar(m, dur, p, glide=None, mod=None):
    """Sitar: a plucked steel string over the buzzing jawari bridge, a cloud of sympathetic strings ringing behind it,
    and meend - the pulled-string glide into the note (from below when glide is set, a small bend otherwise)."""
    f = float(mtof(m))
    n = int((min(dur, 3.5) + 0.8) * SR)
    t = np.arange(n) / SR
    if glide is not None:
        f0 = float(mtof(glide))
        fr = f + (f0 - f) * np.exp(-t * 9)
    else:
        fr = f * 2 ** ((-30 * np.exp(-t * 14)) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = sum(np.sin(k * ph) * (0.9 ** k) * np.exp(-t * (1.2 + 0.25 * k)) for k in range(1, 16))
    x += 0.4 * hp(noise(n), 2500) * np.exp(-t * 250)                       # the mizrab (wire plectrum)
    y = _jawari(x, p.get('buzz', 1.2))
    symp = signal.lfilter([1.0], [1.0] + [0.0] * (int(SR / (f * 2)) - 1) + [-0.6], hp(y, 1500) * 0.15)
    y = eq(hp(y + symp, 120), 'peak', 2500, 1.5, 4.0)
    g = int(dur * SR) + int(0.4 * SR)
    if g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.1 * SR))
    return np.vstack([y, np.roll(y, 150)]) * 0.12


def i_tanpura(m, dur, p, glide=None, mod=None):
    """Tanpura drone: the four strings plucked in their slow cycle (Pa, Sa, Sa, low Sa), each buzzing and ringing into
    the next - played as one long note per chord."""
    f = float(mtof(m))
    n = int((dur + 1.5) * SR)
    out = np.zeros(n)
    cyc = (1.5, 2.0, 2.0, 1.0)
    step = 0.9
    k = 0
    while k * step < dur:
        s = int(k * step * SR)
        fr = f * cyc[k % 4] / 2
        L = min(n - s, int(3.0 * SR))
        t = np.arange(L) / SR
        ph = 2 * np.pi * fr * t
        x = sum(np.sin(j * ph) * (0.85 ** j) for j in range(1, 20)) * np.exp(-t * 0.9)
        out[s:s + L] += _jawari(x, 1.5)[:L] * 0.5
        k += 1
    y = lp(hp(out, 80), 6000) * 0.09
    return np.vstack([y, np.roll(y, 240)])


def i_koto(m, dur, p, glide=None, mod=None):
    """Koto: a silk / nylon string over a movable bridge, plucked with ivory picks - a twangy, hollow attack, a quick
    pitch dip as the pick releases, and the left hand pressing the string to bend the note up a step on long notes."""
    f = float(mtof(m))
    y = i_pluck(m, min(dur, 2.5), dict(bright=6000, damp=0.995, r=0.5))
    n = len(y)
    t = np.arange(n) / SR
    if dur > 0.8 and p.get('press', True):                 # oshide: the pressed bend up after the pluck
        bend = np.clip((t - 0.45) / 0.2, 0, 1) * 1.0
        idx = np.cumsum(2 ** (bend / 12))
        idx = np.clip(idx, 0, n - 1)
        y = np.interp(idx, np.arange(n), y)
    y = eq(eq(hp(y, 140), 'peak', 600, 1.0, 4.0), 'peak', 2200, 1.6, 5.0)
    y += 0.25 * bp(noise(n), 2000, 7000) * np.exp(-t * 300)
    return np.vstack([y, np.roll(y, 90)]) * 0.55 * (1 if f else 1)


def d_bodhran(p):
    """Bodhrán: a goatskin frame drum hit with a double-ended tipper - a low, pitch-dropping boom (the hand on the back
    of the skin sets the pitch) with the tipper's dry slap."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 85)
    f = f0 * (1 + 0.35 * np.exp(-t * 25))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * p.get('decay', 9))
    y += 0.45 * bp(noise(n), 500, 3500) * np.exp(-t * 90)
    return fade_out(soft(y, 1.3), 0.03)


def d_timbale(p):
    """Timbales: shallow metal-shelled drums, hit near the rim - a high, ringing, slightly metallic 'ping' with a sharp
    stick attack. pitch ~ 500 (macho) / 380 (hembra); 'paila' = the cáscara pattern on the metal shell."""
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    if p.get('paila'):
        x = hp(noise(n), 2500) * np.exp(-t * 120) + 0.4 * np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 60)
        return fade_out(x, 0.02)
    f0 = p.get('pitch', 480)
    x = (np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * f0 * 2.31 * t) + 0.3 * np.sin(2 * np.pi * f0 * 3.7 * t)) \
        * np.exp(-t * 11)
    x += 0.6 * bp(noise(n), 2000, 9000) * np.exp(-t * 180)
    return fade_out(x, 0.05)


def d_tabla(p):
    """Tabla dayan ('na' / 'tin'): a tuned, ringing treble drum - the black syahi patch gives it harmonic overtones -
    with a short finger slap."""
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 300)
    x = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t * d) for r, a, d in ((1, 1.0, 6), (2, 0.6, 8), (3, 0.4, 11), (4, 0.25, 14)))
    x += 0.5 * bp(noise(n), 1500, 7000) * np.exp(-t * 220)
    return fade_out(x, 0.05)


def d_bayan(p):
    """Tabla bayan ('ge'): the big bass drum of the pair - a deep boom whose pitch the heel of the hand slides up."""
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 75)
    f = f0 * (1 + 0.5 * (1 - np.exp(-t * 6)))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5) + 0.2 * bp(noise(n), 300, 2000) * np.exp(-t * 60)
    return fade_out(y, 0.08)


INSTRUMENTS.update({'mandolin': i_mandolin, 'tinwhistle': i_tinwhistle, 'pipes': i_pipes, 'drone': i_drone, 'sitar': i_sitar,
                    'tanpura': i_tanpura, 'koto': i_koto})
DRUMS.update({'bodhran': d_bodhran, 'timbale': d_timbale, 'tabla': d_tabla, 'bayan': d_bayan})
INSTRUMENT_INFO.update({'mandolin': 'Mandolin', 'tinwhistle': 'Tin whistle', 'pipes': 'Uilleann pipes', 'drone': 'Pipe drones',
                        'sitar': 'Sitar', 'tanpura': 'Tanpura (drone)', 'koto': 'Koto'})
for _r, _l in (('chords', ['mandolin', 'koto', 'sitar']), ('arp', ['mandolin', 'koto', 'sitar']),
               ('lead', ['mandolin', 'tinwhistle', 'pipes', 'sitar', 'koto']), ('pad', ['drone', 'tanpura'])):
    ROLE_CHOICES[_r] += _l
GM_PROGRAM.update({'mandolin': 25, 'tinwhistle': 78, 'pipes': 109, 'drone': 109, 'sitar': 104, 'tanpura': 104, 'koto': 107})


def i_whine(m, dur, p, glide=None, mod=None):
    """G-funk 'whine': the high Minimoog lead of West Coast rap - a soft square / sine blend that glides from the note
    before (portamento) and sings with a slow, wide vibrato."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.03, 0.2, 0.9, 0.15)
    n = len(env)
    t = np.arange(n) / SR
    if glide is not None:
        f0 = float(mtof(glide))
        fr = f + (f0 - f) * np.exp(-t / p.get('porta', 0.07))
    else:
        fr = np.full(n, f)
    fr = fr * 2 ** ((p.get('vib', 22) * np.clip((t - 0.25) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.2 * t)) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = 0.7 * np.sin(ph) + 0.35 * np.sign(np.sin(ph)) * 0.5 + 0.15 * np.sin(2 * ph)
    y = lp(x, p.get('cut', 3200)) * env * 0.35
    return np.vstack([y, np.roll(y, 120)])


VOWELS = {'u': (320, 800, 2500), 'o': (450, 850, 2600), 'a': (750, 1250, 2650), 'e': (450, 1900, 2600), 'i': (300, 2300, 3000)}


def i_talkbox(m, dur, p, glide=None, mod=None):
    """Talk-box style synth (Roger Troutman / Zapp, 80s electro-funk): a bright saw + square played through moving vowel
    formants, so each note 'speaks' - opening from 'oo' to 'ah' and closing again. A synth sound, no words."""
    f = float(mtof(m))
    env = adsr(dur * SR, 0.02, 0.15, 0.9, 0.12)
    n = len(env)
    t = np.arange(n) / SR
    if glide is not None:
        fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.06)
    else:
        fr = np.full(n, f)
    fr = fr * 2 ** ((10 * np.clip((t - 0.3) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.5 * t)) / 1200)
    src = saw(fr, n) * 0.7 + square(fr, n, pw=0.3) * 0.3
    seq = p.get('vowels', ('u', 'a', 'o'))
    pos = np.clip(t / max(dur, 0.15), 0, 1) * (len(seq) - 1)
    out = np.zeros(n)
    for k in range(3):                                    # three moving formants
        fk = np.array([VOWELS[v][k] for v in seq], float)
        cut = np.interp(pos, np.arange(len(seq)), fk)
        out += svf_sweep(src, cut, q=6.0 - k * 1.2, mode='bandpass') * (1.0, 0.6, 0.35)[k]
    y = hp(out, 150) * env * 0.5
    return np.vstack([y, np.roll(y, 90)])


INSTRUMENTS.update({'whine': i_whine, 'talkbox': i_talkbox})
INSTRUMENT_INFO.update({'whine': 'G-funk whine lead (Minimoog glide)', 'talkbox': 'Talk-box style synth'})
ROLE_CHOICES['lead'] += ['whine', 'talkbox']
ROLE_CHOICES['chords'] += ['talkbox']
GM_PROGRAM.update({'whine': 80, 'talkbox': 81})


# ---------------------------------------------------------------------------------------------------------------------
#  v1.52: Hindu devotional instruments - harmonium, santoor, manjira, dholak
# ---------------------------------------------------------------------------------------------------------------------
def i_harmonium(m, dur, p, glide=None, mod=None):
    """Hand-pumped harmonium (bhajan / kirtan): free metal reeds - a bright, nasal, slightly buzzy tone with strong odd
    and even harmonics, two reed banks a few cents apart that beat gently, the bellows' breathing swell and a little
    air noise. It speaks a moment after the key goes down and holds as long as the bellows push."""
    f = float(mtof(m))
    n = int((dur + 0.12) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for det, g in ((0.0, 1.0), (p.get('beat', 4.0), 0.7)):          # two reed banks
        fr = f * 2 ** (det / 1200)
        ph = 2 * np.pi * fr * t + _rng().random() * 6.28
        for k in range(1, 18):
            if fr * k > 12000:
                break
            y += g * np.sin(k * ph) * (0.78 ** k) * (1.25 if k in (2, 3, 4) else 1.0)
    y = np.tanh(y * 0.7)                                              # the reed's buzzy clip
    y += 0.05 * bp(noise(n), 1500, 6000)                              # air through the reeds
    bellows = 1.0 + p.get('bellows', 0.06) * np.sin(2 * np.pi * 0.55 * t + _rng().random() * 6.28)
    env = adsr(int(dur * SR), 0.035, 0.1, 0.92, 0.09)
    env = np.pad(env, (0, max(0, n - len(env))))[:n]
    y = eq(hp(y * env * bellows, 110), 'peak', 1800, 1.0, 2.0) * 0.16
    return np.vstack([y, np.roll(y, 70)])


def i_santoor(m, dur, p, glide=None, mod=None):
    """Santoor: a hammered dulcimer - light walnut mallets strike groups of three or four steel strings tuned in unison.
    A clear, bell-like strike, then a shimmering string ring (the unison strings drift a few cents apart) that keeps
    sounding after the next note, so fast runs blur into a sparkling cascade."""
    f = float(mtof(m))
    ring = p.get('ring', 2.6)
    n = int((max(dur, 0.2) + ring) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    B = 0.00012                                                       # steel-string stiffness
    for j, det in enumerate((-3.5, 0.0, 3.0, 6.0)):
        fr = f * 2 ** (det / 1200)
        for k in range(1, 12):
            fk = fr * k * np.sqrt(1 + B * k * k)
            if fk > 15000:
                break
            amp = (1.0 / k ** 0.8) * (1.3 if k in (2, 3) else 1.0)
            y += amp * np.sin(2 * np.pi * fk * t + j * 1.7) * np.exp(-t * (1.1 + 0.55 * k))
    y *= 0.25
    y += 0.5 * bp(noise(n), 2500, 9000) * np.exp(-t * 120)          # the mallet tick
    y += 0.35 * np.sin(2 * np.pi * f * 4.2 * t) * np.exp(-t * 18)  # bell-like inharmonic ping on the strike
    y = eq(hp(y, 150), 'peak', 3200, 1.2, 3.0) * 0.12
    return np.vstack([y, np.roll(y, 110)]) * fade_out(np.ones(n), 0.15)


def d_manjira(p):
    """Manjira / kartal: a pair of small, thick bronze hand cymbals struck together - a bright, sweet 'ching' that rings."""
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 2650)
    x = sum(a * np.sin(2 * np.pi * f0 * r * t + r) * np.exp(-t * d)
            for r, a, d in ((1.0, 1.0, 4.5), (1.47, 0.7, 5.5), (2.09, 0.55, 6.5), (2.76, 0.4, 8), (3.51, 0.25, 9)))
    x += 0.35 * hp(noise(n), 5000) * np.exp(-t * 35)
    return fade_out(x * 0.5, 0.1)


def d_dholak(p):
    """Dholak 'dha': the two-headed folk barrel drum's bass side - a round boom the palm presses up in pitch."""
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 105)
    f = f0 * (1 + 0.35 * (1 - np.exp(-t * 9)))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + 0.25 * bp(noise(n), 200, 1500) * np.exp(-t * 80)
    return fade_out(y, 0.06)


def d_dholak_ta(p):
    """Dholak 'ta / na': the treble head slapped with the fingers - a tight, pitched crack."""
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 420)
    x = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t * d) for r, a, d in ((1, 1.0, 16), (1.6, 0.5, 22), (2.3, 0.3, 30)))
    x += 0.6 * bp(noise(n), 1200, 6000) * np.exp(-t * 150)
    return fade_out(x * 0.8, 0.04)


INSTRUMENTS.update({'harmonium': i_harmonium, 'santoor': i_santoor})
DRUMS.update({'manjira': d_manjira, 'dholak': d_dholak, 'dholak_ta': d_dholak_ta})
INSTRUMENT_INFO.update({'harmonium': 'Harmonium (bhajan / kirtan)', 'santoor': 'Santoor (hammered dulcimer)'})
ROLE_CHOICES['chords'] += ['harmonium', 'santoor']
ROLE_CHOICES['pad'] += ['harmonium']
ROLE_CHOICES['arp'] += ['santoor']
ROLE_CHOICES['lead'] += ['harmonium', 'santoor']
GM_PROGRAM.update({'harmonium': 20, 'santoor': 15})


def d_bongo(p):
    """Bongo (macho, the small drum): a bright, high finger slap with a short ring - here also standing in for the
    small hand drums of devotional percussion jams."""
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 470)
    f = f0 * (1 + 0.08 * np.exp(-t * 60))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.35 * np.sin(1.59 * ph) + 0.2 * np.sin(2.14 * ph)) * np.exp(-t * 18)
    x += 0.5 * bp(noise(n), 1500, 7000) * np.exp(-t * 170)
    return fade_out(x * 0.8, 0.03)


def d_bongo_lo(p):
    """Bongo (hembra, the bigger drum): a rounder, lower slap."""
    return d_bongo(dict(p, pitch=p.get('pitch', 330)))


DRUMS.update({'bongo': d_bongo, 'bongo_lo': d_bongo_lo})


# ---------------------------------------------------------------------------------------------------------------------
#  v1.53: world instruments - saz, oud, veena, khaen, phin, tres, gamelan; mridangam, darbuka, cajon, gong
# ---------------------------------------------------------------------------------------------------------------------
def _pluck(f, n, bright=0.9, decay=1.6, B=0.0002, partials=18, tdec=0.3):
    """A plucked string: stiff-string partials, each dying faster the higher it is."""
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(1, partials + 1):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 16000:
            break
        y += (bright ** k) / k ** 0.5 * np.sin(2 * np.pi * fk * t + k) * np.exp(-t * (decay + tdec * k))
    return y


def i_saz(m, dur, p, glide=None, mod=None):
    """Baglama / saz (Turkish long-necked lute): thin steel strings in doubled courses, plucked hard with a plectrum -
    a bright, metallic, slightly buzzy twang that rings, with the two strings of a course a few cents apart."""
    f = float(mtof(m))
    n = int((min(dur, 2.5) + 0.6) * SR)
    t = np.arange(n) / SR
    y = _pluck(f, n, 0.9, 2.2, 0.0003) + 0.8 * _pluck(f * 2 ** (4 / 1200), n, 0.9, 2.4, 0.0003)
    y = _jawari(y * 0.5, p.get('buzz', 0.5))
    y += 0.3 * hp(noise(n), 3000) * np.exp(-t * 300)
    y = eq(hp(y, 160), 'peak', 3000, 1.2, 3.0)
    g = int(dur * SR) + int(0.15 * SR)
    if g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.08 * SR))
    return np.vstack([y, np.roll(y, 120)]) * 0.11


def i_oud(m, dur, p, glide=None, mod=None):
    """Oud: the fretless, round-backed Arabic lute - gut / nylon courses plucked with a long risha: warm, dark and
    woody, a soft thump and a short, singing decay."""
    f = float(mtof(m))
    n = int((min(dur, 2.0) + 0.4) * SR)
    t = np.arange(n) / SR
    if glide is not None:
        f0 = float(mtof(glide))
        fr = f + (f0 - f) * np.exp(-t * 12)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        y = sum((0.72 ** k) / k ** 0.3 * np.sin(k * ph) * np.exp(-t * (2.5 + 0.6 * k)) for k in range(1, 12))
    else:
        y = _pluck(f, n, 0.72, 2.5, 0.0001, 12, 0.6) + 0.7 * _pluck(f * 2 ** (3 / 1200), n, 0.72, 2.6, 0.0001, 12, 0.6)
    y += 0.4 * lp(noise(n), 900) * np.exp(-t * 60)                    # the body thump
    y = eq(lp(hp(y, 90), 5000), 'peak', 250, 1.0, 3.0)
    g = int(dur * SR) + int(0.1 * SR)
    if g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.07 * SR))
    return np.vstack([y, np.roll(y, 90)]) * 0.13


def i_veena(m, dur, p, glide=None, mod=None):
    """Saraswati veena (Carnatic): a deep, rich plucked string over a big wooden resonator - like a sitar without the
    sympathetic cloud, rounder, with gamaka (the note is pressed and swung around its pitch)."""
    y = i_sitar(m - 12 if m > 72 else m, dur, dict(p, buzz=p.get('buzz', 0.55)), glide, mod)
    y = np.vstack([eq(lp(c, 4500), 'peak', 300, 1.0, 3.0) for c in y]) * 1.1
    return y


def i_khaen(m, dur, p, glide=None, mod=None):
    """Khaen (Lao / Isan mouth organ): bamboo pipes with free reeds, played as chords with a drone - a breathy,
    soft-reedy organ with a pulsing breath."""
    y = i_harmonium(m, dur, dict(p, beat=p.get('beat', 2.0), bellows=0.12))
    n = y.shape[1]
    t = np.arange(n) / SR
    puff = 1.0 + 0.18 * np.sin(2 * np.pi * p.get('pulse', 3.2) * t)      # rhythmic breathing
    return np.vstack([lp(c, 3500) * puff for c in y]) * 0.95


def i_phin(m, dur, p, glide=None, mod=None):
    """Phin (Thai / Isan electric lute): two or three metal strings, a drone string ringing along, bright and twangy -
    the sound of molam and Thai funk."""
    f = float(mtof(m))
    n = int((min(dur, 1.6) + 0.5) * SR)
    y = _pluck(f, n, 0.88, 3.0, 0.0002) + 0.35 * _pluck(f * 0.5, n, 0.8, 2.0, 0.0002)   # the drone string
    y = np.tanh(y * 1.6) * 0.7                                        # a little pickup / amp crunch
    y = eq(hp(y, 180), 'peak', 2400, 1.0, 4.0)
    g = int(dur * SR) + int(0.1 * SR)
    if g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.08 * SR))
    return np.vstack([np.roll(y, 60), y]) * 0.12


def i_tres(m, dur, p, glide=None, mod=None):
    """Cuban tres: three doubled steel courses (the middle one in octaves) - a bright, jangly, slightly out-of-unison
    pluck that drives the son montuno."""
    f = float(mtof(m))
    n = int((min(dur, 1.5) + 0.4) * SR)
    y = _pluck(f, n, 0.86, 3.2, 0.0002) + 0.75 * _pluck(f * 2 ** (6 / 1200), n, 0.86, 3.3, 0.0002) \
        + 0.4 * _pluck(f * 2, n, 0.8, 3.8, 0.0002)
    y = eq(hp(y, 140), 'peak', 2000, 1.0, 2.5)
    g = int(dur * SR) + int(0.08 * SR)
    if g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.06 * SR))
    return np.vstack([y, np.roll(y, 100)]) * 0.09


def i_gamelan(m, dur, p, glide=None, mod=None):
    """Gamelan metallophone (saron / gender): a bronze bar struck with a mallet - inharmonic bell partials and the
    'ombak', the slow beating between two instruments tuned a few hertz apart; it rings on until damped."""
    f = float(mtof(m))
    ring = p.get('ring', 2.2)
    n = int((max(dur, 0.3) + ring) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for df in (0.0, p.get('ombak', 6.0)):
        for r, a, d in ((1.0, 1.0, 0.9), (2.76, 0.45, 2.2), (5.4, 0.2, 4.5), (8.9, 0.08, 8.0)):
            y += a * np.sin(2 * np.pi * (f * r + df) * t) * np.exp(-t * d)
    y += 0.3 * bp(noise(n), 1000, 5000) * np.exp(-t * 90)
    y = hp(y, 120) * 0.1
    g = int(dur * SR) + int(0.25 * SR)
    if p.get('damp') and g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.05 * SR))
    return np.vstack([y, np.roll(y, 160)])


def d_gong(p):
    """Gong ageng: the great hanging gong - a deep, slowly swelling hum with a wobbling, shimmering bloom."""
    n = int(4.0 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 58)
    y = sum(a * np.sin(2 * np.pi * f0 * r * t * (1 - 0.004 * np.exp(-t * 2))) * np.exp(-t * d)
            for r, a, d in ((1.0, 1.0, 0.6), (2.02, 0.5, 0.9), (2.98, 0.3, 1.2), (4.1, 0.15, 1.8)))
    y *= (1 - np.exp(-t * 18)) * (1 + 0.25 * np.sin(2 * np.pi * 3.2 * t))
    return fade_out(y * 0.9, 0.5)


def d_kempul(p):
    """Kempul / kenong: the smaller hanging and kettle gongs that mark the cycle - a pitched, ringing 'nong'."""
    return d_gong(dict(p, pitch=p.get('pitch', 150)))[: int(2.0 * SR)] * fade_out(np.ones(int(2.0 * SR)), 0.3)


def d_mridangam(p):
    """Mridangam right head ('ta / nam / din'): a strongly pitched, ringing treble with clear harmonic overtones."""
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 330)
    x = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t * d) for r, a, d in ((1, 1.0, 7), (2, 0.7, 9), (3, 0.45, 12), (4, 0.3, 16)))
    x += 0.5 * bp(noise(n), 1800, 7000) * np.exp(-t * 200)
    return fade_out(x, 0.05)


def d_mridangam_lo(p):
    """Mridangam left head ('tham'): the bass side - a dull, deep thump with a short pitch rise."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 95)
    f = f0 * (1 + 0.25 * (1 - np.exp(-t * 10)))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8) + 0.3 * bp(noise(n), 150, 1200) * np.exp(-t * 70)
    return fade_out(y, 0.05)


def d_darbuka(p):
    """Darbuka 'doum': the goblet drum struck in the centre - a deep, round boom."""
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 90)
    f = f0 * (1 + 0.3 * np.exp(-t * 25))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + 0.2 * bp(noise(n), 200, 2000) * np.exp(-t * 90)
    return fade_out(y, 0.05)


def d_darbuka_tek(p):
    """Darbuka 'tek / ka': the rim struck with a finger - a sharp, bright, ringing crack."""
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 700)
    x = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t * d) for r, a, d in ((1, 1.0, 30), (1.7, 0.6, 40), (2.6, 0.4, 50)))
    x += 0.8 * bp(noise(n), 2500, 9000) * np.exp(-t * 160)
    return fade_out(x * 0.8, 0.03)


def d_cajon(p):
    """Cajon bass: the box's front struck in the middle - a woody, boomy low thud."""
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 85) * (1 + 0.5 * np.exp(-t * 30))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) + 0.35 * bp(noise(n), 100, 900) * np.exp(-t * 50)
    return fade_out(y, 0.04)


def d_cajon_slap(p):
    """Cajon slap: struck near the top edge - the snare wires behind it buzz."""
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    y = 0.6 * np.sin(2 * np.pi * 240 * t) * np.exp(-t * 30) + 0.9 * bp(noise(n), 1500, 8000) * np.exp(-t * 22)
    return fade_out(y * 0.8, 0.03)


INSTRUMENTS.update({'saz': i_saz, 'oud': i_oud, 'veena': i_veena, 'khaen': i_khaen, 'phin': i_phin, 'tres': i_tres,
                    'gamelan': i_gamelan})
DRUMS.update({'gong': d_gong, 'kempul': d_kempul, 'mridangam': d_mridangam, 'mridangam_lo': d_mridangam_lo,
              'darbuka': d_darbuka, 'darbuka_tek': d_darbuka_tek, 'cajon': d_cajon, 'cajon_slap': d_cajon_slap})
INSTRUMENT_INFO.update({'saz': 'Saz / baglama (Turkish lute)', 'oud': 'Oud', 'veena': 'Veena (Carnatic)',
                        'khaen': 'Khaen (mouth organ)', 'phin': 'Phin (Thai lute)', 'tres': 'Tres (Cuban guitar)',
                        'gamelan': 'Gamelan metallophone'})
ROLE_CHOICES['lead'] += ['saz', 'oud', 'veena', 'phin', 'gamelan']
ROLE_CHOICES['arp'] += ['saz', 'oud', 'phin', 'tres', 'gamelan']
ROLE_CHOICES['chords'] += ['tres', 'khaen']
ROLE_CHOICES['pad'] += ['khaen']
GM_PROGRAM.update({'saz': 107, 'oud': 24, 'veena': 104, 'khaen': 109, 'phin': 105, 'tres': 25, 'gamelan': 13})
