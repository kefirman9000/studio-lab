"""Built-in effects on the parts: chorus, phaser, flanger, tremolo, auto-wah, bit-crusher, OTT, stereo widener,
drive, synced echoes and a slow filter sweep.

The renderer has had these pedals for a while (render.track_fx & co.), but only a few genres switched them on in their
track list, so most songs never used them. Now:
  * the genre picks: each electronic / pop family has the effects that suit each part (house chords through a chorus or
    a phaser, a dotted-8th echo on a trance lead, OTT on a dubstep bass, a slow filter sweep on a techno arp ...).
    Every song rolls its own, so two songs of one genre don't share one sound. A part the genre already dressed in
    its track list keeps that.
  * you pick: every part in the Parts panel has an effect chain - add as many as you like with "+ FX"
    (opts.part_effects {part: [preset ids]}; [] = dry, even if the genre had one). The genre's picks for your last
    song show on the part until you change them. The pedals always run in the same order (amp > drive > chorus >
    phaser / flanger / tremolo / wah / crush / wide / OTT > filter sweep > echo send), whatever order you add them.
"""
import random

from .genre_groups import group_of

# id -> (menu label, track settings it sets)
PRESETS = {
    'chorus':  ('Chorus (warm, wide)', {'chorus': 0.35}),
    'phaser':  ('Phaser (slow swirl)', {'phaser': 0.35}),
    'flanger': ('Flanger (jet sweep)', {'flanger': 0.3}),
    'trem8':   ('Tremolo (8ths)', {'trem': {'rate': 0.5, 'depth': 0.35}}),
    'trem16':  ('Tremolo (16ths, gated feel)', {'trem': {'rate': 0.25, 'depth': 0.45}}),
    'wah':     ('Auto-wah (funky)', {'wah': 0.5}),
    'crush_l': ('Bit-crusher (light grit)', {'crush': 0.25}),
    'crush':   ('Bit-crusher (lo-fi)', {'crush': 0.5}),
    'ott':     ('OTT (dense, forward)', {'ott': 0.4}),
    'wide':    ('Stereo widener', {'wide': 0.5}),
    'drive_l': ('Drive (warm)', {'drive': 0.2}),
    'drive':   ('Drive (dirty)', {'drive': 0.45}),
    'echo_8':  ('Echo (1/8)', {'dly': 0.3, 'dly_time': 0.5}),
    'echo_d8': ('Echo (dotted 1/8)', {'dly': 0.3, 'dly_time': 0.75}),
    'echo_q':  ('Echo (1/4)', {'dly': 0.28, 'dly_time': 1.0}),
    'sweep':   ('Filter sweep (slow, 16 bars)', {'sweep': (400.0, 7000.0, 16)}),
}
# the settings that count as "an effect" (a part with any of these is already dressed by its genre)
FX_KEYS = ('chorus', 'phaser', 'flanger', 'trem', 'wah', 'crush', 'ott', 'wide', 'drive', 'sweep', 'leslie_fx', 'gate')

# genre family -> part -> [(preset, weight)]
_HOUSE = {'chords': [('chorus', 3), ('phaser', 2), ('wide', 1), ('echo_d8', 1)],
          'lead': [('echo_d8', 3), ('chorus', 1), ('phaser', 1)],
          'arp': [('echo_8', 2), ('phaser', 1), ('sweep', 1)],
          'pad': [('wide', 2), ('chorus', 2), ('phaser', 1)],
          'bass': [('drive_l', 1)]}
_TECHNO = {'arp': [('echo_d8', 3), ('sweep', 2), ('crush_l', 1), ('phaser', 1)],
           'chords': [('sweep', 2), ('trem16', 1), ('wide', 1), ('echo_d8', 1)],
           'pad': [('wide', 3), ('phaser', 1), ('trem16', 1)],
           'lead': [('echo_d8', 3), ('wide', 1)],
           'bass': [('drive_l', 2)]}
_BASS = {'bass': [('ott', 3), ('drive', 1)],
         'chords': [('wide', 2), ('ott', 1), ('chorus', 1)],
         'pad': [('wide', 2), ('phaser', 1)],
         'lead': [('ott', 1), ('echo_d8', 2)],
         'arp': [('echo_8', 2), ('flanger', 1)]}
_DNB = {'pad': [('phaser', 3), ('wide', 2)],
        'chords': [('chorus', 2), ('phaser', 2)],
        'bass': [('drive_l', 2)],
        'lead': [('echo_d8', 2), ('chorus', 1)],
        'arp': [('echo_8', 2), ('flanger', 1)]}
_HIPHOP = {'lead': [('echo_d8', 2), ('crush_l', 1)],
           'chords': [('chorus', 2), ('trem8', 1)],
           'pad': [('wide', 2)],
           'arp': [('echo_8', 1)]}
_POP = {'chords': [('chorus', 2), ('wide', 1)],
        'pad': [('wide', 2), ('chorus', 1)],
        'lead': [('echo_d8', 2)],
        'arp': [('echo_8', 2)]}
_CHILL = {'chords': [('chorus', 3), ('trem8', 1), ('phaser', 1)],
          'pad': [('wide', 2), ('phaser', 1)],
          'lead': [('echo_d8', 2), ('echo_q', 1)],
          'arp': [('echo_8', 2), ('echo_d8', 1)]}
_RETRO = {'chords': [('chorus', 3)],
          'pad': [('chorus', 2), ('wide', 1)],
          'lead': [('echo_d8', 2), ('chorus', 1)],
          'arp': [('echo_8', 2)]}
FAMILY = {'House & Disco': _HOUSE, 'Techno & Trance': _TECHNO, 'Dubstep, Garage & Bass': _BASS,
          'Drum & Bass, Breaks & Hard': _DNB, 'Hip-Hop, Trap & Phonk': _HIPHOP, 'Pop, R&B & Hopecore': _POP,
          'Afro, Latin & Caribbean': _POP, 'Chill, Lo-fi & Ambient': _CHILL, 'Retro & Video Game': _RETRO,
          'Footwork & Juke': _HIPHOP}
CHANCE = 0.45            # how often a part gets an effect from its genre (the rest stay dry: room in the mix)
MELODIC = ('lead', 'arp', 'chords', 'pad', 'bass')


def _clear(t):
    for k in FX_KEYS + ('dly_time',):
        t.pop(k, None)                                   # (the part's plain delay / reverb send stays - that's the mix)


def describe(t):
    """The preset ids a track is wearing (effects from the genre's own track list reported by the nearest preset)."""
    out = []
    for k in ('chorus', 'phaser', 'flanger', 'wah', 'ott', 'wide'):
        if t.get(k):
            out.append(k)
    if t.get('trem'):
        tr = t['trem'] if isinstance(t['trem'], dict) else {}
        out.append('trem16' if float(tr.get('rate', 0.25)) <= 0.3 else 'trem8')
    if t.get('crush'):
        out.append('crush_l' if float(t['crush']) < 0.4 else 'crush')
    if t.get('drive'):
        out.append('drive_l' if float(t['drive']) < 0.3 else 'drive')
    if t.get('dly') and t.get('dly_time'):
        dt = float(t['dly_time'])
        out.append(min(('echo_8', 0.5), ('echo_d8', 0.75), ('echo_q', 1.0), key=lambda e: abs(e[1] - dt))[0])
    if t.get('sweep'):
        out.append('sweep')
    if t.get('leslie_fx'):
        out.append('leslie')
    if t.get('gate'):
        out.append('gate')
    return out


EXTRA_LABELS = {'leslie': 'Rotary speaker', 'gate': 'Trance gate'}


def label(pid):
    return PRESETS[pid][0] if pid in PRESETS else EXTRA_LABELS.get(pid, pid)


def apply(st, tracks, opts, sname):
    """Genre picks + your picks. Returns {part: [preset ids]} for the main track of each part."""
    mine = dict(getattr(opts, 'part_effects', None) or {})
    fam = FAMILY.get(group_of(sname)) if st.get('category') == 'Electronic' or group_of(sname) in FAMILY else None
    rnd = random.Random((getattr(opts, 'seed', 0) or 0) * 59 + 11)
    picked = {}
    for role in MELODIC:
        group = [t for t in tracks.values() if t.get('layer') == role]
        if not group:
            continue
        if role in mine:                                 # yours: one effect or a chain of several ([] / 'none' = dry)
            chain = mine[role]
            chain = [chain] if isinstance(chain, str) else list(chain or [])
            for t in group:
                _clear(t)
                for pid in chain:
                    if pid in PRESETS:
                        t.update(PRESETS[pid][1])
            continue
        main = next((t for t in group if t['name'] == role), group[0])
        if any(main.get(k) for k in FX_KEYS) or main.get('dly_time') or not fam or role not in fam:
            continue                                     # the genre already dressed it, or this family leaves it dry
        if rnd.random() > CHANCE or st.get('no_part_fx'):
            continue
        opts_ = fam[role]
        pid = rnd.choices([p for p, _ in opts_], [w for _, w in opts_])[0]
        for t in group:
            if t.get('double_of') and pid in ('ott', 'drive', 'crush'):
                continue                                 # a layer under the part doesn't need the same grit twice
            for k, v in PRESETS[pid][1].items():
                if k == 'dly' and (t.get('dly') or 0) >= v:
                    continue
                t[k] = v
    for role in MELODIC:
        main = tracks.get(role) or next((t for t in tracks.values() if t.get('layer') == role), None)
        if main:
            picked[role] = describe(main)
    return picked


def menu():
    """[(id, label)] for the Parts panel."""
    return [(k, v[0]) for k, v in PRESETS.items()]
