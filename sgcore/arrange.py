"""Arrangement: build-ups, transitions between sections and endings."""
import random
from .theory import COLORS, Ev, fold, grid_of, voice_chord


BUILD_STYLES = ['roll', 'triplet', 'kick_roll', 'filter', 'stutter', 'pause', 'lift', 'swell', 'hats', 'claps', 'toms',
                'halftime', 'drumless']


# a genre's own build-up first, then the other ones that suit it - each song (and each build in a song) picks from these
BUILD_FAMILY = {
    'roll': ['roll', 'triplet', 'claps', 'hats', 'drumless', 'swell', 'halftime'],
    'triplet': ['triplet', 'roll', 'hats', 'drumless', 'claps'],
    'kick_roll': ['kick_roll', 'roll', 'drumless', 'halftime'],
    'filter': ['filter', 'hats', 'drumless', 'claps', 'toms'],
    'stutter': ['stutter', 'halftime', 'drumless', 'roll', 'hats'],
    'pause': ['pause', 'drumless', 'halftime', 'hats'],
    'lift': ['lift', 'toms', 'claps', 'hats'],
    'swell': ['swell', 'toms', 'drumless'],
}


def build_sequence(default, forced, rnd, n=4):
    """The build-up style for each build in the song: never the same one twice in a row, and the genre's own one
    only some of the time, so songs (and the builds inside one song) don't all ramp up the same way."""
    if forced:
        return [default] * n
    fam = BUILD_FAMILY.get(default, [default])
    seq = [default if rnd.random() < 0.4 else rnd.choice(fam)]
    while len(seq) < n:
        seq.append(rnd.choice([b for b in fam if b != seq[-1]] or fam))
    return seq


GENRE_BUILD = {'riddim': 'pause', 'chillstep': 'swell', 'jazz_rap': 'pause', 'cloud_rap': 'swell', 'slow_jam': 'lift', 'smooth_jazz': 'lift', 'smooth_funk': 'lift', 'quiet_storm': 'swell', 'g_funk': 'lift', 'neo_soul': 'lift', 'new_jack_swing': 'claps', 'alt_rnb': 'pause', 'rage': 'roll', 'plugg': 'hats', 'hauntology_sunlit': 'pause', 'hauntology_dark': 'pause', 'epic_orchestral': 'roll', 'epic_battle': 'roll', 'epic_choir': 'swell', 'heroic_anthem': 'roll', 'symphonic_finale': 'swell', 'italo_disco': 'lift', 'new_beat': 'filter', 'gabber': 'kick_roll', 'rave_hardcore': 'roll', 'future_funk': 'filter', 'bebop': 'lift', 'modal_jazz': 'lift', 'soul_jazz': 'lift', 'fusion': 'lift', 'classical_period': 'swell', 'romantic': 'swell', 'impressionism': 'swell', 'minimalism': 'swell', 'deep_dubstep': 'pause', 'progressive_trance': 'roll', 'organic_house': 'filter', 'disco_funk': 'lift', 'trance': 'roll', 'bigroom': 'roll', 'progressive_house': 'roll', 'electro': 'roll', 'eurodance': 'roll',
               'moombahton': 'roll', 'dnb': 'roll', 'jungle': 'stutter', 'hardstyle': 'kick_roll', 'future_bass': 'triplet',
               'hyperpop': 'triplet', 'dubstep': 'stutter', 'breakcore': 'stutter', 'house': 'filter', 'deep_house': 'filter',
               'tech_house': 'filter', 'techno': 'filter', 'minimal': 'filter', 'acid_house': 'filter', 'psytrance': 'filter',
               'ukgarage': 'pause', 'amapiano': 'pause', 'afrobeats': 'pause', 'reggaeton': 'pause', 'synthwave': 'lift',
               'synthpop': 'lift', 'chiptune': 'lift', 'orchestral_hiphop': 'pause', 'hybrid_trailer': 'swell',
               'symphonic_metal': 'roll', 'kpop': 'lift', 'melodic_techno': 'filter', 'afro_house': 'filter',
               'jersey_club': 'pause', 'baile_funk': 'stutter', 'punk': 'roll', 'waltz': 'swell', 'celtic_jig': 'swell',
               'soul_ballad': 'swell', 'braindance': 'stutter', 'hauntology': 'pause', 'brostep': 'roll', 'melodic_dubstep': 'roll',
               'neurofunk': 'stutter', 'liquid_dnb': 'filter', 'house_phonk': 'pause', 'memphis_phonk': 'pause', 'phonk': 'pause', 'brazilian_phonk': 'pause', 'uplifting_trance': 'roll',
               'melodic_house': 'filter', 'teen_pop': 'lift', 'luxury_rap': 'pause', 'jam_band': 'lift', 'soft_rock': 'lift'}


BIG_SECTIONS = {'chorus', 'hook', 'climax', 'theme', 'drop'}


HIT_FORMS = {'song', 'song_b', 'jazz', 'orchestral', 'cinematic', 'trap', 'halftime', 'halftime_b', 'chip', 'trailer'}


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
    if bs == 'roll' and snare:
        roll(snare, (1, 2, 4, 8))
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
            div = 0.5 if pb < 0.5 else (2 if pb < 0.8 else 4)
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


def add_build_fx(fx, bs, start, nbars, riser=True):
    end = start + nbars * 4
    if bs in ('hats', 'claps', 'drumless') and not riser:     # band / pop / film styles: a swell, never an EDM riser
        fx.append(('swell', end - 4, 4))
        fx.append(('gap', end - 0.5, 0.5))
        return
    if bs in ('hats', 'claps'):
        fx.append(('riser', end - min(8, nbars * 4), min(8, nbars * 4)))
        fx.append(('gap', end - 0.5, 0.5))
        return
    if bs == 'toms':
        fx.append(('swell', end - 4, 4))
        return
    if bs == 'halftime':
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('swell', end - 4, 4))
        fx.append(('gap', end - 1, 1))
        return
    if bs == 'drumless':                                # drums out: only the riser, a filter and a reverse swell
        fx.append(('riser', end - min(8, nbars * 2), min(8, nbars * 2)))
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('swell', end - 4, 4))
        fx.append(('gap', end - 0.5, 0.5))
        return
    if bs in ('roll', 'triplet', 'kick_roll', 'stutter'):
        fx.append(('riser', start, nbars * 4))
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('gap', end - (1.0 if bs == 'stutter' else 0.5), 1.0 if bs == 'stutter' else 0.5))
    elif bs == 'filter':                                # long filter, short riser, kick-out
        fx.append(('hpsweep', start, nbars * 4))
        fx.append(('riser', end - 8, 8))
        fx.append(('gap', end - 1, 1))
    elif bs == 'pause':                                 # the band drops out, a swell, straight back in
        fx.append(('swell', end - 4, 4))
        fx.append(('gap', end - 0.5, 0.5))
    elif bs == 'lift':
        fx.append(('swell', end - 4, 4))
    elif bs == 'swell':
        fx.append(('riser', start, nbars * 4))
        fx.append(('swell', end - 4, 4))


def add_transitions(sections, evs, fx, tracks, st, opts):
    """A fill and a reverse-cymbal swell into every bigger section (chorus, drop, climax), in the genre's idiom:
    tom fills for band styles, snare fills for electronic ones."""
    from .instruments import DRUMS
    rnd = random.Random(opts.seed * 13 + 5)
    cat = st.get('category')
    snare = next((s for s in st.get('snare_tracks', []) if s in tracks), None)
    for cur, nxt in zip(sections, sections[1:]):
        bigger = nxt['opts'].get('drop') or nxt['name'] in BIG_SECTIONS
        if not bigger or cur['opts'].get('build'):
            continue
        end = (cur['bar'] + cur['bars']) * 4
        fx.append(('swell', end - 4, 4))
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
