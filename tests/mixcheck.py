"""Mix check for every genre: no part loses its level, the lead is never buried, nothing is extreme.

    python -m tests.mixcheck                 # every genre, 3 seeds each, from the arrangement (fast, no audio)
    python -m tests.mixcheck --measured      # also render genres and measure the actual stems (slow)
    python -m tests.mixcheck --measured qawwali ghazal    # measure just these

The static pass catches the kind of bug where a genre picks one of its alternative sounds and the part silently drops
to a generic level (riffs too quiet, pads too loud). The measured pass renders songs and compares each part's real
level with the lead.
"""
import glob
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sgcore.compose import Options, compose  # noqa: E402
from sgcore.render import ROLE_DB  # noqa: E402
from sgcore.styles import STYLES  # noqa: E402

MELODIC = ('bass', 'chords', 'pad', 'arp', 'lead')
# genres whose unusual balance is the point
LOUD_BASS = {'bass_warp_trap', 'bass_warp_fast', 'switchup_808', 'switchup_808_dj', 'switchup_808_hard', 'switchup_mallets', 'trap_metal', 'switchup_deathcore', 'dark_drill'}             # the 808 is the lead instrument
LEAD_IN_THE_WASH = {'dub_techno', 'shoegaze', 'dream_pop'}              # the melody sits inside the chords / guitars


def static_check(names=None, seeds=(1, 2, 3)):
    issues = []
    for name in names or STYLES:
        sty = STYLES[name]
        if sty.get('composer'):
            continue
        own = {t['name']: t.get('db') for t in sty['tracks']}
        for sd in seeds:
            s = compose(Options(style=name, seed=sd, variety=0.9))
            lv = {}
            for t in s['st']['tracks']:
                if t['name'] != t['layer'] or t['layer'] not in MELODIC + ('kick', 'snare'):
                    continue
                if own.get(t['name']) is not None and t.get('db') is None and not t.get('user_pick'):
                    issues.append(f'{name} seed {sd}: {t["name"]} lost the genre level (now {t["inst"]})')
                lv[t['layer']] = t['db'] if t.get('db') is not None else ROLE_DB.get(t['layer'], -22)
            if 'lead' in lv and name not in LEAD_IN_THE_WASH:
                top = max([lv[k] for k in ('chords', 'pad', 'arp') if k in lv] or [-99])
                if top > lv['lead'] + 4:
                    issues.append(f'{name} seed {sd}: lead {lv["lead"]} dB buried under {top} dB')
            for k, v in lv.items():
                if (v > -8 and not (k == 'bass' and name in LOUD_BASS)) or v < -36:
                    issues.append(f'{name} seed {sd}: {k} level {v} dB is extreme')
    return issues


def measured_check(names, seed=3):
    """Render each genre with stems and compare the real part levels with the lead."""
    import numpy as np
    from scipy.io import wavfile
    from sgcore.api import generate
    issues, out = [], tempfile.mkdtemp()
    try:
        for name in names:
            generate(dict(style=name, seed=seed), out, outputs=['stems'], log=lambda *a: None)
            d = (glob.glob(os.path.join(out, f'*_{name}_*seed{seed}_stems')) or [None])[0]
            if not d:
                continue
            lv = {}
            for f in glob.glob(os.path.join(d, '*.wav')):
                part = os.path.basename(f)[3:-4]
                x = wavfile.read(f)[1].astype(np.float32)
                x = np.abs(x).max(axis=1) if x.ndim == 2 else np.abs(x)
                act = x[x > 1e-3]                                          # only where the part plays
                if len(act) > 1000:
                    lv[part] = 20 * np.log10(np.sqrt(np.mean(act ** 2)) + 1e-12)
            shutil.rmtree(d, ignore_errors=True)
            for f in glob.glob(os.path.join(out, '*')):
                if os.path.isfile(f):
                    os.remove(f)
            if 'lead' not in lv or name in LEAD_IN_THE_WASH:
                continue
            for part, v in lv.items():
                if part in ('lead', 'drum_bus', 'reverb_delay_returns', 'fx') or part.startswith('tom_'):
                    continue
                if v > lv['lead'] + 9 and not (part == 'bass' and name in LOUD_BASS):
                    issues.append(f'{name}: {part} {v:.1f} dB overpowers the lead ({lv["lead"]:.1f} dB)')
            print(f'   measured {name}: ' + '  '.join(f'{k} {v:.0f}' for k, v in sorted(lv.items())))
    finally:
        shutil.rmtree(out, ignore_errors=True)
    return issues


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    names = args or list(STYLES)
    issues = static_check(names)
    for i in issues:
        print('  ✗', i)
    assert not issues, f'{len(issues)} mix problems'
    print(f'ok  mix levels: {len(names)} genres x 3 seeds - no lost levels, no buried leads, nothing extreme')
    if '--measured' in sys.argv:
        m = measured_check(names)
        for i in m:
            print('  ✗', i)
        assert not m, f'{len(m)} measured mix problems'
        print(f'ok  measured mix: {len(names)} genres')
    print('all good')


if __name__ == '__main__':
    main()
