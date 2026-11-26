"""(2.27) The song's theme, told as a story - what makes a melody memorable across a whole track, not just per section.

- theme_reprise: the hook (the first two bars of the lead in the first big section) comes back where a listener
  expects to hear it again:
    foreshadow - its opening notes, soft, at the end of a long intro (a hint before it arrives);
    breakdown  - in the first breakdown / bridge it's played at half speed (augmentation: every note twice as long),
                 the emotional restatement of the theme over the open pads;
    farewell   - its first bar once more, soft, near the end of the outro.
- final_lift: the last big section is bigger than the first - the lead gets a second voice a diatonic third above
  for its second half (a harmony line), on top of whatever the drop / chorus already does.
Both stay in the key, never pile onto notes the lead is already playing there, and are skipped for through-composed
scores, exact forms and Development: off.
"""
import random

from .develop import step

BIG = ('drop', 'chorus', 'hook', 'main', 'theme', 'peak', 'climax', 'refrain', 'B')
BREAKS = ('break', 'breakdown', 'bridge', 'calm', 'interlude')


def _on(st, opts):
    return not (st.get('composer') or st.get('exact_form') or st.get('no_theme')
                or (getattr(opts, 'development', 'auto') or 'auto') == 'off')


def _hook(evs, sections):
    big = next((s for s in sections if (s.get('opts') or {}).get('drop') or s['name'] in BIG), None)
    if not big:
        return None, None
    b0 = big['bar'] * 4
    notes = sorted((e for e in evs if e.track == 'lead' and e.midi is not None and b0 <= e.beat < b0 + 8),
                   key=lambda e: e.beat)
    return (notes if len(notes) >= 3 else None), big


def theme_reprise(evs, sections, st, opts, key):
    """Returns the list of reprises placed (for the song info)."""
    if not _on(st, opts):
        return []
    hook, big = _hook(evs, sections)
    if not hook:
        return []
    rnd = random.Random(f'{opts.seed}-theme-{st.get("name")}')
    h0 = big['bar'] * 4
    done = []
    vmax = max(e.vel for e in hook)
    # foreshadow: the opening 3-4 notes at the end of a long intro, if the lead doesn't play there
    intro = sections[0] if sections and sections[0]['name'] == 'intro' else None
    if intro and intro['bars'] >= 8 and rnd.random() < 0.6:
        a, b = intro['bar'] * 4, (intro['bar'] + intro['bars']) * 4
        if not any(e.track == 'lead' and a <= e.beat < b for e in evs):
            head = [e for e in hook if e.beat < h0 + 4][:4]
            start = b - 8
            for e in head:
                evs.append(e.copy(beat=start + (e.beat - h0), vel=min(e.vel, vmax) * 0.5))
            done.append('intro foreshadows the theme')
    # breakdown: the theme at half speed
    brk = next((s for s in sections if s['name'] in BREAKS and s['bars'] >= 8 and s['bar'] * 4 > h0), None)
    if brk and rnd.random() < 0.7:
        a = brk['bar'] * 4
        b = a + 16
        if b <= (brk['bar'] + brk['bars']) * 4:
            evs[:] = [e for e in evs if not (e.track == 'lead' and a <= e.beat < b)]
            for e in hook:
                evs.append(e.copy(beat=a + (e.beat - h0) * 2, dur=min(e.dur * 2, 8.0), vel=e.vel * 0.8))
            done.append('breakdown restates the theme at half speed')
    # farewell: the first bar near the end of the outro
    out = sections[-1] if sections and sections[-1]['name'] == 'outro' else None
    if out and out['bars'] >= 8 and rnd.random() < 0.5:
        a = (out['bar'] + out['bars']) * 4 - 12
        if not any(e.track == 'lead' and a <= e.beat < a + 4 for e in evs):
            for e in hook:
                if e.beat < h0 + 4:
                    evs.append(e.copy(beat=a + (e.beat - h0), vel=e.vel * 0.45))
            done.append('outro says goodbye with the theme')
    return done


def final_lift(evs, sections, st, opts, key):
    """The last big section gets a harmony a third above the lead for its second half. Returns True if added."""
    if not _on(st, opts):
        return False
    bigs = [s for s in sections if (s.get('opts') or {}).get('drop') or s['name'] in BIG]
    if len(bigs) < 2:
        return False
    rnd = random.Random(f'{opts.seed}-lift-{st.get("name")}')
    if rnd.random() < 0.4:
        return False
    last = bigs[-1]
    a, b = last['bar'] * 4, (last['bar'] + last['bars']) * 4
    half = a + (b - a) / 2
    lead = [e for e in evs if e.track == 'lead' and e.midi is not None and half <= e.beat < b]
    if len(lead) < 4 or max(e.midi for e in lead) + 4 > 96:
        return False
    from .theory import MAQAM_QUARTER
    if MAQAM_QUARTER.get(getattr(key, 'scale_name', '')) or any(getattr(e, 'bend', None) for e in lead):
        return False                                     # ornamented / quarter-tone melodies stay one voice
    for e in lead:
        h = e.copy(midi=step(key, e.midi, 2), vel=e.vel * 0.72)
        h.bend = None
        evs.append(h)
    return True
