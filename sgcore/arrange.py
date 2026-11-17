"""Arrangement: build-ups, transitions between sections and endings."""
import random
from .theory import COLORS, Ev, fold, grid_of, voice_chord


BUILD_STYLES = ['roll', 'triplet', 'kick_roll', 'filter', 'stutter', 'pause', 'lift', 'swell', 'hats', 'claps', 'toms',
                'halftime', 'drumless', 'pickup', 'ride', 'march', 'tomgroove', 'pulse', 'stops', 'tapestop', 'cymbal',
                'wash', 'none']
# the ones a live band / natural record would do: no accelerating rolls, no EDM risers
NATURAL_BUILDS = ['pickup', 'ride', 'tomgroove', 'march', 'stops', 'cymbal', 'lift', 'pause', 'toms', 'none']
BUILD_AMOUNTS = ['auto', 'subtle', 'off']          # how hard the songs ramp up into the big sections
TRANSITION_FX = ['auto', 'fewer', 'fills', 'off']  # risers / reverse cymbals / impacts: all, fewer, drum fills only, nothing
FX_SOUNDS = {'riser', 'swell', 'cymroll', 'wash', 'impact', 'crash', 'tapestop', 'downlift'}


# a genre's own build-up first, then the other ones that suit it - each song (and each build in a song) picks from these
BUILD_FAMILY = {
    'roll': ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup'],
    'triplet': ['triplet', 'roll', 'hats', 'drumless', 'wash', 'pulse', 'stops'],
    'kick_roll': ['kick_roll', 'roll', 'drumless', 'halftime', 'pulse', 'tapestop', 'wash'],
    'filter': ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride'],
    'stutter': ['stutter', 'halftime', 'drumless', 'tapestop', 'hats', 'stops', 'wash'],
    'pause': ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash'],
    'lift': ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps'],
    'swell': ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride'],
    'hats': ['hats', 'pulse', 'filter', 'pickup', 'wash', 'claps'],
    'claps': ['claps', 'pickup', 'hats', 'stops', 'lift', 'pulse'],
    'toms': ['toms', 'tomgroove', 'pickup', 'ride', 'stops', 'cymbal'],
    'ride': ['ride', 'pickup', 'lift', 'stops', 'cymbal', 'toms'],
    'march': ['march', 'cymbal', 'tomgroove', 'swell', 'pickup'],
    'tomgroove': ['tomgroove', 'march', 'toms', 'pickup', 'cymbal'],
    'pickup': ['pickup', 'ride', 'stops', 'lift', 'toms', 'none'],
}
SUBTLE = {'roll': 'pickup', 'triplet': 'pickup', 'kick_roll': 'pulse', 'stutter': 'pickup', 'drumless': 'pause',
          'halftime': 'pause', 'hats': 'ride', 'claps': 'pickup', 'filter': 'pickup', 'swell': 'cymbal', 'wash': 'pickup',
          'tapestop': 'pickup', 'pulse': 'pickup'}


def build_sequence(default, forced, rnd, n=4, amount='auto', family=None):
    """The build-up style for each build in the song. Each build in a song is a different one (until the genre runs
    out of ideas), the genre's own one only some of the time, so songs don't all ramp up the same way.
    amount: 'subtle' swaps the big EDM ramps for natural ones; 'off' = no build-ups at all."""
    if amount == 'off':
        return ['none'] * n
    if forced:
        seq = [default] * n
    else:
        fam = list(family or BUILD_FAMILY.get(default, [default, 'pickup', 'stops']))   # a genre may name its own
        first = default if rnd.random() < 0.35 else rnd.choice(fam)
        seq, pool = [first], [b for b in fam if b != first]
        while len(seq) < n:
            if not pool:
                pool = [b for b in fam if b != seq[-1]] or fam
            pick = rnd.choice(pool)
            pool.remove(pick)
            seq.append(pick)
    if amount == 'subtle':                          # natural ones only: the usual swap, or another natural one
        out = []
        for b in seq:
            if b not in NATURAL_BUILDS or b == 'none':
                b = SUBTLE.get(b, 'pickup') if rnd.random() < 0.4 else \
                    rnd.choice(['pickup', 'ride', 'stops', 'lift', 'pause', 'cymbal', 'tomgroove', 'toms'])
            if out and b == out[-1]:
                b = rnd.choice([x for x in ('pickup', 'ride', 'stops', 'lift', 'cymbal') if x != b])
            out.append(b)
        seq = out
    return seq


GENRE_BUILD = {'riddim': 'pause', 'chillstep': 'swell', 'jazz_rap': 'pause', 'cloud_rap': 'swell', 'slow_jam': 'lift', 'smooth_jazz': 'lift', 'smooth_funk': 'lift', 'quiet_storm': 'swell', 'g_funk': 'lift', 'neo_soul': 'lift', 'new_jack_swing': 'claps', 'alt_rnb': 'pause', 'rage': 'roll', 'plugg': 'hats', 'hauntology_sunlit': 'pause', 'hauntology_dark': 'pause', 'epic_orchestral': 'roll', 'epic_battle': 'roll', 'epic_choir': 'swell', 'heroic_anthem': 'roll', 'symphonic_finale': 'swell', 'italo_disco': 'lift', 'new_beat': 'filter', 'gabber': 'kick_roll', 'rave_hardcore': 'roll', 'future_funk': 'filter', 'bebop': 'lift', 'modal_jazz': 'lift', 'soul_jazz': 'lift', 'fusion': 'lift', 'classical_period': 'swell', 'romantic': 'swell', 'impressionism': 'swell', 'minimalism': 'swell', 'deep_dubstep': 'pause', 'deep_dubstep_minimal': 'pause', 'progressive_trance': 'roll', 'organic_house': 'filter', 'disco_funk': 'lift', 'trance': 'roll', 'bigroom': 'roll', 'progressive_house': 'roll', 'electro': 'roll', 'eurodance': 'roll',
               'moombahton': 'roll', 'dnb': 'roll', 'jungle': 'stutter', 'hardstyle': 'kick_roll', 'future_bass': 'triplet',
               'hyperpop': 'triplet', 'dubstep': 'stutter', 'breakcore': 'stutter', 'house': 'filter', 'deep_house': 'filter',
               'tech_house': 'filter', 'techno': 'filter', 'minimal': 'filter', 'acid_house': 'filter', 'psytrance': 'filter',
               'ukgarage': 'pause', 'amapiano': 'pause', 'afrobeats': 'pause', 'reggaeton': 'pause', 'synthwave': 'lift',
               'synthpop': 'lift', 'chiptune': 'lift', 'orchestral_hiphop': 'pause', 'hybrid_trailer': 'swell',
               'symphonic_metal': 'roll', 'kpop': 'lift', 'melodic_techno': 'filter', 'afro_house': 'filter',
               'jersey_club': 'pause', 'baile_funk': 'stutter', 'punk': 'roll', 'waltz': 'swell', 'celtic_jig': 'swell',
               'soul_ballad': 'swell', 'braindance': 'stutter', 'hauntology': 'pause', 'brostep': 'roll', 'melodic_dubstep': 'roll',
               'neurofunk': 'stutter', 'neurofunk_lite': 'roll', 'jump_up': 'roll', 'dark_synthwave': 'filter', 'modern_gospel': 'swell', 'liquid_dnb': 'filter', 'house_phonk': 'pause', 'memphis_phonk': 'pause', 'phonk': 'pause', 'brazilian_phonk': 'pause', 'uplifting_trance': 'roll',
               'melodic_house': 'filter', 'teen_pop': 'lift', 'luxury_rap': 'pause', 'jam_band': 'lift', 'soft_rock': 'lift',
               'funky_breaks': 'stutter', 'piano_miniature': 'none', 'uk_road_rap': 'pause'}


BIG_SECTIONS = {'chorus', 'hook', 'climax', 'theme', 'drop'}


HIT_FORMS = {'spooky_surf', 'surf_rock', 'monster_theme', 'lofi_rock', 'nu_metal', 'song', 'song_b', 'jazz', 'orchestral', 'cinematic', 'trap', 'halftime', 'halftime_b', 'chip', 'trailer'}


def _track_of(tracks, layer):
    return next((n for n, t in tracks.items() if t['layer'] == layer), None)


def add_build_drums(evs, st, tracks, snares, kick, b, nbars, beat0, rnd):
    """The build-up's drums, in the genre's idiom."""
    bs = st.get('build_style', 'roll')
    last = b == nbars - 1
    pb = b / max(1, nbars - 1)
    snare = snares[0] if snares else None

    def roll(track, divs):
        div = divs[0] if pb < 0.5 else (divs[1] if pb < 0.75 else (divs[2] if not last else divs[3]))
        for k in range(int(4 * div)):
            pos = k / div
            if last and pos >= 3.5:
                break
            evs.append(Ev(track, beat0 + pos, 0.25, None, 0.35 + 0.6 * (b + pos / 4) / nbars))
    sec0 = int(beat0 - 4 * b) // 4                      # each build in a song gets its own ramp shape
    if bs == 'roll' and snare:
        roll(snare, [(1, 2, 4, 8), (2, 2, 4, 4), (1, 2, 2, 4), (2, 4, 4, 8), (1, 1, 2, 4)][sec0 % 5])
    elif bs == 'triplet' and snare:
        roll(snare, (1, 1.5, 3, 6))                     # triplet subdivisions
    elif bs == 'kick_roll' and kick in tracks:
        roll(kick, (1, 2, 4, 4))
    elif bs == 'stutter' and snare:
        if b >= nbars - 2:                              # chopped, stuttering last two bars
            for k in range(16 if not last else 12):
                if rnd.random() < 0.85:
                    evs.append(Ev(snare, beat0 + k / 4, 0.12, None, 0.5 + 0.4 * k / 16))
        else:
            for pos in (1, 3):
                evs.append(Ev(snare, beat0 + pos, 0.25, None, 0.7))
    elif bs == 'filter' and last and snare and rnd.random() < 0.6:
        for k in range(4):                              # a little clap/snare push into the drop
            evs.append(Ev(snare, beat0 + 2 + k / 2, 0.25, None, 0.5 + 0.12 * k))
    elif bs == 'lift' and last and snare:
        for k in range(8):
            evs.append(Ev(snare, beat0 + k / 2, 0.25, None, 0.4 + 0.07 * k))
        for k in range(4):
            evs.append(Ev(snare, beat0 + 3 + k / 4, 0.25, None, 0.85))
    elif bs == 'swell' and snare and b >= nbars - 2:
        g = grid_of(st)
        for k in range(g if not last else g - 2):
            evs.append(Ev(snare, beat0 + 4 * k / g, 0.25, None, 0.25 + 0.6 * ((b - nbars + 2) * g + k) / (2 * g)))
    elif bs == 'hats':                                  # hats accelerate, open hats on the last off-beats
        hat = next((h for h in ('chat', 'hat', 'shaker', 'ohat') if h in tracks), None)
        if hat:
            roll(hat, (2, 4, 4, 8))
            if last and 'ohat' in tracks:
                for pos in (0.5, 1.5, 2.5):
                    evs.append(Ev('ohat', beat0 + pos, 0.25, None, 0.8))
    elif bs == 'claps':                                 # claps on 2 and 4, then 8ths, then 16ths
        clap = 'clap' if 'clap' in tracks else snare
        if clap:
            div = [(0.5, 2, 4), (0.5, 1, 2), (0.5, 0.5, 2), (1, 2, 2)][sec0 % 4]
            div = div[0] if pb < 0.5 else (div[1] if pb < 0.8 else div[2])
            for k in range(int(4 * div)):
                pos = k / div
                if div == 0.5:
                    pos = 1 + 2 * k
                if last and pos >= 3.5:
                    break
                evs.append(Ev(clap, beat0 + pos, 0.25, None, 0.45 + 0.5 * (b + pos / 4) / nbars))
    elif bs == 'toms':                                  # a tom run down the kit, getting busier
        toms = ensure_toms(st, tracks)
        sub = 2 if pb < 0.6 else 4
        steps = int(4 * sub) if not last else int(3 * sub)
        for k in range(steps):
            if sub == 2 or k % 2 == 0 or rnd.random() < 0.7:
                name = toms[min(2, int(3 * k / steps))]
                evs.append(Ev(name, beat0 + k / sub, 0.25, None, 0.45 + 0.45 * (b + k / steps) / nbars))
    elif bs == 'halftime':                              # the beat drops to half-time, then snaps forward
        if kick in tracks and not last:
            evs.append(Ev(kick, beat0, 0.25, None, 0.9))
        if snare:
            if not last:
                evs.append(Ev(snare, beat0 + 2, 0.25, None, 0.8))
            else:
                for k in range(8):
                    evs.append(Ev(snare, beat0 + k / 2 if k < 4 else beat0 + 2 + (k - 4) / 4, 0.25, None, 0.5 + 0.06 * k))
    elif bs == 'pickup' and last:                       # the groove just carries on - a short fill on the last beat
        toms = ensure_toms(st, tracks) if rnd.random() < 0.5 else None
        figs = [(3.0, 3.25, 3.5, 3.75), (3.5, 3.75), (3.0, 3.5, 3.75), (2.5, 3.0, 3.5), (3.25, 3.5, 3.75)]
        fig = rnd.choice(figs)
        evs[:] = [e for e in evs if not (e.track in (snare, *(toms or [])) and e.beat >= beat0 + fig[0])]
        for k, pos in enumerate(fig):
            name = toms[min(2, k)] if toms and k < len(fig) - 1 else snare
            if name:
                evs.append(Ev(name, beat0 + pos, 0.25, None, 0.6 + 0.3 * k / max(1, len(fig) - 1)))
    elif bs == 'ride':                                  # a ride (or crash) on every 8th, getting louder, bell on the beat
        cym = ensure_drum(st, tracks, 'bride', 'ride', 'top', -24, 0.3)
        for k in range(8 if not last else 7):
            evs.append(Ev(cym, beat0 + k / 2, 0.25, None, (0.35 + 0.45 * (b + k / 8) / nbars) * (1.0 if k % 2 == 0 else 0.75)))
        if last and snare:
            for pos in (3.0, 3.5, 3.75):
                evs.append(Ev(snare, beat0 + pos, 0.25, None, 0.8))
    elif bs == 'march' and snare:                       # a marching snare: rudiments, crescendo, no speeding up
        pats = ['X.xxX.x.X.xxX.x.', 'X.x.X.xxX.x.X.xx', 'X.xxX.xxX.xxX.x.'] if grid_of(st) == 16 else ['X.xX.xX.xX.x']
        pat = pats[b % len(pats)] if not last else ('X.xxX.xxxxxxxxxx' if grid_of(st) == 16 else 'X.xX.xxxxxxx')
        g = len(pat)
        for k, c in enumerate(pat):
            if c != '.':
                v = (0.3 + 0.55 * (b + k / g) / nbars) * (1.0 if c == 'X' else 0.7)
                evs.append(Ev(snare, beat0 + 4 * k / g, 0.25, None, v))
                if c == 'X' and rnd.random() < 0.3:          # a flam
                    evs.append(Ev(snare, beat0 + 4 * k / g - 0.04, 0.25, None, v * 0.5))
    elif bs == 'tomgroove':                             # floor toms carry a rolling tribal groove
        toms = ensure_toms(st, tracks)
        pat = [(0, 2), (0.75, 1), (1.5, 2), (2, 1), (2.5, 0), (3, 2), (3.5, 1)] if not last else \
              [(0, 2), (0.75, 1), (1.5, 2), (2, 1), (2.5, 0), (2.75, 0), (3, 1), (3.25, 1), (3.5, 2), (3.75, 2)]
        for pos, t in pat:
            evs.append(Ev(toms[t], beat0 + pos, 0.25, None, 0.4 + 0.5 * (b + pos / 4) / nbars))
    elif bs == 'pulse' and kick in tracks:              # the beat thins to a steady kick pulse, then holds its breath
        for k in range(4):
            if not (last and k == 3):
                evs.append(Ev(kick, beat0 + k, 0.25, None, 0.6 + 0.35 * (b + k / 4) / nbars))
        if last and snare:
            for pos in (3.0, 3.25, 3.5):
                evs.append(Ev(snare, beat0 + pos, 0.25, None, 0.7))
    elif bs == 'stops' and b >= nbars - 2:             # the band plays stop-time hits together
        hits = stop_hits(beat0 - (b - (nbars - 2)) * 4 if b == nbars - 1 else beat0, b == nbars - 1)
        drum_like = {n for n, t in tracks.items() if t.get('layer') in ('kick', 'snare', 'top')}
        evs[:] = [e for e in evs if not (e.track in drum_like and beat0 <= e.beat < beat0 + 4)]
        for pos in hits:
            if kick in tracks:
                evs.append(Ev(kick, beat0 + pos, 0.25, None, 0.9))
            if snare:
                evs.append(Ev(snare, beat0 + pos, 0.25, None, 0.85))
    elif bs == 'cymbal' and last and snare:            # a mallet cymbal roll (fx) - the drums just mark the last beat
        evs.append(Ev(snare, beat0 + 3.5, 0.25, None, 0.7))
        evs.append(Ev(snare, beat0 + 3.75, 0.25, None, 0.85))
    if bs in ('filter', 'kick_roll', 'lift') and last:   # kick drops out on the final beat
        evs[:] = [e for e in evs if not (e.track == kick and e.beat >= beat0 + 3)]


def ensure_toms(st, tracks):
    names = []
    for name, pitch, pan in (('tom_hi', 190, 0.25), ('tom_mid', 140, 0.0), ('tom_lo', 100, -0.25)):
        if name not in tracks:
            t = dict(name=name, layer='snare', inst='tom', pan=pan, rev=0.12, dly=0.0, sc=0.0, db=-19, hp=None, drive=None, p={})
            tracks[name] = t
            st['tracks'].append(t)
        st.setdefault('drum_voice', {})[name] = {'pitch': pitch}
        names.append(name)
    return names


def ensure_drum(st, tracks, name, inst, layer, db, pan):
    if name not in tracks:
        t = dict(name=name, layer=layer, inst=inst, pan=pan, rev=0.1, dly=0.0, sc=0.0, db=db, hp=None, drive=None, p={})
        tracks[name] = t
        st['tracks'].append(t)
    return name


STOP_FIGURES = [[0, 1.5, 3.0], [0, 0.75, 1.5, 3.0], [0, 2.0, 3.0, 3.5], [0, 1.0, 2.5], [0, 1.5, 2.5, 3.5]]


def stop_hits(pair_start, second):
    """Beats (within the bar) of the band's stop-time hits for a 'stops' build; the same figure for the build's drums
    and its silences. The second bar answers the first."""
    fig = STOP_FIGURES[int(pair_start) // 4 % len(STOP_FIGURES)]
    return [0, 1.0, 2.0, 2.5, 3.0, 3.25, 3.5] if second else fig


def stop_gaps(beat0, hits, hit_len=0.4):
    out = []
    for k, h in enumerate(hits):
        nxt = hits[k + 1] if k + 1 < len(hits) else 4.0
        if nxt - h > hit_len + 0.1:
            out.append(('gap', beat0 + h + hit_len, nxt - h - hit_len))
    return out


def _end_fx(rnd, end, riser):
    """How the last bar leads into the next section - varied, not always a reverse cymbal."""
    kind = rnd.choice(['swell', 'cymroll', 'wash', None, None] if riser else ['swell', 'cymroll', None, None])
    if kind == 'cymroll':
        return [('cymroll', end - 2, 2)]
    if kind == 'wash':
        return [('wash', end - 4, 4)]
    if kind == 'swell':
        return [('swell', end - rnd.choice([2, 4]), 2 if rnd.random() < 0.4 else 4)]
    return []


def add_build_fx(fx, bs, start, nbars, riser=True, rnd=None):
    end = start + nbars * 4
    rnd = rnd or random.Random(int(start) * 7 + len(bs))
    if bs in ('none', 'pickup', 'march', 'tomgroove', 'ride'):     # natural builds: the drums do it all
        if bs in ('march', 'tomgroove') and rnd.random() < 0.4:
            fx.append(('cymroll', end - 2, 2))
        return
    if bs == 'cymbal':
        fx.append(('cymroll', end - min(8, nbars * 4), min(8, nbars * 4)))
        return
    if bs == 'stops':
        if nbars >= 2:
            fx.extend(stop_gaps(end - 8, stop_hits(end - 8, False)))
        fx.extend(stop_gaps(end - 4, stop_hits(end - 8, True), 0.2))
        return
    if bs == 'tapestop':
        fx.append(('tapestop', end - 2, 1.5))
        fx.append(('gap', end - 0.5, 0.5))
        return
    if bs == 'wash':
        fx.append(('wash', start, nbars * 4))
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('gap', end - 0.5, 0.5))
        return
    if bs == 'pulse':
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('riser', start, nbars * 4) if riser else ('wash', end - 4, 4))
        return
    if bs in ('hats', 'claps', 'drumless') and not riser:     # band / pop / film styles: a swell, never an EDM riser
        fx.extend(_end_fx(rnd, end, False))
        fx.append(('gap', end - 0.5, 0.5))
        return
    if bs in ('hats', 'claps'):
        fx.append(('riser', end - min(8, nbars * 4), min(8, nbars * 4)))
        fx.append(('gap', end - 0.5, 0.5))
        return
    if bs == 'toms':
        fx.extend(_end_fx(rnd, end, False))
        return
    if bs == 'halftime':
        fx.append(('hpsweep', start, nbars * 4))
        fx.extend(_end_fx(rnd, end, riser))
        fx.append(('gap', end - 1, 1))
        return
    if bs == 'drumless':                                # drums out: a riser or noise wash, a filter, a lead-in
        fx.append(('riser', end - min(8, nbars * 2), min(8, nbars * 2)) if riser and rnd.random() < 0.6 else ('wash', start, nbars * 4))
        fx.append(('hpsweep', start, nbars * 4))
        fx.extend(_end_fx(rnd, end, riser))
        fx.append(('gap', end - 0.5, 0.5))
        return
    if bs in ('roll', 'triplet', 'kick_roll', 'stutter'):
        fx.append(('riser', start, nbars * 4) if riser or rnd.random() < 0.3 else ('wash', start, nbars * 4))
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('gap', end - (1.0 if bs == 'stutter' else 0.5), 1.0 if bs == 'stutter' else 0.5))
    elif bs == 'filter':                                # long filter, short riser, kick-out
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('riser', end - 8, 8))
        fx.append(('gap', end - 1, 1))
    elif bs == 'pause':                                 # the band drops out, a lead-in, straight back in
        fx.extend(_end_fx(rnd, end, riser))
        fx.append(('gap', end - 0.5, 0.5))
    elif bs == 'lift':
        fx.extend(_end_fx(rnd, end, False))
    elif bs == 'swell':
        fx.append(('riser', start, nbars * 4) if riser else ('cymroll', end - min(8, nbars * 4), min(8, nbars * 4)))
        fx.append(('swell', end - 4, 4))


def add_transitions(sections, evs, fx, tracks, st, opts):
    """A fill and a lead-in into every bigger section (chorus, drop, climax), in the genre's idiom: tom fills for band
    styles, snare fills for electronic ones; the lead-in changes each time (reverse cymbal, mallet roll, noise wash,
    tape stop, a moment of silence, just a crash - or nothing). opts.transition_fx: auto | fewer | fills | off."""
    from .instruments import DRUMS
    rnd = random.Random(opts.seed * 13 + 5)
    cat = st.get('category')
    mode = getattr(opts, 'transition_fx', 'auto') or 'auto'
    if mode == 'off' or st.get('no_transition_fx'):
        return
    snare = next((s for s in st.get('snare_tracks', []) if s in tracks), None)
    # how each transition is marked - a mix of moves, never the same one twice in a row (and mostly no reverse cymbal)
    moves = {'Electronic': ['swell', 'wash', 'tapestop', 'gap', 'crash', 'none', 'none', 'downlift'],
             'Classic': ['swell', 'cymroll', 'crash', 'crash', 'none', 'none', 'gap'],
             'Orchestral': ['cymroll', 'cymroll', 'swell', 'none', 'crash']}.get(cat, ['swell', 'crash', 'none', 'gap'])
    moves = st.get('transition_moves') or moves                 # a genre's own way of moving between sections
    last_move = None
    for cur, nxt in zip(sections, sections[1:]):
        bigger = nxt['opts'].get('drop') or nxt['name'] in BIG_SECTIONS
        if not bigger or cur['opts'].get('build'):
            continue
        end = (cur['bar'] + cur['bars']) * 4
        if mode == 'fewer' and rnd.random() < 0.5:
            continue
        move = rnd.choice([m for m in moves if m != last_move] or moves)
        last_move = move
        if mode != 'fills':
            if move == 'swell':
                d = 2 if rnd.random() < 0.4 else 4
                fx.append(('swell', end - d, d))
            elif move == 'cymroll':
                fx.append(('cymroll', end - 2, 2))
            elif move == 'wash':
                fx.append(('wash', end - 4, 4))
            elif move == 'tapestop' and st.get('category') == 'Electronic':
                fx.append(('tapestop', end - 1.5, 1.0))
                fx.append(('gap', end - 0.5, 0.5))
                continue                                    # the tape stop is the fill
            elif move == 'downlift':
                fx.append(('downlift', end, 4))
            elif move == 'crash':
                fx.append(('crash', end, 0))
        if move == 'gap':
            fx.append(('gap', end - 0.5, 0.5))
        if 'snare' not in cur['layers'] or not snare or rnd.random() > (0.55 + 0.45 * opts.energy) * (1 - 0.8 * float(getattr(opts, 'simplicity', 0) or 0)):
            continue
        beats = 2 if cat == 'Classic' else rnd.choice([1, 1, 2])
        start = end - beats
        drum_names = {n for n, t in tracks.items() if t['inst'] in DRUMS and t['layer'] in ('snare', 'top')}
        evs[:] = [e for e in evs if not (e.track in drum_names and start <= e.beat < end)]
        sub = 4 if grid_of(st) == 16 else 3                 # 16ths, or triplet 8ths in 3/4, 6/8, 12/8
        if cat == 'Classic' and opts.structure != 'loop':
            for name, pitch in (('tom_hi', 190), ('tom_mid', 140), ('tom_lo', 100)):
                if name not in tracks:
                    t = dict(name=name, layer='snare', inst='tom', pan={'tom_hi': 0.25, 'tom_mid': 0.0, 'tom_lo': -0.25}[name],
                             rev=0.12, dly=0.0, sc=0.0, db=-19, hp=None, drive=None, p={})
                    tracks[name] = t
                    st['tracks'].append(t)
                st.setdefault('drum_voice', {})[name] = {'pitch': pitch}
            n = beats * sub
            for k in range(n):
                name = 'tom_hi' if k < n / 3 else ('tom_mid' if k < 2 * n / 3 else 'tom_lo')
                if k % 2 == 0 or rnd.random() < 0.6:
                    evs.append(Ev(snare if k == 0 else name, start + k / sub, 0.25, None, 0.6 + 0.35 * k / n))
        else:                                               # electronic: the fill changes from one transition to the next
            n = beats * sub
            kind = rnd.choice(['snare', 'snare', 'toms', 'hats', 'gap', 'clap_flam'])
            if kind == 'toms':
                toms = ensure_toms(st, tracks)
                for k in range(n):
                    if k % 2 == 0 or rnd.random() < 0.6:
                        evs.append(Ev(toms[min(2, int(3 * k / n))], start + k / sub, 0.25, None, 0.55 + 0.35 * k / n))
            elif kind == 'hats' and any(h in tracks for h in ('chat', 'ohat')):
                hat = 'chat' if 'chat' in tracks else 'ohat'
                for k in range(n * 2):
                    evs.append(Ev(hat, start + k / (2 * sub), 0.12, None, 0.35 + 0.5 * k / (2 * n)))
                if 'ohat' in tracks:
                    evs.append(Ev('ohat', end - 0.5, 0.25, None, 0.85))
            elif kind == 'gap':                             # everything stops for the last beat - silence is the fill
                fx.append(('gap', end - 1, 1))
            elif kind == 'clap_flam':
                clap = 'clap' if 'clap' in tracks else snare
                for pos in (end - 1.0, end - 0.5, end - 0.25):
                    evs.append(Ev(clap, pos, 0.25, None, 0.8))
            else:
                for k in range(n):
                    evs.append(Ev(snare, start + k / sub, 0.25, None, 0.45 + 0.5 * k / n))


def apply_ending(sections, evs, fx, tracks, st, opts, key, chord_size, chord_color, total_bars):
    """End on a final chord hit with crash (bands, film, hip-hop) instead of fading out; club mixes keep their fade."""
    mode = getattr(opts, 'ending', 'auto') or 'auto'
    form = st.get('form') if isinstance(st.get('form'), str) else ''
    if mode == 'auto':
        mode = 'hit' if (form in HIT_FORMS and opts.structure not in ('club', 'loop')) else 'fade'
    if mode != 'hit' or opts.structure == 'loop' or not sections:
        return total_bars
    last = sections[-1]
    fx[:] = [f for f in fx if not (f[0] == 'fade' and f[1] >= last['bar'] * 4)]
    end = total_bars * 4
    shift = next((s_['key_change'] for s_ in sections if s_.get('key_change')), 0)
    ring = 6.0
    ch, pad, bass = _track_of(tracks, 'chords'), _track_of(tracks, 'pad'), _track_of(tracks, 'bass')
    third = (key.deg(2, 4) - key.deg(0, 4)) % 12
    pic = None                                     # Picardy third: a minor-key piece ends on a major chord
    if third == 3 and st.get('category') in ('Orchestral', 'Classic') and st.get('voicing') != 'power' \
            and random.Random(opts.seed * 17 + 3).random() < 0.35:
        pic = key.deg(2, 4) % 12
    lift = lambda m: m + 1 if pic is not None and m % 12 == pic else m
    if ch:
        for m in voice_chord(key, 0, chord_size, st.get('chord_center', 62), st.get('voicing', 'close'),
                             chord_color if chord_color in COLORS else None):
            evs.append(Ev(ch, end, ring, lift(m) + shift, 0.88))
    if pad:
        for m in voice_chord(key, 0, 3, st.get('chord_center', 62) - 2, 'open'):
            evs.append(Ev(pad, end, ring, lift(m) + shift, 0.7))
    if pic is not None:
        last['picardy'] = True
    if bass:
        evs.append(Ev(bass, end, ring - 1, fold(key.deg(0, 2), st['bass_lo']) + shift, 0.9))
    kick = st.get('kick_track', 'kick')
    if kick in tracks:
        evs.append(Ev(kick, end, 0.25, None, 1.0))
    fx.append(('crash', end, 0))
    if st.get('category') == 'Orchestral' or form == 'cinematic':
        fx.append(('impact', end, 0))
    last['ending'] = 'hit'
    return total_bars + 1                          # the hit rings out into the render's tail
