"""Malware checks for downloaded plugins, before anything is installed.

1. Microsoft Defender (Windows): a custom scan of the downloaded archive and the unpacked plugin files.
2. VirusTotal (optional, free API key): the exact file is checked by ~70 antivirus engines; Studio Lab installs only when
   none of them flags it. Unknown files are uploaded for analysis (they are public open-source releases).

No check can prove a file is free of malware; these are the strongest checks available to a desktop app.
"""
import json
import os
import subprocess
from .proc import NOWIN
import sys
import time
import urllib.error
import urllib.request

VT = 'https://www.virustotal.com/api/v3'
VT_MAX_UPLOAD = 650 * 1024 * 1024


# ----------------------------------------------------------------------------- Microsoft Defender
def defender_path():
    if not sys.platform.startswith('win'):
        return None
    cands = [os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Windows Defender', 'MpCmdRun.exe')]
    plat = os.path.join(os.environ.get('ProgramData', r'C:\ProgramData'), 'Microsoft', 'Windows Defender', 'Platform')
    if os.path.isdir(plat):
        for v in sorted(os.listdir(plat), reverse=True):
            cands.insert(0, os.path.join(plat, v, 'MpCmdRun.exe'))
    return next((c for c in cands if os.path.isfile(c)), None)


def defender_scan(path, timeout=600):
    """-> dict(ran, clean, detail). Exit code 0 = no threats, 2 = threats found."""
    exe = defender_path()
    if not exe:
        return dict(ran=False, clean=None, detail='Microsoft Defender is not available on this computer')
    try:
        r = subprocess.run([exe, '-Scan', '-ScanType', '3', '-File', path, '-DisableRemediation'],
                           capture_output=True, text=True, timeout=timeout, **NOWIN)
    except Exception as e:
        return dict(ran=False, clean=None, detail=f'Defender could not run ({e})')
    out = (r.stdout or '') + (r.stderr or '')
    return defender_verdict(r.returncode, out)


def defender_verdict(code, out):
    """Read MpCmdRun's answer. Exit code 2 (or 'found N threats' with N > 0) = a threat. Anything else that isn't 0 is
    the scanner failing to run - e.g. 'CmdTool: Failed with hr = 0x80004005' when Defender is switched off or another
    antivirus is in charge - which says nothing about the file, so it must never be reported as a threat."""
    import re
    m = re.search(r'found\s+(\d+)\s+threats?', out or '', re.I)
    if code == 2 or (m and int(m.group(1)) > 0):
        return dict(ran=True, clean=False, detail='Microsoft Defender found a threat: ' + ' '.join((out or '').split())[:200])
    if code == 0:
        return dict(ran=True, clean=True, detail='Microsoft Defender: no threats found')
    hr = re.search(r'hr\s*=\s*(0x[0-9a-f]+)', out or '', re.I)
    why = f'Windows error {hr.group(1)}' if hr else f'code {code}'
    return dict(ran=False, clean=None, detail=f'Microsoft Defender could not scan this file ({why}) - usually Defender is switched '
                                              'off or another antivirus is in charge. This is not a threat.')


# ----------------------------------------------------------------------------- VirusTotal
def _vt(method, url, key, data=None, headers=None, timeout=60):
    h = {'x-apikey': key, 'accept': 'application/json'}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode() or '{}')
        except Exception:
            body = {}
        return e.code, body


def verdict(stats):
    """Studio Lab's rule: installed only if not a single engine says malicious or suspicious."""
    bad = int(stats.get('malicious', 0)) + int(stats.get('suspicious', 0))
    total = sum(int(v) for k, v in stats.items() if k in ('malicious', 'suspicious', 'undetected', 'harmless'))
    return dict(clean=bad == 0 and total > 0, flagged=bad, engines=total)


def _report(sha256, attrs):
    v = verdict(attrs.get('last_analysis_stats') or attrs.get('stats') or {})
    names = sorted({r.get('engine_name') for r in (attrs.get('last_analysis_results') or attrs.get('results') or {}).values()
                    if r.get('category') in ('malicious', 'suspicious')} - {None})
    v.update(sha256=sha256, flagged_by=names[:8], link=f'https://www.virustotal.com/gui/file/{sha256}')
    return v


def vt_check(path, sha256, key, log=print, upload=True, wait=300):
    """-> dict(ran, clean, flagged, engines, link, detail)."""
    if not key:
        return dict(ran=False, clean=None, detail='no VirusTotal key (optional)')
    code, body = _vt('GET', f'{VT}/files/{sha256}', key)
    if code == 401:
        return dict(ran=False, clean=None, detail='the VirusTotal key was not accepted')
    if code == 200:
        attrs = body.get('data', {}).get('attributes', {})
        v = _report(sha256, attrs)
        if v['engines'] > 0:
            v.update(ran=True, detail=f"VirusTotal: {v['flagged']}/{v['engines']} engines flagged it")
            return v
    if code not in (200, 404) or not upload:
        return dict(ran=False, clean=None, detail=f'VirusTotal could not check it (HTTP {code})')
    size = os.path.getsize(path)
    if size > VT_MAX_UPLOAD:
        return dict(ran=False, clean=None, detail='too large for a VirusTotal upload')
    log('   VirusTotal has not seen this file yet - sending it for analysis (open-source release) ...')
    url = f'{VT}/files'
    if size > 32 * 1024 * 1024:
        c, b = _vt('GET', f'{VT}/files/upload_url', key)
        if c != 200:
            return dict(ran=False, clean=None, detail=f'VirusTotal upload not possible (HTTP {c})')
        url = b.get('data')
    boundary = '----studiolab' + os.urandom(8).hex()
    with open(path, 'rb') as f:
        payload = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
                   f'Content-Type: application/octet-stream\r\n\r\n').encode() + f.read() + f'\r\n--{boundary}--\r\n'.encode()
    c, b = _vt('POST', url, key, data=payload, headers={'content-type': f'multipart/form-data; boundary={boundary}'}, timeout=600)
    aid = b.get('data', {}).get('id')
    if c != 200 or not aid:
        return dict(ran=False, clean=None, detail=f'VirusTotal upload failed (HTTP {c})')
    t0 = time.time()
    while time.time() - t0 < wait:
        time.sleep(15)
        c, b = _vt('GET', f'{VT}/analyses/{aid}', key)
        attrs = b.get('data', {}).get('attributes', {})
        if c == 200 and attrs.get('status') == 'completed':
            v = _report(sha256, attrs)
            v.update(ran=True, detail=f"VirusTotal: {v['flagged']}/{v['engines']} engines flagged it")
            return v
        log('   ... still being analysed by VirusTotal')
    return dict(ran=False, clean=None, detail='VirusTotal analysis is taking longer than 5 minutes - try again later')


def scan_binaries(folder, key):
    """Look up every plugin program file (DLL / dylib / so) on VirusTotal by hash - no upload."""
    import hashlib
    if not key:
        return []
    out, n = [], 0
    for root, dirs, files in os.walk(folder):
        for fn in files:
            fp = os.path.join(root, fn)
            if os.path.islink(fp) or os.path.getsize(fp) < 10_000:
                continue
            with open(fp, 'rb') as f:
                head = f.read(4)
            if head[:2] != b'MZ' and head not in (b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\x7fELF'):
                continue
            with open(fp, 'rb') as f:
                h = hashlib.sha256(f.read()).hexdigest()
            if n >= 2:
                time.sleep(16)                          # free keys allow 4 lookups a minute
            n += 1
            code, body = _vt('GET', f'{VT}/files/{h}', key)
            if code == 200:
                v = _report(h, body.get('data', {}).get('attributes', {}))
                v['file'] = fn
                out.append(v)
    return out
