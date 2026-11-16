"""Runs in its own process so a misbehaving plugin can never crash Studio Lab.
   python -m sgcore.vst_worker <job.json>
   job: {"mode": "probe"|"editor"|"render", "path": ..., "plugin_name": ..., "state": {...}, "events": [...],
         "duration": s, "out": result-path}"""
import base64
import json
import sys


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


def main(path):
    with open(path) as f:
        job = json.load(f)
    out = {'ok': False}
    try:
        plugin = _load(job)
        mode = job['mode']
        if mode == 'probe':
            out = {'ok': True, 'name': getattr(plugin, 'name', ''), 'is_instrument': bool(getattr(plugin, 'is_instrument', False))}
        elif mode == 'editor':
            plugin.show_editor()                      # blocks until the plugin window is closed
            out = {'ok': True, 'state': _state(plugin)}
        elif mode == 'render':
            import numpy as np
            sr = int(job.get('sr', 44100))
            msgs = []
            for (t0, dur, note, vel) in job['events']:
                n = max(0, min(127, int(note)))
                v = max(1, min(127, int(vel)))
                msgs.append((bytes([0x90, n, v]), float(t0)))
                msgs.append((bytes([0x80, n, 0]), float(t0 + max(0.01, dur))))
            msgs.sort(key=lambda m: (m[1], m[0][0] == 0x90))
            audio = plugin(msgs, duration=float(job['duration']), sample_rate=sr, num_channels=2, buffer_size=1024, reset=True)
            audio = np.asarray(audio, dtype=np.float32)
            if audio.ndim == 1:
                audio = np.vstack([audio, audio])
            if not np.isfinite(audio).all():
                raise RuntimeError('plugin produced invalid audio')
            np.save(job['out'], audio)
            out = {'ok': True, 'shape': list(audio.shape), 'peak': float(np.max(np.abs(audio)) if audio.size else 0)}
    except Exception as e:  # report, never crash the app
        out = {'ok': False, 'error': f'{type(e).__name__}: {e}'}
    with open(path + '.result', 'w') as f:
        json.dump(out, f)


if __name__ == '__main__':
    main(sys.argv[1])
