"""Which Studio Lab genres sound closest to a reference song? Tempo, key / mode, and above all the drum feel.

The song's drums are folded onto one bar of 16 steps: where the kick (low band), the snare / clap (mid band) and the
hats (high band) hit on average. Every genre has written drum patterns, so those are compared directly - four on the
floor, a backbeat, a half-time snare, a broken kick, 8th or 16th hats - together with the tempo range (half / double
time allowed) and whether its scales are major- or minor-type.
"""
import numpy as np
from scipy import signal

MINORISH = {'minor', 'dorian', 'phrygian', 'harmonic_minor', 'melodic_minor', 'phrygian_dominant', 'pelog', 'ukrainian_dorian'}


def spectrum(x, sr):
    """Tonal balance: share of energy in sub / low / low-mid / mid / high bands (sums to 1)."""
    f, P = signal.welch(np.asarray(x, dtype=np.float64), sr, nperseg=4096)
    edges = (20, 60, 250, 1000, 4000, 11000)
    e = np.array([P[(f >= a) & (f < b)].sum() for a, b in zip(edges, edges[1:])])
    e = e / (e.sum() + 1e-12)
    return [round(float(v), 4) for v in e]


def fingerprint(x, sr, bpm):
    """What a piece of audio 'looks like' to the matcher - the same measurement for references and for genres."""
    fe = drum_feel(x, sr, bpm) or {}
    return dict(bpm=round(float(bpm), 1), spectrum=spectrum(x, sr), **{k: fe[k] for k in ('kick', 'snare', 'hat', 'percussive', 'four',
                'backbeat', 'halftime', 'kick_density', 'hat16') if k in fe})


def _bands(x, sr):
    hop = 256
    f, t, S = signal.stft(x, sr, nperseg=1024, noverlap=1024 - hop)
    mag = np.log1p(np.abs(S) * 50)
    out = {}
    for name, lo, hi in (('kick', 30, 140), ('snare', 1200, 4500), ('hat', 6000, 11000), ('all', 30, 11000)):
        sel = (f >= lo) & (f < hi)
        flux = np.maximum(np.diff(mag[sel], axis=1), 0).sum(axis=0)
        flux = np.maximum(flux - np.convolve(flux, np.ones(24) / 24, mode='same'), 0)
        out[name] = flux / (flux.max() + 1e-9)
    return out, sr / hop


def drum_feel(x, sr, bpm):
    """Average hit strength of kick / snare / hats on a 16-step bar, plus how drum-driven the song is."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim > 1:
        x = x.mean(axis=0)
    env, fps = _bands(x, sr)
    # the tempo has to be exact to fold two minutes onto one bar: try +-1.5 BPM around the estimate and keep the one
    # whose beat pulse folds sharpest
    best_b = (None, bpm)
    for b in np.arange(bpm - 1.5, bpm + 1.51, 0.05):
        st_ = fps * 60.0 / b
        n_ = int(len(env['all']) / st_) - 1
        if n_ < 16:
            continue
        sharp = 0.0
        for ph in np.arange(0, st_, max(1.0, st_ / 8)):
            idx = (ph + np.arange(n_) * st_).astype(int)
            sharp = max(sharp, float(env['all'][idx].mean()))
        if best_b[0] is None or sharp > best_b[0]:
            best_b = (sharp, b)
    bpm = float(best_b[1])
    step = fps * 60.0 / bpm / 4                                    # frames per 16th
    n_steps = int(len(env['all']) / step) - 1
    if n_steps < 64:
        return None

    def grid(e, phase):
        idx = (phase + np.arange(n_steps) * step).astype(int)
        idx = idx[idx < len(e) - 2]
        v = np.maximum(np.maximum(e[idx], e[np.minimum(idx + 1, len(e) - 1)]), e[np.maximum(idx - 1, 0)])
        k = len(v) // 16 * 16
        return v[:k].reshape(-1, 16).mean(axis=0)
    # beat phase: where the kick (or everything) lines up best with the 4 beats of a bar
    best = None
    for ph in np.arange(0, step * 16, max(1.0, step / 4)):
        k = grid(env['kick'], ph)
        a = grid(env['all'], ph)
        sc = k[[0, 4, 8, 12]].sum() + 0.5 * a[[0, 4, 8, 12]].sum() + 0.6 * k[0]
        if best is None or sc > best[0]:
            best = (sc, ph)
    ph = best[1]
    k, s, h = grid(env['kick'], ph), grid(env['snare'], ph), grid(env['hat'], ph)
    rel = lambda v: (v - v.min()) / (v.max() - v.min() + 1e-9)
    perc = float(np.mean(env['all'] > 0.25))                       # how often something hits
    k, s, h = rel(k), rel(s), rel(h)
    return dict(kick=k.round(3).tolist(), snare=s.round(3).tolist(), hat=h.round(3).tolist(),
                percussive=round(perc, 3), bpm_exact=round(bpm, 2), **_summary(k, s, h))


def _summary(k, s, h):
    """Drum feel as a few numbers (0..1): four on the floor, backbeat, half-time snare, kick density, 16th hats."""
    k, s, h = (np.asarray(v, float) if v is not None else np.zeros(16) for v in (k, s, h))
    beats, offs = [0, 4, 8, 12], [2, 6, 10, 14]
    four = float(np.clip(k[beats].min() - 0.5 * k[[i for i in range(16) if i not in beats]].mean(), 0, 1))
    back = float(np.clip((s[4] + s[12]) / 2 - (s[0] + s[8]) / 2 * 0.7, 0, 1))
    half = float(np.clip(s[8] - (s[4] + s[12]) / 2, 0, 1))
    kden = float(np.mean(k > 0.45))
    h16 = float(np.clip(h[[1, 3, 5, 7, 9, 11, 13, 15]].mean() / (h[offs + beats].mean() + 1e-9), 0, 1)) if h.max() > 0 else 0.0
    return dict(four=round(four, 2), backbeat=round(back, 2), halftime=round(half, 2), kick_density=round(kden, 2),
                hat16=round(h16, 2))


def _pat(pats):
    """A genre's drum patterns -> average 16-step hit strength."""
    rows = []
    for p in pats or []:
        if not isinstance(p, str) or len(p) != 16:
            continue
        rows.append([1.0 if c == 'X' else 0.8 if c in 'xo' else 0.0 for c in p])
    return np.mean(rows, axis=0) if rows else None


def _profile(st):
    d = st.get('drums') or {}
    kick_t = st.get('kick_track', 'kick')
    snares = st.get('snare_tracks') or ['snare']
    hats = [k for k in d if k in ('chat', 'ohat', 'hat', 'shaker', 'ride', 'guiro', 'maracas', 'manjira', 'tamb', 'ching')]
    k = _pat(d.get(kick_t))
    s = [x for x in (_pat(d.get(n)) for n in snares) if x is not None]
    h = [x for x in (_pat(d.get(n)) for n in hats) if x is not None]
    out = dict(kick=k, snare=np.max(s, axis=0) if s else None, hat=np.max(h, axis=0) if h else None, drumless=not d)
    out.update(_summary(out['kick'], out['snare'], out['hat']))
    return out


def _corr(a, b):
    if a is None or b is None:
        return 0.0
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.std() < 1e-6 or b.std() < 1e-6:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


_FP = None


def fingerprints():
    global _FP
    if _FP is None:
        import json
        import os
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'genre_fingerprints.json')) as f:
                _FP = json.load(f)
        except Exception:
            _FP = {}
    return _FP


def _fp_distance(ref, gp):
    """0 = sounds the same, larger = further apart (drum feel + tonal balance), against one genre fingerprint."""
    d = 0.0
    for k, w in (('four', 1.4), ('backbeat', 0.9), ('halftime', 0.9), ('kick_density', 0.7), ('hat16', 0.4)):
        d += w * abs(ref.get(k, 0) - gp.get(k, 0))
    for k, w in (('kick', 0.9), ('snare', 0.6), ('hat', 0.3)):
        d += w * (1 - max(-1.0, min(1.0, _corr(ref.get(k), gp.get(k))))) / 2
    if ref.get('spectrum') and gp.get('spectrum'):
        a, b = np.sqrt(ref['spectrum']), np.sqrt(gp['spectrum'])           # Hellinger distance of the tonal balance
        d += 2.2 * float(np.sqrt(0.5 * np.sum((a - b) ** 2)))
    d += 0.8 * abs(np.log((ref.get('percussive', 0.05) + 0.01) / (gp.get('percussive', 0.05) + 0.01))) / 2
    return d


def analyze_reference(x, sr, a):
    """Add the matcher's measurements to an analyze() result: tonal balance, and the drum feel for every plausible tempo
    reading (as detected, double, half, x1.5, x2/3 - triplet hats and half-time beats fool tempo detection)."""
    a['spectrum'] = spectrum(x, sr)
    b0, feels = float(a['bpm']), []
    for f in (1.0, 2.0, 0.5, 1.5, 2 / 3):
        b = b0 * f
        if 55 <= b <= 200:
            fe = drum_feel(x, sr, b)
            if fe:
                feels.append(dict(fe, ratio=round(f, 3)))
    a['feels'] = feels
    a['feel'] = feels[0] if feels else None
    return a


def suggest(features, styles, labels=None, top=6):
    """features: analyze() output + drum_feel(). -> [dict(id, name, score, why)] best first."""
    bpm = features.get('bpm') or 120
    feel0 = features.get('feel')
    minor = (features.get('scale') or 'minor') != 'major'
    out = []
    for sid, st in styles.items():
        if st.get('composer'):
            continue
        lo, hi = st['bpm']
        # tempo: every reading of the reference (as detected, double, half, x1.5, x2/3) - the one that suits this genre
        hyps = features.get('feels') or ([dict(feel0 or {}, ratio=1.0)] if feel0 is not None else [dict(ratio=1.0)])
        fps = fingerprints().get(sid)
        best_h = None
        for h in hyps:
            r = h.get('ratio', 1.0)
            b = (h.get('bpm_exact') or bpm * r)
            dist = max(0, lo - b, b - hi) + (0 if r == 1.0 else 1.5 if r in (2.0, 0.5) else 2.5)
            fd = min(_fp_distance(dict(h, spectrum=features.get('spectrum')), g) for g in fps) if (fps and h.get('kick')) else None
            val = 2.0 * float(np.exp(-dist / 7.0)) + (3.6 - 2.2 * fd if fd is not None else 0)
            if best_h is None or val > best_h[0]:
                best_h = (val, h, dist, fd)
        _, feel_h, dist, fd_best = best_h
        t_score = float(np.exp(-dist / 7.0))
        scales = st.get('scales') or []
        mode_ok = any((sc in MINORISH) == minor for sc in scales) if scales else True
        why = []
        score = 2.0 * t_score + (0.6 if mode_ok else 0.0)
        if t_score > 0.8:
            why.append(f'{lo}-{hi} BPM')
        prof = _profile(st)
        feel = feel_h if feel_h.get('kick') else feel0
        if feel and fps and fd_best is not None:           # compare with how the genre actually sounds
            dist_fp = fd_best
            score += 3.6 - 2.2 * dist_fp
            g = fps[0]
            if feel.get('four', 0) > 0.4 and g.get('four', 0) > 0.4:
                why.append('four-on-the-floor')
            if feel.get('halftime', 0) > 0.3 and g.get('halftime', 0) > 0.3:
                why.append('half-time snare')
            if feel.get('backbeat', 0) > 0.4 and g.get('backbeat', 0) > 0.4:
                why.append('backbeat on 2 & 4')
            if dist_fp < 0.9:
                why.append('similar drum feel and sound')
        elif feel:
            if prof['drumless']:
                score += 0.8 * (1.0 - min(1.0, feel['percussive'] * 3))
            else:
                ck, cs, ch = _corr(feel['kick'], prof['kick']), _corr(feel['snare'], prof['snare']), _corr(feel['hat'], prof['hat'])
                score += 0.8 * max(0.0, ck) + 0.5 * max(0.0, cs) + 0.3 * max(0.0, ch)
                diff = sum(w * abs(feel.get(f_, 0) - prof.get(f_, 0)) for f_, w in
                           (('four', 1.6), ('backbeat', 1.0), ('halftime', 1.0), ('kick_density', 0.8), ('hat16', 0.4)))
                score += 1.6 - diff
                if feel.get('four', 0) > 0.4 and prof.get('four', 0) > 0.4:
                    why.append('four-on-the-floor')
                if feel.get('halftime', 0) > 0.3 and prof.get('halftime', 0) > 0.3:
                    why.append('half-time snare')
                score -= 0.6 * max(0.0, 0.5 - feel['percussive'] * 3)     # a drumless reference vs a drum genre
                if ck > 0.75:
                    why.append('same kick pattern')
                if cs > 0.75:
                    why.append('same snare / clap placement')
                if ch > 0.75:
                    why.append('same hi-hat feel')
        if mode_ok:
            why.append('major key' if not minor else 'minor-type key')
        out.append(dict(id=sid, name=(labels or {}).get(sid) or st.get('label') or sid, score=round(score, 3), why=why))
    out.sort(key=lambda r: -r['score'])
    best = out[0]['score'] if out else 1.0
    for r in out:
        r['match'] = int(round(100 * r['score'] / max(best, 1e-9)))
    return out[:top]
