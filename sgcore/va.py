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

# 'analog' (1.77): every note is its own take - a velocity that changes the tone (harder = brighter, more filter
# envelope, a little more drive), slightly different tuning, cutoff and envelope times from note to note like a real
# analog poly, and the per-sample ladder filter. 'classic': the sound before 1.77, note for note.
# The renderer sets this per song (Options.synth_character).
CHARACTER = 'analog'
NOTE = None          # the note being synthesised: {'vel': layer} (set by the renderer around each note, else None)


def analog():
    return CHARACTER == 'analog'


def note_tone(p, spread=1.0):
    """(cutoff multiplier, envelope multiplier, drive multiplier) for this note: velocity + analog variation.
    p['vel'] is the note's velocity layer (set by the renderer); 1.0s in classic mode."""
    if not analog():
        return 1.0, 1.0, 1.0
    vel = float(p.get('vel', (NOTE or {}).get('vel', 0.8)))
    cm = 2 ** (1.1 * (vel - 0.8) + spread * _RNG.normal(0.0, 0.07))
    em = (0.7 + 0.375 * vel) * 2 ** (spread * _RNG.normal(0.0, 0.05))
    dm = 0.9 + 0.15 * vel
    return float(cm), float(em), float(dm)


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


def vcf(x, cut, res=0.2, drive=1.2, block=96, tone=True):
    """Resonant 24 dB/oct low-pass with a moving cutoff `cut` (Hz, array or number). res 0..1 (self-oscillation ~1).
    Driven into soft saturation before the filter, like an analog VCF's input stage.
    Analog character (with numba): a per-sample zero-delay-feedback transistor ladder (sgcore.fastdsp.ladder) - the
    cutoff moves smoothly sample by sample (no steps on fast plucks), the resonance tracks the cutoff and compresses
    on loud notes. Classic: two cookbook stages updated every `block` samples (the sound before 1.77)."""
    if analog():
        from . import fastdsp
        if tone and NOTE is not None:                # instruments built straight on the filter (supersaws, stabs
            cm, _, dm = note_tone({})                # ...): their notes respond to velocity too
            cut = np.asarray(cut, float) * cm
            drive = drive * dm
        if fastdsp.HAVE_NUMBA:
            return fastdsp.ladder(x, cut, res, drive, SR)
    x = np.tanh(np.asarray(x, float) * drive) / np.tanh(drive)
    n = x.shape[-1]
    cut = np.broadcast_to(np.asarray(cut, float), (n,))
    q1 = 0.55 + 6.0 * float(res) ** 1.6
    chans = x if x.ndim == 2 else x[None, :]
    out = np.empty_like(chans)
    for c in range(chans.shape[0]):
        z1, z2 = np.zeros(2), np.zeros(2)
        s = 0
        while s < n:                                 # (2.17) a steady cutoff runs as one long segment (far fewer calls)
            e = min(n, s + block)
            fc = float(np.clip(cut[s], 25.0, SR * 0.42))
            while e < n and abs(float(np.clip(cut[e], 25.0, SR * 0.42)) - fc) < 0.004 * fc and e - s < 128 * block:
                e = min(n, e + block)
            b1, a1 = _biquad_lp(fc, q1)
            b2, a2 = _biquad_lp(fc, 0.54)
            y, z1 = signal.lfilter(b1, a1, chans[c, s:e], zi=z1)
            out[c, s:e], z2 = signal.lfilter(b2, a2, y, zi=z2)
            s = e
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
    tune = 0.0
    if analog():                        # this note's own take: velocity -> tone, and the small analog differences
        cm, em, dm = note_tone(p)
        cut, fenv, drive = cut * cm, fenv * em, drive * dm
        jit = 2 ** _RNG.normal(0.0, 0.06)
        d_, fd = d_ * jit, fd * jit
        tune = _RNG.normal(0.0, 1.6)                  # cents: oscillators never quite land on the same pitch
    gate = int(max(dur, 0.01) * SR)
    env = adsr(gate, a_, d_, s_, r_)
    n = len(env)
    t = np.arange(n) / SR
    f = float(mtof(m + 12 * octave)) * 2 ** (tune / 1200)
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
    y = vcf(np.vstack([L, R]), cutoff, res, drive, tone=False)
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


def sync_saw(f_master, ratio, n, ph0=0.0):
    """Hard-sync saw: a slave saw at f_master * ratio (ratio may move per sample) restarted by every master cycle -
    the tearing, vocal 80s sync-lead sound as the ratio sweeps. Oversampled 4x then low-passed to keep it clean."""
    os_ = 4
    N = n * os_
    fm = np.repeat(np.broadcast_to(np.asarray(f_master, float), (n,)), os_) / (SR * os_)
    rt = np.repeat(np.broadcast_to(np.asarray(ratio, float), (n,)), os_)
    mph = ph0 + np.cumsum(fm)
    cyc = np.floor(mph)
    reset = np.concatenate([[0], np.diff(cyc) > 0]).astype(bool)
    inc = fm * rt
    acc = np.cumsum(inc)
    idx = np.where(reset, np.arange(N), 0)
    np.maximum.accumulate(idx, out=idx)
    base = acc[idx] - inc[idx]
    sph = (acc - base) % 1.0
    y = 2.0 * sph - 1.0
    b, a = signal.butter(8, 0.9 / os_, 'low')
    y = signal.lfilter(b, a, y)
    return y[::os_]


FORMANTS = {'a': (800, 1150, 2900), 'o': (450, 800, 2830), 'u': (325, 700, 2530), 'e': (400, 1600, 2700),
            'i': (300, 1900, 2950)}


def formant(x, vowel='a', q=8.0):
    """A choir-ish vowel: three band-passes at the vowel's formants, summed (parallel, so the level stays even)."""
    out = np.zeros_like(x)
    for k, fc in enumerate(FORMANTS.get(vowel, FORMANTS['a'])):
        w = fc / (SR / 2)
        b, a = signal.butter(2, [w / (1 + 0.5 / q), min(0.99, w * (1 + 0.5 / q))], 'band')
        out += signal.lfilter(b, a, x, axis=-1) * (1.0, 0.6, 0.35)[k]
    return out


def tonewheel(m, dur, p):
    """Tonewheel organ: nine drawbars (16', 5 1/3', 8', 4', 2 2/3', 2', 1 3/5', 1 1/3', 1') set by a registration string
    like '888000000', a key click, the 2nd / 3rd-harmonic percussion that decays, a slight tube overdrive, and a
    two-rotor rotary speaker (the horn fast, the drum slow, each with its Doppler wobble and its own stereo throw)."""
    reg = str(p.get('reg', '888600000'))
    ratios = (0.5, 1.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    n = gate + int(0.06 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for r, d in zip(ratios, reg.ljust(9, '0')[:9]):
        lvl = int(d) / 8.0
        if lvl and f * r < 12000:
            y += lvl * np.sin(2 * np.pi * f * r * t + _RNG.random() * 6.28)
    y /= 3.0
    if p.get('perc', True):                                        # percussion: 2nd (or 3rd) harmonic, decaying
        y += 0.5 * np.sin(2 * np.pi * f * (3.0 if p.get('perc3') else 2.0) * t) * np.exp(-t * 7)
    ck = min(n, int(0.004 * SR))                                   # key click
    y[:ck] += _RNG.standard_normal(ck) * 0.15 * np.linspace(1, 0, ck)
    env = np.ones(n)
    env[:int(0.004 * SR)] = np.linspace(0, 1, int(0.004 * SR))
    env[gate:] = np.linspace(1, 0, n - gate)
    y = np.tanh(y * env * p.get('drive', 1.6)) / np.tanh(p.get('drive', 1.6))
    if p.get('leslie', 1) == 0:                                    # the track runs its own rotary effect (leslie_fx)
        return np.vstack([y, y]) * 0.35
    # rotary speaker: split at 800 Hz, horn ~6.7 Hz, drum ~5.8 Hz ('chorale' slow if p['slow'])
    slow = p.get('slow', False)
    bl, al = signal.butter(2, 800 / (SR / 2), 'low')
    lo = signal.lfilter(bl, al, y)
    hi = y - lo
    out = np.zeros((2, n))
    idx = np.arange(n)
    for band, rate, dep, amp_m in ((hi, 0.8 if slow else 6.7, 0.00045, 0.35), (lo, 0.7 if slow else 5.8, 0.0003, 0.15)):
        ph = 2 * np.pi * rate * t + _RNG.random() * 6.28
        for c, sgn in ((0, 1.0), (1, -1.0)):
            dl = (0.001 + dep * (1 + sgn * np.sin(ph))) * SR
            v = np.interp(idx - dl, idx, band, left=0.0)
            out[c] += v * (1 + amp_m * sgn * np.sin(ph + 0.6))
    return out * 0.35


# JP-8000 supersaw (after Adam Szabo's analysis of the original): seven saws at fixed relative offsets, a non-linear
# detune knob, and a mix that trades the centre saw against the six side saws
_JP_OFF = np.array([-0.11002313, -0.06288439, -0.01952356, 0.0, 0.01991221, 0.06216538, 0.10745242])


def _jp_detune(x):
    x = float(np.clip(x, 0, 1))
    return (10028.7312891634 * x ** 11 - 50818.8652045924 * x ** 10 + 111363.4808729368 * x ** 9
            - 138150.6761080548 * x ** 8 + 106649.6679158292 * x ** 7 - 53046.9642751875 * x ** 6
            + 17019.9518580080 * x ** 5 - 3425.0836591318 * x ** 4 + 404.2703938388 * x ** 3
            - 24.1878824391 * x ** 2 + 0.6717417634 * x + 0.0030115596)


def jp_supersaw(fr, n, detune=0.5, mix=0.7, spread=1.0):
    """Seven saws, JP-8000 style -> stereo (2, n). fr: Hz (number or per-sample array)."""
    d = _jp_detune(detune)
    side = -0.73764 * mix ** 2 + 1.2841 * mix + 0.044372
    centre = -0.55366 * mix + 0.99785
    fr = np.broadcast_to(np.asarray(fr, float), (n,))
    L = np.zeros(n)
    R = np.zeros(n)
    for k, off in enumerate(_JP_OFF):
        s = saw(fr * (1 + off * d), n, _RNG.random())
        g = centre if k == 3 else side
        pan = 0.5 + 0.5 * spread * (k - 3) / 3
        L += s * g * np.cos(pan * np.pi / 2)
        R += s * g * np.sin(pan * np.pi / 2)
    return np.vstack([L, R]) * 0.45


def vcf18(x, cut, res=0.5, drive=1.0, block=64):
    """TB-303-style low-pass: an 18 dB/oct slope (one resonant 2-pole stage + a one-pole), squelchy resonance that
    sings but stops just short of self-oscillation, and a soft-clipping input like the diode ladder's."""
    x = np.tanh(np.asarray(x, float) * drive) / np.tanh(drive)
    n = x.shape[-1]
    cut = np.broadcast_to(np.asarray(cut, float), (n,))
    q = 0.6 + 9.0 * float(np.clip(res, 0, 0.95)) ** 1.4
    chans = x if x.ndim == 2 else x[None, :]
    out = np.empty_like(chans)
    for c in range(chans.shape[0]):
        z1, z2 = np.zeros(2), np.zeros(1)
        for s in range(0, n, block):
            e = min(n, s + block)
            fc = float(np.clip(cut[s], 30.0, SR * 0.4))
            b1, a1 = _biquad_lp(fc, q)
            pole = np.exp(-2 * np.pi * fc / SR)
            y, z1 = signal.lfilter(b1, a1, chans[c, s:e], zi=z1)
            out[c, s:e], z2 = signal.lfilter([1 - pole], [1, -pole], y, zi=z2)
    out *= 1.0 / (1.0 + 0.25 * float(res))
    return out if x.ndim == 2 else out[0]


def juno_chorus(x, mode=2, mix=0.5):
    """The Juno-60/106 BBD chorus: the (mono) voice through a short delay swept by a triangle LFO, the left and right
    copies swept in opposite directions and summed with the dry signal. Mode I is slow and gentle, II faster and deeper,
    I+II a fast shallow shimmer. The bucket-brigade wet path is darker than the dry one."""
    mono = x.mean(axis=0) if np.ndim(x) == 2 else np.asarray(x, float)
    n = len(mono)
    t = np.arange(n) / SR
    rate, lo, hi = {1: (0.513, 1.66, 5.35), 2: (0.863, 1.66, 5.35), 3: (9.75, 3.3, 3.7)}.get(mode, (0.863, 1.66, 5.35))
    tri = 2 * np.abs(2 * ((t * rate + _RNG.random()) % 1.0) - 1) - 1
    mid, dep = (lo + hi) / 2, (hi - lo) / 2
    idx = np.arange(n, dtype=float)
    bl, al = signal.butter(2, 7500 / (SR / 2))
    wet_src = signal.lfilter(bl, al, mono)
    out = []
    for sgn in (1.0, -1.0):
        d = (mid + sgn * dep * tri) * SR / 1000.0
        out.append(mono * (1 - 0.3 * mix) + np.interp(idx - d, idx, wet_src, left=0.0) * mix)
    return np.vstack(out)


def string(f, n, exc, t60=4.0, bright=0.5, gate=None, mute_t60=0.12, pickup=0.0):
    """A plucked string as a digital waveguide (Karplus-Strong family), computed one period at a time so numpy can do
    the work: the excitation `exc` is fed into a delay line one period long, whose loop has a one-pole low-pass (how
    fast the high harmonics die: `bright` 0..1), a fractional-delay tap for exact tuning and a loss set so the note
    falls 60 dB in `t60` seconds. From `gate` (samples) the finger mutes the string (`mute_t60`). `pickup` (0..0.5)
    reads the string at that point of its length - a comb that gives a pickup its tone."""
    P = SR / float(f)
    L = int(P)
    frac = P - L
    # one-pole loop low-pass y = (1-a) x + a y[-1]; its phase delay at f is ~a/(1-a) samples - take it off the line
    a = float(np.clip(0.55 - 0.5 * bright, 0.02, 0.6))
    lag = a / (1 - a)
    Lw = P - lag
    L = max(2, int(Lw))
    frac = Lw - L
    y = np.zeros(n + L + 2)
    exc = np.asarray(exc, float)
    x = np.zeros(n)
    x[:min(n, len(exc))] = exc[:n]
    g_on = 10 ** (-3.0 / (f * t60))
    g_off = 10 ** (-3.0 / (f * max(0.01, mute_t60)))
    zi = np.zeros(1)
    b_lp, a_lp = [1 - a], [1, -a]
    off = L + 2                                                  # y[off + i] is output sample i
    for s in range(0, n, L):
        e = min(n, s + L)
        i0 = off + s
        d0 = y[i0 - L:i0 - L + (e - s)]                          # delayed by L
        d1 = y[i0 - L - 1:i0 - L - 1 + (e - s)]                  # delayed by L + 1
        tap = (1 - frac) * d0 + frac * d1
        z, zi = signal.lfilter(b_lp, a_lp, tap, zi=zi)
        g = g_on if gate is None or s < gate else g_off
        y[i0:i0 + (e - s)] = x[s:e] + g * z
    out = y[off:off + n]
    if pickup:
        k = max(1, int(round(pickup * P)))
        out = out - np.concatenate([np.zeros(k), out[:-k]]) * 0.5
    return out
