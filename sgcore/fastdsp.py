"""Per-sample DSP kernels (1.77): the analog-modelled ladder filter and the feedback-delay-network reverb.

These need a loop over every sample, which is far too slow in plain Python. With numba installed (it is in
requirements.txt and in the installers) they're compiled to machine code the first time they run and cached on disk.
Without numba, HAVE_NUMBA is False and the callers fall back to their older block-based versions, so nothing breaks.
"""
import math

import numpy as np

try:                                                    # optional speed-up
    from numba import njit
    HAVE_NUMBA = True
except Exception:                                       # noqa: BLE001 - any import problem means "not available"
    HAVE_NUMBA = False

    def njit(*a, **k):                                  # a no-op decorator so the module still imports
        if a and callable(a[0]):
            return a[0]
        return lambda f: f


@njit(cache=True, fastmath=True)
def _ladder_kernel(x, g, k, drive, comp):
    """Zero-delay-feedback 4-pole ladder (24 dB/oct), one sample at a time.
    x: input (n,), g: tan(pi fc / SR) per sample (n,), k: feedback (0 .. ~4 = self-oscillation).
    The feedback loop is solved exactly each sample (no unit delay, so the resonance tracks the cutoff the way an
    analog filter does), and the input + feedback pass through tanh like a transistor ladder's differential pair:
    loud notes saturate and the resonance compresses instead of exploding."""
    n = x.shape[0]
    y = np.empty(n)
    s1 = 0.0
    s2 = 0.0
    s3 = 0.0
    s4 = 0.0
    for i in range(n):
        gi = g[i]
        G = gi / (1.0 + gi)
        inv = 1.0 / (1.0 + gi)
        S = G * G * G * s1 * inv + G * G * s2 * inv + G * s3 * inv + s4 * inv
        G4 = G * G * G * G
        u = (math.tanh(x[i] * drive) - k * math.tanh(S)) / (1.0 + k * G4)
        v = (u - s1) * G
        y1 = v + s1
        s1 = y1 + v
        v = (y1 - s2) * G
        y2 = v + s2
        s2 = y2 + v
        v = (y2 - s3) * G
        y3 = v + s3
        s3 = y3 + v
        v = (y3 - s4) * G
        y4 = v + s4
        s4 = y4 + v
        y[i] = y4 * comp
    return y


def ladder(x, cut, res, drive, sr):
    """Analog-style 24 dB ladder low-pass for (n,) or (2, n) input with a per-sample (or fixed) cutoff in Hz."""
    x = np.asarray(x, np.float64)
    n = x.shape[-1]
    fc = np.clip(np.broadcast_to(np.asarray(cut, np.float64), (n,)), 20.0, sr * 0.45)
    g = np.tan(np.pi * fc / sr)
    k = 4.0 * float(np.clip(res, 0.0, 1.05)) ** 1.15 * 0.97
    d = max(0.3, float(drive))
    # level matched to the old filter at low frequencies: the ladder's own DC gain is 1 / (1 + k)
    comp = (1.0 + k) / (1.0 + 0.35 * float(res)) / math.tanh(d) * 0.98
    if x.ndim == 1:
        return _ladder_kernel(x, g, k, d, comp)
    return np.vstack([_ladder_kernel(np.ascontiguousarray(x[c]), g, k, d, comp) for c in range(x.shape[0])])


@njit(cache=True, fastmath=True)
def _fdn_kernel(x, delays, g_lo, g_hi, damp, mod_depth, mod_rate, sr):
    """8-line feedback delay network (Hadamard mixing). Each line has its own decay gain split into a low and a high
    band (one-pole), so highs die away faster than lows like in a real room, and a slow, slightly different
    modulation of its length so the tail doesn't ring metallic. x: mono input (n,) -> (2, n) stereo."""
    n = x.shape[0]
    N = 8
    maxd = 0
    for j in range(N):
        if delays[j] + mod_depth + 4 > maxd:
            maxd = int(delays[j] + mod_depth + 4)
    buf = np.zeros((N, maxd))
    lp = np.zeros(N)
    w = 0
    out = np.zeros((2, n))
    o = np.zeros(N)
    for i in range(n):
        for j in range(N):                               # read each line with a fractional, modulated tap
            dl = delays[j] + mod_depth * math.sin(2.0 * math.pi * mod_rate * (1.0 + 0.13 * j) * i / sr + j)
            rp = w - dl
            while rp < 0:
                rp += maxd
            i0 = int(rp)
            fr = rp - i0
            i1 = i0 + 1
            if i1 >= maxd:
                i1 -= maxd
            o[j] = buf[j, i0] * (1.0 - fr) + buf[j, i1] * fr
        # Hadamard 8x8 (fast butterfly), normalised
        a0 = o[0] + o[1]
        a1 = o[0] - o[1]
        a2 = o[2] + o[3]
        a3 = o[2] - o[3]
        a4 = o[4] + o[5]
        a5 = o[4] - o[5]
        a6 = o[6] + o[7]
        a7 = o[6] - o[7]
        b0 = a0 + a2
        b1 = a1 + a3
        b2 = a0 - a2
        b3 = a1 - a3
        b4 = a4 + a6
        b5 = a5 + a7
        b6 = a4 - a6
        b7 = a5 - a7
        h0 = (b0 + b4) * 0.35355339
        h1 = (b1 + b5) * 0.35355339
        h2 = (b2 + b6) * 0.35355339
        h3 = (b3 + b7) * 0.35355339
        h4 = (b0 - b4) * 0.35355339
        h5 = (b1 - b5) * 0.35355339
        h6 = (b2 - b6) * 0.35355339
        h7 = (b3 - b7) * 0.35355339
        hs = (h0, h1, h2, h3, h4, h5, h6, h7)
        for j in range(N):
            v = hs[j]
            lp[j] = lp[j] + damp * (v - lp[j])          # split: lows decay at g_lo, highs at g_hi
            fb = lp[j] * g_lo[j] + (v - lp[j]) * g_hi[j]
            buf[j, w] = fb + x[i] * (0.5 if j % 2 == 0 else -0.5)
        out[0, i] = o[0] + o[2] + o[4] + o[6]
        out[1, i] = o[1] + o[3] + o[5] + o[7]
        w += 1
        if w >= maxd:
            w = 0
    return out


def fdn_ir(decay, sr, size=1.0, bright=0.6, predelay=0.02, seed=0, er=0.6):
    """A stereo reverb impulse response from the delay network: early reflections (a sparse set of taps whose
    spacing grows with the room size) followed by a dense, modulated tail whose highs decay faster than its lows
    (bright = how long the highs last, relative to the lows). Normalised like dsp.make_ir."""
    rng = np.random.default_rng(seed)
    n = int((decay * 1.2 + predelay) * sr) + 1
    base = np.array([1031, 1327, 1523, 1801, 2053, 2311, 2633, 2963], float) * (0.55 + 0.6 * size) * sr / 44100.0
    t60_lo = float(decay)
    t60_hi = float(decay) * (0.25 + 0.6 * bright)
    g_lo = 10 ** (-3.0 * base / (t60_lo * sr))
    g_hi = 10 ** (-3.0 * base / (t60_hi * sr))
    imp = np.zeros(n)
    pd = int(predelay * sr)
    imp[pd] = 1.0
    damp = 1.0 - math.exp(-2 * math.pi * 3000.0 / sr)
    if HAVE_NUMBA:
        tail = _fdn_kernel(imp, base, g_lo, g_hi, damp, 6.0 * size, 0.35, float(sr))
    else:                                               # (pure Python would take minutes: a static fallback tail)
        t = np.arange(n) / sr
        tail = rng.standard_normal((2, n)) * np.exp(-6.9 * t / decay)
    # early reflections: 10-14 taps in the first ~15-60 ms, alternating sides, falling off with distance
    n_er = 12
    er_t = pd + np.sort(rng.uniform(0.004, 0.012 + 0.05 * size, n_er)) * sr
    ers = np.zeros((2, n))
    for j, tt in enumerate(er_t.astype(int)):
        if tt < n:
            amp = (0.9 - 0.6 * j / n_er) * er
            ers[j % 2, tt] += amp * (1 if rng.random() < 0.7 else -1)
            ers[(j + 1) % 2, min(n - 1, tt + int(0.0007 * sr))] += amp * 0.4
    tail[:, :pd] = 0.0
    env = np.clip((np.arange(n) - pd) / max(1.0, 0.02 * size * sr), 0, 1)       # the tail builds up after the ERs
    ir = ers + tail * env[None, :] * 0.9
    ir /= np.sqrt(np.sum(ir ** 2) / 2) + 1e-12
    return ir
