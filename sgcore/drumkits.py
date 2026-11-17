"""Drum kits: what a genre's drums sound like, and the kit menu you can switch between.

Three kinds of kit:
  drum machines   synthesized 808 / 909 / trance / techno / 80s LinnDrum-style / hardstyle ... (no download)
  real kits       recorded acoustic drums from the free drum library (studio, big rock room, vintage lo-fi)
  breaks          the classic breakbeat *patterns* (Amen, Think, Funky Drummer, Apache, Back to Life, Levee),
                  re-played on the real kit - with jungle-style chopping where the genre does that.

The breaks are re-played, not sampled: a drum pattern isn't anyone's recording, so songs that use them stay yours.
If you own a recording of a break, put its hits in "My sounds" and tick "my samples" to play the patterns with it.
"""

# ----------------------------------------------------------------------------- break patterns (16 steps per bar, 4 bars)
# X accent, x normal, o ghost. Classic transcriptions of the drummer's pattern.
BREAKS = {
    'amen': dict(
        label='Amen-style break', bpm=(136, 176), mic='lofi', pitch=1.5, swing=0.5,
        drums={'kick': ['X.X.......XX....', 'X.X.......XX....', 'X.X.......X.....', '..XX......X.....'],
               'snare': ['....X..x.x..X..x', '....X..x.x..X..x', '....X..x.x....X.', '.x..X..x.x....X.'],
               'ride': ['x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.......'],
               'crash': ['................', '................', '................', '..........X.....']}),
    'think': dict(
        label='Think-style break', bpm=(110, 176), mic='lofi', pitch=1.0, swing=0.52,
        drums={'kick': ['X.......X.X.....', 'X.X.......X..X..', 'X.......X.X.....', 'X.X.......X.....'],
               'snare': ['....X..x.x..X...', '....X..x....X.x.', '....X..x.x..X...', '.o..X..x....X..x'],
               'chat': ['x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x...', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.....'],
               'ohat': ['................', '..............x.', '................', '............x...']}),
    'funky_drummer': dict(
        label='Funky Drummer-style break', bpm=(86, 104), mic='lofi', pitch=0.0, swing=0.54,
        drums={'kick': ['X.X.......X..X..', 'X.X.......X..X..', 'X.X.......X..X..', 'X.X...X...X.....'],
               'snare': ['....X..o.o.oX..o', '.o..X..o.o..X..o', '....X..o.o.oX..o', '.o..X..o.o..X.oo'],
               'chat': ['x.xxx.x.x.xxx.xx', 'x.xxx.x.x.xxx.xx', 'x.xxx.x.x.xxx.xx', 'x.xxx.x.x.xx....'],
               'ohat': ['.......x........', '.......x........', '.......x........', '.......x....x...']}),
    'apache': dict(
        label='Apache-style break', bpm=(90, 120), mic='lofi', pitch=0.5, swing=0.53,
        drums={'kick': ['X.....X...X.....', 'X.....X...X..X..', 'X.....X...X.....', 'X.....X.X.X.....'],
               'snare': ['....X.......X...', '....X.......X...', '....X.......X...', '....X.....x.X..x'],
               'chat': ['x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.'],
               'conga': ['..x.xx..x..x.x.x', '..x.xx..x..x.xx.', '..x.xx..x..x.x.x', 'x.x.xx..x.xx.x..']}),
    'back_to_life': dict(
        label='Back to Life / Tom\'s Diner-style groove', bpm=(88, 104), mic='studio', pitch=0.0, swing=0.62,
        drums={'kick': ['X......X..X.....', 'X......X..X..x..', 'X......X..X.....', 'X......X..X...x.'],
               'snare': ['....X.......X...', '....X.......X...', '....X.......X...', '....X.......X..o'],
               'chat': ['x.xxx.xxx.xxx.xx', 'x.xxx.xxx.xxx.xx', 'x.xxx.xxx.xxx.xx', 'x.xxx.xxx.xx..xx'],
               'ohat': ['..............x.', '..............x.', '..............x.', '..........x.....'],
               'shaker': ['x.xxx.xxx.xxx.xx', 'x.xxx.xxx.xxx.xx', 'x.xxx.xxx.xxx.xx', 'x.xxx.xxx.xxx.xx']}),
    'levee': dict(
        label='Levee-style break (big room)', bpm=(70, 100), mic='room', pitch=-0.5, swing=0.52,
        drums={'kick': ['XX.....X..XX....', 'XX.....X..XX....', 'XX.....X..XX....', 'XX.....X..X.X...'],
               'snare': ['....X.......X...', '....X.......X...', '....X.......X...', '....X.......X.xx'],
               'chat': ['x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.']}),
}
BREAK_TRACKS = {'kick': ('kick', 'kick', -13, 0.0), 'snare': ('snare', 'snare', -16, 0.0), 'ride': ('top', 'ride', -26, 0.25),
                'chat': ('top', 'chat', -25, 0.2), 'ohat': ('top', 'ohat', -27, 0.25), 'crash': ('top', 'crash', -26, -0.2),
                'conga': ('top', 'conga', -23, -0.3), 'shaker': ('top', 'shaker', -29, 0.35)}

# ----------------------------------------------------------------------------- the kit menu
# id -> (group, label, synth preset used when nothing else applies, real-kit mic or None, break or None)
KIT_MENU = [
    ('808', 'Drum machines', 'TR-808 (rap, trap, drill)', '808', None, None),
    ('909', 'Drum machines', 'TR-909 (house)', '909', None, None),
    ('trance', 'Drum machines', 'Trance 909 (rolling kick, open hats)', 'trance', None, None),
    ('techno', 'Drum machines', 'Techno 909 (hard, rumble)', 'techno', None, None),
    ('linn', 'Drum machines', '80s LinnDrum-style (gated snare)', 'linn', None, None),
    ('punchy', 'Drum machines', 'Punchy EDM', 'punchy', None, None),
    ('hard', 'Drum machines', 'Hardstyle / big room', 'hard', None, None),
    ('soft', 'Drum machines', 'Soft / deep', 'soft', None, None),
    ('studio', 'Real kits', 'Studio acoustic kit', 'acoustic', 'studio', None),
    ('rock', 'Real kits', 'Rock kit (big room)', 'acoustic', 'room', None),
    ('vintage', 'Real kits', 'Vintage / lo-fi kit', 'soft', 'lofi', None),
    ('seventies', 'Real kits', '70s soul / funk kit (dry, warm)', 'acoustic', 'seventies', None),
    ('brushes', 'Real kits', 'Jazz brushes kit', 'soft', 'brushes', None),
    ('rusty', 'Real kits', 'Big vintage rock kit', 'acoustic', 'rusty', None),
    ('amen', 'Breaks (re-played)', BREAKS['amen']['label'] + ' - jungle, DnB', 'acoustic', None, 'amen'),
    ('think', 'Breaks (re-played)', BREAKS['think']['label'] + ' - DnB, breaks', 'acoustic', None, 'think'),
    ('funky_drummer', 'Breaks (re-played)', BREAKS['funky_drummer']['label'] + ' - boom bap', 'acoustic', None, 'funky_drummer'),
    ('apache', 'Breaks (re-played)', BREAKS['apache']['label'] + ' - hip-hop, breaks', 'acoustic', None, 'apache'),
    ('back_to_life', 'Breaks (re-played)', BREAKS['back_to_life']['label'] + ' - downtempo, trip-hop', 'acoustic', None, 'back_to_life'),
    ('levee', 'Breaks (re-played)', BREAKS['levee']['label'] + ' - trip-hop, big beat', 'acoustic', None, 'levee'),
]
MENU = {k[0]: k for k in KIT_MENU}

# the kit each genre plays by default (genres not listed keep their own synthesized kit)
GENRE_KIT = {
    'jungle': 'amen', 'breakcore': 'amen', 'dnb': 'amen', 'liquid_dnb': 'think',
    'boombap': 'funky_drummer', 'downtempo': 'back_to_life', 'hauntology': 'vintage', 'vaporwave': 'vintage', 'lofi': 'vintage',
    'hauntology_sunlit': 'vintage', 'hauntology_dark': 'vintage', 'neo_soul': 'funky_drummer', 'g_funk': '808', 'new_jack_swing': 'linn',
    'alt_rnb': '808', 'rage': '808', 'plugg': '808', 'jazz_rap': 'funky_drummer', 'cloud_rap': '808', 'slow_jam': '808',
    'trap': '808', 'uk_drill': '808', 'luxury_rap': '808', 'orchestral_hiphop': '808', 'reggaeton': '808', 'jersey_club': '808',
    'house': '909', 'tech_house': '909', 'acid_house': '909', 'progressive_house': '909', 'eurodance': '909',
    'techno': 'techno', 'minimal': 'techno', 'melodic_techno': 'techno',
    'trance': 'trance', 'uplifting_trance': 'trance', 'progressive_trance': 'trance', 'psytrance': 'trance',
    'synthwave': 'linn', 'synthpop': 'linn', 'city_pop': 'linn',
    'rock': 'rock', 'indie_rock': 'rock', 'punk': 'rock', 'metal': 'rock', 'symphonic_metal': 'rock', 'jam_band': 'rock',
    'soft_rock': 'studio', 'funk': 'studio', 'disco': 'studio', 'disco_funk': 'studio', 'motown': 'studio', 'gospel': 'studio',
    'blues': 'studio', 'reggae': 'studio', 'ska': 'studio', 'jazz': 'studio', 'swing': 'studio', 'soul_ballad': 'studio',
    'country': 'studio', 'folk': 'studio', 'pop': 'studio', 'modern_country': 'studio', 'country_waltz': 'studio',
    'outlaw_country': 'studio', 'western_swing': 'studio', 'smooth_jazz': 'studio', 'smooth_funk': 'studio', 'quiet_storm': 'studio',
    'rave_hardcore': 'amen', 'braindance': 'think', 'future_funk': '909', 'italo_disco': 'linn', 'new_beat': 'techno',
    'bebop': 'studio', 'modal_jazz': 'studio', 'soul_jazz': 'studio', 'fusion': 'studio',
}
# how much jungle-style chopping a genre does with its break (0 = played straight)
CHOP = {'braindance': 0.75, 'rave_hardcore': 0.3, 'jungle': 0.55, 'breakcore': 0.85, 'dnb': 0.2, 'liquid_dnb': 0.1, 'boombap': 0.08}


def menu():
    return [dict(id=k, group=g, label=l) for k, g, l, _, _, _ in KIT_MENU]


def effective(opts, style, st):
    """The kit id a song uses: yours if you picked one, else the genre's, else None (= the style's own synth preset)."""
    k = getattr(opts, 'kit', None)
    if k:
        return k
    return GENRE_KIT.get(style)


def configure(st, kit_id, style, opts):
    """Set the synth preset, real-kit mic and break for a kit. Returns the synth preset name for KITS."""
    entry = MENU.get(kit_id)
    if not entry:
        return kit_id                                   # a plain synth preset name ('acoustic', 'default' ...)
    _, _, _, preset, mic, brk = entry
    st['kit_id'] = kit_id
    if kit_id == 'linn':
        st['gated_snare'] = True                       # the 80s gated-reverb snare
    if mic:
        st['want_real_kit'] = mic
    if brk:
        b = BREAKS[brk]
        st['break'] = brk
        st['want_real_kit'] = b['mic']
        st['break_pitch'] = b['pitch']
        st['break_chop'] = CHOP.get(style, 0.0) if not getattr(opts, 'kit', None) or style in CHOP else 0.0
        st['swing'] = max(st.get('swing', 0.5), b['swing'])
        st['break_seq'] = b['drums']
    return preset


def install_break(st, tracks_list):
    """Replace the style's drum patterns with the break's (adding the drum tracks it needs)."""
    seq = st.get('break_seq')
    if not seq:
        return
    names = {t['name']: t for t in tracks_list}
    drum_layers = ('kick', 'snare', 'top')
    keep = []
    for t in tracks_list:                                # the break replaces the kit; percussion and melodic parts stay
        if t['layer'] in drum_layers and t['name'] not in seq and t['inst'] in ('kick', 'snare', 'clap', 'chat', 'ohat', 'ride',
                                                                                 'crash', 'rim', 'snap', 'tom'):
            continue
        keep.append(t)
    for d, (layer, inst, db, pan) in BREAK_TRACKS.items():
        if d in seq and d not in names:
            keep.append(dict(name=d, layer=layer, inst=inst, pan=pan, rev=0.12 if layer == 'snare' else 0.0, dly=0.0, sc=0.0,
                             db=db, hp=None, drive=None, p={}))
        elif d in seq:
            names[d]['inst'] = inst
    tracks_list[:] = keep
    st['drums'] = {d: list(p) for d, p in seq.items()}
    st['snare_tracks'] = ['snare']
    st['kick_track'] = 'kick'
    st['trap_hats'] = False
    st['ghosts'] = False


def chop_map(st, bar, rnd, energy, section_bar):
    """Which (bar of the break, beat) each beat of this bar plays: straight, or chopped jungle-style."""
    straight = [(bar % 4, k) for k in range(4)]
    c = float(st.get('break_chop') or 0.0)
    if c <= 0 or section_bar % 8 == 0 or rnd.random() > c * (0.35 + 0.65 * energy):
        return straight
    out = []
    for k in range(4):
        if k == 0 and rnd.random() < 0.6:
            out.append(straight[0])                     # the downbeat usually stays put, so the groove still lands
        else:
            out.append((rnd.randrange(4), rnd.randrange(4)))
    if c > 0.7 and rnd.random() < 0.4:                  # breakcore: stutter one beat
        j = rnd.randrange(1, 4)
        out[j] = out[j - 1]
    return out


def bar_pattern(st, drum, slices):
    seq = st['break_seq'].get(drum)
    if not seq:
        return None
    return ''.join(seq[b][k * 4:(k + 1) * 4] for b, k in slices)


# 1.35: genres that now default to the new real kits
GENRE_KIT.update({k: 'brushes' for k in ('jazz', 'swing', 'bebop', 'modal_jazz', 'bossa_nova', 'soul_ballad', 'quiet_storm',
                                          'country_waltz', 'western_swing')})
GENRE_KIT.update({k: 'seventies' for k in ('funk', 'motown', 'soul_jazz', 'blues', 'reggae', 'disco_funk', 'gospel')})
GENRE_KIT.update({k: 'rusty' for k in ('rock', 'indie_rock', 'punk', 'jam_band')})
