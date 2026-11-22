"""Celtic (2.4.1): session instruments, session drums, and the ornaments that make the music sound Irish / Scottish.

Instruments
    fiddle        a session fiddle: bowed (rosin noise, a scratchy bow change), a woody violin body, almost no vibrato on
                  short notes - folk fiddlers ornament with the fingers, not with vibrato - a little on long ones
    bouzouki      Irish bouzouki: four paired steel courses, the low ones in octaves, so every note shimmers (the pair
                  slightly out of tune) - the session's chiming, drone-friendly accompaniment
    irish_flute   wooden simple-system flute: breathy, hollow, a soft chiff at the start of each note
    lowwhistle    low D whistle: a big, soft, round, airy tone (slow airs)
    concertina    Anglo concertina: bright, thin free-reed tone, two reeds a hair apart (shanties, sessions)
    uilleann      uilleann pipes: a sweet, reedy chanter over its own drones (bellows-blown, so notes join)
    bagpipe       Great Highland bagpipe chanter: loud, bright, very nasal, no dynamics at all, notes always joined
    bagpipe_drones the Highland drones: two tenors on the tonic and a bass an octave below, beating gently

Drums
    bodhran       goatskin frame drum: a deeper boom whose pitch the back hand bends; p tone='top' for the high, dry
                  tipper strokes near the rim
    bones / spoons  the rhythm players' clatter: two clicks a few ms apart / a bright metallic clack
    pipe_snare    a pipe-band snare: tuned very high and tight, a hard, crisp crack with bright wires
    tenor_drum    the pipe band's tenor: a soft mallet boom, mid-pitched, a little ring

Ornaments (ornament_pass) - what a melody needs to sound like trad:
    trad   fiddle / whistle / flute / pipes leads: a CUT (a flick to a higher note just before the note) on many
           longer notes, a TAP (a flick below) now and then, and a ROLL on the longest ones (note - cut - note -
           tap - note, inside the note's time)
    pipes  Highland pipes can't tongue or stop, so every change of note is articulated by GRACENOTES: a high-G
           grace before most notes, a doubling (high G, the note, a D) on the strong beats
"""
import zlib

import numpy as np

from .dsp import SR, adsr, bp, eq, fade_out, hp, lp, mtof, noise, saw, soft, square
from . import va as _va
from .instruments import DRUMS, GM_PROGRAM, INSTRUMENT_INFO, INSTRUMENTS, ROLE_CHOICES, _bass_exc
from .theory import Ev


def _rng(name, m, dur):
    return np.random.default_rng(zlib.crc32(f'{name}|{m:.2f}|{dur:.3f}'.encode()))


def _gate(dur, a=0.01, d=0.08, s=0.9, r=0.06):
    return adsr(max(dur, 0.02) * SR, a, d, s, r)


def c_fiddle(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    r = _rng('fiddle', m, dur)
    env = _gate(dur, 0.012, 0.06, 0.85, 0.07)
    n = len(env)
    t = np.arange(n) / SR
    vib = (6 if dur > 0.45 else 0) * np.clip((t - 0.25) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.6 * t)   # only on long notes
    jit = np.cumsum(r.standard_normal(n)) * 0.0006
    jit -= np.linspace(jit[0], jit[-1], n)
    fv = f * 2 ** ((vib + jit) / 1200)
    x = saw(fv, n) * 0.75 + square(fv, n, pw=0.3) * 0.25          # the stick-slip bow wave
    x = eq(eq(eq(eq(x, 'peak', 275, 2.0, 5.0), 'peak', 460, 2.0, 3.5), 'peak', 2900, 1.5, 6.0), 'peak', 1600, 3.0, -3.0)
    rosin = bp(noise(n), 2500, 7000) * (0.05 + 0.12 * np.exp(-t * 30))   # rosin, loud at the bow change
    y = lp(x + rosin, 9000) * env
    return hp(y, 180) * 0.22


def c_bouzouki(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(1.6 * SR)
    out = np.zeros(n)
    pairs = [(f, 0.0), (f * 2 ** (6 / 1200), 0.0)]                 # a paired course, a few cents apart
    if m < 57:
        pairs[1] = (f * 2.0, 0.0)                                  # the low courses are strung in octaves
    for k, (fk, _) in enumerate(pairs):
        d = int(0.004 * SR * k)                                    # the pick catches the two strings a hair apart
        y = _va.string(fk, n - d, _bass_exc(fk, 'pick', 1.6), t60=3.2 * (200 / max(fk, 80)) ** 0.3, bright=0.85,
                       gate=gate - d if gate > d else None, mute_t60=0.25, pickup=0.0)
        out[d:] += y * (0.55 if k else 0.6)
    out = eq(eq(out, 'peak', 220, 1.5, 3.0), 'peak', 3200, 1.5, 4.0)    # small round body, bright steel
    return hp(out, 90) * 0.32


def _breathy(name, m, dur, body, breath, chiff, oct_=1.0):
    f = float(mtof(m)) * oct_
    r = _rng(name, m, dur)
    env = _gate(dur, 0.03, 0.1, 0.88, 0.08)
    n = len(env)
    t = np.arange(n) / SR
    fv = f * 2 ** ((4 * np.sin(2 * np.pi * 5.0 * t) * np.clip((t - 0.3) / 0.4, 0, 1)) / 1200)
    ph = 2 * np.pi * np.cumsum(fv) / SR
    x = np.sin(ph) + 0.18 * np.sin(2 * ph) + body * np.sin(3 * ph)
    air = bp(noise(n), f * 0.8, min(f * 6, 12000)) * breath
    ch = bp(r.standard_normal(n), 1500, 6000) * np.exp(-t * 60) * chiff
    return (x + air) * env + ch


def c_irish_flute(m, dur, p, glide=None, mod=None):
    return hp(lp(_breathy('irish_flute', m, dur, 0.12, 0.22, 0.35), 7000), 200) * 0.24


def c_lowwhistle(m, dur, p, glide=None, mod=None):
    return hp(lp(_breathy('lowwhistle', m, dur, 0.06, 0.28, 0.15, oct_=0.5), 5000), 120) * 0.26


def c_concertina(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = _gate(dur, 0.02, 0.05, 0.92, 0.05)
    n = len(env)
    x = square(f, n, pw=0.42) * 0.6 + saw(f * 2 ** (5 / 1200), n) * 0.5      # two reeds, a hair apart
    y = eq(eq(lp(x, 6000), 'peak', 1800, 1.4, 4.0), 'peak', 500, 1.0, -2.0)
    return hp(y, 160) * env * 0.17


def _chanter(f, n, nasal, bright):
    x = square(f, n, pw=0.14) * 0.7 + saw(f, n) * 0.3
    return eq(eq(eq(lp(x, bright), 'peak', 1300, 2.0, nasal), 'peak', 2800, 2.2, nasal * 0.8), 'peak', 400, 1.0, -5.0)


def c_uilleann(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = _gate(dur, 0.006, 0.05, 0.95, 0.04)
    n = len(env)
    t = np.arange(n) / SR
    y = _chanter(f * 2 ** (2 * np.sin(2 * np.pi * 4 * t) / 1200), n, 6.0, 5500)
    root = 73.42 if p.get('drone_root') is None else float(p['drone_root'])   # the drones sit on D
    dr = lp(saw(root, n) + 0.6 * saw(root * 2, n) + 0.4 * saw(root * 4.0 * 2 ** (3 / 1200), n), 1500) * 0.25
    return hp(y * env + dr * env * float(p.get('drone', 1.0)), 60) * 0.2


def _reed(fv, n, r, pw=0.16):
    """A double reed: a narrow, slightly asymmetric pulse (the reed slamming shut) with reed buzz - noise gated by the
    reed's own cycle, so the hiss pulses at the note's pitch instead of floating on top of it."""
    ph = np.cumsum(fv) / SR
    frac = ph % 1.0
    pulse = np.where(frac < pw, 1.0, -pw / (1 - pw))
    pulse = lp(pulse, 9000) * 0.75 + saw(fv, n) * 0.25
    gate = np.exp(-frac * 9.0)                                    # buzz bursts at each reed closure
    buzz = hp(r.standard_normal(n), 2500) * gate * 0.22
    return pulse + buzz


_CH = dict(pos=0.375, offset=0.7, slope=0.4, refl=0.9)      # chanter reed + bore: stable across the whole chanter range
_DR = dict(offset=0.7, slope=-0.3, refl=0.95)                # drone reeds


def _f0(y):
    y = y[len(y) // 3:]
    y = y - y.mean()
    if len(y) < 2000 or np.abs(y).max() < 1e-4:
        return 0.0
    m = min(len(y), 6000)
    ac = np.correlate(y[:m], y[:m], 'full')[m - 1:]
    lo, hi = int(SR / 2500), int(SR / 50)
    seg = ac[lo:hi]
    if seg.max() <= 0:
        return 0.0
    peaks = [j for j in range(1, len(seg) - 1) if seg[j] >= seg[j - 1] and seg[j] >= seg[j + 1] and seg[j] > 0.85 * seg.max()]
    k = lo + (peaks[0] if peaks else int(np.argmax(seg)))            # the first strong peak: no octave errors
    if 1 <= k < len(ac) - 1:                                       # parabolic peak: sub-sample accuracy
        a, b, c = ac[k - 1], ac[k], ac[k + 1]
        d = a - 2 * b + c
        k = k + (0.5 * (a - c) / d if d else 0.0)
    return SR / k


_TUNED = {}


def _chanter_raw(d, b0, n, seed, rate=SR, turb_amt=0.06):
    """The chanter's bore output for n samples at `rate`: bore length d, bag pressure b0 - with the crow and the
    turbulence (time constants and the turbulence band set in real time / Hz, whatever the rate)."""
    from . import fastdsp as F
    t = np.arange(n) / rate
    crow = 1 + 0.02 * np.exp(-t / 0.008)
    br = np.full(n, b0) * (0.7 + 0.3 * np.clip(t / 0.02, 0, 1))       # started exactly as pipe_part starts a phrase
    turb = lp(np.random.default_rng(seed).standard_normal(n), 800 * SR / rate) * turb_amt
    turb = turb + np.random.default_rng(seed + 1).standard_normal(n) * 0.1 * np.exp(-t / 0.01)     # the first puff of air
    return F.reed_conical(br, turb, d * crow, _CH['pos'], _CH['offset'], _CH['slope'], _CH['refl'])


def _tuned_delay(f, kind):
    """(bore length, breath) that really sound at f: short test notes, measured and corrected, cached per pitch. A note
    that overblows (jumps an octave) is blown a little softer until it locks - as a piper would."""
    from . import fastdsp as F
    key = (kind, round(f, 2))
    if key in _TUNED:
        return _TUNED[key]
    n = int(0.25 * SR)
    b0 = 0.65 if kind == 'chanter' else 0.7 if kind == 'chanter_os' else 0.6
    d = (SR / f - 3.0) if kind == 'chanter' else (2 * SR / f - 3.0) if kind == 'chanter_os' else SR / f / 2 - 1.0
    for _ in range(10):
        br = np.full(n, b0)
        br[:150] = np.linspace(0, b0, 150)
        if kind == 'chanter':
            y = _chanter_raw(d, b0, n, 7)
        elif kind == 'chanter_os':                        # tested exactly as the band plays it: at twice the rate
            y = _chanter_raw(d, b0, 2 * n, 7, rate=2 * SR, turb_amt=0.03)
        else:
            y = F.reed_cylindrical(br, np.zeros(n), np.full(n, d), _DR['offset'], _DR['slope'], _DR['refl'])
        got = _f0(y)
        if not got or got <= 0:
            break
        if kind == 'chanter_os':
            got *= 2.0
        if got > 1.6 * f and b0 > 0.4:                               # overblown: ease off the bag
            b0 -= 0.04
            continue
        d = max(4.0, d * got / f)
        if abs(1200 * np.log2(got / f)) < 2:
            break
    _TUNED[key] = (d, b0)
    return d, b0


def c_bagpipe(m, dur, p, glide=None, mod=None):
    """Great Highland bagpipe chanter - a physical model: a double reed driving a conical bore (a digital waveguide),
    blown by a bag at constant high pressure (no dynamics, the pitch locks in by itself), the reed's turbulence in the
    air stream, a quick 'crow' as the reed catches, then the chanter's bright radiation from the sole and holes."""
    f = float(mtof(m))
    n = int((max(dur, 0.03) + 0.02) * SR)
    d, b0 = _tuned_delay(f, 'chanter')
    y = _chanter_raw(d, b0, n, 7)                                  # the reed catching (crow), turbulence, the bag's pressure
    if _f0(y[: int(0.25 * SR)]) > 1.6 * f if n > int(0.12 * SR) else False:   # (safety) overblown: blow softer
        y = _chanter_raw(d, b0 - 0.08, n, 7)
    y = np.diff(y, prepend=y[0]) * 3.0 + 0.4 * y                  # radiated sound: the bore's output, brighter (holes / sole)
    y = eq(eq(y, 'peak', 2600, 1.2, 3.0), 'peak', 300, 1.0, -4.0)
    tail = int(0.02 * SR)
    y[-tail:] *= np.linspace(1, 0, tail)
    return hp(lp(y, 10000), 200) * 0.16


def c_bagpipe_drones(m, dur, p, glide=None, mod=None):
    """The Highland drones - three physical-model reeds on cylindrical bores (the hollow, odd-harmonic hum): two tenors
    on the tonic, a hair apart so they beat slowly, and a bass an octave below, all fed by the same bag."""
    from . import fastdsp as F
    from .instruments import _ms_stereo
    f = float(mtof(m))
    r = _rng('drones', m, dur)
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, amp, cents in ((1.0, 1.0, 0.0), (1.0, 0.85, 1.8), (0.5, 1.0, -0.8)):
        fk = f * ratio * 2 ** (cents / 1200)
        d0, b0 = _tuned_delay(fk, 'drone')
        d = d0 * (1 + 0.0004 * np.sin(2 * np.pi * 0.09 * t + r.random() * 6))
        br = np.full(n, b0) * np.clip(t / 0.05, 0, 1)
        y = F.reed_cylindrical(br, lp(r.standard_normal(n), 2000) * 0.03, d, _DR['offset'], _DR['slope'], _DR['refl'])
        out += amp * (y - y.mean())
    out = np.diff(out, prepend=out[0]) * 2.0 + 0.5 * out
    env = np.minimum(t / 0.35, 1) * np.clip((dur + 0.4 - t) / 0.3, 0, 1)
    y = lp(out, 5000) * env * 0.05
    return _ms_stereo(y, 150)


def c_bagpipe_bright(m, dur, p, glide=None, mod=None):
    """The bright Highland bagpipe: the same chanter with its overtones pushed forward (see _brighten)."""
    return _brighten(c_bagpipe(m, dur, p, glide, mod))


def c_synthpipes(m, dur, p, glide=None, mod=None):
    """Synth pipes: a bagpipe-flavoured EDM lead - a stack of detuned pulses and saws shaped like a chanter (the same
    formants and crow), its own fifth-and-root drone underneath, and a gracenote flick a fourth up at the start of
    every note - big, bright, Celtic festival lead."""
    f = float(mtof(m))
    r = _rng('synthpipes', m, dur)
    env = _gate(dur, 0.005, 0.08, 0.92, 0.08)
    n = len(env)
    t = np.arange(n) / SR
    g0 = f * 2 ** ((glide - m) / 12) if glide is not None else None
    bend = 500 * np.clip(1 - t / 0.035, 0, 1) ** 2                  # the gracenote flick, a fourth up, into the note
    if g0 is not None:
        fbase = g0 + (f - g0) * np.clip(t / 0.08, 0, 1)
    else:
        fbase = np.full(n, f)
    x = np.zeros(n)
    for c in (-14, -6, 0, 6, 14):
        fv = fbase * 2 ** ((bend + c) / 1200)
        x += square(fv, n, pw=0.2) * 0.5 + saw(fv, n) * 0.5
    x = eq(eq(eq(x / 5, 'peak', 1200, 1.4, 6.0), 'peak', 2500, 1.6, 5.0), 'peak', 4100, 2.0, 3.0)
    drone = (saw(f / 2, n) + 0.7 * saw(f / 2 * 1.5, n)) * 0.18           # root and fifth an octave down
    y = lp(x + lp(drone, 1800), 9000)
    return hp(soft(y * 1.3, 1.2), 120) * env * 0.2


# ------------------------------------------------------------------------------------------------------------ drums
def d_bodhran2(p):
    """Bodhrán: tone='low' (default) a deep boom whose pitch the back hand bends; tone='top' the tipper high on the
    skin near the rim - higher, drier and shorter."""
    top = p.get('tone') == 'top'
    n = int((0.25 if top else 0.6) * SR)
    t = np.arange(n) / SR
    f0 = p.get('pitch', 150 if top else 78)
    bend = p.get('bend', 0.0)                                      # the hand pressing in: the pitch climbs
    f = f0 * (1 + 0.3 * np.exp(-t * 28)) * (1 + bend * np.clip(t / 0.15, 0, 1))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * p.get('decay', 22 if top else 8))
    y += (0.7 if top else 0.4) * bp(noise(n), 700 if top else 450, 4000) * np.exp(-t * (140 if top else 80))   # goatskin slap
    return fade_out(soft(y, 1.3), 0.02)


def d_bones(p):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    click = bp(noise(n), 1800, 6000) * np.exp(-t * 400)
    y = click.copy()
    d = int(0.006 * SR)                                            # two bones: a double click
    y[d:] += 0.7 * click[:-d]
    y += 0.4 * np.sin(2 * np.pi * 2300 * t) * np.exp(-t * 300)
    return fade_out(y * 0.9, 0.01)


def d_spoons(p):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    y = bp(noise(n), 3000, 9000) * np.exp(-t * 250) + 0.5 * np.sin(2 * np.pi * 3700 * t) * np.exp(-t * 120)
    return fade_out(y * 0.8, 0.01)


def d_pipe_snare(p):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    head = np.sin(2 * np.pi * 420 * t * (1 + 0.15 * np.exp(-t * 60))) * np.exp(-t * 45)
    wires = bp(noise(n), 3000, 11000) * np.exp(-t * p.get('decay', 28))
    crack = bp(noise(n), 1500, 5000) * np.exp(-t * 200)
    return fade_out(soft(0.5 * head + 0.9 * wires + 0.7 * crack, 1.5), 0.02)


def d_tenor_drum(p):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    f = p.get('pitch', 110) * (1 + 0.1 * np.exp(-t * 20))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) + 0.2 * lp(noise(n), 1200) * np.exp(-t * 40)
    return fade_out(soft(y, 1.2), 0.03)


# ---- (2.5.0) more of the Celtic world: harps, citterns, the other bagpipes, Breton reeds, the hurdy-gurdy, melodeon ----

def c_clarsach(m, dur, p, glide=None, mod=None):
    """Clarsach - the old wire-strung Gaelic harp, plucked with the fingernails: a bright, bell-like ring that sustains
    for seconds, a faint metallic shimmer from the brass strings and the sympathetic ring of its neighbours."""
    f = float(mtof(m))
    n = int(max(dur, 0.1) * SR) + int(3.0 * SR)
    t = np.arange(n) / SR
    y = _va.string(f, n, _bass_exc(f, 'pick', 1.3), t60=5.0 * (220 / max(f, 90)) ** 0.25, bright=0.9, pickup=0.0)
    y = y + 0.18 * _va.string(f * 2 ** (4 / 1200), n, _bass_exc(f, 'finger', 1.0), t60=6.0, bright=0.8) * np.clip(t / 0.15, 0, 1)
    y = eq(eq(y, 'peak', 2600, 1.0, 4.0), 'peak', 350, 1.2, 2.0)       # brass shimmer + the soundbox
    return hp(y, 110) * 0.3


def c_cittern(m, dur, p, glide=None, mod=None):
    """Cittern - the small, high, flat-backed cousin of the bouzouki: tight steel courses, crisp and jangly."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(1.2 * SR)
    out = np.zeros(n)
    for k, fk in enumerate((f, f * 2 ** (8 / 1200), f * 2.0)):
        d = int(0.003 * SR * k)
        y = _va.string(fk, n - d, _bass_exc(fk, 'pick', 1.8), t60=2.4 * (220 / max(fk, 90)) ** 0.3, bright=0.92,
                       gate=gate - d if gate > d else None, mute_t60=0.2, pickup=0.0)
        out[d:] += y * (0.55, 0.45, 0.22)[k]
    out = eq(eq(out, 'peak', 380, 1.4, 2.0), 'peak', 4000, 1.3, 4.5)
    return hp(out, 140) * 0.3


def _reed_voice(name, m, dur, pw, peaks, bright, drone=None, vib=0.0, att=0.008):
    f = float(mtof(m))
    r = _rng(name, m, dur)
    env = _gate(dur, att, 0.05, 0.95, 0.05)
    n = len(env)
    t = np.arange(n) / SR
    fv = f * 2 ** ((vib * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.2) / 0.3, 0, 1)) / 1200)
    y = lp(_reed(fv, n, r, pw), bright)
    for fc, q, g in peaks:
        y = eq(y, 'peak', fc, q, g)
    y = y * env
    if drone is not None:
        y = y + drone * env
    return y


def c_smallpipes(m, dur, p, glide=None, mod=None):
    """Scottish smallpipes - bellows-blown, cylindrical bore, quiet and sweet enough for the parlour: soft-edged, round,
    with gentle drones on the tonic."""
    f = float(mtof(m))
    n = len(_gate(dur, 0.01, 0.05, 0.95, 0.05))
    root = 58.27 if p.get('drone_root') is None else float(p['drone_root'])
    dr = lp(saw(root * 2, n) * 0.6 + saw(root * 4 * 2 ** (2 / 1200), n) * 0.35, 900) * 0.18
    y = _reed_voice('smallpipes', m, dur, 0.3, ((900, 1.0, 3.0), (2200, 1.2, 2.0), (300, 1.0, -3.0)), 4200, dr)
    return hp(y, 90) * 0.2 * (220 / max(f, 220)) ** 0.1


def c_gaita(m, dur, p, glide=None, mod=None):
    """Gaita - the Galician / Asturian bagpipe: a conical chanter, sweeter and more open than the Highland pipes, played
    with vibrato and a little expression, over a single deep bass drone (the roncón)."""
    root = 73.42 if p.get('drone_root') is None else float(p['drone_root'])
    n = len(_gate(dur, 0.01, 0.05, 0.95, 0.05))
    dr = lp(saw(root, n) * 0.7 + saw(root * 2, n) * 0.3, 1100) * 0.2
    y = _reed_voice('gaita', m, dur, 0.2, ((1400, 1.3, 4.5), (3000, 1.4, 3.0), (350, 1.0, -3.0)), 6500, dr, vib=8.0)
    return hp(y, 70) * 0.18


def c_bombarde(m, dur, p, glide=None, mod=None):
    """Bombarde - the Breton oboe: a loud, piercing double reed that answers the biniou in call and response."""
    y = _reed_voice('bombarde', m, dur, 0.11, ((1800, 1.4, 6.0), (3600, 1.5, 4.0), (450, 1.0, -5.0)), 8000, vib=3.0, att=0.012)
    return hp(y, 280) * 0.16


def c_melodeon(m, dur, p, glide=None, mod=None):
    """Melodeon - the Irish/Scottish button box: two reeds tuned 'wet' (well apart), so every note shimmers with a fast
    tremolo, bouncy and bright."""
    f = float(mtof(m))
    env = _gate(dur, 0.015, 0.04, 0.9, 0.04)
    n = len(env)
    x = square(f, n, pw=0.4) * 0.5 + square(f * 2 ** (22 / 1200), n, pw=0.4) * 0.5 + saw(f * 2 ** (-6 / 1200), n) * 0.3
    y = eq(eq(lp(x, 7000), 'peak', 2000, 1.3, 4.0), 'peak', 450, 1.0, -2.0)
    return hp(y, 170) * env * 0.15


NEW = {
    'fiddle': (c_fiddle, 'Fiddle (session / folk bowing)', 110, ('lead', 'arp')),
    'bouzouki': (c_bouzouki, 'Irish bouzouki (paired steel courses)', 25, ('chords', 'arp')),
    'irish_flute': (c_irish_flute, 'Irish wooden flute (breathy)', 73, ('lead', 'arp')),
    'lowwhistle': (c_lowwhistle, 'Low whistle (soft, airy)', 78, ('lead',)),
    'concertina': (c_concertina, 'Concertina (free reeds)', 21, ('lead', 'chords', 'pad')),
    'uilleann': (c_uilleann, 'Uilleann pipes (chanter + drones)', 109, ('lead', 'pad')),
    'bagpipe': (c_bagpipe, 'Great Highland bagpipe (chanter)', 109, ('lead',)),
    'bagpipe_bright': (c_bagpipe_bright, 'Great Highland bagpipe, bright (more edge and overtones)', 109, ('lead',)),
    'bagpipe_drones': (c_bagpipe_drones, 'Highland bagpipe drones', 109, ('pad',)),
    'clarsach': (c_clarsach, 'Clarsach (wire-strung Gaelic harp)', 46, ('arp', 'chords', 'lead')),
    'cittern': (c_cittern, 'Cittern (bright steel courses)', 25, ('chords', 'arp')),
    'smallpipes': (c_smallpipes, 'Scottish smallpipes (soft, bellows-blown)', 109, ('lead',)),
    'gaita': (c_gaita, 'Gaita (Galician bagpipe)', 109, ('lead',)),
    'bombarde': (c_bombarde, 'Bombarde (Breton oboe)', 68, ('lead',)),
    'melodeon': (c_melodeon, 'Melodeon (button accordion)', 21, ('lead', 'chords')),
    'synthpipes': (c_synthpipes, 'Synth pipes (bagpipe-style EDM lead)', 109, ('lead', 'arp')),
}
for _n, (_fn, _info, _gm, _roles) in NEW.items():
    INSTRUMENTS[_n] = _fn
    INSTRUMENT_INFO[_n] = _info
    GM_PROGRAM[_n] = _gm
    for _r in _roles:
        if _n not in ROLE_CHOICES.setdefault(_r, []):
            ROLE_CHOICES[_r].append(_n)
DRUMS.update({'bodhran2': d_bodhran2, 'bones': d_bones, 'spoons': d_spoons, 'pipe_snare': d_pipe_snare,
              'tenor_drum': d_tenor_drum})


# -------------------------------------------------------------------------------------------------------- ornaments
def _step(m, scale, up):
    for k in range(1, 4):
        c = m + (k if up else -k)
        if c % 12 in scale:
            return c
    return m + (2 if up else -2)


def ornament_pass(evs, tracks, sections, st, bpm, seed, tonic=None):
    """Cuts, taps and rolls (trad) or Highland gracenotes (pipes) on every lead-layer part - see the module docstring."""
    import random
    style = st.get('celtic_orn')
    if not style:
        return
    rnd = random.Random(f'{seed}-celtic-orn')
    amt = st.get('_orn_amount')
    amt = 0.5 if amt is None else max(0.0, min(1.0, float(amt)))
    if amt <= 0.01 and not st.get('set_shift'):
        return
    shift = st.get('set_shift') or {}
    if shift:                                            # a session set: each next tune in its new key (drums stay put)
        for sec in sections:
            k = shift.get((sec.get('opts') or {}).get('tune'))
            if not k:
                continue
            b0, b1 = sec['bar'] * 4.0, (sec['bar'] + sec['bars']) * 4.0
            for e in evs:
                if b0 <= e.beat < b1 and e.midi is not None and tracks.get(e.track, {}).get('inst') not in DRUMS:
                    e.midi += k
    leads = {n for n, t in tracks.items() if t.get('layer') == 'lead'}
    chords = [e for e in evs if e.track in ('chords', 'pad')]
    scale = {e.midi % 12 for e in chords} if chords else None
    if not scale or len(scale) < 5:
        scale = {e.midi % 12 for e in evs if e.track in leads} or set(range(12))
    sec_beat = 60.0 / max(40, bpm)
    g = (0.038 if style == 'pipes' else 0.045) / sec_beat           # a grace note: ~38 ms on pipes (snappy), 45 ms trad
    new = []
    ch_notes = None
    if style == 'pipes' and tonic is not None:          # (2.4.6) the Highland chanter has exactly nine notes: low G to
        t = 60 + tonic % 12                               # high A (mixolydian + the low G) - the tune is fitted onto them
        if t < 66:
            t += 12
        ch_notes = [t - 2, t, t + 2, t + 4, t + 5, t + 7, t + 9, t + 10, t + 12]
        for e in evs:
            if e.track in leads and e.midi is not None:
                same = [c for c in ch_notes if c % 12 == e.midi % 12]
                e.midi = min(same or ch_notes, key=lambda c: abs(c - e.midi))
    lead_evs = sorted((e for e in evs if e.track in leads), key=lambda e: (e.track, e.beat))
    prev = {}
    for e in lead_evs:
        p = prev.get(e.track)
        prev[e.track] = e
        if style == 'pipes':                             # Highland piping: the ornament follows the melody
            if e.dur < 2.5 * g or rnd.random() > 0.35 + 0.65 * amt:
                continue
            if ch_notes:                                  # the real gracenotes: high G (high A on the top notes)
                top = ch_notes[7] if e.midi < ch_notes[7] else ch_notes[8]
                i_ = ch_notes.index(e.midi) if e.midi in ch_notes else 1
                lo = ch_notes[max(0, i_ - 1)]
            else:
                top = max(m for m in range(e.midi, e.midi + 13) if m % 12 in scale)
                if top == e.midi:
                    top = _step(e.midi, scale, True)
                lo = _step(e.midi, scale, False)
            on_beat = abs(e.beat - round(e.beat)) < 0.01
            fig = []
            if p is not None and p.midi == e.midi:                # a repeated note: the chanter can't stop, so it
                fig = [top] if rnd.random() < 0.6 else [top, e.midi, lo]   # MUST be split - a gracenote or a strike
            elif e.dur > 6 * g and on_beat and amt > 0.6 and rnd.random() < 0.25 * amt:
                low = ch_notes[0] if ch_notes else min(m for m in range(e.midi - 12, e.midi + 1) if m % 12 in scale)
                fig = [top, low, ch_notes[3] if ch_notes else _step(low, scale, True)]   # a taorluath-like figure (D grace)
            elif e.dur > 4 * g and on_beat and rnd.random() < 0.35 + 0.3 * amt:
                up = ch_notes[min(8, ch_notes.index(e.midi) + 1)] if ch_notes and e.midi in ch_notes else _step(e.midi, scale, True)
                fig = [top, e.midi, up]                            # a doubling
            elif p is not None and p.midi > e.midi:
                fig = [p.midi if p.midi > e.midi + 2 else top]     # going down: a cut from the note above
            else:
                fig = [top]                                         # going up / starting: a high-G gracenote
            k = len(fig)
            for q, gm in enumerate(fig):
                new.append(Ev(e.track, e.beat - (k - q) * g, g * 0.9, gm, e.vel))
            continue
        # trad: cuts, taps, rolls
        if amt <= 0.01:
            continue
        if e.dur >= 0.75 and rnd.random() < 0.7 * amt:                    # a roll on the long notes
            cut, tap = _step(e.midi, scale, True), _step(e.midi, scale, False)
            third = e.dur / 3
            new += [Ev(e.track, e.beat + third - g, g, cut, e.vel * 0.85), Ev(e.track, e.beat + third, third - g, e.midi, e.vel),
                    Ev(e.track, e.beat + 2 * third - g, g, tap, e.vel * 0.85), Ev(e.track, e.beat + 2 * third, third, e.midi, e.vel)]
            e.dur = third - g
        elif e.dur >= 0.4 and rnd.random() < 0.9 * amt:                  # a cut
            new.append(Ev(e.track, e.beat - g, g, _step(e.midi, scale, True), e.vel * 0.8))
        elif e.dur >= 0.4 and rnd.random() < 0.24 * amt:                 # a tap
            new.append(Ev(e.track, e.beat - g, g, _step(e.midi, scale, False), e.vel * 0.8))
    evs.extend(x for x in new if x.beat >= 0)


# ------------------------------------------------------------------------------- whole-part pipes (2.4.3, rendering)
# the traditional Highland scale, tuned pure against the drones (cents away from equal temperament, by interval above
# the tonic): the 2nd 9/8, the 3rd 5/4, the 4th 4/3, the 5th 3/2, the 6th 5/3 and 'high G' the natural 7th 7/4 - which is
# why real pipes ring and lock with their drones (and why the high G sounds 'flat' to a piano)
PIPE_JI = {0: 0.0, 2: 3.9, 4: -13.7, 5: -2.0, 7: 2.0, 9: -15.6, 10: -31.2, 11: -11.7}


def pipe_band(notes, length, tonic=None, players=3, bright=False):
    """A pipe band's chanters: several pipers on the same line, never quite together - each a few cents apart, a few
    ms early or late, on their own reed - summed and soft-saturated the way the reeds blend into one wall. (2, length)."""
    if players <= 1:
        y = pipe_part(notes, length, tonic)
        out = _hall(np.vstack([y, y]))
        return _brighten(out) if bright else out
    out = np.zeros((2, length))
    rnd = np.random.default_rng(len(notes) * 7 + players)
    for k in range(players):
        # (2.4.11) a real group, not one piper copied: every piper drifts ahead and behind on their own (a slow sway of
        # up to ~12 ms plus a few ms per note, never out of order), sits a few cents off the others and wanders in pitch
        # on their own - that slow beating between chanters is what makes a band sound like a band
        dt0 = (rnd.random() - 0.5) * 0.012
        sw_f, sw_p = 0.12 + rnd.random() * 0.15, rnd.random() * 2 * np.pi
        nk, prev = [], -1.0
        for (t, d, m) in notes:
            tt = t + dt0 + 0.005 * np.sin(2 * np.pi * sw_f * t + sw_p) + (rnd.random() - 0.5) * 0.005   # a bit tighter, as 2.4.6
            tt = max(0.0, tt, prev + 0.006)
            nk.append((tt, d, m))
            prev = tt
        cents = (k - (players - 1) / 2) / max(1, players - 1) * 7.0 + (rnd.random() - 0.5) * 2.0   # spread over ~7 cents
        rp = _CH['pos'] + (k - (players - 1) / 2) * 0.02               # every piper's reed is a little different: a
        y = pipe_part(nk, length, tonic, cents=cents, seed=k + 1, reed_pos=rp, life=4.0)   # different harmonic balance, not a copy
        pan = (k - (players - 1) / 2) / max(1, players - 1) * 0.9       # spread wide (summed close, near-copies flange)
        out[0] += y * np.sqrt(0.5 * (1 - pan))
        out[1] += y * np.sqrt(0.5 * (1 + pan))
    out /= players ** 0.7
    out = soft(out * 1.2, 1.1) / 1.05               # (2.4.13) between 2.4.6's and 2.4.8's blend of the reeds into one wall
    out = _hall(out)
    return _brighten(out) if bright else out


def _brighten(x):
    """(2.4.15) The bright pipes: the same band with the overtones pushed well forward - the fundamental of even the top
    notes thinned, a strong 3-4 kHz edge and an open top - at the same loudness."""
    y = eq(eq(eq(x, 'highpass', 900, 0.6), 'peak', 3500, 0.8, 4.0), 'highshelf', 3000, 0.7, 5.0)
    ry, rx = np.sqrt(np.mean(y ** 2)), np.sqrt(np.mean(x ** 2))
    return y * (rx / ry) if ry > 1e-9 else y


def pipe_part(notes, length, tonic=None, cents=0.0, seed=0, reed_pos=None, life=2.0):
    """The Highland chanter as it really plays: ONE reed sounding continuously through each phrase. Each note's pitch
    holds until the next note starts (the chanter never stops between notes - the gracenotes are what separate them),
    the reed only catches (the crow) at the start of a phrase, and a phrase ends only at a real silence.
    The reed model runs at twice the sample rate (2.4.8): its reed snapping shut every cycle makes harmonics far above
    hearing, which at the normal rate fold back down as a fizzy, electronic buzz - oversampled, they're filtered away.
    notes: [(start_s, dur_s, midi)] sorted; returns (length,) mono."""
    from . import fastdsp as F
    from scipy.signal import resample_poly
    OS = 2
    R = SR * OS
    out = np.zeros(length)
    if not notes:
        return out
    phrases, cur = [], [notes[0]]
    for nt in notes[1:]:
        last = cur[-1]
        if nt[0] - (last[0] + last[1]) > 1.5:              # pipes never stop inside a tune: a note holds over a rest
            phrases.append(cur)
            cur = [nt]
        else:
            cur.append(nt)
    phrases.append(cur)
    for ph in phrases:
        a = int(ph[0][0] * SR)
        b = min(length, int((ph[-1][0] + ph[-1][1]) * SR) + int(0.03 * SR))
        if b - a < 64:
            continue
        n = (b - a) * OS
        delay = np.empty(n)
        breath = np.empty(n)
        for k, (t0, dur, m) in enumerate(ph):
            s0 = max(0, int(t0 * R) - a * OS)
            s1 = n if k == len(ph) - 1 else max(s0 + 1, int(ph[k + 1][0] * R) - a * OS)
            ji = PIPE_JI.get((m - tonic) % 12, 0.0) if tonic is not None else 0.0
            # at twice the rate, the bore tuned (at the normal rate) for half the pitch sounds exactly this pitch
            d, b0 = _tuned_delay(float(mtof(m)) * 2 ** ((ji + cents + 2.0) / 1200), 'chanter_os')   # +2: the drift pulls it a touch flat
            delay[s0:s1] = d
            breath[s0:s1] = b0
        first = max(0, int(ph[0][0] * R) - a * OS)
        delay[:first] = delay[first]
        breath[:first] = breath[first]
        w = int(0.0025 * R)
        delay = np.convolve(delay, np.ones(w) / w, mode='same')       # ~2.5 ms: smooth, no crackle, but no sitar bend
        delay[:w] = delay[w]
        delay[-w:] = delay[-w - 1]
        t = np.arange(n) / R
        delay *= 1 + 0.02 * np.exp(-t / 0.008)                       # the crow: half of 2.4.8's (the full one twanged)
        drift = lp(np.random.default_rng(a * 31 + seed).standard_normal(n), 0.8 * SR / R)
        delay *= 2 ** (-(drift / (np.std(drift) + 1e-12) * life) / 1200)   # this piper's reed: slow life in cents
        breath = breath * (0.7 + 0.3 * np.clip(t / 0.02, 0, 1))        # a step to 70 % sets the reed going, then it eases in
        fo = int(0.02 * R)
        breath[-fo:] *= np.linspace(1, 0, fo)
        # (2.4.10) no breath noise while it sounds (the reed turns ANY of it into hiss and crunch) - only the first puff of
        # air, a few ms, which is what sets the reed going
        turb = np.random.default_rng(a + 9973 * seed).standard_normal(n) * 0.1 * np.exp(-t / 0.01)
        # (2.4.12) the 2.4.8 reed's breath is back - but slow (below 800 Hz): on this reed it gives life, not hiss
        turb = turb + lp(np.random.default_rng(a + 7 * seed).standard_normal(n), 800 * SR / R) * 0.03
        y = F.reed_conical(breath, turb, delay, _CH['pos'] if reed_pos is None else reed_pos, _CH['offset'], _CH['slope'],
                           _CH['refl'])
        y = resample_poly(y, 1, OS)[: b - a]                         # back to the normal rate, the fizz filtered off
        y = np.diff(y, prepend=y[0]) * 3.0 + 0.4 * y                 # radiation: (2.4.14) all of 2.4.6's brightness
        y = eq(eq(eq(eq(y, 'peak', 1150, 1.2, 3.5), 'peak', 1300, 1.1, 2.5), 'peak', 2800, 1.2, 3.5), 'peak', 3200, 1.1, 1.5)
        y = eq(eq(y, 'peak', 520, 0.9, 1.5), 'peak', 300, 1.0, -2.0)   # (2.4.13) 2.4.6's nasal formants over 2.4.8's, less boom   # nasal bite + body
        y = eq(eq(y, 'peak', 6500, 0.8, -1.5), 'highshelf', 3500, 0.7, 3.0)   # (2.4.14) open the top: it was muffled
        y = eq(eq(y, 'highpass', 650, 0.7), 'peak', 2400, 0.6, 5.0)  # and the fundamental no longer drowns the reed's bright overtones
        out[a:a + len(y)] += hp(lp(y, 14000), 220) * 0.19
    return out


def _hall(x, seed=4):
    """(2.4.12) 2.4.8's stone-hall space, gently: only later, weaker reflections (the strong 7-13 ms ones made the
    tunnel), so the band sounds like it's playing in a room, not a pipe."""
    rnd = np.random.default_rng(seed)
    out = x.copy()
    for ms, g in ((23, 0.16), (34, 0.13), (47, 0.11), (63, 0.08)):
        d = int(ms * 0.001 * SR)
        for c in range(out.shape[0]):
            dc = d + int(rnd.integers(0, 60))
            out[c, dc:] += g * lp(x[(c + 1) % out.shape[0], :-dc], 7000)
    return out / 1.2


def _drone_table(bass, N=4096):
    """One period of a drone reed on a long cylindrical pipe: odd harmonics strong, even ones weak, gently falling."""
    k = np.arange(1, 64)
    amp = k ** (-1.15 if bass else -0.95) * np.where(k % 2 == 1, 1.0, 0.35 if bass else 0.5)
    amp *= np.exp(-k / (14.0 if bass else 22.0))
    ph = np.random.default_rng(3 if bass else 5).random(len(k)) * 2 * np.pi
    x = np.arange(N) / N
    tab = (amp[:, None] * np.sin(2 * np.pi * k[:, None] * x[None, :] + ph[:, None])).sum(0)
    return tab / np.max(np.abs(tab))


def _drone_voice(f, n, bag, tab, beat_hz=0.0, seed=0):
    phase = np.cumsum(f * 2 ** (bag / 1200) + beat_hz) / SR
    frac = phase % 1.0
    pos = frac * len(tab)
    i0 = pos.astype(np.int64) % len(tab)
    fr = pos - np.floor(pos)
    y = tab[i0] * (1 - fr) + tab[(i0 + 1) % len(tab)] * fr
    buzz = bp(np.random.default_rng(seed).standard_normal(n), 1500, 4000) * np.exp(-frac * 8) * 0.006   # the reed, faintly
    return y + buzz


def drone_part(notes, length, tonic=None):
    """The Highland drones, unbroken under the whole pipe part: two tenors an octave below the chanter's low A and a
    bass an octave below them, all on the tonic. The tenors are a third of a hertz apart, so they beat slowly; the
    three share the bag's slow pressure wobble. (2, length)"""
    out = np.zeros((2, length))
    if not notes:
        return out
    t0 = notes[0][0]
    t1 = max(t + d for t, d, _ in notes)
    if tonic is not None:
        ch = 60 + tonic % 12
        ch = ch + 12 if ch < 66 else ch
        tenor = ch - 12
    else:
        tenor = notes[0][2] + 12
    a = int(t0 * SR)
    n = min(length - a, int((t1 - t0 + 0.4) * SR))
    if n <= 0:
        return out
    t = np.arange(n) / SR
    w = lp(np.random.default_rng(11).standard_normal(n), 1.5)        # the bag's pressure: a slow, BOUNDED sway (a steady
    bag = w / (np.std(w) + 1e-12) * 0.5 + 0.4 * np.sin(2 * np.pi * 0.07 * t)   # piper holds the drones within ~1 cent)
    ft = float(mtof(tenor))
    tt, tb = _drone_table(False), _drone_table(True)
    ten1 = _drone_voice(ft, n, bag, tt, 0.0, 1)
    ten2 = _drone_voice(ft, n, bag, tt, 0.33, 2)
    bass = _drone_voice(ft / 2, n, bag, tb, 0.0, 3)
    env = np.minimum(t / 0.4, 1) * np.clip((t[-1] - t) / 0.3, 0, 1)
    left = lp(0.55 * ten1 + 0.35 * ten2 + 0.75 * bass, 4500)
    right = lp(0.35 * ten1 + 0.55 * ten2 + 0.75 * bass, 4500)
    left, right = (eq(x, 'peak', 950, 0.9, -3.5) for x in (left, right))   # leave room for the chanters to cut through
    y = soft(np.vstack([left, right]) * 0.9, 1.1) * env * 0.12
    out[:, a:a + n] = y
    return out
