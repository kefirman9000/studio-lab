"""Bar-long moves for switch-up bass (2.2.2): effects that ride a whole bar (or two) and then let go.

Rising / sinking (the reference's transitions - the whole top end sinks over a bar into the next scene):
    tape_rise   the part speeds up like a tape being pushed: pitch and brightness climb across the bar
    tape_sink   ... or slowed down: everything slides down and drags (a tape stop that doesn't stop)
    filter_rise a low-pass opening from muffled to bright over the bar
    filter_sink ... closing from bright to a dark thud

Alien (sci-fi, inhuman - each one moves across its bar):
    freqshift   a frequency shifter sweeping up or down: every partial moves by the same Hz, so the sound turns
                inharmonic, metallic and 'not from here' (the classic barber-pole / UFO sweep)
    ringmod     ring modulation by a carrier gliding 40 Hz -> 1.6 kHz: from a growl to a robotic clang
    vowel       a formant filter morphing a-e-i-o-u: the part 'talks' like a robot
    comb        a resonant comb filter whose pitch sweeps: a metallic laser / flanger scream
    zap         every 16th cut into a grain that dives in pitch: laser 'pew pew' zaps
    stutter     the bar's first beat retriggered faster and faster (8ths -> 32nds), pitched up as it goes
    crushdive   the sample rate dives from 22 kHz to 600 Hz: the sound dissolves into digital grit

apply_motion(buf, motions, renderer) - motions: [(beat0, beat1, kind, up), ...]; up = +1 rise / -1 sink.
"""
import numpy as np
from scipy import signal

from .dsp import SR, bp, lp

KINDS_MOVE = ('tape_rise', 'tape_sink', 'filter_rise', 'filter_sink')
KINDS_ALIEN = ('freqshift', 'ringmod', 'vowel', 'comb', 'zap', 'stutter', 'crushdive')


def _tape(x, up):
    """Varispeed across the segment: the read speed ramps 1 -> 1.9 (rise) or 1 -> 0.45 (sink)."""
    n = x.shape[-1]
    r = np.linspace(0, 1, n) ** 1.5
    rate = 1 + (0.9 if up > 0 else -0.55) * r
    pos = np.cumsum(rate) - rate[0]
    pos = np.clip(pos, 0, n - 1)
    i0 = pos.astype(np.int64)
    fr = pos - i0
    i1 = np.minimum(i0 + 1, n - 1)
    return x[..., i0] * (1 - fr) + x[..., i1] * fr


def _filter_sweep(x, up, lo=180.0, hi=14000.0):
    """A low-pass moving in 64 short blocks (cross-faded), opening (up) or closing (down)."""
    n = x.shape[-1]
    out = np.zeros_like(x)
    blocks = 64
    edges = np.linspace(0, n, blocks + 1).astype(int)
    for k in range(blocks):
        a, b = edges[k], edges[k + 1]
        f = k / (blocks - 1)
        fc = lo * (hi / lo) ** (f if up > 0 else 1 - f)
        pad = min(a, 2048)
        seg = lp(x[..., a - pad:b], min(fc, SR / 2 - 200), 2)
        out[..., a:b] = seg[..., pad:]
    return out


def _hilbert_shift(x, shift_hz):
    """Frequency shifter: an analytic signal times e^(i w t) - shift_hz is an array (Hz per sample)."""
    ph = 2 * np.pi * np.cumsum(shift_hz) / SR
    out = np.empty_like(x)
    for c in range(x.shape[0]):
        a = signal.hilbert(x[c])
        out[c] = np.real(a * np.exp(1j * (ph + c * 0.4)))
    return out


def _freqshift(x, up):
    n = x.shape[-1]
    r = np.linspace(0, 1, n) ** 1.4
    return 0.35 * x + 0.85 * _hilbert_shift(x, (900.0 if up > 0 else -450.0) * r)


def _ringmod(x, up):
    n = x.shape[-1]
    r = np.linspace(0, 1, n)
    fc = 40 * (40.0 ** (r if up > 0 else 1 - r))           # 40 Hz <-> 1.6 kHz
    car = np.sin(2 * np.pi * np.cumsum(fc) / SR)
    return 0.3 * x + 0.9 * x * car


VOWELS = [(730, 1090, 2440), (530, 1840, 2480), (270, 2290, 3010), (570, 840, 2410), (300, 870, 2240)]   # a e i o u


def _vowel(x, up):
    n = x.shape[-1]
    seq = VOWELS if up > 0 else VOWELS[::-1]
    out = np.zeros_like(x)
    edges = np.linspace(0, n, len(seq) * 6 + 1).astype(int)
    for k in range(len(edges) - 1):
        a, b = edges[k], edges[k + 1]
        f = k / (len(edges) - 2) * (len(seq) - 1)
        j = int(f)
        t = f - j
        v0, v1 = seq[j], seq[min(j + 1, len(seq) - 1)]
        pad = min(a, 2048)
        src = x[..., a - pad:b]
        y = 0
        for (f0, f1), g in zip(zip(v0, v1), (1.0, 0.7, 0.4)):
            fc = f0 + (f1 - f0) * t
            y = y + g * bp(src, fc * 0.85, min(fc * 1.18, SR / 2 - 300))
        out[..., a:b] = y[..., pad:]
    return out * 2.2


def _comb(x, up):
    """Feedback comb whose delay glides (1/80 s <-> 1/1200 s): a pitched, metallic scream."""
    n = x.shape[-1]
    r = np.linspace(0, 1, n)
    f = 80 * (15.0 ** (r if up > 0 else 1 - r))
    d = SR / f
    out = np.copy(x)
    fb = 0.82
    for c in range(x.shape[0]):
        y = np.zeros(n)
        xc = x[c]
        # block-wise approximation: fixed delay per 256-sample block, fed back from the output so far
        blk = 256
        for a in range(0, n, blk):
            b = min(n, a + blk)
            dd = int(d[a])
            src = y[a - dd:b - dd] if a - dd >= 0 else np.concatenate([np.zeros(dd - a), y[:max(0, b - dd)]])[:b - a]
            y[a:b] = xc[a:b] + fb * src[:b - a]
        out[c] = 0.4 * xc + 0.6 * y / 3.0
    return out


def _zap(x, up, spb):
    n = x.shape[-1]
    g = max(64, int(spb / 4 * SR))                        # one grain per 16th
    out = np.zeros_like(x)
    for a in range(0, n, g):
        b = min(n, a + g)
        L = b - a
        t = np.arange(L) / SR
        rate = np.linspace(1.8, 0.35, L) if up <= 0 else np.linspace(0.5, 2.2, L)
        pos = np.clip(np.cumsum(rate) - rate[0], 0, L - 1)
        i0 = pos.astype(np.int64)
        seg = x[..., a:b][..., i0]
        env = np.exp(-t / (L / SR * 0.55))
        out[..., a:b] = seg * env
    return out * 1.2


def _stutter(x, up, spb):
    n = x.shape[-1]
    out = np.zeros_like(x)
    pos = 0
    k = 0
    beat = int(spb * SR)
    while pos < n:
        frac = pos / n
        size = int(beat / (2 ** (1 + int(frac * 3.2))))     # 8ths -> 16ths -> 32nds -> 64ths
        size = max(256, size)
        L = min(size, n - pos)
        grain = x[..., :L].copy()
        if up > 0:                                         # pitched up as it accelerates
            rate = 1 + frac * 0.9
            idx = np.clip((np.arange(L) * rate).astype(np.int64), 0, L - 1)
            grain = grain[..., idx]
        fade = np.minimum(1, np.minimum(np.arange(L), L - 1 - np.arange(L)) / 64.0)
        out[..., pos:pos + L] = grain * fade
        pos += L
        k += 1
    return out


def _crushdive(x, up):
    n = x.shape[-1]
    r = np.linspace(0, 1, n) ** 1.3
    sr_t = 22050 * (0.027 ** (r if up <= 0 else 1 - r))     # 22 kHz <-> 600 Hz
    acc = np.floor(np.cumsum(sr_t / SR))                  # sample & hold at the falling rate
    new = np.concatenate([[True], acc[1:] != acc[:-1]])
    idx = np.maximum.accumulate(np.where(new, np.arange(n), 0))
    y = x[..., idx]
    bits = 16 - 11 * (r if up <= 0 else 1 - r)
    q = 2.0 ** (bits - 1)
    return np.round(y * q) / q


def _one(x, kind, up, spb):
    if kind == 'tape_rise':
        return _tape(x, 1)
    if kind == 'tape_sink':
        return _tape(x, -1)
    if kind == 'filter_rise':
        return _filter_sweep(x, 1)
    if kind == 'filter_sink':
        return _filter_sweep(x, -1)
    if kind == 'freqshift':
        return _freqshift(x, up)
    if kind == 'ringmod':
        return _ringmod(x, up)
    if kind == 'vowel':
        return _vowel(x, up)
    if kind == 'comb':
        return _comb(x, up)
    if kind == 'zap':
        return _zap(x, up, spb)
    if kind == 'stutter':
        return _stutter(x, up, spb)
    if kind == 'crushdive':
        return _crushdive(x, up)
    return x


def apply_motion(buf, motions, r):
    """Run each bar-long move over its stretch of the part (with 10 ms cross-fades in and out, so nothing clicks)."""
    x = np.asarray(buf, dtype=np.float64)
    mono = x.ndim == 1
    if mono:
        x = x[None, :]
    n = x.shape[-1]
    for (b0, b1, kind, up) in motions:
        a, b = int(r._bt(b0) * SR), int(r._bt(b1) * SR)
        a, b = max(0, a), min(n, b)
        if b - a < 2048:
            continue
        seg = x[..., a:b]
        if not np.any(seg):
            continue
        rms0 = np.sqrt(np.mean(seg ** 2)) + 1e-9
        y = _one(seg.copy(), kind, up, r.spb)
        y = np.nan_to_num(y)
        rms1 = np.sqrt(np.mean(y ** 2)) + 1e-9
        y *= min(2.0, rms0 / rms1)                         # every move about as loud as the bar it replaces
        pk0, pk1 = float(np.max(np.abs(seg))) + 1e-9, float(np.max(np.abs(y))) + 1e-9
        if pk1 > 1.4 * pk0:                                # ... and never jumping out of the mix
            y *= 1.4 * pk0 / pk1
        f = min(int(0.01 * SR), (b - a) // 4)
        w = np.ones(b - a)
        w[:f] = np.linspace(0, 1, f)
        w[-f:] = np.linspace(1, 0, f)
        x[..., a:b] = seg * (1 - w) + y * w
    out = x[0] if mono else x
    return out.astype(np.float32)
