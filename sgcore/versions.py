"""(2.19) Versions of one song: a radio edit, the original, an extended mix - built from the song's OWN sections
(each section keeps its exact notes and sounds; only which sections play, and how long the intro / outro run, changes).

version_edits(base_form, bpm, version) -> a section list for Options.sections, or None for the original.
  'radio'    : ~3 minutes - shorter intro and outro, then (only while it's still too long) the solo / bridge, the second
               verse's second half, the second verse, extra middle choruses go - never the first or the last chorus / drop
  'extended' : dance music gets a DJ-friendly drums-and-bass intro and outro and one more drop; everything else gets one
               more verse + chorus before the end
  'shorter' / 'longer' : one step down / up from the given section list (the editor's - / + buttons)
"""
HOOK = {'chorus', 'hook', 'drop', 'climax', 'theme', 'B', 'refrain', 'head', 'loop'}
OUTRO = {'outro', 'ending', 'end', 'coda', 'fade', 'tag'}
EXTRA = {'solo', 'bridge', 'interlude', 'instrumental', 'middle8', 'breakdown2', 'jam', 'trade', 'trades'}
INTRO = {'intro', 'alap', 'alapana', 'buka', 'invocation', 'doina', 'bells', 'drums'}
DRUMS = {'kick', 'snare', 'top', 'bass'}
RADIO_SEC = 200.0


def _kind(f):
    name, bars, layers, o = f
    n = str(name).lower()
    if o.get('build'):
        return 'build'
    if o.get('fade') or n in OUTRO:
        return 'outro'
    if n in INTRO:
        return 'intro'
    if o.get('drop') or name in HOOK or n in HOOK:
        return 'hook'
    if n in EXTRA:
        return 'extra'
    if n.startswith('break'):
        return 'break'
    return 'verse'


def _bars(e, base_form):
    return int(e.get('bars') or base_form[e['src']][1])


def duration(edits, base_form, bpm):
    return sum(_bars(e, base_form) for e in edits) * 4 * 60.0 / bpm


def _radio(edits, base_form, bpm, target):
    edits = [dict(e) for e in edits]
    kinds = [_kind(base_form[e['src']]) for e in edits]
    bar_s = 4 * 60.0 / bpm

    def too_long():
        return duration(edits, base_form, bpm) > target
    # 1. intro and outro to ~8 s / ~12 s (whole 4-bar steps; written 1-2 bar parts stay)
    for i, k in enumerate(kinds):
        b = _bars(edits[i], base_form)
        if k == 'intro' and i < 2 and b > 4:
            edits[i]['bars'] = max(4, min(b, int(round(8 / bar_s / 4)) * 4 or 4))
        if k == 'outro' and b > 4:
            edits[i]['bars'] = max(4, min(b, int(round(12 / bar_s / 4)) * 4 or 4))
    hooks = [i for i, k in enumerate(kinds) if k == 'hook']
    # the first REAL chorus / drop: the first one after a verse (an 8-bar chorus up front is a teaser)
    v0 = next((i for i, k in enumerate(kinds) if k == 'verse'), -1)
    first_h = next((i for i in hooks if i > v0), hooks[0] if hooks else -1)
    last_h = hooks[-1] if hooks else -1
    # 2. while too long, in this order: halve the second verse; halve then drop a solo / bridge; halve long breaks and
    #    drops; drop a middle verse together with the chorus after it (never the first real chorus or the last one);
    #    drop a chorus that directly repeats another; drop middle breaks
    verses = [i for i, k in enumerate(kinds) if k == 'verse']
    extras = [i for i, k in enumerate(kinds) if k == 'extra']
    order = [('half', i, 8) for i in verses[1:]]
    order += [('half', i, 8) for i in extras] + extras[1:] + [('half', i, 8) for i in extras]
    order += [('half', i, 16) for i, k in enumerate(kinds) if k == 'break'] + [('half', i, 16) for i in hooks if i not in (first_h, last_h)]
    order += [('half', i, 32) for i in (first_h, last_h) if i >= 0]
    order += [i - 1 for i in hooks[1:] if kinds[i - 1] == 'hook' and i - 1 != first_h]     # chorus, chorus -> one chorus
    for v in reversed(verses[1:]):
        nxt = [j for j in range(v + 1, len(kinds)) if kinds[j] in ('hook', 'verse', 'outro', 'extra')]
        h = nxt[0] if nxt and kinds[nxt[0]] == 'hook' and nxt[0] not in (first_h, last_h) else None
        order.append(('pair', v, h))
    order += extras[:1]
    order += [i for i, k in enumerate(kinds) if k == 'break'][:-1]
    gone = set()

    def cur():
        return duration([e for j, e in enumerate(edits) if j not in gone], base_form, bpm)

    def cut(ids):
        ids = [i for i in ids if i is not None and i not in gone]
        after = duration([e for j, e in enumerate(edits) if j not in gone and j not in ids], base_form, bpm)
        if after < target - 50 and cur() < target + 40:
            return                                    # close enough: don't land far too short
        gone.update(ids)
    for step in order:
        if cur() <= target:
            break
        if isinstance(step, tuple) and step[0] == 'half':
            _, i, floor = step
            b = _bars(edits[i], base_form)
            if i not in gone and b >= 2 * floor and b > floor:
                edits[i]['bars'] = max(floor, (b // 2) // 4 * 4 or floor)
            continue
        if isinstance(step, tuple) and step[0] == 'pair':
            _, v, h = step
            builds = [j for j in range(v + 1, (h if h is not None else v + 1)) if kinds[j] == 'build']
            cut([v, h] + builds if h is not None else [v])
            continue
        cut([step])
    keep = [i for i in range(len(edits)) if i not in gone]
    # a build-up must still lead into a chorus / drop
    keep = [i for n, i in enumerate(keep) if kinds[i] != 'build' or (n + 1 < len(keep) and kinds[keep[n + 1]] in ('hook', 'verse')
                                                                       and kinds[keep[n + 1]] != 'build')]
    return [edits[i] for i in keep]


def _extended(edits, base_form, dance=True):
    edits = [dict(e) for e in edits]
    kinds = [_kind(base_form[e['src']]) for e in edits]
    copies = {}

    def copy_of(src):
        copies[src] = copies.get(src, max([int(e.get('copy', 0)) for e in edits if e['src'] == src] + [0])) + 1
        return copies[src]
    hooks = [i for i, k in enumerate(kinds) if k == 'hook']
    if not hooks:
        hooks = [max(range(len(edits)), key=lambda i: len(base_form[edits[i]['src']][2]))]
    last = hooks[-1]
    hsrc = edits[last]['src']
    layers = set(base_form[hsrc][2])
    outro_at = next((i for i in range(len(edits) - 1, -1, -1) if kinds[i] != 'outro'), len(edits) - 1) + 1
    if dance and 'kick' in layers:                    # dance music: DJ intro / outro (drums + bass), one more drop
        mute = sorted(layers - DRUMS)
        dj_in = dict(src=hsrc, copy=copy_of(hsrc), bars=16, mute=mute + (['bass'] if 'bass' in layers else []), label='DJ intro')
        dj_out = dict(src=hsrc, copy=copy_of(hsrc), bars=16, mute=mute, label='DJ outro')
        prev_build = next((i for i in range(last - 1, -1, -1) if kinds[i] == 'build'), None)
        more = ([dict(src=edits[prev_build]['src'], copy=copy_of(edits[prev_build]['src']))] if prev_build is not None else []) + \
            [dict(src=hsrc, copy=copy_of(hsrc))]
        return [dj_in] + edits[:outro_at] + more + edits[outro_at:] + [dj_out]
    # songs: one more verse + chorus before the ending
    verse = next((i for i in range(last - 1, -1, -1) if kinds[i] == 'verse'), None)
    more = ([dict(src=edits[verse]['src'], copy=copy_of(edits[verse]['src']))] if verse is not None else []) + \
        [dict(src=hsrc, copy=copy_of(hsrc))]
    return edits[:outro_at] + more + edits[outro_at:]


def version_edits(base_form, bpm, version, edits=None, dance=None):
    if dance is None:
        dance = any(f[3].get('drop') for f in base_form)
    edits = [dict(e) for e in (edits or [dict(src=i, copy=0) for i in range(len(base_form))])]
    if version == 'radio':
        out = _radio(edits, base_form, bpm, RADIO_SEC)
    elif version == 'extended':
        out = _extended(edits, base_form, dance)
    elif version == 'shorter':                     # one step: about one section's worth shorter
        cur = duration(edits, base_form, bpm)
        out = edits
        for t in (cur - 1, cur - 8, cur - 15, cur - 25):
            out = _radio(edits, base_form, bpm, t)
            if duration(out, base_form, bpm) < cur - 0.5:
                break
    elif version == 'longer':                      # one step: the last chorus / drop (and its build) once more
        kinds = [_kind(base_form[e['src']]) for e in edits]
        end = next((i for i in range(len(edits)) if kinds[i] == 'outro' and i > len(edits) // 2), len(edits))
        hooks = [i for i, k in enumerate(kinds) if k == 'hook' and i < end and not edits[i].get('label')] or [len(edits) // 2]
        last = hooks[-1]
        src = edits[last]['src']
        c = max([int(e.get('copy', 0)) for e in edits if e['src'] == src] + [0]) + 1
        at = last + 1
        out = edits[:at] + [dict(src=src, copy=c)] + edits[at:]
    else:
        return None
    return out if out != edits or version in ('radio', 'extended') else edits
