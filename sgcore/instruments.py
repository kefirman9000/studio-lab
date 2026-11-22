"""Built-in instruments: melodic synths, drum machine and FX - all synthesized from scratch."""
import numpy as np
from scipy import signal
from . import dsp
from .dsp import (SR, mtof, lp, hp, bp, eq, soft, noise, fade_out, adsr, saw, square, sine, tri,
                  filt_env, vibrato, svf_sweep)


def _rng():
    return dsp.get_rng()


def _aspirate(x, f, ph=None, tube=0.55, top=5.0):
    """Turn plain band-passed noise into breath. Hiss beside a tone sounds like white noise; real breath is air
    turbulence *inside* the instrument: it resonates in the bore (so the noise carries the note's harmonics - a comb
    tuned to the pitch), it pulses with the vibrating air jet / reed (amplitude follows each cycle of the tone), it
    wavers slowly with the player's breath, and its fizzy top is soft. Keeps the input's level and envelope."""
    x = np.asarray(x, np.float64)
    n = len(x)
    if n < 64 or not np.any(x):
        return x
    r0 = float(np.sqrt(np.mean(x ** 2)))
    y = lp(x, min(max(f * top, 2500.0), 8000.0))
    P = max(2, int(round(SR / max(f, 30.0))))
    out = y * (1 - tube)                                 # feedback comb at the note's period, done P samples at a time
    for i in range(P, n, P):
        j = min(n, i + P)
        out[i:j] += tube * out[i - P:j - P]
    if ph is None:
        ph = 2 * np.pi * f * np.arange(n) / SR
    out = out * (0.45 + 0.55 * (0.5 + 0.5 * np.cos(np.asarray(ph)[:n])))      # pitch-synchronous pulsing
    w = lp(dsp.get_rng().standard_normal(n), 5.0)
    out = out * (1 + 0.15 * np.tanh(w / (np.std(w) + 1e-9)))   # the slow waver of a real breath
    r1 = float(np.sqrt(np.mean(out ** 2)))
    return out * (r0 / (r1 + 1e-12)) * 0.85


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
    # the moving, detuned saws stay above the fundamental: down there their phasing used to cancel and reinforce the
    # sub, so the low end swelled and dropped out by ~8 dB on held notes (the bass seemed to 'break'). The sub below
    # is one steady sine.
    hpf = max(70.0, f * 1.9)
    L, R = (hp(hp(soft(v * 0.5, 2.0), hpf, 2), hpf, 2) for v in (L, R))     # 4th order: the saws' fundamental ~24 dB down
    sub = sine(f, n) * 1.3
    out = np.vstack([L + sub, R + sub]) * env
    return out


def i_808(m, dur, p, glide=None, mod=None):
    """Trap 808: a sine with a long tail and drive, sliding from the previous note. `mod` warps one note (bass-warp
    genres): 'dive' (falls up to an octave as it ends), 'rise' (shoots up an octave), 'wob:<Hz>' (a 2-3 semitone pitch
    wobble), 'growl' (warm saturation with a slow low-pass 'wah'), 'fold' (wave-folded buzz)."""
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
    if w == 'growl':                                               # a warm, saturated 808 with a slow 'wah' in the mids
        y = y + 0.25 * np.sin(2 * np.pi * np.cumsum(freq * 2) / SR) + 0.12 * np.sin(2 * np.pi * np.cumsum(freq * 3) / SR)
    elif w == 'fold':                                              # wave-folded: a buzzing, distorted 808 (switch-up 808)
        y = np.sin(2.6 * y + 0.8 * np.sin(2 * np.pi * np.cumsum(freq * 2) / SR) * np.minimum(t / 0.3, 1))
        y = y * 0.75 + 0.25 * np.sin(2 * np.pi * np.cumsum(freq) / SR)
    amp = np.exp(-t * p.get('decay', 0.9)) * np.minimum(t / 0.002, 1)
    rel = np.ones(n)
    rel[gate:] = np.linspace(1, 0, n - gate)
    drive = p.get('drive', 2.4) * (1.8 if w in ('growl', 'fold') else 1.0)
    if drive <= 3.0 and not w:
        return soft(y * amp * rel, drive)
    # heavy drive: the higher the note, the less it's driven (a hard-driven 808 an octave or two up turned into a
    # fizzy, torn-speaker buzz), distorted at 4x the sample rate so no harmonics fold back as inharmonic hash, and
    # the top end above the 808's growl rolled off
    drive = 3.0 + (drive - 3.0) * min(1.0, (55.0 / max(f, 1.0)) ** 0.7) if drive > 3.0 else drive
    up = signal.resample_poly(y * amp * rel, 4, 1)
    z = signal.resample_poly(soft(up, drive), 1, 4)[:n]
    if p.get('split') and not w:                                   # phonk: a clean sine sub under the driven growl,
        sub = lp(y * amp * rel, 110) * 0.9                         # so the low end stays solid and round while the
        mid = hp(lp(lp(z, 3800), 3800), 2.2 * f if f > 45 else 100)   # distortion lives in the mids
        return sub + mid * p.get('mid', 0.85)
    if w == 'growl':                                               # the growl: a low-pass that opens and closes
        z = _sweep_lp(z, 380, 1400, 2.2 / max(0.2, p.get('spb', 0.37) * 2))
        return z * 1.15
    return lp(lp(z, 3800), 3800)


def _sweep_lp(x, lo, hi, rate):
    """A smooth low-pass whose cutoff swings between lo and hi (Hz) at `rate` (Hz) - a vowel-like 'wah'."""
    n = len(x)
    out = np.empty(n)
    zi = np.zeros(2)
    B = 256
    for s0 in range(0, n, B):
        tt = s0 / SR
        fc = lo + (hi - lo) * (0.5 - 0.5 * np.cos(2 * np.pi * rate * tt))
        b, a = signal.butter(2, min(0.45, fc / (SR / 2)), 'low')
        out[s0:s0 + B], zi = signal.lfilter(b, a, x[s0:s0 + B], zi=zi)
    return out


def i_midbass(m, dur, p, glide=None, mod=None):
    """Mid-bass: what an 808 turns into when it's played up high in the switch-up / bass-warp genres - a round,
    saturated tone (sine with its 2nd and 3rd harmonics, softly overdriven at 4x the sample rate, two voices a few
    cents apart), low-passed so it's thick and warm instead of thin and squeaky, with a short, punchy attack."""
    f = float(mtof(m))
    gate = int(dur * SR)
    n = gate + int(0.06 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for c in (-6.0, 6.0):
        ph = 2 * np.pi * f * 2 ** (c / 1200) * t
        y += np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    amp = np.minimum(t / 0.004, 1) * (0.75 + 0.25 * np.exp(-t * 6))
    amp[gate:] *= np.linspace(1, 0, n - gate)
    up = signal.resample_poly(y * 0.5 * amp, 4, 1)
    z = signal.resample_poly(soft(up, p.get('drive', 2.2)), 1, 4)[:n]
    return lp(lp(z, p.get('cut', 1300)), p.get('cut', 1300)) * 0.9


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


def _analog_kick(p):
    """Analog drum-machine kick (909 / techno / house - since 1.72): a bridged-T style body - a sine pushed through a
    soft triangle shaper (the 909's slightly square, 'woody' tone), a two-stage pitch drop (a fast click-like sweep
    from high, then a slower settle into the note), the body HELD for a moment before it decays (an analog kick doesn't
    start fading the instant it's hit - that's the weight), the beater click (a 1 ms pulse plus a short noise burst,
    like the 909's sampled attack), and drive smoothed back down so it's fat, not fizzy."""
    n = int(p.get('len', 0.5) * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 50)
    f = f0 + p.get('punch', 140) * np.exp(-t * p.get('sweep', 40) * 1.6) + f0 * 0.9 * np.exp(-t * 14)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph)
    body = np.tanh(body * 1.6) / np.tanh(1.6) * 0.7 + 0.3 * (2 / np.pi) * np.arcsin(np.sin(ph))
    hold = p.get('hold', 0.035)
    dec = p.get('decay', 7)
    env = np.where(t < hold, 1.0, np.exp(-(t - hold) * dec)) * np.minimum(1.0, t / 0.0008)
    y = body * env
    click = np.zeros(n)
    k = int(0.001 * SR)
    click[:k] = np.hanning(2 * k)[k:]                    # the beater: a 1 ms pulse
    click = lp(click, 6000) * 3.0 + bp(noise(n), 2200, 9000) * np.exp(-t * 400) * 0.9
    y = y + click * p.get('click', 0.4)
    drv = p.get('drive', 1.8)
    y = np.tanh(y * drv) / np.tanh(drv)
    y = lp(y, 5500 + 2500 * min(1.0, p.get('click', 0.4)))
    return fade_out(y, 0.02)


def _analog_snare(p):
    """Analog snare (909-style): two shell oscillators that drop slightly in pitch as they ring (the head), and the
    'snappy' - noise through a high and a low filter with its own, longer envelope - mixed by `snap`."""
    n = int(p.get('len', 0.35) * SR)
    t = np.arange(n) / SR
    tf = p.get('tone', 185)
    drop = 1 + 0.18 * np.exp(-t * 60)
    ph1 = 2 * np.pi * np.cumsum(tf * drop) / SR
    ph2 = 2 * np.pi * np.cumsum(tf * 1.62 * drop) / SR
    shell = ((2 / np.pi) * np.arcsin(np.sin(ph1)) * 0.65 + np.sin(ph2) * 0.35) * np.exp(-t * p.get('tdecay', 24))
    nz = noise(n)
    wires = (hp(lp(nz, min(p.get('nhi', 9000), 7500)), p.get('nlo', 1500)) * 0.75 + bp(nz, 2500, 6500) * 0.45) \
        * np.exp(-t * p.get('decay', 15)) * np.minimum(1.0, t / 0.0015)
    y = shell * p.get('body', 0.7) * 1.2 + wires * p.get('snap', 1.1)
    if p.get('crack'):
        y += p['crack'] * hp(noise(n), 2500) * np.exp(-t * 600)
    return fade_out(soft(y, p.get('drive', 1.4)), 0.02)


def _analog_clap(p):
    """Analog hand clap: a band-passed noise source hit 3-4 times a few ms apart (the 'hands', each a sharp sawtooth
    envelope - slightly uneven, like real hands), then the reverb-like tail: the same noise through a narrower band,
    decaying slower. Two filter bands give the 'body' (~1.1 kHz) and the 'slap' (~2.5 kHz)."""
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    nz = noise(n)
    src = bp(nz, 800, 1600) * 0.8 + bp(nz, 1800, 3600) * 0.6
    rng = _rng()
    env = np.zeros(n)
    o = 0.0
    for _ in range(int(p.get('hands', 4)) - 1):
        on = t >= o
        env[on] += np.exp(-(t[on] - o) * 330) * (0.85 + 0.3 * rng.random())
        o += 0.0085 + 0.003 * rng.random()
    on = t >= o
    tail = np.zeros(n)
    tail[on] = np.exp(-(t[on] - o) * p.get('tail', 13))
    y = src * env + bp(nz, 900, 2200) * tail * 0.85
    return fade_out(soft(y * 1.3, 1.2), 0.03)


def _analog_hat(p, n_sec, decay):
    """Analog hi-hat: six square oscillators at inharmonic ratios (the 808 / 909 metal) through two band-passes,
    plus noise - with a 'choke-able' envelope. `tone` shifts the metal up / down; `metal` vs noise sets how
    clangy or airy it is."""
    n = int(n_sec * SR)
    t = np.arange(n) / SR
    sc = p.get('tone', 1.0) * 1.75
    m = _metallic(n, sc)
    nz = noise(n)
    metal = bp(m, 6000, 10500) * 1.4 + bp(m, 3200, 6000) * 0.4
    x = metal * p.get('metal', 0.7) + lp(hp(nz, min(p.get('hp', 7500), 6500)), 12000) * (1 - p.get('metal', 0.7) * 0.6)
    env = np.exp(-t * decay) * np.minimum(1.0, t / 0.0006)
    return fade_out(lp(hp(x, 4500), 13000) * env, 0.01)


def d_kick(p):
    if p.get('tail'):
        return d_hardkick(p)
    if p.get('model') == 'analog':
        return _analog_kick(p)
    n = int(p.get('len', 0.5) * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 48) + p.get('punch', 120) * np.exp(-t * p.get('sweep', 40))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * p.get('decay', 7))
    click = bp(noise(n), 1500, 7000) * np.exp(-t * 300) * p.get('click', 0.3)
    return fade_out(soft(body + click, p.get('drive', 1.6)), 0.02)


def d_snare(p):
    """Snare: a pitched shell tone + band-passed wire noise. Optional: crack (a hard stick transient - the crisp DnB
    snare), nlo / nhi (the wire band), tdecay (how long the shell rings), drive (a squashed, distorted neuro snare)."""
    if p.get('model') == 'analog':
        return _analog_snare(p)
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
    if p.get('model') == 'analog':
        return _analog_clap(p)
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    nz = bp(noise(n), 900, 4200)
    env = np.zeros(n)
    for k, o in enumerate((0.0, 0.009, 0.018, 0.027)):
        on = t >= o
        env[on] += np.exp(-(t[on] - o) * (220 if k < 3 else p.get('tail', 13)))
    return fade_out(nz * env, 0.02)


def d_chat(p):
    if p.get('model') == 'analog':
        return _analog_hat(p, 0.14, p.get('decay', 70))
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = hp(p.get('metal', 0.6) * _metallic(n) + 0.5 * noise(n), p.get('hp', 7000))
    return fade_out(x * np.exp(-t * p.get('decay', 70)), 0.01)


def d_ohat(p):
    if p.get('model') == 'analog':
        return _analog_hat(p, 0.7, p.get('decay', 8))
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
}
KITS['909_classic'] = {d: dict(v) for d, v in KITS['909'].items()}
KITS.update({
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
})
# v1.72: the house / techno / trance drum machines on the analog-modelled voices (held kick body, two-stage pitch drop,
# beater click; 909-style snare and clap; six-oscillator metal hats). The old sounds stay as '<kit>_classic'.
for _k in ('909', 'trance', 'techno'):
    if _k != '909':
        KITS[_k + '_classic'] = {d: dict(v) for d, v in KITS[_k].items()}
    for _d in ('kick', 'snare', 'clap', 'chat', 'ohat'):
        KITS[_k].setdefault(_d, {})
        KITS[_k][_d] = dict(KITS[_k][_d], model='analog')
# 1.97 surf 60s: a small early-60s rock kit played hard in a live room - a boomy, short kick, a bright, ringing snare
# with lots of wire rattle, and splashy, washy hats and ride (the 'Wipe Out' kit)
KITS['surf60s'] = dict(kick=dict(pitch=60, punch=55, sweep=26, decay=12, drive=1.2, len=0.36, click=0.35),
                       snare=dict(tone=215, snap=1.25, body=0.85, decay=10, tdecay=30, nlo=1600, nhi=9000, crack=0.45),
                       chat=dict(decay=38), ohat=dict(decay=4))
# 1.96 sun room: a warm, soft live-room kit for sunlit electronica - a round kick with body and only a little click,
# a warm, fairly dry snare (shell and body over sizzle, its noise kept under ~6 kHz), dark soft hats
KITS['sunroom'] = dict(kick=dict(pitch=56, punch=75, sweep=32, decay=10, drive=1.4, len=0.42, click=0.2),
                       snare=dict(tone=192, snap=0.85, body=1.05, decay=13, tdecay=24, nlo=900, nhi=6000, crack=0.2),
                       chat=dict(decay=70, hp=5500), ohat=dict(decay=7, hp=5000))
KITS['909']['kick'].update(hold=0.04, drive=1.9)
KITS['techno']['kick'].update(hold=0.05, drive=2.6)
KITS['trance']['kick'].update(hold=0.03)


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
    y = bp(src, 450, 1400) + 0.6 * bp(src, 1600, 3000) + 0.12 * _aspirate(bp(noise(n), 1500, 5000), f) * (0.4 + 0.6 * np.exp(-t * 12))
    return soft(y * env * 1.6, 1.4) * 0.5


def i_flute(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.06, 0.3, 0.85, 0.2)
    n = len(env)
    fv = vibrato(f, n, rate=5.0, cents=12, delay=0.2)
    y = sine(fv, n) + 0.12 * sine(fv * 2, n) + 0.05 * sine(fv * 3, n)
    y += 0.08 * _aspirate(bp(noise(n), f * 0.8, min(f * 3, 15000)), f)
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
    x += 0.6 * saw(f * 0.5, n)
    if in_key_interval(m, p, (7,)) is not None:                  # (1.92) the power-chord fifth only when it is in key
        x += 0.4 * saw(f * 1.5 * 2 ** (3 / 1200), n)
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
    y = bp(x, 400, 4000) + 0.12 * _aspirate(bp(noise(n), 1500, 5000), f)
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
    return _ms_stereo(y, 220) * env * 0.35


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
    return _ms_stereo(y, 90) * fade_out(np.ones(n), 0.03) * 0.42


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
INSTRUMENTS['midbass'] = i_midbass
INSTRUMENT_INFO['midbass'] = 'Mid-bass (saturated, warm - a high 808)'
ROLE_CHOICES['bass'] += ['midbass']
GM_PROGRAM['midbass'] = 38
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
    """Brostep screech: a high, harsh FM tone with a sweeping notch / formant and a pitch bend that whines up at the
    start - played an octave above the growls (only when the note is in the bass register)."""
    f = float(mtof(m)) * 2 ** p.get('octave', 1 if m < 55 else 0)
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
    return _ms_stereo(y, 90)


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
    return _ms_stereo(y, 160)


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
    return _ms_stereo(y, 110)


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
    return _ms_stereo(y, 300)


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
    return _ms_stereo(y, 70) * 0.5


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
    breath = _aspirate(bp(noise(n), f * 1.5, min(f * 6, 16000)), f, ph) * (0.25 * np.exp(-t * 30) + 0.04)
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
    return _ms_stereo(y, 200)


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
    return _ms_stereo(y, 150) * 0.12


def i_tanpura(m, dur, p, glide=None, mod=None):
    """Tanpura drone: the four strings plucked in their slow cycle (Pa, Sa, Sa, low Sa), each buzzing and ringing into
    the next - one long note per chord, or (mod 'str:<0-3>') a single string, plucked by the arranger on the beat."""
    f = float(mtof(m))
    one = isinstance(mod, str) and mod.startswith('str:')   # the arranger plucks one string per beat, on the grid
    n = int(max(dur + 1.5, 3.05 if one else 0) * SR)
    out = np.zeros(n)
    first = 1.5 if in_key_interval(m, p, (7,)) is not None else 4 / 3       # (1.92) Pa, or Ma when Pa is out of key
    cyc = (first, 2.0, 2.0, 1.0)
    gains = (0.9, 1.0, 1.0, 0.45)                     # the low Sa string stays soft: a drone, not a bass line
    step = float(p.get('step', 0.9))
    k = int(mod[4:]) if one else 0
    while (k * step < dur) if not one else k == int(mod[4:]):
        s = 0 if one else int(k * step * SR)
        fr = f * cyc[k % 4] / 2
        L = min(n - s, int(3.0 * SR))
        t = np.arange(L) / SR
        ph = 2 * np.pi * fr * t
        x = sum(np.sin(j * ph) * (0.85 ** j) for j in range(1, 20)) * np.exp(-t * 0.9)
        out[s:s + L] += _jawari(x, 1.5)[:L] * 0.5 * gains[k % 4]
        k += 1
    y = lp(hp(out, 80), 6000) * 0.09
    return _ms_stereo(y, 240)


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
    return _ms_stereo(y, 90) * 0.55 * (1 if f else 1)


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
    return _ms_stereo(y, 120)


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
    return _ms_stereo(y, 90)


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
    return _ms_stereo(y, 70)


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
    return _ms_stereo(y, 110) * fade_out(np.ones(n), 0.15)


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
    return _ms_stereo(y, 120) * 0.11


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
    return _ms_stereo(y, 90) * 0.13


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
    return _ms_stereo(y, 100) * 0.09


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
    return _ms_stereo(y, 160)


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


def i_shakuhachi(m, dur, p, glide=None, mod=None):
    """Shakuhachi - the end-blown bamboo flute, and the famous 80s sampler version of it: a loud, breathy 'chiff' as the
    note speaks (an overblown puff that jumps up and falls in), the pitch scooping up into the note from a little
    below (meri-kari), a hollow tone with lots of air, and a slow, wide vibrato that blooms on held notes."""
    f = float(mtof(m))
    n = int((dur + 0.25) * SR)
    t = np.arange(n) / SR
    scoop = p.get('scoop', 1.0)
    cents = -110 * scoop * np.exp(-t * 9)                             # meri: starts flat, rises into the note
    if glide is not None:
        cents = cents + (float(glide) - m) * 100 * np.exp(-t * 10)
    vib = np.clip((t - 0.28) / 0.45, 0, 1) * p.get('vib', 28) * np.sin(2 * np.pi * 5.0 * t + 0.4 * np.sin(2 * np.pi * 0.6 * t))
    fr = f * 2 ** ((cents + vib) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph) + 0.03 * np.sin(5 * ph)
    over = 0.55 * np.sin(2 * ph + 0.7) * np.exp(-t * 22)              # the overblown puff an octave up as it speaks
    air = _aspirate(bp(noise(n), f * 0.9, min(f * 4.5, 16000)), f, ph, tube=0.4) * (0.32 + 0.9 * np.exp(-t * 14))   # breath, strongest at the chiff
    env = adsr(dur * SR, 0.035, 0.25, 0.82, 0.18)
    env = np.pad(env, (0, max(0, n - len(env))))[:n]
    breath = 1 + 0.08 * np.sin(2 * np.pi * 0.9 * t)
    y = (tone * breath + over + air) * env
    y = eq(hp(y, max(120, f * 0.6)), 'peak', 1400, 1.0, 2.5) * 0.5
    return _ms_stereo(y, 90)


def i_qanun(m, dur, p, glide=None, mod=None):
    """Qanun: the Arabic plucked zither - three nylon strings per note, plucked with metal finger picks: a bright,
    harp-like twang with a quick, singing decay; held notes are played as a fast tremolo (rapid re-plucking)."""
    f = float(mtof(m))
    n = int((min(dur, 2.5) + 0.8) * SR)

    def one(n_):
        t_ = np.arange(n_) / SR
        y_ = sum(_pluck(f * 2 ** (c / 1200), n_, 0.8, 2.2, 0.00008, 14, 0.5) for c in (-3.0, 0.0, 2.5)) / 3
        return y_ + 0.25 * bp(noise(n_), 3000, 9000) * np.exp(-t_ * 140)   # the pick
    y = np.zeros(n)
    trem = dur >= float(p.get('trem_min', 0.9)) and p.get('tremolo', True)
    gap = 0.075 if trem else dur + 1
    k = 0
    while k * gap < max(dur, 0.01) and k < 64:
        s = int(k * gap * SR)
        y[s:] += one(n - s) * (1.0 if k == 0 else 0.55)
        k += 1
    y = eq(hp(y, 110), 'peak', 2400, 1.0, 2.0) * 0.16
    return _ms_stereo(y, 70) * fade_out(np.ones(n), 0.1)


def i_ney(m, dur, p, glide=None, mod=None):
    """Ney: the end-blown reed flute of Arabic, Turkish and Persian music - mostly breath: a soft, hollow, husky tone
    with a lot of air in it, a gentle swell into each note and a slow, deep vibrato on long notes."""
    f = float(mtof(m))
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    cents = -45 * np.exp(-t * 7)
    if glide is not None:
        cents = cents + (float(glide) - m) * 100 * np.exp(-t * 9)
    vib = np.clip((t - 0.4) / 0.6, 0, 1) * p.get('vib', 22) * np.sin(2 * np.pi * 4.6 * t)
    fr = f * 2 ** ((cents + vib) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    tone = np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    air = _aspirate(bp(noise(n), f * 0.8, min(f * 6, 15000)), f, ph, tube=0.3) * (0.5 + 0.4 * np.exp(-t * 9))
    env = adsr(dur * SR, 0.09, 0.2, 0.9, 0.22)
    env = np.pad(env, (0, max(0, n - len(env))))[:n]
    y = (tone * 0.8 + air) * env * (1 + 0.1 * np.sin(2 * np.pi * 0.7 * t))
    y = eq(hp(y, max(100, f * 0.55)), 'peak', 900, 0.9, 2.0) * 0.45
    return _ms_stereo(y, 120)


def d_riq(p):
    """Riq: the Arabic tambourine - a tight fish-skin head and five pairs of heavy brass jingles: a crisp, silvery
    shimmer with a dry 'tak' on the skin."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    j = hp(_metallic(n, 4.3) + 0.5 * noise(n), 5000) * np.exp(-t * 11) * (1 + 0.5 * np.sin(2 * np.pi * 33 * t))
    skin = np.sin(2 * np.pi * p.get('pitch', 420) * t) * np.exp(-t * 45) * 0.5
    return fade_out((j + skin) * 0.8, 0.04)


def d_bendir(p):
    """Bendir / daf: the big frame drum of Sufi music - a deep, soft 'dum' from the middle of the skin, with the snare
    strings stretched under it buzzing."""
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 70) * (1 + 0.25 * np.exp(-t * 20))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5)
    y += 0.35 * bp(noise(n), 300, 3000) * np.exp(-t * 9) * (1 + 0.6 * np.sin(2 * np.pi * 47 * t))   # the buzz
    return fade_out(y, 0.06)


def d_bendir_tek(p):
    """Bendir edge stroke: fingers near the rim - a higher, slapped 'tek' with the buzz."""
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    y = 0.6 * np.sin(2 * np.pi * 330 * t) * np.exp(-t * 28) + 0.7 * bp(noise(n), 800, 5000) * np.exp(-t * 25)
    return fade_out(y * 0.8, 0.03)


INSTRUMENTS.update({'qanun': i_qanun, 'ney': i_ney})
DRUMS.update({'riq': d_riq, 'bendir': d_bendir, 'bendir_tek': d_bendir_tek})
INSTRUMENT_INFO.update({'qanun': 'Qanun (Arabic zither)', 'ney': 'Ney (breathy reed flute)'})
ROLE_CHOICES['lead'] += ['qanun', 'ney']
ROLE_CHOICES['arp'] += ['qanun', 'ney']
GM_PROGRAM.update({'qanun': 46, 'ney': 77})

INSTRUMENTS['shakuhachi'] = i_shakuhachi
INSTRUMENT_INFO['shakuhachi'] = 'Shakuhachi (breathy bamboo flute / 80s sampler)'
ROLE_CHOICES['lead'] += ['shakuhachi']
ROLE_CHOICES['arp'] += ['shakuhachi']
GM_PROGRAM['shakuhachi'] = 77


# ----------------------------------------------------------------------------- 1.57: the built-in analog synth
# The classic synth sounds are rebuilt on one virtual-analog voice (sgcore/va.py): band-limited oscillators with
# unison and drift, a resonant 24 dB low-pass with its own envelope, analog-style envelopes. Same names and the same
# track parameters (cut / a / d / s / r ...), so every genre that uses them sounds better at once. The previous
# versions stay available as '<name>_v1'.
from . import va as _va  # noqa: E402


def _ms_stereo(y, d, k=0.35):
    """(1.82) Mono-safe stereo from a mono note: a delayed, high-passed copy goes into the SIDE (left +, right -), so
    left + right gives back the note exactly - no comb filter in mono. (The old way - the right channel a copy delayed
    by d samples - hollowed notes out on phones / club systems in mono.) Classic synth character keeps the old way."""
    y = np.asarray(y, float)
    if _va.CHARACTER == 'classic':
        return np.vstack([y, np.roll(y, d)])
    if d <= 0:
        return np.vstack([y, y])
    dl = np.concatenate([np.zeros(d), y[:-d]]) if d < len(y) else np.zeros_like(y)
    side = hp(dl, 300) * k
    return np.vstack([y + side, y - side])


def _oct(lo, hi):
    return float(np.log2(max(hi, 1.0) / max(lo, 1.0)))


def v_warmpad(m, dur, p, glide=None, mod=None):
    """Juno-style pad: saw + slowly moving pulse + sub, three detuned voices, a soft resonant filter that opens as
    the pad swells in."""
    return _va.voice(m, dur, dict(p, cut=p.get('cut', 1100) * 0.7), glide, saw_mix=0.9, pulse_mix=0.45, pwm=0.6, pwm_rate=0.45,
                     sub=0.2, unison=3, detune=9, spread=0.8, res=0.12, fenv=0.6, fa=p.get('a', 1.2) * 1.1, fd=2.0, fs=1.0,
                     amp=(1.2, 1.0, 0.85, 2.0), drive=1.05, keytrack=0.3) * 0.42


def v_polysynth(m, dur, p, glide=None, mod=None):
    """Prophet-style poly: saw + pulse, two detuned voices, filter envelope 'bwow' on each chord."""
    top = p.get('cut', 1800) * 1.6
    fenv = 1.8
    return _va.voice(m, dur, dict(p, cut=top / 2 ** fenv), glide, saw_mix=1.0, pulse_mix=0.6, pw=0.42, unison=2, detune=7,
                     res=0.28, fenv=fenv, fd=p.get('fdecay', 0.4) * 1.2, fs=0.35, amp=(0.006, 0.35, 0.7, 0.35),
                     drive=1.25, keytrack=0.4) * 0.4


def v_supersaw(m, dur, p, glide=None, mod=None):
    """Supersaw: seven saws spread wide in pitch and stereo, bright, high-passed so the low end stays clean."""
    return _va.voice(m, dur, dict(p, cut=p.get('cut', 3000) * 1.6), glide, saw_mix=1.0, unison=7, detune=34, spread=1.0,
                     res=0.08, amp=(0.25, 0.6, 0.85, 0.6), drive=1.1, keytrack=0.2, hp=140) * 0.5


def v_leadsaw(m, dur, p, glide=None, mod=None):
    """Mono saw lead: saw + a touch of pulse, gentle unison, glide, delayed vibrato, a filter that bites on the attack."""
    top = p.get('cut', 5000)
    return _va.voice(m, dur, dict(p, cut=top / 2), glide, saw_mix=1.0, pulse_mix=0.3, unison=2, detune=6, res=0.25,
                     fenv=1.0, fd=0.28, fs=0.0, vib=p.get('vib', 14), amp=(0.004, 0.3, 0.85, 0.15), drive=1.3,
                     keytrack=0.5) * 0.5


def v_softlead(m, dur, p, glide=None, mod=None):
    """Soft square lead (the 'sine-ish' synth melody of chillwave / synthpop): hollow, rounded, slow vibrato."""
    return _va.voice(m, dur, dict(p, cut=p.get('cut', 3000) * 0.8), glide, saw_mix=0.2, pulse_mix=1.0, pw=0.5, unison=1,
                     res=0.12, fenv=0.6, fd=0.25, fs=0.0, vib=p.get('vib', 18), vib_rate=5.0, amp=(0.03, 0.3, 0.85, 0.3),
                     drive=1.05, keytrack=0.4) * 0.7


def v_pluck_saw(m, dur, p, glide=None, mod=None):
    """Synth pluck: saw + pulse with the filter snapping shut - the arp sound of house, trance and chillwave."""
    top = p.get('cut', 6000)
    fenv = _oct(320, top)
    return _va.voice(m, dur, dict(p, cut=320), glide, saw_mix=1.0, pulse_mix=0.3, unison=2, detune=8, res=0.3, fenv=fenv,
                     fd=5.0 / p.get('fdecay', 14), fs=0.0, amp=(0.002, p.get('d', 0.3), p.get('s', 0.15), 0.14),
                     drive=1.2, keytrack=0.6) * 0.62


def v_stab(m, dur, p, glide=None, mod=None):
    """Chord stab: bright saws through a filter that closes fast - house / rave / dub-techno stabs."""
    top = p.get('cut', 5000)
    fenv = _oct(260, top)
    return _va.voice(m, dur, dict(p, cut=260), glide, saw_mix=1.0, pulse_mix=0.5, unison=2, detune=10, res=0.32, fenv=fenv,
                     fd=5.0 / p.get('fdecay', 20), fs=0.0, amp=(0.002, p.get('d', 0.22), p.get('s', 0.2), 0.08),
                     drive=1.3, keytrack=0.5) * 0.55


def v_sawbass(m, dur, p, glide=None, mod=None):
    """Saw bass: saw + sub-octave square, a filter envelope with some resonance, driven."""
    if p.get('reverse'):
        return INSTRUMENTS['sawbass_v1'](m, dur, p, glide, mod)
    top = p.get('cut', 2200)
    fenv = _oct(170, top)
    y = _va.voice(m, dur, dict(p, cut=170), glide, saw_mix=1.0, sub=0.55, unison=1, res=0.3, fenv=fenv,
                  fd=5.0 / p.get('fdecay', 16), fs=0.1, amp=(p.get('a', 0.003), p.get('d', 0.18), p.get('s', 0.6), 0.05),
                  drive=1.7, keytrack=0.3, drift=1.0, stereo=False)
    return y * 0.5


def v_moogbass(m, dur, p, glide=None, mod=None):
    """Minimoog-style bass: two saws a few cents apart + square sub, a fat resonant ladder-ish filter that settles."""
    if p.get('pluck'):
        return v_moogpluck(m, dur, p, glide, mod)
    cut = p.get('cut', 500)
    sus = p.get('fsus', 0.55)
    return _va.voice(m, dur, dict(p, cut=cut * 0.9), glide, saw_mix=1.0, pulse_mix=0.5, pw=0.5, sub=0.35, unison=2,
                     detune=5, spread=0.0, res=0.38, fenv=_oct(cut * 0.9, cut * 3.5), fd=p.get('fd', 0.3), fs=sus,
                     amp=(p.get('a', 0.004), p.get('d', 0.35), p.get('s', 0.88), p.get('r', 0.08)), drive=1.9,
                     keytrack=0.0, drift=1.5, stereo=False, hp=30) * 0.55


def v_moogpluck(m, dur, p, glide=None, mod=None):
    """Plucked Moog bass (G-funk / boogie): the same fat oscillators, but the filter snaps shut after the attack."""
    cut = p.get('cut', 500)
    return _va.voice(m, dur, dict(p, cut=cut * 0.35), glide, saw_mix=1.0, pulse_mix=0.5, sub=0.35, unison=2, detune=5,
                     spread=0.0, res=0.35, fenv=_oct(cut * 0.35, cut * 3.5), fd=p.get('fd', 0.12), fs=0.0,
                     amp=(0.003, 0.4, 0.5, 0.06), drive=1.9, keytrack=0.0, drift=1.5, stereo=False, hp=30) * 0.6


def v_epiano(m, dur, p, glide=None, mod=None):
    """DX7 electric piano (FM): warm body and the bright 'tine' bark on the attack, tremolo."""
    return _va.fm_epiano(m, dur, p, glide)


for _name, _fn in (('warmpad', v_warmpad), ('polysynth', v_polysynth), ('supersaw', v_supersaw), ('leadsaw', v_leadsaw),
                   ('softlead', v_softlead), ('pluck_saw', v_pluck_saw), ('stab', v_stab), ('sawbass', v_sawbass),
                   ('moogbass', v_moogbass), ('moogpluck', v_moogpluck), ('epiano', v_epiano)):
    INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.57)'
    for _role, _lst in ROLE_CHOICES.items():                   # the old sound stays pickable next to the new one
        if _name in _lst and _name + '_v1' not in _lst:
            _lst.append(_name + '_v1')
    GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)


# ----------------------------------------------------------------------------- 1.58: more of the analog synth
def v_organ(m, dur, p, glide=None, mod=None):
    """Tonewheel organ: drawbar registration, key click, decaying percussion, tube drive and a two-rotor rotary
    speaker (see va.tonewheel). Old drawbar lists ('bars') still play the classic sound."""
    if p.get('bars'):
        return INSTRUMENTS['organ_v1'](m, dur, p, glide, mod)
    return _va.tonewheel(m, dur, p)


def v_synthbrass(m, dur, p, glide=None, mod=None):
    """Synth brass (OB / Prophet): detuned saws + a sub, the filter swelling open on each note and settling - the
    'brass' of 80s anthems and synthwave."""
    top = p.get('cut', 3200)
    return _va.voice(m, dur, dict(p, cut=top / 3.0), glide, saw_mix=1.0, sub=0.3, unison=3, detune=12, spread=0.6, res=0.18,
                     fenv=1.6, fa=0.07, fd=0.5, fs=0.55, amp=(p.get('a', 0.05), 0.4, 0.8, 0.25), drive=1.35,
                     keytrack=0.4, hp=90) * 0.45


def v_synclead(m, dur, p, glide=None, mod=None):
    """Hard-sync lead: a slave saw synced to the note, its pitch swept by an envelope - the tearing, vocal 80s / synthwave
    lead - with a little unison, glide and delayed vibrato."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.004, 0.3, 0.85, p.get('r', 0.2))
    n = len(env)
    t = np.arange(n) / SR
    fr = np.full(n, f)
    if glide is not None:
        fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.06)
    fr = fr * 2 ** (np.clip((t - 0.3) / 0.35, 0, 1) * p.get('vib', 14) * np.sin(2 * np.pi * 5.3 * t) / 1200)
    ratio = 1.0 + p.get('sweep', 2.6) * np.exp(-t / p.get('sweep_t', 0.35)) + 0.6
    a = _va.sync_saw(fr, ratio, n)
    b = _va.sync_saw(fr * 2 ** (8 / 1200), ratio * 1.01, n, 0.3)
    y = _va.vcf(np.vstack([a + 0.4 * b, b + 0.4 * a]), p.get('cut', 6000), 0.15, 1.3)
    return y * env * 0.4


def v_mellotron(m, dur, p, glide=None, mod=None):
    """Tape-replay keyboard (Mellotron strings / flute): a bowed or breathy tone recorded to tape - a soft swell in, the
    tape's wow and flutter, a little hiss, a narrow, dusty band - and every note runs out after about 8 seconds."""
    flute = p.get('voice', 'strings') == 'flute'
    f = float(mtof(m))
    d = min(max(dur, 0.05), 8.0)
    gate = int(d * SR)
    env = _va.adsr(gate, 0.09 if not flute else 0.06, 0.4, 0.9, 0.25)
    n = len(env)
    t = np.arange(n) / SR
    wow = 2 ** ((6 * np.sin(2 * np.pi * 0.55 * t + _rng().random() * 6) + 2.5 * np.sin(2 * np.pi * 7.5 * t)) / 1200)
    fr = f * wow
    if flute:
        x = np.sin(2 * np.pi * np.cumsum(fr) / SR) + 0.15 * np.sin(4 * np.pi * np.cumsum(fr) / SR)
        x += 0.25 * bp(noise(n), f, min(f * 5, 12000)) * (0.5 + 0.5 * np.exp(-t * 6))
    else:
        x = sum(_va.saw(fr * 2 ** (c / 1200), n, _rng().random()) for c in (-7.0, 0.0, 6.0)) / 3
        x = _va.formant(x, 'a', 3.0) * 2.2 + 0.25 * x
    x = bp(x, 180 if not flute else 250, 6500) + 0.01 * noise(n)
    y = x * env
    return _ms_stereo(y, 120) * (0.5 if flute else 0.6)


def v_dxbell(m, dur, p, glide=None, mod=None):
    """DX7 bell / tine: the bright, glassy FM bell of 80s ballads, city pop and synthpop."""
    return _va.fm_bell(m, dur, dict(p, index=p.get('index', 3.0), ratio=p.get('ratio', 3.5)), glide)


def v_vocalpad(m, dur, p, glide=None, mod=None):
    """Synth choir 'aah' pad: soft detuned saws through vowel formants, a slow swell and a gentle vibrato - the wordless
    vocal pad of chillwave, downtempo and 80s ballads."""
    y = _va.voice(m, dur, dict(p, cut=p.get('cut', 4500)), glide, saw_mix=1.0, unison=4, detune=14, spread=0.8, res=0.0,
                  vib=10, vib_rate=4.8, vib_delay=0.4, amp=(p.get('a', 0.5), 0.6, 0.9, p.get('r', 1.2)), drive=1.0,
                  keytrack=0.0)
    return _va.formant(y, p.get('vowel', 'a'), 5.0) * 1.3


for _name, _fn, _info, _roles in (
        ('organ', v_organ, None, None), ('synthbrass', v_synthbrass, None, None),
        ('synclead', v_synclead, 'Sync lead (80s hard-sync synth)', ('lead',)),
        ('mellotron', v_mellotron, 'Mellotron strings (tape keyboard)', ('chords', 'pad', 'lead')),
        ('dxbell', v_dxbell, 'DX bell (FM)', ('arp', 'lead', 'chords')),
        ('vocalpad', v_vocalpad, 'Synth choir "aah" pad', ('pad', 'chords'))):
    if _name in INSTRUMENTS and _info is None:
        INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
        INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.58)'
        for _role, _lst in ROLE_CHOICES.items():
            if _name in _lst and _name + '_v1' not in _lst:
                _lst.append(_name + '_v1')
        GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)
    INSTRUMENTS[_name] = _fn
    if _info:
        INSTRUMENT_INFO[_name] = _info
        for _role in _roles:
            if _name not in ROLE_CHOICES[_role]:
                ROLE_CHOICES[_role].append(_name)
GM_PROGRAM.update({'synclead': 81, 'mellotron': 49, 'dxbell': 14, 'vocalpad': 54})
INSTRUMENTS['mellotron_flute'] = lambda m, dur, p, glide=None, mod=None: v_mellotron(m, dur, dict(p, voice='flute'), glide, mod)
INSTRUMENT_INFO['mellotron_flute'] = 'Mellotron flute (tape keyboard)'
ROLE_CHOICES['lead'].append('mellotron_flute')
ROLE_CHOICES['arp'].append('mellotron_flute')
GM_PROGRAM['mellotron_flute'] = 73


# ----------------------------------------------------------------------------- 1.59: trance + bass-music synths
from . import va_bass as _vb  # noqa: E402


def _hpf(y, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high')
    return signal.lfilter(b, a, y, axis=-1)


def v2_supersaw(m, dur, p, glide=None, mod=None):
    """JP-8000 supersaw chords: seven saws at the original's offsets and detune curve, wide, a soft filter, high-passed
    so the chords leave the low end to the bass."""
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.25), 0.6, 0.85, p.get('r', 0.6))
    n = len(env)
    x = _va.jp_supersaw(float(mtof(m)), n, p.get('detune', 0.5) * 0.9, 0.75)
    y = _va.vcf(x, p.get('cut', 3000) * 1.8, 0.1, 1.1)
    return _hpf(y, 160) * env * 0.6


def v2_supersaw_lead(m, dur, p, glide=None, mod=None):
    """The trance lead, layered the way producers stack it: a JP supersaw body, a second, wider supersaw for the mids, an
    octave-up layer high-passed for the 'air', and a whisper of high-passed noise for sparkle - with glide, delayed
    vibrato and a filter that opens on every note. Long hall + stereo delay come from the track."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.004, 0.25, 0.85, p.get('r', 0.3))
    n = len(env)
    t = np.arange(n) / SR
    fr = np.full(n, f)
    if glide is not None:
        fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.05)
    fr = fr * 2 ** (np.clip((t - 0.3) / 0.35, 0, 1) * p.get('vib', 12) * np.sin(2 * np.pi * 5.2 * t) / 1200)
    body = _va.jp_supersaw(fr, n, 0.45, 0.65, 0.7)
    mids = _va.jp_supersaw(fr * 1.0015, n, 0.7, 0.85, 1.0)
    air = _hpf(_va.jp_supersaw(fr * 2, n, 0.55, 0.8, 1.0), 3500, 2) * 0.22
    noise_ = _hpf(np.random.default_rng().standard_normal((2, n)), 7000, 2) * 0.04
    fe = 0.6 + 0.4 * np.exp(-t * 5)
    top = p.get('cut', 9000)
    x = _va.vcf(body + 0.8 * mids, top * fe, 0.12, 1.15) + air + noise_
    return _hpf(x, 180) * env * 0.5


def v_trancepad(m, dur, p, glide=None, mod=None):
    """Trance pad: a slow-attack JP supersaw bed with the filter breathing on a slow LFO, very wide - built to be
    sidechained and trance-gated."""
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.6), 1.0, 0.9, p.get('r', 1.5))
    n = len(env)
    t = np.arange(n) / SR
    x = _va.jp_supersaw(float(mtof(m)), n, 0.6, 0.8, 1.0)
    cut = p.get('cut', 2200) * (1 + 0.5 * np.sin(2 * np.pi * 0.12 * t - 1.5))
    return _hpf(_va.vcf(x, cut, 0.15, 1.05), 150) * env * 0.55


def v_rollbass(m, dur, p, glide=None, mod=None):
    """Rolling trance bass: saw + square an octave apart with a short pluck envelope and a snappy filter - the 16th-note
    offbeat bass that rolls between the kicks (sidechained to them by the track)."""
    return _va.voice(m, dur, dict(p, cut=p.get('cut', 260)), glide, saw_mix=1.0, pulse_mix=0.5, sub=0.4, unison=1, res=0.3,
                     fenv=2.6, fd=0.12, fs=0.15, amp=(0.002, 0.16, 0.35, 0.04), drive=1.6, keytrack=0.3, drift=0.5,
                     stereo=False, hp=35) * 0.6


def v_superpluck(m, dur, p, glide=None, mod=None):
    """Supersaw pluck: the JP stack with the filter snapping shut - the trance / future-rave arp."""
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.002, 0.28, 0.1, 0.18)
    n = len(env)
    t = np.arange(n) / SR
    x = _va.jp_supersaw(float(mtof(m)), n, 0.4, 0.7, 0.9)
    cut = 350 * (p.get('cut', 7000) / 350) ** np.exp(-t * p.get('fdecay', 12))
    return _hpf(_va.vcf(x, cut, 0.25, 1.15), 150) * env * 0.65


for _name, _fn, _info, _roles in (
        ('supersaw', v2_supersaw, None, None), ('supersaw_lead', v2_supersaw_lead, None, None),
        ('wobble', _vb.wobble, None, None), ('growl', _vb.growl, None, None), ('reese', _vb.reese, None, None),
        ('riddim', _vb.riddim, None, None), ('screech', _vb.screech, None, None), ('hoover', _vb.hoover, None, None),
        ('trancepad', v_trancepad, 'Trance pad (supersaw, breathing filter)', ('pad', 'chords')),
        ('rollbass', v_rollbass, 'Rolling trance bass (offbeat 16ths)', ('bass',)),
        ('superpluck', v_superpluck, 'Supersaw pluck (trance arp)', ('arp', 'lead')),
        ('neuro', _vb.neuro, 'Neuro bass (torn-up reese)', ('bass',)),
        ('houseorgan', _vb.house_organ, 'House organ stab (M1-style)', ('chords', 'arp', 'lead'))):
    if _info is None:
        if _name + '_v1' not in INSTRUMENTS:
            INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
            INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.59)'
            for _role, _lst in ROLE_CHOICES.items():
                if _name in _lst and _name + '_v1' not in _lst:
                    _lst.append(_name + '_v1')
            GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)
        else:                                                     # supersaw already moved to the analog voice in 1.57
            INSTRUMENTS[_name + '_v2'] = INSTRUMENTS[_name]
    else:
        INSTRUMENT_INFO[_name] = _info
        for _role in _roles:
            if _name not in ROLE_CHOICES[_role]:
                ROLE_CHOICES[_role].append(_name)
    INSTRUMENTS[_name] = _fn
GM_PROGRAM.update({'trancepad': 90, 'rollbass': 38, 'superpluck': 81, 'neuro': 39, 'houseorgan': 17})


# ----------------------------------------------------------------------------- 1.60: the classic-hardware voices
def _q01(r):
    """Old acid params give resonance as a filter Q (5..10); the new voices take 0..1."""
    r = float(r)
    return float(np.clip((r - 3.0) / 7.0, 0.15, 0.92)) if r > 1.5 else r


def v_acid303(m, dur, p, glide=None, mod=None):
    """TB-303: one saw (or the 303's lopsided square) into an 18 dB resonant low-pass. The decay knob sets the filter
    envelope; accented notes get a louder VCA, a short fixed decay and the accent circuit's extra cutoff 'wow' that grows
    with resonance; slid notes glide over ~60 ms with no new attack - the filter envelope carries on instead of
    re-triggering, which is the 'squelch' of a slide."""
    acc = bool(mod)
    slide = glide is not None
    f = float(mtof(m))
    gate = int(max(dur, 0.02) * SR)
    n = gate + int(0.012 * SR)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.06) if slide else np.full(n, f)
    if p.get('wave', 'saw') == 'saw':
        x = _va.saw(fr, n)
    else:
        x = _va.pulse(fr, n, 0.0, 0.45) * 0.85 + _va.saw(fr, n) * 0.15
    res = _q01(p.get('res', 0.7))
    envmod = p.get('envmod', 0.6)
    envmod = envmod / 9.0 if envmod > 1.5 else envmod           # old param: a multiplier around 6
    dec = 0.2 if acc else p.get('decay', 0.5)
    env = np.exp(-t / dec) * (0.35 if slide else 1.0)
    octs = envmod * 4.2 * env
    if acc:                                                      # the accent "sweep" capacitor
        bump = (1 - np.exp(-t / 0.012)) * np.exp(-t / 0.22)
        octs = octs + (0.7 + 1.6 * res) * bump
    cut = p.get('cut', 380) * 0.85 * 2 ** octs
    y = _va.vcf18(x, cut, res, 1.3 + (0.5 if acc else 0.0))
    amp = np.exp(-t / 3.0) * (1.45 if acc else 1.0)
    if not slide:
        amp *= np.minimum(t / 0.003, 1)
    amp[gate:] *= np.exp(-np.arange(n - gate) / (0.004 * SR))
    return _hpf(np.tanh(y * amp * 1.4) * 0.62, 28)


def v_junopad(m, dur, p, glide=None, mod=None):
    """Juno-106 pad: one rock-steady DCO (saw + slowly modulated pulse + square sub), the high-pass, a gentle 24 dB
    filter that swells open with the pad, then the stereo BBD chorus II that makes the Juno sound."""
    x = _va.voice(m, dur, dict(p, cut=p.get('cut', 1500) * 0.6), glide, saw_mix=0.85, pulse_mix=0.5, pwm=0.7,
                  pwm_rate=0.5, sub=0.3, unison=1, drift=0.0, res=0.15, fenv=0.8, fa=p.get('a', 0.9), fd=1.8, fs=0.85,
                  amp=(0.9, 1.0, 0.9, 1.6), drive=1.05, keytrack=0.35, stereo=False, hp=70)
    return _va.juno_chorus(x, p.get('chorus', 2), 0.55) * 0.4


def v_junopoly(m, dur, p, glide=None, mod=None):
    """Juno-106 poly chord: the same DCO with a quick filter 'blip' and chorus I - the house / garage / synth-pop
    chord and stab patch."""
    x = _va.voice(m, dur, dict(p, cut=p.get('cut', 1600) * 0.5), glide, saw_mix=1.0, pulse_mix=0.45, pw=0.4, sub=0.2,
                  unison=1, drift=0.0, res=0.22, fenv=1.6, fd=p.get('fd', 0.22), fs=0.35, amp=(0.003, 0.45, 0.6, 0.25),
                  drive=1.15, keytrack=0.4, stereo=False, hp=90)
    return _va.juno_chorus(x, p.get('chorus', 1), 0.5) * 0.45


def v_junobass(m, dur, p, glide=None, mod=None):
    """Juno-106 bass: narrow pulse + square sub through a plucky resonant filter, no chorus - the round, rubbery
    house / deep house bass."""
    return _va.voice(m, dur, dict(p, cut=p.get('cut', 300)), glide, saw_mix=0.3, pulse_mix=1.0, pw=0.3, sub=0.6,
                     unison=1, drift=0.0, res=0.3, fenv=2.2, fd=p.get('fd', 0.16), fs=0.2, amp=(0.002, 0.3, 0.7, 0.05),
                     drive=1.4, keytrack=0.2, stereo=False, hp=30) * 0.4


def v_jupiterpad(m, dur, p, glide=None, mod=None):
    """Jupiter-8 pad: two saw VCOs per voice, gently out of tune and drifting, into the warm 24 dB filter with a slow
    swell, a lighter chorus - the lush 80s pad."""
    x = _va.voice(m, dur, dict(p, cut=p.get('cut', 1800) * 0.55), glide, saw_mix=1.0, pulse_mix=0.25, sub=0.12,
                  unison=2, detune=11, spread=0.0, drift=2.5, res=0.2, fenv=1.0, fa=p.get('a', 1.0) * 1.2, fd=2.5,
                  fs=0.8, amp=(1.0, 1.0, 0.9, 1.8), drive=1.1, keytrack=0.3, stereo=False, hp=60)
    return _va.juno_chorus(x, 1, 0.35) * 0.48


def v_obstab(m, dur, p, glide=None, mod=None):
    """OB-Xa brass: two bright saws per voice a few cents apart through the open, barely resonant filter, a fast swell
    on each chord - the big 80s rock / synth-pop keyboard stab."""
    return _va.voice(m, dur, dict(p, cut=p.get('cut', 2600) * 0.7), glide, saw_mix=1.0, pulse_mix=0.3, pw=0.45, sub=0.1,
                     unison=2, detune=9, spread=0.7, drift=2.0, res=0.1, fenv=1.3, fa=0.012, fd=0.35, fs=0.55,
                     amp=(p.get('a', 0.004), 0.5, 0.78, 0.22), drive=1.45, keytrack=0.4, hp=80) * 0.42


def v_moog_lead(m, dur, p, glide=None, mod=None):
    """Minimoog lead: three oscillators (two saws a few cents apart + a square an octave down) overdriving the mixer
    into the resonant ladder filter, glide, and the mod-wheel vibrato coming in late."""
    top = p.get('cut', 2400)
    return _va.voice(m, dur, dict(p, cut=top / 2.3), glide, saw_mix=1.0, sub=0.45, unison=2, detune=6, spread=0.0,
                     drift=2.0, res=0.45, fenv=1.2, fd=0.35, fs=0.4, amp=(0.004, 0.3, 0.9, 0.12), drive=2.1,
                     vib=p.get('vib', 18), vib_delay=0.35, slide=0.08, keytrack=0.6, stereo=False, hp=60) * 0.5


def v_hypersaw(m, dur, p, glide=None, mod=None):
    """Virus-style hypersaw: two supersaw stacks a few cents apart (fourteen saws), a sub, high-passed and wide - the
    huge 2000s trance / electro / big-room chord and lead."""
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.008), 0.4, 0.85, p.get('r', 0.3))
    n = len(env)
    f = float(mtof(m))
    x = _va.jp_supersaw(f * 2 ** (-7 / 1200), n, 0.55, 0.75, 1.0) + _va.jp_supersaw(f * 2 ** (7 / 1200), n, 0.55, 0.75, 1.0)
    x = x * 0.75 + _va.saw(np.full(n, f / 2), n)[None, :] * 0.18
    return _hpf(_va.vcf(x, p.get('cut', 5200), 0.1, 1.1), 130) * env * 0.5


def v_dxbass(m, dur, p, glide=None, mod=None):
    """DX7 solid bass: a sine carrier phase-modulated 1:1 with an index that snaps from bright to round, a little
    operator feedback for edge, and a sine sub - the 80s funk / pop FM bass."""
    f = float(mtof(m))
    gate = int(max(dur, 0.02) * SR)
    env = _va.adsr(gate, 0.002, 0.6, 0.55, 0.06)
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.05) if glide is not None else np.full(n, f)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    idx = p.get('index', 2.6) * np.exp(-t * 10) + 0.7
    modu = np.sin(ph + 0.4 * np.sin(ph))                         # feedback-ish modulator
    y = np.sin(ph + idx * modu) * 0.8 + np.sin(ph) * 0.35
    return np.tanh(y * 1.2) * env * 0.6


for _name, _fn, _info, _roles in (
        ('acid', v_acid303, None, None),
        ('junopad', v_junopad, 'Juno pad (DCO + BBD chorus)', ('pad', 'chords')),
        ('junopoly', v_junopoly, 'Juno poly chords (house / synth-pop)', ('chords', 'arp')),
        ('junobass', v_junobass, 'Juno bass (round house bass)', ('bass',)),
        ('jupiterpad', v_jupiterpad, 'Jupiter pad (lush 80s)', ('pad', 'chords')),
        ('obstab', v_obstab, 'OB brass stab (big 80s chords)', ('chords', 'lead')),
        ('moog_lead', v_moog_lead, 'Mono analog lead (3-osc ladder)', ('lead',)),
        ('hypersaw', v_hypersaw, 'Hypersaw (14 saws, chords / leads)', ('chords', 'lead', 'pad')),
        ('dxbass', v_dxbass, 'FM solid bass (80s funk / pop)', ('bass',))):
    if _info is None:
        if _name + '_v1' not in INSTRUMENTS:
            INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
            INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.60)'
            for _role, _lst in ROLE_CHOICES.items():
                if _name in _lst and _name + '_v1' not in _lst:
                    _lst.append(_name + '_v1')
            GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)
    else:
        INSTRUMENT_INFO[_name] = _info
        for _role in _roles:
            if _name not in ROLE_CHOICES[_role]:
                ROLE_CHOICES[_role].append(_name)
    INSTRUMENTS[_name] = _fn
GM_PROGRAM.update({'junopad': 89, 'junopoly': 90, 'junobass': 38, 'jupiterpad': 89, 'obstab': 62, 'moog_lead': 81,
                   'hypersaw': 81, 'dxbass': 39})


# ----------------------------------------------------------------------------- 1.61: real-sounding basses
def _rs(seed=None):
    return np.random.default_rng(seed)


def _bass_exc(f, kind='finger', bright=1.0):
    """How the string is set moving: a finger rolls off it (soft, round), a pick flicks it (bright click), a slapping
    thumb or a popped finger hits it hard against the frets (bright, plus clank). The excitation is shaped like the
    string at the plucking point (a comb at that fraction of its length)."""
    P = SR / f
    L = max(8, int(P))
    rng = _rs()
    cut, beta, amp = {'finger': (1800, 0.2, 1.0), 'pick': (6000, 0.1, 1.0), 'thumb': (8000, 0.3, 1.3),
                      'pop': (10000, 0.08, 1.2), 'upright': (900, 0.3, 1.1)}[kind]
    x = np.arange(L) / L
    k = max(1, int(beta * L))
    tri_ = np.where(np.arange(L) < k, x / beta, (1 - x) / (1 - beta))     # a finger pulls the string into a triangle
    w = {'finger': 0.06, 'pick': 0.03, 'thumb': 0.035, 'pop': 0.015, 'upright': 0.1}[kind]
    d = (x - beta + 0.5) % 1.0 - 0.5
    hit = np.exp(-0.5 * (d / w) ** 2)                                     # a pick / thumb / pop strikes it: a narrow pulse
    mix = {'finger': 0.35, 'pick': 0.6, 'thumb': 0.9, 'pop': 0.9, 'upright': 0.15}[kind]
    tri_ = tri_ / (np.abs(tri_ - tri_.mean()).max() + 1e-9)
    hit = hit / (np.abs(hit - hit.mean()).max() + 1e-9)
    shape = (1 - mix) * tri_ + mix * hit
    shape = shape - shape.mean() + 0.06 * rng.uniform(-1, 1, L)
    bl, al = signal.butter(2, min(0.45, cut * bright / (SR / 2)))
    burst = signal.lfilter(bl, al, np.tile(shape, 3))[L:2 * L]   # (circular: the shape wraps along the string)
    burst = burst - burst.mean()
    return burst / (np.abs(burst).max() + 1e-9) * amp


def _glide_curve(y, f, glide, t_s=0.06):
    """Bend a rendered note from the previous note's pitch into its own (a slide up / down the neck)."""
    if glide is None:
        return y
    f0 = float(mtof(glide))
    n = len(y)
    t = np.arange(n) / SR
    ratio = (f + (f0 - f) * np.exp(-t / t_s)) / f
    pos = np.cumsum(ratio) - ratio[0]
    return np.interp(pos, np.arange(n), y, right=0.0)


def _bass_string(m, dur, p, glide, kind, t60, bright, pickup, release=0.12, comp=0.0):
    f = float(mtof(m))
    gate = int(max(dur, 0.04) * SR)
    n = gate + int(release * SR)
    y = _va.string(f, n, _bass_exc(f, kind, p.get('tone', 1.0)), t60=t60 * (55.0 / max(f, 30)) ** 0.35, bright=bright,
                   gate=gate, mute_t60=p.get('mute', 0.09), pickup=pickup)
    y = _glide_curve(y, f, glide)
    if comp:                                                     # the bassist's compressor: the note holds its level
        e = np.sqrt(signal.lfilter([0.002], [1, -0.998], y * y) + 1e-9)
        e = np.maximum(e, e.max() * 0.04)
        gn = np.minimum((e / e.max()) ** (-comp), 4.0)
        gn[gate:] = gn[gate - 1] if gate > 0 else 1.0
        y = y * gn
    return y, f, n, gate


def v_ebass(m, dur, p, glide=None, mod=None):
    """Electric finger bass (P / J style): a waveguide string plucked by a finger, read by a pickup near the bridge
    (the hollow, punchy midrange), muted by the fretting hand at the end of the note, then the DI / amp tone - a
    round low end, a little 800 Hz growl, the top rolled off - and gentle compression."""
    y, f, n, gate = _bass_string(m, dur, p, glide, 'finger', 11.0, 0.62, 0.13, comp=0.7)
    t = np.arange(n) / SR
    y = y + 0.12 * np.sin(2 * np.pi * f * t) * np.exp(-t * 1.2) * np.minimum(t / 0.004, 1)   # body under the pickup
    y = eq(eq(hp(y, 35), 'peak', 85, 0.9, 3.0), 'peak', 800, 1.2, p.get('growl', 2.5))
    y = lp(y, p.get('bright', 1400) * 2.6)
    y = np.tanh(y * 1.6) / 1.6
    y[gate:] *= np.exp(-np.arange(n - gate) / (0.03 * SR))
    return y * 0.6


def v_pickbass(m, dur, p, glide=None, mod=None):
    """Picked electric bass: the pick's bright click and a mid-forward, slightly grindy tone - rock, punk, post-punk,
    new wave, motown-style pick lines."""
    y, f, n, gate = _bass_string(m, dur, p, glide, 'pick', 5.0, 0.75, 0.1, comp=0.55)
    t = np.arange(n) / SR
    y = y + 0.25 * hp(_rs().standard_normal(n), 2500) * np.exp(-t * 350)                   # the pick on the string
    y = eq(eq(hp(y, 40), 'peak', 100, 0.9, 2.0), 'peak', 1300, 1.0, 3.5)
    y = lp(y, p.get('bright', 2000) * 2.8)
    y = np.tanh(y * 2.2) / 2.0
    y[gate:] *= np.exp(-np.arange(n - gate) / (0.025 * SR))
    return y * 1.05


def v_slapbass(m, dur, p, glide=None, mod=None):
    """Slap bass: low notes thumbed (a hard, bright thud with the string clanking on the frets), high notes popped
    (a sharp snap), the classic scooped funk tone. `mod='pop'` forces a pop."""
    pop = mod == 'pop' or (mod is None and m >= 50)
    y, f, n, gate = _bass_string(m, dur, p, glide, 'pop' if pop else 'thumb', 3.0, 0.92, 0.12, comp=0.4)
    t = np.arange(n) / SR
    clank = bp(_rs().standard_normal(n), 1800, 6000) * np.exp(-t * (120 if pop else 70)) * (0.5 if pop else 0.4)
    y = y + clank
    y = eq(eq(eq(hp(y, 35), 'peak', 70, 0.9, 4.0), 'peak', 550, 1.0, -4.0), 'peak', 3000, 1.0, 4.0)   # the scoop
    y = np.tanh(y * 2.0) / 1.8
    y[gate:] *= np.exp(-np.arange(n - gate) / (0.02 * SR))
    return y * 0.92


def v_fretless(m, dur, p, glide=None, mod=None):
    """Fretless bass: no frets to stop the string, so notes slide and sing - a softer attack, a long singing sustain
    and the 'mwah' as the string buzzes on the fingerboard, slides between notes."""
    y, f, n, gate = _bass_string(m, dur, p, None, 'finger', 9.0, 0.55, 0.15, comp=0.7)
    t = np.arange(n) / SR
    y = _glide_curve(y, f, glide, 0.11)
    mw = 1200 + 900 * np.exp(-t * 3.5)                            # the mwah: a moving mid formant
    y = y + 0.5 * _va.vcf(y, mw, 0.55, 1.0) * np.exp(-t * 1.5)
    y = lp(eq(hp(y, 35), 'peak', 90, 0.9, 2.5), 4200)
    y = np.tanh(y * 1.5) / 1.5
    y[gate:] *= np.exp(-np.arange(n - gate) / (0.05 * SR))
    return y * 0.5


def v_upright(m, dur, p, glide=None, mod=None):
    """Upright (double) bass, pizzicato: a long, heavy gut string plucked with the side of the finger near the end of
    the fingerboard - a woody thump, a big low body resonance, a quick bloom that settles into a soft sustain - jazz,
    swing, bluegrass, rockabilly, folk."""
    y, f, n, gate = _bass_string(m, max(dur, 0.25), p, glide, 'upright', 3.0, 0.4, 0.0, release=0.18, comp=0.3)
    t = np.arange(n) / SR
    thump = 0.5 * np.sin(2 * np.pi * f * t) * np.exp(-t * 9) * np.minimum(t / 0.003, 1)
    finger = 0.12 * bp(_rs().standard_normal(n), 300, 1500) * np.exp(-t * 90)              # the finger on the string
    y = y + thump + finger
    y = eq(eq(eq(hp(y, 32), 'peak', 95, 1.1, 3.0), 'peak', 210, 1.4, 2.5), 'peak', 650, 1.2, 2.5)  # the box resonances
    y = lp(y, p.get('bright', 900) * 2.6)
    y = np.tanh(y * 1.3) / 1.3
    g = int(max(dur, 0.25) * SR)
    y[g:] *= np.exp(-np.arange(n - g) / (0.06 * SR))
    return y * 0.68


def v_sinebass(m, dur, p, glide=None, mod=None):
    """Warm sine bass: a pure, phase-continuous sine that can slide between notes, a soft click-free attack, and a
    touch of tube-like saturation so its 2nd / 3rd harmonics let it be heard on small speakers."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.006), p.get('d', 0.5), p.get('s', 0.8), p.get('r', 0.08))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.05) if glide is not None else np.full(n, f)
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR)
    sat = p.get('sat', 1.0)
    y = np.tanh(x * (1.0 + 0.9 * sat) + 0.15 * sat) - np.tanh(0.15 * sat)                   # asymmetric: 2nd harmonic
    ph_ = np.linspace(0, 2 * np.pi, 512, endpoint=False)                                     # (2.5.3) minus the DC the
    y = y - np.mean(np.tanh(np.sin(ph_) * (1.0 + 0.9 * sat) + 0.15 * sat) - np.tanh(0.15 * sat))   # asymmetry makes: it
    y = lp(y / np.tanh(1.0 + 0.9 * sat), p.get('cut', 700) * 1.4)                           # thumped on/off every note
    return y * env * 0.95


def v_sawbass(m, dur, p, glide=None, mod=None):
    """Analog saw bass: saw + square sub into a resonant 24 dB filter with a punchy envelope, glide, a little drive."""
    if p.get('reverse'):
        return INSTRUMENTS['sawbass_v1'](m, dur, p, glide, mod)
    cut = p.get('cut', 2200)
    return _va.voice(m, dur, dict(p, cut=150), glide, saw_mix=1.0, pulse_mix=0.0, sub=0.55, unison=2, detune=4,
                     spread=0.0, res=0.25, fenv=_oct(150, cut), fd=1.0 / max(4.0, p.get('fdecay', 16)) * 4,
                     fs=0.25, amp=(p.get('a', 0.003), p.get('d', 0.18), p.get('s', 0.6), 0.05), drive=1.7,
                     keytrack=0.25, drift=1.0, stereo=False, hp=30) * 0.62


for _name, _fn, _info, _roles in (
        ('ebass', v_ebass, None, None), ('upright', v_upright, None, None), ('sinebass', v_sinebass, None, None),
        ('sawbass', v_sawbass, None, None),
        ('pickbass', v_pickbass, 'Picked electric bass', ('bass',)),
        ('slapbass', v_slapbass, 'Slap bass (thumb + pop)', ('bass',)),
        ('fretless', v_fretless, 'Fretless bass', ('bass', 'lead'))):
    if _info is None:
        if _name + '_v1' not in INSTRUMENTS:
            INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
            INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.61)'
            for _role, _lst in ROLE_CHOICES.items():
                if _name in _lst and _name + '_v1' not in _lst:
                    _lst.append(_name + '_v1')
            GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)
    else:
        INSTRUMENT_INFO[_name] = _info
        for _role in _roles:
            if _name not in ROLE_CHOICES[_role]:
                ROLE_CHOICES[_role].append(_name)
    INSTRUMENTS[_name] = _fn
GM_PROGRAM.update({'pickbass': 34, 'slapbass': 36, 'fretless': 35})


# ----------------------------------------------------------------------------- 1.62: more wobbles + techno voices
for _name, _fn, _info, _roles, _gm in (
        ('dnbwob', _vb.dnb_wobble, 'DnB wobble (fast, rolling)', ('bass',), 39),
        ('vowelwob', _vb.vowel_wobble, 'Vocal wobble (talking "yoy")', ('bass',), 39),
        ('multiwob', _vb.multi_wobble, 'Multiband wobble (layered drop)', ('bass',), 39),
        ('tablewob', _vb.table_wobble, 'Wavetable wobble (morphing)', ('bass',), 39),
        ('chopwob', _vb.chop_wobble, 'Chop wobble (stuttering, crushed)', ('bass',), 39),
        ('rumble', _vb.rumble, 'Techno rumble bass', ('bass',), 38),
        ('dubstab', _vb.dub_stab, 'Dub-techno chord stab', ('chords', 'arp'), 81),
        ('technoseq', _vb.techno_seq, 'Techno sequence (evolving blips)', ('arp', 'lead'), 81),
        ('darkpad', _vb.dark_pad, 'Dark techno pad (evolving)', ('pad', 'chords'), 89),
        ('atmos', _vb.atmosphere, 'Atmosphere / texture', ('pad',), 99)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


def v_emolead(m, dur, p, glide=None, mod=None):
    """Emotional trance lead: the softer, singing variation of the supersaw lead - a gently detuned supersaw blended
    with a round triangle, a small scoop up into each note, a vibrato that deepens as the note is held and a filter
    that opens over the length of the note, so long notes bloom instead of hitting hard."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.015), 0.5, 0.82, p.get('r', 0.45))
    n = len(env)
    t = np.arange(n) / SR
    fr = np.full(n, f)
    if glide is not None:
        fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.07)
    else:
        fr = fr * 2 ** (-35 * np.exp(-t / 0.05) / 1200)           # the scoop
    fr = fr * 2 ** (np.clip((t - 0.25) / 0.6, 0, 1) * p.get('vib', 16) * np.sin(2 * np.pi * 5.0 * t) / 1200)
    body = _va.jp_supersaw(fr, n, 0.3, 0.55, 0.8)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    tri_ = (2 / np.pi * np.arcsin(np.sin(ph)))[None, :] * 0.5
    cut = p.get('cut', 4500) * (0.45 + 0.55 * (1 - np.exp(-t / 0.5)))
    x = _va.vcf(body + tri_, cut, 0.15, 1.1)
    return _hpf(x, 200) * env * 0.42


INSTRUMENTS['emolead'] = v_emolead
INSTRUMENT_INFO['emolead'] = 'Emotional trance lead (soft supersaw, blooms)'
ROLE_CHOICES['lead'].append('emolead')
GM_PROGRAM['emolead'] = 81


# ----------------------------------------------------------------------------- 1.63: melodic / deep house voices
def v_deepbass(m, dur, p, glide=None, mod=None):
    """Deep rolling house bass: a clean sine sub under two softly detuned saws through a low, gently resonant filter
    with a small 'bow' on each note, a little tape-warm saturation - round and warm, never buzzy, built for the
    off-beat 16ths that roll between the kicks (the track's sidechain pumps it)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.004, p.get('d', 0.35), p.get('s', 0.75), p.get('r', 0.07))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.04) if glide is not None else np.full(n, f)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    sub = np.sin(ph)
    mid = (_va.saw(fr * 2 ** (-6 / 1200), n) + _va.saw(fr * 2 ** (6 / 1200), n, 0.4)) * 0.5
    cut = p.get('cut', 420) * (1 + 1.2 * np.exp(-t / 0.09))
    mid = _va.vcf(mid, cut, 0.22, 1.3)
    y = np.tanh((sub * 0.9 + mid * p.get('body', 0.7)) * 1.4) / 1.25
    return hp(y, 28) * env * 0.62


def v_mhpluck(m, dur, p, glide=None, mod=None):
    """Melodic-house pluck: saw + square a few cents apart, softened by a low-pass that falls from warm to dark over a
    quarter of a second, a gentle chorus - the round, woody pluck that carries the melody and the delayed arps (not the
    bright, glassy trance pluck)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.002, p.get('d', 0.45), 0.08, p.get('r', 0.25))
    n = len(env)
    t = np.arange(n) / SR
    x = _va.saw(np.full(n, f * 2 ** (-4 / 1200)), n) * 0.7 + _va.pulse(np.full(n, f * 2 ** (4 / 1200)), n, 0.3, 0.45) * 0.5
    cut = 260 * (p.get('cut', 3200) / 260) ** np.exp(-t / p.get('fdecay', 0.16))
    y = _va.vcf(x, cut, 0.18, 1.1)
    return _va.juno_chorus(hp(y, 120), 1, 0.35) * env * 0.62


def v_lushpad(m, dur, p, glide=None, mod=None):
    """Lush house pad: a soft supersaw bed and a warm string-ensemble layer swelling in together, a dark filter that
    opens slowly as the chord is held, wide chorus - the emotional bed under breakdowns, made to breathe with the kick."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = _va.adsr(gate, p.get('a', 0.9), 1.5, 0.9, p.get('r', 1.6))
    n = len(env)
    t = np.arange(n) / SR
    ss = _va.jp_supersaw(f, n, 0.35, 0.6, 0.8)
    strings = _va.voice(m, max(dur, 0.1), dict(cut=1800), None, saw_mix=1.0, pulse_mix=0.3, pwm=0.6, unison=3, detune=10,
                        spread=0.9, res=0.1, amp=(0.01, 1.0, 1.0, 0.5), drive=1.0, keytrack=0.3, hp=90)[:, :n]
    if strings.shape[1] < n:
        strings = np.pad(strings, ((0, 0), (0, n - strings.shape[1])))
    cut = p.get('cut', 2400) * (0.35 + 0.65 * (1 - np.exp(-t / 1.6)))
    y = _va.vcf(ss * 0.8 + strings * 0.6, cut, 0.12, 1.05)
    return _va.juno_chorus(_hpf(y, 110), 1, 0.3) * env * 0.5


def v_breathlead(m, dur, p, glide=None, mod=None):
    """Breathy lead: a round triangle / sine tone with breath noise shaped like the note, a soft scoop into each note and
    a slow, late vibrato - the airy, flute-like synth melody of melodic and organic house."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.035), 0.4, 0.8, p.get('r', 0.3))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.06) if glide is not None else f * 2 ** (-25 * np.exp(-t / 0.04) / 1200)
    fr = np.broadcast_to(fr, (n,)) * 2 ** (np.clip((t - 0.35) / 0.5, 0, 1) * p.get('vib', 14) * np.sin(2 * np.pi * 4.8 * t) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    tone = 2 / np.pi * np.arcsin(np.sin(ph)) * 0.7 + np.sin(ph) * 0.4 + 0.12 * np.sin(2 * ph)
    breath = _aspirate(bp(_rng().standard_normal(n), f * 1.5, min(9000.0, f * 8)), f, ph) * (0.25 + 0.5 * np.exp(-t / 0.08))
    y = lp(tone + breath * p.get('breath', 0.5), 5000)
    return _ms_stereo(y, 40) * env * 0.5


for _name, _fn, _info, _roles, _gm in (
        ('deepbass', v_deepbass, 'Deep rolling house bass', ('bass',), 38),
        ('mhpluck', v_mhpluck, 'Melodic house pluck (warm, woody)', ('arp', 'lead', 'chords'), 84),
        ('lushpad', v_lushpad, 'Lush house pad (supersaw + strings swell)', ('pad', 'chords'), 89),
        ('breathlead', v_breathlead, 'Breathy flute-like synth lead', ('lead',), 75)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


def v_techstab(m, dur, p, glide=None, mod=None):
    """Tech-trance riff synth: two saws a little apart plus a square an octave down, through a resonant filter that
    snaps from bright to dark in under a tenth of a second, driven - the punchy, syncopated synth riff of 2000s club
    trance remixes (it rides the trance gate and a dotted delay)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.002, p.get('d', 0.18), p.get('s', 0.35), p.get('r', 0.08))
    n = len(env)
    t = np.arange(n) / SR
    x = np.vstack([_va.saw(np.full(n, f * 2 ** (-12 / 1200)), n), _va.saw(np.full(n, f * 2 ** (12 / 1200)), n, 0.3)])
    x = x + _va.pulse(np.full(n, f / 2), n, 0.1, 0.5)[None, :] * 0.45
    cut = 320 * (p.get('cut', 6500) / 320) ** np.exp(-t / p.get('fdecay', 0.07))
    y = _va.vcf(x, cut, p.get('res', 0.35), 1.6)
    return _hpf(y, 150) * env * 0.5


INSTRUMENTS['techstab'] = v_techstab
INSTRUMENT_INFO['techstab'] = 'Tech-trance riff synth (punchy, gated)'
GM_PROGRAM['techstab'] = 81
for _role in ('lead', 'arp', 'chords'):
    ROLE_CHOICES[_role].append('techstab')


def v_bouncebass(m, dur, p, glide=None, mod=None):
    """Bouncing liquid / dancefloor DnB mid-bass: saw + square an octave apart through a resonant filter that kicks open
    on every note and settles ('bwow'), a touch of drive, with a mono sine sub underneath - round, musical and
    bouncy, for the big-chord, piano-and-vocal side of drum & bass."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.003, p.get('d', 0.3), p.get('s', 0.7), p.get('r', 0.06))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.05) if glide is not None else np.full(n, f)
    fo = fr * (1 if f > 55 else 2)
    x = _va.saw(fo * 2 ** (-5 / 1200), n) * 0.6 + _va.saw(fo * 2 ** (5 / 1200), n, 0.5) * 0.6 + _va.pulse(fo * 2, n, 0.2, 0.4) * 0.3
    cut = p.get('cut', 700) * (1 + 3.0 * np.exp(-t / p.get('fdecay', 0.12)))
    if p.get('lfo'):                                              # the moving liquid / dancefloor bass: an 8th-note
        spb = p.get('spb', 0.35)                                  # filter LFO inside a slow one-bar sweep
        fast = 0.5 - 0.5 * np.cos(2 * np.pi * t / (float(p['lfo']) * spb))
        slow = 0.5 - 0.5 * np.cos(2 * np.pi * t / (float(p.get('sweep', 4)) * spb))
        cut = cut * (0.45 + 0.9 * fast) * (0.6 + 0.8 * slow)
    mid = _vb.dist(_va.vcf(x, cut, 0.4, 1.4), 1.8)
    mid = _vb._split_hp(mid, f)
    sub = np.sin(2 * np.pi * np.cumsum(fr * (1 if f < 70 else 0.5)) / SR)
    y = mid * p.get('mid', 0.7) + sub * 0.8
    return np.vstack([y, y]) * env * 0.55


def v_pianosaw(m, dur, p, glide=None, mod=None):
    """Anthem keys: a bright piano doubled by a soft, wide supersaw that swells in under it - the big chord sound of
    euphoric drum & bass and pop-dance drops (the piano's attack, the supersaw's size)."""
    pn = np.asarray(INSTRUMENTS['piano'](m, dur, p, None, None), float)
    pn = np.vstack([pn, pn]) if pn.ndim == 1 else pn
    n = pn.shape[1]
    t = np.arange(n) / SR
    ss = _va.jp_supersaw(float(mtof(m)), n, 0.45, 0.65, 1.0)
    sw = (1 - np.exp(-t / 0.08)) * np.exp(-np.maximum(t - dur, 0) / 0.25)
    ss = _hpf(_va.vcf(ss, p.get('cut', 3800), 0.1, 1.05), 160) * sw
    return pn * 0.85 + ss * 0.32


INSTRUMENTS['bouncebass'] = v_bouncebass
INSTRUMENT_INFO['bouncebass'] = 'Bouncing DnB mid-bass (+ sub)'
INSTRUMENTS['pianosaw'] = v_pianosaw
INSTRUMENT_INFO['pianosaw'] = 'Anthem keys (piano + supersaw)'
GM_PROGRAM.update({'bouncebass': 39, 'pianosaw': 1})
ROLE_CHOICES['bass'].append('bouncebass')
ROLE_CHOICES['chords'].append('pianosaw')
ROLE_CHOICES['arp'].append('pianosaw')


# ----------------------------------------------------------------------------- 1.64: vocal chops, future-bass chords, lo-fi keys
_CHOP_VOWELS = {'a': (800, 1200, 2700), 'o': (500, 850, 2600), 'e': (450, 2000, 2700), 'u': (330, 800, 2400),
                'i': (300, 2300, 3000)}


def v_vocalchop(m, dur, p, glide=None, mod=None):
    """Vocal chop: a short sung syllable cut from a 'vocal' - a breathy glottal tone through three vowel formants, the
    vowel picked from the note (so a chopped phrase moves between 'ah', 'oh', 'eh', 'oo', 'ee'), a quick scoop and a
    hard, clean cut at the end - the pitched vocal-chop hook of house, future bass, tropical house and DnB."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.6), 0.05) * SR)
    env = _va.adsr(gate, 0.006, 0.12, 0.85, 0.02)
    n = len(env)
    t = np.arange(n) / SR
    vow = p.get('vowel') or 'aoeui'[int(m) % 5]
    fr = f * 2 ** (-40 * np.exp(-t / 0.03) / 1200) * 2 ** (6 * np.sin(2 * np.pi * 5.5 * t) / 1200)
    ph = np.cumsum(fr) / SR
    src = (2 * (ph % 1.0) - 1.0)
    src = signal.lfilter([1.0], [1, -0.7], src) * 0.5 + _rng().standard_normal(n) * 0.06
    y = 0
    for (fc, g, bw) in zip(_CHOP_VOWELS[vow], (1.0, 0.6, 0.3), (90, 120, 180)):
        b, a = signal.iirpeak(min(fc, SR * 0.45) / (SR / 2), fc / bw)
        y = y + g * signal.lfilter(b, a, src)
    y = hp(y, 180)
    y = y / (np.sqrt(np.mean(y[:gate] ** 2)) + 1e-9) * 0.2 * env     # every vowel at the same level
    return _ms_stereo(y, 30)


def v_fbchord(m, dur, p, glide=None, mod=None):
    """Future-bass chord: a bright supersaw with a vocal-ish formant on top, its volume swelling up after each hit (the
    'sidechain' bloom) and a small pitch scoop into it - the wide, wobbling chord stabs of future bass and melodic
    dubstep (an LFO on the volume when held: `mod` = beats per wobble)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    env = _va.adsr(gate, 0.003, 0.4, 0.85, p.get('r', 0.2))
    n = len(env)
    t = np.arange(n) / SR
    fr = f * 2 ** (-60 * np.exp(-t / 0.04) / 1200)
    x = _va.jp_supersaw(fr, n, 0.55, 0.75, 1.0)
    x = x + 0.6 * _vb._bp(x, np.full(n, 1100.0), 3.0)
    x = _va.vcf(x, p.get('cut', 6500), 0.12, 1.25)
    swell = 0.35 + 0.65 * (1 - np.exp(-t / 0.09))
    if isinstance(mod, (int, float)) and mod:
        rate = 1.0 / (mod * p.get('spb', 0.43))
        swell = swell * (0.55 + 0.45 * (0.5 - 0.5 * np.cos(2 * np.pi * rate * t)))
    return _hpf(x, 170) * env * swell * 0.6


def v_lofikeys(m, dur, p, glide=None, mod=None):
    """Lo-fi keys: a soft FM electric piano recorded to worn tape - slow pitch wow and flutter, a dark top, gentle
    saturation and a touch of hiss under the note - the dusty, wobbly chords of lo-fi hip hop and chillhop."""
    y = np.asarray(_va.fm_epiano(m, dur, dict(p, decay=p.get('decay', 1.3)), None), float)
    y = np.vstack([y, y]) if y.ndim == 1 else y
    n = y.shape[1]
    t = np.arange(n) / SR
    ph0 = _rng().random() * 6.28
    wow = 1 + 0.0035 * np.sin(2 * np.pi * 0.55 * t + ph0) + 0.0008 * np.sin(2 * np.pi * 7.3 * t)
    pos = np.cumsum(wow) - wow[0]
    idx = np.arange(n)
    y = np.vstack([np.interp(pos, idx, y[c], right=0.0) for c in range(2)])
    y = lp(np.tanh(y * 1.6) / 1.4, p.get('bright', 3200))
    hiss = hp(_rng().standard_normal(n), 4000) * 0.006 * np.minimum(t / 0.05, 1) * np.exp(-t / max(dur, 0.2))
    return (y + hiss[None, :]) * 0.9


for _name, _fn, _info, _roles, _gm in (
        ('vocalchop', v_vocalchop, 'Vocal chops (pitched syllables)', ('lead', 'arp'), 54),
        ('fbchord', v_fbchord, 'Future-bass chord (bright, blooming)', ('chords', 'pad'), 81),
        ('lofikeys', v_lofikeys, 'Lo-fi keys (worn-tape electric piano)', ('chords', 'arp', 'lead'), 4)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.65: Rhodes, modelled acoustic guitars, hard lead
def v_rhodes(m, dur, p, glide=None, mod=None):
    """Rhodes-style electric piano (tine + tonebar): a hammer strikes a tine whose sine-like vibration passes an
    electromagnetic pickup slightly off-centre - so the louder the note the more it 'barks' (even and odd harmonics
    from the pickup's non-linear field), a short metallic tine ping and hammer thump at the attack, a fast-then-slow
    decay, felt dampers at the release and the suitcase's stereo tremolo. The warm EP of soul, R&B, jazz, lo-fi and
    deep house (the DX-style FM piano is still 'Electric piano')."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(0.25 * SR)
    t = np.arange(n) / SR
    k = f / 261.6
    amp = (0.55 * np.exp(-t * (2.2 + 1.5 * k)) + 0.45 * np.exp(-t * (0.35 + 0.35 * k)))
    x = np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * f * t) * np.exp(-t * 6)) * amp
    bark = p.get('bark', 1.0) * (1.1 - 0.4 * min(1.0, k))
    off = 0.45
    dr = 2.8 * bark
    y = (np.tanh(dr * (x + off)) - np.tanh(dr * off)) / dr
    y = y - lp(y, 25)                                              # (the pickup's offset is DC: off)
    if f * 7.1 < 16000:
        y = y + 0.08 * np.sin(2 * np.pi * f * 7.1 * t) * np.exp(-t * 40)       # tine ping
    y = y + 0.05 * lp(_rng().standard_normal(n), 900) * np.exp(-t * 160)        # hammer thump
    rel = np.ones(n)
    rel[gate:] = np.exp(-np.arange(n - gate) / (0.07 * SR))
    y = lp(y * rel * np.minimum(t / 0.0015, 1), p.get('bright', 5500))
    tr = p.get('trem', 0.22)
    lfo = np.sin(2 * np.pi * p.get('trem_rate', 4.6) * t + _rng().random() * 6.28)
    return np.vstack([y * (1 + tr * lfo), y * (1 - tr * lfo)]) * 0.85


def _guitar_body(y, nylon=False):
    """The guitar's box: the air resonance (~100 Hz), the top plate (~200 Hz), the upper plate modes, a gentle top."""
    for fc, q, g in (((98 if nylon else 105), 2.0, 5.0), ((195 if nylon else 210), 2.5, 4.0), (400, 2.0, 2.0), (1100, 1.5, -2.0 if nylon else 1.0)):
        y = eq(y, 'peak', fc, q, g)
    return lp(hp(y, 70), 4500 if nylon else 8000)


def v_acguitar(m, dur, p, glide=None, mod=None):
    """Steel-string acoustic guitar: a waveguide string flicked by a pick, ringing on (it isn't muted until the next
    chord), through the resonances of the wooden body. `mod='pm'` = palm-muted."""
    f = float(mtof(m))
    pm = mod == 'pm'
    gate = int(max(dur, 0.05) * SR)
    n = gate + int((0.08 if pm else 0.6) * SR)
    y = _va.string(f, n, _bass_exc(f, 'pick', p.get('tone', 1.2)), t60=(0.25 if pm else 6.0) * (110.0 / max(f, 60)) ** 0.5,
                   bright=0.35 if pm else 0.75, gate=gate, mute_t60=0.25, pickup=0.0)
    y = _guitar_body(y)
    t = np.arange(n) / SR
    y = y + 0.06 * hp(_rng().standard_normal(n), 3000) * np.exp(-t * 300)       # the pick on the string
    return _ms_stereo(y, 25) * 0.55


def v_nylon(m, dur, p, glide=None, mod=None):
    """Nylon-string (classical) guitar: a soft, round finger pluck on a waveguide string with a shorter, warmer ring,
    through the body's resonances - bossa nova, flamenco, Latin, lo-fi and folk."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(0.5 * SR)
    y = _va.string(f, n, _bass_exc(f, 'finger', p.get('tone', 1.6)), t60=3.2 * (110.0 / max(f, 60)) ** 0.5, bright=0.5,
                   gate=gate, mute_t60=0.3, pickup=0.0)
    y = _guitar_body(y, nylon=True)
    return _ms_stereo(y, 25) * 0.48


def v_hardlead(m, dur, p, glide=None, mod=None):
    """Hard-dance lead (euphoric hardstyle / hardcore): a supersaw stack with an octave layer driven hard into a
    clipper, the bite pushed at 2.5 kHz, glide, and a fast vibrato that comes in late - huge, harsh and singing."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.004, 0.2, 0.9, p.get('r', 0.18))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.04) if glide is not None else np.full(n, f)
    fr = fr * 2 ** (np.clip((t - 0.25) / 0.3, 0, 1) * 22 * np.sin(2 * np.pi * 6.2 * t) / 1200)
    x = _va.jp_supersaw(fr, n, 0.6, 0.75, 1.0) + 0.5 * _va.jp_supersaw(fr * 2, n, 0.5, 0.7, 1.0)
    x = _vb.dist(x, p.get('drive', 4.0), 'hard')
    x = eq(_va.vcf(x, p.get('cut', 9000), 0.1, 1.0), 'peak', 2500, 1.0, 3.0)
    return _hpf(x, 220) * env * 0.22


_n65 = []
for _name, _fn, _info, _roles, _gm in (
        ('rhodes', v_rhodes, 'Rhodes electric piano (tine, bark, tremolo)', ('chords', 'arp', 'lead'), 4),
        ('nylon', v_nylon, 'Nylon-string guitar (modelled)', ('chords', 'arp', 'lead'), 24),
        ('hardlead', v_hardlead, 'Hard-dance lead (driven supersaw)', ('lead',), 81)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)
INSTRUMENTS['acguitar_v1'] = INSTRUMENTS['acguitar']
INSTRUMENT_INFO['acguitar_v1'] = 'Acoustic guitar (classic sound, before 1.65)'
INSTRUMENTS['acguitar'] = v_acguitar
INSTRUMENTS['steelguitar'] = v_acguitar                      # the sampled steel guitar's stand-in
INSTRUMENT_INFO['steelguitar'] = 'Steel-string guitar (modelled)'


# ----------------------------------------------------------------------------- 1.66: the acoustic workhorses rebuilt
def v_strings(m, dur, p, glide=None, mod=None):
    """String section: seven players a few cents apart, each with their own vibrato (rate, depth, when it starts) and
    a slow drift, panned across the stage; the bow's brightness grows as it bites in, a whisper of bow noise, and the
    wooden body's resonances (the warm 280 Hz, the 2.8 kHz 'singing' formant, the nasal dip between)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    a_ = p.get('a', 0.35)
    env = _va.adsr(gate, a_, 0.5, 0.9, p.get('r', 0.7))
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    L = np.zeros(n)
    R = np.zeros(n)
    for i in range(7):
        c = (i / 6 - 0.5) * 2 * p.get('spread', 13) + rng.normal(0, 2)
        dl = rng.uniform(0.12, 0.35)
        dep = rng.uniform(5, 11) * np.clip((t - dl) / 0.4, 0, 1)
        drift = 2.5 * np.sin(2 * np.pi * rng.uniform(0.08, 0.2) * t + rng.random() * 6.28)
        fr = f * 2 ** ((c + drift + dep * np.sin(2 * np.pi * rng.uniform(4.6, 5.8) * t + rng.random() * 6.28)) / 1200)
        s_ = _va.saw(fr, n, rng.random())
        pan = i / 6
        L += s_ * np.cos(pan * np.pi / 2)
        R += s_ * np.sin(pan * np.pi / 2)
    x = np.vstack([L, R]) * 0.4
    cut = p.get('cut', 3200) * (0.5 + 0.5 * np.clip(t / max(0.05, a_ * 1.3), 0, 1))
    y = _va.vcf(x, cut, 0.05, 1.0)
    y = y + 0.03 * bp(rng.standard_normal((2, n)), 2000, 7000) * (env[None, :] ** 0.5)
    for fc, q, g in ((280, 1.2, 3.0), (520, 1.5, 1.5), (1500, 1.4, -2.5), (2800, 1.6, 3.0)):
        y = eq(y, 'peak', fc, q, g)
    y = hp(y, min(160.0, f * 0.7))
    return y * env * 0.43


def v_piano(m, dur, p, glide=None, mod=None):
    """Acoustic piano: stretched (inharmonic) partials whose number and brightness follow the register and the hammer,
    each with the piano's two-stage decay (the quick 'prompt' sound and the long aftersound), the slow beating of the
    two or three strings of a note, a hammer knock, a soundboard bloom, the dampers at the release, and the notes
    spread low-left to high-right like sitting at the keyboard."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    ring = min(max(dur, 0.1) + 1.0, 4.0 if f < 300 else 2.8)
    n = int(ring * SR)
    t = np.arange(n) / SR
    B = 0.00012 * (f / 261.6) ** 1.2 + 0.00003
    kc = p.get('hammer', 1.0) * 9.0 * (261.6 / f) ** 0.35
    reg = (f / 261.6) ** 0.45
    y = np.zeros(n)
    for k in range(1, 28):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > 15000:
            break
        a = (1.0 / k) * np.exp(-(k - 1) / kc)
        fast, slow = (1.6 + 0.9 * k) * reg, (0.25 + 0.12 * k) * reg
        dec = 0.65 * np.exp(-t * fast) + 0.35 * np.exp(-t * slow)
        ph = _rng().random() * 6.28
        part = np.sin(2 * np.pi * fk * t + ph)
        if k <= 6:                                                   # unison strings beating
            part = part + 0.6 * np.sin(2 * np.pi * fk * 2 ** (0.9 / 1200) * t + ph * 1.7)
        y += a * part * dec
    y += 0.05 * lp(_rng().standard_normal(n), 2500) * np.exp(-t * 90)        # hammer knock
    y = eq(eq(y, 'peak', 110, 1.0, 2.0), 'peak', 2600, 1.2, -1.0)            # soundboard
    damp = np.ones(n)
    if gate < n:
        damp[gate:] = np.exp(-np.arange(n - gate) / (0.11 * SR))
    w = min(n, int(0.3 * SR))
    y = y / (np.sqrt(np.mean(y[:w] ** 2)) + 1e-9) * 0.13 * (f / 261.6) ** -0.08      # an even keyboard
    y *= damp * np.minimum(t / 0.0012, 1)
    pan = np.clip((m - 60) / 40, -0.6, 0.6)
    return np.vstack([y * (1 - pan * 0.5), y * (1 + pan * 0.5)])


def _eg_string(m, dur, p, mod, t60=5.0, bright=0.7, pickup=0.12):
    """Electric guitar string: picked waveguide string read by a magnetic pickup; palm mutes (`mod='pm'`) damp it."""
    f = float(mtof(m))
    pm = mod == 'pm'
    gate = int(max(dur, 0.04) * SR)
    n = gate + int((0.04 if pm else 0.12) * SR)
    y = _va.string(f, n, _bass_exc(f, 'pick', p.get('tone', 1.3)), t60=(0.18 if pm else t60) * (196.0 / max(f, 70)) ** 0.4,
                   bright=0.3 if pm else bright, gate=gate, mute_t60=0.06, pickup=p.get('pickup', pickup))
    y[gate:] *= np.exp(-np.arange(n - gate) / (0.02 * SR))
    w = min(n, int(0.15 * SR))
    y = y / (np.sqrt(np.mean(y[:w] ** 2)) + 1e-9) * 0.3                       # every string as loud
    return hp(y, 70), pm


def v_eguitar_clean(m, dur, p, glide=None, mod=None):
    """Clean electric guitar: a picked string on a bridge-side pickup into a clean amp - a little tube compression,
    the scooped American-amp tone (round lows, dipped mids, a sparkling top). A genre's `dist` setting (the old
    guitar's drive amount) sends it to the crunch amp (up to 9) or the high-gain amp (10 and up)."""
    d = float(p.get('dist') or 0)
    if d >= 10:
        return v_eguitar_dist(m, dur, dict(p, gain=d * 1.4), glide, mod)
    if d >= 2:
        return v_eguitar_crunch(m, dur, dict(p, gain=d * 1.2), glide, mod)
    y, pm = _eg_string(m, dur, p, mod)
    y = np.tanh(y * (1.6 + 2.0 * d)) / (1.3 + 1.2 * d)                  # (a little grit: the amp pushed)
    y = eq(eq(eq(y, 'peak', 120, 0.9, 2.0), 'peak', 500, 1.0, -3.0), 'peak', 3200, 1.0, 3.0)
    y = lp(y, 7500)
    if pm:
        y = eq(y, 'peak', 160, 1.0, 4.0)
    return _ms_stereo(y, 20) * 0.66


def v_eguitar_crunch(m, dur, p, glide=None, mod=None):
    """Overdriven electric guitar (crunch): the string into a cranked tube amp - asymmetric clipping that sags and
    cleans up as the note decays, a mid hump, and a 4x12 cabinet's top roll-off and presence peak."""
    y, pm = _eg_string(m, dur, p, mod, 4.0, 0.75)
    y = hp(y, 120)
    y = _vb.dist(y * p.get('gain', 6.0) + 0.15, 1.0) - np.tanh(0.15)
    y = eq(eq(y, 'peak', 800, 0.9, 4.0), 'peak', 2200, 1.2, 3.0)
    y = lp(lp(y, 5200), 6000)
    if pm:
        y = eq(y, 'peak', 140, 1.0, 5.0)
    return _ms_stereo(y, 30) * 0.22


def v_eguitar_dist(m, dur, p, glide=None, mod=None):
    """High-gain distorted guitar (rock / metal): a tight boost into two hard clipping stages, the scooped metal mids,
    a thick low end and a steep cabinet roll-off - palm mutes turn it into the chug."""
    y, pm = _eg_string(m, dur, p, mod, 4.0, 0.8)
    y = hp(y, 180)
    y = _vb.dist(y * p.get('gain', 18.0), 1.0, 'hard')
    y = _vb.dist(eq(y, 'peak', 1000, 0.8, 4.0) * 3.0, 1.0)
    y = eq(eq(eq(y, 'peak', 110, 0.9, 3.5), 'peak', 650, 0.9, -5.0), 'peak', 1700, 1.1, 3.0)
    b, a = signal.butter(4, 4800 / (SR / 2))
    y = signal.lfilter(b, a, y)
    if pm:
        y = eq(y, 'peak', 120, 1.0, 5.0)
    return _ms_stereo(y, 35) * 0.18


def v_sax(m, dur, p, glide=None, mod=None):
    """Tenor saxophone: a reed on a conical bore - every harmonic present, getting brighter the harder it's blown (the
    tone opens up with the breath), the horn's formants, breath noise riding the tone, a scoop up into each note,
    a delayed vibrato, and an optional growl."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.035), 0.3, 0.82, p.get('r', 0.1))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.05) if glide is not None else f * 2 ** (-45 * np.exp(-t / 0.035) / 1200)
    fr = np.broadcast_to(fr, (n,)) * 2 ** (np.clip((t - 0.25) / 0.4, 0, 1) * p.get('vib', 16) * np.sin(2 * np.pi * 5.4 * t) / 1200)
    x = _va.saw(fr, n) * 0.8 + _va.pulse(fr, n, 0.0, 0.45) * 0.25
    blow = np.concatenate([env[:n], np.zeros(0)])
    cut = 700 + 4200 * blow ** 1.4 * (1 + 0.6 * np.exp(-t / 0.08))
    y = _va.vcf(x, cut, 0.12, 1.4)
    for fc, q, g in ((500, 1.3, 4.0), (1600, 1.4, 3.0), (2800, 1.8, 2.0)):
        y = eq(y, 'peak', fc, q, g)
    y = y + 0.07 * _aspirate(bp(_rng().standard_normal(n), 1200, 6000), f) * (0.3 + 0.7 * blow)
    if p.get('growl'):
        y = y * (1 + 0.25 * np.sin(2 * np.pi * 32 * t))
    y = np.tanh(y * 1.5) * env
    return _ms_stereo(y, 25) * 0.4


def v_flute(m, dur, p, glide=None, mod=None):
    """Flute: an air jet across the embouchure - a near-sine tone with a little 2nd / 3rd harmonic that grows in the
    upper register, breath noise tuned around the note, the 'chiff' of the attack, a soft start slightly flat and a
    flute vibrato that moves the pitch and the loudness together."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.06), 0.3, 0.85, p.get('r', 0.18))
    n = len(env)
    t = np.arange(n) / SR
    vib = np.clip((t - 0.2) / 0.4, 0, 1) * np.sin(2 * np.pi * 5.0 * t)
    fr = f * 2 ** ((-20 * np.exp(-t / 0.05) + 14 * vib) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    over = 0.15 + 0.25 * min(1.0, max(0.0, (f - 500) / 1000))
    y = np.sin(ph) + over * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    y = y * (1 + 0.08 * vib)
    rng = _rng()
    breath = _aspirate(bp(rng.standard_normal(n), f * 0.8, min(f * 4, 16000)), f, ph) * 0.12
    chiff = bp(rng.standard_normal(n), f * 1.5, min(f * 6, 16000)) * np.exp(-t / 0.025) * 0.5
    y = (y + breath + chiff) * env
    return _ms_stereo(y, 30) * 0.45


for _name, _fn in (('strings', v_strings), ('piano', v_piano), ('guitar', v_eguitar_clean), ('sax', v_sax), ('flute', v_flute)):
    if _name + '_v1' not in INSTRUMENTS:
        INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
        INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.66)'
        for _role, _lst in ROLE_CHOICES.items():
            if _name in _lst and _name + '_v1' not in _lst:
                _lst.append(_name + '_v1')
        GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)
    INSTRUMENTS[_name] = _fn
INSTRUMENTS['sopsax'] = lambda m, dur, p, glide=None, mod=None: v_sax(m, dur, dict(p, vib=p.get('vib', 18)), glide, mod)
for _name, _fn, _info, _gm in (('cleanguitar', v_eguitar_clean, 'Clean electric guitar (modelled)', 27),
                               ('odguitar', v_eguitar_crunch, 'Overdriven guitar (crunch)', 29),
                               ('distguitar', v_eguitar_dist, 'Distorted guitar (high gain)', 30)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in ('chords', 'lead', 'arp'):
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)
INSTRUMENT_INFO['guitar'] = 'Electric guitar (clean, modelled)'


# ----------------------------------------------------------------------------- 1.67: mallets, choir, brass section, plucked strings
def _modes(f, n, modes, hard=1.0, rng=None):
    """Modal synthesis: a struck bar / tine / bell as a sum of its vibration modes (ratio to the fundamental, level,
    decay rate in 1/s). The mallet's hardness brings out the high modes; above 16 kHz they are left out."""
    t = np.arange(n) / SR
    y = np.zeros(n)
    rng = rng or _rng()
    for r, a, d in modes:
        fr = f * r
        if fr > 16000:
            continue
        y += a * (hard ** (np.log2(max(r, 1.0)) * 0.6)) * np.sin(2 * np.pi * fr * t + rng.random() * 6.28) * np.exp(-t * d)
    return y


def v_marimba(m, dur, p, glide=None, mod=None):
    """Marimba: a rosewood bar tuned so its 2nd mode sits two octaves up (4x) and the 3rd near 10x, struck with a yarn
    mallet; a tuned tube under the bar makes the fundamental bloom. Warm, woody, quick."""
    f = float(mtof(m))
    n = int(min(1.6, 0.5 + 220 / f) * SR)
    k = (f / 261.6) ** 0.5
    y = _modes(f, n, [(1.0, 1.0, 3.2 * k), (3.99, 0.32, 10 * k), (9.9, 0.1, 25 * k)], p.get('hard', 0.9))
    t = np.arange(n) / SR
    y = y * (1 + 0.6 * (1 - np.exp(-t / 0.02))) + 0.08 * lp(_rng().standard_normal(n), 3000) * np.exp(-t * 300)
    y *= np.minimum(t / 0.001, 1)
    return _ms_stereo(y, 20) * 0.42


def v_celesta(m, dur, p, glide=None, mod=None):
    """Celesta: felt hammers on steel plates over wooden resonators - a pure, sweet, bell-like tone with a soft attack
    and a clean ring, the high modes fading fast. Fairy-tale and Christmas sparkle."""
    f = float(mtof(m))
    n = int(min(2.5, 0.8 + 400 / f) * SR)
    k = (f / 523.0) ** 0.5
    y = _modes(f, n, [(1.0, 1.0, 1.4 * k), (2.0, 0.12, 4 * k), (3.0, 0.06, 7 * k), (5.4, 0.05, 18 * k)], p.get('hard', 0.6))
    t = np.arange(n) / SR
    y *= np.minimum(t / 0.002, 1)
    g = int(max(dur, 0.1) * SR)
    if g < n:
        y[g:] *= np.exp(-np.arange(n - g) / (0.4 * SR))
    return _ms_stereo(y, 20) * 0.42


def v_glock(m, dur, p, glide=None, mod=None):
    """Glockenspiel: hard mallets on steel bars - bright, piercing, long-ringing, with the inharmonic 2.76x / 5.4x
    bar modes giving its metallic shimmer."""
    f = float(mtof(m))
    n = int(min(3.0, 1.2 + 500 / f) * SR)
    y = _modes(f, n, [(1.0, 1.0, 1.0), (2.76, 0.35, 4.0), (5.4, 0.18, 9.0), (8.93, 0.08, 16.0)], p.get('hard', 1.3))
    t = np.arange(n) / SR
    y = y * np.minimum(t / 0.0005, 1) + 0.04 * hp(_rng().standard_normal(n), 5000) * np.exp(-t * 400)
    return _ms_stereo(y, 15) * 0.38


def v_kalimba(m, dur, p, glide=None, mod=None):
    """Kalimba (thumb piano): a steel tine plucked by the thumb over a small wooden box - a round fundamental, the
    tine's high, quickly fading overtone, a buzz of the box and a soft thumb click."""
    f = float(mtof(m))
    n = int(min(2.0, 0.7 + 300 / f) * SR)
    y = _modes(f, n, [(1.0, 1.0, 2.2), (5.9, 0.22, 22.0), (12.7, 0.08, 45.0)], p.get('hard', 1.0))
    y = eq(y, 'peak', 400, 1.0, 3.0)
    t = np.arange(n) / SR
    y = y * np.minimum(t / 0.001, 1) + 0.05 * bp(_rng().standard_normal(n), 800, 4000) * np.exp(-t * 200)
    return _ms_stereo(y, 20) * 0.45


_CHOIR_V = {'a': ((800, 1150, 2900, 3900, 4950), (80, 90, 120, 130, 140), (0, -6, -32, -20, -50)),
            'o': ((450, 800, 2830, 3800, 4950), (70, 80, 100, 130, 135), (0, -11, -22, -22, -50)),
            'u': ((325, 700, 2530, 3500, 4950), (50, 60, 170, 180, 200), (0, -16, -35, -40, -60)),
            'e': ((400, 1600, 2700, 3300, 4950), (60, 80, 120, 150, 200), (0, -24, -30, -35, -60)),
            'i': ((270, 2140, 2950, 3900, 4950), (60, 90, 100, 120, 120), (0, -12, -26, -26, -44))}


def v_choir(m, dur, p, glide=None, mod=None):
    """Choir: six singers on the note, each a breathy glottal pulse with their own pitch, vibrato and timing, through
    the five formants of the vowel ('aah' by default, `vowel` = o / u / e / i for 'ooh' and the rest), the formants
    shifted down a little for low (men's) voices and up for high ones; a slow swell and a wide stage."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = _va.adsr(gate, p.get('a', 0.4), 0.5, 0.9, p.get('r', 0.8))
    n = len(env)
    t = np.arange(n) / SR
    fr_, bw_, g_ = _CHOIR_V.get(p.get('vowel', 'a'), _CHOIR_V['a'])
    shift = (f / 300.0) ** 0.12
    rng = _rng()
    L = np.zeros(n)
    R = np.zeros(n)
    for i in range(6):
        c = rng.normal(0, 7)
        vib = np.clip((t - rng.uniform(0.1, 0.4)) / 0.5, 0, 1) * rng.uniform(15, 30) * np.sin(2 * np.pi * rng.uniform(4.8, 5.8) * t + rng.random() * 6.28)
        ph = np.cumsum(f * 2 ** ((c + vib) / 1200)) / SR + rng.random()
        pulse = (2 * (ph % 1.0) - 1.0)
        src = signal.lfilter([1.0], [1, -0.85], pulse) * 0.3 + rng.standard_normal(n) * 0.04
        v = 0
        for fc, bw, gd in zip(fr_, bw_, g_):
            fcs = min(fc * shift, SR * 0.45)
            b, a = signal.iirpeak(fcs / (SR / 2), fcs / bw)
            v = v + 10 ** (gd / 20) * signal.lfilter(b, a, src)
        d = int(rng.uniform(0, 0.03) * SR)
        v = np.concatenate([np.zeros(d), v[:n - d]])
        pan = i / 5
        L += v * np.cos(pan * np.pi / 2)
        R += v * np.sin(pan * np.pi / 2)
    y = hp(np.vstack([L, R]), 120)
    y = y / (np.sqrt(np.mean(y[:, :min(n, int(0.8 * SR))] ** 2)) + 1e-9) * 0.12
    return y * env


def _brass_voice(fr, n, t, bright, a_):
    """One brass player: the lips' buzz (every harmonic) through a bell whose brightness opens with the breath, a
    short 'blat' as the note speaks."""
    x = _va.saw(fr, n)
    cut = bright * (0.3 + 0.7 * np.clip(t / max(a_, 0.01), 0, 1)) * (1 + 0.5 * np.exp(-t / 0.05))
    y = _va.vcf(x, cut, 0.15, 1.6)
    return eq(y, 'peak', 1200, 1.0, 3.0)


def v_brass(m, dur, p, glide=None, mod=None):
    """Brass section: three players (trumpet / trombone colour by register) on the note, each a buzzing-lip voice whose
    bell opens with the breath, a little out of time and tune with each other, a scoop into the note and a punchy
    attack - the horn section of soul, funk, ska, salsa and big band (synth brass is 'Synth brass')."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    a_ = p.get('a', 0.03)
    env = _va.adsr(gate, a_, 0.25, 0.82, p.get('r', 0.12))
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    bright = p.get('cut', 3800) * (f / 440) ** 0.25
    L = np.zeros(n)
    R = np.zeros(n)
    for i in range(3):
        c = rng.normal(0, 5)
        fr = f * 2 ** ((c - 40 * np.exp(-t / 0.03) + np.clip((t - 0.3) / 0.4, 0, 1) * 10 * np.sin(2 * np.pi * rng.uniform(5, 6) * t)) / 1200)
        v = _brass_voice(fr, n, t, bright, a_)
        d = int(rng.uniform(0, 0.015) * SR)
        v = np.concatenate([np.zeros(d), v[:n - d]])
        pan = 0.2 + 0.3 * i
        L += v * np.cos(pan * np.pi / 2)
        R += v * np.sin(pan * np.pi / 2)
    y = np.tanh(np.vstack([L, R]) * 0.9) * env
    return hp(y, 90) * 0.55


def v_harp(m, dur, p, glide=None, mod=None):
    """Concert harp: a gut / nylon string plucked by the fingertip near its middle (round, few high partials), a long,
    free ring (harpists let the strings sound), the soundboard's warmth."""
    f = float(mtof(m))
    n = int(min(4.0, 1.2 + 300 / f) * SR)
    y = _va.string(f, n, _bass_exc(f, 'finger', p.get('tone', 1.8)), t60=4.5 * (220.0 / max(f, 60)) ** 0.5, bright=0.45)
    y = lp(eq(hp(y, 60), 'peak', 300, 1.0, 3.0), 6000)
    y = y / (np.sqrt(np.mean(y[:int(0.2 * SR)] ** 2)) + 1e-9) * 0.13
    return _ms_stereo(y, 25)


def v_pizz(m, dur, p, glide=None, mod=None):
    """Pizzicato strings: a section plucking - four short, woody plucks a hair apart in time and tune, through the
    violin family's body resonances."""
    f = float(mtof(m))
    n = int(min(1.2, 0.35 + 120 / f) * SR)
    rng = _rng()
    out = np.zeros((2, n))
    for i in range(4):
        fi = f * 2 ** (rng.normal(0, 6) / 1200)
        y = _va.string(fi, n, _bass_exc(fi, 'finger', 1.5), t60=0.55 * (220.0 / max(f, 60)) ** 0.4, bright=0.4)
        d = int(rng.uniform(0, 0.02) * SR)
        y = np.concatenate([np.zeros(d), y[:n - d]])
        pan = i / 3
        out[0] += y * np.cos(pan * np.pi / 2)
        out[1] += y * np.sin(pan * np.pi / 2)
    for fc, q, g in ((280, 1.2, 4.0), (520, 1.5, 2.0), (2800, 1.6, 2.0)):
        out = eq(out, 'peak', fc, q, g)
    out = hp(out, 100)
    return out / (np.sqrt(np.mean(out[:, :int(0.15 * SR)] ** 2)) + 1e-9) * 0.13


def v_clav(m, dur, p, glide=None, mod=None):
    """Clavinet: a string struck from below by a rubber tip and read by two pickups - bright, nasal and percussive; the
    yarn damper chokes it the moment the key comes up. Funk's rhythm keyboard."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.6), 0.04) * SR)
    n = gate + int(0.03 * SR)
    y = _va.string(f, n, _bass_exc(f, 'pop', p.get('tone', 1.2)), t60=2.5, bright=0.85, gate=gate, mute_t60=0.02, pickup=0.08)
    y = eq(eq(hp(y, 180), 'peak', 1500, 1.0, 5.0), 'peak', 3500, 1.2, 3.0)
    y = np.tanh(y * 2.0)
    y = y / (np.sqrt(np.mean(y[:min(n, int(0.1 * SR))] ** 2)) + 1e-9) * 0.13
    return _ms_stereo(y, 15)


def v_mutedgtr(m, dur, p, glide=None, mod=None):
    """Palm-muted / chicken-scratch electric guitar: the modelled string choked by the palm into the clean amp - the
    short, percussive 'chk' of funk, afrobeats, disco and highlife."""
    return v_eguitar_clean(m, min(dur, 0.2), dict(p, pickup=0.1), glide, 'pm')


def v_twang(m, dur, p, glide=None, mod=None):
    """Telecaster twang: the modelled string on a bright bridge pickup, a snappy attack, the amp pushed just into grit
    (surf, country, rockabilly, desert blues)."""
    y = np.asarray(v_eguitar_clean(m, dur, dict(p, pickup=0.07, dist=p.get('dist', 0.6), tone=1.5), glide, mod))
    return eq(y, 'peak', 3000, 1.0, 3.0) * 0.9


for _name, _fn in (('marimba', v_marimba), ('celesta', v_celesta), ('kalimba', v_kalimba), ('choir', v_choir),
                   ('brass', v_brass), ('harp', v_harp), ('pizz', v_pizz), ('clav', v_clav), ('mutedgtr', v_mutedgtr),
                   ('twang', v_twang)):
    if _name + '_v1' not in INSTRUMENTS:
        INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
        INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.67)'
        for _role, _lst in ROLE_CHOICES.items():
            if _name in _lst and _name + '_v1' not in _lst:
                _lst.append(_name + '_v1')
        GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)
    INSTRUMENTS[_name] = _fn
INSTRUMENT_INFO['brass'] = 'Brass section (trumpets / trombones)'   # (1.97: it was still labelled 'Synth brass')
INSTRUMENTS['glock'] = v_glock
INSTRUMENT_INFO['glock'] = 'Glockenspiel'
GM_PROGRAM['glock'] = 9
for _role in ('arp', 'lead'):
    ROLE_CHOICES[_role].append('glock')


def v_horn(m, dur, p, glide=None, mod=None):
    """French horns: the brass-section model played mellow - a darker bell, a softer, slower attack, more warmth."""
    return v_brass(m, dur, dict(p, cut=p.get('cut', 1500), a=p.get('a', 0.08)), glide, mod)


def v_trombone(m, dur, p, glide=None, mod=None):
    """Trombones: the brass-section model a little darker and broader, with the slide's lazy scoop."""
    return v_brass(m, dur, dict(p, cut=p.get('cut', 2400), a=p.get('a', 0.05)), glide, mod)


def v_tuba(m, dur, p, glide=None, mod=None):
    """Tuba: the brass model at its darkest, with a round low-end bloom."""
    y = np.asarray(v_brass(m, dur, dict(p, cut=p.get('cut', 900), a=p.get('a', 0.06)), glide, mod))
    return eq(y, 'peak', 90, 1.0, 4.0)


def v_churchbell(m, dur, p, glide=None, mod=None):
    """Church bell: a struck metal bell by modal synthesis - its hum tone an octave below, the strike tone, the minor-third
    partial that makes a bell sound like a bell, the bright upper partials that fade first, and a long ring."""
    f = float(mtof(m))
    n = int((max(dur, 0.1) + p.get('ring', 1.6)) * SR)
    d = p.get('decay', 1.0)
    y = _modes(f, n, [(0.5, 0.35, 0.6 * d), (1.0, 1.0, 1.0 * d), (1.19, 0.45, 1.3 * d), (1.5, 0.3, 1.8 * d),
                      (2.0, 0.35, 2.4 * d), (2.5, 0.15, 3.5 * d), (3.0, 0.12, 4.5 * d), (4.2, 0.08, 7 * d)], p.get('hard', 1.0))
    t = np.arange(n) / SR
    y = y * np.minimum(t / 0.001, 1) + 0.03 * hp(_rng().standard_normal(n), 4000) * np.exp(-t * 250)
    y = fade_out(y, 0.05)
    y = y / (np.sqrt(np.mean(y[:int(0.3 * SR)] ** 2)) + 1e-9) * 0.14
    return _ms_stereo(y, 20)


def v_tubular(m, dur, p, glide=None, mod=None):
    """Tubular bells (chimes): long brass tubes struck at the top - the tube's strong 2nd-4th partials heard as the
    pitch, a long, slowly beating ring."""
    f = float(mtof(m))
    n = int((max(dur, 2.5) + 1.5) * SR)
    y = _modes(f, n, [(1.0, 0.5, 0.5), (2.76, 1.0, 0.7), (5.4, 0.7, 1.1), (8.9, 0.35, 1.8), (13.3, 0.15, 3.0)], p.get('hard', 1.0))
    y = fade_out(y * np.minimum(np.arange(n) / SR / 0.001, 1), 0.1)
    y = y / (np.sqrt(np.mean(y[:int(0.4 * SR)] ** 2)) + 1e-9) * 0.13
    return _ms_stereo(y, 30)


for _name, _fn in (('horn', v_horn), ('trombone', v_trombone), ('tuba', v_tuba), ('tubular', v_tubular)):
    if _name + '_v1' not in INSTRUMENTS:
        INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
        INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.67)'
        for _role, _lst in ROLE_CHOICES.items():
            if _name in _lst and _name + '_v1' not in _lst:
                _lst.append(_name + '_v1')
        GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)
    INSTRUMENTS[_name] = _fn

INSTRUMENTS['churchbell'] = v_churchbell
INSTRUMENT_INFO['churchbell'] = 'Church bell (hum, strike, minor third)'
GM_PROGRAM['churchbell'] = 14
for _role in ('arp', 'lead'):
    ROLE_CHOICES[_role].append('churchbell')


# ----------------------------------------------------------------------------- 1.68: house upgrade + psy
def v_m1piano(m, dur, p, glide=None, mod=None):
    """The 90s house piano (the classic workstation 'Piano 16''): a bright acoustic piano layered with a glassy FM
    tine on the attack, the low mids hollowed out and the top pushed, a short release and a little chorus - the
    pumping, glassy piano chords of 90s / piano house."""
    pn = np.asarray(v_piano(m, min(dur, 1.2), dict(p, hammer=1.5)), float)
    n = pn.shape[1]
    t = np.arange(n) / SR
    f = float(mtof(m))
    tine = np.sin(2 * np.pi * f * t + 1.8 * np.exp(-t * 9) * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t * 5) * 0.12
    y = pn + tine[None, :]
    y = eq(eq(eq(y, 'peak', 380, 1.0, -4.0), 'peak', 3000, 1.0, 4.0), 'highshelf', 7000, 0.7, 2.0)
    g = int(max(dur, 0.05) * SR)
    if g < n:
        y[:, g:] *= np.exp(-np.arange(n - g) / (0.08 * SR))[None, :]
    return _va.juno_chorus(y, 1, 0.25) * 1.1


def v_samplerstab(m, dur, p, glide=None, mod=None):
    """Sampled chord stab: the house / garage / rave chord stab as it came out of a 12-bit sampler - bright detuned
    saws and an organ-ish pulse snapped shut by the filter, then crunched to 12 bits at a lower rate (the grit and
    'air' of the old samplers), with a short tail."""
    f = float(mtof(m))
    gate = int(min(max(dur, 0.06), 0.35) * SR)
    env = _va.adsr(gate, 0.002, 0.16, 0.25, 0.08)
    n = len(env)
    t = np.arange(n) / SR
    x = _vb._stack(f, n, 3, 12, 0.4)
    cut = 400 * (p.get('cut', 7000) / 400) ** np.exp(-t / 0.09)
    y = _va.vcf(x, cut, 0.25, 1.3)
    hold = 2
    y = np.repeat(np.round(y[:, ::hold] * 2048) / 2048, hold, axis=1)[:, :n]
    y = lp(y, 9000)
    return y * env * 0.55


def v_techbass(m, dur, p, glide=None, mod=None):
    """Rubbery tech-house bass: a sine / triangle whose pitch snaps down into the note (the 'boing'), a little FM
    wobble on the attack, a short, round body - the bouncy, rubbery bassline of tech house and minimal."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.002, p.get('d', 0.18), p.get('s', 0.5), 0.04)
    n = len(env)
    t = np.arange(n) / SR
    fr = f * 2 ** (p.get('snap', 7.0) * np.exp(-t / 0.025) / 12)
    if glide is not None:
        fr = fr * 0 + f + (float(mtof(glide)) - f) * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph + 1.2 * np.exp(-t / 0.05) * np.sin(2 * ph)) * 0.8 + 2 / np.pi * np.arcsin(np.sin(ph)) * 0.3
    y = lp(np.tanh(y * 1.6), p.get('cut', 1600))
    return hp(y, 28) * env * 0.6


def v_bhbass(m, dur, p, glide=None, mod=None):
    """Bass-house bass: a square-and-saw mid-bass whose filter and vowel formant snap 'yoy' on every note, driven hard,
    over a clean sub - the growling, talking bassline of bass house and G-house."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.002, 0.2, 0.7, 0.04)
    n = len(env)
    t = np.arange(n) / SR
    fo = f if f > 55 else f * 2
    x = _va.pulse(np.full(n, fo), n, 0.0, 0.35) * 0.6 + _va.saw(np.full(n, fo * 1.005), n) * 0.6
    sweep = np.exp(-t / p.get('fdecay', 0.09))
    y = _va.vcf(x, 250 + 2600 * sweep, 0.5, 1.6)
    y = y + 0.9 * _vb._vowel(y, 0.15 + 0.7 * sweep)
    y = _vb._split_hp(_vb.dist(y, 3.0), f) * 0.5
    sub = _vb._sub(f, n, 0.8)
    return np.vstack([y + sub, y + sub]) * env * 0.55


def v_psybass(m, dur, p, glide=None, mod=None):
    """Psy / festival rolling bass: a tight saw with a snappy filter envelope and a small pitch click, mono and very
    short - three of them between every kick (the 'K-B-B-B' roll)."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.2), 0.02) * SR)
    env = _va.adsr(gate, 0.001, p.get('d', 0.09), 0.2, 0.02)
    n = len(env)
    t = np.arange(n) / SR
    fr = f * 2 ** (2.0 * np.exp(-t / 0.006) / 12)
    x = _va.saw(fr, n) * 0.8 + np.sin(2 * np.pi * np.cumsum(fr) / SR) * 0.5
    cut = 150 * (p.get('cut', 2600) / 150) ** np.exp(-t / p.get('fdecay', 0.035))
    y = _va.vcf(x, cut, 0.3, 1.5)
    return hp(y, 30) * env * 0.7


def v_psylead(m, dur, p, glide=None, mod=None):
    """Psy / festival lead: an FM tone whose modulation index is swept by a resonant filter envelope and a fast
    LFO, a vowel formant on top, driven and wide - the squelchy, twisting, alien lead riffs of psytrance and
    psy-influenced festival music."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.003, 0.2, 0.8, p.get('r', 0.12))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.03) if glide is not None else np.full(n, f)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * p.get('rate', 6.0) * t)
    idx = 0.8 + 3.5 * np.exp(-t / 0.12) + 1.5 * lfo
    x = np.sin(ph + idx * np.sin(ph * p.get('ratio', 2.0)))
    x = np.vstack([x, x]) + _va.jp_supersaw(fr, n, 0.4, 0.5, 1.0) * 0.4
    y = _va.vcf(x, 600 + 5000 * (0.4 * np.exp(-t / 0.1) + 0.6 * lfo), 0.45, 1.6)
    y = y + 0.5 * _vb._vowel(y, lfo)
    y = _vb.dist(y, 2.5)
    return _hpf(y, 200) * env * 0.35


for _name, _fn in (('m1piano', v_m1piano),):
    if _name + '_v1' not in INSTRUMENTS:
        INSTRUMENTS[_name + '_v1'] = INSTRUMENTS[_name]
        INSTRUMENT_INFO[_name + '_v1'] = (INSTRUMENT_INFO.get(_name) or _name) + ' (classic sound, before 1.68)'
        for _role, _lst in ROLE_CHOICES.items():
            if _name in _lst and _name + '_v1' not in _lst:
                _lst.append(_name + '_v1')
        GM_PROGRAM[_name + '_v1'] = GM_PROGRAM.get(_name, 0)
    INSTRUMENTS[_name] = _fn
for _name, _fn, _info, _roles, _gm in (
        ('samplerstab', v_samplerstab, 'Sampled chord stab (12-bit, house / garage / rave)', ('chords', 'arp', 'lead'), 81),
        ('techbass', v_techbass, 'Rubbery tech-house bass', ('bass',), 38),
        ('bhbass', v_bhbass, 'Bass-house bass (growling "yoy")', ('bass',), 39),
        ('psybass', v_psybass, 'Psy rolling bass (K-B-B-B)', ('bass',), 38),
        ('psylead', v_psylead, 'Psy lead (squelchy FM riff)', ('lead', 'arp'), 81)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)
INSTRUMENT_INFO['m1piano'] = '90s house piano (bright, glassy)'


# ----------------------------------------------------------------------------- 1.69: more dubstep / bass-music basses
for _name, _fn, _info in (('darkwob', _vb.dark_wobble, 'Dark smooth wobble (deep dubstep)'),
                          ('subwob', _vb.sub_wobble, 'Sub wobble (deep pressure)'),
                          ('fmgrowl', _vb.fm_growl, 'FM growl (brostep / neuro, talking sidebands)'),
                          ('talkgrowl', _vb.talk_growl, 'Talking growl (stepped vowel LFO)'),
                          ('metalbass', _vb.metal_bass, 'Metallic neuro bass (comb + FM)'),
                          ('fuzzbass', _vb.fuzz_bass, 'Fuzzy filter bass (rubbery electro)')):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = 39
    if _name not in ROLE_CHOICES['bass']:
        ROLE_CHOICES['bass'].append(_name)


def v_progpluck(m, dur, p, glide=None, mod=None):
    """Progressive / tech-trance pluck-lead: two saws and a hollow square through a resonant band-limited filter that
    falls slowly from bright to dark, mid-focused and round rather than glassy - built to be fed into long dotted
    delays and big reverbs, the hypnotic riff of progressive and tech trance."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.002, p.get('d', 0.35), 0.3, p.get('r', 0.25))
    n = len(env)
    t = np.arange(n) / SR
    x = np.vstack([_va.saw(np.full(n, f * 2 ** (-7 / 1200)), n), _va.saw(np.full(n, f * 2 ** (7 / 1200)), n, 0.4)])
    x = x + _va.pulse(np.full(n, f), n, 0.25, 0.5)[None, :] * 0.5
    cut = 300 * (p.get('cut', 4200) / 300) ** np.exp(-t / p.get('fdecay', 0.22))
    y = _va.vcf(x, cut, p.get('res', 0.42), 1.4)
    y = eq(_hpf(y, 220), 'peak', 1100, 1.0, 3.0)
    return y * env * 0.55


def v_gatepad(m, dur, p, glide=None, mod=None):
    """Trance-gated supersaw pad: a wide JP supersaw chord chopped into 16ths by a built-in, tempo-synced gate (each
    slice with a soft edge), the filter breathing slowly - the pulsing wall of progressive and tech trance."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = _va.adsr(gate, 0.02, 0.4, 0.9, p.get('r', 0.3))
    n = len(env)
    t = np.arange(n) / SR
    spb = p.get('spb', 0.45)
    step = spb / 4
    ph = (t / step) % 1.0
    duty = p.get('duty', 0.55)
    g = np.clip(np.minimum(ph / 0.06, (duty - ph) / 0.06), 0, 1)
    x = _va.jp_supersaw(f, n, 0.5, 0.75, 1.0)
    cut = p.get('cut', 3600) * (1 + 0.3 * np.sin(2 * np.pi * 0.1 * t))
    y = _hpf(_va.vcf(x, cut, 0.12, 1.05), 160)
    return y * env * (0.15 + 0.85 * g) * 0.55


for _name, _fn, _info, _roles in (('progpluck', v_progpluck, 'Progressive pluck-lead (round, delayed)', ('lead', 'arp')),
                                  ('gatepad', v_gatepad, 'Trance-gated supersaw pad (16ths)', ('pad', 'chords'))):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = 81
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# switch-up / Memphis / phonk voices
def v_orchhit(m, dur, p, glide=None, mod=None):
    """Orchestra hit: the 80s sampler's whole orchestra in one stab - brass, strings and a timpani thump struck
    together, crunched to 8-bit-ish resolution, short and huge (Memphis, phonk, freestyle, early hip hop)."""
    f = float(mtof(m))
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    br = np.asarray(v_brass(m, 0.25, {'a': 0.005}), float)[:, :n]
    st = np.asarray(v_strings(m + 12, 0.25, {'a': 0.005}), float)[:, :n]
    br = np.pad(br, ((0, 0), (0, max(0, n - br.shape[1]))))
    st = np.pad(st, ((0, 0), (0, max(0, n - st.shape[1]))))
    thump = (np.sin(2 * np.pi * (f / 4 if f > 200 else f / 2) * t) * np.exp(-t * 12))[None, :] * 0.5
    y = (br + st * 0.6 + thump) * np.exp(-t / 0.18)[None, :]
    y = np.repeat(np.round(y[:, ::3] * 160) / 160, 3, axis=1)[:, :n]
    y = lp(y, 7000)
    return y / (np.sqrt(np.mean(y[:, :int(0.1 * SR)] ** 2)) + 1e-9) * 0.18


def v_darkpiano(m, dur, p, glide=None, mod=None):
    """Horror piano (Memphis / switch-up): the piano out of tune with itself (each note doubled a little flat), slow
    tape wow, the top rolled off and crushed to 10 bits - eerie, cheap, haunted."""
    a = np.asarray(v_piano(m, dur, p), float)
    b = np.asarray(v_piano(m - 0.25, dur, p), float)
    n = min(a.shape[1], b.shape[1])
    y = a[:, :n] * 0.7 + b[:, :n] * 0.5
    t = np.arange(n) / SR
    wow = 1 + 0.004 * np.sin(2 * np.pi * 0.45 * t + _rng().random() * 6.28)
    pos = np.cumsum(wow) - wow[0]
    idx = np.arange(n)
    y = np.vstack([np.interp(pos, idx, y[c], right=0.0) for c in range(2)])
    y = np.round(lp(y, 4200) * 512) / 512
    return y * 1.1


def v_eeriepad(m, dur, p, glide=None, mod=None):
    """Eerie pad: a choir-and-strings bed whose players drift slowly out of tune against each other (beating, almost
    dissonant), a dark filter and tape hiss - the haunted backdrop of horrorcore, phonk and switch-up tracks."""
    st = np.asarray(v_strings(m, dur, dict(p, spread=28, a=p.get('a', 0.8), cut=1800)), float)
    n = st.shape[1]
    t = np.arange(n) / SR
    drift = 2 ** ((18 * np.sin(2 * np.pi * 0.07 * t + _rng().random() * 6.28)) / 1200)
    f = float(mtof(m))
    ph = 2 * np.pi * np.cumsum(f * drift) / SR
    ghost = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.minimum(t / 1.0, 1) * 0.08
    y = st + ghost[None, :] + 0.004 * _rng().standard_normal((2, n))
    return lp(y, 2600) * 1.1


def v_musicbox(m, dur, p, glide=None, mod=None):
    """Music box: tiny steel comb teeth plucked by a turning drum - a high, glassy, quickly fading ping with its
    inharmonic overtones, the comb's buzz and a little mechanical tick. Lullabies, horror and switch-up intros."""
    f = float(mtof(m))
    n = int(min(1.8, 0.6 + 300 / f) * SR)
    y = _modes(f, n, [(1.0, 1.0, 2.5), (3.06, 0.35, 9.0), (6.7, 0.15, 20.0)], p.get('hard', 1.2))
    t = np.arange(n) / SR
    y = y * np.minimum(t / 0.0005, 1) + 0.03 * hp(_rng().standard_normal(n), 6000) * np.exp(-t * 500)
    y = y / (np.sqrt(np.mean(y[:int(0.2 * SR)] ** 2)) + 1e-9) * 0.13
    return _ms_stereo(y, 15)


def v_crushlead(m, dur, p, glide=None, mod=None):
    """Crushed lead: a detuned saw lead with portamento crushed to 6 bits at a low sample rate - the gritty, aliased,
    cheap-sampler lead of phonk, Memphis and switch-up drops."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.004, 0.2, 0.85, 0.08)
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.06) if glide is not None else np.full(n, f)
    x = (_va.saw(fr * 2 ** (-8 / 1200), n) + _va.saw(fr * 2 ** (8 / 1200), n, 0.4)) * 0.5
    x = lp(x, 5000)
    hold = 4
    y = np.repeat(np.round(x[::hold] * 32) / 32, hold)[:n]
    y = lp(y, 7000) * env
    return _ms_stereo(y, 20) * 0.5


for _name, _fn, _info, _roles in (('orchhit', v_orchhit, 'Orchestra hit (80s sampler stab)', ('chords', 'arp', 'lead')),
                                  ('darkpiano', v_darkpiano, 'Horror piano (detuned, crushed, wobbly)', ('chords', 'arp', 'lead')),
                                  ('eeriepad', v_eeriepad, 'Eerie pad (drifting, haunted)', ('pad', 'chords')),
                                  ('musicbox', v_musicbox, 'Music box', ('arp', 'lead')),
                                  ('crushlead', v_crushlead, 'Crushed lead (6-bit saw, portamento)', ('lead',))):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = 55 if _name == 'orchhit' else 81
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.71: classic mono + rave / trance voices
def v_sh101(m, dur, p, glide=None, mod=None):
    """SH-101-style mono synth: one oscillator mixing saw, a variable pulse and a square sub an octave down, a little
    noise, into a snappy 24 dB filter with key tracking and a fast envelope - the round, rubbery bass and bleep sequence
    sound of techno, minimal, acid and electro (gentler and rounder than the 303)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.02) * SR)
    env = _va.adsr(gate, 0.002, p.get('d', 0.18), p.get('s', 0.35), p.get('r', 0.05))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.04) if glide is not None else np.full(n, f)
    pw = p.get('pw', 0.35) + 0.1 * np.sin(2 * np.pi * 0.7 * t)
    x = _va.saw(fr, n) * p.get('saw', 0.6) + _va.pulse(fr, n, 0.0, pw) * 0.6 + _va.pulse(fr / 2, n, 0.0, 0.5) * p.get('sub', 0.5)
    x = x + 0.03 * _rng().standard_normal(n)
    kt = (f / 110.0) ** 0.5
    cut = p.get('cut', 500) * kt * (1 + p.get('envmod', 3.5) * np.exp(-t / p.get('fdecay', 0.08)))
    y = _va.vcf(x, cut, p.get('res', 0.35), 1.3)
    y = hp(y, 30) * env * 0.6
    return np.vstack([y, y])


def v_nordpluck(m, dur, p, glide=None, mod=None):
    """Sharp digital pluck (the late-90s / 2000s virtual-analog trance pluck): two saws with a touch of FM edge on the
    attack, a bright filter snapping shut very fast, a tight stereo spread - crisp, bouncy and clean, for trance arps
    and offbeat plucks."""
    f = float(mtof(m))
    gate = int(max(dur, 0.02) * SR)
    env = _va.adsr(gate, 0.001, p.get('d', 0.16), 0.05, 0.12)
    n = len(env)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    edge = np.sin(ph + 2.5 * np.exp(-t / 0.01) * np.sin(3 * ph)) * 0.4
    x = np.vstack([_va.saw(np.full(n, f * 2 ** (-6 / 1200)), n) + edge, _va.saw(np.full(n, f * 2 ** (6 / 1200)), n, 0.3) + edge])
    cut = 500 * (p.get('cut', 9000) / 500) ** np.exp(-t / p.get('fdecay', 0.045))
    y = _va.vcf(x, cut, 0.2, 1.2)
    return _hpf(y, 200) * env * 0.5


def v_ravestab(m, dur, p, glide=None, mod=None):
    """Rave stab (the early-90s hardcore / trance chord stab): a detuned saw-and-square stack with a downward pitch
    'whoop' into the note, a band-limited, slightly resonant filter and a hard, short envelope - huge and a bit
    cheesy, as it should be."""
    f = float(mtof(m))
    gate = int(min(max(dur, 0.05), 0.4) * SR)
    env = _va.adsr(gate, 0.001, 0.18, 0.4, 0.1)
    n = len(env)
    t = np.arange(n) / SR
    fr = f * 2 ** (p.get('whoop', 3.0) * np.exp(-t / 0.03) / 12)
    x = np.zeros((2, n))
    for k, c in enumerate((-14, -5, 5, 14)):
        x[k % 2] += _va.saw(fr * 2 ** (c / 1200), n, _rng().random())
    x += _va.pulse(fr, n, 0.2, 0.5)[None, :] * 0.6
    y = _va.vcf(x * 0.4, p.get('cut', 3800) * (1 + 0.8 * np.exp(-t / 0.06)), 0.3, 1.5)
    b, a = signal.butter(2, [180 / (SR / 2), 7000 / (SR / 2)], 'band')
    return signal.lfilter(b, a, y, axis=-1) * env * 0.6


for _name, _fn, _info, _roles, _gm in (('sh101', v_sh101, 'Mono synth (SH-101 style bass / bleeps)', ('bass', 'arp', 'lead'), 38),
                                       ('nordpluck', v_nordpluck, 'Sharp digital pluck (trance)', ('arp', 'lead', 'chords'), 81),
                                       ('ravestab', v_ravestab, 'Rave stab (90s hardcore / trance)', ('chords', 'arp', 'lead'), 81)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.73: psytrance family
def v_psyroll(m, dur, p, glide=None, mod=None):
    """Rolling psy bass, built the way psy producers build it: a SPLIT bass - a clean sine sub for the very bottom
    (under ~95 Hz, mono, steady) and a filtered saw / square on top for the bite - with the oscillators reset on every
    note (each of the three 16ths between the kicks attacks identically), a fast-attack, short-decay filter envelope
    (the 'pluck' on each note), a short amp envelope with almost no sustain (the note is gone before the next one or
    the kick), and a tiny random cutoff change per note so the roll breathes instead of machine-gunning.
    p: cut (filter peak), fdecay (s), res, sq (square mix), bite (top layer level), growl (FM grit, dark psy)."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.16), 0.02) * SR)
    env = _va.adsr(gate, 0.0008, p.get('d', 0.07), 0.12, 0.012)
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    ph = 2 * np.pi * f * t                              # phase reset: every note starts at 0
    sub = lp(np.sin(ph), 110) * np.minimum(1.0, t / 0.002)
    src = 2 * ((f * t) % 1.0) - 1                       # saw from phase 0
    src = src * 0.75 + np.sign(np.sin(ph)) * p.get('sq', 0.3)
    if p.get('growl'):
        src = np.sin(ph + float(p['growl']) * 2.5 * np.sin(2 * ph) * np.exp(-t / 0.05)) * 0.5 + src * 0.6
    var = 1 + 0.18 * (rng.random() - 0.5)
    cut = 140 + (p.get('cut', 2200) * var - 140) * np.exp(-t / p.get('fdecay', 0.026))
    bite = _va.vcf(src, cut, p.get('res', 0.35), 1.6)
    bite = hp(bite, 95)
    y = sub * 0.95 + bite * p.get('bite', 0.85)
    return np.tanh(y * 1.3) * env * 0.75


def v_goalead(m, dur, p, glide=None, mod=None):
    """Goa lead: two detuned saws and a square an octave down through a resonant low-pass that squelches - a fast
    envelope on every note plus a slow LFO that sweeps the filter over the phrase - with a little vibrato and glide:
    the bubbling, melodic, slightly eastern lead lines of 90s Goa trance."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.004, 0.15, 0.75, p.get('r', 0.1))
    n = len(env)
    t = np.arange(n) / SR
    fr = f + (float(mtof(glide)) - f) * np.exp(-t / 0.04) if glide is not None else np.full(n, f)
    fr = fr * 2 ** (np.clip((t - 0.15) / 0.3, 0, 1) * 12 * np.sin(2 * np.pi * 5.5 * t) / 1200)
    x = _va.saw(fr * 2 ** (7 / 1200), n) * 0.5 + _va.saw(fr * 2 ** (-7 / 1200), n) * 0.5 + _va.pulse(fr * 0.5, n, 0.0, 0.5) * 0.35
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * p.get('rate', 0.7) * t)
    cut = 350 + p.get('cut', 2600) * (0.55 * np.exp(-t / 0.09) + 0.45 * lfo)
    y = _va.vcf(x, cut, p.get('res', 0.62), 1.8)
    y = np.tanh(y * 1.4)
    return _ms_stereo(y, 35) * env * 0.45


def v_psyzap(m, dur, p, glide=None, mod=None):
    """Psy zap: a sine that dives from three octaves above the note down onto it in a few milliseconds, with a little
    FM and noise on the attack - the laser 'pew' / bubbling percussive blips of dark and forest psy."""
    f = float(mtof(m))
    n = int((min(dur, 0.35) + 0.08) * SR)
    t = np.arange(n) / SR
    fr = f * 2 ** (p.get('dive', 36) * np.exp(-t / p.get('speed', 0.012)) / 12)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = np.sin(ph + 1.2 * np.exp(-t / 0.03) * np.sin(3 * ph)) + 0.25 * hp(noise(n), 3000) * np.exp(-t * 200)
    env = np.exp(-t * p.get('decay', 14)) * np.minimum(1.0, t / 0.0005)
    y = x * env
    return _ms_stereo(y, 60) * 0.5


for _name, _fn, _info, _roles, _gm in (('psyroll', v_psyroll, 'Psy rolling bass (split sub + bite, phase reset)', ('bass',), 38),
                                       ('goalead', v_goalead, 'Goa lead (squelchy detuned saws)', ('lead', 'arp'), 81),
                                       ('psyzap', v_psyzap, 'Psy zap (laser blips, dark / forest psy)', ('arp', 'lead'), 81)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.75: festive / film-score orchestra
def v_kidchoir(m, dur, p, glide=None, mod=None):
    """Children's choir: young voices - pure, high and almost without vibrato, a softer, rounder 'ooh' with less of
    the adult chest resonance, a gentle swell and a little air. The innocent carol sound of a Christmas film score."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = _va.adsr(gate, p.get('a', 0.25), 0.4, 0.9, p.get('r', 0.7))
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    L = np.zeros(n)
    R = np.zeros(n)
    fr_ = (420, 900, 2700, 3600) if p.get('vowel', 'o') == 'o' else (850, 1300, 3000, 3900)
    for i in range(5):
        c = rng.normal(0, 5)
        vib = np.clip((t - 0.4) / 0.6, 0, 1) * rng.uniform(4, 9) * np.sin(2 * np.pi * rng.uniform(5.0, 5.8) * t + rng.random() * 6.28)
        ph = 2 * np.pi * np.cumsum(f * 2 ** ((c + vib) / 1200)) / SR + rng.random() * 6.28
        src = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph) + 0.06 * np.sin(4 * ph)
        v = src * 0.4
        for fc, g in zip(fr_, (1.0, 0.5, 0.18, 0.08)):
            b, a = signal.iirpeak(min(fc * (f / 500) ** 0.1, SR * 0.45) / (SR / 2), 4.0)
            v = v + g * signal.lfilter(b, a, src)
        v = v + 0.03 * bp(rng.standard_normal(n), 2000, 7000)
        d = int(rng.uniform(0, 0.025) * SR)
        v = np.concatenate([np.zeros(d), v[:n - d]])
        pan = 0.15 + 0.7 * i / 4
        L += v * np.cos(pan * np.pi / 2)
        R += v * np.sin(pan * np.pi / 2)
    y = hp(np.vstack([L, R]), 180)
    y = y / (np.sqrt(np.mean(y[:, :min(n, int(0.8 * SR))] ** 2)) + 1e-9) * 0.12
    return y * env


def v_piccolo(m, dur, p, glide=None, mod=None):
    """Piccolo: the little flute an octave above - bright, piercing and agile, almost a pure tone with a crisp chiff:
    the sparkling runs and 'falling snow' figures of a Christmas score."""
    y = v_flute(m, dur, dict(p, a=p.get('a', 0.03)))
    return eq(y, 'highshelf', 3000, 0.7, 3.0) * 0.85


def v_xylophone(m, dur, p, glide=None, mod=None):
    """Xylophone: hard mallets on rosewood bars tuned so the 2nd mode sits a twelfth up (3x) - short, dry, bright and
    clacky: the comic, scampering mallet runs of cartoon and family-film scoring."""
    f = float(mtof(m))
    n = int(min(0.9, 0.25 + 120 / f) * SR)
    t = np.arange(n) / SR
    y = _modes(f, n, [(1.0, 1.0, 9.0), (3.0, 0.45, 22.0), (6.2, 0.15, 45.0)], p.get('hard', 1.4))
    y = y + 0.18 * bp(_rng().standard_normal(n), 2500, 9000) * np.exp(-t * 400)
    y *= np.minimum(t / 0.0006, 1)
    return _ms_stereo(y, 15) * 0.4


def v_bassclarinet(m, dur, p, glide=None, mod=None):
    """Bass clarinet: a reed on a cylindrical bore, so mostly ODD harmonics - a dark, hollow, woody tone with a soft
    breathy edge; staccato it's the sneaky, comic low-woodwind sound of cartoon villains."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.03), 0.2, 0.85, p.get('r', 0.08))
    n = len(env)
    t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f * 2 ** (np.clip((t - 0.3) / 0.4, 0, 1) * 8 * np.sin(2 * np.pi * 5 * t) / 1200)) / SR
    x = sum((1.0 / k) * np.sin(k * ph) for k in (1, 3, 5, 7, 9)) + 0.12 * np.sin(2 * ph)
    x = _va.vcf(x, 900 + 1800 * env, 0.1, 1.0)
    br = _aspirate(bp(_rng().standard_normal(n), 400, 2500), f, ph) * 0.04
    y = np.tanh((x + br) * 1.2) * env
    return _ms_stereo(y, 25) * 0.42


def d_triangle(p):
    """Triangle: a steel rod bent into a triangle - a high, ringing, inharmonic shimmer with a bright 'ting'."""
    n = int(p.get('len', 1.6) * SR)
    t = np.arange(n) / SR
    y = _modes(p.get('pitch', 1250.0), n, [(1.0, 0.6, 2.5), (2.76, 0.8, 2.0), (5.4, 0.7, 2.8), (8.9, 0.5, 3.5), (12.1, 0.35, 4.0)], 1.0)
    y = hp(y, 2500) + 0.25 * hp(noise(n), 6000) * np.exp(-t * 300)
    return fade_out(y * np.minimum(t / 0.0005, 1), 0.1)


def d_windchime(p):
    """Wind chimes / bell tree: a quick glissando of small tuned bars, each ringing on - the 'magic' shimmer at the
    start of a scene."""
    n = int(2.2 * SR)
    y = np.zeros(n)
    rng = _rng()
    base = p.get('pitch', 2000.0)
    for k in range(12):
        s0 = int((k * 0.035 + rng.uniform(0, 0.01)) * SR)
        f = base * 2 ** ((11 - k) * 0.17 + rng.normal(0, 0.02))
        m = n - s0
        y[s0:] += _modes(f, m, [(1.0, 1.0, 3.0), (2.8, 0.4, 5.0)], 1.0) * (0.6 + 0.4 * rng.random())
    return fade_out(hp(y, 1500), 0.2)


DRUMS.update({'triangle': d_triangle, 'windchime': d_windchime})
for _name, _fn, _info, _roles, _gm in (('kidchoir', v_kidchoir, "Children's choir (pure, high)", ('pad', 'lead', 'chords'), 53),
                                       ('piccolo', v_piccolo, 'Piccolo (bright, sparkling)', ('lead', 'arp'), 73),
                                       ('xylophone', v_xylophone, 'Xylophone (hard, comic)', ('arp', 'lead'), 14),
                                       ('bassclarinet', v_bassclarinet, 'Bass clarinet (dark, comic low woodwind)', ('bass', 'lead', 'arp'), 72)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.77: club synths (analog character)
# Built for the per-sample ladder filter (va.vcf in analog mode): each note responds to its velocity layer (brighter
# and more envelope when played harder) and every take differs a little - tuning, cutoff, envelope times.

def _blip(n, cents=25.0, tau=0.012):
    """Pitch 'blip' into the note (cents above, settling in tau s) - the snap of an analog envelope on the VCO."""
    t = np.arange(n) / SR
    return 2 ** (cents * np.exp(-t / tau) / 1200)


def _click(n, level=0.25, hp_hz=2500.0, dur=0.006):
    """A short noise transient on the attack (the 'tick' that makes a stab or pluck cut through a dense mix)."""
    k = min(n, int(dur * SR))
    y = np.zeros(n)
    if k > 8:
        y[:k] = hp(_rng().standard_normal(k), hp_hz) * np.exp(-np.arange(k) / (k / 4)) * level
    return y


def v_housechord(m, dur, p, glide=None, mod=None):
    """House chord stab, built like a hardware poly's chord-memory stab: two saws a few cents apart and a square
    an octave down, a pitch snap and a noise tick on the attack, through a resonant ladder that snaps from bright to
    warm, with a short body and a little drive - the stab that sits on the off-beat of a house groove."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.6), 0.04) * SR)
    env = _va.adsr(gate, 0.0015, p.get('d', 0.2), p.get('s', 0.25), p.get('r', 0.09))
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    fr = f * _blip(n, 20.0, 0.01)
    x = np.vstack([_va.saw(fr * 2 ** (-7 / 1200), n, rng.random()), _va.saw(fr * 2 ** (7 / 1200), n, rng.random())])
    x += _va.pulse(fr / 2, n, rng.random(), 0.5)[None, :] * 0.35
    x += _click(n, 0.3)[None, :]
    cut = 420 + (p.get('cut', 6500) - 420) * np.exp(-t / p.get('fdecay', 0.09))
    y = _va.vcf(x * 0.7, cut, p.get('res', 0.42), 1.5)
    return _hpf(y, 170) * env * 0.62


def v_dubchord(m, dur, p, glide=None, mod=None):
    """Dub-techno chord: a soft stack of detuned saws, a dark resonant low-pass that barely opens, a slow-ish decay -
    the muffled chord that lives in a long echo and a big reverb (the track supplies those)."""
    f = float(mtof(m))
    gate = int(max(min(dur, 1.0), 0.05) * SR)
    env = _va.adsr(gate, 0.004, p.get('d', 0.45), p.get('s', 0.2), p.get('r', 0.35))
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    x = np.zeros((2, n))
    for k, c in enumerate((-9, -3, 4, 10)):
        x[k % 2] += _va.saw(np.full(n, f * 2 ** (c / 1200)), n, rng.random()) * 0.5
    cut = p.get('cut', 900) * (1 + 0.9 * np.exp(-t / 0.15))
    y = _va.vcf(x, cut, p.get('res', 0.5), 1.25)
    return _hpf(y, 200) * env * 0.85


def v_bleep(m, dur, p, glide=None, mod=None):
    """Techno bleep: a sine with a fast FM 'blip' on the attack (ratio 2:1, the index dying in a few ms) and a tiny
    resonant tick - the clean, hypnotic sequencer bleep of minimal and Detroit-style techno."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.25), 0.02) * SR)
    env = _va.adsr(gate, 0.0008, p.get('d', 0.09), 0.0, 0.05)
    n = len(env)
    t = np.arange(n) / SR
    idx = p.get('fm', 3.0) * (0.6 + 0.5 * float(p.get('vel', 0.8))) * np.exp(-t / 0.012)
    ph = 2 * np.pi * f * t * float(_blip(1, 8.0)[0])
    y = np.sin(ph + idx * np.sin(2 * ph))
    y = y + 0.25 * _va.vcf(_va.saw(np.full(n, f), n), 300 + 5000 * np.exp(-t / 0.02), 0.5, 1.0)
    y = y * env
    return _ms_stereo(y, 9) * 0.5


def v_trancepluck(m, dur, p, glide=None, mod=None):
    """Layered trance pluck, stacked the way it's done in a big trance arp: a supersaw pluck for the width, a
    triangle body an octave down for weight, and a noise tick for the attack - each through its own envelope, the
    saw layer through the ladder snapping shut."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.5), 0.02) * SR)
    env = _va.adsr(gate, 0.001, p.get('d', 0.24), 0.08, 0.16)
    n = len(env)
    t = np.arange(n) / SR
    saws = _va.jp_supersaw(f, n, 0.35, 0.65, 0.9)
    cut = 380 * (p.get('cut', 8000) / 380) ** np.exp(-t * p.get('fdecay', 11))
    top = _hpf(_va.vcf(saws, cut, 0.3, 1.2), 160)
    body = tri(f / 2, n) * np.exp(-t / 0.13) * 0.32
    y = top * env + body[None, :] * np.minimum(1.0, t / 0.002) + _click(n, 0.18, 4000)[None, :]
    return y * 0.62


def v_analoglead(m, dur, p, glide=None, mod=None):
    """Analog mono lead: two saws and a pulse with slow width movement, three-voice unison, a ladder filter with its
    own envelope (bite on the attack, then it settles), glide and a delayed vibrato - a lead that breathes, for
    trance, techno and progressive."""
    return _va.voice(m, dur, dict(p, cut=p.get('cut', 1600)), glide, saw_mix=1.0, pulse_mix=0.45, pw=0.4, pwm=0.5,
                     pwm_rate=0.4, unison=3, detune=9, spread=0.55, res=0.32, fenv=2.0, fd=0.35, fs=0.35,
                     amp=(0.006, 0.4, 0.85, 0.22), drive=1.45, keytrack=0.55, vib=p.get('vib', 16), vib_delay=0.3,
                     slide=0.07, drift=2.5) * 0.48


def v_hypnoseq(m, dur, p, glide=None, mod=None):
    """Hypnotic techno sequence: saw + square through a resonant ladder, a short decay, the cutoff and resonance
    moving a little on every note (a modular sequence with a randomised CV) - the rolling, evolving one-bar line of
    hypnotic and Berlin techno."""
    rng = _rng()
    c = p.get('cut', 1300) * 2 ** rng.normal(0.0, 0.35)
    return _va.voice(m, dur, dict(p, cut=c), glide, saw_mix=1.0, pulse_mix=0.6, pw=0.5, unison=1, res=0.55 + 0.15 * rng.random(),
                     fenv=1.6, fd=0.09, fs=0.0, amp=(0.001, p.get('d', 0.16), 0.0, 0.05), drive=1.8, keytrack=0.4,
                     drift=1.0, stereo=False) * 0.55


def v_splitbass(m, dur, p, glide=None, mod=None):
    """Split club bass, the modern way: a clean sine sub for the very bottom (under ~100 Hz, mono, steady) and a
    saw / square top through the ladder for the bite and the groove, each with its own envelope - the sub stays
    solid on any system while the top carries the movement. House, techno and trance."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.002, p.get('d', 0.22), p.get('s', 0.55), 0.04)
    n = len(env)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    if glide is not None:
        f0 = float(mtof(glide))
        fr = f + (f0 - f) * np.exp(-t / 0.05)
        ph = 2 * np.pi * np.cumsum(fr) / SR
    sub = np.sin(ph) * (0.75 if f < 110 else 0.45)
    top = (2 * ((ph / (2 * np.pi)) % 1.0) - 1) * 0.7 + np.sign(np.sin(ph)) * 0.25
    cut = 220 + (p.get('cut', 1900) - 220) * np.exp(-t / p.get('fdecay', 0.11))
    bite = _hpf(_va.vcf(top, cut, p.get('res', 0.3), 1.6), 110, 2)
    y = (lp(sub, 140) + bite * p.get('bite', 0.55)) * env
    return np.vstack([y, y]) * 0.6


for _name, _fn, _info, _roles, _gm in (
        ('housechord', v_housechord, 'House chord stab (chord memory, punchy)', ('chords', 'arp', 'lead'), 81),
        ('dubchord', v_dubchord, 'Dub-techno chord (dark, for long echoes)', ('chords', 'arp', 'pad'), 81),
        ('bleep', v_bleep, 'Techno bleep (FM blip, hypnotic)', ('arp', 'lead'), 81),
        ('trancepluck', v_trancepluck, 'Layered trance pluck (saws + body + tick)', ('arp', 'lead', 'chords'), 81),
        ('analoglead', v_analoglead, 'Analog mono lead (breathing, glide)', ('lead', 'arp'), 81),
        ('hypnoseq', v_hypnoseq, 'Hypnotic techno sequence (resonant, moving)', ('arp', 'bass', 'lead'), 38),
        ('splitbass', v_splitbass, 'Split club bass (clean sub + filtered top)', ('bass',), 38)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.79: instruments from around the world,
# a few rare acoustic colours, and synth engines (wavetable, granular, formant chops, 808 variants, hollow pluck)

def _st(y, d=25):
    y = np.asarray(y, float)
    return y if y.ndim == 2 else _ms_stereo(y, d)


def _gate_tail(y, dur, tail=0.15):
    g = int(max(dur, 0.03) * SR)
    n = y.shape[-1]
    if g < n:
        y = y.copy()
        y[..., g:] *= np.exp(-np.arange(n - g) / (tail * SR))
    return y


def _glide_freq(f, n, glide, tau):
    t = np.arange(n) / SR
    if glide is None:
        return np.full(n, f)
    f0 = float(mtof(glide))
    return f + (f0 - f) * np.exp(-t / tau)


def v_theremin(m, dur, p, glide=None, mod=None):
    """Theremin: an almost pure tone (a little 2nd and 3rd harmonic from the heterodyne), slid continuously from the
    last note (the player's hand never jumps), a slow swell and a wide, singing vibrato - the haunted 50s sci-fi
    and spooky-surf lead."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    env = _va.adsr(gate, p.get('a', 0.09), 0.3, 0.9, p.get('r', 0.25))
    n = len(env)
    t = np.arange(n) / SR
    fr = _glide_freq(f, n, glide, 0.11)
    vib = np.clip((t - 0.12) / 0.3, 0, 1) * p.get('vib', 32) * np.sin(2 * np.pi * 6.1 * t)
    ph = 2 * np.pi * np.cumsum(fr * 2 ** (vib / 1200)) / SR
    y = (np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)) * env
    return _st(y, 40) * 0.5


def v_handpan(m, dur, p, glide=None, mod=None):
    """Handpan: a steel shell with tuned dimples struck by the fingertips - a soft-attack, round fundamental, its
    octave and a fifth above that (the 'tuned harmonics' of each note field), a long shimmering ring and the faint
    hum of the shell."""
    f = float(mtof(m))
    n = int(min(4.0, 1.8 + 300 / f) * SR)
    t = np.arange(n) / SR
    k = (f / 293.7) ** 0.4
    y = _modes(f, n, [(1.0, 1.0, 0.9 * k), (2.0, 0.45, 1.5 * k), (3.0, 0.22, 2.4 * k), (4.02, 0.06, 5 * k)], p.get('hard', 0.7))
    beat = 1 + 0.12 * np.sin(2 * np.pi * 2.3 * t)          # two nearly identical modes beating: the shimmer
    y = y * beat * (1 - np.exp(-t / 0.004))
    y += 0.03 * lp(_rng().standard_normal(n), 900) * np.exp(-t * 60)    # the finger on the steel
    return _st(y, 35) * 0.45


def v_duduk(m, dur, p, glide=None, mod=None):
    """Duduk: an apricot-wood oboe with a huge, soft double reed - dark, velvety and mournful; a nasal formant body,
    a lot of breath, notes scooped up into from below and a slow, narrow vibrato."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    env = _va.adsr(gate, p.get('a', 0.12), 0.4, 0.88, p.get('r', 0.3))
    n = len(env)
    t = np.arange(n) / SR
    vib = np.clip((t - 0.35) / 0.5, 0, 1) * 9 * np.sin(2 * np.pi * 4.6 * t)
    fr = _glide_freq(f, n, glide, 0.08) * 2 ** ((-45 * np.exp(-t / 0.07) + vib) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    src = sum((0.9 ** k) / k * np.sin(k * ph) for k in range(1, 12) if f * k < 9000)
    body = eq(eq(eq(src, 'peak', 520, 2.0, 7.0), 'peak', 1250, 2.5, 5.0), 'highshelf', 2500, 0.7, -9.0)
    breath = _aspirate(bp(_rng().standard_normal(n), f, min(f * 5, 15000)), f, ph) * 0.18
    y = (body * 0.6 + breath) * env
    return _st(y, 30) * 0.5


def v_erhu(m, dur, p, glide=None, mod=None):
    """Erhu: two strings bowed between them, over a small python-skin drum - a nasal, singing, almost vocal tone,
    sliding into notes from below, with a deep expressive vibrato made by the finger's pressure."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    env = _va.adsr(gate, p.get('a', 0.07), 0.3, 0.9, p.get('r', 0.2))
    n = len(env)
    t = np.arange(n) / SR
    vib = np.clip((t - 0.15) / 0.35, 0, 1) * p.get('vib', 28) * np.sin(2 * np.pi * 5.4 * t)
    fr = _glide_freq(f, n, glide, 0.07) * 2 ** ((-80 * np.exp(-t / 0.05) + vib) / 1200)
    x = _va.saw(fr, n, _rng().random())
    y = eq(eq(eq(x, 'peak', 850, 2.0, 7.0), 'peak', 1750, 2.5, 6.0), 'peak', 3000, 3.0, 3.0)
    y = lp(hp(y, 250), 6000)
    y += 0.05 * bp(_rng().standard_normal(n), 2000, 8000) * (0.4 + 0.6 * np.exp(-t / 0.08))     # the bow hair
    return _st(y * env, 30) * 0.45


def v_guzheng(m, dur, p, glide=None, mod=None):
    """Guzheng: a long zither with 21 steel-nylon strings over movable bridges, plucked with finger picks - a bright,
    ringing pluck, and on long notes the left hand pressing the string behind the bridge to make the pitch sway
    (rou) or bend up a step (an)."""
    f = float(mtof(m))
    n = int((min(dur, 3.0) + 1.2) * SR)
    t = np.arange(n) / SR
    y = _pluck(f, n, 0.92, 0.9, 0.00015, 24, 0.22)
    if dur > 0.6:                                        # rou: the pressing vibrato on long notes
        dep = np.clip((t - 0.25) / 0.3, 0, 1) * 0.35 * np.sin(2 * np.pi * 4.5 * t)
        idx = np.clip(np.cumsum(2 ** (dep / 12)), 0, n - 1)
        y = np.interp(idx, np.arange(n), y)
    y = eq(hp(y, 120), 'peak', 2400, 1.4, 3.5) + 0.12 * hp(_rng().standard_normal(n), 3500) * np.exp(-t * 400)
    return _st(_gate_tail(y, dur + 0.8, 0.5), 60) * 0.45


def v_pipa(m, dur, p, glide=None, mod=None):
    """Pipa: a pear-shaped lute plucked with the fingernails - a bright, snappy, short-lived attack; long notes
    are sustained by lunzhi, the rapid tremolo of the five fingers (about 12 plucks a second)."""
    f = float(mtof(m))
    n = int((min(dur, 2.5) + 0.4) * SR)
    one = _pluck(f, int(0.6 * SR), 0.88, 4.5, 0.0003, 20, 0.35)
    one = one + 0.18 * hp(_rng().standard_normal(len(one)), 3000) * np.exp(-np.arange(len(one)) / SR * 500)
    y = np.zeros(n)
    hits = [0.0] if dur < 0.45 else list(np.arange(0.0, dur, 1 / 12.0))
    for k, h in enumerate(hits):
        s0 = int(h * SR)
        ln = min(len(one), n - s0)
        if ln > 0:
            y[s0:s0 + ln] += one[:ln] * (1.0 if k == 0 else 0.55 + 0.1 * _rng().random())
    y = eq(hp(y, 180), 'peak', 1800, 1.5, 4.0)
    return _st(y, 40) * 0.42


def v_dizi(m, dur, p, glide=None, mod=None):
    """Dizi: a bamboo flute with a membrane (dimo) glued over an extra hole - the membrane buzzes, giving the tone
    its bright, reedy, slightly raspy edge over a breathy flute body."""
    y = np.asarray(v_flute(m, dur, dict(p, a=p.get('a', 0.04))), float)
    f = float(mtof(m))
    buzz = np.tanh(bp(y.mean(axis=0), max(f * 2, 900), min(f * 8, 12000)) * 6.0) * 0.18
    y = y + buzz[None, :]
    return eq(y, 'peak', 3200, 1.5, 3.0)


def v_kora(m, dur, p, glide=None, mod=None):
    """Kora: a West African 21-string harp-lute over a big calabash gourd covered in cowhide - a clear, harp-like
    pluck with a warm, woody bloom from the gourd and a faint buzz from the metal jingles."""
    f = float(mtof(m))
    n = int((min(dur, 2.5) + 0.9) * SR)
    t = np.arange(n) / SR
    y = _pluck(f, n, 0.85, 1.3, 0.0001, 18, 0.25)
    y = eq(eq(y, 'peak', 190, 1.5, 6.0), 'peak', 2800, 2.0, 2.0)
    env = np.abs(signal.lfilter([0.002], [1, -0.998], np.abs(y)))
    y = y + 0.05 * np.tanh(bp(y, 2500, 6000) * 20) * (env / (env.max() + 1e-9))
    return _st(hp(y, 90) * np.minimum(t / 0.001, 1), 45) * 0.5


def v_balafon(m, dur, p, glide=None, mod=None):
    """Balafon: wooden bars over calabash resonators, each gourd with a hole covered by a spider-egg membrane that
    buzzes - a dry, woody knock with a rattly buzz in its bloom."""
    f = float(mtof(m))
    n = int(min(1.4, 0.4 + 200 / f) * SR)
    t = np.arange(n) / SR
    k = (f / 261.6) ** 0.5
    y = _modes(f, n, [(1.0, 1.0, 5.5 * k), (3.9, 0.35, 16 * k), (9.6, 0.12, 40 * k)], p.get('hard', 1.1))
    bloom = y * (1 - np.exp(-t / 0.015))
    buzz = np.tanh(bp(bloom, 300, 3000) * 14) * 0.12 * np.exp(-t * 6)
    y = y + buzz + 0.1 * lp(_rng().standard_normal(n), 2500) * np.exp(-t * 400)
    return _st(y * np.minimum(t / 0.0008, 1), 20) * 0.45


def v_hurdygurdy(m, dur, p, glide=None, mod=None):
    """Hurdy-gurdy: a rosined wheel bows the strings while keys stop the melody string - a nasal, buzzy, continuous
    tone over a drone a fifth and an octave below, the 'dog' bridge giving it its raspy edge."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    env = _va.adsr(gate, 0.03, 0.2, 0.92, 0.15)
    n = len(env)
    t = np.arange(n) / SR
    mel = _va.saw(np.full(n, f), n, _rng().random()) + 0.6 * _va.saw(np.full(n, f * 2 ** (3 / 1200)), n, _rng().random())
    drone = 0.35 * _va.saw(np.full(n, f / 2), n) + 0.25 * _va.saw(np.full(n, f * 2 / 3), n)
    x = mel + drone
    rasp = np.tanh(hp(x, 1500) * 3) * 0.2 * (1 + 0.5 * np.sin(2 * np.pi * 7 * t))
    y = eq(eq(lp(x, 5000), 'peak', 1100, 1.5, 6.0), 'peak', 300, 1.0, -3.0) + rasp
    return _st(hp(y, 100) * env, 30) * 0.32


def v_cimbalom(m, dur, p, glide=None, mod=None):
    """Cimbalom: a big hammered dulcimer - courses of three or four steel strings a few cents apart, struck with
    cotton-tipped hammers: a bright, ringing, shimmering note that sustains (the damper pedal is usually up)."""
    f = float(mtof(m))
    n = int((min(dur, 2.5) + 1.5) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for c in (-4, 0, 3, 6):
        y += _pluck(f * 2 ** (c / 1200), n, 0.9, 0.7, 0.0004, 22, 0.18)
    y = eq(hp(y, 110), 'peak', 3500, 1.2, 3.0) * 0.4 + 0.1 * bp(_rng().standard_normal(n), 1500, 6000) * np.exp(-t * 500)
    return _st(_gate_tail(y, dur + 1.0, 0.7), 50) * 0.42


def v_glassharmonica(m, dur, p, glide=None, mod=None):
    """Glass harmonica: wet fingers rubbing spinning glass bowls - an eerie, pure, floating tone that swells in
    slowly, with a soft octave and the faint flutter of the rubbing (it was said to drive its players mad)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = _va.adsr(gate, p.get('a', 0.25), 0.4, 0.9, p.get('r', 1.2))
    n = len(env)
    t = np.arange(n) / SR
    flutter = 1 + 0.06 * np.sin(2 * np.pi * 7.3 * t) + 0.03 * np.sin(2 * np.pi * 11.1 * t)
    y = (np.sin(2 * np.pi * f * t) + 0.18 * np.sin(4 * np.pi * f * t + 0.5) + 0.04 * np.sin(6 * np.pi * f * t)) * flutter
    y = y + 0.01 * bp(_rng().standard_normal(n), f * 3, min(f * 8, 15000))
    return _st(y * env, 60) * 0.45


def v_waterphone(m, dur, p, glide=None, mod=None):
    """Waterphone: bronze rods around a steel bowl with water inside, bowed - inharmonic, metallic howls whose pitch
    bends and wobbles as the water moves (the horror-film sound)."""
    f = float(mtof(m))
    n = int((min(dur, 4.0) + 1.5) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    y = np.zeros(n)
    for r, a, d in ((1.0, 1.0, 0.7), (2.76, 0.5, 1.1), (5.40, 0.35, 1.6), (8.93, 0.2, 2.4)):
        wob = 2 ** (40 * np.sin(2 * np.pi * (0.4 + rng.random() * 0.5) * t + rng.random() * 6) / 1200)
        ph = 2 * np.pi * np.cumsum(f * r * wob) / SR
        y += a * np.sin(ph) * np.exp(-t * d)
    bow = np.minimum(t / 0.35, 1) * (1 + 0.15 * rng.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1)))
    y = y * bow + 0.02 * hp(rng.standard_normal(n), 4000) * np.exp(-t * 2)
    return _st(hp(y, 200), 70) * 0.35


_WT_FRAMES = None


def _wavetable():
    """A 32-frame wavetable that morphs sine -> triangle-ish -> saw -> hollow (odd) -> a formant-like buzz; each
    frame band-limited by the harmonic count (computed once, then read per note)."""
    global _WT_FRAMES
    if _WT_FRAMES is None:
        L, H = 2048, 64
        k = np.arange(1, H + 1)
        ph = np.arange(L) / L * 2 * np.pi
        frames = []
        for i in range(32):
            u = i / 31
            saw_a = 1 / k
            sine_a = (k == 1).astype(float)
            odd_a = np.where(k % 2 == 1, 1 / k, 0.0)
            form_a = np.exp(-((k - 7) / 2.5) ** 2) + 0.4 / k
            if u < 0.33:
                a = sine_a * (1 - u / 0.33) + saw_a * (u / 0.33)
            elif u < 0.66:
                v = (u - 0.33) / 0.33
                a = saw_a * (1 - v) + odd_a * v
            else:
                v = (u - 0.66) / 0.34
                a = odd_a * (1 - v) + form_a * v
            w = np.sum(a[:, None] * np.sin(k[:, None] * ph[None, :]), axis=0)
            frames.append(w / (np.max(np.abs(w)) + 1e-9))
        _WT_FRAMES = np.array(frames)
    return _WT_FRAMES


def v_wavetable(m, dur, p, glide=None, mod=None):
    """Wavetable synth: the oscillator scans through 32 frames (sine -> saw -> hollow -> vocal buzz) as the note
    plays - an envelope sweeps the position up, a slow LFO keeps it moving - two detuned voices, through the ladder
    filter. Modern bass-music and progressive leads / chords."""
    W = _wavetable()
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, p.get('a', 0.005), p.get('d', 0.4), p.get('s', 0.75), p.get('r', 0.25))
    n = len(env)
    t = np.arange(n) / SR
    fr = _glide_freq(f, n, glide, 0.06)
    pos = np.clip(p.get('pos', 0.15) + 0.55 * (1 - np.exp(-t / p.get('scan', 0.6))) + 0.08 * np.sin(2 * np.pi * 0.3 * t), 0, 0.999)
    fi = pos * 31
    i0 = np.floor(fi).astype(int)
    fr_ = fi - i0
    i1 = np.minimum(i0 + 1, 31)
    out = []
    rng = _rng()
    for c in (-7, 7):
        ph = (rng.random() + np.cumsum(fr * 2 ** (c / 1200)) / SR) % 1.0
        j = (ph * 2048).astype(int)
        out.append(W[i0, j] * (1 - fr_) + W[i1, j] * fr_)
    x = np.vstack(out)
    y = _va.vcf(x, p.get('cut', 4500) * (0.5 + 0.5 * np.exp(-t / 0.3)) + 300, p.get('res', 0.2), 1.2)
    return y * env * 0.5


def v_granular(m, dur, p, glide=None, mod=None):
    """Granular pad: hundreds of short grains (30-90 ms) taken from a rich, slowly moving source at the note's pitch,
    each with its own position, a little pitch scatter and its own place in the stereo field - a shimmering,
    breathing cloud rather than a held note. Ambient, cinematic, psy textures."""
    f = float(mtof(m))
    gate = int(max(dur, 0.2) * SR)
    env = _va.adsr(gate, p.get('a', 0.6), 0.6, 0.85, p.get('r', 1.5))
    n = len(env)
    rng = _rng()
    src_n = int(1.5 * SR)
    src = _va.jp_supersaw(f, src_n, 0.3, 0.6, 0.5).mean(axis=0)
    src = lp(src, min(8000, f * 12)) + 0.4 * np.sin(2 * np.pi * f * 2 * np.arange(src_n) / SR)
    out = np.zeros((2, n))
    density = p.get('density', 60)                         # grains per second
    for s0 in np.sort(rng.uniform(0, n, int(density * n / SR))).astype(int):
        gl = int(rng.uniform(0.03, 0.09) * SR)
        if s0 + gl >= n:
            continue
        rate = 2 ** (rng.normal(0, 0.08) / 12 + (12 / 12 if rng.random() < 0.12 else 0))   # a few an octave up
        pos = int(rng.uniform(0, src_n - gl * 2.2))
        idx = pos + np.arange(gl) * rate
        g = np.interp(idx, np.arange(src_n), src) * np.hanning(gl)
        pan = rng.random()
        out[0, s0:s0 + gl] += g * np.cos(pan * np.pi / 2)
        out[1, s0:s0 + gl] += g * np.sin(pan * np.pi / 2)
    return hp(out, 120) * env * (0.9 / np.sqrt(max(1.0, density / 30)))


_FCHOP_VOWELS = ('a', 'o', 'e', 'i', 'u')


def v_formantchop(m, dur, p, glide=None, mod=None):
    """Formant vocal chop: a breathy glottal buzz shaped into a vowel - a different vowel on each note, gliding into
    the next vowel as it ends ('ah-ee', 'oh-ay') - the pitched vocal-chop hook of future bass, house and garage,
    without needing a sample."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.6), 0.05) * SR)
    env = _va.adsr(gate, 0.004, 0.15, 0.6, 0.06)
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    fr = f * 2 ** ((-30 * np.exp(-t / 0.03)) / 1200)
    x = _va.saw(fr, n, rng.random()) * 0.8 + 0.15 * rng.standard_normal(n)
    v1, v2 = rng.choice(_FCHOP_VOWELS, 2, replace=False)
    a = _va.formant(x, str(v1), 9.0)
    b = _va.formant(x, str(v2), 9.0)
    mix = np.clip((t - 0.6 * n / SR) / (0.4 * n / SR + 1e-9), 0, 1)
    y = a * (1 - mix) + b * mix
    return _st(hp(y, 200) * env, 18) * 0.9


def v_808dist(m, dur, p, glide=None, mod=None):
    """Distorted 808: the trap 808 driven hard into a clipper so its harmonics carry it on small speakers - gritty
    and loud, the low end kept round underneath."""
    y = np.asarray(i_808(m, dur, p, glide, mod), float)
    lo_ = lp(y, 90)
    hi_ = np.tanh((y - lo_ + lo_ * 0.6) * 5.0) * 0.5
    return lo_ * 0.8 + hi_


def v_808long(m, dur, p, glide=None, mod=None):
    """Long-glide 808: the 808 with a slow, deep slide between notes and a longer tail - the drill / UK sliding 808."""
    return i_808(m, dur, dict(p, slide=p.get('slide', 0.16)), glide, mod)


def v_808punch(m, dur, p, glide=None, mod=None):
    """Punchy 808: a short 808 with a fast pitch drop and a click on top - tight and bouncy, for faster patterns."""
    f = float(mtof(m))
    n = int(min(max(dur, 0.12), 0.7) * SR)
    t = np.arange(n) / SR
    fr = f * 2 ** (24 * np.exp(-t / 0.012) / 12)
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.35)
    y = np.tanh(y * 1.6) / np.tanh(1.6)
    y[:int(0.003 * SR)] += hp(_rng().standard_normal(int(0.003 * SR)), 2000) * 0.4
    return _st(fade_out(y, 0.02), 0) * 0.85


def v_hollowpluck(m, dur, p, glide=None, mod=None):
    """Hollow pluck: a waveguide string plucked in the middle (so the even harmonics cancel - hollow, clarinet-like)
    with a short body - the woody, hollow pluck of melodic house and future garage."""
    f = float(mtof(m))
    gate = int(max(dur, 0.04) * SR)
    n = gate + int(0.3 * SR)
    exc = _bass_exc(f, 'finger', p.get('tone', 1.0))
    y = _va.string(f, n, exc, t60=p.get('t60', 0.9), bright=0.55, gate=gate, mute_t60=0.15, pickup=0.5)
    y = eq(hp(y, 150), 'peak', 900, 1.2, 3.0)
    return _st(y, 22) * 0.6


for _name, _fn, _info, _roles, _gm in (
        ('theremin', v_theremin, 'Theremin (sliding, haunted)', ('lead',), 80),
        ('handpan', v_handpan, 'Handpan (soft steel, shimmering)', ('arp', 'lead', 'chords'), 114),
        ('duduk', v_duduk, 'Duduk (dark, mournful reed)', ('lead',), 68),
        ('erhu', v_erhu, 'Erhu (Chinese two-string fiddle)', ('lead',), 110),
        ('guzheng', v_guzheng, 'Guzheng (Chinese zither)', ('arp', 'lead', 'chords'), 107),
        ('pipa', v_pipa, 'Pipa (Chinese lute, tremolo)', ('arp', 'lead'), 106),
        ('dizi', v_dizi, 'Dizi (Chinese bamboo flute, buzzing)', ('lead', 'arp'), 77),
        ('kora', v_kora, 'Kora (West African harp-lute)', ('arp', 'lead', 'chords'), 46),
        ('balafon', v_balafon, 'Balafon (West African xylophone, buzzing)', ('arp', 'lead'), 13),
        ('hurdygurdy', v_hurdygurdy, 'Hurdy-gurdy (wheel fiddle with drones)', ('lead', 'pad'), 109),
        ('cimbalom', v_cimbalom, 'Cimbalom (hammered dulcimer)', ('arp', 'lead', 'chords'), 15),
        ('glassharmonica', v_glassharmonica, 'Glass harmonica (eerie, floating)', ('pad', 'lead', 'chords'), 92),
        ('waterphone', v_waterphone, 'Waterphone (horror howls)', ('pad', 'lead'), 99),
        ('wavetable', v_wavetable, 'Wavetable synth (morphing)', ('lead', 'chords', 'arp', 'bass'), 81),
        ('granular', v_granular, 'Granular pad (shimmering cloud)', ('pad', 'chords'), 95),
        ('formantchop', v_formantchop, 'Formant vocal chop (synth, no sample)', ('lead', 'arp'), 54),
        ('808dist', v_808dist, '808 distorted (gritty)', ('bass',), 38),
        ('808long', v_808long, '808 long glide (sliding)', ('bass',), 38),
        ('808punch', v_808punch, '808 punchy (short, bouncy)', ('bass',), 38),
        ('hollowpluck', v_hollowpluck, 'Hollow pluck (woody, mid-plucked string)', ('arp', 'lead', 'chords'), 46)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


def v_chuggtr(m, dur, p, glide=None, mod=None):
    """Down-tuned extended-range metal guitar (deathcore / grind / djent): a low, thick string through a tight boost,
    two hard clipping stages and a steep cabinet, quad-tracked - two separately played takes hard left and right, so
    the wall is wide and never phasey - and a noise gate that slams shut the moment the note stops (the 'chug' stops
    dead, the silence between chugs is the groove). Palm mutes ('pm') give the deep, percussive chug."""
    takes = []
    for k in range(2):
        y, pm = _eg_string(m + (0.02 if k else 0.0), dur, dict(p, tone=p.get('tone', 1.5) + 0.25 * k), mod, 4.0, 0.85 - 0.1 * k,
                           0.1 + 0.08 * k)                # the second take: a few cents off, another pick position
        if k:
            y = np.concatenate([np.zeros(int(0.0015 * SR)), y])[:len(y)]   # ... and a few ms late, like a real double
        y = hp(y, 90)
        y = _vb.dist(eq(y, 'peak', 700, 0.9, 6.0) * p.get('gain', 26.0), 1.0, 'hard')    # tight boost: mids into the clip
        y = _vb.dist(y * 2.5, 1.0)
        y = eq(eq(eq(y, 'peak', 85, 1.0, 5.0 if pm else 3.0), 'peak', 500, 0.9, -6.0), 'peak', 2300, 1.2, 4.0)
        b, a = signal.butter(4, 5200 / (SR / 2))
        y = signal.lfilter(b, a, y)
        g = int(max(dur, 0.03) * SR)
        if g < len(y):                                   # the gate: shut within ~8 ms of the note's end
            y[g:] *= np.exp(-np.arange(len(y) - g) / (0.008 * SR))
        takes.append(y)
    n = min(len(takes[0]), len(takes[1]))
    return np.vstack([takes[0][:n], takes[1][:n]]) * 0.17


INSTRUMENTS['chuggtr'] = v_chuggtr
INSTRUMENT_INFO['chuggtr'] = 'Down-tuned metal guitar (quad-tracked, gated chugs)'
GM_PROGRAM['chuggtr'] = 30
for _role in ('chords', 'arp', 'lead', 'bass'):
    if 'chuggtr' not in ROLE_CHOICES[_role]:
        ROLE_CHOICES[_role].append('chuggtr')


# ----------------------------------------------------------------------------- 1.79: whistle + DnB-style synths
def v_whistle(m, dur, p, glide=None, mod=None):
    """Whistling: an almost pure, slightly breathy tone, sliding between notes, a wide, slow, slightly uneven
    vibrato and soft onsets - the lonely whistled melody of a mystery-TV theme, or a western."""
    f = float(mtof(m)) * (2.0 if float(mtof(m)) < 600 else 1.0)       # whistles live high (an octave up when low)
    gate = int(max(dur, 0.05) * SR)
    env = _va.adsr(gate, p.get('a', 0.05), 0.3, 0.92, p.get('r', 0.15))
    n = len(env)
    t = np.arange(n) / SR
    fr = _glide_freq(f, n, None if glide is None else glide + (12 if float(mtof(glide)) < 600 else 0), 0.06)
    vib = np.clip((t - 0.2) / 0.4, 0, 1) * (22 + 6 * np.sin(2 * np.pi * 0.7 * t)) * np.sin(2 * np.pi * 5.2 * t)
    ph = 2 * np.pi * np.cumsum(fr * 2 ** ((vib - 25 * np.exp(-t / 0.04)) / 1200)) / SR
    tone = np.sin(ph) + 0.03 * np.sin(2 * ph)
    breath = bp(_rng().standard_normal(n), f * 0.85, min(f * 1.25, 16000)) * 0.12
    y = (tone + breath) * env
    return _st(y, 35) * 0.45


def v_electrosaw(m, dur, p, glide=None, mod=None):
    """Electro saw lead / bass (2010s electro DnB and dubstep): a stack of detuned saws through a formant 'talk' that
    moves with the beat, hard-clipped and band-limited - huge, buzzing and vocal, for riffs and drops."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.003, 0.3, 0.85, 0.06)
    n = len(env)
    t = np.arange(n) / SR
    spb = float(p.get('spb', 0.35))
    x = _vb._stack(f, n, 5, 22, 0.8)
    x = x.mean(axis=0) if np.ndim(x) == 2 else x
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * t / (spb * p.get('rate', 1.0)))
    a = _va.formant(x, 'a', 6.0)
    o = _va.formant(x, 'o', 6.0)
    y = a * lfo + o * (1 - lfo) + 0.35 * x
    y = np.tanh(hp(y, 90) * 3.0)
    y = lp(y, 7000)
    return _st(y * env, 18) * 0.42


def v_techneuro(m, dur, p, glide=None, mod=None):
    """Tech / neuro bass: an FM-buzzed saw through a resonant comb (the metallic 'tech' tone), a fast filter
    snap per note and a clean sine sub underneath - tight, dark and rolling (2000s tech DnB)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.002, 0.25, 0.7, 0.03)
    n = len(env)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    src = np.sin(ph + p.get('fm', 2.2) * np.sin(2 * ph + 1.5 * np.sin(0.5 * ph)))
    d = max(2, int(SR / (f * 4)))
    comb = src + 0.6 * np.concatenate([np.zeros(d), src[:-d]])
    top = _va.vcf(comb, 300 + 3200 * np.exp(-t / p.get('fdecay', 0.09)), 0.55, 2.2)
    top = hp(top, 120)
    sub = lp(np.sin(ph), 120) * 0.7
    return _st((top * 0.8 + sub) * env, 0) * 0.55


def v_dancestab(m, dur, p, glide=None, mod=None):
    """Dancefloor DnB chord stab: bright detuned saws and a square with a pitch drop into the note, a bandpassed
    'hoover-ish' body and a short gated tail - the anthemic stab of 2000s dancefloor drum & bass."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.5), 0.04) * SR)
    env = _va.adsr(gate, 0.002, 0.18, 0.35, 0.07)
    n = len(env)
    t = np.arange(n) / SR
    fr = f * 2 ** (-0.6 * np.exp(-t / 0.03) + 0.0)
    rng = _rng()
    x = np.vstack([_va.saw(fr * 2 ** (-11 / 1200), n, rng.random()) + 0.5 * _va.pulse(fr, n, rng.random(), 0.35),
                   _va.saw(fr * 2 ** (11 / 1200), n, rng.random()) + 0.5 * _va.pulse(fr, n, rng.random(), 0.65)])
    y = _va.vcf(x * 0.6, 900 + 5500 * np.exp(-t / 0.08), 0.35, 1.6)
    y = bp(y, 220, 7500)
    return y * env * 0.6


for _name, _fn, _info, _roles, _gm in (
        ('whistle', v_whistle, 'Whistle (lonely, sliding)', ('lead',), 78),
        ('electrosaw', v_electrosaw, 'Electro saw (talking, distorted stack)', ('lead', 'bass', 'chords'), 81),
        ('techneuro', v_techneuro, 'Tech / neuro bass (metallic, rolling)', ('bass',), 38),
        ('dancestab', v_dancestab, 'Dancefloor DnB stab (anthemic)', ('chords', 'arp', 'lead'), 81)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.81: more trance voices
def v_sylpluck(m, dur, p, glide=None, mod=None):
    """Classic trance pluck (the 2000s software-synth pluck): two detuned saws and a square a few cents apart, a
    filter that snaps shut in ~0.1 s with a little resonance, a short amp tail and a wide chorus - bouncy and bright,
    made for 1/16 arps into a dotted delay."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.4), 0.02) * SR)
    env = _va.adsr(gate, 0.001, p.get('d', 0.2), 0.0, 0.12)
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    x = np.vstack([_va.saw(np.full(n, f * 2 ** (-9 / 1200)), n, rng.random()) + 0.5 * _va.pulse(np.full(n, f * 2 ** (4 / 1200)), n, rng.random(), 0.5),
                   _va.saw(np.full(n, f * 2 ** (9 / 1200)), n, rng.random()) + 0.5 * _va.pulse(np.full(n, f * 2 ** (-4 / 1200)), n, rng.random(), 0.5)])
    cut = 300 * (p.get('cut', 9000) / 300) ** np.exp(-t / p.get('fdecay', 0.06))
    y = _hpf(_va.vcf(x * 0.6, cut, 0.3, 1.2), 180) * env
    return _va.juno_chorus(y, 2, 0.35) * 0.6


def v_trancebell(m, dur, p, glide=None, mod=None):
    """Trance bell: an FM bell (a bright, slightly inharmonic 3.5:1 strike that fades to a pure tone) layered with a
    short saw pluck for the body - the glassy counter-melody of a breakdown or the arp of a big drop."""
    f = float(mtof(m))
    n = int(min(2.2, 0.8 + 300 / f) * SR)
    t = np.arange(n) / SR
    idx = 3.0 * np.exp(-t / 0.15) + 0.3
    bell = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t / 0.9)
    bell += 0.3 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.4)
    pl = _va.vcf(_va.saw(np.full(n, f), n), 300 + 6000 * np.exp(-t / 0.05), 0.2, 1.1) * np.exp(-t / 0.18)
    y = (bell * 0.6 + pl * 0.35) * np.minimum(t / 0.001, 1)
    return _st(_gate_tail(y, dur + 0.6, 0.5), 30) * 0.5


def v_screamlead(m, dur, p, glide=None, mod=None):
    """Uplifting 'screamer' lead: a wide stack of detuned saws plus a pulse an octave up for the bite, a filter
    that opens on every note, a long glide between notes, delayed vibrato and a touch of grit - the lead that
    soars over the last drop."""
    f = float(mtof(m))
    gate = int(max(dur, 0.04) * SR)
    env = _va.adsr(gate, 0.005, 0.3, 0.9, p.get('r', 0.3))
    n = len(env)
    t = np.arange(n) / SR
    fr = _glide_freq(f, n, glide, p.get('slide', 0.09))
    fr = fr * 2 ** (np.clip((t - 0.25) / 0.35, 0, 1) * p.get('vib', 18) * np.sin(2 * np.pi * 5.6 * t) / 1200)
    body = _va.jp_supersaw(fr, n, 0.55, 0.7, 0.9)
    octv = _va.pulse(fr * 2, n, _rng().random(), 0.3) * 0.28
    x = body + octv[None, :]
    cut = p.get('cut', 6000) * (0.55 + 0.45 * np.exp(-t / 0.12)) + 1500
    y = np.tanh(_va.vcf(x, cut, 0.18, 1.4) * 1.6) / 1.6
    return _hpf(y, 200) * env * 0.55


def v_trancestrings(m, dur, p, glide=None, mod=None):
    """Trance strings: a string-machine ensemble (saws with a slow, three-way chorus 'ensemble') that swells in, a
    soft low-pass that opens a little as it grows - the warm breakdown strings under a piano or a vocal."""
    f = float(mtof(m))
    gate = int(max(dur, 0.2) * SR)
    env = _va.adsr(gate, p.get('a', 0.5), 0.6, 0.9, p.get('r', 1.0))
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    x = np.zeros((2, n))
    for k, c in enumerate((-8, -3, 3, 8)):
        lfo = 1 + 0.0025 * np.sin(2 * np.pi * (0.6 + 0.23 * k) * t + rng.random() * 6)
        x[k % 2] += _va.saw(f * 2 ** (c / 1200) * lfo, n, rng.random()) * 0.5
    y = _va.vcf(x, p.get('cut', 2600) * (0.6 + 0.4 * (1 - np.exp(-t / 1.2))), 0.1, 1.0)
    y = eq(_hpf(y, 160), 'peak', 3000, 0.8, -2.0)
    return y * env * 0.5


def v_laserpluck(m, dur, p, glide=None, mod=None):
    """Laser pluck: a square + saw whose pitch dives an octave into the note in a few milliseconds ('pew'), through a
    snappy filter - the zappy arp of 90s / 2000s trance and hard trance."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.3), 0.02) * SR)
    env = _va.adsr(gate, 0.001, p.get('d', 0.14), 0.0, 0.07)
    n = len(env)
    t = np.arange(n) / SR
    fr = f * 2 ** (p.get('dive', 1.0) * np.exp(-t / 0.012))
    x = _va.pulse(fr, n, 0.0, 0.4) * 0.7 + _va.saw(fr * 2 ** (6 / 1200), n, 0.3) * 0.5
    y = _va.vcf(x, 400 + 7000 * np.exp(-t / 0.05), 0.35, 1.3) * env
    return _st(_hpf(y, 200), 22) * 0.6


def v_upstab(m, dur, p, glide=None, mod=None):
    """Uplifting supersaw stab: the JP supersaw stack with a fast filter 'bwow' (opening, then settling), a short
    body and a gated tail - the chord stabs on the off-beats of an uplifting or tech-trance drop."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.5), 0.04) * SR)
    env = _va.adsr(gate, 0.002, p.get('d', 0.18), 0.3, 0.07)
    n = len(env)
    t = np.arange(n) / SR
    x = _va.jp_supersaw(f, n, 0.5, 0.75, 1.0)
    cut = 900 + p.get('cut', 7000) * np.exp(-t / 0.07) * (1 - np.exp(-t / 0.004))
    y = _va.vcf(x, cut, 0.3, 1.3)
    return _hpf(y, 170) * env * 0.65


def v_fmroll(m, dur, p, glide=None, mod=None):
    """FM rolling bass: the trance roll with more bite - a sine sub plus a short FM 'tok' on top (2:1, the index
    dying in ~40 ms) and a snappy filtered saw, each note reset so every 16th attacks the same - tight and punchy."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.2), 0.02) * SR)
    env = _va.adsr(gate, 0.0008, p.get('d', 0.09), 0.2, 0.015)
    n = len(env)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    sub = lp(np.sin(ph), 110)
    tok = np.sin(ph + 2.6 * np.exp(-t / 0.04) * np.sin(2 * ph))
    sawl = _va.vcf(2 * ((f * t) % 1.0) - 1, 180 + 2200 * np.exp(-t / 0.03), 0.3, 1.5)
    y = (sub * 0.7 + hp(tok, 120) * 0.35 + _hpf(sawl, 120) * 0.3) * env
    return _st(y, 0) * 0.6


for _name, _fn, _info, _roles, _gm in (
        ('sylpluck', v_sylpluck, 'Classic trance pluck (bright, chorused)', ('arp', 'lead', 'chords'), 81),
        ('trancebell', v_trancebell, 'Trance bell (FM bell + pluck)', ('arp', 'lead'), 11),
        ('screamlead', v_screamlead, 'Uplifting screamer lead (soaring, glide)', ('lead',), 81),
        ('trancestrings', v_trancestrings, 'Trance strings (warm ensemble)', ('pad', 'chords'), 50),
        ('laserpluck', v_laserpluck, 'Laser pluck (zappy pitch-dive arp)', ('arp', 'lead'), 81),
        ('upstab', v_upstab, 'Uplifting supersaw stab', ('chords', 'arp', 'lead'), 81),
        ('fmroll', v_fmroll, 'FM rolling bass (punchy trance roll)', ('bass',), 38)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.83: drill + jam-band voices
def v_drill808(m, dur, p, glide=None, mod=None):
    """Drill 808: a long, deep 808 driven into saturation so its harmonics carry it on phones and car speakers, with
    the heavy, slow slides between notes that drill is built on (the glide is part of the line, not an effect)."""
    y = np.asarray(i_808(m, dur, dict(p, slide=p.get('slide', 0.12), decay=p.get('decay', 0.9), drive=p.get('drive', 2.2)),
                         glide, mod), float)
    lo_ = lp(y, 100)
    grit = np.tanh((y - lo_) * 3.0 + lo_ * 1.4) * 0.35
    return lo_ * 0.85 + hp(grit, 90)


def v_darksample(m, dur, p, glide=None, mod=None):
    """Dark sample bed (stands in for the chopped, filtered loop of a drill / dark trap beat): a shimmering, eerie
    bell-choir tone - a soft FM bell, an airy vowel and a detuned sine pair - crushed slightly, filtered dark, with a
    slow tape wobble, so it sounds like an old record sampled and pitched rather than a synth."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = _va.adsr(gate, p.get('a', 0.03), 0.6, 0.75, p.get('r', 0.5))
    n = len(env)
    t = np.arange(n) / SR
    wob = 2 ** ((9 * np.sin(2 * np.pi * 0.45 * t) + 4 * np.sin(2 * np.pi * 3.1 * t)) / 1200)
    ph = 2 * np.pi * np.cumsum(f * wob) / SR
    bell = np.sin(ph + 1.4 * np.exp(-t / 0.4) * np.sin(3.01 * ph)) * (0.55 + 0.45 * np.exp(-t / 0.8))
    pair = 0.5 * np.sin(ph * 1.003) + 0.3 * np.sin(2 * ph * 0.998)
    air = _va.formant(_rng().standard_normal(n) * 0.25 + _va.saw(f * wob, n, 0.2) * 0.3, 'o', 7.0) * 0.6
    y = bell * 0.5 + pair * 0.4 + air
    bits = 2 ** 10                                         # a little sampler crunch
    y = np.round(y * bits) / bits
    y = lp(hp(y, 220), p.get('cut', 3200))
    return _ms_stereo(y * env, 60, 0.45) * 0.55


def v_wob808(m, dur, p, glide=None, mod=None):
    """Wobble 808: an 808 sub underneath, and on top a distorted saw through a resonant filter swept by an LFO locked
    to the beat (1/8, 1/8 triplet or 1/16, picked per note) - the dubstep-style wobble a dark trap / drill beat
    switches into for a few bars."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(0.05 * SR)
    t = np.arange(n) / SR
    spb = float(p.get('spb', 0.42))
    rate = _rng().choice([2.0, 3.0, 4.0]) / spb             # wobbles per second: 1/8, 1/8 triplet, 1/16
    sub = np.sin(2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.08)) / SR) * 0.8
    sub = lp(sub, 90)
    saw = _vb._stack(f * 2, n, 3, 14, 0.5)
    saw = saw.mean(axis=0) if np.ndim(saw) == 2 else saw
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * rate * t)
    top = _va.vcf(np.tanh(saw * 2.0), 180 * (3500 / 180) ** lfo, 0.6, 1.8)
    env = np.minimum(1.0, t / 0.004) * np.where(np.arange(n) < gate, 1.0, np.exp(-(np.arange(n) - gate) / (0.03 * SR)))
    y = (sub + hp(top, 110) * 0.55) * env
    return np.vstack([y, y]) * 0.6


def v_jamlead(m, dur, p, glide=None, mod=None):
    """Jam-band lead guitar: a clean-to-slightly-crunchy single-coil tone through a big clean valve amp - compressed so
    long notes sing and sustain, a little edge when picked hard, a gentle chorus-y shimmer - the long, melodic,
    meandering solos of a 70s psychedelic jam band."""
    y, pm = _eg_string(m, dur, dict(p, tone=p.get('tone', 1.1)), mod, 9.0, 0.75, 0.15)
    y = hp(y, 110)
    env = np.abs(signal.lfilter([0.01], [1, -0.99], np.abs(y))) + 1e-4
    y = y / (env ** 0.45) * 0.08                            # sustain: the compressor holds the note up as it decays
    y = np.tanh(y * p.get('gain', 2.2)) / np.tanh(p.get('gain', 2.2))
    y = eq(eq(eq(y, 'peak', 180, 1.0, 2.0), 'peak', 800, 1.0, -2.0), 'peak', 2600, 1.0, 3.0)
    y = lp(y, 7000)
    return _ms_stereo(y, 45, 0.3) * 0.32


def v_envguitar(m, dur, p, glide=None, mod=None):
    """Envelope-filter guitar: a clean, funky chord-chop guitar through an envelope filter (the 'quack' that opens with
    every pick attack and closes as the note decays) - the bouncy late-70s jam-band rhythm guitar."""
    y, pm = _eg_string(m, dur, p, mod, 4.0, 0.8, 0.12)
    n = len(y)
    t = np.arange(n) / SR
    env = np.exp(-t / p.get('sweep', 0.18))
    out = np.zeros(n)
    blk = 128
    zi = np.zeros(2)
    for s0 in range(0, n, blk):                            # a resonant band-pass swept by the note's own envelope
        fc = 350 * (2800 / 350) ** env[s0]
        w = 2 * np.pi * fc / SR
        al = np.sin(w) / (2 * 4.0)
        b = np.array([al, 0, -al]) / (1 + al)
        a = np.array([1, -2 * np.cos(w) / (1 + al), (1 - al) / (1 + al)])
        out[s0:s0 + blk], zi = signal.lfilter(b, a, y[s0:s0 + blk], zi=zi)
    y = out * 3.0 + y * 0.3
    return _ms_stereo(hp(y, 120), 30, 0.3) * 0.45


for _name, _fn, _info, _roles, _gm in (
        ('drill808', v_drill808, 'Drill 808 (deep, saturated, heavy slides)', ('bass',), 38),
        ('darksample', v_darksample, 'Dark sample bed (eerie, lo-fi, sampled-loop feel)', ('chords', 'pad', 'arp', 'lead'), 89),
        ('wob808', v_wob808, 'Wobble 808 (sub + beat-synced wobble)', ('bass',), 38),
        ('jamlead', v_jamlead, 'Jam-band lead guitar (singing, sustained)', ('lead', 'arp'), 27),
        ('envguitar', v_envguitar, 'Envelope-filter guitar (funky quack)', ('chords', 'arp', 'lead'), 28)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.84: the club synth bank
# Six new voices each for house, techno, drum & bass and dubstep. All on the ladder filter (velocity + per-note takes).
def _env_n(dur, a, d, s, r, cap=None):
    gate = int(max(min(dur, cap) if cap else dur, 0.02) * SR)
    env = _va.adsr(gate, a, d, s, r)
    return env, len(env), np.arange(len(env)) / SR


def _sync_lfo(t, p, choices=(2.0, 3.0, 4.0), mod=None):
    """0..1 LFO locked to the beat: `choices` cycles per beat. A wobble written into the song (mod = beats per cycle,
    from the wobble bass part) wins over a random choice."""
    spb = float(p.get('spb', 0.45))
    if isinstance(mod, (int, float)) and not isinstance(mod, bool) and mod > 0:
        rate = 1.0 / (float(mod) * spb)
    else:
        rate = (p.get('rate') or _rng().choice(choices)) / spb
    return 0.5 - 0.5 * np.cos(2 * np.pi * rate * t)


# --- house
def v_frenchchord(m, dur, p, glide=None, mod=None):
    """French-house filtered disco chord: a bright, chopped-sample-like saw + square stack through a phaser and a low-pass
    that pumps open with every hit - the filter-house loop sound."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.3, 0.6, 0.12, 0.8)
    rng = _rng()
    x = np.vstack([_va.saw(np.full(n, f * 2 ** (-6 / 1200)), n, rng.random()) + 0.6 * _va.pulse(np.full(n, f / 2), n, rng.random(), 0.4),
                   _va.saw(np.full(n, f * 2 ** (6 / 1200)), n, rng.random()) + 0.6 * _va.pulse(np.full(n, f / 2), n, rng.random(), 0.6)])
    y = _va.vcf(x * 0.6, 500 + p.get('cut', 3500) * (0.5 + 0.5 * np.exp(-t / 0.15)), 0.35, 1.4)
    ph = np.sin(2 * np.pi * 0.5 * t)
    y = y + 0.4 * np.vstack([np.roll(y[0], int(30 + 20 * ph[0])), np.roll(y[1], int(30 - 20 * ph[0]))])
    return _hpf(y, 150) * env * 0.4


def v_discostrings(m, dur, p, glide=None, mod=None):
    """Disco strings: a lush string ensemble with a fast swell and the classic upward 'swoop' into the stab (a quick
    pitch scoop), bright and wide - the string stabs and runs of disco and nu-disco house."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.03, 0.4, 0.8, 0.3)
    rng = _rng()
    fr = f * 2 ** (-60 * np.exp(-t / 0.05) / 1200)
    x = np.zeros((2, n))
    for k, c in enumerate((-10, -4, 3, 9)):
        x[k % 2] += _va.saw(fr * 2 ** (c / 1200) * (1 + 0.002 * np.sin(2 * np.pi * (5 + k) * t)), n, rng.random()) * 0.5
    y = _va.vcf(x, 5500, 0.1, 1.0)
    y = eq(_hpf(y, 200), 'peak', 3000, 1.0, 2.5)
    return y * env * 0.42


def v_garagebass(m, dur, p, glide=None, mod=None):
    """UK garage / organ bass: a bouncy FM-ish organ tone with a punchy pluck and a short body - the skippy bass of
    garage and speed garage, also great in tech house."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, p.get('d', 0.18), 0.4, 0.04)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.04)) / SR
    y = np.sin(ph + 1.6 * np.exp(-t / 0.06) * np.sin(2 * ph)) + 0.35 * np.sin(2 * ph) + 0.2 * np.sign(np.sin(ph)) * np.exp(-t / 0.05)
    y = _va.vcf(y, 300 + 2400 * np.exp(-t / 0.05), 0.25, 1.4) * env
    return np.vstack([y, y]) * 0.55


def v_detroitchord(m, dur, p, glide=None, mod=None):
    """Detroit chord pad: warm, slightly detuned analog strings-meets-brass with a slow filter swell and a wide pitch drift -
    the soulful, futuristic chords of Detroit techno and deep house."""
    return _va.voice(m, dur, dict(p, cut=p.get('cut', 1400)), glide, saw_mix=1.0, pulse_mix=0.5, pwm=0.5, unison=3, detune=12,
                     spread=0.8, res=0.25, fenv=1.2, fa=0.25, fd=1.0, fs=0.5, amp=(p.get('a', 0.08), 0.6, 0.8, p.get('r', 0.5)),
                     drive=1.2, keytrack=0.4, drift=6.0) * 0.38


def v_housevox(m, dur, p, glide=None, mod=None):
    """House vocal stab: a short sung 'oh' / 'ah' / 'yeah'-like formant stab with a breathy edge and a quick pitch
    fall - the chopped diva stab of 90s and modern house, made from scratch."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.006, 0.18, 0.4, 0.08, 0.6)
    rng = _rng()
    fr = f * 2 ** ((25 * np.exp(-t / 0.03) - 30 * np.clip((t - 0.25) / 0.3, 0, 1)) / 1200)
    src = _va.saw(fr, n, rng.random()) * 0.8 + 0.12 * rng.standard_normal(n)
    y = _va.formant(src, str(rng.choice(['o', 'a', 'e'])), 8.0)
    return _ms_stereo(hp(y * env, 200), 25, 0.3) * 1.2


def v_organchord(m, dur, p, glide=None, mod=None):
    """Deep house organ chord: a soft drawbar-like organ (1st, 2nd and 3rd harmonics) with a gentle key click and
    rotary shimmer - the warm organ stabs and pads of deep and soulful house."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.006, 0.2, 0.85, 0.12)
    ph = 2 * np.pi * f * t
    y = np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.35 * np.sin(3 * ph) + 0.15 * np.sin(4 * ph)
    y = y * (1 + 0.08 * np.sin(2 * np.pi * 6.5 * t)) + 0.15 * hp(_rng().standard_normal(n), 2000) * np.exp(-t * 400)
    return _ms_stereo(y * env, 40, 0.4) * 0.35


# --- techno
def v_berlinseq(m, dur, p, glide=None, mod=None):
    """Berlin sequencer: a single saw through a resonant ladder with a short envelope and a touch of glide, the cutoff
    set per note around a slowly drifting centre - the hypnotic analog sequencer line of Berlin-school and techno."""
    c = p.get('cut', 900) * 2 ** (0.5 * np.sin(m * 0.7))
    return _va.voice(m, dur, dict(p, cut=c), glide, saw_mix=1.0, unison=1, res=0.62, fenv=2.0, fd=0.12, fs=0.0,
                     amp=(0.001, p.get('d', 0.2), 0.0, 0.06), drive=1.6, keytrack=0.5, slide=0.03, stereo=False) * 0.55


def v_industrialstab(m, dur, p, glide=None, mod=None):
    """Industrial techno stab: detuned saws ring-modulated by a fifth and smashed through distortion and a band-pass -
    a harsh, metallic, aggressive hit for warehouse techno."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.001, 0.12, 0.15, 0.06, 0.4)
    x = _va.saw(np.full(n, f), n, 0.1) + _va.saw(np.full(n, f * 1.01), n, 0.5)
    x = x * np.sin(2 * np.pi * f * 2.0 * t)      # (1.92) ring-mod on the octave: harmonic sidebands, always in key
    y = np.tanh(_va.vcf(x, 600 + 6000 * np.exp(-t / 0.04), 0.4, 2.0) * 3.0)
    y = bp(y, 250, 6000) * env
    return _ms_stereo(y, 20, 0.35) * 0.45


def v_metalperc(m, dur, p, glide=None, mod=None):
    """Metallic FM percussion synth: a short, pitched, inharmonic FM 'clank' (1:1.41 ratio, fast decaying index) that
    plays melodic sequences - the tuned percussion loops of minimal and hypnotic techno."""
    f = float(mtof(m))
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    y = np.sin(ph + 4.0 * np.exp(-t / 0.015) * np.sin(1.41 * ph)) * np.exp(-t / p.get('decay', 0.07))
    return _ms_stereo(hp(y, 150), 12, 0.3) * 0.5


def v_hypnopad(m, dur, p, glide=None, mod=None):
    """Hypnotic drone pad: a dark, evolving saw drone whose filter breathes slowly and whose harmonics shift with a
    slow PWM - the grey, endless pad under hypnotic and dub techno."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 1.2), 1.0, 0.9, p.get('r', 1.5))
    rng = _rng()
    x = np.vstack([_va.saw(np.full(n, f * 2 ** (-7 / 1200)), n, rng.random()) + 0.5 * _va.pulse(np.full(n, f), n, rng.random(), 0.5 + 0.3 * np.sin(2 * np.pi * 0.11 * t)),
                   _va.saw(np.full(n, f * 2 ** (7 / 1200)), n, rng.random()) + 0.5 * _va.pulse(np.full(n, f), n, rng.random(), 0.5 + 0.3 * np.sin(2 * np.pi * 0.13 * t + 1))])
    cut = 300 + 900 * (0.5 - 0.5 * np.cos(2 * np.pi * 0.07 * t + rng.random() * 6))
    y = _va.vcf(x * 0.5, cut, 0.45, 1.1)
    return _hpf(y, 120) * env * 0.5


def v_peaklead(m, dur, p, glide=None, mod=None):
    """Peak-time techno lead: a screaming FM-and-saw lead with a hard sync-like bite and a fast filter snap, short and
    stabby - the hook riff of big-room / peak-time techno."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.25, 0.5, 0.08)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.05)) / SR
    x = np.sin(ph + 3.0 * np.exp(-t / 0.1) * np.sin(2.01 * ph)) * 0.6 + (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.5
    y = np.tanh(_va.vcf(x, 900 + 7000 * np.exp(-t / 0.08), 0.4, 1.8) * 1.8)
    return _ms_stereo(_hpf(y, 200) * env, 25, 0.35) * 0.42


def v_ravestab2(m, dur, p, glide=None, mod=None):
    """Rave hoover stab: the classic rave hoover sound - a detuned, PWM-ed saw stack with a falling pitch swoop into the note
    and a big chorus - the screaming rave / hard techno stab."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.3, 0.5, 0.15, 0.8)
    fr = f * 2 ** (5 * np.exp(-t / 0.06) / 12)
    rng = _rng()
    x = np.zeros((2, n))
    for k, c in enumerate((-25, -9, 0, 9, 25)):
        x[k % 2] += _va.pulse(fr * 2 ** (c / 1200), n, rng.random(), 0.3 + 0.2 * np.sin(2 * np.pi * 1.3 * t + k)) * 0.4
    y = _va.vcf(x, 4500, 0.15, 1.5)
    return _hpf(_va.juno_chorus(y, 2, 0.4), 150) * env * 0.5


# --- drum & bass
def v_liquidpad(m, dur, p, glide=None, mod=None):
    """Liquid pad: an airy, bright, breathing pad - a soft supersaw with a vowel-ish formant shimmer and slow filter
    movement - the glossy background of liquid drum & bass."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.8), 0.8, 0.9, p.get('r', 1.2))
    x = _va.jp_supersaw(f, n, 0.35, 0.55, 0.9)
    air = _va.formant(x.mean(axis=0), 'e', 5.0) * 0.4
    y = _va.vcf(x + air[None, :], 2500 + 1500 * np.sin(2 * np.pi * 0.09 * t) ** 2, 0.15, 1.0)
    return _hpf(y, 180) * env * 0.45


def v_jumpup(m, dur, p, glide=None, mod=None):
    """Jump-up bass: a fat square-and-saw mid bass with a bouncy pitch 'wub' (a quick pitch LFO) and a squelchy filter,
    over a clean sub - the cheeky, bouncing bass of jump-up drum & bass."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.3, 0.8, 0.04)
    lfo = _sync_lfo(t, p, (4.0, 6.0, 8.0))
    fr = _glide_freq(f, n, glide, 0.05) * 2 ** (lfo * 0.6)
    x = _va.pulse(fr, n, 0.0, 0.5) * 0.6 + _va.saw(fr * 1.005, n, 0.3) * 0.5
    top = _va.vcf(x, 300 + 2500 * lfo, 0.55, 2.0)
    sub = lp(np.sin(2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.05)) / SR), 100)
    y = (hp(top, 110) * 0.7 + sub * 0.75) * env
    return np.vstack([y, y]) * 0.55


def v_rollerbass(m, dur, p, glide=None, mod=None):
    """Roller bass: a deep, warm saturated sine-saw that rolls under the breaks - clean sub, a little harmonic warmth
    and a slow filter breath - the steady, hypnotic bass of rollers and minimal drum & bass."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.4, 0.85, 0.05)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.06)) / SR
    y = np.tanh((np.sin(ph) + 0.3 * np.sin(2 * ph)) * 1.8) / np.tanh(1.8)
    y = _va.vcf(y + 0.2 * (2 * ((ph / (2 * np.pi)) % 1) - 1), 400 + 300 * np.sin(2 * np.pi * 0.25 * t) ** 2, 0.2, 1.2)
    return np.vstack([y * env, y * env]) * 0.6


def v_neuroformant(m, dur, p, glide=None, mod=None):
    """Neuro formant bass: a reese-like detuned saw pair through a moving formant filter (the bass 'talks' from 'oh' to
    'ee' in time with the beat), distorted, over a clean sub - the technical, robotic neurofunk bass."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.3, 0.85, 0.04)
    lfo = _sync_lfo(t, p, (1.0, 2.0, 3.0))
    x = _va.saw(np.full(n, f * 2), n, 0.1) + _va.saw(np.full(n, f * 2 * 1.012), n, 0.6)
    o, e = _va.formant(x, 'o', 6.0), _va.formant(x, 'e', 6.0)
    top = np.tanh((o * (1 - lfo) + e * lfo) * 3.0)
    sub = lp(np.sin(2 * np.pi * f * t), 100)
    y = (hp(top, 140) * 0.45 + sub * 0.8) * env
    return np.vstack([y, y]) * 0.55


def v_liquidkeys(m, dur, p, glide=None, mod=None):
    """Liquid keys: a soft electric piano with a slow stereo tremolo and a glossy chorus - the jazzy keys of liquid
    drum & bass and soulful jungle."""
    y = np.asarray(INSTRUMENTS['epiano'](m, dur, p, glide, mod), float)
    y = y if y.ndim == 2 else np.vstack([y, y])
    t = np.arange(y.shape[1]) / SR
    tr = 0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * t)
    y = np.vstack([y[0] * (0.7 + 0.3 * tr), y[1] * (0.7 + 0.3 * (1 - tr))])
    return _va.juno_chorus(y, 1, 0.3) * 0.9


def v_dancereese(m, dur, p, glide=None, mod=None):
    """Dancefloor reese: two saws slowly drifting against each other (the phasing reese movement), band-limited and
    driven, over a clean sub - the classic rolling reese of 2000s dancefloor drum & bass."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.4, 0.85, 0.05)
    det = 1 + 0.008 * (1 + np.sin(2 * np.pi * 0.3 * t))
    x = _va.saw(np.full(n, f), n, 0.0) + _va.saw(f * det, n, 0.5)
    top = np.tanh(_va.vcf(x, p.get('cut', 900), 0.3, 1.6) * 1.6)
    sub = lp(np.sin(2 * np.pi * f * t), 90)
    y = (hp(top, 100) * 0.6 + sub * 0.7) * env
    return np.vstack([y, y]) * 0.55


# --- dubstep
def v_yoi(m, dur, p, glide=None, mod=None):
    """Yoi bass: the vowel 'yoi' / 'yah' bass - a distorted saw stack whose formant sweeps fast from 'oo' to 'ee' and
    back on every note - the cartoonish talking bass of riddim and melodic dubstep."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.3, 0.85, 0.05)
    x = _vb._stack(f, n, 4, 18, 0.6)
    x = x.mean(axis=0) if np.ndim(x) == 2 else x
    u = np.clip(t / max(0.12, dur * 0.6), 0, 1)
    sweep = np.sin(np.pi * u)
    y = _va.formant(x, 'u', 6.0) * (1 - sweep) + _va.formant(x, 'i', 6.0) * sweep
    y = np.tanh(y * 4.0) * env
    sub = lp(np.sin(2 * np.pi * f / 2 * t), 90) * 0.6 * env
    return np.vstack([hp(y, 120) * 0.5 + sub] * 2) * 0.6


def v_fmscreech(m, dur, p, glide=None, mod=None):
    """FM screech: a high, metallic FM screech (inharmonic ratio, an index that wobbles with the beat) pushed through
    distortion - the screaming lead / fill sound of tearout and heavy dubstep."""
    f = float(mtof(m)) * 2
    env, n, t = _env_n(dur, 0.002, 0.2, 0.8, 0.05)
    lfo = _sync_lfo(t, p, (2.0, 4.0, 6.0))
    ph = 2 * np.pi * f * t
    y = np.sin(ph + (2 + 6 * lfo) * np.sin(2.7 * ph))
    y = np.tanh(bp(y, 400, 9000) * 3.0) * env
    return _ms_stereo(y, 18, 0.4) * 0.35


def v_squareriddim(m, dur, p, glide=None, mod=None):
    """Square riddim: a hollow, bit-crushed square bass gated in a stuttering 1/16 - 1/8 rhythm with a resonant low-pass
    - the minimal, bouncy, repetitive riddim dubstep bass."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.2, 0.9, 0.03)
    x = _va.pulse(np.full(n, f), n, 0.0, 0.5)
    x = np.round(x * 24) / 24
    lfo = _sync_lfo(t, p, (4.0, 8.0))
    y = _va.vcf(x, 250 + 1800 * lfo, 0.5, 1.8)
    gate = (lfo > 0.25).astype(float)
    gate = np.convolve(gate, np.ones(64) / 64, 'same')
    y = np.tanh(y * 2.0) * env * (0.4 + 0.6 * gate)
    return np.vstack([y, y]) * 0.55


def v_talkgrowl(m, dur, p, glide=None, mod=None):
    """Talking growl: an FM growl whose vowel changes several times per note ('wow-ow-ah') - the conversational,
    articulate growl bass of modern heavy dubstep."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.3, 0.85, 0.05)
    ph = 2 * np.pi * f * t
    src = np.sin(ph + 3.0 * np.sin(2 * ph + 1.5 * np.sin(0.5 * ph)))
    src = np.tanh(src * 2.5)
    k = max(2, int(dur / max(0.08, float(p.get('spb', 0.45)) / 2)))
    vowels = [str(_rng().choice(['a', 'o', 'u', 'e'])) for _ in range(k)]
    seg = np.minimum((t / max(dur, 0.05) * k).astype(int), k - 1)
    y = np.zeros(n)
    for i, v in enumerate(vowels):
        msk = seg == i
        if np.any(msk):
            y[msk] = _va.formant(src, v, 7.0)[msk]
    y = np.convolve(y, np.ones(48) / 48, 'same')
    sub = lp(np.sin(ph), 90)
    out = (hp(np.tanh(y * 3), 120) * 0.5 + sub * 0.7) * env
    return np.vstack([out, out]) * 0.55


def v_dubsub(m, dur, p, glide=None, mod=None):
    """Deep dubstep sub: a pure, heavy sine sub with a slow attack-less swell and a hint of 2nd harmonic for small
    speakers, sliding between notes - the soundsystem sub of deep / original dubstep."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.01, 0.5, 0.95, 0.12)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.12)) / SR
    y = (np.sin(ph) + 0.12 * np.sin(2 * ph)) * env
    return np.vstack([y, y]) * 0.6


def v_tearout(m, dur, p, glide=None, mod=None):
    """Tearout bass: a brutal, metallic bass - a comb-filtered FM saw, heavily distorted and resampled down, its comb
    sweeping with the beat - the screeching, tearing mid-bass of tearout dubstep, over a clean sub."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.25, 0.85, 0.04)
    ph = 2 * np.pi * f * t
    src = np.tanh((np.sin(ph + 4 * np.sin(1.5 * ph)) + (2 * ((f * t) % 1) - 1)) * 3.0)
    lfo = _sync_lfo(t, p, (2.0, 4.0))
    d = (SR / (f * (2 + 4 * lfo))).astype(int)
    idx = np.clip(np.arange(n) - d, 0, n - 1)
    comb = src + 0.8 * src[idx]
    comb = np.repeat(comb[::3], 3)[:n]                    # resampled-down grit
    top = hp(np.tanh(comb * 2.0), 150)
    sub = lp(np.sin(ph), 90)
    y = (top * 0.4 + sub * 0.75) * env
    return np.vstack([y, y]) * 0.55


for _name, _fn, _info, _roles, _gm in (
        ('frenchchord', v_frenchchord, 'French-house filtered disco chord', ('chords', 'arp'), 81),
        ('discostrings', v_discostrings, 'Disco strings (swooping stabs)', ('chords', 'pad', 'arp'), 48),
        ('garagebass', v_garagebass, 'UK garage organ bass (bouncy)', ('bass',), 38),
        ('detroitchord', v_detroitchord, 'Detroit chord pad (warm, futuristic)', ('chords', 'pad'), 89),
        ('housevox', v_housevox, 'House vocal stab (made from scratch)', ('lead', 'arp', 'chords'), 54),
        ('organchord', v_organchord, 'Deep house organ chord', ('chords', 'pad', 'arp'), 16),
        ('berlinseq', v_berlinseq, 'Berlin sequencer (hypnotic analog line)', ('arp', 'bass', 'lead'), 81),
        ('industrialstab', v_industrialstab, 'Industrial techno stab (harsh, metallic)', ('chords', 'arp', 'lead'), 81),
        ('metalperc', v_metalperc, 'Metallic FM percussion synth (tuned clanks)', ('arp', 'lead'), 112),
        ('hypnopad', v_hypnopad, 'Hypnotic drone pad (dark, evolving)', ('pad', 'chords'), 95),
        ('peaklead', v_peaklead, 'Peak-time techno lead (screaming FM)', ('lead', 'arp'), 81),
        ('ravestab2', v_ravestab2, 'Rave hoover stab (swooping, PWM)', ('chords', 'lead', 'arp'), 81),
        ('liquidpad', v_liquidpad, 'Liquid DnB pad (airy, glossy)', ('pad', 'chords'), 89),
        ('jumpup', v_jumpup, 'Jump-up bass (bouncy wub)', ('bass',), 38),
        ('rollerbass', v_rollerbass, 'Roller bass (deep, warm, rolling)', ('bass',), 38),
        ('neuroformant', v_neuroformant, 'Neuro formant bass (talking, robotic)', ('bass',), 38),
        ('liquidkeys', v_liquidkeys, 'Liquid keys (e-piano, tremolo, chorus)', ('chords', 'arp', 'lead'), 4),
        ('dancereese', v_dancereese, 'Dancefloor reese (phasing, rolling)', ('bass',), 38),
        ('yoi', v_yoi, 'Yoi bass (talking vowel sweep)', ('bass', 'lead'), 38),
        ('fmscreech', v_fmscreech, 'FM screech (metallic, wobbling)', ('lead', 'arp'), 81),
        ('squareriddim', v_squareriddim, 'Square riddim bass (gated, crushed)', ('bass',), 38),
        ('talkgrowl2', v_talkgrowl, 'Talking growl (vowel changes per note)', ('bass', 'lead'), 38),
        ('dubsub', v_dubsub, 'Deep dubstep sub (pure, sliding)', ('bass',), 38),
        ('tearout', v_tearout, 'Tearout bass (metallic, brutal)', ('bass',), 38)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.84: the moog-style basses, rebuilt
# The 1.57 version beat against itself (two detuned saws at bass pitch phase in and out, so notes swelled and thinned),
# sat behind a fixed dull filter with no key tracking, and lost its fundamental to the resonance. The new one is built
# like the real three-oscillator mono synth: oscillators restart on every note (identical punch each time), the third
# oscillator a square an octave down, a key-tracked ladder with a contour that bites then settles, a clean sine holding
# the fundamental, and gentle output drive.
def _moog_core(m, dur, p, glide, pluck):
    f = float(mtof(m))
    vel = float(p.get('vel', 0.85))
    env, n, t = _env_n(dur, p.get('a', 0.004), p.get('d', 0.4 if not pluck else 0.3), p.get('s', 0.92 if not pluck else 0.5),
                       p.get('r', 0.07))
    fr = _glide_freq(f, n, glide, 0.06)
    low = fr / 2 if f >= 50 else fr                                     # (the octave-down square: never sub-audible rumble)
    x = _va.saw(fr, n, 0.0) + 0.55 * _va.pulse(fr * 2 ** (2 / 1200), n, 0.0, 0.5) + 0.5 * _va.pulse(low, n, 0.0, 0.5)
    # the genre's filter value is the most the filter ever opens (on a hard hit); it settles well below, never far
    # above the low harmonics - a round, dark, warm bass that sits under the mix instead of buzzing over it
    peak = min(float(p.get('cut', 700)), 1800.0) * (0.75 + 0.25 * vel) * (f / 55.0) ** 0.25
    rest = max(peak * (0.18 if pluck else 0.62), f * (1.4 if pluck else 2.5))   # (the pluck closes right down)
    cut = rest + (peak - rest) * np.exp(-t / p.get('fd', 0.07 if pluck else 0.12))
    y = _va.vcf(x * 0.4, cut, p.get('res', 0.25), 1.2)
    y = lp(y, 2600)                                                      # no fizz on top, whatever the filter does
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = y + 0.3 * np.sin(ph)                                             # the fundamental stays solid
    y = np.tanh(y * 1.25) / np.tanh(1.25)
    y = hp(y * env, 28)
    return np.vstack([y, y]) * (0.62 if pluck else 0.58)


def v_moogbass3(m, dur, p, glide=None, mod=None):
    """Moog-style bass: a saw, a square and a square an octave down, restarting on every note, through a dark ladder
    filter that opens a little on the attack and settles low, a solid sine fundamental and gentle warmth - round, fat
    and steady, sitting under the mix."""
    if p.get('pluck'):
        return v_moogpluck3(m, dur, p, glide, mod)
    return _moog_core(m, dur, p, glide, False)


def v_moogpluck3(m, dur, p, glide=None, mod=None):
    """Plucked Moog-style bass (funk / boogie / G-funk): the same oscillators, the filter closing quickly after a
    rubbery attack."""
    return _moog_core(m, dur, p, glide, True)


for _name, _fn in (('moogbass', v_moogbass3), ('moogpluck', v_moogpluck3)):
    INSTRUMENTS[_name + '_v2'] = INSTRUMENTS[_name]
    INSTRUMENT_INFO[_name + '_v2'] = (INSTRUMENT_INFO.get(_name + '_v1', _name).replace(' (classic sound, before 1.57)', '')
                                      + ' (1.57-1.83 sound)')
    GM_PROGRAM[_name + '_v2'] = GM_PROGRAM.get(_name, 38)
    INSTRUMENTS[_name] = _fn


INSTRUMENTS['reese_v2'] = _vb.reese_v2           # 1.84 rebuilt the reese (cleaner drive, more headroom); the old one stays
INSTRUMENT_INFO['reese_v2'] = 'Reese bass (1.59-1.83 sound, grittier)'
GM_PROGRAM['reese_v2'] = GM_PROGRAM.get('reese', 39)
ROLE_CHOICES['bass'].append('reese_v2')
for _n in ('moogbass_v2', 'moogpluck_v2'):
    ROLE_CHOICES['bass'].append(_n)


# ----------------------------------------------------------------------------- 1.84: dreamy trance / house synths
# Built for atmosphere rather than aggression: soft attacks, long releases, gentle slow movement, wide tops and a mono
# low end.
def v_dreampad(m, dur, p, glide=None, mod=None):
    """Dreamy pad: three lightly detuned saw stacks plus a quiet octave-down triangle for body and a soft sine, a high,
    gently glowing low-pass that opens slowly after the note starts, slow pitch / filter / pan drift and a light
    ensemble - a wide, floating cloud for trance and melodic house."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.22), 1.0, 1.0, p.get('r', 2.2))
    rng = _rng()
    drift = 2 ** (4 * np.sin(2 * np.pi * 0.17 * t + rng.random() * 6) / 1200)
    x = np.zeros((2, n))
    for k, c in enumerate((-11, -4, 3, 10)):
        x[k % 2] += _va.saw(f * drift * 2 ** (c / 1200), n, rng.random()) * 0.4
    tri = 2 * np.abs(2 * ((f / 2 * t + rng.random()) % 1) - 1) - 1
    x += 0.35 * tri + 0.15 * np.sin(2 * np.pi * f * t)
    opn = 1 - np.exp(-t / p.get('fa', 0.9))                               # the filter opens after the note starts
    cut = (900 + p.get('cut', 3800) * opn) * (1 + 0.18 * np.sin(2 * np.pi * 0.23 * t + rng.random() * 6))
    y = _va.vcf(x * 0.55, cut, 0.18, 1.05)
    y = _va.juno_chorus(y, 1, 0.35)
    pan = 0.25 * np.sin(2 * np.pi * 0.11 * t + rng.random() * 6)
    y = np.vstack([y[0] * (1 - pan), y[1] * (1 + pan)])
    return _hpf(y, 160) * env * 0.42


def v_dreamlead(m, dur, p, glide=None, mod=None):
    """Dreamy lead: a soft five-voice saw stack with low detune over a pure sine for body and a breath of filtered
    noise, a moderate low-pass with almost no resonance that blooms open with the note, generous glide and a slow,
    delayed vibrato - it sings rather than cuts."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.045), 0.5, 0.95, p.get('r', 0.6))
    rng = _rng()
    vib = 2 ** (14 * np.clip((t - 0.25) / 0.4, 0, 1) * np.sin(2 * np.pi * 5.0 * t) / 1200)
    fr = _glide_freq(f, n, glide, p.get('glide_t', 0.12)) * vib
    x = np.zeros((2, n))
    for k, c in enumerate((-9, -4, 0, 4, 9)):
        x[k % 2 if c else 0] += _va.saw(fr * 2 ** (c / 1200), n, rng.random()) * 0.32
        if c == 0:
            x[1] += _va.saw(fr, n, rng.random()) * 0.32
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x += 0.45 * np.sin(ph) + 0.03 * hp(rng.standard_normal(n), 3000)
    vel = float(p.get('vel', 0.85))
    cut = (1400 + 2600 * vel) * (1 + 0.6 * (1 - np.exp(-t / 0.12)) * np.exp(-t / 0.9))
    y = _va.vcf(x * 0.6, cut, 0.08, 1.15)
    y = np.tanh(y * 1.3) / np.tanh(1.3)
    return _hpf(_va.juno_chorus(y, 1, 0.25), 180) * env * 0.42


def v_dreamair(m, dur, p, glide=None, mod=None):
    """Dream air: a texture, not a note - pink-ish noise tuned faintly to the pitch through two narrow, slowly sweeping
    band-passes, a very slow attack and long release, kept to a narrow band - the floating wash behind everything."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 1.2), 1.0, 1.0, p.get('r', 3.0))
    rng = _rng()
    w = np.cumsum(rng.standard_normal((2, n)), axis=1)
    w = w - np.cumsum(w, axis=1) / (np.arange(n) + 1)
    w = hp(w / (np.abs(w).max() + 1e-9), 300)
    c1 = 2 ** (0.6 * np.sin(2 * np.pi * 0.05 * t + rng.random() * 6))
    y = np.vstack([bp(w[i], f * 4 * c1.mean() * 0.8, f * 4 * c1.mean() * 1.25) for i in range(2)])
    tone = 0.08 * np.sin(2 * np.pi * f * 4 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t))
    y = y / (np.abs(y).max() + 1e-9) * 0.5 + tone
    y = bp(y, 600, 9000)
    return y * env * 0.32


def v_dreampluck(m, dur, p, glide=None, mod=None):
    """Dreamy pluck: a clean saw and triangle with a sine underneath, a fast filter envelope with low sustain and a
    moderate, rounded resonance - a soft pluck (no sharp click) that blooms into the reverb, slightly wide."""
    f = float(mtof(m))
    n = int((min(dur, 1.2) + 0.5) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    tri = 2 * np.abs(2 * ((f * t + rng.random()) % 1) - 1) - 1
    x = np.vstack([_va.saw(np.full(n, f * 2 ** (-5 / 1200)), n, rng.random()), _va.saw(np.full(n, f * 2 ** (5 / 1200)), n, rng.random())]) * 0.45
    x += 0.4 * tri + 0.3 * np.sin(2 * np.pi * f * t)
    cut = 500 + p.get('cut', 4200) * np.exp(-t / p.get('fd', 0.11))
    y = _va.vcf(x, cut, 0.35, 1.0)
    env = np.minimum(1, t / 0.004) * np.exp(-t / p.get('decay', 0.45))
    return _hpf(y, 160) * env * 0.5


def v_dreambass(m, dur, p, glide=None, mod=None):
    """Dreamy bass: clean and supportive - a sine sub with a lightly filtered square mid layer for definition on small
    speakers, a short-to-medium envelope to stay tight, almost no drive."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, p.get('d', 0.35), 0.75, 0.06)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.05)) / SR
    mid = _va.vcf(_va.pulse(np.full(n, f), n, 0.0, 0.5), 300 + 900 * np.exp(-t / 0.08), 0.15, 1.0)
    y = (np.sin(ph) * 0.8 + hp(mid, 120) * 0.35) * env
    return np.vstack([y, y]) * 0.6


for _name, _fn, _info, _roles, _gm in (
        ('dreampad', v_dreampad, 'Dreamy pad (wide, floating, slow bloom)', ('pad', 'chords'), 89),
        ('dreamlead', v_dreamlead, 'Dreamy lead (soft, singing, glide)', ('lead',), 81),
        ('dreamair', v_dreamair, 'Dream air (atmospheric texture wash)', ('pad',), 95),
        ('dreampluck', v_dreampluck, 'Dreamy pluck (soft, blooming)', ('arp', 'lead', 'chords'), 84),
        ('dreambass', v_dreambass, 'Dreamy bass (clean sub + soft mid)', ('bass',), 38)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.84: festival / big-room synths
# Built for impact and clarity on big systems: heavy unison, fast filter envelopes, saturation after the filter, tight
# amp envelopes, wide tops and a mono low end.
def v_anthemlead(m, dur, p, glide=None, mod=None):
    """Anthem supersaw lead: seven heavily detuned saws (20-40 cents) spread wide, one an octave down and a quiet square
    for body, a 24 dB low-pass with real resonance whose fast-attack / medium-decay envelope opens hard on every note,
    saturation after the filter and a tight release - the big room / festival progressive drop lead."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.3, 1.0, p.get('r', 0.12))
    rng = _rng()
    x = np.zeros((2, n))
    for k, c in enumerate((-38, -24, -12, 0, 12, 24, 38)):
        pan = (k - 3) / 3.0
        s_ = _va.saw(f * 2 ** (c / 1200), n, rng.random()) * 0.3
        x[0] += s_ * (1 - 0.6 * pan)
        x[1] += s_ * (1 + 0.6 * pan)
    x += 0.35 * _va.saw(np.full(n, f / 2), n, rng.random()) + 0.15 * _va.pulse(np.full(n, f), n, rng.random(), 0.5)
    vel = float(p.get('vel', 0.9))
    cut = p.get('cut', 2200) * (1 + (2.5 + 2.5 * vel) * np.exp(-t / p.get('fd', 0.22)))
    y = _va.vcf(x * 0.4, np.minimum(cut, 16000), p.get('res', 0.45), 1.3)
    y = np.tanh(y * 1.8) / np.tanh(1.8)
    return _hpf(y, 200) * env * 0.42


def v_festpluck(m, dur, p, glide=None, mod=None):
    """Festival pluck / stab: two saws (light 4-voice unison) with a short noise burst on the attack, a resonant
    low-pass snapped open by an almost instant envelope that harder hits open further, a little bit-reduction for
    edge - the percussive, melodic drop hook of electro and festival house."""
    f = float(mtof(m))
    n = int((min(dur, 0.6) + 0.25) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    x = np.zeros((2, n))
    for k, c in enumerate((-10, -3, 3, 10)):
        x[k % 2] += (_va.saw(np.full(n, f * 2 ** (c / 1200)), n, rng.random()) * 0.4
                     + 0.2 * _va.pulse(np.full(n, f * 2 ** (c / 1200)), n, rng.random(), 0.5))
    x += 0.35 * hp(rng.standard_normal(n), 2000) * np.exp(-t / 0.006)
    vel = float(p.get('vel', 0.9))
    cut = 350 + p.get('cut', 3500) * (0.6 + 0.8 * vel) * np.exp(-t / p.get('fd', 0.07))
    y = _va.vcf(x, cut, p.get('res', 0.6), 1.5)
    y = np.round(np.tanh(y * 1.6) * 64) / 64
    env = np.minimum(1, t / 0.002) * np.exp(-t / p.get('decay', 0.2))
    return _hpf(y, 180) * env * 0.48


def v_hardbass(m, dur, p, glide=None, mod=None):
    """Hard driving bass: a saw and a square through a low-pass with a short, punchy envelope and mild distortion, over
    a clean mono sine sub an octave down - tight, locked to the kick, leaving the mids to the leads."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, p.get('d', 0.16), 0.55, 0.04)
    x = _va.saw(np.full(n, f), n, 0.0) + 0.5 * _va.pulse(np.full(n, f), n, 0.25, 0.5)
    top = np.tanh(_va.vcf(x * 0.5, 250 + 2200 * np.exp(-t / 0.05), 0.3, 1.5) * 2.0)
    sub = np.sin(2 * np.pi * (f if f < 70 else f / 2) * t)
    y = (hp(top, 110) * 0.55 + sub * 0.7) * env
    return np.vstack([y, y]) * 0.55


def v_electrobass(m, dur, p, glide=None, mod=None):
    """Electro growl bass: saw + square + noise, wavefolded and FM-roughened, its filter ripped by a fast envelope and
    a synced LFO, over a clean sub - the aggressive electro-house / festival bass."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.25, 0.85, 0.04)
    lfo = _sync_lfo(t, p, (2.0, 4.0))
    ph = 2 * np.pi * f * t
    x = _va.saw(np.full(n, f), n, 0.0) + 0.6 * _va.pulse(np.full(n, f * 1.003), n, 0.3, 0.5) + 0.1 * _rng().standard_normal(n)
    x = np.sin((x + 0.6 * np.sin(2 * ph)) * 1.6)                          # wavefold + a touch of FM
    cut = 300 + 3500 * np.maximum(np.exp(-t / 0.06), lfo)
    top = np.tanh(_va.vcf(x, cut, 0.45, 1.8) * 2.2)
    sub = lp(np.sin(ph if f < 70 else ph / 2), 100)
    y = (hp(top, 120) * 0.45 + sub * 0.75) * env
    return np.vstack([y, y]) * 0.55


def v_buildpad(m, dur, p, glide=None, mod=None):
    """Build pad: detuned supersaws with a longer attack and release than the lead, a slow filter rise, a layer of
    high noise for air, high-passed so it never fights the bass - the tension pad of breakdowns and builds."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.35), 1.0, 1.0, p.get('r', 1.4))
    x = _va.jp_supersaw(f, n, 0.6, 0.75, 1.0)
    x = x + 0.05 * hp(_rng().standard_normal((2, n)), 5000)
    cut = 800 + p.get('cut', 5000) * np.clip(t / max(0.5, dur), 0, 1) ** 1.5
    y = _va.vcf(x * 0.6, cut, 0.25, 1.1)
    return _hpf(y, 250) * env * 0.42


for _name, _fn, _info, _roles, _gm in (
        ('anthemlead', v_anthemlead, 'Anthem supersaw lead (big room, festival)', ('lead', 'chords'), 81),
        ('festpluck', v_festpluck, 'Festival pluck / stab (resonant, punchy)', ('arp', 'lead', 'chords'), 84),
        ('hardbass', v_hardbass, 'Hard driving bass (tight, mild drive)', ('bass',), 38),
        ('electrobass', v_electrobass, 'Electro growl bass (folded, aggressive)', ('bass',), 38),
        ('buildpad', v_buildpad, 'Build pad (rising supersaw, breakdowns)', ('pad', 'chords'), 89)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.86: from three sets of references
# dark sub-weight dubstep (2009-12), classic vocal trance (2004-09), festival techno / big-room trance (2011-14)
def v_dreadwob(m, dur, p, glide=None, mod=None):
    """Dread wobble: a dark, slow wobble - a detuned square / saw pair whose low-pass swings between ~100 Hz and ~900 Hz
    on a half- or quarter-note LFO, never bright - over a heavy mono sine sub. The sub carries the weight; the wobble
    is a growl in the low mids (the deep, sub-weight dubstep sound)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.006, 0.4, 0.95, 0.08)
    lfo = _sync_lfo(t, p, (0.5, 1.0, 2.0), mod)
    x = _va.pulse(np.full(n, f), n, 0.0, 0.5) * 0.6 + _va.saw(np.full(n, f * 1.006), n, 0.4) * 0.5
    top = _va.vcf(x, 100 + p.get('cut', 800) * lfo, 0.5, 1.8)
    top = np.tanh(top * 2.2)
    sub = np.sin(2 * np.pi * (f if f < 70 else f / 2) * t)
    y = (hp(top, 90) * 0.5 + sub * 0.85) * env
    return np.vstack([y, y]) * 0.55


def v_grimesquare(m, dur, p, glide=None, mod=None):
    """Grime square: a hollow square-wave lead / bleep with a quick pitch drop on the attack, a short decay and a little
    bit-crush - the cold, playful square riffs of grime and early dark dubstep."""
    f = float(mtof(m))
    n = int((min(dur, 0.8) + 0.12) * SR)
    t = np.arange(n) / SR
    fr = f * 2 ** (1.5 * np.exp(-t / 0.012) / 12)
    y = _va.pulse(fr, n, 0.0, 0.5)
    y = np.round(y * 12) / 12
    y = lp(y, 5000) * np.minimum(1, t / 0.002) * np.exp(-t / p.get('decay', 0.25))
    return _ms_stereo(y, 18, 0.25) * 0.32


def v_horrorstab(m, dur, p, glide=None, mod=None):
    """Horror stab: a dissonant, metallic hit - the note with its minor second and tritone, FM-roughened, with a fast
    pitch fall and a band-passed ring - the eerie one-shot stab of dark dubstep."""
    f = float(mtof(m))
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k, r in enumerate((1.0, 2 ** (1 / 12), 2 ** (6 / 12))):
        fr = f * r * 2 ** (-0.6 * (1 - np.exp(-t / 0.3)) / 12)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        y += np.sin(ph + 2.5 * np.exp(-t / 0.08) * np.sin(3.5 * ph)) * (1.0 if k == 0 else 0.6)
    y = bp(np.tanh(y * 1.5), 250, 6000) * np.minimum(1, t / 0.002) * np.exp(-t / 0.35)
    return _ms_stereo(y, 30, 0.45) * 0.35


def v_dubsiren(m, dur, p, glide=None, mod=None):
    """Dub siren: a square tone swept up and down by a fast LFO (the soundsystem siren), slightly crushed - a call
    over the drop in dubstep, reggae and jungle; give it echo."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.01, 0.2, 0.9, 0.15)
    rate = p.get('rate', 6.0)
    fr = f * 2 ** (0.5 * np.sin(2 * np.pi * rate * t) + 0.3 * np.clip(t / max(dur, 0.1), 0, 1))
    y = _va.pulse(fr, n, 0.0, 0.5)
    y = lp(np.round(y * 16) / 16, 4500) * env
    return _ms_stereo(y, 22, 0.3) * 0.28


def v_classiclead(m, dur, p, glide=None, mod=None):
    """Classic trance lead: a bright detuned saw pair over a pulse, with portamento, a short bright 'pluck' on the
    attack and a slow, delayed vibrato - the singing, cutting lead of mid-2000s vocal and uplifting trance."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.35, 0.85, p.get('r', 0.25))
    rng = _rng()
    vib = 2 ** (10 * np.clip((t - 0.3) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.5 * t) / 1200)
    fr = _glide_freq(f, n, glide, 0.07) * vib
    x = np.vstack([_va.saw(fr * 2 ** (-11 / 1200), n, rng.random()) + 0.35 * _va.pulse(fr, n, rng.random(), 0.35),
                   _va.saw(fr * 2 ** (11 / 1200), n, rng.random()) + 0.35 * _va.pulse(fr, n, rng.random(), 0.65)]) * 0.5
    cut = 2400 + 6500 * np.exp(-t / 0.09)
    y = _va.vcf(x, cut, 0.25, 1.3)
    return _hpf(y, 200) * env * 0.42


def v_megastab(m, dur, p, glide=None, mod=None):
    """Mega stab: an extremely wide supersaw chord stab - nine saws spread hard left and right with a short Haas offset
    (the very wide leads of festival techno), a punchy filter snap and saturation; keep the low end out (it is
    high-passed) so it stays mono-safe where it matters."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.25, 0.7, 0.12, 1.2)
    rng = _rng()
    x = np.zeros((2, n))
    for k, c in enumerate((-40, -28, -17, -8, 0, 8, 17, 28, 40)):
        s_ = _va.saw(f * 2 ** (c / 1200), n, rng.random()) * 0.25
        side = (k - 4) / 4.0
        x[0] += s_ * (1 - 0.9 * side)
        x[1] += s_ * (1 + 0.9 * side)
    x[1] = np.roll(x[1], int(0.008 * SR))
    cut = 1800 + 9000 * np.exp(-t / 0.12)
    y = np.tanh(_va.vcf(x * 0.5, cut, 0.35, 1.3) * 1.6)
    return _hpf(y, 300) * env * 0.4


def v_syncstab(m, dur, p, glide=None, mod=None):
    """Sync stab: a hard-synced saw whose slave pitch sweeps down on every hit (the 'tearing' sync sound) with a pulse
    underneath - a punchy, aggressive hook stab for festival techno and electro."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.2, 0.5, 0.08, 0.8)
    ratio = 1.5 + 3.0 * np.exp(-t / p.get('sweep', 0.08))
    ph = (f * t) % 1.0                                     # master phase
    y = 2 * ((ph * ratio) % 1.0) - 1                         # slave restarts with the master: hard sync
    y = y * 0.6 + 0.35 * _va.pulse(np.full(n, f), n, 0.0, 0.5)
    y = np.tanh(lp(y, 9000) * 1.6) * env
    return _ms_stereo(hp(y, 180), 20, 0.4) * 0.42


for _name, _fn, _info, _roles, _gm in (
        ('dreadwob', v_dreadwob, 'Dread wobble (dark, slow, sub-heavy)', ('bass',), 38),
        ('grimesquare', v_grimesquare, 'Grime square (hollow, crushed bleep)', ('lead', 'arp'), 80),
        ('horrorstab', v_horrorstab, 'Horror stab (dissonant metallic hit)', ('chords', 'lead', 'arp'), 55),
        ('dubsiren', v_dubsiren, 'Dub siren (soundsystem call)', ('lead',), 80),
        ('classiclead', v_classiclead, 'Classic trance lead (bright, singing, glide)', ('lead', 'arp'), 81),
        ('megastab', v_megastab, 'Mega stab (very wide supersaw)', ('chords', 'lead', 'arp'), 81),
        ('syncstab', v_syncstab, 'Sync stab (tearing hard-sync hook)', ('lead', 'arp', 'chords'), 81)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.87: from more reference sets
def v_squarewob(m, dur, p, glide=None, mod=None):
    """Early dubstep wobble: a plain square / saw pair through a low-pass that opens and closes on a slow quarter- or
    eighth-note LFO (100 Hz - 1.2 kHz), a little gritty, over a clean sine sub - the simple, heavy, hypnotic bass of
    mid-2000s dubstep, before the screaming mid-basses."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.005, 0.4, 0.95, 0.06)
    lfo = _sync_lfo(t, p, (1.0, 2.0, 2.0, 4.0), mod)
    x = _va.pulse(np.full(n, f), n, 0.0, 0.5) * 0.7 + _va.saw(np.full(n, f), n, 0.0) * 0.3
    top = np.tanh(_va.vcf(x, 100 + p.get('cut', 1100) * lfo, 0.35, 1.5) * 1.6)
    sub = np.sin(2 * np.pi * (f if f < 70 else f / 2) * t)
    y = (hp(top, 80) * 0.55 + sub * 0.8) * env
    return np.vstack([y, y]) * 0.55


def v_tonesub(m, dur, p, glide=None, mod=None):
    """Saturated sine sub: a sine pushed into soft saturation so its 2nd and 3rd harmonics carry it on small speakers,
    with a short pitch drop on the attack - the round, booming one-note bass of early dubstep and grime."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.5, 0.9, 0.08)
    fr = f * 2 ** (0.6 * np.exp(-t / 0.03) / 12)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.08) * (fr / f)) / SR
    y = np.tanh(np.sin(ph) * p.get('drive', 2.2)) / np.tanh(p.get('drive', 2.2)) * env
    return np.vstack([y, y]) * 0.6


def v_warblepad(m, dur, p, glide=None, mod=None):
    """Warble pad: a detuned PWM pad that drifts slightly out of tune the way an old tape or a cheap analog poly does
    (slow, random wow and flutter, different in each ear), dark and soft - the nostalgic, washed-out pad of 90s and
    2000s ambient electronica."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.4), 1.0, 0.95, p.get('r', 1.6))
    rng = _rng()
    out = np.zeros((2, n))
    for ch in range(2):
        w = lp(rng.standard_normal(n), 1.5)
        w = w / (np.abs(w).max() + 1e-9)
        wow = 2 ** ((p.get('wow', 18) * w + 3 * np.sin(2 * np.pi * 5.5 * t + rng.random() * 6)) / 1200)
        fr = f * wow
        x = _va.pulse(fr, n, rng.random(), 0.5 + 0.25 * np.sin(2 * np.pi * 0.3 * t + ch)) * 0.5 + \
            _va.saw(fr * 2 ** (7 / 1200), n, rng.random()) * 0.35
        out[ch] = x
    y = _va.vcf(out, p.get('cut', 1300), 0.15, 1.05)
    y = lp(y, 5000)
    return _hpf(y, 120) * env * 0.42


def v_warblelead(m, dur, p, glide=None, mod=None):
    """Warble lead: a soft, slightly detuned triangle-and-saw lead whose pitch sags and drifts like a stretched tape,
    with a gentle vibrato and a rolled-off top - the wistful, out-of-tune melody synth of ambient electronica."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.03, 0.5, 0.85, 0.4)
    rng = _rng()
    w = lp(rng.standard_normal(n), 2.0)
    w = w / (np.abs(w).max() + 1e-9)
    fr = _glide_freq(f, n, glide, 0.1) * 2 ** ((14 * w - 10 * (1 - np.exp(-t / 0.8)) + 6 * np.sin(2 * np.pi * 4.8 * t)) / 1200)
    ph = np.cumsum(fr) / SR
    tri = 2 * np.abs(2 * (ph % 1) - 1) - 1
    y = tri * 0.7 + 0.25 * _va.saw(fr, n, 0.3)
    y = _va.vcf(y, 1800, 0.1, 1.0) * env
    return _ms_stereo(lp(y, 4500), 30, 0.3) * 0.4


for _name, _fn, _info, _roles, _gm in (
        ('squarewob', v_squarewob, 'Early dubstep wobble (square, slow LFO)', ('bass',), 38),
        ('tonesub', v_tonesub, 'Saturated sine sub (round, booming)', ('bass',), 38),
        ('warblepad', v_warblepad, 'Warble pad (out-of-tune tape analog)', ('pad', 'chords'), 89),
        ('warblelead', v_warblelead, 'Warble lead (drifting, wistful)', ('lead', 'arp'), 80)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.88: another broad synth bank
# retro / synthwave, future bass & pop, lo-fi & R&B, ambient & cinematic, chip, funk and acid
def _stack_saw(fr, n, cents, rng, spread=0.7):
    x = np.zeros((2, n))
    for k, c in enumerate(cents):
        s_ = _va.saw(fr * 2 ** (c / 1200), n, rng.random())
        pan = (k / max(1, len(cents) - 1)) * 2 - 1
        x[0] += s_ * (1 - spread * pan) / len(cents)
        x[1] += s_ * (1 + spread * pan) / len(cents)
    return x


def v_cs80brass(m, dur, p, glide=None, mod=None):
    """Swelling poly brass: two detuned saws per voice whose filter and pitch rise slowly as the note is held (the
    'aftertouch' swell of the big 70s polysynths), with a slow chorus - the soaring brass of retro film and synthwave."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.12), 0.8, 0.95, p.get('r', 0.6))
    rng = _rng()
    swell = np.clip(t / max(0.4, dur * 0.7), 0, 1)
    fr = f * 2 ** ((-12 * np.exp(-t / 0.08) + 8 * swell * np.sin(2 * np.pi * 5.5 * t)) / 1200)
    x = _stack_saw(fr, n, (-9, 9), rng, 0.6)
    y = _va.vcf(x, 500 + p.get('cut', 3500) * (0.25 + 0.75 * swell), 0.2, 1.3)
    return _hpf(_va.juno_chorus(y, 1, 0.3), 150) * env * 0.5


def v_outrunbass(m, dur, p, glide=None, mod=None):
    """Outrun bass: a punchy saw-and-square bass with a fast filter snap and a short tail - built for the driving
    16th-note and octave-bouncing basslines of synthwave."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.14, 0.35, 0.04)
    x = _va.saw(np.full(n, f), n, 0.0) * 0.6 + _va.pulse(np.full(n, f * 1.004), n, 0.2, 0.5) * 0.5
    y = np.tanh(_va.vcf(x, 220 + 3200 * np.exp(-t / 0.045), 0.4, 1.6) * 1.4) * env
    return np.vstack([y, y]) * 0.55


def v_ppgwave(m, dur, p, glide=None, mod=None):
    """Digital wavetable bell-pad: an early-80s style wavetable that steps through bright, glassy, slightly aliased
    waveforms as the note sustains, with a bell attack - the shimmering digital pads of 80s pop and synthwave."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.005, 1.2, 0.7, p.get('r', 0.8))
    ph = 2 * np.pi * f * t
    pos = np.clip(t / max(0.5, dur), 0, 1)
    y = np.zeros(n)
    for h, a in ((1, 1.0), (2, 0.5), (3, 0.6), (5, 0.4), (7, 0.3), (9, 0.25)):
        y += a * np.sin(h * ph) * (1 - pos if h > 4 else 0.5 + 0.5 * pos)
    y = np.round(y * 48) / 48                                  # (8-bit-ish wavetable steps)
    y += 0.4 * np.sin(ph * 3.5) * np.exp(-t / 0.15)           # the bell attack
    y = lp(y, 7000) * env
    return _ms_stereo(y, 28, 0.45) * 0.35


def v_futurechord(m, dur, p, glide=None, mod=None):
    """Future bass chord: a wide detuned supersaw chord with a pitch 'wobble' bend and a volume LFO in time with the
    beat (the wavy, sidechained chords of future bass and melodic dubstep)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.4, 0.9, 0.15)
    rng = _rng()
    lfo = _sync_lfo(t, p, (2.0, 4.0), mod)
    fr = f * 2 ** ((-35 * np.exp(-t / 0.05) + 12 * np.sin(2 * np.pi * 0.5 / float(p.get('spb', 0.45)) * t)) / 1200)
    x = _stack_saw(fr, n, (-24, -12, -4, 4, 12, 24), rng, 0.9)
    y = _va.vcf(x, 1500 + 5000 * lfo, 0.15, 1.2)
    y = y * (0.4 + 0.6 * lfo)
    return _hpf(y, 180) * env * 0.55


def v_kawaiipluck(m, dur, p, glide=None, mod=None):
    """Kawaii pluck: a bright square pluck with an octave blip on the attack and a touch of pitch bend - the bouncy,
    candy-coloured lead plucks of future bass, kawaii and hyperpop."""
    f = float(mtof(m))
    n = int((min(dur, 0.5) + 0.25) * SR)
    t = np.arange(n) / SR
    fr = f * np.where(t < 0.018, 2.0, 1.0) * 2 ** (20 * np.exp(-t / 0.04) / 1200)
    y = _va.pulse(fr, n, 0.0, 0.3 + 0.2 * np.exp(-t / 0.1))
    y = lp(y, 6500) * np.minimum(1, t / 0.002) * np.exp(-t / p.get('decay', 0.18))
    return _ms_stereo(y, 20, 0.4) * 0.38


def v_tropicalpluck(m, dur, p, glide=None, mod=None):
    """Tropical pluck: a soft, woody, marimba-like pluck with a breathy pan-flute edge - the sunny lead of tropical
    house and chilled pop."""
    f = float(mtof(m))
    n = int((min(dur, 0.8) + 0.3) * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    y = np.sin(ph) * np.exp(-t / 0.22) + 0.35 * np.sin(4 * ph) * np.exp(-t / 0.03) + 0.2 * np.sin(2 * ph) * np.exp(-t / 0.1)
    air = bp(_rng().standard_normal(n), f * 1.5, f * 4) * 0.08 * np.exp(-t / 0.08)
    y = (y + air) * np.minimum(1, t / 0.003)
    return _ms_stereo(y, 22, 0.35) * 0.45


def v_vocalead(m, dur, p, glide=None, mod=None):
    """Vowel lead: a sung 'ooh' moving to 'aah' (and back on long notes) from a saw through formant filters, with
    vibrato and glide - a wordless synth-voice lead for pop, trance and ambient."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.04, 0.4, 0.9, 0.25)
    vib = 2 ** (18 * np.clip((t - 0.2) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.2 * t) / 1200)
    fr = _glide_freq(f, n, glide, 0.09) * vib
    src = _va.saw(fr, n, 0.0) * 0.8 + 0.06 * _rng().standard_normal(n)
    u = np.sin(np.pi * np.clip(t / max(0.3, dur), 0, 1)) ** 2
    y = _va.formant(src, 'u', 8.0) * (1 - u) + _va.formant(src, 'a', 8.0) * u
    return _ms_stereo(hp(y * env, 180), 25, 0.3) * 0.9


def v_chiparp(m, dur, p, glide=None, mod=None):
    """Chip lead: an 8-bit pulse whose duty cycle sweeps (12.5% -> 50%) with a fast, delayed vibrato and a crushed top
    - the expressive melody voice of chiptune and video-game music."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.1, 0.8, 0.03)
    vib = 2 ** (30 * np.clip((t - 0.12) / 0.1, 0, 1) * np.sin(2 * np.pi * 7 * t) / 1200)
    fr = _glide_freq(f, n, glide, 0.04) * vib
    duty = 0.125 + 0.375 * np.clip(t / 0.25, 0, 1)
    y = _va.pulse(fr, n, 0.0, duty)
    y = np.round(y * 8) / 8 * env
    return np.vstack([y, y]) * 0.3


def v_shimmerpad(m, dur, p, glide=None, mod=None):
    """Shimmer pad: a soft pad with an octave-up and a fifth-up halo blooming in slowly, as if through a shimmer
    reverb - glowing, heavenly, for ambient, post-rock and cinematic music."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.8), 1.0, 1.0, p.get('r', 2.5))
    rng = _rng()
    base = _stack_saw(np.full(n, f), n, (-6, 6), rng, 0.5)
    base = _va.vcf(base, 1600, 0.1, 1.0)
    halo = np.zeros((2, n))
    for r, a in ((2.0, 0.5), (3.0, 0.25), (4.0, 0.2)):
        for ch in range(2):
            halo[ch] += np.sin(2 * np.pi * f * r * t * (1 + 0.0015 * (ch - 0.5)) + rng.random() * 6) * a
    bloom = np.clip(t / max(1.0, dur * 0.8), 0, 1) ** 1.5
    y = base * 0.7 + halo * bloom[None, :] * 0.5
    return _hpf(y, 150) * env * 0.42


def v_reverseswell(m, dur, p, glide=None, mod=None):
    """Reverse swell: a bright pluck-pad played backwards - it swells up out of nothing and cuts off at the end of the
    note, sucking into the next beat; for transitions, builds and lo-fi / ambient textures."""
    f = float(mtof(m))
    n = max(int(dur * SR), 256)
    t = np.arange(n) / SR
    rng = _rng()
    x = _stack_saw(np.full(n, f), n, (-10, 0, 10), rng, 0.7)
    fwd = _va.vcf(x, 400 + 6000 * np.exp(-t / 0.25), 0.2, 1.1) * np.exp(-t / max(0.2, dur / 3))
    y = fwd[:, ::-1]
    k = min(n, int(0.01 * SR))
    y[:, -k:] *= np.linspace(1, 0, k)
    return _hpf(y, 150) * 0.5


def v_icebell(m, dur, p, glide=None, mod=None):
    """Ice bell: a glassy, crystalline FM bell (inharmonic 1 : 3.5 and 1 : 7.1 ratios) with a long, shimmering decay
    and a slight beating between the ears - for ambient, Christmas, music-box and dreamy pop."""
    f = float(mtof(m))
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    out = np.zeros((2, n))
    for ch, det in ((0, 1.0), (1, 1.0015)):
        ph = 2 * np.pi * f * det * t
        y = np.sin(ph + 2.2 * np.exp(-t / 0.6) * np.sin(3.5 * ph)) * np.exp(-t / 1.2)
        y += 0.3 * np.sin(7.1 * ph) * np.exp(-t / 0.25)
        out[ch] = y
    return hp(out, 200) * np.minimum(1, t / 0.002)[None, :] * 0.3


def v_bowedpad(m, dur, p, glide=None, mod=None):
    """Bowed glass: the sound of a bow on glass or metal - a sine-rich tone with a rough, noisy bow texture that
    swells and wavers, eerie and beautiful, for ambient, horror and cinematic beds."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.6), 1.0, 1.0, p.get('r', 1.5))
    rng = _rng()
    bow = lp(np.abs(rng.standard_normal(n)), 30)
    bow = bow / (bow.max() + 1e-9)
    ph = 2 * np.pi * f * t * (1 + 0.002 * np.sin(2 * np.pi * 0.3 * t))
    tone = np.sin(ph) + 0.3 * np.sin(2.01 * ph) + 0.15 * np.sin(3.98 * ph)
    rough = bp(rng.standard_normal(n), f * 0.8, f * 5) * 0.15
    y = (tone * (0.7 + 0.3 * bow) + rough * bow) * env
    return _ms_stereo(y, 40, 0.5) * 0.35


def v_ebowguitar(m, dur, p, glide=None, mod=None):
    """Swelling guitar: an infinitely sustaining, bowed-sounding guitar tone (as with a magnetic sustainer) that fades
    in with no pick attack and holds with a soft, singing overdrive - for ambient, post-rock and shoegaze."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.35), 1.0, 1.0, 0.6)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.12) * (1 + 0.003 * np.sin(2 * np.pi * 5 * t))) / SR
    y = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.15 * np.sin(4 * ph)
    y = np.tanh(y * 1.8) / np.tanh(1.8)
    y = eq(lp(y, 3500), 'peak', 1200, 1.0, 3.0) * env
    return _ms_stereo(y, 35, 0.45) * 0.35


def v_bitpiano(m, dur, p, glide=None, mod=None):
    """Crushed piano: the piano through a bit-crusher and a low sample rate - gritty, nostalgic, video-game-memory
    keys for lo-fi, hyperpop and glitch."""
    y = np.asarray(INSTRUMENTS['piano'](m, dur, p, glide, mod), float)
    y = y if y.ndim == 2 else np.vstack([y, y])
    step = int(p.get('down', 4))
    y = np.repeat(y[:, ::step], step, axis=1)[:, :y.shape[1]]
    y = np.round(y * 32) / 32
    return lp(y, 7000) * 0.9


def v_tapekeys(m, dur, p, glide=None, mod=None):
    """Tape keys: an electric piano played back from a worn cassette - wow and flutter, a soft, rolled-off top and a
    little hiss - the warm, wobbly chords of lo-fi hip-hop."""
    y = np.asarray(INSTRUMENTS['epiano'](m, dur, p, glide, mod), float)
    y = y if y.ndim == 2 else np.vstack([y, y])
    n = y.shape[1]
    t = np.arange(n) / SR
    rng = _rng()
    wow = 0.0008 * np.sin(2 * np.pi * 0.7 * t + rng.random() * 6) + 0.00003 * np.sin(2 * np.pi * 7 * t)   # (1.92) ~+/-6 cents
    idx = np.clip(np.arange(n) + wow * SR, 0, n - 1)                       # (it swung ~75 cents: audibly out of tune)
    y = np.vstack([np.interp(idx, np.arange(n), y[0]), np.interp(idx, np.arange(n), y[1])])
    y = lp(y, 4200) + 0.004 * hp(rng.standard_normal((2, n)), 4000)
    return y * 0.95


def v_rnbpad(m, dur, p, glide=None, mod=None):
    """R&B pad: a dark, silky pad - a filtered, chorused saw-and-triangle with a slow filter swell and a long release -
    the moody background of modern R&B and slow jams."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.3), 1.0, 0.95, p.get('r', 1.2))
    rng = _rng()
    x = _stack_saw(np.full(n, f), n, (-7, 7), rng, 0.6)
    tri = 2 * np.abs(2 * ((f * t) % 1) - 1) - 1
    x = x + 0.4 * tri[None, :]
    y = _va.vcf(x, 500 + 900 * np.clip(t / 1.5, 0, 1), 0.2, 1.05)
    return _hpf(_va.juno_chorus(y, 2, 0.35), 120) * env * 0.45


def v_pluckbell(m, dur, p, glide=None, mod=None):
    """Trap bell pluck: a bright, short, glassy bell-pluck (FM with a quick index fall) that cuts through 808s - the
    catchy little melody of trap, plugg and pop rap."""
    f = float(mtof(m))
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    y = np.sin(ph + 1.8 * np.exp(-t / 0.06) * np.sin(2 * ph)) * np.exp(-t / 0.28) + 0.25 * np.sin(4 * ph) * np.exp(-t / 0.05)
    return _ms_stereo(hp(y, 250) * np.minimum(1, t / 0.001), 18, 0.35) * 0.4


def v_acidsquare(m, dur, p, glide=None, mod=None):
    """Acid square: the 303's square-wave voice - hollow and rubbery, squelching through a resonant filter with accents
    and slides - a deeper, rounder acid line than the saw."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.2, 0.6, 0.03)
    acc = bool(mod) if not isinstance(mod, float) else mod > 0
    fr = _glide_freq(f, n, glide, 0.06)
    x = _va.pulse(fr, n, 0.0, 0.5)
    cut = 250 + p.get('cut', 1800) * (1.6 if acc else 1.0) * np.exp(-t / (0.12 if acc else 0.08))
    y = np.tanh(_va.vcf(x, cut, 0.75, 1.8) * (2.0 if acc else 1.4)) * env
    return np.vstack([y, y]) * 0.5


def v_synthwavelead(m, dur, p, glide=None, mod=None):
    """Synthwave lead: a bright detuned saw-and-square lead with portamento and a slow vibrato, slightly wide - the
    singing, nostalgic hook of synthwave and 80s-inspired pop (give it delay and reverb)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.006, 0.4, 0.85, 0.3)
    rng = _rng()
    vib = 2 ** (12 * np.clip((t - 0.25) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.0 * t) / 1200)
    fr = _glide_freq(f, n, glide, 0.08) * vib
    x = _stack_saw(fr, n, (-8, 8), rng, 0.5) * 0.8
    x += 0.3 * _va.pulse(fr, n, rng.random(), 0.5)[None, :]
    y = _va.vcf(x, 2600 + 4000 * np.exp(-t / 0.2), 0.2, 1.3)
    return _hpf(y, 200) * env * 0.5


def v_slapsynth(m, dur, p, glide=None, mod=None):
    """Synth slap bass: an FM bass with a hard, metallic 'pop' on the attack (the 80s digital slap) and a round body -
    for synthpop, funk, city pop and new jack swing."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.001, 0.25, 0.5, 0.05)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.04)) / SR
    y = np.sin(ph + 3.5 * np.exp(-t / 0.025) * np.sin(ph * 1.0) + 1.2 * np.exp(-t / 0.15) * np.sin(2 * ph))
    y = (y + 0.3 * np.sin(ph)) * env
    return np.vstack([y, y]) * 0.5


def v_sinelead(m, dur, p, glide=None, mod=None):
    """Sine lead: a pure, round sine with long portamento and a gentle vibrato - the sliding, almost-sub lead of trap
    and plugg melodies (and the classic 'G-funk whistle' an octave down)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.01, 0.3, 0.9, 0.15)
    vib = 2 ** (15 * np.clip((t - 0.2) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.5 * t) / 1200)
    ph = 2 * np.pi * np.cumsum(_glide_freq(f, n, glide, 0.15) * vib) / SR
    y = (np.sin(ph) + 0.08 * np.sin(2 * ph)) * env
    return _ms_stereo(y, 20, 0.2) * 0.45


def v_windpad(m, dur, p, glide=None, mod=None):
    """Wind pad: filtered noise tuned faintly to the note through two resonant band-passes that drift - an airy,
    breathing texture-pad for ambient, cinematic and lo-fi intros."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 1.0), 1.0, 1.0, p.get('r', 2.0))
    rng = _rng()
    x = rng.standard_normal((2, n))
    a = bp(x, f * 0.9, f * 1.12)
    b = bp(x, f * 1.9, f * 2.2)
    sway = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t + rng.random() * 6)
    y = (a * sway + b * (1 - sway) * 0.6)
    y = y / (np.abs(y).max() + 1e-9)
    return y * env * 0.4


for _name, _fn, _info, _roles, _gm in (
        ('cs80brass', v_cs80brass, 'Swelling poly brass (retro film, synthwave)', ('chords', 'lead', 'pad'), 62),
        ('outrunbass', v_outrunbass, 'Outrun bass (punchy, synthwave 16ths)', ('bass',), 38),
        ('ppgwave', v_ppgwave, 'Digital wavetable bell-pad (80s)', ('pad', 'chords', 'arp'), 88),
        ('futurechord', v_futurechord, 'Future bass chord (wavy, wide)', ('chords', 'pad'), 81),
        ('kawaiipluck', v_kawaiipluck, 'Kawaii pluck (bright square, octave blip)', ('arp', 'lead'), 80),
        ('tropicalpluck', v_tropicalpluck, 'Tropical pluck (woody, breathy)', ('arp', 'lead'), 12),
        ('vocalead', v_vocalead, 'Vowel lead (sung ooh-aah)', ('lead',), 54),
        ('chiparp', v_chiparp, 'Chip lead (duty sweep, vibrato)', ('lead', 'arp'), 80),
        ('shimmerpad', v_shimmerpad, 'Shimmer pad (octave halo)', ('pad', 'chords'), 91),
        ('reverseswell', v_reverseswell, 'Reverse swell (sucks into the beat)', ('pad', 'chords', 'arp'), 89),
        ('icebell', v_icebell, 'Ice bell (glassy FM, long)', ('arp', 'lead'), 14),
        ('bowedpad', v_bowedpad, 'Bowed glass (eerie bowed metal)', ('pad',), 92),
        ('ebowguitar', v_ebowguitar, 'Swelling guitar (bowed sustain)', ('lead', 'pad'), 30),
        ('bitpiano', v_bitpiano, 'Crushed piano (lo-fi, bit-crushed)', ('chords', 'arp', 'lead'), 0),
        ('tapekeys', v_tapekeys, 'Tape keys (wobbly cassette e-piano)', ('chords', 'arp'), 4),
        ('rnbpad', v_rnbpad, 'R&B pad (dark, silky)', ('pad', 'chords'), 89),
        ('pluckbell', v_pluckbell, 'Trap bell pluck (bright, short)', ('arp', 'lead'), 14),
        ('acidsquare', v_acidsquare, 'Acid square (303 square wave)', ('bass', 'arp'), 38),
        ('synthwavelead', v_synthwavelead, 'Synthwave lead (bright, gliding)', ('lead',), 81),
        ('slapsynth', v_slapsynth, 'Synth slap bass (80s digital)', ('bass',), 37),
        ('sinelead', v_sinelead, 'Sine lead (round, sliding)', ('lead',), 80),
        ('windpad', v_windpad, 'Wind pad (airy, breathing noise)', ('pad',), 95)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.89: trance and dubstep banks
# --- trance
def v_gatedchoir(m, dur, p, glide=None, mod=None):
    """Gated choir: a wide 'aah' voice pad cut into a trance-gate rhythm in 16ths (the chopped, pulsing vocal pads of
    vocal and uplifting trance breakdowns)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.01, 0.6, 0.9, 0.2)
    rng = _rng()
    x = _stack_saw(np.full(n, f), n, (-8, 0, 8), rng, 0.7)
    y = np.vstack([_va.formant(x[i], 'a', 7.0) for i in range(2)])
    spb = float(p.get('spb', 0.45))
    pat = str(p.get('gate_pat') or 'x.xxx.xx.xxx.x.x')
    step = ((t / (spb / 4)).astype(int)) % len(pat)
    g = np.array([1.0 if pat[i] == 'x' else 0.0 for i in step])
    g = np.convolve(g, np.ones(96) / 96, 'same')
    return _hpf(y * g[None, :], 200) * env * 0.9


def v_breakpiano(m, dur, p, glide=None, mod=None):
    """Breakdown piano: a bright, hall-ready piano layered with a soft saw pluck an octave up - the emotional, glassy
    keys of trance breakdowns."""
    y = np.asarray(INSTRUMENTS['piano'](m, dur, p, glide, mod), float)
    y = y if y.ndim == 2 else np.vstack([y, y])
    f = float(mtof(m)) * 2
    n = y.shape[1]
    t = np.arange(n) / SR
    pl = _va.vcf(_va.saw(np.full(n, f), n, 0.0), 300 + 5000 * np.exp(-t / 0.12), 0.2, 1.0) * np.exp(-t / 0.5) * 0.25
    y = y + np.vstack([pl, np.roll(pl, 30)])
    return eq(y, 'highshelf', 5000, 0.7, 3.0) * 0.85


def v_tranceseq(m, dur, p, glide=None, mod=None):
    """Trance sequence: a mono saw whose resonant filter snaps open on every 16th and shuts again, its cutoff rising
    over the bar - the driving, hypnotic off-beat sequencer line of trance and progressive."""
    f = float(mtof(m))
    n = int((min(dur, 0.4) + 0.06) * SR)
    t = np.arange(n) / SR
    x = _va.saw(np.full(n, f), n, 0.0) * 0.7 + _va.pulse(np.full(n, f * 1.003), n, 0.3, 0.5) * 0.3
    y = _va.vcf(x, 300 + p.get('cut', 3000) * np.exp(-t / 0.05), 0.55, 1.5)
    env = np.minimum(1, t / 0.002) * np.exp(-t / 0.09)
    return _ms_stereo(_hpf(y * env, 150), 15, 0.3) * 0.5


def v_tranceflute(m, dur, p, glide=None, mod=None):
    """Trance flute: a breathy synth flute - a sine-and-triangle tone with a noisy breath, gentle glide and vibrato -
    the airy hook of progressive and Balearic trance."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.05, 0.3, 0.9, 0.3)
    rng = _rng()
    vib = 2 ** (14 * np.clip((t - 0.2) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.3 * t) / 1200)
    fr = _glide_freq(f, n, glide, 0.08) * vib
    ph = np.cumsum(fr) / SR
    tri = 2 * np.abs(2 * (ph % 1) - 1) - 1
    y = np.sin(2 * np.pi * ph) * 0.7 + tri * 0.25
    breath = bp(rng.standard_normal(n), f * 1.5, f * 6) * (0.12 + 0.2 * np.exp(-t / 0.08))
    return _ms_stereo((y + breath) * env, 22, 0.3) * 0.45


def v_vocoderchord(m, dur, p, glide=None, mod=None):
    """Vocoder chord: a robot-choir chord - a bright saw carrier through a bank of vowel formants with a slight
    movement between 'ee' and 'ah' - the vocoded hooks and pads of 2000s trance and electro."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.01, 0.4, 0.85, 0.2)
    rng = _rng()
    x = _va.saw(np.full(n, f), n, 0.0) + 0.4 * _va.pulse(np.full(n, f), n, 0.3, 0.5) + 0.05 * rng.standard_normal(n)
    u = 0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t)
    y = _va.formant(x, 'i', 9.0) * u + _va.formant(x, 'a', 9.0) * (1 - u)
    return _ms_stereo(hp(y * env, 200), 30, 0.4) * 0.8


def v_trancepizz(m, dur, p, glide=None, mod=None):
    """Trance pizzicato: a hollow, string-like synth pizzicato (filtered square with a fast decay) - the plucked
    ostinato of uplifting trance intros and breakdowns."""
    f = float(mtof(m))
    n = int((min(dur, 0.4) + 0.2) * SR)
    t = np.arange(n) / SR
    x = _va.pulse(np.full(n, f), n, 0.0, 0.35)
    y = _va.vcf(x, 400 + 3500 * np.exp(-t / 0.04), 0.3, 1.1) * np.minimum(1, t / 0.002) * np.exp(-t / 0.12)
    return _ms_stereo(hp(y, 180), 18, 0.35) * 0.5


def v_rawlead(m, dur, p, glide=None, mod=None):
    """Raw lead: a hard, distorted, pitch-bent screech lead - detuned saws driven into clipping with a downward pitch
    bend on every note - the aggressive hook of hard trance and hardstyle."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.2, 0.9, 0.08)
    rng = _rng()
    fr = _glide_freq(f, n, glide, 0.04) * 2 ** ((150 * np.exp(-t / 0.04)) / 1200)
    x = _stack_saw(fr, n, (-20, -7, 7, 20), rng, 0.6)
    y = np.tanh(_va.vcf(x, 4000, 0.3, 2.0) * 4.0)
    y = eq(y, 'peak', 2500, 1.0, 4.0)
    return _hpf(y, 250) * env * 0.35


def v_offbass(m, dur, p, glide=None, mod=None):
    """Off-beat trance bass: a short, tight saw bass with a quick filter pluck, high-passed slightly so it sits between
    the kicks without fighting them - the classic 'oom-PAH' off-beat bass of trance and progressive."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.12, 0.4, 0.03, 0.25)
    x = _va.saw(np.full(n, f), n, 0.0) + 0.5 * _va.saw(np.full(n, f * 1.005), n, 0.4)
    y = _va.vcf(x * 0.6, 300 + 1500 * np.exp(-t / 0.05), 0.25, 1.3)
    y = hp(y, 40) * env
    return np.vstack([y, y]) * 0.6


# --- dubstep
def v_laserwob(m, dur, p, glide=None, mod=None):
    """Laser bass: rapid FM 'zaps' whose pitch dives on every repeat (in 16ths or triplets) - the laser-gun bass of
    brostep and riddim fills - over a sub."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.2, 0.9, 0.04)
    spb = float(p.get('spb', 0.45))
    per = spb / (4 if not mod else max(1, int(mod) * 2))
    ph_t = t % per
    fr = f * 2 * (1 + 6 * np.exp(-ph_t / (per * 0.25)))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    zap = np.tanh(np.sin(ph + 2.0 * np.sin(1.5 * ph)) * 3.0) * np.exp(-ph_t / (per * 0.6))
    sub = lp(np.sin(2 * np.pi * f * t), 100)
    y = (hp(zap, 150) * 0.45 + sub * 0.7) * env
    return np.vstack([y, y]) * 0.55


def v_robotbass(m, dur, p, glide=None, mod=None):
    """Robot bass: a ring-modulated saw spoken through a fast-changing sequence of vowels - a mechanical, talking
    'robot voice' mid-bass for brostep and electro-dubstep, over a sub."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.3, 0.85, 0.05)
    x = _va.saw(np.full(n, f * 2), n, 0.0) * np.sign(np.sin(2 * np.pi * f * 3.01 * t))
    k = max(3, int(dur / 0.07))
    seq = ['a', 'o', 'i', 'u', 'e']
    seg = np.minimum((t / max(dur, 0.05) * k).astype(int), k - 1)
    y = np.zeros(n)
    forms = {v: _va.formant(x, v, 8.0) for v in seq}
    for i in range(k):
        msk = seg == i
        y[msk] = forms[seq[(i * 3) % len(seq)]][msk]
    y = np.convolve(y, np.ones(64) / 64, 'same')
    sub = lp(np.sin(2 * np.pi * f * t), 100)
    out = (hp(np.tanh(y * 3.0), 140) * 0.5 + sub * 0.7) * env
    return np.vstack([out, out]) * 0.55


def v_dubhorn(m, dur, p, glide=None, mod=None):
    """Dubstep horn: a huge, brassy FM stab - a falling, blaring 'horn' with grit and a short tail - the sound of
    big festival dubstep drops, over a sub."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.3, 0.7, 0.08, 1.0)
    fr = f * 2 * 2 ** (-0.5 * np.clip(t / 0.4, 0, 1) / 12)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph + (3.0 + 2.0 * np.exp(-t / 0.15)) * np.sin(ph))
    y = np.tanh(eq(y, 'peak', 1200, 0.8, 6.0) * 3.0)
    sub = lp(np.sin(2 * np.pi * f * t), 100)
    out = (hp(y, 150) * 0.45 + sub * 0.65) * env
    return np.vstack([out, np.roll(out, 20)]) * 0.55


def v_divebass(m, dur, p, glide=None, mod=None):
    """Dive bass: a distorted mid-bass that drops an octave over the length of each note (the pitch 'dive') - for
    brostep fills and the end of a phrase - with a sub that dives with it."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.3, 0.9, 0.04)
    fr = f * 2 ** (-np.clip(t / max(0.1, dur), 0, 1) ** 1.5)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    top = np.tanh((np.sin(2 * ph) + 0.6 * (2 * ((2 * ph / (2 * np.pi)) % 1) - 1)) * 3.0)
    sub = np.sin(ph) * 0.7
    out = (hp(_va.vcf(top, 3000, 0.3, 1.5), 130) * 0.45 + lp(sub, 100)) * env
    return np.vstack([out, out]) * 0.55


def v_creakbass(m, dur, p, glide=None, mod=None):
    """Creak bass: a gritty, creaking low growl - a pulse train through a resonant comb whose delay creeps up and down,
    like a door creaking in the low mids - for heavy and tearout dubstep, over a sub."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.3, 0.9, 0.04)
    x = _va.pulse(np.full(n, f * 2), n, 0.0, 0.15)
    lfo = _sync_lfo(t, p, (1.0, 2.0), mod)
    d = (SR / (f * (3 + 5 * lfo))).astype(int)
    idx = np.clip(np.arange(n) - d, 0, n - 1)
    y = x + 0.9 * x[idx]
    y = np.tanh(_va.vcf(y, 800 + 2500 * lfo, 0.5, 2.0) * 2.5)
    sub = lp(np.sin(2 * np.pi * f * t), 100)
    out = (hp(y, 140) * 0.45 + sub * 0.7) * env
    return np.vstack([out, out]) * 0.55


def v_mdsawlead(m, dur, p, glide=None, mod=None):
    """Melodic dubstep lead: a big, soaring supersaw lead with long portamento, a pitch bend into every note and a
    slow vibrato - the emotional hook of melodic dubstep and future bass."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.005, 0.4, 0.9, 0.3)
    rng = _rng()
    vib = 2 ** (14 * np.clip((t - 0.3) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.0 * t) / 1200)
    fr = _glide_freq(f, n, glide, 0.12) * vib * 2 ** (-60 * np.exp(-t / 0.06) / 1200)
    x = _stack_saw(fr, n, (-22, -11, 0, 11, 22), rng, 0.9)
    y = _va.vcf(x, 5000, 0.15, 1.3)
    return _hpf(y, 220) * env * 0.5


def v_colorbass(m, dur, p, glide=None, mod=None):
    """Color bass: a chord played as the bass - the root, fifth and tenth (or a minor third) stacked as bright,
    wobbling supersaws over a sub, so the bass carries the harmony - the 'color bass' of melodic and future riddim."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.3, 0.9, 0.06)
    rng = _rng()
    lfo = _sync_lfo(t, p, (2.0, 4.0), mod)
    third = in_key_interval(m, p, (3, 4) if p.get('minor', True) else (4, 3))       # (1.92) the key's own third
    fifth = in_key_interval(m, p, (7, 6, 8))                                           # ... and fifth
    top = np.zeros((2, n))
    for semis in [12] + ([12 + fifth] if fifth is not None else []) + ([24 + third] if third is not None else []):
        top += _stack_saw(np.full(n, f * 2 ** (semis / 12)), n, (-10, 10), rng, 0.8)
    top = _va.vcf(top * 0.6, 400 + 4000 * lfo, 0.3, 1.5)
    sub = lp(np.sin(2 * np.pi * f * t), 100)
    out = (_hpf(np.tanh(top * 1.5), 150) * 0.5 + sub[None, :] * 0.7) * env
    return out * 0.55


def v_stabwob(m, dur, p, glide=None, mod=None):
    """Stab wobble: a short, punchy wobble burst - one fast filter 'wob' per note with a hard attack - for the
    stop-start, stuttering bass hits of riddim and brostep."""
    f = float(mtof(m))
    n = int((min(dur, 0.35) + 0.04) * SR)
    t = np.arange(n) / SR
    x = _va.saw(np.full(n, f), n, 0.0) + _va.pulse(np.full(n, f * 1.01), n, 0.4, 0.5)
    cut = 150 + 3000 * np.sin(np.pi * np.clip(t / 0.18, 0, 1))
    y = np.tanh(_va.vcf(x * 0.5, cut, 0.6, 2.0) * 3.0)
    sub = lp(np.sin(2 * np.pi * f * t), 100)
    env = np.minimum(1, t / 0.002) * np.exp(-t / 0.2)
    out = (hp(y, 120) * 0.5 + sub * 0.7) * env
    return np.vstack([out, out]) * 0.55


for _name, _fn, _info, _roles, _gm in (
        ('gatedchoir', v_gatedchoir, 'Gated choir (trance-gated aah pad)', ('pad', 'chords'), 52),
        ('breakpiano', v_breakpiano, 'Breakdown piano (bright, layered)', ('chords', 'arp', 'lead'), 0),
        ('tranceseq', v_tranceseq, 'Trance sequence (16th filter snaps)', ('arp',), 81),
        ('tranceflute', v_tranceflute, 'Trance flute (breathy synth flute)', ('lead', 'arp'), 73),
        ('vocoderchord', v_vocoderchord, 'Vocoder chord (robot choir)', ('chords', 'pad', 'lead'), 54),
        ('trancepizz', v_trancepizz, 'Trance pizzicato (hollow synth pizz)', ('arp',), 45),
        ('rawlead', v_rawlead, 'Raw lead (distorted, pitch-bent screech)', ('lead',), 81),
        ('offbass', v_offbass, 'Off-beat trance bass (tight saw)', ('bass',), 38),
        ('laserwob', v_laserwob, 'Laser bass (diving FM zaps)', ('bass', 'lead'), 38),
        ('robotbass', v_robotbass, 'Robot bass (talking ring-mod)', ('bass', 'lead'), 38),
        ('dubhorn', v_dubhorn, 'Dubstep horn (blaring FM brass)', ('bass', 'lead', 'chords'), 38),
        ('divebass', v_divebass, 'Dive bass (drops an octave per note)', ('bass',), 38),
        ('creakbass', v_creakbass, 'Creak bass (creaking comb growl)', ('bass',), 38),
        ('mdsawlead', v_mdsawlead, 'Melodic dubstep lead (soaring supersaw)', ('lead',), 81),
        ('colorbass', v_colorbass, 'Color bass (chord-bass, wobbling)', ('bass', 'chords'), 38),
        ('stabwob', v_stabwob, 'Stab wobble (short wob hits)', ('bass',), 38)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.91: synthscape bank
def v_warmpulse(m, dur, p, glide=None, mod=None):
    """Warm pulse: a round, felt-soft synth tone (triangle over two gently detuned saws, low-passed around 1 kHz with
    a slight bloom) with a little cassette wow - played as pulsing chord notes it becomes the breathing heart of a
    dreamy synthscape."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.025), 0.35, 0.8, p.get('r', 0.45))
    rng = _rng()
    wow = 2 ** (6 * np.sin(2 * np.pi * 0.55 * t + rng.random() * 6) / 1200)
    fr = f * wow
    ph = np.cumsum(fr) / SR
    tri = 2 * np.abs(2 * ((ph + rng.random()) % 1) - 1) - 1
    x = np.zeros((2, n))
    x += 0.7 * tri[None, :]
    for k, c in enumerate((-6, 6)):
        x[k] += _va.saw(fr * 2 ** (c / 1200), n, rng.random()) * 0.28
    cut = float(p.get('cut', 1100)) * (1 + 0.5 * np.exp(-t / 0.18))
    y = _va.vcf(x, cut, 0.12, 1.0)
    return _hpf(_va.juno_chorus(y, 1, 0.3), 110) * env * 0.55


def v_glintchime(m, dur, p, glide=None, mod=None):
    """Glint chime: a tiny, soft bell glint (a sine with a quiet inharmonic partial and a fast decay), each note
    thrown to a slightly different place in the stereo field - the sparkles that drift high above a synthscape,
    meant to be drowned in reverb and echo."""
    f = float(mtof(m))
    n = int((min(dur, 1.2) + 1.0) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.45) + 0.25 * np.sin(2 * np.pi * f * 3 * t) * np.exp(-t / 0.12)
    y += 0.12 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.05)                 # harmonic partials only: always in key
    y *= np.minimum(1, t / 0.004)
    pan = rng.uniform(-0.6, 0.6)
    out = np.vstack([y * (1 - pan), y * (1 + pan)])
    return lp(out, 6000) * 0.35


def v_glidetone(m, dur, p, glide=None, mod=None):
    """Glide tone: a soft sine-and-triangle voice that slides into every note from a few semitones away and sings with
    a slow vibrato and tape wow - the drifting, bending lines that float through a synthscape."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.08), 0.5, 0.9, p.get('r', 0.9))
    rng = _rng()
    start = (glide - m) if glide is not None else rng.choice([-5, -3, -2, 2, 3])   # (glide: the note it slides from)
    bend = start * np.exp(-t / 0.16)                                    # the slide into the note
    vib = 18 * np.clip((t - 0.3) / 0.5, 0, 1) * np.sin(2 * np.pi * 4.6 * t)
    wow = 7 * np.sin(2 * np.pi * 0.6 * t + rng.random() * 6)
    fr = f * 2 ** ((bend * 100 + vib + wow) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    tri = 2 / np.pi * np.arcsin(np.sin(ph))
    y = 0.75 * np.sin(ph) + 0.3 * tri
    y = lp(y, 2200)
    return _ms_stereo(y * env, 240) * 0.5


for _name, _fn, _info, _roles, _gm in (
        ('warmpulse', v_warmpulse, 'Warm pulse (round, felt-soft, breathing chords)', ('chords', 'pad', 'arp'), 89),
        ('glintchime', v_glintchime, 'Glint chime (tiny sparkles for reverb)', ('arp', 'lead'), 9),
        ('glidetone', v_glidetone, 'Glide tone (sliding, singing sine)', ('lead',), 80)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.91: sine bank (measured from a
# chill synth record whose every layer is a near-pure sine: two copies ~1.2 Hz apart beating slowly, a hint of 2nd
# and 3rd harmonic, ~7 cents of slow tape wobble, nothing bright)
def _beating_sine(f, n, t, rng, beat=1.2, wob=7.0, h2=0.06, h3=0.03):
    """Two sines `beat` Hz apart (one per side, so the beating also moves across the stereo field), a little 2nd / 3rd
    harmonic and a slow wobble (cents)."""
    w = 2 ** (wob * 1.4 * np.sin(2 * np.pi * 0.55 * t + rng.random() * 6) / 1200)
    out = np.zeros((2, n))
    for ch, d in enumerate((-beat / 2, beat / 2)):
        ph = 2 * np.pi * np.cumsum((f + d) * w) / SR + rng.random() * 6
        out[ch] = np.sin(ph) + h2 * np.sin(2 * ph) + h3 * np.sin(3 * ph)
    return out


def v_sinepad(m, dur, p, glide=None, mod=None):
    """Sine pad: soft, pure chord tones that bloom in slowly and beat gently against a twin a hair out of tune, with
    a slow tape wobble - the glassy-warm drone of a chill synth piece (no saw buzz at all)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.35), 1.0, 1.0, p.get('r', 1.4))
    y = _beating_sine(f, n, t, _rng(), float(p.get('beat', 1.2)), 7.0, 0.05, 0.02)
    return y * env * 0.32


def v_sinepulse(m, dur, p, glide=None, mod=None):
    """Sine pulse: a soft sine note that speaks quickly, settles about 6 dB lower within 150 ms and holds - played in
    quarter notes on the chord tones, the gently pulsing heart of a synthscape."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.012), 0.15, 0.5, p.get('r', 0.35))
    y = _beating_sine(f, n, t, _rng(), 1.1, 6.0, 0.1, 0.04)
    y = y * (0.5 + 0.5 * np.exp(-t / 0.12))[None, :]                     # the quick settle after the attack
    return y * env * 0.5


def v_roundbass(m, dur, p, glide=None, mod=None):
    """Round bass: a near-pure sine in the low-mid register (it lives around 100 Hz, not in the sub), a soft attack
    and a touch of 2nd harmonic so it is heard on small speakers - the bass of a dark, warm, sub-less mix."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.04), 0.4, 0.9, p.get('r', 0.5))
    rng = _rng()
    w = 2 ** (4 * np.sin(2 * np.pi * 0.5 * t + rng.random() * 6) / 1200)
    ph = 2 * np.pi * np.cumsum(f * w) / SR
    y = np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.03 * np.sin(3 * ph)
    return np.vstack([y, y]) * env * 0.6


for _name, _fn, _info, _roles, _gm in (
        ('sinepad', v_sinepad, 'Sine pad (pure, slowly beating drone)', ('pad', 'chords'), 89),
        ('sinepulse', v_sinepulse, 'Sine pulse (soft pulsing chord tones)', ('arp', 'chords'), 80),
        ('roundbass', v_roundbass, 'Round bass (pure low-mid sine, no sub)', ('bass',), 38)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


def v_whistlelead(m, dur, p, glide=None, mod=None):
    """Whistle lead: a smooth, near-pure sine that never sits still - it slides from the last note (a slow portamento),
    wavers with a lazy vibrato and a slower, uneven drift (about +/-40 cents in all, like a whistle or a theremin played
    gently) and breathes in softly. The singing, gliding top line of a chill synthscape."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.07), 0.5, 0.92, p.get('r', 0.7))
    rng = _rng()
    fr = _glide_freq(f, n, glide, p.get('glide_t', 0.11))
    vib = 22 * np.clip((t - 0.15) / 0.4, 0, 1) * np.sin(2 * np.pi * (3.6 + 0.4 * rng.random()) * t + rng.random() * 6)
    drift = 14 * np.sin(2 * np.pi * 0.7 * t + rng.random() * 6) + 6 * np.sin(2 * np.pi * 1.9 * t + rng.random() * 6)
    fr = fr * 2 ** ((vib + drift) / 1200)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph) + 0.07 * np.sin(2 * ph) + 0.02 * np.sin(3 * ph)
    y = y + 0.012 * lp(hp(rng.standard_normal(n), 900), 3000) * np.exp(-t / 0.2)    # a little breath at the start
    return _ms_stereo(y * env, 200) * 0.45


def v_sinepluck(m, dur, p, glide=None, mod=None):
    """Sine pluck: a soft, round sine note that rings briefly (with the same slow beating as the sine pads) - the
    gentle background arpeggios of a synthscape, meant for long reverb and echo."""
    f = float(mtof(m))
    n = int((min(dur, 1.0) + 0.6) * SR)
    t = np.arange(n) / SR
    y = _beating_sine(f, n, t, _rng(), 1.3, 5.0, 0.08, 0.03)
    env = np.minimum(1, t / 0.006) * np.exp(-t / float(p.get('decay', 0.32)))
    return y * env[None, :] * 0.5


for _name, _fn, _info, _roles, _gm in (
        ('whistlelead', v_whistlelead, 'Whistle lead (smooth sine, slides and wavers)', ('lead',), 79),
        ('sinepluck', v_sinepluck, 'Sine pluck (soft round arpeggio note)', ('arp',), 9)):
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.92: new sounds across the genres
# Every one is built from harmonic partials (whole-number ratios, octaves and fifths) with only a few cents of
# detune or drift, so they always sit in key and in tune with the chords.
def in_key_interval(m, p, choices):
    """(1.92) The first of `choices` (semitones above note m) that lands in the song's key (p['key_pcs'], passed by the
    renderer), or the first choice when the key is unknown - for sounds that stack intervals on one note."""
    pcs = p.get('key_pcs') if isinstance(p, dict) else None
    if not pcs:
        return choices[0]
    for c in choices:
        if (int(round(m)) + c) % 12 in pcs:
            return c
    return None


def _sine_stack(fr, n, amps, rng, ph=None):
    """Harmonic additive tone: amps[k] for harmonic k+1 at frequency curve fr (array)."""
    base = 2 * np.pi * np.cumsum(fr) / SR + (rng.random() * 6 if ph is None else ph)
    return sum(a * np.sin((k + 1) * base) for k, a in enumerate(amps) if a)


def _wow(t, rng, cents=5.0, rate=0.6):
    return 2 ** (cents * np.sin(2 * np.pi * rate * t + rng.random() * 6) / 1200)


# --- synthscape / chill
def v_tapeflute(m, dur, p, glide=None, mod=None):
    """Tape flute: a breathy, soft flute tone (sine with a little 2nd / 3rd harmonic and filtered breath) played back
    from a slightly wobbly tape, sliding from the last note - a gentle lead for chill synthscapes and lo-fi."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.09, 0.4, 0.9, 0.5)
    rng = _rng()
    fr = _glide_freq(f, n, glide, 0.09) * _wow(t, rng, 6) * 2 ** (10 * np.clip((t - 0.3) / 0.4, 0, 1) * np.sin(2 * np.pi * 4.8 * t) / 1200)
    y = _sine_stack(fr, n, (1.0, 0.12, 0.05), rng)
    y += 0.05 * lp(hp(rng.standard_normal(n), 1200), 4000) * (0.4 + 0.6 * np.exp(-t / 0.15))
    return _ms_stereo(lp(y, 3500) * env, 180) * 0.5


def v_glasskeys(m, dur, p, glide=None, mod=None):
    """Glass keys: a soft sine electric piano (a 1:1 FM tine that mellows as it rings, a hint of 2:1 bark), chorused -
    the mellow keys of chillhop, synthscapes and R&B."""
    f = float(mtof(m))
    n = int((min(dur, 3.0) + 1.2) * SR)
    t = np.arange(n) / SR
    idx = 1.4 * np.exp(-t / 0.35) + 0.15
    ph = 2 * np.pi * f * t
    y = np.sin(ph + idx * np.sin(ph)) + 0.08 * np.sin(2 * ph + 0.6 * np.exp(-t / 0.08) * np.sin(2 * ph))
    env = np.minimum(1, t / 0.004) * np.exp(-t / (1.6 if m < 72 else 1.0))
    off = np.clip((t - dur) / 0.25, 0, 1)
    y = y * env * (1 - off)
    return _va.juno_chorus(np.vstack([y, y]) * 0.4, 1, 0.3)


def v_humchoir(m, dur, p, glide=None, mod=None):
    """Hum choir: a soft 'ooh' sung on closed lips - harmonics shaped like the vowel u (strong fundamental, a gentle
    hump near 300 Hz) with three voices a few cents apart and a slow swell."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.45, 1.0, 1.0, 1.0)
    rng = _rng()
    amps = [1.0 / (1 + ((k + 1) * f / 330.0 - 1) ** 2 * 2) for k in range(8)]
    out = np.zeros((2, n))
    for i, c in enumerate((-7, 0, 6)):
        fr = f * 2 ** (c / 1200) * _wow(t, rng, 4, 0.4 + 0.2 * i)
        out[i % 2] += _sine_stack(fr, n, amps, rng) * (0.7 if c else 0.5)
    out[1] += out[0] * 0.3
    return lp(out, 2500) * env * 0.22


def v_dustpiano(m, dur, p, glide=None, mod=None):
    """Dust piano: a felt piano heard from an old cassette - the top rolled off, a slow wow, a little hiss - the
    sampled-keys sound of lo-fi and chill beats."""
    y = np.asarray(INSTRUMENTS['piano'](m, dur, p, glide, mod), float)
    y = y if y.ndim == 2 else np.vstack([y, y])
    n = y.shape[1]
    t = np.arange(n) / SR
    rng = _rng()
    idx = np.clip(np.arange(n) + 0.0009 * SR * np.sin(2 * np.pi * 0.5 * t + rng.random() * 6), 0, n - 1)   # wow of ~+/-5 cents
    y = np.vstack([np.interp(idx, np.arange(n), y[0]), np.interp(idx, np.arange(n), y[1])])
    return lp(y, 2600) * 1.1 + 0.002 * hp(rng.standard_normal((2, n)), 3000)


def v_bloomlead(m, dur, p, glide=None, mod=None):
    """Bloom lead: a sine voice that swells in slowly, with an octave-up halo fading in behind it and a slide from the
    last note - a soft, glowing top line."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.22, 0.5, 1.0, 0.9)
    rng = _rng()
    fr = _glide_freq(f, n, glide, 0.14) * _wow(t, rng, 8, 0.5)
    halo = np.clip(t / 1.2, 0, 1) * 0.22
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph) + 0.06 * np.sin(2 * ph) + halo * np.sin(2 * ph + 0.3)
    return _ms_stereo(y * env, 300) * 0.45


def v_tapebell(m, dur, p, glide=None, mod=None):
    """Tape bell: a round sine bell (fundamental, octave and twelfth only - always in key) with a gentle tape wobble
    and a long, soft ring."""
    f = float(mtof(m))
    n = int((min(dur, 1.5) + 1.5) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    fr = f * _wow(t, rng, 5, 0.7)
    y = _sine_stack(fr, n, (1.0, 0.3, 0.12), rng)
    y = y * np.minimum(1, t / 0.003) * np.exp(-t / 0.9)
    return _ms_stereo(y, 260) * 0.35


# --- house / techno
def v_chordmemory(m, dur, p, glide=None, mod=None):
    """Chord-memory stab: a saw-and-square poly stab stacked in octaves (the song's own chord voicing supplies the
    harmony, so it stays in key on every note) with a snappy filter - the deep-house / garage stab sound."""
    f = float(mtof(m))
    env, n, t = _env_n(min(dur, 0.6), 0.003, 0.25, 0.25, 0.25)
    rng = _rng()
    x = np.zeros((2, n))
    for k, r in enumerate((1.0, 2.0, 1.0)):
        x[k % 2] += _va.saw(f * r * 2 ** ((k - 1) * 5 / 1200), n, rng.random()) * 0.4
        x[(k + 1) % 2] += _va.pulse(f * r, n, rng.random(), 0.4) * 0.2
    cut = 600 + 3800 * np.exp(-t / 0.09)
    return _hpf(_va.vcf(x, cut, 0.3, 1.1), 150) * env * 0.5


def v_deepfmbass(m, dur, p, glide=None, mod=None):
    """Deep FM bass: a round, plucky 1:1 FM bass whose brightness falls fast - the bouncing low end of deep and
    tech house (sine body, no buzz)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.3, 0.55, 0.12)
    ph = 2 * np.pi * f * t
    y = np.sin(ph + 2.2 * np.exp(-t / 0.06) * np.sin(ph)) + 0.15 * np.sin(2 * ph)
    return np.vstack([y, y]) * env * 0.6


def v_discofilter(m, dur, p, glide=None, mod=None):
    """Filtered disco chord: a string-machine chord tone pushed through a slowly sweeping low-pass and a phaser - the
    filtered-disco sound of French house and nu-disco."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.04, 0.3, 0.9, 0.35)
    rng = _rng()
    x = _stack_saw(np.full(n, f), n, (-7, 0, 7), rng, 0.6)
    cut = 900 + 1800 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t + rng.random() * 6))
    y = _va.vcf(x, cut, 0.35, 1.1)
    ph = 0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t)
    d = (10 + 30 * ph).astype(int)
    idx = np.clip(np.arange(n) - d, 0, n - 1)
    y = 0.65 * y + 0.35 * y[:, idx]
    return _hpf(y, 180) * env * 0.42


def v_fmbleep(m, dur, p, glide=None, mod=None):
    """FM bleep: a short, clean 2:1 FM blip - the bleeps of techno, minimal and electro sequences."""
    f = float(mtof(m))
    n = int((min(dur, 0.25) + 0.08) * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    y = np.sin(ph + 1.5 * np.exp(-t / 0.03) * np.sin(2 * ph)) * np.exp(-t / 0.07) * np.minimum(1, t / 0.002)
    return np.vstack([y, y]) * 0.45


def v_pingchord(m, dur, p, glide=None, mod=None):
    """Ping chord: a short, resonant filtered hit (root and octaves - the chord comes from the voicing) with a fast-closing filter - the dub-
    techno / minimal ping, made to be fed into a long echo."""
    f = float(mtof(m))
    env, n, t = _env_n(min(dur, 0.3), 0.002, 0.15, 0.0, 0.2)
    rng = _rng()
    x = sum(_va.saw(f * r, n, rng.random()) for r in (1.0, 2.0, 4.0)) / 3
    y = _va.vcf(np.vstack([x, x]), 400 + 2200 * np.exp(-t / 0.05), 0.3, 1.0)
    return _hpf(y, 200) * env * 0.6


# --- drum & bass / jungle
def v_junglesub(m, dur, p, glide=None, mod=None):
    """Jungle sub: a pure sine sub that drops a little in pitch at the start of each note (in tune once it settles) -
    the rolling sub of jungle and liquid."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.005, 0.3, 0.9, 0.08)
    fr = f * 2 ** (3 * np.exp(-t / 0.03) / 12)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph) + 0.05 * np.sin(2 * ph)
    return np.vstack([y, y]) * env * 0.7


def v_atmosbell(m, dur, p, glide=None, mod=None):
    """Atmos bell: a soft harmonic bell with a long shimmering tail (octave halo) - the floating bells of liquid
    drum & bass and atmospheric jungle."""
    f = float(mtof(m))
    n = int((min(dur, 2.0) + 2.5) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    y = _sine_stack(np.full(n, f), n, (1.0, 0.35, 0.0, 0.15), rng) * np.exp(-t / 1.4)
    y += 0.25 * np.sin(4 * np.pi * f * t + 1) * np.clip(t / 0.8, 0, 1) * np.exp(-t / 2.2)
    y *= np.minimum(1, t / 0.004)
    return _ms_stereo(y, 340) * 0.32


# --- hip-hop / trap / drill
def v_choirstab(m, dur, p, glide=None, mod=None):
    """Choir stab: a dark, dramatic 'ah' choir hit - harmonics shaped like the vowel a, a few voices, a quick swell and
    a cut-off tail - the choir stabs of drill and dark trap."""
    f = float(mtof(m))
    env, n, t = _env_n(min(dur, 1.2), 0.02, 0.3, 0.7, 0.3)
    rng = _rng()
    amps = [1.0 / (1 + ((k + 1) * f / 750.0 - 1) ** 2 * 3) + (0.5 if k == 0 else 0) for k in range(14)]
    out = np.zeros((2, n))
    for i, c in enumerate((-9, -3, 4, 10)):
        out[i % 2] += _sine_stack(f * 2 ** (c / 1200) * np.ones(n), n, amps, rng) * 0.35
    return _hpf(lp(out, 4000), 150) * env * 0.3


def v_darkbell(m, dur, p, glide=None, mod=None):
    """Dark bell: a low, round bell (fundamental and octave, a soft twelfth) with a quick attack and a medium ring -
    the haunting melodies of trap and drill (in tune on every note)."""
    f = float(mtof(m))
    n = int((min(dur, 1.2) + 1.0) * SR)
    t = np.arange(n) / SR
    y = _sine_stack(np.full(n, f), n, (1.0, 0.45, 0.18), _rng()) * np.exp(-t / 0.7) * np.minimum(1, t / 0.002)
    return _ms_stereo(lp(y, 3000), 200) * 0.4


# --- pop / r&b / afro / latin
def v_pluckvox(m, dur, p, glide=None, mod=None):
    """Vocal pluck: a short sung 'ah' cut into a pluck - the vocal-chop leads of pop, future bass and afro house."""
    f = float(mtof(m))
    env, n, t = _env_n(min(dur, 0.4), 0.004, 0.18, 0.2, 0.15)
    rng = _rng()
    x = _stack_saw(np.full(n, f), n, (-6, 6), rng, 0.6)
    y = np.vstack([_va.formant(x[i], 'a', 7.0) for i in range(2)])
    return _hpf(y, 200) * env * 0.9


def v_afropluck(m, dur, p, glide=None, mod=None):
    """Wood pluck: a short, woody harmonic pluck (fundamental, octave, a soft click) - the marimba-like synth plucks
    of afro house, amapiano and afrobeats."""
    f = float(mtof(m))
    n = int((min(dur, 0.6) + 0.3) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    y = _sine_stack(np.full(n, f), n, (1.0, 0.4, 0.1, 0.12), rng) * np.exp(-t / 0.18)
    y += 0.2 * lp(rng.standard_normal(n), 3000) * np.exp(-t / 0.004)
    return _ms_stereo(y * np.minimum(1, t / 0.001), 120) * 0.45


def v_dembowlead(m, dur, p, glide=None, mod=None):
    """Dembow lead: a bright, plucky square-and-saw lead with a quick slide from the last note - the catchy synth
    hooks of reggaeton and latin trap."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.2, 0.6, 0.15)
    rng = _rng()
    fr = _glide_freq(f, n, glide, 0.04)
    x = _va.pulse(fr, n, rng.random(), 0.45) * 0.5 + _va.saw(fr * 2 ** (6 / 1200), n, rng.random()) * 0.4
    y = _va.vcf(np.vstack([x, x]), 1500 + 3000 * np.exp(-t / 0.12), 0.2, 1.2)
    return _hpf(_va.juno_chorus(y, 1, 0.3), 180) * env * 0.4


# --- retro / synthwave / hauntology
def v_dxepiano(m, dur, p, glide=None, mod=None):
    """DX electric piano: the glassy 80s FM electric piano - a 1:1 body with a bright 14:1 tine on the attack (both
    harmonic), chorused - the ballad keys of synthwave, 80s pop and city pop."""
    f = float(mtof(m))
    n = int((min(dur, 3.0) + 1.0) * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    body = np.sin(ph + 0.9 * np.exp(-t / 0.6) * np.sin(ph))
    tine = 0.25 * np.sin(14 * ph) * np.exp(-t / 0.02)
    y = (body + tine) * np.minimum(1, t / 0.002) * np.exp(-t / 1.4) * (1 - np.clip((t - dur) / 0.2, 0, 1))
    return _va.juno_chorus(np.vstack([y, y]) * 0.4, 2, 0.4)


def v_arpsquare(m, dur, p, glide=None, mod=None):
    """Square arp: a hollow pulse-wave arp note with a little PWM and a quick filter blip - the bouncing arpeggios of
    synthwave, italo and retro games."""
    f = float(mtof(m))
    env, n, t = _env_n(min(dur, 0.35), 0.002, 0.12, 0.3, 0.1)
    rng = _rng()
    pw = 0.35 + 0.1 * np.sin(2 * np.pi * 3 * t)
    x = _va.pulse(f, n, rng.random(), float(np.mean(pw)))
    y = _va.vcf(np.vstack([x, x]), 1200 + 3500 * np.exp(-t / 0.05), 0.25, 1.1)
    return _hpf(y, 150) * env * 0.4


def v_shortwave(m, dur, p, glide=None, mod=None):
    """Shortwave tone: a pure tone heard over an old radio - band-limited, wavering slightly (but centred on the note),
    with faint static - the eerie broadcast melodies of hauntology."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.06, 0.4, 0.9, 0.4)
    rng = _rng()
    fr = f * _wow(t, rng, 9, 0.9)
    y = _sine_stack(fr, n, (1.0, 0.25, 0.12), rng)
    y = lp(hp(y, 300), 2800) + 0.02 * lp(hp(rng.standard_normal(n), 1500), 4000)
    return np.vstack([y, y]) * env * 0.45


def v_tapeorgan(m, dur, p, glide=None, mod=None):
    """Tape organ: a soft combo organ (drawbar-style harmonics 1, 2, 3, 4) on a wobbly old tape - warm, slightly sad
    chords for hauntology and lo-fi."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.02, 0.2, 1.0, 0.15)
    rng = _rng()
    fr = f * _wow(t, rng, 7, 0.55)
    y = _sine_stack(fr, n, (1.0, 0.6, 0.35, 0.25, 0.0, 0.12), rng)
    return _ms_stereo(lp(y, 3000) * env, 220) * 0.3


NEW_192 = (
    ('tapeflute', v_tapeflute, 'Tape flute (breathy, wobbly, sliding)', ('lead',), 73),
    ('glasskeys', v_glasskeys, 'Glass keys (soft sine electric piano)', ('chords', 'arp'), 4),
    ('humchoir', v_humchoir, 'Hum choir (soft closed-lip ooh)', ('pad', 'chords'), 52),
    ('dustpiano', v_dustpiano, 'Dust piano (felt piano on cassette)', ('chords', 'arp'), 0),
    ('bloomlead', v_bloomlead, 'Bloom lead (swelling sine with octave halo)', ('lead',), 80),
    ('tapebell', v_tapebell, 'Tape bell (round sine bell, wobbly)', ('arp', 'lead'), 14),
    ('chordmemory', v_chordmemory, 'Chord-memory stab (deep house / garage, octaves)', ('chords',), 81),
    ('deepfmbass', v_deepfmbass, 'Deep FM bass (round pluck)', ('bass',), 38),
    ('discofilter', v_discofilter, 'Filtered disco chord (sweeping, phased)', ('chords', 'pad'), 50),
    ('fmbleep', v_fmbleep, 'FM bleep (techno blip)', ('arp', 'lead'), 80),
    ('pingchord', v_pingchord, 'Ping chord (dub techno, for echoes)', ('chords',), 81),
    ('junglesub', v_junglesub, 'Jungle sub (sine with a pitch drop)', ('bass',), 38),
    ('atmosbell', v_atmosbell, 'Atmos bell (liquid DnB, long shimmer)', ('arp', 'pad', 'lead'), 14),
    ('choirstab', v_choirstab, 'Choir stab (dark ah hit)', ('chords', 'lead'), 52),
    ('darkbell', v_darkbell, 'Dark bell (trap / drill melody)', ('lead', 'arp'), 14),
    ('pluckvox', v_pluckvox, 'Vocal pluck (short sung ah)', ('lead', 'arp'), 54),
    ('afropluck', v_afropluck, 'Wood pluck (afro house / amapiano)', ('arp', 'lead'), 12),
    ('dembowlead', v_dembowlead, 'Dembow lead (reggaeton hook)', ('lead',), 80),
    ('dxepiano', v_dxepiano, 'DX electric piano (80s FM keys)', ('chords', 'arp'), 5),
    ('arpsquare', v_arpsquare, 'Square arp (bouncing pulse wave)', ('arp',), 80),
    ('shortwave', v_shortwave, 'Shortwave tone (radio melody)', ('lead',), 79),
    ('tapeorgan', v_tapeorgan, 'Tape organ (wobbly combo organ)', ('chords', 'pad'), 16),
)
for _name, _fn, _info, _roles, _gm in NEW_192:
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# ----------------------------------------------------------------------------- 1.92: variations of popular sounds
# Slight variations of the sounds genres use most, built only from changes that keep a note in tune: a darker or
# brighter filter, a softer attack, a chorus double a few cents either side, an octave layer, a gentle tape wobble
# (+/- 5 cents), a little drive. Each keeps its base sound's roles.
def _fit(y, n):
    y = np.asarray(y, float)
    y = y if y.ndim == 2 else np.vstack([y, y])
    return y[:, :n] if y.shape[1] >= n else np.pad(y, ((0, 0), (0, n - y.shape[1])))


def _variant(base, kind):
    fn = INSTRUMENTS[base]

    def v(m, dur, p, glide=None, mod=None):
        y = np.asarray(fn(m, dur, p, glide, mod), float)
        y = y if y.ndim == 2 else np.vstack([y, y])
        n = y.shape[1]
        if kind == 'dark':
            return lp(y, 2200) * 1.2
        if kind == 'bright':
            return y + 0.35 * hp(y, 3500)
        if kind == 'soft':
            a = min(n, int(0.05 * SR))
            y = y.copy()
            y[:, :a] *= np.linspace(0, 1, a) ** 1.5
            return lp(y, 5000)
        if kind == 'wide':                               # a chorus double 6 cents either side, one per side
            g = None if glide is None else glide + 0.06
            up = _fit(fn(m + 0.06, dur, p, g, mod), n)
            g = None if glide is None else glide - 0.06
            dn = _fit(fn(m - 0.06, dur, p, g, mod), n)
            return np.vstack([0.6 * y[0] + 0.55 * up[0], 0.6 * y[1] + 0.55 * dn[1]])
        if kind == 'octave':                             # an octave above, quieter
            hi = _fit(fn(m + 12, dur, p, None if glide is None else glide + 12, mod), n)
            return y + 0.35 * hi
        if kind == 'suboct':                             # an octave below, for weight
            if float(mtof(m - 12)) < 30:                 # (1.96) below 30 Hz it is felt as headroom eaten, not heard
                return y
            lo = _fit(fn(m - 12, dur, p, None if glide is None else glide - 12, mod), n)
            return (y + 0.45 * lp(lo, 900)) * 0.8
        if kind == 'tape':                               # +/- 5 cents of slow wow, softened top
            t = np.arange(n) / SR
            idx = np.clip(np.arange(n) + 0.0009 * SR * np.sin(2 * np.pi * 0.55 * t + 1.3), 0, n - 1)
            y = np.vstack([np.interp(idx, np.arange(n), y[0]), np.interp(idx, np.arange(n), y[1])])
            return lp(y, 6500)
        if kind == 'driven':
            return np.tanh(y * 2.2) / np.tanh(2.2) * 0.8
        return y
    return v


VARIANT_NAMES = {'dark': 'darker', 'bright': 'brighter', 'soft': 'soft attack', 'wide': 'wide chorus',
                 'octave': 'with octave', 'suboct': 'with sub-octave', 'tape': 'tape wobble', 'driven': 'driven'}
POPULAR_VARIANTS = {
    # pads / chords
    'supersaw': ('dark', 'wide', 'octave'), 'warmpad': ('wide', 'tape'), 'junopad': ('dark', 'wide'),
    'jupiterpad': ('dark', 'tape'), 'polysynth': ('soft', 'wide', 'tape'), 'strings': ('dark', 'wide'),
    'solina': ('wide', 'tape'), 'glasspad': ('dark', 'wide'), 'lushpad': ('dark', 'tape'), 'dreampad': ('dark', 'octave'),
    'trancepad': ('dark', 'wide'), 'vocalpad': ('dark', 'wide'), 'choir': ('dark', 'wide'), 'darkpad': ('wide', 'tape'),
    # keys / plucks
    'epiano': ('tape', 'bright', 'dark'), 'rhodes': ('tape', 'dark', 'wide'), 'wurli': ('tape', 'dark'),
    'piano': ('dark', 'tape'), 'organ': ('dark', 'driven'), 'pluck': ('dark', 'wide', 'octave'),
    'pluck_saw': ('dark', 'wide'), 'trancepluck': ('dark', 'wide', 'octave'), 'superpluck': ('dark', 'wide'),
    'mhpluck': ('wide', 'tape'), 'marimba': ('tape', 'octave'), 'kalimba': ('tape', 'octave'), 'bell': ('dark', 'tape'),
    'lofikeys': ('dark', 'wide'), 'm1piano': ('dark', 'wide'), 'stab': ('dark', 'wide'), 'housechord': ('dark', 'wide'),
    # leads
    'leadsaw': ('soft', 'octave', 'wide'), 'supersaw_lead': ('dark', 'octave'), 'softlead': ('octave', 'wide'),
    'analoglead': ('soft', 'octave'), 'moog_lead': ('soft', 'octave'), 'synthwavelead': ('soft', 'wide'),
    'sh101': ('dark', 'driven'), 'acid': ('dark', 'driven'), 'hoover': ('dark',), 'sinelead': ('octave', 'tape'),
    'trancebell': ('dark', 'octave'), 'brass': ('dark', 'wide'), 'synthbrass': ('dark', 'wide'), 'flute': ('tape', 'soft'),
    # basses
    'reese': ('dark', 'driven'), 'sawbass': ('dark', 'driven'), 'sinebass': ('driven', 'suboct'),
    'moogbass': ('dark', 'driven'), 'deepbass': ('dark', 'driven'), 'wobble': ('dark', 'driven'), 'growl': ('dark',),
    'fmbass': ('dark', 'driven'), 'junobass': ('dark', 'driven'), 'ebass': ('dark', 'driven'), '808': ('driven', 'dark'),
}
VARIANT_OF = {}
for _base, _kinds in POPULAR_VARIANTS.items():
    if _base not in INSTRUMENTS:
        continue
    for _k in _kinds:
        _name = f'{_base}_{_k}'
        if _name in INSTRUMENTS:
            continue
        INSTRUMENTS[_name] = _variant(_base, _k)
        INSTRUMENT_INFO[_name] = f"{INSTRUMENT_INFO.get(_base, _base)} - {VARIANT_NAMES[_k]}"
        GM_PROGRAM[_name] = GM_PROGRAM.get(_base, 80)
        VARIANT_OF[_name] = _base
        for _role, _lst in ROLE_CHOICES.items():
            if _base in _lst and _name not in _lst:
                _lst.append(_name)


# ----------------------------------------------------------------------------- 1.93: house / trance / techno bank
# (harmonic partials, octave-only stacks and pitch moves that settle on the note: always in key)
def v_rubberbass(m, dur, p, glide=None, mod=None):
    """Rubber bass: a bouncy, elastic FM bass - each note starts a little sharp and dips onto the pitch in 40 ms, with
    a quick 'boing' of brightness - the rubbery low end of tech house."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.003, 0.18, 0.6, 0.08)
    fr = f * 2 ** (2.5 * np.exp(-t / 0.04) / 12)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph + 1.8 * np.exp(-t / 0.05) * np.sin(ph)) + 0.12 * np.sin(2 * ph)
    return np.vstack([y, y]) * env * 0.62


def v_rhodestrem(m, dur, p, glide=None, mod=None):
    """Tremolo keys: an electric piano with the stereo tremolo on - the sound pulsing between the speakers in time with
    the beat (an 8th-note tremolo) - deep-house chords."""
    y = np.asarray(INSTRUMENTS['rhodes'](m, dur, p, glide, mod), float)
    y = y if y.ndim == 2 else np.vstack([y, y])
    n = y.shape[1]
    t = np.arange(n) / SR
    rate = 2.0 / float(p.get('spb', 0.48))
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t)
    return np.vstack([y[0] * (0.55 + 0.45 * lfo), y[1] * (0.55 + 0.45 * (1 - lfo))]) * 1.05


def v_discohorn(m, dur, p, glide=None, mod=None):
    """Disco horn stab: a punchy brass-section hit - bright saws with a quick 'blat' of filter, a small scoop up into
    the note (settling on pitch) and a short fall-off - for funky and disco house."""
    f = float(mtof(m))
    env, n, t = _env_n(min(dur, 0.5), 0.008, 0.15, 0.55, 0.12)
    rng = _rng()
    fr = f * 2 ** (-0.6 * np.exp(-t / 0.03) / 12)
    x = _stack_saw(fr, n, (-8, 0, 7), rng, 0.6)
    y = _va.vcf(x, 900 + 4200 * np.exp(-t / 0.07), 0.2, 1.4)
    return _hpf(y, 160) * env * 0.5


def v_vocalbounce(m, dur, p, glide=None, mod=None):
    """Vocal bounce: a short sung 'oh-ah' whose vowel opens with the note - the bouncing filtered vocal chops of
    house."""
    f = float(mtof(m))
    env, n, t = _env_n(min(dur, 0.45), 0.006, 0.2, 0.35, 0.1)
    rng = _rng()
    x = _stack_saw(np.full(n, f), n, (-5, 5), rng, 0.5)
    a = np.vstack([_va.formant(x[i], 'o', 7.0) for i in range(2)])
    b = np.vstack([_va.formant(x[i], 'a', 7.0) for i in range(2)])
    k = np.clip(t / 0.12, 0, 1)[None, :]
    return _hpf(a * (1 - k) + b * k, 220) * env * 0.85


def v_vowelpad(m, dur, p, glide=None, mod=None):
    """Vowel-morph pad: a choir pad that slowly moves from 'aah' to 'ooh' (over about eight seconds) - the breathing
    vocal pads of trance breakdowns."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.6, 1.0, 1.0, 1.6)
    rng = _rng()
    x = _stack_saw(np.full(n, f), n, (-9, -3, 4, 10), rng, 0.8)
    a = np.vstack([_va.formant(x[i], 'a', 6.0) for i in range(2)])
    u = np.vstack([_va.formant(x[i], 'u', 6.0) for i in range(2)])
    k = (0.5 - 0.5 * np.cos(np.pi * np.clip(t / 8.0, 0, 1)))[None, :]
    return _hpf(a * (1 - k) + u * k * 1.2, 150) * env * 0.5


def v_sawharp(m, dur, p, glide=None, mod=None):
    """Saw harp: a bright plucked saw that rings out like a harp string (the filter closing slowly) - the shimmering
    arpeggios of trance breakdowns."""
    f = float(mtof(m))
    n = int((min(dur, 1.5) + 1.2) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    x = _stack_saw(np.full(n, f), n, (-6, 6), rng, 0.6)
    y = _va.vcf(x, 500 + 5500 * np.exp(-t / 0.35), 0.15, 1.1)
    return _hpf(y, 180) * (np.minimum(1, t / 0.002) * np.exp(-t / 0.9))[None, :] * 0.45


def v_risinglead(m, dur, p, glide=None, mod=None):
    """Rising unison lead: a big supersaw lead whose detune and brightness swell while the note is held - the uplifting
    trance 'lift' on long notes."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.01, 0.3, 0.95, 0.4)
    rng = _rng()
    sw = np.clip(t / max(0.4, min(dur, 3.0)), 0, 1)
    fr = _glide_freq(f, n, glide, 0.06)
    x = np.zeros((2, n))
    for k, c in enumerate((-14, -8, -3, 0, 3, 8, 14)):
        x[k % 2] += _va.saw(fr * 2 ** (c * (0.4 + 0.6 * sw) / 1200), n, rng.random()) * 0.3
    y = _va.vcf(x, 1800 + 6000 * sw, 0.15, 1.15)
    return _hpf(y, 200) * env * 0.42


def v_warehousestab(m, dur, p, glide=None, mod=None):
    """Warehouse stab: a dark, resonant hit (root and octave) thrown into a big concrete room - a short stab with a
    long, gritty reverb tail - for techno."""
    f = float(mtof(m))
    n = int((min(dur, 0.3) + 2.2) * SR)
    t = np.arange(n) / SR
    rng = _rng()
    x = (_va.saw(f, n, rng.random()) + 0.6 * _va.saw(2 * f, n, rng.random())) * np.exp(-t / 0.09)
    y = _va.vcf(np.vstack([x, x]), 500 + 2000 * np.exp(-t / 0.05), 0.2, 1.4)
    from .dsp import make_ir, reverb
    y = y * 0.7 + reverb(y.astype(np.float32), make_ir(2.0, 0.02, 0.6)) * 0.5
    return _hpf(y, 140) * 0.55


def v_fmacid(m, dur, p, glide=None, mod=None):
    """FM acid: a 303-style line with an FM growl in it - the resonant squelch plus a 2:1 FM bite that opens on
    accents - harder than the classic acid."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.15, 0.6, 0.05)
    rng = _rng()
    fr = _glide_freq(f, n, glide, 0.04)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    acc = 1.5 if mod == 'acc' else 1.0
    x = _va.saw(fr, n, rng.random()) * 0.7 + 0.5 * np.sin(ph + acc * 1.6 * np.exp(-t / 0.08) * np.sin(2 * ph))
    y = _va.vcf(np.vstack([x, x]), 300 + 2600 * acc * np.exp(-t / 0.1), 0.72, 1.5)
    return _hpf(np.tanh(y * 1.6), 60) * env * 0.4


def v_tonalbass(m, dur, p, glide=None, mod=None):
    """Tonal kick-bass: a deep, rumbling sine bass with a soft saturated edge, tuned to the note - the pitched low end
    that hard and Berlin-style techno run under the kick."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.25, 0.75, 0.1)
    ph = 2 * np.pi * f * t
    y = np.tanh((np.sin(ph) + 0.25 * np.sin(2 * ph)) * 1.8) * 0.8
    return np.vstack([y, y]) * env * 0.65


NEW_193 = (
    ('rubberbass', v_rubberbass, 'Rubber bass (bouncy tech-house FM)', ('bass',), 38),
    ('rhodestrem', v_rhodestrem, 'Tremolo keys (pulsing electric piano)', ('chords', 'arp'), 4),
    ('discohorn', v_discohorn, 'Disco horn stab (punchy brass hit)', ('chords', 'lead'), 61),
    ('vocalbounce', v_vocalbounce, 'Vocal bounce (oh-ah house chop)', ('lead', 'arp'), 54),
    ('vowelpad', v_vowelpad, 'Vowel-morph pad (aah to ooh)', ('pad', 'chords'), 52),
    ('sawharp', v_sawharp, 'Saw harp (ringing plucked saw)', ('arp', 'lead'), 46),
    ('risinglead', v_risinglead, 'Rising unison lead (swells as it holds)', ('lead',), 81),
    ('warehousestab', v_warehousestab, 'Warehouse stab (dark hit, big room)', ('chords', 'arp'), 81),
    ('fmacid', v_fmacid, 'FM acid (303 squelch with FM bite)', ('bass', 'arp', 'lead'), 87),
    ('tonalbass', v_tonalbass, 'Tonal kick-bass (rumbling techno low end)', ('bass',), 38),
)
for _name, _fn, _info, _roles, _gm in NEW_193:
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# 1.96: modern takes on the 60s monster-theme band (a fuzz baritone synth for the creeping riff, a driven detuned
# combo organ) - harmonic partials only, so everything stays in key.
def v_fuzzbari(m, dur, p, glide=None, mod=None):
    """Fuzz baritone synth: the twangy baritone-guitar riff rebuilt as a synth - a bright saw + square pair with a
    quick pluck of filter, pushed through fuzz and a low-mid honk, then a short spring-like slap - the creeping
    chromatic monster riff with modern weight."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.002, 0.25, 0.55, 0.09)
    fr = _glide_freq(f, n, glide, 0.03)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    k = np.arange(1, 16)[:, None]
    cut = 900 + 3800 * np.exp(-t / 0.07)
    amp = np.exp(-((k * fr[None, :]) / cut[None, :]) ** 2)
    sawp = (np.sin(k * ph[None, :]) / k * amp).sum(0)
    sq = (np.sin(k[::2] * ph[None, :]) / k[::2] * amp[::2]).sum(0)
    y = np.tanh(2.6 * (0.7 * sawp + 0.45 * sq)) * env
    y = eq(eq(y, 'peak', 700, 0.9, 4.0), 'peak', 2600, 1.2, 2.0)
    d = int(0.021 * SR)
    sl = np.concatenate([np.zeros(d), y[:-d]]) * 0.22
    return np.vstack([y + sl, y + 0.8 * sl]) * 0.42


def v_creeporgan(m, dur, p, glide=None, mod=None):
    """Creep organ: a modern haunted combo organ - bright upper drawbars on two slightly detuned voices (a chorus, a
    few cents apart), a fast vibrato, a little valve drive and a key click - the reedy horror organ with width."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.006, 0.05, 0.95, 0.07)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 6.6 * t)
    bars = ((1, 0.8), (2, 0.9), (3, 0.5), (4, 0.65), (6, 0.3), (8, 0.4))
    out = []
    for cents, pan in ((-5, 0), (5, 1)):
        ph = 2 * np.pi * np.cumsum(f * 2 ** (cents / 1200) * vib) / SR
        out.append(sum(a * np.sin(h * ph) for h, a in bars))
    click = np.exp(-t / 0.004) * np.sin(2 * np.pi * f * 8 * t) * 0.25
    y = np.vstack([np.tanh(1.5 * (o + click)) for o in out]) * env
    return y * 0.32


NEW_196 = (
    ('fuzzbari', v_fuzzbari, 'Fuzz baritone synth (creeping monster riff)', ('bass', 'lead', 'arp'), 30),
    ('creeporgan', v_creeporgan, 'Creep organ (modern haunted combo organ)', ('chords', 'pad', 'arp', 'lead'), 18),
)
for _name, _fn, _info, _roles, _gm in NEW_196:
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# =============================================================================
#  1.96: sunlit electronica sounds (analog-warm downtempo / electronic post-rock)
#  Harmonic partials only (everything in key); detune is a few cents of chorus, never a pitch offset.
# =============================================================================
def v_spaceguitar(m, dur, p, glide=None, mod=None):
    """Space guitar: a clean neck-pickup guitar note run into a huge hall until it stops being a pluck and becomes a
    pad - the string's soft attack, then its harmonics (warm, few highs) frozen into a slow-swelling, chorused
    sustain that blooms and fades like a reverb tail. Effects as the instrument: the guitar IS the pad."""
    f = float(mtof(m))
    gate = int(max(dur, 0.25) * SR)
    rel = p.get('r', 1.4)
    n = gate + int(rel * SR)
    t = np.arange(n) / SR
    swell = np.clip(t / p.get('a', 0.45), 0, 1) ** 1.5
    tail = np.where(np.arange(n) < gate, 1.0, np.exp(-(np.arange(n) - gate) / (rel * SR / 4)))
    tail[-int(0.04 * SR):] *= np.linspace(1, 0, int(0.04 * SR))
    out = np.zeros((2, n))
    nh = int(min(12, max(3, 5000 // f)))
    for side, cents in ((0, -4.0), (1, 4.0)):
        y = np.zeros(n)
        for k in range(1, nh + 1):
            a = (1.0 / k ** 1.35) * (1.0 if k < 4 else 0.6) * np.exp(-k * f / 2600)
            sh = 1 + 0.12 * np.sin(2 * np.pi * (0.13 + 0.05 * k) * t + k * 1.7 + side)    # slow shimmer per partial
            y += a * sh * np.sin(2 * np.pi * k * f * 2 ** (cents / 1200) * t + k * 0.9 * (side + 1))
        out[side] = y
    out *= swell * tail
    pick = np.asarray(v_eguitar_clean(m, min(dur, 0.5), dict(p, dist=0.0), None, None), float)    # the faint pluck
    pick = pick if pick.ndim == 2 else np.vstack([pick, pick])
    k = min(n, pick.shape[1])
    out[:, :k] += 0.35 * pick[:, :k] / (np.abs(pick).max() + 1e-9) * np.max(np.abs(out) + 1e-9) * 0.5
    return out / (np.abs(out).max() + 1e-9) * 0.3


def v_sunpad(m, dur, p, glide=None, mod=None):
    """Sun pad: a warm analog poly pad - three saws a few cents apart and a triangle an octave down through a
    gently driven ladder low-pass that slowly opens as the chord blooms (slow attack, long release); soft, dense and
    rounded, made to sit under guitars."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = _va.adsr(gate, p.get('a', 0.35), 0.8, 0.85, p.get('r', 0.9))
    n = len(env)
    t = np.arange(n) / SR
    drift = 1 + 0.0009 * np.sin(2 * np.pi * 0.31 * t + m)
    out = np.zeros((2, n))
    for side in (0, 1):
        x = np.zeros(n)
        for c, ph in ((-7, 0.1), (0, 0.5), (7, 0.8)):
            x += _va.saw(f * 2 ** ((c + (3 if side else -3)) / 1200) * drift, n, ph)
        x += 0.6 * (2 * np.abs(2 * ((np.cumsum(np.full(n, f / 2)) / SR) % 1.0) - 1) - 1)
        cut = p.get('cut', 1500) * (0.45 + 0.55 * (1 - np.exp(-t / 0.9)))
        out[side] = _va.vcf(x * 0.25, cut, res=0.12, drive=1.3)
    return out * env * 0.42


def v_softmoog(m, dur, p, glide=None, mod=None):
    """Soft mono lead: a warm 3-oscillator mono synth played gently - saw and triangle a hair apart through a ladder
    low-pass with a soft filter swell, a smooth portamento from the last note, slow drift and a vibrato that only
    comes in on held notes - the understated, singing analog melody."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, p.get('a', 0.03), 0.35, 0.8, p.get('r', 0.35))
    fr = _glide_freq(f, n, glide, 0.07)
    vib = 1 + np.clip((t - 0.35) / 0.4, 0, 1) * 0.0035 * np.sin(2 * np.pi * 5.2 * t)
    fr = fr * vib * (1 + 0.0007 * np.sin(2 * np.pi * 0.4 * t))
    x = _va.saw(fr, n, 0.0) + 0.8 * (2 * np.abs(2 * ((np.cumsum(fr * 1.0015) / SR) % 1.0) - 1) - 1)
    cut = p.get('cut', 1800) * (0.6 + 0.6 * np.exp(-t / 0.25)) + 2.5 * f
    y = _va.vcf(x * 0.35, cut, res=0.18, drive=1.4)
    return _st(y * env, 18) * 0.5


def v_roundmoog(m, dur, p, glide=None, mod=None):
    """Round mono bass: the classic 3-oscillator analog bass played warm - saw and square through a ladder low-pass
    with a short, soft filter 'bow', a gently driven input; weight in the low mids rather than a deep sub, so it
    sounds full on small speakers (the warm bass under sunlit electronica)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.006, 0.25, 0.75, p.get('r', 0.12))
    fr = _glide_freq(f, n, glide, 0.04)
    x = _va.saw(fr, n, 0.0) + 0.7 * _va.pulse(fr * 0.999, n, 0.3, 0.5)
    cut = p.get('cut', 420) + 900 * np.exp(-t / 0.12) + 1.5 * f
    y = _va.vcf(x * 0.4, cut, res=0.15, drive=1.6)
    y = y + p.get('fund', 0.7) * np.sin(2 * np.pi * np.cumsum(fr) / SR)   # a pure fundamental under it (the weight)
    return np.vstack([y, y]) * env * 0.55


NEW_196B = (
    ('spaceguitar', v_spaceguitar, 'Space guitar (clean guitar frozen into a pad)', ('pad', 'chords'), 27),
    ('sunpad', v_sunpad, 'Sun pad (warm analog poly, slow bloom)', ('pad', 'chords'), 89),
    ('softmoog', v_softmoog, 'Soft mono lead (warm, gliding analog melody)', ('lead', 'arp'), 81),
    ('roundmoog', v_roundmoog, 'Round mono bass (warm analog, low-mid weight)', ('bass',), 39),
)
for _name, _fn, _info, _roles, _gm in NEW_196B:
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# =============================================================================
#  1.97: a better surf band - spring-reverb guitars, a real combo organ
# =============================================================================
_SPRING_IR = {}


def _spring_ir(decay, tank, tone):
    """The spring tank's impulse response (built once): each round trip down a spring passes the echo through ten
    first-order all-passes - the dispersion that smears it into the falling 'chirp' of the surf 'drip'."""
    key = (decay, tank, tone)
    if key not in _SPRING_IR:
        from scipy.signal import lfilter
        n = int(1.4 * SR)
        imp = np.zeros(n)
        imp[0] = 1.0
        src = hp(imp, 300)
        wet = np.zeros(n)
        for T, side in zip(tank, (1.0, 0.85)):
            d = int(T * SR)
            e = src.copy()
            g = 1.0
            for _ in range(7):                         # seven round trips down the spring
                for _ in range(10):
                    e = lfilter([0.62, 1.0], [1.0, 0.62], e)
                e = np.concatenate([np.zeros(d), e[:-d]])
                g *= decay
                wet += side * g * e
        wet = lp(wet, tone)
        wet[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
        _SPRING_IR[key] = wet / (np.sqrt(np.sum(wet ** 2)) + 1e-12)
    return _SPRING_IR[key]


def _spring(y, mix=0.45, decay=0.55, tank=(0.0337, 0.0411), tone=4200):
    """A guitar amp's spring reverb tank (bright, boingy, its lows kept dry). Returns dry + wet, 1.4 s longer."""
    from scipy.signal import fftconvolve
    y = np.asarray(y, float)
    ir = _spring_ir(decay, tank, tone)
    wet = fftconvolve(y, ir)
    wet = wet / (np.abs(wet).max() + 1e-9) * np.abs(y).max() * 0.9
    out = np.concatenate([y, np.zeros(len(ir) - 1)]) + mix * wet
    return out


def v_surfguitar(m, dur, p, glide=None, mod=None):
    """Surf guitar: an offset-body guitar's bright single-coil bridge pickup, played hard with a flat pick into a clean,
    loud amp and its spring reverb tank turned way up - the snappy attack, the wet 'drip' of the springs and a faint
    amp tremolo (p trem = tremolo depth). The lead and baritone sound of 60s surf and monster themes."""
    y, pm = _eg_string(m, dur, dict(p, pickup=p.get('pickup', 0.06)), mod)
    y = np.tanh(y * 2.2) / 1.6
    y = eq(eq(eq(y, 'peak', 180, 0.9, 1.5), 'peak', 900, 1.0, -2.5), 'peak', 2800, 1.0, 4.0)
    y = lp(y, 7000)
    y = _spring(y, mix=p.get('spring', 0.5))
    tr = float(p.get('trem', 0.15))
    if tr:
        t = np.arange(len(y)) / SR
        y = y * (1 - tr * (0.5 + 0.5 * np.sin(2 * np.pi * p.get('trem_hz', 5.5) * t)))
    return _ms_stereo(y, 22) * 0.6


def v_baritwang(m, dur, p, glide=None, mod=None):
    """Baritone twang: a six-string bass / baritone guitar (a fourth or an octave below a guitar) picked near the
    bridge - a deep, growling twang with a hard pick attack, the spring reverb a little lower in the mix; the creeping
    low riffs of monster and spy themes."""
    y, pm = _eg_string(m, dur, dict(p, pickup=0.05), mod)
    y = np.tanh(y * 2.6) / 1.7
    y = eq(eq(y, 'peak', 110, 0.9, 3.0), 'peak', 1600, 1.1, 4.5)
    y = lp(y, 5000)
    y = _spring(y, mix=p.get('spring', 0.32), decay=0.5)
    return _ms_stereo(y, 15) * 0.62


def v_combo(m, dur, p, glide=None, mod=None):
    """Combo organ: the reedy transistor organ of 60s garage and surf bands - bright divider-tone pulse waves at 8' and
    4' (thin and buzzy, not a tonewheel's round sines) through a hollow formant, an instant on / off key gate, a fast
    shallow vibrato and a small speaker's mid bark. The haunted-house organ of monster themes."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.004, 0.05, 0.95, 0.05)
    n = len(env)
    t = np.arange(n) / SR
    vib = 1 + p.get('vib', 0.0045) * np.sin(2 * np.pi * p.get('vib_hz', 6.8) * t)
    fr = f * vib
    x = 0.9 * _va.pulse(fr, n, 0.0, 0.32) + 0.55 * _va.pulse(fr * 2, n, 0.25, 0.4) + 0.25 * _va.pulse(fr * 4, n, 0.5, 0.5)
    x = lp(x, p.get('cut', 3800))
    x = eq(eq(x, 'peak', 1100, 1.2, 5.0), 'peak', 2400, 1.5, 3.0)
    x = hp(x, 160)
    y = np.tanh(x * 1.3) * env
    return _ms_stereo(y, 30, 0.5) * 0.33


NEW_197 = (
    ('surfguitar', v_surfguitar, 'Surf guitar (bright twang, dripping spring reverb)', ('lead', 'arp', 'chords', 'bass'), 27),
    ('baritwang', v_baritwang, 'Baritone twang (six-string bass, spring reverb)', ('bass', 'lead', 'arp'), 32),
    ('combo', v_combo, 'Combo organ (reedy 60s transistor organ)', ('chords', 'pad', 'arp', 'lead'), 17),
)
for _name, _fn, _info, _roles, _gm in NEW_197:
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# =============================================================================
#  1.97: wave (ethereal half-time bass music) sounds
# =============================================================================
def v_wavebass(m, dur, p, glide=None, mod=None):
    """Wave bass: a long, heavy 808-style sub that holds through the bar - a short pitch drop into the note, a slow
    'breathing' pitch drift of a few cents and a soft tube saturation adding the 2nd and 3rd harmonics, so the huge
    low end is heard on small speakers too; slides from the last note (glide)."""
    f = float(mtof(m))
    env, n, t = _env_n(dur, 0.004, 0.6, 0.85, p.get('r', 0.3))
    fr = _glide_freq(f, n, glide, 0.09) * 2 ** ((1.2 * np.exp(-t / 0.03) + 0.08 * np.sin(2 * np.pi * 0.3 * t)) / 12)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph)
    y = np.tanh(y * p.get('drive', 1.8)) / np.tanh(p.get('drive', 1.8))
    y = y + 0.12 * np.sin(2 * ph)
    return np.vstack([y, y]) * env * 0.55


def v_etherchop(m, dur, p, glide=None, mod=None):
    """Ether chop: a breathy, sung vocal chop - an 'ah' / 'oo' formant voice with air in it, scooping up into the note
    and fading out soft - the floating vocal chops of wave and melodic bass, made to sit in a huge reverb."""
    f = float(mtof(m))
    env, n, t = _env_n(min(dur, 1.6), 0.02, 0.3, 0.7, 0.35)
    rng = _rng()
    fr = f * 2 ** (-0.6 * np.exp(-t / 0.06) / 12)
    x = _stack_saw(fr, n, (-5, 5), rng, 0.6)
    vow = p.get('vowel', 'a' if m % 2 else 'o')
    y = np.vstack([_va.formant(x[i], vow, 6.0) for i in range(2)])
    air = hp(lp(rng.standard_normal(n), 7000), 2500) * 0.08
    y = y + np.vstack([air, air[::-1]])
    return _hpf(y, 220) * env * 0.8


NEW_197B = (
    ('wavebass', v_wavebass, 'Wave bass (held 808 sub, saturated, slides)', ('bass',), 38),
    ('etherchop', v_etherchop, 'Ether chop (breathy floating vocal chop)', ('lead', 'arp', 'chords'), 54),
)
for _name, _fn, _info, _roles, _gm in NEW_197B:
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES[_role]:
            ROLE_CHOICES[_role].append(_name)


# (2.0) synths the library was missing for trance, techno and hip hop
from . import synths2  # noqa: E402,F401
from . import guitars2  # noqa: E402,F401
from . import instruments3  # noqa: E402,F401
from . import celtic  # noqa: E402,F401
from . import synths25  # noqa: E402,F401
from . import deepwob as _deepwob  # noqa: E402
_deepwob.register()
