"""Studio Lab 2.0 guitars: played like a real guitar part, then through a real rig.

Why the old synth guitars sounded synthetic:
  * every note of a chord was distorted on its own and then summed - a real amp distorts the whole chord at once,
    and that intermodulation is what makes a power chord thick;
  * the left and right channels were one take, so a "double-tracked" wall was a mono note made wide;
  * the cabinet was a plain low-pass.

So these instruments return a clean DI: two separately played takes (left / right), each with its own pick attack,
pick position, a few cents of tuning and a few milliseconds of timing between them. The renderer then runs the whole
part through the guitar's rig - an amp, a speaker cabinet and the effects the style uses - in `guitar_rig()`.

    rhythmgtr   rock rhythm: humbucker into a cranked plexi-style amp, 4x12 greenback          classic / hard / punk rock
    metalgtr    down-tuned high gain: a tight boost, two hard stages, scooped mids, V30 4x12, gate   metal, nu metal, doom
    grungegtr   fuzz / big-muff into a worn 2x12: wooly, scooped, a little loose and out of tune    grunge, 90s alt, sludge
    telegtr     Telecaster bridge pickup: bright twang + snap, a compressor, slapback and a little spring    country
    jangle      clean chorused single-coil arpeggios through a clean combo                    indie, 90s verses, dream pop
    dreadnought steel-string acoustic recorded with two mics (body + 12th fret), strum noise and the room   folk, country
"""
import zlib

import numpy as np
from scipy import signal

from .dsp import SR, eq, hp, lp, mtof
from .instruments import GM_PROGRAM, INSTRUMENT_INFO, INSTRUMENTS, ROLE_CHOICES, _bass_exc, _guitar_body
from . import va as _va


def _rng(name, m, dur, k=0):
    return np.random.default_rng(zlib.crc32(f'{name}|{m:.2f}|{dur:.3f}|{k}'.encode()))


def _take(name, m, dur, p, mod, k, t60=4.0, bright=0.75, pickup=0.12, tail=0.12, tone=1.3):
    """One played take of a note on an electric guitar (clean, as if from the DI box)."""
    r = _rng(name, m, dur, k)
    cents = (r.random() - 0.5) * (9.0 if k else 4.0) + float(p.get('detune', 0.0))
    f = float(mtof(m)) * 2 ** (cents / 1200)
    pm = mod == 'pm'
    gate = int(max(dur, 0.04) * SR)
    n = gate + int((0.035 if pm else tail) * SR)
    exc = _bass_exc(f, 'pick', tone * (0.85 + 0.3 * r.random()) * (0.75 if pm else 1.0))
    y = _va.string(f, n, exc, t60=(0.16 if pm else t60) * (196.0 / max(f, 60)) ** 0.4, bright=(0.3 if pm else bright),
                   gate=gate, mute_t60=0.05, pickup=float(np.clip(pickup + (r.random() - 0.5) * 0.05, 0.02, 0.45)))
    t = np.arange(n) / SR
    y = y + 0.025 * hp(r.standard_normal(n), 2500) * np.exp(-t * 400)            # the pick scraping the string
    y[gate:] *= np.exp(-np.arange(n - gate) / (0.015 * SR))
    w = min(n, int(0.12 * SR))
    y = y / (np.sqrt(np.mean(y[:w] ** 2)) + 1e-9) * 0.28                          # every string as loud
    d = int((0.0 if not k else 0.003 + 0.011 * r.random()) * SR)                  # the double lands a few ms late
    if d:
        y = np.concatenate([np.zeros(d), y])[:n]
    return hp(y, 60)


def _di(name, m, dur, p, mod, **kw):
    a = _take(name, m, dur, p, mod, 0, **kw)
    b = _take(name, m, dur, p, mod, 1, **dict(kw, pickup=kw.get('pickup', 0.12) + 0.05))
    return np.vstack([a, b])


def g_rhythm(m, dur, p, glide=None, mod=None):
    return _di('rhythmgtr', m, dur, p, mod, t60=4.0, bright=0.75, pickup=0.14)


def g_metal(m, dur, p, glide=None, mod=None):
    return _di('metalgtr', m - int(p.get('drop', 0)), dur, p, mod, t60=3.5, bright=0.85, pickup=0.1, tail=0.05, tone=1.6)


def g_grunge(m, dur, p, glide=None, mod=None):
    return _di('grungegtr', m, dur, dict(p, detune=p.get('detune', 6.0)), mod, t60=4.5, bright=0.6, pickup=0.22, tail=0.18,
               tone=1.1)


def g_tele(m, dur, p, glide=None, mod=None):
    return _di('telegtr', m, dur, p, mod, t60=2.8, bright=0.9, pickup=0.07, tail=0.08, tone=1.8)


def g_jangle(m, dur, p, glide=None, mod=None):
    return _di('jangle', m, dur, p, mod, t60=5.0, bright=0.85, pickup=0.12, tail=0.5, tone=1.5)


def g_dreadnought(m, dur, p, glide=None, mod=None):
    """Steel-string acoustic, two mics: one at the body (warm, boomy), one at the 12th fret (bright, airy), so left
    and right are the same performance heard from two places - plus the strum noise and finger squeak."""
    f = float(mtof(m))
    r = _rng('dreadnought', m, dur)
    pm = mod == 'pm'
    gate = int(max(dur, 0.05) * SR)
    n = gate + int((0.08 if pm else 0.9) * SR)
    y = _va.string(f, n, _bass_exc(f, 'pick', p.get('tone', 1.25)), t60=(0.25 if pm else 6.5) * (110.0 / max(f, 60)) ** 0.5,
                   bright=0.35 if pm else 0.8, gate=gate, mute_t60=0.22, pickup=0.0)
    t = np.arange(n) / SR
    strum = hp(r.standard_normal(n), 1800) * np.exp(-t * 140) * 0.05
    body = _guitar_body(y + strum * 0.5)
    fret = eq(hp(y + strum, 180), 'peak', 5500, 0.9, 4.0)
    fret = lp(fret, 13000)
    mix = 0.55 * body / (np.max(np.abs(body)) + 1e-9) + 0.45 * fret / (np.max(np.abs(fret)) + 1e-9)
    if dur > 0.5 and r.random() < 0.25:                                          # a finger squeak sliding to the next
        sq = gate - int(0.05 * SR)
        if sq > 0:
            k = min(n - sq, int(0.06 * SR))
            tt = np.arange(k) / SR
            mix[sq:sq + k] += 0.02 * np.sin(2 * np.pi * (2000 + 3000 * tt / 0.06) * tt) * np.hanning(k)
    nb, nf = body / (np.max(np.abs(body)) + 1e-9), fret / (np.max(np.abs(fret)) + 1e-9)
    return np.vstack([0.6 * nb + 0.4 * mix, 0.6 * nf + 0.4 * mix]) * 0.85


# ------------------------------------------------------------------------------------------------------------- rigs
RIGS = {
    'rhythmgtr': dict(amp='plexi', gain=9.0, cab='greenback', out=-3.6),
    'metalgtr': dict(amp='highgain', gain=30.0, cab='v30', gate=True, out=-3.4),
    'grungegtr': dict(amp='fuzz', gain=14.0, cab='worn', out=-5.6),
    'telegtr': dict(amp='clean', gain=1.6, cab='combo', comp=True, slap=True, spring=0.18, width=0.55, out=-4.6),
    'jangle': dict(amp='clean', gain=1.2, cab='combo', comp=True, chorus=True, spring=0.12, width=0.8, out=-7.0),
}


def _cab(y, kind):
    """A speaker cabinet as its frequency response: the low resonance, the cone break-up mids and presence peak,
    the dip a close mic sees off-axis, and the steep top end - plus a 0.5 ms floor reflection."""
    lo, lo_g, pres, pres_g, top, notch = {'v30': (95, 5.0, 2500, 4.5, 5200, 4300), 'greenback': (110, 3.5, 1900, 4.0, 5600, 3600),
                                         'worn': (120, 3.0, 1400, 2.0, 4600, 3200), 'combo': (130, 1.5, 3000, 2.5, 7500, 5200)}[kind]
    y = hp(y, 75, 2)
    y = eq(y, 'peak', lo, 1.2, lo_g)
    y = eq(y, 'peak', 400 if kind != 'combo' else 500, 1.0, -2.5)
    y = eq(y, 'peak', pres, 1.1, pres_g)
    y = eq(y, 'peak', notch, 3.0, -5.0)
    b, a = signal.butter(4, min(top, SR / 2 - 100) / (SR / 2))
    y = signal.lfilter(b, a, y, axis=-1)
    d = int(0.0005 * SR)
    y[..., d:] += 0.25 * y[..., :-d]
    return y


def _amp(y, kind, gain):
    if kind == 'clean':
        return np.tanh(y * gain) / np.tanh(gain)
    if kind == 'plexi':                                   # one cranked stage, asymmetric (valve), mid-forward
        y = hp(y, 110)
        y = np.tanh(y * gain + 0.2) - np.tanh(0.2)
        return eq(y, 'peak', 800, 0.8, 3.0)
    if kind == 'fuzz':                                    # a fuzz pedal into a pushed amp: square-ish, scooped mids
        y = hp(y, 60)
        y = np.tanh(y * gain * 2.0)
        y = eq(y, 'peak', 1000, 0.6, -7.0)
        return np.tanh(eq(y, 'peak', 200, 0.8, 3.0) * 1.8)
    # high gain: a tube-screamer in front cuts the lows so the chugs stay tight, then two hard stages
    y = eq(hp(y, 500, 1), 'peak', 750, 0.8, 6.0)
    y = np.tanh(y * gain + 0.08) - np.tanh(0.08)
    y = np.tanh(hp(y, 50) * 3.0)
    return eq(eq(y, 'peak', 600, 0.7, -5.0), 'peak', 100, 0.9, 4.0)


def guitar_rig(buf, rig, spb=0.5):
    """The whole guitar part (stereo DI: two takes) through the rig - both sides through their own amp, so chords
    distort together like on a real amp, then the cabinet and the style's effects."""
    x = np.asarray(buf, dtype=np.float64)
    if x.ndim == 1:
        x = np.vstack([x, x])
    peak = float(np.max(np.abs(x)))
    if peak < 1e-7:
        return buf
    y = x / peak
    if rig.get('comp'):                                   # a compressor in front: the country / clean "snap"
        env = np.maximum(lp(np.abs(y), 30), 1e-4)
        y = y * np.minimum(1.0, (env / 0.35) ** (-0.6))
        y = y / (np.max(np.abs(y)) + 1e-9)
    if rig.get('chorus'):
        n = y.shape[1]
        t = np.arange(n) / SR
        for c, ph in ((0, 0.0), (1, 1.6)):
            d = (0.007 + 0.002 * np.sin(2 * np.pi * 0.8 * t + ph)) * SR
            i = np.clip(np.arange(n) - d, 0, n - 1)
            i0 = i.astype(np.int64)
            fr = i - i0
            i1 = np.minimum(i0 + 1, n - 1)
            y[c] = 0.7 * y[c] + 0.45 * (y[c][i0] * (1 - fr) + y[c][i1] * fr)
    y = _amp(y, rig['amp'], float(rig.get('gain', 8.0)))
    y = _cab(y, rig['cab'])
    if rig.get('gate'):                                   # the gate: silence between chugs is part of the groove
        env = lp(np.max(np.abs(y), axis=0), 60)
        thr = 0.04 * float(np.max(env) + 1e-9)
        g = np.clip((env - thr) / thr, 0, 1)
        y = y * lp(g, 200)
    if rig.get('slap'):                                   # slapback: one repeat ~110 ms, darker, a little to the side
        d = int(0.11 * SR)
        e = lp(y, 3500)
        y[0, d:] += 0.28 * e[1, :-d]
        y[1, d:] += 0.28 * e[0, :-d]
    if rig.get('spring'):                                 # a short drippy spring: a few dispersive echoes
        amt = float(rig['spring'])
        s = np.zeros_like(y)
        for k, (ms, g) in enumerate(((23, 0.5), (37, 0.4), (53, 0.32), (71, 0.25), (97, 0.18), (131, 0.12))):
            d = int(ms * 0.001 * SR)
            s[:, d:] += g * y[::(-1 if k % 2 else 1), :-d]           # alternate sides: the spring's width
        s = eq(hp(lp(s, 4000), 250), 'peak', 2200, 2.0, 4.0)
        y = y + amt * s
    w = float(rig.get('width', 1.0))                      # (a single lead / country guitar: not a hard-panned wall)
    mid, side = (y[0] + y[1]) * 0.5, hp((y[0] - y[1]) * 0.5 * w, 160, 2)   # the lows stay in the middle (mono-safe)
    y = np.vstack([mid + side, mid - side])
    y = y / (np.max(np.abs(y)) + 1e-9) * peak * 10 ** (float(rig.get('out', 0.0)) / 20)   # level-matched to 1.x
    return y.astype(np.float32)


NEW = {
    'rhythmgtr': (g_rhythm, 'Rock rhythm guitar (double-tracked, plexi amp, 4x12)', 29, ('chords', 'arp', 'lead')),
    'metalgtr': (g_metal, 'Metal guitar (double-tracked, high gain, V30 4x12, gated)', 30, ('chords', 'arp', 'lead', 'bass')),
    'grungegtr': (g_grunge, 'Grunge guitar (fuzz, scooped, a little loose)', 30, ('chords', 'arp', 'lead')),
    'telegtr': (g_tele, 'Telecaster twang (compressed, slapback, spring)', 27, ('chords', 'arp', 'lead')),
    'jangle': (g_jangle, 'Jangly clean guitar (chorus, clean combo)', 27, ('chords', 'arp', 'lead')),
    'dreadnought': (g_dreadnought, 'Acoustic guitar - dreadnought, two mics', 25, ('chords', 'arp', 'lead')),
}
for _name, (_fn, _info, _gm, _roles) in NEW.items():
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES.setdefault(_role, []):
            ROLE_CHOICES[_role].append(_name)
