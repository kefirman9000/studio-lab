"""Studio Lab 2.0 synths: sounds the library was missing for trance, techno and hip hop.

    trance   pwmpad        an 80s / anthem string pad from two pulse waves whose widths sweep against each other
             formantlead   a vocal-ish 'ooh-aah' lead: a bright saw through moving vowel formants, delayed vibrato
    techno   fmperc        pitched metallic FM percussion (inharmonic ratios, a fast pitch tick), tuned to the notes
             modseq        a modular-synth sequence voice: every note gets its own filter cutoff, decay and slew,
                           like a hand-patched step sequencer drifting through a ladder filter
             noisestab     a Berlin noise stab: a chord's pitches as resonant filters over a noise burst
    hip hop  slide808      an 808 that dives into each note from above (or glides from the previous one) - drill / trap
             mpckeys       chopped soul keys: an e-piano chord through a 12-bit / 26 kHz sampler, a dusty low-pass and
                           a hard gate, as if cut from a record on an MPC
             soulhorn      a sampled-sounding soul horn stab: brass section, tape-saturated, band-limited like vinyl
             scratch       a turntable scratch: a 'fresh' vocal sample pushed back and forth (baby / chirp scratches)

Every voice is (m, dur, p, glide=None, mod=None) -> mono numpy array, like the rest of the instruments, and is
seeded from the note it plays so the same note always sounds the same.
"""
import zlib

import numpy as np
from scipy import signal

from .dsp import SR, adsr, bp, hp, lp, mtof, saw, sine, soft, square, svf_sweep
from .instruments import GM_PROGRAM, INSTRUMENT_INFO, INSTRUMENTS, ROLE_CHOICES


def _rng(name, m, dur):
    return np.random.default_rng(zlib.crc32(f'{name}|{m:.2f}|{dur:.3f}'.encode()))


def _t(n):
    return np.arange(n) / SR


def _formants(x, f1, f2, f3=2600.0, q=7.0):
    return svf_sweep(x, f1, q=q, mode='bandpass') + 0.8 * svf_sweep(x, f2, q=q, mode='bandpass') + \
        0.35 * svf_sweep(x, np.full(len(x), f3) if np.isscalar(f3) else f3, q=q, mode='bandpass')


# ------------------------------------------------------------------ trance
def i_pwmpad(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.45, 0.6, 0.85, 1.2)
    n = len(env)
    t = _t(n)
    w1 = 0.5 + 0.38 * np.sin(2 * np.pi * 0.31 * t)
    w2 = 0.5 + 0.38 * np.sin(2 * np.pi * 0.23 * t + 1.7)
    x = np.empty(n)
    blk = 512
    a = np.zeros(n)
    b = np.zeros(n)
    for i in range(0, n, blk):                        # pulse width changes block by block (smooth enough at 512)
        k = min(n, i + blk)
        ph = (np.arange(i, k) * f / SR) % 1.0
        ph2 = (np.arange(i, k) * f * 1.004 / SR + 0.37) % 1.0
        a[i:k] = np.where(ph < w1[i], 1.0, -1.0)
        b[i:k] = np.where(ph2 < w2[i], 1.0, -1.0)
    x = lp(a + b, 6000)
    x = svf_sweep(x, 900 + 2400 * (1 - np.exp(-t / 1.5)), q=0.9)
    return x * env * 0.32


def i_formantlead(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.012, 0.2, 0.85, 0.25)
    n = len(env)
    t = _t(n)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.4 * t) * np.clip((t - 0.2) / 0.3, 0, 1)
    x = saw(f * vib, n) + 0.6 * saw(f * 1.006 * vib, n, 0.3) + 0.25 * square(f * 0.5 * vib, n)
    ah = np.clip(t / max(0.2, dur * 0.7), 0, 1)                 # 'ooh' opening to 'aah' across the note
    y = _formants(x, 350 + 450 * ah, 800 + 400 * ah, 2600.0) + 0.15 * x
    return soft(y * 1.6, 1.4) * env * 0.5


# ------------------------------------------------------------------ techno
def i_fmperc(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    n = int(min(max(dur, 0.12), 0.6) * SR) + int(0.05 * SR)
    t = _t(n)
    pitch = f * (1 + 1.5 * np.exp(-t / 0.004))
    ratio = [1.41, 2.76, 3.53][int(m) % 3]                      # inharmonic: metal, not a note
    idx = 4.0 * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(pitch) / SR
    x = np.sin(ph + idx * np.sin(ph * ratio))
    x = hp(x, 180)
    return soft(x * 1.6, 1.3) * np.exp(-t / 0.09) * 0.6


def i_modseq(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    r = _rng('modseq', m, dur)
    env = adsr(min(dur, 0.5) * SR, 0.002, 0.08 + 0.25 * r.random(), 0.0, 0.05)
    n = len(env)
    t = _t(n)
    slew = f * (1 - 0.03 * np.exp(-t / 0.02) * (r.random() - 0.5))
    x = saw(slew, n) + 0.5 * square(slew * 0.5, n, pw=0.3 + 0.4 * r.random())
    cut0 = 300 + 3000 * r.random()                               # each step its own patch-cable mood
    cut = cut0 + (2500 + 3000 * r.random()) * np.exp(-t / (0.03 + 0.12 * r.random()))
    y = svf_sweep(x, cut, q=1.5 + 4 * r.random())
    return soft(y * 1.4, 1.2) * env * 0.5


def i_noisestab(m, dur, p, glide=None, mod=None):
    r = _rng('noisestab', m, dur)
    n = int((min(dur, 0.8) + 0.25) * SR)
    t = _t(n)
    nz = r.standard_normal(n)
    f = float(mtof(m))
    y = sum(svf_sweep(nz, np.full(n, f * k), q=25.0, mode='bandpass') * w for k, w in ((1, 1.0), (1.5, 0.7), (2, 0.6), (3, 0.3)))
    y += 0.25 * bp(nz, 1500, 6000)
    return soft(y * 2.0, 1.5) * np.exp(-t / (0.08 + 0.25 * min(dur, 0.8))) * 0.35


# ------------------------------------------------------------------ hip hop
def i_slide808(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.002, 0.3, 0.9, 0.15)
    n = len(env)
    t = _t(n)
    if glide:                                                    # glide from the previous note
        f0 = float(mtof(glide))
        curve = f0 + (f - f0) * np.clip(t / 0.09, 0, 1) ** 0.6
    else:                                                        # dive in from a fifth above
        curve = f * (1 + 0.5 * np.exp(-t / 0.035))
    x = sine(curve, n) + 0.08 * sine(curve * 2, n)
    x = soft(x * 2.2, 1.6)                                       # the distorted top that reads on phones
    return x * env * 0.7


def i_mpckeys(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(dur * SR, 0.002, 0.4, 0.55, 0.03)                 # hard gate: a chop, not a played note
    n = len(env)
    t = _t(n)
    tine = sine(f, n) * np.exp(-t / 1.2) + 0.35 * sine(f * 2, n) * np.exp(-t / 0.4) + 0.15 * sine(f * 3.01, n) * np.exp(-t / 0.15)
    tine += 0.08 * sine(f * 7.1, n) * np.exp(-t / 0.02)          # the bark
    x = soft(tine * 1.3, 1.1)
    hold = max(1, int(SR / 26040))                               # 26 kHz sampler, 12 bits
    y = np.repeat(x[::hold], hold)[:n] if hold > 1 else x
    y = np.round(y * 2047) / 2047
    y = lp(y, 5200)
    r = _rng('mpckeys', m, dur)
    crackle = (r.random(n) > 0.9993) * r.standard_normal(n) * 0.15 + r.standard_normal(n) * 0.004
    return (y + lp(crackle, 6000)) * env * 0.55


def i_soulhorn(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = adsr(min(dur, 0.6) * SR, 0.012, 0.15, 0.6, 0.12)
    n = len(env)
    t = _t(n)
    voices = sum(saw(f * d * (1 + 0.004 * np.sin(2 * np.pi * (4.5 + k) * t)), n, 0.17 * k) for k, d in enumerate((1.0, 1.005, 0.995, 2.0)))
    bright = 1200 + 2600 * np.exp(-t / 0.12)                     # the 'blat' of a horn attack
    y = svf_sweep(voices, bright, q=1.2)
    y = np.tanh(y * 1.6) / 1.4                                   # tape
    y = bp(y, 180, 7000)                                         # vinyl band
    return y * env * 0.35


def i_scratch(m, dur, p, glide=None, mod=None):
    r = _rng('scratch', m, dur)
    n = int(max(0.12, min(dur, 1.0)) * SR)
    t = _t(n)
    src_len = int(0.6 * SR)                                      # the 'sample': a short sung 'ahh' (formant noise + tone)
    ts = _t(src_len)
    f0 = float(mtof(m))
    voice = saw(f0 * (1 + 0.02 * np.sin(2 * np.pi * 5 * ts)), src_len) * 0.6 + r.standard_normal(src_len) * 0.25
    sample = _formants(voice, np.full(src_len, 750.0), np.full(src_len, 1200.0), 2500.0, q=5.0) * np.exp(-ts / 0.5)
    kind = int(m) % 3                                            # baby / chirp / transformer-ish
    rate = r.choice([4.0, 6.0, 8.0])
    hand = np.sin(2 * np.pi * rate * t)                          # the record pushed back and forth
    pos = (0.5 + 0.45 * hand) * (src_len - 1)
    y = np.interp(pos, np.arange(src_len), sample)
    if kind == 1:                                                # chirp: the fader cuts on the back-stroke
        y *= (np.gradient(hand) > 0)
    elif kind == 2:                                              # transformer: fader chops
        y *= (np.sin(2 * np.pi * rate * 3 * t) > 0)
    y = hp(lp(y, 6500), 250)
    return soft(y * 2.0, 1.3) * np.clip(t / 0.003, 0, 1) * np.clip((n - np.arange(n)) / (0.01 * SR), 0, 1) * 0.6


NEW = {
    'pwmpad': (i_pwmpad, 'PWM string pad (80s / anthem trance)', ['pad', 'chords'], 50),
    'formantlead': (i_formantlead, 'Vocal formant lead (ooh-aah)', ['lead'], 54),
    'fmperc': (i_fmperc, 'FM metal percussion (tuned, techno)', ['arp', 'lead'], 115),
    'modseq': (i_modseq, 'Modular sequence (every step its own patch)', ['arp', 'lead', 'bass'], 81),
    'noisestab': (i_noisestab, 'Berlin noise stab', ['chords', 'arp'], 121),
    'slide808': (i_slide808, '808 with slides (drill / trap)', ['bass'], 38),
    'mpckeys': (i_mpckeys, 'MPC-chopped soul keys (12-bit, dusty)', ['chords', 'lead', 'arp'], 4),
    'soulhorn': (i_soulhorn, 'Soul horn stab (sampled-sounding)', ['chords', 'lead'], 61),
    'scratch': (i_scratch, 'Turntable scratch', ['lead', 'arp', 'fx'], 120),
}
for _k, (_fn, _info, _roles, _gm) in NEW.items():
    INSTRUMENTS[_k] = _fn
    INSTRUMENT_INFO[_k] = _info
    GM_PROGRAM[_k] = _gm
    for _r in _roles:
        if _r in ROLE_CHOICES and _k not in ROLE_CHOICES[_r]:
            ROLE_CHOICES[_r].append(_k)
