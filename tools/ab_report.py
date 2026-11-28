"""What your A/B picks say (2.30): which settings and sounds the songs you preferred had.

    python tools/ab_report.py              # reads ab_picks.jsonl next to studiolab.py
    python tools/ab_report.py --style trance

Every time you press "A is better" / "B is better" in the app, both songs' settings are saved. This report compares the
winners with the losers: numeric knobs (energy, complexity, variety, humanize, tempo) on average, and the sounds that
win or lose most often. With a few dozen picks in one genre it shows what to change in that genre's defaults.
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOBS = ('energy', 'complexity', 'variety', 'humanize', 'bpm', 'swing', 'reverb', 'width')


def load(path):
    out = []
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def report(picks, style=None):
    if style:
        picks = [p for p in picks if (p.get('winner') or {}).get('style') == style or (p.get('loser') or {}).get('style') == style]
    lines = [f'{len(picks)} A/B picks' + (f' involving {style}' if style else '')]
    if not picks:
        return '\n'.join(lines + ['(press "A is better" / "B is better" in the A/B bar to collect some)'])
    styles = Counter()
    for p in picks:
        w, lo = (p.get('winner') or {}).get('style'), (p.get('loser') or {}).get('style')
        if w != lo:
            styles[w] += 1
            styles[lo] -= 1
    if styles:
        lines.append('\nGenres (wins minus losses, when the two songs were different genres):')
        lines += [f'  {k:28} {v:+d}' for k, v in styles.most_common() if v]
    lines.append('\nKnobs (winner average vs loser average, where both songs set them):')
    for k in KNOBS:
        pairs = [(p['winner'][k], p['loser'][k]) for p in picks
                 if isinstance((p.get('winner') or {}).get(k), (int, float)) and isinstance((p.get('loser') or {}).get(k), (int, float))]
        if len(pairs) >= 3:
            w = sum(a for a, _ in pairs) / len(pairs)
            lo = sum(b for _, b in pairs) / len(pairs)
            lines.append(f'  {k:12} winners {w:7.2f}   losers {lo:7.2f}   ({len(pairs)} picks)')
    snd = Counter()
    for p in picks:
        ws, ls = p.get('winner_sounds') or {}, p.get('loser_sounds') or {}
        for part in set(ws) | set(ls):
            if ws.get(part) != ls.get(part):
                if ws.get(part):
                    snd[(part, ws[part])] += 1
                if ls.get(part):
                    snd[(part, ls[part])] -= 1
    if snd:
        lines.append('\nSounds that won most (part: sound, wins minus losses):')
        lines += [f'  {pt}: {s}  {v:+d}' for (pt, s), v in snd.most_common(12) if v > 0]
        lines.append('\nSounds that lost most:')
        lines += [f'  {pt}: {s}  {v:+d}' for (pt, s), v in sorted(snd.items(), key=lambda x: x[1])[:12] if v < 0]
    return '\n'.join(lines)


if __name__ == '__main__':
    st = sys.argv[sys.argv.index('--style') + 1] if '--style' in sys.argv else None
    print(report(load(os.path.join(ROOT, 'ab_picks.jsonl')), st))
