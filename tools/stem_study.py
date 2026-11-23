"""(2.20) Study real songs from their stems: how they're built, played, sounded and mixed - measured directly on each
stem (not through the app's genre matcher).

    python tools/stem_study.py <folder> [--json out.json] [--jobs 2]

Reads Native Instruments .stem.mp4 files (mix + drums, bass, other, vocals) and multitrack folders ("Song_v1.flac",
"Song_v1_bass.flac" ...). Per song:
  tempo        onset autocorrelation of the drum stem, octave settled by where kick and snare fall
  groove       kick / snare / hat strength on a 16-step bar, swing of the off-beat 16ths, ghost-note density
  structure    which stems play in every bar -> sections (intro, build, drop / full, break, outro) with bar counts
  bass         notes per 16th (pitch tracking), the most common 1-bar pattern, sub vs upper harmonics (clean / growl),
               note length, wobble rate (amplitude / brightness LFO locked to the beat)
  synths       chords per bar from the chroma of the 'other' stem, brightness and filter movement, pad vs pluck,
               stereo width
  effects      sidechain pumping depth and shape (level over the beat), echo (delay) at 1/8 / dotted 1/8 / 1/4,
               reverb tail length
  mix          loudness, peak, tonal balance, stereo width, low end mono, each stem's level at the drops
Only measurements leave this script.
"""
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
SR = 22050
HOP = 256
NOTE = 'C C# D D# E F F# G G# A A# B'.split()


# ----------------------------------------------------------------------------- loading
def load(path, stream=None, seconds=None):
    cmd = ['ffmpeg', '-loglevel', 'error', '-i', path]
    if stream is not None:
        cmd += ['-map', f'0:a:{stream}']
    if seconds:
        cmd += ['-t', str(seconds)]
    cmd += ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x.reshape(-1, 2).T if len(x) >= 2 else np.zeros((2, 1))


def find_songs(folder):
    """{name: {'mix': (path, stream), 'drums': ..., ...}}"""
    songs = {}
    for f in sorted(os.listdir(folder)):
        p = os.path.join(folder, f)
        low = f.lower()
        if low.endswith(('.stem.mp4', '_stem.mp4', '_stem_1.mp4')):
            name = re.sub(r'^[0-9a-f]{6,10}-', '', f)
            name = re.sub(r'[._]stem(_\d)?\.mp4$', '', name, flags=re.I)
            songs.setdefault(name, {k: (p, i) for i, k in enumerate(['mix', 'drums', 'bass', 'other', 'vocals'])})
        elif low.endswith(('.flac', '.wav')):
            b = re.sub(r'^[0-9a-f]{6,10}-', '', os.path.splitext(f)[0])
            m = re.match(r'(.+?_v\d+)(?:_(.+))?$', b)
            if m:
                part = m.group(2) or 'mix'
                kind = 'drums' if 'drum' in part else 'bass' if 'bass' in part else 'vocals' if part in ('choir', 'vox', 'vocals') \
                    else 'mix' if part == 'mix' else 'other:' + part
                songs.setdefault(m.group(1), {})[kind] = (p, None)
    return songs


# ----------------------------------------------------------------------------- helpers
def mono(x):
    return x.mean(axis=0)


def db(v):
    return 20 * np.log10(np.maximum(v, 1e-9))


def band(x, lo, hi, order=4):
    if lo <= 0:
        sos = signal.butter(order, hi / (SR / 2), output='sos')
    elif hi >= SR / 2 - 10:
        sos = signal.butter(order, lo / (SR / 2), 'high', output='sos')
    else:
        sos = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos')
    return signal.sosfilt(sos, x, axis=-1)


def env(x, hop=HOP):
    x = mono(x) if x.ndim > 1 else x
    n = len(x) // hop
    return np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)


def flux(x, lo, hi):
    """Onset strength in a band (positive spectral flux), frames of HOP."""
    x = mono(x) if x.ndim > 1 else x
    f, t, S = signal.stft(x, SR, nperseg=1024, noverlap=1024 - HOP, boundary=None)
    sel = (f >= lo) & (f < hi)
    m = np.log1p(np.abs(S[sel]) * 30)
    fl = np.maximum(np.diff(m, axis=1), 0).sum(0)
    fl = np.concatenate([[0], fl])
    return fl / (fl.max() + 1e-9)


# ----------------------------------------------------------------------------- tempo + grid
def tempo(drums):
    o = flux(drums, 30, 11000)
    fps = SR / HOP
    o = o - np.convolve(o, np.ones(16) / 16, 'same')
    o = np.maximum(o, 0)
    ac = np.correlate(o[:int(fps * 120)], o[:int(fps * 120)], 'full')[len(o[:int(fps * 120)]) - 1:]
    cands = []
    at = lambda l: float(np.interp(l, np.arange(len(ac)), ac))       # fractional lags: 0.1 BPM resolution
    for bpm in np.arange(60, 200.01, 0.1):
        lag = fps * 60 / bpm
        if 4 * lag + 1 >= len(ac):
            continue
        v = at(lag) + 0.5 * at(2 * lag) + 0.5 * at(4 * lag) + 0.25 * at(8 * lag if 8 * lag < len(ac) - 1 else 4 * lag)
        cands.append((v, bpm))
    cands.sort(reverse=True)
    return cands[0][1] if cands else 120.0, [round(b, 2) for _, b in cands[:6]]


def refine(drums, bpm):
    """Exact tempo and the bar phase: fold the kick onsets for tempos around bpm, keep the sharpest."""
    k = flux(band(drums, 0, 150), 30, 150)
    a = flux(drums, 30, 11000)
    fps = SR / HOP
    best = None
    for b in np.arange(bpm - 1.5, bpm + 1.51, 0.05):
        beat = fps * 60 / b
        n = int(len(a) / beat) - 1
        if n < 32:
            continue
        for ph in np.arange(0, beat, beat / 16):
            idx = (ph + np.arange(n) * beat).astype(int)
            s = a[idx].mean() + k[idx].mean()
            if best is None or s > best[0]:
                best = (s, b, ph)
    _, b, ph = best
    # bar phase: which of the 4 beats is the downbeat - the one with the most kick
    beat = fps * 60 / b
    n = int(len(k) / beat) - 1
    kb = [k[(ph + np.arange(j, n, 4) * beat).astype(int)].mean() for j in range(4)]
    return float(b), float(ph + int(np.argmax(kb)) * beat)


def fold16(o, bpm, phase, bars=None):
    """Onset strength on the 16 steps of a bar (max of +-1 frame), averaged over the bars (or given bars)."""
    fps = SR / HOP
    step = fps * 60 / bpm / 4
    n = int((len(o) - phase) / step) // 16
    if n < 1:
        return np.zeros(16)
    idx = (phase + np.arange(n * 16) * step).astype(int)
    idx = np.clip(idx, 1, len(o) - 2)
    v = np.maximum(np.maximum(o[idx], o[idx - 1]), o[idx + 1]).reshape(n, 16)
    if bars is not None:
        bars = [b for b in bars if b < n]
        v = v[bars] if bars else v
    return v.mean(0)


def bar_frames(bpm, phase, nframes):
    fps = SR / HOP
    bar = fps * 60 / bpm * 4
    n = int((nframes - phase) / bar)
    return [(int(phase + i * bar), int(phase + (i + 1) * bar)) for i in range(n)]


# ----------------------------------------------------------------------------- analyses
def groove(drums, bpm, phase, full_bars):
    k = flux(band(drums, 0, 140), 30, 140)
    s = flux(band(drums, 1200, 5000), 1200, 5000)
    h = flux(band(drums, 7000, 11000), 7000, 11000)
    rel = lambda v: ((v - v.min()) / (v.max() - v.min() + 1e-9)).round(2).tolist()
    K, S, H = (fold16(x, bpm, phase, full_bars) for x in (k, s, h))
    # swing: where the off-beat 16th hats land between their neighbours (0.5 = straight, 0.66 = triplet swing)
    fps = SR / HOP
    step = fps * 60 / bpm / 4
    offs = []
    n = int((len(h) - phase) / step) - 2
    for i in range(1, n, 2):
        c = int(phase + i * step)
        lo, hi = int(c - step * 0.45), int(c + step * 0.45)
        if hi >= len(h) or lo < 0:
            continue
        w = h[lo:hi]
        if w.max() > 0.25:
            offs.append((lo + int(np.argmax(w)) - (c - step)) / (2 * step))
    swing = float(np.median(offs)) if len(offs) > 20 else None
    return dict(kick=rel(K), snare=rel(S), hat=rel(H), swing=round(swing, 3) if swing else None,
                four=bool(min(rel(K)[i] for i in (0, 4, 8, 12)) > 0.55),
                halftime=bool(rel(S)[8] > 0.7 and rel(S)[4] < 0.45 and rel(S)[12] < 0.45),
                backbeat=bool(rel(S)[4] > 0.6 and rel(S)[12] > 0.6),
                hats16=float(np.mean([rel(H)[i] for i in range(1, 16, 2)])) > 0.45)


def structure(stems, bpm, phase, nframes):
    """Per bar: which stems play (level vs the stem's loud bars), -> sections."""
    bars = bar_frames(bpm, phase, nframes)
    lv = {}
    for k, x in stems.items():
        e = env(x)
        per = np.array([db(e[a:b].mean()) if b <= len(e) else -120 for a, b in bars])
        lv[k] = per - np.percentile(per, 95)
    kick = None
    if 'drums' in stems:
        ke = env(band(stems['drums'], 0, 120))
        per = np.array([db(ke[a:b].mean()) if b <= len(ke) else -120 for a, b in bars])
        kick = per - np.percentile(per, 95)
    on = {k: (v > -14) for k, v in lv.items()}
    kick_on = kick > -12 if kick is not None else None
    total = np.zeros(len(bars))
    for v in lv.values():
        total = total + 10 ** (v / 10)
    tot_db = db(np.sqrt(total))
    tot_db -= tot_db.max()
    # 8-bar blocks -> labels
    labels = []
    for b0 in range(0, len(bars), 8):
        sl = slice(b0, min(len(bars), b0 + 8))
        play = {k for k, v in on.items() if v[sl].mean() > 0.5}
        kk = kick_on[sl].mean() > 0.5 if kick_on is not None else 'drums' in play
        e = float(tot_db[sl].mean())
        labels.append(dict(bar=b0, stems=sorted(play), kick=bool(kk), energy=round(e, 1)))
    # name the blocks
    full = max((x['energy'] for x in labels), default=0)
    for i, x in enumerate(labels):
        nxt = labels[i + 1] if i + 1 < len(labels) else None
        if x['kick'] and 'bass' in x['stems'] and x['energy'] > full - 4:
            x['name'] = 'drop'
        elif not x['kick'] and i not in (0, len(labels) - 1):
            x['name'] = 'break'
        elif nxt and nxt['energy'] - x['energy'] > 2 and not (x['kick'] and 'bass' in x['stems']):
            x['name'] = 'build'
        elif i < 2:
            x['name'] = 'intro'
        elif i >= len(labels) - 2:
            x['name'] = 'outro'
        else:
            x['name'] = 'groove'
    # merge into sections
    secs = []
    for x in labels:
        if secs and secs[-1]['name'] == x['name']:
            secs[-1]['bars'] += 8
        else:
            secs.append(dict(name=x['name'], bars=8, stems=x['stems']))
    full_bars = [i for i in range(len(bars)) if kick_on is not None and kick_on[i] and on.get('bass', np.ones(len(bars), bool))[i]]
    return dict(sections=secs, bars=len(bars), blocks=labels), full_bars


def pitch_track(x, bpm, phase, nsteps):
    """Bass: one pitch per 16th step (YIN-like on a lowpassed signal); None where silent."""
    y = band(mono(x), 25, 400)
    fps = SR / HOP
    step = fps * 60 / bpm / 4 * HOP          # samples per 16th
    out = []
    e_all = np.sqrt(np.mean(y ** 2)) + 1e-9
    for i in range(nsteps):
        a = int(phase * HOP + i * step + step * 0.15)
        b = int(a + min(step * 0.7, SR * 0.12))
        seg = y[a:b]
        if len(seg) < 600 or np.sqrt(np.mean(seg ** 2)) < 0.25 * e_all:
            out.append(None)
            continue
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, 'full')[len(seg) - 1:]
        lo, hi = int(SR / 400), min(len(ac) - 1, int(SR / 28))
        if hi <= lo + 2:
            out.append(None)
            continue
        d = ac[0] - ac[lo:hi]
        lag = lo + int(np.argmin(d / (np.arange(lo, hi) + 1)))
        # first strong dip (avoid octave errors): the earliest lag within 10% of the best
        thr = d.min() + 0.1 * (d.max() - d.min())
        cand = np.where(d <= thr)[0]
        if len(cand):
            lag = lo + int(cand[0])
        f0 = SR / lag
        out.append(int(round(69 + 12 * np.log2(f0 / 440.0))))
    return out


def bass_study(x, bpm, phase, full_bars, key_pc):
    nbars = max(full_bars) + 1 if full_bars else 0
    steps = pitch_track(x, bpm, phase, nbars * 16) if nbars else []
    pats = {}
    for b in full_bars[:64]:
        seq = steps[b * 16:(b + 1) * 16]
        if len(seq) < 16 or sum(v is not None for v in seq) < 2:
            continue
        rel_ = tuple('.' if v is None else (v - key_pc) % 12 for v in seq)
        pats[rel_] = pats.get(rel_, 0) + 1
    top = sorted(pats.items(), key=lambda t: -t[1])[:3]
    xm = mono(x)
    sub = np.mean(band(xm, 20, 70) ** 2)
    low = np.mean(band(xm, 70, 250) ** 2)
    upper = np.mean(band(xm, 250, 4000) ** 2)
    tot = sub + low + upper + 1e-12
    played = [v for v in steps if v is not None]
    # note length: of the steps with a note, how many continue the previous one
    sus = np.mean([steps[i] is not None and steps[i] == steps[i - 1] for i in range(1, len(steps)) if steps[i] is not None]) if played else 0
    return dict(patterns=[dict(steps=''.join('.' if s == '.' else '0123456789AB'[s] for s in p), bars=n) for p, n in top],
                median_note=NOTE[int(np.median(played)) % 12] + str(int(np.median(played)) // 12 - 1) if played else None,
                range=[min(played), max(played)] if played else None,
                sub_pct=int(100 * sub / tot), low_pct=int(100 * low / tot), upper_pct=int(100 * upper / tot),
                busy=round(len(played) / max(1, len(steps)), 2), held=round(float(sus), 2),
                wobble=lfo_rate(x, bpm))


def lfo_rate(x, bpm):
    """A rhythmic LFO on the sound (wobble / tremolo / filter): the strongest modulation rate of its brightness+level,
    named in note values. None if nothing beat-locked stands out."""
    xm = mono(x)
    hop = 128
    n = len(xm) // hop
    if n < 2000:
        return None
    seg = xm[:n * hop].reshape(n, hop)
    lev = np.sqrt((seg ** 2).mean(1) + 1e-12)
    hi = band(xm, 300, 3000)[:n * hop].reshape(n, hop)
    br = np.sqrt((hi ** 2).mean(1) + 1e-12) / lev
    fps = SR / hop
    out = {}
    for name, sig in (('level', lev), ('tone', br)):
        s = (sig - np.convolve(sig, np.ones(int(fps * 2)) / int(fps * 2), 'same'))[int(fps):-int(fps)]
        if len(s) < 1000:
            continue
        f, P = signal.welch(s, fps, nperseg=min(len(s), 4096))
        beat_hz = bpm / 60
        rates = {'1/2': beat_hz / 2, '1/4': beat_hz, '1/4T': beat_hz * 1.5, '1/8': beat_hz * 2, '1/8T': beat_hz * 3,
                 '1/16': beat_hz * 4, '1/16T': beat_hz * 6}
        base = np.median(P[(f > 0.3) & (f < 20)]) + 1e-12
        sc = {k: float(P[np.argmin(abs(f - v))] / base) for k, v in rates.items() if v < fps / 2}
        best = max(sc, key=sc.get)
        out[name] = (best, round(sc[best], 1))
    return out


def chroma_chords(x, bpm, phase, nbars):
    """The chord (root + quality) of every bar from the 'other' stem; a short list of the most common progression."""
    xm = mono(x)
    f, t, S = signal.stft(xm, SR, nperseg=4096, noverlap=4096 - 1024, boundary=None)
    P = np.abs(S) ** 2
    sel = (f > 80) & (f < 2500)
    midi = 69 + 12 * np.log2(f[sel] / 440.0)
    pc = np.mod(np.round(midi), 12).astype(int)
    C = np.zeros((12, P.shape[1]))
    for k in range(12):
        C[k] = P[sel][pc == k].sum(0)
    fps = SR / 1024
    bar = fps * 60 / bpm * 4
    p0 = phase * HOP / 1024
    tmpl = []
    for r in range(12):
        for q, iv in (('', (0, 4, 7)), ('m', (0, 3, 7))):
            v = np.zeros(12)
            for i in iv:
                v[(r + i) % 12] = 1
            v[r] += 0.3
            tmpl.append((NOTE[r] + q, v / np.linalg.norm(v)))
    out, tot = [], np.zeros(12)
    for b in range(nbars):
        a, e = int(p0 + b * bar), int(p0 + (b + 1) * bar)
        if e > C.shape[1]:
            break
        v = C[:, a:e].sum(1)
        tot += v
        if v.sum() < 1e-9:
            out.append(None)
            continue
        v = np.sqrt(v / v.sum())
        nm, sc = max(((n, float(v @ t)) for n, t in tmpl), key=lambda z: z[1])
        out.append(nm if sc > 0.55 else None)
    return out, tot


def key_of(chroma_total):
    """Krumhansl key profile match -> (root pc, 'major'/'minor')."""
    maj = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    mnr = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    v = chroma_total / (chroma_total.sum() + 1e-12)
    best = max(((np.corrcoef(v, np.roll(p, r))[0, 1], r, m) for r in range(12) for p, m in ((maj, 'major'), (mnr, 'minor'))))
    return best[1], best[2]


def synth_study(x, bpm, phase, nbars, full_bars):
    xm = mono(x)
    f, t, S = signal.stft(xm, SR, nperseg=2048, noverlap=2048 - 512, boundary=None)
    P = np.abs(S)
    cen = (P * f[:, None]).sum(0) / (P.sum(0) + 1e-9)
    lev = P.sum(0)
    on = lev > np.percentile(lev, 60) * 0.3
    cen_on = cen[on] if on.any() else cen
    # filter movement: the brightness range over 4-bar windows
    fps = SR / 512
    win = int(fps * 60 / bpm * 16)
    moves = []
    for a in range(0, len(cen) - win, win):
        c = cen[a:a + win][on[a:a + win]]
        if len(c) > win * 0.3:
            moves.append(np.percentile(c, 90) / max(1, np.percentile(c, 10)))
    # pad vs pluck: how much of each beat the level stays near its peak
    e = env(x)
    fpsb = SR / HOP
    beat = fpsb * 60 / bpm
    keep = []
    for i in range(int((len(e) - phase) / beat) - 1):
        seg = e[int(phase + i * beat):int(phase + (i + 1) * beat)]
        if len(seg) > 4 and seg.max() > np.percentile(e, 70) * 0.5:
            keep.append(np.mean(seg > 0.5 * seg.max()))
    width = stereo_width(x)
    return dict(brightness_hz=int(np.median(cen_on)), filter_move=round(float(np.median(moves)), 2) if moves else None,
                sustain=round(float(np.median(keep)), 2) if keep else None, width=width, lfo=lfo_rate(x, bpm))


def stereo_width(x):
    if x.shape[0] < 2:
        return None
    m, s = (x[0] + x[1]) / 2, (x[0] - x[1]) / 2
    return round(float(np.sqrt(np.mean(s ** 2)) / (np.sqrt(np.mean(m ** 2)) + 1e-9)), 2)


def pump(x, bpm, phase, full_bars):
    """Sidechain: the level shape over one beat in the full bars (16 points), and its depth in dB."""
    e = env(x)
    fps = SR / HOP
    beat = fps * 60 / bpm
    shapes = []
    for b in full_bars[:96]:
        for j in range(4):
            a = phase + (b * 4 + j) * beat
            idx = (a + np.arange(16) * beat / 16).astype(int)
            if idx[-1] < len(e):
                shapes.append(e[idx])
    if len(shapes) < 16:
        return None
    sh = np.median(np.array(shapes), axis=0)
    sh = sh / (sh.max() + 1e-12)
    if sh.min() < 0.05:                                     # it stops between notes: rhythm, not ducking
        return dict(depth_db=None, gaps=True, shape=[int(round(v * 9)) for v in sh])
    depth = float(-db(sh.min()))
    dip_at = int(np.argmin(sh))
    recover = next((i for i in range(dip_at, 16) if sh[i] > 0.8), 16)
    return dict(depth_db=round(depth, 1), dip_step=dip_at, recover_16ths=recover - dip_at,
                shape=[int(round(v * 9)) for v in sh])


def echo(x, bpm):
    """Delay: envelope autocorrelation at musical lags beyond the beat grid's own repetition."""
    e = env(x)
    fps = SR / HOP
    e = e - np.convolve(e, np.ones(int(fps)) / int(fps), 'same')
    e = e[: int(fps * 90)]
    if len(e) < fps * 10:
        return None
    ac = np.correlate(e, e, 'full')[len(e) - 1:]
    ac /= ac[0] + 1e-12
    beat = fps * 60 / bpm
    lags = {'1/8': beat / 2, '1/8.': beat * 0.75, '1/4': beat, '1/4.': beat * 1.5, '1/8T': beat / 3}
    v = {k: round(float(ac[int(round(l))]), 2) for k, l in lags.items() if int(round(l)) < len(ac)}
    # a dotted lag that rings about as much as the straight ones = a dotted delay on the part
    return v


def reverb_tail(x):
    """How long the stem rings after its loud moments stop: median time from a drop of 6 dB to -30 dB (s)."""
    e = db(env(x))
    fps = SR / HOP
    pk = np.percentile(e, 95)
    tails = []
    i = 0
    while i < len(e) - int(fps * 3):
        if e[i] > pk - 3 and e[i + 1] < e[i] - 1:
            seg = e[i:i + int(fps * 3)]
            below = np.where(seg < seg[0] - 30)[0]
            if len(below):
                tails.append(below[0] / fps)
                i += int(fps)
        i += 1
    return round(float(np.median(tails)), 2) if len(tails) > 5 else None


def mix_study(mix, stems, full_bars, bpm, phase):
    m = mono(mix)
    rms = db(np.sqrt(np.mean(m ** 2)))
    out = dict(rms_db=round(float(rms), 1), peak_db=round(float(db(np.abs(mix).max())), 1),
               crest_db=round(float(db(np.abs(mix).max()) - rms), 1), width=stereo_width(mix))
    tot = np.mean(m ** 2) + 1e-12
    for nm, lo, hi in (('sub', 20, 60), ('bass', 60, 250), ('lowmid', 250, 1000), ('mid', 1000, 4000), ('air', 4000, 11000)):
        out[nm + '_pct'] = round(float(100 * np.mean(band(m, lo, hi) ** 2) / tot), 1)
    lo_side = band((mix[0] - mix[1]) / 2, 0, 120)
    lo_mid = band((mix[0] + mix[1]) / 2, 0, 120)
    out['low_mono'] = round(float(1 - np.sqrt(np.mean(lo_side ** 2)) / (np.sqrt(np.mean(lo_mid ** 2)) + 1e-9)), 2)
    # each stem's level against the mix in the full bars
    bars = bar_frames(bpm, phase, len(env(mix)))
    me = env(mix)
    sel = [bars[b] for b in full_bars if b < len(bars)] or bars
    mlev = db(np.mean([me[a:b].mean() for a, b in sel]))
    lv = {}
    for k, x in stems.items():
        se = env(x)
        lv[k] = round(float(db(np.mean([se[a:b].mean() for a, b in sel if b <= len(se)] or [1e-9])) - mlev), 1)
    out['stem_levels_db'] = lv
    return out


# ----------------------------------------------------------------------------- one song
def study(item):
    name, files = item
    try:
        stems, mix = {}, None
        for k, (p, i) in files.items():
            x = load(p, i)
            if k == 'mix':
                mix = x
            else:
                stems[k] = x
        others = [k for k in stems if k.startswith('other')]
        if len(others) > 1 or (others and others[0] != 'other'):
            n = max(stems[k].shape[1] for k in others)
            acc = np.zeros((2, n))
            for k in others:
                acc[:, :stems[k].shape[1]] += stems[k]
            for k in others:
                del stems[k]
            stems['other'] = acc
        if mix is None:
            n = max(v.shape[1] for v in stems.values())
            mix = np.zeros((2, n))
            for v in stems.values():
                mix[:, :v.shape[1]] += v
        drums = stems.get('drums', mix)
        bpm0, cands = tempo(drums)
        # octave: house/techno/trance live at 110-150 with a kick on every beat; a half-time snare on 3 at 140-ish
        # means dubstep (70); otherwise prefer 70-180
        bpm, phase = refine(drums, bpm0)
        g = groove(drums, bpm, phase, None)
        if bpm < 100 and 2 * bpm <= 165:
            # 61.5 with a kick on every 8th is 123 four on the floor; 70 with the snare on 3 at double speed is
            # 140 dubstep; hip-hop at 85-95 (double = 170-190) stays where it is
            g2 = groove(drums, bpm * 2, phase, None)
            if bpm < 75 or g2['four'] or (g2['halftime'] and 2 * bpm >= 128) or \
                    (not (g['backbeat'] or g['four']) and g2['backbeat']):
                bpm, phase = refine(drums, bpm * 2)
        nframes = len(env(mix))
        st, full_bars = structure({k: v for k, v in stems.items()}, bpm, phase, nframes)
        g = groove(drums, bpm, phase, full_bars or None)
        nb = st['bars']
        chords, ctot = chroma_chords(stems.get('other', mix), bpm, phase, nb)
        if 'bass' in stems:
            _, btot = chroma_chords(stems['bass'], bpm, phase, nb)
            ctot = ctot + 0.5 * btot
        kpc, mode = key_of(ctot)
        rep = dict(name=name, bpm=round(bpm, 2), bpm_candidates=cands, key=NOTE[kpc] + ('m' if mode == 'minor' else ''),
                   length_s=round(mix.shape[1] / SR, 1), groove=g, structure=st)
        # most common 4-chord loop, relative to the key
        seq = [c for c in chords if c]
        if seq:
            loops = {}
            for i in range(0, len(seq) - 3):
                loop = tuple(seq[i:i + 4])
                loops[loop] = loops.get(loop, 0) + 1
            rep['chords'] = dict(top_loop=list(max(loops, key=loops.get)) if loops else seq[:4],
                                 changes_per_8_bars=round(8 * sum(1 for a, b in zip(chords, chords[1:]) if a and b and a != b) / max(1, nb), 1))
        if 'bass' in stems:
            rep['bass'] = bass_study(stems['bass'], bpm, phase, full_bars, kpc)
            rep['bass']['pump'] = pump(stems['bass'], bpm, phase, full_bars)
        if 'other' in stems:
            rep['synths'] = synth_study(stems['other'], bpm, phase, nb, full_bars)
            rep['synths']['pump'] = pump(stems['other'], bpm, phase, full_bars)
            rep['synths']['echo'] = echo(stems['other'], bpm)
            rep['synths']['tail_s'] = reverb_tail(stems['other'])
        if 'vocals' in stems:
            v = stems['vocals']
            ev = env(v)
            rep['vocals'] = dict(plays_pct=int(100 * np.mean(ev > np.percentile(ev, 95) * 0.1)),
                                 width=stereo_width(v), tail_s=reverb_tail(v), echo=echo(v, bpm))
        rep['mix'] = mix_study(mix, stems, full_bars, bpm, phase)
        return name, rep
    except Exception as e:                                  # noqa: BLE001
        import traceback
        return name, dict(error=repr(e), trace=traceback.format_exc()[-800:])


def main():
    folder = sys.argv[1]
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else 2
    songs = find_songs(folder)
    out = {}
    with ProcessPoolExecutor(jobs) as ex:
        for name, rep in ex.map(study, sorted(songs.items())):
            out[name] = rep
            print('done', name, rep.get('bpm'), rep.get('key'), rep.get('error', ''), flush=True)
    if '--json' in sys.argv:
        with open(sys.argv[sys.argv.index('--json') + 1], 'w') as f:
            json.dump(out, f, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))


if __name__ == '__main__':
    main()
