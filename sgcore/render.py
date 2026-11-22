"""Rendering: events -> tracks -> mix (sidechain, sends, buses) -> master."""
import hashlib
import json
import math
import os
import random
import sys
import time
import zlib

import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d

from .dsp import (SR, hp, lp, bp, eq, soft, k_weight, compressor, limiter, low_limit, lufs, active_rms_db, make_ir, reverb, pingpong,
                  make_spring_ir, dub_delay, svf_sweep, mtof,
                  sweep_region, write_wav_float)
from .instruments import INSTRUMENTS, DRUMS, fx_riser, fx_impact, fx_vinyl, fx_texture
from . import va as _va
from . import fx2 as _fx2

SYNTH_TAKES = 3          # analog character: takes per (note, length, velocity layer)
from .compose import SECTION_ENERGY, GROOVES
from .guitars2 import RIGS as _GTR_RIGS, guitar_rig as _guitar_rig
from .instruments3 import PART_FX as _PART_FX

HELD = 0.75     # notes held this many beats or longer (pads, sustained chords) are never swung - only short notes swing

ROLE_DB = {'kick': -13, 'snare': -17, 'top': -25, 'bass': -15, 'chords': -21, 'pad': -23, 'arp': -25, 'lead': -19, 'fx': -26}
CUT_KEYS = ('cut', 'bright')


def chorus(buf, mix=0.5, rate=0.8, depth_ms=3.0, base_ms=12.0):
    """Stereo chorus (Juno-style): a slowly wobbling delayed copy, opposite phase left and right."""
    n = buf.shape[1]
    t = np.arange(n, dtype=np.float32) / SR
    out = buf.copy()
    for ch, ph in ((0, 0.0), (1, np.pi)):
        d = (base_ms + depth_ms * np.sin(2 * np.pi * rate * t + ph)) * SR / 1000.0
        src = np.arange(n, dtype=np.float32) - d
        out[ch] = buf[ch] * (1 - 0.35 * mix) + np.interp(src, np.arange(n, dtype=np.float32), buf[ch], left=0.0) * mix * 0.8
    return out.astype(np.float32)


def gated_reverb(x, hold=0.24):
    """80s gated reverb: a dense, bright room tail that's chopped off hard after ~240 ms."""
    n = int((hold + 0.03) * SR)
    rng = np.random.default_rng(7)
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-np.arange(n) / (0.5 * SR)).astype(np.float32)
    ir[0] = 6.0
    from scipy.signal import fftconvolve
    y = fftconvolve(x[:n], ir)[:n].astype(np.float32)
    g = np.ones(n, dtype=np.float32)
    k = int(0.02 * SR)
    g[-k:] = np.linspace(1, 0, k)
    y = y / (np.max(np.abs(y)) + 1e-9) * g
    return y




def track_fx(buf, tcfg, spb):
    """Per-part effect pedals, applied to the whole part like a pedal on its channel:
    phaser   - four all-pass stages swept by a slow LFO with feedback (funk clav / guitar, 70s strings, psych rock)
    flanger  - a very short delay swept 1-6 ms, mixed back in (jet-plane sweeps)
    trem     - amp tremolo synced to the beat: {'rate': beats per cycle, 'depth': 0..1} or a depth (16ths default)
    wah      - an auto-wah: a resonant band-pass that follows the playing's loudness (funk guitar, clavinet)
    crush    - a bit-crusher: fewer bits and a lower sample rate (lo-fi, chip, glitch)
    ott      - a three-band upward / downward squash (dense, forward EDM synths)
    wide     - mid / side widening above 200 Hz with a little Haas, the bass kept mono (pads, supersaws)
    Each value is the amount (0..1) unless noted."""
    x = np.asarray(buf, np.float32)                      # (1.90: 32-bit - half the memory of the old 64-bit chain)
    n = x.shape[1]
    t = (np.arange(n, dtype=np.float64) / SR)
    if tcfg.get('phaser'):
        amt = float(tcfg['phaser'])
        lfo = 0.5 - 0.5 * np.cos(2 * np.pi * 0.35 * t)
        fc = 250 * (3200 / 250) ** lfo
        fb = np.zeros(2)
        blk = 64
        z = np.zeros((4, 2))
        out = np.empty_like(x)
        for s0 in range(0, n, blk):
            e = min(n, s0 + blk)
            w = np.tan(np.pi * fc[s0] / SR)
            a1 = (w - 1) / (w + 1)
            seg = x[:, s0:e] + 0.5 * fb[:, None]
            for st_ in range(4):
                for c in range(2):
                    seg[c], zz = signal.lfilter([a1, 1.0], [1.0, a1], seg[c], zi=[z[st_, c]])
                    z[st_, c] = zz[0]
            out[:, s0:e] = seg
            fb = seg[:, -1]
        y = x + amt * out
        x = y / (1 + amt)
    if tcfg.get('flanger'):
        amt = float(tcfg['flanger'])
        idx = np.arange(n, dtype=float)
        d = (3.5 + 2.5 * np.sin(2 * np.pi * 0.2 * t)) * SR / 1000
        x = np.vstack([x[c] + amt * np.interp(idx - d * (1 if c == 0 else 0.85), idx, x[c], left=0.0) for c in range(2)]) / (1 + amt * 0.6)
    if tcfg.get('trem'):
        tr = tcfg['trem'] if isinstance(tcfg['trem'], dict) else {'depth': float(tcfg['trem'])}
        rate = 1.0 / (float(tr.get('rate', 0.5)) * spb)
        dep = float(tr.get('depth', 0.5))
        x = x * (1 - dep * (0.5 - 0.5 * np.cos(2 * np.pi * rate * t)))[None, :]
    if tcfg.get('wah'):
        amt = float(tcfg['wah'])
        env = np.sqrt(signal.lfilter([0.003], [1, -0.997], (x.mean(axis=0)) ** 2) + 1e-12)
        env = env / (np.percentile(env, 98) + 1e-9)
        fc = 400 * (2600 / 400) ** np.clip(env, 0, 1)
        out = np.empty_like(x)
        blk = 64
        for c in range(2):
            zi = np.zeros(2)
            for s0 in range(0, n, blk):
                e = min(n, s0 + blk)
                b, a = _bp_coeffs(float(fc[s0]), 4.0)
                out[c, s0:e], zi = signal.lfilter(b, a, x[c, s0:e], zi=zi)
        x = x * (1 - amt) + out * amt * 2.5
    if tcfg.get('ott'):                                  # multiband squash ('OTT'): quiet details pulled up, peaks held
        amt = float(tcfg['ott'])                         # down, per band - the dense, forward synth sound of EDM
        bands_ = [(None, 200), (200, 2500), (2500, None)]
        out = np.zeros_like(x)
        for lo_, hi_ in bands_:
            if lo_ is None:
                bnd = signal.sosfiltfilt(signal.butter(2, hi_ / (SR / 2), output='sos'), x, axis=-1)
            elif hi_ is None:
                bnd = signal.sosfiltfilt(signal.butter(2, lo_ / (SR / 2), 'high', output='sos'), x, axis=-1)
            else:
                bnd = signal.sosfiltfilt(signal.butter(2, [lo_ / (SR / 2), hi_ / (SR / 2)], 'band', output='sos'), x, axis=-1)
            k = max(16, int(0.012 * SR))
            env = np.sqrt(np.maximum(uniform_filter1d((bnd ** 2).mean(axis=0), k), 0.0)) + 1e-6
            ref = float(np.percentile(env[env > env.max() * 0.01], 70)) if np.any(env > env.max() * 0.01) else 1.0
            g = np.clip((ref / env) ** (0.5 * amt), 0.25, 4.0)
            out += bnd * g[None, :]
        r0 = np.sqrt(np.mean(x ** 2)) + 1e-9
        x = out * (r0 / (np.sqrt(np.mean(out ** 2)) + 1e-9))
    if tcfg.get('wide'):                                 # mid / side widening above 200 Hz (the low end stays mono)
        amt = float(tcfg['wide'])
        mid_, side_ = (x[0] + x[1]) / 2, (x[0] - x[1]) / 2
        side_ = signal.lfilter(*signal.butter(2, 200 / (SR / 2), 'high'), side_)
        haas = np.concatenate([np.zeros(int(0.011 * SR)), mid_[:-int(0.011 * SR)]])
        hp_h = signal.lfilter(*signal.butter(2, 300 / (SR / 2), 'high'), haas)
        side_ = side_ * (1 + 0.8 * amt) + 0.15 * amt * hp_h
        x = np.vstack([mid_ + side_, mid_ - side_])
    if tcfg.get('crush'):
        amt = float(tcfg['crush'])
        bits = 2 ** (12 - 7 * amt)
        hold = max(1, int(1 + 5 * amt))
        y = np.round(x * bits) / bits
        x = np.repeat(y[:, ::hold], hold, axis=1)[:, :n]
    return x


def _bp_coeffs(fc, q):
    w = 2 * np.pi * min(fc, SR * 0.45) / SR
    al = np.sin(w) / (2 * q)
    return np.array([al, 0, -al]) / (1 + al), np.array([1, -2 * np.cos(w) / (1 + al), (1 - al) / (1 + al)])


def kick_rumble(kick, amount, duck=None):
    """The techno rumble: the kick sent into a long, dark reverb, low-passed to the sub region, driven so it growls,
    high-passed under 35 Hz and ducked by the kick itself - the rolling low-end roar between the kicks (built from the
    kick, so it always sits in its key and its rhythm)."""
    x = np.asarray(kick, np.float64)
    ir = make_ir(2.6, predelay=0.0, bright=0.15)
    wet = reverb(x, ir)[:, :x.shape[1]]
    b, a = signal.butter(4, 190 / (SR / 2))
    wet = signal.lfilter(b, a, wet, axis=-1)
    pk = np.abs(wet).max() + 1e-9
    wet = np.tanh(wet / pk * 3.0) / 3.0 * pk
    b, a = signal.butter(2, 35 / (SR / 2), 'high')
    wet = signal.lfilter(b, a, wet, axis=-1)
    if duck is not None:
        d = np.asarray(duck, np.float64)[:wet.shape[1]]
        wet[:, :len(d)] *= (1 - 0.95 * d)[None, :]
    else:                                                # no sidechain in this genre: duck under the kick's own body
        ke = uniform_filter1d(np.abs(x).max(axis=0), int(0.03 * SR))
        wet *= (1 - 0.9 * np.clip(ke / (ke.max() + 1e-9) * 2.0, 0, 1))[None, :]
    k_rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    w_rms = np.sqrt(np.mean(wet ** 2)) + 1e-9
    return (wet * (k_rms / w_rms) * 0.55 * amount).astype(np.float32)


def hat_choke_env(chat, ohat, fade=0.004):
    """Open-hat choke (as on the drum machines): the open hat's gain drops to zero, over a few ms, the moment a closed
    hat is struck, and comes back for the next open-hat hit."""
    n = ohat.shape[1]
    ca = np.abs(np.asarray(chat, np.float64)).max(axis=0)[:n]
    oa = np.abs(np.asarray(ohat, np.float64)).max(axis=0)[:n]
    thr_c = 0.25 * (ca.max() + 1e-9)
    thr_o = 0.25 * (oa.max() + 1e-9)
    c_on = np.flatnonzero((ca[1:] > thr_c) & (ca[:-1] <= thr_c)) + 1
    o_on = np.flatnonzero((oa[1:] > thr_o) & (oa[:-1] <= thr_o)) + 1
    g = np.ones(n)
    f = max(1, int(fade * SR))
    j = 0
    for c in c_on:
        while j < len(o_on) and o_on[j] <= c:
            j += 1
        if j == 0 and (not len(o_on) or o_on[0] > c):
            continue
        end = o_on[j] if j < len(o_on) else n
        if end - c > f:
            g[c:c + f] = np.minimum(g[c:c + f], np.linspace(1, 0, f))
            g[c + f:end] = 0.0
    return g.astype(np.float32)


TONE_BANDS = ((20, 60), (60, 120), (120, 250), (250, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 8000), (8000, 11000))


def band_balance(x):
    """The tonal balance of the loudest 20 s of a mix: level per band (dB, the loudest band = 0) - measured the same
    way the reference records were."""
    m = np.asarray(x, np.float64).mean(axis=0)
    n = len(m)
    w = min(n, 20 * SR)
    if n > w:
        e = uniform_filter1d(m ** 2, SR)
        s0 = int(np.argmax(np.convolve(e[::SR // 4], np.ones(80), 'valid')) * (SR // 4))
        m = m[s0:s0 + w]
    f, P = signal.welch(m, SR, nperseg=8192)
    db = np.array([10 * np.log10(P[(f >= a) & (f < b)].sum() + 1e-12) for a, b in TONE_BANDS])
    return db - db.max()


def band_balance_quiet(x):
    """(1.86) The tonal balance of a mix's quiet-but-playing part (its breakdown): the quietest 15 s whose level is
    within 18 dB of the loudest. None when the song has no clear quiet part."""
    m = np.asarray(x, np.float64).mean(axis=0)
    hop = SR // 4
    e = uniform_filter1d(m ** 2, SR)[::hop]
    w = 60                                                    # 15 s in quarter-second steps
    if len(e) < w * 3:
        return None
    win = np.convolve(e, np.ones(w) / w, 'valid')
    db = 10 * np.log10(win + 1e-12)
    ok = np.where(db > db.max() - 18)[0]
    if not len(ok):
        return None
    i = ok[np.argmin(db[ok])]
    if db.max() - db[i] < 3:                                  # nothing quieter than the loud part: no quiet section
        return None
    seg = m[i * hop:i * hop + 15 * SR]
    f, P = signal.welch(seg, SR, nperseg=8192)
    out = np.array([10 * np.log10(P[(f >= a) & (f < b)].sum() + 1e-12) for a, b in TONE_BANDS])
    return out - out.max()


def loud_mask(x, span_db=8.0):
    """0..1 per sample: 1 in the song's loud parts, 0 in its quiet parts (2 s smoothing), from the short-term level."""
    m = np.asarray(x, np.float64).mean(axis=0)
    hop = SR // 10
    e = uniform_filter1d(m ** 2, 2 * SR)[::hop]
    db = 10 * np.log10(e + 1e-12)
    top = np.percentile(db, 95)
    k = np.clip((db - (top - span_db)) / (span_db * 0.6), 0, 1)
    return np.interp(np.arange(len(m)), np.arange(len(k)) * hop, k)


def tone_match(x, target, log=print, amount=0.6, limit=3.0):
    """Gentle reference matching: compare the mix's band balance with the genre's reference records and nudge each
    band part of the way there (at most +-3 dB), with broad peaking EQs - the sub with a low shelf, the air with a high
    shelf. Fixes a too-dark or too-thin render without forcing it onto the records."""
    cur = band_balance(x)
    tgt = np.asarray(target, float)
    d = (tgt - tgt.mean()) - (cur - cur.mean())
    d = np.clip(d * amount, -limit, limit)
    for (a, b), g in zip(TONE_BANDS, d):
        if abs(g) < 0.3:
            continue
        fc = float(np.sqrt(a * b))
        if a == 20:
            x = eq(x, 'lowshelf', 60, 0.7, g)
        elif b == 11000:
            x = eq(x, 'highshelf', 8000, 0.7, g)
        else:
            x = eq(x, 'peak', fc, 1.1, g)
    log('   tone match: ' + ' '.join(f'{g:+.1f}' for g in d))
    return x


def loudness_range(y, win=3.0, hop=1.0):
    """EBU R128 loudness range (LRA): the spread between the 10th and 95th percentile of the short-term (3 s)
    loudness, gated at -70 LUFS absolute and 20 LU below the average. Also returns the loudest short-term value."""
    n, h = int(win * SR), int(hop * SR)
    if y.shape[-1] < n * 2:
        L = float(lufs(y))
        return 0.0, L
    from .dsp import k_weight
    k = k_weight(y)
    cs = np.concatenate([[0.0], np.cumsum(np.sum(k ** 2, axis=0))])
    st_ = np.arange(0, k.shape[-1] - n, h)
    z = (cs[st_ + n] - cs[st_]) / n
    lk = -0.691 + 10 * np.log10(z + 1e-12)
    g = lk[lk > -70]
    if len(g) < 3:
        return 0.0, float(np.max(lk))
    rel = -0.691 + 10 * np.log10(np.mean(10 ** ((g + 0.691) / 10))) - 20
    g = g[g > rel]
    return float(np.percentile(g, 95) - np.percentile(g, 10)), float(np.max(lk))


def mix_report(y, song=None, spb=None, tone=None, low_env=None, dyn_eq=None, lead_db=None):
    """Quality check of a finished master - what a mastering engineer looks at:
    loudness (LUFS), true peak (dBTP, 4x oversampled), peak-to-loudness ratio (PLR - how much punch the limiter left),
    loudness range (LRA) and the loudest 3-second moment, stereo correlation (+1 mono ... 0 wide ... <0 phasey),
    how much quieter the song gets folded to mono, low-end mono-compatibility (side energy under 120 Hz), section
    contrast (how much louder the big sections are than the quiet ones), the tonal balance against the genre's
    reference records, and how often the kick and the bass hit the low end at the same moment.
    Returns numbers + plain warnings."""
    from .dsp import lufs as _lufs
    y = np.asarray(y, np.float64)
    L = float(_lufs(y))
    from .dsp import true_peak as _tp
    tp = 20 * np.log10(_tp(y) + 1e-12)
    st_win = int(3 * SR)
    sl = [float(_lufs(y[:, i:i + st_win])) for i in range(0, max(1, y.shape[1] - st_win), st_win)] if y.shape[1] > st_win * 2 else [L]
    plr = tp - L
    m, s_ = (y[0] + y[1]) / 2, (y[0] - y[1]) / 2
    corr = float(np.corrcoef(y[0], y[1])[0, 1]) if np.std(y[0]) > 0 and np.std(y[1]) > 0 else 1.0
    lo_m = signal.sosfilt(signal.butter(4, 120 / (SR / 2), output='sos'), m)
    lo_s = signal.sosfilt(signal.butter(4, 120 / (SR / 2), output='sos'), s_)
    low_side = 10 * np.log10((np.mean(lo_s ** 2) + 1e-12) / (np.mean(lo_m ** 2) + 1e-12))
    good = [v for v in sl if v > -60]
    contrast = (float(np.percentile(good, 90)) - float(np.percentile(good, 20))) if len(good) > 4 else 0.0
    lra, st_max = loudness_range(y)
    mono_drop = L - float(_lufs(np.vstack([m, m])))       # how much loudness goes missing in mono (phasey parts cancel)
    tone_dev = None
    if tone and len(tone) == 9:
        bb = band_balance(y)
        tone_dev = [round(float(a - b), 1) for a, b in zip(bb, tone)]
    kb_overlap = None        # share of the kick hits where the bass's low end is strong at the same moment (info:
    if low_env and low_env.get('kick') is not None and low_env.get('bass') is not None:   # sidechain / dodge handle it)
        k_, b_ = low_env['kick'], low_env['bass']
        n_ = min(len(k_), len(b_))
        k_, b_ = k_[:n_] / (np.max(k_[:n_]) + 1e-9), b_[:n_] / (np.max(b_[:n_]) + 1e-9)
        hit = k_ > 0.5
        kb_overlap = round(float(np.mean(b_[hit] > 0.5)), 2) if np.any(hit) else 0.0
    warn = []
    if tp > -0.9:
        warn.append('true peak above -1 dBTP')
    if plr < 7.5:
        warn.append('very squashed (little punch left)')
    if corr < 0.15:
        warn.append('very wide / phasey stereo - check in mono')
    if mono_drop > 1.5:
        warn.append(f'loses {mono_drop:.1f} dB in mono (wide parts cancel out)')
    if low_side > -12:
        warn.append('stereo low end (bass not mono)')
    if contrast < 2.0 and len(good) > 20:
        warn.append('sections all equally loud (little contrast)')
    if lead_db is not None and lead_db < -3.0:
        warn.append(f'lead buried ({lead_db:+.1f} dB against the chords and pads where it plays)')
    if tone_dev:
        names = ('sub', 'bass', 'low-mids', 'mids', 'upper mids', 'presence', 'highs', 'air', 'top air')
        far = [(names[i], d) for i, d in enumerate(tone_dev) if abs(d) > 4.5 and i < 8]
        if far:
            warn.append('tone vs genre refs: ' + ', '.join(f"{n} {'+' if d > 0 else ''}{d:.0f} dB" for n, d in far[:3]))
    return dict(lufs=round(L, 1), true_peak=round(float(tp), 1), plr=round(float(plr), 1), correlation=round(corr, 2),
                low_side_db=round(float(low_side), 1), section_contrast=round(contrast, 1), lra=round(lra, 1),
                st_max=round(st_max, 1), mono_drop=round(float(mono_drop), 1), tone_dev=tone_dev,
                kick_bass_overlap=kb_overlap, dyn_eq=dyn_eq or {}, lead_over_music_db=lead_db, warnings=warn)


def auto_lp(buf, cut, block=256):
    """A 12 dB low-pass whose cutoff follows `cut` (Hz per sample), in blocks with carried state; blocks where it is
    wide open are (a track that never closes is passed straight through)."""
    from .dsp import biquad
    from . import fastdsp
    n = buf.shape[1]
    if float(np.min(cut[:n])) >= 17500:
        return buf
    if fastdsp.HAVE_NUMBA:                               # (1.82) per sample, one compiled pass: smoother and ~10x faster
        return fastdsp.svf_lp(buf, cut[:n], SR)
    x = np.asarray(buf, np.float64)
    out = x.copy()
    zi = np.zeros((2, 2))
    for s0 in range(0, n, block):
        e = min(n, s0 + block)
        b, a = biquad('lowpass', float(min(cut[s0], SR * 0.45)), 0.707)
        for c in range(2):
            out[c, s0:e], zi[c] = signal.lfilter(b, a, x[c, s0:e], zi=zi[c])
    return out

# ----------------------------------------------------------------------------- (1.92.4) parallel part rendering
# Full songs render their parts on several CPU cores: worker processes each hold a copy of the song and render whole
# parts (with the same per-part random seed as the main process, so the result is identical); the main process mixes
# them in the usual order, asking for at most a few parts ahead so memory stays bounded. Parts that use plugins, your
# own samples, sampled instruments or real drum kits always render in the main process.
_WORKER = {}


def _parent_watch(ppid):
    """(2.5.3) A render worker quits when the engine that started it is gone (killed, crashed, restarted for an
    update) instead of staying behind holding a gigabyte of memory."""
    import os
    import time
    if sys.platform.startswith('win'):
        try:
            import ctypes
            h = ctypes.windll.kernel32.OpenProcess(0x00100000, False, ppid)        # SYNCHRONIZE
            if h:
                ctypes.windll.kernel32.WaitForSingleObject(h, 0xFFFFFFFF)
                os._exit(0)
        except Exception:                                                         # noqa: BLE001
            return
        return
    while True:
        time.sleep(2.0)
        if os.getppid() != ppid:
            os._exit(0)


def _pool_init(song_blob, character):
    import os
    import pickle
    import threading
    threading.Thread(target=_parent_watch, args=(os.getppid(),), daemon=True).start()
    song = pickle.loads(song_blob) if song_blob is not None else _WORKER.get('song')
    _WORKER['r'] = Renderer(song, log=lambda *a: None)
    _va.CHARACTER = character


def _pool_render(name, seed_):
    from . import dsp as _dsp
    r = _WORKER['r']
    tcfg = next(t for t in r.st['tracks'] if t['name'] == name)
    evs = [e for e in r.song['events'] if e.track == name]
    _va._RNG = np.random.default_rng(seed_)
    _dsp.RNG = np.random.default_rng(seed_ + 1)
    buf = np.asarray(r.render_track(tcfg, evs), dtype=np.float32)
    r.cache.clear()
    _trim()
    return buf


def render_workers(length_samples):
    """How many worker processes a render uses: none for short renders (starting them costs more than it saves),
    else up to 3 (one core is left for the app), or STUDIOLAB_WORKERS."""
    env = os.environ.get('STUDIOLAB_WORKERS')
    if env is not None:
        try:
            return max(0, int(env))
        except ValueError:
            pass
    if length_samples < 60 * SR:
        return 0
    return max(0, min(3, (os.cpu_count() or 1) - 1))


MONO_FADE = int(0.006 * SR)                                  # the bass retrigger crossfade (6 ms)
MONO_RAMP = (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, MONO_FADE))).astype(np.float32)
MONO_SAME = int(0.002 * SR)                                  # notes this close together count as one chord
_DC_IN = int(0.0012 * SR)                                     # (2.9.1) de-click: a 1.2 ms fade into every bass note
_DC_OUT = int(0.004 * SR)                                     # and a 4 ms fade at the very end of every pitched note
_DC_IN_RAMP = (np.sin(np.linspace(0, np.pi / 2, _DC_IN)) ** 2).astype(np.float32)
_DC_OUT_RAMP = (np.cos(np.linspace(0, np.pi / 2, _DC_OUT)) ** 2).astype(np.float32)


def declick(sig, start=True):
    """(2.9.1) Notes that started on a non-zero sample or were cut off mid-wave (many synth basses' last sample was
    still 5-50 % of their peak) clicked at their start and end - heard as a 'clipping' tick on every note. Every pitched
    note now ends in a 4 ms fade, and bass notes also start with a 1.2 ms one (too short to soften a pluck)."""
    if sig is None or sig.shape[-1] < 4 * (_DC_IN + _DC_OUT):
        return sig
    sig = np.array(sig, dtype=np.float32, copy=True)
    sig[..., -_DC_OUT:] *= _DC_OUT_RAMP
    if start:
        sig[..., :_DC_IN] *= _DC_IN_RAMP
    return sig


class Renderer:
    def __init__(self, song, log=print):
        self.song = song
        self.st = song['st']
        self.opts = song['opts']
        self.spb = 60.0 / song['bpm']
        self.log = log
        self.cache = {}
        self._tm = song.get('tempo_map')                    # through-composed scores: tempo changes along the story
        self._tgrid = None
        if self._tm:
            from .windows import tempo_seconds
            beats = np.arange(0.0, song['total_bars'] * 4 + 64.0, 1 / 16)
            self._tgrid = (beats, np.array([tempo_seconds(self._tm, b) for b in beats]))
        self.length = int((self._bt(song['total_bars'] * 4) + 4.0 + self._rubato(song['total_bars'] * 4)
                           + (6.0 if self._tm else 0.0)) * SR)
        self.hrng = random.Random(song['seed'] + 99)
        self.bright = 2 ** (float(self.opts.brightness) * 1.2)
        self.track_gains = {}

    def t_of(self, beat, human=True, layer=None, swing=True, track=None):
        st = self.st
        b = beat
        feel = (st.get('track_feel') or {}).get(track) if track else None
        if feel:                                        # each drum sound its own feel: hats swing harder than the
            sw_x, ms = feel                             # kick, shakers push ahead, rims sit back (house groove)
            q = beat * 4
            if abs(q - round(q)) < 1e-6 and int(round(q)) % 2 == 1:
                b += sw_x * 0.25
            b += ms / 1000.0 / self.spb
        g = GROOVES.get(st.get('groove')) if layer else None
        if g and layer in g:                            # genre timing feel (e.g. lazy late snares, pushed Afro hats)
            q16 = beat * 4
            if abs(q16 - round(q16)) < 1e-6:
                amt = min(1.5, max(0.0, float(getattr(self.opts, 'humanize', 1.0))))
                b += g[layer][int(round(q16)) % 16] * 0.25 * amt
        unit = st.get('swing_unit', 16)
        q = beat * (4 if unit == 16 else 2)
        if swing and abs(q - round(q)) < 1e-6 and int(round(q)) % 2 == 1:
            b += (st['swing'] - 0.5) * (0.5 if unit == 16 else 1.0)
        t = self._bt(b) + self._rubato(beat)
        if human and st.get('human'):
            # deterministic per position, so editing one section never shifts the feel of another
            t += random.Random(self.song['seed'] * 1000003 + int(round(beat * 960))).gauss(0, st['human'])
        return max(0.0, t)

    def _bt(self, b):
        """Seconds at beat b (strict time, no rubato / humanising)."""
        if self._tgrid is None:
            return b * self.spb
        return float(np.interp(b, self._tgrid[0], self._tgrid[1], left=b * self.spb))

    def _dsec(self, beat, dur):
        return dur * self.spb if self._tgrid is None else max(0.01, self._bt(beat + dur) - self._bt(beat))

    def _rubato(self, beat):
        """Romantic-style rubato: each 4-bar phrase pushes a little, then broadens into its cadence (seconds added)."""
        R = float(self.st.get('rubato') or 0.0)
        if not R:
            return 0.0
        span = 16.0
        n, p = divmod(beat, span)
        p /= span
        E = R * span * self.spb * 0.07                  # how much later each phrase ends than strict time
        return n * E + E * p ** 4 + R * self.spb * 0.12 * math.sin(2 * math.pi * p) * (1 - p)

    def _params(self, tcfg):
        p = dict(tcfg['p'])
        p['spb'] = self.spb
        k_ = self.song.get('key') if isinstance(self.song, dict) else None
        if k_ is not None and hasattr(k_, 'scale'):     # (1.92) sounds that stack intervals keep them in the key
            p.setdefault('key_pcs', tuple(sorted({(k_.root + s_) % 12 for s_ in k_.scale})))
            if tcfg['inst'] in ('uilleann', 'gaita', 'smallpipes'):   # (2.5.0) the pipes' drones sit on the song's key
                p.setdefault('drone_root', float(mtof(36 + k_.root)))
        if self.bright != 1.0:
            for k in CUT_KEYS:
                if k in p:
                    p[k] = p[k] * self.bright
            if 'cut' not in p and tcfg['inst'] in ('supersaw', 'warmpad', 'stab', 'pluck_saw', 'leadsaw', 'sawbass', 'strings', 'brass'):
                p['cut'] = {'supersaw': 3000, 'warmpad': 1100, 'stab': 5000, 'pluck_saw': 6000, 'leadsaw': 5000,
                            'sawbass': 2200, 'strings': 3200, 'brass': 3800}[tcfg['inst']] * self.bright
        return p

    def _note(self, tcfg, ev, p):
        dur = round(self._dsec(ev.beat, ev.dur), 3)
        if tcfg['inst'] == 'voxsample':                  # your voice sample, chopped / stuttered / screwed
            from .usersounds import vocal_slice
            key = ('vx', ev.midi, dur, ev.mod)
            if key not in self.cache:
                y = vocal_slice(tcfg['p'].get('sample', ''), ev.mod, (ev.midi or 60) - 60, dur).astype(np.float32)
                self.cache[key] = np.vstack([y, y])
            return self.cache[key]
        if tcfg['inst'].startswith('real:'):
            sig = self._real(tcfg, ev, dur)
            if sig is not None:
                return sig
            alt = tcfg.get('real_from') or ''
            tcfg = dict(tcfg, inst=alt if alt.startswith('sf:') else (tcfg.get('fallback') or 'pluck_saw'), p={})
            p = self._params(tcfg)
        if tcfg['inst'].startswith('sf:'):
            return self._sampled(tcfg, ev, dur, p)
        user = tcfg['inst'].startswith('user:')
        if _va.analog() and not user:
            # every note its own take: one of three velocity layers (soft / medium / hard - the tone changes, not only
            # the level) x one of SYNTH_TAKES takes, alternating along the part, so repeated notes are never the
            # identical waveform (the 'machine-gun', MIDI-file sound of copy-pasted notes)
            v_ = float(ev.vel)
            vl = 0.6 if v_ < 0.72 else (0.8 if v_ < 0.9 else 1.0)
            take = (int(round(ev.beat * 4)) * 7 + int(ev.midi or 0)) % SYNTH_TAKES
            key = (tcfg['name'], ev.midi, dur, ev.glide, ev.mod, vl, take)
        else:
            vl, key = None, (tcfg['name'], ev.midi, dur, ev.glide, ev.mod)
        sig = self.cache.get(key)
        if sig is None:
            fn = INSTRUMENTS.get(tcfg['inst'])
            if fn is None and user:
                from .usersounds import sampler
                fn = sampler(tcfg['inst'][5:])
            if vl is not None:
                _va.NOTE = {'vel': vl}
                try:
                    sig = fn(ev.midi, dur, dict(p, vel=vl), ev.glide, ev.mod).astype(np.float32)
                finally:
                    _va.NOTE = None
            else:
                sig = fn(ev.midi, dur, p, ev.glide, ev.mod).astype(np.float32)
            self.cache[key] = sig
        return sig

    def _real(self, tcfg, ev, dur):
        """Multi-sampled orchestra: nearest recorded note, velocity layer, round robin, articulation by note length."""
        from . import samplelibs as sl
        vel = max(0.05, min(1.0, ev.vel))
        vb = round(vel * 8) / 8
        rr = int(round(ev.beat * 4) * 7 + ev.midi) % 4
        key = ('real', tcfg['name'], ev.midi, dur, vb, rr)
        sig = self.cache.get(key)
        if sig is None:
            try:
                sig = sl.orch_note(tcfg['inst'][5:], int(ev.midi), dur, vb, f'{rr}')
            except Exception as e:
                if not getattr(self, '_real_warned', False):
                    self.log(f'   real instrument unavailable ({e}) - using the fallback sound')
                    self._real_warned = True
                sig = None
            if sig is None:
                return None
            self.cache[key] = sig
        return sig

    def _real_drum(self, inst, ev, idx, kit=None):
        """Real kit / percussion hit with a velocity layer and a different take each time (None: not available).
        `kit`: this hit comes from another real kit than the song's (a kick you picked from a different kit)."""
        from . import samplelibs as sl
        perc = self.st.get('real_perc')
        rs = None if kit else self.st.get('real_snare')
        kit = kit or self.st.get('real_kit')
        name = None
        if kit and inst == 'snare' and rs and sl.has(rs + ':snare', 'hit'):
            name = rs + ':snare'                           # a kit with a different snare (e.g. a crisp piccolo for DnB)
        elif kit and inst in sl.KIT_PARTS and inst != 'clap':
            name = kit + ':' + sl.KIT_PARTS[inst]
        elif inst == 'clap' and kit and perc:
            name = 'clap'
        elif perc and inst in sl.PERC:
            name = sl.PERC[inst]
        elif perc and inst == 'cowbell808' and self.st.get('real_cowbell'):
            name = 'cowbell'                                # latin styles: a real campana, not an 808
        if not name:
            return None
        from . import samplelibs as _sl
        if kit and name.startswith(kit + ':') and not _sl.has(name, 'hit') and _sl.has('studio:' + name.split(':', 1)[1], 'hit'):
            name = 'studio:' + name.split(':', 1)[1]          # a kit without cymbals borrows the studio kit's
        vb = round(max(0.05, min(1.0, ev.vel)) * 6) / 6
        key = ('realdrum', name, vb, idx % 4)
        sig = self.cache.get(key, False)
        if sig is False:
            try:
                sig = clean_hit(sl.hit(name, vb, f'{idx % 4}'))
                if sig is not None and name.split(':')[0] in KIT_EQ and inst in KIT_EQ[name.split(':')[0]]:
                    sig = kit_eq(sig, KIT_EQ[name.split(':')[0]][inst])
                if sig is not None and inst in ('kick', 'snare'):
                    sig = tame_transient(sig, 13.0 if inst == 'kick' else 15.0, 6.0)
                semis = float(self.st.get('break_pitch') or 0.0)
                ob = self.st.get('break_orig_bpm')
                if ob and self.st.get('break_seq') and inst in ('kick', 'snare', 'ride', 'chat', 'ohat', 'crash'):
                    # a sped-up record: every 10% faster is ~1.6 semitones higher (half of it - real jungle also re-tuned)
                    semis += max(-3.0, min(5.0, 0.5 * 12 * math.log2((60.0 / self.spb) / ob)))
                bs_ = self.st.get('break_sampler') or (None, None)
                if sig is not None and self.st.get('break_seq') and (bs_[0] or bs_[1]) and inst in ('kick', 'snare', 'ride', 'chat', 'ohat', 'crash'):
                    sig = crush(sig, int(bs_[0] or 16), float(bs_[1] or SR)).astype(np.float32)
                if sig is not None and semis and kit and name.split(':')[0] in (kit, rs):
                    # breaks: the kit tuned up / down like a sped-up / slowed record
                    r = 2 ** (semis / 12.0)
                    pos = np.arange(0, len(sig) - 1, r)
                    i0 = pos.astype(np.int64)
                    fr = (pos - i0).astype(np.float32)
                    sig = (sig[i0] * (1 - fr) + sig[i0 + 1] * fr).astype(np.float32)
            except Exception:
                sig = None
            self.cache[key] = sig
        return sig

    def _sampled(self, tcfg, ev, dur, p):
        """Real recorded instrument from the sound library; velocity changes the tone, not just the level.
        Orchestral sounds get a performance pass: section width, expression swells and round-robin variation."""
        from . import soundfont as sfm
        vel = int(min(127, max(24, round((30 + 92 * min(1.1, ev.vel)) / 12) * 12)))
        name = tcfg['inst'][3:]
        rr = 0
        if name in sfm.PERFORMED:                       # round robin: 3 takes per note, picked by position in the song
            rr = int(round(ev.beat * 4) + ev.midi) % 3
        key = (tcfg['name'], ev.midi, dur, vel, rr)
        sig = self.cache.get(key)
        if sig is None:
            try:
                sig = sfm.sampled_note(name, ev.midi, dur, vel)
                if name in sfm.PERFORMED:
                    sig = sfm.perform(name, sig, dur, vel, rr)
                a = (p or {}).get('a', 0) if (p or {}).get('a', 0) > 0.04 else 0
                if a:
                    n = min(sig.shape[1], int(a * SR))
                    sig[:, :n] *= np.linspace(0, 1, n, dtype=np.float32) ** 1.5
                sig = sig.astype(np.float32)
            except Exception as e:
                fb = tcfg.get('fallback') or sfm.fallback_for(name)
                if not getattr(self, '_sf_warned', False):
                    self.log(f'   sampled instrument unavailable ({e}) - using built-in sounds')
                    self._sf_warned = True
                fn = INSTRUMENTS.get(fb) or INSTRUMENTS['pluck_saw']
                sig = fn(ev.midi, dur, self._params(dict(tcfg, inst=fb, p={})), ev.glide, ev.mod).astype(np.float32)
            self.cache[key] = sig
        return sig

    def _sampled_drum(self, inst):
        kit = self.st.get('sampled_kit')
        if not kit:
            return None
        from . import soundfont as sfm
        try:
            if inst in ('timp', 'timpani'):
                root = self.song['key'].root
                m = 41 + ((root - 41) % 12)                    # tonic, in the timpani's range
                return sfm.sampled_note('timpani', m, 1.2, 112).mean(axis=0)
            if inst == 'taiko':
                return sfm.sampled_note('taikodrum', 40, 1.2, 120).mean(axis=0)
            if inst == 'crash' and kit == 'orchestra':
                return sfm.sampled_drum('crash', 'orchestra')
            return sfm.sampled_drum(inst, kit)
        except Exception:
            return None

    ROUND_ROBIN = ('chat', 'ohat', 'clap', 'snare', 'shaker', 'ride', 'rim')

    def _drum_accent(self, name, sig, vel):
        """Drum-machine accent (analog character): a harder hit is brighter as well as louder - the noise and the top
        of the hit come up, a soft one is duller. Three layers per take, cached."""
        vl = 0 if vel < 0.62 else (1 if vel < 0.88 else 2)
        if vl == 1:
            return sig
        key = ('acc', name, id(sig), vl)
        y = self.cache.get(key)
        if y is None:
            top = hp(sig, 4500).astype(np.float32)
            y = (sig + top * np.float32(0.6 if vl == 2 else -0.45)).astype(np.float32)
            self.cache[key] = y
            self.cache[('acc_ref', name, id(sig))] = sig      # keep the source alive so its id() stays unique
        return y

    def _drum(self, name, inst=None, var=0):
        """One drum hit. Noisy hits (hats, claps, snares, shakers ...) come in three takes that the pattern cycles
        through (round robin) - a real drum machine's noise is never the same twice, and one frozen sample repeated
        16 times a bar is the 'machine-gun' sound of cheap programming. Kicks and toms stay one take."""
        inst = inst or name
        if var and inst in self.ROUND_ROBIN and not getattr(self.opts, 'user_drums', False) and not self.st.get('sampled_kit'):
            key = ('drum', name, var)
            sig = self.cache.get(key)
            if sig is None:
                self._drum(name, inst)                            # make sure take 0 exists first (stable order)
                saved = self.cache.pop(('drum', name))
                try:
                    sig = self._drum(name, inst)
                finally:
                    self.cache[('drum', name)] = saved
                self.cache[key] = sig
            return sig
        sig = self.cache.get(('drum', name))
        if sig is None:
            user = None
            if getattr(self.opts, 'user_drums', False):
                from .usersounds import drum
                user = drum(inst)
            if user is None:
                user = self._sampled_drum(inst)
            if user is not None:
                sig = user
            else:
                kitp = dict(self.st.get('kitparams', {}).get(inst, {}))
                kitp.update(self.st.get('drum_voice', {}).get(name, {}))     # e.g. high / mid / low toms
                sig = DRUMS[inst](kitp)
                if kitp.get('bits') or kitp.get('srate'):         # sample-based drum machines: their low bit depth / rate
                    sig = crush(sig, int(kitp.get('bits') or 16), float(kitp.get('srate') or SR))
            sig = (sig / (np.max(np.abs(sig)) + 1e-9)).astype(np.float32)
            k = min(len(sig) // 4, int(0.006 * SR))          # never end a hit on a click
            if k > 1:
                sig = sig.copy()
                sig[-k:] *= np.linspace(1.0, 0.0, k, dtype=np.float32)
            if self.st.get('gated_snare') and inst in ('snare', 'clap'):
                sig = gated_reverb(sig)
            self.cache[('drum', name)] = sig
        return sig

    @staticmethod
    def _add(buf, sig, s):
        if s >= buf.shape[1]:
            return
        if sig.ndim == 1:
            n = min(len(sig), buf.shape[1] - s)
            buf[0, s:s + n] += sig[:n]
            buf[1, s:s + n] += sig[:n]
        else:
            n = min(sig.shape[1], buf.shape[1] - s)
            buf[:, s:s + n] += sig[:, :n]

    def _mono_flush(self, buf, pend, cut):
        """Add the held bass note(s), cut at the next note's start `cut` with a short fade (a mono synth's retrigger)."""
        for sig, s0 in pend:
            if cut is not None:
                keep = cut - s0
                if keep <= 0:
                    continue
                if sig.shape[-1] > keep:
                    k = min(sig.shape[-1], keep + MONO_FADE)
                    sig = sig[..., :k].copy()
                    sig[..., keep:k] *= MONO_RAMP[:k - keep]
            self._add(buf, sig, s0)

    def render_track(self, tcfg, evs):
        buf = np.zeros((2, self.length), dtype=np.float32)
        if tcfg['inst'] == 'vinyl':
            buf[:] = fx_vinyl(self.length)
            return buf
        if tcfg['inst'] == 'sung':                            # sung vocals: the whole line at once (the singer phrases it)
            from .daisy import sing_part
            p = tcfg.get('p') or {}
            notes = sorted(((self.t_of(e.beat, human=False), max(0.1, self._dsec(e.beat, e.dur) * 0.97), e.midi)
                            for e in evs if e.midi is not None), key=lambda x: x[0])
            y = sing_part(notes, p.get('style', 'ooh'), p.get('voice', 'female'), p.get('lyrics', ''), seed=self.song['seed'])
            if y is not None:
                n = min(self.length, y.shape[1])
                buf[:, :n] = y[:, :n] * 0.5
            return buf
        if tcfg['inst'] in ('gaita', 'smallpipes'):           # (2.5.1) the other bagpipes: the same reed model
            from .celtic import other_pipes
            notes = sorted(((self.t_of(e.beat, human=False), max(0.03, self._dsec(e.beat, e.dur)), e.midi)
                            for e in evs if e.midi is not None), key=lambda x: x[0])
            buf[:] = other_pipes(notes, self.length, getattr(self.song.get('key'), 'root', None),
                                 'gaita' if tcfg['inst'] == 'gaita' else 'small')
            return buf
        if tcfg['inst'] in ('bagpipe', 'bagpipe_bright', 'bagpipe_drones'):    # (2.4.3) the pipes: one continuous reed per phrase, unbroken drones
            from .celtic import drone_part
            notes = sorted(((self.t_of(e.beat, human=False), max(0.03, self._dsec(e.beat, e.dur)), e.midi)
                            for e in evs if e.midi is not None), key=lambda x: x[0])
            if tcfg['inst'] in ('bagpipe', 'bagpipe_bright'):
                from .celtic import pipe_band
                k_ = self.song.get('key')
                buf[:] = pipe_band(notes, self.length, getattr(k_, 'root', None), int(self.st.get('pipers') or 1),
                                   bright=tcfg['inst'] == 'bagpipe_bright')
            else:
                buf[:] = drone_part(notes, self.length, getattr(self.song.get('key'), 'root', None))
            return buf
        if tcfg['inst'] == 'texture':
            # (2.9.1) the background texture is no longer the same washing-waves noise in every song: about half the
            # songs have none, the others get one of a few kinds (unless a genre insists on its own)
            kind = self.st.get('texture_kind') or ['none', 'none', 'none', 'none', 'waves', 'air', 'rain', 'vinyl']
            if isinstance(kind, (list, tuple)):              # (2.9.9) a genre can give its own list to pick from
                kind = random.Random(self.song['seed'] * 31 + 11).choice(list(kind))
            self.song['texture_kind'] = kind
            if kind == 'none':
                return buf
            if kind == 'vinyl':
                buf[0] = fx_vinyl(self.length) * 0.4
                buf[1] = fx_vinyl(self.length) * 0.4
                return buf
            for c in range(2):
                if kind == 'air':                           # a soft high breath that swells very slowly
                    t = np.arange(self.length) / SR
                    x = bp(np.random.default_rng(self.song['seed'] + c).standard_normal(self.length), 3000, 9000) * 0.5
                    buf[c] = x * (0.4 + 0.6 * np.sin(2 * np.pi * t / 23.0 + c) ** 2)
                elif kind == 'wind':                        # (2.9.9) wind: low, slowly gusting band-passed noise
                    t = np.arange(self.length) / SR
                    rng_ = np.random.default_rng(self.song['seed'] * 5 + c)
                    gust = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * t / (9.0 + 2 * c) + c)) ** 2
                    buf[c] = (lp(bp(rng_.standard_normal(self.length), 150, 1400), 900) * 0.9 +
                              bp(rng_.standard_normal(self.length), 1800, 4500) * 0.08) * gust
                elif kind == 'fire':                        # (2.9.9) fire: a warm roar with crackles and pops
                    rng_ = np.random.default_rng(self.song['seed'] * 7 + c)
                    roar = lp(rng_.standard_normal(self.length), 500) * 0.35
                    pops = np.zeros(self.length)
                    hits = rng_.random(self.length) < 0.0005
                    pops[hits] = rng_.standard_normal(int(hits.sum())) * rng_.random(int(hits.sum()))
                    buf[c] = roar + bp(pops, 800, 6000) * 2.5
                elif kind == 'rain':                        # light rain: a soft bed and scattered drops
                    rng_ = np.random.default_rng(self.song['seed'] * 3 + c)
                    bed = bp(rng_.standard_normal(self.length), 1500, 7000) * 0.25
                    drops = np.zeros(self.length)
                    hits = rng_.random(self.length) < 0.0009
                    drops[hits] = rng_.standard_normal(int(hits.sum()))
                    buf[c] = bed + bp(drops, 2000, 9000) * 1.5
                else:
                    buf[c] = fx_texture(self.length)
            return buf
        if tcfg['inst'].startswith('vst:') and not evs:
            return buf
        if tcfg['inst'].startswith('vst:'):
            out = self._render_vst(tcfg, evs)
            if out is not None:
                return out
            tcfg = dict(tcfg, inst=tcfg.get('fallback') or 'pluck_saw', p={})
        is_drum = tcfg['inst'] in DRUMS
        p = None if is_drum else self._params(tcfg)
        if tcfg.get('touch'):                                 # a lighter (or heavier) touch: softer velocity layers
            t_ = float(tcfg['touch'])
            evs = [e.copy(vel=max(0.05, min(1.0, e.vel * t_))) for e in evs]
        kick = self.st.get('kick_track', 'kick')
        from .drumkits import voice_of
        vce = voice_of(tcfg['name'], tcfg['inst']) if is_drum else None
        vreal = (self.st.get('voice_real') or {}).get(vce)       # (1.84) this voice comes from another (real) kit
        real_drums = is_drum and (self.st.get('real_kit') or self.st.get('real_perc') or vreal) and not tcfg.get('synth') \
            and vce not in (self.st.get('voice_synth') or ())
        brk = self.st.get('break_seq') or {}
        # kicks are never humanised (a layered kick would flam), and a break plays as one tight unit
        tight = tcfg['name'] == kick or tcfg['layer'] == 'kick' or tcfg['name'] in brk or tcfg['name'] in ('lkick', 'lsnare')
        # (1.96) bass plays monophonic, like a mono synth: a new note cuts the one before it (a short crossfade), so
        # release tails never stack under the next note - stacked tails doubled the level at every note change (clipped
        # starts / ends) and two detuned bass notes at once phased and glitched
        mono = not is_drum and tcfg['layer'] == 'bass' and not tcfg.get('poly')
        if mono:
            evs = sorted(evs, key=lambda e: e.beat)
        pend = []
        for i, ev in enumerate(evs):
            s = int((self.t_of(ev.beat, human=not tight, layer=tcfg['layer'], swing=is_drum or ev.dur < HELD, track=tcfg['name'])
                     + getattr(ev, 'strum', 0.0) * self.spb) * SR)
            sig = None
            if real_drums:
                sig = self._real_drum(tcfg.get('real') or tcfg['inst'], ev, i, kit=vreal)
            if sig is None:
                sig = self._drum(tcfg['name'], tcfg['inst'], var=(int(round(ev.beat * 4)) * 5 + int(ev.vel * 7)) % 3) \
                    if is_drum else self._note(tcfg, ev, p)
                if is_drum and sig is not None and _va.analog() and tcfg['name'] != kick and tcfg['layer'] != 'kick':
                    sig = self._drum_accent(tcfg['name'], sig, ev.vel)
            if is_drum and ev.mod and sig is not None:      # break edits: reversed / re-pitched / cut-short hits
                sig = drum_mod(sig, ev.mod)
                if ev.mod == 'rev':                         # a reversed hit swells INTO its beat and ends on it
                    s = max(0, s - sig.shape[-1])
            if ev.mod == 'pm' and tcfg['inst'].startswith('real:') and sig is not None:   # palm mute on the recorded guitar
                sig = lp(hp(sig, 70), 1300).astype(np.float32)
                k = sig.shape[-1]
                sig = sig * np.exp(-np.arange(k) / (0.07 * SR)).astype(np.float32)
            if getattr(ev, 'slide', 0) and not is_drum:          # slide / bend up into the note
                sig = pitch_slide(sig, float(ev.slide), min(0.22, max(0.07, self._dsec(ev.beat, ev.dur) * 0.3)))
            if getattr(ev, 'bend', None) and not is_drum and sig is not None:   # meend / gamak / andolan
                sig = pitch_curve(sig, ev.bend, self._dsec(ev.beat, ev.dur))
            if tcfg.get('vibfx') and not is_drum and ev.dur >= 0.75:   # expressive delayed vibrato on held notes (sax, voice)
                sig = pitch_vibrato(sig, float(tcfg['vibfx']), self._dsec(ev.beat, ev.dur))
            if tcfg.get('swell') and not is_drum and ev.dur >= 2:     # bowed / blown swell: the note grows out of nothing
                n = min(sig.shape[-1], int(self._dsec(ev.beat, ev.dur) * float(tcfg['swell']) * SR))
                if n > 16:
                    sig = sig.copy()
                    sig[..., :n] *= (np.linspace(0.08, 1.0, n, dtype=np.float32) ** 1.6)
            if not is_drum and sig is not None:
                sig = declick(sig, start=tcfg['layer'] == 'bass')
            if mono and sig is not None:
                if pend and s > pend[0][1] + MONO_SAME:
                    self._mono_flush(buf, pend, s)
                    pend = []
                pend.append((sig * ev.vel, s))
                continue
            self._add(buf, sig * ev.vel, s)
        if pend:
            self._mono_flush(buf, pend, None)
        if self.st.get('sampler') and tcfg['layer'] in ('chords', 'lead', 'arp', 'pad') and np.any(buf):
            buf = sp1200(buf)                             # the sampled-loop grit of an SP-1200 / MPC
        if tcfg['inst'] in _GTR_RIGS and np.any(buf):    # (2.0) the guitar's rig on the whole part: chords distort together
            rig = dict(_GTR_RIGS[tcfg['inst']])
            if tcfg.get('amp'):
                rig['gain'] = float(tcfg['amp'])
            if tcfg['layer'] == 'lead':
                rig['width'] = min(float(rig.get('width', 1.0)), 0.35)   # a solo is one player, not a wall
                rig.pop('gate', None)
            rig.update(tcfg.get('rig') or {})
            buf = _guitar_rig(buf, rig, self.spb)
        elif tcfg['inst'] in _PART_FX and np.any(buf):  # (2.6) whole-part effects: the organs' rotary speaker
            buf = _PART_FX[tcfg['inst']](buf, tcfg, self.spb)
        elif tcfg.get('amp') and (tcfg['inst'].startswith('real:') or tcfg['inst'] in ('guitar', 'mutedgtr')):
            buf = guitar_amp(buf, float(tcfg['amp']))
        if tcfg.get('drive'):
            buf = (soft(buf * (1 + tcfg['drive'] * 3), 1.5) / (1 + tcfg['drive'])).astype(np.float32)
        if tcfg.get('gate'):
            buf = self._gate(buf, tcfg['gate'])
        if tcfg.get('chorus'):
            buf = chorus(buf, float(tcfg['chorus']))
        if any(tcfg.get(k) for k in ('phaser', 'flanger', 'trem', 'wah', 'crush', 'wide', 'ott')) and np.any(buf):
            buf = track_fx(buf, tcfg, self.spb).astype(np.float32)
        if tcfg.get('motion') and np.any(buf):           # (2.2.2) bar-long rises, sinks and alien moves (switch-up bass)
            from .alienfx import apply_motion
            buf = apply_motion(buf, tcfg['motion'], self)
        if tcfg.get('sweep') and np.any(buf):             # techno: a filter that opens and closes over 16-32 bars
            lo_hz, hi_hz, bars = tcfg['sweep']
            n = buf.shape[1]
            t = np.arange(n) / SR
            period = max(1.0, bars * 4 * self.spb)
            cut = lo_hz * (hi_hz / lo_hz) ** (0.5 - 0.5 * np.cos(2 * np.pi * t / period))
            buf = np.vstack([svf_sweep(buf[c], cut, q=0.9) for c in range(buf.shape[0])]).astype(np.float32)
        if tcfg['name'] == self.st.get('kick_track', 'kick') and self.st.get('rumble') and np.any(buf):
            buf = self._rumble(buf, float(self.st['rumble']))
        if tcfg.get('leslie_fx') and tcfg['inst'] not in _PART_FX and np.any(buf):   # (the new organs spin their own)
            buf = leslie(buf, float(tcfg['leslie_fx']), float(tcfg.get('overdrive', 0.0)))
        if any(tcfg.get(k) for k in _fx2.KEYS) and np.any(buf):    # 1.78 pedals (sgcore.fx2)
            buf = _fx2.apply(buf, tcfg, self)
        return buf

    def _gate(self, buf, pattern):
        """Trance gate: the part is chopped to a 16th-note pattern during drops (breakdowns stay open)."""
        steps = [c != '.' for c in pattern]
        env = np.ones(self.length, dtype=np.float32)
        sm = int(0.004 * SR)
        for sec in self.song.get('sections', []):
            if not (sec['opts'].get('drop') or sec['name'] in ('drop', 'chorus', 'climax')):
                continue
            b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
            k = 0
            beat = b0
            while beat < b1:
                a = int(self.t_of(beat, human=False) * SR)
                z = int(self.t_of(beat + 0.25, human=False) * SR)
                if a >= self.length:
                    break
                z = min(z, self.length)
                if not steps[k % len(steps)]:
                    seg = np.full(z - a, 0.08, dtype=np.float32)
                    r = min(sm, len(seg) // 2)
                    if r:
                        seg[:r] = np.linspace(1, 0.08, r)
                        seg[-r:] = np.linspace(0.08, 1, r)
                    env[a:z] = seg
                k += 1
                beat += 0.25
        return buf * env

    def _render_vst(self, tcfg, evs):
        """Play this part through one of your own VST3/AU instruments (falls back to the built-in sound on failure)."""
        from . import vsthost
        sid = tcfg['inst'][4:]
        events = [(self.t_of(e.beat, human=True, layer=tcfg['layer'], swing=e.dur < HELD) + getattr(e, 'strum', 0.0) * self.spb, max(0.02, self._dsec(e.beat, e.dur)), int(e.midi), int(max(1, min(127, e.vel * 110))))
                  for e in evs if e.midi is not None]
        ccs = None
        curve = (self.song.get('expr') or {}).get(tcfg['name'])
        if curve:
            snd = vsthost.get_sound(sid) or {}
            if not snd.get('auto'):                    # your own saved sounds (orchestra libraries): dynamics on CC1
                ccs = [(0.0, 11, 100)] + [(self.t_of(b, human=False), 1, v) for b, v in curve]
        try:
            t0 = time.time()
            audio = vsthost.render(sid, events, self.length / SR, ccs=ccs)
            buf = np.zeros((2, self.length), dtype=np.float32)
            n = min(self.length, audio.shape[1])
            buf[:, :n] = audio[:2, :n] if audio.shape[0] >= 2 else np.vstack([audio[0, :n], audio[0, :n]])
            if np.max(np.abs(buf)) < 1e-6:
                raise RuntimeError('the plugin produced silence')
            self.log(f'   {tcfg["name"]}: rendered with your plugin ({time.time() - t0:.1f}s)')
            return buf
        except Exception as e:
            self.log(f'   {tcfg["name"]}: plugin failed ({e}) - using the built-in sound instead')
            self.vst_failures = getattr(self, 'vst_failures', []) + [f'{tcfg["name"]}: {e}']
            return None

    def _rumble(self, kick, amount):
        """The modern techno 'rumble': the kick sent into a long dark reverb, low-passed to a tonal sub-bass cloud,
        driven, then ducked hard by the kick itself so it swells in the gaps between kicks."""
        k = kick.astype(np.float64)
        ir = make_ir(2.4, predelay=0.0, bright=0.3)
        tail = lp(reverb(k, ir), 140, 2)
        tail = np.tanh(tail / (np.max(np.abs(tail)) + 1e-9) * 2.5)
        env = uniform_filter1d(np.abs(k).max(axis=0), int(0.03 * SR))
        duck = 1 - np.clip(env / (env.max() + 1e-9) * 2.2, 0, 1)
        duck = uniform_filter1d(duck, int(0.02 * SR))
        peak = float(np.max(np.abs(k))) + 1e-9
        return (k + tail * duck * peak * 0.45 * amount).astype(np.float32)

    def throw_mask(self, b2s, amount):
        """Where the dub engineer opens the echo send: the last beat (sometimes two) of most 2-bar phrases, and a
        whole-bar throw at the end of 8-bar phrases. Short fades so the send never clicks."""
        L = self.length
        m = np.zeros(L, dtype=np.float32)
        rng = random.Random(self.song['seed'] + 7)
        for bar in range(1, self.song['total_bars'], 2):
            if (bar + 1) % 8 == 0:
                b0, b1 = bar * 4, bar * 4 + 4
            elif rng.random() < 0.35 + 0.4 * amount:
                b0 = bar * 4 + rng.choice((2.0, 3.0, 3.0, 3.5))
                b1 = bar * 4 + 4
            else:
                continue
            s0, s1 = b2s(b0), min(L, b2s(b1))
            if s1 > s0:
                m[s0:s1] = 1
        return uniform_filter1d(m, int(0.012 * SR))

    def sc_times(self):
        """When the sidechain ducks: on the kicks - or (styles with 'sc_quarters') on every beat of each bar the kick
        plays in, the steady quarter-note breathing of pads pumped by a ghost trigger, whatever the kick pattern."""
        if not self.st.get('sc_quarters'):
            return self.kick_times()
        kn = self.st.get('kick_track', 'kick')
        bars = sorted({int(e.beat // 4) for e in self.song['events'] if e.track == kn})
        return [self.t_of(b * 4 + q, human=False) for b in bars for q in range(4)]

    def kick_times(self):
        kn = self.st.get('kick_track', 'kick')
        return sorted(self.t_of(e.beat, human=False) for e in self.song['events'] if e.track == kn)

    ARC_CUT = {'intro': (2500, 5000), 'verse': (5500, 5500), 'break': (2200, 8000), 'breakdown': (2200, 8000),
               'build': (3000, 18000), 'outro': (18000, 3000)}
    ARC_SC = {'drop': (1.25, 1.25), 'chorus': (1.2, 1.2), 'climax': (1.25, 1.25), 'break': (0.5, 0.5),
              'breakdown': (0.5, 0.5), 'build': (0.6, 1.2), 'intro': (0.8, 0.8), 'outro': (0.8, 0.8)}

    def automation_curve(self, points, n):
        """A volume line drawn in the song editor -> gain per sample. points: [[beat, dB], ...] (dB <= -60 = silent);
        between two points the level moves in a straight line in dB, before the first / after the last it holds."""
        off = float((self.song.get('preview_of') or (0, 0))[0]) * 4      # previews / section windows start mid-song
        pts = sorted((float(b) - off, float(d)) for b, d in points if b is not None and d is not None)
        if not pts:
            return np.ones(n, dtype=np.float32)
        xs = np.array([self.t_of(b, human=False) * SR for b, _ in pts])
        ds = np.clip(np.array([d for _, d in pts]), -80.0, 12.0)
        db = np.interp(np.arange(n), xs, ds)
        g = np.where(db <= -60, 0.0, 10 ** (db / 20)).astype(np.float32)
        return uniform_filter1d(g, 64)                    # no clicks at the corners

    def track_key(self, tcfg, evs):
        """A fingerprint of everything a part's raw render depends on (its settings, notes, tempo, length, the song's
        style data, the synth character ...), or None when the part shouldn't be cached (full songs, plugins, samples
        you loaded)."""
        if self.length > 75 * SR or str(tcfg.get('inst', '')).startswith(('vst:', 'user:')) or tcfg.get('vst'):
            return None
        try:
            st = {k: v for k, v in self.st.items() if k != 'tracks'}
            o = self.opts
            blob = json.dumps([tcfg, [(e.beat, e.dur, e.midi, round(float(e.vel), 4), e.glide, e.mod, getattr(e, 'strum', 0),
                                       getattr(e, 'slide', 0), getattr(e, 'bend', None)) for e in evs],
                               self.song['bpm'], self.length, self.song.get('preview_of'), self.song.get('tempo_map'), st,
                               [getattr(o, k, None) for k in ('seed', 'humanize', 'brightness', 'synth_character', 'user_drums',
                                                               'style', 'sound_seed')], RENDER_VERSION],
                              sort_keys=True, default=str)
        except Exception:                                 # noqa: BLE001 - anything odd: just don't cache
            return None
        return hashlib.sha1(blob.encode()).hexdigest()

    def lane_curve(self, points, n, default):
        """An editor lane (filter / reverb / pan) -> a value per sample: straight lines between the points, held
        before the first and after the last."""
        off = float((self.song.get('preview_of') or (0, 0))[0]) * 4
        pts = sorted((float(b) - off, float(v)) for b, v in (points or []) if b is not None and v is not None)
        if not pts:
            return np.full(n, default, dtype=np.float32)
        xs = np.array([self.t_of(b, human=False) * SR for b, _ in pts])
        return uniform_filter1d(np.interp(np.arange(n), xs, [v for _, v in pts]).astype(np.float32), 256)

    def knob_ride(self, tcfg, L):
        """A producer riding the cutoff knob (analog character, electronic genres): the chords' and arp's low-pass
        drifts slowly open and closed over 8 or 16 bars, each part on its own cycle - so a loop that repeats for
        32 bars still moves, instead of sitting frozen like a MIDI file. Gentle (~1.3 octaves at most); parts that
        already sweep their own filter are left alone. -> cutoff multiplier per sample (or None)."""
        if tcfg['layer'] not in ('chords', 'arp') or tcfg.get('sweep') or tcfg.get('no_ride'):
            return None
        r = random.Random(f"{getattr(self.opts, 'seed', 0)}-{tcfg['name']}-ride")
        if r.random() < 0.3:                              # not every part, not every song
            return None
        bars = r.choice([8, 16, 16])
        period = bars * 4 * self.spb
        t = np.arange(L) / SR
        depth = r.uniform(0.6, 1.3)                       # octaves
        ph = r.random() * 2 * np.pi
        lfo = 0.5 - 0.5 * np.cos(2 * np.pi * t / period + ph)   # 0 = most closed, 1 = open
        return (2.0 ** (-depth * (1 - lfo))).astype(np.float32)

    def filter_arc(self, song, b2s, L):
        """Filter automation across the arrangement (trance / techno): the synths' low-pass is part-closed in the intro
        and groove, darker in the breakdown and slowly opening, swept open through the build and wide open in the drop -
        tension by closing, release by opening. -> cutoff per sample (Hz)."""
        cut = np.full(L, 20000.0)
        for sec in song['sections']:
            a, b = b2s(sec['bar'] * 4), min(L, b2s((sec['bar'] + sec['bars']) * 4))
            rng = self.ARC_CUT.get(sec['name'])
            if b <= a or rng is None or (sec['name'] == 'intro' and sec['opts'].get('filter_in')):
                continue
            cut[a:b] = np.geomspace(rng[0], rng[1], b - a)
        return np.exp(uniform_filter1d(np.log(cut), int(0.4 * SR))).astype(np.float32)

    def sc_arc(self, song, b2s, L):
        """How hard the kick ducks the music, section by section: deepest in the drops, gentle in the breakdown."""
        g = np.ones(L)
        for sec in song['sections']:
            a, b = b2s(sec['bar'] * 4), min(L, b2s((sec['bar'] + sec['bars']) * 4))
            r = self.ARC_SC.get(sec['name'])
            if b > a and r:
                g[a:b] = np.linspace(r[0], r[1], b - a)
        return uniform_filter1d(g, int(0.4 * SR))

    def return_duck(self):
        """0..1 envelope of the dry lead (10 ms attack, 300 ms release), for ducking the reverb / delay returns."""
        k = self._lead_key
        if not np.any(k):
            return None
        hop = 220
        m = len(k) // hop
        e = k[:m * hop].reshape(m, hop).max(axis=1)
        out = np.empty_like(e)
        y, rel = 0.0, np.exp(-hop / (0.3 * SR))
        for i, v in enumerate(e):
            y = v if v > y else v + (y - v) * rel
            out[i] = y
        ref = float(np.percentile(out[out > 0], 90)) if np.any(out > 0) else 1.0
        out = np.clip(out / (ref + 1e-9), 0, 1)
        full = np.interp(np.arange(len(k)), np.arange(m) * hop + hop / 2, out).astype(np.float32)
        return full

    def throw_notes(self, evs):
        """(1.86) A mask that is 1 on the lead's phrase-ending notes (a note followed by at least a beat of rest) and 0
        elsewhere: those notes get thrown into the delay, the way an engineer rides the echo send at a phrase's end."""
        ns = sorted((e for e in evs if e.midi is not None), key=lambda e: e.beat)
        if len(ns) < 4:
            return None
        mask = np.zeros(self.length, dtype=np.float32)
        hit = False
        for a, b in zip(ns, ns[1:] + [None]):
            gap = (b.beat - (a.beat + a.dur)) if b is not None else 4.0
            if gap >= 1.0:
                s0 = int(self.t_of(a.beat, human=False) * SR)
                s1 = min(self.length, int(self.t_of(a.beat + a.dur, human=False) * SR) + int(0.05 * SR))
                if s1 > s0:
                    mask[s0:s1] = 1.0
                    hit = True
        if not hit:
            return None
        return np.convolve(mask, np.ones(441) / 441, 'same').astype(np.float32)

    def sc_shape(self):
        """(1.85) The sidechain's shape for this genre family: 'pump' (holds the dip, then swings back - big room,
        French / club house), 'breathe' (shallow and smooth - dreamy trance, deep / melodic house), 'tight' (only the
        kick's attack - DnB, breaks, dubstep), or 'classic' (the old curve)."""
        st = self.st
        if st.get('sc_shape'):
            return st['sc_shape']
        if not _va.analog():
            return 'classic'
        name = st.get('name') or getattr(self.opts, 'style', '')
        if name in SC_SHAPE_GENRE:
            return SC_SHAPE_GENRE[name]
        from .genre_groups import group_of
        g = group_of(name)
        if any(w in name for w in ('deep', 'melodic', 'organic', 'progressive', 'dream', 'balearic', 'chill', 'sunny')):
            return 'breathe'
        return SC_SHAPE_GROUP.get(g, 'classic')

    def sidechain_curve(self, release_beats):
        duck = np.zeros(self.length, dtype=np.float32)
        kind = self.sc_shape()
        if kind == 'tight':
            release_beats = min(release_beats, 0.3)
        elif kind == 'breathe':
            release_beats = max(release_beats, 0.6)
        rel = release_beats * self.spb
        n = int(rel * SR)
        t = np.arange(n) / SR
        x = np.clip(t / rel, 0, 1)
        if kind == 'pump':                               # holds the dip for a moment, then swings back up (S-curve)
            hold = 0.18
            y = np.clip((x - hold) / (1 - hold), 0, 1)
            body = 1 - (3 * y ** 2 - 2 * y ** 3)
        elif kind == 'breathe':                          # a smooth cosine dip, shallower (depth x 0.75)
            body = 0.75 * (0.5 + 0.5 * np.cos(np.pi * x))
        elif kind == 'tight':
            body = (1 - x) ** 3
        else:
            body = (1 - x) ** 2
        shape = (body * np.minimum(t / 0.004, 1)).astype(np.float32)
        for kt in self.sc_times():
            s = int(kt * SR)
            if s >= self.length:
                continue
            m = min(n, self.length - s)
            np.maximum(duck[s:s + m], shape[:m], out=duck[s:s + m])
        return duck

    def render(self, stems_dir=None, progress=None):
        song, st, opts = self.song, self.st, self.opts
        _va.CHARACTER = 'classic' if getattr(opts, 'synth_character', 'analog') == 'classic' else 'analog'
        _va._RNG = np.random.default_rng((int(getattr(opts, 'seed', 0) or 0) * 7919 + 57) % (2 ** 32))   # reproducible
        L = self.length
        by_track = {}
        for e in song['events']:
            by_track.setdefault(e.track, []).append(e)
        sc_depth = st['sc_depth']
        duck = self.sidechain_curve(st['sc_release']) if sc_depth > 0 else None
        mix = np.zeros((2, L), dtype=np.float32)
        self._hats = {}
        self._dly_extra = {}
        self._dodge = None
        self.low_env = {}                                   # layer -> 10 ms peak envelope below 100 Hz (kick, bass)
        drums = np.zeros((2, L), dtype=np.float32)
        music = np.zeros((2, L), dtype=np.float32)          # (1.97) chords, pads, arps: a bus that makes room for the lead
        lead_mono = np.zeros(L, dtype=np.float32)
        rev_send = np.zeros((2, L), dtype=np.float32)
        self._duck_on = _va.analog() and st.get('category') != 'Orchestral' and getattr(opts, 'send_duck', 'auto') != 'off'
        self._lead_key = np.zeros(L, dtype=np.float32)
        dly_send = np.zeros((2, L), dtype=np.float32)
        b2s = lambda b: int(self.t_of(b, human=False) * SR)
        dub_send, throw = None, None
        if st.get('dub'):                                 # dub mixing: the engineer 'throws' a hit into the tape echo
            dub_send = np.zeros((2, L), dtype=np.float32)
            throw = self.throw_mask(b2s, float(st['dub']))
        gaps = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'gap']
        lpsweeps = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'lpsweep']
        hpsweeps = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'hpsweep']
        tapestops = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'tapestop']
        djslows = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'djslow']
        rewinds = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'rewind']
        # ---- energy contour + fades
        env = np.ones(L)
        for sec in song['sections']:
            s0, s1 = b2s(sec['bar'] * 4), min(L, b2s((sec['bar'] + sec['bars']) * 4))
            e = SECTION_ENERGY.get(sec['name'], 0.9)
            e = 1 - (1 - e) * (0.5 + song['energy'])
            if sec['opts'].get('level') is not None:      # written-out dynamics (Cinematic Journey): pp ... ff
                env[s0:s1] = np.linspace(sec['opts']['level'], sec['opts'].get('level_to', sec['opts']['level']), max(0, s1 - s0))
            elif sec['opts'].get('build') and (getattr(opts, 'builds', 'auto') or 'auto') != 'off':
                env[s0:s1] = np.linspace(0.72 if (getattr(opts, 'builds', 'auto') or 'auto') == 'auto' else 0.86, 0.95, s1 - s0)
            else:
                env[s0:s1] = e
        env = uniform_filter1d(env, int(0.25 * SR))
        for kind, b, d in song['fx']:
            if kind == 'fade':
                s0, s1 = b2s(b), min(L, b2s(b + d) + int(3.5 * SR))
                env[s0:s1] *= np.linspace(1, 0, s1 - s0) ** 1.6
                env[s1:] = 0
        env32 = env.astype(np.float32)
        arc_cut = self.filter_arc(song, b2s, L) if st.get('filter_arc') else None
        sc_mult = self.sc_arc(song, b2s, L) if st.get('sc_arc') and duck is not None else None
        fade_end = next((min(L, b2s(b + d) + int(3.5 * SR)) for kind, b, d in song['fx'] if kind == 'fade'), None)
        stems = []
        n_tracks = len(st['tracks'])
        has_answer = any(t['name'] == 'answer' for t in st['tracks']) and bool(by_track.get('answer'))
        hook_mask = call_sum = None
        if has_answer:                                    # the sections where the lead and its answer trade phrases
            hook_mask = np.zeros(L, dtype=bool)
            ab = sorted(e.beat for e in by_track['answer'])
            for sec in song['sections']:
                b0, b1 = sec['bar'] * 4, (sec['bar'] + sec['bars']) * 4
                if any(b0 <= x < b1 for x in ab):
                    hook_mask[b2s(b0):min(L, b2s(b1))] = True
            call_sum = np.zeros(int(hook_mask.sum()), dtype=np.float32)
        # (1.92.4) the parts that may render in worker processes, in mix order
        pool, futs, par = None, {}, []
        nw = render_workers(L)
        if nw > 0:
            from .instruments import INSTRUMENTS as _I, DRUMS as _D
            for tcfg in st['tracks']:
                n_, inst_ = tcfg['name'], str(tcfg.get('inst', ''))
                if not by_track.get(n_) or tcfg.get('vst') or tcfg['layer'] == 'fx' or (opts.muted and tcfg['layer'] in opts.muted):
                    continue
                if not (inst_ in _I or inst_ in _D) or inst_.startswith(('vst:', 'user:', 'sf:', 'real:')):
                    continue
                if tcfg['layer'] in ('kick', 'snare', 'top') and (st.get('real_kit') or st.get('real_perc') or st.get('voice_real')):
                    continue
                ck_ = self.track_key(tcfg, by_track[n_])
                if ck_ and TRACK_CACHE.get(ck_) is not None:
                    continue
                par.append(n_)
        if len(par) >= 2:
            try:
                import pickle
                import multiprocessing as _mp
                from concurrent.futures import ProcessPoolExecutor
                ctx = _mp.get_context('fork' if sys.platform.startswith('linux') else 'spawn')
                blob = None
                if ctx.get_start_method() == 'fork':
                    _WORKER['song'] = song                # (forked workers see it directly)
                else:
                    blob = pickle.dumps(song)
                pool = ProcessPoolExecutor(max_workers=min(nw, len(par)), mp_context=ctx, initializer=_pool_init,
                                           initargs=(blob, _va.CHARACTER))
                self.log(f'   rendering {len(par)} parts on {min(nw, len(par))} extra cores')
            except Exception as e:                        # noqa: BLE001 - no workers: render one by one as before
                pool = None
                self.log(f'   (parallel rendering unavailable: {e})')
        ahead = (min(nw, len(par)) + 1) if pool else 0

        def _submit_upto(i):
            for n_ in par[:i]:
                if n_ not in futs:
                    sd = (int(getattr(opts, 'seed', 0) or 0) * 7919 + 57 + zlib.crc32(n_.encode())) % (2 ** 32)
                    futs[n_] = pool.submit(_pool_render, n_, sd)
        if pool:
            _submit_upto(ahead)
        for ti, tcfg in enumerate(st['tracks']):
            name = tcfg['name']
            evs = by_track.get(name, [])
            if not evs and tcfg['layer'] != 'fx':
                continue
            if tcfg['layer'] == 'fx' and 'fx' in (opts.muted or []):
                continue
            t0 = time.time()
            ck = self.track_key(tcfg, evs)
            hitc = TRACK_CACHE.get(ck) if ck else None
            if pool and name in par:
                _submit_upto(par.index(name) + 1 + ahead)
                try:
                    hitc = futs.pop(name).result()
                    ck_new = ck
                except Exception as e:                    # noqa: BLE001 - a worker failed: render this part here
                    self.log(f'   {name}: worker failed ({e}) - rendering it here')
                    hitc, ck_new = None, None
                if hitc is not None and ck_new:
                    TRACK_CACHE[ck_new] = hitc.copy()
                    while len(TRACK_CACHE) > 40:
                        TRACK_CACHE.popitem(last=False)
            from_worker = pool is not None and name in par
            if hitc is not None:                          # (1.87) unchanged since the last preview: reuse it
                if ck and ck in TRACK_CACHE:              # (1.92.4) ... or rendered by a worker process
                    TRACK_CACHE.move_to_end(ck)
                buf = hitc if from_worker else hitc.copy()
            else:
                seed_ = (int(getattr(opts, 'seed', 0) or 0) * 7919 + 57 + zlib.crc32(name.encode())) % (2 ** 32)
                _va._RNG = np.random.default_rng(seed_)   # each part its own random stream: the same part renders the
                from . import dsp as _dsp                 # same whatever else changed (and can be cached)
                _dsp.RNG = np.random.default_rng(seed_ + 1)
                buf = self.render_track(tcfg, evs)
                _trim()
                if not is_drum_layer(tcfg):              # (1.90) this part's notes are done: free them (drum hits are
                    for k_ in [k_ for k_ in self.cache if isinstance(k_, tuple) and k_ and k_[0] == name]:   # reused)
                        del self.cache[k_]
                if ck:
                    TRACK_CACHE[ck] = buf.copy()
                    while len(TRACK_CACHE) > 40:
                        TRACK_CACHE.popitem(last=False)
            fxname = (getattr(opts, 'part_fx', None) or {}).get(tcfg['layer'])
            if fxname and tcfg['layer'] != 'fx' and np.any(buf):
                try:                                      # your effect plugin on this part (own process)
                    from . import vsthost
                    y = vsthost.process([fxname], buf)
                    n = min(buf.shape[1], y.shape[1])
                    buf = np.zeros_like(buf)
                    buf[:, :n] = y[:, :n]
                    self.log(f'   {name}: through {fxname}')
                except Exception as e:
                    self.log(f'   {name}: effect {fxname} failed ({e}) - left dry')
                    self.vst_failures = getattr(self, 'vst_failures', []) + [f'{name} effect {fxname}: {e}']
            if tcfg['layer'] == 'fx':
                g = np.zeros(L, dtype=np.float32)
                for sec in song['sections']:
                    if 'fx' in sec['layers']:
                        g[b2s(sec['bar'] * 4):b2s((sec['bar'] + sec['bars']) * 4)] = 1
                buf *= uniform_filter1d(g, int(0.5 * SR))
            if tcfg['layer'] != 'fx' and not st.get('flat_dynamics') and np.any(buf):
                arc = dynamics_arc(song['sections'], tcfg['layer'], L, b2s, gentle=bool(st.get('master', {}).get('gentle')))
                if arc is not None:
                    buf *= arc[None, :buf.shape[1]] if buf.ndim == 2 else arc[:buf.shape[-1]]
            if tcfg.get('hp'):
                buf = hp(buf, tcfg['hp']).astype(np.float32)
            if tcfg.get('lp'):                                # a muffled, felted tone
                buf = lp(buf, tcfg['lp']).astype(np.float32)
            if tcfg.get('presence'):                          # amp-style tone: scoop the boxy 400 Hz, push the 2.5 kHz bite
                pr = float(tcfg['presence'])
                buf = eq(eq(buf, 'peak', 400, 0.9, -0.6 * pr), 'peak', 2500, 0.8, pr).astype(np.float32)
            ride = self.knob_ride(tcfg, L) if (_va.analog() and st.get('category') == 'Electronic') else None
            if arc_cut is not None and tcfg['layer'] in ('chords', 'pad', 'arp', 'lead'):
                buf = auto_lp(buf, arc_cut * ride if ride is not None else arc_cut).astype(np.float32)
            elif ride is not None:
                buf = auto_lp(buf, 16000.0 * ride).astype(np.float32)
            if tcfg['layer'] in ('chords', 'pad', 'arp'):
                for s0, s1 in lpsweeps:
                    sweep_region(buf, s0, s1, 'lp', 250, 18000)
            if tcfg['layer'] in ('chords', 'pad', 'arp', 'lead', 'bass'):
                for s0, s1 in hpsweeps:
                    sweep_region(buf, s0, s1, 'hp', 30, 900)
            target = tcfg['db'] if tcfg['db'] is not None else ROLE_DB.get(tcfg['layer'], -22)
            try:                                          # your per-part level (Mix & master)
                target += max(-24.0, min(9.0, float((getattr(opts, 'part_levels', None) or {}).get(tcfg['layer'], 0))))
            except (TypeError, ValueError):
                pass
            try:                                          # ... and this one sound's own level (song editor)
                target += max(-24.0, min(9.0, float((getattr(opts, 'track_levels', None) or {}).get(name, 0))))
            except (TypeError, ValueError):
                pass
            cur = active_rms_db(buf)
            if cur > -110:
                g = 10 ** ((target - cur) / 20)
                buf *= np.float32(g)
                self.track_gains[name] = g
            if tcfg['pan']:
                th = (tcfg['pan'] * min(1.0, opts.width) + 1) * np.pi / 4
                buf[0] *= np.float32(np.cos(th) * np.sqrt(2))
                buf[1] *= np.float32(np.sin(th) * np.sqrt(2))
            if tcfg['layer'] == 'bass' and not (duck is not None and tcfg['sc']) and not st.get('no_dodge') and np.any(buf):
                if self._dodge is None:                     # kick / bass separation: the bass's lowest band (< 110 Hz)
                    self._dodge = self.sidechain_curve(0.18)   # dips ~5 dB for the length of each kick, so the two
                lo_ = lp(buf, 110, 2).astype(np.float32)      # never sum into one smeared boom (genres with no
                buf = buf - lo_ * (0.45 * self._dodge[None, :buf.shape[1]])   # sidechain of their own)
            if duck is not None and tcfg['sc']:
                if sc_mult is not None:                   # the pumping deepens in the drops, eases in the breakdown
                    buf *= (1 - duck * np.minimum(1.0, sc_depth * tcfg['sc'] * sc_mult).astype(np.float32))[None, :]
                else:
                    buf *= (1 - duck * np.float32(min(1.0, sc_depth * tcfg['sc'])))[None, :]
            for s0, s1 in tapestops:
                if tcfg['layer'] != 'fx':
                    tape_stop(buf, s0, s1)
            for s0, s1 in djslows:
                if tcfg['layer'] != 'fx':
                    dj_slow(buf, s0, s1)
            for s0, s1 in rewinds:
                if tcfg['layer'] != 'fx':
                    rewind(buf, s0, s1)
            for s0, s1 in gaps:
                if tcfg['layer'] != 'fx':
                    buf[:, s0:s1] = 0
            buf *= env32[None, :]
            auto = (getattr(opts, 'automation', None) or {}).get(name)
            if auto and np.any(buf):                       # your volume line from the song editor
                buf *= self.automation_curve(auto, buf.shape[1])[None, :]
            lanes = getattr(opts, 'lanes', None) or {}            # (1.87) the editor's filter / reverb / pan lanes
            fl = (lanes.get('filter') or {}).get(name)
            if fl and np.any(buf):                                 # 0 = closed (200 Hz), 1 = open
                v = self.lane_curve(fl, buf.shape[1], 1.0)
                if float(v.min()) < 0.995:
                    buf = auto_lp(buf, 200 * (18000 / 200) ** v).astype(np.float32)
            pl = (lanes.get('pan') or {}).get(name)
            if pl and np.any(buf):                                 # -1 left ... +1 right (constant power)
                v = self.lane_curve(pl, buf.shape[1], 0.0)
                a = (np.clip(v, -1, 1) + 1) * np.pi / 4
                m_ = buf.mean(axis=0)
                buf = np.vstack([m_ * np.cos(a) * 1.414, m_ * np.sin(a) * 1.414]).astype(np.float32)
            rl = (lanes.get('reverb') or {}).get(name)
            rev_curve = self.lane_curve(rl, buf.shape[1], 1.0) * 2.0 if rl else None   # 0 dry ... 1 = twice the send
            if has_answer and np.any(buf) and (name.startswith('lead') and tcfg['layer'] == 'lead' or name == 'answer'):
                # (1.90.1) call & response: the answering sound plays as loud as the lead it answers - matched by
                # loudness as the ear hears it (K-weighted), with the lead's doubled layer counted, in the hook sections
                kw = k_weight(buf.mean(axis=0))[hook_mask].astype(np.float32)
                if name != 'answer':
                    call_sum[:len(kw)] += kw
                elif np.any(call_sum):
                    a_db, c_db = active_rms_db(kw), active_rms_db(call_sum)
                    if a_db > -110 and c_db > -110:
                        g = np.float32(10 ** (max(-12.0, min(12.0, c_db - 0.5 - a_db)) / 20))   # a hair under the call
                        buf *= g
                        self.track_gains[name] = self.track_gains.get(name, 1.0) * float(g)
                        self.log(f'   answer matched to the lead: {20 * np.log10(float(g)):+.1f} dB')
            if tcfg['layer'] in ('kick', 'bass') and np.any(buf):   # low-band envelopes for the kick / bass overlap check
                lo_e = np.abs(lp(buf.mean(axis=0), 100, 2))
                hop = 441
                m_ = len(lo_e) // hop
                e_ = lo_e[:m_ * hop].reshape(m_, hop).max(axis=1)
                prev_ = self.low_env.get(tcfg['layer'])
                self.low_env[tcfg['layer']] = e_ if prev_ is None else np.maximum(prev_[:m_], e_[:len(prev_)])
            if tcfg['layer'] == 'lead' and np.any(buf) and self._duck_on:
                self._lead_key += np.abs(buf.mean(axis=0))          # (1.86) the dry lead ducks the echo / reverb returns
                if not st.get('dub'):                               # ... and its phrase endings are thrown into the delay
                    tm = self.throw_notes(evs)
                    if tm is not None:
                        dly_send += buf * tm[None, :] * np.float32(max(0.12, tcfg['dly']) * 1.6 * max(0.4, opts.delay))
            if rev_curve is not None:
                rev_send += buf * (rev_curve[None, :] * np.float32(max(tcfg['rev'], 0.15) * opts.reverb)).astype(np.float32)
            elif tcfg['rev']:
                rev_send += buf * np.float32(tcfg['rev'] * opts.reverb)
            if tcfg['dly'] and tcfg.get('dly_time'):         # this part's own echo time (a 1/8 pluck under a dotted-8th lead)
                k_ = float(tcfg['dly_time'])
                if k_ not in self._dly_extra:
                    self._dly_extra[k_] = np.zeros((2, L), dtype=np.float32)
                self._dly_extra[k_] += buf * np.float32(tcfg['dly'] * opts.delay)
            elif tcfg['dly']:
                dly_send += buf * np.float32(tcfg['dly'] * opts.delay)
            if dub_send is not None and tcfg.get('throw'):
                dub_send += buf * throw[None, :] * np.float32(tcfg['throw'] * max(0.3, opts.delay))
            if st.get('hat_choke') and name in ('ohat', 'chat'):
                self._hats[name] = buf                     # (the open hat is choked by the closed hat below)
            if st.get('kick_rumble') and name == st.get('kick_track', 'kick') and np.any(buf):
                rum = kick_rumble(buf, float(st['kick_rumble']), duck)
                mix += rum
                if stems_dir:
                    rp = os.path.join(stems_dir, f'{ti + 1:02d}_{name}_rumble.wav')
                    write_wav_float(rp, rum)
                    stems.append(dict(name=name + '_rumble', layer='bass', inst='rumble', path=rp))
            if tcfg['layer'] == 'bass' and np.any(buf) and st.get('sub_harmonics', st.get('category') == 'Electronic'):
                buf = sub_harmonics(buf, float(st.get('sub_harmonics_amt', 0.12)))   # the bass reads on small speakers
            if tcfg['layer'] == 'lead' and np.any(buf):
                lead_mono[:buf.shape[1]] += buf.mean(axis=0)[:L]
            if tcfg['layer'] in ('kick', 'snare', 'top'):
                drums += buf
            elif tcfg['layer'] in ('chords', 'pad', 'arp'):
                music += buf
            else:
                mix += buf
            if stems_dir:
                path = os.path.join(stems_dir, f'{ti + 1:02d}_{name}.wav')
                write_wav_float(path, buf)
                stems.append(dict(name=name, layer=tcfg['layer'], inst=tcfg['inst'], path=path))
            self.log(f'   rendered {name:<11} {len(evs):5d} notes  {time.time() - t0:5.1f}s')
            if progress:
                progress((ti + 1) / (n_tracks + 3))
        for _v in ('buf', 'lo_e', 'e_'):                  # (1.90) the last part's buffers aren't needed any more
            locals().pop(_v, None)
        buf = lo_e = e_ = None
        if pool:
            pool.shutdown(wait=True, cancel_futures=True)
            _WORKER.pop('song', None)
        # (1.87) after the parts, the random streams start from a fixed point again (cached or not, same result)
        _post = (int(getattr(opts, 'seed', 0) or 0) * 7919 + 9001) % (2 ** 32)
        _va._RNG = np.random.default_rng(_post)
        from . import dsp as _dsp
        _dsp.RNG = np.random.default_rng(_post + 1)
        # ---- one-shot FX
        fxbuf = np.zeros((2, L), dtype=np.float32)
        if 'fx' not in (opts.muted or []):
            new_fx = _va.analog()                               # (classic synth character keeps the old FX)
            root_hz = 440.0 * 2 ** (((song['key'].root % 12) + 48 - 69) / 12) if song.get('key') is not None else 65.4
            from .genre_groups import group_of
            rstyle = st.get('riser_style') or RISER_FAMILY.get(group_of(st.get('name') or opts.style), 'noise')
            for kind, b, d in song['fx']:
                s = b2s(b)
                if kind == 'crash':
                    self._add(fxbuf, self._drum('crash') * 0.5, s)
                elif kind == 'impact':
                    self._add(fxbuf, fx_impact2(root_hz, seed=int(b)) if new_fx else fx_impact().astype(np.float32) * 0.8, s)
                elif kind == 'riser' and d > 0 and new_fx:
                    sec = max(0.5, self._bt(b + d) - self._bt(b))
                    self._add(fxbuf, fx_riser2(sec, root_hz, rstyle, self.spb, seed=int(b)) * 0.75, s)
                elif kind == 'riser' and d > 0:
                    self._add(fxbuf, fx_riser(d * self.spb).astype(np.float32) * 0.6, s)
                elif kind == 'downlift' and d > 0 and new_fx:
                    self._add(fxbuf, fx_downlift2(max(0.5, self._bt(b + d) - self._bt(b)), root_hz, seed=int(b)), s)
                elif isinstance(kind, str) and kind.startswith('shout'):    # (1.90) 'shout:oi' - the hype man
                    self._add(fxbuf, fx_shout(kind.split(':')[1] if ':' in kind else 'oi', seed=int(b) + 3,
                                              spb=self.spb) * 0.9, s)
                elif kind == 'cymroll' and d > 0:             # suspended cymbal roll (soft mallets), swelling to the edge
                    self._add(fxbuf, fx_cymroll(max(0.5, self._bt(b + d) - self._bt(b))), s)
                elif kind == 'wash' and d > 0:                # a filtered noise wash opening up (no synth tone)
                    self._add(fxbuf, fx_wash(max(0.5, self._bt(b + d) - self._bt(b))), s)
                elif kind == 'downlift' and d > 0:            # noise falling away after the downbeat
                    self._add(fxbuf, fx_wash(max(0.5, self._bt(b + d) - self._bt(b)), down=True), s)
                elif kind == 'swell' and d > 0:               # reverse cymbal leading into the next section
                    c = self._drum('crash')[::-1]
                    n = min(len(c), int(d * self.spb * SR))
                    self._add(fxbuf, c[-n:] * np.linspace(0.2, 0.55, n, dtype=np.float32), s + int(d * self.spb * SR) - n)
        if np.any(fxbuf):
            cur = active_rms_db(fxbuf)
            band = st.get('category') == 'Classic'           # a live band's crash sits in the kit, not on top of it
            fxbuf *= np.float32(10 ** ((ROLE_DB['fx'] + (-1 if band else 3) - cur) / 20))
            fxbuf *= env32[None, :]
            rev_send += fxbuf * 0.3
            mix += fxbuf
            if stems_dir:
                path = os.path.join(stems_dir, '90_fx.wav')
                write_wav_float(path, fxbuf)
                stems.append(dict(name='fx', layer='fx', inst='fx', path=path))
        # ---- drum bus
        self.log('   drum bus: glue compression + saturation')
        if st.get('hat_choke') and 'ohat' in self._hats and 'chat' in self._hats:
            oh = self._hats['ohat']
            drums -= oh                                    # the open hat rings only until the closed hat shuts it
            drums += oh * hat_choke_env(self._hats['chat'], oh)[None, :]
        if st.get('drum_crush'):                          # phonk: the whole kit a little bit-crushed (lo-fi grit)
            c = float(st['drum_crush'])
            q = 2 ** (14 - 6 * c)
            hold = max(1, int(1 + 3 * c))
            dm = np.round(np.asarray(drums, np.float64) * q) / q
            drums = np.repeat(dm[:, ::hold], hold, axis=1)[:, :drums.shape[1]].astype(np.float32)
        # ---- music bus (1.97): chords, pads and arps dip at the lead's own frequency while the lead plays
        self.lead_over_music = None
        if np.any(music):
            if np.any(lead_mono) and st.get('lead_room', st.get('category') != 'Orchestral'):
                music, self.lead_over_music, f0 = lead_room(music, lead_mono)
                if f0:
                    self.log(f'   music bus: -3 dB at {f0:.0f} Hz while the lead plays (lead {self.lead_over_music:+.1f} dB over the music)')
            mix += music
        del music
        par = st.get('drum_parallel', {'Electronic': 0.28, 'Classic': 0.15}.get(st.get('category'), 0.0))
        drums = drum_bus(drums, float(st.get('drum_drive', 0.25)), float(par))
        if stems_dir and np.any(drums):
            path = os.path.join(stems_dir, '00_drum_bus.wav')
            write_wav_float(path, drums)
            stems.insert(0, dict(name='drum_bus', layer='drums', inst='drums', path=path, bus=True))
        mix += drums.astype(np.float32, copy=False)        # (1.90: the mix stays 32-bit until the master)
        del drums
        # ---- returns
        if st.get('category') == 'Electronic' and not st.get('no_send_arc') and _va.analog():
            arc = self.send_arc(song, b2s, L)                # (1.97) wet breakdowns and intros, tighter drops
            rev_send *= arc[None, :]
            dly_send *= arc[None, :]
        _trim()
        self.log('   reverb + delay returns')
        returns = np.zeros_like(mix)
        rduck = self.return_duck() if self._duck_on else None
        if np.any(rev_send):
            ir = make_spring_ir(st['reverb']) if st.get('spring') else room_ir(st['reverb'], st.get('rev_predelay', 0.02),
                                                                                 st.get('category'))
            rv = eq(reverb(rev_send, ir), 'lowshelf', 300, 0.7, -4.0)          # (32-bit convolution: half the memory)
            if st.get('rev_hp'):                         # a high-passed return keeps the low end tight (trance halls)
                rv = hp(rv, st['rev_hp'])
            if st.get('fx_reverb'):                      # the genre's reverb plugin (Dragonfly), level-matched to the built-in
                from . import fxrig
                pv = fxrig.run_reverb(st, rev_send, self.log)
                if pv is not None and pv.shape[1] >= rv.shape[1] // 2:
                    pv = np.asarray(pv, dtype=np.float64)[:, :rv.shape[1]]
                    if pv.shape[1] < rv.shape[1]:
                        pv = np.pad(pv, ((0, 0), (0, rv.shape[1] - pv.shape[1])))
                    a, b = float(np.sqrt(np.mean(rv ** 2)) + 1e-12), float(np.sqrt(np.mean(pv ** 2)) + 1e-12)
                    rv = eq(pv * (a / b), 'lowshelf', 300, 0.7, -3.0)
            if duck is not None:
                rv *= (1 - duck * sc_depth * 0.7)[None, :]
            if rduck is not None:
                rv *= (1 - 0.35 * rduck)[None, :]
            returns += rv * 0.55
        for k_, snd in self._dly_extra.items():
            if np.any(snd):
                returns += hp(pingpong(snd.astype(np.float64), k_ * self.spb, fb=0.4), 250) * 0.45
        if np.any(dly_send):
            dl = hp(pingpong(dly_send.astype(np.float64), st['delay_beats'] * self.spb, fb=0.42), 250)
            if rduck is not None:                        # the echoes step back while the lead plays, bloom in its gaps
                dl *= (1 - 0.6 * rduck)[None, :]
            if duck is not None and st.get('sc_quarters'):  # (1.96) the whole music bus breathes: the echoes pump too
                dl *= (1 - duck * sc_depth * 0.8)[None, :]
            returns += dl * 0.45
            if np.any(rev_send):
                returns += reverb(dl * 0.3, ir) * 0.3
        if dub_send is not None and np.any(dub_send):
            self.log('   dub throws: tape echo + spring')
            dd = dub_delay(dub_send.astype(np.float64), float(st.get('dub_beats', 0.75)) * self.spb)
            dd += reverb(dd * 0.5, make_spring_ir(1.6)) * 0.5
            returns += dd * 0.8
        if fade_end is not None:
            returns[:, fade_end:] *= 0
            ramp = min(int(0.5 * SR), fade_end)
            returns[:, fade_end - ramp:fade_end] *= np.linspace(1, 0, ramp)[None, :]
        mix += returns
        if stems_dir and np.any(returns):
            path = os.path.join(stems_dir, '91_reverb_delay_returns.wav')
            write_wav_float(path, returns)
            stems.append(dict(name='reverb_delay', layer='fx', inst='returns', path=path))
        if progress:
            progress((n_tracks + 1) / (n_tracks + 3))
        self.stems = stems
        self.stem_env = env
        if _va.analog() and st.get('category') == 'Electronic' and not st.get('no_section_width'):
            mix = self.section_width(mix)
        return mix

    SEND_ARC = {'intro': 1.2, 'break': 1.45, 'breakdown': 1.45, 'build': 1.15, 'calm': 1.3, 'outro': 1.35,
                'drop': 0.8, 'chorus': 0.85, 'climax': 0.8, 'hook': 0.85}

    def send_arc(self, song, b2s, L):
        """(1.97) How much reverb / delay each kind of section gets (1 = as set): an engineer rides the sends - wetter in
        the breakdown, drier and tighter in the drop."""
        arc = np.ones(L, np.float32)
        for sec in song['sections']:
            m = next((v for k, v in self.SEND_ARC.items() if sec['name'].startswith(k)), 1.0)
            arc[b2s(sec['bar']):min(L, b2s(sec['bar'] + sec['bars']))] = m
        return uniform_filter1d(arc, int(0.25 * SR)).astype(np.float32)

    # how wide each kind of section sits (above 150 Hz; 1 = as mixed): the drop opens up after a narrower break / build
    SECTION_WIDTH = {'intro': 0.85, 'break': 0.82, 'breakdown': 0.82, 'build': 0.88, 'calm': 0.85, 'outro': 0.88,
                     'drop': 1.12, 'chorus': 1.08, 'climax': 1.12, 'hook': 1.08}

    def section_width(self, mix):
        """Width automation across the arrangement (analog character, electronic genres): intros, breakdowns and builds
        a little narrower, drops and choruses a little wider - the drop feels bigger by contrast. Smoothed over a bar,
        the low end untouched."""
        L = mix.shape[1]
        w = np.ones(L)
        for sec in self.song.get('sections', []):
            k = self.SECTION_WIDTH.get(sec['name'], 1.12 if sec['opts'].get('drop') else 1.0)
            a = int(self.t_of(sec['bar'] * 4, human=False) * SR)
            b = min(L, int(self.t_of((sec['bar'] + sec['bars']) * 4, human=False) * SR))
            if b > a:
                w[a:b] = k
        if np.allclose(w, 1.0):
            return mix
        w = uniform_filter1d(w, max(1, int(4 * self.spb * SR))).astype(np.float32)
        # (1.90: in place, 32-bit - this used to make a full 64-bit stereo copy of the whole mix)
        side = (mix[0] - mix[1]) * np.float32(0.5)
        mid = (mix[0] + mix[1]) * np.float32(0.5)
        lo = signal.sosfiltfilt(signal.butter(2, 150 / (SR / 2), output='sos'), side).astype(np.float32)
        side -= lo
        side *= w
        side += lo
        del lo, w
        out = mix if mix.dtype == np.float32 else mix.astype(np.float32)
        np.add(mid, side, out=out[0])
        np.subtract(mid, side, out=out[1])
        return out if mix.dtype == np.float32 else out.astype(mix.dtype)


_IR_CACHE = {}


def room_ir(decay, predelay=0.02, category=None):
    """The main reverb's impulse response. Analog character (with numba): a room from the 8-line delay network -
    early reflections, then a dense, slowly moving tail whose highs die away faster than its lows, like a real hall
    or plate (electronic genres a little brighter, acoustic ones warmer and bigger-sounding). Classic: the decaying
    filtered noise used before 1.77. Cached per setting."""
    from . import fastdsp
    if not (_va.analog() and fastdsp.HAVE_NUMBA):
        return make_ir(decay, predelay=predelay)
    bright = 0.7 if category == 'Electronic' else 0.5
    size = float(np.clip(decay / 2.5, 0.4, 1.6))
    key = (round(float(decay), 2), round(float(predelay), 3), bright)
    if key not in _IR_CACHE:
        ir = fastdsp.fdn_ir(float(decay), SR, size=size, bright=bright, predelay=float(predelay), seed=7)
        _IR_CACHE[key] = hp(ir, 180)                    # (like make_ir: the reverb never muddies the low end)
        _IR_CACHE[key] /= np.sqrt(np.sum(_IR_CACHE[key] ** 2) / 2) + 1e-12
    return _IR_CACHE[key]


def split_low(x, f=150.0):
    """Zero-phase band split: low (below f) + high = x exactly, so clipping the high band never touches the bass."""
    lo = signal.sosfiltfilt(signal.butter(2, f / (SR / 2), output='sos'), x, axis=-1)
    return lo, x - lo


def clip_stage(x, ceiling_db=-1.0, knee_db=-0.5, out_db=0.8, split=150.0):
    """(1.80) Clips only the band above `split` Hz: the drum transients that poke over the ceiling are rounded off,
    but the bass waveform underneath is never flattened (clipping a sub or 808 is the fuzzy 'clipping bass' sound).
    The bass band is kept in check by the slow bass-safe pre-limiter (dsp.low_limit) instead."""
    if split:
        lo, hi = split_low(x, split)
        c = 10 ** (ceiling_db / 20)
        if float(np.max(np.abs(x))) <= c * 10 ** (knee_db / 20):
            return x
        room = np.maximum(c * 10 ** (out_db / 20) - np.max(np.abs(lo), axis=0), c * 0.25)   # what the bass leaves free
        return lo + _soft_clip_to(hi, room, knee=10 ** (knee_db / 20))
    return _clip_full(x, ceiling_db, knee_db, out_db)


def _soft_clip_to(h, room, knee=0.944):
    """Soft-clip (2x oversampled) each sample of h to its own limit `room` (an array), starting at knee * room."""
    from .dsp import chunked
    return chunked(lambda seg, rm_: _soft_clip_seg(seg, rm_, knee), h, extra=room)


def _soft_clip_seg(h, room, knee):
    up = signal.resample_poly(h, 2, 1, axis=-1)
    rm = np.repeat(room, 2)[:up.shape[-1]]
    k = rm * knee
    w = np.maximum(rm - k, 1e-9)
    a = np.abs(up)
    up = np.where(a > k, np.sign(up) * (k + w * np.tanh((a - k) / w)), up)
    return signal.resample_poly(up, 1, 2, axis=-1)[..., :h.shape[-1]]


def _clip_full(x, ceiling_db=-1.0, knee_db=-0.5, out_db=0.8):
    """Mastering clipper ahead of the limiter (2x oversampled): the kick / snare transients that poke above the ceiling
    are rounded off sample by sample, with no attack or release. A limiter alone ducks the whole mix for each kick and
    holds it down for its release - in a four-on-the-floor drop that's 2-4 dB of constant gain reduction, which flattens
    the drop down to the level of the breakdown. The clipper takes the first dB or two of that instead, so the limiter
    only catches what's left and the arrangement keeps its loud and quiet parts."""
    c = 10 ** (ceiling_db / 20)
    k = c * 10 ** (knee_db / 20)
    top = c * 10 ** (out_db / 20)
    if float(np.max(np.abs(x))) <= k:
        return x
    from .dsp import chunked

    def seg(v):
        u = signal.resample_poly(v, 2, 1, axis=-1)
        a = np.abs(u)
        w = top - k
        u = np.where(a > k, np.sign(u) * (k + w * np.tanh((a - k) / w)), u)
        return signal.resample_poly(u, 1, 2, axis=-1)[..., :v.shape[-1]].astype(v.dtype)
    return chunked(seg, x)


def peak_round(x, ceiling_db=-1.0, above_db=2.5):
    """Round off only the rare extreme peaks (more than `above_db` over the limiter's ceiling - a crash landing on a
    kick) sample by sample, so the limiter doesn't have to duck the whole mix for them."""
    c = 10 ** (ceiling_db / 20)
    t = c * 10 ** (above_db / 20)
    a = np.abs(x)
    over = a > t
    if not np.any(over):
        return x
    w = t * 0.5
    y = np.where(over, np.sign(x) * (t + w * np.tanh((a - t) / w)), x)
    return y


def drum_bus(drums, drive=0.25, parallel=0.0):
    """Drum-bus glue that behaves the same however loud the drums arrive: work at a fixed level (peaks at -6 dBFS),
    compress gently a few dB above the kit's own average with a slow-enough attack that the hits keep their snap,
    saturate with unity small-signal gain (only the very top of a peak rounds off), then restore the level.
    (1.97) parallel: a hard-squashed copy blended under the kit ('New York' compression) - the body and room come up
    between the hits while the transients stay untouched; the bus is level-matched afterwards."""
    x = np.asarray(drums, dtype=np.float64)
    pk = float(np.max(np.abs(x))) if x.size else 0.0
    if pk < 1e-6:
        return x
    g = 0.5 / pk
    y = x * g
    ref = active_rms_db(y)
    if parallel > 0:
        squash = compressor(y, thresh=ref - 6.0, ratio=8.0, attack=0.001, release=0.08)
        squash *= np.sqrt(np.mean(y ** 2) / max(np.mean(squash ** 2), 1e-12))
        before = np.sqrt(np.mean(y ** 2))
        y = y + parallel * squash
        y *= before / max(np.sqrt(np.mean(y ** 2)), 1e-12)
    y = compressor(y, thresh=ref + 5.0, ratio=2.0, attack=0.012, release=0.12)
    k = 1.0 + max(0.0, drive)
    y *= k
    np.tanh(y, out=y)
    y /= (k * g)
    return y.astype(np.float32)


def sub_harmonics(x, amount=0.12):
    """(1.97) The bass's own upper harmonics (160 Hz - 1.2 kHz), made by saturating its sub, blended in quietly: on phones
    and laptop speakers that can't play the sub, the ear still hears the bass line. The low end itself stays as it is."""
    y = np.asarray(x, np.float64)
    lo = signal.sosfilt(signal.butter(4, 120 / (SR / 2), 'low', output='sos'), y.mean(axis=0))
    if not np.any(lo):
        return x
    pk = float(np.max(np.abs(lo))) + 1e-9
    h = np.tanh(lo / pk * 4.0)
    h = signal.sosfilt(signal.butter(2, [160 / (SR / 2), 1200 / (SR / 2)], 'band', output='sos'), h)
    h *= amount * np.sqrt(np.mean(lo ** 2) / max(np.mean(h ** 2), 1e-12))
    return (y + h[None, :]).astype(np.float32)


def lead_room(music, lead_mono, cut_db=-3.0):
    """(1.97) A dynamic EQ keyed by the lead: the chords / pads / arps dip at the lead's strongest frequency (400 Hz -
    5 kHz) only while the lead plays, so the melody sits on top without turning the whole bed down.
    -> (music, lead-over-music dB in 0.8-5 kHz where the lead plays, the frequency)"""
    f, P = signal.welch(lead_mono[:SR * 120].astype(np.float64), SR, nperseg=8192)
    band = (f > 400) & (f < 5000)
    if not np.any(P[band] > 0):
        return music, None, None
    f0 = float(f[band][np.argmax(P[band])])
    m = np.asarray(music, np.float64)
    cut = eq(m, 'peak', f0, 1.2, cut_db)
    env = np.sqrt(np.maximum(uniform_filter1d(lead_mono.astype(np.float64) ** 2, int(0.05 * SR)), 0))
    live = env > 1e-5
    ref = float(np.percentile(env[live], 80)) if np.any(live) else 1.0
    act = uniform_filter1d(np.clip(env / (ref + 1e-9), 0, 1), int(0.1 * SR))[None, :m.shape[1]]
    out = m + (cut - m) * act
    on = env > np.percentile(env, 70)
    lod = None
    if on.sum() > SR:
        bp = signal.butter(4, [800 / (SR / 2), 5000 / (SR / 2)], 'band', output='sos')
        a = signal.sosfilt(bp, lead_mono.astype(np.float64))[on[:len(lead_mono)]]
        b = signal.sosfilt(bp, out.mean(axis=0))[on[:out.shape[1]]]
        lod = round(float(10 * np.log10(np.mean(a ** 2) / max(np.mean(b ** 2), 1e-12))), 1)
    return out.astype(np.float32), lod, f0


# the engineer's EQ on a kit's raw close mics (the Unruly kick is a huge, boomy 20" with little beater click)
KIT_EQ = {'unruly': {'kick': [('hp', 38), ('peak', 55, 1.0, -4.0), ('peak', 3800, 1.0, 7.0)]},
          'dirty': {'kick': [('hp', 38), ('peak', 55, 1.0, -4.0), ('peak', 2500, 1.0, 5.0)]}}


def kit_eq(x, chain):
    y = x.astype(np.float64)
    for band in chain:
        if not isinstance(band, tuple):
            continue
        if band[0] == 'hp':
            y = hp(y, band[1])
        else:
            y = eq(y, 'peak', band[1], band[2], band[3])
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def tame_transient(x, max_crest=15.0, most=5.0):
    """Close-miked kicks / snares can peak 20 dB above their body, which stops the master getting them loud without
    limiting. Round off just the very first spike (gently, like tape) so the hit's crest is at most ~15 dB."""
    n = min(len(x), int(0.12 * SR))
    if n < 64:
        return x
    pk = float(np.max(np.abs(x))) + 1e-9
    rms = float(np.sqrt(np.mean(x[:n].astype(np.float64) ** 2))) + 1e-9
    crest = 20 * np.log10(pk / rms)
    if crest <= max_crest:
        return x
    cut = min(most, crest - max_crest)
    thr = pk * 10 ** (-cut / 20)
    y = x.astype(np.float64)
    over = np.abs(y) > thr * 0.7
    k = thr * 0.7
    y[over] = np.sign(y[over]) * (k + (thr - k) * np.tanh((np.abs(y[over]) - k) / (thr - k)))
    return (y / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)


def crush(x, bits=8, rate=25000.0):
    """Old drum-machine sample playback: sample-and-hold to a lower rate, fewer bits (one-shots, mono or stereo)."""
    x = np.asarray(x, dtype=np.float64)
    step = max(1.0, SR / float(rate))
    n = x.shape[-1]
    idx = (np.floor(np.arange(n) / step) * step).astype(np.int64)
    y = x[..., idx]
    q = 2 ** (bits - 1)
    pk = float(np.max(np.abs(y))) + 1e-9
    y = np.round(y / pk * q) / q * pk
    return lp(y, min(rate * 0.45, SR * 0.45))


def sp1200(x, rate=26040.0, bits=12):
    """E-mu SP-1200 character: 26.04 kHz sample-and-hold (aliasing sparkle), 12-bit grain and the dull top end of its
    output filters - what makes a boom-bap loop sound sampled rather than played."""
    x = np.asarray(x, dtype=np.float32)
    n = x.shape[-1]
    idx = np.floor(np.arange(n) * rate / SR) * (SR / rate)
    idx = np.minimum(idx.astype(np.int64), n - 1)
    y = x[..., idx]
    peak = float(np.max(np.abs(y))) + 1e-9
    q = 2 ** (bits - 1)
    y = np.round(y / peak * q) / q * peak
    return lp(y.astype(np.float64), 11000).astype(np.float32)


def guitar_amp(x, gain):
    """A guitar amp + 4x12 cabinet for the recorded electric: tighten the lows, clip hard (asymmetric, like a valve
    stage), then the speaker's mid bump and top roll-off. gain ~3 = crunch, 10-20 = rock lead, 25+ = metal."""
    if gain >= 24:
        return metal_amp(x, gain)
    y = hp(x.astype(np.float64), 110)
    peak = float(np.max(np.abs(y))) + 1e-9
    g = 1.0 + gain * 1.5
    y = y / peak * g
    y = np.tanh(y + 0.15) - np.tanh(0.15)
    y = eq(eq(y, 'peak', 1800, 0.9, 4.0), 'peak', 400, 1.0, -2.0)
    y = lp(hp(y, 90), 5200)
    return (y / (np.max(np.abs(y)) + 1e-9) * peak).astype(np.float32)


def leslie(x, speed=6.5, overdrive=0.0):
    """Leslie 122 rotary speaker for the Hammond: the tube preamp's growl, then a crossover at 800 Hz - the treble horn
    and the bass drum rotor spin at different speeds (the drum a little slower, so they drift against each other),
    each giving a doppler pitch wobble plus a volume / brightness swirl, picked up by two mics left and right.
    speed ~0.8 = 'chorale' (slow), ~6.5 = 'tremolo' (fast, gospel / rock)."""
    x = np.asarray(x, dtype=np.float64)
    peak = float(np.max(np.abs(x))) + 1e-9
    mono = (x[0] + x[-1]) * 0.5 / peak
    if overdrive > 0:
        mono = np.tanh(mono * (1 + 4 * overdrive)) / np.tanh(1 + 4 * overdrive)
    n = mono.shape[0]
    t = np.arange(n) / SR
    lo, hi = lp(mono, 800, 2), hp(mono, 800, 2)
    idx = np.arange(n, dtype=np.float64)
    out = np.zeros((2, n))
    for band, rate, depth, am in ((hi, speed, 0.00034, 0.32), (lo, speed * 0.86, 0.00018, 0.18)):
        for c, ph in ((0, 0.0), (1, np.pi * 0.55)):
            lfo = np.sin(2 * np.pi * rate * t + ph)
            d = (0.0006 + depth * (1 + lfo)) * SR                       # the horn moving toward / away from the mic
            y = np.interp(idx - d, idx, band)
            out[c] += y * (1 + am * lfo)
    out = eq(out, 'peak', 2500, 1.0, 1.5)
    return (out / (np.max(np.abs(out)) + 1e-9) * peak).astype(np.float32)


def metal_amp(x, gain):
    """High-gain rig: a tube-screamer style boost in front (cuts the lows so the chugs stay tight), two clipping stages,
    the scooped mids of a modern high-gain head, then a 4x12 with its 100 Hz thump and fizz roll-off. Each side gets a
    slightly different cab (a double-tracked rhythm guitar)."""
    x = np.asarray(x, dtype=np.float64)
    peak = float(np.max(np.abs(x))) + 1e-9
    y = eq(hp(x / peak, 380, 1), 'peak', 750, 0.8, 6.0)
    y = np.tanh(y * (gain * 0.9) + 0.1) - np.tanh(0.1)
    y = hp(y, 60)
    y = np.tanh(y * 3.0)
    y = eq(eq(y, 'peak', 650, 0.7, -5.0), 'peak', 110, 0.9, 4.0)
    y = eq(y, 'peak', 2600, 1.0, 3.0)
    l, r = lp(y[0], 5600, 2), lp(y[-1], 5000, 2)
    y = np.vstack([l, eq(r, 'peak', 1700, 1.2, 1.5)])
    return (y / (np.max(np.abs(y)) + 1e-9) * peak).astype(np.float32)


def pitch_vibrato(x, amount, note_sec):
    """Delayed, widening vibrato on a held note (a smooth-jazz sax vibrato): starts straight, then ~5.5 Hz
    wobbling up to ~35 cents at amount 1."""
    x = np.asarray(x, dtype=np.float32)
    n = x.shape[-1]
    t = np.arange(n) / SR
    onset = min(0.35, note_sec * 0.3)
    depth = np.clip((t - onset) / 0.5, 0, 1) * 35.0 * amount                 # cents
    r = 2.0 ** (depth * np.sin(2 * np.pi * 5.4 * t) / 1200.0)                # playback rate = pitch
    pos = np.concatenate([[0.0], np.cumsum(r[:-1])])
    pos = pos[pos < n - 1]
    i0 = pos.astype(np.int64)
    fr = (pos - i0).astype(np.float32)
    if x.ndim == 1:
        return x[i0] * (1 - fr) + x[i0 + 1] * fr
    return x[:, i0] * (1 - fr) + x[:, i0 + 1] * fr


def pitch_slide(x, semis, sec):
    """Bend a rendered note so it starts `semis` semitones low and glides up into pitch over `sec` seconds."""
    x = np.asarray(x, dtype=np.float32)
    n = x.shape[-1]
    m = min(n - 1, max(2, int(sec * SR)))
    r = np.ones(n, dtype=np.float64)
    u = np.linspace(0.0, 1.0, m)
    r[:m] = 2.0 ** (-semis * (1.0 - u) ** 2 / 12.0)          # fast at first, settling gently into the note
    pos = np.concatenate([[0.0], np.cumsum(r[:-1])])
    pos = pos[pos < n - 1]
    i0 = pos.astype(np.int64)
    fr = (pos - i0).astype(np.float32)
    if x.ndim == 1:
        return x[i0] * (1 - fr) + x[i0 + 1] * fr
    return x[:, i0] * (1 - fr) + x[:, i0 + 1] * fr


def bend_curve(spec, n, note_sec):
    """Semitone offset over n samples for a list of ornaments (see Ev.bend)."""
    t = np.arange(n) / SR
    out = np.zeros(n)
    T = max(0.05, note_sec)
    for orn in spec or []:
        kind = orn[0]
        if kind == 'meend':                          # a slow, smooth pull from another note into this one
            semis, frac = float(orn[1]), float(orn[2]) if len(orn) > 2 else 0.45
            L = max(0.06, min(0.9, T * frac))
            u = np.clip(t / L, 0, 1)
            out += semis * (1 - u * u * (3 - 2 * u))           # smoothstep: eases out of the start, settles into the note
        elif kind == 'gamak':                        # shaking up to the note above and back, growing as it's held
            depth, rate = float(orn[1]), float(orn[2]) if len(orn) > 2 else 5.5
            t0 = T * 0.22
            ramp = np.clip((t - t0) / max(0.08, T * 0.25), 0, 1) * (t < T + 0.05)
            out += depth * 0.5 * (1 - np.cos(2 * np.pi * rate * np.maximum(0, t - t0))) * ramp
        elif kind == 'andolan':                      # a slow sway around the note
            depth = float(orn[1])
            ramp = np.clip((t - T * 0.2) / max(0.1, T * 0.3), 0, 1)
            out += depth * np.sin(2 * np.pi * 1.7 * t) * ramp
        elif kind == 'shift':                        # a fixed microtone: maqam quarter tones (e.g. -0.5 = half-flat)
            out += float(orn[1])
        elif kind == 'fall':                         # the end of the note pulled down / up into the next one
            semis = float(orn[1])
            t0 = T * 0.75
            out += semis * np.clip((t - t0) / max(0.05, T * 0.25), 0, 1) ** 2
    return out


def pitch_curve(x, spec, note_sec):
    """Bend a rendered note along an ornament curve (works on synths and recordings alike)."""
    x = np.asarray(x, dtype=np.float32)
    n = x.shape[-1]
    r = 2.0 ** (bend_curve(spec, n, note_sec) / 12.0)
    pos = np.concatenate([[0.0], np.cumsum(r[:-1])])
    pos = pos[pos < n - 1]
    i0 = pos.astype(np.int64)
    fr = (pos - i0).astype(np.float32)
    if x.ndim == 1:
        return x[i0] * (1 - fr) + x[i0 + 1] * fr
    return x[:, i0] * (1 - fr) + x[:, i0 + 1] * fr


def clean_hit(x):
    """A recorded one-shot, ready to fire: any pre-roll before the hit trimmed (so nothing sounds before
    the beat), a 1 ms fade in and a short fade out (no clicks at either end)."""
    if x is None or len(x) < 256:
        return x
    x = np.asarray(x, dtype=np.float32)
    pk = float(np.max(np.abs(x))) + 1e-9
    on = int(np.argmax(np.abs(x) > pk * 0.1))
    start = max(0, on - int(0.0015 * SR))
    x = x[start:].copy()
    k = min(len(x) // 8, int(0.001 * SR))
    if k > 1:
        x[:k] *= np.linspace(0, 1, k, dtype=np.float32)
    k = min(len(x) // 4, int(0.008 * SR))
    if k > 1:
        x[-k:] *= np.linspace(1, 0, k, dtype=np.float32)
    return x


def drum_mod(sig, mod):
    """'rev' a reversed hit (it swells into the next beat), 'cut' gated short, 'pt:N' re-pitched by N semitones,
    'sw:A:B' swept from A to B semitones during the hit (DJ-style pitch dives / rises on hats)."""
    if mod == 'rev':
        k = min(len(sig), int(0.35 * SR)) if sig.ndim == 1 else min(sig.shape[-1], int(0.35 * SR))
        out = sig[..., :k][..., ::-1].copy()
        out[..., :k] *= np.linspace(0, 1, k, dtype=np.float32) ** 2      # fade in from the tail: no click at its start
        return out
    if mod == 'cut':
        k = min(sig.shape[-1], int(0.07 * SR))
        out = sig[..., :k].copy()
        out[..., -int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR), dtype=np.float32)
        return out
    if isinstance(mod, str) and mod.startswith('sw:'):          # a pitch sweep inside the hit: 'sw:0:-9' dives 9 semitones
        try:
            a, b = (float(v) for v in mod[3:].split(':'))
        except ValueError:
            return sig
        n = sig.shape[-1]
        semis = np.linspace(a, b, n)
        pos = np.concatenate([[0.0], np.cumsum(2 ** (semis[:-1] / 12.0))])
        pos = pos[pos < n - 1]
        i0 = pos.astype(np.int64)
        fr = (pos - i0).astype(np.float32)
        return (sig[..., i0] * (1 - fr) + sig[..., i0 + 1] * fr).astype(np.float32)
    if isinstance(mod, str) and mod.startswith('pt:'):
        try:
            semis = float(mod[3:])
        except ValueError:
            return sig
        if not semis:
            return sig
        r = 2 ** (semis / 12.0)
        n = sig.shape[-1]
        pos = np.arange(0, n - 1, r)
        i0 = pos.astype(np.int64)
        fr = (pos - i0).astype(np.float32)
        return (sig[..., i0] * (1 - fr) + sig[..., i0 + 1] * fr).astype(np.float32)
    return sig


def fx_wash(sec, down=False):
    """A noise wash: a low-passed noise bed whose filter opens up (or, down=True, closes and fades after a drop)."""
    n = int(sec * SR)
    w = np.linspace(0, 1, n)
    if down:
        w = w[::-1]
    x = np.random.default_rng(23).standard_normal((2, n))
    lo, mid, hi = lp(x, 500), lp(hp(x, 500), 3500), hp(x, 3500)
    out = lo * (1 - w) ** 2 + mid * 2 * w * (1 - w) * 1.3 + hi * w ** 2 * 1.2
    env = w ** (1.8 if not down else 1.2)
    k = min(n, int(0.03 * SR))
    if not down:
        env[-k:] *= np.linspace(1, 0, k)
    return (hp(out, 150) * env * 0.5).astype(np.float32)


def tape_stop(buf, s0, s1):
    """The tape slows to a halt over s0..s1 (pitch and speed falling together), then silence."""
    n = min(s1, buf.shape[1]) - s0
    if n <= 4:
        return
    speed = (1 - np.linspace(0, 1, n)) ** 1.4
    pos = s0 + np.cumsum(speed)
    pos = np.clip(pos, 0, buf.shape[1] - 2)
    i0 = pos.astype(np.int64)
    fr = (pos - i0).astype(np.float32)
    seg = buf[:, i0] * (1 - fr) + buf[:, i0 + 1] * fr
    seg *= np.linspace(1, 0.2, n, dtype=np.float32) ** 0.5
    buf[:, s0:s0 + n] = seg


def dj_slow(buf, s0, s1, floor=0.32):
    """A fake DJ slowdown before the drop: a hand dragging on the platter - the music keeps playing but slows and
    sinks in pitch (to about a third of the speed), then the drop slams back in at full speed."""
    n = min(s1, buf.shape[1]) - s0
    if n <= 4:
        return
    u = np.linspace(0, 1, n)
    speed = 1 - (1 - floor) * u ** 0.8
    pos = np.clip(s0 + np.cumsum(speed), 0, buf.shape[1] - 2)
    i0 = pos.astype(np.int64)
    fr = (pos - i0).astype(np.float32)
    seg = buf[:, i0] * (1 - fr) + buf[:, i0 + 1] * fr
    seg *= np.float32(1.0) - np.float32(0.35) * (u ** 1.5).astype(np.float32)
    buf[:, s0:s0 + n] = seg


def fx_cymroll(sec):
    """A suspended-cymbal roll: bright noise with the flutter of two soft mallets, growing to a peak at the end."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    x = np.random.default_rng(11).standard_normal((2, n))
    x = hp(lp(x, 13000), 2800)
    rate = 10 + 4 * t / max(sec, 0.1)
    flutter = 1 + 0.3 * np.sin(2 * np.pi * np.cumsum(rate) / SR)
    env = (t / max(sec, 0.1)) ** 2.4
    tail = np.ones(n)
    k = min(n, int(0.04 * SR))
    tail[-k:] = np.linspace(1, 0, k)
    return (x * env * flutter * tail * 0.6).astype(np.float32)


def tape_wobble(x, depth=1.0):
    """Tape wow & flutter. depth 1 = a gentle ~6 cent drift; 3 = the warped, seasick tape of hauntology. The whole mix
    moves together, so the parts stay in tune with each other - only the 'tape speed' drifts."""
    n = x.shape[1]
    t = np.arange(n) / SR
    d = 0.0025 * max(1.0, depth) + depth * (0.0012 * np.sin(2 * np.pi * 0.45 * t) + 0.0009 * np.sin(2 * np.pi * 0.13 * t + 1.3)) \
        + 0.00015 * np.sin(2 * np.pi * 6.3 * t)
    idx = np.arange(n) - d * SR
    return np.vstack([np.interp(idx, np.arange(n), x[c]) for c in range(2)])



def loud_part_lufs(x, win=3.0, top=0.35):
    """Loudness of a song's loud parts: the louder ~third of its 3-second windows (gated like LUFS), so a chorus or a
    drop sets the level, not the intro. Short songs / loops: plain integrated loudness."""
    n = int(win * SR)
    if x.shape[-1] < n * 6:
        return lufs(x)
    vals = np.array([lufs(x[:, i:i + n]) for i in range(0, x.shape[-1] - n, n)])
    vals = vals[vals > -50]
    if len(vals) < 6:
        return lufs(x)
    thr = np.percentile(vals, 100 * (1 - top))
    loud = vals[vals >= thr]
    return float(10 * np.log10(np.mean(10 ** (loud / 10))))

def oversampled(fn, x, factor=2):
    """Run a non-linear stage (saturation, clipping) at `factor` x the sample rate, so the harmonics it adds above
    the audio band are filtered off instead of folding back down as harsh, out-of-key aliasing."""
    if x.shape[-1] < 64:
        return fn(x)
    from .dsp import chunked
    return chunked(lambda v: signal.resample_poly(fn(signal.resample_poly(v, factor, 1, axis=-1)), 1, factor, axis=-1)[..., :v.shape[-1]], x)


# dynamic EQ bands on the master: (centre Hz, Q, max cut dB, how far above the song's own average the band must
# rise before it's cut). They only act when that band builds up (a muddy chord stack, a harsh lead in the drop).
DYN_EQ_BANDS = ((300.0, 1.1, 3.0, 2.5), (3600.0, 1.4, 3.0, 3.5))


def dynamic_eq(x, bands=DYN_EQ_BANDS, amount=1.0, block=1024):
    """Dynamic EQ: each band's level is followed (about 0.2 s) and compared with its own long-term level across the song.
    Where it climbs more than `over` dB above that, a bell cut of up to `max_cut` dB follows it down, smoothly.
    The rest of the time the band is left alone, unlike a static EQ cut that thins the whole song."""
    if amount <= 0 or x.shape[-1] < block * 4:
        return x, {}
    y = np.asarray(x, np.float64)
    stats = {}
    mono = y.mean(axis=0)
    nb = len(mono) // block
    full = 10 * np.log10(uniform_filter1d(np.mean(mono[:nb * block].reshape(nb, block) ** 2, axis=1), 9) + 1e-12)
    for f0, q, max_cut, over in bands:
        bw = f0 / q
        sos = signal.butter(2, [max(20.0, f0 - bw / 2) / (SR / 2), min(SR * 0.45, f0 + bw / 2) / (SR / 2)], 'band',
                            output='sos')
        band = signal.sosfilt(sos, y.mean(axis=0))
        n = len(band) // block
        if n < 4:
            continue
        pw = uniform_filter1d(np.mean(band[:n * block].reshape(n, block) ** 2, axis=1), 9)   # ~0.2 s: build-ups,
        lvl = 10 * np.log10(pw + 1e-12) - full[:n]       # the band's SHARE of the mix (not its level: a drop is
        loud = float(np.percentile(full[:n], 80))        # louder in every band - that's not a build-up)
        live = full[:n] > loud - 4                        # judged in the full sections only: a sparse intro (piano
        ref = float(np.median(lvl[live])) if np.any(live) else float(np.median(lvl))   # alone) isn't mud
        cut = np.clip((lvl - ref - over) * 0.6, 0.0, max_cut) * amount
        cut *= np.clip((full[:n] - (loud - 8)) / 4, 0, 1)
        cut = uniform_filter1d(cut, 3)
        if float(np.max(cut)) < 0.2:
            stats[int(f0)] = 0.0
            continue
        stats[int(f0)] = round(float(np.mean(cut[cut > 0.2])), 1) if np.any(cut > 0.2) else 0.0   # avg cut when on
        stats[f'{int(f0)}_time'] = round(float(np.mean(cut > 0.2)), 2)                             # share of the song
        out = np.empty_like(y)
        zi = None
        for i in range(n + 1):                         # block-wise bell cut, coefficients per block, state carried
            s0, s1 = i * block, min(y.shape[-1], (i + 1) * block)
            if s0 >= s1:
                break
            g = -float(cut[min(i, n - 1)])
            b, a = _peak_coeffs(f0, q, g)
            if zi is None:
                zi = np.zeros((2, 2))
            for c in range(2):
                out[c, s0:s1], zi[c] = signal.lfilter(b, a, y[c, s0:s1], zi=zi[c])
        y = out
    return y, stats


def _peak_coeffs(f0, q, gain_db):
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w), 1 - al / A])
    return b / a[0], a / a[0]


def mono_safe_width(mid, side, w, min_corr=0.2):
    """Width guard: the widest setting (up to `w`) whose left / right correlation stays at or above `min_corr`, so a
    wide genre still sounds wide but doesn't turn phasey and fall apart in mono (phones, club PAs, radio).
    Correlation of (m + w s, m - w s) = (M - w^2 S) / (M + w^2 S), with M, S the mid / side energies."""
    M = float(np.mean(mid[::4] ** 2)) + 1e-12
    S = float(np.mean(side[::4] ** 2)) + 1e-12
    w_max = np.sqrt(M * (1 - min_corr) / ((1 + min_corr) * S))
    return float(min(w, max(w_max, min(w, 0.6))))     # (never narrower than 0.6 just to pass the guard)


DRUM_LAYERS = ('kick', 'snare', 'top')
BIG = ('chorus', 'drop', 'hook', 'B')


def dynamics_arc(sections, layer, L, b2s, gentle=False):
    """(2.10.2) The natural rise and fall of a played song, instead of every section sitting at one level and then
    jumping: the drums dig in a little more across each verse (about -1.2 dB to 0), the pads and chords swell over
    the last two bars into a chorus or drop, and everything eases back over the bar before a break. Gentle,
    acoustic genres move a little more. Returns a gain curve (or None if nothing moves)."""
    k = 1.3 if gentle else 1.0
    g_db = np.zeros(L, dtype=np.float32)
    moved = False
    for i, sec in enumerate(sections):
        a = b2s(sec['bar'] * 4)
        e = min(L, b2s((sec['bar'] + sec['bars']) * 4))
        if e - a < SR:
            continue
        nxt = sections[i + 1]['name'] if i + 1 < len(sections) else None
        bar_s = max(1, (e - a) // max(1, sec['bars']))
        if sec['name'] in ('verse', 'A') and layer in DRUM_LAYERS:
            g_db[a:e] += np.linspace(-1.2 * k, 0.0, e - a, dtype=np.float32)
            moved = True
        if nxt in BIG and layer in ('pad', 'chords', 'arp') and sec['name'] not in BIG:
            n2 = min(e - a, 2 * bar_s)
            g_db[a:e - n2] -= 1.0 * k
            g_db[e - n2:e] += np.linspace(-1.0 * k, 0.0, n2, dtype=np.float32)
            moved = True
        if nxt in ('break', 'bridge', 'C') and sec['name'] in BIG:
            n1 = min(e - a, bar_s)
            g_db[e - n1:e] += np.linspace(0.0, -1.5 * k, n1, dtype=np.float32)
            moved = True
    if not moved:
        return None
    g_db = uniform_filter1d(g_db, int(0.25 * SR))
    return (10 ** (g_db / 20)).astype(np.float32)


def master(x, cfg, log=print):
    master.last_dyn_eq = {}
    log('   mastering: EQ > dynamic EQ > glue comp > stereo image > saturation > limiter')
    x = hp(x, 28)
    if cfg.get('sub_cut'):                                # (1.91) genres with no sub at all (a synthscape): a steep cut
        x = hp(x, float(cfg['sub_cut']), 4).astype(x.dtype)
    l0 = lufs(x)
    x *= 10 ** ((-18 - l0) / 20)
    x = eq(x, 'lowshelf', 90, 0.7, cfg.get('low', 1.0))
    gentle = cfg.get('gentle')
    # (2.10.2) mix like a record: a little more room in the low mids, the brightest top pulled back a touch, a softer
    # presence lift and the harsh 4-5 kHz eased - the air lift each genre asks for still applies, just 1 dB less
    x = eq(x, 'peak', 320, 0.8, -0.9 if gentle else -2.0)
    x = eq(x, 'peak', 3000, 0.8, 0.2)
    x = eq(x, 'peak', 4600, 1.2, -0.7)
    x = eq(x, 'highshelf', 9000, 0.7, float(cfg.get('air', 1.5)) - 1.0)
    if cfg.get('tone'):                # steer the tonal balance toward the genre's reference records
        x0 = x
        x = tone_match(x, cfg['tone'], log, amount=float(cfg.get('tone_amount', 0.6)), limit=float(cfg.get('tone_limit', 3.0)))
        if cfg.get('tone_quiet') and x.shape[1] > 30 * SR:
            # (1.86) a reference song's quiet parts have their own balance (a breakdown is thinner, darker or airier
            # than the drop): the song's loud parts are matched to the reference's loud parts, its quiet parts to the
            # reference's quiet parts, crossfaded by the song's own loudness
            xq = tone_match(x0, cfg['tone_quiet'], lambda *a: None, amount=float(cfg.get('tone_amount', 0.6)), limit=3.0)
            m = loud_mask(x0)
            x = xq * (1 - m)[None, :] + x * m[None, :]
            log('   tone match: quiet sections matched to the reference\'s quiet sections')
    if cfg.get('vintage_lp'):        # a 60s tape / tube top end: rolls off above this (Hz) - dark, warm, bass-forward
        x = lp(x, float(cfg['vintage_lp']))
    if cfg.get('lofi'):
        x = lp(x, 9500)
        x = tape_wobble(x, cfg.get('wobble', 1.0))
        x = soft(x * 1.4, 1.3) / 1.4
    if cfg.get('dyn_eq', 1.0) > 0:     # tame low-mid build-up / harshness only where it happens
        x, master.last_dyn_eq = dynamic_eq(x, amount=float(cfg.get('dyn_eq', 0.6 if gentle else 1.0)))
    if gentle:     # acoustic / orchestral: keep the dynamics, no pumping glue
        x = compressor(x, thresh=-24, ratio=1.3, attack=0.05, release=0.4, win=0.05)
    else:   # (2.5.3) the level detector averages over 50 ms - two cycles of a 40 Hz sub. At 20 ms it rose and fell
        #     with every wave of a low bass, so the glue compressor rode the waveform and fuzzed the bass ('clipping')
        x = compressor(x, thresh=cfg.get('glue_thresh', -14) - 1.5, ratio=2.0, attack=0.025, release=0.2, win=0.05, sc_hp=90)
    mid = (x[0] + x[1]) / 2
    # width 1.0 = the mix as it is (it used to widen every song by 15%); the genre's width x your width slider
    w_ = max(0.0, min(2.0, float(cfg.get('genre_width', 1.0)) * float(cfg.get('width', 1.0))))
    side = hp((x[0] - x[1]) / 2, 120, 2)               # below 120 Hz the side is removed: the low end stays mono
    w_ = mono_safe_width(mid, side, w_, float(cfg.get('min_corr', 0.2)))
    side = side * w_
    x = np.vstack([mid + side, mid - side])
    drv = 1.05 + 2.0 * cfg.get('drive', 0.0)
    if not gentle or cfg.get('drive', 0) > 0:
        x = oversampled(lambda u: soft(u * 1.1, drv) / 1.1, x)
    target = cfg.get('lufs', -10)
    # the loudness target is for the song's LOUD parts (drops, choruses), the way a mastering engineer works - not the
    # whole-song average. Aiming the average at -10 squashed a dynamic track: long quiet intros / breakdowns pulled the
    # average down, so the drop got pushed into the limiter until it was barely louder than the breakdown (a 5 dB
    # arrangement came out ~1 dB apart). Flat songs land where they did; dynamic ones keep their build-ups and drops.
    meas = loud_part_lufs if not cfg.get('integrated') else lufs
    g_db = target - meas(x)
    # never let the limiter squash the drum hits: at most `max_gr` dB of gain reduction on the loud peaks (99.9th
    # percentile). A song that can't reach its loudness target without that ends up a little quieter, not distorted.
    a = np.max(np.abs(x), axis=0)
    p999 = float(np.percentile(a, 99.9)) + 1e-9
    max_gr = float(cfg.get('max_gr', 2.0))                 # (2.10.2) at most 2 dB of limiting (was 3): punchier peaks
    g_cap = max_gr + 20 * np.log10(10 ** (-1.0 / 20) / p999)
    # and never push a loud bass line into the limiter: the band below 120 Hz may reach ~80% of the ceiling (the
    # bass-safe pre-limiter takes at most another 1.5 dB) - a bass-heavy song ends up a little quieter, not clipped
    lo = signal.sosfiltfilt(signal.butter(2, 120 / (SR / 2), output='sos'), x.mean(axis=0))
    lp999 = float(np.percentile(np.abs(lo), 99.9)) + 1e-9
    g_cap = min(g_cap, 1.5 + 20 * np.log10(0.8 * 10 ** (-1.0 / 20) / lp999))
    clip_amt = float(cfg.get('clip', 0.0 if gentle else 0.5))   # (2.10.2) half the clipping (was 1.0)

    def chain(v, g):                                       # gain > clipper > bass-safe limiter > limiter
        v = peak_round(v * 10 ** (g / 20))
        if clip_amt > 0:
            v = clip_stage(v, out_db=0.8 * clip_amt)
        return limiter(low_limit(v, 10 ** (-1.0 / 20) * 0.78), ceiling_db=-1.0, hold=0.025)   # (held for a whole 40 Hz
        #                                                         cycle: the gain never wobbles inside one bass wave - 1.80)
    # (1.92.4) find the gain on an excerpt of the loud windows the loudness is measured on (up to 12 of them, each
    # with a short lead-in so the limiter has settled), then master the whole song once - the same result, several
    # times faster than limiting the full song up to eight times
    ex = None
    nwin = int(3.0 * SR)
    if meas is loud_part_lufs and x.shape[-1] >= nwin * 6:
        starts = list(range(0, x.shape[-1] - nwin, nwin))
        vals = np.array([lufs(x[:, i:i + nwin]) for i in starts])
        ok = vals > -50
        if ok.sum() >= 6:
            thr = np.percentile(vals[ok], 65)
            loud = [st_ for st_, v in zip(starts, vals) if v >= thr and v > -50]
            if len(loud) > 12:
                loud = [loud[int(k)] for k in np.linspace(0, len(loud) - 1, 12)]
            pre = int(0.5 * SR)
            segs = [(max(0, i - pre), i) for i in loud]
            ex = (np.concatenate([x[:, a:b + nwin] for a, b in segs], axis=1), [(b - a, nwin) for a, b in segs])

    def meas_ex(v):                                        # loudness of the excerpt's measured parts (pre-rolls left out)
        e, pos = [], 0
        for p0, n0 in ex[1]:
            e.append(10 ** (lufs(v[:, pos + p0:pos + p0 + n0]) / 10))
            pos += p0 + n0
        return float(10 * np.log10(np.mean(e) + 1e-12))
    y = x
    if ex is not None:
        for _ in range(8):
            g_db = min(g_db, g_cap)
            err = target - meas_ex(chain(ex[0], g_db))
            if abs(err) < 0.1 or (err > 0 and g_db >= g_cap - 1e-6):
                break
            g_db += err
        y = chain(x, g_db)
        err = target - meas(y)                             # one check on the whole song (and a nudge if needed)
        if abs(err) >= 0.25 and not (err > 0 and g_db >= g_cap - 1e-6):
            g_db = min(g_cap, g_db + err)
            y = chain(x, g_db)
    else:
        for _ in range(8):
            g_db = min(g_db, g_cap)
            y = chain(x, g_db)
            err = target - meas(y)
            if abs(err) < 0.1 or (err > 0 and g_db >= g_cap - 1e-6):
                break
            g_db += err
    # (1.85) never squashed flat: the whole song keeps at least ~7.8 dB between its peaks and its loudness (big room
    # and dubstep masters used to reach -7.9 LUFS with 6.9 dB left - loud, but the kick and drops lost their punch)
    min_plr = float(cfg.get('min_plr', 8.0))
    if min_plr > 0:
        short = min_plr - (-1.0 - lufs(y))
        if short > 0.15:
            g_db -= short
            y = chain(x, g_db)
    # true peak: the peaks between the samples (4x oversampled) kept under -1 dBTP, so the file never clips when
    # it's converted to MP3 / AAC or played through a DAC that reconstructs the waveform
    ceil_ = 10 ** (-1.0 / 20)
    from .dsp import true_peak as _tp
    tp = _tp(y)
    if tp > ceil_:                          # a last overshoot: limit just those peaks a little harder (turning the whole
        over_db = 20 * np.log10(tp / ceil_)    # song down for one peak used to land it under its loudness target)
        y = limiter(y, ceiling_db=-1.0 - over_db - 0.05)
        tp = _tp(y)
        if tp > ceil_:
            y = y * (ceil_ / tp)
    return y


# ----------------------------------------------------------------------------- 1.85: transition FX, tuned to the key
# Each genre family has its own riser: a supersaw that climbs two octaves with the filter opening and a stutter at the
# end (house / trance / big room), an FM siren whose wobble speeds up (dubstep / bass), a noise sweep with a saw
# underneath (DnB / breaks), a plain noise sweep elsewhere. Impacts are a sub drop on the song's root note with a noise
# burst and a short tail; downlifters fall in pitch and filter. All in stereo, widening as they rise.
def _trim():
    """Hand freed memory back to the system (Linux / glibc): between parts the allocator otherwise keeps the freed
    blocks of the last part's temporaries, and the next part's peak lands on top of them."""
    global _LIBC
    try:
        if _LIBC is None:
            import ctypes
            import ctypes.util
            _LIBC = ctypes.CDLL(ctypes.util.find_library('c') or 'libc.so.6')
        if hasattr(_LIBC, 'malloc_trim'):
            _LIBC.malloc_trim(0)
    except Exception:                                     # noqa: BLE001 - macOS / Windows: their allocators do this themselves
        _LIBC = False


_LIBC = None


def is_drum_layer(tcfg):
    return tcfg.get('layer') in ('kick', 'snare', 'top')


TRACK_CACHE = __import__('collections').OrderedDict()   # (1.87) rendered parts, reused by the next preview
RENDER_VERSION = '1.87'
SC_SHAPE_GROUP = {'House & Disco': 'pump', 'Techno & Trance': 'classic', 'Drum & Bass, Breaks & Hard': 'tight',
                  'Dubstep, Garage & Bass': 'tight', 'Pop, R&B & Hopecore': 'classic'}
SC_SHAPE_GENRE = {'bigroom': 'pump', 'electro': 'pump', 'trance': 'breathe', 'uplifting_trance': 'breathe',
                  'vocal_trance_remix': 'breathe', 'hardstyle': 'tight', 'french_house': 'pump', 'techno': 'classic',
                  'hard_techno': 'tight', 'eurodance': 'pump', 'electro_prog_trance': 'pump',
                  'festival_techno': 'pump', 'classic_vocal_trance': 'pump', 'dark_dubstep_classic': 'tight'}
RISER_FAMILY = {'House & Disco': 'saw', 'Techno & Trance': 'saw', 'Dubstep, Garage & Bass': 'siren',
                'Drum & Bass, Breaks & Hard': 'noisesaw', 'Retro & Video Game': 'saw', 'Pop, R&B & Hopecore': 'noise'}


def _bands_sweep(x, w, up=True):
    """Noise whose brightness follows w (0..1): crossfades a ladder of band-passes from low to high."""
    edges = [150, 400, 1000, 2500, 6000, 14000]
    out = np.zeros_like(x)
    pos = w * (len(edges) - 2) if up else (1 - w) * (len(edges) - 2)
    for i in range(len(edges) - 1):
        band = signal.sosfilt(signal.butter(2, [edges[i] / (SR / 2), min(edges[i + 1], 18000) / (SR / 2)], 'band', output='sos'), x, axis=-1)
        out += band * np.clip(1 - np.abs(pos - i), 0, 1)
    return out


def fx_riser2(sec, root_hz, style='saw', spb=0.47, seed=5):
    n = max(int(sec * SR), 64)
    t = np.arange(n) / SR
    w = t / sec
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((2, n))
    noise = _bands_sweep(x, w) * (0.35 if style != 'noise' else 0.7)
    tone = np.zeros((2, n))
    base = root_hz
    while base < 110:
        base *= 2
    if style in ('saw', 'noisesaw'):
        fr = base * 2 ** (2 * w ** 1.4)                          # two octaves up
        for k, c in enumerate((-18, -7, 0, 7, 18)):
            tone[k % 2] += _va.saw(fr * 2 ** (c / 1200), n, rng.random()) * 0.3
        tone = _va.vcf(tone, 300 + 11000 * w ** 1.6, 0.35, 1.2)
        tone = np.tanh(tone * (1 + 3 * w)) * (0.7 if style == 'saw' else 0.35)
        if style == 'saw':                                       # the last quarter stutters, faster and faster
            g_rate = np.where(w > 0.75, np.where(w > 0.9, 8.0, 4.0), 0.0) / spb
            ph = np.cumsum(g_rate) / SR
            gate = np.where(g_rate > 0, (ph % 1) < 0.55, 1.0).astype(float)
            tone *= np.convolve(gate, np.ones(64) / 64, 'same')[None, :]
    elif style == 'siren':
        fr = base * 2 * 2 ** (1.5 * w ** 1.3)
        rate = (1 + 7 * w ** 2) / spb                            # the wobble speeds up into the drop
        lfo = 0.5 - 0.5 * np.cos(2 * np.pi * np.cumsum(rate) / SR)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        y = np.tanh(np.sin(ph + (1 + 5 * lfo) * np.sin(2 * ph)) * (1.5 + 2 * w))
        y = signal.sosfilt(signal.butter(2, 150 / (SR / 2), 'high', output='sos'), y)
        tone = np.vstack([y, np.roll(y, 40)]) * 0.5
    y = noise + tone
    mid, side = (y[0] + y[1]) / 2, (y[0] - y[1]) / 2
    side = side * (0.3 + 0.9 * w)                                # widening as it rises
    y = np.vstack([mid + side, mid - side]) * (w ** 2.0)
    k = min(n, int(0.012 * SR))
    y[:, -k:] *= np.linspace(1, 0, k)                            # a hair of silence before the drop lands
    return (hp(y, 120) * 0.6).astype(np.float32)


def fx_impact2(root_hz, seed=7):
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    sub = root_hz
    while sub > 62:
        sub /= 2
    while sub < 38:
        sub *= 2
    f = sub * (1 + 1.5 * np.exp(-t / 0.05))
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7)
    rng = np.random.default_rng(seed)
    burst = rng.standard_normal((2, n)) * np.exp(-t / 0.08)
    burst = signal.sosfilt(signal.butter(2, [200 / (SR / 2), 9000 / (SR / 2)], 'band', output='sos'), burst, axis=-1)
    tail = rng.standard_normal((2, n)) * np.exp(-t / 0.6) * 0.25
    tail = signal.sosfilt(signal.butter(2, [300 / (SR / 2), 5000 / (SR / 2)], 'band', output='sos'), tail, axis=-1)
    y = np.tanh((boom[None, :] * 1.2 + burst * 0.6 + tail) * 1.4)
    from .dsp import fade_out
    return fade_out(y, 0.3).astype(np.float32) * 0.8


SHOUT_WORDS = {'oi': ('o', 'i'), 'hey': ('e', 'i'), 'yeah': ('i', 'a'), 'whoa': ('u', 'o'), 'go': ('o', 'u')}


def fx_shout(word='oi', seed=11, low=True, spb=0.47):
    """(1.90) A hype-man shout for the moment the music stops before a drop: a synthesized voice (a sawtooth throat,
    breath noise, three moving formants from one vowel to the next), an octave-down 'monster' double, a gritty
    megaphone band and a short echo tail. Synthesized here, so there is no sample to clear."""
    v0, v1 = SHOUT_WORDS.get(word, SHOUT_WORDS['oi'])
    rng = np.random.default_rng(seed)
    dur = 0.42 + 0.1 * rng.random()
    n = int(dur * SR)
    t = np.arange(n) / SR
    w = t / dur
    f0 = (205 + 30 * rng.random()) * (1 + 0.12 * np.sin(np.pi * np.minimum(1, w * 1.6)) - 0.18 * w ** 2)
    f0 = f0 * (1 + 0.012 * rng.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1)))      # a rough, unsteady voice
    ph = np.cumsum(f0) / SR
    src = 2 * (ph % 1.0) - 1
    if low:
        src = src * 0.55 + (2 * ((ph / 2) % 1.0) - 1) * 0.75                                     # the octave-down double
    src = src + rng.standard_normal(n) * (0.18 + 0.5 * np.exp(-t / 0.035))                       # breath, and the 'h' onset
    k = np.clip((w - 0.25) / 0.45, 0, 1)                                                          # the vowel moves after a beat
    out = np.zeros(n)
    fa, fb = _va.FORMANTS[v0], _va.FORMANTS[v1]
    hop = 512
    zi = [None, None, None]
    for i0 in range(0, n, hop):                                                                   # formants, frame by frame
        kk = float(k[min(n - 1, i0)])
        seg = src[i0:i0 + hop]
        for j in range(3):
            fc = fa[j] * (1 - kk) + fb[j] * kk
            sos = signal.butter(2, [fc * 0.85 / (SR / 2), min(0.99, fc * 1.15 / (SR / 2))], 'band', output='sos')
            if zi[j] is None:
                zi[j] = np.zeros((sos.shape[0], 2))
            y, zi[j] = signal.sosfilt(sos, seg, zi=zi[j])
            out[i0:i0 + hop] += y * (1.0, 0.7, 0.4)[j]
    env = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.09).clip(0)
    out = np.tanh(out * env * 6.0)                                                                # shouted, a bit torn
    out = signal.sosfilt(signal.butter(2, [320 / (SR / 2), 4200 / (SR / 2)], 'band', output='sos'), out)
    tail = int(1.6 * SR)
    y = np.zeros((2, n + tail))
    y[:, :n] = out[None, :]
    d = max(1, int(spb * 0.75 * SR))                                                              # a dotted-8th echo, left / right
    for r in range(1, 5):
        if d * r < y.shape[1]:
            y[r % 2, d * r:] += y[0, :y.shape[1] - d * r] * (0.42 ** r) * (r <= 1 or True)
    y = y + reverb(y.astype(np.float32), make_ir(1.4, 0.015, 0.8)) * 0.22
    pk = float(np.max(np.abs(y))) or 1.0
    return (y / pk * 0.85).astype(np.float32)


def rewind(buf, s0, s1):
    """(1.90) The DJ's rewind ('pull up'): the hand grabs the record, which stops and spins backwards, faster and faster,
    over s0..s1 - the music rushing back the way it came - then silence until the tune starts again."""
    n = min(s1, buf.shape[1]) - s0
    if n <= 4:
        return
    u = np.linspace(0, 1, n)
    speed = np.where(u < 0.12, 1 - u / 0.12, -5.5 * (np.clip(u - 0.12, 0, None) / 0.88) ** 1.3)                  # grab, stop, spin back
    pos = np.clip(s0 + np.cumsum(speed), 0, buf.shape[1] - 2)
    i0 = pos.astype(np.int64)
    fr = (pos - i0).astype(np.float32)
    seg = buf[:, i0] * (1 - fr) + buf[:, i0 + 1] * fr
    g = np.ones(n, dtype=np.float32)
    g[-int(0.18 * n):] = np.linspace(1, 0, int(0.18 * n), dtype=np.float32) ** 1.5
    buf[:, s0:s0 + n] = seg * g[None, :]


def fx_downlift2(sec, root_hz, seed=9):
    n = max(int(sec * SR), 64)
    t = np.arange(n) / SR
    w = t / sec
    rng = np.random.default_rng(seed)
    noise = _bands_sweep(rng.standard_normal((2, n)), w, up=False) * 0.5
    base = root_hz
    while base < 220:
        base *= 2
    fr = base * 2 ** (-2 * w)
    tone = np.vstack([_va.saw(fr * 2 ** (-6 / 1200), n, 0.1), _va.saw(fr * 2 ** (6 / 1200), n, 0.6)]) * 0.25
    tone = _va.vcf(tone, 9000 * (1 - w) ** 2 + 200, 0.3, 1.1)
    y = (noise + tone) * (1 - w) ** 1.5
    return (hp(y, 120) * 0.6).astype(np.float32)
