"""More part effects (1.78): auto-pan, beat-repeat stutter, shimmer, tape echo, ring mod / frequency shifter,
transient shaper, de-esser, volume shaper and reverse swells.

Each takes a part's whole stereo buffer (2, n) and the renderer for timing (seconds per beat, section starts), the way
a pedal sits on a channel. They run after the older pedals in render.Renderer.render_track, in this order:
punch > de-ess > ring / shift > auto-pan > volume shaper > stutter > tape echo > shimmer > reverse swell.
"""
import numpy as np
from scipy import signal

from .dsp import SR, hp, lp, make_ir, reverb, dub_delay

KEYS = ('punch', 'deess', 'ring', 'fshift', 'autopan', 'vshape', 'stutter', 'tape', 'shimmer', 'revswell')


def apply(buf, tcfg, r):
    """Run the part's new effects (tcfg keys in KEYS). r: the Renderer (spb, song sections, beat -> sample)."""
    x = np.asarray(buf, np.float64)
    if not np.any(x):
        return buf
    if tcfg.get('punch'):
        x = punch(x, float(tcfg['punch']))
    if tcfg.get('deess'):
        x = deess(x, float(tcfg['deess']))
    if tcfg.get('ring'):
        x = ring(x, float(tcfg['ring']), r.spb)
    if tcfg.get('fshift'):
        x = freq_shift(x, float(tcfg['fshift']))
    if tcfg.get('autopan'):
        x = autopan(x, tcfg['autopan'], r.spb)
    if tcfg.get('vshape'):
        x = volume_shaper(x, float(tcfg['vshape']), r.spb)
    if tcfg.get('stutter'):
        x = stutter(x, float(tcfg['stutter']), r)
    if tcfg.get('tape'):
        x = tape_echo(x, float(tcfg['tape']), r.spb)
    if tcfg.get('shimmer'):
        x = shimmer(x, float(tcfg['shimmer']))
    if tcfg.get('revswell'):
        x = reverse_swell(x, float(tcfg['revswell']), r)
    return x.astype(np.float32)


def _env(x, ms):
    a = np.abs(x).max(axis=0)
    k = np.exp(-1.0 / max(1.0, ms * SR / 1000))
    return signal.lfilter([1 - k], [1, -k], a)


def punch(x, amt):
    """Transient shaper: the difference between a fast and a slow envelope is the attack; amt > 0 lifts it
    (snappier plucks, harder drums), amt < 0 softens it (rounder, further back). About +-6 dB at amt +-1."""
    fast, slow = _env(x, 1.0), _env(x, 30.0)
    att = np.clip((fast - slow) / (slow + 1e-6), 0, 4)
    g = 10 ** (np.clip(amt, -1, 1) * 6.0 * np.tanh(att) / 20)
    return x * g[None, :]


def deess(x, amt, lo=5000.0, hi=9500.0):
    """De-esser: the 5-9.5 kHz band is turned down only while it's loud relative to the whole voice (the 's' and
    't' sounds of a vocal or choir), by up to ~8 dB at amt 1."""
    sos = signal.butter(2, [lo / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], 'band', output='sos')
    band = signal.sosfilt(sos, x, axis=-1)
    eb, ea = _env(band, 5.0), _env(x, 5.0)
    ratio = eb / (ea + 1e-9)
    over = np.clip((ratio - 0.25) / 0.25, 0, 1)
    g = 1 - (1 - 10 ** (-8 * amt / 20)) * over
    return x - band * (1 - g)[None, :]


def ring(x, amt, spb):
    """Ring modulator: the part multiplied by a sine (a metallic, bell-like, inharmonic edge - psy, dubstep FX).
    The carrier sits at a fixed, musically odd 2.5 x the beat rate x 64 so it doesn't follow the notes."""
    n = x.shape[1]
    f = (64 * 2.5 / max(spb, 0.1)) % 900 + 120
    car = np.sin(2 * np.pi * f * np.arange(n) / SR)
    return x * (1 - amt) + x * car[None, :] * amt * 1.2


def freq_shift(x, hz):
    """Frequency shifter (single-sideband): every partial moves up (or down) by the same Hz, so harmonics stop
    being harmonic - a few Hz = a slow, phasey swirl; tens of Hz = clangorous, robotic."""
    n = x.shape[1]
    t = np.arange(n) / SR
    out = np.empty_like(x)
    for c in range(x.shape[0]):
        a = signal.hilbert(x[c])
        out[c] = np.real(a * np.exp(2j * np.pi * hz * t))
    return out


def autopan(x, spec, spb):
    """Auto-pan synced to the beat: spec = depth (0..1) or (beats per cycle, depth). A constant-power sweep left
    and right, the low end below 150 Hz left in the middle."""
    beats, depth = (spec if isinstance(spec, (list, tuple)) else (2.0, float(spec)))
    n = x.shape[1]
    lo_ = lp(x, 150)
    hi_ = x - lo_
    m = hi_.mean(axis=0)
    t = np.arange(n) / SR
    pan = 0.5 + 0.5 * float(depth) * np.sin(2 * np.pi * t / (float(beats) * spb))
    out = np.vstack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)]) * np.sqrt(2)
    side = (hi_[0] - hi_[1]) / 2
    return lo_ + out + np.vstack([side, -side]) * (1 - float(depth))


def volume_shaper(x, depth, spb, shape=2.2):
    """Volume shaper ('LFO tool'): every beat the part dips and swells back - the pumping of sidechain compression
    drawn as a curve, independent of whether a kick is playing (it keeps pumping in a breakdown)."""
    n = x.shape[1]
    t = (np.arange(n) / SR) / spb % 1.0
    g = 1 - depth * (1 - np.clip(t / 0.55, 0, 1)) ** shape
    g = np.convolve(g, np.ones(64) / 64, mode='same')    # no click at the dip
    return x * g[None, :]


def stutter(x, amt, r):
    """Beat-repeat: at the end of sections, the last beat (or two) is replaced by a 1/16 - 1/32 slice repeating
    faster and faster - the stutter fill into the next part. amt = how often (0..1) and how long."""
    rng = np.random.default_rng(int(getattr(r.opts, 'seed', 0) or 0) * 31 + 5)
    y = x.copy()
    secs = r.song.get('sections', [])
    for k, sec in enumerate(secs[:-1]):
        if rng.random() > 0.35 + 0.5 * amt:
            continue
        end_b = (sec['bar'] + sec['bars']) * 4
        beats = 2 if rng.random() < amt * 0.6 else 1
        s0 = int(r.t_of(end_b - beats, human=False) * SR)
        s1 = int(r.t_of(end_b, human=False) * SR)
        if s0 < 0 or s1 > x.shape[1] or s1 - s0 < 256:
            continue
        sl16 = (s1 - s0) // (4 * beats)
        pos = s0
        cur = sl16
        src = x[:, s0:s0 + sl16].copy()
        while pos < s1:
            ln = min(cur, s1 - pos)
            seg = src[:, :ln].copy()
            f_ = min(32, ln // 4)
            if f_ > 1:                                   # tiny fades: no clicks at the slice joins
                seg[:, :f_] *= np.linspace(0, 1, f_)[None, :]
                seg[:, -f_:] *= np.linspace(1, 0, f_)[None, :]
            y[:, pos:pos + ln] = seg
            pos += ln
            if pos > s0 + (s1 - s0) // 2:
                cur = max(sl16 // 2, 64)                 # the second half doubles up: 1/32s
    return y


def tape_echo(x, amt, spb):
    """Tape echo: dotted-1/8 repeats that get darker and more worn each time round, with the slight pitch wobble
    of the tape transport (dub, chill, lo-fi, techno)."""
    wet = dub_delay(x, 0.75 * spb, fb=0.45 + 0.25 * amt, n_rep=10, lo=250, hi=3200, drift=0.015)
    return x + wet * (0.35 + 0.4 * amt)


def _octave_up(y, grain=2048):
    """A simple octave-up pitch shifter (overlap-add of resampled grains) for the shimmer's wet signal."""
    n = len(y)
    out = np.zeros(n)
    hop = grain // 4
    w = np.hanning(grain)
    for s in range(0, n - grain, hop):
        g = y[s:s + grain] * w
        g2 = g[::2]                                       # twice the speed = an octave up, half as long
        g2 = np.concatenate([g2, g2])[:grain] * w         # fill the grain twice (smooth with the window)
        out[s:s + grain] += g2
    return out / 1.5


def shimmer(x, amt):
    """Shimmer reverb: a long, bright hall whose tail is pitched up an octave and fed into a second hall - the
    glowing, rising halo of ambient pads and melodic house / trance breakdowns."""
    ir = make_ir(4.5, predelay=0.03, bright=1.0)
    wet = reverb(hp(x, 300), ir)
    up = np.vstack([_octave_up(wet[c]) for c in range(2)])
    halo = reverb(up, make_ir(5.5, predelay=0.0, bright=1.2))
    halo = hp(halo, 900)
    return x + (0.25 * wet + 0.45 * halo) * amt


def reverse_swell(x, amt, r):
    """Reverse reverb swells into section starts: the first beat of the part's new section, drowned in reverb,
    played backwards so it rises into the downbeat."""
    y = x.copy()
    ir = make_ir(2.8, predelay=0.0, bright=0.8)
    for sec in r.song.get('sections', [])[1:]:
        s0 = int(r.t_of(sec['bar'] * 4, human=False) * SR)
        s1 = int(r.t_of(sec['bar'] * 4 + 1, human=False) * SR)
        if s1 >= x.shape[1] or not np.any(x[:, s0:s1]):
            continue
        wet = reverb(np.pad(x[:, s0:s1], ((0, 0), (0, int(2.5 * SR)))), ir)[:, ::-1]
        ln = min(wet.shape[1], s0)
        if ln < 64:
            continue
        seg = wet[:, -ln:] * np.linspace(0, 1, ln)[None, :] ** 2
        y[:, s0 - ln:s0] += seg * amt * 0.6
    return y
