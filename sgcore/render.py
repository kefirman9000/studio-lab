"""Rendering: events -> tracks -> mix (sidechain, sends, buses) -> master."""
import math
import os
import random
import time

import numpy as np
from scipy.ndimage import uniform_filter1d

from .dsp import (SR, hp, lp, eq, soft, compressor, limiter, lufs, active_rms_db, make_ir, reverb, pingpong,
                  make_spring_ir, dub_delay, svf_sweep,
                  sweep_region, write_wav_float)
from .instruments import INSTRUMENTS, DRUMS, fx_riser, fx_impact, fx_vinyl, fx_texture
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

    def t_of(self, beat, human=True, layer=None, swing=True):
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
            s = int((self.t_of(ev.beat, human=not tight, layer=tcfg['layer'], swing=is_drum or ev.dur < HELD)
                     + getattr(ev, 'strum', 0.0) * self.spb) * SR)
            sig = None
            if real_drums:
                sig = self._real_drum(tcfg.get('real') or tcfg['inst'], ev, i)
            if sig is None:
                sig = self._drum(tcfg['name'], tcfg['inst']) if is_drum else self._note(tcfg, ev, p)
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
            if tcfg['rev']:
                rev_send += buf * np.float32(tcfg['rev'] * opts.reverb)
            if tcfg['dly']:
                dly_send += buf * np.float32(tcfg['dly'] * opts.delay)
            if dub_send is not None and tcfg.get('throw'):
                dub_send += buf * throw[None, :] * np.float32(tcfg['throw'] * max(0.3, opts.delay))
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
            ir = make_spring_ir(st['reverb']) if st.get('spring') else make_ir(st['reverb'])
            rv = eq(reverb(rev_send.astype(np.float64), ir), 'lowshelf', 300, 0.7, -4.0)
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
        return mix


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
    if cfg.get('vintage_lp'):        # a 60s tape / tube top end: rolls off above this (Hz) - dark, warm, bass-forward
        x = lp(x, float(cfg['vintage_lp']))
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
    # never let the limiter squash the drum hits: at most `max_gr` dB of gain reduction on the loud peaks (99.9th
    # percentile). A song that can't reach its loudness target without that ends up a little quieter, not distorted.
    a = np.max(np.abs(x), axis=0)
    p999 = float(np.percentile(a, 99.9)) + 1e-9
    max_gr = float(cfg.get('max_gr', 3.0))
    g_cap = max_gr + 20 * np.log10(10 ** (-1.0 / 20) / p999)
    y = x
    for _ in range(8):
        g_db = min(g_db, g_cap)
        y = limiter(peak_round(x * 10 ** (g_db / 20)), ceiling_db=-1.0)
        err = target - lufs(y)
        if abs(err) < 0.1 or (err > 0 and g_db >= g_cap - 1e-6):
            break
        g_db += err
    return y
