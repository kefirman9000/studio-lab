"""Rendering: events -> tracks -> mix (sidechain, sends, buses) -> master."""
import math
import os
import random
import time

import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d

from .dsp import (SR, hp, lp, eq, soft, compressor, limiter, low_limit, lufs, active_rms_db, make_ir, reverb, pingpong,
                  make_spring_ir, dub_delay, svf_sweep,
                  sweep_region, write_wav_float)
from .instruments import INSTRUMENTS, DRUMS, fx_riser, fx_impact, fx_vinyl, fx_texture
from . import va as _va
from . import fx2 as _fx2

SYNTH_TAKES = 3          # analog character: takes per (note, length, velocity layer)
from .compose import SECTION_ENERGY, GROOVES

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
    x = np.asarray(buf, np.float64)
    n = x.shape[1]
    t = np.arange(n) / SR
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


def mix_report(y, song=None, spb=None, tone=None, low_env=None, dyn_eq=None):
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
    tp = 20 * np.log10(float(np.max(np.abs(signal.resample_poly(y, 4, 1, axis=-1)))) + 1e-12)
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
    if tone_dev:
        names = ('sub', 'bass', 'low-mids', 'mids', 'upper mids', 'presence', 'highs', 'air', 'top air')
        far = [(names[i], d) for i, d in enumerate(tone_dev) if abs(d) > 4.5 and i < 8]
        if far:
            warn.append('tone vs genre refs: ' + ', '.join(f"{n} {'+' if d > 0 else ''}{d:.0f} dB" for n, d in far[:3]))
    return dict(lufs=round(L, 1), true_peak=round(float(tp), 1), plr=round(float(plr), 1), correlation=round(corr, 2),
                low_side_db=round(float(low_side), 1), section_contrast=round(contrast, 1), lra=round(lra, 1),
                st_max=round(st_max, 1), mono_drop=round(float(mono_drop), 1), tone_dev=tone_dev,
                kick_bass_overlap=kb_overlap, dyn_eq=dyn_eq or {}, warnings=warn)


def auto_lp(buf, cut, block=256):
    """A 12 dB low-pass whose cutoff follows `cut` (Hz per sample), in blocks with carried state; blocks where it is
    wide open are (a track that never closes is passed straight through)."""
    from .dsp import biquad
    x = np.asarray(buf, np.float64)
    out = x.copy()
    n = x.shape[1]
    if float(np.min(cut[:n])) >= 17500:
        return out
    zi = np.zeros((2, 2))
    for s0 in range(0, n, block):
        e = min(n, s0 + block)
        b, a = biquad('lowpass', float(min(cut[s0], SR * 0.45)), 0.707)
        for c in range(2):
            out[c, s0:e], zi[c] = signal.lfilter(b, a, x[c, s0:e], zi=zi[c])
    return out

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
        if g and layer in g:                            # genre timing feel (e.g. Dilla-late snares, pushed Afro hats)
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

    def _real_drum(self, inst, ev, idx):
        """Real kit / percussion hit with a velocity layer and a different take each time (None: not available)."""
        from . import samplelibs as sl
        kit, perc = self.st.get('real_kit'), self.st.get('real_perc')
        name = None
        rs = self.st.get('real_snare')
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
        if tcfg['inst'] == 'texture':
            buf[0] = fx_texture(self.length)
            buf[1] = fx_texture(self.length)
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
        real_drums = is_drum and (self.st.get('real_kit') or self.st.get('real_perc')) and not tcfg.get('synth')
        brk = self.st.get('break_seq') or {}
        # kicks are never humanised (a layered kick would flam), and a break plays as one tight unit
        tight = tcfg['name'] == kick or tcfg['layer'] == 'kick' or tcfg['name'] in brk or tcfg['name'] in ('lkick', 'lsnare')
        for i, ev in enumerate(evs):
            s = int((self.t_of(ev.beat, human=not tight, layer=tcfg['layer'], swing=is_drum or ev.dur < HELD, track=tcfg['name'])
                     + getattr(ev, 'strum', 0.0) * self.spb) * SR)
            sig = None
            if real_drums:
                sig = self._real_drum(tcfg.get('real') or tcfg['inst'], ev, i)
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
            self._add(buf, sig * ev.vel, s)
        if self.st.get('sampler') and tcfg['layer'] in ('chords', 'lead', 'arp', 'pad') and np.any(buf):
            buf = sp1200(buf)                             # the sampled-loop grit of an SP-1200 / MPC
        if tcfg.get('amp') and (tcfg['inst'].startswith('real:') or tcfg['inst'] in ('guitar', 'mutedgtr')):
            buf = guitar_amp(buf, float(tcfg['amp']))
        if tcfg.get('drive'):
            buf = (soft(buf * (1 + tcfg['drive'] * 3), 1.5) / (1 + tcfg['drive'])).astype(np.float32)
        if tcfg.get('gate'):
            buf = self._gate(buf, tcfg['gate'])
        if tcfg.get('chorus'):
            buf = chorus(buf, float(tcfg['chorus']))
        if any(tcfg.get(k) for k in ('phaser', 'flanger', 'trem', 'wah', 'crush', 'wide', 'ott')) and np.any(buf):
            buf = track_fx(buf, tcfg, self.spb).astype(np.float32)
        if tcfg.get('sweep') and np.any(buf):             # techno: a filter that opens and closes over 16-32 bars
            lo_hz, hi_hz, bars = tcfg['sweep']
            n = buf.shape[1]
            t = np.arange(n) / SR
            period = max(1.0, bars * 4 * self.spb)
            cut = lo_hz * (hi_hz / lo_hz) ** (0.5 - 0.5 * np.cos(2 * np.pi * t / period))
            buf = np.vstack([svf_sweep(buf[c], cut, q=0.9) for c in range(buf.shape[0])]).astype(np.float32)
        if tcfg['name'] == self.st.get('kick_track', 'kick') and self.st.get('rumble') and np.any(buf):
            buf = self._rumble(buf, float(self.st['rumble']))
        if tcfg.get('leslie_fx') and np.any(buf):
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
        return (2.0 ** (-depth * (1 - lfo))).astype(np.float64)

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
        return np.exp(uniform_filter1d(np.log(cut), int(0.4 * SR)))

    def sc_arc(self, song, b2s, L):
        """How hard the kick ducks the music, section by section: deepest in the drops, gentle in the breakdown."""
        g = np.ones(L)
        for sec in song['sections']:
            a, b = b2s(sec['bar'] * 4), min(L, b2s((sec['bar'] + sec['bars']) * 4))
            r = self.ARC_SC.get(sec['name'])
            if b > a and r:
                g[a:b] = np.linspace(r[0], r[1], b - a)
        return uniform_filter1d(g, int(0.4 * SR))

    def sidechain_curve(self, release_beats):
        duck = np.zeros(self.length, dtype=np.float32)
        rel = release_beats * self.spb
        n = int(rel * SR)
        t = np.arange(n) / SR
        shape = ((1 - np.clip(t / rel, 0, 1)) ** 2 * np.minimum(t / 0.004, 1)).astype(np.float32)
        for kt in self.kick_times():
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
        rev_send = np.zeros((2, L), dtype=np.float32)
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
        for ti, tcfg in enumerate(st['tracks']):
            name = tcfg['name']
            evs = by_track.get(name, [])
            if not evs and tcfg['layer'] != 'fx':
                continue
            if tcfg['layer'] == 'fx' and 'fx' in (opts.muted or []):
                continue
            t0 = time.time()
            buf = self.render_track(tcfg, evs)
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
            for s0, s1 in gaps:
                if tcfg['layer'] != 'fx':
                    buf[:, s0:s1] = 0
            buf *= env32[None, :]
            auto = (getattr(opts, 'automation', None) or {}).get(name)
            if auto and np.any(buf):                       # your volume line from the song editor
                buf *= self.automation_curve(auto, buf.shape[1])[None, :]
            if tcfg['layer'] in ('kick', 'bass') and np.any(buf):   # low-band envelopes for the kick / bass overlap check
                lo_e = np.abs(lp(buf.mean(axis=0), 100, 2))
                hop = 441
                m_ = len(lo_e) // hop
                e_ = lo_e[:m_ * hop].reshape(m_, hop).max(axis=1)
                prev_ = self.low_env.get(tcfg['layer'])
                self.low_env[tcfg['layer']] = e_ if prev_ is None else np.maximum(prev_[:m_], e_[:len(prev_)])
            if tcfg['rev']:
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
            if tcfg['layer'] in ('kick', 'snare', 'top'):
                drums += buf
            else:
                mix += buf
            if stems_dir:
                path = os.path.join(stems_dir, f'{ti + 1:02d}_{name}.wav')
                write_wav_float(path, buf)
                stems.append(dict(name=name, layer=tcfg['layer'], inst=tcfg['inst'], path=path))
            self.log(f'   rendered {name:<11} {len(evs):5d} notes  {time.time() - t0:5.1f}s')
            if progress:
                progress((ti + 1) / (n_tracks + 3))
        # ---- one-shot FX
        fxbuf = np.zeros((2, L), dtype=np.float32)
        if 'fx' not in (opts.muted or []):
            for kind, b, d in song['fx']:
                s = b2s(b)
                if kind == 'crash':
                    self._add(fxbuf, self._drum('crash') * 0.5, s)
                elif kind == 'impact':
                    self._add(fxbuf, fx_impact().astype(np.float32) * 0.8, s)
                elif kind == 'riser' and d > 0:
                    self._add(fxbuf, fx_riser(d * self.spb).astype(np.float32) * 0.6, s)
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
        drums = drum_bus(drums, float(st.get('drum_drive', 0.25)))
        if stems_dir and np.any(drums):
            path = os.path.join(stems_dir, '00_drum_bus.wav')
            write_wav_float(path, drums)
            stems.insert(0, dict(name='drum_bus', layer='drums', inst='drums', path=path, bus=True))
        mix = mix.astype(np.float64) + drums
        # ---- returns
        self.log('   reverb + delay returns')
        returns = np.zeros_like(mix)
        if np.any(rev_send):
            ir = make_spring_ir(st['reverb']) if st.get('spring') else room_ir(st['reverb'], st.get('rev_predelay', 0.02),
                                                                                 st.get('category'))
            rv = eq(reverb(rev_send.astype(np.float64), ir), 'lowshelf', 300, 0.7, -4.0)
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
            returns += rv * 0.55
        for k_, snd in self._dly_extra.items():
            if np.any(snd):
                returns += hp(pingpong(snd.astype(np.float64), k_ * self.spb, fb=0.4), 250) * 0.45
        if np.any(dly_send):
            dl = hp(pingpong(dly_send.astype(np.float64), st['delay_beats'] * self.spb, fb=0.42), 250)
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
        w = uniform_filter1d(w, max(1, int(4 * self.spb * SR)))
        x = mix.astype(np.float64)
        mid, side = (x[0] + x[1]) / 2, (x[0] - x[1]) / 2
        lo = signal.sosfiltfilt(signal.butter(2, 150 / (SR / 2), output='sos'), side)
        side = lo + (side - lo) * w
        return np.vstack([mid + side, mid - side]).astype(mix.dtype)


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
    u = signal.resample_poly(x, 2, 1, axis=-1)
    a = np.abs(u)
    w = top - k
    u = np.where(a > k, np.sign(u) * (k + w * np.tanh((a - k) / w)), u)
    return signal.resample_poly(u, 1, 2, axis=-1)[..., :x.shape[-1]].astype(x.dtype)


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


def drum_bus(drums, drive=0.25):
    """Drum-bus glue that behaves the same however loud the drums arrive: work at a fixed level (peaks at -6 dBFS),
    compress gently a few dB above the kit's own average with a slow-enough attack that the hits keep their snap,
    saturate with unity small-signal gain (only the very top of a peak rounds off), then restore the level."""
    x = np.asarray(drums, dtype=np.float64)
    pk = float(np.max(np.abs(x))) if x.size else 0.0
    if pk < 1e-6:
        return x
    g = 0.5 / pk
    y = x * g
    ref = active_rms_db(y)
    y = compressor(y, thresh=ref + 5.0, ratio=2.0, attack=0.012, release=0.12)
    k = 1.0 + max(0.0, drive)
    y = np.tanh(y * k) / k
    return y / g


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
    """Delayed, widening vibrato on a held note (a sax player's 'Kenny G' vibrato): starts straight, then ~5.5 Hz
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
    u = signal.resample_poly(x, factor, 1, axis=-1)
    return signal.resample_poly(fn(u), 1, factor, axis=-1)[..., :x.shape[-1]]


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


def master(x, cfg, log=print):
    master.last_dyn_eq = {}
    log('   mastering: EQ > dynamic EQ > glue comp > stereo image > saturation > limiter')
    x = hp(x, 28)
    l0 = lufs(x)
    x *= 10 ** ((-18 - l0) / 20)
    x = eq(x, 'lowshelf', 90, 0.7, cfg.get('low', 1.0))
    gentle = cfg.get('gentle')
    if not gentle:
        x = eq(x, 'peak', 320, 1.0, -1.5)
    x = eq(x, 'peak', 3000, 0.8, 0.5)
    x = eq(x, 'highshelf', 9000, 0.7, cfg.get('air', 1.5))
    if cfg.get('tone'):                # steer the tonal balance toward the genre's reference records
        x = tone_match(x, cfg['tone'], log, amount=float(cfg.get('tone_amount', 0.6)))
    if cfg.get('vintage_lp'):        # a 60s tape / tube top end: rolls off above this (Hz) - dark, warm, bass-forward
        x = lp(x, float(cfg['vintage_lp']))
    if cfg.get('lofi'):
        x = lp(x, 9500)
        x = tape_wobble(x, cfg.get('wobble', 1.0))
        x = soft(x * 1.4, 1.3) / 1.4
    if cfg.get('dyn_eq', 1.0) > 0:     # tame low-mid build-up / harshness only where it happens
        x, master.last_dyn_eq = dynamic_eq(x, amount=float(cfg.get('dyn_eq', 0.6 if gentle else 1.0)))
    if gentle:     # acoustic / orchestral: keep the dynamics, no pumping glue
        x = compressor(x, thresh=-24, ratio=1.3, attack=0.05, release=0.4, win=0.03)
    else:
        x = compressor(x, thresh=cfg.get('glue_thresh', -14), ratio=2.0, attack=0.025, release=0.2, win=0.02)
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
    max_gr = float(cfg.get('max_gr', 3.0))
    g_cap = max_gr + 20 * np.log10(10 ** (-1.0 / 20) / p999)
    # and never push a loud bass line into the limiter: the band below 120 Hz may reach ~80% of the ceiling (the
    # bass-safe pre-limiter takes at most another 1.5 dB) - a bass-heavy song ends up a little quieter, not clipped
    lo = signal.sosfiltfilt(signal.butter(2, 120 / (SR / 2), output='sos'), x.mean(axis=0))
    lp999 = float(np.percentile(np.abs(lo), 99.9)) + 1e-9
    g_cap = min(g_cap, 1.5 + 20 * np.log10(0.8 * 10 ** (-1.0 / 20) / lp999))
    clip_amt = float(cfg.get('clip', 0.0 if gentle else 1.0))
    y = x
    for _ in range(8):
        g_db = min(g_db, g_cap)
        y = peak_round(x * 10 ** (g_db / 20))
        if clip_amt > 0:
            y = clip_stage(y, out_db=0.8 * clip_amt)
        y = limiter(low_limit(y, 10 ** (-1.0 / 20) * 0.78), ceiling_db=-1.0, hold=0.025)   # (held for a whole 40 Hz cycle:
        #                                                         the gain never wobbles inside one bass wave - 1.80)
        err = target - meas(y)
        if abs(err) < 0.1 or (err > 0 and g_db >= g_cap - 1e-6):
            break
        g_db += err
    # true peak: the peaks between the samples (4x oversampled) kept under -1 dBTP, so the file never clips when
    # it's converted to MP3 / AAC or played through a DAC that reconstructs the waveform
    ceil_ = 10 ** (-1.0 / 20)
    tp = float(np.max(np.abs(signal.resample_poly(y, 4, 1, axis=-1)))) if y.size else 0.0
    if tp > ceil_:                          # a last overshoot: limit just those peaks a little harder (turning the whole
        over_db = 20 * np.log10(tp / ceil_)    # song down for one peak used to land it under its loudness target)
        y = limiter(y, ceiling_db=-1.0 - over_db - 0.05)
        tp = float(np.max(np.abs(signal.resample_poly(y, 4, 1, axis=-1))))
        if tp > ceil_:
            y = y * (ceil_ / tp)
    return y
