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
