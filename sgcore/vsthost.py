"""Experimental: use your own VST3 / Audio Unit instruments to render parts (via Spotify's pedalboard library).
Every plugin call runs in a separate process (sgcore.vst_worker) so a crashing plugin can't take the app down."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

import numpy as np

from . import updater

ROOT = updater.ROOT
PLUGIN_DIR = os.path.join(ROOT, 'plugins')          # drop .vst3 / .component files here
SOUNDS = os.path.join(ROOT, 'vst_sounds')           # saved plugin sounds (presets)


def available():
    try:
        import pedalboard  # noqa: F401
        return True
    except Exception:
        return False


def install(log=print):
    """pip-install pedalboard for the current Python (needs internet)."""
    cmd = [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', 'pedalboard']
    log('Installing VST support: ' + ' '.join(cmd))
    p = subprocess.run(cmd, capture_output=True, text=True)
    log((p.stdout or '')[-2000:])
    if p.returncode != 0:
        log((p.stderr or '')[-2000:])
    return p.returncode == 0


def _search_dirs():
    from .plugins import plugin_dirs
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    return [PLUGIN_DIR] + list(plugin_dirs())


def find_plugins():
    """VST3 bundles/files (all OS) and Audio Units (macOS) on this computer."""
    out, seen = [], set()
    for d in _search_dirs():
        if not os.path.isdir(d):
            continue
        for root, dirs, files in os.walk(d):
            for name in list(dirs) + files:
                low = name.lower()
                fmt = 'vst3' if low.endswith('.vst3') else ('au' if low.endswith('.component') and sys.platform == 'darwin' else None)
                if not fmt:
                    continue
                path = os.path.join(root, name)
                key = os.path.realpath(path)
                if key in seen:
                    continue
                seen.add(key)
                out.append(dict(name=os.path.splitext(name)[0], path=path, format=fmt,
                                folder='plugins folder' if path.startswith(PLUGIN_DIR) else os.path.dirname(path)))
            dirs[:] = [x for x in dirs if not x.lower().endswith(('.vst3', '.component'))]
            if root[len(d):].count(os.sep) >= 3:
                dirs[:] = []
    return sorted(out, key=lambda p: p['name'].lower())


def _run(job, timeout):
    d = tempfile.mkdtemp(prefix='sl_vst_')
    path = os.path.join(d, 'job.json')
    with open(path, 'w') as f:
        json.dump(job, f)
    env = dict(os.environ)
    env['PYTHONPATH'] = ROOT + os.pathsep + env.get('PYTHONPATH', '')
    try:
        subprocess.run([sys.executable, '-m', 'sgcore.vst_worker', path], cwd=ROOT, env=env, timeout=timeout,
                       capture_output=True)
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'the plugin took too long and was stopped'}, d
    try:
        with open(path + '.result') as f:
            return json.load(f), d
    except Exception:
        return {'ok': False, 'error': 'the plugin crashed while loading or playing'}, d


def probe(path, list_params=False):
    res, d = _run(dict(mode='probe', path=path, list_params=list_params), timeout=60)
    shutil.rmtree(d, ignore_errors=True)
    return res


# ----------------------------------------------------------------------------- saved sounds
def _safe(name):
    return re.sub(r'[^A-Za-z0-9 ._-]', '', name).strip()[:60] or 'sound'


def list_sounds():
    os.makedirs(SOUNDS, exist_ok=True)
    out = []
    for f in sorted(os.listdir(SOUNDS)):
        if f.endswith('.json'):
            try:
                with open(os.path.join(SOUNDS, f)) as fh:
                    d = json.load(fh)
                out.append(dict(id=f[:-5], name=d.get('name', f[:-5]), plugin=d.get('plugin_label', ''), path=d.get('path', ''),
                                ok=os.path.exists(d.get('path', '')), auto=bool(d.get('auto')), patch=d.get('patch')))
            except Exception:
                pass
    return out


def get_sound(sid):
    p = os.path.join(SOUNDS, _safe(sid) + '.json')
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def delete_sound(sid):
    p = os.path.join(SOUNDS, _safe(sid) + '.json')
    if os.path.exists(p):
        os.remove(p)


def create_sound(path, name, existing=None, timeout=3600):
    """Open the plugin's own window; when you close it, the chosen sound is saved."""
    if not any(os.path.realpath(path) == os.path.realpath(p['path']) for p in find_plugins()):
        return {'ok': False, 'error': 'unknown plugin'}
    prev = get_sound(existing) if existing else None
    res, d = _run(dict(mode='editor', path=path, state=(prev or {}).get('state')), timeout=timeout)   # recipe applied first
    if prev and prev.get('auto'):
        existing = None                        # editing a genre-rig sound saves your own copy; the rig sound stays
    shutil.rmtree(d, ignore_errors=True)
    if not res.get('ok'):
        return res
    sid = existing or (_safe(name).replace(' ', '_') + '_' + uuid.uuid4().hex[:6])
    os.makedirs(SOUNDS, exist_ok=True)
    with open(os.path.join(SOUNDS, _safe(sid) + '.json'), 'w') as f:
        json.dump(dict(name=name, path=path, plugin_label=os.path.splitext(os.path.basename(path))[0],
                       state=res.get('state'), created=int(time.time())), f)
    return {'ok': True, 'id': sid}


def render(sid, events, duration, sr=44100, timeout=900):
    """events: [(start_s, dur_s, midi_note, velocity_0_127)] -> (2, n) float32 or raises RuntimeError."""
    snd = get_sound(sid)
    if not snd:
        raise RuntimeError(f'VST sound "{sid}" not found')
    if not available():
        raise RuntimeError('VST support is not installed')
    d = tempfile.mkdtemp(prefix='sl_vst_')
    out = os.path.join(d, 'audio.npy')
    try:
        res, _ = _run(dict(mode='render', path=snd['path'], state=snd.get('state'), events=events,
                           duration=duration, sr=sr, out=out), timeout=timeout)
        if not res.get('ok'):
            raise RuntimeError(res.get('error', 'plugin failed'))
        audio = np.load(out)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if audio.shape[0] > 2:
        audio = audio[:2]
    return audio


def preview(sid):
    """Short test phrase so you can hear a saved sound."""
    ev = [(i * 0.25, 0.22, n, 100) for i, n in enumerate([48, 55, 60, 64, 67, 72, 67, 64])] + [(2.0, 1.5, 60, 100), (2.0, 1.5, 64, 90), (2.0, 1.5, 67, 90)]
    return render(sid, ev, 4.0)
