"""Low-level DSP: oscillators, filters, envelopes, dynamics, loudness, file writing."""
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
    out = np.empty_like(x)
    for c in range(2):
        out[c] = signal.oaconvolve(x[c], ir[c])[:x.shape[1]]
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


def compressor(x, thresh=-18.0, ratio=3.0, attack=0.01, release=0.15, knee=6.0, win=0.005):
    pw = uniform_filter1d(np.mean(x ** 2, axis=0), size=max(1, int(win * SR)))
    ldb = 10 * np.log10(pw + 1e-12) + 3.0  # +3 so a sine's rms reads near its peak
    over = ldb - thresh
    slope = 1 - 1 / ratio
    gr = np.where(over <= -knee / 2, 0.0,
                  np.where(over >= knee / 2, over * slope, slope * (over + knee / 2) ** 2 / (2 * knee)))
    g = _smooth_gr(gr, attack, release)
    return x * 10 ** (-g / 20)


def limiter(x, ceiling_db=-1.0, lookahead=0.005, release=0.08):
    c = 10 ** (ceiling_db / 20)
    a = np.max(np.abs(x), axis=0)
    W = int(lookahead * SR) | 1
    pk = maximum_filter1d(a, size=2 * W + 1)
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
    y = x * gs
    return np.clip(y, -c, c)


def lufs(x):
    """Integrated loudness, ITU-R BS.1770 (K-weighting + gating)."""
    y = eq(x, 'highshelf', 1681.97, 0.7072, 4.0)
    y = eq(y, 'highpass', 38.135, 0.5003)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    cs = np.concatenate([[0.0], np.cumsum(np.sum(y ** 2, axis=0))])
    starts = np.arange(0, y.shape[1] - blk, hop)
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


def write_wav(path, x, rng=None):
    """16-bit stereo WAV with TPDF dither."""
    rng = rng or RNG
    x = np.clip(np.asarray(x, dtype=np.float64), -1, 1)
    d = (rng.random(x.shape) - rng.random(x.shape)) / 32768.0
    i16 = np.clip(np.round((x + d) * 32767), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(i16.T.tobytes())


def seed_rng(seed):
    global RNG
    RNG = np.random.default_rng(seed)
    return RNG


def get_rng():
    return RNG
