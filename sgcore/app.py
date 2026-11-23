"""Local web app: a tiny HTTP server (standard library only) + a single-page UI that opens in your browser."""
import hmac
import json
import re
import mimetypes
import secrets
import os
import queue
import random
import subprocess
import sys
import threading
import time
import traceback
import uuid
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote

import numpy as np

from . import updater, plugins
from .api import generate, have_ffmpeg
from .compose import Options, MOODS, FUSION_PARTS, PART_LABELS, MELODY_STYLES
from .theory import SCALES, NOTE_NAMES, VOICINGS, COLORS
from .instruments import ROLE_CHOICES, INSTRUMENT_INFO, KITS
from .styles import STYLES, CATEGORIES, POOLS, label

ROOT = updater.ROOT
HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = os.path.join(ROOT, 'settings.json')
PRESETS = os.path.join(ROOT, 'presets')



EXTRA_LABELS = {'horns': 'Horn stabs', 'stabs': 'Brass stabs', 'gtr': 'Rhythm guitar', 'whistle': 'Tin whistle (with the tune)',
                'keys': 'Keys (with the chords)', 'saws': 'Supersaws (with the chords)', 'chords_r': 'Second guitar (double-tracked)',
                'bass_up': 'Upper bass (doubling)', 'solo_banjo': 'Banjo breaks', 'solo_mando': 'Mandolin breaks',
                'solo_gtr': 'Guitar breaks / solo', 'solo_sax': 'Sax solo', 'solo_keys': 'Keys solo', 'celli': 'Celli (doubling)',
                'lead_oct': 'Lead an octave down', 'counter': 'Counter-melody'}


def extra_label(t):
    """A readable name for a genre's extra part in the Sound panel."""
    if t['name'] in EXTRA_LABELS:
        return EXTRA_LABELS[t['name']]
    return t['name'].replace('_', ' ').capitalize() + f" ({t['layer']})"

def load_settings():
    try:
        with open(SETTINGS) as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(d):
    s = load_settings()
    s.update(d)
    with open(SETTINGS, 'w') as f:
        json.dump(s, f, indent=2)


def host_os():
    return 'windows' if sys.platform.startswith('win') else ('mac' if sys.platform == 'darwin' else 'linux')


_DETECT = {'t': 0.0, 'res': None, 'lock': threading.Lock()}


def detected(refresh=False, max_age=300):
    """Plugins installed on this computer (scanned automatically, cached for a few minutes)."""
    with _DETECT['lock']:
        if refresh or _DETECT['res'] is None or time.time() - _DETECT['t'] > max_age:
            try:
                _DETECT['res'] = plugins.scan()
            except Exception:
                _DETECT['res'] = _DETECT['res'] or dict(found={}, other=[], dirs=[])
            _DETECT['t'] = time.time()
            try:
                from . import vsthost as _vh
                _vh._FIND['t'] = 0.0                     # (2.14.3) a fresh plugin list after a rescan / install
                _vh._SIG_CACHE.clear()
            except Exception:
                pass
            try:
                from . import vstrigs
                vstrigs.plugins_on_disk(refresh=True)
            except Exception:
                pass
        return _DETECT['res']


def plugin_prefs():
    st = load_settings()
    found = detected()['found']
    return dict(owned=sorted(found), daws=st.get('daws') or ['lmms', 'waveform'],
                os=st.get('os') or host_os(), found=found)


def storage_loop():
    """Tidy the output folder at start-up and then every hour (old previews; unkept songs per the storage setting)."""
    from . import storage
    while True:
        try:
            storage.clean(out_dir(), storage.policy(load_settings()), log=print)
        except Exception as e:
            print('storage clean-up skipped:', e)
        time.sleep(3600)


def _native_window_support():
    """Windows: install pywebview in the background (once) so the NEXT launch opens Studio Lab in a native window - it
    then runs as its own app (pythonw), so a pinned taskbar shortcut and the running window are one taskbar button.
    Without it the app window is an Edge / Chrome app window, which Windows groups with the browser."""
    if sys.platform != 'win32' or load_settings().get('no_native_window'):
        return
    try:
        import webview  # noqa: F401
        return
    except ImportError:
        pass
    try:
        import subprocess
        exe = sys.executable
        if exe.lower().endswith('pythonw.exe'):
            exe = exe[:-len('pythonw.exe')] + 'python.exe'
        subprocess.run([exe, '-m', 'pip', 'install', '--user', '--quiet', 'pywebview'], capture_output=True, timeout=600,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except Exception as e:
        print('native window support not installed:', e)


def startup_detect():
    """Scan plugin folders; if any plugin the genre rigs can play is installed, make sure VST support is ready."""
    _native_window_support()
    try:
        detected(refresh=True)
        from . import vsthost, vstrigs
        if not vsthost.available():
            usable = [pid for pid, pl in vstrigs.PLAYERS.items() if vstrigs.player_path(pid)]
            if usable:
                print('Found plugins Studio Lab can play (' + ', '.join(vstrigs.PLAYERS[u]['name'] for u in usable) +
                      ') - installing VST support (pedalboard) in the background ...')
                print('VST support ready.' if vsthost.install(log=lambda *a: None) else
                      'Could not install VST support - run:  python -m pip install pedalboard')
        if vsthost.available():
            n = vsthost.probe_all()                      # instrument or effect? (once per plugin, cached)
            if n:
                print(f'Checked {n} plugin(s) - instruments now appear in the Sound menus.')
    except Exception as e:
        print('Plugin scan failed:', e)


def plugin_state():
    pr = plugin_prefs()
    cat = []
    for p in plugins.CATALOG:
        cat.append(dict(id=p['id'], name=p['name'], maker=p['maker'], url=p['url'], free=p['free'], cats=p['cats'], tip=p['tip'],
                        formats=pr['found'].get(p['id']) or p['formats'], owned=p['id'] in pr['owned'],
                        installed=p['id'] in pr['found'], works=plugins.works_in(p, pr['daws'], pr['os'], pr['found'].get(p['id']))))
    d = detected()
    return dict(catalog=cat, daws=pr['daws'], os=pr['os'], host_os=host_os(), other=d.get('other', []),
                scanned=d.get('dirs', []), scanned_at=int(_DETECT['t']))


RATINGS = os.path.join(ROOT, 'ratings.json')


def load_ratings():
    try:
        with open(RATINGS) as f:
            return json.load(f)
    except Exception:
        return []


def taste():
    """What you tend to like: weights for styles and moods, preferred energy/complexity."""
    rs = load_ratings()
    styles, moods, en, cx = {}, {}, [], []
    part_likes, inst_likes = {}, {}
    for r in rs:
        if r.get('part'):                              # "I like this drum part" etc.
            o = r.get('options', {})
            if r.get('rating', 0) > 0:
                part_likes.setdefault(o.get('style'), {}).setdefault(r['part'], []).append(r.get('part_seed'))
                role = {'melody': 'lead', 'drums': None}.get(r['part'], r['part'])
                if role and r.get('inst') and not str(r['inst']).startswith(('VST', 'my sample')):
                    inst_likes.setdefault(role, {})[r['inst']] = inst_likes.get(role, {}).get(r['inst'], 0) + 1
            continue
        o, v = r.get('options', {}), r.get('rating', 0)
        for sname in [o.get('style')] + list(o.get('blend') or []):
            if sname:
                styles[sname] = styles.get(sname, 0) + v
        if o.get('mood'):
            moods[o['mood']] = moods.get(o['mood'], 0) + v
        if v > 0:
            en.append(o.get('energy', 0.5))
            cx.append(o.get('complexity', 0.5))
    return dict(count=len(rs), styles=styles, moods=moods,
                energy=round(sum(en) / len(en), 2) if en else None, complexity=round(sum(cx) / len(cx), 2) if cx else None,
                liked=sorted([k for k, v in styles.items() if v > 0], key=lambda k: -styles[k])[:5],
                part_likes={k: {p: v[-5:] for p, v in d.items()} for k, d in part_likes.items()}, inst_likes=inst_likes)


def out_dir():
    d = load_settings().get('output_dir') or os.path.join(ROOT, 'songs')
    os.makedirs(d, exist_ok=True)
    return d


# ----------------------------------------------------------------------------- job queue (one render at a time)
JOBS = {}
WORK = queue.Queue()

# ----------------------------------------------------------------------------- security
# The server only listens on 127.0.0.1 (never reachable from other computers). On top of that:
#  * every API/file request must carry a random per-launch token (cookie set only on our own page, SameSite=Strict,
#    plus a custom header on API calls) -> other websites open in your browser cannot drive the app (CSRF)
#  * the Host header must be 127.0.0.1/localhost -> blocks DNS-rebinding attacks
#  * files are only served / opened from inside the output folder; uploads are size-limited
TOKEN = secrets.token_urlsafe(32)
PORT = [8765]
MAX_UPLOAD = 64 * 1024 * 1024


def inside(path, root):
    try:
        path, root = os.path.realpath(path), os.path.realpath(root)
        return os.path.commonpath([path, root]) == root
    except ValueError:
        return False


RECENT_FILE = os.path.join(ROOT, 'recent_instruments.json')
SEED_AVOID = {}                                   # (style, seed) -> the freshness list that song was made with
_RECENT_LOCK = threading.Lock()


def recent_avoid(style, songs=3):
    """Instruments the last few songs in this genre used (picked less often next time, so it sounds fresh)."""
    try:
        with open(RECENT_FILE) as f:
            hist = json.load(f).get(style, [])
    except Exception:
        return {}
    out = {}
    for h in hist[-songs:]:
        for role, insts in h.items():
            out.setdefault(role, [])
            out[role] += [i for i in insts if i not in out[role]]
    return out


def remember_instruments(style, ids):
    if not ids:
        return
    with _RECENT_LOCK:
        try:
            with open(RECENT_FILE) as f:
                d = json.load(f)
        except Exception:
            d = {}
        d[style] = (d.get(style, []) + [ids])[-6:]
        with open(RECENT_FILE, 'w') as f:
            json.dump(d, f)


def worker():
    while True:
        job = WORK.get()
        job['status'] = 'running'
        job['started'] = time.time()
        try:
            for i, item in enumerate(job['items']):
                job['current'] = i

                def log(*a):
                    job['log'].append(' '.join(str(x) for x in a))

                def prog(p, i=i):
                    job['progress'] = (i + p) / len(job['items'])
                sub = os.path.join(out_dir(), 'previews') if item['preview'] else out_dir()
                info = generate(item['options'], sub, outputs=item['outputs'], preview=item['preview'], log=log, progress=prog,
                                prefs=plugin_prefs(), section=item.get('section'), loop=item.get('loop', False))
                info['options'] = item['options']
                if not item.get('section'):
                    remember_instruments(item['options'].get('style'), info.get('inst_ids'))
                rel = lambda v: '/files/' + os.path.relpath(v, out_dir()).replace(os.sep, '/')
                info['urls'] = {k: rel(v) for k, v in info['files'].items() if k != 'waveform' and isinstance(v, str) and os.path.isfile(v)}
                info['part_urls'] = {k: rel(v) for k, v in (info.get('parts') or {}).items()}
                if not item['preview'] and isinstance(info['files'].get('wav') or info['files'].get('mp3'), str):
                    info['project'] = project_base(info['files'].get('wav') or info['files'].get('mp3'))   # for ⭐ Keep
                info.pop('parts', None)
                info['id'] = uuid.uuid4().hex[:8]
                job['results'].append(info)
            job['status'] = 'done'
        except Exception as e:
            job['status'] = 'error'
            job['error'] = str(e)
            job['log'].append(traceback.format_exc())
            print('ERROR in generate job:\n' + traceback.format_exc())
        job['progress'] = 1.0
        WORK.task_done()


def submit(items):
    jid = uuid.uuid4().hex[:10]
    JOBS[jid] = dict(id=jid, status='queued', progress=0.0, log=[], results=[], items=items, error=None, current=0)
    WORK.put(JOBS[jid])
    return jid


def real_insts(role):
    try:
        from . import samplelibs
        return samplelibs.choices(role)
    except Exception:
        return []


def other_insts(role, suited):
    """Every other sound, listed under the ones that suit the part: any instrument can play any part if you want it to."""
    from .instruments import INSTRUMENTS, DRUMS
    seen = set(suited)
    out = [dict(id=i, name=INSTRUMENT_INFO.get(i, i), group='Other built-in sounds (any part)')
           for i in sorted(INSTRUMENTS, key=lambda x: INSTRUMENT_INFO.get(x, x).lower()) if i not in seen and i not in DRUMS]
    mine = {x['id'] for x in real_insts(role)}
    out += [dict(x, group='Other real instruments (any part)') for x in real_insts(None) if x['id'] not in mine]
    return out


def user_insts():
    from . import usersounds, vsthost
    return ([dict(id='user:' + n, name='My sound: ' + n, group='My sounds') for n in usersounds.listing()['inst']] +
            [dict(id='vst:' + v['id'], name='VST: ' + v['name'], group='My VST sounds') for v in vsthost.list_sounds()
             if v['ok'] and not v.get('auto')])


_PRESETS = {'t': 0.0, 'v': {}}


def plugin_presets():
    from . import vsthost
    if time.time() - _PRESETS['t'] > 120:
        try:
            _PRESETS['v'] = vsthost.presets()
        except Exception:
            _PRESETS['v'] = {}
        _PRESETS['t'] = time.time()
    return _PRESETS['v']


def vst_insts(role):
    try:
        from . import vsthost, vstrigs
        if not vsthost.available():
            return []
        insts = vsthost.instrument_names()
        out = vstrigs.layer_choices(role, instruments=insts)
        pr = sorted(plugin_presets().items(), key=lambda kv: (kv[1]['plugin'].lower(), kv[1]['name'].lower()))
        out += [dict(id='vstq:' + pid, name=f"{p['plugin']} · {p['name']}", group='Plugin presets')
                for pid, p in pr if p['plugin'] in insts][:300]
        return out
    except Exception:
        return []


def vst_effects():
    try:
        from . import vsthost
        return vsthost.effect_names() if vsthost.available() else []
    except Exception:
        return []


def bg_job(fn):
    """Run a non-render task (install, plugin window, preview) in the background with the same job API."""
    jid = uuid.uuid4().hex[:10]
    job = dict(id=jid, status='running', progress=0.0, log=[], results=[], items=[], error=None, current=0)
    JOBS[jid] = job

    def run():
        try:
            res = fn(lambda *a: job['log'].append(' '.join(str(x) for x in a)))
            job['results'].append(res if isinstance(res, dict) else {'value': res})
            job['status'] = 'done'
        except Exception as e:
            job['status'] = 'error'
            job['error'] = str(e)
            job['log'].append(traceback.format_exc())
            print('ERROR in background task:\n' + traceback.format_exc())
        job['progress'] = 1.0
    job['started'] = time.time()
    threading.Thread(target=run, daemon=True).start()
    return jid


def _search_tags(st):
    """Words the genre search also matches: its instruments (built-in names and the plain-English hint) and scales."""
    from .instruments import INSTRUMENT_INFO
    words = {t['inst'] for t in st.get('tracks', [])} | {INSTRUMENT_INFO.get(t['inst'], '') for t in st.get('tracks', [])}
    words |= set(st.get('scales', [])) | {st.get('gm_hint') or ''}
    return ' '.join(sorted(w.replace('_', ' ').lower() for w in words if w))


def meta():
    from .genre_groups import display_group as group_of, display_rank as rank, display_order as order   # (2.14.1)
    by_cat = {c: [] for c in CATEGORIES}
    for k, v in sorted(STYLES.items(), key=lambda kv: rank(kv[0])):
        by_cat[v['category']].append(dict(id=k, name=label(k), desc=v['desc'], bpm=v['bpm'], group=group_of(k),
                                       tags=_search_tags(v)))
    return dict(
        version=updater.local_version(), repo=updater.repo(), ffmpeg=have_ffmpeg(), output_dir=out_dir(),
        categories=by_cat, group_order={c: order(c) for c in CATEGORIES}, moods=list(MOODS), scales=list(SCALES), keys=NOTE_NAMES,
        roles={r: [dict(id=i, name=INSTRUMENT_INFO.get(i, i), group='Built-in (suits this part)') for i in lst] + real_insts(r) + vst_insts(r) + user_insts()
               + other_insts(r, lst) for r, lst in ROLE_CHOICES.items()},
        vox_samples=__import__('sgcore.usersounds', fromlist=['listing']).listing()['vocal'],
        effects=vst_effects(), part_effects=[[k, v] for k, v in __import__('sgcore.part_effects', fromlist=['menu']).menu()], drum_voice_menu=[list(e) for e in __import__('sgcore.drumkits', fromlist=['voice_menu']).voice_menu()], voicings=VOICINGS, melody_styles=MELODY_STYLES, chord_colors=[c for c in COLORS if c != 'add9no3'],
        drum_patterns=__import__('sgcore.drumkits', fromlist=['pattern_menu']).pattern_menu(),
        perc_sets=__import__('sgcore.drummer', fromlist=['perc_menu']).perc_menu(), beat_feels={k: __import__('sgcore.drummer', fromlist=['beat_feel']).beat_feel(k) for k in STYLES}, drummer_menu=__import__('sgcore.drummer', fromlist=['DRUMMER_MENU']).DRUMMER_MENU,
        kits=__import__('sgcore.drumkits', fromlist=['sound_menu']).sound_menu() + [dict(id=k, group='Other synth kits', label=k.title())
                                                                         for k in KITS if k not in ('default',) and k not in
                                                                         __import__('sgcore.drumkits', fromlist=['MENU']).MENU],
        window=load_settings().get('window', 'app'), genre_kits=__import__('sgcore.drumkits', fromlist=['GENRE_KIT']).GENRE_KIT, journey_presets=__import__('sgcore.journey', fromlist=['PRESETS']).PRESETS, journey_parts=[dict(id=n, name=l, layer=next(t['layer'] for t in STYLES['cinematic_journey']['tracks'] if t['name'] == n), inst=next(t['inst'] for t in STYLES['cinematic_journey']['tracks'] if t['name'] == n)) for n, l in __import__('sgcore.journey', fromlist=['PLAYERS']).PLAYERS], parts=[dict(id=p, name=PART_LABELS[p]) for p in FUSION_PARTS],
        labels={k: label(k) for k in STYLES},
        drum_sounds=[dict(id=d, name=__import__('sgcore.api', fromlist=['DRUM_PART']).DRUM_PART.get(d, d.replace('_', ' ').capitalize()))
                     for d in sorted(__import__('sgcore.instruments', fromlist=['DRUMS']).DRUMS)],
        traits_meta=[dict(id=k, name=lab, values=[v for v in vals if v not in __import__('sgcore.traits', fromlist=['x']).DESCRIPTIVE_VALUES.get(k, ())])
                     for k, (lab, vals) in __import__('sgcore.traits', fromlist=['x']).CATEGORIES.items()
                     if k not in __import__('sgcore.traits', fromlist=['x']).DESCRIPTIVE],
        genre_traits=__import__('sgcore.traits', fromlist=['x']).all_traits(),
        style_pools={k: {r: list(v) for r, v in (POOLS.get(k) or {}).items()} for k in STYLES},
        style_defaults={k: {t['layer']: t['inst'] for t in sorted(v['tracks'], key=lambda t: t['name'] == t['layer'])
                            if t['layer'] in ROLE_CHOICES} for k, v in STYLES.items()},
        style_extras={k: [dict(id=t['name'], layer=t['layer'], inst=t['inst'], name=extra_label(t)) for t in v['tracks']
                          if t['layer'] in ROLE_CHOICES and t['name'] != t['layer']]
                      for k, v in STYLES.items() if not v.get('composer')},
    )


def _lib_item(d, base, s=None):
    if s is None:
        with open(os.path.join(d, base + '_settings.json')) as fh:
            s = json.load(fh)
    files = {}
    for ext, k in (('.mp3', 'mp3'), ('.wav', 'wav'), ('.mid', 'midi'), ('.mmp', 'lmms')):
        if os.path.exists(os.path.join(d, base + ext)):
            files[k] = '/files/' + base + ext
    wf = os.path.join(d, base + '_waveform')
    info = dict(s.get('info') or {})
    info['files'] = {'folder': wf if os.path.isdir(wf) else d}
    return dict(title=base, info=info, options=s.get('options') or {}, urls=files, kept=bool(s.get('kept')),
                trimmed=not any(k in files for k in ('mp3', 'wav')))


def library():
    items = []
    d = out_dir()
    rated = {}                                       # (2.7) latest whole-song 👍 / 👎 per (style, seed), for the filters
    for r in load_ratings():
        o = r.get('options') or {}
        if not r.get('part') and o.get('style'):
            rated[(o.get('style'), o.get('seed'))] = r.get('rating')
    for f in sorted(os.listdir(d), key=lambda x: os.path.getmtime(os.path.join(d, x)), reverse=True):
        if f.endswith('_settings.json'):
            try:
                it = _lib_item(d, f[:-len('_settings.json')])
                o = it.get('options') or {}
                it['rating'] = rated.get((o.get('style'), o.get('seed', (it.get('info') or {}).get('seed'))))
                items.append(it)
            except Exception:
                pass
        if len(items) >= 300:                        # (2.7) the filters make a longer list usable
            break
    return items


PROJECT_SUFFIXES = ('_settings.json', '_PLUGIN_GUIDE.txt', '_samplepack', '_waveform', '_DAW', '_parts', '_stems',
                    '.mp3', '.wav', '.mid', '.mmp', '.json', '.zip', '.flac')


def project_base(name):
    """'Song_house_C-minor_124bpm_seed5_settings.json' / '.mp3' / '_waveform' ... -> the project's base name."""
    base = os.path.basename(str(name or '').replace('\\', '/'))
    changed = True
    while changed:
        changed = False
        for suf in PROJECT_SUFFIXES:
            if base.lower().endswith(suf.lower()) and len(base) > len(suf):
                base = base[:-len(suf)]
                changed = True
    return base


def open_project(name=None, settings=None):
    """A past project to open in the editor: from a dropped settings file, or any file it exported (the MP3, WAV,
    MIDI, plugin guide ...) whose settings are still in your output folder."""
    d = out_dir()
    base = project_base(name) if name else ''
    if base and os.path.exists(os.path.join(d, base + '_settings.json')):
        return dict(_lib_item(d, base), found=True)
    if isinstance(settings, dict):
        opts = settings.get('options') if isinstance(settings.get('options'), dict) else settings
        if not isinstance(opts, dict) or not opts.get('style'):
            raise ValueError('that file has no Studio Lab settings in it')
        Options.from_dict(opts)                                       # validates
        return dict(title=base or 'Imported project', info=settings.get('info') or {}, options=opts, urls={}, found=False)
    raise ValueError(f'no project called "{base}" in your output folder - drop its _settings.json file instead')


def open_dir(p):
    if sys.platform.startswith('win'):
        os.startfile(p)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', p])
    else:
        subprocess.Popen(['xdg-open', p])


def open_path(p):
    if not os.path.isdir(p):           # only ever open folders - never launch files
        p = os.path.dirname(p)
    if not inside(p, out_dir()):
        return False
    if sys.platform.startswith('win'):
        os.startfile(p)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', p])
    else:
        subprocess.Popen(['xdg-open', p])
    return True


def _slow(path, t0):
    """(2.14.3) Requests that keep the page waiting go into startup.log, so a slow start can be traced."""
    dt = time.time() - t0
    if dt > 1.5:
        print(f'slow request {str(path).split("?")[0]} {dt:.1f}s', flush=True)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _host_ok(self):
        host = (self.headers.get('Host') or '').lower()
        return host in (f'127.0.0.1:{PORT[0]}', f'localhost:{PORT[0]}')

    def _cookie_ok(self):
        for part in (self.headers.get('Cookie') or '').split(';'):
            k, _, v = part.strip().partition('=')
            if k == 'sl_token' and hmac.compare_digest(v, TOKEN):
                return True
        return False

    def _query_token_ok(self):
        from urllib.parse import parse_qs
        q = parse_qs(urlparse(self.path).query)
        return hmac.compare_digest((q.get('t') or [''])[0], TOKEN)

    def _authorized(self, need_header):
        if not self._host_ok():
            return False
        if not need_header and self._query_token_ok():      # drag-and-drop downloads carry the token in the URL
            return True
        if not self._cookie_ok():
            return False
        if need_header and not hmac.compare_digest(self.headers.get('X-Studio-Token', ''), TOKEN):
            return False
        return True

    def _deny(self):
        self.send_response(403)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(b)

    def _raw(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > MAX_UPLOAD:
            raise ValueError('upload too large')
        return self.rfile.read(n)

    def _body(self):
        if 'application/json' not in (self.headers.get('Content-Type') or ''):
            raise ValueError('json expected')
        return json.loads(self._raw() or b'{}')

    def _file(self, path, ctype=None):
        if not os.path.isfile(path):
            self.send_error(404)
            return
        size = os.path.getsize(path)
        ctype = ctype or mimetypes.guess_type(path)[0] or 'application/octet-stream'
        rng = self.headers.get('Range')
        start, end = 0, size - 1
        if rng and rng.startswith('bytes='):
            a, _, b = rng[6:].partition('-')
            start = int(a) if a else 0
            end = int(b) if b else size - 1
            self.send_response(206)
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        else:
            self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        with open(path, 'rb') as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 16, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def do_OPTIONS(self):
        self._deny()                     # no cross-origin access, ever

    def do_GET(self):
        t0 = time.time()
        try:
            return self._do_GET()
        finally:
            _slow(self.path, t0)

    def do_POST(self):
        t0 = time.time()
        try:
            return self._do_POST()
        finally:
            _slow(self.path, t0)

    def _do_GET(self):
        u = urlparse(self.path)
        p = u.path
        if not self._host_ok():
            return self._deny()
        if p in ('/', '/index.html'):
            with open(os.path.join(HERE, 'ui.html'), 'rb') as f:
                page = f.read().replace(b'__SL_TOKEN__', TOKEN.encode())
            prefs = json.dumps(load_settings().get('ui_prefs') or {}).replace('</', '<\\/')   # theme etc. from last time
            page = page.replace(b"'__SL_UIPREFS__'", prefs.encode())
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(page)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Set-Cookie', f'sl_token={TOKEN}; Path=/; HttpOnly; SameSite=Strict')
            self.end_headers()
            self.wfile.write(page)
            return
        if p != '/favicon.ico' and not self._authorized(need_header=p.startswith('/api/')):
            return self._deny()
        if p == '/favicon.ico':
            svg = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
                   b'<stop offset="0" stop-color="#7c5cff"/><stop offset="1" stop-color="#29d3b2"/></linearGradient></defs>'
                   b'<rect width="32" height="32" rx="8" fill="url(#g)"/></svg>')
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml')
            self.send_header('Content-Length', str(len(svg)))
            self.end_headers()
            self.wfile.write(svg)
            return
        if p == '/api/meta':
            return self._json(meta())
        if p == '/api/genremap':                         # (1.90) which genres sound closest to which
            from .genrematch import genre_map
            from . import styles as _sty
            return self._json(genre_map(_sty.STYLES, _sty.LABELS))
        if p.startswith('/api/job/'):
            j = JOBS.get(p.rsplit('/', 1)[1])
            if not j:
                return self._json({'error': 'no such job'}, 404)
            return self._json({k: v for k, v in j.items() if k != 'items'})
        if p == '/api/library':
            return self._json(library())
        if p == '/api/plugins':
            return self._json(plugin_state())
        if p == '/api/presets':
            os.makedirs(PRESETS, exist_ok=True)
            out = []
            for f in sorted(os.listdir(PRESETS)):
                if f.endswith('.json'):
                    with open(os.path.join(PRESETS, f)) as fh:
                        out.append(dict(name=f[:-5], options=json.load(fh)))
            return self._json(out)
        if p.startswith('/files/'):
            rel = unquote(p[len('/files/'):])
            full = os.path.realpath(os.path.join(out_dir(), rel))
            if not inside(full, out_dir()):
                return self._deny()
            return self._file(full)
        self.send_error(404)

    def _do_POST(self):
        p = urlparse(self.path).path
        if not self._authorized(need_header=True):
            return self._deny()
        try:
            body = {} if p.startswith('/api/upload/') else self._body()
        except ValueError as e:
            return self._json({'error': str(e)}, 400)
        return self._post(p, body)

    def _post(self, p, body):
        if p.startswith('/api/upload/'):
            from urllib.parse import parse_qs
            q = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
            try:
                raw = self._raw()
                if p == '/api/upload/reffile':          # MIDI / MusicXML / settings reference
                    from .refparse import analyze_file
                    try:
                        return self._json(analyze_file(q.get('name', ''), raw))
                    except ValueError:
                        raise
                    except Exception as e:
                        raise ValueError(f'could not read that file ({type(e).__name__})')
                if len(raw) % 4:
                    raise ValueError('bad audio data')
                pcm = np.frombuffer(raw, dtype='<f4')
                if not np.isfinite(pcm).all():
                    raise ValueError('bad audio data')
                if p == '/api/upload/reference':
                    from .analysis import analyze
                    sr_ = int(q.get('sr', 44100))
                    res = analyze(pcm, sr_)
                    try:                                  # its tonal balance, for 'match its tone' (1.80)
                        from .render import band_balance
                        from scipy.signal import resample_poly
                        xm = np.asarray(pcm, dtype=np.float64)
                        if sr_ != 44100:
                            xm = resample_poly(xm, 44100, sr_, axis=-1)
                        xs = xm if xm.ndim == 2 else np.vstack([xm, xm])
                        res['tone'] = [round(float(v), 1) for v in band_balance(xs)]
                        from .render import band_balance_quiet
                        tq = band_balance_quiet(xs)
                        if tq is not None:                # (1.86) its breakdown's balance too
                            res['tone_quiet'] = [round(float(v), 1) for v in tq]
                    except Exception:                     # noqa: BLE001 - a bonus
                        pass
                    try:                                  # the genres this sounds closest to (tempo, key, drum feel, sound)
                        from . import genrematch
                        from .styles import LABELS as _LABELS   # (a local 'STYLES' here broke every other endpoint)
                        x_ = np.asarray(pcm, dtype=np.float64)
                        genrematch.analyze_reference(x_, sr_, res)
                        res['genres'] = genrematch.suggest(res, STYLES, _LABELS, top=6)
                        res.pop('feels', None)
                    except Exception as e:                # suggestions are a bonus - the analysis still applies
                        res['genres_error'] = str(e)
                    return self._json(res)
                if p == '/api/upload/sound':
                    from . import usersounds
                    name = usersounds.save(q.get('kind', 'drums'), q.get('name', 'kick'), pcm, int(q.get('root', 60)),
                                           q.get('vtype', 'phrase'))
                    return self._json(dict(usersounds.listing(), saved=name, slots=usersounds.DRUM_SLOTS))
            except ValueError as e:
                return self._json({'error': str(e)}, 400)
            return self._deny()
        if p == '/api/project':
            try:
                return self._json(open_project(body.get('name'), body.get('settings')))
            except ValueError as e:
                return self._json({'error': str(e)}, 400)
        if p == '/api/notes':                             # song editor: the note timeline + volume lines
            try:
                from .api import song_notes
                return self._json(song_notes(body.get('options') or {}))
            except Exception as e:                       # noqa: BLE001 - shown in the editor, never crashes the app
                return self._json({'error': str(e)}, 400)
        if p == '/api/audition':                          # hear one sound / drum hit before rendering a song
            try:
                from .api import audition
                from .instruments import INSTRUMENTS, DRUMS
                inst, kit, voice = body.get('inst'), body.get('kit'), body.get('voice')
                if inst and not (inst in INSTRUMENTS or inst in DRUMS or str(inst).startswith(('sf:', 'real:', 'user:'))):
                    raise ValueError('unknown sound')
                if voice and voice not in ('kick', 'snare', 'clap', 'hats'):
                    raise ValueError('unknown drum voice')
                midi = body.get('midi')
                midi = None if midi is None else max(12, min(120, int(midi)))
                data = audition(inst=inst, role=str(body.get('role') or 'lead'), kit=kit, voice=voice, midi=midi,
                                dur=body.get('dur'), bpm=int(body.get('bpm') or 124))
            except Exception as e:                       # noqa: BLE001
                return self._json({'error': str(e)}, 400)
            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)
            return
        if p == '/api/generate':
            o = body.get('options', {})
            if isinstance(o, dict) and 'vst_rig' not in o:
                o['vst_rig'] = True                    # installed plugins are used automatically
            fresh = isinstance(o, dict) and 'avoid' not in o and body.get('section') is None
            if fresh:
                o['avoid'] = recent_avoid(o.get('style'))   # lean away from what your last songs in this genre used
            Options.from_dict(o)  # validate keys early
            n = max(1, min(8, int(body.get('count', 1))))
            preview = bool(body.get('preview', True))
            section = body.get('section')
            outputs = [x for x in (body.get('outputs') or ['mp3' if have_ffmpeg() else 'wav']) if isinstance(x, str)]
            if preview or section is not None:
                outputs = ['wav']
            items = []
            base = int(o.get('seed') or random.randrange(1, 10 ** 6))
            vary = body.get('vary_part')
            for i in range(n):
                if vary in ('drums', 'bass', 'chords', 'melody', 'harmony'):
                    # N versions of one part over the exact same song: same seed, only that part's seed changes
                    ps = dict(o.get('part_seeds') or {})
                    ps[vary] = random.randrange(1, 10 ** 6)
                    oi = dict(o, seed=base, part_seeds=ps)
                else:
                    oi = dict(o, seed=base + i if n > 1 else base)
                if fresh:                                # the same seed again (e.g. Full song after its preview) = the same song
                    k = (oi.get('style'), oi['seed'])
                    if k in SEED_AVOID:
                        oi['avoid'] = SEED_AVOID[k]
                    else:
                        SEED_AVOID[k] = oi['avoid']
                        if len(SEED_AVOID) > 500:
                            SEED_AVOID.pop(next(iter(SEED_AVOID)))
                items.append(dict(options=oi, outputs=outputs, preview=preview, section=section,
                                  loop=bool(body.get('loop')) and section is not None))
            return self._json({'job': submit(items)})
        if p == '/api/open' and body.get('path') == 'plugins':
            from .vsthost import PLUGIN_DIR
            os.makedirs(PLUGIN_DIR, exist_ok=True)
            open_dir(PLUGIN_DIR)
            return self._json({'ok': True})
        if p == '/api/vst':
            from . import vsthost
            out = dict(available=False, plugins=[], sounds=[], folder=vsthost.PLUGIN_DIR, python=sys.executable, real=[])
            for k, fn in (('available', vsthost.available), ('plugins', vsthost.find_plugins), ('sounds', vsthost.list_sounds),
                          ('real', lambda: real_insts(None))):
                try:                                     # one broken part (an odd plugin folder) never blanks the window
                    out[k] = fn()
                except Exception as e:
                    out.setdefault('errors', []).append(f'{k}: {e}')
            return self._json(out)
        if p == '/api/vst/install':
            from . import vsthost
            return self._json({'job': bg_job(lambda log: {'ok': vsthost.install(log)})})
        if p == '/api/vst/create':
            from . import vsthost
            path, name = str(body.get('path', '')), str(body.get('name', 'My sound'))[:60]
            existing = body.get('existing')
            return self._json({'job': bg_job(lambda log: vsthost.create_sound(path, name, existing))})
        if p == '/api/storage':                          # read / change the clean-up setting, with space used
            from . import storage
            st_ = load_settings()
            if body.get('mode') in storage.MODES or 'days' in body:
                cur = storage.policy(st_)
                if body.get('mode') in storage.MODES:
                    cur['mode'] = body['mode']
                if 'days' in body:
                    cur['days'] = body['days']
                st_['storage'] = storage.policy({'storage': cur})
                save_settings(st_)
            return self._json(dict(storage.policy(load_settings()), usage=storage.usage(out_dir()), modes=list(storage.MODES)))
        if p == '/api/storage/clean':
            from . import storage
            res = storage.clean(out_dir(), storage.policy(load_settings()))
            return self._json(dict(res, usage=storage.usage(out_dir())))
        if p == '/api/library/keep':                     # ⭐ Keep: this song is never trimmed or deleted
            from . import storage
            base = project_base(str(body.get('name', '')))
            if not base or not os.path.exists(storage.settings_path(out_dir(), base)):
                return self._json({'ok': False, 'error': 'song not found in the output folder'})
            return self._json({'ok': True, 'kept': storage.set_kept(out_dir(), base, bool(body.get('keep', True)))})
        if p == '/api/special/daisy':                    # Daisy Bell (1892) sung by a creepy computer voice
            from . import daisy

            def job(log):
                r = daisy.render(out_dir(), log=log, wind_down=bool(body.get('wind_down', True)),
                                 voice=str(body.get('voice', 'machine')))
                rel = lambda v: '/files/' + os.path.relpath(v, out_dir()).replace(os.sep, '/')
                r['urls'] = {k: rel(v) for k, v in r['files'].items()}
                r['folder'] = os.path.dirname(r['files']['wav'])
                return r
            return self._json({'job': bg_job(job)})
        if p == '/api/vst/scan':                         # orchestra detection: one plugin window, every instrument
            from . import vsthost
            path, prefix = str(body.get('path', '')), str(body.get('prefix', 'BBC'))[:12]
            return self._json({'job': bg_job(lambda log: vsthost.scan_orchestra(path, prefix, log))})
        if p == '/api/vst/rename':
            from . import vsthost
            return self._json(vsthost.rename_sound(str(body.get('id', '')), str(body.get('name', ''))))
        if p == '/api/vst/delete':
            from . import vsthost
            vsthost.delete_sound(str(body.get('id', '')))
            return self._json({'ok': True})
        if p == '/api/vststatus':
            from . import vsthost
            return self._json(dict(vsthost.PROBE_STATUS))
        if p == '/api/vstpacks':
            from . import vstpacks, vsthost
            st_ = load_settings()
            key = st_.get('vt_key') or ''
            return self._json(dict(vstpacks.status(), available=vsthost.available(),
                                   vt=dict(configured=bool(key), hint=('…' + key[-4:]) if key else '',
                                           require=bool(st_.get('vt_require', bool(key))))))
        if p == '/api/vstpacks/safety':
            import re as _re
            upd = {}
            if 'key' in body:
                k = str(body.get('key') or '').strip()
                if k and not _re.fullmatch(r'[0-9a-fA-F]{64}', k):
                    return self._json({'error': 'a VirusTotal API key is 64 letters and digits (0-9, a-f)'}, 400)
                upd['vt_key'] = k
            if 'require' in body:
                upd['vt_require'] = bool(body['require'])
            save_settings(upd)
            return self._json({'ok': True})
        if p == '/api/vstpacks/plan':
            from . import vstrigs
            style = str(body.get('style', ''))
            if style not in STYLES:
                return self._json({'error': 'unknown style'}, 400)
            return self._json(vstrigs.plan(style))
        if p == '/api/vstpacks/install':
            from . import vstpacks, vsthost, vstrigs
            ids = [str(i) for i in (body.get('ids') or []) if str(i) in vstpacks.BY_ID or vstpacks.installer_available(str(i))]
            if body.get('style') in STYLES:
                ids += [i for i in vstrigs.plan(body['style'])['missing_packs'] if i not in ids]

            def job(log):
                if not vsthost.available():
                    log('VST support (pedalboard) is not installed yet - installing it first ...')
                    if not vsthost.install(log):
                        raise RuntimeError('could not install VST support')
                st_ = load_settings()
                res = vstpacks.install_many(ids, log, vt_key=st_.get('vt_key') or None,
                                            require_vt=bool(st_.get('vt_require', bool(st_.get('vt_key')))))
                detected(refresh=True)
                vsthost.probe_all(log)
                return res
            return self._json({'job': bg_job(job)})
        if p == '/api/vstpacks/remove':
            from . import vstpacks, vstrigs
            if str(body.get('id')) not in vstpacks.BY_ID and str(body.get('id')) not in vstpacks.recorded():
                return self._json({'error': 'unknown pack'}, 400)
            r = vstpacks.remove(str(body['id']))
            detected(refresh=True)
            return self._json(r)
        if p == '/api/diagnostics':
            from . import diagnostics
            if body.get('synths'):
                return self._json({'text': diagnostics.synth_params()})
            if body.get('summary'):
                return self._json({'text': diagnostics.summary(JOBS, str(body.get('note', ''))[:4000])})
            return self._json({'text': diagnostics.build(JOBS, str(body.get('note', ''))[:4000]),
                               'name': 'studiolab-report-' + time.strftime('%Y%m%d-%H%M') + '.txt'})
        if p == '/api/window':
            mode = 'browser' if body.get('mode') == 'browser' else 'app'
            s_ = load_settings()
            s_['window'] = mode
            save_settings(s_)
            return self._json({'window': mode})
        if p == '/api/shortcut':
            from . import appwindow
            try:
                return self._json({'path': appwindow.make_shortcut()})
            except Exception as e:
                return self._json({'error': str(e)})
        if p == '/api/soundlib':
            from . import soundfont, samplelibs
            return self._json({'installed': soundfont.installed(), 'path': soundfont.library_path(), 'real': samplelibs.status()})
        if p == '/api/samplelibs/install':
            from . import samplelibs
            lib = str(body.get('id', ''))
            if lib not in samplelibs.LIB_ORDER:
                return self._json({'error': 'unknown library'})
            ref = {}

            def job(log):
                def prog(f):
                    j = JOBS.get(ref.get('id'))
                    if j:
                        j['progress'] = f
                samplelibs.install(lib, log, prog)
                return {'ok': True}
            ref['id'] = bg_job(job)
            return self._json({'job': ref['id']})
        if p == '/api/samplelibs/remove':
            from . import samplelibs
            lib = str(body.get('id', ''))
            if lib in samplelibs.LIB_ORDER:
                samplelibs.remove(lib)
            return self._json({'real': samplelibs.status()})
        if p == '/api/soundlib/install':
            from . import soundfont

            def job(log):
                soundfont.download(log)
                return {'ok': True}
            return self._json({'job': bg_job(job)})
        if p == '/api/vst/preview':
            from . import vsthost
            sid = str(body.get('id', ''))

            def job(log):
                from .dsp import write_wav
                a = vsthost.preview(sid)
                d = os.path.join(out_dir(), 'previews')
                os.makedirs(d, exist_ok=True)
                fn = os.path.join(d, f'vst_{re.sub(r"[^A-Za-z0-9_-]", "", sid)}_{int(time.time())}.wav')
                peak = float(np.max(np.abs(a))) or 1.0
                write_wav(fn, a / max(peak, 1.0))
                return {'url': '/files/' + os.path.relpath(fn, out_dir()).replace(os.sep, '/')}
            return self._json({'job': bg_job(job)})
        if p == '/api/open':
            target = body.get('path') or out_dir()
            if not os.path.isabs(target):
                target = os.path.join(out_dir(), target)
            return self._json({'ok': bool(open_path(target))})
        if p == '/api/settings':
            allowed = {k: body[k] for k in ('output_dir',) if isinstance(body.get(k), str) and body[k].strip()}
            if allowed.get('output_dir'):
                os.makedirs(allowed['output_dir'], exist_ok=True)
            save_settings(allowed)
            return self._json(meta())
        if p == '/api/presets':
            os.makedirs(PRESETS, exist_ok=True)
            name = ''.join(c for c in body.get('name', 'preset') if c.isalnum() or c in ' -_')[:60] or 'preset'
            with open(os.path.join(PRESETS, name + '.json'), 'w') as f:
                json.dump(body.get('options', {}), f, indent=2)
            return self._json({'ok': True})
        if p == '/api/meta':
            return self._json(meta())
        if p == '/api/genremap':                         # (1.90) which genres sound closest to which
            from .genrematch import genre_map
            from . import styles as _sty
            return self._json(genre_map(_sty.STYLES, _sty.LABELS))
        if p == '/api/plugins':
            upd = {k: body[k] for k in ('daws', 'os') if k in body}
            save_settings(upd)
            return self._json(plugin_state())
        if p == '/api/plugins/scan':
            res = detected(refresh=True)
            from . import vsthost
            threading.Thread(target=vsthost.probe_all, daemon=True).start()
            out = plugin_state()
            out['scan'] = dict(found=len(res['found']), other=len(res['other']), dirs=res['dirs'])
            return self._json(out)
        if p == '/api/fix':                              # (2.7) repair what breaks the genre, keep the rest of the song
            from .fitness import fix_options
            return self._json(fix_options(body.get('options') or {}))
        if p == '/api/rate':
            rs = load_ratings()
            rec = dict(options=body.get('options', {}), rating=1 if body.get('rating', 0) > 0 else -1, t=int(time.time()))
            if body.get('part') in ('drums', 'bass', 'chords', 'melody', 'harmony'):
                rec.update(part=body['part'], part_seed=body.get('part_seed'), inst=body.get('inst'))
            rs.append(rec)
            with open(RATINGS, 'w') as f:
                json.dump(rs[-500:], f)
            return self._json(taste())
        if p == '/api/uiprefs':                          # the app's own settings (theme, visualizer, window size ...)
            prefs = body.get('prefs')                    # kept in settings.json, so they survive a new port / profile
            if isinstance(prefs, dict):
                clean = {str(k)[:40]: str(v)[:20000] for k, v in list(prefs.items())[:100] if str(k).startswith('sl_')}
                win = body.get('window')
                upd = {'ui_prefs': clean}
                if isinstance(win, dict):
                    try:
                        w = {k: int(win[k]) for k in ('w', 'h', 'x', 'y') if k in win}
                        if 600 <= w.get('w', 0) <= 10000 and 400 <= w.get('h', 0) <= 10000:
                            upd['window_geom'] = w
                    except (TypeError, ValueError):
                        pass
                save_settings(upd)
            return self._json({'ok': True})
        if p == '/api/taste':
            return self._json(taste())
        if p == '/api/sounds':
            from . import usersounds
            if body.get('delete'):
                usersounds.delete(body.get('kind', ''), body.get('name', ''))
            return self._json(dict(usersounds.listing(), slots=usersounds.DRUM_SLOTS))
        if p == '/api/update/check':
            return self._json(updater.check())
        if p == '/api/update/apply':
            res = updater.apply()
            self._json(res)
            if res.get('ok'):
                threading.Timer(1.0, updater.restart).start()
            return
        self.send_error(404)


def start_server(port=8765):
    """Start the background workers and the local web server (serving in its own thread). Returns (server, url)."""
    from . import diagnostics
    diagnostics.capture()
    threading.Thread(target=worker, daemon=True).start()
    for delay, fn in ((20.0, startup_detect), (30.0, storage_loop)):   # (2.2.6) after the window has loaded
        t = threading.Timer(delay, fn)
        t.daemon = True
        t.start()
    for p in range(port, port + 20):
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', p), Handler)
            PORT[0] = p
            break
        except OSError:
            continue
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f'http://127.0.0.1:{srv.server_address[1]}/'


def run(port=8765, open_browser=True, window='auto'):
    srv, url = start_server(port)
    print(f'Studio Lab is running at {url}')
    if window == 'auto':
        window = load_settings().get('window', 'app')
    if open_browser and window == 'app':
        # its own app window; the web server runs in the background and stops when the window is closed
        from . import appwindow
        mode = appwindow.open_window(url, lambda: os._exit(0))
        print(f'   opened as: {mode}')
        if mode == 'webview':
            return
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        return
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
