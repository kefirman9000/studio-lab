"""Style library. Each style is a recipe: tempo, harmony, groove, arrangement, instruments, mix and master."""

ALL = {'kick', 'snare', 'top', 'bass', 'chords', 'pad', 'arp', 'lead', 'fx'}


def T(name, layer, inst, **kw):
    d = dict(name=name, layer=layer, inst=inst, pan=0.0, rev=0.0, dly=0.0, sc=0.0, db=None, hp=None, drive=None, p={})
    d.update(kw)
    return d


# ----------------------------------------------------------------------------- arrangement templates
EDM_FORM = [
    ('intro', 8, {'kick', 'top', 'chords', 'pad'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'arp'}, {'crash': True}),
    ('build', 8, {'chords', 'arp', 'top', 'pad'}, {'build': True}),
    ('drop', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'lead', 'arp', 'pad'}, {'drop': True}),
    ('break', 8, {'pad', 'lead', 'chords'}, {'alt': True, 'crash': True}),
    ('build', 8, {'chords', 'arp', 'top', 'lead'}, {'build': True, 'alt': True}),
    ('drop', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'lead', 'arp', 'pad'}, {'drop': True}),
    ('outro', 8, {'kick', 'top', 'chords', 'pad'}, {'fade': True, 'crash': True}),
]
HALFTIME_FORM = [
    ('intro', 8, {'chords', 'pad', 'top'}, {'filter_in': True}),
    ('build', 8, {'chords', 'pad', 'arp', 'top'}, {'build': True}),
    ('drop', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'drop': True}),
    ('break', 8, {'pad', 'chords', 'lead', 'arp'}, {'alt': True}),
    ('build', 8, {'chords', 'arp', 'top', 'lead'}, {'build': True, 'alt': True}),
    ('drop', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad', 'arp'}, {'drop': True}),
    ('outro', 8, {'chords', 'pad'}, {'fade': True}),
]
TRAP_FORM = [
    ('intro', 8, {'chords', 'pad'}, {'filter_in': True}),
    ('hook', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'drop': True}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'chords'}, {'crash': True}),
    ('hook', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'crash': True}),
    ('bridge', 8, {'chords', 'pad', 'lead'}, {'alt': True}),
    ('hook', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'drop': True}),
    ('outro', 8, {'chords', 'pad'}, {'fade': True}),
]
LOFI_FORM = [
    ('intro', 4, {'chords', 'fx'}, {'filter_in': True}),
    ('A', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'fx'}, {}),
    ('B', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'fx'}, {}),
    ('C', 8, {'chords', 'lead', 'bass', 'fx'}, {'alt': True}),
    ('A', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'fx'}, {}),
    ('outro', 4, {'chords', 'fx'}, {'fade': True}),
]
AMBIENT_FORM = [
    ('intro', 8, {'pad', 'fx'}, {'filter_in': True}),
    ('A', 16, {'pad', 'arp', 'bass', 'fx'}, {}),
    ('B', 16, {'pad', 'lead', 'arp', 'bass', 'fx', 'top'}, {}),
    ('C', 16, {'pad', 'lead', 'chords', 'bass', 'fx'}, {'alt': True}),
    ('outro', 8, {'pad', 'fx'}, {'fade': True}),
]
CHIP_FORM = [
    ('intro', 4, {'arp', 'bass'}, {}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'arp'}, {}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'arp', 'lead'}, {}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'arp'}, {}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'arp', 'lead'}, {}),
    ('bridge', 8, {'bass', 'arp', 'lead', 'top'}, {'alt': True}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'arp', 'lead'}, {}),
    ('outro', 4, {'arp', 'bass', 'kick'}, {'fade': True}),
]
SONG_FORM = [
    ('intro', 4, {'chords', 'top'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'chords'}, {}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'crash': True}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'arp'}, {'crash': True}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad', 'arp'}, {'crash': True}),
    ('bridge', 8, {'chords', 'pad', 'lead', 'bass'}, {'alt': True}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad', 'arp'}, {'crash': True}),
    ('outro', 8, {'chords', 'pad', 'top'}, {'fade': True}),
]
JAZZ_FORM = [
    ('intro', 4, {'chords', 'bass', 'top'}, {}),
    ('head', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead'}, {}),
    ('solo', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead'}, {'alt': True}),
    ('solo', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'arp'}, {}),
    ('head', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead'}, {}),
    ('outro', 4, {'chords', 'bass', 'top'}, {'fade': True}),
]
CINEMATIC_FORM = [
    ('intro', 8, {'pad', 'fx', 'chords'}, {'filter_in': True}),
    ('rise', 8, {'pad', 'arp', 'bass', 'chords', 'kick'}, {}),
    ('theme', 16, {'pad', 'arp', 'bass', 'chords', 'lead', 'kick', 'snare'}, {'drop': True}),
    ('calm', 8, {'pad', 'chords', 'lead'}, {'alt': True}),
    ('build', 8, {'pad', 'arp', 'bass', 'kick', 'chords'}, {'build': True}),
    ('climax', 16, ALL, {'drop': True}),
    ('outro', 8, {'pad', 'chords', 'fx'}, {'fade': True}),
]
ORCH_FORM = [
    ('intro', 4, {'pad', 'chords'}, {'filter_in': True}),
    ('A', 16, {'pad', 'chords', 'bass', 'lead'}, {}),
    ('B', 16, {'pad', 'chords', 'bass', 'arp', 'lead'}, {'alt': True}),
    ('A', 16, {'pad', 'chords', 'bass', 'lead', 'arp', 'kick'}, {}),
    ('outro', 8, {'pad', 'chords', 'bass'}, {'fade': True}),
]

EDM_FORM_B = [  # early drop
    ('intro', 8, {'kick', 'top', 'chords'}, {'filter_in': True}),
    ('build', 8, {'chords', 'arp', 'top', 'pad'}, {'build': True}),
    ('drop', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'lead', 'arp', 'pad'}, {'drop': True}),
    ('verse', 16, {'kick', 'top', 'snare', 'bass', 'chords'}, {'crash': True}),
    ('break', 8, {'pad', 'lead', 'arp'}, {'alt': True}),
    ('build', 8, {'chords', 'arp', 'top', 'lead'}, {'build': True, 'alt': True}),
    ('drop', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'lead', 'arp', 'pad'}, {'drop': True}),
    ('outro', 8, {'kick', 'top', 'pad'}, {'fade': True}),
]
EDM_FORM_C = [  # long-form club arrangement with a post-drop
    ('intro', 16, {'kick', 'top'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'top', 'snare', 'bass', 'arp'}, {'crash': True}),
    ('build', 8, {'chords', 'arp', 'top'}, {'build': True}),
    ('drop', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'lead', 'pad'}, {'drop': True}),
    ('break', 16, {'pad', 'chords', 'lead'}, {'alt': True, 'crash': True}),
    ('build', 8, {'chords', 'arp', 'top', 'pad'}, {'build': True}),
    ('drop', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'lead', 'arp', 'pad'}, {'drop': True}),
    ('verse', 8, {'kick', 'top', 'snare', 'bass', 'arp'}, {}),
    ('outro', 8, {'kick', 'top'}, {'fade': True}),
]
SONG_FORM_B = [  # with pre-choruses and a double final chorus
    ('intro', 8, {'chords', 'pad'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'chords'}, {}),
    ('pre', 4, {'snare', 'top', 'bass', 'chords', 'pad'}, {'build': True}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'crash': True}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'arp'}, {}),
    ('pre', 4, {'snare', 'top', 'bass', 'chords', 'pad'}, {'build': True}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad', 'arp'}, {'crash': True}),
    ('bridge', 8, {'chords', 'pad', 'arp'}, {'alt': True}),
    ('chorus', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad', 'arp'}, {'crash': True}),
    ('outro', 8, {'chords', 'pad'}, {'fade': True}),
]
HALFTIME_FORM_B = [
    ('intro', 8, {'chords', 'pad'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'chords'}, {}),
    ('build', 8, {'chords', 'pad', 'arp', 'top'}, {'build': True}),
    ('drop', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'drop': True}),
    ('break', 8, {'pad', 'lead'}, {'alt': True}),
    ('drop', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'arp'}, {'drop': True}),
    ('outro', 8, {'chords', 'pad'}, {'fade': True}),
]
GROOVE_FORM = [  # DJ-style: parts enter one by one, a long filtered breakdown, no snare-roll build
    ('intro', 16, {'kick', 'top'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'top', 'snare', 'bass'}, {}),
    ('verse', 16, {'kick', 'top', 'snare', 'bass', 'arp'}, {'crash': True}),
    ('break', 16, {'top', 'pad', 'chords', 'arp'}, {'build': True}),
    ('drop', 32, {'kick', 'top', 'snare', 'bass', 'chords', 'arp', 'lead'}, {'drop': True}),
    ('outro', 16, {'kick', 'top', 'bass'}, {'fade': True}),
]
DNB_FORM = [  # bar counts (except build-ups) are doubled at drum & bass tempos
    ('intro', 8, {'top', 'pad', 'chords'}, {'filter_in': True}),
    ('build', 8, {'top', 'snare', 'pad', 'chords', 'arp'}, {'build': True}),
    ('drop', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'drop': True}),
    ('break', 8, {'pad', 'chords', 'lead', 'top'}, {'alt': True, 'crash': True}),
    ('build', 8, {'top', 'snare', 'chords', 'arp'}, {'build': True, 'alt': True}),
    ('drop', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'arp'}, {'drop': True}),
    ('outro', 8, {'kick', 'snare', 'top', 'bass'}, {'fade': True}),
]
AMAPIANO_FORM = [
    ('intro', 16, {'top', 'chords', 'pad'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'top', 'snare', 'chords', 'pad'}, {}),
    ('drop', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'pad', 'lead'}, {'drop': True}),
    ('break', 8, {'top', 'chords', 'pad'}, {'build': True}),
    ('drop', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'pad', 'lead', 'arp'}, {'drop': True}),
    ('verse', 16, {'kick', 'top', 'bass', 'chords', 'arp'}, {}),
    ('outro', 16, {'kick', 'top', 'chords'}, {'fade': True}),
]
GARAGE_FORM = [
    ('intro', 8, {'top', 'chords', 'pad'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'chords'}, {}),
    ('hook', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad'}, {'crash': True}),
    ('verse', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'arp'}, {}),
    ('break', 4, {'top', 'chords'}, {'build': True}),
    ('hook', 16, {'kick', 'snare', 'top', 'bass', 'chords', 'lead', 'pad', 'arp'}, {'drop': True}),
    ('outro', 8, {'kick', 'snare', 'top', 'chords'}, {'fade': True}),
]
FORM_VARIANTS = {'edm': ['edm_b', 'edm_c'], 'song': ['song_b'], 'halftime': ['halftime_b'], 'trap': ['halftime_b']}

FORMS = {'groove': GROOVE_FORM, 'dnb': DNB_FORM, 'amapiano': AMAPIANO_FORM, 'garage': GARAGE_FORM, 'edm_b': EDM_FORM_B, 'edm_c': EDM_FORM_C, 'song_b': SONG_FORM_B, 'halftime_b': HALFTIME_FORM_B, 'edm': EDM_FORM, 'halftime': HALFTIME_FORM, 'trap': TRAP_FORM, 'lofi': LOFI_FORM, 'ambient': AMBIENT_FORM,
         'chip': CHIP_FORM, 'song': SONG_FORM, 'jazz': JAZZ_FORM, 'cinematic': CINEMATIC_FORM, 'orchestral': ORCH_FORM}

FOUR = 'X...X...X...X...'
BACKBEAT = '....X.......X...'
HALF = '........X.......'
OFFHAT = '..x...x...x...x.'

# ----------------------------------------------------------------------------- styles
STYLES = {}


def style(name, category, desc, **kw):
    s = dict(name=name, category=category, desc=desc, swing=0.5, swing_unit=16, human=0.0, chord_bars=1, chord_size=3,
             form='edm', sc_depth=0.0, sc_release=0.45, reverb=2.0, delay_beats=0.75, kit='default', kit_override={},
             drums={}, snare_tracks=[], bass=['R.......R.......'], bass_mode='pattern', bass_lo=31, bass_gate=0.92,
             chord_rh=['x---------------'], chord_center=62, strum=0.0, voicing='close',
             arp=dict(rate=2, mode='up', oct=5), lead_oct=5, fill=False, ghosts=False, trap_hats=False,
             kick_track='kick', tracks=[], master=dict(lufs=-10.0, air=1.5, low=1.0), form_scale=1,
             gm_hint='', suggest='')
    s.update(kw)
    STYLES[name] = s


# ============================== ELECTRONIC ==================================

style('house', 'Electronic', 'Classic/deep house: four-on-the-floor, offbeat bass, chord stabs, pumping sidechain',
      bpm=(120, 126), scales=['minor', 'dorian'], swing=0.55, human=0.002,
      progs={'minor': [[0, 5, 2, 6], [0, 3, 4, 3], [0, 6, 5, 6], [5, 3, 0, 4]],
             'dorian': [[0, 3, 0, 3], [0, 3, 6, 4], [0, 6, 2, 3]]}, chord_size=4,
      sc_depth=0.75, sc_release=0.45, reverb=1.8, kit='909',
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['.o.o.o.o.o.o.o.o', 'oooooooooooooooo'],
             'shaker': ['o.o.o.o.o.o.o.o.']}, snare_tracks=['clap'],
      bass=['..R...R...R...R.', '..R..R..O.R...R.', '..R...R-..R...O.'],
      chord_rh=['..x...x.x...x..x', '...x..x....x..x.', 'x..x..x...x..x..'], chord_center=64,
      arp=dict(rate=2, mode='updown', oct=5),
      lead_rh=['x.x.x-..x-x.x-..', 'x-..x.x-..x.x-..', '..x.x..x..x.x...', 'x--.x--.x-x-x---'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.18),
              T('ohat', 'top', 'ohat', pan=0.15), T('chat', 'top', 'chat', pan=-0.2, db=-29),
              T('shaker', 'top', 'shaker', pan=0.35, db=-31),
              T('bass', 'bass', 'sawbass', sc=1.0, p=dict(cut=1800)),
              T('chords', 'chords', 'stab', sc=0.9, rev=0.25, dly=0.15, p=dict(cut=4500)),
              T('pad', 'pad', 'supersaw', sc=1.0, rev=0.35, p=dict(cut=2200, a=0.3)),
              T('arp', 'arp', 'pluck_saw', sc=0.8, rev=0.25, dly=0.3, pan=-0.25, db=-27),
              T('lead', 'lead', 'pluck', sc=0.5, rev=0.3, dly=0.3, pan=0.1, p=dict(bright=7000, damp=0.997))],
      master=dict(lufs=-9.0, air=2.0, low=1.0))

style('deep_house', 'Electronic', 'Deep house: warm organ & Rhodes 7th chords, round sub, shuffled shakers',
      bpm=(118, 123), scales=['dorian', 'minor'], swing=0.57, human=0.004,
      progs={'dorian': [[0, 3, 0, 3], [0, 3, 6, 4], [0, 6, 3, 0]], 'minor': [[0, 3, 6, 5], [0, 5, 3, 4]]}, chord_size=4,
      sc_depth=0.55, sc_release=0.5, reverb=2.2, kit='soft',
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'rim': ['......o.....o..o', '...o......o.....'], 'ohat': [OFFHAT],
             'shaker': ['oxoxoxoxoxoxoxox']}, snare_tracks=['clap'],
      bass=['R.....R...R..O..', '..R.....R.R...R.', 'R-....R-..R-..A.'], bass_lo=31,
      chord_rh=['x--.......x--...', '...x--......x-..', 'x-.x--....x-....'], chord_center=62,
      arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x-.x-.x---......', '..x-x-..x-x-....', 'x-------x-.x----', '....x-x-x-------'],
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.25, db=-21), T('rim', 'top', 'rim', pan=0.3, db=-30),
              T('ohat', 'top', 'ohat', pan=-0.15, db=-28), T('shaker', 'top', 'shaker', pan=0.25, db=-30),
              T('bass', 'bass', 'sinebass', sc=0.8, p=dict(cut=500)),
              T('chords', 'chords', 'organ', sc=0.7, rev=0.3, dly=0.15),
              T('pad', 'pad', 'warmpad', sc=0.8, rev=0.4, p=dict(cut=1200)),
              T('arp', 'arp', 'epiano', sc=0.5, rev=0.3, dly=0.3, pan=0.2, db=-27),
              T('lead', 'lead', 'vox', sc=0.4, rev=0.35, dly=0.3)],
      master=dict(lufs=-10.0, air=1.0, low=1.5))

style('tech_house', 'Electronic', 'Tech house: rolling groovy bass, shakers & congas, sparse vocal chops',
      bpm=(124, 128), scales=['minor', 'dorian'], swing=0.56,
      progs=[[0, 0, 0, 0], [0, 0, 5, 6], [0, 3, 0, 3]], chord_size=3,
      sc_depth=0.65, sc_release=0.4, reverb=1.6, kit='punchy',
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'shaker': ['oxoxoxoxoxoxoxox'],
             'conga': ['..o..x.....o.x..', '.....x..o.....x.'], 'rim': ['...o.......o..o.']}, snare_tracks=['clap'],
      bass=['..RR..R...RO..R.', '..R.R..R..R..RO.', '.RR..R.R.RR..R..'], bass_gate=0.55, bass_lo=31,
      chord_rh=['......x.........', '...x......x.....'], chord_center=64,
      arp=dict(rate=1, mode='random', oct=5, prob=0.5),
      lead_rh=['x.x.....x.x.....', '..x.x.....x.x...', 'x...x.x.........', 'x.x.x...........'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.2), T('ohat', 'top', 'ohat', db=-27),
              T('shaker', 'top', 'shaker', pan=0.3, db=-29), T('conga', 'top', 'conga', pan=-0.3, db=-27),
              T('rim', 'top', 'rim', pan=0.2, db=-30),
              T('bass', 'bass', 'fmbass', sc=1.0, p=dict(index=2.0, cut=1600, drive=2.0)),
              T('chords', 'chords', 'organ', sc=0.8, rev=0.3, dly=0.3, db=-24),
              T('arp', 'arp', 'pluck_saw', sc=0.6, dly=0.35, pan=0.25, db=-29, p=dict(cut=3000)),
              T('lead', 'lead', 'vox', sc=0.5, rev=0.3, dly=0.35)],
      master=dict(lufs=-8.5, air=1.5, low=1.5))

style('progressive_house', 'Electronic', 'Progressive house: emotive plucks, wide supersaws, long builds and big drops',
      bpm=(124, 128), scales=['minor'], progs=[[0, 5, 2, 6], [5, 3, 0, 4], [0, 6, 5, 3]], chord_size=3,
      sc_depth=0.8, sc_release=0.5, reverb=2.6, kit='punchy',
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.x.x.x.x.x.x.x.'], 'ride': ['..o...o...o...o.']},
      snare_tracks=['clap'], bass=['..R...R...R...R.', '..RO..RO..RO..RO'], bass_gate=0.6,
      chord_rh=['x---------------'], chord_center=64, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x.x.x.x.x.x.x...', 'x-x-x-..x-x-x-x-', 'x.x.x...x.x.x...', 'x---x---x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.3), T('ohat', 'top', 'ohat', db=-27),
              T('chat', 'top', 'chat', pan=-0.2, db=-30), T('ride', 'top', 'ride', pan=0.3, db=-32),
              T('bass', 'bass', 'sawbass', sc=1.0, p=dict(cut=1500)),
              T('chords', 'chords', 'supersaw', sc=1.0, rev=0.35, p=dict(cut=3500, a=0.05)),
              T('pad', 'pad', 'warmpad', sc=1.0, rev=0.45),
              T('arp', 'arp', 'pluck_saw', sc=0.9, rev=0.3, dly=0.35, pan=-0.2, db=-25),
              T('lead', 'lead', 'supersaw_lead', sc=0.7, rev=0.35, dly=0.25)],
      master=dict(lufs=-8.5, air=2.0, low=1.0))

style('trance', 'Electronic', 'Uplifting trance: gated supersaw chords, rolling offbeat bass, euphoric leads',
      bpm=(136, 140), scales=['minor'], progs=[[0, 5, 2, 6], [5, 6, 0, 0], [0, 6, 5, 6], [5, 3, 0, 4]], chord_size=3,
      sc_depth=0.7, sc_release=0.4, reverb=3.0, kit='909',
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['oxoxoxoxoxoxoxox'], 'ride': ['..x...x...x...x.']},
      snare_tracks=['clap'], bass=['..RR..RR..RR..RR', '.RRR.RRR.RRR.RRR'], bass_gate=0.55,
      chord_rh=['xx.xx.xx.x.xx.x.', 'x.xx.xx.x.xx.xx.', 'x-x-x-x-x-x-x-x-'], chord_center=66,
      arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x-x-x-x-x-x-x---', 'x--x--x-x--x--x-', 'x---x---x-x-x---', 'x-------x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.3), T('ohat', 'top', 'ohat', db=-26),
              T('chat', 'top', 'chat', pan=-0.2, db=-30), T('ride', 'top', 'ride', pan=0.25, db=-31),
              T('bass', 'bass', 'sawbass', sc=1.0, p=dict(cut=1400, d=0.08, s=0.3)),
              T('chords', 'chords', 'supersaw', sc=0.9, rev=0.35, dly=0.15, p=dict(cut=5000, a=0.005, r=0.08)),
              T('pad', 'pad', 'strings', sc=0.8, rev=0.5),
              T('arp', 'arp', 'pluck_saw', sc=0.8, rev=0.3, dly=0.4, pan=0.25, db=-26),
              T('lead', 'lead', 'supersaw_lead', sc=0.5, rev=0.4, dly=0.3)],
      master=dict(lufs=-8.5, air=2.5, low=1.0))

style('psytrance', 'Electronic', 'Psytrance: relentless kick-bass rolls, acid squelches, hypnotic phrygian riffs',
      bpm=(140, 146), scales=['phrygian', 'minor'], progs=[[0, 0, 0, 0], [0, 0, 1, 0]], chord_size=3,
      sc_depth=0.3, sc_release=0.25, reverb=2.2, kit='punchy', kit_override=dict(kick=dict(len=0.28, decay=14)),
      drums={'kick': [FOUR], 'clap': ['....x.......x...'], 'ohat': [OFFHAT], 'chat': ['xxxxxxxxxxxxxxxx']},
      snare_tracks=['clap'], bass=['.RRR.RRR.RRR.RRR'], bass_gate=0.55, bass_lo=33,
      chord_rh=['......x.........'], arp=dict(rate=1, mode='random', oct=4),
      lead_rh=['x.x.xx.x.x.xx.x.', 'xxx.xxx.xxx.x.x.', 'x.xxx.x.x.xxx.x.', 'xxxxxxxxxxxx....'],
      lead_oct=4, fill=False,
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.35, db=-22), T('ohat', 'top', 'ohat', db=-27),
              T('chat', 'top', 'chat', pan=0.2, db=-30),
              T('bass', 'bass', 'sawbass', sc=0.6, p=dict(cut=1100, d=0.06, s=0.2)),
              T('chords', 'chords', 'stab', rev=0.4, dly=0.5, db=-26),
              T('pad', 'pad', 'warmpad', rev=0.5, db=-27),
              T('arp', 'arp', 'acid', dly=0.35, pan=-0.2, db=-25, p=dict(res=8)),
              T('lead', 'lead', 'acid', rev=0.3, dly=0.4, p=dict(res=9, cut=500))],
      master=dict(lufs=-8.0, air=2.0, low=1.0))

style('techno', 'Electronic', 'Peak-time techno: distorted kick, rolling 16th bass, dub stabs drowned in delay',
      bpm=(128, 134), scales=['minor'], progs=[[0, 0, 0, 0], [0, 0, 5, 5], [0, 6, 0, 5]], chord_size=3,
      sc_depth=0.85, sc_release=0.4, reverb=2.6, kit='punchy', kit_override=dict(kick=dict(drive=3.2)),
      drums={'kick': [FOUR], 'clap': ['....x.......x...'], 'ohat': ['..X...X...X...X.'], 'chat': ['oxoxoxoxoxoxoxox'],
             'ride': ['..o...o...o...o.']}, snare_tracks=['clap'],
      bass=['.RRR.RRR.RRR.RRR', '..RR.RRR..RR.RRO'], bass_gate=0.6,
      chord_rh=['......x.......x.', '..x.......x.....', '...x.......x....'],
      arp=dict(rate=1, mode='random', oct=5),
      lead_rh=['x...x...x.......', '..x...x...x...x.', 'x.......x-------', 'x...x...x...x...'],
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.3, db=-20), T('ohat', 'top', 'ohat', pan=0.1),
              T('chat', 'top', 'chat', pan=-0.25, db=-29), T('ride', 'top', 'ride', pan=0.3, db=-30),
              T('bass', 'bass', 'sawbass', sc=1.0, p=dict(cut=1200, d=0.1, s=0.3)),
              T('chords', 'chords', 'stab', sc=0.8, rev=0.35, dly=0.55, p=dict(cut=2600, fdecay=12)),
              T('pad', 'pad', 'warmpad', sc=1.0, rev=0.4, p=dict(cut=900)),
              T('arp', 'arp', 'pluck_saw', sc=0.9, rev=0.2, dly=0.4, pan=0.2, db=-28, p=dict(cut=3500)),
              T('lead', 'lead', 'bell', sc=0.6, rev=0.4, dly=0.4, pan=-0.15, db=-22)],
      master=dict(lufs=-8.5, air=1.5, low=1.5))

style('minimal', 'Electronic', 'Minimal techno: sparse clicks and blips, deep sub, lots of space and delay',
      bpm=(124, 128), scales=['minor'], progs=[[0, 0, 0, 0], [0, 0, 6, 6]], chord_size=3,
      sc_depth=0.5, reverb=2.5, kit='soft',
      drums={'kick': [FOUR], 'rim': ['..o..o.....o..o.', '...o..o...o..o..'], 'clap': ['....o.......o...'],
             'chat': ['..x...x...x...x.'], 'shaker': ['o.o.o.o.o.o.o.o.']}, snare_tracks=['clap'],
      bass=['R.....R...R.....', '..R.....R..R....'], bass_gate=0.5,
      chord_rh=['......x.........', '...........x....'], arp=dict(rate=1, mode='random', oct=5, prob=0.35),
      lead_rh=['x.......x.......', '..x.......x.....', 'x...x...........', '....x.......x...'],
      tracks=[T('kick', 'kick', 'kick'), T('rim', 'top', 'rim', pan=0.3, dly=0.3, db=-28), T('clap', 'snare', 'clap', rev=0.4, db=-24),
              T('chat', 'top', 'chat', db=-28), T('shaker', 'top', 'shaker', pan=-0.3, db=-31),
              T('bass', 'bass', 'sinebass', sc=0.7, p=dict(cut=400)),
              T('chords', 'chords', 'stab', dly=0.6, rev=0.3, db=-26, p=dict(cut=1800)),
              T('arp', 'arp', 'pluck_saw', dly=0.5, pan=-0.3, db=-28, p=dict(cut=2500)),
              T('lead', 'lead', 'bell', dly=0.5, rev=0.4, db=-24)],
      master=dict(lufs=-9.5, air=1.0, low=1.5))

style('acid_house', 'Electronic', 'Acid house: squelching 303 lines, raw 909 drums, rave stabs',
      bpm=(122, 128), scales=['minor', 'phrygian'], progs=[[0, 0, 0, 0], [0, 0, 5, 6]], chord_size=3,
      sc_depth=0.4, kit='909', bass_mode='acid', bass_lo=31,
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['xxxxxxxxxxxxxxxx', 'x.x.x.x.x.x.x.x.']},
      snare_tracks=['clap'], chord_rh=['x.....x.........', '...x......x.....'],
      arp=dict(rate=1, mode='random', oct=5, prob=0.6),
      lead_rh=['x.x.x.x.........', 'x...x...x.x.x...', '..x...x...x...x.', 'x-------........'],
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.2), T('ohat', 'top', 'ohat', db=-26),
              T('chat', 'top', 'chat', pan=0.2, db=-29),
              T('bass', 'bass', 'acid', sc=0.6, dly=0.2, db=-15, p=dict(res=8.5)),
              T('chords', 'chords', 'organ', rev=0.3, dly=0.3, db=-25),
              T('pad', 'pad', 'warmpad', rev=0.4, db=-28),
              T('arp', 'arp', 'pluck_saw', dly=0.4, pan=-0.25, db=-28),
              T('lead', 'lead', 'hoover', rev=0.3, db=-22)],
      master=dict(lufs=-9.0, air=1.5, low=1.0))

style('synthwave', 'Electronic', '80s synthwave/retrowave: gated-reverb snares, pulsing octave bass, supersaws, saw lead',
      bpm=(96, 112), scales=['minor'], progs=[[0, 5, 2, 6], [0, 6, 5, 6], [5, 3, 0, 4], [0, 3, 5, 4]],
      sc_depth=0.5, sc_release=0.5, reverb=2.4,
      kit='punchy', kit_override=dict(snare=dict(tone=200, snap=1.0, decay=12)),
      drums={'kick': [FOUR, 'X.......X.x.....'], 'snare': [BACKBEAT], 'clap': [BACKBEAT],
             'chat': ['x.x.x.x.x.x.x.x.', 'xoxoxoxoxoxoxoxo']}, snare_tracks=['snare', 'clap'],
      bass=['R.O.R.O.R.O.R.O.', 'RRRRRRRRRRRRRRRR'], bass_gate=0.7, bass_lo=33,
      arp=dict(rate=1, mode='up', oct=5),
      lead_rh=['x-x-x---x---x-x-', 'x---x---x-x-x---', 'x-----x-x---x---', 'x-------x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.5), T('clap', 'snare', 'clap', rev=0.4, db=-22),
              T('chat', 'top', 'chat', pan=0.2),
              T('bass', 'bass', 'sawbass', sc=0.9, p=dict(cut=2500, d=0.12, s=0.5)),
              T('chords', 'chords', 'supersaw', sc=0.7, rev=0.35, p=dict(cut=3500, a=0.05)),
              T('pad', 'pad', 'warmpad', sc=0.7, rev=0.4, p=dict(cut=1400)),
              T('arp', 'arp', 'pluck_saw', sc=0.6, rev=0.25, dly=0.35, pan=-0.2, db=-27),
              T('lead', 'lead', 'leadsaw', sc=0.3, rev=0.35, dly=0.3)],
      master=dict(lufs=-9.5, air=2.0, low=1.0))

style('synthpop', 'Electronic', 'Synth-pop: punchy LinnDrum-style beats, bright plucks, string pads, catchy leads',
      bpm=(110, 122), scales=['major', 'minor'], progs={'major': [[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4]],
                                                         'minor': [[0, 5, 2, 6], [0, 3, 5, 4]]},
      sc_depth=0.3, reverb=2.0, kit='punchy', form='song',
      drums={'kick': ['X.......X.X.....', FOUR], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.'], 'tom': ['................']},
      snare_tracks=['snare'], bass=['R.R.R.R.R.R.R.R.', 'R.RRR.R.R.RRR.R.'], bass_gate=0.6, bass_lo=33,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x--x--x-x--x--x-'], chord_center=64, arp=dict(rate=1, mode='up', oct=5),
      lead_rh=['x-x-x---x-x-x---', 'x.x.x.x.x---....', 'x---x---x-x-x---', 'x-------x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.4), T('chat', 'top', 'chat', pan=0.2, db=-27),
              T('bass', 'bass', 'sawbass', sc=0.5, p=dict(cut=2000)),
              T('chords', 'chords', 'pluck_saw', sc=0.4, rev=0.3, dly=0.2),
              T('pad', 'pad', 'strings', sc=0.4, rev=0.4),
              T('arp', 'arp', 'bell', rev=0.3, dly=0.3, pan=-0.25, db=-27),
              T('lead', 'lead', 'leadsaw', rev=0.3, dly=0.25)],
      master=dict(lufs=-9.5, air=2.0, low=1.0))

style('electro', 'Electronic', 'Electro: robotic 808 funk, FM bass grit, zappy leads',
      bpm=(125, 132), scales=['minor', 'phrygian'], progs=[[0, 0, 5, 6], [0, 0, 0, 0], [0, 6, 5, 6]],
      sc_depth=0.4, kit='808',
      drums={'kick': ['X..X......X..X..', 'X......X..X.....'], 'clap': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.', 'xxx.x.x.xxx.x.x.'],
             'cowbell808': ['......x.......x.', '................']}, snare_tracks=['clap'],
      bass=['R..R..R...R..RO.', 'R.R...RR..R.R...'], bass_gate=0.6,
      chord_rh=['x.....x.........'], arp=dict(rate=1, mode='random', oct=5, prob=0.6),
      lead_rh=['x.x.x...x.x.....', 'x..x..x.x..x....', 'xxx.x...x.......', 'x---x---........'],
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.25), T('chat', 'top', 'chat', pan=0.2, db=-27),
              T('cowbell808', 'top', 'cowbell808', pan=-0.3, db=-30),
              T('bass', 'bass', 'fmbass', sc=0.7, p=dict(index=3.5, drive=3.0)),
              T('chords', 'chords', 'stab', rev=0.3, dly=0.3, db=-25),
              T('arp', 'arp', 'chip', dly=0.3, pan=0.25, db=-28, p=dict(pw=0.25)),
              T('lead', 'lead', 'leadsaw', rev=0.25, dly=0.3)],
      master=dict(lufs=-9.0, air=1.5, low=1.0))

style('bigroom', 'Electronic', 'Big room / festival EDM: huge kicks, massive drops, stabby supersaw leads',
      bpm=(126, 128), scales=['minor'], progs=[[0, 5, 2, 6], [0, 0, 5, 6], [5, 6, 0, 0]],
      sc_depth=0.9, sc_release=0.45, reverb=2.8, kit='hard', kit_override=dict(kick=dict(drive=4.0, decay=5)),
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.x.x.x.x.x.x.x.']}, snare_tracks=['clap'],
      bass=['..R...R...R...R.'], bass_gate=0.5,
      chord_rh=['x---------------'], chord_center=64, arp=dict(rate=1, mode='up', oct=5),
      lead_rh=['x.x...x.x.x...x.', 'x..x..x.x.......', 'x.x.x.x.x.x.x.x.', 'x...x...x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.35), T('ohat', 'top', 'ohat', db=-26),
              T('chat', 'top', 'chat', db=-29),
              T('bass', 'bass', 'fmbass', sc=1.0, p=dict(index=2.0, drive=2.0)),
              T('chords', 'chords', 'supersaw', sc=1.0, rev=0.4, p=dict(cut=4000, a=0.1)),
              T('pad', 'pad', 'warmpad', sc=1.0, rev=0.5),
              T('arp', 'arp', 'pluck_saw', sc=0.8, dly=0.35, pan=0.25, db=-27),
              T('lead', 'lead', 'hoover', sc=0.6, rev=0.4, db=-17)],
      master=dict(lufs=-7.5, air=2.0, low=1.5))

style('hardstyle', 'Electronic', 'Hardstyle: distorted pitched kicks, screeching leads, euphoric supersaw melodies',
      bpm=(148, 154), scales=['minor', 'harmonic_minor'], progs=[[0, 5, 2, 6], [0, 5, 3, 4], [0, 6, 5, 4]],
      sc_depth=0.9, sc_release=0.35, reverb=3.0, kit='hard',
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['..x...x...x...x.']}, snare_tracks=['clap'],
      bass=['..R...R...R...R.'], bass_gate=0.45, chord_rh=['x---------------'], chord_center=64,
      arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x-x-x-x-x---x-x-', 'x--x--x-x--x--x-', 'x-x-x---x-------', 'x---x---x---x---'], fill=True,
      tracks=[T('kick', 'kick', 'kick', db=-11), T('clap', 'snare', 'clap', rev=0.4, db=-19), T('ohat', 'top', 'ohat', db=-27),
              T('chat', 'top', 'chat', db=-29),
              T('bass', 'bass', 'sawbass', sc=1.0, db=-19, p=dict(cut=900)),
              T('chords', 'chords', 'supersaw', sc=1.0, rev=0.45, p=dict(cut=5000, a=0.1)),
              T('pad', 'pad', 'choir', sc=0.9, rev=0.5, db=-25),
              T('arp', 'arp', 'pluck_saw', sc=0.9, dly=0.35, db=-27),
              T('lead', 'lead', 'supersaw_lead', sc=0.7, rev=0.45, dly=0.25, db=-17)],
      master=dict(lufs=-7.5, air=2.0, low=1.0))

style('future_bass', 'Electronic', 'Future bass: lush pitch-chopped supersaw chords, vocal chops, half-time trap drums',
      bpm=(140, 160), scales=['major', 'minor'], progs={'major': [[3, 4, 5, 0], [0, 4, 5, 3], [3, 4, 2, 5]],
                                                         'minor': [[5, 6, 0, 0], [0, 5, 6, 4]]}, chord_size=4,
      sc_depth=0.85, sc_release=0.35, reverb=2.4, kit='808', form='halftime', trap_hats=True,
      drums={'kick': ['X.....X...X.....', 'X......X..X..X..'], 'snare': [HALF], 'clap': [HALF]}, snare_tracks=['snare', 'clap'],
      bass_mode='808', bass_lo=31,
      chord_rh=['x.xx.x.xx.x.xx.x', 'x--x--x-x--x--x-', 'x-x-x-x-x-x-x-x-'], chord_center=65,
      arp=dict(rate=2, mode='up', oct=6),
      lead_rh=['x.x.xx.x..x.x...', 'xx.x.x..x.x.xx..', 'x.x.x.x.x-x-....', 'x-x-x-x-x-------'],
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.3), T('clap', 'snare', 'clap', rev=0.3, db=-20),
              T('chat', 'top', 'chat', pan=0.15, db=-26),
              T('bass', 'bass', '808', sc=0.6, db=-14),
              T('chords', 'chords', 'supersaw', sc=1.0, rev=0.35, p=dict(cut=6000, a=0.01, r=0.1, detune=1.4)),
              T('pad', 'pad', 'warmpad', sc=1.0, rev=0.5, db=-27),
              T('arp', 'arp', 'bell', sc=0.6, dly=0.3, rev=0.3, db=-27),
              T('lead', 'lead', 'vox', sc=0.6, rev=0.35, dly=0.3)],
      master=dict(lufs=-8.5, air=2.5, low=1.0))

style('dubstep', 'Electronic', 'Dark / UK dubstep: half-time at 140, deep clean sub with a slow wobbling mid-bass, sparse '
      'syncopated drums, lots of space, dark atmospheres',
      bpm=(138, 142), scales=['minor', 'phrygian'], progs=[[0, 0, 5, 6], [0, 0, 1, 0], [0, 5, 0, 6], [0, 0, 0, 6]],
      sc_depth=0.5, sc_release=0.3, reverb=3.0, delay_beats=0.75, kit='hard', form='halftime', sub_layer=True,
      kit_override=dict(kick=dict(drive=2.0, punch=200, decay=6), snare=dict(snap=1.5, decay=10)),
      drums={'kick': ['X.........X.....', 'X.....X...X.....', 'X.......X.X.....'], 'snare': [HALF],
             'chat': ['x...x...x...x.x.', '..x...x...x...x.'], 'ohat': ['..............x.'], 'rim': ['.....x.......x..']},
      snare_tracks=['snare'], bass_mode='wobble', bass_lo=26, chord_rh=['x---------------'],
      arp=dict(rate=2, mode='random', oct=5, prob=0.35),
      lead_rh=['x-------x-------', 'x---x---x-------', 'x---------------', '........x-------'], lead_oct=5,
      gm_hint='Clean mono sine sub + LFO-wobbled mid-bass; sparse punchy drums; dark pads and drones',
      tracks=[T('kick', 'kick', 'kick', db=-12), T('snare', 'snare', 'snare', rev=0.35, db=-14),
              T('chat', 'top', 'chat', pan=0.2, db=-29), T('ohat', 'top', 'ohat', db=-30), T('rim', 'top', 'rim', pan=-0.25, db=-30),
              T('bass', 'bass', 'wobble', sc=0.7, db=-14, p=dict(sub=0.0)),
              T('chords', 'chords', 'warmpad', sc=0.5, rev=0.6, db=-27, p=dict(cut=900)),
              T('pad', 'pad', 'choir', sc=0.5, rev=0.6, db=-28, p=dict(vowel='o')),
              T('arp', 'arp', 'bell', dly=0.5, rev=0.4, db=-29),
              T('lead', 'lead', 'hoover', sc=0.4, rev=0.4, db=-22),
              T('texture', 'fx', 'texture', rev=0.5, db=-36)],
      master=dict(lufs=-8.0, air=1.2, low=1.8))

style('trap', 'Electronic', 'Modern trap: half-time snares, rolling hi-hats, gliding 808s, dark bells',
      bpm=(136, 150), scales=['minor', 'harmonic_minor'], progs=[[0, 0, 5, 4], [0, 5, 3, 4], [0, 3, 0, 4], [0, 6, 5, 4]],
      sc_depth=0.25, sc_release=0.3, reverb=2.2, form='trap', trap_hats=True,
      kit_override=dict(kick=dict(pitch=55, punch=90, decay=14, drive=1.8, len=0.35), snare=dict(tone=210, snap=1.0, decay=20)),
      drums={'kick': ['X.....X...X.....', 'X......X..X...X.', 'X.....X.X.......', 'X..X......X.....'],
             'snare': [HALF], 'clap': [HALF], 'ohat': ['..............x.', '................']},
      snare_tracks=['snare', 'clap'], bass_mode='808', bass_lo=28, chord_rh=['x---------------', 'x-------x-------'],
      chord_center=64, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x.x.x.x.x...x...', 'x..x..x.x.......', 'x.xxx...x.x.....', 'x-------x---x---'],
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.15),
              T('clap', 'snare', 'clap', rev=0.15, db=-20), T('chat', 'top', 'chat', pan=0.15, db=-25),
              T('ohat', 'top', 'ohat', pan=-0.2, db=-29), T('bass', 'bass', '808', sc=0.6, db=-13),
              T('chords', 'chords', 'pluck', rev=0.4, dly=0.2, p=dict(bright=2500, damp=0.998, r=0.6), db=-22),
              T('pad', 'pad', 'warmpad', rev=0.5, p=dict(cut=900), db=-26),
              T('lead', 'lead', 'bell', rev=0.4, dly=0.3, pan=0.1)],
      master=dict(lufs=-9.0, air=2.0, low=1.5))

style('phonk', 'Electronic', 'Drift phonk: a heavily distorted pitched 808 cowbell riff on loop, clipped growling 808s, '
      'rolling hats, dark minor / phrygian mood, chopped vocals and tape grit - made at 3 a.m., played too loud in a car',
      bpm=(145, 165), scales=['phrygian', 'minor', 'harmonic_minor'],
      progs={'phrygian': [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], 'minor': [[0, 0, 0, 0], [0, 0, 5, 0], [0, 0, 0, 6]],
             'harmonic_minor': [[0, 0, 0, 4], [0, 0, 5, 4]]},
      sc_depth=0.3, sc_release=0.25, reverb=1.6, kit='808', form='phonk', trap_hats=True, human=0.005, swing=0.53, swing_unit=16,
      kit_override=dict(kick=dict(drive=6.0), clap=dict(drive=2.5), snare=dict(drive=3.0)),
      drums={'kick': ['X.....X...X.....', 'X..X......X..X..', 'X.....X.X...X...'], 'snare': [HALF], 'clap': [HALF],
             'cowbell808': ['................', '..x.......x.....']},
      snare_tracks=['snare', 'clap'], bass_mode='808', bass_lo=26,
      chord_rh=['x---------------'], arp=dict(rate=4, mode='random', oct=4, prob=0.25),
      lead_rh=['x..x..x.........', 'x.x.x...x.......', 'x..x..x.x..x....', 'x.xx.x..x.x.....', 'x.x.x.x.x..x..x.'],
      repetition=0.9, simplicity=0.25,
      gm_hint='Distorted pitched TR-808 cowbell (lead); clipped saturated 808; TR-808 kit with fast hats; pitched-down vocal chops; '
              'horror pad; vinyl crackle and tape saturation',
      tracks=[T('kick', 'kick', 'kick', db=-12, drive=0.5), T('snare', 'snare', 'snare', rev=0.3, db=-16), T('clap', 'snare', 'clap', rev=0.25, db=-18),
              T('chat', 'top', 'chat', pan=0.2, db=-25, drive=0.2), T('cowbell808', 'top', 'cowbell808', pan=-0.2, db=-30),
              T('bass', 'bass', '808', sc=0.35, db=-11, drive=0.4, p=dict(drive=9.0, decay=0.6)),
              T('chords', 'chords', 'warmpad', rev=0.5, db=-30, p=dict(cut=650)),
              T('pad', 'pad', 'choir', rev=0.6, db=-30, p=dict(vowel='o')),
              T('arp', 'arp', 'vox', rev=0.35, dly=0.3, db=-25),
              T('lead', 'lead', 'cowbell', rev=0.25, db=-15),],
      lead_lo=57,
      master=dict(lufs=-7.0, air=-0.5, low=2.5, drive=0.45, lofi=True, wobble=0.3))

style('ukgarage', 'Electronic', 'UK garage / 2-step: skippy shuffled drums, organ stabs, vocal chops, sub bass',
      bpm=(130, 134), scales=['minor', 'dorian'], swing=0.6, human=0.004,
      progs={'minor': [[0, 5, 3, 4], [0, 3, 6, 5]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 4]]}, chord_size=4,
      sc_depth=0.5, kit='punchy',
      drums={'kick': ['X.........X.....', 'X......X..X.....', 'X.........X..x..'], 'snare': [BACKBEAT],
             'chat': ['.xox.xox.xox.xox', 'x.xxx.xxx.xxx.xx'], 'shaker': ['o.o.o.o.o.o.o.o.'], 'rim': ['......o......o..']},
      snare_tracks=['snare'], bass=['R-......R..R....', 'R-....R-..R..O..', '..R-.....R-..R..'], bass_gate=0.8,
      chord_rh=['..x..x....x..x..', 'x..x..x...x.....', '...x..x...x..x..'], chord_center=63,
      arp=dict(rate=2, mode='random', oct=5, prob=0.4),
      lead_rh=['x.x..x.x..x.....', '..x.x..x.x......', 'x..x..x.x.x.....', 'x.xx.x..x.......'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.25), T('chat', 'top', 'chat', pan=0.2, db=-27),
              T('shaker', 'top', 'shaker', pan=-0.3, db=-30), T('rim', 'top', 'rim', db=-29),
              T('bass', 'bass', 'sinebass', sc=0.7, p=dict(cut=600)),
              T('chords', 'chords', 'organ', sc=0.5, rev=0.3, dly=0.2),
              T('pad', 'pad', 'warmpad', rev=0.4, db=-27),
              T('arp', 'arp', 'epiano', dly=0.3, db=-28),
              T('lead', 'lead', 'vox', rev=0.3, dly=0.3)],
      master=dict(lufs=-9.0, air=1.5, low=1.5))

style('dnb', 'Electronic', 'Drum & bass: two-step breaks at 174, growling reese bass, wide pads',
      bpm=(170, 176), scales=['minor'], progs=[[0, 5, 6, 4], [0, 3, 5, 6], [0, 0, 5, 6]], chord_size=4,
      sc_depth=0.55, sc_release=0.35, reverb=2.0, form_scale=2, ghosts=True, kit='punchy',
      drums={'kick': ['X.........X.....', 'X.........X..x..', 'X.X.......X.....'], 'snare': [BACKBEAT],
             'chat': ['x.x.x.x.x.x.x.x.', 'x.xxx.x.x.xxx.x.'], 'ride': ['x...x...x...x...']},
      snare_tracks=['snare'], bass=['R-------R-----..', 'R-----R---R-----', 'R---------------'], bass_lo=28,
      chord_center=64, arp=dict(rate=2, mode='updown', oct=5),
      lead_rh=['x---x---x-x-----', 'x-x---x-x---x---', 'x-------x---x---', 'x---------------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.2, db=-16),
              T('chat', 'top', 'chat', pan=0.2, db=-26), T('ride', 'top', 'ride', pan=-0.25, db=-31),
              T('bass', 'bass', 'reese', sc=1.0, p=dict(cut=850)),
              T('chords', 'chords', 'epiano', sc=0.6, rev=0.3, db=-24),
              T('pad', 'pad', 'supersaw', sc=0.8, rev=0.4, p=dict(cut=2500, a=0.5)),
              T('arp', 'arp', 'bell', sc=0.6, rev=0.3, dly=0.3, pan=0.25, db=-28),
              T('lead', 'lead', 'leadsaw', sc=0.5, rev=0.35, dly=0.25, p=dict(cut=4000))],
      master=dict(lufs=-9.0, air=1.5, low=1.0))

style('jungle', 'Electronic', 'Jungle / breakbeat: chopped amen-style breaks, deep subs, rave stabs and dub pads',
      bpm=(160, 172), scales=['minor'], progs=[[0, 0, 5, 6], [0, 3, 0, 4]], chord_size=3, form_scale=2,
      sc_depth=0.3, reverb=2.2, kit='acoustic', ghosts=True, swing=0.52,
      drums={'kick': ['X.X.......X.....', 'X.........XX....', 'X.X.......X..X..'],
             'snare': ['....X..x.x..X...', '....X.......X..x', '....X..x....X.x.'],
             'chat': ['x.x.x.x.x.x.x.x.'], 'ride': ['x.x.x.x.x.x.x.x.']},
      snare_tracks=['snare'], bass=['R-------........', 'R-----..R-......', 'R---------------'], bass_lo=28,
      chord_rh=['x.......x.......', '......x.........'], arp=dict(rate=2, mode='random', oct=5, prob=0.4),
      lead_rh=['x---x---........', 'x-------x---x---', '..x-x---x-------', 'x---------------'],
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.15, db=-15),
              T('chat', 'top', 'chat', db=-27), T('ride', 'top', 'ride', pan=0.3, db=-31),
              T('bass', 'bass', 'sinebass', sc=0.5, db=-14, p=dict(cut=300)),
              T('chords', 'chords', 'stab', rev=0.4, dly=0.4, db=-25),
              T('pad', 'pad', 'warmpad', rev=0.5, db=-26),
              T('arp', 'arp', 'bell', dly=0.4, db=-28),
              T('lead', 'lead', 'vox', rev=0.4, dly=0.3)],
      master=dict(lufs=-9.0, air=1.5, low=1.5))

style('downtempo', 'Electronic', 'Downtempo / chillout: laid-back beats, Rhodes & piano, warm pads, glassy bells',
      bpm=(85, 100), scales=['dorian', 'minor', 'major'], swing=0.56, human=0.008,
      progs={'dorian': [[0, 3, 6, 2], [0, 3, 0, 4]], 'minor': [[0, 5, 3, 4], [0, 3, 6, 5]], 'major': [[0, 5, 3, 4], [3, 4, 2, 5]]},
      chord_size=4, sc_depth=0.25, reverb=2.6, kit='soft', form='lofi',
      drums={'kick': ['X.....x...X.....', 'X.......X.x.....'], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.'],
             'shaker': ['.o.o.o.o.o.o.o.o']}, snare_tracks=['snare'],
      bass=['R-----..R...F...', 'R-------R---A---'], chord_rh=['x---------------', 'x-------x-------'],
      arp=dict(rate=2, mode='up', oct=5, prob=0.7),
      lead_rh=['x---x---x-------', '....x-x-x-------', 'x-------x---x---', 'x---------------'],
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.3), T('chat', 'top', 'chat', db=-28),
              T('shaker', 'top', 'shaker', pan=0.3, db=-31),
              T('bass', 'bass', 'sinebass', sc=0.4), T('chords', 'chords', 'epiano', rev=0.3),
              T('pad', 'pad', 'warmpad', rev=0.5, db=-26), T('arp', 'arp', 'bell', rev=0.4, dly=0.35, db=-27),
              T('lead', 'lead', 'softlead', rev=0.4, dly=0.3), T('vinyl', 'fx', 'vinyl', db=-44)],
      master=dict(lufs=-12.0, air=0.5, low=1.0))

style('lofi', 'Electronic', 'Lo-fi hip hop: swung boom-bap, jazzy 7th/9th Rhodes chords, warm bass, vinyl + tape wobble',
      bpm=(72, 88), scales=['major', 'dorian'], swing=0.6, human=0.012,
      progs={'major': [[1, 4, 0, 5], [3, 2, 1, 4], [0, 5, 1, 4], [3, 4, 2, 5]],
             'dorian': [[0, 3, 6, 2], [0, 3, 0, 4], [3, 4, 0, 0], [0, 6, 3, 4]]}, chord_size=5,
      sc_depth=0.2, sc_release=0.6, reverb=1.6, form='lofi', kit='soft',
      drums={'kick': ['X.....x...X.....', 'X......xX.....x.', 'X.x.......X..x..'], 'snare': [BACKBEAT],
             'rim': ['......o.......o.', '..........o.....'], 'chat': ['x.ox.ox.x.ox.oxo', 'x.x.x.x.x.x.x.x.']},
      snare_tracks=['snare'], bass=['R.....R...F.....', 'R-----..A.R.....', 'R-------F---A---'], bass_lo=33,
      chord_rh=['x-------x-------', 'x--------..x----', 'x---------------'], strum=0.015,
      lead_rh=['x--.x-x---......', '..x-x-x-x---....', 'x---..x-x-x-----', '....x-x-x---x---'],
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.2),
              T('rim', 'top', 'rim', pan=0.25, db=-30), T('chat', 'top', 'chat', pan=-0.15, db=-28),
              T('bass', 'bass', 'sinebass', sc=0.6), T('chords', 'chords', 'epiano', sc=0.4, rev=0.25),
              T('lead', 'lead', 'pluck', rev=0.3, dly=0.2, pan=0.2, p=dict(bright=3000, damp=0.995)),
              T('vinyl', 'fx', 'vinyl', db=-40)],
      master=dict(lufs=-12.0, air=-3.0, low=1.5, lofi=True))

style('ambient', 'Electronic', 'Ambient: slow evolving pads, glassy bells, soft lead, huge reverbs, no drums',
      bpm=(66, 80), scales=['major', 'mixolydian'], human=0.02, progs=[[0, 3, 5, 4], [0, 4, 5, 3], [3, 0, 4, 5]],
      chord_size=4, chord_bars=2, form='ambient', reverb=6.0, delay_beats=1.5,
      drums={'shaker': ['..o.......o.....', '......o.......o.']}, bass=['R---------------'],
      chord_center=60, strum=0.08, arp=dict(rate=2, mode='random', oct=5, prob=0.45),
      lead_rh=['x-------x-------', 'x-----------x---', '....x-------x---', 'x---------------'],
      tracks=[T('shaker', 'top', 'shaker', rev=0.6, pan=0.3, db=-34),
              T('bass', 'bass', 'sinebass', db=-20, p=dict(cut=400)), T('chords', 'chords', 'epiano', rev=0.6, db=-24),
              T('pad', 'pad', 'warmpad', rev=0.7, p=dict(cut=1400, a=2.5, r=3.0), db=-20),
              T('arp', 'arp', 'bell', rev=0.7, dly=0.4, pan=-0.3, db=-26, p=dict(ratio=1.4, index=1.5)),
              T('lead', 'lead', 'softlead', rev=0.6, dly=0.35, pan=0.15, db=-21),
              T('texture', 'fx', 'texture', rev=0.5, db=-36)],
      master=dict(lufs=-14.0, air=1.5, low=0.5))

style('chiptune', 'Electronic', '8-bit chiptune: pulse-wave leads, triangle bass, noise drums, lightning arpeggios',
      bpm=(140, 160), scales=['major'], progs=[[0, 4, 5, 3], [0, 5, 3, 4], [5, 3, 0, 4], [0, 3, 4, 4]],
      reverb=0.8, form='chip', kick_track='chipkick',
      drums={'chipkick': ['X.......X.x.....', FOUR], 'chipsnare': [BACKBEAT], 'chiphat': ['x.x.x.x.x.x.x.x.', 'xxxxxxxxxxxxxxxx']},
      snare_tracks=['chipsnare'], bass=['R.O.R.O.R.O.R.O.', 'R.R.O.R.R.R.O.R.'], bass_gate=0.8, bass_lo=33,
      arp=dict(rate=0.5, mode='up', oct=5),
      lead_rh=['x.x.x-x-x.x.x---', 'x-x-x-x-x---x---', 'x.xxx.x.x-x-x---', 'x-----x-x-------'], fill=True,
      tracks=[T('chipkick', 'kick', 'chipkick'), T('chipsnare', 'snare', 'chipsnare'), T('chiphat', 'top', 'chiphat', db=-27),
              T('bass', 'bass', 'chipbass', db=-16),
              T('arp', 'arp', 'chip', pan=-0.2, p=dict(pw=0.25, vib=0, d=0.05, s=0.5), db=-26),
              T('lead', 'lead', 'chip', pan=0.1, rev=0.12, dly=0.15, p=dict(pw=0.5))],
      master=dict(lufs=-10.0, air=0.5, low=0.5))

# ============================== CLASSIC =====================================

style('disco', 'Classic', 'Disco / nu-disco: four-on-the-floor, octave bass, string sweeps, brass hits, funky guitar',
      bpm=(112, 124), scales=['minor', 'dorian'], swing=0.52, human=0.004,
      progs={'minor': [[0, 3, 6, 5], [0, 5, 3, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 4]]}, chord_size=4,
      sc_depth=0.3, kit='acoustic', form='song',
      drums={'kick': [FOUR], 'snare': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.x.x.x.x.x.x.x.'],
             'conga': ['...x..x....x.x..']}, snare_tracks=['snare'],
      bass=['R.O.R.O.R.O.R.O.', 'R.ORR.O.R.ORR.O.'], bass_gate=0.6, bass_lo=31,
      chord_rh=['..x.x..x..x.x..x', 'x.xx.xx.x.xx.xx.'], chord_center=66, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x.x.x-..x-x.x-..', 'x--.x--.x.x.x---', '..x.x..x..x.x...', 'x-------x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.2), T('ohat', 'top', 'ohat', db=-26),
              T('chat', 'top', 'chat', pan=0.2, db=-29), T('conga', 'top', 'conga', pan=-0.3, db=-29),
              T('bass', 'bass', 'sawbass', sc=0.4, p=dict(cut=1500, d=0.12, s=0.4)),
              T('chords', 'chords', 'guitar', pan=-0.3, rev=0.15, db=-24, p=dict(bright=7000, damp=0.99)),
              T('pad', 'pad', 'strings', pan=0.2, rev=0.4, db=-24),
              T('arp', 'arp', 'epiano', rev=0.2, db=-27),
              T('lead', 'lead', 'brass', rev=0.3, db=-20)],
      master=dict(lufs=-10.0, air=2.0, low=1.0))

style('funk', 'Classic', 'Funk: syncopated grooves, slap-style bass, clavinet chops, horn section',
      bpm=(96, 112), scales=['dorian', 'mixolydian'], swing=0.54, human=0.006,
      progs={'dorian': [[0, 0, 3, 3], [0, 3, 0, 4]], 'mixolydian': [[0, 0, 3, 0], [0, 6, 3, 0]]}, chord_size=4,
      kit='acoustic', ghosts=True, form='song',
      drums={'kick': ['X..x..X...X..x..', 'X.x...X..x..X...'], 'snare': [BACKBEAT], 'chat': ['xxxxxxxxxxxxxxxx', 'x.xxx.xxx.xxx.xx'],
             'ohat': ['......x.........']}, snare_tracks=['snare'],
      bass=['R..O.R...RR.O..A', 'R.R..O.R..R.O.R.', 'R...O.RR..R.O..A'], bass_gate=0.5, bass_lo=31,
      chord_rh=['.x.x..x..x.x..x.', 'x..x.x..x..x.x..', '.xx..x.x.xx..x.x'], chord_center=64,
      arp=dict(rate=2, mode='random', oct=5, prob=0.5),
      lead_rh=['x.x.x...x.x.....', '..x..x.x..x.....', 'x..x..x.x.......', 'x-x-x-..x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.15), T('chat', 'top', 'chat', pan=0.2, db=-28),
              T('ohat', 'top', 'ohat', db=-29),
              T('bass', 'bass', 'sawbass', p=dict(cut=2600, d=0.1, s=0.3)),
              T('chords', 'chords', 'pluck', pan=-0.25, db=-23, p=dict(bright=9000, damp=0.985)),
              T('pad', 'pad', 'organ', pan=0.25, rev=0.3, db=-27),
              T('arp', 'arp', 'guitar', pan=0.3, db=-27, p=dict(bright=7000, damp=0.99)),
              T('lead', 'lead', 'brass', rev=0.25)],
      master=dict(lufs=-10.0, air=1.5, low=1.0))

style('pop', 'Classic', 'Pop: four-chord hooks, piano & guitar, punchy drums, sing-along lead line',
      bpm=(95, 122), scales=['major'], progs=[[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4], [3, 4, 0, 5]],
      sc_depth=0.2, kit='punchy', form='song',
      drums={'kick': ['X.......X.X.....', 'X...X...X...X...'], 'snare': [BACKBEAT], 'clap': [BACKBEAT],
             'chat': ['x.x.x.x.x.x.x.x.']}, snare_tracks=['snare', 'clap'],
      bass=['R.......R...R...', 'R...R...R.R.R...', 'R-..R-..R-..A...'], bass_lo=33,
      chord_rh=['x---x---x---x---', 'x-.x-.x-x-.x-.x-'], chord_center=62, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x-x-x---x-x-x---', 'x---x-x-x-------', 'x-x-x-x-x---x---', 'x-------x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.3), T('clap', 'snare', 'clap', db=-21),
              T('chat', 'top', 'chat', pan=0.2, db=-28),
              T('bass', 'bass', 'sawbass', sc=0.3, p=dict(cut=1200)),
              T('chords', 'chords', 'piano', rev=0.25),
              T('pad', 'pad', 'strings', rev=0.4, db=-26),
              T('arp', 'arp', 'guitar', pan=-0.3, rev=0.2, db=-27),
              T('lead', 'lead', 'pluck', rev=0.3, dly=0.25, p=dict(bright=6000))],
      master=dict(lufs=-9.5, air=2.0, low=1.0))

style('rock', 'Classic', 'Rock: driving drums, distorted power-chord guitars, solid bass, lead guitar',
      bpm=(110, 140), scales=['minor', 'mixolydian', 'major'],
      progs={'minor': [[0, 5, 6, 0], [0, 3, 5, 6]], 'mixolydian': [[0, 6, 3, 0]], 'major': [[0, 4, 5, 3], [0, 3, 4, 3]]},
      kit='acoustic', form='song', voicing='power', human=0.004,
      drums={'kick': ['X.....X.X.......', 'X.......X.X.....'], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.'],
             'ride': ['x.x.x.x.x.x.x.x.']}, snare_tracks=['snare'],
      bass=['R.R.R.R.R.R.R.R.', 'R-R-R-R-R-R-A-R-'], bass_gate=0.85, bass_lo=28,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x-x-x-x-x-x-x-x-', 'x--x--x-x--x--x-'], chord_center=52,
      arp=dict(rate=2, mode='up', oct=4),
      lead_rh=['x-x-x---x-x-x---', 'x---x-x-x-------', 'x.x.x.x.x---x---', 'x-------x-------'], lead_oct=4, fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.25), T('chat', 'top', 'chat', pan=0.2, db=-27),
              T('ride', 'top', 'ride', pan=-0.3, db=-32),
              T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1800, damp=0.997)),
              T('chords', 'chords', 'guitar', drive=1.0, p=dict(dist=12, bright=5000)),
              T('pad', 'pad', 'organ', rev=0.3, db=-28),
              T('arp', 'arp', 'guitar', pan=0.4, db=-27, p=dict(dist=6)),
              T('lead', 'lead', 'guitar', rev=0.35, dly=0.25, p=dict(dist=20, bright=6000, damp=0.999))],
      master=dict(lufs=-9.5, air=1.5, low=1.0))

style('jazz', 'Classic', 'Jazz / swing: walking bass, ride-cymbal swing, piano comping with extended chords',
      bpm=(100, 160), scales=['major', 'dorian'], swing=0.66, swing_unit=8, human=0.01,
      progs={'major': [[1, 4, 0, 0], [1, 4, 0, 5], [0, 5, 1, 4]], 'dorian': [[0, 3, 0, 3], [0, 4, 0, 3]]}, chord_size=5,
      kit='acoustic', form='jazz', bass_mode='walk', bass_lo=28, ghosts=True,
      drums={'ride': ['x...x.x.x...x.x.'], 'chat': ['....x.......x...'], 'kick': ['o...o...o...o...'],
             'snare': ['................']}, snare_tracks=['snare'],
      chord_rh=['x-....x-........', '...x-.....x-....', 'x-.....x-.......'], chord_center=62,
      arp=dict(rate=2, mode='random', oct=5, prob=0.5),
      lead_rh=['x.x.x.x.x---....', '..x.x-x.x.x-....', 'x-.xx-x.x---x...', 'x---x-x-x-------'],
      tracks=[T('ride', 'top', 'ride', pan=0.3, db=-24), T('chat', 'top', 'chat', pan=-0.2, db=-29),
              T('kick', 'kick', 'kick', db=-24), T('snare', 'snare', 'snare', db=-26),
              T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1200, damp=0.996)),
              T('chords', 'chords', 'piano', rev=0.2, db=-21),
              T('arp', 'arp', 'piano', rev=0.2, db=-25),
              T('lead', 'lead', 'brass', rev=0.25, db=-19)],
      master=dict(lufs=-14.0, air=1.0, low=0.5))

style('boombap', 'Classic', 'Boom bap hip hop: dusty swung drums, chopped piano loops, deep bass',
      bpm=(84, 96), scales=['minor', 'dorian'], swing=0.58, human=0.008,
      progs={'minor': [[0, 5, 3, 4], [0, 0, 5, 6]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 4]]}, chord_size=4,
      kit='soft', form='lofi',
      drums={'kick': ['X.....x.X.....x.', 'X......XX.......'], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.'],
             'rim': ['..............o.']}, snare_tracks=['snare'],
      bass=['R.....R.R.......', 'R-----..R-....A.'], chord_rh=['x--x--..x---....', 'x---..x-..x-....'],
      lead_rh=['x-x-..x-x-......', '....x-x-x-x-....', 'x---x---........', 'x-------x-------'],
      tracks=[T('kick', 'kick', 'kick', db=-12), T('snare', 'snare', 'snare', rev=0.15), T('chat', 'top', 'chat', db=-28),
              T('rim', 'top', 'rim', db=-30), T('bass', 'bass', 'sinebass', db=-15),
              T('chords', 'chords', 'piano', rev=0.2), T('lead', 'lead', 'strings', rev=0.3, db=-24),
              T('vinyl', 'fx', 'vinyl', db=-40)],
      master=dict(lufs=-10.0, air=-1.5, low=1.5, lofi=True))

style('reggae', 'Classic', 'Reggae one-drop: offbeat skank chords, melodic bass, laid-back drums',
      bpm=(70, 90), scales=['major', 'minor'], swing=0.55, human=0.006,
      progs={'major': [[0, 3, 0, 4], [0, 4, 3, 3]], 'minor': [[0, 3, 0, 3], [0, 6, 5, 6]]}, chord_size=3,
      kit='acoustic', form='song',
      drums={'kick': [HALF], 'rim': [HALF], 'chat': ['x.x.x.x.x.x.x.x.'], 'snare': ['................']},
      snare_tracks=['snare'], bass=['R---..R.F-..A...', '..R-R-..F---R...', 'R-..R...F.R.A...'], bass_lo=28,
      chord_rh=['....x.......x...', '..x...x...x...x.'], chord_center=64,
      arp=dict(rate=2, mode='up', oct=5, prob=0.5),
      lead_rh=['x---x-x-x-------', '..x-x-x-x---....', 'x-------x---x---', 'x---------------'],
      tracks=[T('kick', 'kick', 'kick'), T('rim', 'snare', 'rim', rev=0.3, db=-20), T('chat', 'top', 'chat', db=-28),
              T('snare', 'snare', 'snare', rev=0.3, db=-22),
              T('bass', 'bass', 'sinebass', db=-13, p=dict(cut=500)),
              T('chords', 'chords', 'organ', pan=-0.2, rev=0.2, p=dict(leslie=6.5)),
              T('arp', 'arp', 'guitar', pan=0.3, dly=0.3, db=-26),
              T('lead', 'lead', 'softlead', rev=0.3, dly=0.3)],
      master=dict(lufs=-11.0, air=1.0, low=2.0))

# ============================== ORCHESTRAL ==================================

style('cinematic', 'Orchestral', 'Epic cinematic / trailer: string ostinatos, taiko & timpani, horns, choir, huge climax',
      bpm=(80, 110), scales=['minor', 'harmonic_minor'], progs=[[0, 5, 2, 6], [0, 5, 3, 4], [0, 3, 5, 4], [0, 6, 5, 6]],
      chord_size=3, form='cinematic', reverb=3.5, kit_override=dict(),
      drums={'taiko': ['X.....x.X...x.x.', 'X..x..x.X.x.x...'], 'snare': ['....x.......x...'], 'timp': ['X.......X.......']},
      kick_track='taiko', snare_tracks=['snare'], bass=['R.R.R.R.R.R.R.R.', 'R-------R-------'], bass_lo=28,
      chord_rh=['x-x-x-x-x-x-x-x-', 'xxxxxxxxxxxxxxxx'], chord_center=58, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x-------x---x---', 'x---x---x-------', 'x-----x-x-------', 'x---------------'], lead_oct=4,
      gm_hint='Strings: violins 1/2, violas (ostinato); Celli/Basses; French horns (theme); Choir; Taiko & timpani',
      tracks=[T('taiko', 'kick', 'taiko', rev=0.3, db=-13), T('snare', 'snare', 'snare', rev=0.4, db=-22),
              T('timp', 'snare', 'timp', rev=0.4, db=-19),
              T('bass', 'bass', 'strings', rev=0.3, db=-17, p=dict(cut=1500, a=0.05)),
              T('chords', 'chords', 'spiccato', rev=0.35, db=-21),
              T('pad', 'pad', 'choir', rev=0.5, db=-22),
              T('arp', 'arp', 'pizz', rev=0.3, pan=-0.3, db=-24),
              T('lead', 'lead', 'horn', rev=0.45, db=-18),
              T('texture', 'fx', 'texture', rev=0.5, db=-38)],
      master=dict(lufs=-11.0, air=1.5, low=1.5))

style('orchestral', 'Orchestral', 'Classical / romantic orchestra: lyrical violin melody, string harmony, harp, horns',
      bpm=(66, 96), scales=['major', 'minor'], human=0.012,
      progs={'major': [[0, 3, 4, 0], [0, 5, 3, 4], [0, 4, 5, 3]], 'minor': [[0, 3, 4, 0], [0, 5, 3, 4]]},
      chord_size=3, chord_bars=1, form='orchestral', reverb=3.2,
      drums={'timp': ['X...............']}, kick_track='timp',
      bass=['R-------R-------', 'R---R---R---R---'], bass_lo=31,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=60, arp=dict(rate=2, mode='updown', oct=5),
      lead_rh=['x---x-x-x-------', 'x-----x-x---x---', 'x-x-x---x-------', 'x---------------'], lead_oct=5,
      gm_hint='Violin solo (melody); String ensemble; Cellos & basses; Harp arpeggios; French horns pad; Timpani',
      tracks=[T('timp', 'kick', 'timp', rev=0.4, db=-22),
              T('bass', 'bass', 'strings', rev=0.35, db=-19, p=dict(a=0.15, cut=1200)),
              T('chords', 'chords', 'strings', rev=0.4, db=-21, p=dict(a=0.3, r=0.6)),
              T('pad', 'pad', 'horn', rev=0.45, db=-25),
              T('arp', 'arp', 'harp', rev=0.4, pan=-0.3, db=-23),
              T('lead', 'lead', 'violin', rev=0.45, db=-17)],
      master=dict(lufs=-16.0, air=1.0, low=0.5))

style('film_piano', 'Orchestral', 'Emotional film score: solo piano theme over warm strings, celesta sparkles',
      bpm=(64, 84), scales=['major', 'minor'], human=0.015,
      progs={'major': [[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4]], 'minor': [[0, 5, 2, 6], [0, 3, 5, 4]]},
      chord_size=3, chord_bars=1, form='orchestral', reverb=3.5,
      drums={}, bass=['R---------------'], bass_lo=31,
      chord_rh=['x---------------'], chord_center=58, arp=dict(rate=2, mode='updown', oct=4),
      lead_rh=['x---x---x-------', 'x-x-x---x---x---', '....x---x---x---', 'x---------------'], lead_oct=5,
      gm_hint='Piano (melody + arpeggios); String ensemble; Celli/Basses; Celesta',
      tracks=[T('bass', 'bass', 'strings', rev=0.4, db=-21, p=dict(a=0.4, cut=900)),
              T('chords', 'chords', 'strings', rev=0.45, db=-22, p=dict(a=0.6, r=1.0)),
              T('pad', 'pad', 'choir', rev=0.5, db=-29, p=dict(vowel='o')),
              T('arp', 'arp', 'piano', rev=0.35, db=-22),
              T('lead', 'lead', 'piano', rev=0.35, db=-17)],
      master=dict(lufs=-16.0, air=1.0, low=0.5))

CATEGORIES = ['Electronic', 'Classic', 'Orchestral']

LABELS = {'dnb': 'Drum & Bass', 'ukgarage': 'UK Garage', 'bigroom': 'Big Room', 'lofi': 'Lo-fi Hip Hop', 'boombap': 'Boom Bap',
          'film_piano': 'Film Piano', 'acid_house': 'Acid House', 'deep_house': 'Deep House', 'tech_house': 'Tech House',
          'progressive_house': 'Progressive House', 'future_bass': 'Future Bass', 'synthpop': 'Synth-pop', 'psytrance': 'Psytrance',
          'chiptune': 'Chiptune', 'downtempo': 'Downtempo', 'cinematic': 'Cinematic / Epic', 'orchestral': 'Orchestral',
          'trap': 'Trap', 'phonk': 'Phonk', 'hardstyle': 'Hardstyle', 'dubstep': 'Dubstep'}


def label(sid):
    return LABELS.get(sid, sid.replace('_', ' ').title())


# ============================== MORE STYLES (v1.2) ==========================
DEMBOW_K = 'X...X...X...X...'
DEMBOW_S = '...X..X....X..X.'

style('afrobeats', 'Electronic', 'Afrobeats: bouncy syncopated percussion, warm guitar chops, marimba hooks',
      bpm=(100, 116), scales=['major', 'minor', 'dorian'], swing=0.56, human=0.006, chord_size=4, kit='soft', form='song',
      drums={'kick': ['X..x..X...X..x..', 'X.....X.X.....x.'], 'snare': ['....x.......x...', '......x.......x.'],
             'rim': ['..x..x....x..x..', '...x..x..x..x...'], 'shaker': ['oxoxoxoxoxoxoxox'], 'conga': ['..o.x..o..o.x...', 'x..o..x...o..x..']},
      snare_tracks=['snare'], bass=['R..R....R.R.....', 'R...R.R...R..A..', 'R-..R...R-..R...'], bass_lo=31,
      chord_rh=['.x.x..x..x.x..x.', 'x..x..x...x..x..'], chord_center=64, arp=dict(rate=2, mode='random', oct=5, prob=0.6),
      lead_rh=['x.x..x.x..x.....', '..x.x..x..x.x...', 'x..x..x.x.......', 'x-.x-.x-x-......'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.15, db=-19), T('rim', 'top', 'rim', pan=0.3, db=-27),
              T('shaker', 'top', 'shaker', pan=-0.3, db=-28), T('conga', 'top', 'conga', pan=0.2, db=-25),
              T('bass', 'bass', 'sinebass', p=dict(cut=600)), T('chords', 'chords', 'guitar', pan=-0.25, db=-23, p=dict(bright=6000, damp=0.99)),
              T('pad', 'pad', 'warmpad', rev=0.4, db=-28), T('arp', 'arp', 'marimba', rev=0.2, pan=0.25, db=-24),
              T('lead', 'lead', 'vox', rev=0.3, dly=0.2)],
      master=dict(lufs=-9.5, air=1.5, low=1.5))

style('amapiano', 'Electronic', 'Amapiano: log-drum basslines, jazzy piano chords, rolling shakers, deep groove',
      bpm=(108, 116), scales=['minor', 'dorian'], swing=0.57, human=0.005, chord_size=5, kit='soft',
      progs={'minor': [[0, 3, 6, 5], [0, 5, 3, 4], [0, 6, 3, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]]},
      drums={'kick': ['X.......X.......', 'X...X...X...X...'], 'clap': ['....x.......x...'], 'shaker': ['oxoxoxoxoxoxoxox'],
             'woodblock': ['..x.....x.x.....', '......x.....x...'], 'chat': ['..x...x...x...x.']}, snare_tracks=['clap'],
      bass=['R..R..R...R..R..', '..R...R.R...R...', 'R..R....R..R..R.'], bass_gate=0.6, bass_lo=33,
      chord_rh=['x--.......x--...', '...x-.....x-....', 'x---------------'], chord_center=62, arp=dict(rate=2, mode='random', oct=5, prob=0.5),
      lead_rh=['x---x---........', '..x-x-x---......', 'x-------x-------', '....x-x-x-------'], sc_depth=0.3,
      tracks=[T('kick', 'kick', 'kick', db=-14), T('clap', 'snare', 'clap', rev=0.3, db=-21), T('shaker', 'top', 'shaker', pan=0.3, db=-27),
              T('woodblock', 'top', 'woodblock', pan=-0.3, db=-27), T('chat', 'top', 'chat', db=-29),
              T('bass', 'bass', 'logdrum', sc=0.5, db=-13), T('chords', 'chords', 'piano', rev=0.3, sc=0.4),
              T('pad', 'pad', 'warmpad', rev=0.5, db=-27), T('arp', 'arp', 'kalimba', rev=0.3, dly=0.3, db=-26),
              T('lead', 'lead', 'flute', rev=0.3, dly=0.3)],
      master=dict(lufs=-9.5, air=1.0, low=2.0))

style('reggaeton', 'Electronic', 'Reggaeton: dembow rhythm, deep 808s, plucky synths, latin percussion',
      bpm=(88, 100), scales=['minor', 'harmonic_minor'], swing=0.5, kit='808', form='song',
      progs=[[0, 5, 2, 6], [0, 5, 3, 4], [0, 3, 5, 4], [5, 3, 0, 4]],
      drums={'kick': [DEMBOW_K], 'snare': [DEMBOW_S], 'chat': ['x.x.x.x.x.x.x.x.'], 'tamb': ['....x.......x...'],
             'conga': ['..o...o...o...o.']}, snare_tracks=['snare'], bass_mode='808', bass_lo=28,
      chord_rh=['x..x..x...x..x..', 'x---------------'], chord_center=64, arp=dict(rate=2, mode='updown', oct=5),
      lead_rh=['x.x.x..x..x.x...', 'x..x..x.x.x.....', '..x.x.x.x..x....', 'x-x-x---x-------'],
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.15, db=-17), T('chat', 'top', 'chat', db=-28),
              T('tamb', 'top', 'tamb', pan=0.3, db=-28), T('conga', 'top', 'conga', pan=-0.3, db=-27),
              T('bass', 'bass', '808', db=-13), T('chords', 'chords', 'pluck_saw', rev=0.25, dly=0.2),
              T('pad', 'pad', 'warmpad', rev=0.4, db=-27), T('arp', 'arp', 'marimba', db=-26), T('lead', 'lead', 'pluck', rev=0.3, dly=0.25)],
      master=dict(lufs=-9.0, air=1.5, low=1.5))

style('moombahton', 'Electronic', 'Moombahton: dembow groove at 110 with big-room synths and heavy drops',
      bpm=(106, 112), scales=['minor'], progs=[[0, 5, 2, 6], [0, 6, 5, 6], [0, 5, 3, 4]], kit='punchy', sc_depth=0.5,
      drums={'kick': [DEMBOW_K], 'snare': [DEMBOW_S], 'clap': ['....X.......X...'], 'chat': ['x.x.x.x.x.x.x.x.'], 'tamb': ['..x...x...x...x.']},
      snare_tracks=['snare', 'clap'], bass=['R..R..R.R..R..R.', 'R...R.R...R.R...'], bass_gate=0.6,
      chord_rh=['x..x..x.x..x..x.'], arp=dict(rate=1, mode='up', oct=5),
      lead_rh=['x.x...x.x.x...x.', 'x..x..x.x.......', 'x.x.x.x.x.x.x.x.', 'x---x---x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.2), T('clap', 'snare', 'clap', rev=0.3, db=-21),
              T('chat', 'top', 'chat', db=-28), T('tamb', 'top', 'tamb', pan=0.3, db=-28),
              T('bass', 'bass', 'fmbass', sc=0.8), T('chords', 'chords', 'stab', sc=0.7, rev=0.3),
              T('pad', 'pad', 'supersaw', sc=0.8, rev=0.4, db=-26), T('arp', 'arp', 'pluck_saw', sc=0.5, dly=0.3, db=-27),
              T('lead', 'lead', 'hoover', sc=0.5, rev=0.3)],
      master=dict(lufs=-8.5, air=1.5, low=1.5))

style('uk_drill', 'Electronic', 'UK/NY drill: sliding 808s, triplet hats, offbeat snares, dark piano & strings',
      bpm=(140, 145), scales=['minor', 'harmonic_minor'], form='trap', kit='808', sc_depth=0.2,
      progs=[[0, 5, 0, 4], [0, 0, 5, 4], [0, 3, 5, 4]],
      drums={'kick': ['X.........X.....', 'X......X..x.....'], 'snare': ['....X......X....', '....X.......X..x'],
             'chat': ['x..x..x.x..x..x.', 'x.xx..x.x..x.x..'], 'snap': ['........x.......']},
      snare_tracks=['snare'], bass_mode='808', bass_lo=28, chord_rh=['x---------------', 'x-------x-------'], chord_center=62,
      arp=dict(rate=2, mode='random', oct=5, prob=0.4), lead_rh=['x--x--x-x-------', 'x-x-x---x---x---', '..x-x-x-x-------', 'x-------x-------'],
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.15), T('snap', 'snare', 'snap', db=-22),
              T('chat', 'top', 'chat', pan=0.2, db=-25), T('bass', 'bass', '808', sc=0.4, db=-12, p=dict(decay=0.6)),
              T('chords', 'chords', 'piano', rev=0.35), T('pad', 'pad', 'strings', rev=0.45, db=-26),
              T('arp', 'arp', 'bell', dly=0.3, db=-27), T('lead', 'lead', 'strings', rev=0.4, db=-21)],
      master=dict(lufs=-9.0, air=1.5, low=2.0))

style('hyperpop', 'Electronic', 'Hyperpop: maximal, bright and glitchy - distorted 808s, supersaws, chiptune sparkle',
      bpm=(150, 170), scales=['major', 'minor'], form='halftime', kit='hard', trap_hats=True, sc_depth=0.6,
      progs={'major': [[0, 4, 5, 3], [3, 4, 5, 0]], 'minor': [[5, 6, 0, 0], [0, 5, 2, 6]]}, chord_size=4,
      drums={'kick': ['X.....X...X.....', 'X..X......X..X..'], 'snare': [HALF], 'clap': [HALF]}, snare_tracks=['snare', 'clap'],
      bass_mode='808', bass_lo=28, chord_rh=['x.xx.x.xx.x.xx.x', 'x-x-x-x-x-x-x-x-'], chord_center=66, arp=dict(rate=0.5, mode='up', oct=6),
      lead_rh=['x.x.xx.x.x.xx.x.', 'xx.xx.x.x.xx.x..', 'x.x.x.x.x-x-x---', 'x-x-x-x-x-------'],
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.2), T('clap', 'snare', 'clap', db=-20),
              T('chat', 'top', 'chat', db=-26), T('bass', 'bass', '808', sc=0.6, db=-13, p=dict(drive=6.0)),
              T('chords', 'chords', 'supersaw', sc=1.0, rev=0.3, p=dict(cut=7000, a=0.005, r=0.08, detune=1.6)),
              T('pad', 'pad', 'vox', sc=0.8, rev=0.4, db=-26), T('arp', 'arp', 'chip', db=-26, p=dict(pw=0.25)),
              T('lead', 'lead', 'supersaw_lead', sc=0.5, rev=0.3, drive=0.4)],
      master=dict(lufs=-7.5, air=3.0, low=1.0))

style('vaporwave', 'Electronic', 'Vaporwave: slowed 80s nostalgia - lush Rhodes, sax, chorused pads, tape haze',
      bpm=(60, 80), scales=['major', 'dorian'], swing=0.52, human=0.01, chord_size=5, kit='soft', form='lofi',
      progs={'major': [[3, 2, 1, 4], [1, 4, 0, 5], [3, 4, 2, 5]], 'dorian': [[0, 3, 6, 2]]},
      drums={'kick': ['X.......X.x.....'], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.']}, snare_tracks=['snare'],
      bass=['R-----..R-..F...', 'R-------A-------'], chord_rh=['x---------------', 'x-------x-------'], strum=0.02,
      lead_rh=['x-----x-x-------', '....x---x---x---', 'x---x---x-------', 'x---------------'], reverb=4.0,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.5), T('chat', 'top', 'chat', db=-30),
              T('bass', 'bass', 'sinebass'), T('chords', 'chords', 'epiano', rev=0.5, dly=0.2),
              T('pad', 'pad', 'warmpad', rev=0.6), T('lead', 'lead', 'sax', rev=0.5, dly=0.3), T('vinyl', 'fx', 'vinyl', db=-42)],
      master=dict(lufs=-12.0, air=-2.0, low=1.0, lofi=True))

style('eurodance', 'Electronic', '90s eurodance: driving four-on-the-floor, offbeat bass, piano stabs, big anthemic leads',
      bpm=(134, 142), scales=['minor'], progs=[[0, 5, 2, 6], [0, 5, 3, 4], [5, 3, 0, 4]], kit='909', sc_depth=0.4, form='song',
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.x.x.x.x.x.x.x.'], 'tamb': ['....x.......x...']},
      snare_tracks=['clap'], bass=['..R...R...R...R.', '.RR..RR..RR..RR.'], bass_gate=0.6,
      chord_rh=['x..x..x...x..x..', 'x.x...x.x.x...x.'], chord_center=64, arp=dict(rate=1, mode='up', oct=5),
      lead_rh=['x-x-x-x-x---x-x-', 'x--x--x-x-------', 'x-x-x---x-x-x---', 'x-------x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.2), T('ohat', 'top', 'ohat', db=-26),
              T('chat', 'top', 'chat', db=-29), T('tamb', 'top', 'tamb', db=-29),
              T('bass', 'bass', 'sawbass', sc=0.6, p=dict(cut=1500)), T('chords', 'chords', 'piano', sc=0.4, rev=0.25),
              T('pad', 'pad', 'strings', sc=0.6, rev=0.4, db=-26), T('arp', 'arp', 'pluck_saw', dly=0.3, db=-27),
              T('lead', 'lead', 'supersaw_lead', sc=0.4, rev=0.35)],
      master=dict(lufs=-9.0, air=2.0, low=1.0))

style('breakcore', 'Electronic', 'Breakcore: frantic chopped breaks at 180+, reese bass, melancholic pads and chiptune',
      bpm=(170, 190), scales=['minor'], progs=[[0, 5, 2, 6], [0, 3, 5, 6], [5, 6, 0, 0]], kit='punchy', ghosts=True, form_scale=1.5,
      drums={'kick': ['X.X...X..XX.....', 'X..X.X....X.X...', 'XX......X.X..X..'],
             'snare': ['....X..x.X..X.xX', '..x.X.x.....Xx.x', '....X.xx..x.X..X'], 'chat': ['xxxxxxxxxxxxxxxx'], 'ride': ['x.x.x.x.x.x.x.x.']},
      snare_tracks=['snare'], bass=['R-------R-------', 'R---R---R-R-R---'], bass_lo=28, fill=True,
      chord_rh=['x---------------'], arp=dict(rate=1, mode='random', oct=5, prob=0.7),
      lead_rh=['x---x---x-x-----', 'x-x-x-x-x-------', 'x-------x---x---', 'x---------------'],
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.15, db=-15), T('chat', 'top', 'chat', db=-27),
              T('ride', 'top', 'ride', db=-31), T('bass', 'bass', 'reese', sc=0.5), T('chords', 'chords', 'warmpad', rev=0.5, db=-24),
              T('pad', 'pad', 'strings', rev=0.5, db=-26), T('arp', 'arp', 'chip', dly=0.3, db=-27), T('lead', 'lead', 'piano', rev=0.4)],
      master=dict(lufs=-8.5, air=1.5, low=1.0))

style('city_pop', 'Classic', 'City pop: 80s Japanese pop - slap-style bass, lush 7th chords, Rhodes, brass & sax',
      bpm=(104, 120), scales=['major', 'dorian'], swing=0.53, human=0.005, chord_size=4, kit='punchy', form='song',
      progs={'major': [[3, 2, 1, 4], [1, 4, 0, 5], [3, 4, 2, 5], [0, 5, 1, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]]},
      drums={'kick': ['X.......X.X.....', 'X..x....X.X.....'], 'snare': [BACKBEAT], 'chat': ['x.xxx.xxx.xxx.xx'],
             'ohat': ['......x.......x.']}, snare_tracks=['snare'],
      bass=['R..O.R...RR.O..A', 'R.R..O.R..R.O.R.'], bass_gate=0.5, bass_lo=31,
      chord_rh=['x--.x--...x.x...', '.x.x..x..x.x..x.'], chord_center=64, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x-x-x---x-x-x---', 'x--.x--.x.x.x---', '..x.x-x-x-------', 'x-------x-------'], fill=True,
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.35), T('chat', 'top', 'chat', db=-28),
              T('ohat', 'top', 'ohat', db=-29), T('bass', 'bass', 'fmbass', p=dict(index=2.5, drive=1.6, cut=3000)),
              T('chords', 'chords', 'epiano', rev=0.3), T('pad', 'pad', 'strings', rev=0.4, db=-26),
              T('arp', 'arp', 'guitar', pan=-0.3, db=-27, p=dict(bright=7000)), T('lead', 'lead', 'sax', rev=0.35, dly=0.2)],
      master=dict(lufs=-10.0, air=2.0, low=1.0))

style('bossa_nova', 'Classic', 'Bossa nova: gentle syncopated nylon guitar, rim clicks, soft bass and flute',
      bpm=(120, 140), scales=['major', 'dorian'], swing=0.52, human=0.01, chord_size=5, kit='soft', form='song',
      progs={'major': [[1, 4, 0, 0], [0, 5, 1, 4], [3, 2, 1, 4]], 'dorian': [[0, 3, 0, 3], [0, 4, 0, 3]]},
      drums={'rim': ['x..x..x...x..x..'], 'shaker': ['xoxoxoxoxoxoxoxo'], 'kick': ['X.....x.X.....x.']}, snare_tracks=['rim'],
      bass=['R.....F.R.....F.', 'R-....F-R-....F-'], bass_lo=31,
      chord_rh=['x..x..x...x..x..', 'x.x..x.x..x..x..'], chord_center=62, arp=dict(rate=2, mode='up', oct=5, prob=0.5),
      lead_rh=['x---x-x-x---....', '..x-x-x-x-------', 'x-------x---x---', 'x---------------'],
      tracks=[T('kick', 'kick', 'kick', db=-20), T('rim', 'snare', 'rim', db=-22), T('shaker', 'top', 'shaker', pan=0.3, db=-29),
              T('bass', 'bass', 'pluck', db=-16, p=dict(bright=1200, damp=0.996)),
              T('chords', 'chords', 'guitar', rev=0.2, p=dict(bright=4000, damp=0.995)), T('pad', 'pad', 'strings', rev=0.4, db=-28),
              T('arp', 'arp', 'piano', rev=0.25, db=-27), T('lead', 'lead', 'flute', rev=0.35, dly=0.15)],
      master=dict(lufs=-14.0, air=1.0, low=0.5))

style('blues', 'Classic', 'Blues shuffle: 12-bar form, swung grooves, piano, organ and expressive lead guitar',
      bpm=(80, 120), scales=['mixolydian'], swing=0.66, swing_unit=8, human=0.008, chord_size=4, kit='acoustic', form='song',
      progs=[[0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4], [0, 3, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4]],
      drums={'kick': ['X.......X.......'], 'snare': [BACKBEAT], 'ride': ['x...x.x.x...x.x.'], 'chat': ['....x.......x...']},
      snare_tracks=['snare'], bass_mode='walk', bass_lo=28, ghosts=True,
      chord_rh=['x-.x-.x-.x-.x-.x', 'x---x---x---x---'], chord_center=60, arp=dict(rate=2, mode='random', oct=4, prob=0.6),
      lead_rh=['x.x.x-....x.x---', '..x-x-x-x-------', 'x-.xx-x.x---....', 'x---x-x-x-------'], lead_oct=4,
      tracks=[T('kick', 'kick', 'kick', db=-17), T('snare', 'snare', 'snare', rev=0.2), T('ride', 'top', 'ride', db=-25),
              T('chat', 'top', 'chat', db=-29), T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1200)),
              T('chords', 'chords', 'piano', rev=0.2), T('pad', 'pad', 'organ', rev=0.25, db=-26),
              T('arp', 'arp', 'guitar', pan=0.3, db=-26), T('lead', 'lead', 'guitar', rev=0.3, p=dict(dist=10, bright=5000, damp=0.999))],
      master=dict(lufs=-12.0, air=1.0, low=1.0))

style('metal', 'Classic', 'Metal: palm-muted power chords, double-kick drums, shredding lead guitar',
      bpm=(140, 180), scales=['phrygian', 'minor', 'harmonic_minor'], progs=[[0, 0, 1, 0], [0, 5, 6, 0], [0, 6, 5, 4]],
      kit='acoustic', form='song', voicing='power', human=0.003,
      drums={'kick': ['XxXxXxXxXxXxXxXx', 'X.X.X.X.X.X.X.X.'], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.'], 'ride': ['x...x...x...x...']},
      snare_tracks=['snare'], bass=['RRRRRRRRRRRRRRRR', 'R.R.R.R.R.R.R.R.'], bass_gate=0.8, bass_lo=26, fill=True,
      chord_rh=['xxxxxxxxxxxxxxxx', 'x.xxx.xxx.xxx.xx', 'x-x-xxx-x-x-xxx-'], chord_center=48, arp=dict(rate=1, mode='updown', oct=4),
      lead_rh=['xxxxx.x.x-x-x---', 'x-x-x-x-xxxx----', 'x.x.x.x.x-------', 'x-------x-------'], lead_oct=4,
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.2, db=-15), T('chat', 'top', 'chat', db=-28),
              T('ride', 'top', 'ride', db=-30), T('bass', 'bass', 'pluck', db=-15, drive=0.6, p=dict(bright=2000, damp=0.997)),
              T('chords', 'chords', 'guitar', drive=1.5, p=dict(dist=25, bright=4500, damp=0.99)),
              T('arp', 'arp', 'guitar', pan=0.4, db=-26, p=dict(dist=18)),
              T('lead', 'lead', 'guitar', rev=0.3, dly=0.2, p=dict(dist=30, bright=6000, damp=0.999))],
      master=dict(lufs=-9.0, air=1.5, low=1.0))

style('folk', 'Classic', 'Folk / acoustic: strummed guitar, warm piano, gentle percussion, flute melody',
      bpm=(80, 116), scales=['major', 'mixolydian', 'minor'], human=0.012, kit='soft', form='song',
      progs={'major': [[0, 4, 5, 3], [0, 3, 0, 4], [0, 5, 3, 4]], 'mixolydian': [[0, 6, 3, 0]], 'minor': [[0, 6, 5, 6], [0, 3, 6, 0]]},
      drums={'kick': ['X.......X.......'], 'tamb': [BACKBEAT], 'shaker': ['x.x.x.x.x.x.x.x.']}, snare_tracks=['tamb'],
      bass=['R.......F.......', 'R...F...R...A...'], bass_lo=31,
      chord_rh=['x.x.xxx.x.x.xxx.', 'x--x--x-x--x--x-'], chord_center=60, strum=0.012, arp=dict(rate=2, mode='updown', oct=5),
      lead_rh=['x---x-x-x---....', 'x-x-x---x-------', '..x-x-x-x---x---', 'x---------------'],
      tracks=[T('kick', 'kick', 'kick', db=-19), T('tamb', 'snare', 'tamb', db=-23), T('shaker', 'top', 'shaker', db=-29),
              T('bass', 'bass', 'pluck', db=-17, p=dict(bright=1500)), T('chords', 'chords', 'guitar', rev=0.2, p=dict(bright=5500)),
              T('pad', 'pad', 'strings', rev=0.4, db=-27), T('arp', 'arp', 'piano', rev=0.3, db=-26),
              T('lead', 'lead', 'flute', rev=0.35)],
      master=dict(lufs=-13.0, air=1.0, low=0.5))

style('adventure', 'Orchestral', 'Adventure / fantasy score: heroic brass theme, galloping strings, snare marches',
      bpm=(100, 128), scales=['major', 'mixolydian'], form='cinematic', reverb=3.0,
      progs={'major': [[0, 4, 5, 3], [0, 3, 4, 0], [0, 6, 3, 4]], 'mixolydian': [[0, 6, 3, 0]]},
      drums={'timp': ['X.......X.......'], 'snare': ['x.xxx.x.x.xxx.x.', 'x..xx..xx.x.x...'], 'taiko': ['X.......X...X...']},
      kick_track='taiko', snare_tracks=['snare'], bass=['R.RR.RR.R.RR.RR.', 'R-R-R-R-R-R-R-R-'], bass_lo=28,
      chord_rh=['x.xx.xx.x.xx.xx.', 'x-x-x-x-x-x-x-x-'], chord_center=60, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x--.x-x-x-------', 'x-x-x---x---x---', 'x-----x-x-------', 'x---------------'], lead_oct=4,
      gm_hint='Trumpets/horns (theme); Violins (gallop ostinato); Celli/Basses; Snare drum; Timpani; Harp',
      tracks=[T('taiko', 'kick', 'taiko', rev=0.3, db=-16), T('snare', 'snare', 'snare', rev=0.35, db=-22),
              T('timp', 'snare', 'timp', rev=0.4, db=-20), T('bass', 'bass', 'strings', rev=0.3, db=-18, p=dict(a=0.02, cut=1500)),
              T('chords', 'chords', 'spiccato', rev=0.35, db=-21), T('pad', 'pad', 'horn', rev=0.45, db=-24),
              T('arp', 'arp', 'harp', rev=0.35, pan=-0.3, db=-24), T('lead', 'lead', 'brass', rev=0.45, db=-17)],
      master=dict(lufs=-11.0, air=1.5, low=1.0))

style('tension', 'Orchestral', 'Dark tension / horror: creeping low strings, eerie celesta, choir swells, timpani hits',
      bpm=(60, 84), scales=['phrygian', 'harmonic_minor'], form='orchestral', reverb=4.5, human=0.02,
      progs={'phrygian': [[0, 1, 0, 1], [0, 0, 1, 0], [0, 6, 1, 0]], 'harmonic_minor': [[0, 5, 0, 4], [0, 3, 0, 4]]},
      drums={'timp': ['X...............', '........X.......']}, kick_track='timp',
      bass=['R---------------', 'R-------R---R---'], bass_lo=26, chord_rh=['x---------------'], chord_center=56,
      arp=dict(rate=2, mode='random', oct=6, prob=0.35),
      lead_rh=['x-------........', '....x-------....', 'x---x-----------', '........x-------'], lead_oct=5,
      gm_hint='Low strings tremolo; Celesta / music box; Choir; Timpani; sustained horns',
      tracks=[T('timp', 'kick', 'timp', rev=0.5, db=-20), T('bass', 'bass', 'strings', rev=0.4, db=-18, p=dict(a=0.8, cut=800)),
              T('chords', 'chords', 'tremolo', rev=0.5, db=-23, p=dict(a=0.8, r=1.5, cut=2200)), T('pad', 'pad', 'choir', rev=0.6, db=-23, p=dict(vowel='o')),
              T('arp', 'arp', 'celesta', rev=0.6, dly=0.4, db=-25), T('lead', 'lead', 'violin', rev=0.55, db=-20, p=dict(vib=8))],
      master=dict(lufs=-16.0, air=0.5, low=1.0))

# ============================== STRINGS & ORCHESTRA (v1.9) ==================
# Built around a real string section / orchestra: with BBC Symphony Orchestra, LABS or the sampled sound library these
# parts play real strings, celli, woodwinds and brass (save sounds like "BBC strings legato", "BBC strings spiccato",
# "BBC celli", "BBC horns", "LABS soft piano" and each part finds the right one).
TRAILER_FORM = [
    ('intro', 8, {'chords', 'fx', 'top'}, {'filter_in': True}),
    ('rise', 8, {'chords', 'bass', 'kick', 'arp', 'top'}, {}),
    ('build', 8, {'chords', 'bass', 'kick', 'arp', 'snare'}, {'build': True}),
    ('climax', 16, ALL, {'drop': True}),
    ('calm', 8, {'chords', 'lead', 'fx'}, {'alt': True}),
    ('build', 8, {'chords', 'bass', 'kick', 'arp', 'snare', 'top'}, {'build': True, 'alt': True}),
    ('climax', 16, ALL, {'drop': True}),
    ('outro', 4, {'chords', 'fx', 'pad'}, {}),
]
FORMS['trailer'] = TRAILER_FORM
HIT_FORMS_EXTRA = {'trailer'}

style('neoclassical', 'Orchestral', 'Neoclassical / modern classical: intimate piano figures, slow string swells, solo cello',
      bpm=(60, 82), scales=['minor', 'major'], human=0.018,
      progs={'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4], [0, 6, 5, 3], [0, 5, 3, 3]],
             'major': [[0, 4, 5, 3], [3, 0, 4, 5], [0, 2, 3, 0], [5, 3, 0, 4]]},
      chord_size=3, chord_bars=1, form='orchestral', reverb=3.8, voicing='open',
      drums={}, bass=['R---------------', 'R-------R-------'], bass_lo=33,
      chord_rh=['x---------------'], chord_center=57, arp=dict(rate=2, mode='updown', oct=4),
      lead_rh=['x---x---x-------', 'x-----x-x-------', '....x---x---x---', 'x-------x---x---'], lead_oct=5,
      gm_hint='Felt / soft piano (figures + melody); String ensemble legato (swells); Solo cello',
      tracks=[T('bass', 'bass', 'cello', rev=0.4, db=-21, p=dict(a=0.3)),
              T('chords', 'chords', 'strings', rev=0.45, db=-23, p=dict(a=0.9, r=1.4, cut=2600)),
              T('arp', 'arp', 'piano', rev=0.35, pan=-0.15, db=-22),
              T('lead', 'lead', 'piano', rev=0.4, pan=0.1, db=-18)],
      master=dict(lufs=-16.0, air=0.8, low=0.5))

style('chamber', 'Orchestral', 'Chamber / string quartet: violin melody, viola harmony, cello line, pizzicato colour',
      bpm=(72, 112), scales=['major', 'minor', 'harmonic_minor'], human=0.014,
      progs={'major': [[0, 3, 4, 0], [0, 5, 1, 4], [0, 4, 5, 3], [0, 3, 1, 4]],
             'minor': [[0, 3, 4, 0], [0, 5, 3, 4], [0, 6, 5, 4]], 'harmonic_minor': [[0, 3, 4, 0], [0, 5, 3, 4]]},
      chord_size=3, chord_bars=1, form='orchestral', reverb=2.6, voicing='open',
      drums={}, bass=['R-------R-------', 'R---R---R---R---', 'R-----R-R-------'], bass_lo=36,
      chord_rh=['x-------x-------', 'x---x---x---x---', 'x-----x-x-------'], chord_center=58,
      arp=dict(rate=2, mode='up', oct=5, prob=0.6),
      lead_rh=['x---x-x-x-------', 'x-x-x---x---x---', 'x-----x-x-x-x---', '..x-x-x-x-------'], lead_oct=5,
      gm_hint='Violin I (melody); Viola (harmony); Cello (bass line); Violin II pizzicato',
      tracks=[T('bass', 'bass', 'cello', rev=0.3, db=-19),
              T('chords', 'chords', 'strings', rev=0.3, db=-23, p=dict(a=0.12, r=0.4, cut=3200)),
              T('arp', 'arp', 'pizz', rev=0.3, pan=-0.3, db=-25),
              T('lead', 'lead', 'violin', rev=0.35, pan=0.2, db=-17)],
      master=dict(lufs=-16.0, air=1.0, low=0.5))

style('baroque', 'Orchestral', 'Baroque: harpsichord continuo, running string lines, cello octave bass, circle-of-fifths harmony',
      bpm=(96, 128), scales=['major', 'harmonic_minor'], human=0.006,
      progs={'major': [[0, 3, 1, 4], [0, 5, 1, 4], [0, 3, 4, 0], [5, 1, 4, 0], [0, 4, 5, 2, 3, 0, 1, 4]],
             'harmonic_minor': [[0, 3, 4, 0], [0, 5, 3, 4], [5, 3, 4, 0]]},
      chord_size=3, chord_bars=1, form='orchestral', reverb=2.2,
      drums={}, bass=['R.R.R.R.R.R.R.R.', 'R.O.R.O.R.O.R.O.', 'R...F...R...F...'], bass_lo=36, bass_gate=0.7,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x...x...x...x...', 'x.xxx.x.x.xxx.x.'], chord_center=60,
      arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x.x.x.x.x-x-x---', 'x-x-x-x-x.x.x---', 'x.x.x.x.x.x.x.x.', 'x---x.x.x---x---'], lead_oct=5,
      gm_hint='Harpsichord (continuo); Violins (running 16ths); Cello + bass (octaves); Oboe / violin solo',
      tracks=[T('bass', 'bass', 'cello', rev=0.25, db=-19, p=dict(a=0.03)),
              T('chords', 'chords', 'harpsichord', rev=0.25, pan=-0.2, db=-22),
              T('pad', 'pad', 'strings', rev=0.3, db=-30, p=dict(a=0.2, cut=2400)),
              T('arp', 'arp', 'spiccato', rev=0.25, pan=0.25, db=-26, p=dict(len=0.14)),
              T('lead', 'lead', 'violin', rev=0.3, pan=0.1, db=-18, p=dict(vib=10))],
      master=dict(lufs=-15.0, air=1.2, low=0.5))

style('fantasy_rpg', 'Orchestral', 'Fantasy RPG / video-game score: harp arpeggios, flute & oboe melody, warm strings, horn swells',
      bpm=(84, 116), scales=['major', 'lydian', 'dorian'], human=0.01,
      progs={'major': [[0, 4, 5, 3], [0, 3, 0, 4], [3, 4, 2, 5], [0, 2, 3, 4], [0, 5, 3, 4]],
             'lydian': [[0, 1, 0, 1], [0, 1, 4, 0], [0, 1, 5, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0], [0, 3, 6, 4]]},
      chord_size=3, chord_bars=1, form='orchestral', reverb=3.0, voicing='open',
      drums={'timp': ['X...............', 'X.......X.......'], 'shaker': ['..x...x...x...x.']}, kick_track='timp',
      bass=['R-------R-------', 'R---R---R---R---'], bass_lo=33,
      chord_rh=['x---------------', 'x-------x-------', 'x---x---x---x---'], chord_center=60,
      arp=dict(rate=2, mode='updown', oct=5),
      lead_rh=['x---x-x-x-------', 'x-x-x---x---x---', 'x-----x-x-------', '..x-x-x-x---x---'], lead_oct=5,
      gm_hint='Flute / oboe (melody); Harp (arpeggios); Strings; French horns; Timpani',
      tracks=[T('timp', 'kick', 'timp', rev=0.4, db=-24), T('shaker', 'top', 'shaker', rev=0.3, pan=0.3, db=-34),
              T('bass', 'bass', 'cello', rev=0.35, db=-20),
              T('chords', 'chords', 'strings', rev=0.4, db=-22, p=dict(a=0.25, r=0.6)),
              T('pad', 'pad', 'horn', rev=0.45, db=-27),
              T('arp', 'arp', 'harp', rev=0.4, pan=-0.3, db=-22),
              T('lead', 'lead', 'flute', rev=0.4, pan=0.15, db=-18)],
      master=dict(lufs=-14.0, air=1.2, low=0.5))

style('hybrid_trailer', 'Orchestral', 'Hybrid trailer: pulsing spiccato ostinatos, braams, taiko, distorted synth bass, huge choir',
      bpm=(90, 120), scales=['minor', 'phrygian', 'harmonic_minor'],
      progs={'minor': [[0, 5, 2, 6], [0, 0, 5, 5], [0, 6, 5, 6], [0, 5, 3, 4]], 'phrygian': [[0, 1, 0, 1], [0, 0, 1, 0]],
             'harmonic_minor': [[0, 5, 0, 4], [0, 3, 5, 4]]},
      chord_size=3, form='trailer', reverb=3.4, delay_beats=0.75,
      drums={'taiko': ['X.....x.X...x.x.', 'X..x..x.X.x.x...', 'X.x.X...X.x.X.x.'], 'snare': ['....x.......x...', '....X..x....X.x.'],
             'timp': ['X.......X.......'], 'tom': ['......x.......xx', '..............xx']},
      kick_track='taiko', snare_tracks=['snare'], fill=True,
      bass=['R.R.R.R.R.R.R.R.', 'RRRRRRRRRRRRRRRR', 'R-R-R-R-R-R-R-R-'], bass_lo=28, bass_gate=0.6,
      chord_rh=['xxxxxxxxxxxxxxxx', 'x.xxx.xxx.xxx.xx', 'xx.xx.xx.xx.xx.x'], chord_center=57,
      arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x-------x---x---', 'x---x---x-------', 'x-----x-x-------', 'x---------------'], lead_oct=4,
      gm_hint='Strings spiccato (ostinato); Low brass braams; Horns (theme); Choir; Taiko + timpani; distorted synth bass',
      tracks=[T('taiko', 'kick', 'taiko', rev=0.3, db=-12), T('snare', 'snare', 'snare', rev=0.4, db=-21),
              T('timp', 'snare', 'timp', rev=0.4, db=-19), T('tom', 'top', 'tom', rev=0.35, db=-22),
              T('bass', 'bass', 'sawbass', drive=0.5, db=-19, p=dict(cut=700, d=0.1, s=0.5)),
              T('chords', 'chords', 'spiccato', rev=0.35, db=-21),
              T('pad', 'pad', 'braam', rev=0.45, db=-21),
              T('arp', 'arp', 'spiccato', rev=0.3, pan=0.3, db=-27, p=dict(len=0.12)),
              T('lead', 'lead', 'horn', rev=0.45, db=-17),
              T('texture', 'fx', 'texture', rev=0.5, db=-36)],
      master=dict(lufs=-11.0, air=1.5, low=1.5))

style('orchestral_hiphop', 'Electronic', 'Orchestral hip hop / drill: dramatic string stabs, choir, pizzicato, sliding 808s, rolling hats',
      bpm=(132, 145), scales=['harmonic_minor', 'minor'], form='trap', kit='808', trap_hats=True, sc_depth=0.15,
      progs={'harmonic_minor': [[0, 5, 0, 4], [0, 3, 5, 4], [0, 0, 5, 4]], 'minor': [[0, 5, 3, 6], [0, 3, 5, 6], [0, 5, 6, 4]]},
      drums={'kick': ['X.........X.....', 'X......X..x.....', 'X.....X...X.....'], 'snare': ['........X.......', '....X......X....'],
             'clap': ['........X.......']},
      snare_tracks=['snare', 'clap'], bass_mode='808', bass_lo=28,
      chord_rh=['x..x..x.x..x..x.', 'x.x.....x.x.....', 'x--x--x-x-------', 'xxxx....xxxx....'], chord_center=60,
      arp=dict(rate=2, mode='random', oct=5, prob=0.5),
      lead_rh=['x--x--x-x-------', 'x-x-x---x---x---', '..x-x-x-x-------', 'x-------x-------'],
      gm_hint='String section stabs (staccato); Strings legato / choir (pad); Pizzicato; Violin or horn theme; 808',
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.2), T('clap', 'snare', 'clap', db=-21),
              T('bass', 'bass', '808', sc=0.4, db=-12, p=dict(decay=0.7)),
              T('chords', 'chords', 'spiccato', rev=0.3, db=-21, p=dict(len=0.3)),
              T('pad', 'pad', 'strings', rev=0.45, db=-26, p=dict(a=0.5)),
              T('arp', 'arp', 'pizz', rev=0.3, pan=-0.25, db=-25),
              T('lead', 'lead', 'violin', rev=0.4, db=-19)],
      master=dict(lufs=-9.0, air=1.5, low=2.0))

style('symphonic_metal', 'Classic', 'Symphonic metal: double-kick drums and power chords under choir, string ostinatos and a soaring lead',
      bpm=(120, 170), scales=['harmonic_minor', 'minor', 'phrygian'],
      progs={'harmonic_minor': [[0, 5, 3, 4], [0, 3, 4, 0], [0, 5, 0, 4]], 'minor': [[0, 5, 2, 6], [0, 6, 5, 4], [0, 3, 6, 5]],
             'phrygian': [[0, 1, 0, 6], [0, 0, 1, 0]]},
      kit='acoustic', form='song', voicing='power', human=0.003, reverb=2.6,
      drums={'kick': ['XxXxXxXxXxXxXxXx', 'X.X.X.X.X.X.X.X.', 'X.XxX.XxX.XxX.Xx'], 'snare': [BACKBEAT, HALF],
             'chat': ['x.x.x.x.x.x.x.x.'], 'ride': ['x...x...x...x...']},
      snare_tracks=['snare'], bass=['RRRRRRRRRRRRRRRR', 'R.R.R.R.R.R.R.R.'], bass_gate=0.8, bass_lo=26, fill=True,
      chord_rh=['x.xxx.xxx.xxx.xx', 'xxxxxxxxxxxxxxxx', 'x-x-x-x-x-x-x-x-'], chord_center=48,
      arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x---x-x-x-------', 'x-x-x---x---x---', 'x-------x---x---', 'x-.x-.x-x-------'], lead_oct=5,
      gm_hint='Distorted guitars; Choir (pad); Strings spiccato (ostinato); Violin / guitar / horn lead; Organ',
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.25, db=-15), T('chat', 'top', 'chat', db=-28),
              T('ride', 'top', 'ride', db=-30), T('bass', 'bass', 'pluck', db=-15, drive=0.6, p=dict(bright=2000, damp=0.997)),
              T('chords', 'chords', 'guitar', drive=1.5, pan=-0.2, p=dict(dist=25, bright=4500, damp=0.99)),
              T('pad', 'pad', 'choir', rev=0.5, db=-22),
              T('arp', 'arp', 'spiccato', rev=0.3, pan=0.3, db=-25),
              T('lead', 'lead', 'violin', rev=0.4, dly=0.2, db=-17)],
      master=dict(lufs=-9.5, air=1.5, low=1.0))

style('holiday', 'Classic', 'Holiday / Christmas: sleigh bells, celesta, pizzicato, warm strings, brass and a cosy swing',
      bpm=(100, 140), scales=['major'], swing=0.57, human=0.008, kit='soft', form='song',
      progs=[[0, 5, 1, 4], [0, 3, 4, 0], [0, 2, 3, 4], [0, 3, 1, 4], [0, 5, 3, 4]], chord_size=4,
      drums={'kick': ['X.......X.......', 'X.......X.x.....'], 'snare': [BACKBEAT], 'sleigh': ['x.x.x.x.x.x.x.x.', 'xxxxxxxxxxxxxxxx'],
             'tamb': ['....x.......x...']}, snare_tracks=['snare'],
      bass=['R...F...R...F...', 'R.......F.......', 'R...F...R...A...'], bass_lo=31,
      chord_rh=['x---x---x---x---', '..x...x...x...x.', 'x--.x--.x---x---'], chord_center=62,
      arp=dict(rate=2, mode='updown', oct=6),
      lead_rh=['x-x-x---x-x-x---', 'x---x-x-x-------', 'x-x-x-x-x---x---', 'x-------x-------'], fill=True,
      gm_hint='Sleigh bells; Glockenspiel / celesta; Strings; Brass section; Pizzicato; Upright bass',
      tracks=[T('kick', 'kick', 'kick', db=-19), T('snare', 'snare', 'snare', rev=0.3, db=-22),
              T('sleigh', 'top', 'sleigh', pan=0.25, db=-28), T('tamb', 'top', 'tamb', pan=-0.25, db=-29),
              T('bass', 'bass', 'pluck', db=-16, p=dict(bright=1200, damp=0.996)),
              T('chords', 'chords', 'piano', rev=0.3, db=-22), T('pad', 'pad', 'strings', rev=0.4, db=-25),
              T('arp', 'arp', 'celesta', rev=0.35, pan=-0.2, db=-26),
              T('lead', 'lead', 'brass', rev=0.35, db=-19)],
      master=dict(lufs=-12.0, air=1.8, low=0.8))

style('western', 'Classic', 'Spaghetti western: twangy reverb guitar, lonely trumpet, whistled tune, choir and galloping hooves',
      bpm=(88, 120), scales=['minor', 'harmonic_minor', 'dorian'], human=0.01, kit='soft', form='song', reverb=3.2,
      progs={'minor': [[0, 6, 5, 6], [0, 3, 0, 4], [0, 5, 6, 0], [0, 6, 0, 4]], 'harmonic_minor': [[0, 3, 4, 0], [0, 5, 4, 0]],
             'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]},
      drums={'kick': ['X.......X.......'], 'snare': ['....x.......x...'], 'woodblock': ['x.xxx.xxx.xxx.xx', 'x..xx..xx..xx..x'],
             'tom': ['..............xx']}, snare_tracks=['snare'],
      bass=['R-------F-------', 'R...F...R...F...'], bass_lo=31,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x--x--x-x--x--x-', 'x---x---x---x---'], chord_center=57,
      arp=dict(rate=2, mode='updown', oct=4, prob=0.6),
      lead_rh=['x-------x---x---', 'x---x-x-x-------', 'x-----x-x-------', 'x---------------'],
      gm_hint='Twangy electric guitar (lots of spring reverb); Trumpet / whistle melody; Choir; Woodblock hooves',
      tracks=[T('kick', 'kick', 'kick', db=-19), T('snare', 'snare', 'snare', rev=0.4, db=-23),
              T('woodblock', 'top', 'woodblock', pan=0.3, db=-27), T('tom', 'top', 'tom', rev=0.4, db=-24),
              T('bass', 'bass', 'pluck', db=-17, p=dict(bright=1200)),
              T('chords', 'chords', 'guitar', pan=-0.2, rev=0.45, dly=0.25, p=dict(bright=4500, damp=0.995)),
              T('pad', 'pad', 'choir', rev=0.55, db=-25, p=dict(vowel='o')),
              T('arp', 'arp', 'guitar', pan=0.3, rev=0.4, db=-26, p=dict(bright=3500)),
              T('lead', 'lead', 'brass', rev=0.5, dly=0.25, db=-18)],
      master=dict(lufs=-12.0, air=1.0, low=0.8))

style('chamber_pop', 'Classic', 'Chamber / orchestral pop: pop drums & piano with a string section, horns, pizzicato and glockenspiel',
      bpm=(90, 124), scales=['major', 'minor'], human=0.006, kit='punchy', form='song',
      progs={'major': [[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4], [3, 4, 0, 5], [0, 2, 3, 4]],
             'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4]]},
      drums={'kick': ['X.......X.X.....', 'X...X...X...X...'], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.'], 'tamb': ['....x.......x...']},
      snare_tracks=['snare'], bass=['R.......R...R...', 'R...R...R.R.R...', 'R-..R-..R-..A...'], bass_lo=33,
      chord_rh=['x---x---x---x---', 'x-.x-.x-x-.x-.x-', 'x.x.x.x.x.x.x.x.'], chord_center=62,
      arp=dict(rate=2, mode='up', oct=5, prob=0.8),
      lead_rh=['x-x-x---x-x-x---', 'x---x-x-x-------', 'x-x-x-x-x---x---', 'x-------x-------'], fill=True,
      gm_hint='Piano; String section (legato pad + spiccato); Pizzicato / glockenspiel; Horns; Violin or flute counter-melody',
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.3), T('chat', 'top', 'chat', pan=0.2, db=-28),
              T('tamb', 'top', 'tamb', pan=-0.25, db=-30),
              T('bass', 'bass', 'pluck', db=-16, p=dict(bright=1500)),
              T('chords', 'chords', 'piano', rev=0.25), T('pad', 'pad', 'strings', rev=0.4, db=-24),
              T('arp', 'arp', 'pizz', rev=0.3, pan=-0.3, db=-25),
              T('lead', 'lead', 'violin', rev=0.35, db=-18)],
      master=dict(lufs=-10.5, air=1.8, low=1.0))

LABELS.update({'neoclassical': 'Neoclassical', 'chamber': 'Chamber / String Quartet', 'baroque': 'Baroque',
               'fantasy_rpg': 'Fantasy RPG', 'hybrid_trailer': 'Hybrid Trailer', 'orchestral_hiphop': 'Orchestral Hip Hop',
               'symphonic_metal': 'Symphonic Metal', 'holiday': 'Holiday', 'western': 'Spaghetti Western',
               'chamber_pop': 'Chamber Pop'})

LABELS.update({'uk_drill': 'UK Drill', 'city_pop': 'City Pop', 'bossa_nova': 'Bossa Nova', 'hyperpop': 'Hyperpop',
               'vaporwave': 'Vaporwave', 'eurodance': 'Eurodance', 'breakcore': 'Breakcore', 'moombahton': 'Moombahton',
               'afrobeats': 'Afrobeats', 'amapiano': 'Amapiano', 'reggaeton': 'Reggaeton', 'adventure': 'Adventure / Fantasy',
               'tension': 'Dark Tension'})


# ----------------------------------------------------------------------------- authentic sampled versions
# When the sampled sound library is installed, these parts are played by real recorded instruments.
ACOUSTIC_MAP = {
    'rock': {'bass': 'fingerbass', 'chords': 'odguitar', 'arp': 'cleanguitar', 'lead': 'odguitar'},
    'metal': {'bass': 'pickbass', 'chords': 'distguitar', 'arp': 'distguitar', 'lead': 'distguitar'},
    'blues': {'bass': 'fingerbass', 'arp': 'cleanguitar', 'lead': 'odguitar'},
    'jazz': {'bass': 'acbass', 'lead': 'mutedtrumpet'},
    'bossa_nova': {'bass': 'acbass', 'chords': 'nylon', 'pad': 'slowstrings'},
    'folk': {'bass': 'acbass', 'pad': 'slowstrings'},
    'funk': {'bass': 'slapbass', 'chords': 'muted', 'arp': 'cleanguitar'},
    'disco': {'bass': 'fingerbass', 'chords': 'cleanguitar', 'pad': 'strings'},
    'pop': {'bass': 'fingerbass', 'arp': 'cleanguitar'},
    'city_pop': {'bass': 'slapbass', 'arp': 'cleanguitar', 'lead': 'tenorsax'},
    'reggae': {'bass': 'fingerbass', 'arp': 'muted'},
    'boombap': {'bass': 'acbass'},
    'neoclassical': {'chords': 'slowstrings'},
    'cinematic': {'bass': 'cello'}, 'adventure': {'bass': 'cello'}, 'orchestral': {'bass': 'cello'},
    'tension': {'bass': 'contrabass'}, 'film_piano': {'bass': 'cello', 'chords': 'slowstrings'},
    'chamber': {'chords': 'viola'},
    'baroque': {'pad': 'slowstrings'},
    'fantasy_rpg': {'pad': 'horn'},
    'hybrid_trailer': {'pad': 'trombone'},
    'orchestral_hiphop': {'pad': 'strings'},
    'symphonic_metal': {'bass': 'pickbass', 'chords': 'distguitar'},
    'holiday': {'bass': 'acbass', 'lead': 'brass'},
    'western': {'bass': 'acbass', 'chords': 'cleanguitar', 'arp': 'cleanguitar', 'lead': 'trumpet'},
    'chamber_pop': {'bass': 'fingerbass'},
}
# which recorded drum kit suits each acoustic genre (GS kits: acoustic=Standard, room, rock=Power, jazz, brush, orchestra)
ACOUSTIC_KIT = {'rock': 'rock', 'metal': 'rock', 'blues': 'room', 'jazz': 'brush', 'bossa_nova': 'brush', 'folk': 'room',
                'funk': 'acoustic', 'disco': 'acoustic', 'pop': 'acoustic', 'city_pop': 'acoustic', 'reggae': 'room',
                'symphonic_metal': 'rock', 'holiday': 'brush', 'western': 'room', 'chamber_pop': 'acoustic'}
POWER_CHORDS = {'rock', 'metal', 'symphonic_metal'}
GENTLE_MASTER = {'jazz', 'bossa_nova', 'folk', 'blues', 'holiday', 'western'}   # plus every Orchestral style


def styles_by_category():
    out = {c: [] for c in CATEGORIES}
    for k, v in STYLES.items():
        out[v['category']].append(k)
    return out


# arrangements that fit the genre better than the generic EDM build/drop form
for _n, _f in {'techno': 'groove', 'minimal': 'groove', 'tech_house': 'groove', 'acid_house': 'groove',
               'dnb': 'dnb', 'jungle': 'dnb', 'amapiano': 'amapiano', 'ukgarage': 'garage'}.items():
    if _n in STYLES:
        STYLES[_n]['form'] = _f


# ----------------------------------------------------------------------------- per-genre instrument pools
# Every song picks each part's instrument from its genre's own pool (the style's default comes first and is the most
# likely pick), so a genre keeps its identity while songs don't all sound like the same preset. 'sf:' names are real
# recorded instruments from the sound library (they fall back to the closest built-in sound if it isn't installed).
# Parts not listed keep the style's instrument. With genre VSTs installed, whatever is picked here is then played by the
# best plugin for it (and the rig itself varies between the suitable plugins/patches you have).
POOLS = {
    # ---- electronic
    'house': dict(bass=['sawbass', 'fmbass', 'sinebass'], chords=['stab', 'organ', 'epiano', 'piano', 'pluck_saw'],
                  pad=['supersaw', 'warmpad', 'strings'], arp=['pluck_saw', 'bell', 'marimba', 'epiano'],
                  lead=['pluck', 'vox', 'piano', 'bell', 'organ']),
    'deep_house': dict(bass=['sinebass', 'fmbass', 'sf:fingerbass'], chords=['organ', 'epiano', 'piano', 'stab'],
                       pad=['warmpad', 'strings', 'choir'], arp=['epiano', 'marimba', 'bell', 'kalimba'],
                       lead=['vox', 'epiano', 'sax', 'flute', 'bell']),
    'tech_house': dict(bass=['fmbass', 'sawbass', 'sinebass'], chords=['organ', 'stab', 'epiano'],
                       arp=['pluck_saw', 'bell', 'marimba'], lead=['vox', 'pluck_saw', 'organ', 'bell']),
    'progressive_house': dict(bass=['sawbass', 'fmbass'], chords=['supersaw', 'pluck_saw', 'piano', 'stab'],
                              pad=['warmpad', 'strings', 'supersaw', 'choir'], arp=['pluck_saw', 'bell', 'pluck'],
                              lead=['supersaw_lead', 'pluck', 'leadsaw', 'piano']),
    'trance': dict(bass=['sawbass', 'fmbass'], chords=['supersaw', 'stab', 'pluck_saw'], pad=['strings', 'warmpad', 'choir', 'supersaw'],
                   arp=['pluck_saw', 'bell', 'pluck', 'acid'], lead=['supersaw_lead', 'leadsaw', 'pluck_saw', 'bell']),
    'psytrance': dict(bass=['sawbass', 'fmbass'], chords=['stab', 'warmpad'], pad=['warmpad', 'choir'],
                      arp=['acid', 'pluck_saw', 'bell'], lead=['acid', 'leadsaw', 'hoover', 'bell']),
    'techno': dict(bass=['sawbass', 'fmbass', 'reese'], chords=['stab', 'organ', 'warmpad', 'bell'], pad=['warmpad', 'strings', 'choir'],
                   arp=['pluck_saw', 'bell', 'acid', 'marimba'], lead=['bell', 'acid', 'leadsaw', 'vox', 'stab']),
    'minimal': dict(bass=['sinebass', 'fmbass', 'sawbass'], chords=['stab', 'bell', 'marimba', 'organ'],
                    arp=['pluck_saw', 'bell', 'marimba', 'kalimba'], lead=['bell', 'marimba', 'vox', 'kalimba']),
    'acid_house': dict(chords=['organ', 'stab', 'piano'], pad=['warmpad', 'strings'], arp=['pluck_saw', 'acid', 'bell'],
                       lead=['hoover', 'acid', 'piano', 'vox', 'stab']),
    'synthwave': dict(bass=['sawbass', 'fmbass'], chords=['supersaw', 'brass', 'stab', 'epiano', 'warmpad'],
                      pad=['warmpad', 'strings', 'choir'], arp=['pluck_saw', 'bell', 'chip'],
                      lead=['leadsaw', 'supersaw_lead', 'sax', 'softlead', 'brass']),
    'synthpop': dict(bass=['sawbass', 'fmbass', 'chipbass'], chords=['pluck_saw', 'stab', 'epiano', 'piano', 'brass'],
                     pad=['strings', 'warmpad', 'choir'], arp=['bell', 'pluck_saw', 'marimba', 'chip'],
                     lead=['leadsaw', 'pluck', 'bell', 'softlead', 'vox', 'brass']),
    'electro': dict(bass=['fmbass', 'sawbass', 'acid'], chords=['stab', 'brass', 'pluck_saw'], arp=['chip', 'pluck_saw', 'bell'],
                    lead=['leadsaw', 'chip', 'vox', 'acid']),
    'bigroom': dict(bass=['fmbass', 'sawbass', 'reese'], chords=['supersaw', 'stab', 'pluck_saw'], pad=['warmpad', 'supersaw', 'choir'],
                    arp=['pluck_saw', 'bell'], lead=['hoover', 'supersaw_lead', 'leadsaw', 'pluck_saw']),
    'hardstyle': dict(bass=['sawbass', 'fmbass'], chords=['supersaw', 'stab'], pad=['choir', 'strings', 'warmpad'],
                      arp=['pluck_saw', 'bell'], lead=['supersaw_lead', 'hoover', 'leadsaw']),
    'future_bass': dict(chords=['supersaw', 'pluck_saw', 'stab', 'epiano'], pad=['warmpad', 'vox', 'choir'],
                        arp=['bell', 'pluck_saw', 'chip', 'kalimba'], lead=['vox', 'supersaw_lead', 'bell', 'pluck', 'chip']),
    'dubstep': dict(bass=['wobble', 'reese', 'growl'], chords=['warmpad', 'supersaw', 'strings'], pad=['choir', 'warmpad', 'strings'],
                    arp=['bell', 'pluck_saw', 'celesta'], lead=['hoover', 'leadsaw', 'vox', 'bell', 'supersaw_lead']),
    'trap': dict(chords=['pluck', 'piano', 'epiano', 'harp', 'strings', 'sf:nylon'], pad=['warmpad', 'strings', 'choir', 'vox'],
                 lead=['bell', 'piano', 'pluck', 'flute', 'celesta', 'vox', 'violin']),
    'phonk': dict(chords=['warmpad', 'organ', 'strings'], pad=['choir', 'warmpad', 'glasspad'], arp=['vox', 'phonkbell'],
                  lead=['cowbell']),      # the pitched cowbell IS the genre
    'ukgarage': dict(bass=['sinebass', 'reese', 'fmbass'], chords=['organ', 'epiano', 'stab', 'piano'], pad=['warmpad', 'strings'],
                     arp=['epiano', 'bell', 'marimba'], lead=['vox', 'pluck', 'bell', 'epiano']),
    'dnb': dict(bass=['reese', 'sawbass', 'sinebass', 'fmbass'], chords=['epiano', 'warmpad', 'piano', 'strings', 'stab'],
                pad=['supersaw', 'warmpad', 'strings', 'choir'], arp=['bell', 'pluck_saw', 'epiano'],
                lead=['leadsaw', 'vox', 'pluck', 'bell', 'supersaw_lead']),
    'jungle': dict(bass=['sinebass', 'reese'], chords=['stab', 'warmpad', 'organ', 'strings', 'epiano'], pad=['warmpad', 'strings', 'choir'],
                   arp=['bell', 'marimba', 'pluck_saw'], lead=['vox', 'flute', 'sax', 'bell', 'pluck']),
    'downtempo': dict(bass=['sinebass', 'sf:fingerbass', 'sf:acbass'], chords=['epiano', 'piano', 'sf:nylon', 'guitar', 'harp'],
                      pad=['warmpad', 'strings', 'choir'], arp=['bell', 'kalimba', 'marimba', 'harp', 'celesta'],
                      lead=['softlead', 'flute', 'sax', 'vox', 'piano', 'cello']),
    'lofi': dict(bass=['sinebass', 'sf:acbass', 'sf:fingerbass'], chords=['epiano', 'piano', 'sf:nylon', 'guitar', 'organ'],
                 lead=['pluck', 'piano', 'epiano', 'flute', 'sax', 'kalimba', 'bell', 'sf:cleanguitar']),
    'ambient': dict(chords=['epiano', 'piano', 'harp', 'strings', 'warmpad'], pad=['warmpad', 'strings', 'choir', 'tremolo'],
                    arp=['bell', 'celesta', 'kalimba', 'harp', 'marimba'], lead=['softlead', 'flute', 'piano', 'cello', 'vox']),
    'afrobeats': dict(bass=['sinebass', 'sf:fingerbass', 'fmbass'], chords=['guitar', 'sf:cleanguitar', 'piano', 'epiano', 'organ'],
                      pad=['warmpad', 'strings'], arp=['marimba', 'kalimba', 'steeldrum', 'guitar', 'bell'],
                      lead=['vox', 'flute', 'sax', 'pluck', 'marimba']),
    'amapiano': dict(chords=['piano', 'epiano', 'organ'], pad=['warmpad', 'strings', 'choir'], arp=['kalimba', 'marimba', 'bell'],
                     lead=['flute', 'sax', 'vox', 'piano', 'kalimba']),
    'reggaeton': dict(chords=['pluck_saw', 'guitar', 'sf:nylon', 'piano', 'stab'], pad=['warmpad', 'strings'],
                      arp=['marimba', 'pluck', 'bell', 'steeldrum'], lead=['pluck', 'vox', 'flute', 'leadsaw', 'sf:nylon']),
    'moombahton': dict(bass=['fmbass', 'sawbass'], chords=['stab', 'supersaw', 'pluck_saw'], pad=['supersaw', 'warmpad'],
                       arp=['pluck_saw', 'marimba', 'steeldrum'], lead=['hoover', 'leadsaw', 'vox', 'flute']),
    'uk_drill': dict(chords=['piano', 'strings', 'spiccato', 'bell'], pad=['strings', 'choir', 'tremolo'], arp=['bell', 'pizz', 'celesta'],
                     lead=['strings', 'violin', 'piano', 'bell', 'choir', 'flute']),
    'hyperpop': dict(chords=['supersaw', 'pluck_saw', 'chip'], pad=['vox', 'warmpad'], arp=['chip', 'bell'],
                     lead=['supersaw_lead', 'chip', 'vox', 'leadsaw']),
    'vaporwave': dict(bass=['sinebass', 'fmbass'], chords=['epiano', 'warmpad', 'organ'], pad=['warmpad', 'strings', 'choir'],
                      lead=['sax', 'epiano', 'softlead', 'vox', 'sf:tenorsax']),
    'eurodance': dict(bass=['sawbass', 'fmbass'], chords=['piano', 'stab', 'supersaw', 'organ'], pad=['strings', 'warmpad', 'choir'],
                      arp=['pluck_saw', 'bell'], lead=['supersaw_lead', 'leadsaw', 'piano', 'vox', 'pluck_saw']),
    'breakcore': dict(bass=['reese', 'sawbass'], chords=['warmpad', 'piano', 'strings', 'supersaw'], pad=['strings', 'choir', 'warmpad'],
                      arp=['chip', 'bell', 'piano', 'celesta'], lead=['piano', 'chip', 'vox', 'violin', 'bell']),
    'orchestral_hiphop': dict(chords=['spiccato', 'strings', 'piano', 'brass'], pad=['strings', 'choir', 'tremolo', 'horn'],
                              arp=['pizz', 'celesta', 'harp', 'bell'], lead=['violin', 'horn', 'piano', 'choir', 'cello', 'flute']),
    # ---- classic
    'disco': dict(bass=['sawbass', 'sf:fingerbass', 'sf:slapbass'], chords=['guitar', 'sf:cleanguitar', 'sf:muted', 'epiano', 'piano', 'clav'],
                  pad=['strings', 'sf:slowstrings', 'organ'], arp=['epiano', 'guitar', 'piano', 'clav'],
                  lead=['brass', 'sf:trumpet', 'strings', 'flute', 'sax', 'violin']),
    'funk': dict(bass=['sawbass', 'sf:slapbass', 'sf:fingerbass', 'fmbass'], chords=['pluck', 'clav', 'sf:muted', 'guitar', 'epiano', 'organ'],
                 pad=['organ', 'brass', 'strings'], arp=['guitar', 'clav', 'epiano'],
                 lead=['brass', 'sax', 'sf:tenorsax', 'sf:trumpet', 'organ', 'flute']),
    'pop': dict(bass=['sawbass', 'sf:fingerbass', 'sinebass'], chords=['piano', 'guitar', 'sf:cleanguitar', 'epiano', 'pluck_saw'],
                pad=['strings', 'warmpad', 'organ'], arp=['guitar', 'sf:cleanguitar', 'bell', 'piano', 'pizz', 'celesta'],
                lead=['pluck', 'piano', 'guitar', 'bell', 'vox', 'violin', 'flute']),
    'rock': dict(bass=['pluck', 'sf:fingerbass', 'sf:pickbass'], chords=['guitar', 'sf:odguitar', 'sf:distguitar'],
                 pad=['organ', 'strings', 'warmpad'], arp=['guitar', 'piano', 'sf:cleanguitar'], lead=['guitar', 'sf:odguitar', 'organ']),
    'jazz': dict(bass=['pluck', 'sf:acbass'], chords=['piano', 'epiano', 'guitar', 'organ'], arp=['piano', 'guitar', 'epiano'],
                 lead=['brass', 'sax', 'sf:tenorsax', 'sf:mutedtrumpet', 'piano', 'guitar', 'flute', 'clarinet']),
    'boombap': dict(bass=['sinebass', 'sf:acbass'], chords=['piano', 'epiano', 'strings', 'organ', 'harp', 'guitar'],
                    lead=['strings', 'piano', 'flute', 'sax', 'brass', 'horn', 'bell']),
    'reggae': dict(bass=['sinebass', 'sf:fingerbass'], chords=['organ', 'guitar', 'piano', 'epiano'], arp=['guitar', 'sf:muted', 'organ'],
                   lead=['softlead', 'flute', 'brass', 'sax', 'organ', 'sf:trumpet']),
    'city_pop': dict(bass=['fmbass', 'sf:slapbass', 'sf:fingerbass'], chords=['epiano', 'piano', 'guitar', 'brass'], pad=['strings', 'warmpad'],
                     arp=['guitar', 'sf:cleanguitar', 'epiano', 'bell', 'marimba'], lead=['sax', 'sf:tenorsax', 'brass', 'leadsaw', 'epiano', 'flute']),
    'bossa_nova': dict(bass=['pluck', 'sf:acbass'], chords=['guitar', 'sf:nylon', 'piano', 'epiano'], pad=['strings', 'warmpad'],
                       arp=['piano', 'guitar', 'sf:nylon'], lead=['flute', 'sax', 'clarinet', 'piano', 'sf:nylon', 'vox']),
    'blues': dict(bass=['pluck', 'sf:fingerbass', 'sf:acbass'], chords=['piano', 'organ', 'guitar'], pad=['organ', 'brass'],
                  arp=['guitar', 'piano'], lead=['guitar', 'sf:odguitar', 'sax', 'sf:tenorsax', 'organ', 'piano', 'brass']),
    'metal': dict(bass=['pluck', 'sf:pickbass'], chords=['guitar', 'sf:distguitar'], arp=['guitar', 'sf:distguitar', 'spiccato'],
                  lead=['guitar', 'sf:distguitar']),
    'folk': dict(bass=['pluck', 'sf:acbass'], chords=['guitar', 'sf:nylon', 'piano', 'harp'], pad=['strings', 'sf:slowstrings', 'organ'],
                 arp=['piano', 'guitar', 'sf:nylon', 'harp'], lead=['flute', 'violin', 'clarinet', 'oboe', 'guitar', 'sf:nylon', 'piano']),
    'symphonic_metal': dict(bass=['pluck', 'sf:pickbass'], chords=['guitar', 'sf:distguitar'], pad=['choir', 'strings', 'organ', 'horn', 'tremolo'],
                            arp=['spiccato', 'harp', 'piano', 'pizz'], lead=['violin', 'guitar', 'sf:distguitar', 'choir', 'horn', 'flute']),
    'holiday': dict(bass=['pluck', 'sf:acbass'], chords=['piano', 'epiano', 'guitar', 'harp', 'strings'], pad=['strings', 'organ', 'choir', 'horn'],
                    arp=['celesta', 'bell', 'pizz', 'harp', 'marimba'],
                    lead=['brass', 'flute', 'clarinet', 'violin', 'celesta', 'sax', 'sf:trumpet', 'oboe']),
    'western': dict(bass=['pluck', 'sf:acbass', 'cello'], chords=['guitar', 'sf:cleanguitar', 'sf:nylon', 'harp'],
                    pad=['choir', 'strings', 'tremolo', 'organ'], arp=['guitar', 'harp', 'sf:nylon', 'pizz'],
                    lead=['brass', 'sf:trumpet', 'flute', 'violin', 'guitar', 'sf:cleanguitar', 'cello', 'oboe']),
    'chamber_pop': dict(bass=['pluck', 'sf:fingerbass', 'cello'], chords=['piano', 'guitar', 'epiano', 'harp', 'spiccato'],
                        pad=['strings', 'sf:slowstrings', 'horn', 'organ'], arp=['pizz', 'celesta', 'harp', 'bell', 'marimba', 'spiccato'],
                        lead=['violin', 'flute', 'horn', 'cello', 'piano', 'oboe', 'clarinet']),
    # ---- orchestral
    'cinematic': dict(bass=['strings', 'cello', 'sf:contrabass', 'spiccato'], chords=['spiccato', 'strings', 'tremolo'],
                      pad=['choir', 'horn', 'strings', 'braam', 'tremolo'], arp=['pizz', 'spiccato', 'harp', 'celesta'],
                      lead=['horn', 'brass', 'violin', 'choir', 'cello', 'sf:trumpet']),
    'orchestral': dict(bass=['strings', 'cello', 'sf:contrabass', 'pizz'], chords=['strings', 'sf:slowstrings', 'harp', 'tremolo'],
                       pad=['horn', 'choir', 'strings', 'clarinet'], arp=['harp', 'pizz', 'celesta', 'flute'],
                       lead=['violin', 'flute', 'oboe', 'clarinet', 'cello', 'horn']),
    'film_piano': dict(bass=['strings', 'cello'], chords=['strings', 'sf:slowstrings', 'tremolo'], pad=['choir', 'strings', 'horn'],
                       arp=['piano', 'harp', 'celesta'], lead=['piano', 'cello', 'violin', 'oboe']),
    'adventure': dict(bass=['strings', 'cello', 'spiccato'], chords=['spiccato', 'strings'], pad=['horn', 'choir', 'strings'],
                      arp=['harp', 'pizz', 'spiccato', 'celesta'], lead=['brass', 'horn', 'sf:trumpet', 'violin', 'flute']),
    'tension': dict(bass=['strings', 'cello', 'tremolo', 'sf:contrabass'], chords=['tremolo', 'strings'], pad=['choir', 'tremolo', 'horn', 'braam'],
                    arp=['celesta', 'harp', 'pizz', 'bell'], lead=['violin', 'cello', 'oboe', 'clarinet', 'choir']),
    'neoclassical': dict(bass=['cello', 'strings'], chords=['strings', 'sf:slowstrings', 'tremolo'], arp=['piano', 'harp', 'celesta'],
                         lead=['piano', 'cello', 'violin']),
    'chamber': dict(bass=['cello', 'pizz'], chords=['strings', 'sf:viola'], arp=['pizz', 'harp'],
                    lead=['violin', 'cello', 'flute', 'oboe', 'clarinet']),
    'baroque': dict(bass=['cello', 'sf:bassoon'], chords=['harpsichord', 'strings', 'organ'], pad=['strings', 'organ'],
                    arp=['spiccato', 'harpsichord', 'harp'], lead=['violin', 'oboe', 'flute', 'harpsichord', 'sf:trumpet']),
    'fantasy_rpg': dict(bass=['cello', 'strings', 'pizz', 'harp'], chords=['strings', 'harp', 'piano'], pad=['horn', 'choir', 'strings'],
                        arp=['harp', 'celesta', 'pizz', 'marimba', 'kalimba'],
                        lead=['flute', 'oboe', 'violin', 'clarinet', 'sf:piccolo', 'horn', 'celesta']),
    'hybrid_trailer': dict(bass=['sawbass', 'reese', 'fmbass', 'cello'], chords=['spiccato', 'strings'], pad=['braam', 'choir', 'horn', 'sf:trombone'],
                           arp=['spiccato', 'pizz', 'bell'], lead=['horn', 'choir', 'brass', 'violin', 'cello']),
}


# ============================== MORE GENRES (v1.10) =========================
# Triple and compound meters: 12-step patterns. In 3/4 and 6/8 one bar of the engine holds two bars of music
# (form_scale halves the section lengths to match); in 12/8 it holds one. 'bpm' counts the engine's beat - a dotted
# quarter (the felt pulse of 6/8 and 12/8; in 3/4 the app also shows the quarter-note tempo).

style('waltz', 'Orchestral', 'Viennese waltz (3/4): oom-pah-pah strings, lilting violin melody, harp and woodwind colours',
      meter='3/4', bpm=(96, 124), scales=['major', 'minor'], human=0.012, form='orchestral', form_scale=1, reverb=3.0,
      progs={'major': [[0, 4, 4, 0], [0, 3, 4, 0], [0, 1, 4, 0], [0, 5, 1, 4]], 'minor': [[0, 4, 4, 0], [0, 3, 4, 0], [0, 5, 3, 4]]},
      chord_size=3, chord_bars=1, drums={'timp': ['X...........', 'X.....X.....']}, kick_track='timp',
      bass=['R.....F.....', 'R.....R.....', 'R.....O.....'], bass_lo=33, bass_gate=0.5,
      chord_rh=['..x.x...x.x.', '..x.x...x.x-'], chord_center=62, arp=dict(rate=1, mode='updown', oct=5, prob=0.7),
      lead_rh=['x---x-x-x---', 'x-----x---x-', 'x-x-x-x-----', 'x---------x-', 'x-xx-xx-----'], lead_oct=5,
      gm_hint='Violins (melody); String section short (pah-pah); Celli + basses (oom); Harp; Flute / clarinet',
      tracks=[T('timp', 'kick', 'timp', rev=0.4, db=-26),
              T('bass', 'bass', 'cello', rev=0.35, db=-19, p=dict(a=0.03)),
              T('chords', 'chords', 'spiccato', rev=0.35, db=-22, p=dict(len=0.3)),
              T('arp', 'arp', 'harp', rev=0.4, pan=-0.3, db=-26),
              T('lead', 'lead', 'violin', rev=0.4, pan=0.15, db=-17)],
      master=dict(lufs=-15.0, air=1.2, low=0.6))

style('celtic_jig', 'Classic', 'Celtic jig (6/8): fiddle and tin whistle tunes, bodhran pulse, bouncing guitar and bass',
      meter='6/8', bpm=(104, 124), scales=['major', 'mixolydian', 'dorian'], human=0.008, kit='soft', form='song', form_scale=1,
      progs={'major': [[0, 3, 4, 0], [0, 4, 0, 4], [0, 0, 3, 4], [0, 5, 3, 4]], 'mixolydian': [[0, 6, 0, 6], [0, 3, 6, 0]],
             'dorian': [[0, 6, 0, 6], [0, 3, 0, 6]]},
      drums={'tom': ['X.xX.xX.xX.x', 'X..X.xX..X.x'], 'tamb': ['...x.....x..'], 'kick': ['X.....X.....']},
      kick_track='kick', snare_tracks=['tom'],
      bass=['R.....F.....', 'R..F..R..F..'], bass_lo=31, bass_gate=0.7,
      chord_rh=['x.xx.xx.xx.x', 'x..x..x..x..'], chord_center=58, arp=dict(rate=1, mode='updown', oct=5, prob=0.5),
      lead_rh=['xxxxxxxxxxxx', 'x-xx-xx-xx-x', 'xxx-xxxxx-x-', 'x-xxxxx-xx-x'], lead_oct=5,
      gm_hint='Fiddle / tin whistle (tune); Bodhran; Acoustic guitar or bouzouki; Upright bass',
      tracks=[T('kick', 'kick', 'kick', db=-22), T('tom', 'snare', 'tom', rev=0.25, db=-19), T('tamb', 'top', 'tamb', pan=0.3, db=-30),
              T('bass', 'bass', 'pluck', db=-17, p=dict(bright=1200, damp=0.996)),
              T('chords', 'chords', 'guitar', pan=-0.25, rev=0.25, db=-22, p=dict(bright=5000)),
              T('arp', 'arp', 'harp', rev=0.3, pan=0.3, db=-27),
              T('lead', 'lead', 'violin', rev=0.3, db=-17, p=dict(vib=8))],
      master=dict(lufs=-12.0, air=1.4, low=0.8))

style('soul_ballad', 'Classic', 'Soul / doo-wop ballad (12/8): triplet piano, slow backbeat, organ and strings, a big vocal-style lead',
      meter='12/8', bpm=(48, 66), scales=['major'], human=0.01, kit='soft', form='song', form_scale=0.5, reverb=2.6,
      progs=[[0, 5, 3, 4], [0, 5, 1, 4], [0, 3, 4, 0], [0, 2, 3, 4]], chord_size=4,
      drums={'kick': ['X.....X..X..', 'X.....X.....'], 'snare': ['...X.....X..'], 'chat': ['xxxxxxxxxxxx'],
             'ride': ['x..x..x..x..']}, snare_tracks=['snare'],
      bass=['R.....R..F..', 'R..R..F..A..', 'R.....F.....'], bass_lo=31,
      chord_rh=['xxxxxxxxxxxx', 'x..x..x..x..', 'x.xx.xx.xx.x'], chord_center=62,
      lead_rh=['x--x--x--...', 'x-xx-xx-x...', 'x-----x-xx..', 'x--x-xx-....'], fill=True,
      gm_hint='Piano (triplets); Hammond organ; Strings; Saxophone or vocal lead; Bass guitar',
      tracks=[T('kick', 'kick', 'kick', db=-19), T('snare', 'snare', 'snare', rev=0.35, db=-19), T('chat', 'top', 'chat', db=-30),
              T('ride', 'top', 'ride', db=-31), T('bass', 'bass', 'pluck', db=-16, p=dict(bright=1200)),
              T('chords', 'chords', 'piano', rev=0.3, db=-21), T('pad', 'pad', 'organ', rev=0.3, db=-27),
              T('lead', 'lead', 'sax', rev=0.35, db=-18)],
      master=dict(lufs=-12.0, air=1.2, low=1.0))

# ---- band, roots and latin
style('gospel', 'Classic', 'Gospel: Hammond organ and piano, choir, hand claps, swinging backbeat and a preaching lead',
      bpm=(70, 120), scales=['major'], swing=0.6, swing_unit=16, human=0.008, kit='acoustic', form='song_b', chord_size=4,
      progs=[[0, 3, 0, 4], [3, 4, 2, 5], [0, 5, 1, 4], [3, 3, 0, 5], [0, 2, 3, 4]],
      drums={'kick': ['X.....X.X.......', 'X.......X.x.....'], 'snare': [BACKBEAT], 'clap': [BACKBEAT],
             'chat': ['x.x.x.x.x.x.x.x.'], 'tamb': ['....x.......x...']}, snare_tracks=['snare', 'clap'], ghosts=True, fill=True,
      bass=['R...R.F.R...A...', 'R..R..F.R..R.A..', 'R-..F-..R-..A...'], bass_lo=28,
      chord_rh=['x--.x--.x--.x---', '..x...x...x...x.', 'x---x---x---x---'], chord_center=62,
      lead_rh=['x-x-x---x-x-x---', 'x---x-x-x-------', '..x-x-x-x---x---', 'x-.x-.x-x-------'],
      gm_hint='Hammond B3 organ (Leslie); Piano; Choir; Bass; Hand claps',
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.3), T('clap', 'snare', 'clap', rev=0.35, db=-20),
              T('chat', 'top', 'chat', db=-28), T('tamb', 'top', 'tamb', pan=0.3, db=-29),
              T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1100)),
              T('chords', 'chords', 'organ', pan=-0.2, rev=0.25, p=dict(leslie=6.0)),
              T('pad', 'pad', 'choir', rev=0.4, db=-24),
              T('arp', 'arp', 'piano', rev=0.25, pan=0.25, db=-24),
              T('lead', 'lead', 'piano', rev=0.3, db=-18)],
      master=dict(lufs=-11.0, air=1.4, low=1.0))

style('country', 'Classic', 'Country: train-beat drums, boom-chick bass, strummed acoustic, fiddle and twangy guitar licks',
      bpm=(92, 132), scales=['major', 'mixolydian'], human=0.008, kit='soft', form='song', strum=0.012,
      progs={'major': [[0, 3, 4, 0], [0, 4, 3, 0], [0, 0, 3, 4], [0, 5, 3, 4], [3, 0, 4, 0]], 'mixolydian': [[0, 6, 3, 0]]},
      drums={'kick': ['X.......X.......', 'X...X...X...X...'], 'snare': [BACKBEAT, 'x.x.X.x.x.x.X.x.'], 'chat': ['x.x.x.x.x.x.x.x.']},
      snare_tracks=['snare'], bass=['R...F...R...F...', 'R...F...R.F.A...', 'R.......F.......'], bass_lo=31,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x...x.x.x...x.x.', 'x---x---x---x---'], chord_center=57,
      arp=dict(rate=2, mode='updown', oct=4, prob=0.5),
      lead_rh=['x-x-x---x-x-....', 'x---x-x-x---....', 'x-x-x-x-x---x...', '..x-x-x-x---....'], fill=True,
      gm_hint='Acoustic steel guitar (strum); Telecaster licks; Fiddle; Pedal steel; Upright / electric bass',
      tracks=[T('kick', 'kick', 'kick', db=-17), T('snare', 'snare', 'snare', rev=0.25, db=-19), T('chat', 'top', 'chat', db=-28),
              T('bass', 'bass', 'pluck', db=-16, p=dict(bright=1300, damp=0.996)),
              T('chords', 'chords', 'guitar', pan=-0.25, rev=0.2, p=dict(bright=5500)),
              T('arp', 'arp', 'guitar', pan=0.3, rev=0.25, db=-25, p=dict(bright=7000)),
              T('lead', 'lead', 'violin', rev=0.3, db=-18, p=dict(vib=12))],
      master=dict(lufs=-11.0, air=1.5, low=0.9))

style('bluegrass', 'Classic', 'Bluegrass: banjo rolls, fiddle breakdowns, mandolin chop on the offbeat, driving upright bass',
      bpm=(112, 150), scales=['major', 'mixolydian'], human=0.006, form='song',
      progs={'major': [[0, 3, 4, 0], [0, 0, 3, 0], [0, 4, 0, 4], [0, 3, 0, 4]], 'mixolydian': [[0, 6, 0, 0]]},
      drums={}, bass=['R...F...R...F...', 'R...F...R...A...'], bass_lo=31, bass_gate=0.6,
      chord_rh=['....x.......x...', '..x...x...x...x.'], chord_center=62,
      arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x.x.x.x.x.x.x.x.', 'x.x.x-x.x.x.x---', 'xx.x.x.xx.x.x.x.', 'x-x-x-x-x.x.x---'],
      gm_hint='Banjo (rolls); Fiddle (lead); Mandolin chop; Acoustic guitar; Upright bass',
      tracks=[T('bass', 'bass', 'pluck', db=-16, p=dict(bright=1100, damp=0.995)),
              T('chords', 'chords', 'guitar', pan=0.25, rev=0.15, db=-22, p=dict(bright=7000, damp=0.985)),
              T('arp', 'arp', 'banjo', pan=-0.3, rev=0.15, db=-24),
              T('lead', 'lead', 'violin', rev=0.25, db=-17, p=dict(vib=8))],
      master=dict(lufs=-12.0, air=1.5, low=0.6))

style('motown', 'Classic', 'Motown / 60s soul: tambourine on every backbeat, melodic bass, piano and guitar chops, strings and horns',
      bpm=(100, 126), scales=['major', 'minor'], human=0.008, kit='acoustic', form='song', chord_size=4,
      progs={'major': [[0, 5, 3, 4], [0, 3, 1, 4], [0, 2, 3, 4], [3, 4, 0, 5]], 'minor': [[0, 3, 6, 4], [0, 6, 5, 4]]},
      drums={'kick': ['X.......X.X.....', 'X...X...X...X...'], 'snare': [BACKBEAT], 'tamb': ['....x.......x...', 'x.x.x.x.x.x.x.x.'],
             'chat': ['x.x.x.x.x.x.x.x.']}, snare_tracks=['snare'], fill=True,
      bass=['R..R.R..F..A....', 'R...R..RF...A.R.', 'R.R...R.F.F.A...'], bass_lo=28,
      chord_rh=['....x.......x...', 'x---x---x---x---', '..x...x...x...x.'], chord_center=62,
      arp=dict(rate=2, mode='up', oct=5, prob=0.5),
      lead_rh=['x-x-x---x-x-x---', 'x---x-x-x-------', '..x-x-x-x---x---', 'x-x-x-x-x-------'],
      gm_hint='Bass guitar (melodic, Jamerson-style); Piano; Rhythm guitar; Strings; Horn section; Tambourine',
      tracks=[T('kick', 'kick', 'kick', db=-17), T('snare', 'snare', 'snare', rev=0.3), T('tamb', 'top', 'tamb', pan=0.3, db=-25),
              T('chat', 'top', 'chat', db=-29), T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1000, damp=0.996)),
              T('chords', 'chords', 'piano', rev=0.25, db=-22), T('pad', 'pad', 'strings', rev=0.4, db=-25),
              T('arp', 'arp', 'guitar', pan=-0.3, db=-26), T('lead', 'lead', 'brass', rev=0.3, db=-19)],
      master=dict(lufs=-11.0, air=1.3, low=1.0))

style('rnb', 'Classic', 'R&B / neo-soul: lazy swung drums, Rhodes 9th chords, deep sub bass, finger snaps and silky leads',
      bpm=(66, 98), scales=['minor', 'dorian', 'major'], swing=0.58, human=0.012, kit='soft', form='song_b', chord_size=5,
      progs={'minor': [[0, 5, 3, 4], [0, 3, 6, 5], [0, 6, 5, 3]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]],
             'major': [[1, 4, 0, 5], [3, 2, 1, 4], [3, 4, 2, 5]]},
      drums={'kick': ['X......X..X.....', 'X.....X...X..x..'], 'snare': [BACKBEAT], 'snap': [BACKBEAT],
             'chat': ['x.xxx.x.x.xxx.x.', 'x.x.x.x.x.x.x.xx']}, snare_tracks=['snare', 'snap'], ghosts=True,
      bass=['R-----..R---F...', 'R---..R-..F-A...', 'R-....R...R-....'], bass_lo=28,
      chord_rh=['x---------x-----', 'x-------..x-----', 'x--.....x--.....'], chord_center=62,
      lead_rh=['x-x-..x-x---....', '..x-x-x-x-x-....', 'x-.x-.x-x-------', 'x---x-x---......'],
      gm_hint='Rhodes / Wurlitzer; Sub or finger bass; Snaps; Pads; Vocal-style lead or guitar',
      tracks=[T('kick', 'kick', 'kick', db=-15), T('snare', 'snare', 'snare', rev=0.3, db=-18), T('snap', 'snare', 'snap', db=-22),
              T('chat', 'top', 'chat', db=-28), T('bass', 'bass', 'sinebass', db=-13, p=dict(cut=500)),
              T('chords', 'chords', 'epiano', rev=0.3, dly=0.15), T('pad', 'pad', 'warmpad', rev=0.4, db=-28),
              T('lead', 'lead', 'vox', rev=0.35, dly=0.2, db=-19)],
      master=dict(lufs=-11.0, air=1.4, low=1.8))

style('swing', 'Classic', 'Big-band swing: walking bass, ride and hi-hat on 2 & 4, brass section shouts, a sax solo',
      bpm=(132, 196), scales=['major', 'minor'], swing=0.66, swing_unit=8, human=0.01, chord_size=4,
      kit='acoustic', form='jazz', bass_mode='walk', bass_lo=28, ghosts=True,
      progs={'major': [[0, 5, 1, 4], [1, 4, 0, 0], [0, 3, 1, 4], [2, 5, 1, 4]], 'minor': [[0, 3, 4, 0], [0, 5, 3, 4]]},
      drums={'ride': ['x...x.x.x...x.x.'], 'chat': ['....x.......x...'], 'kick': ['o...o...o...o...'],
             'snare': ['................', '.......x......x.']}, snare_tracks=['snare'],
      chord_rh=['x-....x-........', '...x-.....x-....', 'x-..x-..x-..x-..', '....x-.....x-...'], chord_center=62,
      arp=dict(rate=2, mode='random', oct=5, prob=0.4),
      lead_rh=['x.x.x.x.x---....', '..x.x-x.x.x-....', 'x-.xx-x.x---x...', 'x---x-x-x-------'],
      gm_hint='Brass section (trumpets + trombones); Saxophones; Piano; Upright bass (walking); Ride cymbal',
      tracks=[T('ride', 'top', 'ride', pan=0.3, db=-23), T('chat', 'top', 'chat', pan=-0.2, db=-29),
              T('kick', 'kick', 'kick', db=-24), T('snare', 'snare', 'snare', db=-25),
              T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1200, damp=0.996)),
              T('chords', 'chords', 'brass', rev=0.25, db=-21),
              T('arp', 'arp', 'piano', rev=0.2, pan=0.25, db=-26),
              T('lead', 'lead', 'sax', rev=0.25, db=-18)],
      master=dict(lufs=-13.0, air=1.2, low=0.6))

style('ska', 'Classic', 'Ska: offbeat guitar & organ skank, fast walking bass, rimshot backbeat, punchy horn lines',
      bpm=(120, 164), scales=['major', 'minor'], human=0.006, kit='acoustic', form='song',
      progs={'major': [[0, 5, 1, 4], [0, 3, 4, 0], [0, 4, 3, 4]], 'minor': [[0, 3, 0, 4], [0, 5, 6, 4]]},
      drums={'kick': ['X.......X.......', 'X...X...X...X...'], 'snare': [BACKBEAT], 'rim': ['....x.......x...'],
             'chat': ['x.x.x.x.x.x.x.x.']}, snare_tracks=['snare'], fill=True,
      bass=['R.R.R.R.F.F.A.A.', 'R...R...F...A...', 'R.R.F.F.R.R.A.A.'], bass_lo=28, bass_gate=0.7,
      chord_rh=['..x...x...x...x.', '..x.x.x.x.x.x.x.'], chord_center=64,
      arp=dict(rate=2, mode='up', oct=5, prob=0.4),
      lead_rh=['x-x-x---x-x-x---', 'x.x.x-x.x---....', 'x---x-x-x-------', 'x-.x-.x-x-------'],
      gm_hint='Clean guitar skank; Organ (offbeats); Bass guitar; Trumpet + trombone + sax horns',
      tracks=[T('kick', 'kick', 'kick', db=-17), T('snare', 'snare', 'snare', rev=0.25), T('rim', 'snare', 'rim', db=-22),
              T('chat', 'top', 'chat', db=-28), T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1200)),
              T('chords', 'chords', 'guitar', pan=-0.25, db=-22, p=dict(bright=6000, damp=0.98)),
              T('pad', 'pad', 'organ', pan=0.25, db=-27),
              T('lead', 'lead', 'brass', rev=0.25, db=-18)],
      master=dict(lufs=-10.5, air=1.4, low=1.0))

style('punk', 'Classic', 'Punk rock: fast down-picked power chords, driving 8th-note bass, pounding drums, shouty guitar hooks',
      bpm=(160, 200), scales=['major', 'minor'], kit='hard', form='song', voicing='power', human=0.004,
      progs={'major': [[0, 3, 4, 0], [0, 4, 5, 3], [0, 3, 0, 4]], 'minor': [[0, 5, 6, 0], [0, 6, 5, 6]]},
      drums={'kick': ['X...X...X...X...', 'X.X...X.X.X...X.'], 'snare': [BACKBEAT, '..X...X...X...X.'], 'chat': ['x.x.x.x.x.x.x.x.'],
             'crash': ['X...............']}, snare_tracks=['snare'], fill=True,
      bass=['R.R.R.R.R.R.R.R.'], bass_lo=28, bass_gate=0.85,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x-x-x-x-x-x-x-x-'], chord_center=50,
      lead_rh=['x-x-x-x-x---x---', 'x---x---x-x-x---', 'x-x-x---x-x-x---'],
      gm_hint='Distorted guitars (down-picked); Bass guitar (8ths); Drums',
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.2, db=-15), T('chat', 'top', 'chat', db=-27),
              T('crash', 'top', 'crash', db=-28), T('bass', 'bass', 'pluck', db=-15, drive=0.5, p=dict(bright=2200, damp=0.997)),
              T('chords', 'chords', 'guitar', drive=1.4, pan=-0.2, p=dict(dist=22, bright=4500, damp=0.99)),
              T('lead', 'lead', 'guitar', drive=1.0, pan=0.2, rev=0.2, db=-18, p=dict(dist=14, bright=5000))],
      master=dict(lufs=-9.0, air=1.5, low=0.8))

style('indie_rock', 'Classic', 'Indie rock: jangly clean guitars in 8ths, melodic bass, straight-ahead drums, a hooky guitar lead',
      bpm=(108, 140), scales=['major', 'minor', 'mixolydian'], human=0.006, kit='punchy', form='song_b',
      progs={'major': [[0, 4, 5, 3], [3, 0, 4, 5], [0, 3, 5, 4], [5, 3, 0, 4]], 'minor': [[0, 5, 2, 6], [0, 3, 5, 6]],
             'mixolydian': [[0, 6, 3, 0]]},
      drums={'kick': ['X.......X.X.....', 'X...X...X..X....'], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.'],
             'ride': ['x.x.x.x.x.x.x.x.']}, snare_tracks=['snare'], fill=True,
      bass=['R.R.R.R.R.R.R.R.', 'R...R.R.R...A...', 'R.......R.R.A...'], bass_lo=28,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x.xx.xx.x.xx.xx.', 'x---x---x---x---'], chord_center=60,
      arp=dict(rate=2, mode='updown', oct=5, prob=0.8),
      lead_rh=['x-x-x---x-x-x---', 'x---x-x-x-------', '..x-x-x-x---x---', 'x-x-x-x-x---....'],
      gm_hint='Clean / chorus guitars (jangle); Arpeggiated lead guitar; Bass guitar; Drums; Synth or organ pad',
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.3), T('chat', 'top', 'chat', db=-28),
              T('ride', 'top', 'ride', db=-32), T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1800, damp=0.997)),
              T('chords', 'chords', 'guitar', pan=-0.25, rev=0.25, dly=0.15, p=dict(bright=6500, damp=0.992)),
              T('pad', 'pad', 'organ', rev=0.35, db=-29),
              T('arp', 'arp', 'guitar', pan=0.3, rev=0.3, dly=0.25, db=-24, p=dict(bright=7000)),
              T('lead', 'lead', 'guitar', rev=0.3, dly=0.2, db=-18, p=dict(dist=6, bright=5000))],
      master=dict(lufs=-10.0, air=1.6, low=1.0))

style('salsa', 'Classic', 'Salsa: clave and cowbell, conga tumbao, piano montuno, anticipated bass and a blazing trumpet section',
      bpm=(160, 200), scales=['minor', 'major', 'harmonic_minor'], human=0.006, kit='acoustic', form='song',
      progs={'minor': [[0, 3, 4, 0], [0, 3, 6, 4], [0, 5, 3, 4]], 'major': [[0, 3, 4, 3], [0, 4, 0, 4], [1, 4, 0, 0]],
             'harmonic_minor': [[0, 3, 4, 0], [0, 4, 0, 4]]},
      drums={'woodblock': ['x..x..x...x.x...'], 'cowbell808': ['x.x.x.x.x.x.x.x.'], 'conga': ['..o.x..o..o.x..o', 'x.o.x.ox..o.x.o.'],
             'kick': ['...X.......X....'], 'rim': ['............x...'], 'shaker': ['xxxxxxxxxxxxxxxx']}, kick_track='kick',
      snare_tracks=['rim'], bass=['...R..R....R..R.', '...R..F....R..A.', '...R..R.....R.F.'], bass_lo=28,
      chord_rh=['x.xx.x.xx.x.x.x.', '.x.x.xx..x.x.xx.'], chord_center=64,
      arp=dict(rate=2, mode='updown', oct=5, prob=0.5),
      lead_rh=['x-x-x---x-x-x---', 'x.x.x.x.x---....', 'x-.x-.x-x-------', '..x.x-x.x.x-....'], fill=True,
      gm_hint='Piano montuno; Trumpets + trombones; Congas, timbales, cowbell, clave; Baby bass (anticipated)',
      tracks=[T('woodblock', 'top', 'woodblock', pan=0.25, db=-26), T('cowbell808', 'top', 'cowbell808', pan=-0.25, db=-30),
              T('conga', 'top', 'conga', pan=0.3, db=-23), T('kick', 'kick', 'kick', db=-22), T('rim', 'snare', 'rim', db=-24),
              T('shaker', 'top', 'shaker', db=-32), T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1000, damp=0.996)),
              T('chords', 'chords', 'piano', rev=0.2, db=-21), T('arp', 'arp', 'piano', rev=0.2, db=-27),
              T('lead', 'lead', 'brass', rev=0.25, db=-17)],
      master=dict(lufs=-11.0, air=1.5, low=0.9))

style('cumbia', 'Classic', 'Cumbia: guira scrape and congas, kick on one and three, offbeat guitar, accordion melodies',
      bpm=(84, 104), scales=['minor', 'major'], human=0.008, kit='soft', form='song',
      progs={'minor': [[0, 4, 4, 0], [0, 3, 4, 0], [0, 6, 5, 4]], 'major': [[0, 4, 4, 0], [0, 3, 4, 0], [0, 4, 0, 4]]},
      drums={'kick': ['X.......X.......'], 'shaker': ['x.xxx.xxx.xxx.xx'], 'conga': ['..o...ox..o...ox', '......ox......o.'],
             'rim': ['....x.......x...'], 'cowbell808': ['..x...x...x...x.']}, snare_tracks=['rim'],
      bass=['R...F...R...F...', 'R..RF...R..RF...', 'R...F..RR...F...'], bass_lo=28,
      chord_rh=['..x...x...x...x.', '..xx..xx..xx..xx'], chord_center=62,
      arp=dict(rate=2, mode='updown', oct=5, prob=0.4),
      lead_rh=['x-x-x---x-x-x---', 'x.x.x.x.x-x-x---', 'x---x-x-x-------', '..x-x-x-x---x---'],
      gm_hint='Accordion (melody); Guira / shaker; Congas & timbales; Guitar (offbeats); Bass',
      tracks=[T('kick', 'kick', 'kick', db=-17), T('shaker', 'top', 'shaker', pan=0.3, db=-25), T('conga', 'top', 'conga', pan=-0.25, db=-23),
              T('rim', 'snare', 'rim', db=-24), T('cowbell808', 'top', 'cowbell808', db=-32),
              T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1000)),
              T('chords', 'chords', 'guitar', pan=-0.2, db=-23, p=dict(bright=6000, damp=0.985)),
              T('arp', 'arp', 'marimba', pan=0.3, db=-27),
              T('lead', 'lead', 'accordion', rev=0.25, db=-18)],
      master=dict(lufs=-11.0, air=1.3, low=1.2))

style('tango', 'Classic', 'Tango: marcato four-beat pulse, bandoneon, dramatic violin lines, staccato piano and double bass',
      bpm=(108, 126), scales=['harmonic_minor', 'minor'], human=0.01, form='song', chord_size=3,
      progs={'harmonic_minor': [[0, 3, 4, 0], [0, 5, 3, 4], [0, 4, 0, 4], [3, 4, 0, 0]], 'minor': [[0, 3, 6, 2]]},
      drums={}, bass=['R...R...R...R...', 'R..R..R.R...R...', 'R...F...R...F...'], bass_lo=28, bass_gate=0.45,
      chord_rh=['X...x...X...x...', 'x..x..x.x...x...', 'x.......x.......'], chord_center=60,
      arp=dict(rate=2, mode='up', oct=5, prob=0.4),
      lead_rh=['x---x-x-x---x---', 'x-x-x-x-x-------', 'x-----x-x-x-x---', 'x--x--x-x-------'],
      gm_hint='Bandoneon; Violins; Piano (marcato); Double bass',
      tracks=[T('bass', 'bass', 'cello', rev=0.25, db=-18, p=dict(a=0.02)),
              T('chords', 'chords', 'piano', rev=0.25, db=-21),
              T('pad', 'pad', 'accordion', rev=0.3, db=-26),
              T('arp', 'arp', 'pizz', rev=0.25, pan=0.3, db=-27),
              T('lead', 'lead', 'violin', rev=0.35, db=-17, p=dict(vib=16))],
      master=dict(lufs=-13.0, air=1.2, low=0.7))

style('dancehall', 'Electronic', 'Dancehall: digital riddim, syncopated kick and snare, sub bass, synth stabs and chanted hooks',
      bpm=(88, 104), scales=['minor', 'dorian'], human=0.004, kit='808', form='halftime', sc_depth=0.15,
      progs={'minor': [[0, 5, 6, 0], [0, 3, 0, 3], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3]]},
      drums={'kick': ['X..X......X.....', 'X.....X...X.....'], 'snare': ['...X..X....X..X.', '....X.......X...'],
             'chat': ['x.x.x.x.x.x.x.x.'], 'rim': ['..x...x...x...x.']}, snare_tracks=['snare'],
      bass=['R..R......R.....', 'R..R...R..R.....'], bass_lo=28, bass_gate=0.8,
      chord_rh=['..x...x...x...x.', 'x..x..x...x.....'], chord_center=64,
      lead_rh=['x.x..x.x..x.....', 'x..x..x.x.......', '..x.x..x..x.x...', 'x-x-x---x-------'],
      gm_hint='Synth stabs; Sub bass; Digital drums; Vocal chant / hook',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.15, db=-16), T('chat', 'top', 'chat', db=-27),
              T('rim', 'top', 'rim', pan=0.25, db=-27), T('bass', 'bass', 'sinebass', db=-12, p=dict(cut=400)),
              T('chords', 'chords', 'stab', rev=0.2, db=-22), T('pad', 'pad', 'warmpad', rev=0.4, db=-29),
              T('lead', 'lead', 'vox', rev=0.3, dly=0.25, db=-19)],
      master=dict(lufs=-9.0, air=1.4, low=2.0))

# ---- electronic
style('afro_house', 'Electronic', 'Afro house: four-on-the-floor with rolling congas and shakers, deep bass, kalimba & marimba hooks, chants',
      bpm=(118, 124), scales=['minor', 'dorian'], swing=0.54, human=0.004, kit='soft', form='groove', sc_depth=0.3, chord_size=4,
      progs={'minor': [[0, 6, 5, 6], [0, 3, 0, 3], [0, 5, 6, 0]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]},
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'shaker': ['xxxxxxxxxxxxxxxx'], 'conga': ['..o.x..o..o.x.o.', 'x..o..x.o..x..o.'],
             'woodblock': ['..x.....x.x.....'], 'ohat': [OFFHAT]}, snare_tracks=['clap'],
      bass=['R..R....R..R....', '..R...R...R..R..', 'R-..R-..R-..R-..'], bass_lo=31, bass_gate=0.7,
      chord_rh=['x---------x-----', '..x.....x.......', 'x--.....x--.....'], chord_center=62,
      arp=dict(rate=2, mode='random', oct=5, prob=0.6),
      lead_rh=['x.x..x.x..x.....', '..x.x..x..x.x...', 'x--x--x-x-------', 'x---x---x-x-----'],
      gm_hint='Kalimba / marimba (hooks); Congas, shakers; Deep bass; Pads; Vocal chants',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('clap', 'snare', 'clap', rev=0.3, db=-21), T('shaker', 'top', 'shaker', pan=0.3, db=-27),
              T('conga', 'top', 'conga', pan=-0.25, db=-23), T('woodblock', 'top', 'woodblock', pan=0.2, db=-29),
              T('ohat', 'top', 'ohat', db=-28), T('bass', 'bass', 'sinebass', sc=0.5, db=-13, p=dict(cut=500)),
              T('chords', 'chords', 'warmpad', sc=0.5, rev=0.4, db=-24), T('pad', 'pad', 'choir', rev=0.5, db=-28),
              T('arp', 'arp', 'kalimba', rev=0.3, dly=0.3, db=-24), T('lead', 'lead', 'marimba', rev=0.3, dly=0.25, db=-19)],
      master=dict(lufs=-9.5, air=1.4, low=1.6))

style('melodic_techno', 'Electronic', 'Melodic techno: rolling 16th basslines, hypnotic arpeggios, big emotional pads and plucks',
      bpm=(120, 128), scales=['minor', 'phrygian', 'harmonic_minor'], kit='909', form='groove', sc_depth=0.5,
      progs={'minor': [[0, 5, 2, 6], [0, 6, 5, 6], [0, 0, 5, 5]], 'phrygian': [[0, 1, 0, 6]], 'harmonic_minor': [[0, 5, 0, 4]]},
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'chat': ['..x...x...x...x.'], 'ohat': [OFFHAT], 'ride': ['x.x.x.x.x.x.x.x.']},
      snare_tracks=['clap'], bass=['.RRR.RRR.RRR.RRR', 'RRRRRRRRRRRRRRRR', '.R.R.R.R.R.R.R.R'], bass_lo=28, bass_gate=0.55,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=60, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x.x.x.x.x.x.x.x.', 'x..x..x.x..x..x.', 'x---x---x---x---', 'x-------x-------'],
      gm_hint='Rolling mono bass (Diva / Repro style); Arpeggiated pluck; Wide pads; Emotional lead',
      tracks=[T('kick', 'kick', 'kick', db=-12), T('clap', 'snare', 'clap', rev=0.35, db=-21), T('chat', 'top', 'chat', db=-28),
              T('ohat', 'top', 'ohat', db=-27), T('ride', 'top', 'ride', db=-32),
              T('bass', 'bass', 'sawbass', sc=0.7, db=-15, p=dict(cut=900, d=0.08, s=0.2)),
              T('chords', 'chords', 'warmpad', sc=0.6, rev=0.5, db=-23), T('pad', 'pad', 'strings', sc=0.6, rev=0.5, db=-27),
              T('arp', 'arp', 'pluck_saw', sc=0.4, dly=0.4, db=-24), T('lead', 'lead', 'leadsaw', sc=0.3, rev=0.4, dly=0.3, db=-20)],
      master=dict(lufs=-9.0, air=1.4, low=1.3))

style('kpop', 'Electronic', 'K-pop: polished genre-hopping pop - punchy drums, bright plucks and piano, big pre-chorus lifts, catchy hooks',
      bpm=(110, 132), scales=['minor', 'major'], kit='punchy', form='song_b', sc_depth=0.3, chord_size=4,
      progs={'minor': [[0, 5, 2, 6], [5, 6, 0, 0], [0, 3, 5, 4], [3, 4, 2, 5]], 'major': [[3, 4, 2, 5], [0, 4, 5, 3], [3, 4, 0, 5]]},
      drums={'kick': ['X.....X...X.....', 'X..X..X...X.....', FOUR], 'snare': [BACKBEAT], 'clap': [BACKBEAT],
             'chat': ['x.xxx.x.x.xxx.x.', 'x.x.x.x.x.x.x.x.']}, snare_tracks=['snare', 'clap'], fill=True,
      bass=['R..R..R.R..R....', 'R...R...R.R.R...'], bass_lo=28, bass_gate=0.7,
      chord_rh=['x..x..x.x..x..x.', 'x---x---x---x---', '..x...x...x...x.'], chord_center=64,
      arp=dict(rate=2, mode='updown', oct=5, prob=0.7),
      lead_rh=['x.x.x..x..x.x...', 'x-x-x---x-x-x---', '..x.x.x.x..x....', 'x--x--x-x-------'],
      gm_hint='Bright pluck & piano; Synth bass / 808; Supersaw pads; Vocal-chop hooks',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.2, db=-16), T('clap', 'snare', 'clap', db=-20),
              T('chat', 'top', 'chat', db=-27), T('bass', 'bass', 'fmbass', sc=0.5, db=-14),
              T('chords', 'chords', 'pluck_saw', sc=0.4, rev=0.25, dly=0.15), T('pad', 'pad', 'supersaw', sc=0.6, rev=0.4, db=-27),
              T('arp', 'arp', 'bell', dly=0.3, db=-26), T('lead', 'lead', 'vox', rev=0.3, dly=0.2, db=-18)],
      master=dict(lufs=-8.5, air=2.0, low=1.2))

style('jersey_club', 'Electronic', 'Jersey club: kick triplets and bed-squeak bounce, chopped vocal hooks, sliding 808s',
      bpm=(136, 145), scales=['minor'], kit='808', form='halftime', sc_depth=0.3,
      progs=[[0, 5, 2, 6], [0, 6, 5, 6], [0, 3, 5, 4]],
      drums={'kick': ['X..X..X.X.X.X...', 'X..X..X...X.X...', 'X.X.X..X..X.X...'], 'clap': ['....X.......X...'],
             'chat': ['x.x.x.x.x.x.x.x.'], 'snap': ['......x.......x.']}, snare_tracks=['clap'],
      bass_mode='808', bass_lo=28, chord_rh=['x---------------', 'x..x..x.........'], chord_center=62,
      lead_rh=['x.x.x..x.x.x....', 'x..x..x.x..x..x.', 'xx.xx.x.x.x.....', 'x-x-x---x-------'],
      gm_hint='808 kick & slides; Vocal chops (lead); Bed-squeak / snaps; Dark pad',
      tracks=[T('kick', 'kick', 'kick', db=-12), T('clap', 'snare', 'clap', rev=0.2, db=-17), T('chat', 'top', 'chat', db=-27),
              T('snap', 'top', 'snap', db=-24), T('bass', 'bass', '808', db=-13, p=dict(decay=0.5)),
              T('chords', 'chords', 'warmpad', rev=0.4, db=-25), T('lead', 'lead', 'vox', rev=0.2, dly=0.2, db=-18)],
      master=dict(lufs=-8.5, air=1.6, low=1.8))

style('baile_funk', 'Electronic', 'Baile funk (Brazilian funk carioca): tamborzao beat, booming 808, chanted vocal hooks, horn stabs',
      bpm=(126, 134), scales=['minor', 'phrygian'], kit='808', form='halftime', sc_depth=0.25,
      progs={'minor': [[0, 0, 5, 5], [0, 6, 5, 6], [0, 5, 6, 0]], 'phrygian': [[0, 1, 0, 1]]},
      drums={'kick': ['X..X..X...X..X..', 'X..X..X...X.X...'], 'snare': ['....X..X....X...', '...X..X....X..X.'],
             'conga': ['..o..o..o..o..o.', '.o..o.o..o..o.o.'], 'chat': ['x.x.x.x.x.x.x.x.'], 'clap': ['....x.......x...']},
      snare_tracks=['snare', 'clap'], bass_mode='808', bass_lo=28,
      chord_rh=['x..x..x...x.....', 'x.......x.......'], chord_center=62,
      lead_rh=['x.x..x.x..x.....', 'x..x..x.x.......', 'xx.x.x..x.x.....', 'x-x-x---x-------'],
      gm_hint='Tamborzao drums (kick + congas/toms); 808; Vocal chant hooks; Brass stabs',
      tracks=[T('kick', 'kick', 'kick', db=-12), T('snare', 'snare', 'snare', rev=0.15, db=-17), T('clap', 'snare', 'clap', db=-21),
              T('conga', 'top', 'conga', pan=0.25, db=-21), T('chat', 'top', 'chat', db=-28),
              T('bass', 'bass', '808', db=-12, p=dict(decay=0.5, drive=3.0)),
              T('chords', 'chords', 'brass', rev=0.2, db=-22), T('lead', 'lead', 'vox', rev=0.25, dly=0.2, db=-17)],
      master=dict(lufs=-8.0, air=1.5, low=2.0))

LABELS.update({'waltz': 'Waltz (3/4)', 'celtic_jig': 'Celtic Jig (6/8)', 'soul_ballad': 'Soul Ballad (12/8)', 'gospel': 'Gospel',
               'country': 'Country', 'bluegrass': 'Bluegrass', 'motown': 'Motown / 60s Soul', 'rnb': 'R&B / Neo-soul',
               'swing': 'Big Band Swing', 'ska': 'Ska', 'punk': 'Punk', 'indie_rock': 'Indie Rock', 'salsa': 'Salsa',
               'cumbia': 'Cumbia', 'tango': 'Tango', 'dancehall': 'Dancehall', 'afro_house': 'Afro House',
               'melodic_techno': 'Melodic Techno', 'kpop': 'K-pop', 'jersey_club': 'Jersey Club', 'baile_funk': 'Baile Funk'})
ACOUSTIC_MAP.update({
    'waltz': {'bass': 'cello'}, 'celtic_jig': {'bass': 'acbass', 'chords': 'nylon', 'lead': 'fiddle'},
    'soul_ballad': {'bass': 'fingerbass'}, 'gospel': {'bass': 'fingerbass'},
    'country': {'bass': 'acbass', 'chords': 'steelguitar', 'arp': 'cleanguitar', 'lead': 'fiddle'},
    'bluegrass': {'bass': 'acbass', 'chords': 'steelguitar', 'arp': 'banjo', 'lead': 'fiddle'},
    'motown': {'bass': 'fingerbass', 'arp': 'cleanguitar'}, 'swing': {'bass': 'acbass', 'chords': 'trumpetsection', 'lead': 'tenorsax'},
    'ska': {'bass': 'fingerbass', 'chords': 'cleanguitar', 'lead': 'trumpet'},
    'punk': {'bass': 'pickbass', 'chords': 'distguitar', 'lead': 'odguitar'},
    'indie_rock': {'bass': 'pickbass', 'chords': 'cleanguitar', 'arp': 'cleanguitar', 'lead': 'odguitar'},
    'salsa': {'bass': 'acbass', 'lead': 'trumpetsection'}, 'cumbia': {'bass': 'fingerbass', 'chords': 'cleanguitar'},
    'tango': {'bass': 'contrabass', 'pad': 'bandoneon'},
})
ACOUSTIC_KIT.update({'celtic_jig': 'room', 'soul_ballad': 'room', 'gospel': 'acoustic', 'country': 'room', 'motown': 'room',
                     'swing': 'brush', 'ska': 'acoustic', 'punk': 'rock', 'indie_rock': 'rock', 'salsa': 'acoustic',
                     'cumbia': 'room', 'rnb': 'acoustic'})
POWER_CHORDS.add('punk')
GENTLE_MASTER.update({'bluegrass', 'tango', 'swing', 'soul_ballad', 'celtic_jig'})
POOLS.update({
    'waltz': dict(bass=['cello', 'pizz', 'sf:contrabass'], chords=['spiccato', 'strings', 'harp', 'pizz'],
                  arp=['harp', 'celesta', 'flute', 'pizz'], lead=['violin', 'flute', 'clarinet', 'oboe', 'cello']),
    'celtic_jig': dict(bass=['pluck', 'sf:acbass'], chords=['guitar', 'sf:nylon', 'harp', 'accordion'],
                       arp=['harp', 'guitar', 'banjo'], lead=['violin', 'flute', 'sf:piccolo', 'accordion', 'sf:fiddle']),
    'soul_ballad': dict(bass=['pluck', 'sf:fingerbass', 'sf:acbass'], chords=['piano', 'epiano', 'organ', 'guitar'],
                        pad=['organ', 'strings', 'choir'], lead=['sax', 'sf:tenorsax', 'vox', 'guitar', 'organ', 'strings']),
    'gospel': dict(bass=['pluck', 'sf:fingerbass', 'fmbass'], chords=['organ', 'piano', 'epiano'], pad=['choir', 'organ', 'strings'],
                   arp=['piano', 'organ', 'epiano'], lead=['piano', 'organ', 'vox', 'choir', 'sax', 'guitar']),
    'country': dict(bass=['pluck', 'sf:acbass', 'sf:fingerbass'], chords=['guitar', 'sf:steelguitar', 'sf:cleanguitar', 'piano', 'banjo'],
                    arp=['guitar', 'sf:cleanguitar', 'banjo', 'piano'],
                    lead=['violin', 'sf:fiddle', 'guitar', 'sf:cleanguitar', 'softlead', 'piano']),
    'bluegrass': dict(bass=['pluck', 'sf:acbass'], chords=['guitar', 'sf:steelguitar', 'banjo'], arp=['banjo', 'guitar', 'sf:banjo'],
                      lead=['violin', 'sf:fiddle', 'banjo', 'guitar', 'sf:steelguitar']),
    'motown': dict(bass=['pluck', 'sf:fingerbass'], chords=['piano', 'guitar', 'sf:cleanguitar', 'organ', 'epiano'],
                   pad=['strings', 'sf:slowstrings', 'organ', 'brass'], arp=['guitar', 'sf:cleanguitar', 'piano', 'celesta'],
                   lead=['brass', 'sax', 'sf:tenorsax', 'strings', 'vox', 'flute', 'sf:trumpet']),
    'rnb': dict(bass=['sinebass', 'sf:fingerbass', 'fmbass', '808'], chords=['epiano', 'piano', 'guitar', 'sf:cleanguitar', 'organ'],
                pad=['warmpad', 'strings', 'choir', 'vox'], lead=['vox', 'guitar', 'sf:cleanguitar', 'sax', 'softlead', 'epiano', 'flute']),
    'swing': dict(bass=['pluck', 'sf:acbass'], chords=['brass', 'sf:trumpetsection', 'piano', 'sax'], arp=['piano', 'guitar'],
                  lead=['sax', 'sf:tenorsax', 'brass', 'sf:trumpet', 'sf:mutedtrumpet', 'clarinet', 'sf:trombone']),
    'ska': dict(bass=['pluck', 'sf:fingerbass'], chords=['guitar', 'sf:cleanguitar', 'organ', 'piano'], pad=['organ', 'brass'],
                lead=['brass', 'sf:trumpet', 'sax', 'sf:trombone', 'organ']),
    'punk': dict(bass=['pluck', 'sf:pickbass'], chords=['guitar', 'sf:distguitar', 'sf:odguitar'], lead=['guitar', 'sf:odguitar', 'sf:distguitar']),
    'indie_rock': dict(bass=['pluck', 'sf:pickbass', 'sf:fingerbass'], chords=['guitar', 'sf:cleanguitar', 'sf:odguitar', 'piano'],
                       pad=['organ', 'warmpad', 'strings'], arp=['guitar', 'sf:cleanguitar', 'bell', 'piano'],
                       lead=['guitar', 'sf:odguitar', 'sf:cleanguitar', 'leadsaw', 'piano']),
    'salsa': dict(bass=['pluck', 'sf:acbass', 'sf:fingerbass'], chords=['piano', 'epiano'], arp=['piano', 'marimba', 'guitar'],
                  lead=['brass', 'sf:trumpetsection', 'sf:trumpet', 'sf:trombone', 'flute', 'sax', 'violin']),
    'cumbia': dict(bass=['pluck', 'sf:fingerbass', 'sinebass'], chords=['guitar', 'sf:cleanguitar', 'organ', 'accordion'],
                   arp=['marimba', 'guitar', 'flute'], lead=['accordion', 'sf:accordion', 'flute', 'organ', 'brass', 'guitar']),
    'tango': dict(bass=['cello', 'sf:contrabass', 'pluck'], chords=['piano', 'accordion', 'strings'], pad=['accordion', 'sf:bandoneon', 'strings'],
                  arp=['pizz', 'piano', 'harp'], lead=['violin', 'accordion', 'sf:bandoneon', 'cello', 'piano', 'clarinet']),
    'dancehall': dict(bass=['sinebass', '808', 'fmbass'], chords=['stab', 'pluck_saw', 'organ', 'marimba', 'steeldrum'],
                      pad=['warmpad', 'strings'], lead=['vox', 'pluck', 'leadsaw', 'flute', 'steeldrum', 'bell']),
    'afro_house': dict(bass=['sinebass', 'fmbass', 'sawbass'], chords=['warmpad', 'epiano', 'piano', 'organ', 'stab'],
                       pad=['choir', 'warmpad', 'strings', 'vox'], arp=['kalimba', 'marimba', 'bell', 'pluck', 'steeldrum'],
                       lead=['marimba', 'kalimba', 'flute', 'vox', 'pluck', 'sax']),
    'melodic_techno': dict(bass=['sawbass', 'fmbass', 'reese', 'acid'], chords=['warmpad', 'supersaw', 'strings', 'stab'],
                           pad=['strings', 'warmpad', 'choir', 'tremolo'], arp=['pluck_saw', 'bell', 'pluck', 'marimba'],
                           lead=['leadsaw', 'supersaw_lead', 'pluck_saw', 'bell', 'vox', 'cello']),
    'kpop': dict(bass=['fmbass', 'sawbass', '808', 'sf:slapbass'], chords=['pluck_saw', 'piano', 'stab', 'supersaw', 'guitar', 'epiano'],
                 pad=['supersaw', 'strings', 'warmpad', 'choir'], arp=['bell', 'pluck', 'chip', 'piano', 'marimba'],
                 lead=['vox', 'pluck', 'supersaw_lead', 'leadsaw', 'bell', 'piano']),
    'jersey_club': dict(chords=['warmpad', 'piano', 'strings', 'pluck_saw'], lead=['vox', 'pluck', 'bell', 'chip']),
    'baile_funk': dict(chords=['brass', 'stab', 'organ', 'pluck_saw'], lead=['vox', 'brass', 'leadsaw', 'flute', 'cowbell']),
})

# song lengths that match how each genre is usually released (half-time forms at 140-170 BPM run short otherwise)
for _n, _k in {'future_bass': 1.5, 'dubstep': 1.75, 'hyperpop': 1.25, 'jersey_club': 1.25, 'jazz': 1.75, 'swing': 1.5,
               'waltz': 1.5, 'rnb': 0.75}.items():
    STYLES[_n]['form_scale'] = _k


# ----------------------------------------------------------------------------- v1.11: new instruments in the genres
# Upright bass is the real sound of these genres (was a generic plucked string)
for _n in ('jazz', 'swing', 'bluegrass', 'bossa_nova', 'folk', 'holiday', 'celtic_jig', 'western'):
    for _t in STYLES[_n]['tracks']:
        if _t['layer'] == 'bass' and _t['inst'] == 'pluck':
            _t.update(inst='upright', p={})
    _pool = POOLS[_n].get('bass')
    if _pool and _pool[0] == 'pluck':
        _pool[0] = 'upright'
        if 'pluck' not in _pool:
            _pool.append('pluck')
# country: pedal-steel swells under the band
STYLES['country']['tracks'].insert(-1, T('pad', 'pad', 'pedalsteel', rev=0.4, pan=0.2, db=-25))
POOLS['country']['pad'] = ['pedalsteel', 'organ', 'strings']
STYLES['country']['gm_hint'] += '; Pedal steel swells'

_ADD = {   # genre -> part -> instruments that belong in that genre's sound
    'synthwave': dict(bass=['moogbass'], chords=['polysynth', 'synthbrass'], pad=['solina', 'polysynth', 'glasspad'], lead=['synthbrass', 'polysynth']),
    'synthpop': dict(bass=['moogbass'], chords=['polysynth', 'synthbrass'], pad=['solina', 'glasspad'], lead=['synthbrass']),
    'city_pop': dict(bass=['moogbass'], chords=['polysynth', 'wurli', 'synthbrass'], pad=['solina'], arp=['mutedgtr', 'vibes'], lead=['synthbrass', 'trumpet']),
    'vaporwave': dict(chords=['polysynth', 'wurli'], pad=['solina', 'glasspad'], lead=['vibes', 'polysynth']),
    'house': dict(bass=['moogbass'], chords=['polysynth'], pad=['glasspad', 'solina']),
    'deep_house': dict(chords=['wurli', 'polysynth'], pad=['glasspad'], arp=['vibes']),
    'progressive_house': dict(pad=['glasspad'], chords=['polysynth']),
    'trance': dict(pad=['glasspad']), 'melodic_techno': dict(bass=['moogbass'], pad=['glasspad']),
    'future_bass': dict(chords=['polysynth'], pad=['glasspad']), 'ambient': dict(pad=['glasspad', 'solina'], arp=['vibes']),
    'downtempo': dict(chords=['wurli', 'polysynth'], pad=['glasspad'], arp=['vibes']),
    'lofi': dict(chords=['wurli'], lead=['vibes']), 'boombap': dict(chords=['wurli', 'vibes']),
    'dnb': dict(pad=['glasspad'], chords=['wurli']), 'kpop': dict(bass=['moogbass'], chords=['polysynth', 'synthbrass'], pad=['glasspad'], arp=['mutedgtr']),
    'eurodance': dict(chords=['polysynth'], pad=['solina']), 'electro': dict(bass=['moogbass'], chords=['synthbrass', 'polysynth']),
    'disco': dict(bass=['moogbass'], pad=['solina', 'synthbrass'], arp=['mutedgtr'], lead=['trumpet']),
    'funk': dict(bass=['moogbass'], chords=['mutedgtr', 'wurli'], pad=['synthbrass'], lead=['trumpet', 'synthbrass']),
    'jazz': dict(chords=['vibes', 'wurli'], arp=['vibes'], lead=['trumpet', 'vibes']),
    'swing': dict(arp=['vibes'], lead=['trumpet', 'vibes']), 'bossa_nova': dict(chords=['vibes', 'wurli'], arp=['vibes'], lead=['vibes']),
    'rnb': dict(bass=['moogbass'], chords=['wurli', 'polysynth'], pad=['glasspad']), 'soul_ballad': dict(chords=['wurli'], lead=['trumpet']),
    'gospel': dict(chords=['wurli']), 'motown': dict(chords=['wurli'], arp=['mutedgtr', 'vibes'], lead=['trumpet']),
    'blues': dict(lead=['harmonica'], chords=['wurli']), 'country': dict(lead=['pedalsteel', 'harmonica']),
    'folk': dict(lead=['harmonica']), 'western': dict(lead=['harmonica', 'trumpet'], pad=['pedalsteel']), 'bluegrass': dict(lead=['harmonica']),
    'ska': dict(chords=['mutedgtr'], lead=['trumpet']), 'salsa': dict(lead=['trumpet'], arp=['vibes']), 'cumbia': dict(chords=['mutedgtr'], lead=['trumpet']),
    'reggae': dict(arp=['mutedgtr'], lead=['trumpet', 'harmonica']), 'afrobeats': dict(chords=['mutedgtr'], arp=['vibes']),
    'dancehall': dict(chords=['mutedgtr']), 'indie_rock': dict(chords=['wurli'], pad=['solina', 'polysynth']),
    'holiday': dict(arp=['vibes'], lead=['trumpet', 'vibes']), 'chamber_pop': dict(arp=['vibes'], lead=['trumpet']),
    'pop': dict(chords=['polysynth', 'wurli'], pad=['glasspad']), 'hyperpop': dict(chords=['polysynth']),
    'cinematic': dict(lead=['trumpet']), 'adventure': dict(lead=['trumpet']), 'baroque': dict(lead=['trumpet']),
}
for _n, _parts in _ADD.items():
    for _l, _insts in _parts.items():
        if not any(t['layer'] == _l for t in STYLES[_n]['tracks']):
            continue
        _pool = POOLS[_n].setdefault(_l, [next(t['inst'] for t in STYLES[_n]['tracks'] if t['layer'] == _l)])
        for _i in _insts:
            if _i not in _pool:
                _pool.append(_i)


# ============================== v1.11: braindance + hauntology ==============
style('braindance', 'Electronic', 'Braindance / IDM: hyperactive chopped breakbeats with ratchets and ghost notes, squelchy acid bass, '
      'music-box melodies over warm detuned pads, odd modes',
      bpm=(120, 168), scales=['minor', 'lydian', 'phrygian', 'dorian'], human=0.002, kit='punchy', form='groove', ghosts=True, fill=True,
      progs={'minor': [[0, 5, 3, 6], [0, 0, 6, 5], [0, 3, 6, 2]], 'lydian': [[0, 1, 0, 1], [0, 1, 4, 5]],
             'phrygian': [[0, 1, 0, 6]], 'dorian': [[0, 3, 0, 6], [0, 6, 3, 3]]}, chord_size=4,
      drums={'kick': ['X..X.X....X..X..', 'X.X...X..X.X....', 'XX....X...X.X..X'],
             'snare': ['....X..x.x.xX..x', '..x.X.....x.X.xx', '....X.x..X..X.X.'],
             'chat': ['xxxxxxxxxxxxxxxx', 'x.xxx.xxxx.xx.xx'], 'snap': ['...x.....x..x...', '.x.....x...x..x.'], 'ohat': ['..x.......x.....']},
      snare_tracks=['snare', 'snap'], bass=['R..R..R.R.R...R.', 'R-..R...R.R.R...', 'R...R.RR..R.R...'], bass_lo=28, bass_gate=0.7,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=62, arp=dict(rate=1, mode='random', oct=6, prob=0.7),
      lead_rh=['x..x..x.x..x.x..', 'x.x...x.xx..x...', 'x---x-x-x--x----', 'x.xx.x...x.x.x..'],
      gm_hint='Acid bass (303); Detuned analog pads (Juno / CS-80 style); Music-box / celesta; Chopped breakbeats',
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.15, db=-16), T('snap', 'snare', 'snap', db=-24),
              T('chat', 'top', 'chat', pan=0.2, db=-27), T('ohat', 'top', 'ohat', db=-29),
              T('bass', 'bass', 'acid', db=-16), T('chords', 'chords', 'polysynth', rev=0.4, db=-23, p=dict(a=0.25, r=0.8, cut=1400)),
              T('pad', 'pad', 'glasspad', rev=0.5, db=-27), T('arp', 'arp', 'celesta', rev=0.35, dly=0.3, pan=-0.25, db=-24),
              T('lead', 'lead', 'bell', rev=0.35, dly=0.25, db=-19)],
      master=dict(lufs=-10.0, air=1.4, low=1.2))

style('hauntology', 'Electronic', 'Hauntology: warped-tape analog synths, slow dusty hip-hop breaks, nostalgic melodies and '
      'string-machine haze, all drifting like an old cassette',
      bpm=(78, 96), scales=['major', 'dorian', 'mixolydian', 'minor'], swing=0.56, human=0.012, kit='soft', form='lofi', chord_size=4,
      progs={'major': [[0, 3, 0, 3], [0, 5, 3, 4], [3, 0, 3, 0], [0, 2, 3, 0]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]],
             'mixolydian': [[0, 6, 0, 6], [0, 3, 6, 0]], 'minor': [[0, 5, 6, 0], [0, 3, 0, 3]]}, chord_bars=1, voicing='open',
      drums={'kick': ['X.......X.x.....', 'X......XX.......', 'X.....x...X.....'], 'snare': [BACKBEAT],
             'chat': ['x.x.x.x.x.x.x.x.', 'x...x...x...x...']}, snare_tracks=['snare'],
      bass=['R-------R---....', 'R-----..R-......', 'R-------F-------'], bass_lo=31,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=60, arp=dict(rate=2, mode='updown', oct=5, prob=0.6),
      lead_rh=['x-------x---x---', 'x---x---x-------', 'x-----x-x-------', 'x---------------'], reverb=3.4,
      gm_hint='Detuned analog poly (Prophet / Juno); String machine; Sine lead or vocal sample; Dusty drum break; tape + vinyl',
      tracks=[T('kick', 'kick', 'kick', db=-16), T('snare', 'snare', 'snare', rev=0.35, db=-19), T('chat', 'top', 'chat', db=-30),
              T('bass', 'bass', 'sinebass', db=-15, p=dict(cut=450)),
              T('chords', 'chords', 'polysynth', rev=0.45, dly=0.15, db=-22, p=dict(a=0.3, r=1.0, cut=1200)),
              T('pad', 'pad', 'solina', rev=0.5, db=-25),
              T('arp', 'arp', 'polysynth', rev=0.4, dly=0.3, pan=0.25, db=-26, p=dict(a=0.004, d=0.3, s=0.15, r=0.4, cut=2200)),
              T('lead', 'lead', 'softlead', rev=0.45, dly=0.3, db=-19), T('vinyl', 'fx', 'vinyl', db=-40)],
      master=dict(lufs=-12.5, air=-1.5, low=1.5, lofi=True, wobble=3.0))

LABELS.update({'braindance': 'Braindance / IDM', 'hauntology': 'Hauntology'})
POOLS.update({
    'braindance': dict(bass=['acid', 'reese', 'moogbass', 'sawbass', 'fmbass'], chords=['polysynth', 'warmpad', 'glasspad', 'epiano', 'solina'],
                       pad=['glasspad', 'warmpad', 'solina', 'choir', 'strings'], arp=['celesta', 'bell', 'chip', 'vibes', 'marimba', 'pluck_saw'],
                       lead=['bell', 'acid', 'celesta', 'leadsaw', 'piano', 'chip', 'polysynth']),
    'hauntology': dict(bass=['sinebass', 'moogbass', 'fmbass'], chords=['polysynth', 'solina', 'wurli', 'epiano', 'warmpad'],
                       pad=['solina', 'warmpad', 'glasspad', 'choir', 'strings'], arp=['polysynth', 'vibes', 'bell', 'celesta'],
                       lead=['softlead', 'vox', 'polysynth', 'flute', 'vibes']),
})


# ============================== v1.11: styles after well-known sounds (named for the style, not the artist)
style('uplifting_trance', 'Electronic', 'Uplifting trance: emotional minor-key anthems, rolling off-beat bass, supersaw leads and '
      'plucky arps, a long piano / pad breakdown that explodes into the drop',
      bpm=(132, 138), scales=['minor'], kit='909', form='edm', sc_depth=0.55, chord_size=4,
      progs=[[5, 3, 0, 4], [0, 5, 2, 6], [0, 5, 3, 4], [5, 6, 0, 0], [0, 3, 5, 4]],
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.x.x.x.x.x.x.x.'], 'ride': ['x.x.x.x.x.x.x.x.']},
      snare_tracks=['clap'], bass=['.RRR.RRR.RRR.RRR', '..R...R...R...R.'], bass_lo=31, bass_gate=0.6, fill=True,
      chord_rh=['x---------------', '..x...x...x...x.'], chord_center=64, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x-x-x-x-x---x---', 'x--x--x-x-------', 'x-x-x---x-x-x---', 'x-------x---x---'],
      gm_hint='Supersaw lead; Plucky arp (gated); Rolling off-beat bass; Piano (breakdown); Wide pads; Vocal',
      tracks=[T('kick', 'kick', 'kick', db=-12), T('clap', 'snare', 'clap', rev=0.3, db=-19), T('ohat', 'top', 'ohat', db=-26),
              T('chat', 'top', 'chat', db=-29), T('ride', 'top', 'ride', db=-32),
              T('bass', 'bass', 'sawbass', sc=0.7, db=-15, p=dict(cut=1100, d=0.1, s=0.3)),
              T('chords', 'chords', 'supersaw', sc=0.8, rev=0.4, db=-22), T('pad', 'pad', 'strings', sc=0.6, rev=0.5, db=-26),
              T('arp', 'arp', 'pluck_saw', sc=0.5, dly=0.35, db=-24), T('lead', 'lead', 'supersaw_lead', sc=0.4, rev=0.4, dly=0.25, db=-18)],
      master=dict(lufs=-8.5, air=2.0, low=1.0))

style('melodic_house', 'Electronic', 'Melodic deep house: warm rolling bassline, organic shakers and congas, emotive piano and plucked '
      'melodies over lush pads, gentle and euphoric',
      bpm=(116, 122), scales=['minor', 'major', 'dorian'], swing=0.53, kit='soft', form='groove', sc_depth=0.35, chord_size=4,
      progs={'minor': [[0, 5, 2, 6], [0, 6, 5, 3], [5, 3, 0, 4]], 'major': [[0, 4, 5, 3], [3, 0, 4, 5], [5, 3, 0, 4]],
             'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]},
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'shaker': ['x.xxx.xxx.xxx.xx'], 'conga': ['......o.......o.', '..o.....o.o.....'],
             'ohat': [OFFHAT], 'rim': ['...x......x.....']}, snare_tracks=['clap'],
      bass=['R..R..R.R..R..R.', '..R...R...R..R..', 'R-..R-..R-..R-..'], bass_lo=31, bass_gate=0.65,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=62, arp=dict(rate=2, mode='updown', oct=5),
      lead_rh=['x-x-x---x-x-x---', 'x---x-x-x-------', '..x-x-x-x---x---', 'x--x--x-x-------'],
      gm_hint='Felt / grand piano; Plucked guitar or harp; Lush pads; Rolling bass; Shakers, congas; field-recording textures',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('clap', 'snare', 'clap', rev=0.35, db=-21), T('shaker', 'top', 'shaker', pan=0.3, db=-27),
              T('conga', 'top', 'conga', pan=-0.25, db=-26), T('ohat', 'top', 'ohat', db=-28), T('rim', 'top', 'rim', pan=0.2, db=-29),
              T('bass', 'bass', 'moogbass', sc=0.6, db=-15, p=dict(cut=450)),
              T('chords', 'chords', 'warmpad', sc=0.5, rev=0.5, db=-24), T('pad', 'pad', 'glasspad', sc=0.5, rev=0.5, db=-27),
              T('arp', 'arp', 'harp', rev=0.4, dly=0.3, pan=0.25, db=-25), T('lead', 'lead', 'piano', rev=0.4, dly=0.2, db=-18),
              T('texture', 'fx', 'texture', rev=0.5, db=-38)],
      master=dict(lufs=-9.5, air=1.6, low=1.3))

style('jam_band', 'Classic', 'Jam band / psychedelic Americana: noodling clean lead guitar, melodic wandering bass, organ, '
      'loose two-drummer groove, long improvised sections',
      bpm=(100, 132), scales=['mixolydian', 'major', 'dorian'], swing=0.54, human=0.012, kit='acoustic', form='jazz', form_scale=1.5,
      progs={'mixolydian': [[0, 6, 3, 0], [0, 3, 0, 6], [0, 6, 0, 3]], 'major': [[0, 4, 3, 0], [0, 3, 4, 3], [0, 5, 3, 4]],
             'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]},
      drums={'kick': ['X.......X.x.....', 'X...X.....X.X...'], 'snare': [BACKBEAT], 'ride': ['x.x.x.x.x.x.x.x.'],
             'chat': ['x.x.x.x.x.x.x.x.'], 'tom': ['.............x.x', '................']}, snare_tracks=['snare'], ghosts=True, fill=True,
      bass=['R.R.F.A.R..RF.A.', 'R...F.R.A..RF...', 'R.FA.R..F.A.R.F.'], bass_lo=28,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x---x---x---x---', '..x...x...x...x.'], chord_center=60,
      arp=dict(rate=2, mode='random', oct=5, prob=0.4),
      lead_rh=['x.x.x.x.x-x-x---', 'x.xx.x.xx.x.x...', 'x-x-x.x.x.x-x---', '..x.x-x.x.x.x.x.'],
      gm_hint='Clean electric guitars (lead + rhythm); Bass guitar (melodic); Hammond organ; Piano; two drummers',
      tracks=[T('kick', 'kick', 'kick', db=-17), T('snare', 'snare', 'snare', rev=0.3, db=-18), T('ride', 'top', 'ride', pan=0.25, db=-26),
              T('chat', 'top', 'chat', pan=-0.25, db=-29), T('tom', 'top', 'tom', rev=0.3, db=-24),
              T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1400, damp=0.997)),
              T('chords', 'chords', 'guitar', pan=-0.25, rev=0.3, db=-22, p=dict(bright=5500)),
              T('pad', 'pad', 'organ', pan=0.25, rev=0.3, db=-26), T('arp', 'arp', 'piano', rev=0.3, db=-27),
              T('lead', 'lead', 'guitar', rev=0.35, dly=0.2, db=-18, p=dict(dist=4, bright=5000))],
      master=dict(lufs=-12.0, air=1.2, low=0.9))

style('teen_pop', 'Electronic', "Late-90s teen pop: punchy dance-pop drums, dramatic minor chords, muted-guitar and synth-pluck "
      'riffs, string stabs, call-and-response hooks and a last-chorus key change',
      bpm=(92, 112), scales=['minor', 'major'], kit='punchy', form='song_b', sc_depth=0.25, chord_size=4, ghosts=True,
      progs={'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4], [0, 5, 3, 4]], 'major': [[0, 4, 5, 3], [5, 3, 0, 4], [3, 4, 2, 5]]},
      drums={'kick': ['X.....X.X.......', 'X..X..X...X.....', 'X.....X...X..X..'], 'snare': [BACKBEAT], 'clap': [BACKBEAT],
             'chat': ['x.xxx.x.x.xxx.x.', 'xxxxxxxxxxxxxxxx'], 'tamb': ['....x.......x...']}, snare_tracks=['snare', 'clap'], fill=True,
      bass=['R..R..R.R.R...R.', 'R...R..RR...R.R.', 'R.R...R.R.R...A.'], bass_lo=28, bass_gate=0.7,
      chord_rh=['x..x..x.x..x..x.', 'x---x---x---x---', 'x.x...x.x.x...x.'], chord_center=63,
      arp=dict(rate=2, mode='updown', oct=5, prob=0.8),
      lead_rh=['x.x.x..x..x.x...', 'x-x-x---x-x-x---', '..x.x.x.x..x....', 'x--x--x-x-------'],
      gm_hint='Muted / funk guitar; Synth plucks & piano; String stabs; Punchy drum machine; Vocal-style lead with harmonies',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.25, db=-16), T('clap', 'snare', 'clap', db=-20),
              T('chat', 'top', 'chat', db=-27), T('tamb', 'top', 'tamb', pan=0.3, db=-29),
              T('bass', 'bass', 'moogbass', sc=0.4, db=-14),
              T('chords', 'chords', 'pluck_saw', sc=0.3, rev=0.25, db=-22), T('pad', 'pad', 'strings', rev=0.35, db=-25),
              T('arp', 'arp', 'mutedgtr', pan=-0.3, db=-24), T('lead', 'lead', 'vox', rev=0.3, dly=0.15, db=-18)],
      master=dict(lufs=-9.0, air=1.8, low=1.2))

style('soft_rock', 'Classic', '70s soft rock (California): steady groove, round melodic bass, strummed acoustic and clean electric '
      'guitars, Rhodes and organ, a smooth vocal-style lead',
      bpm=(100, 126), scales=['major', 'dorian', 'mixolydian', 'minor'], human=0.008, kit='soft', form='song_b', chord_size=4, strum=0.01,
      progs={'major': [[0, 4, 5, 3], [3, 0, 4, 0], [0, 3, 0, 4], [5, 3, 0, 4]], 'dorian': [[0, 6, 0, 6], [0, 3, 0, 3]],
             'mixolydian': [[0, 6, 3, 0]], 'minor': [[0, 6, 5, 6], [5, 6, 0, 0]]},
      drums={'kick': ['X.......X.......', 'X.....X.X.......'], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.', 'xxxxxxxxxxxxxxxx'],
             'tom': ['............x.x.', '................'], 'tamb': ['....x.......x...']}, snare_tracks=['snare'], fill=True,
      bass=['R.....R.R...F...', 'R...R...F...A...', 'R.......R.R.F...'], bass_lo=28,
      chord_rh=['x.x.x.x.x.x.x.x.', 'x---x---x---x---', 'x..x..x.x.x.x...'], chord_center=60,
      arp=dict(rate=2, mode='updown', oct=5, prob=0.6),
      lead_rh=['x-x-x---x-x-....', 'x---x-x-x---....', '..x-x-x-x---x...', 'x-x-x-x-x-------'],
      gm_hint='Acoustic + clean electric guitars; Fender Rhodes; Hammond organ; Bass guitar (melodic); soft drums with tom fills',
      tracks=[T('kick', 'kick', 'kick', db=-16), T('snare', 'snare', 'snare', rev=0.35, db=-18), T('chat', 'top', 'chat', db=-28),
              T('tom', 'top', 'tom', rev=0.35, db=-23), T('tamb', 'top', 'tamb', pan=0.3, db=-30),
              T('bass', 'bass', 'pluck', db=-15, p=dict(bright=1200, damp=0.997)),
              T('chords', 'chords', 'guitar', pan=-0.25, rev=0.25, p=dict(bright=5500)), T('pad', 'pad', 'organ', pan=0.25, rev=0.3, db=-27),
              T('arp', 'arp', 'epiano', rev=0.3, pan=0.2, db=-25), T('lead', 'lead', 'guitar', rev=0.35, dly=0.2, db=-18, p=dict(dist=3, bright=5000))],
      master=dict(lufs=-11.0, air=1.3, low=1.0))

style('luxury_rap', 'Electronic', 'Luxury rap: majestic soul and orchestral samples - lush strings, choir, horn stabs and piano - over '
      'booming 808s and crisp trap drums, slow and triumphant',
      bpm=(136, 152), scales=['minor', 'major', 'harmonic_minor'], kit='808', form='trap', trap_hats=True, sc_depth=0.15, chord_size=4,
      progs={'minor': [[0, 5, 3, 4], [0, 6, 5, 6], [0, 3, 5, 4]], 'major': [[0, 4, 5, 3], [3, 4, 0, 5]], 'harmonic_minor': [[0, 5, 3, 4]]},
      drums={'kick': ['X.........X.....', 'X.....X...X.....', 'X......X..X.....'], 'snare': [HALF], 'clap': [HALF],
             'ohat': ['......x.......x.']}, snare_tracks=['snare', 'clap'], bass_mode='808', bass_lo=26,
      chord_rh=['x-------x-------', 'x---------------', 'x--x--x-x-------'], chord_center=62,
      arp=dict(rate=2, mode='updown', oct=5, prob=0.5),
      lead_rh=['x-------x---x---', 'x---x---x-------', 'x-x-x---x-------', 'x---------------'],
      gm_hint='Soul / orchestral sample: lush strings, choir, horn stabs, piano; booming 808; trap drums',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.3, db=-16), T('clap', 'snare', 'clap', db=-20),
              T('ohat', 'top', 'ohat', db=-28), T('bass', 'bass', '808', db=-12, p=dict(decay=0.45, drive=3.5)),
              T('chords', 'chords', 'piano', rev=0.35, db=-21), T('pad', 'pad', 'strings', rev=0.45, db=-23),
              T('arp', 'arp', 'harp', rev=0.4, db=-27), T('lead', 'lead', 'brass', rev=0.35, db=-18)],
      master=dict(lufs=-8.5, air=1.4, low=2.0))

LABELS.update({'uplifting_trance': 'Uplifting Trance', 'melodic_house': 'Melodic Deep House', 'jam_band': 'Jam Band',
               'teen_pop': "Teen Pop ('99)", 'soft_rock': '70s Soft Rock', 'luxury_rap': 'Luxury Rap'})
ACOUSTIC_MAP.update({'jam_band': {'bass': 'fingerbass', 'chords': 'cleanguitar', 'lead': 'cleanguitar'},
                     'soft_rock': {'bass': 'fingerbass', 'chords': 'steelguitar', 'lead': 'cleanguitar'}})
ACOUSTIC_KIT.update({'jam_band': 'room', 'soft_rock': 'room'})
POOLS.update({
    'uplifting_trance': dict(bass=['sawbass', 'fmbass', 'moogbass'], chords=['supersaw', 'stab', 'pluck_saw', 'piano', 'polysynth'],
                             pad=['strings', 'warmpad', 'choir', 'glasspad', 'supersaw'], arp=['pluck_saw', 'bell', 'pluck', 'piano'],
                             lead=['supersaw_lead', 'leadsaw', 'pluck_saw', 'piano', 'vox']),
    'melodic_house': dict(bass=['moogbass', 'sinebass', 'sawbass'], chords=['warmpad', 'piano', 'polysynth', 'epiano', 'strings'],
                          pad=['glasspad', 'strings', 'warmpad', 'choir', 'solina'], arp=['harp', 'pluck', 'guitar', 'marimba', 'kalimba', 'bell'],
                          lead=['piano', 'pluck', 'guitar', 'sf:nylon', 'violin', 'flute', 'vox']),
    'jam_band': dict(bass=['pluck', 'sf:fingerbass', 'upright'], chords=['guitar', 'sf:cleanguitar', 'piano', 'organ'],
                     pad=['organ', 'wurli', 'pedalsteel'], arp=['piano', 'guitar', 'wurli'],
                     lead=['guitar', 'sf:cleanguitar', 'organ', 'piano', 'pedalsteel', 'harmonica']),
    'teen_pop': dict(bass=['moogbass', 'fmbass', 'sawbass', 'sf:fingerbass'], chords=['pluck_saw', 'piano', 'mutedgtr', 'stab', 'guitar', 'polysynth'],
                     pad=['strings', 'polysynth', 'warmpad', 'choir'], arp=['mutedgtr', 'pluck', 'bell', 'guitar', 'harp'],
                     lead=['vox', 'pluck', 'guitar', 'strings', 'flute', 'synthbrass']),
    'soft_rock': dict(bass=['pluck', 'sf:fingerbass', 'moogbass'], chords=['guitar', 'sf:steelguitar', 'sf:cleanguitar', 'epiano', 'piano', 'wurli'],
                      pad=['organ', 'strings', 'solina', 'polysynth', 'pedalsteel'], arp=['epiano', 'guitar', 'piano', 'vibes'],
                      lead=['guitar', 'sf:cleanguitar', 'vox', 'epiano', 'pedalsteel', 'flute', 'sax']),
    'luxury_rap': dict(chords=['piano', 'strings', 'epiano', 'brass', 'harp'], pad=['strings', 'choir', 'horn', 'solina', 'sf:slowstrings'],
                       arp=['harp', 'bell', 'celesta', 'pizz', 'vibes'], lead=['brass', 'horn', 'violin', 'choir', 'sax', 'trumpet', 'piano']),
})
for _n, _k in {'uplifting_trance': 1.75, 'luxury_rap': 1.4}.items():
    STYLES[_n]['form_scale'] = _k
POOLS['jam_band']['lead'] = ['guitar', 'sf:cleanguitar', 'guitar', 'organ', 'pedalsteel', 'harmonica', 'piano']


# ============================== v1.11: bass-music & phonk families, trance arrangement (after the genre reference guides)
TRANCE_FORM = [   # DJ intro, a long beatless breakdown as the emotional peak, then the climax
    ('intro', 16, {'kick', 'top', 'bass'}, {'filter_in': True}),
    ('verse', 16, {'kick', 'top', 'snare', 'bass', 'chords', 'arp'}, {'crash': True}),
    ('break', 24, {'pad', 'chords', 'lead', 'arp', 'fx'}, {'alt': True, 'crash': True}),
    ('build', 8, {'chords', 'arp', 'top', 'pad', 'lead'}, {'build': True}),
    ('drop', 32, ALL, {'drop': True}),
    ('break', 8, {'pad', 'lead', 'fx'}, {'alt': True}),
    ('drop', 16, ALL, {'drop': True}),
    ('outro', 16, {'kick', 'top', 'bass'}, {}),
]
FORMS['trance'] = TRANCE_FORM
for _n in ('trance', 'uplifting_trance'):
    STYLES[_n]['form'] = 'trance'
STYLES['uplifting_trance']['form_scale'] = 1.25
STYLES['trance']['bpm'] = (132, 140)
for _n in ('dnb', 'jungle'):
    STYLES[_n]['sub_layer'] = True
STYLES['phonk']['bpm'] = (145, 165)                          # drift phonk: 140-170 with a half-time feel

style('brostep', 'Electronic', 'Brostep: festival dubstep - snarling growls, wobbles and FM stabs trading bars in the drop over a '
      'clean sub, aggressive half-time drums, pitch dives, risers and hard stops',
      bpm=(140, 150), scales=['minor', 'phrygian', 'harmonic_minor'], progs=[[0, 0, 5, 6], [0, 0, 1, 0], [0, 6, 5, 6]],
      sc_depth=0.65, sc_release=0.25, reverb=2.2, kit='hard', form='halftime', sub_layer=True, fill=True,
      bass_switch=['wobble', 'fmbass'], switch_bars=1,
      kit_override=dict(kick=dict(drive=3.5, punch=220, decay=6), snare=dict(snap=2.0, decay=9, drive=1.5)),
      drums={'kick': ['X.........X.....', 'X.....X...X..X..', 'X..X......X.....'], 'snare': [HALF],
             'chat': ['x.x.x.x.x.x.x.x.', 'xxxxxxxxxxxxxxxx'], 'crash': ['X...............'], 'clap': [HALF]},
      snare_tracks=['snare', 'clap'], bass_mode='wobble', bass_lo=26, chord_rh=['x---------------'],
      arp=dict(rate=2, mode='random', oct=5, prob=0.3),
      lead_rh=['x-------x-------', 'x.x.x...x.......', 'x---x---x-------', 'x---------------'], lead_oct=5,
      gm_hint='Growl / FM / wobble mid-basses (Serum / Vital style) over a mono sine sub; hard half-time drums; risers, impacts',
      tracks=[T('kick', 'kick', 'kick', db=-11), T('snare', 'snare', 'snare', rev=0.25, db=-13), T('clap', 'snare', 'clap', db=-19),
              T('chat', 'top', 'chat', pan=0.2, db=-27), T('crash', 'top', 'crash', db=-27),
              T('bass', 'bass', 'growl', sc=0.7, db=-13),
              T('chords', 'chords', 'warmpad', sc=0.6, rev=0.5, db=-27), T('pad', 'pad', 'choir', sc=0.6, rev=0.5, db=-28),
              T('arp', 'arp', 'bell', dly=0.4, rev=0.3, db=-28), T('lead', 'lead', 'hoover', sc=0.4, rev=0.3, db=-21)],
      master=dict(lufs=-6.5, air=1.6, low=2.0, drive=0.25))

style('melodic_dubstep', 'Electronic', 'Melodic dubstep: emotional chords and a big supersaw theme over half-time drums - the drop '
      'carries the melody, with piano, strings and vocal chops and a heavy but musical bass',
      bpm=(140, 150), scales=['minor', 'major'], sc_depth=0.6, sc_release=0.3, reverb=2.6, kit='hard', form='halftime',
      sub_layer=True, chord_size=4, fill=True,
      progs={'minor': [[5, 3, 0, 4], [0, 5, 2, 6], [0, 5, 3, 4]], 'major': [[3, 4, 5, 0], [0, 4, 5, 3], [5, 3, 0, 4]]},
      drums={'kick': ['X.........X.....', 'X.....X...X.....'], 'snare': [HALF], 'clap': [HALF], 'chat': ['x.x.x.x.x.x.x.x.'],
             'crash': ['X...............']}, snare_tracks=['snare', 'clap'],
      bass=['R-------R-------', 'R---R---R-R-R---', 'R-------R---R---'], bass_lo=26, bass_gate=0.9,
      chord_rh=['x---------------', 'x.xx.x.xx.x.xx.x', 'x--x--x-x--x--x-'], chord_center=64,
      arp=dict(rate=2, mode='updown', oct=5, prob=0.7),
      lead_rh=['x-x-x---x-x-x---', 'x--x--x-x-------', 'x-x-x-x-x---x---', 'x-------x---x---'],
      gm_hint='Supersaw chords + lead; Piano; Strings; Vocal chops; Reese / growl mid-bass over a sine sub',
      tracks=[T('kick', 'kick', 'kick', db=-12), T('snare', 'snare', 'snare', rev=0.3, db=-14), T('clap', 'snare', 'clap', db=-20),
              T('chat', 'top', 'chat', db=-28), T('crash', 'top', 'crash', db=-28),
              T('bass', 'bass', 'reese', sc=0.8, db=-15, p=dict(cut=900)),
              T('chords', 'chords', 'supersaw', sc=0.9, rev=0.4, db=-22), T('pad', 'pad', 'strings', sc=0.6, rev=0.5, db=-25),
              T('arp', 'arp', 'vox', rev=0.3, dly=0.3, db=-25), T('lead', 'lead', 'supersaw_lead', sc=0.5, rev=0.4, dly=0.25, db=-18)],
      master=dict(lufs=-7.5, air=2.0, low=1.5))

style('liquid_dnb', 'Electronic', 'Liquid drum & bass: rolling, swung two-step breaks at 174, warm melodic bass over a sine sub, '
      'Rhodes and jazzy 7th chords, lush pads, soulful leads',
      bpm=(170, 176), scales=['minor', 'dorian', 'major'], swing=0.53, ghosts=True, kit='punchy', form='dnb', form_scale=2,
      sub_layer=True, chord_size=4, sc_depth=0.45, fill=True,
      progs={'minor': [[0, 5, 3, 4], [0, 3, 6, 5], [5, 3, 0, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]], 'major': [[1, 4, 0, 5], [3, 2, 1, 4]]},
      drums={'kick': ['X.........X.....', 'X.........X..x..'], 'snare': [BACKBEAT], 'chat': ['x.xxx.x.x.xxx.x.', 'x.x.x.x.x.x.x.x.'],
             'ride': ['x...x...x...x...'], 'shaker': ['xxxxxxxxxxxxxxxx']}, snare_tracks=['snare'],
      bass=['R-------R-----..', 'R-----R---R-----', 'R---..R---R-....'], bass_lo=28,
      chord_rh=['x-------x-------', 'x---------------'], chord_center=62, arp=dict(rate=2, mode='updown', oct=5, prob=0.6),
      lead_rh=['x-x-x---x-x-....', 'x---x-x-x---....', '..x-x-x-x---x...', 'x-------x---....'],
      gm_hint='Rhodes / piano 7th chords; Warm melodic bass + sine sub; Strings & pads; Vocal or flute lead; rolling breaks',
      tracks=[T('kick', 'kick', 'kick'), T('snare', 'snare', 'snare', rev=0.25, db=-17), T('chat', 'top', 'chat', pan=0.2, db=-27),
              T('ride', 'top', 'ride', pan=-0.25, db=-32), T('shaker', 'top', 'shaker', db=-32),
              T('bass', 'bass', 'moogbass', sc=0.8, db=-15, p=dict(cut=600)),
              T('chords', 'chords', 'epiano', sc=0.5, rev=0.35, db=-22), T('pad', 'pad', 'strings', sc=0.6, rev=0.5, db=-25),
              T('arp', 'arp', 'vibes', rev=0.35, dly=0.3, pan=0.25, db=-27), T('lead', 'lead', 'vox', rev=0.4, dly=0.25, db=-19)],
      master=dict(lufs=-8.5, air=1.6, low=1.2))

style('neurofunk', 'Electronic', 'Neurofunk: tight, technical two-step at 174, dark and mechanical - growls, reese and FM stabs '
      'trading every bar over a sine sub, cold stabs and sparse atmospheres',
      bpm=(172, 176), scales=['minor', 'phrygian'], ghosts=True, kit='hard', form='dnb', form_scale=2, sub_layer=True,
      bass_switch=['reese', 'fmbass'], switch_bars=1, sc_depth=0.6, fill=True,
      progs={'minor': [[0, 0, 0, 0], [0, 0, 5, 6], [0, 6, 0, 5]], 'phrygian': [[0, 1, 0, 0], [0, 0, 1, 0]]},
      drums={'kick': ['X.........X.....', 'X.X.......X..x..', 'X.........XX....'], 'snare': [BACKBEAT, '....X.......X..x'],
             'chat': ['x.xxx.x.x.xxx.x.', 'xxxxxxxxxxxxxxxx'], 'rim': ['......x.......x.']}, snare_tracks=['snare'],
      bass=['R..R..R...R.R...', 'R-.R..R.R..R....', 'RR..R...R.R.R...'], bass_lo=26, bass_gate=0.7,
      chord_rh=['x...............', '......x.......x.'], chord_center=62, arp=dict(rate=2, mode='random', oct=5, prob=0.25),
      lead_rh=['x-------........', 'x---x-----......', '........x-------', 'x.x.............'],
      gm_hint='Neuro / growl / reese mid-basses (resampled, distorted) over a mono sub; tight punchy breaks; cold stabs',
      tracks=[T('kick', 'kick', 'kick', db=-12), T('snare', 'snare', 'snare', rev=0.15, db=-14), T('chat', 'top', 'chat', pan=0.2, db=-26),
              T('rim', 'top', 'rim', pan=-0.2, db=-28), T('bass', 'bass', 'growl', sc=0.8, db=-13),
              T('chords', 'chords', 'stab', sc=0.5, rev=0.3, db=-25), T('pad', 'pad', 'warmpad', sc=0.5, rev=0.5, db=-29, p=dict(cut=800)),
              T('arp', 'arp', 'bell', rev=0.3, dly=0.3, db=-29), T('lead', 'lead', 'leadsaw', sc=0.4, rev=0.35, db=-22)],
      master=dict(lufs=-7.0, air=1.4, low=1.6, drive=0.2))

style('house_phonk', 'Electronic', 'House phonk: four-on-the-floor phonk - distorted detuned cowbell hooks, punchy 808 bass on '
      'the offbeat, hard claps and Memphis vocal chops at club tempo',
      bpm=(128, 142), scales=['phrygian', 'minor', 'phrygian_dominant'], kit='808', form='phonk', sc_depth=0.55, sc_release=0.25,
      progs={'phrygian': [[0, 0, 1, 0], [0, 1, 0, 6]], 'minor': [[0, 0, 5, 6], [0, 5, 0, 6]], 'phrygian_dominant': [[0, 1, 0, 1], [0, 3, 1, 0]]},
      kit_override=dict(kick=dict(drive=5.0), clap=dict(drive=2.0)),
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.', 'x.xxx.x.x.xxx.x.'], 'ohat': [OFFHAT],
             'cowbell808': ['..x.......x.....']}, snare_tracks=['clap'],
      bass=['..R...R...R...R.', '..R..RR...R..RR.', '.RR..RR..RR..RR.'], bass_lo=28, bass_gate=0.6,
      chord_rh=['x---------------'], arp=dict(rate=4, mode='random', oct=5, prob=0.35),
      gm_hint='Distorted phonk cowbell; offbeat distorted bass; hard four-on-the-floor kick; Memphis vocal chops',
      tracks=[T('kick', 'kick', 'kick', db=-12, drive=0.3), T('clap', 'snare', 'clap', rev=0.2, db=-17), T('chat', 'top', 'chat', db=-27),
              T('ohat', 'top', 'ohat', db=-27), T('cowbell808', 'top', 'cowbell808', pan=-0.2, db=-31),
              T('bass', 'bass', '808', sc=0.6, db=-12, drive=0.4, p=dict(drive=7.0, decay=0.3)),
              T('chords', 'chords', 'warmpad', sc=0.6, rev=0.4, db=-29, p=dict(cut=700)),
              T('arp', 'arp', 'vox', rev=0.3, dly=0.25, db=-24),
              T('lead', 'lead', 'cowbell', sc=0.3, rev=0.2, db=-15),],
      lead_lo=57, chord_center=55, repetition=0.9, simplicity=0.25,
      lead_rh=['x..x..x.........', 'x.x.x...x.......', 'x..x..x.x..x....', 'x.xx.x..x.x.....', 'x.x.x.x.x..x..x.'],
      master=dict(lufs=-7.0, air=0.0, low=2.4, drive=0.4, lofi=True, wobble=0.2))

style('memphis_phonk', 'Electronic', 'Memphis phonk: the original - slow, dusty and lo-fi, eerie cowbell and piano loops, rattling '
      '808 hats and cowbells, chopped vocal shouts, cassette grit',
      bpm=(66, 92), scales=['minor', 'phrygian', 'harmonic_minor'], kit='808', form='phonk', human=0.006, trap_hats=False, sc_depth=0.2,
      progs={'minor': [[0, 0, 5, 5], [0, 6, 5, 6], [0, 0, 0, 5]], 'phrygian': [[0, 1, 0, 0]], 'harmonic_minor': [[0, 0, 4, 4]]},
      kit_override=dict(kick=dict(drive=3.0)),
      drums={'kick': ['X.....X...X.....', 'X..X......X.....'], 'snare': [BACKBEAT], 'clap': [BACKBEAT],
             'chat': ['x.xxx.xxx.xxx.xx', 'xxx.xxx.xxx.xxx.'], 'cowbell808': ['x.....x...x.....', '..x...x...x...x.']},
      snare_tracks=['snare', 'clap'], bass_mode='808', bass_lo=26,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=60, arp=dict(rate=4, mode='random', oct=5, prob=0.4),
      lead_rh=['x...x...x...x...', 'x.x...x.x.x.....', 'x---x---x-------', 'x..x..x.........'],
      gm_hint='808 kit (rattling hats, cowbell); eerie piano or bell loop; pitched-down Memphis vocal chops; tape hiss',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.2, db=-17), T('clap', 'snare', 'clap', db=-21),
              T('chat', 'top', 'chat', pan=0.2, db=-26), T('cowbell808', 'top', 'cowbell808', pan=-0.25, db=-26),
              T('bass', 'bass', '808', db=-12, p=dict(drive=4.0, decay=0.5)),
              T('chords', 'chords', 'piano', rev=0.3, db=-23), T('arp', 'arp', 'vox', rev=0.3, dly=0.3, db=-23),
              T('pad', 'pad', 'choir', rev=0.6, db=-31, p=dict(vowel='o', cut=900)),
              T('lead', 'lead', 'cowbell', rev=0.25, db=-16)],
      lead_lo=57, repetition=0.9, simplicity=0.3,
      master=dict(lufs=-9.0, air=-1.0, low=2.0, lofi=True, wobble=0.8))

LABELS.update({'dubstep': 'Dubstep (Dark / UK)', 'brostep': 'Brostep', 'melodic_dubstep': 'Melodic Dubstep', 'liquid_dnb': 'Liquid DnB',
               'neurofunk': 'Neurofunk', 'house_phonk': 'House Phonk', 'memphis_phonk': 'Memphis Phonk', 'phonk': 'Drift Phonk'})
STYLES['phonk']['scales'] = ['phrygian', 'minor', 'harmonic_minor']

POOLS.update({
    'brostep': dict(bass=['growl', 'wobble', 'fmbass', 'reese'], chords=['warmpad', 'supersaw', 'strings'], pad=['choir', 'warmpad', 'glasspad'],
                    arp=['bell', 'pluck_saw', 'chip'], lead=['hoover', 'leadsaw', 'supersaw_lead', 'vox']),
    'melodic_dubstep': dict(bass=['reese', 'growl', 'fmbass', 'sawbass'], chords=['supersaw', 'piano', 'polysynth', 'stab'],
                            pad=['strings', 'choir', 'glasspad', 'warmpad'], arp=['vox', 'bell', 'pluck_saw', 'piano', 'celesta'],
                            lead=['supersaw_lead', 'leadsaw', 'vox', 'piano', 'pluck_saw']),
    'liquid_dnb': dict(bass=['moogbass', 'sinebass', 'reese', 'sf:fingerbass'], chords=['epiano', 'piano', 'wurli', 'polysynth', 'strings'],
                       pad=['strings', 'glasspad', 'warmpad', 'choir', 'solina'], arp=['vibes', 'bell', 'piano', 'harp', 'celesta'],
                       lead=['vox', 'flute', 'softlead', 'sax', 'piano', 'guitar']),
    'neurofunk': dict(bass=['growl', 'reese', 'fmbass', 'wobble'], chords=['stab', 'warmpad', 'bell'], pad=['warmpad', 'glasspad', 'choir'],
                      arp=['bell', 'chip', 'pluck_saw'], lead=['leadsaw', 'stab', 'hoover', 'bell']),
    'house_phonk': dict(bass=['808', 'fmbass'], chords=['warmpad', 'organ'], arp=['vox', 'phonkbell'],
                        lead=['cowbell', 'cowbell', 'cowbell_808', 'cowbell_dist', 'cowbell_long']),
    'memphis_phonk': dict(chords=['piano', 'organ', 'warmpad', 'epiano'], arp=['vox', 'phonkbell', 'bell'],
                          lead=['cowbell', 'cowbell', 'cowbell_808', 'cowbell_dist', 'cowbell_long']),
})
STYLES['dubstep']['progs'] = {'minor': [[0, 0, 5, 6], [0, 5, 0, 6], [0, 0, 0, 6]], 'phrygian': [[0, 0, 1, 0], [0, 1, 0, 6], [0, 0, 0, 1]]}
STYLES['brostep']['progs'] = {'minor': [[0, 0, 5, 6], [0, 6, 5, 6]], 'phrygian': [[0, 0, 1, 0], [0, 1, 0, 6]],
                              'harmonic_minor': [[0, 0, 5, 4], [0, 5, 0, 4]]}
for _n in ('brostep', 'melodic_dubstep'):
    STYLES[_n]['form_scale'] = 1.75


# ---------------------------------------------------------------------------------------------------------------
# v1.14: classic UK dubstep, emotional progressive trance, organic melodic house, 70s disco-funk
style('tempa_dubstep', 'Electronic', 'Classic UK dubstep (early Tempa / DMZ era): half-time 140, heavy sub-bass pressure, sparse shuffled '
      '2-step drums, dub reverb and delay, dark negative space - soundsystem music, not festival brostep',
      bpm=(138, 142), scales=['minor', 'phrygian'], swing=0.56, swing_unit=16, human=0.006, kit='punchy', form='groove',
      form_scale=1.5, chord_size=3, sc_depth=0.15, reverb=3.0, delay_beats=0.75,
      progs={'minor': [[0, 0, 0, 5], [0, 0, 6, 5], [0, 0, 0, 3], [0, 5, 0, 6]], 'phrygian': [[0, 0, 1, 0], [0, 1, 0, 6]]},
      kit_override={'kick': {'drive': 1.6, 'decay': 6}, 'snare': {'snap': 1.3, 'decay': 9}},
      drums={'kick': ['X.........X.....', 'X.....X.......X.', 'X.........X..x..'], 'snare': ['........X.......'],
             'rim': ['...x......x...x.', '......x.....x...', '...x..x.......x.'],
             'chat': ['..x...x.x...x...', '....x.....x...x.', '..x.....x.x.....'], 'ohat': ['..............x.', '................']},
      snare_tracks=['snare'], ghosts=False, fill=False,
      bass=['R-------....R---', 'R---..R-R-------', 'R-----..R-..R---', 'R-------R---..R-'], bass_lo=26, bass_gate=0.95,
      chord_rh=['....x...........', '........x.......', '............x...', '....x.......x...'], chord_center=60,
      arp=dict(rate=4, mode='random', oct=5, prob=0.25), lead_oct=5,
      lead_rh=['x-------........', '........x---....', 'x---............', '....x-------....'],
      sub_layer=True, repetition=0.75, simplicity=0.3,
      gm_hint='Clean sine sub (the lead instrument); dub chord stabs into long delays; eerie bells / melodica; dark drones',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.4, dly=0.2, db=-17),
              T('rim', 'top', 'rim', pan=0.2, dly=0.35, rev=0.3, db=-27), T('chat', 'top', 'chat', pan=-0.25, db=-31),
              T('ohat', 'top', 'ohat', pan=0.3, rev=0.3, db=-31),
              T('bass', 'bass', 'sinebass', db=-12, p=dict(cut=300)),
              T('chords', 'chords', 'stab', rev=0.5, dly=0.6, db=-26, p=dict(cut=1600)),
              T('pad', 'pad', 'warmpad', rev=0.6, db=-31, p=dict(cut=900, a=0.6)),
              T('arp', 'arp', 'bell', rev=0.6, dly=0.5, pan=0.3, db=-31),
              T('lead', 'lead', 'flute', rev=0.5, dly=0.4, pan=-0.15, db=-24),
              T('texture', 'fx', 'texture', rev=0.6, db=-35)],
      master=dict(lufs=-10.5, air=0.8, low=2.0))

style('progressive_trance', 'Electronic', 'Emotional progressive trance / melodic progressive house: simple emotive chords, a big singable lead, '
      'long builds, a piano breakdown and a clean, wide drop - melody over complexity',
      bpm=(128, 136), scales=['minor', 'major'], swing=0.5, kit='909', form='trance', form_scale=1.0, chord_size=3,
      sc_depth=0.45, sc_release=0.45, reverb=2.4, delay_beats=0.75,
      progs={'minor': [[0, 5, 2, 6], [5, 6, 0, 0], [0, 3, 5, 6], [0, 5, 3, 4]], 'major': [[0, 4, 5, 3], [5, 3, 0, 4], [3, 4, 5, 5]]},
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.x.x.x.x.x.x.x.'], 'ride': ['....x.......x...', '']},
      snare_tracks=['clap'], fill=True,
      bass=['.RRR.RRR.RRR.RRR', '..R...R...R...R.'], bass_lo=31, bass_gate=0.6,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=64, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x---x---x-x-x---', 'x-------x---x---', 'x---x-x-x-------', 'x-x-x---x-------'],
      repetition=0.8, simplicity=0.35,
      gm_hint='Supersaw or clean pluck lead; grand piano (breakdown); wide strings / pads; rolling off-beat bass',
      tracks=[T('kick', 'kick', 'kick'), T('clap', 'snare', 'clap', rev=0.25), T('ohat', 'top', 'ohat', pan=0.15, db=-28),
              T('chat', 'top', 'chat', pan=-0.2, db=-31), T('ride', 'top', 'ride', pan=0.3, db=-31),
              T('bass', 'bass', 'sawbass', sc=1.0, p=dict(cut=900)),
              T('chords', 'chords', 'supersaw', sc=0.9, rev=0.4, db=-25, p=dict(cut=5000)),
              T('pad', 'pad', 'strings', sc=0.6, rev=0.6, db=-27),
              T('arp', 'arp', 'pluck_saw', sc=0.7, rev=0.35, dly=0.3, pan=-0.2, db=-27),
              T('lead', 'lead', 'supersaw_lead', sc=0.4, rev=0.45, dly=0.25, db=-19)],
      master=dict(lufs=-8.5, air=2.0, low=1.0))

style('organic_house', 'Electronic', 'Organic melodic deep house: warm four-on-the-floor with shakers and congas, piano, flute and soft '
      'strings, nature-like atmosphere - spacious, hypnotic and simple, no big drops',
      bpm=(120, 124), scales=['minor', 'dorian', 'major'], swing=0.53, kit='soft', form='groove', chord_size=3,
      sc_depth=0.3, sc_release=0.5, reverb=2.6, delay_beats=0.75,
      progs={'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]], 'major': [[0, 4, 5, 3], [3, 0, 4, 0]]},
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'shaker': ['x.xxx.xxx.xxx.xx', 'x.x.x.x.x.x.x.x.'],
             'conga': ['......o.......o.', '..o.....o.o.....', '...o..o....o..o.'], 'ohat': [OFFHAT], 'rim': ['...x......x.....']},
      snare_tracks=['clap'],
      bass=['R..R..R.R..R..R.', 'R-..R-..R-..R-..', '..R...R...R..R..'], bass_lo=31, bass_gate=0.7,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=62, arp=dict(rate=2, mode='updown', oct=5),
      lead_rh=['x---x-x-x-------', 'x-------x---x---', 'x---x---x-x-x---', '..x-x-x-x-------'],
      repetition=0.8, simplicity=0.35,
      gm_hint='Grand / felt piano; flute; soft strings; harp or plucked guitar; shakers and congas; nature field recordings',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('clap', 'snare', 'clap', rev=0.35, db=-22), T('shaker', 'top', 'shaker', pan=0.3, db=-28),
              T('conga', 'top', 'conga', pan=-0.25, db=-26), T('ohat', 'top', 'ohat', db=-29), T('rim', 'top', 'rim', pan=0.2, db=-30),
              T('bass', 'bass', 'sinebass', sc=0.5, db=-14, p=dict(cut=400)),
              T('chords', 'chords', 'piano', rev=0.5, db=-23), T('pad', 'pad', 'strings', sc=0.4, rev=0.6, db=-28, p=dict(a=0.5)),
              T('arp', 'arp', 'harp', rev=0.45, dly=0.3, pan=0.25, db=-26), T('lead', 'lead', 'flute', rev=0.45, dly=0.25, db=-20),
              T('texture', 'fx', 'texture', rev=0.5, db=-36)],
      master=dict(lufs=-10.0, air=1.6, low=1.2))

style('disco_funk', 'Classic', '70s disco-funk: punchy dry four-on-the-floor, a syncopated electric-bass hook, chicken-scratch guitar, '
      'tight horn-section riffs, claps, congas and tambourine - bright, catchy party music',
      bpm=(112, 122), scales=['major', 'mixolydian', 'dorian'], swing=0.53, human=0.006, kit='acoustic', form='song',
      chord_size=4, sc_depth=0.0, reverb=1.0, delay_beats=0.5,
      progs={'major': [[0, 3, 0, 3], [0, 3, 4, 3], [0, 5, 1, 4], [0, 0, 3, 4]], 'mixolydian': [[0, 6, 3, 0], [0, 3, 0, 6]],
             'dorian': [[0, 3, 0, 3], [0, 3, 6, 4]]},
      drums={'kick': [FOUR], 'snare': [BACKBEAT], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.x.x.x.x.x.x.x.'],
             'tamb': ['..x...x...x...x.', 'x.xxx.xxx.xxx.xx'], 'conga': ['...x..x....x.x..', '......x..x....x.']},
      snare_tracks=['snare'], fill=True, ghosts=True,
      bass=['R..O.R.OR.R..O.A', 'R.R..O.RR..O.RA.', 'R...R.OR..R.O.R.', 'R.OR..R.R.OR..A.'], bass_lo=31, bass_gate=0.7,
      chord_rh=['.x.x.x.x.x.x.x.x', 'x.xx.x.xx.xx.x.x', '..x...x...x...x.'], chord_center=64, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x.x.x-..........', '..x.x.x-..x.x-..', 'x-x-x---........', 'x.x-..x.x-......'],
      repetition=0.7,
      gm_hint='Horn section (trumpet, sax, trombone); chicken-scratch guitar; electric bass; clavinet / Rhodes; strings for gloss',
      tracks=[T('kick', 'kick', 'kick', db=-14), T('snare', 'snare', 'snare', rev=0.15, db=-18), T('clap', 'snare', 'clap', rev=0.12, db=-22),
              T('ohat', 'top', 'ohat', pan=0.2, db=-28), T('chat', 'top', 'chat', pan=-0.2, db=-30),
              T('tamb', 'top', 'tamb', pan=0.35, db=-29), T('conga', 'top', 'conga', pan=-0.3, db=-27),
              T('bass', 'bass', 'pluck', db=-14, p=dict(bright=1600, damp=0.996)),
              T('chords', 'chords', 'mutedgtr', pan=-0.25, rev=0.12, db=-23),
              T('pad', 'pad', 'strings', pan=0.2, rev=0.35, db=-29),
              T('arp', 'arp', 'clav', pan=0.25, rev=0.15, db=-26),
              T('lead', 'lead', 'brass', rev=0.2, db=-18)],
      master=dict(lufs=-10.0, air=2.0, low=1.0))

LABELS.update({'tempa_dubstep': 'Dubstep (classic UK / Tempa)', 'progressive_trance': 'Progressive Trance (emotional)',
               'organic_house': 'Organic Melodic House', 'disco_funk': 'Disco Funk (70s)'})
POOLS.update({
    'tempa_dubstep': {'bass': ['sinebass', 'wobble', 'reese'], 'chords': ['stab', 'organ', 'warmpad', 'epiano'],
                      'pad': ['warmpad', 'strings', 'glasspad', 'choir'], 'arp': ['bell', 'celesta', 'pluck'],
                      'lead': ['flute', 'bell', 'vox', 'organ', 'softlead']},
    'progressive_trance': {'bass': ['sawbass', 'moogbass', 'fmbass'], 'chords': ['supersaw', 'piano', 'pluck_saw', 'polysynth', 'stab'],
                           'pad': ['strings', 'warmpad', 'glasspad', 'choir', 'supersaw'], 'arp': ['pluck_saw', 'pluck', 'piano', 'bell'],
                           'lead': ['supersaw_lead', 'pluck_saw', 'piano', 'leadsaw', 'vox']},
    'organic_house': {'bass': ['sinebass', 'moogbass', 'upright'], 'chords': ['piano', 'epiano', 'warmpad', 'guitar', 'strings'],
                      'pad': ['strings', 'glasspad', 'warmpad', 'choir', 'solina'], 'arp': ['harp', 'pluck', 'guitar', 'marimba', 'kalimba'],
                      'lead': ['flute', 'piano', 'violin', 'pluck', 'sf:nylon', 'vox', 'cello']},
    'disco_funk': {'bass': ['pluck', 'sf:fingerbass', 'sf:slapbass', 'moogbass'], 'chords': ['mutedgtr', 'guitar', 'clav', 'epiano', 'organ'],
                   'pad': ['strings', 'organ', 'synthbrass', 'solina'], 'arp': ['clav', 'epiano', 'mutedgtr', 'piano'],
                   'lead': ['brass', 'trumpet', 'sax', 'synthbrass', 'flute']},
})


# ---------------------------------------------------------------------------------------------------------------
# phonk: sparse intro (cowbell + atmosphere) -> main -> main -> breakdown (bass + atmosphere) -> denser drop -> degrading outro.
# Tight, hypnotic and short; no long EDM build-ups.
_PH_FULL = {'kick', 'snare', 'top', 'bass', 'lead', 'chords', 'pad', 'fx'}
FORMS['phonk'] = [('intro', 8, {'lead', 'pad', 'fx'}, {'filter_in': True}),
                  ('verse', 16, _PH_FULL, {'crash': True}),
                  ('verse', 16, _PH_FULL | {'arp'}, {}),
                  ('break', 8, {'bass', 'pad', 'fx', 'arp'}, {'alt': True}),
                  ('drop', 16, _PH_FULL | {'arp'}, {'drop': True, 'crash': True}),
                  ('outro', 8, {'lead', 'pad', 'fx'}, {'fade': True})]

style('brazilian_phonk', 'Electronic', 'Brazilian phonk: baile-funk bounce under phonk grit - syncopated tamborzao drums, a distorted '
      'pitched cowbell riff, heavy distorted sub, chopped vocal shouts; gritty and danceable',
      bpm=(130, 150), scales=['minor', 'phrygian'], kit='808', form='phonk', swing=0.52, human=0.004,
      progs={'minor': [[0, 0, 0, 0], [0, 0, 5, 0]], 'phrygian': [[0, 0, 1, 0], [0, 0, 0, 0]]},
      sc_depth=0.35, sc_release=0.2, reverb=1.3,
      kit_override=dict(kick=dict(drive=5.0), clap=dict(drive=2.0), snare=dict(drive=2.5)),
      drums={'kick': ['X..X..X...X..X..', 'X..X..X...X.X...', 'X..X..X.X..X..X.'], 'snare': ['....X..X....X...', '...X..X....X..X.'],
             'clap': ['....x.......x...'], 'conga': ['..o..o..o..o..o.', '.o..o.o..o..o.o.'], 'chat': ['x.x.x.x.x.x.x.x.', 'x.xxx.x.x.xxx.x.'],
             'cowbell808': ['..x.......x.....', '......x.......x.']},
      snare_tracks=['snare', 'clap'], bass_mode='808', bass_lo=26,
      chord_rh=['x---------------'], arp=dict(rate=4, mode='random', oct=4, prob=0.3),
      lead_rh=['x..x..x.x..x....', 'x..x..x...x.x...', 'x.xx.x..x.x.....', 'x..x..x.........'],
      lead_lo=57, repetition=0.9, simplicity=0.25,
      gm_hint='Distorted pitched 808 cowbell; baile funk tamborzao (kick, snare, congas); distorted sub 808; vocal shouts',
      tracks=[T('kick', 'kick', 'kick', db=-12, drive=0.4), T('snare', 'snare', 'snare', rev=0.15, db=-17), T('clap', 'snare', 'clap', rev=0.2, db=-20),
              T('conga', 'top', 'conga', pan=-0.25, db=-24), T('chat', 'top', 'chat', pan=0.2, db=-27),
              T('cowbell808', 'top', 'cowbell808', pan=0.25, db=-29),
              T('bass', 'bass', '808', sc=0.35, db=-11, drive=0.4, p=dict(drive=8.0, decay=0.35)),
              T('chords', 'chords', 'warmpad', rev=0.4, db=-31, p=dict(cut=700)),
              T('pad', 'pad', 'choir', rev=0.5, db=-32, p=dict(vowel='o')),
              T('arp', 'arp', 'vox', rev=0.25, dly=0.2, db=-23),
              T('lead', 'lead', 'cowbell', rev=0.2, db=-15),],
      master=dict(lufs=-7.0, air=0.2, low=2.4, drive=0.4))
LABELS['brazilian_phonk'] = 'Brazilian Phonk'
POOLS['brazilian_phonk'] = dict(lead=['cowbell', 'cowbell', 'cowbell_dist', 'cowbell_808', 'cowbell_long'], bass=['808'], chords=['warmpad', 'organ', 'stab'], arp=['vox', 'phonkbell'])


# ---------------------------------------------------------------------------------------------------------------
# v1.18: genres from the technical production bibles (tempo / feel / grid / sound / arrangement as specified there)
style('italo_disco', 'Electronic', 'Italo disco / Eurodisco (early-mid 80s): four-on-the-floor with a gated-reverb snare on 2 and 4, a '
      'melodic octave synth bassline, bright Juno / Jupiter / DX7 arps and anthemic leads - cleaner and more synthetic than disco',
      bpm=(116, 126), scales=['minor', 'major'], kit='linn', form='song', sc_depth=0.2, swing=0.5,
      progs={'minor': [[0, 5, 2, 6], [0, 3, 6, 5], [0, 5, 3, 4]], 'major': [[0, 4, 5, 3], [5, 3, 0, 4]]},
      drums={'kick': [FOUR], 'snare': [BACKBEAT], 'chat': ['x.x.x.x.x.x.x.x.'], 'ohat': [OFFHAT], 'tamb': ['....x.......x...']},
      snare_tracks=['snare'], bass=['R.O.R.O.R.O.R.O.', 'R.O.R.R.O.R.O.R.', 'RRO.RRO.RRO.RRO.'], bass_gate=0.55, bass_lo=33,
      chord_rh=['x-------x-------', 'x---x---x---x---'], chord_center=64, arp=dict(rate=1, mode='up', oct=5),
      lead_rh=['x-x-x---x-x-x---', 'x---x---x-x-x-x-', 'x-x-x-x-x-------', 'x-------x---x-x-'], repetition=0.75,
      gm_hint='Juno / Jupiter octave bass; DX7 / PPG brass and bells; bright saw lead; vocoder; LinnDrum with gated snare',
      tracks=[T('kick', 'kick', 'kick', db=-13), T('snare', 'snare', 'snare', rev=0.3, db=-16), T('chat', 'top', 'chat', pan=0.2, db=-28),
              T('ohat', 'top', 'ohat', db=-28), T('tamb', 'top', 'tamb', pan=-0.3, db=-30),
              T('bass', 'bass', 'sawbass', sc=0.3, db=-14, p=dict(cut=1300)), T('chords', 'chords', 'polysynth', rev=0.35, db=-24),
              T('pad', 'pad', 'solina', rev=0.5, db=-28), T('arp', 'arp', 'pluck_saw', dly=0.3, pan=0.25, db=-27),
              T('lead', 'lead', 'leadsaw', rev=0.4, dly=0.3, db=-19)],
      master=dict(lufs=-10.0, air=2.0, low=0.8))

style('new_beat', 'Electronic', 'New beat (late-80s Belgium): slow, heavy, stomping four-on-the-floor at ~100-115 BPM, industrial EBM '
      'drums, dark acid-tinged bass and sampled stabs - hypnotic and menacing',
      bpm=(100, 116), scales=['minor', 'phrygian'], kit='techno', form='groove', sc_depth=0.15, swing=0.52,
      progs={'minor': [[0, 0, 0, 0], [0, 0, 5, 6]], 'phrygian': [[0, 1, 0, 1], [0, 0, 1, 0]]},
      drums={'kick': [FOUR], 'snare': [BACKBEAT], 'clap': ['....X.......X..x'], 'chat': ['..x...x...x...x.'],
             'rim': ['...x..x....x..x.']},
      snare_tracks=['snare', 'clap'], bass=['R.RR.RR.R.RR.RR.', 'R.R.R.RRR.R.R.RR'], bass_mode='acid', bass_lo=31,
      chord_rh=['x...............', '....x.......x...'], chord_center=58, arp=dict(rate=2, mode='random', oct=4, prob=0.5),
      lead_rh=['x-------........', 'x---....x---....'], repetition=0.85, simplicity=0.4,
      tracks=[T('kick', 'kick', 'kick', db=-12, drive=0.5), T('snare', 'snare', 'snare', rev=0.35, db=-16, drive=0.4),
              T('clap', 'snare', 'clap', rev=0.3, db=-20), T('chat', 'top', 'chat', db=-28), T('rim', 'top', 'rim', pan=0.3, db=-29),
              T('bass', 'bass', 'acid', db=-14, p=dict(res=7, cut=500)), T('chords', 'chords', 'stab', rev=0.45, dly=0.3, db=-25),
              T('pad', 'pad', 'choir', rev=0.6, db=-30), T('arp', 'arp', 'pluck_saw', dly=0.4, db=-29),
              T('lead', 'lead', 'vox', rev=0.4, dly=0.3, db=-22)],
      master=dict(lufs=-9.5, air=0.6, low=1.6, drive=0.3))

style('gabber', 'Electronic', 'Hardcore / gabber (90s Rotterdam): 170-200 BPM four-on-the-floor of heavily distorted, pitched '
      '"gabber" kicks, screeching leads, hoovers and raw, confrontational energy',
      bpm=(170, 195), scales=['minor', 'phrygian'], kit='hard', form='edm', sc_depth=0.5, swing=0.5,
      kit_override={'kick': {'drive': 14.0, 'pitch': 52, 'decay': 4.5, 'punch': 380, 'len': 0.5}},
      progs={'minor': [[0, 0, 5, 6], [0, 5, 6, 4]], 'phrygian': [[0, 1, 0, 1]]},
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.x.x.x.x.x.x.x.']},
      snare_tracks=['clap'], bass=['................'], bass_lo=31,
      chord_rh=['x...x...x...x...', 'x.x.x.x.x.x.x.x.'], chord_center=62, arp=dict(rate=1, mode='random', oct=5),
      lead_rh=['x.x.x.x.x.x.x.x.', 'x-x-x-x-x-x-x-x-', 'xxx.x.x.xxx.x.x.'], repetition=0.8,
      tracks=[T('kick', 'kick', 'kick', db=-10, drive=0.9), T('clap', 'snare', 'clap', rev=0.2, db=-18),
              T('ohat', 'top', 'ohat', db=-27), T('chat', 'top', 'chat', db=-29),
              T('bass', 'bass', 'sinebass', db=-30), T('chords', 'chords', 'hoover', rev=0.3, db=-22, drive=0.5),
              T('pad', 'pad', 'choir', rev=0.5, db=-30), T('arp', 'arp', 'pluck_saw', dly=0.2, db=-27),
              T('lead', 'lead', 'leadsaw', rev=0.3, db=-18, drive=0.6)],
      master=dict(lufs=-7.0, air=1.2, low=1.8, drive=0.6))

style('rave_hardcore', 'Electronic', 'Breakbeat hardcore / early UK rave (1990-93): Amen-style breaks over a four-on-the-floor kick, '
      'piano stabs, hoover and Mentasm leads, pitched-up vocal chops - funky, chaotic, euphoric',
      bpm=(135, 155), scales=['minor', 'major'], kit='acoustic', form='edm', sc_depth=0.3, swing=0.52,
      progs={'minor': [[0, 5, 3, 4], [0, 5, 6, 4]], 'major': [[0, 4, 5, 3], [0, 3, 4, 4]]},
      drums={'kick': [FOUR], 'snare': ['....X..x.x..X..x'], 'ride': ['x.x.x.x.x.x.x.x.']},
      snare_tracks=['snare'], bass=['R...R...R...R...', 'R..RR..RR..RR..R'], bass_lo=31,
      chord_rh=['x..x..x...x..x..', 'x.x..x..x.x..x..'], chord_center=64, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x-x-x---x-x-x---', 'x---x---x-x-x---', 'x.x.x.x.x.x.x.x.'],
      tracks=[T('kick', 'kick', 'kick', db=-12), T('snare', 'snare', 'snare', rev=0.15, db=-15), T('ride', 'top', 'ride', db=-27),
              T('bass', 'bass', 'sinebass', sc=0.3, db=-14), T('chords', 'chords', 'piano', rev=0.3, db=-20),
              T('pad', 'pad', 'choir', rev=0.5, db=-28), T('arp', 'arp', 'vox', dly=0.25, db=-24),
              T('lead', 'lead', 'hoover', rev=0.3, db=-19)],
      master=dict(lufs=-8.5, air=1.6, low=1.2, drive=0.3))

style('future_funk', 'Electronic', 'Future funk: pitched-up, chopped 70s/80s disco and city-pop flavour over a swung four-on-the-floor '
      'with heavy sidechain pumping - funky bass, filter sweeps, vocal chops; bright and nostalgic',
      bpm=(115, 126), scales=['major', 'dorian'], kit='909', form='edm', sc_depth=0.85, sc_release=0.3, swing=0.57, chord_size=4,
      progs={'major': [[3, 2, 1, 4], [1, 4, 0, 5], [3, 4, 2, 5]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]]},
      drums={'kick': [FOUR], 'clap': [BACKBEAT], 'ohat': [OFFHAT], 'chat': ['x.xxx.xxx.xxx.xx'], 'tamb': ['....x.......x...']},
      snare_tracks=['clap'], bass=['R..O.R...RR.O..A', 'R.R..O.R..R.O.R.', 'R..O..R.R.O..R.A'], bass_gate=0.5, bass_lo=31,
      chord_rh=['x..x..x.x..x..x.', '.x.x..x..x.x..x.'], chord_center=64, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x.x.x...x.x.x...', '..x.x.x...x.x...', 'x.xx.x..x.xx.x..'],
      tracks=[T('kick', 'kick', 'kick', db=-12), T('clap', 'snare', 'clap', rev=0.25, db=-18), T('ohat', 'top', 'ohat', db=-27),
              T('chat', 'top', 'chat', pan=0.2, db=-29), T('tamb', 'top', 'tamb', pan=-0.3, db=-30),
              T('bass', 'bass', 'pluck', sc=0.7, db=-14, p=dict(bright=1800, damp=0.996)),
              T('chords', 'chords', 'epiano', sc=0.9, rev=0.3, db=-22), T('pad', 'pad', 'strings', sc=0.8, rev=0.4, db=-27),
              T('arp', 'arp', 'vox', sc=0.6, dly=0.25, db=-23), T('lead', 'lead', 'vox', sc=0.5, rev=0.3, db=-19)],
      master=dict(lufs=-8.5, air=2.4, low=1.0))

# ---- jazz
style('bebop', 'Classic', 'Bebop: fast swing, dense 8th-note lines built from chord tones, tensions and chromatic approach notes over '
      'rapid ii-V changes; ride and walking bass drive, piano comps rootless voicings',
      bpm=(180, 260), scales=['major', 'minor'], swing=0.62, human=0.007, chord_size=4, voicing='rootless', form='jazz',
      progs={'major': [[1, 4, 0, 0], [2, 5, 1, 4], [1, 4, 2, 5], [0, 5, 1, 4]], 'minor': [[1, 4, 0, 0], [0, 3, 1, 4]]},
      chord_bars=1, drums={'ride': ['x...x.x.x...x.x.'], 'chat': ['....x.......x...'], 'kick': ['o...o...o...o...'],
                           'snare': ['................']},
      snare_tracks=['snare'], comp_snare=True, bass=['R.......R.......'], bass_mode='walk', bass_lo=36,
      chord_rh=['...x-.....x-....', '.x-.....x-..x-..', '......x-..x-....'], chord_center=60, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x.x.x.x.x.x.x.x.', 'x.x.x.x.x.x.x-..', '..x.x.x.x.x.x.x.', 'x.x.x.x.x-..x.x.'],
      tracks=[T('ride', 'top', 'ride', pan=0.3, db=-26), T('chat', 'top', 'chat', pan=-0.2, db=-30), T('kick', 'kick', 'kick', db=-24),
              T('snare', 'snare', 'snare', rev=0.2, db=-24), T('bass', 'bass', 'upright', db=-15),
              T('chords', 'chords', 'piano', rev=0.2, pan=-0.15, db=-23), T('lead', 'lead', 'sax', rev=0.25, db=-17)],
      master=dict(lufs=-14.0, air=1.2, low=0.8))

style('modal_jazz', 'Classic', 'Cool / modal jazz (Kind of Blue era): long stretches on one mode, medium tempo, lots of space, quartal-ish '
      'piano voicings, muted trumpet and tenor sax, brushes and ride, walking bass',
      bpm=(110, 150), scales=['dorian', 'mixolydian', 'lydian'], swing=0.6, human=0.008, chord_size=4, voicing='open', form='jazz',
      progs={'dorian': [[0, 0, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]], 'mixolydian': [[0, 0, 0, 0], [0, 0, 6, 6]],
             'lydian': [[0, 0, 1, 1]]}, chord_bars=2,
      drums={'ride': ['x...x.x.x...x.x.'], 'chat': ['....x.......x...'], 'kick': ['o.......o.......'], 'snare': ['................']},
      snare_tracks=['snare'], comp_snare=True, bass=['R.......R.......'], bass_mode='walk', bass_lo=36,
      chord_rh=['x-......x-......', '...x-.......x-..', 'x-..........x-..'], chord_center=60, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x---x-x-x-------', 'x-x-x---....x---', '....x-x-x---x---', 'x-------x-x-x---'], repetition=0.6,
      tracks=[T('ride', 'top', 'ride', pan=0.3, db=-27), T('chat', 'top', 'chat', pan=-0.2, db=-31), T('kick', 'kick', 'kick', db=-26),
              T('snare', 'snare', 'snare', rev=0.2, db=-26), T('bass', 'bass', 'upright', db=-15),
              T('chords', 'chords', 'piano', rev=0.25, pan=-0.15, db=-24), T('lead', 'lead', 'trumpet', rev=0.3, db=-18)],
      master=dict(lufs=-15.0, air=1.0, low=0.8))

style('soul_jazz', 'Classic', 'Hard bop / soul jazz: organ trio grooves - Hammond B3 comping and bass, bluesy guitar and tenor sax, '
      'gospel-tinged harmony, hard swing or straight-8th backbeat',
      bpm=(100, 140), scales=['dorian', 'mixolydian', 'minor'], swing=0.6, human=0.007, chord_size=4, form='jazz',
      progs={'dorian': [[0, 3, 0, 3], [0, 0, 3, 3]], 'mixolydian': [[0, 3, 0, 4], [0, 0, 3, 0]], 'minor': [[0, 3, 0, 4]]},
      drums={'kick': ['X.....X...X.....'], 'snare': [BACKBEAT], 'ride': ['x...x.x.x...x.x.'], 'chat': ['....x.......x...']},
      snare_tracks=['snare'], ghosts=True, bass=['R.......R.......'], bass_mode='walk', bass_lo=33,
      chord_rh=['.x-...x-.x-...x-', 'x-..x-..x-..x-..', '...x-..x-..x-...'], chord_center=60, arp=dict(rate=2, mode='up', oct=5),
      lead_rh=['x.x.x-..x.x.x---', 'x-x-x.x.x-......', '..x.x.x-x.x.x---'], melody_style='blues',
      tracks=[T('kick', 'kick', 'kick', db=-20), T('snare', 'snare', 'snare', rev=0.15, db=-20), T('ride', 'top', 'ride', pan=0.3, db=-27),
              T('chat', 'top', 'chat', pan=-0.2, db=-30), T('bass', 'bass', 'organ', db=-16, p=dict(drawbar='bass')),
              T('chords', 'chords', 'organ', rev=0.2, pan=-0.2, db=-22), T('arp', 'arp', 'guitar', pan=0.3, db=-26),
              T('lead', 'lead', 'sax', rev=0.25, db=-17)],
      master=dict(lufs=-13.0, air=1.2, low=1.0))

style('fusion', 'Classic', 'Jazz fusion / jazz-rock: straight 16th-note grooves, electric bass, Rhodes and synth leads, overdriven '
      'guitar, extended chords and virtuosic unison lines over a rock / funk rhythm section',
      bpm=(96, 140), scales=['dorian', 'mixolydian', 'lydian', 'minor'], swing=0.5, human=0.005, chord_size=4, form='song',
      progs={'dorian': [[0, 3, 6, 2], [0, 6, 3, 4]], 'mixolydian': [[0, 6, 3, 0], [0, 3, 6, 6]], 'lydian': [[0, 1, 0, 1], [0, 1, 4, 5]],
             'minor': [[0, 5, 3, 4], [0, 3, 6, 4]]},
      drums={'kick': ['X..x..X...X..x..', 'X.x...X..x..X...'], 'snare': ['....X..o....X..o'], 'chat': ['xxxxxxxxxxxxxxxx'],
             'ohat': ['......x.......x.'], 'ride': ['x.x.x.x.x.x.x.x.']},
      snare_tracks=['snare'], ghosts=True, bass=['R.RO.R.OR.R.O.RA', 'R..R.O.RR.R..O.R', 'R.R.O.R.R.R.O.RA'], bass_lo=31,
      chord_rh=['x--.x--.x--.x--.', '.x-..x-..x-..x-.', 'x-..x-..x-..x---'], chord_center=60, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x.x.x.x.x.x.x.x.', 'x.xxx.x.x.xxx.x.', 'x-x-x-x-x.x.x---'], voicing='drop2',
      tracks=[T('kick', 'kick', 'kick', db=-17), T('snare', 'snare', 'snare', rev=0.15, db=-18), T('chat', 'top', 'chat', pan=0.2, db=-29),
              T('ohat', 'top', 'ohat', db=-30), T('ride', 'top', 'ride', pan=0.3, db=-31),
              T('bass', 'bass', 'pluck', db=-14, p=dict(bright=1900, damp=0.996)),
              T('chords', 'chords', 'epiano', rev=0.25, pan=-0.2, db=-22), T('pad', 'pad', 'polysynth', rev=0.4, db=-30),
              T('arp', 'arp', 'guitar', pan=0.3, db=-27, drive=0.4), T('lead', 'lead', 'leadsaw', rev=0.3, dly=0.2, db=-18)],
      master=dict(lufs=-12.0, air=1.6, low=1.0))

# ---- classical periods
style('classical_period', 'Orchestral', 'Classical period (Mozart / Haydn): elegant homophony - a clear singing melody over Alberti-bass '
      'and string accompaniment, 4+4-bar phrases, functional cadences, pairs of winds, horns and timpani',
      bpm=(100, 140), scales=['major', 'minor'], human=0.006, chord_size=3, chord_bars=1, form='orchestral', reverb=2.0,
      progs={'major': [[0, 3, 4, 0], [0, 4, 0, 4], [0, 1, 4, 0], [0, 5, 1, 4], [0, 3, 1, 4]], 'minor': [[0, 3, 4, 0], [0, 5, 3, 4]]},
      drums={'timp': ['X...............', '................']}, kick_track='timp',
      bass=['R...R...R...R...', 'R.......R.......'], bass_lo=36,
      chord_rh=['x...x...x...x...', 'x.......x.......'], chord_center=60, arp=dict(rate=1, mode='alberti', oct=5),
      lead_rh=['x.x.x.x.x-------', 'x---x.x.x.x.x---', 'x-x-x-x-x-x-x---', 'x.x.x-x-x-------'], lead_oct=5, repetition=0.65,
      gm_hint='Violins (melody); piano / strings Alberti bass; cellos & basses; pairs of flutes, oboes, horns; timpani',
      tracks=[T('timp', 'kick', 'timp', rev=0.4, db=-28), T('bass', 'bass', 'cello', rev=0.3, db=-20),
              T('chords', 'chords', 'strings', rev=0.3, db=-26, p=dict(a=0.08)),
              T('pad', 'pad', 'horn', rev=0.4, db=-31), T('arp', 'arp', 'piano', rev=0.25, pan=-0.15, db=-23),
              T('lead', 'lead', 'violin', rev=0.3, db=-18)],
      master=dict(lufs=-16.0, air=1.0, low=0.5))

style('romantic', 'Orchestral', 'Romantic orchestra (Tchaikovsky / Brahms): expansive lyrical themes with rubato, rich chromatic '
      'harmony, full strings with continuous vibrato, horns and woodwinds, swelling ppp-to-fff dynamics',
      bpm=(60, 92), scales=['minor', 'major', 'harmonic_minor'], human=0.012, chord_size=4, chord_bars=1, form='cinematic',
      reverb=3.2, voicing='open', rubato=0.8,
      progs={'minor': [[0, 5, 3, 4], [0, 3, 6, 4], [0, 6, 5, 4]], 'major': [[0, 5, 3, 4], [0, 2, 3, 4], [0, 4, 5, 2]],
             'harmonic_minor': [[0, 3, 4, 5], [0, 5, 1, 4]]},
      drums={'timp': ['X...............', 'X.......X.......']}, kick_track='timp',
      bass=['R-------R-------', 'R---------------'], bass_lo=33,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=58, arp=dict(rate=2, mode='updown', oct=5, prob=0.7),
      lead_rh=['x-----x-x-------', 'x---x-x-x-------', 'x-------x---x---', 'x-x-x---x-------'], lead_oct=5,
      tracks=[T('timp', 'kick', 'timp', rev=0.5, db=-26), T('bass', 'bass', 'contrabass' if False else 'cello', rev=0.4, db=-19),
              T('chords', 'chords', 'strings', rev=0.45, db=-21, p=dict(a=0.3, r=0.7)),
              T('pad', 'pad', 'horn', rev=0.5, db=-27), T('arp', 'arp', 'harp', rev=0.45, db=-27),
              T('lead', 'lead', 'violin', rev=0.45, db=-17, p=dict(vib=8))],
      master=dict(lufs=-15.0, air=1.0, low=0.6))

style('impressionism', 'Orchestral', 'Impressionism (Debussy / Ravel): modal and lydian colours, parallel gliding chords, blurred '
      'harmony, harp and flute over muted strings and piano washes, flexible pulse - atmosphere over function',
      bpm=(56, 80), scales=['lydian', 'dorian', 'mixolydian'], human=0.012, chord_size=4, chord_bars=2, form='orchestral', reverb=3.5,
      voicing='open', rubato=0.5,
      progs={'lydian': [[0, 1, 0, 1], [0, 1, 2, 1], [0, 6, 1, 0]], 'dorian': [[0, 3, 0, 6], [0, 1, 0, 3]], 'mixolydian': [[0, 6, 0, 6]]},
      drums={}, bass=['R---------------'], bass_lo=36,
      chord_rh=['x---------------', 'x-------x-------'], chord_center=62, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x-----x-x-x-----', 'x---x---x-------', '..x-x-x-x-------', 'x-x-x-x---------'], lead_oct=5,
      tracks=[T('bass', 'bass', 'cello', rev=0.5, db=-22), T('chords', 'chords', 'piano', rev=0.5, db=-22),
              T('pad', 'pad', 'strings', rev=0.6, db=-27, p=dict(a=0.6, cut=2600)), T('arp', 'arp', 'harp', rev=0.5, pan=0.2, db=-24),
              T('lead', 'lead', 'flute', rev=0.5, db=-19)],
      master=dict(lufs=-17.0, air=1.0, low=0.4))

style('minimalism', 'Orchestral', 'Minimalism (Reich / Glass / Adams): a steady pulse of repeating cells on marimba, piano and strings, '
      'shifting by gradual additive / phasing processes over slow diatonic harmony',
      bpm=(120, 160), scales=['minor', 'major', 'dorian'], human=0.002, chord_size=3, chord_bars=4, form='groove',
      progs={'minor': [[0, 5, 3, 4], [0, 6, 5, 6]], 'major': [[0, 4, 5, 3], [0, 3, 0, 4]], 'dorian': [[0, 3, 0, 3]]},
      drums={}, bass=['R-------R-------', 'R.......R.......'], bass_lo=36,
      chord_rh=['x.x.x.x.x.x.x.x.', 'xx.xx.xx.xx.xx.x'], chord_center=60, arp=dict(rate=1, mode='updown', oct=5),
      lead_rh=['x.x.x.x.x.x.x.x.', 'x.xx.x.xx.x.xx.x', 'xx.x.xx.x.xx.x.x'], lead_oct=5, repetition=0.95, simplicity=0.2,
      tracks=[T('bass', 'bass', 'cello', rev=0.3, db=-21), T('chords', 'chords', 'piano', rev=0.3, pan=-0.2, db=-23),
              T('pad', 'pad', 'strings', rev=0.4, db=-28), T('arp', 'arp', 'marimba', rev=0.3, pan=0.25, db=-23),
              T('lead', 'lead', 'marimba', rev=0.3, pan=-0.25, db=-21)],
      master=dict(lufs=-15.0, air=1.2, low=0.5))

LABELS.update({'italo_disco': 'Italo Disco', 'new_beat': 'New Beat', 'gabber': 'Hardcore / Gabber', 'rave_hardcore': 'Breakbeat Hardcore / Rave',
               'future_funk': 'Future Funk', 'bebop': 'Bebop', 'modal_jazz': 'Cool / Modal Jazz', 'soul_jazz': 'Soul Jazz / Hard Bop',
               'fusion': 'Jazz Fusion', 'classical_period': 'Classical (Mozart era)', 'romantic': 'Romantic Orchestra',
               'impressionism': 'Impressionism', 'minimalism': 'Minimalism'})
POOLS.update({
    'italo_disco': dict(bass=['sawbass', 'fmbass', 'moogbass'], chords=['polysynth', 'synthbrass', 'epiano'], pad=['solina', 'strings', 'choir'],
                        arp=['pluck_saw', 'chip', 'pluck'], lead=['leadsaw', 'synthbrass', 'vox', 'polysynth']),
    'new_beat': dict(bass=['acid', 'sawbass'], chords=['stab', 'organ'], pad=['choir', 'warmpad'], arp=['pluck_saw'], lead=['vox', 'stab']),
    'gabber': dict(chords=['hoover', 'stab', 'supersaw'], lead=['leadsaw', 'hoover', 'supersaw_lead'], arp=['pluck_saw', 'chip']),
    'rave_hardcore': dict(bass=['sinebass', 'reese'], chords=['piano', 'stab', 'organ'], pad=['choir', 'strings'], arp=['vox', 'pluck_saw'],
                          lead=['hoover', 'leadsaw', 'vox', 'piano']),
    'future_funk': dict(bass=['pluck', 'sf:slapbass', 'moogbass'], chords=['epiano', 'polysynth', 'sf:cleanguitar', 'synthbrass'],
                        pad=['strings', 'solina'], arp=['vox', 'mutedgtr', 'epiano'], lead=['vox', 'synthbrass', 'sax', 'leadsaw']),
    'bebop': dict(chords=['piano', 'guitar'], lead=['sax', 'sf:tenorsax', 'trumpet', 'sf:trumpet']),
    'modal_jazz': dict(chords=['piano', 'epiano'], lead=['trumpet', 'sax', 'sf:tenorsax', 'flute']),
    'soul_jazz': dict(chords=['organ'], arp=['guitar'], lead=['sax', 'sf:tenorsax', 'guitar', 'organ']),
    'fusion': dict(chords=['epiano', 'wurli', 'polysynth'], arp=['guitar', 'sf:odguitar'], lead=['leadsaw', 'guitar', 'sax', 'softlead']),
    'classical_period': dict(chords=['strings', 'spiccato'], arp=['piano', 'harpsichord', 'strings'], lead=['violin', 'flute', 'oboe', 'clarinet'],
                             pad=['horn', 'strings']),
    'romantic': dict(chords=['strings', 'tremolo'], lead=['violin', 'cello', 'horn', 'clarinet', 'oboe'], pad=['horn', 'choir', 'strings'],
                     arp=['harp', 'pizz']),
    'impressionism': dict(chords=['piano', 'harp', 'strings'], lead=['flute', 'oboe', 'clarinet', 'violin'], arp=['harp', 'celesta', 'piano'],
                          pad=['strings', 'choir']),
    'minimalism': dict(chords=['piano', 'organ', 'strings'], arp=['marimba', 'piano', 'vibes'], lead=['marimba', 'piano', 'vibes', 'clarinet', 'violin'],
                       pad=['strings', 'organ']),
})


# ---------------------------------------------------------------------------------------------------------------
# wider pad / bass pools for genres that only had one or two options - only sounds that genuinely fit the genre
_PAD_FAMILY = {
    ('house', 'deep_house', 'tech_house', 'ukgarage', 'afro_house', 'melodic_house', 'progressive_house', 'disco'):
        ['warmpad', 'glasspad', 'solina', 'vox', 'organ'],
    ('techno', 'minimal', 'melodic_techno', 'acid_house'): ['glasspad', 'warmpad', 'vox', 'choir'],
    ('trance', 'psytrance', 'uplifting_trance', 'bigroom', 'hardstyle', 'eurodance'): ['supersaw', 'glasspad', 'choir', 'warmpad'],
    ('boombap', 'lofi', 'trap', 'phonk', 'uk_drill', 'memphis_phonk', 'house_phonk', 'luxury_rap', 'orchestral_hiphop'):
        ['strings', 'choir', 'solina', 'glasspad', 'vox'],
    ('jazz', 'bossa_nova', 'soul_ballad', 'rnb', 'motown', 'city_pop', 'gospel'): ['strings', 'organ', 'solina', 'warmpad'],
    ('reggae', 'afrobeats', 'reggaeton', 'dancehall', 'amapiano', 'moombahton', 'ska', 'cumbia', 'salsa'):
        ['organ', 'warmpad', 'strings', 'vox'],
    ('electro', 'synthwave', 'synthpop', 'chiptune', 'vaporwave', 'hauntology', 'braindance'): ['solina', 'glasspad', 'warmpad', 'supersaw'],
    ('ambient', 'downtempo', 'future_bass', 'hyperpop', 'melodic_dubstep', 'liquid_dnb'): ['glasspad', 'warmpad', 'choir', 'vox', 'supersaw'],
}
_BASS_FAMILY = {
    ('trance', 'progressive_house', 'uplifting_trance', 'hardstyle', 'bigroom', 'eurodance'): ['sawbass', 'fmbass', 'moogbass', 'reese'],
    ('psytrance',): ['sawbass', 'fmbass', 'acid', 'moogbass'],
    ('acid_house',): ['acid', 'sawbass', 'moogbass'],
    ('future_bass', 'melodic_dubstep'): ['sawbass', '808', 'reese', 'fmbass'],
    ('jungle', 'dnb', 'liquid_dnb'): ['reese', 'sinebass', 'sawbass', 'moogbass'],
    ('boombap', 'lofi'): ['sinebass', 'sf:acbass', 'upright', 'pluck', 'moogbass'],
    ('reggae', 'dancehall', 'ska'): ['sinebass', 'sf:fingerbass', 'pluck', 'moogbass'],
    ('ambient', 'downtempo'): ['sinebass', 'moogbass', 'fmbass'],
    ('synthwave', 'synthpop', 'electro'): ['sawbass', 'moogbass', 'fmbass'],
    ('house', 'deep_house', 'tech_house', 'ukgarage', 'afro_house'): ['sawbass', 'fmbass', 'moogbass', 'sinebass'],
    ('techno', 'minimal', 'melodic_techno'): ['sawbass', 'acid', 'moogbass', 'sinebass'],
}


def _widen(families, role):
    from .instruments import INSTRUMENTS
    for names, extra in families.items():
        for n in names:
            if n not in STYLES:
                continue
            own = [t['inst'] for t in STYLES[n]['tracks'] if t['layer'] == role][:1]
            cur = list((POOLS.get(n) or {}).get(role) or [])
            if len(cur) > 2 or not own:                   # only parts the genre really has, its own sound first
                continue
            base = cur if cur and cur[0] == own[0] else own + [x for x in cur if x != own[0]]
            merged = list(dict.fromkeys(base + [x for x in extra if x in INSTRUMENTS or x.startswith('sf:')]))
            POOLS.setdefault(n, {})[role] = merged


_widen(_PAD_FAMILY, 'pad')
_widen(_BASS_FAMILY, 'bass')




# ---------------------------------------------------------------------------------------------------------------
# Bells are seasoning, not a default. Bell / celesta / glockenspiel / music-box sounds stay only where they're idiomatic
# (trap bell melodies, film & orchestral, holiday, fantasy, horror music boxes); mallets (marimba, kalimba, vibes,
# steel drum) stay in afro, latin, caribbean, jazz, bossa, lo-fi and organic styles. Everywhere else a bell is
# replaced by the genre's own sound for that part.
BELLS = {'bell', 'celesta', 'sf:glock', 'sf:musicbox', 'sf:tubular', 'glock', 'musicbox', 'tubular', 'sf:celesta'}
MALLETS = {'marimba', 'kalimba', 'vibes', 'steeldrum', 'sf:marimba', 'sf:vibes', 'sf:kalimba', 'sf:steeldrum', 'sf:xylophone'}
BELL_OK = {'impressionism', 'trap', 'holiday', 'fantasy_rpg', 'ambient', 'cinematic', 'orchestral', 'film_piano', 'waltz', 'neoclassical',
           'adventure', 'tension', 'hauntology', 'chamber_pop', 'braindance', 'orchestral_hiphop', 'hybrid_trailer', 'lofi'}
MALLET_OK = BELL_OK | {'minimalism', 'afrobeats', 'amapiano', 'afro_house', 'cumbia', 'salsa', 'dancehall', 'bossa_nova', 'jazz', 'swing',
                       'lofi', 'organic_house', 'liquid_dnb', 'city_pop', 'downtempo'}
# what a genre plays instead (by part); anything not listed falls back to its category
NO_BELL = {
    'trance': dict(arp='pluck_saw', lead='supersaw_lead'), 'uplifting_trance': dict(arp='pluck_saw', lead='supersaw_lead'),
    'psytrance': dict(arp='pluck_saw', lead='acid'), 'progressive_trance': dict(arp='pluck_saw', lead='supersaw_lead'),
    'techno': dict(arp='pluck_saw', lead='stab', chords='stab'), 'minimal': dict(arp='pluck', lead='stab', chords='stab'),
    'melodic_techno': dict(arp='pluck_saw', lead='pluck_saw'), 'house': dict(arp='pluck', lead='stab'),
    'tech_house': dict(arp='pluck', lead='stab'), 'progressive_house': dict(arp='pluck_saw', lead='supersaw_lead'),
    'acid_house': dict(arp='acid', lead='acid'), 'melodic_house': dict(arp='pluck_saw', lead='pluck_saw'),
    'dnb': dict(arp='stab', lead='leadsaw'), 'neurofunk': dict(arp='stab', lead='reese', chords='stab'),
    'jungle': dict(arp='stab', lead='vox'), 'breakcore': dict(arp='stab', lead='chip'),
    'dubstep': dict(arp='pluck_saw', lead='leadsaw'), 'brostep': dict(arp='pluck_saw', lead='leadsaw'),
    'melodic_dubstep': dict(arp='pluck_saw', lead='supersaw_lead'), 'tempa_dubstep': dict(arp='organ', lead='flute'),
    'future_bass': dict(arp='pluck_saw', lead='supersaw_lead'), 'ukgarage': dict(arp='organ', lead='vox'),
    'synthwave': dict(arp='pluck_saw', lead='leadsaw'), 'synthpop': dict(arp='pluck_saw', lead='polysynth'),
    'electro': dict(arp='pluck_saw', lead='leadsaw'), 'bigroom': dict(arp='pluck_saw', lead='supersaw_lead'),
    'hardstyle': dict(arp='pluck_saw', lead='supersaw_lead'), 'eurodance': dict(arp='pluck_saw', lead='supersaw_lead'),
    'hyperpop': dict(arp='chip', lead='supersaw_lead'), 'kpop': dict(arp='pluck', lead='supersaw_lead'),
    'pop': dict(arp='pluck', lead='piano'), 'teen_pop': dict(arp='pluck', lead='piano'), 'uk_drill': dict(arp='piano', lead='piano'),
    'boombap': dict(arp='epiano', lead='piano', chords='epiano'), 'luxury_rap': dict(arp='piano', lead='piano'),
    'jersey_club': dict(arp='vox', lead='vox'), 'vaporwave': dict(arp='epiano', lead='sax'), 'motown': dict(arp='piano', lead='sax'),
    'indie_rock': dict(arp='guitar', lead='guitar'), 'soft_rock': dict(arp='guitar', lead='piano'), 'disco_funk': dict(arp='clav'),
}
NO_BELL_CAT = {'Electronic': dict(arp='pluck_saw', lead='leadsaw', chords='stab', pad='glasspad'),
               'Classic': dict(arp='pluck', lead='piano', chords='epiano', pad='strings'),
               'Orchestral': dict(arp='harp', lead='flute', chords='strings', pad='strings')}


def bell_allowed(style, inst):
    if inst in BELLS:
        return style in BELL_OK
    if inst in MALLETS:
        return style in MALLET_OK
    return True


def bell_swap(style, role, inst=None):
    st = STYLES.get(style, {})
    rep = NO_BELL.get(style, {}).get(role) or NO_BELL_CAT.get(st.get('category'), NO_BELL_CAT['Electronic']).get(role)
    return rep if rep and rep != inst else 'pluck'


for _name, _st in STYLES.items():
    for _t in _st['tracks']:
        if _t['layer'] in ('arp', 'lead', 'chords', 'pad') and not bell_allowed(_name, _t['inst']):
            _t['inst'] = bell_swap(_name, _t['layer'], _t['inst'])
    for _role, _pool in list(POOLS.get(_name, {}).items()):
        if _role in ('arp', 'lead', 'chords', 'pad'):
            _keep = [x for x in _pool if bell_allowed(_name, x)]
            _own = next((t['inst'] for t in _st['tracks'] if t['layer'] == _role), None)
            if _own and _keep and _keep[0] != _own:          # the genre's own sound still leads its pool
                _keep = [_own] + [x for x in _keep if x != _own]
            POOLS[_name][_role] = _keep or [bell_swap(_name, _role)]


# trance: big halls on lead / pad, dotted-8th delay on lead and arp, and the classic 16th trance gate on the pad in drops
_TRANCE_GATE = {'trance': 'x.xx.x.xx.xx.x.x', 'uplifting_trance': 'x.x.xx.xx.x.xx.x', 'progressive_trance': 'xx.x.xx.xx.x.xx.',
                'psytrance': None}
for _n, _g in _TRANCE_GATE.items():
    for _t in STYLES[_n]['tracks']:
        if _t['layer'] == 'lead':
            _t['rev'] = max(_t.get('rev') or 0, 0.55)
            _t['dly'] = max(_t.get('dly') or 0, 0.35)
        elif _t['layer'] == 'arp':
            _t['rev'] = max(_t.get('rev') or 0, 0.35)
            _t['dly'] = max(_t.get('dly') or 0, 0.4)
        elif _t['layer'] == 'pad':
            _t['rev'] = max(_t.get('rev') or 0, 0.6)
            if _g:
                _t['gate'] = _g
    STYLES[_n]['delay_beats'] = 0.75
    STYLES[_n]['reverb'] = max(STYLES[_n].get('reverb') or 0, 3.0)


# audit fixes: disco & funk play an electric bass (not a synth saw), ambient never gets a gritty FM bass
for _n in ('disco', 'funk'):
    for _t in STYLES[_n]['tracks']:
        if _t['layer'] == 'bass':
            _t['inst'] = 'pluck'
            _t['p'] = dict(bright=1700, damp=0.996)
POOLS['disco']['bass'] = ['pluck', 'sf:fingerbass', 'sf:slapbass', 'moogbass']
POOLS['funk']['bass'] = ['pluck', 'sf:slapbass', 'sf:fingerbass', 'moogbass']
POOLS['ambient']['bass'] = ['sinebass', 'moogbass']


# ---------------------------------------------------------------------------------------------------------------
# corrections from the production bibles
STYLES['house']['bpm'] = (120, 127)                       # 118-128, sweet spot 122-125
STYLES['house']['sc_depth'] = 0.55                         # moderate sidechain: groove, not pumping
STYLES['house']['drums']['conga'] = ['..o..x.....o.x..', '......x..x....o.']   # organic percussion fills the mids
STYLES['house']['tracks'].append(T('conga', 'top', 'conga', pan=-0.3, db=-29))
STYLES['deep_house']['form'] = 'groove'                     # linear and hypnotic, fewer drops
STYLES['deep_house']['sc_depth'] = 0.35                     # gentle sidechain
STYLES['progressive_house']['form'] = 'trance'              # long evolving builds, breakdowns that strip to almost nothing
STYLES['progressive_house']['bpm'] = (122, 130)
STYLES['bigroom']['bpm'] = (126, 130)
STYLES['uplifting_trance']['bpm'] = (134, 140)              # uplifting usually 136-138
STYLES['psytrance']['bpm'] = (140, 148)                     # full-on 142-148
STYLES['psytrance']['form'] = 'groove'                      # continuous energy, not build -> drop
STYLES['jungle']['swing'] = 0.56                            # older styles: heavy shuffle
STYLES['synthwave']['bpm'] = (90, 112)
STYLES['reggae']['chord_rh'] = ['..x...x...x...x.', '..x-..x-..x-..x-']   # the skank on every "and"
for _j in ('jazz', 'swing'):
    STYLES[_j]['comp_snare'] = True                         # snare comping / dropping bombs
STYLES['salsa']['real_cowbell'] = True
STYLES['cumbia']['real_cowbell'] = True

# phonk cowbells: the classic pitched 808 cowbell most of the time, sometimes a long-ringing, distorted, raw or crushed one
POOLS['phonk']['lead'] = ['cowbell', 'cowbell', 'cowbell_long', 'cowbell_dist', 'cowbell_808', 'cowbell_crushed']
POOLS['memphis_phonk']['lead'] = ['cowbell', 'cowbell', 'cowbell_808', 'cowbell_long', 'cowbell_crushed']
