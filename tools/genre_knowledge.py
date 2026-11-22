"""Writes docs/GENRE_KNOWLEDGE.txt: everything Studio Lab knows about every genre, for review.

    python tools/genre_knowledge.py

Per genre: name, id, group, description, tempo, scales and chord progressions (as roman numerals), swing / groove
feel, song structure (each section: bars and the parts playing), drum patterns, bass and chord / lead rhythms, every
part's sound and the alternatives it rotates through, sound hints, mix targets and special behaviours.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from sgcore import compose  # noqa: E402,F401  (imports the pools fully widened, as the app uses them)
from sgcore.styles import STYLES, LABELS, FORMS, POOLS, ABS_FORMS  # noqa: E402
from sgcore.compose import GENRE_COLORS  # noqa: E402
from sgcore.genre_groups import GROUPS  # noqa: E402
from sgcore.instruments import INSTRUMENT_INFO  # noqa: E402

ROMAN_MIN = ['i', 'ii°', 'III', 'iv', 'v', 'VI', 'VII']
ROMAN_MAJ = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']
PC = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
SPECIAL = {
    'scene_switch': 'switch-up scenes: one rhythm all song, every section gets new sounds and effects, bar-long '
                    'rises / sinks / alien moves',
    'euphoric': 'piano takes the melody in the breakdown; a chord-aware lead harmony joins at the climax',
    'filter_arc': 'filters open across builds', 'sc_arc': 'sidechain pumping grows toward the drops',
    'no_rotation': 'no per-section sound switching (the arrangement decides who plays)',
    'exact_pools': 'hand-picked sound lists (not widened)', 'trap_hats': 'trap hi-hat rolls',
    'fill': 'drum fills at phrase ends', 'ghosts': 'ghost notes on the snare',
    'polymeter': 'polymeter sequences (loops of 3/5/6/7 sixteenths against the bar)',
}


def sound(i):
    if not isinstance(i, str):
        return str(i)
    base = i.split(':', 1)[-1]
    lab = INSTRUMENT_INFO.get(i) or INSTRUMENT_INFO.get(base)
    return f'{i} ({lab})' if lab and lab.lower() != i.lower() else i


def roman(prog, scale):
    names = ROMAN_MAJ if scale in ('major', 'mixolydian', 'lydian') else ROMAN_MIN
    try:
        return ' - '.join(names[d % 7] for d in prog)
    except (TypeError, IndexError):
        return str(prog)


def progs_text(st):
    pr = st.get('progs')
    if not pr:
        return []
    if isinstance(pr, dict):
        return [f'{sc}: ' + ' | '.join(roman(p, sc) for p in ps[:6]) for sc, ps in pr.items()]
    sc = (st.get('scales') or ['minor'])[0]
    return [' | '.join(roman(p, sc) for p in pr[:8])]


def form_text(st):
    f = st.get('form')
    if st.get('form_gen'):
        return [f'generated fresh for every song ({st["form_gen"]})']
    sec = FORMS.get(f) if isinstance(f, str) else f
    if not sec:
        return [str(f)]
    out, tot = [], 0
    for s in sec:
        try:
            name, bars, layers, opts = s
        except ValueError:
            out.append(str(s))
            continue
        tot += bars
        flags = ', '.join(k for k, v in (opts or {}).items() if v)
        out.append(f'{name:<8} {bars:>3} bars  {", ".join(sorted(layers))}' + (f'   [{flags}]' if flags else ''))
    bpm = sum(st['bpm']) / 2
    out.append(f'= {tot} bars, about {int(tot * 4 * 60 / bpm // 60)}:{int(tot * 4 * 60 / bpm % 60):02d} at {bpm:.0f} BPM'
               + ('' if not st.get('forms') else f'   (other layouts it can pick: {", ".join(st["forms"])})'))
    if not st.get('form_gen') and not st.get('exact_form') and st.get('category') != 'Orchestral' \
            and len(st.get('forms') or []) < 2 and not (isinstance(f, str) and f in ABS_FORMS):
        out.append('(each song reshapes this layout: pre-choruses, a cold open, radio edit, double final chorus, '
                   'DJ intro, longer breakdown, fake-out, switch-up or third drop ... about 1 in 4 plays it as written)')
    return out


def genre(k):
    st = STYLES[k]
    L = [f'{LABELS.get(k, k)}   [{k}]', '-' * 72, st.get('desc', '')]
    L.append(f'Tempo: {st["bpm"][0]}-{st["bpm"][1]} BPM'
             + (f'   swing {st["swing"]:.2f}' if st.get('swing') and abs(st['swing'] - 0.5) > 0.005 else '')
             + (f'   groove feel: {st["groove"]}' if st.get('groove') else '')
             + (f'   meter {st["meter"]}' if st.get('meter') else ''))
    keys = f'   preferred roots: {", ".join(PC[r] for r in st["roots"])}' if st.get('roots') else ''
    L.append(f'Scales: {", ".join(st.get("scales") or [])}{keys}')
    if st.get('parent'):
        L.append(f'Built from: {LABELS.get(st["parent"], st["parent"])} [{st["parent"]}] (its own changes on top)')
    col = GENRE_COLORS.get(k)
    L.append('Harmony: ' + ', '.join(x for x in (
        f'{st.get("chord_size", 3)}-note chords', f'{st.get("voicing", "close")} voicing',
        f'chord colours {"/".join(col)}' if col else '',
        f'one chord every {st.get("chord_bars", 1)} bar' + ('s' if st.get('chord_bars', 1) != 1 else ''),
        'sometimes two bars per chord' if st.get('slow_chords') else '') if x))
    L.append('Melody: ' + ', '.join(x for x in (
        f'lead register octave {st.get("lead_oct", 5)}',
        f'repetition {st["repetition"]}' if st.get('repetition') is not None else 'repetition: genre default',
        f'{len(st.get("lead_rh") or [])} lead rhythms to choose from') if x))
    pt = progs_text(st)
    if pt:
        L.append('Chord progressions:')
        L += ['    ' + x for x in pt]
    L.append('Song structure:')
    L += ['    ' + x for x in form_text(st)]
    dr = st.get('drums') or {}
    if dr:
        L.append(f'Drums (16 steps per bar; kit: {st.get("kit", "-")}):')
        for name, pats in dr.items():
            pats = pats if isinstance(pats, list) else [pats]
            L.append(f'    {name:<8} ' + '   '.join(str(p) for p in pats[:3]) + ('  ...' if len(pats) > 3 else ''))
    for lab, key in (('Bass rhythm', 'bass'), ('Chord rhythm', 'chord_rh'), ('Lead rhythm', 'lead_rh')):
        v = st.get(key)
        if v and isinstance(v, list):
            L.append(f'{lab}: ' + '   '.join(str(p) for p in v[:4]) + ('  ...' if len(v) > 4 else ''))
    if st.get('arp'):
        a = st['arp']
        L.append(f'Arp: {a.get("mode", "")}, rate {a.get("rate", "")}, octave {a.get("oct", "")}')
    L.append('Parts and sounds (main sound -> alternatives it can rotate to):')
    pools = POOLS.get(k) or {}
    shown = set()
    for t in st.get('tracks', []):
        if t['layer'] in ('kick', 'snare', 'top'):
            continue
        alt = [x for x in pools.get(t['layer'], []) if x != t['inst']] if t['name'] == t['layer'] else []
        shown.add(t['layer'])
        fx = ', '.join(f'{x} {t[x]}' for x in ('rev', 'dly', 'sc', 'ott', 'wide', 'drive') if t.get(x))
        L.append(f'    {t["name"]:<11} {sound(t["inst"])}' + (f'   [{fx}]' if fx else ''))
        if alt:
            L.append(f'    {"":<11}   or: {", ".join(alt)}')
    drum_parts = [t['name'] for t in st.get('tracks', []) if t['layer'] in ('kick', 'snare', 'top')]
    if drum_parts:
        L.append(f'    drums       {", ".join(drum_parts)}')
    if st.get('gm_hint'):
        L.append(f'Sound hints: {st["gm_hint"]}')
    m = st.get('master') or {}
    mix = []
    if m.get('lufs'):
        mix.append(f'loudness {m["lufs"]} LUFS')
    if st.get('sc_depth'):
        mix.append(f'sidechain {st["sc_depth"]}')
    if st.get('reverb'):
        mix.append(f'reverb size {st["reverb"]}')
    for kk in ('low', 'air', 'width'):
        if m.get(kk):
            mix.append(f'{kk} {m[kk]}')
    if m.get('lofi'):
        mix.append('lo-fi master')
    if mix:
        L.append('Mix: ' + ', '.join(mix))
    sp = [v for kk, v in SPECIAL.items() if st.get(kk)]
    if sp:
        L.append('Special: ' + '; '.join(sp))
    return L + ['', '']


def main():
    ver = open(os.path.join(ROOT, 'VERSION')).read().strip()
    out = [f'STUDIO LAB - GENRE KNOWLEDGE  (version {ver}, {len(STYLES)} genres)', '',
           'How to read it:',
           '  Patterns are one bar: 16 steps (16th notes) in 4/4; 12 steps in 3/4, 6/8 and 12/8 (the genre shows its meter).',
           '  An empty pattern means the part rests in songs that pick it. "..." = more patterns than shown.',
           '  Drums: X = accent, x = hit, o = ghost note (soft), . = rest.',
           '  Bass: R = root, O = octave up, F = fifth, A = approach note into the next chord (a fifth, octave or step),',
           '        u / d = a half step above / below the root, 3 5 6 7 = boogie chord tones (3rd, 5th, 6th, flat 7th),',
           '        x = a plain hit on the root, - = hold, . = rest.',
           '  Chords / lead: x = a note starts, - = held, . = rest.',
           '  Chord progressions are scale degrees as roman numerals (minor: i ii° III iv v VI VII).',
           '  Song structure: each section, its length and which parts play; [flags] = what the section does',
           '  (drop, build, filter_in, layer_in/out, alt = variation, fade, gap = a drop-out ...).',
           '  Sounds: the main sound of each part, then the sounds it can switch to from song to song.', '']
    cats = {}
    for k, st in STYLES.items():
        cats.setdefault(st['category'], []).append(k)
    out += ['CONTENTS (search for a genre id in [brackets] to jump to it)', '']
    for cat in ('Electronic', 'Classic', 'Orchestral'):
        for g, members in GROUPS.get(cat, []):
            m = [k for k in members if k in STYLES and STYLES[k]['category'] == cat]
            if m:
                out.append(f'  {cat} > {g}: ' + ', '.join(f'{LABELS.get(k, k)} [{k}]' for k in m))
    out.append('')
    for cat in ('Electronic', 'Classic', 'Orchestral'):
        ids = cats.get(cat, [])
        out += ['=' * 72, f'{cat.upper()}  ({len(ids)} genres)', '=' * 72, '']
        seen = set()
        for g, members in GROUPS.get(cat, []):
            m = [k for k in members if k in STYLES and STYLES[k]['category'] == cat]
            if not m:
                continue
            seen |= set(m)
            out += ['#' * 72, f'# {g}  ({len(m)})', '#' * 72, '']
            for k in m:
                out += genre(k)
        rest = [k for k in ids if k not in seen]
        if rest:
            out += ['#' * 72, '# Other', '#' * 72, '']
            for k in rest:
                out += genre(k)
    path = os.path.join(ROOT, 'docs', 'GENRE_KNOWLEDGE.txt')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f'{len(STYLES)} genres -> {path}')


if __name__ == '__main__':
    main()
