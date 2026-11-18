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


def open_window(url, quit_app):
    """Open the app window - the same size and place as last time. Returns 'webview' (blocks until closed), 'app' or
    'browser'."""
    w, h, pos = last_geometry()
    try:
        import webview  # pywebview (optional)
        kw = dict(x=pos[0], y=pos[1]) if pos else {}
        webview.create_window('Studio Lab', url, width=w, height=h, min_size=(900, 600), **kw)
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
    """A desktop shortcut that starts Studio Lab with no console window. Returns the shortcut path."""
    root = updater.ROOT
    script = os.path.join(root, 'studiolab.py')
    desk = os.path.join(os.path.expanduser('~'), 'Desktop')
    if sys.platform == 'win32':
        exe = sys.executable
        w = os.path.join(os.path.dirname(exe), 'pythonw.exe')
        target = w if os.path.isfile(w) else exe
        lnk = os.path.join(desk, 'Studio Lab.lnk')
        ico = os.path.join(root, 'sgcore', 'icon.ico')
        ps = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:SL_LNK);"
              "$s.TargetPath=$env:SL_EXE;$s.Arguments='\"'+$env:SL_SCRIPT+'\"';$s.WorkingDirectory=$env:SL_ROOT;"
              "if(Test-Path $env:SL_ICO){$s.IconLocation=$env:SL_ICO};$s.Description='Studio Lab';$s.Save()")
        env = dict(os.environ, SL_LNK=lnk, SL_EXE=target, SL_SCRIPT=script, SL_ROOT=root, SL_ICO=ico)
        r = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps], env=env, capture_output=True, text=True,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
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
