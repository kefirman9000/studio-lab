"""Your own sounds: drum samples that replace the built-in kit, single-note samples played as instruments, and short
voice samples (a word, a shout, a line) that genres chop, stutter and screw into the song."""
import os
import re

import numpy as np

from . import updater
from .dsp import SR, adsr, mtof, write_wav_float

ROOT = os.path.join(updater.ROOT, 'user_sounds')
DRUM_SLOTS = ['kick', 'snare', 'clap', 'chat', 'ohat', 'ride', 'crash', 'rim', 'shaker', 'tom', 'conga', 'perc']
SLOT_FOR = {'kick': 'kick', 'chipkick': 'kick', 'taiko': 'kick', 'snare': 'snare', 'chipsnare': 'snare', 'timp': 'tom',
            'clap': 'clap', 'chat': 'chat', 'chiphat': 'chat', 'ohat': 'ohat', 'ride': 'ride', 'crash': 'crash',
            'rim': 'rim', 'shaker': 'shaker', 'tom': 'tom', 'conga': 'conga', 'cowbell808': 'perc'}
_cache = {}


KINDS = ('drums', 'inst', 'vocal')
VOCAL_TYPES = ('phrase', 'shout', 'note', 'speech')   # a short line / word, a one-shot ad-lib, a sung note, a spoken quote


def _kind(kind):
    if kind not in KINDS:
        raise ValueError('unknown sound type')
    return kind


def _safe(name):
    return re.sub(r'[^A-Za-z0-9 _-]', '', name).strip()[:40] or 'sound'


def save(kind, name, pcm, root_note=60, vtype='phrase'):
    """kind: 'drums', 'inst' or 'vocal'. pcm: mono float32 at 44.1 kHz. Voice samples keep at most 10 seconds."""
    d = os.path.join(ROOT, _kind(kind))
    os.makedirs(d, exist_ok=True)
    name = _safe(name)
    # drums: a slot name ('snare') is what 'my samples' plays for that part; (2.21) any other name joins your drum
    # library and can be picked for any drum voice
    x = np.asarray(pcm, dtype=np.float32)[: SR * (10 if kind == 'vocal' else 20)]
    if len(x) < 100:
        raise ValueError('sound is too short')
    # trim leading silence, normalise
    nz = np.nonzero(np.abs(x) > 0.01 * (np.max(np.abs(x)) or 1))[0]
    x = x[nz[0]:] if len(nz) else x
    x = x / (np.max(np.abs(x)) or 1.0) * 0.9
    write_wav_float(os.path.join(d, name + '.wav'), np.vstack([x, x]))
    if kind == 'vocal':                                  # trim trailing silence too, so chops land on the voice
        nz = np.nonzero(np.abs(x) > 0.01)[0]
        x = x[:nz[-1] + int(0.03 * SR)] if len(nz) else x
        with open(os.path.join(d, name + '.type'), 'w') as f:
            f.write(vtype if vtype in VOCAL_TYPES else 'phrase')
    if kind in ('inst', 'vocal'):
        with open(os.path.join(d, name + '.root'), 'w') as f:
            f.write(str(int(root_note)))
    _cache.clear()
    return name


def delete(kind, name):
    if kind not in KINDS:
        return
    for ext in ('.wav', '.root', '.type'):
        p = os.path.join(ROOT, kind, _safe(name) + ext)
        if os.path.exists(p):
            os.remove(p)
    _cache.clear()


def listing():
    out = {'drums': [], 'inst': [], 'vocal': []}
    for kind in out:
        d = os.path.join(ROOT, kind)
        if os.path.isdir(d):
            out[kind] = sorted(f[:-4] for f in os.listdir(d) if f.endswith('.wav'))
    return out


def path(kind, name):
    if kind not in KINDS:
        return None
    p = os.path.join(ROOT, kind, _safe(name) + '.wav')
    return p if os.path.exists(p) else None


def load(kind, name):
    key = (kind, name)
    if key not in _cache:
        p = path(kind, name)
        if not p:
            return None
        a = np.fromfile(p, dtype='<f4', offset=58).reshape(-1, 2)[:, 0].astype(np.float64)
        root = 60
        rp = os.path.join(ROOT, kind, _safe(name) + '.root')
        if os.path.exists(rp):
            try:
                root = int(open(rp).read().strip())
            except ValueError:
                pass
        _cache[key] = (a, root)
    return _cache[key]


def drum(inst):
    slot = SLOT_FOR.get(inst)
    if not slot:
        return None
    s = load('drums', slot)
    return None if s is None else s[0]


def sampler(name):
    """Instrument function playing a user sample, re-pitched across the keyboard."""
    def play(m, dur, p, glide=None, mod=None):
        s = load('inst', name)
        if s is None:
            return np.zeros(int(0.1 * SR))
        x, root = s
        ratio = float(mtof(m) / mtof(root))
        env = adsr(dur * SR, 0.003, 0.3, 0.9, p.get('r', 0.15))
        n = min(len(env), int(len(x) / ratio) - 1)
        if n <= 10:
            return np.zeros(10)
        y = np.interp(np.arange(n) * ratio, np.arange(len(x)), x)
        return y * env[:n]
    return play


def vocal_type(name):
    p = os.path.join(ROOT, 'vocal', _safe(name) + '.type')
    try:
        t = open(p).read().strip()
    except OSError:
        return 'phrase'
    return t if t in VOCAL_TYPES else 'phrase'


def vocal_info(name):
    """(length in seconds, sample type, root note, onsets in seconds) of a voice sample - or None if it's gone."""
    s = load('vocal', name)
    if s is None:
        return None
    x, root = s
    hop = 256
    e = np.sqrt(np.convolve(x * x, np.ones(hop) / hop, 'same')[::hop]) + 1e-6
    o = np.maximum(np.diff(np.log(e)), 0)
    on = [0.0] + [float((i + 1) * hop / SR) for i in np.nonzero(o > 0.9)[0] if (i + 1) * hop / SR > 0.08]
    keep = []
    for t in on:                                         # syllable starts at least 0.1 s apart
        if not keep or t - keep[-1] > 0.1:
            keep.append(t)
    return len(x) / SR, vocal_type(name), root, keep[:16]


def vocal_slice(name, mod, semis, dur):
    """One chop of a voice sample. mod = 'vx:<start s>:<length s>:<r>' (r=1 reversed); semis re-pitches it the
    tape way (down = slower and lower - screwed; up = faster and higher - chipmunk); dur caps it (seconds)."""
    s = load('vocal', name)
    if s is None:
        return np.zeros(10)
    x = s[0]
    try:
        _, a, ln, r = str(mod).split(':')
        a, ln, r = float(a), float(ln), r == '1'
    except ValueError:
        a, ln, r = 0.0, len(x) / SR, False
    seg = x[int(a * SR):int((a + ln) * SR)]
    if len(seg) < 64:
        return np.zeros(10)
    if r:
        seg = seg[::-1]
    ratio = 2 ** (float(semis) / 12)
    n = int(min(len(seg) / ratio, max(0.03, dur) * SR))
    if n < 32:
        return np.zeros(10)
    y = np.interp(np.arange(n) * ratio, np.arange(len(seg)), seg)
    f = min(n // 4, int(0.006 * SR))
    y[:f] *= np.linspace(0, 1, f)
    y[-f * 2:] *= np.linspace(1, 0, f * 2)
    return y


# ----------------------------------------------------------------------------- (2.26) chop a break into a drum kit
def chop_break(pcm, name, sr=SR, as_kit=False):
    """Cut a drum break (any recording of a beat) into its hits and keep the best kick, snare, closed and open hat.

    Onsets: spectral flux on a 5.8 ms hop, peaks at least 55 ms apart. Each slice runs to the next onset (at most
    0.6 s) with a short fade. A slice is scored on its first 60 ms: kick = low end (35-120 Hz) against the rest,
    snare = body (150-400 Hz) + crack (1.5-5 kHz) with little sub, hats = energy above 6 kHz. The loudest clear
    example of each wins; the open hat is the hat that rings longest. They're saved to your drum library as
    '<name> kick' etc. (pick them for any drum voice), and with as_kit also into the kick / snare / hat slots that
    'my samples' plays. Returns {voice: saved name}."""
    from scipy import signal as _sig
    x = np.asarray(pcm, dtype=np.float64)
    if x.ndim > 1:
        x = x.mean(axis=0)
    if len(x) < sr // 4:
        raise ValueError('that recording is too short to chop')
    x = x[: sr * 40]
    hop, nfft = 256, 1024
    f, _, Z = _sig.stft(x, sr, nperseg=nfft, noverlap=nfft - hop)
    S = np.abs(Z)
    flux = np.maximum(np.diff(np.log1p(S * 30), axis=1), 0).sum(axis=0)
    flux = flux - _sig.medfilt(flux, 31)
    thr = max(np.percentile(flux, 75), 0.15 * flux.max())
    peaks, _ = _sig.find_peaks(flux, height=thr, distance=max(1, int(0.055 * sr / hop)))
    on = [max(0, int((p + 1) * hop - 0.004 * sr)) for p in peaks]
    if len(on) < 3:
        raise ValueError('no clear drum hits found in that recording')
    lv = [float(np.sqrt(np.mean(x[a:a + int(0.03 * sr)] ** 2))) for a in on]
    slices = []
    for i, a in enumerate(on):
        # a hit rings until the next hit at least ~60 % as loud (ghost notes and hats riding on its tail don't cut it
        # short), at least 0.12 s, at most 0.6 s
        nxt = next((on[j] for j in range(i + 1, len(on)) if lv[j] >= 0.6 * lv[i]), len(x))
        b = min(max(nxt, a + int(0.12 * sr)), a + int(0.6 * sr), len(x))
        y = x[a:b].copy()
        if len(y) < int(0.03 * sr):
            continue
        k = min(len(y) // 4, int(0.008 * sr))
        y[-k:] *= np.linspace(1, 0, k)
        head = y[: int(0.06 * sr)]
        F = np.abs(np.fft.rfft(head * np.hanning(len(head)), 4096)) ** 2
        fr = np.fft.rfftfreq(4096, 1 / sr)
        band = lambda lo, hi: float(F[(fr >= lo) & (fr < hi)].sum()) + 1e-12
        tot = band(20, sr / 2)
        lvl = float(np.sqrt(np.mean(head ** 2)))
        env = np.abs(_sig.hilbert(y)) if len(y) < sr else np.abs(y)
        ring = float(np.argmax(np.cumsum(env ** 2) > 0.9 * np.sum(env ** 2)) / sr)
        slices.append(dict(y=y, lvl=lvl, ring=ring, kick=band(35, 200) / tot, crack=band(1500, 5000) / tot,
                           body=band(150, 400) / tot, hat=band(6000, sr / 2) / tot))
    if not slices:
        raise ValueError('no clear drum hits found in that recording')
    picks = {}
    # in a real break the hat rides on top of the kick and snare, and sped-up breaks push the kick's thump up to
    # 120-200 Hz: the kick is the loudest slice that is mostly low end, the snare the loudest crack + body with little
    # low end, the hats the bright, quiet slices
    ks = [s for s in slices if s['kick'] > 0.4]
    kick = max(ks, key=lambda s: s['kick'] * s['lvl']) if ks else None
    if kick:
        picks['kick'] = kick['y'][: int(0.5 * sr)]
    rest = [s for s in slices if s is not kick]
    sn = [s for s in rest if s['kick'] < 0.3 and s['crack'] > 0.1]
    snare = max(sn, key=lambda s: (s['crack'] + 0.5 * s['body']) * s['lvl']) if sn else None
    if snare:
        picks['snare'] = snare['y'][: int(0.4 * sr)]
    hats = [s for s in rest if s is not snare and s['hat'] > 0.3 and s['kick'] < 0.1]
    if not hats:                                         # darker recordings (a ride, a worn break): the brightest quarter
        cand = sorted((s for s in rest if s is not snare and s['kick'] < 0.15 and s['hat'] > 0.12), key=lambda s: -s['hat'])
        hats = cand[:max(1, len(cand) // 4)]
    if hats:
        ch = min(hats, key=lambda s: s['ring'])
        picks['chat'] = ch['y'][: int(0.25 * sr)]
        oh = max(hats, key=lambda s: s['ring'])
        if oh is not ch and oh['ring'] > ch['ring'] * 1.6:
            picks['ohat'] = oh['y'][: int(0.6 * sr)]
    if sr != SR:
        from scipy.signal import resample_poly
        picks = {k: resample_poly(v, SR, sr) for k, v in picks.items()}
    base = _safe(name)[:28] or 'break'
    label = {'kick': 'kick', 'snare': 'snare', 'chat': 'hat', 'ohat': 'open hat'}
    out = {}
    for v, y in picks.items():
        out[v] = save('drums', f'{base} {label[v]}', y)
        if as_kit:
            save('drums', v, y)                          # the slot 'my samples' plays
    out['hits'] = len(slices)
    return out
