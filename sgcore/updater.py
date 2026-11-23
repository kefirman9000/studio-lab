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


def channel():
    """(2.17) 'stable' (default): only published releases - each one passed the full test run first. 'latest': the
    newest code on the branch, straight away (for testing)."""
    return 'latest' if _config().get('channel') == 'latest' else 'stable'


def _latest_release(r):
    rel = json.loads(_get(f'https://api.github.com/repos/{r}/releases/latest').decode())
    ver = (rel.get('tag_name') or '').lstrip('v')
    zipa = next((a for a in rel.get('assets') or [] if a.get('name') == f'studio-lab-{ver}.zip'), None)
    sha = next((a for a in rel.get('assets') or [] if a.get('name') == f'studio-lab-{ver}.zip.sha256'), None)
    return dict(version=ver, notes=rel.get('body') or '', zip=zipa, sha=sha)


def check():
    """Returns dict(current, latest, available, notes, error)."""
    cur = local_version()
    r = repo()
    if not r or '/' not in r:
        return dict(current=cur, latest=None, available=False, error='No update source configured (update.json)')
    try:
        if channel() == 'stable':
            rel = _latest_release(r)
            if not rel['zip']:
                return dict(current=cur, latest=rel['version'], available=False, notes='', error='The latest release has no download yet - try again in a few minutes')
            return dict(current=cur, latest=rel['version'], available=_vt(rel['version']) > _vt(cur), notes=rel['notes'][:4000],
                        error=None, channel='stable')
        latest = _get(f'https://raw.githubusercontent.com/{r}/{branch()}/VERSION').decode().strip()
        notes = ''
        try:
            notes = _get(f'https://raw.githubusercontent.com/{r}/{branch()}/CHANGELOG.md').decode()[:4000]
        except Exception:
            pass
        return dict(current=cur, latest=latest, available=_vt(latest) > _vt(cur), notes=notes, error=None, channel='latest')
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
    _prev_version = local_version()
    if channel() == 'stable':                           # (2.17) the published, tested release - checksum-verified
        import hashlib
        rel = _latest_release(r)
        if not rel['zip']:
            return dict(ok=False, message='The latest release has no download yet - try again in a few minutes')
        data = _get(rel['zip']['browser_download_url'], timeout=180)
        want = None
        if rel['sha']:
            want = _get(rel['sha']['browser_download_url']).decode().split()[0].strip().lower()
        elif str(rel['zip'].get('digest', '')).startswith('sha256:'):
            want = rel['zip']['digest'][7:].lower()
        if not want:
            return dict(ok=False, message='The release has no published checksum - not installed')
        if hashlib.sha256(data).hexdigest() != want:
            return dict(ok=False, message='The download did not match its published checksum - not installed (try again)')
    else:
        data = _get(f'https://github.com/{r}/archive/refs/heads/{branch()}.zip', timeout=120)
    zf = zipfile.ZipFile(io.BytesIO(data))
    top = zf.namelist()[0].split('/')[0]
    backup = os.path.join(ROOT, '.backup')
    shutil.rmtree(backup, ignore_errors=True)
    os.makedirs(backup, exist_ok=True)
    root = os.path.realpath(ROOT)
    saved = []                                          # (2.2.3) only the files being replaced are backed up - files
    try:                                                # the installer added (StudioLab.exe, the icon ...) stay put
        for member in zf.namelist():
            rel = member[len(top) + 1:]
            if not rel or rel.split('/')[0] in KEEP:
                continue
            dst = os.path.realpath(os.path.join(ROOT, rel))
            if os.path.commonpath([dst, root]) != root:
                continue                    # never write outside the app folder
            if member.endswith('/'):
                os.makedirs(dst, exist_ok=True)
                continue
            if os.path.isfile(dst):
                bk = os.path.join(backup, rel)
                os.makedirs(os.path.dirname(bk), exist_ok=True)
                shutil.copy2(dst, bk)
                saved.append((bk, dst))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with zf.open(member) as src, open(dst, 'wb') as f:
                shutil.copyfileobj(src, f)
    except Exception as e:
        for bk, dst in saved:                     # roll back
            try:
                shutil.copy2(bk, dst)
            except Exception:
                pass
        return dict(ok=False, message=f'Update failed and was rolled back: {e}')
    try:                                                # (2.16) the next start checks the new version works - and
        import json                                     # goes back to this one by itself if it doesn't
        old = _prev_version
        with open(os.path.join(ROOT, '.update_pending.json'), 'w') as f:
            json.dump(dict(prev=old, new=local_version(), files=[[os.path.relpath(b, ROOT), os.path.relpath(d, ROOT)] for b, d in saved],
                           t=__import__('time').time()), f)
    except Exception:
        pass
    try:                                                # (2.2.6) compile now, so the next start doesn't have to
        import compileall
        compileall.compile_dir(os.path.join(ROOT, 'sgcore'), quiet=1,
                               invalidation_mode=__import__('py_compile').PycInvalidationMode.CHECKED_HASH)
    except Exception:
        pass
    return dict(ok=True, message='Updated - restarting', version=local_version())


def restart():
    if os.environ.get('STUDIOLAB_CHILD'):              # (2.2.3) the engine runs beside the window: the window relaunches
        try:                                            # the whole app (window + a new engine)
            os.write(1, b'STUDIOLAB_RESTART\n')
        finally:
            os._exit(0)
    os.execv(sys.executable, [sys.executable] + sys.argv)


PENDING = os.path.join(ROOT, '.update_pending.json')


def update_pending():
    try:
        import json
        with open(PENDING) as f:
            return json.load(f)
    except Exception:
        return None


def update_started_ok():
    """The new version came up: the safety net is no longer needed."""
    try:
        os.remove(PENDING)
    except OSError:
        pass


def roll_back():
    """(2.16) The freshly installed version would not start: put the previous version's files back."""
    p = update_pending()
    if not p:
        return None
    root = os.path.realpath(ROOT)
    n = 0
    for bk, dst in p.get('files') or []:
        b, d = os.path.realpath(os.path.join(ROOT, bk)), os.path.realpath(os.path.join(ROOT, dst))
        if os.path.commonpath([b, root]) != root or os.path.commonpath([d, root]) != root:
            continue
        try:
            shutil.copy2(b, d)
            n += 1
        except OSError:
            pass
    update_started_ok()
    try:
        import json
        with open(os.path.join(ROOT, '.update_rolled_back.json'), 'w') as f:
            json.dump(dict(bad=p.get('new'), back_to=p.get('prev')), f)
    except Exception:
        pass
    return dict(files=n, back_to=p.get('prev'), bad=p.get('new'))
