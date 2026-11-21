"""Extreme metal song writing (1.96): breakdowns that are never the same, and song forms written fresh for every song.

Measured from the reference records (only the numbers are kept, never the audio):

  slam / brutal deathcore (4 reference tracks)
      85-200 s songs at about -5.5 LUFS; 65-85 % of the time a wall of blasts and double kick, slam grooves 8-23 %,
      breakdowns 8-17 % in short bursts (3-15 s). Every breakdown in a song sits on its own pulse (one hit every
      0.3 ... 1.3 s), and the references pile them up toward the end of a song.
  cybergrind (12 reference tracks)
      42-98 s songs at about -10 LUFS, built on ~125 BPM: mostly breakdowns (24-67 %) and grooves, blasts at most
      15 %, full stops and near-silences in the middle of songs (up to 22 % of windows), and constant switching
      between half, normal and double time (pulses of 0.24 / 0.48 / 0.96 s).

A section is (name, bars, layers, opts) like every form in styles.FORMS. The opts used here:
  drums      {drum: [pattern]}   16 steps per bar, or 32 / 64 for a 2- / 4-bar phrase
  riffs      [pattern]           the guitar (and bass) part, same grid; kick_riff locks the kick to every guitar hit
  tempo      factor              the section's tempo against the song's (a slam at 0.5, a blast at 2.0)
"""
import random

# riff letters (figures.gen_riff): p palm-muted chug, X / x ringing power chord, b b2, m minor 3rd, q 4th, f tritone,
# g 5th, n b7, o octave, '-' hold, '.' rest
PALETTES = {
    'root': 'p',
    'b2': 'pppb',                  # the half-step 'slam' rub
    'tritone': 'pppf',
    'minor': 'pppm',
    'squeal': 'pppbo',             # pinch-squeal climbs to the octave
    'dissonant': 'ppbf',
}

KINDS = ['chug', 'slam', 'stop', 'triplet', 'beatdown', 'gallop', 'drag', 'squeal']


def _place(rng, steps, cells):
    """A phrase of `steps` 16ths from rhythm cells (lists of (char, length))."""
    out = []
    while len(out) < steps:
        for c in rng.choice(cells):
            out.append(c)
    return ''.join(out[:steps])


def _notes(rng, pat, palette):
    """Swap some chugs for the palette's riff notes (never the first hit of a bar: the downbeat stays the root)."""
    letters = PALETTES[palette]
    s = list(pat)
    for i, c in enumerate(s):
        if c == 'p' and i % 16 != 0 and rng.random() < 0.25:
            s[i] = rng.choice(letters)
    return ''.join(s)


def _ending(rng, pat, bars):
    """The last bar of a breakdown phrase answers the others: a ringing chord, a squeal, or a hole."""
    last = (bars - 1) * 16
    end = rng.choice(['X-------........', 'p.p.p.p.X-------', 'pppp....b-------', '........X-----..', 'X---X---X---X---',
                      'p..p..p.o-------', 'X-..X-..X-.X-...'])
    return pat[:last] + end


def breakdown(rng, used=None, kind=None, base_bars=8):
    """One breakdown section's opts and its bars. `used` holds the signatures of the song's breakdowns so far: the new
    one is never a repeat of any of them (different rhythm, tempo, snare or kind)."""
    used = used if used is not None else set()
    for _ in range(60):
        fresh = [x for x in KINDS if x not in {u[0] for u in used}] or KINDS
        k = kind or rng.choice(fresh)                               # a kind the song hasn't had yet, while there is one
        bars = rng.choice([2, 4])                                 # the phrase that repeats inside the section
        steps = bars * 16
        tempo = 1.0
        snare = ('........X.......' * bars)
        cym = 'x...x...x...x...' * bars
        hat = None
        palette = rng.choice(list(PALETTES))
        if k == 'chug':
            pat = _place(rng, steps, [['p', 'p', '.'], ['p', '.', '.'], ['p', 'p', '.', '.'], ['p', '.', '.', '.'],
                                      ['p', 'p', 'p', '.'], ['.', '.'], ['X', '-', '-', '.']])
            tempo = rng.choice([1.0, 1.0, 0.75])
        elif k == 'slam':                                          # slow groove over rolling double kick
            pat = _place(rng, steps, [['p', 'p', '.', 'p'], ['p', '.', 'p', 'p'], ['b', '-', '.', '.'], ['p', 'p', 'p', 'p'],
                                      ['X', '-', '-', '-'], ['p', '.', '.', 'p']])
            tempo = rng.choice([0.5, 0.5, 0.667])
            palette = rng.choice(['b2', 'squeal', 'dissonant'])
            cym = 'x.x.x.x.x.x.x.x.' * bars
        elif k == 'stop':                                          # stop-start: hits and silence
            pat = _place(rng, steps, [['X', '-', '.', '.', '.', '.', '.', '.'], ['p', '.', 'p', '.', '.', '.', '.', '.'],
                                      ['X', '-', '-', '-', '.', '.', '.', '.'], ['.', '.', '.', '.'], ['p', 'p', '.', '.']])
            tempo = rng.choice([1.0, 0.75])
            cym = ''.join('x' if c in 'Xpbmqfgno' else '.' for c in pat)
            snare = ('........X.......' * bars) if rng.random() < 0.5 else ('.' * steps)
        elif k == 'triplet':                                       # groups of three across the 4/4 bar
            unit = rng.choice(['p..', 'pp.', 'p.p', 'X-.'])
            pat = (unit * (steps // 3 + 1))[:steps]
            tempo = rng.choice([1.0, 0.75])
            cym = 'x..' * (steps // 3 + 1)
            cym = cym[:steps]
        elif k == 'beatdown':                                      # quarter-note hits, crashes on every one
            pat = _place(rng, steps, [['p', '.', '.', '.'], ['X', '-', '.', '.'], ['p', '.', 'p', '.'], ['.', '.', '.', '.']])
            tempo = rng.choice([0.5, 0.667, 0.75])
            snare = ('....X.......X...' * bars) if rng.random() < 0.4 else snare
        elif k == 'gallop':
            pat = _place(rng, steps, [['p', '.', 'p', 'p'], ['p', 'p', '.', 'p'], ['p', '.', '.', '.'], ['X', '-', '-', '.']])
            tempo = rng.choice([1.0, 0.75])
            hat = 'x.x.x.x.x.x.x.x.' * bars
        elif k == 'drag':                                          # crawling, very slow, long notes
            pat = _place(rng, steps, [['X', '-', '-', '-', '-', '-', '.', '.'], ['p', '.', 'p', '.'], ['b', '-', '-', '-'],
                                      ['.', '.', '.', '.']])
            tempo = rng.choice([0.4, 0.5])
            palette = rng.choice(['b2', 'dissonant', 'tritone'])
            snare = '........X.......' * bars
        else:                                                      # 'squeal': chugs climbing into pinch squeals
            pat = _place(rng, steps, [['p', 'p', '.', 'p'], ['p', '.', 'p', '.'], ['o', '-', '.', '.'], ['b', '-', '.', '.']])
            palette = 'squeal'
            tempo = rng.choice([0.75, 1.0])
        if not pat.strip('.-') or pat[0] in '.-':
            pat = 'p' + pat[1:]
        pat = _notes(rng, pat, palette)
        if bars >= 2 and rng.random() < 0.75:
            pat = _ending(rng, pat, bars)
        if rng.random() < 0.3:                                     # a ghost / double on the snare's beat
            snare = snare[:-6] + 'x.....' if rng.random() < 0.5 else snare
        sig = (k, pat, round(tempo, 3), snare)
        if sig in used or any(s[1] == pat for s in used):
            continue
        used.add(sig)
        drums = dict(snare=[snare], crash=[cym], chat=[hat or ('.' * steps)])
        sec_bars = max(bars * 2, int(round(base_bars / bars)) * bars)
        return dict(drums=drums, riffs=[pat], kick_riff=True, tempo=tempo, breakdown=k), sec_bars
    raise RuntimeError('could not write a new breakdown')       # (60 tries never all collide in practice)


# ------------------------------------------------------------------ the other sections
def blast(rng, kind=None):
    k = kind or rng.choice(['hammer', 'traditional', 'bomb', 'skank', 'gravity'])
    kick = {'hammer': 'XXXXXXXXXXXXXXXX', 'traditional': 'X.X.X.X.X.X.X.X.', 'bomb': 'XXXXXXXXXXXXXXXX',
            'skank': 'X...X...X...X...', 'gravity': 'XXXXXXXXXXXXXXXX'}[k]
    snare = {'hammer': 'x.x.x.x.x.x.x.x.', 'traditional': '.x.x.x.x.x.x.x.x', 'bomb': 'x.x.x.x.x.x.x.x.',
             'skank': '..x...x...x...x.', 'gravity': '....X.......X...'}[k]
    crash = rng.choice(['x...x...x...x...', 'x.......x.......', 'x.x.x.x.x.x.x.x.'])
    riff = rng.choice(['pppppppppppppppp', 'p.ppp.ppp.ppp.pp', 'ppbpppbpppfpppbp', 'pppmpppmppppppfp', 'pmpbpmpbpgpfpmpb',
                       'ppppX-ppppm-ppb-', 'pp.pp.ppX-pp.pp.'])
    return dict(drums=dict(kick=[kick], snare=[snare], crash=[crash], chat=['x.x.x.x.x.x.x.x.']), riffs=[riff], blast=k)


def groove(rng):
    """Mid-tempo slam / thrash groove: a two-step or bounce under a chugging riff."""
    kick = rng.choice(['X.X.X.X.X.X.X.X.', 'XX..XX..X.X.XX..', 'X..X..X.X..X..X.', 'XXXXXXXX........', 'X.XXX.XXX.XXX.XX'])
    snare = rng.choice(['....X.......X...', '..x...x...x...x.', '........X.......'])
    riff = rng.choice(['pp.pp.p.p.pp.p..', 'p.pp.pp.ppb-p.p.', 'pppp..pppp..p.p.', 'p.p.ppp.p.p.ppf-', 'ppm-ppb-ppm-pf-.',
                       'pp..pp..p.p.ppp.'])
    return dict(drums=dict(kick=[kick], snare=[snare], crash=['x...x...x...x...'], chat=['x.x.x.x.x.x.x.x.']), riffs=[riff],
                kick_riff=rng.random() < 0.4)


def stop(rng):
    """A full stop: one hit, then (near) silence - a breath before the next part."""
    return dict(drums=dict(kick=['X...............'], snare=['X...............'], crash=['x...............'],
                           chat=['................']), riffs=[rng.choice(['X---------------', 'p...............', 'b---------------'])])


# ------------------------------------------------------------------ whole songs
ALL = {'kick', 'snare', 'top', 'bass', 'chords'}


def slam_form(rng):
    """Slam / brutal deathcore: walls of blasts and double kick, slam grooves, and breakdowns that pile up toward the
    end - every breakdown different. ~85-200 s."""
    used = set()
    form = []
    opening = rng.choice(['breakdown', 'blast', 'feedback', 'groove'])
    if opening == 'feedback':
        form.append(('intro', 2, {'chords', 'fx'}, dict(stop(rng), crash=True)))
        opening = rng.choice(['blast', 'breakdown'])
    if opening == 'breakdown':
        o, n = breakdown(rng, used, base_bars=4)
        form.append(('breakdown', n, ALL, o))
    elif opening == 'groove':
        form.append(('groove', 4, ALL, groove(rng)))
    n_parts = rng.randint(6, 11)
    late_heavy = rng.random() < 0.6                    # references: breakdowns stack up near the end
    n_bd = 0
    for i in range(n_parts):
        pos = i / max(1, n_parts - 1)
        p_bd = (0.04 + 0.26 * pos) if late_heavy else 0.14
        if n_bd >= 3:
            p_bd = 0.0
        r = rng.random()
        if r < p_bd:
            n_bd += 1
            o, n = breakdown(rng, used, base_bars=rng.choice([2, 4]))
            form.append(('breakdown', n, ALL, o))
        elif r < p_bd + 0.2:
            form.append(('groove', rng.choice([4, 8]), ALL, groove(rng)))
        elif r < p_bd + 0.25:
            form.append(('stop', 1, ALL, stop(rng)))
        else:
            form.append(('blast', rng.choice([4, 8, 8, 12]), ALL | {'lead'} if rng.random() < 0.3 else ALL, blast(rng)))
    o, n = breakdown(rng, used, kind=rng.choice(['slam', 'drag', 'beatdown']), base_bars=4)   # the heaviest one last
    form.append(('breakdown', n, ALL, dict(o, crash=True)))
    if rng.random() < 0.5:
        form.append(('outro', 2, {'chords', 'bass', 'fx'}, dict(stop(rng), cad=False)))
    return _no_repeats(form)


def cyber_form(rng):
    """Cybergrind: ~45-100 s, mostly breakdowns and grooves around ~125 BPM, short double-time
    blasts, full stops and quiet electronic moments, never the same order twice."""
    used = set()
    form = []
    start = rng.choice(['cold', 'chip', 'blast', 'breakdown', 'sample'])
    if start == 'chip':
        form.append(('intro', rng.choice([2, 4]), {'arp', 'lead', 'fx'}, {'tempo': rng.choice([1.0, 2.0])}))
    elif start == 'sample':
        form.append(('intro', 2, {'fx', 'chords'}, dict(stop(rng))))
    elif start == 'blast':
        form.append(('blast', rng.choice([4, 8]), ALL, dict(blast(rng), tempo=2.0, crash=True)))
    elif start == 'breakdown':
        o, n = breakdown(rng, used, base_bars=4)
        form.append(('breakdown', n, ALL, o))
    n_parts = rng.randint(5, 9)
    for _ in range(n_parts):
        r = rng.random()
        if r < 0.3:
            o, n = breakdown(rng, used, base_bars=rng.choice([2, 2, 4]))
            form.append(('breakdown', n, ALL, o))
        elif r < 0.72:
            form.append(('groove', rng.choice([4, 4, 8]), ALL | ({'arp'} if rng.random() < 0.3 else set()),
                         dict(groove(rng), tempo=rng.choice([1.0, 1.0, 2.0]))))
        elif r < 0.84:
            form.append(('blast', rng.choice([2, 4, 4]), ALL | ({'lead'} if rng.random() < 0.4 else set()),
                         dict(blast(rng), tempo=2.0)))
        elif r < 0.93:
            form.append(('stop', 1, ALL, stop(rng)))
        else:                                                    # a quiet electronic moment, then straight back in
            form.append(('interlude', rng.choice([1, 2]), {'arp', 'lead', 'fx'}, {'tempo': 1.0}))
    while sum(1 for sec in form if sec[0] == 'breakdown') < 2:   # every cybergrind song has its breakdowns
        o, n = breakdown(rng, used, base_bars=rng.choice([2, 4]))
        form.insert(rng.randint(1, max(1, len(form))), ('breakdown', n, ALL, o))
    end = rng.choice(['breakdown', 'blast', 'stop', 'chip'])
    if end == 'breakdown':
        o, n = breakdown(rng, used, kind=rng.choice(['slam', 'drag', 'beatdown', 'stop']), base_bars=4)
        form.append(('breakdown', n, ALL, dict(o, crash=True)))
    elif end == 'blast':
        form.append(('blast', 4, ALL, dict(blast(rng), tempo=2.0)))
        form.append(('stop', 1, ALL, stop(rng)))
    elif end == 'stop':
        form.append(('stop', 1, ALL, stop(rng)))
    else:
        form.append(('outro', 2, {'arp', 'lead', 'fx'}, {}))
    return _no_repeats(form)


def _no_repeats(form):
    """Two blasts or grooves in a row merge into one longer section; stops never come twice in a row."""
    out = []
    for sec in form:
        if out and sec[0] == out[-1][0] and sec[0] in ('stop',):
            continue
        out.append(sec)
    return out


FORM_GEN = {'slam': slam_form, 'cyber': cyber_form}


def make_form(name, seed, style):
    return FORM_GEN[name](random.Random(f'{seed}-{style}-grind-form'))


def breakdown_signatures(form):
    """(kind, riff, tempo) of every breakdown in a form - for tests and the song's insights."""
    return [(o.get('breakdown'), o['riffs'][0], o.get('tempo', 1.0)) for (n, b, l, o) in form if n == 'breakdown']
