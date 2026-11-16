"""Genre authenticity + customization checks (no plugins or internet needed).
   python -m tests.genres"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sgcore.compose import Options, compose, voice_chord, Key, GENRE_MELODY, GENRE_VOICING
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
    from sgcore.compose import preview_window
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
    for name, bs in want.items():
        assert compose(Options(style=name, seed=5))['st']['build_style'] == bs, name
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
    from sgcore.compose import NOTE_NAMES
    d = tempfile.mkdtemp()
    song = compose(Options(style='pop', seed=31, variety=0))
    path = write_midi(os.path.join(d, 'x.mid'), song)
    ref = analyze_file(path, open(path, 'rb').read())
    assert ref['bpm'] == song['bpm'] and ref['key'].rstrip('m') == NOTE_NAMES[song['key'].root], (ref, song['key'].name())
    progs = {'-'.join(str(x + 1) for x in song[k]) for k in ('prog_main', 'prog_verse', 'prog_alt')}
    assert ref['progression'] in progs, (ref, progs)
    assert analyze_file('a.json', b'{"options": {"style": "jazz"}}')['options']['style'] == 'jazz'
    try:
        analyze_file('a.txt', b'hello')
        raise AssertionError('accepted a text file')
    except ValueError:
        pass
    print('ok  MIDI / settings references')


if __name__ == '__main__':
    main()
