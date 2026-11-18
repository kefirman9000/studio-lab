"""Self-updater: compares the local VERSION with the one on GitHub and swaps in the latest code."""
import io
import json
import os
import shutil
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, 'update.json')
KEEP = {'runtime', 'songs', 'presets', 'update.json', '.git', 'settings.json', '__pycache__', 'user_sounds', 'ratings.json', 'plugins', 'vst_sounds', 'sound_library', 'recent_instruments.json'}


def _config():
    try:
        with open(CONFIG) as f:
            return json.load(f)
    except Exception:
        return {}


def repo():
    return _config().get('repo', '')


def branch():
    return _config().get('branch', 'main')


def local_version():
    try:
        with open(os.path.join(ROOT, 'VERSION')) as f:
            return f.read().strip()
    except Exception:
        return '0.0.0'


def _vt(v):
    out = []
    for p in v.strip().lstrip('v').split('.'):
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    return tuple(out)


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': 'studio-lab-updater', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def check():
    """Returns dict(current, latest, available, notes, error)."""
    cur = local_version()
    r = repo()
    if not r or '/' not in r:
        return dict(current=cur, latest=None, available=False, error='No update source configured (update.json)')
    try:
        latest = _get(f'https://raw.githubusercontent.com/{r}/{branch()}/VERSION').decode().strip()
        notes = ''
        try:
            notes = _get(f'https://raw.githubusercontent.com/{r}/{branch()}/CHANGELOG.md').decode()[:4000]
        except Exception:
            pass
        return dict(current=cur, latest=latest, available=_vt(latest) > _vt(cur), notes=notes, error=None)
    except Exception as e:
        return dict(current=cur, latest=None, available=False, error=f'Could not reach GitHub: {e}')


def apply():
    """Download the latest code and replace the program files (your songs and presets are kept)."""
    r = repo()
    if os.path.isdir(os.path.join(ROOT, '.git')):
        # running from a git clone: a plain pull is safest
        import subprocess
        from .proc import NOWIN
        out = subprocess.run(['git', '-C', ROOT, 'pull', '--ff-only'], capture_output=True, text=True, **NOWIN)
        if out.returncode == 0:
            return dict(ok=True, message=out.stdout.strip() or 'Updated', version=local_version())
    if not r or '/' not in r or any(c in r for c in ' ?#\\'):
        return dict(ok=False, message='No valid update source configured')
    data = _get(f'https://github.com/{r}/archive/refs/heads/{branch()}.zip', timeout=120)
    zf = zipfile.ZipFile(io.BytesIO(data))
    top = zf.namelist()[0].split('/')[0]
    backup = os.path.join(ROOT, '.backup')
    shutil.rmtree(backup, ignore_errors=True)
    os.makedirs(backup, exist_ok=True)
    for name in os.listdir(ROOT):
        if name in KEEP or name.startswith('.'):
            continue
        shutil.move(os.path.join(ROOT, name), os.path.join(backup, name))
    try:
        for member in zf.namelist():
            rel = member[len(top) + 1:]
            if not rel or rel.split('/')[0] in KEEP:
                continue
            dst = os.path.realpath(os.path.join(ROOT, rel))
            if os.path.commonpath([dst, os.path.realpath(ROOT)]) != os.path.realpath(ROOT):
                continue                    # never write outside the app folder
            if member.endswith('/'):
                os.makedirs(dst, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with zf.open(member) as src, open(dst, 'wb') as f:
                    shutil.copyfileobj(src, f)
    except Exception as e:
        for name in os.listdir(backup):           # roll back
            dst = os.path.join(ROOT, name)
            if os.path.exists(dst):
                shutil.rmtree(dst, ignore_errors=True) if os.path.isdir(dst) else os.remove(dst)
            shutil.move(os.path.join(backup, name), dst)
        return dict(ok=False, message=f'Update failed and was rolled back: {e}')
    return dict(ok=True, message='Updated - restarting', version=local_version())


def restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)
