"""Write docs/GENRES.md: every genre Studio Lab makes, by category, with its id, tempo and current description."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sgcore.styles import STYLES, CATEGORIES, label  # noqa: E402
from sgcore.genre_groups import group_of, order  # noqa: E402


def main():
    out = [f'# Studio Lab genres ({len(STYLES)})', '',
           'Every genre the app can generate, by category: display name, id (used by `--style` and in genre bibles), tempo range '
           'and the description the app currently works from.', '']
    for cat in CATEGORIES:
        names = sorted((k for k, v in STYLES.items() if v['category'] == cat), key=label)
        out += [f'## {cat} ({len(names)})', '']
        for g in order(cat):
            ks = [k for k in names if group_of(k) == g]
            if not ks:
                continue
            out += [f'### {g} ({len(ks)})', '', '| Genre | id | BPM | Current description |', '|---|---|---|---|']
            for k in ks:
                st = STYLES[k]
                out.append(f"| {label(k)} | `{k}` | {st['bpm'][0]}-{st['bpm'][1]} | {st['desc'].replace('|', '/')} |")
            out.append('')
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'GENRES.md')
    with open(path, 'w') as f:
        f.write('\n'.join(out))
    print(path)


if __name__ == '__main__':
    main()
