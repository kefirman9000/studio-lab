"""(2.20) Synths modelled on measured stems of real records (tools/stem_study.py over ~60 songs' stems).

Each sound is built to land on what its family's stems measured - the share of energy below 60 Hz / 60-250 Hz / above,
the spectral centre, how long a note holds (sustain over the beat), the LFO rate that stood out, stereo width:

  rollbass   house / tech house bass stems: ~42 % sub, ~43 % 60-250 Hz, ~6 % above; short notes (held ~0.4), rolling
             16ths or off-beat 8ths. A clean sine sub under a short, low-passed saw 'knock' that gives each note its edge.
  stepsub    140 half-time ('stepper') bass stems: ~65 % sub, ~29 % low, ~2 % above; long held notes; the level / tone
             LFO that stood out most was a half note (7 of 13 records), then a beat and a quarter-triplet. A sine sub with
             a soft octave layer that swells on that LFO (rate from the note's `mod`, default a half note).
  pumpstab   house / techno synth stems: spectral centre ~1.6 kHz, short (sustain ~0.45 of a beat), width ~0.4, sitting
             under deep sidechain (median dip ~9 dB). Two detuned saws + a square, a quick filter snap, wide but not huge.
  dustkeys   boom-bap / hip-hop keys stems: dark (centre ~880 Hz), soft attack, held (~0.7), with tape wow. A soft
             two-operator electric piano through a gentle low-pass and tape saturation.
Only measurements were taken from the records - no audio from them is used.
"""
import numpy as np
from scipy import signal

from . import va
from .dsp import SR, mtof
from .va_bass import sync_hz

_RNG = np.random.default_rng(2020)


def _lp(y, fc, order=2):
    fc = float(np.clip(fc, 40.0, SR * 0.45))
    return signal.sosfilt(signal.butter(order, fc / (SR / 2), output='sos'), y, axis=-1)


def _fade(y, a=0.002, r=0.01):
    n = y.shape[-1]
    ka, kr = min(n, int(a * SR)), min(n, int(r * SR))
    if ka > 1:
        y[..., :ka] *= np.linspace(0, 1, ka)
    if kr > 1:
        y[..., -kr:] *= np.linspace(1, 0, kr)
    return y


def rollbass(m, dur, p, glide=None, mod=None):
    """Rolling house bass: sine sub + a short, low-passed saw knock on each note."""
    f = float(mtof(m))
    while f > 110:
        f /= 2
    while f < 32:
        f *= 2
    gate = max(0.04, float(dur))
    n = int((gate + 0.05) * SR)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * f * t)
    env_s = np.minimum(t / 0.002, 1) * np.where(t < gate, 1.0, np.exp(-(t - gate) / 0.02))
    env_s *= 0.75 + 0.25 * np.exp(-t * 12)
    knock = va.saw(np.full(n, f * 2.0), n, _RNG.random()) * 0.6 + va.saw(np.full(n, f * 2.0 * 1.004), n, _RNG.random()) * 0.4
    cut = float(p.get('cut', 520.0))
    knock = _lp(knock * (0.35 + 0.65 * np.exp(-t * float(p.get('decay', 10.0)))) * env_s, cut, 2)
    y = sub * env_s * 0.46 + knock * 1.15 * np.minimum(t / 0.001, 1)
    y = np.tanh(y * float(p.get('drive', 1.4))) / np.tanh(float(p.get('drive', 1.4)))
    y = signal.lfilter(*signal.butter(1, 25 / (SR / 2), 'high'), y)
    y = _fade(y * 0.8)
    return np.vstack([y, y])


def stepsub(m, dur, p, glide=None, mod=None):
    """140 stepper sub: a clean sine sub held under a soft octave layer that swells on a slow LFO (half note default)."""
    f = float(mtof(m))
    while f > 80:
        f /= 2
    while f < 28:
        f *= 2
    gate = max(0.08, float(dur))
    n = int((gate + 0.08) * SR)
    t = np.arange(n) / SR
    f0 = float(mtof(glide)) if glide is not None else f
    while glide is not None and f0 > 80:
        f0 /= 2
    fr = f + (f0 - f) * np.exp(-t * 18)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    sub = np.sin(ph)
    beats = mod if isinstance(mod, (int, float)) and not isinstance(mod, bool) and mod else float(p.get('lfo_beats', 2.0))
    hz = sync_hz(beats, p.get('spb', 0.43))
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * hz * t)                       # starts closed, swells each cycle
    octv = np.sin(2 * ph) * 0.6 + np.sin(3 * ph) * 0.18                 # soft upper layer (octave + a little 3rd harmonic)
    octv = _lp(octv * (0.15 + 0.85 * lfo) * float(p.get('wob', 2.1)), 240 + 640 * float(p.get('open', 0.6)), 2)
    env = np.minimum(t / 0.006, 1) * np.where(t < gate, 1.0, np.exp(-(t - gate) / 0.04))
    y = np.tanh((sub + octv) * env * float(p.get('drive', 1.2))) * 0.85
    y = signal.lfilter(*signal.butter(1, 22 / (SR / 2), 'high'), y)
    return np.vstack([y, y])


def pumpstab(m, dur, p, glide=None, mod=None):
    """House / techno chord stab: detuned saws + square, a quick filter snap, wide, short."""
    f = float(mtof(m))
    gate = max(0.05, min(float(dur), float(p.get('max_len', 0.5))))
    n = int((gate + 0.18) * SR)
    t = np.arange(n) / SR
    det = float(p.get('detune', 9.0))
    core = va.saw(np.full(n, f), n, _RNG.random()) + 0.5 * va.pulse(np.full(n, f), n, _RNG.random(), 0.45)
    side = va.saw(np.full(n, f * 2 ** (det / 1200)), n, _RNG.random()) - va.saw(np.full(n, f * 2 ** (-det / 1200)), n, _RNG.random())
    L, R = core + 0.32 * side, core - 0.32 * side                    # mostly centred, a measured ~0.4 of width
    cut0, cut1 = float(p.get('cut', 7000.0)), float(p.get('cut_end', 2900.0))
    cut_env = cut1 + (cut0 - cut1) * np.exp(-t * float(p.get('snap', 10.0)))
    # block-wise filter sweep (state carried)
    out = np.zeros((2, n))
    for c, x in enumerate((L, R)):
        zi = np.zeros((2, 2))
        blk = 256
        for s in range(0, n, blk):
            e = min(n, s + blk)
            sos = signal.butter(4, min(SR * 0.45, cut_env[s]) / (SR / 2), output='sos')
            out[c, s:e], zi = signal.sosfilt(sos, x[s:e], zi=zi)
    dk = float(p.get('decay', 2.2))
    env = np.minimum(t / 0.002, 1) * np.where(t < gate, np.exp(-t * dk), np.exp(-gate * dk) * np.exp(-(t - gate) / 0.06))
    out *= env * 0.35
    return _fade(out)


def dustkeys(m, dur, p, glide=None, mod=None):
    """Boom-bap keys: a soft two-operator electric piano, dark, with tape wow and saturation."""
    f = float(mtof(m))
    gate = max(0.08, float(dur))
    n = int((gate + 0.6) * SR)
    t = np.arange(n) / SR
    wow = 1 + 0.0025 * np.sin(2 * np.pi * 0.7 * t + _RNG.random() * 6.28) + 0.001 * np.sin(2 * np.pi * 5.3 * t)
    ph = 2 * np.pi * np.cumsum(f * wow) / SR
    idx = float(p.get('bark', 3.2)) * np.exp(-t * 4) + 0.8
    y = np.sin(ph + idx * np.sin(ph)) + 0.18 * np.sin(2 * ph) * np.exp(-t * 3)
    env = np.minimum(t / 0.006, 1) * np.exp(-t * float(p.get('decay', 1.3)))
    env *= np.where(t < gate, 1.0, np.exp(-(t - gate) / 0.15))
    y = _lp(y * env, float(p.get('cut', 7500.0)), 2)
    y = np.tanh(y * 1.3) * 0.6
    l_ = y
    r_ = 0.88 * y + 0.12 * np.concatenate([np.zeros(int(0.0007 * SR)), y])[:n]   # a hair of width (a stereo tine)
    return _fade(np.vstack([l_, r_]))


NEW_220 = (
    ('rollbass', rollbass, 'Rolling house bass (sine sub + short saw knock) - modelled on house bass stems', 38),
    ('stepsub', stepsub, '140 stepper sub (sine sub + slow swelling octave layer) - modelled on dubstep bass stems', 38),
    ('pumpstab', pumpstab, 'House / techno chord stab (detuned saws, filter snap) - modelled on house synth stems', 81,
     ('chords', 'lead', 'arp')),
    ('dustkeys', dustkeys, 'Dusty boom-bap keys (soft FM e-piano, tape wow) - modelled on hip-hop keys stems', 4,
     ('chords', 'lead', 'pad')),
)


def register():
    from .instruments import GM_PROGRAM, INSTRUMENT_INFO, INSTRUMENTS, ROLE_CHOICES
    for name, fn, info, gm, *roles in NEW_220:
        INSTRUMENTS[name] = fn
        INSTRUMENT_INFO[name] = info
        GM_PROGRAM[name] = gm
        for role in (roles[0] if roles else ('bass',)):
            if name not in ROLE_CHOICES.setdefault(role, []):
                ROLE_CHOICES[role].append(name)
