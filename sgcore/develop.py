"""(2.14) Making the musical decisions inside a song feel intentional rather than independent random choices.

- develop_melody: motivic development. The lead's phrases are no longer stated identically every time: the
  answering (second) phrase of each pair develops the first one - it cadences home, sequences its motif a step up,
  fragments it (the opening cell, echoed), or displaces it rhythmically; later hook sections get a different
  development than the first, and the very last hook can climb to a high point. Character traits steer it
  (variation: low / progressive / theme and variations; melody: minimal motivic, call and response ...).
- humanize_parts: per-part performance profiles. Played instruments (keys, guitars, winds, bowed strings, mallets,
  bass guitar) get their own velocity spread, note-length variation and a dynamic arc over each four-bar phrase;
  synths and drum machines stay nearly exact. The render's timing looseness is scaled per part the same way.
- layer_entries: density that changes which parts play, not only how loud: in the first long section a few
  supporting parts (pad, arp, counter-line) come in one at a time instead of all at once, and the bar before a
  big section thins out for a breath - unless the genre's layout already does this itself.
"""
import math
import random

HOOKS = ('drop', 'chorus', 'hook', 'main', 'theme', 'peak')
LIVE_FAMILIES = ('keys', 'guitar', 'winds', 'mallets')
LIVE_BASS = ('ebass', 'upright', 'tuba', 'fretless', 'slapbass', 'acbass')


def _pcs(key):
    return sorted({(key.root + s) % 12 for s in key.scale})


def step(key, midi, n):
    """midi moved n steps along the key's scale (snapped into the scale first)."""
    pcs = _pcs(key)
    m = int(midi)
    while m % 12 not in pcs:
        m -= 1
    for _ in range(abs(n)):
        m += 1 if n > 0 else -1
        while m % 12 not in pcs:
            m += 1 if n > 0 else -1
    return m


def _amount(st, opts):
    from . import traits as _tr
    tr = _tr.wanted(opts, st.get('name') or opts.style)
    v = {'low': 0.25, 'sectional': 0.55, 'progressive': 0.85, 'theme_and_variations': 0.95, 'switchup': 0.7}.get(tr.get('variation'))
    if v is None:
        v = {'minimal_motivic': 0.8, 'call_and_response': 0.75, 'long_lyrical': 0.6, 'rhythmic_stabs': 0.4}.get(tr.get('melody'), 0.6)
    return v, tr


def develop_melody(evs, sections, st, opts, key, tracks):
    """Second phrases answer and develop the first; repeated hook sections develop differently. Returns a count."""
    if (getattr(opts, 'development', 'auto') or 'auto') == 'off' or st.get('composer') or 'lead' not in tracks:
        return 0
    from .theory import MAQAM_QUARTER
    if key.scale_name in MAQAM_QUARTER or any(e.track == 'lead' and e.bend for e in evs):
        return 0                                          # maqam / raga lines keep their own ornamented shapes
    amt, tr = _amount(st, opts)
    rnd = random.Random(f'{opts.seed}-develop-{st.get("name")}')
    minimal = tr.get('melody') == 'minimal_motivic'
    moves = ['answer', 'sequence', 'fragment', 'displace'] if not minimal else ['fragment', 'fragment', 'sequence', 'answer']
    hook_seen = 0
    last_hook = max((i for i, s in enumerate(sections) if s['name'] in HOOKS or s['opts'].get('drop')), default=-1)
    done = 0
    by_bar = {}
    for e in evs:
        if e.track == 'lead' and e.midi is not None:
            by_bar.setdefault(int(e.beat // 4), []).append(e)
    for si, sec in enumerate(sections):
        if 'lead' not in sec['layers'] or sec['bars'] < 8:
            continue
        is_hook = sec['name'] in HOOKS or sec['opts'].get('drop')
        hook_seen += 1 if is_hook else 0
        later = is_hook and hook_seen >= 2
        for p0 in range(sec['bar'], sec['bar'] + sec['bars'] - 7, 8):      # pairs of 4-bar phrases
            b = p0 + 7                                    # the last bar of the answering phrase
            if sec['opts'].get('cad') and b >= sec['bar'] + sec['bars'] - 1:
                continue                                  # a written cadence (classical forms) stays as it is
            notes = sorted(by_bar.get(b, []), key=lambda e: e.beat)
            if not notes or rnd.random() > amt * (1.15 if later else 1.0):
                continue
            mv = rnd.choice(moves)
            if mv == 'answer':                            # the answer comes home: last note on the tonic, held
                e = notes[-1]
                tonic = [m for m in range(e.midi - 7, e.midi + 8) if (m - key.root) % 12 == 0]
                if tonic:
                    e.midi = min(tonic, key=lambda m: abs(m - e.midi))
                    e.dur = max(e.dur, (b + 1) * 4 - e.beat - 0.15)
            elif mv == 'sequence':                        # the phrase's second bar, a scale step higher
                src = sorted(by_bar.get(p0 + 1, []), key=lambda x: x.beat)
                if not src:
                    continue
                for e in notes:
                    evs.remove(e)
                by_bar[b] = []
                for s in src:
                    n = s.copy(beat=s.beat + (b - p0 - 1) * 4, midi=step(key, s.midi, 1))
                    evs.append(n)
                    by_bar[b].append(n)
            elif mv == 'fragment':                        # the opening cell, echoed twice - the second a step up
                cell = [x for x in sorted(by_bar.get(p0 + 4, []) or by_bar.get(p0, []), key=lambda x: x.beat)
                        if x.beat % 4 < 2][:4]
                if len(cell) < 2:
                    continue
                for e in notes:
                    evs.remove(e)
                by_bar[b] = []
                base = int(cell[0].beat // 4) * 4
                for k in (0, 1):
                    for s in cell:
                        off = s.beat - base
                        n = s.copy(beat=b * 4 + 2 * k + off, dur=min(s.dur, 2 - off - 0.05), midi=step(key, s.midi, k))
                        if n.dur > 0.05:
                            evs.append(n)
                            by_bar[b].append(n)
            elif mv == 'displace':                        # the same notes, an 8th later: the phrase leans forward
                for e in notes:
                    if e.beat + 0.5 < (b + 1) * 4 - 0.1:
                        e.beat += 0.5
                        e.dur = min(e.dur, (b + 1) * 4 - e.beat - 0.05)
                    else:
                        evs.remove(e)
                        by_bar[b].remove(e)
            done += 1
        if si == last_hook and hook_seen >= 2 and rnd.random() < amt:    # the last hook climbs to its high point
            b = sec['bar'] + sec['bars'] - 3
            top = max((e for k in (b - 1, b) for e in by_bar.get(k, [])), key=lambda e: e.midi, default=None)
            if top is not None:
                top.midi = step(key, top.midi, 2)
                top.vel = min(1.0, top.vel * 1.08)
                done += 1
    return done


LIVE_NAMES = ('strings', 'violin', 'viola', 'cello', 'celli', 'spiccato', 'tremolo', 'pizz', 'choir', 'harp', 'brass', 'horn',
              'contrabass', 'humchoir', 'accordion', 'harmonica', 'pedalsteel', 'banjo', 'fiddle', 'mandolin', 'ukulele', 'sitar',
              'koto', 'kora', 'oud', 'bouzouki', 'cittern', 'clarsach', 'erhu', 'shakuhachi', 'tinwhistle')


def _profile(t, cat):
    from .compose import inst_family
    inst = str(t.get('inst', ''))
    base = inst.split(':', 1)[-1]
    if t['layer'] in ('kick', 'snare', 'top'):
        return None
    fam = inst_family(inst)
    if inst.startswith(('real:', 'sf:')) or base in LIVE_BASS or any(w in base for w in LIVE_NAMES):
        return 'live'
    if t['layer'] == 'bass':
        return 'live' if cat != 'Electronic' and fam in LIVE_FAMILIES + ('bass',) and not base.startswith(('808', 'saw', 'sine', 'sub')) \
            else 'machine'
    if fam in LIVE_FAMILIES or (cat in ('Orchestral', 'Classic') and fam != 'synth'):
        return 'live'
    return 'machine'


def humanize_parts(evs, tracks, st, opts):
    """Per-part performance: velocity spread, note lengths and a phrase-level dynamic arc for played instruments."""
    from . import traits as _tr
    tr = _tr.wanted(opts, st.get('name') or opts.style)
    feel = tr.get('feel')
    if feel == 'robotic' or float(getattr(opts, 'humanize', 1.0) or 0) <= 0:
        st['human_mult'] = {n: 0.0 for n in tracks}
        return 0
    k = {'loose_human': 1.6, 'drifting': 1.4, 'live_drums': 1.2, 'tight_swing': 0.6}.get(feel, 1.0) * \
        min(1.5, float(getattr(opts, 'humanize', 1.0) or 1.0))
    prof = {n: _profile(t, st.get('category')) for n, t in tracks.items()}
    st['human_mult'] = {n: (1.0 if p == 'live' else 0.35) for n, p in prof.items() if p}
    n = 0
    for e in evs:
        p = prof.get(e.track)
        if not p or e.midi is None:
            continue
        r = random.Random(hash((e.track, round(e.beat * 96), e.midi, opts.seed)) & 0xffffffff)
        if p == 'live':
            pos = (e.beat % 16) / 16.0                    # a four-bar phrase swells toward its middle and eases off
            arc = 0.93 + 0.1 * math.sin(math.pi * pos)
            e.vel = max(0.05, min(1.0, e.vel * arc * (1 + r.gauss(0, 0.05 * k))))
            if e.dur > 0.2:
                e.dur = max(0.05, e.dur * (1 - min(0.2, abs(r.gauss(0, 0.05 * k)))))   # (never longer: no overlaps)
        else:
            e.vel = max(0.05, min(1.0, e.vel * (1 + r.gauss(0, 0.012 * k))))
        n += 1
    return n


def layer_entries(evs, sections, st, opts, tracks):
    """The first long section brings its supporting parts in one at a time; the bar before a big section takes a
    breath. Skipped where the genre's own layout already stages its parts."""
    if st.get('composer') or st.get('exact_form') or (getattr(opts, 'development', 'auto') or 'auto') == 'off':
        return []
    if any(s['opts'].get('layer_in') or s['opts'].get('layer_out') for s in sections):
        return []
    from . import traits as _tr
    dens = _tr.wanted(opts, st.get('name') or opts.style).get('density')
    rnd = random.Random(f'{opts.seed}-entries-{st.get("name")}')
    moves = []
    support = [n for n, t in tracks.items() if t['layer'] in ('pad', 'arp') or n in ('counter', 'answer')]
    first = next((s for s in sections if s['bars'] >= 16 and s['name'] not in ('intro', 'outro')), None)
    if first and support and (dens in ('evolving', 'sparse') or rnd.random() < 0.55):
        order = [n for n in support if any(e.track == n and first['bar'] * 4 <= e.beat < (first['bar'] + 4) * 4 for e in evs)]
        rnd.shuffle(order)
        for i, name in enumerate(order[:3]):
            enter = (first['bar'] + 4 * (i + 1)) * 4      # one more part every four bars
            evs[:] = [e for e in evs if not (e.track == name and first['bar'] * 4 <= e.beat < enter)]
            moves.append(f'{name} enters at bar {enter // 4 + 1}')
    for i, s in enumerate(sections[1:], 1):               # a breath before a big section
        big = s['name'] in HOOKS or s['opts'].get('drop')
        prev = sections[i - 1]
        if not big or prev['opts'].get('build') or prev['bars'] < 4 or rnd.random() > (0.5 if dens != 'dense' else 0.2):
            continue
        b0, b1 = s['bar'] * 4 - 2, s['bar'] * 4           # the last two beats before it
        drop = [n for n, t in tracks.items() if t['layer'] in ('pad', 'arp', 'chords')]
        evs[:] = [e for e in evs if not (e.track in drop and b0 <= e.beat < b1)]
        for e in evs:
            if e.track in drop and e.beat < b0 < e.beat + e.dur:
                e.dur = b0 - e.beat
        moves.append(f'breath before bar {s["bar"] + 1}')
    return moves
