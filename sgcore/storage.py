"""Keep the output folder from filling up.

- Previews (the short clips in songs/previews) are deleted after a day - press Preview again to hear one.
- Songs you keep (⭐ Keep in the result / Library) are never touched.
- Other full songs older than `days` are, depending on the mode:
    'midi'   trimmed to their MIDI + settings file (the default): the audio, stems, DAW and waveform projects go, but the
             settings rebuild the song note for note (Library -> Re-render)
    'delete' removed completely
    'off'    left alone
Only Studio Lab projects (anything with a <name>_settings.json) are ever touched - other files in the folder stay.
"""
import json
import os
import shutil
import time

MODES = ('midi', 'delete', 'off')
DEFAULT = dict(mode='midi', days=7)
PREVIEW_DAYS = 1.0
# what a trimmed song keeps
KEEP_WHEN_TRIMMED = ('_settings.json', '.mid')
PROJECT_PARTS = ('_settings.json', '_PLUGIN_GUIDE.txt', '_samplepack', '_waveform', '_DAW', '_parts', '_stems',
                 '.mp3', '.wav', '.mid', '.mmp', '.zip', '.flac')


def policy(settings):
    p = dict(DEFAULT)
    p.update({k: v for k, v in (settings.get('storage') or {}).items() if k in DEFAULT})
    if p['mode'] not in MODES:
        p['mode'] = 'midi'
    try:
        p['days'] = max(1, min(365, int(p['days'])))
    except Exception:
        p['days'] = DEFAULT['days']
    return p


def _size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def _remove(path):
    n = _size(path)
    try:
        shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        return n
    except OSError:
        return 0


def settings_path(out_dir, base):
    return os.path.join(out_dir, base + '_settings.json')


def is_kept(out_dir, base):
    try:
        with open(settings_path(out_dir, base)) as f:
            return bool(json.load(f).get('kept'))
    except Exception:
        return False


def set_kept(out_dir, base, kept=True):
    p = settings_path(out_dir, base)
    with open(p) as f:
        s = json.load(f)
    s['kept'] = bool(kept)
    with open(p, 'w') as f:
        json.dump(s, f, indent=1)
    return s['kept']


def is_trimmed(out_dir, base):
    return not any(os.path.exists(os.path.join(out_dir, base + ext)) for ext in ('.mp3', '.wav', '.flac'))


def project_files(out_dir, base):
    return [os.path.join(out_dir, f) for f in os.listdir(out_dir)
            if f.startswith(base) and any(f == base + suf for suf in PROJECT_PARTS)]


def usage(out_dir):
    """Space used: previews, kept songs, other songs (MB)."""
    prev = _size(os.path.join(out_dir, 'previews')) if os.path.isdir(os.path.join(out_dir, 'previews')) else 0
    kept = other = 0
    n_kept = n_other = 0
    for f in os.listdir(out_dir):
        if f.endswith('_settings.json'):
            base = f[:-len('_settings.json')]
            sz = sum(_size(p) for p in project_files(out_dir, base))
            if is_kept(out_dir, base):
                kept += sz
                n_kept += 1
            else:
                other += sz
                n_other += 1
    mb = lambda b: round(b / 1e6, 1)
    return dict(previews_mb=mb(prev), kept_mb=mb(kept), other_mb=mb(other), kept=n_kept, other=n_other)


def clean(out_dir, pol, now=None, log=None):
    """Apply the policy. Returns dict(freed_mb, previews, trimmed, deleted)."""
    now = now or time.time()
    freed = 0
    n_prev = n_trim = n_del = 0
    pdir = os.path.join(out_dir, 'previews')
    if os.path.isdir(pdir):
        for f in os.listdir(pdir):
            p = os.path.join(pdir, f)
            try:
                if now - os.path.getmtime(p) > PREVIEW_DAYS * 86400:
                    freed += _remove(p)
                    n_prev += 1
            except OSError:
                pass
    if pol['mode'] != 'off':
        for f in list(os.listdir(out_dir)):
            if not f.endswith('_settings.json'):
                continue
            base = f[:-len('_settings.json')]
            sp = settings_path(out_dir, base)
            try:
                age = now - os.path.getmtime(sp)
            except OSError:
                continue
            if age < pol['days'] * 86400 or is_kept(out_dir, base):
                continue
            files = project_files(out_dir, base)
            if pol['mode'] == 'delete':
                for p in files:
                    freed += _remove(p)
                n_del += 1
            else:
                gone = [p for p in files if not any(p == os.path.join(out_dir, base + k) for k in KEEP_WHEN_TRIMMED)]
                if gone:
                    for p in gone:
                        freed += _remove(p)
                    n_trim += 1
    res = dict(freed_mb=round(freed / 1e6, 1), previews=n_prev, trimmed=n_trim, deleted=n_del)
    if log and (n_prev or n_trim or n_del):
        log(f"Cleaned the output folder: {n_prev} old previews, {n_trim} songs trimmed to MIDI, {n_del} deleted - "
            f"{res['freed_mb']} MB freed")
    return res
