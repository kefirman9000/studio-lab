"""(1.94) Does a generated song behave like a real club record? Composes songs (no audio) and checks the things that
make house / trance / techno records work: phrasing, arrangement changes, the groove, the bassline, the hook, the
harmony and the energy shape. Run:  python tools/song_audit.py house 12   (genre, number of seeds)."""
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sgcore.compose import compose, Options  # noqa: E402

FAMILY = {'house': 'house', 'deep_house': 'house', 'tech_house': 'house', 'progressive_house': 'house', 'acid_house': 'house',
          'trance': 'trance', 'uplifting_trance': 'trance', 'progressive_trance': 'trance', 'classic_vocal_trance': 'trance',
          'techno': 'techno', 'melodic_techno': 'techno', 'minimal': 'techno', 'hard_techno': 'techno'}


def audit(song):
    st = song['st']
    fam = FAMILY.get(st.get('name'), 'house')
    tr = {t['name']: t for t in st['tracks']}
    role = {n: t['layer'] for n, t in tr.items()}
    ev = [e for e in song['events'] if e.midi is not None or role.get(e.track) in ('kick', 'snare', 'top')]
    secs = song['sections']
    total = sum(s['bars'] for s in secs)
    probs, notes = [], {}
    # ---- phrasing
    odd = [f"{s['name']}{s['bars']}" for s in secs if s['bars'] % 8 and not s['opts'].get('build')]
    if odd:
        probs.append(f'sections off the 8-bar grid: {odd}')
    # ---- arrangement: active tracks per 8-bar block
    blocks = defaultdict(set)
    for e in ev:
        blocks[int(e.beat // 32)].add(e.track)
    nb = (total + 7) // 8
    seq = [blocks.get(i, set()) for i in range(nb)]
    changes = [len(a ^ b) for a, b in zip(seq, seq[1:])]
    run = mx = 0
    for c in changes:
        run = run + 1 if c == 0 else 0
        mx = max(mx, run)
    if mx * 8 >= 32 and fam != 'techno':
        probs.append(f'{(mx + 1) * 8} bars with no element in or out')
    if mx * 8 >= 64:
        probs.append(f'{(mx + 1) * 8} bars with no element in or out (even for techno)')
    churn = sum(1 for c in changes if c >= 4)
    notes['changes/8bars'] = round(sum(1 for c in changes if c) / max(1, len(changes)), 2)
    # ---- groove: kick four-on-the-floor where the drums play
    kick = st.get('kick_track', 'kick')
    kb = Counter(int(e.beat // 4) for e in ev if e.track == kick)
    full = [b for b, c in kb.items() if c >= 4]
    gappy = [b for b, c in kb.items() if 0 < c < 4]
    notes['kick bars 4otf'] = f'{len(full)}/{len(kb)}'
    if kb and len(gappy) > 0.25 * len(kb):
        probs.append(f'kick not four-on-the-floor in {len(gappy)} of {len(kb)} bars')
    claps = [n for n, t in tr.items() if t['layer'] == 'snare']
    in_build = lambda b: any(x['opts'].get('build') and x['bar'] * 4 <= b < (x['bar'] + x['bars']) * 4 for x in secs)
    cb = [e.beat % 4 for e in ev if e.track in claps and not in_build(e.beat)]
    if cb:
        on24 = sum(1 for b in cb if abs(b - 1) < 0.01 or abs(b - 3) < 0.01) / len(cb)
        notes['clap on 2&4'] = round(on24, 2)
        if on24 < 0.6 and fam in ('house', 'trance'):
            probs.append(f'clap / snare only {on24:.0%} on 2 and 4')
    # ---- bass
    bass = [e for e in ev if role.get(e.track) == 'bass']
    if bass:
        off = sum(1 for e in bass if abs((e.beat % 1) - 0.5) < 0.01) / len(bass)
        onb = sum(1 for e in bass if abs(e.beat % 1) < 0.01) / len(bass)
        notes['bass offbeat / on-beat'] = f'{off:.2f} / {onb:.2f}'
        if fam == 'trance' and off < 0.3 and not any('roll' in str(tr.get('bass', {}).get('inst')) for _ in [0]):
            probs.append(f'trance bass only {off:.0%} on the off-beats (rolling / off-beat bass expected)')
    else:
        probs.append('no bassline')
    # ---- lead / hook
    lead = sorted([e for e in ev if e.track == 'lead'], key=lambda e: e.beat)
    drops = [s for s in secs if s['opts'].get('drop') or s['name'] in ('drop', 'chorus', 'B')]
    if fam in ('house', 'trance'):
        if not lead:
            probs.append('no lead / hook at all')
        else:
            dl = [e for e in lead if any(s['bar'] * 4 <= e.beat < (s['bar'] + s['bars']) * 4 for s in drops)]
            if drops and not dl:
                probs.append('no hook in the drops')
            # repetition: 2-bar (house) / 4-bar (trance) phrases repeating
            P = 8 if fam == 'house' else 16
            phr = defaultdict(list)
            for e in dl:
                phr[int(e.beat // P)].append((round(e.beat % P, 2), e.midi))
            pats = [tuple(v) for v in phr.values() if v]
            if pats:
                rep = 1 - len(set(pats)) / len(pats)
                notes['hook repeats'] = round(rep, 2)
                if rep < 0.3:
                    probs.append(f'hook hardly repeats ({rep:.0%} of {P // 4}-bar phrases are repeats)')
            span = 0                                      # the widest range inside one section (a later drop an octave
            for x in secs:                                # up is normal; one hook spanning 2+ octaves is not)
                v = [e.midi for e in lead if x['bar'] * 4 <= e.beat < (x['bar'] + x['bars']) * 4]
                if v:
                    span = max(span, max(v) - min(v))
            notes['lead range (one section)'] = span
            if span > 19:
                probs.append(f'lead range {span} semitones inside one section (a hook should stay within ~1.5 octaves)')
    if fam == 'techno':
        dens = len(lead) / max(1, total)
        notes['lead notes/bar'] = round(dens, 2)
        if dens > 3:
            probs.append(f'busy pop-style lead in techno ({dens:.1f} notes / bar)')
    # ---- harmony
    ch = defaultdict(set)
    for e in ev:
        if role.get(e.track) in ('chords', 'pad') and e.midi is not None:
            ch[int(e.beat // 4)].add(e.midi % 12)
    changes_h = sum(1 for b in ch if b - 1 in ch and ch[b] != ch[b - 1])
    notes['chord changes/bar'] = round(changes_h / max(1, len(ch)), 2)
    key = song['key']
    pcs = {(key.root + s) % 12 for s in key.scale}
    chord_at = defaultdict(set)                       # a note is in key if it's in the scale or in the chord playing then
    for e in ev:                                      # (a borrowed V with its raised 3rd is normal harmony, not a clash)
        if role.get(e.track) in ('chords', 'pad') and e.midi is not None:
            for bb in range(int(e.beat // 4), int((e.beat + max(e.dur, 0.01) - 1e-6) // 4) + 1):
                chord_at[bb].add(e.midi % 12)
    outk = [e for e in ev if e.midi is not None and role.get(e.track) not in ('kick', 'snare', 'top', 'chords', 'pad')
            and e.midi % 12 not in pcs and e.midi % 12 not in chord_at.get(int(e.beat // 4), set())]
    if outk:
        c = Counter(e.track for e in outk)
        notes['out-of-key notes'] = dict(c)
        if len(outk) > 0.02 * len([e for e in ev if e.midi is not None]):
            probs.append(f'{len(outk)} notes outside the key: {dict(c)}')
    # ---- energy shape
    brk = [s for s in secs if s['name'] in ('break', 'breakdown')]
    if fam in ('house', 'trance') and not brk:
        probs.append('no breakdown')
    if fam == 'trance' and brk and max(s['bars'] for s in brk) < 16:
        probs.append('trance breakdown shorter than 16 bars')
    lens = 60 / song['bpm'] * 4 * total
    notes['length'] = f'{int(lens // 60)}:{int(lens % 60):02d}'
    notes['form'] = ' '.join(f"{s['name']}{s['bars']}" for s in secs)
    return probs, notes, churn


if __name__ == '__main__':
    g = sys.argv[1] if len(sys.argv) > 1 else 'house'
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    allp = Counter()
    for k in range(1, n + 1):
        s = compose(Options(style=g, seed=k))
        p, notes, churn = audit(s)
        allp.update(x.split(' (')[0].split(':')[0] for x in p)
        print(f'--- seed {k}: {len(p)} problem(s)   ' + '  '.join(f'{a}={b}' for a, b in notes.items() if a != 'form'))
        print('    ', notes.get('form'), '| inst:', {t['name']: t['inst'] for t in s['st']['tracks'] if t['layer'] in ('bass', 'lead', 'chords', 'arp')})
        for x in p:
            print('     !', x)
    print('== summary', g, dict(allp.most_common()))
