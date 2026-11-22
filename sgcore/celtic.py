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


def c_bagpipe(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    env = _gate(dur, 0.003, 0.01, 1.0, 0.015)                     # no dynamics: on, or off
    n = len(env)
    y = _chanter(f, n, 9.0, 7500)
    return hp(soft(y * 1.4, 1.2), 300) * env * 0.2


def c_bagpipe_drones(m, dur, p, glide=None, mod=None):
    f = float(mtof(m))
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    x = sum(a * (square(f * r * 2 ** (c / 1200), n, pw=0.2) * 0.6 + saw(f * r * 2 ** (c / 1200), n) * 0.4)
            for r, a, c in ((1.0, 1.0, 0), (1.0, 0.9, 3), (0.5, 0.8, -2)))          # two tenors, one bass
    env = np.minimum(t / 0.25, 1) * np.clip((dur + 0.4 - t) / 0.3, 0, 1)
    return eq(lp(x, 3000), 'peak', 1000, 1.5, 4.0) * env * 0.07


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


NEW = {
    'fiddle': (c_fiddle, 'Fiddle (session / folk bowing)', 110, ('lead', 'arp')),
    'bouzouki': (c_bouzouki, 'Irish bouzouki (paired steel courses)', 25, ('chords', 'arp')),
    'irish_flute': (c_irish_flute, 'Irish wooden flute (breathy)', 73, ('lead', 'arp')),
    'lowwhistle': (c_lowwhistle, 'Low whistle (soft, airy)', 78, ('lead',)),
    'concertina': (c_concertina, 'Concertina (free reeds)', 21, ('lead', 'chords', 'pad')),
    'uilleann': (c_uilleann, 'Uilleann pipes (chanter + drones)', 109, ('lead', 'pad')),
    'bagpipe': (c_bagpipe, 'Great Highland bagpipe (chanter)', 109, ('lead',)),
    'bagpipe_drones': (c_bagpipe_drones, 'Highland bagpipe drones', 109, ('pad',)),
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


def ornament_pass(evs, tracks, sections, st, bpm, seed):
    """Cuts, taps and rolls (trad) or Highland gracenotes (pipes) on every lead-layer part - see the module docstring."""
    import random
    style = st.get('celtic_orn')
    if not style:
        return
    rnd = random.Random(f'{seed}-celtic-orn')
    leads = {n for n, t in tracks.items() if t.get('layer') == 'lead'}
    chords = [e for e in evs if e.track in ('chords', 'pad')]
    scale = {e.midi % 12 for e in chords} if chords else None
    if not scale or len(scale) < 5:
        scale = {e.midi % 12 for e in evs if e.track in leads} or set(range(12))
    sec_beat = 60.0 / max(40, bpm)
    g = 0.045 / sec_beat                                            # a grace note: ~45 ms, in beats
    new = []
    lead_evs = sorted((e for e in evs if e.track in leads), key=lambda e: (e.track, e.beat))
    prev = {}
    for e in lead_evs:
        p = prev.get(e.track)
        prev[e.track] = e
        if style == 'pipes':
            if p is not None and p.midi == e.midi or rnd.random() < 0.1 or e.dur < 2.5 * g:
                continue
            hg = max(m for m in range(e.midi, e.midi + 13) if m % 12 in scale)   # 'high G': the top of the scale
            on_beat = abs(e.beat - round(e.beat)) < 0.01
            if on_beat and e.dur > 4 * g and rnd.random() < 0.45:            # a doubling: high G, the note, a D
                lo = _step(e.midi, scale, True)
                new += [Ev(e.track, e.beat - g, g * 0.9, hg, e.vel), Ev(e.track, e.beat, g * 0.9, e.midi, e.vel),
                        Ev(e.track, e.beat + g, g * 0.9, lo, e.vel)]
                e.beat += 2 * g
                e.dur -= 2 * g
            else:
                new.append(Ev(e.track, e.beat - g, g * 0.9, hg, e.vel))
            continue
        # trad: cuts, taps, rolls
        if e.dur >= 0.75 and rnd.random() < 0.35:                         # a roll on the long notes
            cut, tap = _step(e.midi, scale, True), _step(e.midi, scale, False)
            third = e.dur / 3
            new += [Ev(e.track, e.beat + third - g, g, cut, e.vel * 0.85), Ev(e.track, e.beat + third, third - g, e.midi, e.vel),
                    Ev(e.track, e.beat + 2 * third - g, g, tap, e.vel * 0.85), Ev(e.track, e.beat + 2 * third, third, e.midi, e.vel)]
            e.dur = third - g
        elif e.dur >= 0.4 and rnd.random() < 0.45:                       # a cut
            new.append(Ev(e.track, e.beat - g, g, _step(e.midi, scale, True), e.vel * 0.8))
        elif e.dur >= 0.4 and rnd.random() < 0.12:                       # a tap
            new.append(Ev(e.track, e.beat - g, g, _step(e.midi, scale, False), e.vel * 0.8))
    evs.extend(x for x in new if x.beat >= 0)
