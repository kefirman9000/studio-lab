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
    if st.get('category') != 'Electronic' or getattr(opts, 'evolve', 'auto') == 'off' or st.get('gentle'):
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
    if getattr(opts, 'call_response', 'auto') == 'off' or st.get('composer') or 'lead' not in tracks or st.get('gentle'):
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


# ----------------------------------------------------------------------------- (1.90) section dynamics
LIFT_SECTIONS = {'drop', 'chorus', 'climax', 'hook', 'B', 'loop'}


def section_dynamics(evs, sections, st, opts, tracks):
    """Real dynamics between sections (electronic genres): the doubled layers (the second lead / chord / bass sound)
    are saved for the drops, so a drop adds weight instead of only getting louder; a breakdown starts bare (one sound
    per part) and its layers come back for its second half; and each drop hits harder on its first downbeat.
    Returns the number of notes moved / removed (0 when off)."""
    if st.get('category') != 'Electronic' or st.get('composer') or getattr(opts, 'section_dynamics', 'auto') == 'off':
        return 0
    layers = {n for n, t in tracks.items() if t.get('double_of')}
    hit = {n for n, t in tracks.items() if t.get('layer') in ('kick', 'bass', 'lead') and not t.get('double_of')}
    if not any(s['opts'].get('drop') or s['name'] in LIFT_SECTIONS for s in sections):
        return 0
    drop_out = []
    n = 0
    for sec in sections:
        b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
        big = sec['opts'].get('drop') or sec['name'] in LIFT_SECTIONS
        if big:
            first = [e for e in evs if e.track in hit and b0 <= e.beat < b0 + 0.05]
            for e in first:                                   # the first downbeat of the drop lands harder
                e.vel = min(1.0, e.vel * 1.15)
            n += len(first)
        elif sec['opts'].get('build'):
            continue                                          # builds keep what they have: they are rising already
        elif sec['name'] in ('break', 'breakdown', 'C', 'calm', 'bridge'):
            drop_out.append((b0, b0 + 4 * max(2, sec['bars'] // 2)))   # bare first half, layers back for the lift
        elif sec['name'] in ('intro', 'verse', 'A', 'rise'):
            drop_out.append((b0, b1))
    if layers and drop_out:
        keep = [e for e in evs if not (e.track in layers and any(a <= e.beat < b for a, b in drop_out))]
        n += len(evs) - len(keep)
        evs[:] = keep
    return n


# ----------------------------------------------------------------------------- (1.90) genre fills / transitions
REWIND_GENRES = {'dnb', 'jungle', 'jump_up', 'neurofunk', 'neurofunk_lite', 'anthem_dnb', 'liquid_dancefloor',
                 'ukgarage', 'speed_garage', 'grime', 'bassline_140', 'uk_hardcore', 'idm_jungle_theme'}
SHOUT_GENRES = {'dubstep': ('oi', 'yeah'), 'brostep': ('oi', 'yeah', 'go'), 'riddim': ('oi', 'go'),
                'midtempo_bass': ('hey', 'oi'), 'dark_dubstep_classic': ('oi', 'whoa'), 'bass_house': ('hey', 'go'),
                'trap_metal': ('yeah', 'go'), 'hard_trap': ('yeah', 'hey'), 'hardstyle': ('hey', 'yeah')}
TRANCE_ROLL_GENRES = {'trance', 'uplifting_trance', 'progressive_trance', 'club_trance_2000s', 'progressive_trance_2010s',
                      'electro_prog_trance', 'trance_pop_90s', 'hard_trance', 'vocal_trance_remix', 'classic_vocal_trance',
                      'goa_trance', 'festival_psy'}


def genre_fills(evs, fx, sections, st, opts, tracks, seed=0):
    """Transitions the way each scene does them:
    - drum & bass / jungle / garage / grime: the REWIND - a few bars into the second drop the DJ pulls it back (the
      record spins backwards) and the drop starts again from the top;
    - dubstep / brostep / riddim (and a few loud cousins): the DROP STOP - everything cuts out for a beat before the
      drop, and a hype-man shout fills the hole;
    - trance: the SNARE ROLL climbs in pitch through the build while the pads' filter opens (on top of the high-pass).
    Returns a list of what was added."""
    import random as _r
    if getattr(opts, 'genre_fills', 'auto') == 'off' or st.get('composer') or getattr(opts, 'transition_fx', 'auto') == 'off':
        return []
    g = st.get('name') or opts.style
    rnd = _r.Random(f'{seed}-{g}-fills')
    done = []
    for i, sec in enumerate(sections):                               # a section written to end in a dead stop
        if sec['opts'].get('stop_end'):
            e1 = (sec['bar'] + sec['bars']) * 4
            fx.append(('tapestop', e1 - 2, 1.5))
            fx.append(('gap', e1 - 0.5, 0.5))
            done.append(('tape stop', i))
    drops = [i for i, s in enumerate(sections) if s['opts'].get('drop')]
    snares = [s for s in st.get('snare_tracks', []) if s in tracks]
    if g in REWIND_GENRES and len(drops) >= 2:
        sec = sections[drops[1]]
        d0 = sec['bar'] * 4
        if sec['bars'] >= 16:
            span = 16 if sec['bars'] >= 24 else 8                    # rewind after 4 (or 2) bars of the drop
            r = d0 + span
            fx.append(('rewind', r - 2, 2))
            fx.append(('gap', r - 0.25, 0.25))
            head = [e for e in evs if d0 <= e.beat < r - 2]
            evs[:] = [e for e in evs if not (r - 2 <= e.beat < r + span)]
            evs += [e.copy(beat=e.beat + span) for e in head]           # ... and it starts again from the top
            fx[:] = [f for f in fx if not (r - 2 <= f[1] < r + span and f[0] != 'rewind' and f[0] != 'gap')]
            fx += [(k, b + span, d) for k, b, d in list(fx) if d0 <= b < r - 2 and k in ('crash', 'impact')]
            if rnd.random() < 0.5:
                fx.append(('shout:' + rnd.choice(('oi', 'hey')), r - 0.75, 0))
            done.append(('rewind', drops[1]))
    if g in SHOUT_GENRES:
        words = SHOUT_GENRES[g]
        for k, i in enumerate(drops):
            if k > 0 and rnd.random() < 0.4:
                continue
            d0 = sections[i]['bar'] * 4
            stop = 1.0 if rnd.random() < 0.7 else 1.5
            fx[:] = [f for f in fx if not (f[0] == 'gap' and d0 - 2 <= f[1] < d0)]
            fx.append(('gap', d0 - stop, stop))
            fx.append(('shout:' + words[k % len(words)], d0 - stop + 0.02, 0))
            done.append(('drop stop', i))
    if g in TRANCE_ROLL_GENRES:
        for i, sec in enumerate(sections):
            if not sec['opts'].get('build'):
                continue
            b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
            roll = [e for e in evs if e.track in snares and b0 <= e.beat < b1]
            if 0 < len(roll) < 8 and snares and not getattr(opts, 'build_style', None):   # a few hits, no roll: 16ths in the last 2 bars
                st_ = max(b0, b1 - 8)
                roll = [type(evs[0])(snares[0], st_ + k / 4, 0.2, None, 0.35 + 0.6 * k / 32) for k in range(30)] if evs else []
                evs += roll
            for e in roll:                                            # the roll climbs a fifth (an octave on the last one)
                top = 12 if i == max((j for j, s in enumerate(sections) if s['opts'].get('build')), default=-1) else 7
                if not e.mod:
                    e.mod = f'pt:{round(top * ((e.beat - b0) / max(1, b1 - b0)) ** 1.5, 2)}'
            if not any(f[0] == 'lpsweep' and b0 <= f[1] < b1 for f in fx):
                fx.append(('lpsweep', b0, b1 - b0))
            done.append(('snare roll rise', i))
    return done


# ----------------------------------------------------------------------------- (1.91) structure moves
LAYER_ORDER = ('kick', 'top', 'bass', 'snare', 'pad', 'chords', 'arp', 'lead')


def _role(t):
    return t.get('layer')


def structure_moves(evs, sections, st, opts, tracks, bass_pool, fx=None):
    """Section options from the club layouts:
    - layer_in: the parts come in one after another, on 4-bar lines (kick, hats, bass, snare, pads, arp, lead) -
      the way a club track's intro is built for a DJ to mix in;
    - layer_out: the reverse at the end - the melodic parts leave first, the kick and hats last;
    - switch: a switch-up drop (VIP) - the bass line moves to a different bass sound from the genre.
    Returns the switch-up bass track to add, or None."""
    if st.get('composer'):
        return None
    for sec in sections:
        o = sec['opts']
        if not (o.get('layer_in') or o.get('layer_out')):
            continue
        b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
        inside = [e for e in evs if b0 <= e.beat < b1]
        roles = [r for r in LAYER_ORDER if any(_role(tracks.get(e.track, {})) == r for e in inside)]
        if len(roles) < 2:
            continue
        if o.get('layer_out'):
            roles = roles[::-1]                                # first to leave: the last to have come in
        bars = sec['bars']
        at = {r: int(round(i * bars / len(roles) / 4)) * 4 for i, r in enumerate(roles)}
        drop_ids = set()
        n_ = len(roles)
        for e in inside:
            r = _role(tracks.get(e.track, {}))
            if r not in at:
                continue
            i = roles.index(r)
            if o.get('layer_in') and e.beat < b0 + 4 * at[r]:          # not in yet
                drop_ids.add(id(e))
            gone = (n_ - 1 - i) * bars // n_ // 4 * 4                   # layer_out: roles[0] leaves first, the last stays
            if o.get('layer_out') and gone and e.beat >= b1 - 4 * gone:
                drop_ids.add(id(e))
        evs[:] = [e for e in evs if id(e) not in drop_ids]
    import random as _rb
    rb = _rb.Random(f'{opts.seed}-{st.get("name")}-breaths')
    for sec in sections:                                       # breaths: long drops take a breath at phrase ends
        if not sec['opts'].get('breaths'):
            continue
        b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
        for ph in range(int(b0) + 64, int(b1) - 1, 64):         # every 16 bars, not at the end of the drop
            big = (ph - b0) % 128 == 0
            if not big and rb.random() < 0.55:
                continue
            kind = rb.choice(['beats', 'bar', 'stop'] if big else ['beats', 'beats', 'stop'])
            cut = 2.0 if kind == 'beats' else (4.0 if kind == 'bar' else 1.0)
            low = {'kick', 'bass'} | ({'snare'} if kind != 'beats' else set())
            evs[:] = [e for e in evs if not (ph - cut <= e.beat < ph and (tracks.get(e.track, {}).get('layer') in low))]
            for e in evs:                                       # notes ringing into the breath are cut at its start
                if tracks.get(e.track, {}).get('layer') in ('bass',) and e.beat < ph - cut < e.beat + e.dur:
                    e.dur = max(0.1, ph - cut - e.beat)
            if fx is not None:
                if kind == 'stop':
                    fx.append(('gap', ph - cut, cut))
                fx.append(('crash', ph, 0))
    sw = [s for s in sections if s['opts'].get('switch')]
    bass = tracks.get('bass')
    if not sw or not bass or bass.get('user_pick'):
        return None
    import random as _r
    rnd = _r.Random(f'{opts.seed}-{st.get("name")}-vip')
    cands = [b for b in bass_pool if b != bass.get('inst') and not str(b).startswith('808')]
    if not cands:
        return None
    t = dict(bass)
    t.update(name='bass_vip', inst=rnd.choice(cands), p={}, pooled=True)
    t.pop('user_pick', None)
    t.pop('double_of', None)
    moved = 0
    for s in sw:
        b0, b1 = s['bar'] * 4, (s['bar'] + s['bars']) * 4
        for e in evs:
            if e.track == 'bass' and b0 <= e.beat < b1:
                e.track = 'bass_vip'
                moved += 1
    st['switch_bass'] = t['inst'] if moved else None
    return t if moved else None


# ----------------------------------------------------------------------------- (1.91) background arpeggios
def extra_arps(evs, sections, st, opts, tracks):
    """More arpeggio layers behind the main parts (styles with 'arps2'): each walks the current chord's tones at its
    own rate, direction and register - e.g. a faint 8th-note line around C5 and a glittery one in octave 6 that starts
    each phrase brightly and fades into the reverb. They play where the section has its arp. Returns the note count."""
    specs = st.get('arps2') or []
    if not specs or st.get('composer'):
        return 0
    import random as _r
    chords = {}
    for e in evs:
        if e.track == 'chords' and e.midi is not None:
            chords.setdefault(round(e.beat, 3), []).append(e.midi)
    starts = sorted(chords)
    if not starts:
        return 0
    made = 0
    for spec in specs:
        name = spec['track']
        if name not in tracks or tracks[name].get('off'):
            continue
        rnd = _r.Random(f'{opts.seed}-{name}-arps2')
        step, center, mode = float(spec.get('step', 0.5)), int(spec.get('center', 76)), spec.get('mode', 'down')
        for sec in sections:
            if 'arp' not in (sec.get('layers') or []) or sec['opts'].get('build'):
                continue
            b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
            k = 0
            beat = float(b0)
            while beat < b1 - 1e-6:
                c0 = max([s for s in starts if s <= beat + 1e-6] or [starts[0]])
                pcs = sorted({m % 12 for m in chords[c0]})
                sp = int(spec.get('span', 7))                         # how far from its centre it may reach
                notes = sorted(n for n in range(center - sp, center + sp + 1) if n % 12 in pcs)
                if notes and rnd.random() < spec.get('prob', 0.9):
                    if mode == 'down':
                        m = notes[::-1][k % len(notes)]
                    elif mode == 'up':
                        m = notes[k % len(notes)]
                    elif mode == 'updown':
                        cyc = notes + notes[-2:0:-1]
                        m = cyc[k % len(cyc)]
                    else:
                        m = rnd.choice(notes)
                    ph = ((beat - b0) % (4 * spec.get('phrase', 8))) / (4 * spec.get('phrase', 8))
                    vel = spec.get('vel', 0.6) * (1 - spec.get('fade', 0.0) * ph)        # bright at the phrase start
                    evs.append(type(evs[0])(name, beat, step * 0.9, m, vel))
                    made += 1
                k += 1
                beat += step
    return made


def bass_stutter(evs, st):
    """(1.92.2) Styles with 'bass_stutter': the bass comes in once every two bars on the chord root - struck three
    times in triplets, then held for about two and a half beats, then space (the way the bass enters in a chill synth
    piece, about every six seconds). Returns the number of entrances."""
    if not st.get('bass_stutter'):
        return 0
    bass = sorted((e for e in evs if e.track == 'bass' and e.midi is not None), key=lambda e: e.beat)
    keep, drop = [], set()
    for e in bass:                                       # merge a repeated root into one long note
        if keep and keep[-1].midi == e.midi and abs(keep[-1].beat + keep[-1].dur - e.beat) < 0.3:
            keep[-1].dur = e.beat + e.dur - keep[-1].beat
            drop.add(id(e))
        else:
            keep.append(e)
    for e in keep:                                       # one entrance every two bars, held ~2.5 beats, then space
        if int(e.beat // 4) % 2:
            drop.add(id(e))
        else:
            e.dur = min(e.dur, 3.5)
    evs[:] = [e for e in evs if id(e) not in drop]
    keep = [e for e in keep if id(e) not in drop]
    out = []
    for e in keep:
        if e.dur >= 2.0:
            for k in range(3):
                out.append(e.copy(beat=e.beat + k / 3, dur=0.28, vel=e.vel * (1.0 - 0.08 * k)))
            e.beat, e.dur = e.beat + 1.0, e.dur - 1.0
    evs.extend(out)
    return len(out) // 3


# ----------------------------------------------------------------------------- (1.92.3) per-song variations
def song_variations(st, opts):
    """Styles with 'song_variations' pick, per song (seeded), one option from each of their lists: a sound palette,
    a pulse figure, the sparkle and middle arpeggios, a layout, a tempo range, a harmony (mode + chord loops), a bass
    style, a lead rhythm - so songs in one genre keep its character but never come out the same. Your own sound picks
    still win (they are applied later). Returns what was picked."""
    sv = st.get('song_variations')
    if not sv or st.get('composer'):
        return None
    import random as _r
    rnd = _r.Random(f'{opts.seed}-{st.get("name") or opts.style}-songvar')
    picked = {}
    for key in sorted(sv):
        options = sv[key]
        i = rnd.randrange(len(options))
        ch = options[i]
        picked[key] = ch.get('name', i) if isinstance(ch, dict) else i
        if key == 'palette':
            for t in st['tracks']:
                if t['name'] in ch and t['name'] != 'name':
                    # (2.2.8) a part every palette gives the same sound isn't part of the palette choice: the song's
                    # pick from the genre's sound pool stands (else it was always that one sound)
                    if t.get('pooled') and len({o.get(t['name']) for o in options if isinstance(o, dict)}) == 1:
                        continue
                    t['inst'] = ch[t['name']]
                    t.pop('fallback', None)
        elif key in ('pulse', 'mid', 'sparkle'):
            specs = [s for s in (st.get('arps2') or []) if s['track'] != {'pulse': 'arp', 'mid': 'arp_mid', 'sparkle': 'arp_hi'}[key]]
            if ch.get('track'):
                specs.append({k: v for k, v in ch.items() if k != 'name'})
            st['arps2'] = specs
        elif key == 'form':
            if (getattr(opts, 'structure', 'auto') or 'auto') == 'auto':
                st['form'] = ch['form']
        else:                                            # bpm / harmony / bass / lead: values merged into the style
            st.update({k: v for k, v in ch.items() if k != 'name'})
    st['song_var'] = picked
    return picked


# ----------------------------------------------------------------------------- (1.93) polymeter sequences
def polymeter(evs, sections, st, opts, tracks):
    """Techno's polymeter trick (styles with 'polymeter': the chance per song): the sequence (arp part) becomes a
    pattern 3, 5, 6 or 7 sixteenths long that keeps looping across the bar lines, so against the 4/4 kick it lands
    somewhere new every bar and only lines up again after several bars. Its notes are the chord tones the part was
    already playing (so it stays in key). Returns the loop length, or 0."""
    chance = float(st.get('polymeter') or 0)
    if not chance or st.get('composer') or getattr(opts, 'polymeter', 'auto') == 'off' or 'arp' not in tracks:
        return 0
    import random as _r
    rnd = _r.Random(f'{opts.seed}-{st.get("name")}-polymeter')
    if getattr(opts, 'polymeter', 'auto') != 'on' and rnd.random() > chance:
        return 0
    L = rnd.choice([3, 5, 5, 6, 7])
    hits = [0] + sorted(rnd.sample(range(1, L), max(1, (L + 1) // 2 - 1)))
    order = [rnd.randrange(4) for _ in range(L)]
    made = 0
    for sec in sections:
        if 'arp' not in (sec.get('layers') or []) or sec['opts'].get('build'):
            continue
        b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
        old = [e for e in evs if e.track == 'arp' and b0 <= e.beat < b1 and e.midi is not None]
        if not old:
            continue
        by_bar = {}
        for e in old:
            by_bar.setdefault(int(e.beat // 4), set()).add(e.midi)
        ids = {id(e) for e in old}
        evs[:] = [e for e in evs if id(e) not in ids]
        tones = sorted(by_bar.get(int(b0 // 4)) or next(iter(by_bar.values())))
        proto = old[0]
        i = 0
        step = int(b0 * 4)
        while step < int(b1 * 4):
            bar = step // 16
            if bar in by_bar:
                tones = sorted(by_bar[bar])
            k = i % L
            if k in hits and tones:
                m = tones[order[k] % len(tones)]
                evs.append(proto.copy(beat=step / 4, dur=0.22, midi=m, vel=0.95 if k == 0 else 0.68, glide=None))
                made += 1
            i += 1
            step += 1
    st['polymeter_len'] = L if made else 0
    return st['polymeter_len']


# ----------------------------------------------------------------------------- (1.94) phrase evolution (club records)
def phrase_evolution(evs, sections, st, opts, tracks, club=(), trance=()):
    """How a club record keeps moving inside a long section, on the 8-bar grid:
    - a groove (intro / verse, 24 bars or more) builds: two secondary parts (an arp, a pad, a percussion or a layer)
      are held back for its first 8 bars and one for the next 8;
    - a long drop (32 bars or more) hits full, and one extra part (a ride, a layer, the counter line) comes in halfway
      as a lift;
    - in house and techno a very long drop (48 bars or more) also lets the hook step out for 8 bars in the middle
      while the groove carries on (it comes back for the last part).
    Returns the number of notes held back."""
    g = st.get('name') or opts.style
    if (g not in club and not st.get('phrase_evolve')) or st.get('composer') or getattr(opts, 'phrase_evolution', 'auto') == 'off':
        return 0                                       # (1.96: other styles opt in with 'phrase_evolve')
    import random as _r
    rnd = _r.Random(f'{opts.seed}-{g}-phrases')
    kick = st.get('kick_track', 'kick')
    drop_ids = set()

    def secondary(b0, b1):
        here = {e.track for e in evs if b0 <= e.beat < b1}
        out = []
        for n in sorted(here):
            t = tracks.get(n, {})
            if n == kick or t.get('layer') in ('kick', 'snare', 'bass'):
                continue
            if t.get('layer') in ('arp', 'pad', 'top') or t.get('double_of') or t.get('counter') or n in ('counter', 'answer'):
                if n in ('chat',):                          # the main closed hat keeps the groove going
                    continue
                out.append(n)
        rnd.shuffle(out)
        return out

    def hold(names, a, b):
        for e in evs:
            if e.track in names and a <= e.beat < b:
                drop_ids.add(id(e))
    for sec in sections:
        o = sec['opts']
        if o.get('build') or o.get('layer_in') or o.get('layer_out'):
            continue
        b0, bars = sec['bar'] * 4, sec['bars']
        b1 = b0 + bars * 4
        big = o.get('drop') or sec['name'] in ('drop', 'chorus', 'climax', 'B')
        sec_ = secondary(b0, b1)
        if not big and sec['name'] in ('intro', 'verse', 'A') and bars >= 24 and len(sec_) >= 2:
            hold(set(sec_[:2]), b0, b0 + 32)              # first 8 bars: without two of them
            hold({sec_[0]}, b0 + 32, b0 + 64)              # next 8: one comes in, then the last
        elif big and bars >= 32 and sec_:
            hold({sec_[0]}, b0, b0 + bars * 2)             # the lift: an extra part comes in halfway
            if bars >= 48 and g not in trance:
                mid = b0 + (bars // 16) * 32               # an 8-bar breather for the hook, in the middle
                hold({n for n, t in tracks.items() if t.get('layer') == 'lead'}, mid, mid + 32)
    evs[:] = [e for e in evs if id(e) not in drop_ids]
    return len(drop_ids)


def drop_space(evs, sections, st, opts, tracks, genres):
    """(1.95.1) A dubstep drop belongs to the bass: the held pad steps out and the chords thin to one short accent hit
    every two bars, so nothing drones in the mid-range under the wobble (melodic dubstep / chillstep keep their pads -
    lush is their style). Returns the number of notes taken out."""
    g = st.get('name') or opts.style
    if g not in genres or st.get('composer') or getattr(opts, 'drop_space', 'auto') == 'off':
        return 0
    kill = set()
    for sec in sections:
        if not (sec['opts'].get('drop') or sec['name'] in ('drop',)):
            continue
        b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
        for e in evs:
            if not (b0 <= e.beat < b1) or e.midi is None:
                continue
            t = tracks.get(e.track, {})
            role = t.get('layer')
            if role == 'pad':
                kill.add(id(e))
            elif role == 'chords':
                rel = e.beat - b0
                if not (rel % 8 < 0.01):                   # one accent at the top of every second bar
                    kill.add(id(e))
                else:
                    e.dur = min(e.dur, 0.5)
    evs[:] = [e for e in evs if id(e) not in kill]
    return len(kill)
