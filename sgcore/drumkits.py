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
        label='Amen-style break', bpm=(136, 176), mic='lofi', pitch=1.5, swing=0.5, orig_bpm=137, bits=12, srate=30000,
        drums={'kick': ['X.X.......XX....', 'X.X.......XX....', 'X.X.......X.....', '..XX......X.....'],
               'snare': ['....X..x.x..X..x', '....X..x.x..X..x', '....X..x.x....X.', '.x..X..x.x....X.'],
               'ride': ['x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.......'],
               'crash': ['................', '................', '................', '..........X.....']}),
    'think': dict(
        label='Think-style break', bpm=(110, 176), mic='lofi', pitch=1.0, swing=0.52, orig_bpm=114, bits=12, srate=32000,
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
BREAKS.update({
    'hot_pants': dict(
        label='Hot Pants-style break', bpm=(100, 176), mic='lofi', pitch=1.0, swing=0.53,
        drums={'kick': ['X.....X...X..X..', 'X.....X.X.X.....', 'X.....X...X..X..', 'X.X...X...X.....'],
               'snare': ['....X..o.o..X.o.', '.o..X..o.o..X...', '....X..o.o..X.o.', '.o..X..o.o..X.oX'],
               'chat': ['x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x...'],
               'ohat': ['...............x', '................', '...............x', '................']}),
    'skull_snaps': dict(
        label='Skull Snaps-style break (big, dry, heavy)', bpm=(84, 176), mic='lofi', pitch=-0.5, swing=0.52,
        drums={'kick': ['X.........X.....', 'X.X.......X.....', 'X.........X..X..', 'X.X.......X.....'],
               'snare': ['....X..o....X...', '....X..o....X..o', '....X..o....X...', '....X..o..o.X...'],
               'chat': ['x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x.x.']}),
})
# drum & bass: modern DnB layers a tight electronic kick and a crisp snare (the classic two-step) over a break that
# plays the ghost notes and hats underneath - the break's own kick is filtered so the layered kick owns the low end.
TWO_STEP = {'lkick': ['X.........X.....', 'X.........X.....', 'X.X.......X.....', 'X.........X..X..', 'X.........X.X...'],
            'lsnare': ['....X.......X...', '....X.......X...', '....X.......X..o']}
BREAK_TRACKS = {'kick': ('kick', 'kick', -13, 0.0), 'snare': ('snare', 'snare', -16, 0.0), 'ride': ('top', 'ride', -26, 0.25),
                'chat': ('top', 'chat', -25, 0.2), 'ohat': ('top', 'ohat', -27, 0.25), 'crash': ('top', 'crash', -26, -0.2),
                'conga': ('top', 'conga', -23, -0.3), 'shaker': ('top', 'shaker', -29, 0.35)}

# ----------------------------------------------------------------------------- the kit menu
# id -> (group, label, synth preset used when nothing else applies, real-kit mic or None, break or None[, extras])
# extras: layer = the synth preset of a layered two-step kick/snare over the break (DnB); snare = a real snare from the
#         Frankensnare library in place of the kit's own; gated = 80s gated-reverb snare
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
    ('hot_pants', 'Breaks (re-played)', BREAKS['hot_pants']['label'] + ' - jungle, DnB, funk', 'acoustic', None, 'hot_pants'),
    ('skull_snaps', 'Breaks (re-played)', BREAKS['skull_snaps']['label'] + ' - hip-hop, DnB', 'acoustic', None, 'skull_snaps'),
    # drum & bass
    ('dnb_rollers', 'Drum & bass', 'Modern DnB: two-step kick + crisp snare over a Think break', 'acoustic', None, 'think',
     dict(layer='dnb', snare='crisp')),
    ('dnb_amen', 'Drum & bass', 'Amen rollers: two-step layered over the Amen', 'acoustic', None, 'amen', dict(layer='dnb', snare='crisp')),
    ('neuro', 'Drum & bass', 'Neurofunk: hard, distorted snare, compressed break', 'acoustic', None, 'hot_pants', dict(layer='neuro')),
    ('liquid', 'Drum & bass', 'Liquid: rounder kick, softer snare, shuffled Think', 'acoustic', None, 'think', dict(layer='liquid')),
    ('jungle_raw', 'Drum & bass', 'Jungle: raw Amen, pitched up, crisp piccolo snare', 'acoustic', None, 'amen', dict(snare='piccolo')),
    ('dnb_machine', 'Drum & bass', 'DnB drum machine (no break): tight & crisp', 'dnb', None, None),
    # more machines
    ('cr78', 'Drum machines', 'CR-78-style rhythm box (soft, vintage)', 'cr78', None, None),
    ('606', 'Drum machines', 'TR-606-style (small, snappy - acid, electro)', '606', None, None),
    ('707', 'Drum machines', 'TR-707-style (punchy 80s digital)', '707', None, None),
    ('dmx', 'Drum machines', 'DMX-style (fat 8-bit 80s hip-hop)', 'dmx', None, None),
    ('phonk808', 'Drum machines', 'Distorted 808 (phonk, crunchy)', 'phonk808', None, None),
    # more real kits
    ('unruly', 'Real kits', 'Modern studio kit (tight, punchy)', 'acoustic', 'unruly', None),
    ('dirty', 'Real kits', 'Dirty kit (saturated kick, trashy snare)', 'acoustic', 'dirty', None),
    ('crisp_kit', 'Real kits', 'Studio kit + crisp steel piccolo snare', 'acoustic', 'studio', None, dict(snare='crisp')),
    ('dead70s', 'Real kits', 'Studio kit + dead muffled 70s snare', 'acoustic', 'studio', None, dict(snare='deadsnare')),
    ('big80s', 'Real kits', 'Big 80s kit (huge snare, gated reverb)', 'acoustic', 'rusty', None, dict(snare='bigsnare', gated=True)),
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
    return [dict(id=e[0], group=e[1], label=e[2]) for e in KIT_MENU]


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
    preset, mic, brk = entry[3], entry[4], entry[5]
    extra = entry[6] if len(entry) > 6 else {}
    st['kit_id'] = kit_id
    if kit_id == 'linn' or extra.get('gated'):
        st['gated_snare'] = True                       # the 80s gated-reverb snare
    if extra.get('snare'):
        st['real_snare'] = extra['snare']
    if extra.get('layer'):
        st['break_layer'] = extra['layer']
    if mic:
        st['want_real_kit'] = mic
    if brk:
        b = BREAKS[brk]
        st['break'] = brk
        st['want_real_kit'] = b['mic']
        st['break_pitch'] = b['pitch']
        st['break_orig_bpm'] = b.get('orig_bpm')         # sped-up record: the pitch rises with the tempo (no time-stretch)
        st['break_sampler'] = (b.get('bits'), b.get('srate'))   # the 12-bit sampler it was chopped on
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
    layer = st.get('break_layer')
    if layer:                                            # DnB: two-step kick + snare on top, the break underneath
        from .instruments import KITS
        from . import samplelibs as sl
        kp = KITS.get(layer, {})
        for t in tracks_list:
            if t['name'] == 'kick':
                t.update(hp=170, db=(t.get('db') or -13) - 4)    # the break's kick: thump filtered out, knock kept
            elif t['name'] == 'snare':
                t.update(db=(t.get('db') or -16) - 3)
            if layer == 'neuro' and t['name'] in seq:            # neuro: the break squashed and driven hard
                t['drive'] = 0.6
        tracks_list += [dict(name='lkick', layer='kick', inst='kick', pan=0.0, rev=0.0, dly=0.0, sc=0.0, db=-11, hp=None,
                             drive=None, p={}, synth=True),
                        dict(name='lsnare', layer='snare', inst='snare', pan=0.0, rev=0.1, dly=0.0, sc=0.0, db=-14, hp=None,
                             drive=None, p={}, synth=not (st.get('real_snare') and sl.installed('snares')))]
        st['drums'].update({k: list(v) for k, v in TWO_STEP.items()})
        st['drum_voice'] = dict(st.get('drum_voice') or {}, lkick=dict(kp.get('kick', {})), lsnare=dict(kp.get('snare', {})))
        st['kick_track'] = 'lkick'
        st['snare_tracks'] = ['lsnare', 'snare']


def _slice_roles(seq):
    """For each (bar, beat) slice of the break: does it open on the backbeat snare, on a kick, or neither."""
    roles = {}
    for bar in range(4):
        for k in range(4):
            sn = (seq.get('snare') or ['.' * 16] * 4)[bar][k * 4]
            kk = (seq.get('kick') or ['.' * 16] * 4)[bar][k * 4]
            roles[(bar, k)] = 'snare' if sn in 'Xx' else ('kick' if kk in 'Xx' else 'other')
    return roles


# classic re-arrangements of the four bars (bar, beat) - the edits jungle producers kept coming back to
EDITS = [
    [(0, 0), (0, 1), (2, 2), (3, 3)],        # the bar, with the crash-bar's tail
    [(0, 0), (0, 1), (0, 0), (0, 3)],        # kick-kick restart on beat 3
    [(3, 0), (0, 1), (1, 2), (2, 3)],        # starts on the 'skipping' last bar
    [(0, 0), (2, 3), (1, 2), (0, 1)],        # snare-heavy, backwards half
    [(0, 0), (0, 1), (1, 0), (2, 1)],        # two-step-ish: kick, snare, kick, snare
    [(2, 0), (2, 1), (0, 2), (3, 1)],
]


def chop_map(st, bar, rnd, energy, section_bar):
    """Which (bar of the break, beat) each beat of this bar plays: straight, or chopped jungle-style. Chops keep the
    backbeat: a slice that opens on the snare lands on beats 2 and 4, kick slices on 1 and 3 - so the edit still
    grooves instead of tripping over itself."""
    straight = [(bar % 4, k) for k in range(4)]
    c = float(st.get('break_chop') or 0.0)
    if c <= 0 or section_bar % 8 == 0 or rnd.random() > c * (0.35 + 0.65 * energy):
        return straight
    if rnd.random() < 0.45:
        return list(rnd.choice(EDITS))
    roles = st.get('_break_roles') or _slice_roles(st['break_seq'])
    st['_break_roles'] = roles
    snares = [sl for sl, r in roles.items() if r == 'snare']
    others = [sl for sl, r in roles.items() if r != 'snare']
    out = []
    for k in range(4):
        if k == 0 and rnd.random() < 0.7:
            out.append(straight[0])                     # the downbeat usually stays put, so the groove still lands
        elif rnd.random() < 0.35:
            out.append(straight[k])
        else:
            out.append(rnd.choice(snares if k % 2 == 1 and snares else others or snares))
    if c > 0.7 and rnd.random() < 0.4:                  # breakcore: stutter one beat
        j = rnd.randrange(1, 4)
        out[j] = out[j - 1]
    return out


def break_edits(st, rnd, energy, section_bar, nbars):
    """Phrase-end edits on a chopped break (jungle / breakcore / DnB): None, or (from_beat, [(beat, drum, vel, mod)])
    to replace the last beat(s) of this bar. Snare rushes rising in pitch, a reversed snare into the downbeat, a
    stuttered ghost-note roll."""
    c = float(st.get('break_chop') or 0.0)
    end_of_phrase = section_bar % 4 == 3 or section_bar == nbars - 1
    if c <= 0 or not end_of_phrase or rnd.random() > 0.1 + c * 0.8 * (0.4 + 0.6 * energy):
        return None
    kind = rnd.choice(['rush', 'rush', 'reverse', 'stutter', 'pitchdown'] + (['rush32'] if c > 0.4 else []))
    if kind == 'reverse':
        return 3.0, [(3.0, 'kick', 0.85, None), (3.5, 'snare', 0.5, 'cut'), (3.98, 'snare', 0.9, 'rev')]   # swells into the next downbeat
    if kind == 'stutter':
        return 3.0, [(3.0 + k / 4, 'snare', 0.45 + 0.1 * k, 'cut') for k in range(4)]
    if kind == 'pitchdown':
        return 2.0, [(2.0 + k / 2, 'snare', 0.9 - 0.08 * k, 'pt:%d' % (-2 * k)) for k in range(4)]
    if kind == 'rush32':
        return 3.0, [(3.0 + k / 8, 'snare', 0.4 + 0.07 * k, 'pt:%d' % k) for k in range(8)]
    return 2.0, [(2.0 + k / 4, 'snare', 0.4 + 0.06 * k, 'pt:%d' % (k // 2)) for k in range(8)]


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


# 1.38: drum & bass kits, more machines and real kits
GENRE_KIT.update({'dnb': 'dnb_rollers', 'liquid_dnb': 'liquid', 'neurofunk': 'neuro', 'jungle': 'jungle_raw',
                  'jazz_rap': 'skull_snaps', 'phonk': 'phonk808', 'memphis_phonk': 'phonk808', 'brazilian_phonk': 'phonk808',
                  'acid_house': '606', 'pop': 'unruly', 'modern_country': 'unruly', 'soft_rock': 'dead70s'})
CHOP.update({'jungle': 0.55, 'dnb': 0.15, 'neurofunk': 0.1, 'liquid_dnb': 0.08})
GENRE_KIT.update({'hopecore': 'amen', 'alt_rock_90s': 'rock', 'bedroom_pop': '707',
                  'electro_funk': 'dmx', 'ps1_game': 'think', 'nineties_club_house': '909', 'sunny_melodic_house': '909'})
CHOP.update({'hopecore': 0.45, 'ps1_game': 0.12})
GENRE_KIT.update({'swing_tomtom': 'studio', 'big_band_50s': 'studio'})
GENRE_KIT.update({k: 'vintage' for k in ('hauntology_melody', 'hauntology_campfire', 'hauntology_cold')})


# 1.39: funky breaks / glitch electro - a chopped Think break with jungle-style edits
GENRE_KIT.update({'funky_breaks': 'think'})
CHOP.update({'funky_breaks': 0.35})

# 1.41: kits for the genres that had none (each picks the recorded / machine kit its records were made with)
GENRE_KIT.update({'holiday': 'brushes', 'western': 'vintage', 'chamber_pop': 'studio', 'jam_rock_80s': 'big80s',
                  'lofi_rock': 'rusty', 'sophisti_pop': 'big80s', 'folk_jam': 'brushes', 'psych_pop': 'dead70s',
                  'boogie_rock': 'rock', 'spooky_surf': 'vintage', 'surf_rock': 'vintage', 'monster_theme': 'vintage', 'nu_metal': 'rock', 'soul_sample_rap': 'vintage',
                  'new_age_chant': 'funky_drummer', 'midfi_synthfunk': 'linn', 'uk_bass_130': 'techno', 'hard_trance': 'trance',
                  'nu_disco': '909', 'piano_house_90s': '909', 'tokyo_deep_house': '909', 'smooth_90s_rap': '808',
                  'bay_rap': '808', 'futuristic_bounce': '808', 'hard_trap': '808', 'switch_trap': '808', 'club_pop': '707',
                  'garage_house': 'punchy', 'future_garage': 'vintage', 'grime': 'punchy'})
GENRE_KIT.update({'funk_150': '808'})
GENRE_KIT.setdefault('new_jack_swing', 'linn')       # SP-1200 / drum-machine era, gated snare
GENRE_KIT.update({'jump_up': 'dnb_amen', 'dark_synthwave': 'linn'})
