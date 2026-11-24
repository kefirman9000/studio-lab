"""Learn from MIDI: read a MIDI file and teach a genre its grooves.

From the notes we pull out what a genre is built from - the tempo, the scale, the chord loops (as scale degrees) and the
drum and bass rhythms (as Studio Lab step patterns) - and either add them to an existing genre or save them as your own
variant of it. What you teach is kept in learned.json next to the app, so it survives restarts and updates, and can be
forgotten again.
"""
import copy
import json
import os
from collections import Counter

from . import updater
from .refparse import parse_midi, _key, bar_degrees

PATH = os.path.join(updater.ROOT, 'user_sounds', 'learned.json')
_ORIG = {}                                   # each genre as it was before anything was taught to it
STEPS = 16                                   # a 4/4 bar on a 16th-note grid

# General MIDI drum notes -> Studio Lab drum parts
GM_SLOT = {35: 'kick', 36: 'kick', 38: 'snare', 40: 'snare', 37: 'rim', 39: 'clap', 42: 'chat', 44: 'chat', 46: 'ohat',
           51: 'ride', 53: 'ride', 59: 'ride', 49: 'crash', 57: 'crash', 41: 'tom', 43: 'tom', 45: 'tom', 47: 'tom',
           48: 'tom', 50: 'tom', 54: 'tamb', 56: 'cowbell', 69: 'shaker', 70: 'shaker', 82: 'shaker'}
NO_TRACK_ALIAS = {'clap': 'snare', 'rim': 'snare', 'shaker': 'chat', 'tamb': 'chat', 'ride': 'chat', 'chat': 'ride'}


# ----------------------------------------------------------------------------- reading a file
def _bars(notes, bpb):
    end = max(b + ln for b, ln, m, v, d in notes)
    return max(1, int(end // bpb + (1 if end % bpb > 0.01 else 0)))


def _grid(times, vels, nbars, bpb, steps=STEPS):
    """Hits -> one step string per bar ('X' strong, 'x' normal, 'o' soft, '.' rest)."""
    rows = [['.'] * steps for _ in range(nbars)]
    for t, v in zip(times, vels):
        bar, pos = divmod(t, bpb)
        s = int(round(pos / bpb * steps))
        if s >= steps:
            bar, s = bar + 1, 0
        bar = int(bar)
        if 0 <= bar < nbars:
            c = 'X' if v >= 0.85 else ('o' if v < 0.45 else 'x')
            old = rows[bar][s]
            rows[bar][s] = max(old, c, key='.oxX'.index)
    return [''.join(r) for r in rows]


def _top(rows, n=3, min_count=2, plain=False):
    """The most common non-empty bar patterns (accents folded together when counting)."""
    if plain:
        rows = [r.replace('X', 'x').replace('o', 'x') for r in rows]
    key = lambda r: r.replace('X', 'x').replace('o', 'x')     # noqa: E731
    counts = Counter(key(r) for r in rows if r.strip('.'))
    out = []
    for pat, c in counts.most_common():
        if c < min_count or len(out) >= n:
            break
        # keep the accents of the most common spelling of this rhythm
        spell = Counter(r for r in rows if key(r) == pat).most_common(1)[0][0]
        out.append(spell)
    return out


def _bass_part(notes, chans):
    """The bass: the pitched channel with the lowest median note that plays at least now and then."""
    by = {}
    for n, ch in zip(notes, chans):
        if not n[4]:
            by.setdefault(ch, []).append(n)
    best, bm = None, 999
    for ch, ns in by.items():
        if len(ns) < 8:
            continue
        ms = sorted(m for b, ln, m, v, d in ns)
        med = ms[len(ms) // 2]
        if med < bm and med < 60:
            best, bm = ns, med
    return best or []


def _bass_patterns(bass, nbars, bpb):
    """Bass rhythm as letters: R root, O root an octave up, F fifth, A any other (approach) note, '-' held."""
    rows = []
    for bar in range(nbars):
        b0 = bar * bpb
        ns = sorted((n for n in bass if b0 - 1e-3 <= n[0] < b0 + bpb - 1e-3), key=lambda n: n[0])
        if not ns:
            rows.append('.' * STEPS)
            continue
        first = [n for n in ns if n[0] - b0 < bpb / 4] or ns
        root = min(n[2] for n in first if n[2] % 12 == first[0][2] % 12)
        row = ['.'] * STEPS
        for b, ln, m, v, d in ns:
            s = int(round((b - b0) / bpb * STEPS))
            if s >= STEPS:
                continue
            iv = m - root
            c = 'R' if iv == 0 else ('O' if iv % 12 == 0 else ('F' if iv % 12 == 7 else 'A'))
            row[s] = c
            hold = int(round(ln / bpb * STEPS))
            for k in range(s + 1, min(STEPS, s + hold)):
                if row[k] == '.':
                    row[k] = '-'
        rows.append(''.join(row))
    # a held note only counts as held up to the next onset
    out = []
    for r in rows:
        r2, last = list(r), None
        for i, c in enumerate(r2):
            if c in 'ROFA':
                last = i
            elif c == '-' and last is None:
                r2[i] = '.'
        out.append(''.join(r2))
    return out


def _loops(degs, n=3):
    runs = [d for i, d in enumerate(degs) if i == 0 or d != degs[i - 1]]
    if len(runs) < 2:
        return []
    if len(runs) <= 4:
        return [(runs * 4)[:4]]
    counts = Counter(tuple(runs[i:i + 4]) for i in range(len(runs) - 3)).most_common()
    out = []
    for w, c in counts:
        if c < 2 and out:
            break
        if len(out) >= n:
            break
        out.append(list(w))
    return out


def learn(data, name=''):
    """Everything a genre can take from this MIDI file."""
    parsed = parse_midi(data)
    notes, chans = parsed['notes'], parsed.get('chans') or [0] * len(parsed['notes'])
    num, den = parsed['timesig']
    bpb = num * 4 / den
    root, scale, _ = _key(notes, parsed.get('keysig'), bpb)
    nbars = _bars(notes, bpb)
    bpm = float(parsed['bpm'])
    while bpm < 60:
        bpm *= 2
    while bpm > 200:
        bpm /= 2
    out = dict(name=os.path.basename(name or 'MIDI file'), bpm=int(round(bpm)), scale=scale, meter=f'{num}/{den}',
               bars=nbars, drums={}, bass=[], progs=[])
    pitched = [n for n in notes if not n[4]]
    if pitched:
        out['progs'] = _loops(bar_degrees(pitched, root, scale, bpb))
    if (num, den) != (4, 4):
        out['note'] = 'Only the tempo and chords were learned: rhythms are learned from 4/4 songs.'
        return out
    hits = {}
    for b, ln, m, v, d in notes:
        if d and m in GM_SLOT:
            hits.setdefault(GM_SLOT[m], ([], []))
            hits[GM_SLOT[m]][0].append(b)
            hits[GM_SLOT[m]][1].append(v)
    for slot, (ts, vs) in hits.items():
        if slot == 'crash':
            continue
        rows = _grid(ts, vs, nbars, bpb)
        if slot in ('kick', 'snare', 'clap', 'rim'):     # leave out fills and build-up rolls
            rows = [r for r in rows if sum(c != '.' for c in r) <= 9]
        pats = _top(rows)
        if pats:
            out['drums'][slot] = pats
    bass = _bass_part(notes, chans)
    if bass:
        out['bass'] = _top(_bass_patterns(bass, nbars, bpb))
    return out


# ----------------------------------------------------------------------------- applying it to genres
def _load():
    try:
        with open(PATH) as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(d):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    tmp = PATH + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(d, f, indent=1)
    os.replace(tmp, PATH)


def _merge(st, lr, replace=False):
    """Add what was learned to a genre dict (in place). Returns a list of what was used."""
    used = []
    drums = st.setdefault('drums', {})
    learned = lr.get('drums') or {}
    done = set()
    # parts the genre has first, then a part it lacks onto its nearest part (if nothing filled that one already)
    order = [k for k in learned if k in drums] + [k for k in learned if k not in drums]
    for slot in order:
        pats = learned[slot]
        tgt = slot if slot in drums else NO_TRACK_ALIAS.get(slot)
        if tgt not in drums or not pats or tgt in done:
            continue
        cur = [] if replace else [p for p in drums[tgt] if p not in pats]
        drums[tgt] = list(pats) + cur
        done.add(tgt)
        used.append(f'{tgt} rhythm')
    if lr.get('bass') and st.get('bass_mode', 'pattern') not in ('walk',):
        cur = [] if replace else [p for p in st.get('bass', []) if p not in lr['bass']]
        st['bass'] = list(lr['bass']) + cur
        used.append('bass line')
    progs, sc = lr.get('progs') or [], lr.get('scale')
    if progs and sc in st.get('scales', []):
        if isinstance(st.get('progs'), dict):
            cur = [] if replace else [p for p in st['progs'].get(sc, []) if p not in progs]
            st['progs'][sc] = [list(p) for p in progs] + cur
        else:
            cur = [] if replace else [p for p in (st.get('progs') or []) if p not in progs]
            st['progs'] = [list(p) for p in progs] + cur
        used.append('chord loops')
    if replace and lr.get('bpm'):
        b = int(lr['bpm'])
        st['bpm'] = (max(40, b - 3), b + 3)
        used.append('tempo')
    return used


def _register_variant(styles, vid, base, label, lr):
    from .styles import POOLS, LABELS
    from . import genre_groups, drumkits, arrange, traits
    st = copy.deepcopy(styles[base])
    st['name'] = st.get('name') or base                 # genre-specific behaviour keeps following the original
    st['variant_of'] = base
    st['desc'] = f"Your variant of {LABELS.get(base, base)}, grooving like {lr.get('name') or 'your MIDI file'}: " \
        + (st.get('desc') or '')
    _merge(st, lr, replace=True)
    styles[vid] = st
    if base in POOLS:
        POOLS[vid] = copy.deepcopy(POOLS[base])
    LABELS[vid] = label
    genre_groups.GROUP_OF[vid] = genre_groups.group_of(base)
    for table in (drumkits.GENRE_KIT, arrange.GENRE_BUILD, traits.DECLARED):
        if base in table:
            table[vid] = table[base]


def apply_saved(styles):
    """At start-up: put everything you taught back into the genres."""
    d = _load()
    for g, items in (d.get('genres') or {}).items():
        if g in styles:
            _ORIG.setdefault(g, copy.deepcopy(styles[g]))
            for lr in items:
                _merge(styles[g], lr)
    for vid, v in (d.get('variants') or {}).items():
        if v.get('base') in styles and vid not in styles:
            try:
                _register_variant(styles, vid, v['base'], v.get('label') or vid, v.get('learned') or {})
            except Exception:
                pass


def teach(styles, genre, lr):
    """Add a learned file to a genre (now and on every start)."""
    if genre not in styles:
        raise ValueError('unknown genre')
    before = copy.deepcopy(styles[genre])
    used = _merge(styles[genre], lr)
    if not used:
        raise ValueError("nothing in this file fits that genre's parts (check the scale and the drum parts it uses)")
    _ORIG.setdefault(genre, before)
    d = _load()
    d.setdefault('genres', {}).setdefault(genre, []).append(lr)
    _save(d)
    return used


def make_variant(styles, base, label, lr):
    """Save a new genre: the base genre, but grooving like this file."""
    if base not in styles:
        raise ValueError('unknown genre')
    slug = ''.join(c if c.isalnum() else '_' for c in (label or 'my genre').lower()).strip('_')[:40] or 'my_genre'
    vid = 'my_' + slug
    i = 2
    while vid in styles:
        vid = f'my_{slug}_{i}'
        i += 1
    _register_variant(styles, vid, base, label or vid, lr)
    d = _load()
    d.setdefault('variants', {})[vid] = dict(base=base, label=label or vid, learned=lr)
    _save(d)
    return vid


def listing():
    d = _load()
    return dict(genres={g: [x.get('name') for x in v] for g, v in (d.get('genres') or {}).items()},
                variants={k: dict(base=v.get('base'), label=v.get('label')) for k, v in (d.get('variants') or {}).items()})


def forget(styles, genre=None, variant=None):
    """Forget what was taught to a genre (it goes back to how it was), or delete one of your variants."""
    d = _load()
    if genre:
        (d.get('genres') or {}).pop(genre, None)
        if genre in _ORIG:
            styles[genre] = _ORIG.pop(genre)
    if variant and variant in (d.get('variants') or {}):
        d['variants'].pop(variant)
        styles.pop(variant, None)
    _save(d)
    return listing()
