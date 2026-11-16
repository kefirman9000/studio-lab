"""Local web app: a tiny HTTP server (standard library only) + a single-page UI that opens in your browser."""
import hmac
import json
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

from . import updater, plugins
from .api import generate, have_ffmpeg
from .compose import Options, MOODS, SCALES, NOTE_NAMES, FUSION_PARTS, PART_LABELS
from .instruments import ROLE_CHOICES, INSTRUMENT_INFO, KITS
from .styles import STYLES, CATEGORIES, label

ROOT = updater.ROOT
HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = os.path.join(ROOT, 'settings.json')
PRESETS = os.path.join(ROOT, 'presets')


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


def plugin_prefs():
    st = load_settings()
    return dict(owned=st.get('plugins_owned', []), daws=st.get('daws') or ['lmms', 'waveform'],
                os=st.get('os') or host_os(), found=st.get('plugins_found', {}))


def plugin_state():
    pr = plugin_prefs()
    cat = []
    for p in plugins.CATALOG:
        cat.append(dict(id=p['id'], name=p['name'], maker=p['maker'], url=p['url'], free=p['free'], cats=p['cats'], tip=p['tip'],
                        formats=pr['found'].get(p['id']) or p['formats'], owned=p['id'] in pr['owned'],
                        installed=p['id'] in pr['found'], works=plugins.works_in(p, pr['daws'], pr['os'], pr['found'].get(p['id']))))
    st = load_settings()
    return dict(catalog=cat, daws=pr['daws'], os=pr['os'], host_os=host_os(), other=st.get('plugins_other', []),
                scanned=st.get('plugins_scanned_dirs', []))


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
    for r in rs:
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
                liked=sorted([k for k, v in styles.items() if v > 0], key=lambda k: -styles[k])[:5])


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
                                prefs=plugin_prefs(), section=item.get('section'))
                info['options'] = item['options']
                rel = lambda v: '/files/' + os.path.relpath(v, out_dir()).replace(os.sep, '/')
                info['urls'] = {k: rel(v) for k, v in info['files'].items() if k != 'waveform' and isinstance(v, str) and os.path.isfile(v)}
                info['part_urls'] = {k: rel(v) for k, v in (info.get('parts') or {}).items()}
                info.pop('parts', None)
                info['id'] = uuid.uuid4().hex[:8]
                job['results'].append(info)
            job['status'] = 'done'
        except Exception as e:
            job['status'] = 'error'
            job['error'] = str(e)
            job['log'].append(traceback.format_exc())
        job['progress'] = 1.0
        WORK.task_done()


def submit(items):
    jid = uuid.uuid4().hex[:10]
    JOBS[jid] = dict(id=jid, status='queued', progress=0.0, log=[], results=[], items=items, error=None, current=0)
    WORK.put(JOBS[jid])
    return jid


def user_insts():
    from . import usersounds
    return [dict(id='user:' + n, name='My sound: ' + n) for n in usersounds.listing()['inst']]


def meta():
    by_cat = {c: [] for c in CATEGORIES}
    for k, v in STYLES.items():
        by_cat[v['category']].append(dict(id=k, name=label(k), desc=v['desc'], bpm=v['bpm']))
    return dict(
        version=updater.local_version(), repo=updater.repo(), ffmpeg=have_ffmpeg(), output_dir=out_dir(),
        categories=by_cat, moods=list(MOODS), scales=list(SCALES), keys=NOTE_NAMES,
        roles={r: [dict(id=i, name=INSTRUMENT_INFO.get(i, i)) for i in lst] + user_insts() for r, lst in ROLE_CHOICES.items()},
        kits=list(KITS), parts=[dict(id=p, name=PART_LABELS[p]) for p in FUSION_PARTS],
        labels={k: label(k) for k in STYLES},
        style_defaults={k: {t['layer']: t['inst'] for t in v['tracks'] if t['layer'] in ROLE_CHOICES} for k, v in STYLES.items()},
    )


def library():
    items = []
    d = out_dir()
    for f in sorted(os.listdir(d), key=lambda x: os.path.getmtime(os.path.join(d, x)), reverse=True):
        if f.endswith('_settings.json'):
            try:
                with open(os.path.join(d, f)) as fh:
                    s = json.load(fh)
                base = f[:-len('_settings.json')]
                files = {}
                for ext, k in (('.mp3', 'mp3'), ('.wav', 'wav'), ('.mid', 'midi'), ('.mmp', 'lmms')):
                    if os.path.exists(os.path.join(d, base + ext)):
                        files[k] = '/files/' + base + ext
                wf = os.path.join(d, base + '_waveform')
                info = s.get('info', {})
                info['files'] = {'folder': wf if os.path.isdir(wf) else d}
                items.append(dict(title=base, info=info, options=s.get('options', {}), urls=files))
            except Exception:
                pass
        if len(items) >= 60:
            break
    return items


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
        u = urlparse(self.path)
        p = u.path
        if not self._host_ok():
            return self._deny()
        if p in ('/', '/index.html'):
            with open(os.path.join(HERE, 'ui.html'), 'rb') as f:
                page = f.read().replace(b'__SL_TOKEN__', TOKEN.encode())
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

    def do_POST(self):
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
            import numpy as np
            q = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
            try:
                raw = self._raw()
                if len(raw) % 4:
                    raise ValueError('bad audio data')
                pcm = np.frombuffer(raw, dtype='<f4')
                if not np.isfinite(pcm).all():
                    raise ValueError('bad audio data')
                if p == '/api/upload/reference':
                    from .analysis import analyze
                    return self._json(analyze(pcm, int(q.get('sr', 44100))))
                if p == '/api/upload/sound':
                    from . import usersounds
                    name = usersounds.save(q.get('kind', 'drums'), q.get('name', 'kick'), pcm, int(q.get('root', 60)))
                    return self._json(dict(usersounds.listing(), saved=name, slots=usersounds.DRUM_SLOTS))
            except ValueError as e:
                return self._json({'error': str(e)}, 400)
            return self._deny()
        if p == '/api/generate':
            o = body.get('options', {})
            Options.from_dict(o)  # validate keys early
            n = max(1, min(8, int(body.get('count', 1))))
            preview = bool(body.get('preview', True))
            section = body.get('section')
            outputs = [x for x in (body.get('outputs') or ['mp3' if have_ffmpeg() else 'wav']) if isinstance(x, str)]
            if preview or section is not None:
                outputs = ['wav']
            items = []
            base = int(o.get('seed') or random.randrange(1, 10 ** 6))
            for i in range(n):
                oi = dict(o, seed=base + i if n > 1 else base)
                items.append(dict(options=oi, outputs=outputs, preview=preview, section=section))
            return self._json({'job': submit(items)})
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
        if p == '/api/plugins':
            upd = {k: body[k] for k in ('plugins_owned', 'daws', 'os') if k in body}
            save_settings(upd)
            return self._json(plugin_state())
        if p == '/api/plugins/scan':
            res = plugins.scan(body.get('extra_dirs') or [])
            st = load_settings()
            owned = sorted(set(st.get('plugins_owned', [])) | set(res['found']))
            save_settings(dict(plugins_found=res['found'], plugins_other=res['other'], plugins_scanned_dirs=res['dirs'],
                               plugins_owned=owned))
            out = plugin_state()
            out['scan'] = dict(found=len(res['found']), other=len(res['other']), dirs=res['dirs'])
            return self._json(out)
        if p == '/api/rate':
            rs = load_ratings()
            rs.append(dict(options=body.get('options', {}), rating=1 if body.get('rating', 0) > 0 else -1, t=int(time.time())))
            with open(RATINGS, 'w') as f:
                json.dump(rs[-500:], f)
            return self._json(taste())
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


def run(port=8765, open_browser=True):
    threading.Thread(target=worker, daemon=True).start()
    for p in range(port, port + 20):
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', p), Handler)
            PORT[0] = p
            break
        except OSError:
            continue
    url = f'http://127.0.0.1:{srv.server_address[1]}/'
    print(f'Studio Lab is running at {url}  (close this window to quit)')
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
