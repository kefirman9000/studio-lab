"""Studio Lab 2.22 instruments: the sounds of the fast African electronic dance genres (Shangaan electro, kuduro,
singeli, batida, Congolese electronics, balani show, mahraganat ...), all synthesized here - no samples.

Melodic
    mbira          thumb piano on a gourd, bottle-cap buzz sizzling under each note             Shona, singeli, Afro folk
    likembe        amplified thumb piano through a cheap, overdriven amp (Kinshasa street style) Congolese electronics
    casiomarimba   the cheap home-keyboard marimba preset: 2-op FM, low sample rate, tinny     Shangaan electro, Tsonga disco
    casiolead      cheap home-keyboard lead: thin pulse, delayed vibrato, 8-bit grit            Shangaan, singeli, balani
    ngoni          West African lute: bright, nasal plucked string on a skin-covered body       balani, Mande, desert
    mizmar         Egyptian shawm: loud, nasal double reed with a wide vibrato                  mahraganat, shaabi
    kudurostab     gritty detuned square stab with a pitch drop and bit grit                    kuduro, batida
    casiobass      cheap keyboard FM bass: short, bouncy, rubbery                               singeli, Shangaan, coupe-decale
Drums
    djembe / djembe_slap / djembe_bass    the three djembe strokes (tone, slap, bass)
    talkdrum       talking drum: a squeezed hourglass drum whose pitch bends on each hit
    shekere        gourd rattle with a net of beads
    agogo / agogo_lo                     the two bells of an agogo
    ferrinho       Cape Verdean scraped iron bar (funana)
    refwhistle     a referee's pea whistle (the Shangaan / batucada party whistle)
    udu            Nigerian clay pot drum: a deep, liquid whoop
    dundun         the djembe ensemble's big bass drum, with its bell
"""
import zlib

import numpy as np

from .dsp import SR, mtof, lp, hp, bp, eq, noise, fade_out
from .instruments import INSTRUMENTS, INSTRUMENT_INFO, ROLE_CHOICES, GM_PROGRAM, DRUMS, _ms_stereo, _modes, _bass_exc
from . import va as _va
from . import dsp


def _rng(name, m, dur, k=0):
    return np.random.default_rng(zlib.crc32(f'{name}|{float(m):.2f}|{float(dur):.3f}|{k}'.encode()))


def _t(n):
    return np.arange(n) / SR


def _crush(y, rate=16000, bits=8):
    """A cheap keyboard's DAC: sample-and-hold at a low rate (aliasing) and a few bits."""
    hold = max(1, int(SR / rate))
    y = np.repeat(y[::hold], hold)[:len(y)] if hold > 1 else y
    q = 2.0 ** (bits - 1)
    return np.round(np.clip(y, -1, 1) * q) / q


# ----------------------------------------------------------------------------------------------- thumb pianos
def _thumb(name, m, dur, p, buzz=0.18):
    f = float(mtof(m))
    n = int(min(2.4, 0.8 + 320 / f) * SR)
    r = _rng(name, m, dur)
    t = _t(n)
    y = _modes(f, n, [(1.0, 1.0, 2.0), (5.4, 0.25, 20.0), (11.9, 0.08, 48.0)], p.get('hard', 1.1), rng=r)
    env = np.abs(y)
    env = lp(env, 40)
    caps = bp(r.standard_normal(n), 2500, 9000) * (env / (env.max() + 1e-9)) ** 0.8 * buzz       # bottle caps sizzling
    caps *= 1 + 0.6 * np.sin(2 * np.pi * f * t)                                                  # rattling in time with the tine
    click = 0.08 * bp(r.standard_normal(n), 700, 4000) * np.exp(-t * 260)
    y = eq(y, 'peak', 350, 0.9, 4.0)                                                             # the gourd resonator
    return (y + caps + click) * np.minimum(t / 0.001, 1)


def i_mbira(m, dur, p, glide=None, mod=None):
    """Mbira: metal tines over a hollow gourd with bottle caps that buzz - a round, ringing note with a sizzle under it."""
    return _ms_stereo(fade_out(_thumb('mbira', m, dur, p), 0.08), 22) * 0.42


def i_likembe(m, dur, p, glide=None, mod=None):
    """Electric likembe: a thumb piano with a pickup through a small, overdriven amplifier - fuzzy, buzzing and loud."""
    y = _thumb('likembe', m, dur, p, buzz=0.3)
    y = np.tanh(eq(y, 'peak', 900, 1.0, 6.0) * p.get('drive', 5.0)) * 0.5      # a cheap amp pushed hard
    y = fade_out(bp(y, 180, 5200), 0.08)
    return _ms_stereo(y, 30) * 0.75


# ----------------------------------------------------------------------------------------------- cheap keyboards
def i_casiomarimba(m, dur, p, glide=None, mod=None):
    """The home-keyboard marimba preset: a 2-operator FM knock with a fast decay, played back at a low sample rate."""
    f = float(mtof(m))
    n = int(min(1.0, 0.25 + 120 / f) * SR)
    t = _t(n)
    idx = 2.4 * np.exp(-t * 40)
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t * (7 + f / 220))
    y = _crush(y * 0.9, 14000, 9)
    return _ms_stereo(lp(y, 7000), 18) * 0.75


def i_casiolead(m, dur, p, glide=None, mod=None):
    """Cheap keyboard lead: a thin pulse with vibrato that comes in after a moment, a little 8-bit grit, tinny top."""
    f = float(mtof(m))
    gate = int(max(dur, 0.04) * SR)
    env = _va.adsr(gate, 0.004, 0.08, 0.8, 0.06)
    n = len(env)
    t = _t(n)
    vib = 1 + 0.009 * np.sin(2 * np.pi * 6.0 * t) * np.clip((t - 0.18) / 0.2, 0, 1)
    fr = f * vib
    y = _va.pulse(fr, n, 0.0, 0.28) * 0.6 + 0.25 * _va.pulse(fr * 2, n, 0.3, 0.5)
    y = _crush(lp(y, 6000) * 0.8, 20000, 8)
    y = eq(hp(y, 250), 'peak', 2200, 1.0, 3.0)
    return _ms_stereo(y * env, 26) * 0.75


def i_casiobass(m, dur, p, glide=None, mod=None):
    """Cheap keyboard FM bass: short and bouncy, a rubbery attack that settles to a round tone."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.6), 0.05) * SR)
    env = _va.adsr(gate, 0.002, 0.18, 0.55, 0.05)
    n = len(env)
    t = _t(n)
    idx = 1.6 * np.exp(-t * 14) + 0.3
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    y = _crush(y * 0.85, 22000, 10)
    return np.vstack([y, y]) * env * 1.6


def i_kudurostab(m, dur, p, glide=None, mod=None):
    """Kuduro stab: detuned squares, a quick downward pitch drop on the attack, grit - short and aggressive."""
    f = float(mtof(m))
    gate = int(max(min(dur, 0.4), 0.04) * SR)
    env = _va.adsr(gate, 0.001, 0.12, 0.35, 0.05)
    n = len(env)
    t = _t(n)
    drop = 1 + 0.06 * np.exp(-t * 60)
    y = sum(_va.pulse(f * drop * (1 + d), n, ph, 0.5) for d, ph in ((-0.008, 0.1), (0.0, 0.5), (0.009, 0.8))) / 3
    y = np.tanh(lp(y, 5200) * 2.2)
    y = _crush(y * 0.8, 24000, 7)
    return _ms_stereo(y * env, 40) * 0.85


# ----------------------------------------------------------------------------------------------- strings & reeds
def i_ngoni(m, dur, p, glide=None, mod=None):
    """Ngoni: a West African lute, gut or nylon strings over a skin-covered wooden body - bright, nasal, plucked hard."""
    f = float(mtof(m))
    gate = int(max(dur, 0.04) * SR)
    n = gate + int(0.5 * SR)
    exc = _bass_exc(f, 'pick', 1.2)
    y = _va.string(f, n, exc, t60=p.get('t60', 1.3), bright=0.72, gate=gate, mute_t60=0.25, pickup=0.12)
    t = _t(len(y))
    body = eq(eq(hp(y, 90), 'peak', 1400, 1.6, 4.5), 'peak', 220, 1.2, 3.0)   # the skin: nasal and bright, the
    y = np.tanh(body * 1.3) * 0.8 * np.minimum(t / 0.0012, 1)                  # wooden body keeps the fundamental
    return _ms_stereo(fade_out(y, 0.05), 20) * 1.1


def i_mizmar(m, dur, p, glide=None, mod=None):
    """Mizmar: a loud double-reed shawm - a bright, nasal, buzzing tone with a wide, fast vibrato."""
    f = float(mtof(m))
    gate = int(max(dur, 0.05) * SR)
    env = _va.adsr(gate, 0.025, 0.1, 0.9, 0.08)
    n = len(env)
    t = _t(n)
    r = _rng('mizmar', m, dur)
    vib = 1 + 0.012 * np.sin(2 * np.pi * 6.5 * t + r.random() * 6.28) * np.clip(t / 0.15, 0, 1)
    fr = f * vib
    x = _va.saw(fr, n, r.random()) * 0.6 + _va.pulse(fr, n, r.random(), 0.3) * 0.4
    x = eq(eq(eq(x, 'peak', 1250, 2.0, 10.0), 'peak', 2600, 2.5, 7.0), 'peak', 400, 1.0, -6.0)
    x = np.tanh(hp(x, 220) * 1.8)
    breath = 0.04 * bp(r.standard_normal(n), 1500, 5000)
    return _ms_stereo(hp(lp(x + breath, 7500), 90) * env, 28) * 0.55


# ----------------------------------------------------------------------------------------------- drums
def _rngd():
    return dsp.get_rng()


def _membrane(f0, f1, n, decay, bend_t=0.05):
    t = _t(n)
    f = f1 + (f0 - f1) * np.exp(-t / bend_t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)


def d_djembe(p):
    """Djembe tone: an open, ringing mid stroke at the edge of the skin."""
    n = int(0.35 * SR)
    f = p.get('pitch', 330)
    y = _membrane(f * 1.15, f, n, 16) + 0.35 * _membrane(f * 2.3, f * 2.1, n, 30)
    y += 0.15 * bp(noise(n), 1500, 6000) * np.exp(-_t(n) * 120)
    return fade_out(np.tanh(y * 1.2), 0.03)


def d_djembe_slap(p):
    """Djembe slap: the fingers crack against the edge - a bright, sharp, popping stroke."""
    n = int(0.2 * SR)
    t = _t(n)
    f = p.get('pitch', 520)
    y = 0.5 * _membrane(f * 1.3, f, n, 35) + 0.9 * bp(noise(n), 1800, 9000) * np.exp(-t * 70)
    return fade_out(np.tanh(eq(y, 'peak', 3500, 1.0, 5.0) * 1.6), 0.02)


def d_djembe_bass(p):
    """Djembe bass: the palm in the middle of the skin - a deep, round boom from the goblet."""
    n = int(0.5 * SR)
    f = p.get('pitch', 75)
    y = _membrane(f * 1.6, f, n, 9, 0.03) + 0.1 * bp(noise(n), 200, 1200) * np.exp(-_t(n) * 60)
    return fade_out(y, 0.05)


def d_talkdrum(p):
    """Talking drum: the player squeezes the cords as he strikes, so the pitch glides up or down - it speaks."""
    n = int(0.45 * SR)
    t = _t(n)
    r = _rngd()
    f = p.get('pitch', 180) * (0.85 + 0.35 * r.random())
    up = r.random() < 0.6
    target = f * (1.45 if up else 0.7)
    fr = target + (f - target) * np.exp(-t / (0.06 + 0.08 * r.random()))
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 9)
    y += 0.25 * np.sin(2 * np.pi * np.cumsum(fr * 2.2) / SR) * np.exp(-t * 18)
    y += 0.2 * bp(noise(n), 800, 4000) * np.exp(-t * 150)                          # the curved stick
    return fade_out(np.tanh(y * 1.3), 0.04)


def d_shekere(p):
    """Shekere: a gourd wrapped in a net of beads - shaken, the beads hit the shell in a soft, gritty burst."""
    n = int(0.16 * SR)
    t = _t(n)
    r = _rngd()
    grains = (r.random(n) < 0.02).astype(float) * r.standard_normal(n)
    y = bp(grains * 3 + 0.4 * noise(n), 2500, 9000) * (np.minimum(t / 0.012, 1) * np.exp(-t * 28))
    y += 0.25 * _membrane(260, 240, n, 40)                                            # the gourd's knock
    return fade_out(y, 0.02)


def _bell(f, n, decay):
    t = _t(n)
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * decay * k ** 0.5) for k, a in ((1.0, 1.0), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)))
    return y + 0.2 * bp(noise(n), 3000, 9000) * np.exp(-t * 300)


def d_agogo(p):
    """Agogo, high bell."""
    return fade_out(_bell(p.get('pitch', 1050), int(0.3 * SR), 18), 0.03) * 0.8


def d_agogo_lo(p):
    """Agogo, low bell."""
    return fade_out(_bell(p.get('pitch', 760), int(0.35 * SR), 15), 0.03) * 0.8


def d_ferrinho(p):
    """Ferrinho: a knife scraped down a ridged iron bar - a rasping, metallic zip (funana's motor)."""
    n = int(0.12 * SR)
    t = _t(n)
    ridges = np.sin(2 * np.pi * 95 * t) > 0.6                                         # the blade hitting each ridge
    y = bp(noise(n), 3000, 11000) * (0.3 + ridges) * np.minimum(t / 0.01, 1) * np.exp(-t * 22)
    y += 0.15 * np.sin(2 * np.pi * 4100 * t) * ridges * np.exp(-t * 30)
    return fade_out(y, 0.02)


def d_refwhistle(p):
    """A referee's pea whistle: a shrill tone trilled by the little ball inside."""
    n = int(p.get('len', 0.22) * SR)
    t = _t(n)
    f = p.get('pitch', 2900)
    trill = 1 + 0.5 * np.sin(2 * np.pi * 42 * t)
    y = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.01 * np.sin(2 * np.pi * 42 * t))) / SR) * trill
    y += 0.15 * bp(noise(n), 2000, 6000)
    env = np.minimum(t / 0.01, 1) * np.minimum((t[-1] - t) / 0.02, 1)
    return y * env * 0.5


def d_udu(p):
    """Udu: a clay pot drum - a hand slapped over the side hole gives a deep, liquid 'whoop' that bends up."""
    n = int(0.45 * SR)
    t = _t(n)
    f = p.get('pitch', 95)
    fr = f * (1 + 0.6 * (1 - np.exp(-t / 0.05)))                                       # the air in the pot: pitch rises
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 7) * np.minimum(t / 0.004, 1)
    y += 0.2 * bp(noise(n), 300, 2000) * np.exp(-t * 90)
    return fade_out(y, 0.05)


def d_dundun(p):
    """Dundun: the big cylinder bass drum of a djembe ensemble, struck with a stick, a bell on top clanking with it."""
    n = int(0.5 * SR)
    t = _t(n)
    f = p.get('pitch', 70)
    y = _membrane(f * 1.4, f, n, 8, 0.02) + 0.3 * _membrane(f * 2.6, f * 2.4, n, 20)
    y += 0.25 * bp(noise(n), 1000, 5000) * np.exp(-t * 120)                            # the stick
    y += 0.35 * _bell(1250, n, 22)                                                      # the bell
    return fade_out(np.tanh(y * 1.2), 0.05)


NEW = {
    'mbira': (i_mbira, 'Mbira (thumb piano, buzzing gourd)', ('arp', 'lead', 'chords'), 108),
    'likembe': (i_likembe, 'Electric likembe (amplified, fuzzy thumb piano)', ('arp', 'lead'), 108),
    'casiomarimba': (i_casiomarimba, 'Home-keyboard marimba (cheap FM, tinny)', ('arp', 'lead', 'chords'), 12),
    'casiolead': (i_casiolead, 'Home-keyboard lead (thin pulse, vibrato)', ('lead', 'arp'), 80),
    'casiobass': (i_casiobass, 'Home-keyboard FM bass (bouncy, rubbery)', ('bass',), 38),
    'kudurostab': (i_kudurostab, 'Kuduro stab (gritty detuned square)', ('chords', 'lead', 'arp'), 81),
    'ngoni': (i_ngoni, 'Ngoni (West African lute, bright and nasal)', ('arp', 'lead', 'chords'), 105),
    'mizmar': (i_mizmar, 'Mizmar (Egyptian shawm, loud nasal reed)', ('lead',), 111),
}
for _k, (_fn, _info, _roles, _gm) in NEW.items():
    INSTRUMENTS[_k] = _fn
    INSTRUMENT_INFO[_k] = _info
    GM_PROGRAM[_k] = _gm
    for _r in _roles:
        if _r in ROLE_CHOICES and _k not in ROLE_CHOICES[_r]:
            ROLE_CHOICES[_r].append(_k)

NEW_DRUMS = {'djembe': d_djembe, 'djembe_slap': d_djembe_slap, 'djembe_bass': d_djembe_bass, 'talkdrum': d_talkdrum,
             'shekere': d_shekere, 'agogo': d_agogo, 'agogo_lo': d_agogo_lo, 'ferrinho': d_ferrinho, 'refwhistle': d_refwhistle,
             'udu': d_udu, 'dundun': d_dundun}


def _peak(fn, level=0.9):
    def d(p):
        y = fn(p)
        return y * (level / (np.abs(y).max() + 1e-9))
    d.__doc__ = fn.__doc__
    return d


NEW_DRUMS = {k: _peak(v) for k, v in NEW_DRUMS.items()}
DRUMS.update(NEW_DRUMS)
DRUM_LABELS = {'djembe': 'Djembe (tone)', 'djembe_slap': 'Djembe (slap)', 'djembe_bass': 'Djembe (bass)',
               'talkdrum': 'Talking drum', 'shekere': 'Shekere', 'agogo': 'Agogo (high)', 'agogo_lo': 'Agogo (low)',
               'ferrinho': 'Ferrinho (scraper)', 'refwhistle': 'Party whistle',
               'udu': 'Udu (clay pot drum)', 'dundun': 'Dundun (bass drum + bell)'}
DRUM_GM = {'djembe': 63, 'djembe_slap': 62, 'djembe_bass': 64, 'talkdrum': 47, 'shekere': 82, 'agogo': 67, 'agogo_lo': 68,
           'ferrinho': 73, 'refwhistle': 72, 'udu': 64, 'dundun': 41}
