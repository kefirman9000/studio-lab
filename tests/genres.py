"""Genre authenticity + customization checks (no plugins or internet needed).
   python -m tests.genres"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sgcore.compose import Options, compose, GENRE_MELODY, GENRE_VOICING
from sgcore.theory import voice_chord, Key
from sgcore import samplelibs as _sl  # noqa: E402
_sl.REAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_no_real_libs')   # same sounds as CI
from sgcore.styles import STYLES


def lead(song):
    return [e for e in song['events'] if e.track == 'lead' and e.midi is not None]


def main():
    k = Key(0, 'major')
    assert voice_chord(k, 0, 4, 60, 'rootless', '7') == [55, 59, 64]           # Cmaj7 rootless: G B E (no C)
    assert 60 not in [n % 12 + 60 for n in voice_chord(k, 0, 4, 60, 'rootless', '9')]
    d2 = voice_chord(k, 1, 4, 60, 'drop2', '7')
    assert max(d2) - min(d2) > 12, d2                                           # drop-2 spreads past an octave
    for s in GENRE_MELODY:
        assert s in STYLES, s
    for s in GENRE_VOICING:
        assert s in STYLES, s
    jazz = compose(Options(style='jazz', seed=4))
    assert jazz['st']['voicing'] == 'rootless' and jazz['st']['melody_lang'] == 'bebop'
    pcs = lambda song: {(song['key'].root + x) % 12 for x in song['key'].scale}
    ev = lead(jazz)
    assert sum(1 for e in ev if e.midi % 12 not in pcs(jazz)) > 3                # chromatic approach notes
    folk = compose(Options(style='folk', seed=4, variety=0))
    assert folk['st']['melody_lang'] == 'pentatonic'
    blues = compose(Options(style='blues', seed=4, lead_style='hook'))
    assert sum(1 for e in lead(blues) if e.dur < 0.15) > 0                      # blues slides
    house = compose(Options(style='house', seed=4, melody_style='bebop', voicing='rootless', chord_color='9'))
    assert house['st']['voicing'] == 'rootless' and house['st']['melody_lang'] == 'bebop'
    rock = compose(Options(style='rock', seed=2))
    assert rock['st']['voicing'] == 'power'                                     # power chords survive genre voicings
    from sgcore.windows import preview_window
    from sgcore.render import Renderer
    import numpy as np
    from scipy.io import wavfile

    def lead_rms(levels):
        d = tempfile.mkdtemp()
        song = preview_window(compose(Options(style='house', seed=9, part_levels=levels)))
        Renderer(song, log=lambda *x: None).render(d)
        f = next(os.path.join(d, x) for x in os.listdir(d) if 'lead' in x.lower())
        x = wavfile.read(f)[1].astype(np.float64)
        return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
    drop = lead_rms({}) - lead_rms({'lead': -6})
    assert 5 < drop < 7, drop                                                   # -6 dB on the lead stem
    print('ok  voicings, melody languages, overrides, part levels')

    # ---- arrangement: transitions + endings
    rock = compose(Options(style='rock', seed=21))
    assert any(f[0] == 'swell' for f in rock['fx']) and not any(f[0] == 'fade' and f[1] >= rock['sections'][-1]['bar'] * 4 for f in rock['fx'])
    assert rock['sections'][-1].get('ending') == 'hit'
    end = max(e.beat for e in rock['events'])
    assert end >= rock['sections'][-1]['bar'] * 4 + rock['sections'][-1]['bars'] * 4 - 0.01   # final hit after the outro
    assert compose(Options(style='house', seed=21))['sections'][-1].get('ending') is None   # club tracks keep the fade
    assert compose(Options(style='rock', seed=21, ending='fade'))['sections'][-1].get('ending') is None
    print('ok  fills, swells, endings')

    # ---- genre build-ups and lead devices
    from sgcore.leads import GENRE_DEVICES
    want = {'trance': 'roll', 'techno': 'filter', 'hardstyle': 'kick_roll', 'dubstep': 'stutter', 'amapiano': 'pause', 'pop': 'lift'}
    from sgcore.arrange import BUILD_FAMILY
    for name, bs in want.items():
        for k in (5, 6, 7):
            seq = compose(Options(style=name, seed=k))['st']['build_seq']
            assert set(seq) <= set(BUILD_FAMILY[bs]), (name, seq)               # varies, but within the genre's idiom
    techno = compose(Options(style='techno', seed=5))
    assert techno['st']['form'] == 'groove' and not any(f[0] == 'riser' and f[2] > 8 for f in techno['fx'])   # no long EDM riser
    pop = compose(Options(style='pop', seed=5, structure='auto'))
    assert not any(f[0] == 'riser' for f in pop['fx'])                                # pop pre-choruses don't get EDM risers
    for name in GENRE_DEVICES:
        assert name in STYLES, name
    for dev in ('arp', 'riff', 'ostinato', 'bell', 'call', 'chops', 'hook'):
        song = compose(Options(style='house', seed=7, lead_style=dev))
        assert song['st']['lead_device'] == dev and len(lead(song)) > 20, dev
    a = {round(e.beat, 2) for e in lead(compose(Options(style='house', seed=7, lead_style='chops')))}
    b = {round(e.beat, 2) for e in lead(compose(Options(style='house', seed=7, lead_style='arp')))}
    assert len(a & b) / len(a | b) < 0.6                                             # devices really differ
    print('ok  genre build-ups and lead devices')

    # ---- groove + bass
    bb = compose(Options(style='boombap', seed=3))
    r = Renderer(bb, log=lambda *a: None)
    assert r.t_of(1.0, False, 'snare') > r.t_of(1.0, False) + 0.02                    # Dilla-late backbeat
    st = compose(Options(style='boombap', seed=3, groove='straight'))
    assert Renderer(st, log=lambda *a: None).t_of(1.0, False, 'snare') == Renderer(st, log=lambda *a: None).t_of(1.0, False)
    hk = compose(Options(style='house', seed=3, bass_rhythm='kick', variety=0))
    kicks = {round(e.beat, 3) for e in hk['events'] if e.track == 'kick'}
    assert all(round(e.beat, 3) in kicks for e in hk['events'] if e.track == 'bass')
    print('ok  groove feel, kick-locked bass')

    # ---- vocal guide
    pop = compose(Options(style='pop', seed=8))
    v = pop['vocal']
    assert len(v) > 50 and 57 <= min(e.midi for e in v) and max(e.midi for e in v) <= 84
    assert not any(e.track == 'vocal' for e in pop['events'])                       # silent unless asked
    assert any(e.track == 'vocal' for e in compose(Options(style='pop', seed=8, vocal_guide=True))['events'])
    print('ok  vocal guide')

    # ---- part locks
    def bars(song, names):
        out = {}
        for e in song['events']:
            if e.track in names:
                out.setdefault(int(e.beat // 4), set()).add((e.track, round(e.beat % 4, 3)))
        return {frozenset(x) for x in out.values()}
    D = ('kick', 'clap', 'ohat', 'chat', 'shaker', 'snare')
    a = bars(compose(Options(style='trap', seed=100)), D)
    b = bars(compose(Options(style='trap', seed=555, part_seeds={'drums': 100 * 1009 + 3})), D)
    assert len(a & b) / len(a | b) > 0.8
    print('ok  part locks')

    # ---- references from note files
    from sgcore.exporters import write_midi
    from sgcore.refparse import analyze_file
    from sgcore.theory import NOTE_NAMES
    d = tempfile.mkdtemp()
    song = next(x for x in (compose(Options(style='pop', seed=sd, variety=0)) for sd in range(31, 60))
                if not x['modulate'])                                   # a song that stays in one key
    path = write_midi(os.path.join(d, 'x.mid'), song)
    ref = analyze_file(path, open(path, 'rb').read())
    assert ref['bpm'] == song['bpm'] and ref['key'].rstrip('m') == NOTE_NAMES[song['key'].root], (ref, song['key'].name())
    progs = {'-'.join(str(x + 1) for x in song[k]) for k in ('prog_main', 'prog_verse', 'prog_alt')}
    def cyc(p):                                                          # a loop, wherever it starts
        xs = p.split('-')
        xs = [x for i, x in enumerate(xs) if x != xs[i - 1]] or xs
        return {tuple(xs[i:] + xs[:i]) for i in range(len(xs))}
    assert any(cyc(ref['progression']) & cyc(p) for p in progs), (ref, progs)
    assert analyze_file('a.json', b'{"options": {"style": "jazz"}}')['options']['style'] == 'jazz'
    try:
        analyze_file('a.txt', b'hello')
        raise AssertionError('accepted a text file')
    except ValueError:
        pass
    print('ok  MIDI / settings references')

    # ---- 1.9: in tune, per-genre instrument pools, orchestra genres, rig variety
    import bisect
    from sgcore.styles import POOLS
    from sgcore.instruments import INSTRUMENTS
    from sgcore import soundfont as sfm, vstrigs
    from sgcore.exporters import gm_program

    def clash_rate(song):
        tr = {t['name']: t for t in song['st']['tracks']}
        harm = sorted((e for e in song['events'] if e.midi is not None and tr.get(e.track, {}).get('layer') in ('chords', 'pad')),
                      key=lambda e: e.beat)
        starts = [e.beat for e in harm]
        bad = tot = 0
        for m in song['events']:
            if m.midi is None or tr.get(m.track, {}).get('layer') not in ('lead', 'arp') or m.dur < 0.2:
                continue
            i = bisect.bisect_right(starts, m.beat + 0.01)
            snd = {h.midi % 12 for h in harm[max(0, i - 60):i] if h.beat <= m.beat + 0.01 < h.beat + h.dur}
            tot += 1
            bad += m.midi % 12 not in snd and any((m.midi - p) % 12 in (1, 11) for p in snd)
        return bad / max(1, tot)
    for s in ('trap', 'uk_drill', 'trance', 'pop', 'cinematic', 'baroque', 'orchestral_hiphop', 'hybrid_trailer'):
        r = max(clash_rate(compose(Options(style=s, seed=k))) for k in (1, 2, 3))
        assert r < 0.02, (s, r)                                                 # held notes don't rub against the chords
    for s, d in POOLS.items():
        for layer, pool in d.items():
            assert all(i in INSTRUMENTS or (i.startswith('sf:') and i[3:] in sfm.SAMPLED) for i in pool), (s, layer)
            own = [t['inst'] for t in STYLES[s]['tracks'] if t['name'] == layer] or \
                [t['inst'] for t in STYLES[s]['tracks'] if t['layer'] == layer]          # the part's main track
            assert own and own[0] == pool[0], (s, layer)                        # the genre's own sound leads its pool
    hh = {t['inst'] for k in range(1, 13) for t in compose(Options(style='orchestral_hiphop', seed=k))['st']['tracks'] if t['layer'] == 'chords'}
    assert len(hh) >= 3 and hh <= set(POOLS['orchestral_hiphop']['chords']), hh   # varied, but only authentic choices
    a = {t['layer']: t['inst'] for t in compose(Options(style='cinematic', seed=3))['st']['tracks']}
    b = {t['layer']: t['inst'] for t in compose(Options(style='trance', seed=3))['st']['tracks']}
    assert a['chords'] in POOLS['cinematic']['chords'] and b['chords'] in POOLS['trance']['chords']
    S = [dict(id='a', name='BBC strings legato', ok=1), dict(id='b', name='BBC strings spiccato', ok=1),
         dict(id='c', name='BBC celli', ok=1), dict(id='d', name='BBC strings pizzicato', ok=1)]
    assert vstrigs._user_sound('strings', S)['id'] == 'a' and vstrigs._user_sound('spiccato', S)['id'] == 'b'
    assert vstrigs._user_sound('pizz', S)['id'] == 'd' and vstrigs._user_sound('cello', S)['id'] == 'c'
    assert gm_program(dict(inst='sf:cello')) == 42 and gm_program(dict(inst='vst:x', rig_from='sf:trumpet')) == 56
    print('ok  in tune, genre instrument pools, orchestra articulations')

    # ---- 1.10: meters, layered parts, counter-melodies, expression, more genres
    from sgcore.api import describe
    tmp = tempfile.mkdtemp()
    for s in ('waltz', 'celtic_jig', 'soul_ballad'):
        song = compose(Options(style=s, seed=4, counter='on'))
        assert song['meter'] == STYLES[s]['meter']
        assert all(abs(e.beat * 3 - round(e.beat * 3)) < 0.02 for e in song['events']), s     # everything on the triplet grid
        p = write_midi(os.path.join(tmp, s + '.mid'), song)
        b = open(p, 'rb').read()
        i = b.find(b'\xff\x58\x04')
        assert b[i + 3] == {'3/4': 3, '6/8': 6, '12/8': 12}[song['meter']], s                 # DAWs see the real meter
    for s in ('gospel', 'kpop', 'tango', 'salsa', 'afro_house', 'country', 'motown', 'melodic_techno'):  # (swing: bebop approach notes)
        assert max(clash_rate(compose(Options(style=s, seed=k))) for k in (1, 2)) < 0.03, s
        for layer, pool in POOLS[s].items():
            assert all(i in INSTRUMENTS or (i.startswith('sf:') and i[3:] in sfm.SAMPLED) for i in pool), (s, layer)
    n_layers = 0
    for k in range(1, 9):
        song = compose(Options(style='trance', seed=k))
        tr = {t['name']: t for t in song['st']['tracks']}
        for name, t in tr.items():
            if t.get('double_of'):
                n_layers += 1
                part = {t['double_of']} | {n for n, x in tr.items() if x.get('switch_of') == t['double_of']}   # incl. rotation
                src = [(e.beat, e.midi) for e in song['events'] if e.track in part]
                dup = [(e.beat, e.midi - t['octave']) for e in song['events'] if e.track == name]
                assert len(src) == len(dup) and t['inst'] != tr[t['double_of']]['inst']          # same notes, other sound
    assert n_layers >= 4
    assert not any(t.get('double_of') for t in compose(Options(style='trance', seed=2, layering='off'))['st']['tracks'])
    song = compose(Options(style='orchestral', seed=6, counter='on'))
    assert any(e.track == 'counter' for e in song['events']) and song['expr'] and all(0 <= v <= 127 for c in song['expr'].values() for _, v in c)
    info = describe(song)
    assert 'counter' in info['instruments'] and isinstance(info['arrangement'], list)
    assert len(STYLES) >= 80
    print('ok  meters, layered parts, counter-melodies, expression, new genres')

    # ---- 1.11: same take with a part switched off, lead register in every key, new instruments and genres
    def sig(s, layers):
        tr = {t['name']: t['layer'] for t in s['st']['tracks']}
        return {l: [(round(e.beat, 3), e.midi, round(e.vel, 3)) for e in s['events'] if tr.get(e.track) == l] for l in layers}
    L = ['bass', 'chords', 'arp', 'lead', 'kick', 'snare', 'pad', 'top']
    for s in ('pop', 'orchestral', 'jazz'):
        a = sig(compose(Options(style=s, seed=7)), L)
        for m in ('lead', 'chords', 'pad', 'arp'):
            b = sig(compose(Options(style=s, seed=7, muted=[m])), L)
            assert not b[m] and all(a[l] == b[l] for l in L if l != m), (s, m)            # switching a part off keeps the take
    for s in ('pop', 'house', 'jazz', 'orchestral', 'kpop'):
        for k in range(1, 7):
            song = compose(Options(style=s, seed=k))
            ld = [e.midi for e in song['events'] if e.track == 'lead' and e.midi is not None]
            if ld:
                assert 70 <= sum(ld) / len(ld) <= 88, (s, k, song['key'].name(), sum(ld) / len(ld))   # same register in any key
    for i in ('polysynth', 'synthbrass', 'moogbass', 'glasspad', 'solina', 'wurli', 'vibes', 'upright', 'mutedgtr', 'harmonica',
              'trumpet', 'pedalsteel'):
        y = INSTRUMENTS[i](64, 0.8, {})
        assert np.isfinite(y).all() and 0.01 < np.abs(y).max() < 4, i
    for s in ('braindance', 'hauntology'):
        assert compose(Options(style=s, seed=1))['events']
    print('ok  same take with parts off, lead register, new synths, braindance + hauntology')

    # ---- genre authenticity: every profiled genre passes its own production rules
    from sgcore.fitness import genre_fit
    low = []
    for s in STYLES:
        for k in (1, 2):
            f = genre_fit(compose(Options(style=s, seed=k)))
            if f and f['score'] < 100:
                low.append((s, k, [c['name'] for c in f['checks'] if not c['ok']]))
    assert not low, low
    song = compose(Options(style='neurofunk', seed=2))
    assert any(t.get('switch_of') for t in song['st']['tracks']) and any(e.track.startswith('bass_') for e in song['events'])
    assert any(t.get('double_of') == 'bass' and t['inst'] == 'sinebass' for t in song['st']['tracks'])     # clean sub under it all
    print('ok  genre authenticity checks, bass switching, sub layers')


def test_chords_and_knobs():
    import collections
    from sgcore.compose import Options, compose
    from sgcore.theory import color_fits, Key
    from sgcore.render import Renderer
    k = Key(1, 'major')
    assert not color_fits(k, 3, 'sus4') and not color_fits(k, 2, 'add9') and color_fits(k, 0, 'add9')
    bad = tot = 0
    for i, name in enumerate(['pop', 'house', 'jazz', 'synthwave', 'teen_pop', 'luxury_rap', 'chamber_pop', 'electro', 'salsa']):
        song = compose(Options(style=name, seed=300 + i))
        for t in song['st']['tracks']:
            if t['layer'] not in ('chords', 'pad'):
                continue
            hits = collections.defaultdict(set)
            for e in song['events']:
                if e.track == t['name'] and e.midi is not None:
                    hits[round(e.beat, 3)].add(e.midi)
            for ms in hits.values():
                ms = sorted(ms)
                tot += len(ms) > 1
                bad += any(b - a == 1 for a, b in zip(ms, ms[1:]))
    assert bad / tot < 0.03, (bad, tot)                                   # chords are chords, not neighbouring notes
    song = compose(Options(style='folk', seed=3))                         # strummed: low to high, never reordered
    r = Renderer(song, log=lambda *a: None)
    by = collections.defaultdict(list)
    for e in song['events']:
        if e.track == 'chords' and e.midi is not None:
            by[round(e.beat, 3)].append(e)
    for evs in list(by.values())[:200]:
        ts = [r.t_of(e.beat, True, 'chords') + e.strum * r.spb for e in sorted(evs, key=lambda e: e.strum)]
        assert ts == sorted(ts)
    def lead(o):
        return [e for e in compose(o)['events'] if e.track == 'lead' and e.midi is not None]
    a, b = lead(Options(style='pop', seed=9)), lead(Options(style='pop', seed=9, simplicity=1.0))
    assert len(b) < 0.8 * len(a) and sum(e.dur for e in b) / len(b) > sum(e.dur for e in a) / len(a)
    full = compose(Options(style='house', seed=4)); bare = compose(Options(style='house', seed=4, simplicity=1.0))
    assert sum(e.midi is None for e in bare['events']) < 0.6 * sum(e.midi is None for e in full['events'])
    assert not any(e.track == 'counter' for e in bare['events'])
    rng = lambda o: (lambda m: max(m) - min(m))([e.midi for e in lead(o)])
    assert rng(Options(style='pop', seed=9, melody_range=0.0)) < rng(Options(style='pop', seed=9, melody_range=1.0))
    assert compose(Options(style='pop', seed=9, chord_speed='slow'))['st']['chord_bars'] == 2 * compose(Options(style='pop', seed=9))['st']['chord_bars']
    assert Options().simplicity == 0.0                                    # defaults leave songs as they were
    print('ok  chords without clusters, strums in order, simplicity / repetition / range / chord speed')


def test_rotation_and_freshness():
    import collections
    from sgcore.compose import Options, compose, section_group
    song = compose(Options(style='pop', seed=12, rotation='lots'))
    alts = {t['name']: t for t in song['st']['tracks'] if t.get('switch_of') in ('lead', 'chords', 'pad', 'arp')}
    assert alts, 'rotation=lots made no section instruments'
    for name, t in alts.items():                        # alternates only play in their own section groups
        for e in song['events']:
            if e.track == name:
                sec = next(s_ for s_ in song['sections'] if s_['bar'] * 4 <= e.beat < (s_['bar'] + s_['bars']) * 4)
                assert section_group(sec) in t['groups'], (name, sec['name'])
        assert t['inst'] != next(x for x in song['st']['tracks'] if x['name'] == t['switch_of'])['inst']
    assert not any(t.get('switch_of') in ('lead', 'chords', 'pad', 'arp') for t in compose(Options(style='pop', seed=12, rotation='off'))['st']['tracks'])
    assert not any(t.get('switch_of') == 'lead' for t in compose(Options(style='pop', seed=12, rotation='lots', instruments={'lead': 'flute'}))['st']['tracks'])
    count = lambda avoid: collections.Counter(
        t['inst'] for sd in range(40) for t in compose(Options(style='house', seed=sd, rotation='off', avoid=avoid))['st']['tracks']
        if t['name'] == 'chords')
    base = count({})
    top = base.most_common(1)[0][0]
    fresh = count({'chords': [top]})
    assert fresh[top] < base[top], (top, base[top], fresh[top])           # recent instruments are picked less often
    a = compose(Options(style='pop', seed=12, rotation='lots', avoid={'lead': ['vox']}))
    b = compose(Options(style='pop', seed=12, rotation='lots', avoid={'lead': ['vox']}))
    assert [t['inst'] for t in a['st']['tracks']] == [t['inst'] for t in b['st']['tracks']]   # same options = same song
    print('ok  instrument rotation between sections, freshness, reproducibility')



def test_builds_and_vinyl():
    from collections import Counter
    for st in ('house', 'dubstep', 'future_bass'):
        used = Counter(b for k in range(1, 11) for b in compose(Options(style=st, seed=k))['st'].get('builds_used', []))
        assert len(used) >= 3, (st, used)                                   # not the same build-up every song
    for k in range(1, 9):
        u = compose(Options(style='house', seed=k))['st'].get('builds_used', [])
        assert all(a != b for a, b in zip(u, u[1:])), u                     # never the same build twice in a row
    assert set(compose(Options(style='house', seed=4, build_style='roll'))['st']['builds_used']) == {'roll'}
    for bs in ('hats', 'claps', 'toms', 'halftime', 'drumless'):
        s = compose(Options(style='trance', seed=2, build_style=bs))
        sec = next(x for x in s['sections'] if x['opts'].get('build'))
        a, b = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
        drums = [e for e in s['events'] if a <= e.beat < b and e.midi is None]
        if bs == 'drumless':
            assert not any(e.track in ('kick', 'snare', 'clap') for e in drums), bs
        else:
            assert drums, bs
    vin = lambda **kw: any(t['inst'] == 'vinyl' for t in compose(Options(seed=3, **kw))['st']['tracks'])
    assert not vin(style='phonk') and not vin(style='memphis_phonk') and vin(style='phonk', vinyl=True)
    assert not vin(style='lofi') and vin(style='lofi', vinyl=True) and not vin(style='lofi', vinyl=False)   # off unless asked for
    print('ok  build-ups vary per song and per build, new build types, vinyl on/off')



def test_kits_and_bells():
    from sgcore import drumkits
    from sgcore.styles import BELLS, MALLETS
    # genre kits
    for st, kit in (('jungle', 'jungle_raw'), ('boombap', 'funky_drummer'), ('downtempo', 'back_to_life'), ('trap', '808'),
                    ('trance', 'trance'), ('rock', 'rusty'), ('jazz', 'brushes'), ('funk', 'seventies'), ('metal', 'rock'),
                    ('synthwave', 'linn'), ('techno', 'techno')):
        assert compose(Options(style=st, seed=2))['st'].get('kit_id') == kit, st
    # a break replaces the kit's patterns with its own 4-bar cycle; jungle chops it, a straight break doesn't
    j = compose(Options(style='jungle', seed=3))
    assert {'kick', 'snare', 'ride'} <= {e.track for e in j['events'] if e.midi is None}
    def bars(song, track):
        out = {}
        for e in song['events']:
            if e.track == track:
                out.setdefault(int(e.beat // 4), []).append(round(e.beat % 4, 2))
        return [tuple(sorted(v)) for k, v in sorted(out.items())]
    straight = compose(Options(style='house', seed=3, kit='amen'))
    sb = set(bars(straight, 'snare'))
    assert len(sb) <= 10, sb                                           # the 4 bars of the break (+ fills, builds)
    assert len(set(bars(j, 'snare'))) > len(sb)                        # chopped: many more bar shapes
    # you can switch kits on any genre, and the menu lists them
    for k in drumkits.MENU:
        s = compose(Options(style='pop', seed=1, kit=k))
        assert s['st']['kit_id'] == k and any(e.midi is None for e in s['events']), k
    # bells only where they belong
    for name in ('trance', 'techno', 'dnb', 'house', 'neurofunk', 'future_bass', 'ukgarage', 'synthwave'):
        for k in range(1, 7):
            s = compose(Options(style=name, seed=k))
            for t in s['st']['tracks']:
                if t['layer'] in ('arp', 'lead', 'chords', 'pad'):
                    assert t['inst'] not in BELLS and t['inst'] not in MALLETS, (name, k, t['name'], t['inst'])
    s = compose(Options(style='trance', seed=1, instruments={'arp': 'bell'}))
    assert any(t['inst'] == 'bell' for t in s['st']['tracks'] if t['layer'] == 'arp')   # your own pick is kept
    assert any(t.get('gate') for t in compose(Options(style='trance', seed=1))['st']['tracks'])
    print('ok  genre drum kits, re-played breaks + chops, kit switching, bells only where idiomatic, trance gate')



def test_bible_genres():
    from sgcore.render import Renderer
    from sgcore.styles import STYLES
    new = ('italo_disco', 'new_beat', 'gabber', 'rave_hardcore', 'future_funk', 'bebop', 'modal_jazz', 'soul_jazz', 'fusion',
           'classical_period', 'romantic', 'impressionism', 'minimalism')
    for n in new:
        assert n in STYLES, n
    rng = {'house': (118, 128), 'deep_house': (115, 125), 'tech_house': (122, 128), 'progressive_house': (122, 130), 'bigroom': (125, 132),
           'uplifting_trance': (128, 140), 'psytrance': (138, 148), 'dubstep': (138, 145), 'dnb': (160, 180), 'jungle': (160, 180),
           'acid_house': (120, 130), 'italo_disco': (110, 128), 'new_beat': (90, 120), 'gabber': (160, 200), 'rave_hardcore': (130, 160),
           'synthwave': (80, 120), 'future_funk': (110, 130), 'bebop': (180, 300), 'funk': (90, 120)}
    for n, (lo, hi) in rng.items():
        a, b = STYLES[n]['bpm']
        assert lo <= a and b <= hi, (n, STYLES[n]['bpm'])
    # Alberti bass: low - high - middle - high
    s = compose(Options(style='classical_period', seed=2, rotation='off', layering='off'))
    arp = sorted((e.beat, e.midi) for e in s['events'] if e.track == 'arp')[:4]
    m = [x[1] for x in arp]
    assert m[1] == m[3] and m[0] < m[2] < m[1], m
    # jazz: snare comping on off-beats
    j = compose(Options(style='bebop', seed=2))
    assert any(e.track == 'snare' and (e.beat * 4) % 4 != 0 for e in j['events'])
    # rubato stretches phrase ends; the 80s kit gates its snare
    r = compose(Options(style='romantic', seed=2))
    R = Renderer(r, log=lambda *a: None)
    assert R.t_of(64, human=False) > 64 * R.spb and R.length > int(r['total_bars'] * 4 * R.spb * 44100)
    assert compose(Options(style='italo_disco', seed=1))['st'].get('gated_snare')
    print('ok  bible genres: tempos, Alberti bass, jazz comping, rubato, gated snare, 13 new genres')


if __name__ == '__main__':
    main()
    test_builds_and_vinyl()
    test_kits_and_bells()
    test_bible_genres()
    test_chords_and_knobs()
    test_rotation_and_freshness()
