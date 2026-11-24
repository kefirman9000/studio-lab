"""Find genres that are built almost the same way (likely to sound alike).

    python tools/genre_twins.py            # every pair scoring >= 0.8, worst first
    python tools/genre_twins.py 0.7        # a lower bar

Compares what each genre is made of - tempo range, swing, meter, drum kit, the drum patterns, the bass line and the
sounds of each part - without rendering anything, so it runs in a second (tests.features keeps new twins out).
Score 1.0 = the same recipe.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def recipe(g, st):
    from sgcore import drumkits
    d = st.get('drums') or {}
    first = lambda k: tuple((d.get(k) or [''])[:1])                                  # noqa: E731
    sounds = {(t['layer'], t['inst']) for t in st.get('tracks', []) if t['layer'] not in ('kick', 'snare', 'top', 'fx')}
    return dict(bpm=tuple(st['bpm']), swing=round(float(st.get('swing') or 0.5), 2), meter=st.get('meter') or '4/4',
                kit=drumkits.GENRE_KIT.get(g) or st.get('kit') or 'default', kick=first('kick'),
                snare=first('snare') or first('clap'), hat=first('chat') or first('ride'), bass=tuple((st.get('bass') or [''])[:1]),
                sounds=sounds, form=st.get('form'), drumless=not any(d.values()))


def score(a, b):
    lo, hi = max(a['bpm'][0], b['bpm'][0]), min(a['bpm'][1], b['bpm'][1])
    span = max(a['bpm'][1], b['bpm'][1]) - min(a['bpm'][0], b['bpm'][0]) or 1
    s_bpm = max(0.0, (hi - lo) / span)
    same = lambda k: 1.0 if a[k] == b[k] else 0.0                                     # noqa: E731
    u = a['sounds'] | b['sounds']
    s_snd = len(a['sounds'] & b['sounds']) / len(u) if u else 1.0
    if a['drumless'] and b['drumless']:
        drums = 1.0
    else:
        drums = (same('kick') + same('snare') + same('hat') + same('kit')) / 4
    return round(0.2 * s_bpm + 0.05 * same('swing') + 0.05 * same('meter') + 0.3 * drums + 0.1 * same('bass')
                 + 0.3 * s_snd, 3)


def twins(threshold=0.8):
    from sgcore.styles import STYLES
    rs = {g: recipe(g, st) for g, st in STYLES.items()}
    names = sorted(rs)
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            s = score(rs[a], rs[b])
            if s >= threshold:
                out.append((s, a, b))
    return sorted(out, reverse=True)


if __name__ == '__main__':
    th = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8
    for s, a, b in twins(th):
        print(f'{s:.2f}  {a}  ~  {b}')
