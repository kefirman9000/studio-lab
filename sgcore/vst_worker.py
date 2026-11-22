"""Runs in its own process so a misbehaving plugin can never crash Studio Lab.
   python -m sgcore.vst_worker <job.json>
   job: {"mode": "probe"|"editor"|"render", "path": ..., "plugin_name": ..., "state": {...}, "events": [...],
         "duration": s, "out": result-path}"""
import base64
import time
import json
import re
import sys


def _n(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def _find_param(plugin, key):
    """Plugin parameter for a recipe key like "Filter Cutoff" or "A Osc 1 Unison Voices|Osc 1 Unison Voices"."""
    params = getattr(plugin, 'parameters', {}) or {}
    for alt in key.split('|'):
        want = _n(alt)
        for attr, p in params.items():
            if _n(getattr(p, 'name', '')) == want or _n(attr) == want:
                return attr, p
        pre = [(a, p) for a, p in params.items() if _n(getattr(p, 'name', a)).startswith(want)]
        if len(pre) == 1:
            return pre[0]
    return None, None


def _set(plugin, attr, p, value):
    if isinstance(value, bool):
        value = 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        p.raw_value = max(0.0, min(1.0, float(value)))
        return True
    opts = [v for v in (getattr(p, 'valid_values', None) or []) if isinstance(v, str)]
    want = _n(value)
    hit = next((o for o in opts if _n(o) == want), None) or next((o for o in opts if _n(o).startswith(want)), None) \
        or next((o for o in opts if want in _n(o)), None)
    setattr(plugin, attr, hit if hit is not None else value)
    return True


def apply_recipe(plugin, recipe):
    """Set a genre patch: named parameters (0..1 knob positions or choice labels) and optionally a program.
    Raises if a required setting can't be applied, so the part falls back instead of playing the wrong sound."""
    applied, missing = [], []
    prog = recipe.get('program')
    if prog:
        attr, p = _find_param(plugin, 'Program|Programs|Preset')
        ok = False
        if p is not None:
            names, idx = prog[0], prog[1] if len(prog) > 1 else None
            opts = list(getattr(p, 'valid_values', None) or [])
            hit = next((o for o in opts if isinstance(o, str) and _n(o) == _n(names)), None)
            try:
                if hit is not None:
                    setattr(plugin, attr, hit)
                    ok = True
                elif idx is not None and opts and len(opts) > idx and not any(isinstance(o, str) for o in opts):
                    p.raw_value = idx / max(1, len(opts) - 1)
                    ok = True
            except Exception:
                ok = False
        if not ok:
            raise RuntimeError(f'could not select program "{prog[0]}"')
        applied.append('program')
    for key, value in (recipe.get('params') or {}).items():
        attr, p = _find_param(plugin, key)
        if p is None:
            missing.append(key)
            continue
        try:
            _set(plugin, attr, p, value)
            applied.append(key)
        except Exception:
            missing.append(key)
    req = [r for r in recipe.get('required', []) if not any(_n(r) in [_n(a) for a in m.split('|')] for m in applied)]
    if req:
        raise RuntimeError('this plugin version does not have ' + ', '.join(req))
    return applied, missing


def has_chords(events):
    """True if two or more notes ever sound at once (chords, pads, overlapping arps)."""
    ends = []
    for t0, dur, _n_, _v in sorted(events, key=lambda e: e[0]):
        ends = [e for e in ends if e > t0 + 1e-4]
        if ends:
            return True
        ends.append(t0 + max(0.01, dur))
    return False


def make_poly(plugin):
    """Put a synth in polyphonic mode with no glide, so a chord plays as a chord. Many presets (and some plugins'
    first program) are mono / legato with portamento: given a chord they keep only one note and slide into the next,
    which makes chords sound late, one note after another, and every song alike."""
    changed = []
    for attr, p in (getattr(plugin, 'parameters', {}) or {}).items():
        nm = _n(getattr(p, 'name', '') or attr)
        if 'unison' in nm:                            # unison voices thicken one note - not polyphony
            continue
        choices = [v for v in (getattr(p, 'valid_values', None) or []) if isinstance(v, str)]
        try:
            if any(k in nm for k in ('playmode', 'polymode', 'voicemode', 'keymode', 'monopoly', 'voicing')) and choices:
                hit = next((c for c in choices if 'poly' in _n(c)), None)
                if hit is not None and getattr(plugin, attr, None) != hit:
                    setattr(plugin, attr, hit)
                    changed.append(attr)
            elif nm in ('mono', 'monomode', 'legato', 'monolegato', 'legatomode') and not choices:
                p.raw_value = 0.0
                changed.append(attr)
            elif nm.endswith(('voices', 'polyphony', 'voicecount', 'maxvoices')):
                nums = [c for c in choices if re.fullmatch(r'\d+', c.strip())]
                if nums:
                    setattr(plugin, attr, max(nums, key=lambda c: int(c)))
                elif choices:
                    continue
                else:
                    p.raw_value = 1.0
                changed.append(attr)
            elif any(k in nm for k in ('portamento', 'glide')) and 'mode' in nm and choices:
                hit = next((c for c in choices if _n(c) in ('off', 'none', 'disabled')), None)
                if hit is not None:
                    setattr(plugin, attr, hit)
                    changed.append(attr)
            elif any(k in nm for k in ('portamento', 'glide')) and not choices:
                p.raw_value = 0.0
                changed.append(attr)
        except Exception:
            pass
    return changed


def _load(job):
    from pedalboard import load_plugin
    kw = {}
    if job.get('plugin_name'):
        kw['plugin_name'] = job['plugin_name']
    plugin = load_plugin(job['path'], **kw)
    st = job.get('state') or {}
    if st.get('raw') and hasattr(plugin, 'raw_state'):
        try:
            plugin.raw_state = base64.b64decode(st['raw'])
        except Exception:
            pass
    for k, v in (st.get('params') or {}).items():
        try:
            setattr(plugin, k, v)
        except Exception:
            pass
    if st.get('preset') and hasattr(plugin, 'load_preset'):
        plugin.load_preset(st['preset'])                  # a .vstpreset file shipped with / saved for the plugin
    if st.get('recipe'):
        job['_applied'] = apply_recipe(plugin, st['recipe'])
    return plugin


def _state(plugin):
    st = {'params': {}}
    if hasattr(plugin, 'raw_state'):
        try:
            st['raw'] = base64.b64encode(bytes(plugin.raw_state)).decode()
        except Exception:
            pass
    for k in getattr(plugin, 'parameters', {}):
        try:
            v = getattr(plugin, k)
            if isinstance(v, (int, float, str, bool)):
                st['params'][k] = v
        except Exception:
            pass
    return st


def _scan(plugin, path, job):
    """Orchestra detection: the plugin window stays open while you click through instruments in the plugin's own
    browser. (2.13.4) This process only copies the plugin's state now and then - nothing heavy, so the plugin's window
    stays smooth: a state that has changed and then stayed the same for one more read is written to <job>.cap<n>.bin,
    and Studio Lab (the app, in its own process) works out which instrument it is. Reads slow down by themselves when
    the plugin is slow to hand its state over. Progress goes to <job>.live."""
    import hashlib
    import threading
    last = {'h': None, 'seen': 0, 'saved': set(), 'n': 0, 'reads': 0, 'ms': 0.0, 'busy_since': None, 'blocked': False}
    stop = threading.Event()

    def write_live():
        try:
            with open(path + '.live', 'w') as f:
                json.dump(dict(caps=last['n'], reads=last['reads'], blocked=last['blocked'], ms=round(last['ms'])), f)
        except Exception:
            pass

    def snap(final=False):
        last['busy_since'] = t0 = time.time()
        try:
            raw = bytes(plugin.raw_state)
        except Exception:
            last['busy_since'] = None
            return
        last['busy_since'] = None
        last['ms'] = (time.time() - t0) * 1000
        last['reads'] += 1
        h = hashlib.sha1(raw).hexdigest()
        if h == last['h']:
            last['seen'] += 1
        else:
            last.update(h=h, seen=0)
        if (last['seen'] >= 1 or final) and h not in last['saved']:     # changed, then stayed loaded for a moment
            last['saved'].add(h)
            with open(path + '.cap%d.bin' % last['n'], 'wb') as f:
                f.write(raw)
            last['n'] += 1
        write_live()

    def poll():
        wait = float(job.get('every', 2.0))
        while not stop.wait(wait):
            snap()
            wait = min(10.0, max(2.0, last['ms'] / 1000 * 8))         # a slow plugin is asked less often

    def watchdog():                                   # some plugins can't be read while their window is open
        while not stop.wait(1.0):
            b = last['busy_since']
            if b and time.time() - b > 6 and not last['blocked']:
                last['blocked'] = True
                write_live()
    write_live()
    threading.Thread(target=watchdog, daemon=True).start()
    th = threading.Thread(target=poll, daemon=True)
    th.start()
    try:
        plugin.show_editor(stop)                      # pedalboard: returns when the window closes (or stop is set)
    except TypeError:
        plugin.show_editor()
    stop.set()
    th.join(timeout=15)
    snap(final=True)                                  # what's loaded at the moment you closed the window
    return {'ok': True, 'caps': last['n'], 'reads': last['reads'], 'blocked': last['blocked']}


def main(path):
    with open(path) as f:
        job = json.load(f)
    out = {'ok': False}
    try:
        if job['mode'] == 'process':                     # effect chain on already-rendered audio
            import numpy as np
            from pedalboard import Pedalboard, load_plugin
            audio = np.load(job['in']).astype(np.float32)
            plugs = [load_plugin(p) for p in job['paths']]
            for pl, prm in zip(plugs, job.get('params') or []):
                for k, v in (prm or {}).items():          # e.g. {'decay_s': 2.4, 'dry_level': 0}
                    try:
                        setattr(pl, k, v)
                    except Exception:
                        pass
            board = Pedalboard(plugs)
            y = board(audio, float(job.get('sr', 44100)))
            if y.ndim == 1:
                y = np.vstack([y, y])
            if not np.isfinite(y).all():
                raise RuntimeError('effect produced invalid audio')
            np.save(job['out'], y.astype(np.float32))
            out = {'ok': True}
            with open(path + '.result', 'w') as f:
                json.dump(out, f)
            return
        plugin = _load(job)
        mode = job['mode']
        if mode == 'probe':
            out = {'ok': True, 'name': getattr(plugin, 'name', ''), 'is_instrument': bool(getattr(plugin, 'is_instrument', False))}
            if job.get('list_params'):
                out['params'] = [dict(attr=a, name=getattr(p, 'name', a), value=getattr(p, 'raw_value', None),
                                      choices=[v for v in (getattr(p, 'valid_values', None) or []) if isinstance(v, str)][:40])
                                 for a, p in (getattr(plugin, 'parameters', {}) or {}).items() if not a.startswith('midi_ch')]
        elif mode == 'editor':
            plugin.show_editor()                      # blocks until the plugin window is closed
            out = {'ok': True, 'state': _state(plugin)}
        elif mode == 'scan':
            out = _scan(plugin, path, job)
        elif mode == 'render':
            import numpy as np
            sr = int(job.get('sr', 44100))
            if job.get('poly', True) and has_chords(job['events']):
                out_poly = make_poly(plugin)
            else:
                out_poly = []
            msgs = []
            for (t0, dur, note, vel) in job['events']:
                n = max(0, min(127, int(note)))
                v = max(1, min(127, int(vel)))
                msgs.append((bytes([0x90, n, v]), float(t0)))
                msgs.append((bytes([0x80, n, 0]), float(t0 + max(0.01, dur))))
            for (t0, cc, val) in job.get('ccs') or []:        # mod wheel / expression curves (orchestra dynamics)
                msgs.append((bytes([0xB0, max(0, min(119, int(cc))), max(0, min(127, int(val)))]), float(t0)))
            msgs.sort(key=lambda m: (m[1], m[0][0] == 0x90))
            try:
                audio = plugin(msgs, duration=float(job['duration']), sample_rate=sr, num_channels=2, buffer_size=1024, reset=True)
            except ValueError as e:                    # mono instruments (many synths, e.g. 303 clones) only render 1 channel
                if 'channel' not in str(e):
                    raise
                audio = plugin(msgs, duration=float(job['duration']), sample_rate=sr, num_channels=1, buffer_size=1024, reset=True)
            audio = np.asarray(audio, dtype=np.float32)
            if audio.ndim == 1:
                audio = np.vstack([audio, audio])
            if not np.isfinite(audio).all():
                raise RuntimeError('plugin produced invalid audio')
            np.save(job['out'], audio)
            out = {'ok': True, 'shape': list(audio.shape), 'peak': float(np.max(np.abs(audio)) if audio.size else 0),
                   'poly': out_poly}
            if job.get('_applied'):
                out['applied'], out['missing'] = job['_applied']
    except Exception as e:  # report, never crash the app
        out = {'ok': False, 'error': f'{type(e).__name__}: {e}'}
    with open(path + '.result', 'w') as f:
        json.dump(out, f)


if __name__ == '__main__':
    main(sys.argv[1])
