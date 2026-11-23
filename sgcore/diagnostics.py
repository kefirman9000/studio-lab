"""Problem report: one text file with everything needed to see why something went wrong.

Collected: app / Python / OS versions, libraries, settings, sound libraries, plugins (found, broken and why), recent
jobs with their errors and warnings, and the last few hundred log lines. Secrets are never included: API keys are
replaced by "set / not set", and your user name / home folder / e-mail addresses are masked.
"""
import collections
import io
import os
import platform
import re
import sys
import threading
import time
import traceback

from . import updater

ROOT = updater.ROOT
LOG_DIR = os.path.join(ROOT, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'studiolab.log')
LINES = collections.deque(maxlen=1500)
_lock = threading.Lock()


class _Tee(io.TextIOBase):
    """Copies everything the app prints into a ring buffer and a log file (and the console, if there is one)."""

    def __init__(self, orig, tag=''):
        self.orig = orig
        self.tag = tag
        self.buf = ''

    def write(self, s):
        if self.orig is not None:
            try:
                self.orig.write(s)
            except Exception:
                pass
        with _lock:
            self.buf += s
            while '\n' in self.buf:
                line, self.buf = self.buf.split('\n', 1)
                if line.strip():
                    stamp = time.strftime('%H:%M:%S')
                    LINES.append(f'{stamp} {self.tag}{line}')
                    _to_file(f'{time.strftime("%Y-%m-%d")} {stamp} {self.tag}{line}\n')
        return len(s)

    def flush(self):
        if self.orig is not None:
            try:
                self.orig.flush()
            except Exception:
                pass


def _to_file(text):
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 2_000_000:
            os.replace(LOG_FILE, LOG_FILE + '.1')
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(text)
    except Exception:
        pass


def capture():
    """Start recording the app's output (safe to call once at startup)."""
    if not isinstance(sys.stdout, _Tee):
        sys.stdout = _Tee(sys.stdout)
        sys.stderr = _Tee(sys.stderr, 'ERR ')
    _orig_hook = threading.excepthook

    def hook(args):
        LINES.append('ERR thread crashed: ' + ''.join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)))
        try:
            _orig_hook(args)
        except Exception:
            pass
    threading.excepthook = hook


def log(*a):
    print(' '.join(str(x) for x in a))


# ----------------------------------------------------------------------------- redaction
def redact(text):
    home = os.path.expanduser('~')
    user = os.path.basename(home)
    if home and len(home) > 3:
        text = text.replace(home, '~').replace(home.replace('\\', '/'), '~')
    if user and len(user) > 2:
        text = re.sub(r'(?i)(?<![A-Za-z0-9])' + re.escape(user) + r'(?![A-Za-z0-9])', '<user>', text)
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '<email>', text)
    text = re.sub(r'\b[0-9a-fA-F]{64}\b', '<key>', text)                       # VirusTotal-style API keys
    text = re.sub(r'(?i)(token|apikey|api_key|key)=([A-Za-z0-9_\-]{16,})', r'\1=<hidden>', text)
    return text


# ----------------------------------------------------------------------------- the report
def _section(title, fn):
    out = [f'\n=== {title} ' + '=' * max(3, 70 - len(title))]
    try:
        res = fn()
        out.extend(res if isinstance(res, list) else [str(res)])
    except Exception as e:
        out.append(f'(could not collect: {e})')
    return out


def _versions():
    out = []
    try:
        with open(os.path.join(ROOT, 'VERSION')) as f:
            out.append('Studio Lab ' + f.read().strip())
    except Exception:
        out.append('Studio Lab (version unknown)')
    out.append(f'Python {sys.version.split()[0]} ({platform.architecture()[0]}, {sys.executable and os.path.basename(sys.executable)})')
    out.append(f'OS {platform.platform()}  machine={platform.machine()}')
    for mod in ('numpy', 'scipy', 'pedalboard', 'soundfile', 'mido', 'webview'):
        try:
            m = __import__(mod)
            out.append(f'{mod} {getattr(m, "__version__", "installed")}')
        except Exception as e:
            out.append(f'{mod}: not available ({type(e).__name__})')
    out.append(f'app folder: {ROOT}')
    return out


def _settings():
    import json
    p = os.path.join(ROOT, 'settings.json')
    if not os.path.exists(p):
        return ['(no settings.json)']
    with open(p) as f:
        s = json.load(f)
    out = []
    for k, v in sorted(s.items()):
        if 'key' in k.lower() or 'token' in k.lower():
            v = 'set' if v else 'not set'
        out.append(f'{k}: {json.dumps(v)[:300]}')
    return out


def _libraries():
    out = []
    try:
        from . import soundfont
        out.append(f'General MIDI library: {"installed" if soundfont.installed() else "not installed"}')
    except Exception as e:
        out.append(f'General MIDI library: error {e}')
    from . import samplelibs
    for r in samplelibs.status():
        out.append(f"{r['id']}: {'installed' if r['installed'] else 'not installed'}"
                   + (f" (update available +{r['update_mb']} MB)" if r.get('update_mb') else ''))
    return out


def _plugins():
    out = []
    from . import vsthost
    out.append(f'VST support (pedalboard): {"yes" if vsthost.available() else "no"}')
    try:
        from . import vstrigs
        found = vstrigs.plugins_on_disk()
        out.append(f'{len(found)} plugin(s) found:')
        for x in found:
            if isinstance(x, dict):
                out.append(f"  {x.get('name') or os.path.basename(x.get('path', ''))}  ->  {x.get('path')}  {x.get('kind') or ''}")
            else:
                out.append(f'  {x}')
    except Exception as e:
        out.append(f'plugin scan error: {e}')
    bad = vsthost.broken()
    if bad:
        out.append('plugins that failed to load (and why):')
        for path, why in bad.items():
            out.append(f'  {path}: {why}')
    else:
        out.append('no plugins marked as failing')
    try:
        from . import vstpacks
        st = vstpacks.status()
        out.append(f"genre VST packs (folder {st.get('folder')}, os {st.get('os')}):")
        for p in st.get('packs', []):
            out.append(f"  {p.get('id')}: installed={p.get('installed')} partial={p.get('partial')} version={p.get('version')}"
                       + (f" checks={p.get('checks')}" if p.get('checks') else ''))
            for x in (p.get('paths') or [])[:4]:
                out.append(f'     {x}')
        for k in st.get('known', []):
            out.append(f"  known plugin {k.get('id')}: installed={k.get('installed')}")
    except Exception as e:
        out.append(f'genre packs: {e}')
    try:
        sounds = vsthost.list_sounds()
        out.append(f'saved plugin sounds: {len(sounds)}')
    except Exception:
        pass
    return out


def _jobs(jobs):
    out = []
    items = sorted(jobs.values(), key=lambda j: j.get('started') or 0)[-25:]
    if not items:
        return ['(nothing generated or installed since the app started)']
    for j in items:
        when = time.strftime('%H:%M:%S', time.localtime(j['started'])) if j.get('started') else '--:--:--'
        opts = [it.get('options', {}) for it in j.get('items', [])]
        what = ', '.join(f"{o.get('style')} seed {o.get('seed')}" for o in opts[:3]) or 'task'
        out.append(f"[{when}] {j.get('status')}  {what}")
        if j.get('error'):
            out.append(f"   ERROR: {j['error']}")
        for r in j.get('results', [])[:3]:
            for w in (r.get('warnings') or []):
                out.append(f'   warning: {w}')
        errs = [l for l in j.get('log', []) if 'Traceback' in l or 'Error' in l or '⚠' in l or 'failed' in l.lower()]
        for l in errs[-6:]:
            out.append('   ' + l.strip().replace('\n', '\n   ')[:2000])
    return out


def build(jobs=None, note=''):
    parts = [f'STUDIO LAB PROBLEM REPORT  -  {time.strftime("%Y-%m-%d %H:%M:%S")}',
             'Send this file to whoever is helping you. Keys, your user name and e-mail addresses are removed.']
    if note.strip():
        parts += ['', 'What happened (from you):', note.strip()[:4000]]
    parts += _section('Versions', _versions)
    parts += _section('Settings', _settings)
    parts += _section('Sound libraries', _libraries)
    parts += _section('Plugins', _plugins)
    parts += _section('Recent jobs (generate / preview / installs)', lambda: _jobs(jobs or {}))
    parts += _section('Recent log', lambda: list(LINES)[-400:] or ['(empty)'])
    parts += _section('Start-up log (startup.log)', _startup)
    parts += _section('Last update', _update_state)
    return redact('\n'.join(parts) + '\n')


def _startup():
    """(2.16) The window's start-up log: how far the last start got, and any request that kept the page waiting."""
    try:
        with open(os.path.join(ROOT, 'startup.log'), encoding='utf-8', errors='replace') as f:
            return f.read().splitlines()[-200:] or ['(empty)']
    except OSError:
        return ['(no startup.log yet)']


def _update_state():
    out = []
    for fn in ('.update_pending.json', '.update_rolled_back.json'):
        try:
            with open(os.path.join(ROOT, fn)) as f:
                out.append(f'{fn}: {f.read()[:400]}')
        except OSError:
            pass
    return out or ['(nothing pending)']


# ----------------------------------------------------------------------------- short technical summary (copy & paste)
def _tracebacks(lines, limit=4):
    """The last few Python tracebacks in the log, each with its final error line."""
    out, cur = [], None
    for l in lines:
        if 'Traceback (most recent call last)' in l:
            cur = [l]
            out.append(cur)
        elif cur is not None:
            cur.append(l)
            st = l.strip()
            if st and not l.startswith((' ', '\t')) and ('Error' in st or 'Exception' in st or ':' in st):
                cur = None
    return out[-limit:]


def summary(jobs=None, note=''):
    """A compact, paste-able block with just the technical facts: versions, what failed, the errors and tracebacks,
    the settings of the failing songs and the end of the log. Same redaction as the full report."""
    import json
    v = _versions()
    out = ['STUDIO LAB TECHNICAL SUMMARY  ' + time.strftime('%Y-%m-%d %H:%M'), v[0], v[1], v[2]]
    if note.strip():
        out += ['note: ' + note.strip()[:600]]
    try:
        from . import samplelibs, soundfont
        libs = [r['id'] for r in samplelibs.status() if r['installed']]
        out.append('libraries: GM=' + ('yes' if soundfont.installed() else 'no') + ' real=' + (','.join(libs) or 'none'))
    except Exception as e:
        out.append(f'libraries: error {e}')
    try:
        from . import vsthost
        bad = vsthost.broken()
        out.append(f'vst: pedalboard={"yes" if vsthost.available() else "no"} broken={len(bad)}')
        for path, why in list(bad.items())[:6]:
            out.append(f'  broken: {os.path.basename(path)}: {str(why)[:200]}')
    except Exception as e:
        out.append(f'vst: error {e}')
    items = sorted((jobs or {}).values(), key=lambda j: j.get('started') or 0)
    failed = [j for j in items if j.get('status') == 'error' or j.get('error')
              or any(r.get('warnings') for r in j.get('results', []))]
    out.append(f'jobs since start: {len(items)}, with errors/warnings: {len(failed)}')
    for j in failed[-3:]:
        opts = [it.get('options', {}) for it in j.get('items', [])][:1]
        out.append('--- job ' + str(j.get('status')) + (': ' + str(j.get('error'))[:600] if j.get('error') else ''))
        for o in opts:
            o = {k: v_ for k, v_ in o.items() if v_ not in (None, '', [], {}, False)}
            out.append('options: ' + json.dumps(o, default=str)[:900])
        for r in j.get('results', [])[:2]:
            for w in (r.get('warnings') or [])[:5]:
                out.append('warning: ' + str(w)[:300])
        tail = [x.rstrip() for l in j.get('log', []) for x in str(l).splitlines() if x.strip()][-30:]
        out += ['log> ' + l[:300] for l in tail]
    lines = list(LINES)
    tbs = _tracebacks(lines)
    for tb in tbs:
        out.append('--- traceback')
        out += [l.rstrip()[:300] for l in (tb[:3] + ['  ...'] + tb[-12:] if len(tb) > 16 else tb)]
    errs = [l.rstrip() for l in lines[-400:] if re.search(r'(?i)error|failed|exception|warning|⚠', l)]
    if errs:
        out.append('--- recent error lines')
        out += [l[:300] for l in errs[-15:]]
    out.append('--- last log lines')
    out += [l.rstrip()[:300] for l in lines[-20:]] or ['(empty)']
    text = redact('\n'.join(out))
    if len(text) > 12000:
        text = text[:6000] + '\n... (shortened) ...\n' + text[-5800:]
    return '```\n' + text + '\n```\n'


# ----------------------------------------------------------------------------- synth parameter report (for writing genre patches)
REPORT_SYNTHS = ('ob-xf', 'obxf', 'odin', 'monique', 'six sines', 'sixsines', 'surge xt', 'dexed', 'vital', 'noisemaker', 'jc303', 'ripplerx')


def synth_params(limit=400):
    """Every installed genre synth's parameter names (and the choices of switch-type parameters) - paste this so genre
    patches can be written for the exact plugin you have. Nothing personal is included."""
    from . import vsthost, vstrigs
    out = ['STUDIO LAB SYNTH PARAMETERS  ' + time.strftime('%Y-%m-%d %H:%M')]
    try:
        plugins = vstrigs.plugins_on_disk(refresh=True)
    except Exception as e:
        return f'```\ncould not scan plugins: {e}\n```\n'
    seen = set()
    for pl in plugins:
        name = (pl.get('name') if isinstance(pl, dict) else str(pl)) or ''
        path = pl.get('path') if isinstance(pl, dict) else None
        low = name.lower()
        if not path or not any(k in low for k in REPORT_SYNTHS) or low in seen or pl.get('is_effect'):
            continue
        seen.add(low)
        try:
            res = vsthost.probe(path, list_params=True) or {}
        except Exception as e:
            out.append(f'== {name}: could not load ({e})')
            continue
        params = res.get('params') or []
        out.append(f'== {name}  ({os.path.splitext(os.path.basename(path))[1]}, {len(params)} parameters)')
        for prm in params[:limit]:
            ch = prm.get('choices') or []
            out.append(f"{prm.get('name') or prm.get('attr')}" + (f"  [{' | '.join(ch[:12])}]" if ch else ''))
    if len(out) == 1:
        out.append('(none of OB-Xf, Odin 2, Monique, Six Sines, Surge XT, Dexed, Vital or TAL-NoiseMaker found)')
    text = redact('\n'.join(out))
    return '```\n' + text[:60000] + '\n```\n'
