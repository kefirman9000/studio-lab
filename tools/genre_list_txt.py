"""Writes docs/GENRE_LIST.txt: every genre, grouped as in the app (tab > group), one per line with its command-line id.
New genres in the current version are starred."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from sgcore.styles import STYLES, LABELS  # noqa: E402
from sgcore.genre_groups import GROUPS  # noqa: E402


def main(new=()):
    ver = open(os.path.join(ROOT, 'VERSION')).read().strip()
    cats = {}
    for k, st in STYLES.items():
        cats.setdefault(st['category'], []).append(k)
    out = [f'STUDIO LAB - ALL {len(STYLES)} GENRES  (version {ver})',
           'Grouped as in the app: tab > group. [id] = the name for the command line, e.g.  python studiolab.py generate --style bhajan',
           f'* = new in {".".join(ver.split(".")[:2])}', '']
    for cat in ('Electronic', 'Classic', 'Orchestral'):
        ids = cats.get(cat, [])
        out += ['=' * 72, f'{cat.upper()}  ({len(ids)})', '=' * 72, '']
        seen = set()
        for g, members in GROUPS.get(cat, []):
            m = [k for k in members if k in STYLES]
            seen |= set(m)
            out.append(f'{g}  ({len(m)})')
            out += [f'    {LABELS.get(k, k)}  [{k}]' + ('  *' if k in new else '') for k in m]
            out.append('')
        rest = [k for k in ids if k not in seen]
        if rest:
            out.append(f'More  ({len(rest)})')
            out += [f'    {LABELS.get(k, k)}  [{k}]' for k in rest]
            out.append('')
    with open(os.path.join(ROOT, 'docs', 'GENRE_LIST.txt'), 'w') as f:
        f.write('\n'.join(out).rstrip() + '\n')
    print(f'{len(STYLES)} genres -> docs/GENRE_LIST.txt')


if __name__ == '__main__':
    main(set(sys.argv[1:]))
