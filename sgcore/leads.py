"""Genre lead devices: how a genre's lead line is built, not just which notes it may use.

Each device returns (notes, phrase_bars) with notes as (beat_in_phrase, length_beats, midi, velocity 0..1),
like compose.gen_melody, so every part of the arranger can use it unchanged.
"""
import math
import random

# which devices suit each genre (one is picked per song, so the same style still varies)
GENRE_DEVICES = {
    'bhajan': ['raga'], 'kirtan': ['raga'], 'aarti': ['raga'], 'santoor_raga': ['raga'], 'sitar_bhajan': ['raga'], 'tabla_bhajan': ['raga'], 'drum_kirtan': ['raga'], 'jugalbandi': ['raga'], 'qawwali': ['raga'], 'carnatic_kriti': ['raga'], 'ghazal': ['raga'], 'bollywood': ['raga', 'hook'], 'anatolian_psych': ['raga', 'riff'], 'klezmer': ['raga', 'hook'], 'rai': ['raga', 'hook'], 'ethio_jazz': ['riff', 'hook'], 'thai_funk': ['riff', 'call'], 'chicha': ['hook', 'call'], 'desert_blues': ['riff', 'call'], 'exotica': ['hook'], 'garage_rock': ['riff', 'hook'], 'rockabilly': ['hook', 'riff'], 'krautrock': ['ostinato', 'hook'], 'post_punk': ['riff', 'hook'], 'flamenco_rumba': ['hook', 'raga'], 'gamelan': ['ostinato', 'hook'], 'son_cubano': ['call', 'hook'], 'stoner_raga': ['raga'], 'raga_fusion': ['raga'],
    'epic_orchestral': ['hook'], 'epic_battle': ['hook', 'riff'], 'epic_choir': ['hook'], 'heroic_anthem': ['hook'], 'symphonic_finale': ['hook'],
    'italo_disco': ['hook', 'arp'], 'new_beat': ['ostinato', 'chops'], 'gabber': ['riff', 'hook'], 'rave_hardcore': ['chops', 'hook'],
    'future_funk': ['chops', 'call'], 'bebop': ['hook'], 'modal_jazz': ['hook', 'call'], 'soul_jazz': ['riff', 'call'], 'fusion': ['hook', 'riff'],
    'classical_period': ['hook', 'call'], 'romantic': ['hook'], 'impressionism': ['hook'], 'minimalism': ['ostinato'],
    'deep_dubstep': ['hook', 'ostinato'], 'deep_dubstep_minimal': ['hook', 'ostinato'], 'progressive_trance': ['hook', 'hook', 'call'], 'organic_house': ['hook', 'call'],
    'disco_funk': ['riff', 'call'],
    'trance': ['arp', 'hook'], 'progressive_house': ['arp', 'hook'], 'synthwave': ['arp', 'hook'], 'eurodance': ['hook', 'arp'],
    'chiptune': ['arp', 'hook'], 'electro': ['arp', 'riff'], 'synthpop': ['hook', 'arp'], 'bigroom': ['hook', 'chops'],
    'hardstyle': ['hook', 'arp'], 'future_bass': ['chops', 'hook'], 'hyperpop': ['hook', 'chops'],
    'techno': ['ostinato'], 'minimal': ['ostinato'], 'tech_house': ['ostinato', 'chops'], 'acid_house': ['ostinato'],
    'psytrance': ['ostinato', 'arp'], 'house': ['chops', 'hook'], 'deep_house': ['chops', 'call'], 'ukgarage': ['chops', 'call'],
    'rock': ['riff', 'hook'], 'metal': ['riff'], 'funk': ['riff', 'call'], 'blues': ['riff', 'call'], 'disco': ['hook', 'chops'],
    'trap': ['bell'], 'phonk': ['bell'], 'brazilian_phonk': ['bell'], 'uk_drill': ['bell'], 'boombap': ['hook', 'bell'], 'lofi': ['hook', 'bell'],
    'afrobeats': ['call', 'hook'], 'amapiano': ['call', 'chops'], 'reggaeton': ['call', 'hook'], 'moombahton': ['call', 'chops'],
    'reggae': ['call', 'hook'], 'dnb': ['hook', 'chops'], 'jungle': ['chops', 'hook'], 'dubstep': ['hook', 'riff'],
    'breakcore': ['arp', 'chops'], 'downtempo': ['hook', 'call'], 'vaporwave': ['hook', 'chops'], 'city_pop': ['hook', 'call'],
    'pop': ['hook', 'call'], 'folk': ['hook', 'call'], 'bossa_nova': ['hook', 'call'],
    'neoclassical': ['hook'], 'chamber': ['hook', 'call'], 'baroque': ['arp', 'hook'], 'fantasy_rpg': ['hook', 'call'],
    'hybrid_trailer': ['hook', 'ostinato'], 'orchestral_hiphop': ['bell', 'hook'], 'symphonic_metal': ['hook', 'riff'],
    'holiday': ['hook', 'call'], 'western': ['hook', 'call'], 'chamber_pop': ['hook', 'call'],
    'gospel': ['hook', 'call'], 'country': ['hook'], 'bluegrass': ['hook', 'arp'], 'motown': ['hook', 'call'], 'rnb': ['hook', 'call'],
    'swing': ['hook', 'call'], 'ska': ['hook', 'call'], 'punk': ['riff', 'hook'], 'indie_rock': ['hook', 'riff'],
    'salsa': ['hook', 'call'], 'cumbia': ['hook', 'call'], 'tango': ['hook'], 'dancehall': ['hook', 'call', 'chops'],
    'afro_house': ['hook', 'call', 'ostinato'], 'melodic_techno': ['ostinato', 'arp', 'hook'], 'kpop': ['hook', 'call', 'chops'],
    'jersey_club': ['chops', 'hook', 'call'], 'baile_funk': ['call', 'chops', 'hook'],
    'waltz': ['hook'], 'celtic_jig': ['hook'], 'soul_ballad': ['hook'],
    'braindance': ['arp', 'hook', 'chops'], 'hauntology': ['hook', 'hook', 'call'],
    'brostep': ['hook', 'chops'], 'melodic_dubstep': ['hook', 'hook', 'chops'], 'liquid_dnb': ['hook', 'call'], 'neurofunk': ['hook', 'chops'],
    'house_phonk': ['bell'], 'memphis_phonk': ['bell'],
    'uplifting_trance': ['hook', 'arp'], 'melodic_house': ['hook', 'call'], 'jam_band': ['hook', 'riff'],
    'teen_pop': ['hook', 'call', 'chops'], 'soft_rock': ['hook'], 'luxury_rap': ['hook', 'bell'],
}
DEVICES = ['hook', 'arp', 'riff', 'ostinato', 'bell', 'call', 'chops', 'raga']


def _tones(key, chord, lo, hi):
    """Chord-tone scale degrees (root, 3rd, 5th, 7th) inside [lo, hi]."""
    out = [d for d in range(lo - 7, hi + 8) if (d - chord) % 7 in (0, 2, 4)]
    return [d for d in out if lo <= d <= hi]


def _rh(pat):
    out = []
    for i, c in enumerate(pat):
        if c in 'xX':
            ln = 1
            while i + ln < len(pat) and pat[i + ln] == '-':
                ln += 1
            out.append((i, ln, c == 'X'))
    return out


def arp(key, prog, cb, st, rnd, cx):
    """Trance / synthwave: chord-tone arpeggios that climb and fall, with a top note on the phrase peak."""
    bars = 2 * len(prog) * cb
    shapes = [[0, 1, 2, 3], [0, 2, 1, 3], [3, 2, 1, 0], [0, 1, 2, 1], [0, 2, 3, 1], [1, 0, 2, 3]]
    shape = rnd.choice(shapes)
    rate = 4 if cx > 0.45 else 2                         # 16ths or 8ths
    gate = rnd.choice([0.5, 0.7, 0.9])
    notes = []
    for bar in range(bars):
        chord = prog[(bar // cb) % len(prog)]
        tones = _tones(key, chord, 0, 9)[:5] or [chord]
        if bar % 4 == 3 and rnd.random() < 0.6:
            shape = rnd.choice(shapes)
        n = 4 * rate
        for i in range(n):
            if rate == 4 and rnd.random() < 0.12 * (1 - cx):
                continue
            idx = shape[i % len(shape)] + (1 if (i // len(shape)) % 2 and len(tones) > 4 else 0)
            d = tones[min(idx, len(tones) - 1)]
            vel = 0.95 if i % rate == 0 else 0.72
            notes.append((bar * 4 + i / rate, gate / rate, key.deg(d, st['lead_oct']), vel))
    return notes, bars


def riff(key, prog, cb, st, rnd, cx):
    """Rock / metal / funk: a one-bar riff in a low register on the minor pentatonic, repeated, with a turnaround lick."""
    bars = 2 * len(prog) * cb
    rhs = ['x.x..x.xx.x..x..', 'x-.x.x-.x.x.x...', 'x..x..x.x..x..x.', 'xx.x.x..xx.x.x..', 'x.xx..x.x.xx..x.', 'x-..x.x-..x.x...']
    rh = _rh(rnd.choice(rhs))
    pent = [0, 3, 5, 7, 10, 12]                           # minor pentatonic semitones above the tonic
    base = 12 * (st['lead_oct'] - 1 + 1) + key.root      # an octave lower than other leads
    cells = [rnd.choice([0, 0, 0, 3, 5, 7]) for _ in rh]
    lick = [rnd.choice(pent) for _ in rh]
    notes = []
    for bar in range(bars):
        follow = (key.deg(prog[(bar // cb) % len(prog)], 0) - key.root) % 12 if rnd.random() < 0.5 else 0
        seq = lick if bar % 4 == 3 else cells
        for (step, ln, acc), semi in zip(rh, seq):
            midi = base + (semi + (follow if bar % 4 != 3 else 0)) % 12 + (12 if semi == 12 else 0)
            notes.append((bar * 4 + step / 4, ln / 4 * 0.85, midi, 1.0 if step % 4 == 0 else 0.8))
    return notes, bars


def ostinato(key, prog, cb, st, rnd, cx):
    """Techno / minimal / acid: a hypnotic 2-4 note figure that barely changes; one note shifts every few bars."""
    bars = 2 * len(prog) * cb
    rhs = ['x..x..x...x..x..', 'x.x...x.x.x...x.', '..x...x...x..x..', 'x..x..x.x..x....', 'x.xx.x..x.xx.x..', 'x..x.x..x..x.x..']
    rh = _rh(rnd.choice(rhs))
    pool = [2, 4, 0, 6, 7, 9, 3, 1]
    cell = [rnd.choice(pool[:4 + int(cx * 4)]) for _ in rh]
    cell[0] = rnd.choice([0, 2, 4, 7])
    gate = rnd.choice([0.35, 0.5, 0.8])
    notes = []
    for bar in range(bars):
        if bar and bar % 4 == 0 and rnd.random() < 0.55:
            i = rnd.randrange(len(cell))
            cell[i] = rnd.choice(pool)
        for (step, ln, acc), d in zip(rh, cell):
            notes.append((bar * 4 + step / 4, gate * ln / 4 + 0.05, key.deg(d, st['lead_oct']), 0.95 if acc or step == 0 else 0.75))
    return notes, bars


PHONK = {'phonk', 'house_phonk', 'memphis_phonk', 'brazilian_phonk'}


def bell(key, prog, cb, st, rnd, cx):
    """Trap / drill: a short motif in a narrow minor-pentatonic range, repeated three times, the fourth bar answers."""
    bars = 2 * len(prog) * cb
    pent = [0, 3, 5, 7, 10]
    phonk = st.get('name') in PHONK or st.get('melody_lang') == 'phonk'
    if phonk:
        pent = {'phrygian': [0, 1, 3, 7, 8], 'phrygian_dominant': [0, 1, 4, 7, 8]}.get(key.scale_name, [0, 3, 7, 8, 10])   # b2 / b6
    base = 12 * (st['lead_oct'] + 1) + key.root
    rhs = ['x.x.x...x.x.x...', 'x..x..x.x.x.x...', 'x.xx.x..x.xx.x..', 'x...x.x.x...x.x.', 'x.x.x.x.x..x..x.']
    if phonk:                                          # a short 3-7 note riff, looped hypnotically
        rhs = st.get('lead_rh') or ['x..x..x.x..x....']
    rh = _rh(rnd.choice(rhs))
    motif = [rnd.choice(pent[:4]) for _ in rh]
    answer = motif[:-2] + [rnd.choice(pent), 0] if len(motif) > 2 else motif
    notes = []
    for bar in range(bars):
        seq = answer if bar % 4 == 3 else motif
        oct_up = 12 if (bar // 4) % 2 and rnd.random() < 0.3 and not phonk else 0
        for (step, ln, acc), semi in zip(rh, seq):
            notes.append((bar * 4 + step / 4, max(0.2, ln / 4 * 0.9), base + semi + oct_up, 0.9 if step % 8 == 0 else 0.75))
    return notes, bars


def call(key, prog, cb, st, rnd, cx):
    """Afrobeats / reggae / reggaeton: a syncopated call that ends open, and an answer that comes home."""
    bars = 2 * len(prog) * cb
    rhs = ['..x.x..x.x.x....', 'x..x..x.x.x.....', '.x.x..x.x..x....', 'x.x..x.x..x.....', '..x..x.x..x.x...']
    notes = []
    call_rh, ans_rh = _rh(rnd.choice(rhs)), _rh(rnd.choice(rhs))
    start = rnd.choice([2, 4, 5])
    for pair in range(bars // 2):
        chord = prog[(pair * 2 // cb) % len(prog)]
        tones = _tones(key, chord, -1, 9) or [chord]
        d = min(tones, key=lambda x: abs(x - start))
        for i, (step, ln, acc) in enumerate(call_rh):        # call: rises, ends on a 2nd / 5th
            d += rnd.choice([1, 1, 2, -1, 0])
            if i == len(call_rh) - 1:
                d = rnd.choice([1, 4, 8])
            notes.append((pair * 8 + step / 4, ln / 4 * 0.8, key.deg(d, st['lead_oct']), 0.9))
        chord2 = prog[((pair * 2 + 1) // cb) % len(prog)]
        home = _tones(key, chord2, -2, 7) or [0]
        for i, (step, ln, acc) in enumerate(ans_rh):          # answer: falls, lands on a chord tone
            d -= rnd.choice([1, 1, 2, 0])
            if i == len(ans_rh) - 1:
                d = min(home, key=lambda x: abs(x - d))
            notes.append((pair * 8 + 4 + step / 4, ln / 4 * 0.8, key.deg(d, st['lead_oct']), 0.82))
    return notes, bars


def chops(key, prog, cb, st, rnd, cx):
    """House / garage / future bass: short vocal-chop style stabs on 2-3 high chord tones, syncopated."""
    bars = 2 * len(prog) * cb
    rhs = ['..x..x.x..x..x..', 'x..x..x...x.x...', '.x..x..x.x..x...', '..x.x..x..x.x.x.', 'x...x.x..x..x...']
    rh = _rh(rnd.choice(rhs))
    rh2 = _rh(rnd.choice(rhs))
    notes = []
    for bar in range(bars):
        chord = prog[(bar // cb) % len(prog)]
        tones = _tones(key, chord, 4, 11) or [chord + 7]
        picks = [rnd.choice(tones[-3:]) for _ in range(6)]
        for i, (step, ln, acc) in enumerate(rh if bar % 2 == 0 else rh2):
            notes.append((bar * 4 + step / 4, rnd.choice([0.12, 0.18, 0.25]), key.deg(picks[i % len(picks)], st['lead_oct']),
                          0.9 if i == 0 else 0.75))
    return notes, bars


def raga(key, prog, cb, st, rnd, cx):
    """Raga phrasing (bhajan, kirtan, devotional sitar / santoor / bansuri): melodies are not straight scales but a
    climb and a descent - aroha and avaroha. Each phrase winds upward (now and then touching the note above and
    turning back, a vakra move) to a peak it holds, then falls back down - again with small turns - and comes to rest
    on Sa or Pa with a long note. The long notes get meend (glides) from the style's slides."""
    bars = 2 * len(prog) * cb
    o = st['lead_oct']
    run = 0.25 if cx > 0.7 else 0.5                           # running notes: 8ths (16ths when busy)
    notes, t, end = [], 0.0, bars * 4.0
    while t < end - 2:
        lo = rnd.choice([-3, 0, 0, 0, 2])                      # start from low Pa, Sa or Ga
        peak = rnd.choice([4, 5, 7, 7, 7, 9])                  # Pa, Dha, upper Sa (most often), upper Re / Ga
        land = rnd.choice([x for x in (0, 0, 0, 4, -3) if x < peak])   # always come back down
        up, d = [lo], lo
        while d < peak:
            nxt = min(peak, d + rnd.choice([1, 1, 1, 2]))
            if rnd.random() < 0.22 and nxt < peak:            # vakra: touch the note above, turn back, go on
                up += [nxt, nxt + 1]
            up.append(nxt)
            d = nxt
        down, d = [], peak
        while d > land:
            nxt = max(land, d - rnd.choice([1, 1, 1, 2]))
            if rnd.random() < 0.18 and nxt > land:
                down += [nxt, nxt - 1]
            down.append(nxt)
            d = nxt
        phrase = [(x, run) for x in up[:-1]] + [(up[-1], rnd.choice([1.5, 2.0, 2.0]))]          # hold the peak
        phrase += [(x, run) for x in down[:-1]] + [(down[-1] if down else land, rnd.choice([2.0, 3.0]))]  # rest on Sa / Pa
        for rep in range(2 if st.get('call_response') else 1):   # kirtan: the leader sings it, the group sings it back
            for i, (deg, ln) in enumerate(phrase):
                if t + ln > end:
                    ln = end - t
                if ln < 0.2:
                    break
                strong = abs(t - round(t)) < 1e-6
                notes.append((t, ln * 0.94, key.deg(deg, o), (0.95 if strong else 0.8) * rnd.uniform(0.92, 1.0) * (0.9 if rep else 1.0)))
                t += ln
            t = math.ceil(t + rnd.choice([0.5, 1.0, 1.0]))     # a breath, then the next phrase on a beat
    return notes, bars


GENERATORS = {'raga': raga, 'arp': arp, 'riff': riff, 'ostinato': ostinato, 'bell': bell, 'call': call, 'chops': chops}


def pick_device(style, seed, wanted=None):
    if wanted in DEVICES:
        return wanted
    opts = GENRE_DEVICES.get(style, ['hook'])
    return random.Random(seed * 41 + 13).choice(opts)
