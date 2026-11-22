"""Open Studio Lab as its own app window (no browser tabs, no address bar), and quit when that window closes.

Tried in order:
  1. pywebview, if it's installed (a native window)
  2. Microsoft Edge / Google Chrome / Brave / Chromium in "app mode" (--app): a plain window with only the page - Edge is
     part of Windows, so this works everywhere without installing anything
  3. your normal browser (a tab), if none of the above is available
"""
import os
import shutil
import subprocess
import sys
import threading
import webbrowser

from . import updater


def _candidates():
    if sys.platform == 'win32':
        pf = [os.environ.get(k) for k in ('ProgramFiles(x86)', 'ProgramFiles', 'LOCALAPPDATA')]
        rel = [r'Microsoft\Edge\Application\msedge.exe', r'Google\Chrome\Application\chrome.exe',
               r'BraveSoftware\Brave-Browser\Application\brave.exe', r'Chromium\Application\chrome.exe']
        return [os.path.join(b, r) for r in rel for b in pf if b]
    if sys.platform == 'darwin':
        return ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
                '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
                '/Applications/Chromium.app/Contents/MacOS/Chromium']
    return [shutil.which(x) for x in ('google-chrome', 'google-chrome-stable', 'microsoft-edge', 'chromium', 'chromium-browser',
                                      'brave-browser')]


def find_browser():
    for c in _candidates():
        if c and os.path.isfile(c):
            return c
    return None


def last_geometry():
    """The window's size and position from last time (the page reports it whenever the window is resized)."""
    try:
        import json
        with open(os.path.join(updater.ROOT, 'settings.json')) as f:
            g = json.load(f).get('window_geom') or {}
        w, h = int(g.get('w', 1440)), int(g.get('h', 920))
        x, y = g.get('x'), g.get('y')
        if not (900 <= w <= 10000 and 600 <= h <= 10000):
            w, h = 1440, 920
        pos = (int(x), int(y)) if x is not None and y is not None and -200 < int(x) < 8000 and -50 < int(y) < 5000 else None
        return w, h, pos
    except Exception:
        return 1440, 920, None


class Bridge:
    """(2.0) What the page can ask of the desktop window: window.pywebview.api.save(href) - a real "Save as" dialog for
    every export / download link, then the saved file shown in Explorer / Finder."""

    def __init__(self, base):
        self.base = base.rstrip('/')
        self.window = None

    def save(self, href, name=None):
        import re
        import shutil
        import urllib.parse
        import urllib.request
        import webview
        full = urllib.parse.urljoin(self.base + '/', href)
        if not full.startswith(self.base):
            return dict(ok=False, error='not a Studio Lab file')
        with urllib.request.urlopen(full) as r:
            cd = r.headers.get('Content-Disposition', '')
            m = re.search(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)", cd)
            fname = name or (urllib.parse.unquote(m.group(1)) if m else
                             urllib.parse.unquote(urllib.parse.urlparse(full).path.rsplit('/', 1)[-1]) or 'studio-lab-export')
            dest = self.window.create_file_dialog(webview.SAVE_DIALOG, directory=os.path.expanduser('~'), save_filename=fname)
            if not dest:
                return dict(ok=False, cancelled=True)
            dest = dest if isinstance(dest, str) else dest[0]
            with open(dest + '.part', 'wb') as f:
                shutil.copyfileobj(r, f, 1 << 20)
            os.replace(dest + '.part', dest)
        self.reveal(dest)
        return dict(ok=True, path=dest)

    def reveal(self, path):
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', path])
        except Exception:
            pass
        return True


SPLASH = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:#0d0f14;color:#e7e9ef;font:14px "Segoe UI Variable Text","Segoe UI",-apple-system,system-ui,sans-serif;
  display:flex;align-items:center;justify-content:center;overflow:hidden;user-select:none}
.box{display:flex;flex-direction:column;align-items:center;gap:18px}
.mark{width:64px;height:64px;border-radius:16px;background:conic-gradient(from 210deg,#7c5cff,#29d3b2,#4d8fd8,#7c5cff);
  animation:spin 2.4s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
h1{margin:0;font-size:22px;font-weight:650;letter-spacing:.02em}
.bars{display:flex;gap:4px;align-items:flex-end;height:26px}
.bars i{width:5px;border-radius:3px;background:#7c5cff;animation:eq 1s ease-in-out infinite}
.bars i:nth-child(2n){background:#29d3b2}
@keyframes eq{0%,100%{height:5px}50%{height:26px}}
#msg{color:#8a90a2;min-height:18px}
</style></head><body><div class="box"><div class="mark"></div><h1>Studio Lab</h1>
<div class="bars">%BARS%</div><div id="msg">Starting…</div><div id="sec" style="color:#5d6375;font-size:12px"></div></div>
<script>function say(m){document.getElementById('msg').textContent=m}
var t0=Date.now();setInterval(function(){var s=Math.round((Date.now()-t0)/1000);
document.getElementById('sec').textContent=s>2?s+' s':''},500);</script></body></html>""".replace(
    '%BARS%', ''.join(f'<i style="animation-delay:{i * 0.09:.2f}s"></i>' for i in range(9)))


WINDOW = {}          # the app window (for an in-place restart after an update)


def show_splash(msg):
    """(2.4.3) Back to the loading screen in the same window (an update restarting the engine)."""
    import json
    w = WINDOW.get('win')
    if w is None:
        return
    try:
        w.load_html(SPLASH)
        w.evaluate_js('say(%s)' % json.dumps(msg))
    except Exception:
        pass


def splash_window(boot, quit_app):
    """(2.1) Open the window at once with a loading screen, run boot(say) - the slow part: loading the sound engine and
    starting the server - behind it, then swap in the app. Returns False if there is no pywebview (the caller starts
    the usual way)."""
    try:
        import webview
    except ImportError:
        return False
    try:
        webview.settings['ALLOW_DOWNLOADS'] = True
        webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
    except Exception:
        pass
    w, h, pos = last_geometry()
    kw = dict(x=pos[0], y=pos[1]) if pos else {}
    bridge = Bridge('')
    try:
        win = webview.create_window('Studio Lab', html=SPLASH, width=w, height=h, min_size=(900, 600), js_api=bridge,
                                    background_color='#0d0f14', **kw)
    except TypeError:
        win = webview.create_window('Studio Lab', html=SPLASH, width=w, height=h, min_size=(900, 600), js_api=bridge, **kw)
    bridge.window = win
    WINDOW['win'] = win

    def go():
        import json

        def say(m):                                   # never wait on the window: a hung evaluate_js (pywebview on
            def _s():                                  # Windows) must not stop the start-up
                try:
                    win.evaluate_js('say(%s)' % json.dumps(str(m)))
                except Exception:
                    pass
            threading.Thread(target=_s, daemon=True).start()
        try:
            url = boot(say)
            bridge.base = url.split('?')[0]
            say('Opening…')
            win.load_url(url)
        except Exception as e:                            # show what went wrong instead of a window that never loads
            say('Studio Lab could not start: %s' % e)
    try:
        try:
            webview.start(go, private_mode=False)
        except TypeError:
            webview.start(go)
    except Exception:                                     # no usable web view (e.g. WebView2 missing): the usual way
        return False
    quit_app()
    return True


def open_window(url, quit_app):
    """Open the app window - the same size and place as last time. Returns 'webview' (blocks until closed), 'app' or
    'browser'."""
    w, h, pos = last_geometry()
    try:
        import webview  # pywebview (optional)
        try:
            webview.settings['ALLOW_DOWNLOADS'] = True          # export buttons save files like in a browser
            webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
        except Exception:
            pass
        kw = dict(x=pos[0], y=pos[1]) if pos else {}
        bridge = Bridge(url.split('?')[0])
        bridge.window = webview.create_window('Studio Lab', url, width=w, height=h, min_size=(900, 600), js_api=bridge, **kw)
        try:
            webview.start(private_mode=False)            # keep the page's own storage between launches
        except TypeError:                                 # (older pywebview)
            webview.start()
        quit_app()
        return 'webview'
    except ImportError:
        pass
    except Exception as e:
        print(f'   app window (pywebview) failed: {e}')
    exe = find_browser()
    if exe:
        profile = os.path.join(updater.ROOT, '.appwindow')       # its own profile -> its own window & taskbar entry
        try:
            args = [exe, f'--app={url}', f'--user-data-dir={profile}', f'--window-size={w},{h}',
                    '--no-first-run', '--no-default-browser-check', '--disable-features=Translate']
            if pos:
                args.insert(3, f'--window-position={pos[0]},{pos[1]}')
            p = subprocess.Popen(args,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            def watch():
                p.wait()
                quit_app()                                       # closing the window quits Studio Lab
            threading.Thread(target=watch, daemon=True).start()
            return 'app'
        except Exception as e:
            print(f'   app window ({os.path.basename(exe)}) failed: {e}')
    webbrowser.open(url)
    return 'browser'


def make_shortcut():
    """Shortcuts that start Studio Lab like an installed app, with no console window: one on the desktop and one in
    the Start menu (Windows) - right-click either one > "Pin to taskbar" (or pin it from the Start menu). With the
    native window (pywebview) the running window groups under the pinned icon. Returns the desktop shortcut path."""
    root = updater.ROOT
    script = os.path.join(root, 'studiolab.py')
    desk = os.path.join(os.path.expanduser('~'), 'Desktop')
    if sys.platform == 'win32':
        exe = sys.executable
        w = os.path.join(os.path.dirname(exe), 'pythonw.exe')
        target = w if os.path.isfile(w) else exe
        ico = os.path.join(root, 'installer', 'windows', 'studio-lab.ico')
        # the real Desktop / Start menu folders (the desktop is often moved into OneDrive)
        ps = ("$sh=New-Object -ComObject WScript.Shell;"
              "$d=[Environment]::GetFolderPath('Desktop');$m=[Environment]::GetFolderPath('Programs');"
              "foreach($f in @($d,$m)){ $s=$sh.CreateShortcut((Join-Path $f 'Studio Lab.lnk'));"
              "$s.TargetPath=$env:SL_EXE;$s.Arguments='\"'+$env:SL_SCRIPT+'\"';$s.WorkingDirectory=$env:SL_ROOT;"
              "if(Test-Path $env:SL_ICO){$s.IconLocation=$env:SL_ICO+',0'};$s.Description='Studio Lab - music generator';$s.Save() };"
              "Write-Output (Join-Path $d 'Studio Lab.lnk')")
        env = dict(os.environ, SL_EXE=target, SL_SCRIPT=script, SL_ROOT=root, SL_ICO=ico)
        r = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps], env=env, capture_output=True, text=True,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        lnk = (r.stdout or '').strip().splitlines()[-1] if (r.stdout or '').strip() else os.path.join(desk, 'Studio Lab.lnk')
        if r.returncode != 0 or not os.path.exists(lnk):
            raise RuntimeError('could not create the shortcut: ' + (r.stderr or '').strip()[-300:])
        return lnk
    if sys.platform == 'darwin':
        app = os.path.join(desk, 'Studio Lab.command')
        with open(app, 'w') as f:
            f.write(f'#!/bin/bash\ncd "{root}"\nnohup "{sys.executable}" studiolab.py >/dev/null 2>&1 &\n'
                    'osascript -e \'tell application "Terminal" to close front window\' >/dev/null 2>&1 &\n')
        os.chmod(app, 0o755)
        return app
    path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'applications', 'studiolab.desktop')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(f'[Desktop Entry]\nType=Application\nName=Studio Lab\nExec="{sys.executable}" "{script}"\nPath={root}\nTerminal=false\n')
    return path
