"""Reference-track analysis: tempo, key, loudness, brightness and energy of an audio file."""
import numpy as np
from scipy import signal

from .theory import NOTE_NAMES

# Krumhansl-Schmuckler key profiles
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def analyze(x, sr):
    """x: mono float array. Returns dict(bpm, key, scale, loudness, brightness, energy, confidence)."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim > 1:
        x = x.mean(axis=0)
    if sr != 22050:
        x = signal.resample_poly(x, 22050, sr)
        sr = 22050
    x = x[: sr * 120]
    if len(x) < sr * 5:
        raise ValueError('reference is too short (need at least 5 seconds)')
    # ---- tempo: spectral-flux onset envelope, autocorrelation, prefer 70-180 BPM
    hop = 256
    f, t, S = signal.stft(x, sr, nperseg=1024, noverlap=1024 - hop)
    mag = np.log1p(np.abs(S))
    flux = np.maximum(np.diff(mag, axis=1), 0).sum(axis=0)
    flux = flux - np.convolve(flux, np.ones(16) / 16, mode='same')
    flux = np.maximum(flux, 0)
    ac = np.correlate(flux, flux, mode='full')[len(flux) - 1:]
    fps = sr / hop
    bpms = np.arange(60, 200.5, 0.5)
    lags = fps * 60 / bpms
    score = np.interp(lags, np.arange(len(ac)), ac)
    score *= np.exp(-0.5 * (np.log2(bpms / 120) / 0.9) ** 2)      # gentle prior around 120
    for i, b in enumerate(bpms):                                    # reward octave agreement
        score[i] += 0.5 * np.interp(lags[i] * 2, np.arange(len(ac)), ac)
    bpm = float(bpms[int(np.argmax(score))])
    # ---- key: chroma from a constant-ish pitch mapping of the spectrum
    f2, t2, S2 = signal.stft(x, sr, nperseg=8192, noverlap=4096)
    P = np.abs(S2) ** 2
    band = (f2 > 55) & (f2 < 2000)
    midi = 69 + 12 * np.log2(f2[band] / 440.0)
    pc = np.mod(np.round(midi), 12).astype(int)
    chroma = np.zeros(12)
    e = P[band].sum(axis=1)
    np.add.at(chroma, pc, e)
    chroma /= chroma.sum() + 1e-12
    best = (-9, 0, 'major')
    for r in range(12):
        for prof, name in ((MAJOR, 'major'), (MINOR, 'minor')):
            c = np.corrcoef(np.roll(prof, r), chroma)[0, 1]
            if c > best[0]:
                best = (c, r, name)
    # ---- loudness (approx LUFS) and brightness
    from .dsp import lufs
    x44 = signal.resample_poly(x, 2, 1)[:]
    try:
        loud = float(lufs(np.vstack([x44, x44])))
    except Exception:
        loud = -14.0
    spec = P.mean(axis=1)
    centroid = float((f2 * spec).sum() / (spec.sum() + 1e-12))
    brightness = float(np.clip((np.log2(max(centroid, 200) / 900.0)) / 1.5, -1, 1))
    rms = np.sqrt(np.convolve(x ** 2, np.ones(sr // 2) / (sr // 2), mode='valid'))
    energy = float(np.clip((np.percentile(rms, 75) / (np.max(rms) + 1e-9)) * 1.2 - 0.2, 0, 1))
    return dict(bpm=int(round(bpm)), key=NOTE_NAMES[best[1]] + ('m' if best[2] == 'minor' else ''), scale=best[2],
                loudness=round(max(-18.0, min(-6.0, loud)), 1), brightness=round(brightness, 2),
                energy=round(energy, 2), confidence=round(float(best[0]), 2), centroid=int(centroid))
