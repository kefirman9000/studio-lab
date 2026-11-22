"""(2.5.2) More sounds: trance plucks / pads / leads / bass, acid house's squelchier 303s, and more Celtic instruments."""
import numpy as np

from . import va as _va
from .dsp import SR, eq, lp, mtof
from .instruments import GM_PROGRAM, INSTRUMENT_INFO, INSTRUMENTS, ROLE_CHOICES, _bass_exc, _hpf, _rng, v_acid303


# ---- trance ----

def v_viruspluck(m, dur, p, glide=None, mod=None):
    """Hollow trance pluck in the style of the classic virtual-analog racks: two pulses a few cents apart (thin and
    hollow), a resonant filter that snaps shut and a tiny click - the bouncy 1/16 arp of a breakdown."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.35), 0.02) * SR)
    env = _va.adsr(gate, 0.001, p.get('d', 0.18), 0.0, 0.1)
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    x = np.vstack([_va.pulse(np.full(n, f * 2 ** (-7 / 1200)), n, rng.random(), 0.3) + 0.4 * _va.saw(np.full(n, f * 2), n, rng.random()),
                   _va.pulse(np.full(n, f * 2 ** (7 / 1200)), n, rng.random(), 0.3) + 0.4 * _va.saw(np.full(n, f * 2), n, rng.random())])
    cut = 250 * (p.get('cut', 7000) / 250) ** np.exp(-t / 0.05)
    y = _va.vcf(x * 0.55, cut, 0.55, 1.2) * env
    click = _hpf(rng.standard_normal((2, n)), 3000) * np.exp(-t / 0.002) * 0.05
    return _hpf(y + click, 200) * 0.6


def v_reversepad(m, dur, p, glide=None, mod=None):
    """Reverse-swell pad: a wide supersaw chord that swells up like a reversed reverb tail and cuts off at the next
    chord - the sucking-in 'whoosh' into a trance drop."""
    f = float(mtof(m))
    gate = int(max(dur, 0.2) * SR)
    n = gate + int(0.03 * SR)
    t = np.arange(n) / SR
    x = _va.jp_supersaw(f, n, 0.55, 0.8, 1.0)
    sw = (t / (gate / SR)) ** 2.6
    sw[gate:] = np.linspace(1, 0, n - gate)
    cut = 500 + 5500 * sw
    return _hpf(_va.vcf(x, cut, 0.15, 1.05), 160) * sw * 0.55


def v_sawchoir(m, dur, p, glide=None, mod=None):
    """Trance choir pad: a soft supersaw sung through 'aah' vowel formants, slowly breathing - the angelic wall of a
    breakdown."""
    f = float(mtof(m))
    gate = int(max(dur, 0.1) * SR)
    env = _va.adsr(gate, p.get('a', 0.4), 0.5, 0.9, p.get('r', 0.9))
    n = len(env)
    t = np.arange(n) / SR
    x = _va.jp_supersaw(f, n, 0.35, 0.7, 1.0) * 0.6
    y = sum(eq(x, 'peak', fc, q, g) for fc, q, g in ((750, 4.0, 14.0), (1150, 4.0, 11.0), (2600, 5.0, 8.0))) / 3
    y = lp(y, 6000) * (1 + 0.08 * np.sin(2 * np.pi * 0.3 * t))
    return _hpf(y, 200) * env * 0.4


def v_squarelead(m, dur, p, glide=None, mod=None):
    """Classic trance square lead: two detuned squares and a sub square an octave down, portamento between notes and a
    late vibrato - hollow, singing and nostalgic (late-90s / 2000s trance)."""
    f = float(mtof(m))
    gate = int(max(dur, 0.03) * SR)
    env = _va.adsr(gate, 0.005, 0.2, 0.85, p.get('r', 0.25))
    n = len(env)
    t = np.arange(n) / SR
    fr = np.full(n, f) if glide is None else f + (float(mtof(glide)) - f) * np.exp(-t / 0.06)
    fr = fr * 2 ** (np.clip((t - 0.3) / 0.3, 0, 1) * 14 * np.sin(2 * np.pi * 5.4 * t) / 1200)
    x = np.vstack([_va.pulse(fr * 2 ** (-6 / 1200), n, 0.1, 0.5) + 0.45 * _va.pulse(fr / 2, n, 0.3, 0.5),
                   _va.pulse(fr * 2 ** (6 / 1200), n, 0.6, 0.5) + 0.45 * _va.pulse(fr / 2, n, 0.8, 0.5)])
    y = _va.vcf(x * 0.5, p.get('cut', 4500) * (0.7 + 0.3 * np.exp(-t * 4)), 0.15, 1.1)
    return _hpf(y, 160) * env * 0.5


def v_tribass(m, dur, p, glide=None, mod=None):
    """Rolling trance / psy bass: a punchy triangle-and-saw note per 16th with a fast filter blip on every hit and a
    short tail - the tight, round 'KBass' that rolls under an uplifting or psy track."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.25), 0.02) * SR)
    env = _va.adsr(gate, 0.001, 0.09, 0.35, 0.03)
    n = len(env)
    t = np.arange(n) / SR
    ph = np.cumsum(np.full(n, f)) / SR % 1.0
    tri = 4 * np.abs(ph - 0.5) - 1
    x = tri * 0.8 + 0.4 * _va.saw(np.full(n, f), n, 0.0)
    cut = 180 * (p.get('cut', 2400) / 180) ** np.exp(-t / 0.03)
    y = _va.vcf(x, cut, 0.25, 1.4)
    y = np.tanh(y * 1.3)
    return _hpf(y, 30) * env * 0.7


def v_fmpluck(m, dur, p, glide=None, mod=None):
    """FM pluck: a bright two-operator strike that settles into a soft electric-piano tone - glassy, percussive keys
    for breakdowns and melodic arps."""
    f = float(mtof(m))
    n = int(min(1.6, max(dur, 0.1) + 0.6) * SR)
    t = np.arange(n) / SR
    idx = 3.2 * np.exp(-t / 0.08) + 0.4
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 2 * t))
    y = y + 0.25 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t / 0.05)
    env = np.exp(-t / (0.35 + 60 / f)) * np.minimum(t / 0.001, 1)
    g = int(max(dur, 0.05) * SR)
    if g < n:
        env[g:] *= np.exp(-np.arange(n - g) / (0.08 * SR))
    y = y * env
    return np.vstack([y, np.roll(y, 37)]) * 0.35


# ---- acid ----

def v_acid_squelch(m, dur, p, glide=None, mod=None):
    """The squelchiest 303: resonance near self-oscillation, the envelope cranked and a short decay - every note a
    rubbery 'wow', accents screaming."""
    q = dict(p, res=0.93, envmod=0.95, decay=p.get('decay', 0.28), cut=p.get('cut', 260))
    return v_acid303(m, dur, q, glide, mod)


def v_acid_dist(m, dur, p, glide=None, mod=None):
    """Acid techno 303: a resonant saw 303 slammed into a distortion pedal and band-passed - gritty, nasty and loud."""
    q = dict(p, res=0.8, envmod=0.75, decay=p.get('decay', 0.4), cut=p.get('cut', 420))
    y = v_acid303(m, dur, q, glide, mod)
    y = np.tanh(y * 5.0) * 0.5
    y = eq(eq(y, 'peak', 1200, 0.8, 4.0), 'highshelf', 6000, 0.7, -6.0)
    return _hpf(y, 45) * 0.8


def v_acidlead(m, dur, p, glide=None, mod=None):
    """303 played high as a lead: the square-wave 303 an octave up, a longer decay so the filter sings, slid notes
    gliding - the hypnotic acid line over a house or trance groove."""
    q = dict(p, wave='square', res=0.82, envmod=0.7, decay=p.get('decay', 0.7), cut=p.get('cut', 700))
    y = v_acid303(m + 12, dur, q, None if glide is None else glide + 12, mod)
    y = np.atleast_2d(y)
    if y.shape[0] == 1:
        y = np.vstack([y[0], np.roll(y[0], 61)])
    return _hpf(y, 150) * 0.75


# ---- Celtic ----

def i_tenor_banjo(m, dur, p, glide=None, mod=None):
    """Irish tenor banjo (tuned in fifths, played with a pick): a bright, snappy steel string on a drum head - a hard
    attack, a quick decay and the head's nasal ring."""
    f = float(mtof(m))
    gate = int(max(dur, 0.04) * SR)
    n = gate + int(0.6 * SR)
    y = _va.string(f, n, _bass_exc(f, 'pick', 2.0), t60=0.9 * (300 / max(f, 120)) ** 0.2, bright=0.96,
                   gate=gate, mute_t60=0.12, pickup=0.12)
    y = y + 0.35 * _va.string(f * 2 ** (5 / 1200), n, _bass_exc(f, 'pick', 1.6), t60=0.7, bright=0.94, gate=gate, mute_t60=0.1)
    y = eq(eq(eq(y, 'peak', 650, 2.0, 5.0), 'peak', 2800, 1.4, 5.0), 'peak', 200, 1.0, -6.0)
    return _hpf(y, 160) * 0.32


def i_crwth(m, dur, p, glide=None, mod=None):
    """Crwth - the old Welsh bowed lyre: a rough, reedy bowed string whose bridge buzzes, with the open drone strings
    sounding a fifth and an octave underneath."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    env = _va.adsr(gate, 0.03, 0.1, 0.85, 0.15)
    n = len(env)
    t = np.arange(n) / SR
    rng = _rng()
    jit = np.cumsum(rng.standard_normal(n)) * 0.0008
    jit -= np.linspace(jit[0], jit[-1], n)
    fr = f * 2 ** (jit / 1200)
    x = _va.saw(fr, n, 0.0) * 0.7 + _va.pulse(fr, n, 0.2, 0.2) * 0.3
    x = eq(eq(eq(x, 'peak', 480, 2.0, 5.0), 'peak', 1700, 1.6, 5.0), 'peak', 3300, 2.0, 3.0)
    root = float(mtof(36 + (p.get('key_pcs') or (2,))[0])) * 2
    drones = (_va.saw(np.full(n, root), n, 0.3) + 0.6 * _va.saw(np.full(n, root * 1.5), n, 0.7)) * 0.18
    rosin = _hpf(rng.standard_normal(n), 2500) * 0.035
    y = lp(x + rosin + lp(drones, 1600), 8000)
    return _hpf(y, 120) * env * 0.22


def i_dadgad(m, dur, p, glide=None, mod=None):
    """Celtic guitar in DADGAD: a bright steel string with the open D and A strings ringing along - the modal,
    droning shimmer behind every Irish and Scottish session song."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    n = gate + int(1.6 * SR)
    y = _va.string(f, n, _bass_exc(f, 'pick', 1.4), t60=2.6 * (220 / max(f, 90)) ** 0.3, bright=0.88,
                   gate=gate, mute_t60=0.3, pickup=0.0)
    root = float(mtof(38))
    for k, fr in enumerate((root * 2, root * 3)):
        y = y + 0.12 * _va.string(fr, n, _bass_exc(fr, 'finger', 0.8), t60=3.5, bright=0.7) * (0.8 if k else 1.0)
    y = eq(eq(y, 'peak', 110, 1.2, 2.0), 'peak', 3000, 1.4, 3.0)
    return _hpf(y, 75) * 0.28


NEW_252 = (
    ('viruspluck', v_viruspluck, 'Hollow trance pluck (resonant pulses)', ('arp', 'chords', 'lead'), 81),
    ('reversepad', v_reversepad, 'Reverse-swell supersaw pad (sucks into the drop)', ('pad', 'chords'), 89),
    ('sawchoir', v_sawchoir, 'Trance choir pad (supersaw "aah")', ('pad', 'chords'), 91),
    ('squarelead', v_squarelead, 'Classic trance square lead (portamento)', ('lead',), 80),
    ('tribass', v_tribass, 'Rolling trance / psy bass (tight 16ths)', ('bass',), 38),
    ('fmpluck', v_fmpluck, 'FM pluck (glassy keys)', ('arp', 'chords', 'lead'), 5),
    ('acid_squelch', v_acid_squelch, 'Acid 303, maximum squelch', ('bass', 'arp', 'lead'), 38),
    ('acid_dist', v_acid_dist, 'Acid 303 through distortion (acid techno)', ('bass', 'arp', 'lead'), 38),
    ('acidlead', v_acidlead, 'Acid 303 played high as a lead', ('lead', 'arp'), 81),
    ('tenor_banjo', i_tenor_banjo, 'Irish tenor banjo (picked)', ('arp', 'lead', 'chords'), 105),
    ('crwth', i_crwth, 'Crwth (Welsh bowed lyre with drones)', ('lead', 'pad'), 110),
    ('dadgad', i_dadgad, 'Celtic guitar in DADGAD (open drones ringing)', ('chords', 'arp'), 25),
)
for _name, _fn, _info, _roles, _gm in NEW_252:
    INSTRUMENTS[_name] = _fn
    INSTRUMENT_INFO[_name] = _info
    GM_PROGRAM[_name] = _gm
    for _role in _roles:
        if _name not in ROLE_CHOICES.setdefault(_role, []):
            ROLE_CHOICES[_role].append(_name)
