"""1.85: song-writing passes that make a generated song sound less like a loop.

- score_hook: a melody check. Several hooks are written and the strongest is kept (a clear shape, steps with a few
  leaps, repetition with change, one high point late in the phrase, an ending that lands).
- evolve_drops: the second (and later) drops are not copies of the first: the lead may jump up an octave, the bass
  may push extra notes, the last bars may go half-time or stutter into the next section.
- call_response: in the hook sections a second sound answers the lead every other two bars.
- bar_variation: the 4th and 8th bar of a phrase change a little in the drums and the arp (a dropped hat, a ghost
  snare, an arp note moved), so the loops don't repeat bit for bit.
"""
import random

from .theory import Ev

HOOK_SECTIONS = ('drop', 'chorus', 'hook', 'main', 'theme', 'peak')


# ----------------------------------------------------------------------------- melody check
def score_hook(mel, key, phrase_beats=8):
    """0..1: how strong a hook is. mel: [(beat, dur, midi, vel)]."""
    notes = sorted((n for n in mel if n[2] is not None), key=lambda n: n[0])
    if len(notes) < 4:
        return 0.3
    pitches = [n[2] for n in notes]
    span = max(pitches) - min(pitches)
    s = 0.0
    s += 1.0 if 5 <= span <= 15 else (0.5 if 3 <= span <= 19 else 0.0)                 # a real range, not a drone
    iv = [b - a for a, b in zip(pitches, pitches[1:])]
    steps = sum(1 for d in iv if 0 < abs(d) <= 2) / len(iv)
    leaps = sum(1 for d in iv if abs(d) >= 5) / len(iv)
    same = sum(1 for d in iv if d == 0) / len(iv)
    s += 1.0 - min(1.0, abs(steps - 0.55) * 2.2)                                       # mostly steps ...
    s += 1.0 if 0.05 <= leaps <= 0.3 else 0.4                                          # ... and a few leaps
    s += 1.0 - min(1.0, max(0.0, same - 0.25) * 3)                                     # not one note hammered
    turns = sum(1 for a, b in zip(iv, iv[1:]) if a * b < 0) / max(1, len(iv) - 1)
    s += 1.0 - min(1.0, abs(turns - 0.4) * 2.5)                                        # a shape, not a zig-zag
    # repetition with change: the phrases resemble each other without being identical
    end = notes[-1][0] + notes[-1][1]
    k = max(1, int(round(end / phrase_beats)))
    phr = [[(round(n[0] % phrase_beats, 2), n[2]) for n in notes if i * phrase_beats <= n[0] < (i + 1) * phrase_beats]
           for i in range(k)]
    sims = []
    for a, b in zip(phr, phr[1:]):
        if a and b:
            sa, sb = set(x for x, _ in a), set(x for x, _ in b)
            sims.append(len(sa & sb) / max(1, len(sa | sb)))
    if sims:
        avg = sum(sims) / len(sims)
        s += 1.0 - min(1.0, abs(avg - 0.6) * 2)
    else:
        s += 0.5
    hi = max(range(len(pitches)), key=lambda i: (pitches[i], -i))                      # the high point comes later
    s += 1.0 if 0.35 <= hi / len(pitches) <= 0.9 else 0.4
    last = pitches[-1] % 12
    root = key.root % 12
    tones = {root, (root + key.deg(2, 0) - key.deg(0, 0)) % 12, (root + 7) % 12}
    s += 1.0 if last in tones else 0.3                                                  # an ending that lands
    durs = len(set(round(n[1], 2) for n in notes))
    s += 1.0 if durs >= 2 else 0.4                                                      # some rhythmic variety
    return s / 9.0


# ----------------------------------------------------------------------------- evolving second drops
def _in(e, a, b):
    return a <= e.beat < b


def evolve_drops(evs, sections, st, opts, tracks):
    """Second and later drops: one or two changes each, seeded by the song. Returns [(section index, change)]."""
    if st.get('category') != 'Electronic' or getattr(opts, 'evolve', 'auto') == 'off':
        return []
    drops = [i for i, x in enumerate(sections) if (x.get('opts') or {}).get('drop')]
    done = []
    rnd = random.Random(f'{opts.seed}-evolve-{st.get("name")}')
    for n, i in enumerate(drops[1:], start=1):
        x = sections[i]
        a, b = x['bar'] * 4, (x['bar'] + x['bars']) * 4
        if x['bars'] < 8:
            continue
        menu = ['lead_up', 'bass_push', 'stutter_end', 'halftime_end', 'arp_double']
        if n == len(drops) - 1:
            menu += ['lead_up', 'stutter_end']                      # the last drop: the biggest
        picks = rnd.sample(menu, 2 if n == len(drops) - 1 else 1)
        for ch in dict.fromkeys(picks):
            if ch == 'lead_up':
                lead = [e for e in evs if e.track == 'lead' and _in(e, a, b) and e.midi is not None]
                if lead and max(e.midi for e in lead) + 12 <= 96:
                    half = a + (b - a) / 2                          # the second half of the drop climbs an octave
                    for e in lead:
                        if e.beat >= half:
                            e.midi += 12
                    done.append((i, ch))
            elif ch == 'bass_push':
                bass = [e for e in evs if e.track == 'bass' and _in(e, a, b) and e.midi is not None]
                if bass and str((tracks.get('bass') or {}).get('inst', '')) not in ('808',) and len(bass) < (b - a) * 2:
                    have = {round(e.beat * 4) for e in bass}
                    add = []
                    for e in bass:                                  # an extra off-beat push after held notes
                        nb = e.beat + 0.5
                        if e.dur >= 0.9 and round(nb * 4) not in have and nb < b and rnd.random() < 0.6:
                            e.dur = min(e.dur, 0.45)
                            add.append(Ev('bass', nb, 0.4, e.midi + (12 if rnd.random() < 0.25 else 0), e.vel * 0.85))
                    evs.extend(add)
                    if add:
                        done.append((i, ch))
            elif ch == 'stutter_end':                               # the last bar: the lead re-triggers in 16ths
                c = b - 4
                lead = [e for e in evs if e.track == 'lead' and _in(e, c, b) and e.midi is not None]
                if lead:
                    m = lead[0].midi
                    for e in lead:
                        evs.remove(e)
                    for k in range(8):
                        evs.append(Ev('lead', c + 2 + k * 0.25, 0.2, m, 0.6 + 0.04 * k))
                    for e in lead:
                        if e.beat < c + 2:
                            evs.append(e)
                    done.append((i, ch))
            elif ch == 'halftime_end':                              # the last 2 bars: the snare only on beat 3
                c = b - 8
                sn = set(st.get('snare_tracks') or ['snare', 'clap'])
                gone = [e for e in evs if e.track in sn and _in(e, c, b) and abs(((e.beat - c) % 4) - 2) > 0.01]
                if gone:
                    for e in gone:
                        evs.remove(e)
                    done.append((i, ch))
            elif ch == 'arp_double':                                # the arp doubles the lead an octave up
                if 'arp' in tracks and any(e.track == 'arp' and _in(e, a, b) for e in evs):   # (only where the arp plays)
                    lead = [e for e in evs if e.track == 'lead' and _in(e, a, b) and e.midi is not None and e.midi + 12 <= 100]
                    if lead:
                        evs.extend(Ev('arp', e.beat, e.dur, e.midi + 12, e.vel * 0.7) for e in lead)
                        done.append((i, ch))
    return done


# ----------------------------------------------------------------------------- call and response
def call_response(evs, sections, st, opts, tracks, pool):
    """In the hook sections, every other two bars the lead rests and a second sound answers with the lead's phrase
    (an octave up or down, a little varied). Returns the answer track or None."""
    if getattr(opts, 'call_response', 'auto') == 'off' or st.get('composer') or 'lead' not in tracks:
        return None
    if st.get('category') not in ('Electronic',) and st.get('name') not in ('pop', 'kpop', 'teen_pop', 'synthpop', 'dance_pop'):
        return None
    rnd = random.Random(f'{opts.seed}-callresp-{st.get("name")}')
    forced = getattr(opts, 'call_response', 'auto') == 'on'
    if not forced and rnd.random() > 0.45:
        return None
    lead_inst = tracks['lead']['inst']
    cands = [x for x in (pool or []) if x != lead_inst]
    if not cands:
        return None
    inst = rnd.choice(cands)
    secs = [x for x in sections if x['name'] in HOOK_SECTIONS or (x.get('opts') or {}).get('drop')]
    moved = 0
    shift = rnd.choice([12, -12, 0])
    for x in secs:
        a, b = x['bar'] * 4, (x['bar'] + x['bars']) * 4
        for blk in range(int(a), int(b), 16):                   # bars 3-4 of every four answer bars 1-2
            ans = [e for e in evs if e.track == 'lead' and blk + 8 <= e.beat < blk + 16 and e.midi is not None]
            for e in ans:
                e.track = 'answer'
                m = e.midi + shift
                if not 48 <= m <= 96:
                    m = e.midi
                e.midi = m
                moved += 1
    if not moved:
        return None
    t = dict(tracks['lead'])
    t.update(name='answer', inst=inst, p={}, pan=rnd.choice([-0.25, 0.25]), db=(t.get('db') or -12) - 1, pooled=True)
    t.pop('user_pick', None)
    return t


# ----------------------------------------------------------------------------- 4th / 8th bar variation
def bar_variation(evs, sections, st, opts):
    """Small changes at the end of 4- and 8-bar phrases so loops don't repeat bit for bit. Returns the count."""
    if getattr(opts, 'bar_variation', 'auto') == 'off' or st.get('composer') or st.get('category') != 'Electronic':
        return 0
    ps = getattr(opts, 'part_seeds', None) or {}
    sd = {k: (ps.get(k) if ps.get(k) is not None else opts.seed * 1009 + n) for k, n in (('drums', 3), ('chords', 5))}
    rd = random.Random(f'{sd["drums"]}-barvar-{st.get("name")}')       # (each part follows its own seed: a locked
    ra = random.Random(f'{sd["chords"]}-barvar-arp-{st.get("name")}')  # part stays note-for-note)
    hats = {'chat', 'hat', 'hats', 'ch'}
    sn = set(st.get('snare_tracks') or ['snare'])
    n = 0
    by_bar = {}
    for e in evs:
        by_bar.setdefault(int(e.beat // 4), []).append(e)
    for x in sections:
        for k in range(x['bars']):
            bar = x['bar'] + k
            if (k + 1) % 4:
                continue
            big = (k + 1) % 8 == 0
            es = by_bar.get(bar, [])
            if not es:
                continue
            r = rd.random()
            if r < 0.35:                                        # drop a closed hat or two
                hh = [e for e in es if e.track in hats]
                for e in rd.sample(hh, min(len(hh), 2 if big else 1)):
                    evs.remove(e)
                    n += 1
            elif r < 0.6 and big:                               # a ghost snare before beat 4
                s = [e for e in es if e.track in sn]
                if s:
                    evs.append(Ev(s[0].track, bar * 4 + 2.75, 0.1, s[0].midi, 0.35))
                    n += 1
            if ra.random() < 0.3:                               # one arp note moves to its neighbour in the chord
                ar = [e for e in es if e.track == 'arp' and e.midi is not None]
                beats = {}
                for e in ar:
                    beats.setdefault(round(e.beat, 3), []).append(e)
                ar = [v[0] for v in beats.values() if len(v) == 1]      # (single notes only: doubled octaves stay)
                others = sorted({e.midi for e in ar})
                if len(others) >= 3:
                    e = ra.choice(ar)
                    i = others.index(e.midi)
                    e.midi = others[i + 1] if i + 1 < len(others) else others[i - 1]
                    n += 1
    return n
