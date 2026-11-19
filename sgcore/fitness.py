"""Genre authenticity score: does a generated song actually behave like its genre?

Each check measures the finished song (not the settings that made it): tempo, where kicks and snares land in the big
sections, swing, the low end, signature sounds. Profiles follow common production practice (tempo ranges and rhythmic
skeletons from the genre reference guides); genres without their own profile are checked against their family's rules.
"""
COWBELLS = {'phonkbell', 'cowbell', 'cowbell_808', 'cowbell_long', 'cowbell_dist', 'cowbell_crushed'}
from collections import Counter

# tempo ranges (BPM) per genre, from production practice
TEMPO = {
    'phonk': (140, 170), 'house_phonk': (125, 145), 'memphis_phonk': (60, 95), 'brazilian_phonk': (128, 160), 'dubstep': (138, 142), 'brostep': (140, 150),
    'melodic_dubstep': (140, 150), 'dnb': (160, 180), 'liquid_dnb': (165, 180), 'neurofunk': (170, 180), 'jungle': (155, 175),
    'trance': (125, 150), 'uplifting_trance': (130, 142), 'psytrance': (135, 150), 'house': (118, 130), 'deep_house': (115, 126),
    'tech_house': (120, 130), 'progressive_house': (120, 132), 'melodic_house': (114, 124), 'afro_house': (115, 126),
    'techno': (120, 150), 'melodic_techno': (118, 130), 'minimal': (118, 130), 'acid_house': (118, 132), 'trap': (130, 170),
    'uk_drill': (130, 150), 'future_bass': (130, 160), 'hardstyle': (148, 162), 'synthwave': (80, 120), 'ambient': (40, 110),
    'pop': (90, 140), 'rock': (90, 160), 'metal': (80, 210), 'punk': (140, 210), 'lofi': (60, 95), 'boombap': (78, 102),
    'rnb': (60, 110), 'funk': (88, 122), 'disco': (108, 132), 'reggae': (60, 95), 'reggaeton': (85, 102), 'jazz': (90, 220),
    'swing': (105, 165), 'bossa_nova': (110, 145), 'amapiano': (105, 118), 'afrobeats': (95, 120), 'garage': (128, 138),
    'ukgarage': (128, 138), 'bigroom': (124, 132), 'eurodance': (130, 145), 'hyperpop': (140, 180), 'kpop': (100, 140),
    'teen_pop': (88, 116), 'soft_rock': (95, 130), 'jam_band': (95, 135), 'luxury_rap': (130, 155), 'dancehall': (85, 108),
    'country': (85, 140), 'bluegrass': (105, 160), 'gospel': (65, 125), 'motown': (95, 130), 'salsa': (80, 106),   # salsa written in cut time: one bar = two of 2/2
    'tango': (100, 130), 'cumbia': (80, 108), 'jersey_club': (130, 150), 'baile_funk': (125, 136), 'hauntology': (70, 100),
    'braindance': (100, 180),
}
FOUR_FLOOR = {'house', 'deep_house', 'tech_house', 'progressive_house', 'trance', 'uplifting_trance', 'psytrance', 'techno',
              'minimal', 'acid_house', 'melodic_techno', 'afro_house', 'melodic_house', 'bigroom', 'hardstyle', 'disco',
              'eurodance', 'house_phonk'}
HALF_TIME = {'dubstep', 'brostep', 'melodic_dubstep', 'trap', 'phonk', 'future_bass', 'hyperpop', 'luxury_rap'}
DRILL = {'uk_drill', 'orchestral_hiphop'}          # syncopated snares: beat 2 plus a late, pushed hit
TWO_STEP = {'dnb', 'liquid_dnb', 'neurofunk', 'jungle'}
BACKBEAT = {'pop', 'rock', 'funk', 'motown', 'indie_rock', 'gospel', 'country', 'ska', 'kpop', 'teen_pop', 'soft_rock',
            'rnb', 'boombap', 'lofi', 'synthwave', 'synthpop', 'metal', 'jam_band', 'chamber_pop', 'city_pop', 'memphis_phonk',
            'hauntology', 'eurodance', 'disco'}
SWUNG = {'jazz', 'swing', 'boombap', 'lofi', 'rnb', 'hauntology', 'gospel', 'neo_soul', 'g_funk', 'new_jack_swing', 'hauntology_sunlit', 'quiet_storm'}
SUB_BASS = {'dubstep', 'brostep', 'melodic_dubstep', 'dnb', 'liquid_dnb', 'neurofunk', 'jungle'}
SLIDING_808 = {'trap', 'phonk', 'brazilian_phonk', 'uk_drill', 'memphis_phonk', 'luxury_rap', 'orchestral_hiphop'}
SIGNATURE = {   # genre -> (part, instruments, label): the sound that defines it
    'phonk': ('lead', COWBELLS, 'cowbell melody'), 'house_phonk': ('lead', COWBELLS, 'cowbell melody'), 'brazilian_phonk': ('lead', COWBELLS, 'cowbell melody'),
    'memphis_phonk': ('lead', COWBELLS | {'bell', 'piano'}, 'eerie bell / cowbell loop'),
    'acid_house': ('bass', {'acid'}, '303 acid bass'), 'dubstep': ('bass', {'wobble', 'growl', 'reese', 'fmbass', 'riddim', 'neuro', 'darkwob', 'subwob', 'fmgrowl', 'talkgrowl', 'metalbass', 'vowelwob', 'multiwob', 'tablewob', 'chopwob', 'dnbwob'}, 'modulated mid-bass'),
    'brostep': ('bass', {'growl', 'wobble', 'fmbass', 'reese', 'fmgrowl', 'talkgrowl', 'metalbass', 'darkwob', 'vowelwob', 'multiwob', 'tablewob', 'chopwob', 'dnbwob'}, 'aggressive mid-bass'),
    'neurofunk': ('bass', {'growl', 'reese', 'fmbass', 'wobble', 'neuro', 'dnbwob', 'metalbass', 'fmgrowl', 'talkgrowl'}, 'neuro / reese bass'),
    'amapiano': ('bass', {'logdrum'}, 'log drum'), 'trap': ('bass', {'808'}, '808'), 'uk_drill': ('bass', {'808'}, '808'),
    'festival_psy': ('bass', {'psybass', 'rollbass', 'sawbass', 'psyroll'}, 'rolling psy bass'),
    'progressive_psy': ('bass', {'psyroll', 'psybass', 'rollbass'}, 'rolling psy bass'),
    'goa_trance': ('bass', {'psyroll', 'psybass', 'sawbass', 'rollbass'}, 'rolling psy bass'),
    'darkpsy': ('bass', {'psyroll', 'psybass', 'fmbass'}, 'rolling psy bass'),
    'uplifting_trance': ('lead', {'supersaw_lead', 'leadsaw', 'pluck_saw', 'piano', 'vox', 'emolead', 'hypersaw'}, 'trance lead'),
}


def _base(inst):
    return inst[3:] if isinstance(inst, str) and inst.startswith('sf:') else inst


def analyse(song):
    """Measure the big sections of a song: kick/snare placement, swing, low end."""
    st = song['st']
    tracks = {t['name']: t for t in st['tracks']}
    from .instruments import DRUMS
    big = [s for s in song['sections'] if s['opts'].get('drop') or s['name'] in ('chorus', 'drop', 'climax', 'hook', 'theme', 'head')]
    big = big or song['sections']
    spans = [(s['bar'] * 4, (s['bar'] + s['bars']) * 4) for s in big]
    nbars = max(1, sum(s['bars'] for s in big))
    inside = lambda b: any(a <= b < z for a, z in spans)
    kick = st.get('kick_track', 'kick')
    kicks = [e for e in song['events'] if e.track == kick and inside(e.beat)]
    snares = [e for e in song['events'] if tracks.get(e.track, {}).get('layer') == 'snare' and tracks[e.track]['inst'] in DRUMS
              and inside(e.beat) and e.vel >= 0.6]
    accents = [e for e in snares if e.vel >= 0.9] or snares      # the accented hits define the backbone (not ghost/train notes)
    g = 3 if st.get('meter') else 4
    pos = Counter(round((e.beat % 4) * g) for e in accents)
    on_beat = sum(1 for e in kicks if abs(e.beat - round(e.beat)) < 0.02)
    bass = [t for t in st['tracks'] if t['layer'] == 'bass']
    return dict(
        bpm=song['bpm'], swing=st.get('swing', 0.5),
        kick_per_bar=len(kicks) / nbars, kick_on_beat=on_beat / max(1, len(kicks)),
        kick_every_beat=len({round(e.beat) for e in kicks if abs(e.beat - round(e.beat)) < 0.02}) / (nbars * 4),
        snare_pos=pos, snares=len(snares),
        sub=any(_base(t['inst']) == 'sinebass' or (_base(t['inst']) == 'wobble' and (t['p'] or {}).get('sub', 0.8) > 0) for t in bass),
        glides=sum(1 for e in song['events'] if tracks.get(e.track, {}).get('layer') == 'bass' and e.glide is not None),
        insts={t['layer']: _base(t.get('rig_from') or t['inst']) for t in st['tracks'] if not t.get('double_of') and not t.get('counter')},
        all_insts={(t['layer'], _base(t.get('rig_from') or t['inst'])) for t in st['tracks']},
    )


def genre_fit(song):
    """-> {'score': 0-100, 'checks': [{'name', 'ok'}]} for the song's lead genre."""
    name = (song.get('style') or '').split('+')[0]
    if song['opts'].blend or song['opts'].blend_parts:
        return None                                  # fusions are meant to bend the rules
    a = analyse(song)
    checks = []
    add = lambda label, ok: checks.append(dict(name=label, ok=bool(ok)))
    from .styles import STYLES
    lo, hi = TEMPO.get(name) or STYLES.get(name, {}).get('bpm', (40, 240))
    if not song['opts'].bpm:                         # a tempo you typed yourself isn't held against the genre
        add(f'tempo {lo}-{hi} BPM', lo <= a['bpm'] <= hi)
    sp = a['snare_pos']
    tot = max(1, sum(sp.values()))
    if name in FOUR_FLOOR:
        add('four-on-the-floor kick', a['kick_every_beat'] >= 0.9)
    if name in HALF_TIME:
        add('half-time: snare on beat 3', sp.get(8, 0) / tot >= 0.5 and sp.get(4, 0) / tot < 0.3)
    if name in TWO_STEP:
        add('two-step: snare on 2 and 4', (sp.get(4, 0) + sp.get(12, 0)) / tot >= (0.35 if name == 'jungle' else 0.6))
        add('breakbeat kick (not four-on-the-floor)', a['kick_every_beat'] < 0.7)
    if name in BACKBEAT and not song.get('meter', '4/4') != '4/4':
        add('backbeat on 2 and 4', (sp.get(4, 0) + sp.get(12, 0)) / tot >= 0.5)
    if name in DRILL:
        drill = sp.get(4, 0) > 0 and any(sp.get(k, 0) for k in (10, 11, 13, 14, 15))
        half = sp.get(8, 0) / tot >= 0.5
        add('drill snares (beat 2 + a pushed late hit)' + (' or half-time' if name == 'orchestral_hiphop' else ''),
            drill or (name == 'orchestral_hiphop' and half))
    if name == 'punk':
        add('driving punk beat (backbeat or skate beat)', (sp.get(4, 0) + sp.get(12, 0) + sp.get(2, 0) + sp.get(6, 0) + sp.get(10, 0)
                                                           + sp.get(14, 0)) / tot >= 0.6)
    if name in SWUNG:
        add('swing feel', a['swing'] >= 0.54)
    if name in SUB_BASS:
        add('clean sub under the bass', a['sub'])
    if name in SLIDING_808:
        add('808 bass with slides', a['insts'].get('bass') == '808' and a['glides'] > 0)
    if name in SIGNATURE:
        part, ok, label = SIGNATURE[name]
        add(label, any(p == part and i in ok for p, i in a['all_insts']))
    if not checks:
        return None
    return dict(score=round(100 * sum(c['ok'] for c in checks) / len(checks)), checks=checks)
