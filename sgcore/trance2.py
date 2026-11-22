"""Euphoric trance (2.3): the parts that make uplifting trance more than fast music with supersaws.

  * the breakdown's melody moves to a piano (or a soft pluck): the main melody, played gently, before the climax
  * a lead HARMONY that follows the lead - chord-aware, not a fixed interval: for each lead note it takes the nearest
    chord tone a third above (else a sixth, else a fifth) in the chord sounding at that moment, so it never clashes.
    It is NOT on all the time: in the first climax it joins only the second half of each 4-bar phrase, in the
    extended climax it plays throughout - so the arrangement keeps growing.
"""
from .theory import Ev


def _chord_at(chord_evs, beat):
    """The pitch classes of the chord sounding at this beat (from the chords part)."""
    pcs = {e.midi % 12 for e in chord_evs if e.beat <= beat + 1e-6 < e.beat + max(e.dur, 0.25)}
    if not pcs:                                          # between stabs: the last chord that started before this beat
        prev = [e for e in chord_evs if e.beat <= beat + 1e-6]
        if prev:
            b0 = max(e.beat for e in prev)
            pcs = {e.midi % 12 for e in prev if abs(e.beat - b0) < 1e-6}
    return pcs


def harmony_note(m, pcs, scale=None):
    """The harmony above lead note m. On a chord tone: the chord tone a third above (3-4 semitones), else a sixth (8-9),
    else a fifth (7). On a passing note (not in the chord): the diatonic third above - two scale steps - like a second
    singer would. With nothing known, a sixth below (an inverted third)."""
    if m % 12 in pcs:
        for iv in (4, 3, 9, 8, 7):
            if (m + iv) % 12 in pcs:
                return m + iv
    if scale:
        steps = 0
        for iv in range(1, 6):
            if (m + iv) % 12 in scale:
                steps += 1
                if steps == 2:
                    return m + iv
    for iv in (4, 3, 9, 8, 7):
        if (m + iv) % 12 in pcs:
            return m + iv
    return m - 9 if pcs else m - 12


def euphoric_pass(evs, tracks, sections, st):
    if 'lead' not in tracks:
        return
    chord_evs = [e for e in evs if e.track == 'chords'] or [e for e in evs if e.track == 'pad']
    scale = {e.midi % 12 for e in chord_evs}             # the song's scale, from every chord it plays
    if len(scale) < 6:
        scale = None
    piano = 'lead_piano' in tracks
    harm = 'harm' in tracks
    new = []
    for sec in sections:
        b0, b1 = sec['bar'] * 4.0, (sec['bar'] + sec['bars']) * 4.0
        mode = sec['opts'].get('harm')
        if piano and sec['opts'].get('piano_lead'):     # the lead's doubles rest while the piano has the melody
            evs[:] = [e for e in evs if not (e.track.startswith('lead_') and e.track != 'lead_piano' and b0 <= e.beat < b1)]
        for e in evs:
            if e.track != 'lead' or not (b0 <= e.beat < b1):
                continue
            if piano and sec['opts'].get('piano_lead'):
                e.track = 'lead_piano'                    # the breakdown: the melody, gently, on the piano
                continue
        if not (harm and mode):
            continue
        lead = [e for e in evs if e.track == 'lead' and b0 <= e.beat < b1]
        if mode == 'half':                                # the answering half of each phrase (8 bars, else 4, else
            for span in (8, 4):                           # every other note) - whichever this melody actually fills
                pick = [e for e in lead if int((e.beat - b0) // 4) % span >= span // 2]
                if len(pick) >= max(4, len(lead) // 5):
                    break
            else:
                pick = lead[1::2]
        else:
            pick = lead
        for e in pick:
            new.append(Ev('harm', e.beat, e.dur, harmony_note(e.midi, _chord_at(chord_evs, e.beat), scale), e.vel * 0.82))
    evs.extend(new)
