"""(2.24) Learn from audio: what a genre can take from a recording (WAV / MP3 / FLAC ...), the same shape Learn from
MIDI returns, so it teaches a genre or becomes a ★ My genre exactly the same way.

From the audio (numpy / scipy only):
  tempo and key        analysis.analyze (spectral-flux tempo, chroma key profile)
  the beat grid        the bar phase where kicks land on 1 and snares on 2 and 4 - so step 1 of a pattern is the downbeat
  drum patterns        onsets in three bands per 16th step - kick (35-120 Hz), snare (body 150-300 Hz + crack 1.5-4 kHz,
                       minus what the kick explains) and hats (6-11 kHz) - then the bars that repeat most
  chord loops          per bar, the scale-degree triad that best matches the harmonic chroma (100-1500 Hz)
It can't hear which instrument plays what, so sounds aren't learned; it's built for music with a steady beat (4/4).
"""
import os

import numpy as np
from scipy import signal

from .analysis import analyze
from .midilearn import _top, _loops
from .theory import SCALES

SR = 22050
HOP = 256
STEPS = 16


def _band_onsets(S, f, lo, hi):
    band = (f >= lo) & (f < hi)
    e = np.log1p(S[band].sum(axis=0) * 50)
    d = np.maximum(np.diff(e, prepend=e[:1]), 0)
    return d - np.convolve(d, np.ones(9) / 9, mode='same') * 0.5


def _at(env, frames):
    """The strongest onset within one frame of each step position."""
    out = np.zeros(len(frames))
    for i, fr in enumerate(frames):
        a, b = max(0, fr - 1), min(len(env), fr + 2)
        out[i] = env[a:b].max() if b > a else 0.0
    return out


def _peaks(env):
    """Total strength of the onsets themselves (local maxima above a small floor)."""
    m = (env[1:-1] > env[:-2]) & (env[1:-1] >= env[2:]) & (env[1:-1] > 0.05 * env.max())
    return float(env[1:-1][m].sum())


def _rows(vals, nbars, thresh, accent):
    rows = []
    for b in range(nbars):
        v = vals[b * STEPS:(b + 1) * STEPS]
        rows.append(''.join('X' if x >= accent else ('x' if x >= thresh else '.') for x in v))
    return rows


def _triads(root, scale):
    iv = SCALES.get(scale) or SCALES['major']
    out = []
    for d in range(7):
        pcs = [(root + iv[(d + k) % 7] + 12 * ((d + k) // 7)) % 12 for k in (0, 2, 4)]
        t = np.zeros(12)
        t[pcs[0]], t[pcs[1]], t[pcs[2]] = 1.0, 0.8, 0.8
        out.append(t / np.linalg.norm(t))
    return out


def _key(x):
    """The scale (which 7 notes) from sustained, harmonic energy - long frames, a median over time so drum hits drop out,
    110-2000 Hz, bins near a semitone centre - then its tonic: the major root or its relative minor, whichever the bass
    sits on more. (Checked on 40 songs with known keys: right scale notes in 37, the reference analysis got 29.)"""
    f, _, Z = signal.stft(x, SR, nperseg=8192, noverlap=6144)
    P = signal.medfilt2d(np.abs(Z), kernel_size=(1, 9))
    def chroma(lo, hi):
        band = (f > lo) & (f < hi)
        midi = 69 + 12 * np.log2(f[band] / 440.0)
        near = np.abs(midi - np.round(midi)) < 0.3
        pc = np.mod(np.round(midi), 12).astype(int)
        ch = np.zeros(12)
        np.add.at(ch, pc[near], np.log1p(P[band][near] * 100).sum(axis=1))
        return ch / (ch.sum() + 1e-12)
    ch, low = chroma(100, 2000), chroma(40, 200)
    maj = SCALES['major']
    r = max(range(12), key=lambda q: sum(ch[(q + i) % 12] for i in maj))
    rm = (r + 9) % 12
    return (r, 'major') if low[r] + 0.5 * ch[r] >= low[rm] + 0.5 * ch[rm] else (rm, 'minor')


def _grid(full, step, swing):
    """Step positions (frames): straight 16ths, every second one pushed late by the swing."""
    pos = np.arange(0, len(full) - 2 - step, step)
    pos = pos + np.where(np.arange(len(pos)) % 2 == 1, swing * step, 0.0)
    return pos


def _fit(full, step):
    """The best 16th phase and swing for this tempo, and how well the onsets sit on that grid."""
    best = (-1.0, 0.0, 0.0)
    for ph in np.linspace(0, step, 8, endpoint=False):
        for sw in (0.0, 0.1, 0.2, 0.3):
            g = np.round(_grid(full, step, sw) + ph).astype(int)
            g = g[g < len(full)]
            sc = _at(full, g).mean()
            if sc > best[0]:
                best = (sc, ph, sw)
    return best


def learn(pcm, sr=SR, name=''):
    x = np.asarray(pcm, dtype=np.float64)
    if x.ndim > 1:
        x = x.mean(axis=0)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = x[:SR * 240]
    if len(x) < SR * 8:
        raise ValueError('that recording is too short to learn from (need at least 8 seconds)')
    base = analyze(x, SR)
    root, scale = _key(x)
    f, _, Z = signal.stft(x, SR, nperseg=1024, noverlap=1024 - HOP)
    S = np.abs(Z) ** 2
    fps = SR / HOP
    def norm(e):
        pos = e[e > 0]
        return e / (np.percentile(pos, 95) if len(pos) else 1.0)
    kick = norm(_band_onsets(S, f, 35, 120))
    hats = norm(_band_onsets(S, f, 6000, 11000))
    snare = np.maximum(norm(_band_onsets(S, f, 1000, 5000)) - 0.5 * hats - 0.3 * kick, 0)   # the crack / clap, not hats
    full = kick + snare + hats
    # tempo: the analysis' guess and its usual confusions (4:3, 3:2 ...) - keep the one whose bars line up best
    # (the analysis' tempo is right far more often than any re-reading of the grid - on real, dense mixes a finer grid
    # always 'catches' more - so only its octave errors are considered: half or double)
    cands = sorted({round(base['bpm'] * m) for m in (1, 0.5, 2) if 60 <= base['bpm'] * m <= 200})
    scored = []
    for b in cands:
        step = fps * 60 / b / 4
        sc, ph, sw = _fit(full, step)
        g = np.round(_grid(full, step, sw) + ph).astype(int)
        g = g[g < len(full)]
        k_, s_ = _at(kick, g), _at(snare, g)
        n = len(g) // STEPS * STEPS
        if n < STEPS * 2:
            continue
        kb, sb = k_[:n].reshape(-1, STEPS), s_[:n].reshape(-1, STEPS)
        bar = max(kb[:, o].mean() + sb[:, (o + 4) % 16].mean() + sb[:, (o + 12) % 16].mean() for o in range(STEPS))
        # how much of the song's onset energy this grid catches (a mean per step would favour slower tempos: their
        # grids land on something every step), a bar that looks like a bar, and the analysis' own guess first
        caught = _at(full, g).sum() / (_peaks(full) + 1e-9)
        scored.append((min(caught, 1.0) * (1 + bar / (kb.mean() + sb.mean() + 1e-9) * 0.1) * (0.9 if b < 72 else 1.0),
                       b, ph, sw))
    by = {b: (sc, ph, sw) for sc, b, ph, sw in scored}
    bpm = base['bpm'] if base['bpm'] in by else max(scored)[1]
    dbl = [b for b in by if abs(b - 2 * bpm) <= 1]
    if dbl and by[dbl[0]][0] >= 1.25 * by[bpm][0] and bpm < 90:   # read at half tempo: the double grid catches far more
        bpm = dbl[0]
    for slower in (bpm / 2,):                                       # a double-time reading of the same groove: take the
        near = [b for b in by if abs(b - slower) <= 1 and b >= 60]  # slower one when it catches nearly as much
        if near and by[near[0]][0] >= 0.95 * by[bpm][0]:
            bpm = near[0]
            break
    _, ph, swing = by[bpm]
    step = fps * 60 / bpm / 4
    grid = np.round(_grid(full, step, swing) + ph).astype(int)
    grid = grid[grid < len(full)]
    k, s_, h = _at(kick, grid), _at(snare, grid), _at(hats, grid)
    nsteps = len(grid) // STEPS * STEPS

    def bar_score(off):
        kk, ss = k[off:off + nsteps - STEPS], s_[off:off + nsteps - STEPS]
        kb, sb = kk.reshape(-1, STEPS), ss.reshape(-1, STEPS)
        return kb[:, 0].sum() + 0.5 * kb[:, 8].sum() + sb[:, 4].sum() + sb[:, 12].sum() - 0.5 * sb[:, 0].sum()
    off = max(range(STEPS), key=bar_score)
    k, s_, h = k[off:], s_[off:], h[off:]
    nbars = min(len(k) // STEPS, 128)
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    out = dict(name=os.path.basename(name or 'Audio file'), bpm=int(round(bpm)), scale=scale, meter='4/4', bars=nbars,
               drums={}, bass=[], progs=[], source='audio', key=names[root] + ('m' if scale == 'minor' else ''),
               swing=round(0.5 + swing * 0.5, 2))
    for slot, vals in (('kick', k), ('snare', s_), ('chat', h)):
        v = vals[:nbars * STEPS]
        if not len(v) or v.max() <= 0:
            continue
        p95 = np.percentile(v[v > 0], 95) if (v > 0).any() else 0
        for lvl in (0.42, 0.3):                                     # a quieter, busier mix: try a lower bar once
            rows = _rows(v, nbars, lvl * p95, 0.85 * p95)
            if sum(1 for r in rows if r.strip('.') and sum(c != '.' for c in r) <= 9) >= 2:
                break
        if slot in ('kick', 'snare'):
            rows = [r for r in rows if sum(c != '.' for c in r) <= 9]   # leave out fills and rolls
        live = [r for r in rows if r.strip('.')]
        if len(live) < 2:
            continue
        # the consensus groove: steps hit in most bars (swung / live playing varies a little every bar) ...
        frac = [sum(r[i] != '.' for r in live) / len(live) for i in range(STEPS)]
        acc = [sum(r[i] == 'X' for r in live) / len(live) for i in range(STEPS)]
        cons = ''.join(('X' if acc[i] > 0.5 else 'x') if frac[i] >= 0.45 else '.' for i in range(STEPS))
        pats = [cons] if cons.strip('.') else []
        for r in _top(rows, min_count=max(2, nbars // 16)):        # ... and the exact bars that repeat, as variations
            if r.replace('X', 'x') != cons.replace('X', 'x') and len(pats) < 3:
                pats.append(r)
        if pats:
            out['drums'][slot] = pats
    # chord loops: the best-matching scale triad per bar
    band = (f >= 100) & (f < 1500)
    midi = 69 + 12 * np.log2(f[band] / 440.0)
    pc = np.mod(np.round(midi), 12).astype(int)
    tri = _triads(root, scale)
    degs = []
    for b in range(nbars):
        a = off + b * STEPS
        if a + STEPS >= len(grid):
            break
        ch = np.zeros(12)
        np.add.at(ch, pc, S[band][:, grid[a]:grid[a + STEPS]].sum(axis=1))
        if ch.sum() <= 0:
            continue
        ch = ch / np.linalg.norm(ch)
        degs.append(int(np.argmax([float(ch @ t) for t in tri])))
    out['progs'] = _loops(degs)
    if not out['drums']:
        out['note'] = 'No steady drum pattern was found - only the tempo, key and chords were learned.'
    else:
        out['note'] = 'Learned from audio: tempo, key, swing, drum patterns and chord loops (sounds are not learned).'
    if out['swing'] > 0.52:
        out['note'] += ' Swung groove: if the tempo reads double or 1.5x the real one, use a MIDI file of it instead.'
    return out
