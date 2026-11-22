"""Studio Lab 2.6 instruments (main already has its own bouzouki and modelled bagpipes, so those stay its own): the sounds whole groups of genres were missing.

    tonewheel    tonewheel organ - drawbars, key click, percussion - through a rotary speaker   gospel, soul, rock, jam
    rockorgan    the same organ, overdriven, rotor on fast                                         rock, blues, funk
    wahgtr       funk guitar through a wah (chicken-scratch, envelope wah)                         funk, disco, G-funk
    twelvestring 12-string jangle (octave + unison courses)                                        folk rock, indie, psych
    lapsteel     lap steel / slide guitar (bar slides into the note, glassy, a little grit)        blues, country, Hawaiian
    dobro        resonator guitar (metal cone, slide)                                              bluegrass, blues, country
    ukulele      ukulele (short nylon strings, small bright body, strummed)                        tropical, pop, indie
    dulcimer     hammered dulcimer (struck steel courses, long shimmering sustain)                 Celtic, folk, fantasy
    didgeridoo   didgeridoo (lip drone, moving mouth formants, breath pulses, overtone toots)      world, drone, ambient
    donk         donk bass (hollow, bouncy, pitched-percussion bass)                               bassline, bounce, hard house
    glitchchop   glitch chopper (buffer stutters, pitch-stepped repeats, reverse grains)           IDM, glitch pop
    omnichord    omnichord / strum plate (soft, shimmering harp-strum synth)                       chillwave, bedroom, lo-fi
    stylophone   stylophone (buzzy stylus synth, tiny speaker)                                     synth-pop, electro
    toypiano     toy piano (struck metal rods, clangy, short)                                      storybook, hauntology

PART_FX: effects that run over the whole part (like the guitar rigs), so they don't restart on every note.
"""
import zlib

import numpy as np

from .dsp import SR, mtof, lp, hp, bp, eq, soft, saw, square, sine, svf_sweep
from .instruments import INSTRUMENTS, INSTRUMENT_INFO, ROLE_CHOICES, GM_PROGRAM, _bass_exc, _guitar_body, _ms_stereo
from . import va as _va


def _rng(name, m, dur, k=0):
    return np.random.default_rng(zlib.crc32(f'{name}|{float(m):.2f}|{float(dur):.3f}|{k}'.encode()))


def _t(n):
    return np.arange(n) / SR


def _norm(y, level=0.3, win=0.15):
    w = min(len(y), int(win * SR))
    return y / (np.sqrt(np.mean(y[:w] ** 2)) + 1e-9) * level


# ----------------------------------------------------------------------------------------------- organ
DRAWBAR_RATIOS = (0.5, 1.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)       # 16' 5 1/3' 8' 4' 2 2/3' 2' 1 3/5' 1 1/3' 1'


def _tonewheel(m, dur, p, reg, perc=True, drive=1.2):
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    n = gate + int(0.03 * SR)
    t = _t(n)
    r = _rng('tw', m, dur)
    y = np.zeros(n)
    for ratio, level in zip(DRAWBAR_RATIOS, reg):
        if not level:
            continue
        fr = f * ratio
        while fr > 6000:                                   # the top tonewheels fold back an octave (foldback)
            fr /= 2
        a = level / 8.0
        y += a * (np.sin(2 * np.pi * fr * t + r.random() * 6.28) + 0.03 * np.sin(2 * np.pi * fr * 3 * t))   # near-sine wheels
    if perc:                                               # percussion: the 4' (2nd harmonic) struck and decaying
        y += 0.55 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.2)
    click = bp(r.standard_normal(n), 1200, 5000) * np.exp(-t / 0.004) * 0.35           # key contacts closing
    leak = 0.004 * np.sin(2 * np.pi * f * 7.03 * t)                                     # crosstalk from other wheels
    env = np.clip(t / 0.003, 0, 1) * np.clip((gate + int(0.012 * SR) - np.arange(n)) / (0.012 * SR), 0, 1)
    y = soft((y + leak) * env * 0.5 * drive, 1.0 + 0.5 * drive) + click * env
    return lp(hp(y, 40), 7500) * 0.32


def i_tonewheel(m, dur, p, glide=None, mod=None):
    """Tonewheel organ: nine drawbars of near-sine tonewheels (default 888000000, the gospel / jazz 'first three'),
    key click, 4' percussion, a warm tube preamp. The rotary speaker runs over the whole part (PART_FX)."""
    reg = p.get('reg', (8, 8, 8, 0, 0, 0, 0, 0, 0))
    return _tonewheel(m, dur, p, reg, perc=p.get('perc', True), drive=p.get('pre', 1.2))


def i_rockorgan(m, dur, p, glide=None, mod=None):
    """Rock organ: 888800000-ish, no percussion, the preamp pushed into growl; the rotor runs fast (PART_FX)."""
    return _tonewheel(m, dur, p, p.get('reg', (8, 8, 8, 8, 4, 0, 0, 0, 2)), perc=p.get('perc', False), drive=p.get('pre', 3.0))


def rotary(buf, speed='slow', spb=0.5):
    """Rotary speaker: a treble horn and a bass drum spinning at their own speeds (slow 'chorale' / fast 'tremolo'),
    each with the doppler pitch wobble and the level / tone swing of a speaker turning past the two mics."""
    x = np.asarray(buf, float)
    if x.ndim == 1:
        x = np.vstack([x, x])
    n = x.shape[1]
    t = _t(n)
    mono = 0.5 * (x[0] + x[1])
    low, high = lp(mono, 800, 4), hp(mono, 800, 4)
    rates = {'slow': (0.83, 0.72), 'fast': (6.7, 5.9)}.get(speed, (0.83, 0.72))
    out = np.zeros((2, n))
    for part, rate, depth_ms, am in ((high, rates[0], 0.55, 0.45), (low, rates[1], 0.25, 0.25)):
        for ch, ph in ((0, 0.0), (1, np.pi * 0.8)):
            rot = np.sin(2 * np.pi * rate * t + ph)
            d = (1.2 + depth_ms * rot) * 0.001 * SR
            i = np.clip(np.arange(n) - d, 0, n - 1)
            i0 = i.astype(np.int64)
            fr = i - i0
            i1 = np.minimum(i0 + 1, n - 1)
            v = part[i0] * (1 - fr) + part[i1] * fr
            out[ch] += v * (1 - am * 0.5 + am * 0.5 * rot)
    out = eq(out, 'peak', 2500, 1.0, 2.0)
    peak_in = float(np.max(np.abs(x))) + 1e-9
    return (out / (np.max(np.abs(out)) + 1e-9) * peak_in).astype(np.float32)


# ----------------------------------------------------------------------------------------------- guitars & strings
def _course(f, n, gate, kind='pick', t60=4.0, bright=0.8, tone=1.3, pickup=0.1, mute=0.1, seed=None):
    r = np.random.default_rng(seed)
    exc = _bass_exc(f, kind, tone * (0.85 + 0.3 * r.random()))
    return _va.string(f, n, exc, t60=t60 * (196.0 / max(f, 60)) ** 0.4, bright=bright, gate=gate, mute_t60=mute,
                      pickup=float(np.clip(pickup + (r.random() - 0.5) * 0.04, 0.02, 0.45)))


def i_wahgtr(m, dur, p, glide=None, mod=None):
    """Funk guitar, clean DI (single-coil, two takes); the wah and the clean combo are its rig (guitars2.RIGS)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    pm = mod == 'pm' or dur < 0.2
    n = gate + int((0.03 if pm else 0.12) * SR)
    seed = zlib.crc32(f'wah{m}{dur}'.encode())
    out = []
    for k in range(2):
        y = _course(f * 2 ** (((k * 7) - 3.5) / 1200), n, gate, 'pick', t60=0.25 if pm else 3.0, bright=0.4 if pm else 0.9,
                    tone=1.6, pickup=0.06, mute=0.03, seed=seed + k)
        y = y + 0.06 * hp(np.random.default_rng(seed + 9 + k).standard_normal(n), 2500) * np.exp(-_t(n) * 300)
        d = int((0.002 + 0.006 * k) * SR) if k else 0
        if d:
            y = np.concatenate([np.zeros(d), y])[:n]
        out.append(_norm(hp(y, 90), 0.28, 0.06))
    return np.vstack(out)


def i_twelvestring(m, dur, p, glide=None, mod=None):
    """12-string: every course a pair - the low four an octave apart, the top two in unison, a few cents out - so it
    rings and shimmers; strummed it's the jangle of folk rock."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(0.6 * SR)
    seed = zlib.crc32(f'12s{m}{dur}'.encode())
    oct_ = m < 62
    a = _course(f, n, gate, 'pick', t60=5.5, bright=0.85, tone=1.4, pickup=0.12, mute=0.2, seed=seed)
    b = _course(f * (2.0 if oct_ else 1.0) * 2 ** (4 / 1200), n, gate, 'pick', t60=4.5, bright=0.9, tone=1.2,
                pickup=0.08, mute=0.2, seed=seed + 1)
    d = int(0.006 * SR)
    b = np.concatenate([np.zeros(d), b])[:n]
    body = _guitar_body(a + 0.8 * b)
    air = eq(hp(a + b, 200), 'peak', 6000, 0.8, 5.0)
    L, R = _norm(body, 0.3, 0.1), _norm(air, 0.27, 0.1)
    return np.vstack([0.7 * L + 0.3 * R, 0.35 * L + 0.65 * R])


def i_lapsteel(m, dur, p, glide=None, mod=None):
    """Lap steel / slide: the bar slides into the note (from below, or from the last note with glide), shimmering
    vibrato by rocking the bar, glassy single-coil, a little amp grit."""
    f = float(mtof(m))
    n = int((dur + 0.4) * SR)
    t = _t(n)
    start = float(mtof(glide)) if glide is not None else f * 2 ** (p.get('slide', -150) / 1200)
    tau = 0.09 if glide is not None else 0.06
    fv = f + (start - f) * np.exp(-t / tau)
    fv = fv * 2 ** ((7 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) / 0.4, 0, 1)) / 1200)
    ph = 2 * np.pi * np.cumsum(fv) / SR
    x = sum(a * np.sin(k * ph) for k, a in ((1, 1.0), (2, 0.55), (3, 0.38), (4, 0.2), (5, 0.12), (6, 0.07)))
    env = np.minimum(t / 0.006, 1) * np.exp(-t / max(0.8, min(dur, 3.0) * 1.2))
    env *= np.clip((dur + 0.35 - t) / 0.12, 0, 1)
    y = soft(eq(x * env, 'peak', 2400, 1.5, 4.0) * 1.4, 1.5)
    y = y + 0.02 * hp(np.random.default_rng(int(m)).standard_normal(n), 3000) * np.exp(-t * 60)   # bar on the strings
    return _ms_stereo(lp(hp(y, 90), 6500) * 0.3, 180)


def i_dobro(m, dur, p, glide=None, mod=None):
    """Resonator guitar (dobro): a slid steel string driving an aluminium cone - nasal, metallic, honking mids, a fast
    bright attack and a ringing 'clang'."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(0.7 * SR)
    seed = zlib.crc32(f'dob{m}{dur}'.encode())
    y = _course(f, n, gate, 'pick', t60=3.0, bright=0.9, tone=1.7, pickup=0.0, mute=0.3, seed=seed)
    t = _t(n)
    if glide is not None or p.get('slide', True):
        start = float(mtof(glide)) if glide is not None else f * 2 ** (-90 / 1200)
        bend = (start / f) ** np.exp(-t / 0.05)                     # a quick slide into pitch (resampled)
        pos = np.cumsum(bend) - bend[0]
        y = np.interp(pos, np.arange(n), y, right=0.0)
    for fc, q, g in ((700, 2.0, 7.0), (1400, 3.0, 5.0), (2900, 4.0, 4.0), (250, 1.0, -4.0)):    # the cone
        y = eq(y, 'peak', fc, q, g)
    y = y + 0.15 * bp(y, 3800, 5200) * np.exp(-t * 6)
    return _ms_stereo(_norm(hp(y, 120), 0.3, 0.1), 140)


def i_ukulele(m, dur, p, glide=None, mod=None):
    """Ukulele: short nylon strings (re-entrant: high notes stay high), plucked by a thumb, a small bright body."""
    f = float(mtof(m))
    while f < 260:                                          # re-entrant tuning: nothing below middle C
        f *= 2
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(0.35 * SR)
    seed = zlib.crc32(f'uke{m}{dur}'.encode())
    y = _course(f, n, gate, 'finger', t60=1.6, bright=0.55, tone=1.2, pickup=0.0, mute=0.15, seed=seed)
    y = y + 0.03 * hp(np.random.default_rng(seed).standard_normal(n), 2000) * np.exp(-_t(n) * 200)
    for fc, q, g in ((260, 1.5, 4.0), (520, 2.0, 3.0), (1200, 1.5, 2.0), (3500, 1.0, 2.0)):        # small box
        y = eq(y, 'peak', fc, q, g)
    return _ms_stereo(_norm(hp(lp(y, 9000), 180), 0.28, 0.08), 120)


def i_bouzouki(m, dur, p, glide=None, mod=None):
    """Irish bouzouki: long-scale paired courses (bass courses with an octave string), picked - bright, ringing, a
    harmonic shimmer between the pairs; the drone-and-chord backing of Irish folk."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(1.0 * SR)
    seed = zlib.crc32(f'bzk{m}{dur}'.encode())
    a = _course(f, n, gate, 'pick', t60=6.0, bright=0.88, tone=1.5, pickup=0.1, mute=0.35, seed=seed)
    b = _course(f * (2.0 if m < 57 else 1.0) * 2 ** (5 / 1200), n, gate, 'pick', t60=5.0, bright=0.9, tone=1.3,
                pickup=0.07, mute=0.35, seed=seed + 1)
    b = np.concatenate([np.zeros(int(0.004 * SR)), b])[:n]
    y = a + 0.75 * b
    for fc, q, g in ((180, 2.0, 3.0), (900, 1.5, 2.0), (3200, 1.2, 4.0)):
        y = eq(y, 'peak', fc, q, g)
    y = _norm(hp(y, 100), 0.3, 0.1)
    return np.vstack([y, np.concatenate([np.zeros(int(0.0015 * SR)), eq(y, 'peak', 5000, 1.0, 2.0)])[:n]])


def i_dulcimer(m, dur, p, glide=None, mod=None):
    """Hammered dulcimer: each course three steel strings a few cents apart struck by a light wooden hammer, an
    undamped soundboard - long, bell-like, chorusing sustain with a halo of sympathetic strings."""
    f = float(mtof(m))
    n = int((min(dur, 2.5) + 2.0) * SR)
    seed = zlib.crc32(f'dul{m}{dur}'.encode())
    r = np.random.default_rng(seed)
    y = np.zeros(n)
    for k, c in enumerate((-4.0, 0.0, 3.5)):
        fr = f * 2 ** (c / 1200)
        exc = _bass_exc(fr, 'thumb', 1.0) * (0.7 + 0.3 * r.random())           # a hammer: hard, short
        y += _va.string(fr, n, exc, t60=7.0 * (300.0 / max(f, 80)) ** 0.3, bright=0.8, gate=None, pickup=0.0)
    t = _t(n)
    halo = sum(np.sin(2 * np.pi * f * h * t + r.random() * 6) * a for h, a in ((2, 0.05), (1.5, 0.03), (3, 0.02)))
    y = y / (np.max(np.abs(y)) + 1e-9) + halo * np.minimum(t / 0.05, 1) * np.exp(-t / 1.5)
    y = eq(hp(y, 150), 'peak', 2500, 1.0, 3.0) * np.exp(-t / 3.0)
    return _ms_stereo(lp(y, 10000) * 0.25, 220)


# ----------------------------------------------------------------------------------------------- winds & world
def i_highlandpipes(m, dur, p, glide=None, mod=None):
    """Great Highland bagpipe chanter: loud, bright conical double reed, no dynamics, notes joined (there are no
    rests on the pipes, so every note is articulated by a grace note: a quick high-G or D flick on its attack)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(0.05 * SR)
    t = _t(n)
    grace = p.get('grace', True) and dur >= 0.12
    gf = f * (2 ** (7 / 12) if (int(m) % 2) else 2 ** (12 / 12))              # a G-gracenote or a high-A flick
    g_len = 0.028
    fv = np.where(t < g_len, gf, f) if grace else np.full(n, f)
    fv = lp(fv, 400)                                                            # the finger lifts fast, not instantly
    x = square(fv, n, pw=0.22) * 0.55 + saw(fv, n) * 0.45
    y = eq(eq(eq(lp(x, 7500), 'peak', 1150, 2.0, 5.0), 'peak', 2900, 2.0, 7.0), 'peak', 4300, 3.0, 4.0)
    env = np.clip(t / 0.004, 0, 1) * np.clip((gate + int(0.04 * SR) - np.arange(n)) / (0.04 * SR), 0, 1)
    return _ms_stereo(soft(hp(y, 250) * env * 0.55, 1.4) * 0.3, 150)


def i_didgeridoo(m, dur, p, glide=None, mod=None):
    """Didgeridoo: a buzzing lip drone through a long tube, the mouth reshaping its formants in a rhythmic
    'wah-oo-wah', breath pulses from circular breathing, and now and then an overtone 'toot'."""
    f = float(mtof(m))
    while f > 110:
        f /= 2
    n = int((dur + 0.25) * SR)
    t = _t(n)
    r = _rng('didj', m, dur)
    fv = f * 2 ** ((3 * np.sin(2 * np.pi * 0.31 * t + r.random() * 6)) / 1200)
    src = square(fv, n, pw=0.12) + 0.5 * saw(fv, n)
    rate = r.choice([2.0, 3.0, 4.0])
    mouth = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t + r.random() * 6) ** 3
    f1 = 300 + 700 * mouth
    f2 = 1100 + 900 * (1 - mouth)
    y = svf_sweep(src, f1, q=4.0, mode='bandpass') * 1.4 + svf_sweep(src, f2, q=6.0, mode='bandpass') * 0.8 + lp(src, 180) * 0.6
    breath = (np.sin(2 * np.pi * rate / 2 * t) > 0.93) * 1.0
    y = y * (1 - 0.35 * lp(breath, 30)) + hp(r.standard_normal(n), 800) * lp(breath, 40) * 0.08
    if dur > 1.0 and r.random() < 0.5:                                         # an overtone 'toot'
        k = int(r.uniform(0.3, 0.7) * n)
        w = min(int(0.18 * SR), n - k)
        y[k:k + w] += 0.5 * np.sin(2 * np.pi * f * 2.6 * t[:w]) * np.hanning(w)
    env = np.clip(t / 0.08, 0, 1) * np.clip((dur + 0.25 - t) / 0.2, 0, 1)
    return _ms_stereo(soft(y * env * 0.9, 1.2) * 0.32, 260)


# ----------------------------------------------------------------------------------------------- synths
def i_donk(m, dur, p, glide=None, mod=None):
    """Donk: the hollow, bouncy pitched-percussion bass of bassline, scouse house and hard bounce - a pulse with a
    fast pitch drop through a resonant 'tok' formant, over a short round sub."""
    f = float(mtof(m))
    n = int((min(dur, 0.5) + 0.05) * SR)
    t = _t(n)
    fv = f * (1 + 1.6 * np.exp(-t / 0.012))
    tone = square(fv, n, pw=0.3)
    tok = svf_sweep(tone, np.maximum(f * 3.2, 500.0) * (1 + 1.2 * np.exp(-t / 0.02)), q=6.0, mode='bandpass')
    body = sine(f * (1 + 0.4 * np.exp(-t / 0.01)), n)
    env = np.exp(-t / p.get('decay', 0.11))
    y = (tok * 1.3 + body * 0.9) * env * np.clip(t / 0.001, 0, 1)
    return soft(hp(y, 35) * 0.9, 1.6) * 0.5


def i_glitchchop(m, dur, p, glide=None, mod=None):
    """Glitch chopper: a bright FM / saw tone cut into a buffer - stutter repeats, pitch-stepped slices, reversed grains
    and dropouts, different on every note (seeded), so a held note is a little glitch phrase."""
    f = float(mtof(m))
    n = int(max(0.06, dur) * SR)
    r = _rng('glitch', m, dur)
    src_n = int(0.25 * SR)
    ts = _t(src_n)
    src = 0.6 * saw(f, src_n) + 0.4 * np.sin(2 * np.pi * f * ts + 2.5 * np.sin(2 * np.pi * f * 2 * ts) * np.exp(-ts / 0.06))
    src = lp(src, 7000) * np.exp(-ts / 0.2)
    y = np.zeros(n)
    pos = 0
    slices = [0.016, 0.031, 0.0625, 0.125]
    while pos < n:
        L = min(n - pos, int(r.choice(slices) * SR * (p.get('spb', 0.5) / 0.5)))
        if L <= 8:
            break
        kind = r.choice(['play', 'repeat', 'pitch', 'reverse', 'drop'], p=[0.3, 0.3, 0.2, 0.12, 0.08])
        seg = src[:L] if L <= src_n else np.pad(src, (0, L - src_n))
        if kind == 'pitch':
            k = 2 ** (r.choice([-12, -5, 7, 12]) / 12)
            seg = np.interp(np.arange(L) * k, np.arange(len(seg)), seg, right=0.0)
        elif kind == 'reverse':
            seg = seg[::-1]
        elif kind == 'repeat':
            g = max(16, L // r.choice([2, 4, 8]))
            seg = np.tile(seg[:g], L // g + 1)[:L]
        elif kind == 'drop':
            seg = np.zeros(L)
        w = min(64, L // 4)
        seg = seg.copy()
        seg[:w] *= np.linspace(0, 1, w)
        seg[-w:] *= np.linspace(1, 0, w)
        if r.random() < 0.25:
            q = 2 ** r.integers(3, 6)
            seg = np.round(seg * q) / q
        y[pos:pos + L] = seg[:L]
        pos += L
    return _ms_stereo(soft(hp(y, 120) * 1.2, 1.3) * 0.3, 90)


def i_omnichord(m, dur, p, glide=None, mod=None):
    """Omnichord / strum plate: the soft, chiming harp-strum voice - a hollow square-and-sine tone with a gentle pluck,
    a slow tremolo shimmer and a lot of chorus. Play it as an arp (or chords with strum) for the strum-plate sweep."""
    f = float(mtof(m))
    n = int((min(dur, 2.0) + 1.0) * SR)
    t = _t(n)
    x = 0.5 * square(f, n, pw=0.5) + 0.6 * sine(f, n) + 0.25 * sine(f * 2.003, n)
    x = lp(x, 3200)
    env = np.minimum(t / 0.004, 1) * np.exp(-t / 1.1)
    trem = 1 - 0.18 * (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * t))
    y = x * env * trem
    L = y + 0.6 * np.roll(y, int(0.011 * SR))
    R = y + 0.6 * np.roll(y, int(0.017 * SR))
    return np.vstack([L, R]) * 0.18


def i_stylophone(m, dur, p, glide=None, mod=None):
    """Stylophone: a stylus on a metal keyboard - a raw, buzzy square wave, no envelope but on / off, a slight wobble,
    out of a tiny speaker (no lows, honky mids)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    n = gate + int(0.01 * SR)
    t = _t(n)
    fv = f * 2 ** ((p.get('vib', 9) * np.sin(2 * np.pi * 6.0 * t) * np.clip((t - 0.15) / 0.2, 0, 1)) / 1200)
    x = square(fv, n, pw=0.42) + 0.15 * saw(fv * 1.003, n)
    y = bp(x, 380, 4200)
    y = eq(eq(y, 'peak', 1100, 1.8, 6.0), 'peak', 2600, 3.0, 3.0)
    env = np.clip(t / 0.002, 0, 1) * np.clip((gate - np.arange(n)) / (0.006 * SR) + 1, 0, 1)
    return _ms_stereo(soft(y * env, 1.6) * 0.22, 60)


def i_toypiano(m, dur, p, glide=None, mod=None):
    """Toy piano: small hammers striking metal rods - a clangy, inharmonic, glassy tone (the rod's partials are not
    harmonics), a wooden thunk, and a short, slightly uneven decay."""
    f = float(mtof(m))
    n = int((min(dur, 1.2) + 0.6) * SR)
    t = _t(n)
    r = _rng('toy', m, dur)
    parts = ((1.0, 1.0, 0.9), (2.0, 0.3, 0.5), (4.1, 0.18, 0.25), (6.27, 0.22, 0.15), (9.9, 0.08, 0.08))
    y = sum(a * np.sin(2 * np.pi * f * k * (1 + (r.random() - 0.5) * 0.0008 * (k > 1)) * t) * np.exp(-t / d) for k, a, d in parts)
    thunk = lp(r.standard_normal(n), 900) * np.exp(-t / 0.008) * 0.5
    y = (y + thunk) * np.minimum(t / 0.0015, 1)
    return _ms_stereo(hp(eq(y, 'peak', 3000, 1.0, 3.0), 200) * 0.28, 110)


NEW = {
    'tonewheel': (i_tonewheel, 'Tonewheel organ + rotary speaker (drawbars, click, percussion)', ('chords', 'pad', 'lead', 'arp'), 16, 'organ'),
    'rockorgan': (i_rockorgan, 'Rock organ (overdriven tonewheel, fast rotor)', ('chords', 'pad', 'lead'), 17, 'organ'),
    'wahgtr': (i_wahgtr, 'Wah funk guitar (chicken-scratch, envelope wah)', ('chords', 'arp', 'lead'), 28, 'guitar'),
    'twelvestring': (i_twelvestring, '12-string guitar (jangling octave courses)', ('chords', 'arp', 'lead'), 25, 'guitar'),
    'lapsteel': (i_lapsteel, 'Lap steel / slide guitar', ('lead', 'arp', 'chords'), 26, 'guitar'),
    'dobro': (i_dobro, 'Dobro / resonator guitar (slide, metal cone)', ('lead', 'arp', 'chords'), 25, 'guitar'),
    'ukulele': (i_ukulele, 'Ukulele', ('chords', 'arp', 'lead'), 24, 'guitar'),
    'dulcimer': (i_dulcimer, 'Hammered dulcimer (shimmering struck steel)', ('arp', 'lead', 'chords'), 15, 'mallet'),
    'didgeridoo': (i_didgeridoo, 'Didgeridoo (lip drone, moving formants)', ('bass', 'pad'), 109, 'world'),
    'donk': (i_donk, 'Donk bass (hollow, bouncy - bassline / bounce)', ('bass',), 38, 'bass'),
    'glitchchop': (i_glitchchop, 'Glitch chopper (stutters, pitch-stepped slices)', ('lead', 'arp'), 99, 'lead'),
    'omnichord': (i_omnichord, 'Omnichord / strum plate (shimmering harp-strum synth)', ('arp', 'chords', 'pad'), 46, 'keys'),
    'stylophone': (i_stylophone, 'Stylophone (buzzy stylus synth)', ('lead', 'arp'), 80, 'lead'),
    'toypiano': (i_toypiano, 'Toy piano (clangy metal rods)', ('lead', 'arp', 'chords'), 8, 'keys'),
}
for _k, (_fn, _info, _roles, _gm, _cat) in NEW.items():
    INSTRUMENTS[_k] = _fn
    INSTRUMENT_INFO[_k] = _info
    GM_PROGRAM[_k] = _gm
    for _r in _roles:
        if _r in ROLE_CHOICES and _k not in ROLE_CHOICES[_r]:
            ROLE_CHOICES[_r].append(_k)

# whole-part effects (render.py runs them like the guitar rigs)
def _rot(default):
    def fx(buf, tcfg, spb):
        return rotary(buf, (tcfg.get('p') or {}).get('rotor', default(tcfg)), spb)
    return fx


PART_FX = {
    'tonewheel': _rot(lambda t: 'fast' if t.get('layer') == 'lead' else 'slow'),
    'rockorgan': _rot(lambda t: 'fast'),
}
