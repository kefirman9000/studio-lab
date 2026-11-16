"""Genre effect plugins: when a free effect plugin is installed, genres use it in place of Studio Lab's own processing.

  Dragonfly Reverb (GPL-3, auto-install pack)    hall / plate / room reverb for the reverb send, chosen by genre
  CHOW Tape Model / BYOD (install them yourself)  used if present: tape on lo-fi styles' master, distortion on rock guitars

Every plugin call has a fallback: if a plugin fails, the built-in effect is used and the song still renders.
"""
from . import vsthost

# which reverb a genre's send goes through
HALL = {'Orchestral'}
PLATE_STYLES = {'pop', 'teen_pop', 'kpop', 'soul_ballad', 'gospel', 'rnb', 'motown', 'synthpop', 'italo_disco', 'city_pop', 'disco',
                'disco_funk', 'synthwave', 'chamber_pop', 'soft_rock', 'reggae', 'dancehall', 'country', 'western', 'eurodance'}
ROOM_STYLES = {'rock', 'punk', 'metal', 'indie_rock', 'jam_band', 'funk', 'blues', 'jazz', 'swing', 'bebop', 'modal_jazz', 'soul_jazz',
               'fusion', 'boombap', 'lofi', 'folk', 'bluegrass', 'celtic_jig', 'ska', 'salsa', 'cumbia', 'bossa_nova', 'tango',
               'memphis_phonk', 'chamber'}
HALL_STYLES = {'trance', 'uplifting_trance', 'progressive_trance', 'ambient', 'downtempo', 'melodic_dubstep', 'progressive_house',
               'melodic_techno', 'liquid_dnb', 'organic_house', 'deep_dubstep', 'dubstep', 'hauntology', 'vaporwave', 'hauntology_sunlit', 'hauntology_dark', 'alt_rnb'}
PLUGIN = {'hall': 'DragonflyHallReverb', 'plate': 'DragonflyPlateReverb', 'room': 'DragonflyRoomReverb'}


def reverb_kind(style, category):
    if style in ROOM_STYLES:
        return 'room'
    if style in PLATE_STYLES:
        return 'plate'
    if style in HALL_STYLES or category in HALL:
        return 'hall'
    return 'hall' if category == 'Electronic' else 'plate'


def reverb_params(kind, size):
    """A fully-wet setting (Studio Lab mixes the return) sized from the genre's reverb amount (seconds-ish)."""
    size = float(size or 2.0)
    if kind == 'hall':
        return dict(dry_level=0.0, early_level=25.0, late_level=100.0, size_m=min(60.0, 18 + 8 * size),
                    decay_s=min(10.0, max(0.8, size)), predelay_ms=18.0, diffuse=90.0, high_cut_hz=9000.0, low_cut_hz=60.0)
    if kind == 'plate':
        return dict(dry_level=0.0, wet_level=100.0, decay_s=min(4.0, max(0.6, size * 0.8)), predelay_ms=12.0,
                    low_cut_hz=120.0, high_cut_hz=12000.0)
    return dict(dry_level=0.0, early_level=45.0, late_level=90.0, size_m=min(32.0, 10 + 3 * size),
                decay_s=min(2.0, max(0.3, size * 0.45)), predelay_ms=6.0, high_cut_hz=11000.0, low_cut_hz=60.0)


def plan(st, style, enabled):
    """Pick the reverb plugin for this song (stored in st['fx_reverb']) when it's installed and plugins are on."""
    if not enabled:
        return
    try:
        if not vsthost.available():
            return
        kind = reverb_kind(style, st.get('category'))
        name = PLUGIN[kind]
        if vsthost.path_of(name):
            st['fx_reverb'] = dict(plugin=name, kind=kind, params=reverb_params(kind, st.get('reverb')))
    except Exception:
        pass


def run_reverb(st, send, log=print):
    """The reverb return through the genre's plugin, or None (caller uses the built-in reverb)."""
    cfg = st.get('fx_reverb')
    if not cfg:
        return None
    try:
        y = vsthost.process([cfg['plugin']], send.astype('float32'), params=[cfg['params']])
        log(f"   reverb: {cfg['plugin'].replace('Dragonfly', 'Dragonfly ').replace('Reverb', ' Reverb')} ({cfg['kind']})")
        return y
    except Exception as e:
        log(f'   reverb plugin failed ({e}) - using the built-in reverb')
        return None
