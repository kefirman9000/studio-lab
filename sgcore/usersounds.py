"""Your own sounds: drum samples that replace the built-in kit, and single-note samples played as instruments."""
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


KINDS = ('drums', 'inst')


def _kind(kind):
    if kind not in KINDS:
        raise ValueError('unknown sound type')
    return kind


def _safe(name):
    return re.sub(r'[^A-Za-z0-9 _-]', '', name).strip()[:40] or 'sound'


def save(kind, name, pcm, root_note=60):
    """kind: 'drums' or 'inst'. pcm: mono float32 at 44.1 kHz."""
    d = os.path.join(ROOT, _kind(kind))
    os.makedirs(d, exist_ok=True)
    name = _safe(name)
    if kind == 'drums' and name not in DRUM_SLOTS:
        raise ValueError('unknown drum slot')
    x = np.asarray(pcm, dtype=np.float32)[: SR * 20]
    if len(x) < 100:
        raise ValueError('sound is too short')
    # trim leading silence, normalise
    nz = np.nonzero(np.abs(x) > 0.01 * (np.max(np.abs(x)) or 1))[0]
    x = x[nz[0]:] if len(nz) else x
    x = x / (np.max(np.abs(x)) or 1.0) * 0.9
    write_wav_float(os.path.join(d, name + '.wav'), np.vstack([x, x]))
    if kind == 'inst':
        with open(os.path.join(d, name + '.root'), 'w') as f:
            f.write(str(int(root_note)))
    _cache.clear()
    return name


def delete(kind, name):
    if kind not in KINDS:
        return
    for ext in ('.wav', '.root'):
        p = os.path.join(ROOT, kind, _safe(name) + ext)
        if os.path.exists(p):
            os.remove(p)
    _cache.clear()


def listing():
    out = {'drums': [], 'inst': []}
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
