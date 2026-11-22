"""Experimental: use your own VST3 / Audio Unit instruments to render parts (via Spotify's pedalboard library).
Every plugin call runs in a separate process (sgcore.vst_worker) so a crashing plugin can't take the app down."""
import hashlib
import json
import os
import re
import shutil
import subprocess
from .proc import NOWIN
import sys
import tempfile
import time
import uuid

import numpy as np

from . import updater

ROOT = updater.ROOT
PLUGIN_DIR = os.path.join(ROOT, 'plugins')          # drop .vst3 / .component files here
SOUNDS = os.path.join(ROOT, 'vst_sounds')           # saved plugin sounds (presets)


BROKEN = os.path.join(SOUNDS, '.broken_plugins.json')
LOAD_FAIL = ('Failed to load plugin', 'Unable to scan plugin', 'crashed while loading', 'unsupported plugin format')


def _sig(path):
    """Fingerprint of a plugin file/bundle: its files and sizes (changes when the plugin is reinstalled or repaired)."""
    try:
        if os.path.isfile(path):
            return str(os.path.getsize(path))
        items = []
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                items.append(f'{os.path.relpath(fp, path)}:{os.path.getsize(fp)}')
        return hashlib.sha1('\n'.join(sorted(items)).encode()).hexdigest()[:16]
    except OSError:
        return '0'


def bundle_ok(path):
    """False when the plugin's program file is missing (typically removed by antivirus software)."""
    if os.path.isfile(path):
        return os.path.getsize(path) > 10_000
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp) and os.path.getsize(fp) > 10_000:
                return True
    return False


def broken():
    """Plugins that failed to load, {path: reason}. An entry is forgotten when the plugin file changes (reinstalled)."""
    try:
        with open(BROKEN) as f:
            d = json.load(f)
    except Exception:
        return {}
    return {p: v['why'] for p, v in d.items() if v.get('sig') == _sig(p)}


def diagnose(path, err=''):
    """Plain-language reason a plugin won't load."""
    import platform
    import struct
    if not bundle_ok(path):
        return 'its program file is missing - antivirus software may have removed it. Reinstall it, or remove it'
    if struct.calcsize('P') * 8 == 32:
        return 'your Python is 32-bit, which cannot load 64-bit plugins - install 64-bit Python from python.org'
    if sys.platform.startswith('win') and platform.machine().lower() in ('arm64', 'aarch64'):
        return 'this is an ARM PC - the plugin may only exist for Intel/AMD (x64) processors'
    return 'the plugin is there but could not be loaded (' + str(err).split('Errors were:')[-1].strip()[:160] + ')'


def mark_broken(path, why):
    try:
        with open(BROKEN) as f:
            d = json.load(f)
    except Exception:
        d = {}
    why = diagnose(path, why)
    d[path] = dict(sig=_sig(path), why=str(why)[:300], t=int(time.time()))
    os.makedirs(SOUNDS, exist_ok=True)
    with open(BROKEN, 'w') as f:
        json.dump(d, f)


PROBES = os.path.join(SOUNDS, '.plugin_kinds.json')


def _probes():
    try:
        with open(PROBES) as f:
            return json.load(f)
    except Exception:
        return {}


def instrument_names():
    """Names of installed plugins already checked to be instruments (effects are left out of the Sound menus)."""
    pr = _probes()
    return sorted({p['name'] for p in find_plugins() if pr.get(p['path'], {}).get('inst')
                   and pr[p['path']].get('sig') == _sig(p['path']) and p['path'] not in broken()})


PROBE_STATUS = {'running': False, 'done': 0, 'total': 0, 'current': ''}


def effect_names():
    """Installed plugins checked to be effects (reverbs, delays, EQs ...), for the per-part FX menus."""
    pr = _probes()
    bad = broken()
    return sorted({p['name'] for p in find_plugins() if pr.get(p['path'], {}).get('ok') and not pr[p['path']].get('inst')
                   and pr[p['path']].get('sig') == _sig(p['path']) and p['path'] not in bad})


def path_of(name):
    bad = broken()
    hits = [p['path'] for p in find_plugins() if p['name'] == name and p['path'] not in bad]
    hits.sort(key=lambda x: (not x.startswith(PLUGIN_DIR), len(x)))
    return hits[0] if hits else None


def process(names, audio, sr=44100, timeout=600, params=None):
    """Run rendered audio (2, n) through effect plugins, in their own process. Raises RuntimeError on failure.
    params: one {parameter: value} dict per plugin (optional)."""
    paths = [path_of(n) for n in names]
    if not all(paths):
        raise RuntimeError('effect plugin not found: ' + ', '.join(n for n, p in zip(names, paths) if not p))
    d = tempfile.mkdtemp(prefix='sl_fx_')
    try:
        np.save(os.path.join(d, 'in.npy'), audio.astype(np.float32))
        res, _ = _run(dict(mode='process', paths=paths, sr=sr, params=params or [], **{'in': os.path.join(d, 'in.npy')},
                           out=os.path.join(d, 'out.npy')), timeout=timeout)
        if not res.get('ok'):
            err = res.get('error', 'effect failed')
            for p in paths:
                if any(k in err for k in LOAD_FAIL) and os.path.basename(p) in err:
                    mark_broken(p, err)
            raise RuntimeError(err)
        y = np.load(os.path.join(d, 'out.npy'))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return y[:2]


# ----------------------------------------------------------------------------- .vstpreset files
def preset_dirs():
    home = os.path.expanduser('~')
    if sys.platform.startswith('win'):
        return [os.path.join(home, 'Documents', 'VST3 Presets'),
                os.path.join(os.environ.get('PROGRAMDATA', r'C:\ProgramData'), 'VST3 Presets')]
    if sys.platform == 'darwin':
        return [os.path.join(home, 'Library', 'Audio', 'Presets'), '/Library/Audio/Presets']
    return [os.path.join(home, '.vst3', 'presets'), '/usr/share/vst3/presets', '/usr/local/share/vst3/presets']


def _key(name):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\(?(64|32)[ _-]*bit\)?', '', name.lower()))


def presets(limit_per_plugin=60):
    """{preset_id: dict(plugin, path, preset, name)} for .vstpreset files of installed plugins (folder = plugin name)."""
    installed = {}
    for p in find_plugins():
        installed.setdefault(_key(p['name']), p)
    out = {}
    for base in preset_dirs():
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            fs = sorted(f for f in files if f.lower().endswith('.vstpreset'))[:limit_per_plugin]
            if not fs:
                continue
            owner = next((installed[_key(seg)] for seg in reversed(os.path.relpath(root, base).split(os.sep)) if _key(seg) in installed), None)
            if not owner:
                continue
            for f in fs:
                fp = os.path.join(root, f)
                pid = hashlib.sha1(fp.encode()).hexdigest()[:12]
                out[pid] = dict(plugin=owner['name'], path=owner['path'], preset=fp, name=os.path.splitext(f)[0])
    return out


def ensure_preset_sound(pid):
    pr = presets().get(pid)
    if not pr:
        return None
    sid = 'auto_preset_' + pid
    os.makedirs(SOUNDS, exist_ok=True)
    with open(os.path.join(SOUNDS, sid + '.json'), 'w') as f:
        json.dump(dict(name=f"{pr['plugin']} · {pr['name']}", path=pr['path'], plugin_label=pr['plugin'], auto=True,
                       state={'preset': pr['preset']}), f)
    return sid


def probe_all(log=None, limit=200):
    """Check each installed plugin once (in its own process): instrument or effect? Cached by plugin fingerprint."""
    if not available() or PROBE_STATUS['running']:
        return 0
    pr = _probes()
    n = 0
    todo = [p for p in find_plugins()[:limit] if pr.get(p['path'], {}).get('sig') != _sig(p['path'])]
    PROBE_STATUS.update(running=bool(todo), done=0, total=len(todo), current='')
    for p in todo:
        PROBE_STATUS.update(current=p['name'])
        sig = _sig(p['path'])
        r = probe(p['path'])
        pr[p['path']] = dict(sig=sig, inst=bool(r.get('ok') and r.get('is_instrument')), ok=bool(r.get('ok')))
        if not r.get('ok') and any(k in str(r.get('error')) for k in LOAD_FAIL):
            mark_broken(p['path'], r.get('error'))
        n += 1
        os.makedirs(SOUNDS, exist_ok=True)
        with open(PROBES, 'w') as f:
            json.dump(pr, f)
        PROBE_STATUS['done'] = n
        if log:
            log(f"   checked {p['name']}: {'instrument' if pr[p['path']]['inst'] else 'effect / not loadable'}")
    PROBE_STATUS.update(running=False, current='')
    return n


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
    p = subprocess.run(cmd, capture_output=True, text=True, **NOWIN)
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
                       capture_output=True, **NOWIN)
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


def _save_sound(name, path, state, sid=None, extra=None):
    sid = sid or (_safe(name).replace(' ', '_') + '_' + uuid.uuid4().hex[:6])
    os.makedirs(SOUNDS, exist_ok=True)
    with open(os.path.join(SOUNDS, _safe(sid) + '.json'), 'w') as f:
        json.dump(dict(name=name, path=path, plugin_label=os.path.splitext(os.path.basename(path))[0], state=state,
                       created=int(time.time()), **(extra or {})), f)
    return sid


def rename_sound(sid, name):
    snd = get_sound(sid)
    if not snd:
        return {'ok': False, 'error': 'sound not found'}
    snd['name'] = str(name)[:60]
    with open(os.path.join(SOUNDS, _safe(sid) + '.json'), 'w') as f:
        json.dump(snd, f)
    return {'ok': True}


def scan_orchestra(path, prefix='BBC', log=print, timeout=3 * 3600):
    """Detect an orchestra plugin's instruments: open its window once, click through the instruments you want, close
    it. Each one is saved as a sound named after what the plugin loaded ("BBC celli spiccato (Celli · Spiccato)"), so
    the matching parts of every genre use it. A capture with the same instrument + articulation as an earlier scan
    replaces it instead of piling up duplicates."""
    if not any(os.path.realpath(path) == os.path.realpath(p['path']) for p in find_plugins()):
        return {'ok': False, 'error': 'unknown plugin'}
    from . import orchscan
    d = tempfile.mkdtemp(prefix='sl_vst_')
    jp = os.path.join(d, 'job.json')
    with open(jp, 'w') as f:
        json.dump(dict(mode='scan', path=path), f)
    env = dict(os.environ)
    env['PYTHONPATH'] = ROOT + os.pathsep + env.get('PYTHONPATH', '')
    proc = subprocess.Popen([sys.executable, '-m', 'sgcore.vst_worker', jp], cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **NOWIN)
    shown, t0, warned = [], time.time(), False
    log(f'{os.path.splitext(os.path.basename(path))[0]} is opening. In its own browser, load each instrument you want '
        '(and its articulation). Each one is picked up automatically - close the plugin window when you are done.')
    while proc.poll() is None:
        if time.time() - t0 > timeout:
            proc.kill()
            break
        try:
            with open(jp + '.live') as f:
                live = json.load(f)
        except Exception:
            live = {}
        if isinstance(live, list):
            live = dict(names=live)
        names = live.get('names') or []
        for n in names[len(shown):]:
            log('  ✓ found ' + n)
        shown = names if len(names) >= len(shown) else shown
        if live.get('blocked') and not warned:
            warned = True
            log('  ! this plugin does not let Studio Lab read it while its window is open - the instrument loaded when you '
                'close the window is still saved. To set up several sections, use "set up one section at a time" below '
                '(or run Detect again for each section).')
        time.sleep(0.5)
    try:
        with open(jp + '.result') as f:
            res = json.load(f)
    except Exception:
        res = {'ok': False, 'error': 'the plugin crashed while it was open'}
    shutil.rmtree(d, ignore_errors=True)
    if not res.get('ok'):
        return res
    existing = {(s.get('scan_key') or ''): s['id'] for s in list_sounds_full() if s.get('scan_key')}
    saved = []
    for i, c in enumerate(res.get('captures') or []):
        if c.get('instrument'):
            name = orchscan.sound_name(prefix, c)
            key = f"{os.path.basename(path)}|{c['instrument']}|{c.get('articulation') or ''}"
        else:
            name, key = f'{prefix} sound {i + 1} (rename me)', None
        sid = _save_sound(name, path, c.get('state'), sid=existing.get(key) if key else None,
                          extra=dict(scan_key=key, instrument=c.get('instrument'), articulation=c.get('articulation')))
        saved.append(dict(id=sid, name=name, named=bool(c.get('instrument'))))
    if not saved:
        log('Nothing was captured - load an instrument in the plugin and leave it loaded for a second or two.')
    elif not res.get('named'):
        log('The plugin did not say which instruments these are, so they were saved as "sound 1, 2 ..." - '
            'give each a name (e.g. "BBC celli spiccato") and matching parts will use it.')
        try:                                              # (2.13.3) keep what the state did contain, for a bug report
            with open(os.path.join(SOUNDS, '.last_scan.json'), 'w') as f:
                json.dump(dict(plugin=os.path.basename(path), reads=res.get('reads'), blocked=res.get('blocked'),
                               texts=res.get('texts')), f, indent=1)
        except Exception:
            pass
    return {'ok': True, 'sounds': saved, 'named': bool(res.get('named'))}


def list_sounds_full():
    out = []
    for s in list_sounds():
        d = get_sound(s['id']) or {}
        out.append(dict(s, scan_key=d.get('scan_key')))
    return out


def render(sid, events, duration, sr=44100, timeout=900, ccs=None):
    """events: [(start_s, dur_s, midi_note, velocity_0_127)], ccs: [(time_s, controller, value)] -> (2, n) float32
    or raises RuntimeError."""
    snd = get_sound(sid)
    if not snd:
        raise RuntimeError(f'VST sound "{sid}" not found')
    if not available():
        raise RuntimeError('VST support is not installed')
    bad = broken().get(snd['path'])
    if bad:
        raise RuntimeError(f"{snd.get('plugin_label') or 'plugin'} is skipped: {bad}")
    d = tempfile.mkdtemp(prefix='sl_vst_')
    out = os.path.join(d, 'audio.npy')
    try:
        res, _ = _run(dict(mode='render', path=snd['path'], state=snd.get('state'), events=events, ccs=ccs or [],
                           duration=duration, sr=sr, out=out), timeout=timeout)
        if not res.get('ok'):
            err = res.get('error', 'plugin failed')
            if any(k in err for k in LOAD_FAIL):
                mark_broken(snd['path'], err)          # don't pick it again until it's reinstalled
            raise RuntimeError(err)
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
