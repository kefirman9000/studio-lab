"""Excerpts of a composed song: previews, section auditions and seamless loops."""
import math


def tempo_seconds(tempo_map, beat):
    """Seconds at `beat` for a tempo map [(beat, bpm), ...] whose tempo ramps linearly between points."""
    tm = tempo_map
    t = 0.0
    if beat <= tm[0][0]:
        return (beat - tm[0][0]) * 60.0 / tm[0][1]
    for (b0, v0), (b1, v1) in zip(tm, tm[1:]):
        e = min(beat, b1)
        if e > b0:
            ve = v0 + (v1 - v0) * (e - b0) / (b1 - b0) if b1 > b0 else v0
            t += 60.0 * (e - b0) / v0 if abs(ve - v0) < 1e-9 else 60.0 * (e - b0) / (ve - v0) * math.log(ve / v0)
        if beat <= b1:
            return t
    bl, vl = tm[-1]
    return t + 60.0 * (beat - bl) / vl


def section_window(song, index, preroll_bars=2, max_bars=20):
    """Excerpt containing one section (plus a short lead-in) - for auditioning edits."""
    sec = song['sections'][index]
    b0 = max(0, sec['bar'] - preroll_bars)
    b1 = min(song['total_bars'], sec['bar'] + min(sec['bars'], max_bars))
    return _window(song, b0, b1, fade=True)


def section_loop(song, index, max_bars=8):
    """A seamless loop of one section (up to 8 bars from its start, no lead-in, no fades) - to listen to a part
    over and over while choosing its sound."""
    sec = song['sections'][index]
    b0 = sec['bar']
    return _window(song, b0, min(song['total_bars'], b0 + min(sec['bars'], max_bars)), fade=False)


def loop_window(song, bars=8):
    """Clean loop from the start of the most energetic section, no fades (sample packs)."""
    best = max(song['sections'], key=lambda s: len(s['layers']) + (3 if s['opts'].get('drop') else 0))
    b0 = best['bar']
    return _window(song, b0, min(song['total_bars'], b0 + bars), fade=False, keep_fx=False)


def _window(song, b0, b1, fade=True, keep_fx=True):
    beat0, beat1 = b0 * 4, b1 * 4
    evs = [e.copy(beat=e.beat - beat0, dur=min(e.dur, beat1 - e.beat))
           for e in song['events'] if beat0 <= e.beat < beat1]
    fx = []
    for kind, b, d in song['fx']:
        if not keep_fx:
            continue
        if kind in ('crash', 'impact') and beat0 <= b < beat1:
            fx.append((kind, b - beat0, d))
        if kind in ('riser', 'hpsweep', 'gap', 'lpsweep') and b < beat1 and b + d > beat0:
            nb = max(b, beat0)
            fx.append((kind, nb - beat0, min(b + d, beat1) - nb))
        if kind in ('tapestop', 'djslow') and beat0 <= b and b + d <= beat1:      # whole slowdowns only
            fx.append((kind, b - beat0, d))
    if fade:
        fx.append(('fade', beat1 - beat0 - 4, 4))
    secs = []
    for s in song['sections']:
        s0, s1 = max(s['bar'], b0), min(s['bar'] + s['bars'], b1)
        if s1 > s0:
            secs.append(dict(s, bar=s0 - b0, bars=s1 - s0))
    pv = dict(song)
    pv.update(events=evs, fx=fx, sections=secs, total_bars=b1 - b0, preview_of=(b0, b1))
    if song.get('tempo_map'):                            # the excerpt keeps the tempo it has at that point of the story
        tm = song['tempo_map']
        bpm_at = lambda b: next((v0 + (v1 - v0) * (b - x0) / (x1 - x0) for (x0, v0), (x1, v1) in zip(tm, tm[1:])
                                 if x0 <= b <= x1 and x1 > x0), tm[-1][1] if b > tm[-1][0] else tm[0][1])
        pts = [(0.0, bpm_at(beat0))] + [(b - beat0, v) for b, v in tm if beat0 < b < beat1] + [(beat1 - beat0, bpm_at(beat1))]
        pv['tempo_map'] = pts
    if song.get('expr'):
        pv['expr'] = {k: [(b - beat0, v) for b, v in c if beat0 <= b < beat1] or [(0.0, c[0][1])] for k, c in song['expr'].items() if c}
    return pv


def preview_window(song, target_sec=26.0):
    """Cut a short excerpt around the most energetic section (for quick auditioning)."""
    spb = 60.0 / song['bpm']
    bar_sec = 4 * spb
    nbars = int(max(8, min(16, round(target_sec / bar_sec / 4) * 4)))
    best = None
    for s in song['sections']:
        score = len(s['layers']) + (3 if s['opts'].get('drop') else 0) + (1 if s['name'] in ('chorus', 'hook', 'climax', 'B', 'head', 'theme', 'loop') else 0)
        if best is None or score > best[0]:
            best = (score, s)
    sec = best[1]
    b0 = max(0, sec['bar'] - (2 if sec['bar'] >= 2 else 0))
    b1 = min(song['total_bars'], b0 + nbars)
    beat0, beat1 = b0 * 4, b1 * 4
    evs = []
    for e in song['events']:
        if beat0 <= e.beat < beat1:
            evs.append(e.copy(beat=e.beat - beat0, dur=min(e.dur, beat1 - e.beat)))
    fx = []
    for kind, b, d in song['fx']:
        if kind in ('crash', 'impact') and beat0 <= b < beat1:
            fx.append((kind, b - beat0, d))
        if kind in ('riser', 'hpsweep', 'gap') and b < beat1 and b + d > beat0:
            nb = max(b, beat0)
            fx.append((kind, nb - beat0, min(b + d, beat1) - nb))
    fx.append(('fade', beat1 - beat0 - 4, 4))
    secs = []
    for s in song['sections']:
        s0, s1 = max(s['bar'], b0), min(s['bar'] + s['bars'], b1)
        if s1 > s0:
            secs.append(dict(s, bar=s0 - b0, bars=s1 - s0))
    pv = dict(song)
    pv.update(events=evs, fx=fx, sections=secs, total_bars=b1 - b0, preview_of=(b0, b1))
    return pv
