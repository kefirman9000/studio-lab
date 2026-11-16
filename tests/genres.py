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
    blues = compose(Options(style='blues', seed=4))
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


if __name__ == '__main__':
    main()
