"""Arrangement variants (2.4): every song gets its own take on its genre's layout.

225 of the 355 genres had a single layout, so every song in them had the same shape (intro 4, verse 16, chorus 16 ...).
This reshapes the genre's OWN layout per song with the moves arrangers actually make - so the genre's character stays,
but the song's shape doesn't repeat. About a quarter of songs keep the genre's layout as written.

  verse / chorus songs  pre-chorus builds, the hook first (cold open), a radio edit (no bridge, short intro), a
                        breakdown instead of the bridge, a double final chorus that gains layers, a longer / shorter
                        intro, a cold ending
  club tracks (drops)   a long DJ intro, a longer breakdown, a fake-out build, a switch-up final drop (a different
                        bass), the last drop extended or followed by a short third drop, a 32-bar drop split in two
                        with the second half varied
  A / B forms           an extra A at the end (varied), a longer C, B before A

Not touched: genres modelled on reference records (their exact layouts), generated layouts (slam / cybergrind),
classical forms, scores, genres that already rotate their own layouts, and any structure you picked yourself.
"""
import random

GROW = ('arp', 'pad')                                    # what a final chorus / drop adds when the genre has it


def _has(form, name):
    return any(s[0] == name for s in form)


def _sec(name, bars, layers, **o):
    return (name, int(bars), set(layers), dict(o))


def vary_layout(form, st, seed, available):
    """form: [(name, bars, layers, opts)], available: layers the genre has. Returns (new form, [moves])."""
    rnd = random.Random(f'{seed}-layout-{st.get("name")}')
    if rnd.random() < 0.25 or len(form) < 3:
        return form, []
    form = [(n, b, set(l), dict(o)) for (n, b, l, o) in form]
    total0 = sum(s[1] for s in form)
    song = _has(form, 'chorus')
    club = not song and any(s[3].get('drop') or s[0] == 'drop' for s in form)
    moves = []
    if song:
        menu = ['pre', 'cold_open', 'radio', 'breakdown', 'double_end', 'intro', 'cold_end']
    elif club:
        menu = ['dj_intro', 'long_break', 'fake', 'switch', 'extend_last', 'third_drop', 'split_drop']
    else:
        menu = ['extra_a', 'long_c', 'b_first', 'intro', 'cold_end']
    rnd.shuffle(menu)
    for mv in menu[:rnd.choice([1, 2, 2, 3])]:
        new = _apply(mv, form, available, rnd)
        if new is None:
            continue
        tot = sum(s[1] for s in new)
        if not 0.7 * total0 <= tot <= 1.45 * total0:  # keep the song about its usual length
            continue
        form = new
        moves.append(mv)
    return form, moves


def _apply(mv, form, avail, rnd):
    f = list(form)
    idx = [i for i, s in enumerate(f)]
    if mv == 'pre':                                       # a 4-bar build into every chorus after the first verse
        out, seen_verse = [], False
        for s in f:
            if s[0] == 'chorus' and seen_verse and out and out[-1][0] == 'verse':
                v = out[-1]
                out.append(_sec('build', 4, v[2] - {'kick'} | ({'pad'} & avail), build=True))
            seen_verse = seen_verse or s[0] == 'verse'
            out.append(s)
        return out if len(out) > len(f) else None
    if mv == 'cold_open':                                 # the hook first: 8 bars of chorus right after the intro
        ch = next((s for s in f if s[0] == 'chorus'), None)
        if not ch:
            return None
        i = 1 if f[0][0] == 'intro' else 0
        return f[:i] + [_sec('chorus', 8, ch[2], crash=True)] + f[i:]
    if mv == 'radio':                                     # radio edit: no bridge, a short intro
        out = [s for s in f if s[0] not in ('bridge', 'C')]
        if out and out[0][0] == 'intro':
            out[0] = (out[0][0], min(out[0][1], 4), out[0][2], out[0][3])
        return out if len(out) < len(f) else None
    if mv == 'breakdown':                                 # the bridge becomes a drums-out breakdown + a short build
        i = next((k for k, s in enumerate(f) if s[0] == 'bridge'), None)
        if i is None:
            return None
        b = f[i]
        brk = _sec('break', b[1], (b[2] - {'kick', 'snare', 'top', 'bass'}) | ({'pad'} & avail), alt=True)
        return f[:i] + [brk, _sec('build', 4, (b[2] - {'kick'}) | ({'top'} & avail), build=True)] + f[i + 1:]
    if mv == 'double_end':                                # the last chorus twice - the second one bigger
        i = max((k for k, s in enumerate(f) if s[0] == 'chorus'), default=None)
        if i is None:
            return None
        c = f[i]
        big = _sec('chorus', c[1], c[2] | (set(GROW) & avail), crash=True, alt=True)
        return f[:i + 1] + [big] + f[i + 1:]
    if mv == 'intro':                                     # a longer or shorter intro
        if f[0][0] != 'intro':
            return None
        b = f[0][1]
        nb = b * 2 if b <= 8 and rnd.random() < 0.6 else max(2, b // 2)
        return [(f[0][0], nb, f[0][2], f[0][3])] + f[1:] if nb != b else None
    if mv == 'cold_end':                                  # end on the downbeat instead of fading
        last = f[-1]
        if not last[3].get('fade'):
            return None
        o = dict(last[3])
        o.pop('fade', None)
        o['cad'] = True
        return f[:-1] + [(last[0], last[1], last[2], o)]
    if mv == 'dj_intro':                                  # a long, layered DJ intro
        if f[0][0] != 'intro' or f[0][1] >= 16:
            return None
        o = dict(f[0][3], layer_in=True)
        return [(f[0][0], 16, f[0][2] | ({'kick', 'top'} & avail), o)] + f[1:]
    if mv == 'long_break':                                # the breakdown half as long again
        i = next((k for k, s in enumerate(f) if s[0] == 'break'), None)
        if i is None:
            return None
        s = f[i]
        return f[:i] + [(s[0], int(s[1] * 1.5 // 4 * 4) or s[1], s[2], s[3])] + f[i + 1:]
    if mv == 'fake':                                      # a false start: the build cuts to a stripped beat first
        i = max((k for k, s in enumerate(f) if s[3].get('build')), default=None)
        if i is None or i == 0:
            return None
        s = f[i]
        return f[:i] + [(s[0], s[1], s[2], dict(s[3], fake=True))] + f[i + 1:]
    if mv == 'switch':                                    # the final drop switches up (a different bass)
        i = max((k for k, s in enumerate(f) if s[3].get('drop') or s[0] == 'drop'), default=None)
        if i is None:
            return None
        s = f[i]
        return f[:i] + [(s[0], s[1], s[2], dict(s[3], switch=True, alt=True))] + f[i + 1:]
    if mv == 'extend_last':                               # the last drop runs half as long again
        i = max((k for k, s in enumerate(f) if s[3].get('drop') or s[0] == 'drop'), default=None)
        if i is None:
            return None
        s = f[i]
        return f[:i] + [(s[0], int(s[1] * 1.5 // 4 * 4), s[2] | (set(GROW) & avail), s[3])] + f[i + 1:]
    if mv == 'third_drop':                                # a short third drop after a quick breather
        i = max((k for k, s in enumerate(f) if s[3].get('drop') or s[0] == 'drop'), default=None)
        if i is None:
            return None
        d = f[i]
        breath = _sec('break', 4, (d[2] - {'kick', 'bass'}) or {'pad'}, alt=True)
        return f[:i + 1] + [breath, _sec(d[0], 8, d[2] | (set(GROW) & avail), drop=True, crash=True, alt=True)] + f[i + 1:]
    if mv == 'split_drop':                                # a 32-bar drop as two 16s, the second varied
        i = next((k for k, s in enumerate(f) if (s[3].get('drop') or s[0] == 'drop') and s[1] >= 32), None)
        if i is None:
            return None
        s = f[i]
        return f[:i] + [(s[0], s[1] // 2, s[2], s[3]), (s[0], s[1] - s[1] // 2, s[2], dict(s[3], alt=True))] + f[i + 1:]
    if mv == 'extra_a':                                   # one more A at the end, varied
        a = [s for s in f if s[0] == 'A']
        if not a:
            return None
        end = len(f) - 1 if f[-1][0] == 'outro' else len(f)
        return f[:end] + [_sec('A', a[-1][1], a[-1][2], alt=True)] + f[end:]
    if mv == 'long_c':
        i = next((k for k, s in enumerate(f) if s[0] == 'C'), None)
        if i is None:
            return None
        s = f[i]
        return f[:i] + [(s[0], s[1] * 2, s[2], s[3])] + f[i + 1:]
    if mv == 'b_first':
        ia = next((k for k, s in enumerate(f) if s[0] == 'A'), None)
        ib = next((k for k, s in enumerate(f) if s[0] == 'B'), None)
        if ia is None or ib is None or ib != ia + 1:
            return None
        f[ia], f[ib] = f[ib], f[ia]
        return f
    del idx
    return None
