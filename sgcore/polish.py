"""(2.16) Arranger's polish - small passes that make generated parts behave like written ones.

- recover_leaps: after a big leap the melody turns back by step (the oldest rule of good tunes); without it,
  generated lines can zig-zag or keep climbing.
- bass_approaches: in played-bass genres the bass walks into chord changes - the last 8th before a new chord
  becomes a scale step (or a chromatic half step) leading to the new root.
- callbacks: the song remembers itself - the bridge opens by quoting the verse tune a fourth higher, and the outro
  brings back the intro's figure.
- seat_orchestra: orchestral parts get their concert-hall seats (violins left, celli / basses right, horns behind
  left, trumpets and trombones behind right, harp far left, percussion at the back) instead of all in the middle.
"""
import random

from .develop import step

PLAYED_BASS = ('Classic',)


def _skip(st, evs, track):
    from .theory import MAQAM_QUARTER   # noqa: F401  (imported for the scale check below)
    return st.get('composer') or any(e.track == track and e.bend for e in evs)


def recover_leaps(evs, st, opts, key, track='lead'):
    from .theory import MAQAM_QUARTER
    if (getattr(opts, 'development', 'auto') or 'auto') == 'off' or key.scale_name in MAQAM_QUARTER or _skip(st, evs, track):
        return 0
    if st.get('melody_lang') in ('bebop', 'chromatic', 'serial'):
        return 0
    notes = sorted((e for e in evs if e.track == track and e.midi is not None), key=lambda e: e.beat)
    n = 0
    for a, b, c in zip(notes, notes[1:], notes[2:]):
        if b.beat - a.beat > 2 or c.beat - b.beat > 1.5:
            continue                                      # only inside a phrase
        leap = b.midi - a.midi
        if abs(leap) < 5:
            continue
        nxt = c.midi - b.midi
        if nxt * leap > 0 or abs(nxt) > 4:                # still going the same way, or leaping again: turn back by step
            c.midi = step(key, b.midi, -1 if leap > 0 else 1)
            n += 1
    return n


def bass_approaches(evs, sections, st, opts, key):
    if st.get('category') not in PLAYED_BASS or st.get('composer') or st.get('riff_locked') or st.get('bass_mode') == '808':
        return 0
    if (getattr(opts, 'development', 'auto') or 'auto') == 'off':
        return 0
    rnd = random.Random(f'{opts.seed}-approach-{st.get("name")}')
    bass = sorted((e for e in evs if e.track == 'bass' and e.midi is not None), key=lambda e: e.beat)
    firsts = {}
    for e in bass:
        b = int(e.beat // 4)
        if e.beat - b * 4 < 0.05 and b not in firsts:
            firsts[b] = e
    n = 0
    for i, e in enumerate(bass[:-1]):
        b = int(e.beat // 4)
        nxt = firsts.get(b + 1)
        if nxt is None or nxt.midi == e.midi or not (b * 4 + 3.4 <= e.beat < b * 4 + 3.9) or e.dur > 0.6:
            continue                                      # a short note on the last 8th, before a new root
        if rnd.random() > 0.25:
            continue
        below = rnd.random() < 0.6
        e.midi = step(key, nxt.midi, -1 if below else 1) if rnd.random() < 0.7 else nxt.midi + (-1 if below else 1)
        n += 1
    return n


def callbacks(evs, sections, st, opts, key):
    if st.get('composer') or st.get('exact_form') or (getattr(opts, 'development', 'auto') or 'auto') == 'off':
        return []
    rnd = random.Random(f'{opts.seed}-callback-{st.get("name")}')
    done = []
    verse = next((s for s in sections if s['name'] == 'verse' and 'lead' in s['layers']), None)
    for s in sections:
        if s['name'] == 'bridge' and verse and 'lead' in s['layers'] and rnd.random() < 0.45:
            src = [e for e in evs if e.track == 'lead' and verse['bar'] * 4 <= e.beat < (verse['bar'] + 2) * 4 and e.midi is not None]
            if src:
                b0 = s['bar'] * 4
                evs[:] = [e for e in evs if not (e.track == 'lead' and b0 <= e.beat < b0 + 8)]
                for e in src:
                    evs.append(e.copy(beat=b0 + (e.beat - verse['bar'] * 4), midi=step(key, e.midi, 3)))
                done.append('bridge quotes the verse')
    intro = next((s for s in sections if s['name'] == 'intro'), None)
    outro = next((s for s in reversed(sections) if s['name'] in ('outro', 'coda')), None)
    if intro and outro and rnd.random() < 0.5:
        for tr in ('arp', 'lead'):
            if tr not in intro['layers'] or tr not in outro['layers']:
                continue
            src = [e for e in evs if e.track == tr and intro['bar'] * 4 <= e.beat < (intro['bar'] + min(4, intro['bars'])) * 4]
            if not src:
                continue
            b0, b1 = outro['bar'] * 4, (outro['bar'] + min(4, outro['bars'], intro['bars'])) * 4
            evs[:] = [e for e in evs if not (e.track == tr and b0 <= e.beat < b1)]
            for e in src:
                t = b0 + (e.beat - intro['bar'] * 4)
                if t < b1:
                    evs.append(e.copy(beat=t))
            done.append(f'outro brings back the intro {tr}')
            break
    return done


# concert seating: (pan, extra reverb) by instrument
SEATS = (('contrabass', 0.45, 0.05), ('bass_cb', 0.45, 0.05), ('cello', 0.32, 0.0), ('viola', 0.12, 0.0),
         ('violin', -0.32, 0.0), ('strings', -0.12, 0.0), ('tremolo', -0.12, 0.0), ('spiccato', -0.18, 0.0),
         ('pizz', -0.22, 0.0), ('harp', -0.45, 0.02), ('celesta', 0.35, 0.03), ('glock', 0.3, 0.05),
         ('horn', -0.25, 0.08), ('trumpet', 0.18, 0.08), ('trombone', 0.3, 0.08), ('tuba', 0.38, 0.08),
         ('brass', 0.15, 0.08), ('flute', -0.1, 0.04), ('piccolo', -0.12, 0.04), ('oboe', 0.06, 0.04),
         ('clarinet', -0.05, 0.04), ('bassoon', 0.12, 0.04), ('timp', 0.12, 0.1), ('snare', 0.05, 0.1),
         ('tubular', 0.25, 0.1), ('choir', 0.0, 0.05), ('kidchoir', -0.05, 0.05))


def seat_orchestra(st):
    if st.get('category') != 'Orchestral' or st.get('no_seating'):
        return 0
    n = 0
    for t in st['tracks']:
        if abs(t.get('pan') or 0) > 1e-6:                 # the genre placed it itself
            continue
        inst = str(t.get('inst', '')).split(':', 1)[-1]
        for k, pan, rev in SEATS:
            if k in inst or k == t['name']:
                t['pan'] = pan
                t['rev'] = min(0.8, (t.get('rev') or 0) + rev)   # the back rows sound a little further away
                n += 1
                break
    return n


def song_score(song):
    """(2.16) How promising a composed (not yet rendered) song is, 0-100: the genre check, plus how singable and shapely
    its tune is - a clear range (not too narrow, not too wide), mostly steps with some leaps, a single high point,
    repeated rhythm cells - and whether its sections differ in energy. Used to keep the best of a batch."""
    from . import fitness
    fit = fitness.genre_fit(song)
    g = fit['score'] if fit else 70
    lead = sorted((e for e in song['events'] if e.track == 'lead' and e.midi is not None), key=lambda e: e.beat)
    m = 60.0
    if len(lead) > 8:
        ps = [e.midi for e in lead]
        rng = max(ps) - min(ps)
        m = 100 - min(40, abs(rng - 12) * 4)                  # about an octave and a bit is the singable sweet spot
        iv = [abs(b - a) for a, b in zip(ps, ps[1:])]
        steps = sum(1 for x in iv if 0 < x <= 2) / len(iv)
        leaps = sum(1 for x in iv if x >= 5) / len(iv)
        same = sum(1 for x in iv if x == 0) / len(iv)
        m -= abs(steps - 0.55) * 60 + max(0, leaps - 0.2) * 80 + max(0, same - 0.35) * 60
        top = max(ps)
        m -= max(0, sum(1 for p in ps if p == top) - 3) * 3      # the peak note shouldn't be hammered
        rh = [round((e.beat % 4) * 4) for e in lead]
        cells = {}
        for i in range(0, len(rh) - 3, 4):
            k = tuple(rh[i:i + 4])
            cells[k] = cells.get(k, 0) + 1
        m += min(10, max(cells.values() or [0]) * 2)          # a rhythm that comes back is a hook
    secs = song.get('sections') or []
    lv = [s['opts'].get('level', 0.6) for s in secs if 'level' in s['opts']]
    contrast = (max(lv) - min(lv)) * 100 if len(lv) > 1 else 30
    c = min(100, 40 + contrast * 1.5)
    return round(0.5 * g + 0.4 * max(0, min(100, m)) + 0.1 * c)
