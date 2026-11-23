"""Low-level DSP: oscillators, filters, envelopes, dynamics, loudness, file writing."""
import os
import wave
import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter1d, uniform_filter1d

SR = 44100
RNG = np.random.default_rng(0)  # reseeded per song

# =============================================================================
#  DSP building blocks
# =============================================================================

def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


def _norm_f(fc):
    return float(np.clip(fc, 10.0, SR * 0.47)) / (SR / 2)


def lp(x, fc, order=2):
    b, a = signal.butter(order, _norm_f(fc), 'low')
    return signal.lfilter(b, a, x, axis=-1)


def hp(x, fc, order=2):
    b, a = signal.butter(order, _norm_f(fc), 'high')
    return signal.lfilter(b, a, x, axis=-1)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [_norm_f(f1), _norm_f(f2)], 'band')
    return signal.lfilter(b, a, x, axis=-1)


def biquad(kind, f0, q=0.707, gain_db=0.0):
    """RBJ audio-EQ-cookbook biquads."""
    A = 10 ** (gain_db / 40.0)
    w = 2 * np.pi * f0 / SR
    cw, sw = np.cos(w), np.sin(w)
    al = sw / (2 * q)
    sA = np.sqrt(A)
    if kind == 'peak':
        b = [1 + al * A, -2 * cw, 1 - al * A]
        a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind == 'lowshelf':
        b = [A * ((A + 1) - (A - 1) * cw + 2 * sA * al), 2 * A * ((A - 1) - (A + 1) * cw),
             A * ((A + 1) - (A - 1) * cw - 2 * sA * al)]
        a = [(A + 1) + (A - 1) * cw + 2 * sA * al, -2 * ((A - 1) + (A + 1) * cw),
             (A + 1) + (A - 1) * cw - 2 * sA * al]
    elif kind == 'highshelf':
        b = [A * ((A + 1) + (A - 1) * cw + 2 * sA * al), -2 * A * ((A - 1) + (A + 1) * cw),
             A * ((A + 1) + (A - 1) * cw - 2 * sA * al)]
        a = [(A + 1) - (A - 1) * cw + 2 * sA * al, 2 * ((A - 1) - (A + 1) * cw),
             (A + 1) - (A - 1) * cw - 2 * sA * al]
    elif kind == 'highpass':
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == 'lowpass':
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        a = [1 + al, -2 * cw, 1 - al]
    else:
        raise ValueError(kind)
    b = np.array(b) / a[0]
    a = np.array(a) / a[0]
    return b, a


def eq(x, kind, f0, q=0.707, gain_db=0.0):
    b, a = biquad(kind, f0, q, gain_db)
    return signal.lfilter(b, a, x, axis=-1)


def soft(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def noise(n):
    return RNG.standard_normal(n)


def fade_out(x, sec=0.01):
    n = min(int(sec * SR), x.shape[-1])
    if n > 0:
        x = x.copy()
        x[..., -n:] *= np.linspace(1, 0, n)
    return x


def adsr(gate, a, d, s, r):
    """Envelope with gate length `gate` samples plus release. Exponential segments."""
    a = max(int(a * SR), 1)
    d = max(int(d * SR), 1)
    r = max(int(r * SR), 1)
    g = max(int(gate), 1)
    t = np.arange(g, dtype=float)
    att = np.minimum(t / a, 1.0)
    dec = s + (1 - s) * np.exp(-np.maximum(t - a, 0) * 5.0 / d)
    e = np.empty(g + r)
    e[:g] = np.where(t < a, att, dec)
    lvl = e[g - 1]
    e[g:] = lvl * np.exp(-np.arange(r) * 6.0 / r)
    return e


def _phase(freq, n, ph0=0.0):
    inc = np.full(n, float(freq) / SR) if np.isscalar(freq) else np.asarray(freq, float) / SR
    p = (np.cumsum(inc) + ph0) % 1.0
    return p, inc


def _blep(t, dt):
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    y[m] = x + x - x * x - 1.0
    m2 = t > 1.0 - dt
    x = (t[m2] - 1.0) / dt[m2]
    y[m2] = x * x + x + x + 1.0
    return y


def saw(freq, n, ph0=0.0):
    p, dt = _phase(freq, n, ph0)
    return 2 * p - 1 - _blep(p, dt)


def square(freq, n, ph0=0.0, pw=0.5):
    p, dt = _phase(freq, n, ph0)
    s = np.where(p < pw, 1.0, -1.0)
    s += _blep(p, dt)
    s -= _blep((p + 1.0 - pw) % 1.0, dt)
    return s


def sine(freq, n, ph0=0.0):
    p, _ = _phase(freq, n, ph0)
    return np.sin(2 * np.pi * p)


def tri(freq, n, ph0=0.0):
    p, _ = _phase(freq, n, ph0)
    return 2 * np.abs(2 * p - 1) - 1


def filt_env(x, f_lo, f_hi, env):
    """Cheap swept low-pass: crossfade between three fixed filters following env (0..1)."""
    f_mid = np.sqrt(f_lo * f_hi)
    lo, mid, hi = lp(x, f_lo), lp(x, f_mid), lp(x, f_hi)
    e = np.clip(env, 0, 1) * 2
    w_lo = np.clip(1 - e, 0, 1)
    w_hi = np.clip(e - 1, 0, 1)
    w_mid = 1 - w_lo - w_hi
    return lo * w_lo + mid * w_mid + hi * w_hi


def vibrato(f, n, rate=5.5, cents=15, delay=0.2):
    t = np.arange(n) / SR
    depth = np.clip((t - delay) / 0.3, 0, 1) * cents
    return f * 2 ** (depth * np.sin(2 * np.pi * rate * t) / 1200)



def make_ir(decay, predelay=0.02, bright=1.0):
    n_pd = int(predelay * SR)
    n = int(decay * 1.2 * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.9 * t / decay)
    ir = np.zeros((2, n_pd + n))
    for c in range(2):
        nz = noise(n)
        dark = lp(nz, 1800)
        mix = np.exp(-t * 3.5 / decay) * bright
        ir[c, n_pd:] = (dark + (nz - dark) * np.clip(mix, 0, 1)) * env
    ir = hp(ir, 180)
    ir[:, n_pd:n_pd + 200] *= np.linspace(0, 1, 200)
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    return ir


def reverb(x, ir):
    # (2.8) flush denormals first: a fading feedback tail (delay throws) leaves most samples at ~1e-300, and those
    # crawl through the FFT - one delay return took 4.7 s instead of 0.15 s
    x = np.where(np.abs(x) < 1e-12, 0, x).astype(x.dtype, copy=False)
    out = np.empty_like(x)
    for c in range(2):
        out[c] = signal.oaconvolve(x[c], np.asarray(ir[c], dtype=x.dtype))[:x.shape[1]]
    return out


def pingpong(x, delay_s, fb=0.45, taps=6, cut=4000):
    d = int(delay_s * SR)
    n = x.shape[1]
    out = np.zeros_like(x)
    tap = (x[0] + x[1]) * 0.5
    for k in range(1, taps + 1):
        tap = lp(tap, cut, 1) * (fb if k > 1 else 0.8)
        s = k * d
        if s >= n:
            break
        out[(k - 1) % 2, s:] += tap[:n - s]
    return out


def make_spring_ir(decay=1.8):
    """Spring reverb tank: a dispersive 'boing' (falling chirp), a metallic comb ring and a band-limited splash - the
    sound of the reverb in a guitar amp / King Tubby's mixing desk."""
    n = int(decay * 1.1 * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.9 * t / decay)
    ir = np.zeros((2, n))
    for c in range(2):
        nz = noise(n)
        body = signal.lfilter([1.0], [1.0] + [0.0] * (int(0.031 * SR + c * 37) - 1) + [-0.55], nz * 0.5)
        f = 2200 * np.exp(-t * 9) + 380                 # the dispersive chirp that makes springs 'drip'
        chirp = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
        ir[c] = (body + chirp * 0.35) * env
    ir = hp(lp(ir, 4200), 350)
    ir[:, :120] *= np.linspace(0, 1, 120)
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    return ir


def dub_delay(x, delay_s, fb=0.62, n_rep=12, lo=300, hi=2600, drift=0.02):
    """Tape echo for dub throws: band-limited repeats that darken and pitch-drift as they decay, ping-ponging."""
    d = int(delay_s * SR)
    n = x.shape[1]
    out = np.zeros_like(x)
    tap = hp(lp((x[0] + x[1]) * 0.5, hi, 1), lo, 1)
    for k in range(1, n_rep + 1):
        s = k * d + int(k * drift * d * ((-1) ** k) * 0.1)
        if s >= n:
            break
        g = fb ** (k - 1)
        if g < 0.02:
            break
        out[(k - 1) % 2, s:] += tap[:n - s] * g
        tap = lp(tap, max(900, hi - 150 * k), 1)
        tap = soft(tap * 1.3, 1.2) / 1.3              # tape saturation builds on each pass
    return out


def _smooth_gr(gr_db, attack, release, block=32):
    """Asymmetric attack/release smoothing of gain reduction, computed at block rate."""
    n = len(gr_db)
    nb = int(np.ceil(n / block))
    pad = np.pad(gr_db, (0, nb * block - n), mode='edge')
    gb = pad.reshape(nb, block).max(axis=1)
    ca = np.exp(-block / (attack * SR))
    cr = np.exp(-block / (release * SR))
    out = np.empty(nb)
    y = 0.0
    for i in range(nb):
        v = gb[i]
        y = v + (y - v) * (ca if v > y else cr)
        out[i] = y
    return np.interp(np.arange(n), np.arange(nb) * block + block / 2, out)


def compressor(x, thresh=-18.0, ratio=3.0, attack=0.01, release=0.15, knee=6.0, win=0.005, sc_hp=None):
    """sc_hp (2.5.3): high-pass the level detector (a sidechain filter) so a loud sub doesn't slam the compressor -
    when the bass came in, the whole mix ducked, the limiter caught the overshoot and the bass crunched at its start
    and swelled at its end."""
    det = x
    if sc_hp:
        det = signal.sosfilt(signal.butter(2, sc_hp / (SR / 2), 'high', output='sos'), x, axis=-1)
    if x.ndim == 2:                                   # (1.90: channel by channel - no stereo-sized temporaries)
        pw = np.zeros(x.shape[1])
        for c in range(x.shape[0]):
            pw += det[c] * det[c]
        pw /= x.shape[0]
    else:
        pw = det * det
    pw = uniform_filter1d(pw, size=max(1, int(win * SR)))
    ldb = 10 * np.log10(pw + 1e-12) + 3.0  # +3 so a sine's rms reads near its peak
    over = ldb - thresh
    slope = 1 - 1 / ratio
    gr = np.where(over <= -knee / 2, 0.0,
                  np.where(over >= knee / 2, over * slope, slope * (over + knee / 2) ** 2 / (2 * knee)))
    g = _smooth_gr(gr, attack, release)
    del gr, over, ldb, pw
    g = np.power(10.0, -g / 20)
    return x * g


def low_limit(x, ceiling=0.72, split=120.0, hold=0.03, release=0.18):
    """Bass-safe pre-limiter: the band below `split` gets its own slow limiter - its gain is held over a whole cycle of
    the lowest notes (30 ms) and released slowly - so a loud sub / 808 never drives the final brick-wall limiter, whose
    fast gain changes would ride the bass waveform itself and distort it ('clipping' on the low notes)."""
    sos = signal.butter(2, split / (SR / 2), output='sos')
    if x.ndim == 2:                                   # (1.90: one channel at a time)
        lo = np.empty(x.shape, dtype=np.float64)
        for c in range(x.shape[0]):
            lo[c] = signal.sosfiltfilt(sos, x[c])
        a = np.max(np.abs(lo), axis=0)
    else:
        lo = signal.sosfiltfilt(sos, x)
        a = np.abs(lo)
    pk = maximum_filter1d(a, size=int(hold * SR) | 1)
    g = np.minimum(1.0, ceiling / np.maximum(pk, 1e-9))
    B = 64
    n = len(g)
    nb = int(np.ceil(n / B))
    gb = np.pad(g, (0, nb * B - n), constant_values=1.0).reshape(nb, B).min(axis=1)
    cr = np.exp(-B / (release * SR))
    out = np.empty(nb)
    y = 1.0
    for i in range(nb):
        v = gb[i]
        y = v if v < y else v + (y - v) * cr
        out[i] = y
    gs = uniform_filter1d(np.repeat(out, B)[:n], size=int(hold * SR) | 1)
    del pk, g, a
    gs -= 1.0                                         # x - lo + lo * gs = x + lo * (gs - 1): no separate 'hi' copy
    lo *= gs
    lo += x
    return lo


CHUNK = 1 << 19          # (1.90) ~12 s per block for the oversampled stages: a whole song is never upsampled at once
_PAD = 512


def chunked(fn, x, chunk=CHUNK, pad=_PAD, extra=None):
    """Apply a sample-local stage (oversampled saturation / clipping) block by block, each block with `pad` samples of
    context on both sides that are trimmed off again - the same result as one pass over the whole song, at a small
    fraction of the memory. `extra`: a per-sample array sliced alongside (e.g. a clip limit per sample)."""
    n = x.shape[-1]
    if n <= chunk + 2 * pad:
        return fn(x) if extra is None else fn(x, extra)
    out = np.empty_like(x)
    for s0 in range(0, n, chunk):
        s1 = min(n, s0 + chunk)
        a, b = max(0, s0 - pad), min(n, s1 + pad)
        seg = x[..., a:b]
        y = fn(seg) if extra is None else fn(seg, extra[a:b])
        out[..., s0:s1] = y[..., s0 - a:s0 - a + (s1 - s0)]
    return out


def true_peak_env(x, os=4, chunk=CHUNK, pad=_PAD, floor=None):
    """Per-sample peak of the waveform between the samples (os x oversampled, both channels), computed block by block.
    floor: (1.93) skip the oversampling wherever the sample peaks stay more than 6 dB below it (between-sample peaks
    there can't reach it) - most of a song, so the limiter and the meter run several times faster."""
    a = np.max(np.abs(x), axis=0) if x.ndim == 2 else np.abs(x)
    n = a.shape[-1]
    out = a.astype(np.float64, copy=True)
    B = 2048
    nb = (n + B - 1) // B
    if floor is not None:
        bm = np.pad(a, (0, nb * B - n)).reshape(nb, B).max(axis=1)
        hot = bm > float(floor) * 0.5
    else:
        hot = np.ones(nb, dtype=bool)
    i = 0
    P = 64
    while i < nb:                                          # runs of blocks that need the oversampled look
        if not hot[i]:
            i += 1
            continue
        j = i
        while j < nb and hot[j] and (j - i) * B < chunk:
            j += 1
        s0, s1 = i * B, min(n, j * B)
        lo, hi = max(0, s0 - P), min(n, s1 + P)
        up = signal.resample_poly(x[..., lo:hi], os, 1, axis=-1)   # (scipy's full-length filter: exact on full-band material)
        up = np.max(np.abs(up), axis=0) if up.ndim == 2 else np.abs(up)
        m = up[:(hi - lo) * os].reshape(-1, os).max(axis=1)
        out[s0:s1] = np.maximum(out[s0:s1], m[s0 - lo:s0 - lo + (s1 - s0)])
        i = j
    return out


def true_peak(x, os=4):
    """The highest inter-sample peak (linear), without upsampling the whole song at once."""
    if not x.size:
        return 0.0
    sp = float(np.max(np.abs(x)))
    return float(np.max(true_peak_env(x, os, floor=sp)))


def limiter(x, ceiling_db=-1.0, lookahead=0.005, release=0.08, hold=0.012, os=4):
    c = 10 ** (ceiling_db / 20)
    a = np.max(np.abs(x), axis=0)
    if x.shape[-1] > 64 and os > 1:                      # true-peak detection: the waveform between the samples (4x
        a = np.maximum(a, true_peak_env(x, os, floor=c))   # oversampled) can swing ~1-2 dB above the sample peaks on
                                                         # bright, dense masters - the limiter sees those peaks too
    W = int(lookahead * SR) | 1
    pk = maximum_filter1d(a, size=max(2 * W + 1, int(hold * SR) | 1))   # held over ~half a bass cycle: no audio-rate gain
    g = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    B = 32
    n = len(g)
    nb = int(np.ceil(n / B))
    gb = np.pad(g, (0, nb * B - n), constant_values=1.0).reshape(nb, B).min(axis=1)
    cr = np.exp(-B / (release * SR))
    out = np.empty(nb)
    y = 1.0
    for i in range(nb):
        v = gb[i]
        y = v if v < y else v + (y - v) * cr
        out[i] = y
    gs = uniform_filter1d(np.repeat(out, B)[:n], size=W)
    del pk, g, a
    y = x * gs
    return np.clip(y, -c, c, out=y)


def k_weight(x):
    """ITU-R BS.1770 K-weighting, the spec's two filters re-derived exactly for this sample rate (the same way the
    reference meters do). The plain cookbook shelf it replaces read ~0.2 dB low on a 1 kHz tone."""
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = np.tan(np.pi * f0 / SR)
    Vh = 10 ** (G / 20)
    Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b1 = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    a1 = [1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = np.tan(np.pi * f0 / SR)
    a0 = 1 + K / Q + K * K
    a2 = [1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    y = signal.lfilter(b1, a1, x, axis=-1)
    return signal.lfilter([1.0, -2.0, 1.0], a2, y, axis=-1)


def lufs(x):
    """Integrated loudness, ITU-R BS.1770 (K-weighting + gating)."""
    if x.ndim == 2:                                   # (1.90: channel by channel - same result, a fraction of the memory)
        e = np.zeros(x.shape[1])
        for c in range(x.shape[0]):
            yc = k_weight(x[c])
            e += yc * yc
        del yc
    else:
        e = k_weight(x) ** 2
    n_ = e.shape[0]
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    cs = np.concatenate([[0.0], np.cumsum(e)])
    del e
    starts = np.arange(0, n_ - blk, hop)
    if len(starts) == 0:
        return -70.0
    z = (cs[starts + blk] - cs[starts]) / blk
    lk = -0.691 + 10 * np.log10(z + 1e-12)
    z1 = z[lk > -70]
    if len(z1) == 0:
        return -70.0
    rel = -0.691 + 10 * np.log10(z1.mean()) - 10
    z2 = z[lk > rel]
    return float(-0.691 + 10 * np.log10(z2.mean()))


def active_rms_db(x):
    blk = int(0.05 * SR)
    m = x if x.ndim == 1 else np.mean(x ** 2, axis=0)
    if x.ndim == 1:
        m = x ** 2
    nb = len(m) // blk
    if nb == 0:
        return -120.0
    pw = m[:nb * blk].reshape(nb, blk).mean(axis=1)
    if pw.max() <= 0:
        return -120.0
    act = pw[pw > pw.max() * 1e-4]
    return float(10 * np.log10(act.mean() + 1e-15))


def sweep_region(buf, s0, s1, kind, f0, f1, steps=8):
    s0 = max(0, s0)
    s1 = min(buf.shape[1], s1)
    if s1 - s0 < SR // 10:
        return
    pre = min(s0, SR // 2)
    seg = buf[:, s0 - pre:s1].astype(np.float64)
    n = s1 - s0
    cuts = np.geomspace(f0, f1, steps)
    pos = np.linspace(0, steps - 1, n)
    out = np.zeros((2, n))
    f = lp if kind == 'lp' else hp
    for i, fc in enumerate(cuts):
        w = np.clip(1 - np.abs(pos - i), 0, 1)
        if w.max() == 0:
            continue
        out += f(seg, fc)[:, pre:] * w
    buf[:, s0:s1] = out




def svf_sweep(x, cut, q=0.707, mode='lowpass', block=64):
    """Time-varying resonant filter, processed in short blocks with carried state."""
    x = np.asarray(x, float)
    cut = np.broadcast_to(np.asarray(cut, float), x.shape)
    y = np.empty_like(x)
    zi = np.zeros(2)
    n = len(x)
    for s in range(0, n, block):
        e = min(n, s + block)
        fc = float(np.clip(cut[s], 20.0, SR * 0.45))
        if mode == 'bandpass':
            w = 2 * np.pi * fc / SR
            al = np.sin(w) / (2 * q)
            b = np.array([al, 0, -al]) / (1 + al)
            a = np.array([1, -2 * np.cos(w) / (1 + al), (1 - al) / (1 + al)])
        else:
            b, a = biquad(mode, fc, q)
        y[s:e], zi = signal.lfilter(b, a, x[s:e], zi=zi)
    return y


def write_wav_float(path, x):
    """32-bit float stereo WAV (no clipping) - used for DAW stems."""
    x = np.asarray(x, dtype='<f4')
    data = x.T.tobytes()
    with open(path, 'wb') as f:
        f.write(b'RIFF')
        f.write((4 + 26 + 12 + 8 + len(data)).to_bytes(4, 'little'))
        f.write(b'WAVE')
        f.write(b'fmt ' + (18).to_bytes(4, 'little'))
        f.write((3).to_bytes(2, 'little') + (2).to_bytes(2, 'little') + SR.to_bytes(4, 'little'))
        f.write((SR * 8).to_bytes(4, 'little') + (8).to_bytes(2, 'little') + (32).to_bytes(2, 'little'))
        f.write((0).to_bytes(2, 'little'))
        f.write(b'fact' + (4).to_bytes(4, 'little') + (x.shape[1]).to_bytes(4, 'little'))
        f.write(b'data' + len(data).to_bytes(4, 'little'))
        f.write(data)




def scale_wav_float(path, g):
    """Scale a stem written by write_wav_float in place (its header is always 58 bytes)."""
    if g == 1.0 or not os.path.exists(path):
        return
    m = np.memmap(path, dtype='<f4', mode='r+', offset=58)
    m *= np.float32(g)
    m.flush()
    del m
def write_wav(path, x, rng=None, bits=16):
    """Stereo WAV. 16-bit gets TPDF dither (the noise that keeps quiet fades smooth at 16 bits); 24-bit needs none."""
    rng = rng or RNG
    x = np.clip(np.asarray(x, dtype=np.float64), -1, 1)
    if bits == 24:
        i32 = np.clip(np.round(x * 8388607), -8388608, 8388607).astype('<i4')
        raw = i32.T.reshape(-1).view(np.uint8).reshape(-1, 4)[:, :3].tobytes()   # little-endian: drop the top byte
        with wave.open(path, 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(3)
            w.setframerate(SR)
            w.writeframes(raw)
        return path
    d = (rng.random(x.shape) - rng.random(x.shape)) / 32768.0
    i16 = np.clip(np.round((x + d) * 32767), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(i16.T.tobytes())
    return path


def write_flac(wav_path, flac_path):
    """Lossless FLAC (24-bit source -> 24-bit FLAC) through ffmpeg; None when ffmpeg isn't installed."""
    import shutil
    import subprocess
    ff = shutil.which('ffmpeg')
    if not ff:
        return None
    try:
        subprocess.run([ff, '-y', '-loglevel', 'error', '-i', wav_path, '-c:a', 'flac', '-compression_level', '8', flac_path],
                       check=True, timeout=600, **({'creationflags': 0x08000000} if os.name == 'nt' else {}))
        return flac_path
    except Exception:
        return None


def _id3(tags):
    """A small ID3v2.4 tag (UTF-8 text frames) - lameenc writes bare MP3 frames."""
    ids = {'title': 'TIT2', 'artist': 'TPE1', 'genre': 'TCON', 'composer': 'TCOM'}

    def syncsafe(n):
        return bytes([(n >> 21) & 0x7f, (n >> 14) & 0x7f, (n >> 7) & 0x7f, n & 0x7f])
    body = b''
    for k, v in (tags or {}).items():
        if k in ids and v:
            data = b'\x03' + str(v).encode('utf-8')
            body += ids[k].encode() + syncsafe(len(data)) + b'\x00\x00' + data
    return b'ID3\x04\x00\x00' + syncsafe(len(body)) + body if body else b''


def mp3_encoder():
    """'ffmpeg', 'lameenc' (bundled with the installer) or None."""
    import shutil
    if shutil.which('ffmpeg') and not os.environ.get('STUDIOLAB_NO_FFMPEG'):     # (the env var: installer self-test)
        return 'ffmpeg'
    try:
        import lameenc  # noqa: F401
        return 'lameenc'
    except ImportError:
        return None


def write_mp3(wav_path, mp3_path, kbps=320, tags=None):
    """Encode a 16-bit WAV to MP3 with ffmpeg, or lameenc when ffmpeg isn't installed. Returns mp3_path or None."""
    enc = mp3_encoder()
    if enc == 'ffmpeg':
        import subprocess
        from .proc import NOWIN
        meta = []
        for k, v in (tags or {}).items():
            meta += ['-metadata', f'{k}={v}']
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav_path, '-codec:a', 'libmp3lame', '-b:a', f'{kbps}k']
                       + meta + [mp3_path], capture_output=True, **NOWIN)
    elif enc == 'lameenc':
        import lameenc
        with wave.open(wav_path, 'rb') as w:
            ch, sr, pcm = w.getnchannels(), w.getframerate(), w.readframes(w.getnframes())
        e = lameenc.Encoder()
        e.set_bit_rate(int(kbps))
        e.set_in_sample_rate(sr)
        e.set_channels(ch)
        e.set_quality(2)
        data = e.encode(pcm) + e.flush()
        with open(mp3_path, 'wb') as f:
            f.write(_id3(tags) + bytes(data))
    else:
        return None
    return mp3_path if os.path.exists(mp3_path) else None


def seed_rng(seed):
    global RNG
    RNG = np.random.default_rng(seed)
    return RNG


def get_rng():
    return RNG
