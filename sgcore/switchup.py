"""Switch-up bass: ONE rhythm for the whole song, everything else switches.

What the reference does (measured): 131.75 BPM; a broken UK-bass kick (1, the 'a' of 1, the 'e' of 2, and a push
into the next bar) that never changes from the first bar to the last; a one-note sub on the root riding that kick
and carrying most of the record's energy; and every 8-16 bars a new scene - a different mid-bass voice, different
stabs / vocal chops / samples on top, different effects on them (crushed, phased, filtered down dark, wah'd) - with
short drop-outs where the sub stops dead and dark filtered stretches where the top end is gone.

So the drums and the sub are written once and kept. This pass turns each section into its own scene: the parts that
carry the colour (the mid-bass layer, the stab, the chop, the perc voice) are handed to a new sound and a new effect
for that section only, never the same pair twice in a row.
"""
import random

from .compose import TONE_DEFAULTS
from .instruments import INSTRUMENTS

SCENE_POOLS = {
    'bass_mid': ['reese', 'growl', 'fmbass', 'wobble', 'acid', 'sawbass', 'neuro', 'chopwob', 'techneuro', 'hoover_dark'],
    'chords': ['noisestab', 'ravestab', 'samplerstab', 'stab', 'mpckeys', 'darksample', 'ravestab2', 'organ', 'soulhorn'],
    'lead': ['vocalchop', 'formantchop', 'etherchop', 'housevox', 'pluckvox', 'scratch', 'formantlead', 'screech', 'vocalbounce'],
    'arp': ['fmperc', 'modseq', 'pluck', 'acid', 'technoseq'],
}
FX_MENU = [
    {}, {'crush': 0.6}, {'phaser': 0.7}, {'wah': 0.6}, {'flanger': 0.55}, {'drive': 0.7}, {'trem': 0.5},
    {'sweep': (300, 3500, 8)}, {'crush': 0.4, 'phaser': 0.5}, {'drive': 0.5, 'wah': 0.4}, {'ott': 0.6},
]
DARK = {'sweep': (180, 700, 16)}                         # the filtered-down stretches: the top end gone


def scene_switch(evs, tracks, sections, st, seed):
    """Give every section its own sounds and effects on the colour parts (see the module docstring)."""
    rnd = random.Random(f'{seed}-switchup')
    roles = [n for n in ('bass_mid', 'chords', 'lead', 'arp') if n in tracks]
    if not roles or not sections:
        return
    last = {}
    plan = []                                            # per section: {track: (inst, fx)}
    dark_left = 1 + (rnd.random() < 0.6)                 # one or two dark stretches per song
    for i, sec in enumerate(sections):
        if sec['opts'].get('fade') or sec['name'] == 'intro':
            plan.append({})
            continue
        dark = dark_left > 0 and i > 1 and rnd.random() < 0.3 and not sec['opts'].get('gap')
        if dark:
            dark_left -= 1
        scene = {}
        for name in roles:
            pool = [x for x in SCENE_POOLS.get(name, []) if x in INSTRUMENTS and x != last.get(name, (None,))[0]]
            if not pool:
                continue
            inst = rnd.choice(pool)
            fx = dict(DARK) if dark else dict(rnd.choice([f for f in FX_MENU if f != last.get(name, (None, None))[1]]))
            scene[name] = (inst, fx)
            last[name] = (inst, fx)
        plan.append(scene)
    made = {}
    for i, (sec, scene) in enumerate(zip(sections, plan)):
        b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
        for name, (inst, fx) in scene.items():
            base = tracks[name]
            tname = f'{name}_scene{i + 1}'
            if tname not in tracks:
                t = dict(base, name=tname, inst=inst, p=dict(TONE_DEFAULTS.get(inst, {})), switch_of=None, double_of=None,
                         keep_inst=True, scene=i + 1)
                for k in ('crush', 'phaser', 'wah', 'flanger', 'trem', 'sweep', 'ott'):
                    t.pop(k, None)
                t.update(fx)
                tracks[tname] = t
                st['tracks'].append(t)
                made[tname] = 0
            for e in evs:
                if e.track == name and b0 <= e.beat < b1:
                    e.track = tname
                    made[tname] += 1
    st['scenes'] = [{k: v[0] for k, v in sc.items()} for sc in plan]
    add_motion(tracks, sections, plan, rnd)


def add_motion(tracks, sections, plan, rnd):
    """(2.2.2) Bar-long moves (see alienfx.py): every section ends on a rise (into a drop) or a sink (into a break or
    a dark stretch) on all its colour parts together - sometimes the sub dives with them - and inside the section, every
    few bars, one or two parts do the scene's own alien move (frequency shift, ring mod, robot vowels, comb scream,
    zaps, stutters, crush dive) across a bar or two."""
    from .alienfx import KINDS_ALIEN
    for i, (sec, scene) in enumerate(zip(sections, plan)):
        if not scene:
            continue
        names = [f'{r}_scene{i + 1}' for r in scene if f'{r}_scene{i + 1}' in tracks]
        if not names:
            continue
        b0, nb = sec['bar'], sec['bars']
        nxt = sections[i + 1] if i + 1 < len(sections) else None
        into_low = nxt is None or nxt['opts'].get('gap') or nxt['opts'].get('fade') or any(
            (tracks.get(f'{r}_scene{i + 2}') or {}).get('sweep') == DARK['sweep'] for r in scene)
        last = (b0 + nb - 1) * 4.0, (b0 + nb) * 4.0
        if into_low:
            kind = rnd.choice(['tape_sink', 'filter_sink', 'filter_sink', 'crushdive'])
            up = -1
        else:
            kind = rnd.choice(['tape_rise', 'filter_rise', 'filter_rise', 'stutter'])
            up = 1
        for n in names:
            tracks[n].setdefault('motion', []).append((last[0], last[1], kind, up))
        if into_low and 'bass' in tracks and rnd.random() < 0.55:      # the sub dives into the drop-out
            tracks['bass'].setdefault('motion', []).append((last[0] + 2.0, last[1], 'tape_sink', -1))
        alien = rnd.sample(KINDS_ALIEN, 2)                # this scene's own two alien moves
        every = rnd.choice([2, 4, 4])
        for k in range(every - 1, nb - 1, every):
            if rnd.random() < 0.25:
                continue
            span = 2 if (k + 2 < nb - 1 and rnd.random() < 0.25) else 1
            who = rnd.sample(names, 1 + (len(names) > 2 and rnd.random() < 0.35))
            mv = alien[(k // every) % 2]
            for n in who:
                tracks[n].setdefault('motion', []).append(((b0 + k) * 4.0, (b0 + k + span) * 4.0, mv,
                                                           1 if rnd.random() < 0.5 else -1))
