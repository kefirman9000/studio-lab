"""Rendering: events -> tracks -> mix (sidechain, sends, buses) -> master."""
import os
import random
import time

import numpy as np
from scipy.ndimage import uniform_filter1d

from . import dsp
from .dsp import (SR, hp, lp, eq, soft, compressor, limiter, lufs, active_rms_db, make_ir, reverb, pingpong,
                  sweep_region, write_wav_float)
from .instruments import INSTRUMENTS, DRUMS, fx_riser, fx_impact, fx_vinyl, fx_texture
from .compose import SECTION_ENERGY, GROOVES

ROLE_DB = {'kick': -13, 'snare': -17, 'top': -25, 'bass': -15, 'chords': -21, 'pad': -23, 'arp': -25, 'lead': -19, 'fx': -26}
CUT_KEYS = ('cut', 'bright')


class Renderer:
    def __init__(self, song, log=print):
        self.song = song
        self.st = song['st']
        self.opts = song['opts']
        self.spb = 60.0 / song['bpm']
        self.log = log
        self.cache = {}
        self.length = int((song['total_bars'] * 4 * self.spb + 4.0) * SR)
        self.hrng = random.Random(song['seed'] + 99)
        self.bright = 2 ** (float(self.opts.brightness) * 1.2)
        self.track_gains = {}

    def t_of(self, beat, human=True, layer=None):
        st = self.st
        b = beat
        g = GROOVES.get(st.get('groove')) if layer else None
        if g and layer in g:                            # genre timing feel (e.g. Dilla-late snares, pushed Afro hats)
            q16 = beat * 4
            if abs(q16 - round(q16)) < 1e-6:
                amt = min(1.5, max(0.0, float(getattr(self.opts, 'humanize', 1.0))))
                b += g[layer][int(round(q16)) % 16] * 0.25 * amt
        unit = st.get('swing_unit', 16)
        q = beat * (4 if unit == 16 else 2)
        if abs(q - round(q)) < 1e-6 and int(round(q)) % 2 == 1:
            b += (st['swing'] - 0.5) * (0.5 if unit == 16 else 1.0)
        t = b * self.spb
        if human and st.get('human'):
            # deterministic per position, so editing one section never shifts the feel of another
            t += random.Random(self.song['seed'] * 1000003 + int(round(beat * 960))).gauss(0, st['human'])
        return max(0.0, t)

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
        dur = round(ev.dur * self.spb, 3)
        if tcfg['inst'].startswith('sf:'):
            return self._sampled(tcfg, ev, dur, p)
        key = (tcfg['name'], ev.midi, dur, ev.glide, ev.mod)
        sig = self.cache.get(key)
        if sig is None:
            fn = INSTRUMENTS.get(tcfg['inst'])
            if fn is None and tcfg['inst'].startswith('user:'):
                from .usersounds import sampler
                fn = sampler(tcfg['inst'][5:])
            sig = fn(ev.midi, dur, p, ev.glide, ev.mod).astype(np.float32)
            self.cache[key] = sig
        return sig

    def _sampled(self, tcfg, ev, dur, p):
        """Real recorded instrument from the sound library; velocity changes the tone, not just the level."""
        from . import soundfont as sfm
        vel = int(min(127, max(24, round((30 + 92 * min(1.1, ev.vel)) / 12) * 12)))
        key = (tcfg['name'], ev.midi, dur, vel)
        sig = self.cache.get(key)
        if sig is None:
            name = tcfg['inst'][3:]
            try:
                sig = sfm.sampled_note(name, ev.midi, dur, vel)
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

    def _drum(self, name, inst=None):
        inst = inst or name
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
            sig = (sig / (np.max(np.abs(sig)) + 1e-9)).astype(np.float32)
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
        kick = self.st.get('kick_track', 'kick')
        for ev in evs:
            s = int((self.t_of(ev.beat, human=(tcfg['name'] != kick), layer=tcfg['layer']) + getattr(ev, 'strum', 0.0) * self.spb) * SR)
            sig = self._drum(tcfg['name'], tcfg['inst']) if is_drum else self._note(tcfg, ev, p)
            self._add(buf, sig * ev.vel, s)
        if tcfg.get('drive'):
            buf = (soft(buf * (1 + tcfg['drive'] * 3), 1.5) / (1 + tcfg['drive'])).astype(np.float32)
        return buf

    def _render_vst(self, tcfg, evs):
        """Play this part through one of your own VST3/AU instruments (falls back to the built-in sound on failure)."""
        from . import vsthost
        sid = tcfg['inst'][4:]
        events = [(self.t_of(e.beat, human=True, layer=tcfg['layer']) + getattr(e, 'strum', 0.0) * self.spb, max(0.02, e.dur * self.spb), int(e.midi), int(max(1, min(127, e.vel * 110))))
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

    def kick_times(self):
        kn = self.st.get('kick_track', 'kick')
        return sorted(self.t_of(e.beat, human=False) for e in self.song['events'] if e.track == kn)

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
        L = self.length
        by_track = {}
        for e in song['events']:
            by_track.setdefault(e.track, []).append(e)
        sc_depth = st['sc_depth']
        duck = self.sidechain_curve(st['sc_release']) if sc_depth > 0 else None
        mix = np.zeros((2, L), dtype=np.float32)
        drums = np.zeros((2, L), dtype=np.float32)
        rev_send = np.zeros((2, L), dtype=np.float32)
        dly_send = np.zeros((2, L), dtype=np.float32)
        b2s = lambda b: int(self.t_of(b, human=False) * SR)
        gaps = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'gap']
        lpsweeps = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'lpsweep']
        hpsweeps = [(b2s(b), b2s(b + d)) for k, b, d in song['fx'] if k == 'hpsweep']
        # ---- energy contour + fades
        env = np.ones(L)
        for sec in song['sections']:
            s0, s1 = b2s(sec['bar'] * 4), min(L, b2s((sec['bar'] + sec['bars']) * 4))
            e = SECTION_ENERGY.get(sec['name'], 0.9)
            e = 1 - (1 - e) * (0.5 + song['energy'])
            if sec['opts'].get('build'):
                env[s0:s1] = np.linspace(0.72, 0.95, s1 - s0)
            else:
                env[s0:s1] = e
        env = uniform_filter1d(env, int(0.25 * SR))
        for kind, b, d in song['fx']:
            if kind == 'fade':
                s0, s1 = b2s(b), min(L, b2s(b + d) + int(3.5 * SR))
                env[s0:s1] *= np.linspace(1, 0, s1 - s0) ** 1.6
                env[s1:] = 0
        env32 = env.astype(np.float32)
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
            cur = active_rms_db(buf)
            if cur > -110:
                g = 10 ** ((target - cur) / 20)
                buf *= np.float32(g)
                self.track_gains[name] = g
            if tcfg['pan']:
                th = (tcfg['pan'] * min(1.0, opts.width) + 1) * np.pi / 4
                buf[0] *= np.float32(np.cos(th) * np.sqrt(2))
                buf[1] *= np.float32(np.sin(th) * np.sqrt(2))
            if duck is not None and tcfg['sc']:
                buf *= (1 - duck * np.float32(min(1.0, sc_depth * tcfg['sc'])))[None, :]
            for s0, s1 in gaps:
                if tcfg['layer'] != 'fx':
                    buf[:, s0:s1] = 0
            buf *= env32[None, :]
            if tcfg['rev']:
                rev_send += buf * np.float32(tcfg['rev'] * opts.reverb)
            if tcfg['dly']:
                dly_send += buf * np.float32(tcfg['dly'] * opts.delay)
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
                elif kind == 'swell' and d > 0:               # reverse cymbal leading into the next section
                    c = self._drum('crash')[::-1]
                    n = min(len(c), int(d * self.spb * SR))
                    self._add(fxbuf, c[-n:] * np.linspace(0.2, 0.55, n, dtype=np.float32), s + int(d * self.spb * SR) - n)
        if np.any(fxbuf):
            cur = active_rms_db(fxbuf)
            fxbuf *= np.float32(10 ** ((ROLE_DB['fx'] + 3 - cur) / 20))
            fxbuf *= env32[None, :]
            rev_send += fxbuf * 0.3
            mix += fxbuf
            if stems_dir:
                path = os.path.join(stems_dir, '90_fx.wav')
                write_wav_float(path, fxbuf)
                stems.append(dict(name='fx', layer='fx', inst='fx', path=path))
        # ---- drum bus
        self.log('   drum bus: glue compression + saturation')
        drums = compressor(drums.astype(np.float64), thresh=-14, ratio=3, attack=0.004, release=0.09)
        drums = soft(drums * 1.2, 1.2) / 1.2
        if stems_dir and np.any(drums):
            path = os.path.join(stems_dir, '00_drum_bus.wav')
            write_wav_float(path, drums)
            stems.insert(0, dict(name='drum_bus', layer='drums', inst='drums', path=path, bus=True))
        mix = mix.astype(np.float64) + drums
        # ---- returns
        self.log('   reverb + delay returns')
        returns = np.zeros_like(mix)
        if np.any(rev_send):
            ir = make_ir(st['reverb'])
            rv = eq(reverb(rev_send.astype(np.float64), ir), 'lowshelf', 300, 0.7, -4.0)
            if duck is not None:
                rv *= (1 - duck * sc_depth * 0.7)[None, :]
            returns += rv * 0.55
        if np.any(dly_send):
            dl = hp(pingpong(dly_send.astype(np.float64), st['delay_beats'] * self.spb, fb=0.42), 250)
            returns += dl * 0.45
            if np.any(rev_send):
                returns += reverb(dl * 0.3, ir) * 0.3
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
        return mix


def tape_wobble(x, depth=1.0):
    """Tape wow & flutter. depth 1 = a gentle ~6 cent drift; 3 = the warped, seasick tape of hauntology. The whole mix
    moves together, so the parts stay in tune with each other - only the 'tape speed' drifts."""
    n = x.shape[1]
    t = np.arange(n) / SR
    d = 0.0025 * max(1.0, depth) + depth * (0.0012 * np.sin(2 * np.pi * 0.45 * t) + 0.0009 * np.sin(2 * np.pi * 0.13 * t + 1.3)) \
        + 0.00015 * np.sin(2 * np.pi * 6.3 * t)
    idx = np.arange(n) - d * SR
    return np.vstack([np.interp(idx, np.arange(n), x[c]) for c in range(2)])


def master(x, cfg, log=print):
    log('   mastering: EQ > glue comp > stereo image > saturation > limiter')
    x = hp(x, 28)
    l0 = lufs(x)
    x *= 10 ** ((-18 - l0) / 20)
    x = eq(x, 'lowshelf', 90, 0.7, cfg.get('low', 1.0))
    gentle = cfg.get('gentle')
    if not gentle:
        x = eq(x, 'peak', 320, 1.0, -1.5)
    x = eq(x, 'peak', 3000, 0.8, 0.5)
    x = eq(x, 'highshelf', 9000, 0.7, cfg.get('air', 1.5))
    if cfg.get('lofi'):
        x = lp(x, 9500)
        x = tape_wobble(x, cfg.get('wobble', 1.0))
        x = soft(x * 1.4, 1.3) / 1.4
    if gentle:     # acoustic / orchestral: keep the dynamics, no pumping glue
        x = compressor(x, thresh=-24, ratio=1.3, attack=0.05, release=0.4, win=0.03)
    else:
        x = compressor(x, thresh=-20, ratio=2.0, attack=0.025, release=0.2, win=0.02)
    mid = (x[0] + x[1]) / 2
    side = hp((x[0] - x[1]) / 2, 120, 2) * 1.15 * cfg.get('width', 1.0)
    x = np.vstack([mid + side, mid - side])
    drv = 1.05 + 2.0 * cfg.get('drive', 0.0)
    if not gentle or cfg.get('drive', 0) > 0:
        x = soft(x * 1.1, drv) / 1.1
    target = cfg.get('lufs', -10)
    g_db = target - lufs(x)
    y = x
    for _ in range(8):
        y = limiter(x * 10 ** (g_db / 20), ceiling_db=-1.0)
        err = target - lufs(y)
        if abs(err) < 0.1:
            break
        g_db += err
    return y
