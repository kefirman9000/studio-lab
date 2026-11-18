"""The drummer and the percussionist: how the drums are played, separately from what beat and which kit.

Three independent drum choices now exist:
  drum style   (opts.drum_pattern)  the beat itself - see drumkits.pattern_of / compose.borrow_drums
  drum sounds  (opts.kit)           the kit - see drumkits.configure
  drummer      (this module)        fills, ghost notes and hi-hat busyness on top of whatever beat plays
and the percussion (congas, shakers, tambourine, iron ...) can be picked on its own, or switched off, whatever the genre.
"""

# hand percussion that rides on top of the kit (the kit's own hats, ride and crash are not percussion)
PERC_INSTS = {'conga', 'shaker', 'tamb', 'woodblock', 'cowbell808', 'timbale', 'sleigh'}

# id -> (menu label, {track name: (inst, dB, pan, [patterns, 16 steps])}, needs a real campana)
PERC_SETS = {
    'shakers': ('Shakers (16ths, house / pop)', {
        'pc_shaker': ('shaker', -29, 0.35, ['x.xxx.xxx.xxx.xx', 'xoxoxoxoxoxoxoxo'])}, False),
    'tambourine': ('Tambourine (backbeat, soul / Motown / rock)', {
        'pc_tamb': ('tamb', -28, 0.3, ['....x.......x...', '..x.x.x...x.x.x.'])}, False),
    'disco': ('Disco (offbeat tambourine + congas)', {
        'pc_tamb': ('tamb', -29, 0.3, ['..x...x...x...x.']),
        'pc_conga': ('conga', -27, -0.3, ['..o.x..o..o.x..o', 'x..o..x...o.x..o'])}, False),
    'latin': ('Latin (conga tumbao, bongos, guiro, campana)', {
        'pc_conga': ('conga', -24, 0.3, ['..o.x..o..o.x..o', 'x.o.x.ox..o.x.o.']),
        'pc_bongo': ('conga', -27, -0.35, ['x.xxx.xxx.xxx.xx']),
        'pc_guiro': ('shaker', -28, 0.35, ['x..xx..xx..xx..x']),
        'pc_bell': ('cowbell808', -31, -0.2, ['x...x...x...x...', 'x...x.x.x...x.x.'])}, True),
    'afro': ('Afro (shaker, congas, bell pattern)', {
        'pc_shaker': ('shaker', -28, 0.3, ['x.xxx.xxx.xxx.xx']),
        'pc_conga': ('conga', -24, -0.25, ['..o.x..o..o.x.o.', 'x..o..x.o..x..o.']),
        'pc_bell': ('woodblock', -29, 0.2, ['..x.....x.x.....', 'x.x.x..x.x.x.x..'])}, False),
    'caribbean': ('Caribbean (iron on the offbeats, congas)', {
        'pc_iron': ('cowbell808', -28, 0.25, ['..x...x...x...x.', 'x.x.x.x.x.x.x.x.']),
        'pc_conga': ('conga', -27, -0.3, ['..o.x..o..o.x..o']),
        'pc_tamb': ('tamb', -31, 0.3, ['....x.......x...'])}, True),
    'woodblocks': ('Woodblocks & rim (sparse, organic)', {
        'pc_block': ('woodblock', -28, 0.25, ['..x.......x..x..', '......x.......x.'])}, False),
}

DRUMMER_MENU = {
    'fills': [('', 'Genre'), ('none', 'No fills'), ('fewer', 'Fewer (section ends only)'), ('more', 'More (every 4 bars)')],
    'ghosts': [('', 'Genre'), ('off', 'Off (clean)'), ('more', 'More ghost notes')],
    'hats': [('', 'Genre'), ('sparse', 'Sparse (8ths, no extras)'), ('busy', 'Busy (16th fill-ins)')],
}


def perc_menu():
    return [dict(id=k, label=v[0]) for k, v in PERC_SETS.items()]


def apply_percussion(st, opts):
    """opts.percussion: None = the genre's own, 'off' = none, or a set from PERC_SETS (replaces the genre's)."""
    pick = getattr(opts, 'percussion', None)
    if not pick or pick == 'genre':
        return
    if pick != 'off' and pick not in PERC_SETS:
        return
    drop = {t['name'] for t in st['tracks'] if t['layer'] == 'top' and t['inst'] in PERC_INSTS and not t.get('user_pick')}
    st['tracks'] = [t for t in st['tracks'] if t['name'] not in drop]
    st['drums'] = {k: v for k, v in st['drums'].items() if k not in drop}
    if pick == 'off' or st.get('meter'):                 # the sets are 16-step 4/4 patterns
        return
    label, parts, campana = PERC_SETS[pick]
    for name, (inst, db, pan, pats) in parts.items():
        st['tracks'].append(dict(name=name, layer='top', inst=inst, pan=pan, rev=0.04, dly=0.0, sc=0.0, db=db, hp=None,
                                 drive=None, p={}))
        st['drums'][name] = list(pats)
    if campana:
        st['real_cowbell'] = True                       # a real campana / iron, not an 808 cowbell
    st['percussion'] = pick


def fill_ok(opts, st, b, nbars, energy, S, rnd):
    """Should this bar end with a snare fill?"""
    mode = getattr(opts, 'drum_fills', None) or ''
    if mode == 'none':
        return False
    if mode == 'more':
        return b % 4 == 3 and rnd.random() < 0.85 * (1 - 0.5 * S)
    if mode == 'fewer':
        return b == nbars - 1 and rnd.random() < 0.6 * (1 - S)
    return bool(st.get('fill') or energy > 0.6) and b % 8 == 7 and rnd.random() < (0.4 + 0.5 * energy) * (1 - S)


def ghost_rate(opts, st, energy):
    """Chance per free 16th of a soft ghost snare (0 = none)."""
    mode = getattr(opts, 'drum_ghosts', None) or ''
    if mode == 'off':
        return 0.0
    if mode == 'more':
        return 0.16 + 0.16 * energy
    return (0.06 + 0.12 * energy) if st.get('ghosts') else 0.0


HAT_NAMES = ('chat', 'shaker', 'ohat', 'ride')


def hat_hits(opts, dname, hits):
    """Thin a hi-hat / shaker / ride pattern to 8ths when the drummer plays sparse."""
    if (getattr(opts, 'hat_density', None) or '') != 'sparse' or dname not in HAT_NAMES:
        return hits
    return [h for h in hits if h[0] % 2 == 0]


def hat_extra(opts, dname, energy):
    """Chance per free 16th of a soft extra hat / shaker hit."""
    mode = getattr(opts, 'hat_density', None) or ''
    if dname not in ('chat', 'shaker', 'pc_shaker'):
        return 0.0
    if mode == 'sparse':
        return 0.0
    if mode == 'busy':
        return 0.45 + 0.3 * energy
    return (energy - 0.7) * 1.6 if energy > 0.7 else 0.0


# ----------------------------------------------------------------------------- what kind of beat each genre plays
def beat_feel(style):
    """A short label for a genre's beat, read from its own patterns: four-on-the-floor, half-time, two-step,
    breakbeat, shuffle, backbeat, dembow / syncopated, or the meter (3/4, 6/8, 12/8)."""
    from .styles import STYLES
    from . import drumkits
    st = STYLES[style]
    if st.get('meter') and st['meter'] != '4/4':
        return st['meter']
    dr = st.get('drums') or {}
    if not dr:
        return 'no drums'
    if (drumkits.MENU.get(drumkits.GENRE_KIT.get(style)) or (None,) * 6)[5]:
        return 'breakbeat'
    kick = (dr.get(st.get('kick_track', 'kick')) or dr.get('kick') or [''])[0]
    sn = (dr.get((st.get('snare_tracks') or ['snare'])[0]) or dr.get('snare') or dr.get('clap') or [''])[0]
    k = {i for i, c in enumerate(kick) if c in 'Xx'}
    s_ = {i for i, c in enumerate(sn) if c in 'Xx'}
    if {3, 6} <= s_ and 4 not in s_:
        return 'dembow / clave'
    if {0, 4, 8, 12} <= k:
        return 'four-on-the-floor'
    if s_ and s_ <= {8, 9, 10, 11} and 4 not in s_:
        return 'half-time'
    if st.get('swing', 0.5) >= 0.6:
        return 'swing / shuffle'
    if 0 in k and 10 in k and {4, 12} <= s_ and len(k) <= 3:
        return 'two-step'
    if {4, 12} <= s_:
        return 'backbeat'
    return 'syncopated'
