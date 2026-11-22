#!/usr/bin/env python3
"""Studio Lab - run without arguments to open the app in its own window (--browser: in a browser tab).
   Command line:  python studiolab.py generate --help
                  python studiolab.py vsts --help"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _fail(msg):
    """Show a startup problem even when there is no console (pythonw on Windows starts without one)."""
    print(msg)
    if os.name == 'nt' and not (sys.stdout and sys.stdout.isatty()):
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, msg, 'Studio Lab', 0x10)
        except Exception:
            pass
    elif sys.stdin and sys.stdin.isatty():
        input('Press Enter to close...')
    sys.exit(1)


def _check_python():
    if sys.version_info < (3, 9):
        _fail('Studio Lab needs Python 3.9 or newer (this is %d.%d).\n'
              'Download a newer one from https://www.python.org/downloads/' % sys.version_info[:2])


def _importable(m):
    try:
        __import__(m)
        return True
    except ImportError:
        return False


def _check_deps():
    missing = []
    for m in ('numpy', 'scipy'):
        try:
            __import__(m)
        except ImportError:
            missing.append(m)
    here = os.path.dirname(os.path.abspath(__file__))
    bundled = os.path.isdir(os.path.join(here, 'runtime')) or '.app/Contents/Resources' in sys.executable
    if missing and bundled:                  # installed app: an update needs a new package - fetch it once, quietly
        import subprocess
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '-q', '-r',
                            os.path.join(here, 'requirements.txt')], timeout=600,
                           creationflags=0x08000000 if os.name == 'nt' else 0)
            missing = [m for m in missing if not _importable(m)]
        except Exception:
            pass
    if missing:
        _fail('Studio Lab needs: ' + ' '.join(missing) + '\n'
              'Install them with:   python -m pip install ' + ' '.join(missing))


def _taskbar_identity():
    """Windows: the app window shows under the same taskbar button as the pinned StudioLab.exe / its shortcuts
    (they carry the same AppUserModelID), instead of as a separate 'Python' button."""
    if os.name == 'nt':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('StudioLab.App')
        except Exception:
            pass


_CHILD = []


def _out(line):
    """A line to the window process (works under pythonw too, where sys.stdout can be None)."""
    try:
        os.write(1, (line + '\n').encode('utf-8', 'replace'))
    except OSError:
        pass


def _serve(port):
    """The engine process: load everything, start the server, tell the window where it is, then serve until the
    window goes away (its end of our stdin closes)."""
    import threading
    for what, mod in (('numpy', 'numpy'), ('scipy', 'scipy.signal'), ('the instruments', 'sgcore.instruments'),
                      ('the genres', 'sgcore.styles'), ('the composer', 'sgcore.compose'), ('the studio', 'sgcore.app')):
        _out('STUDIOLAB_SAY Loading ' + what + '…')
        __import__(mod)
    from sgcore import app
    _out('STUDIOLAB_SAY Starting the studio…')
    url = app.start_server(port)[1]
    _out('STUDIOLAB_URL ' + url)
    threading.Thread(target=_watch_window, daemon=True).start()
    threading.Event().wait()


def _watch_window():
    """Close the engine when the window's process ends. (2.2.6: no stdin pipe - on Windows a thread waiting on a
    pipe blocks other threads touching it, which froze 'import numpy'.)"""
    pid = int(os.environ.get('STUDIOLAB_PARENT') or 0)
    if not pid:
        return
    if os.name == 'nt':
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x00100000, False, pid)        # SYNCHRONIZE
        if h:
            k.WaitForSingleObject(h, 0xFFFFFFFF)
            os._exit(0)
        return
    import time
    while os.getppid() == pid:
        time.sleep(2)
    os._exit(0)


def _quit():
    for p in _CHILD:
        try:
            p.kill()
        except Exception:
            pass
    os._exit(0)


def _engine_boot(port):
    """(2.2.3) Start the engine as its own process, so the window stays responsive while it loads (and while songs
    render): Python runs one thing at a time per process, and the engine's loading / rendering used to hold up the
    window until Windows called it 'Not responding'."""
    def boot(say):
        import subprocess
        import threading
        here = os.path.dirname(os.path.abspath(__file__))
        env = dict(os.environ, STUDIOLAB_CHILD='1', PYTHONUNBUFFERED='1', STUDIOLAB_PARENT=str(os.getpid()))
        say('Starting the sound engine…')
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), '--serve'], cwd=here, env=env,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             creationflags=0x08000000 if os.name == 'nt' else 0)
        _CHILD.append(p)
        logp = os.path.join(here, 'startup.log')
        try:
            log = open(logp, 'w', encoding='utf-8')
        except OSError:
            log = None
        found, tail = [], []
        import time
        t0 = time.time()

        def read():
            for raw in iter(p.stdout.readline, b''):
                line = raw.decode('utf-8', 'replace').rstrip()
                if log:
                    try:
                        log.write('[%6.1fs] %s\n' % (time.time() - t0, line))
                        log.flush()
                    except Exception:
                        pass
                if line.startswith('STUDIOLAB_SAY '):
                    say(line[14:])
                elif line.startswith('STUDIOLAB_URL ') and not found:
                    found.append(line[14:])
                elif line.startswith('STUDIOLAB_RESTART'):    # an update was installed: a new engine, same window
                    threading.Thread(target=_swap_engine, daemon=True).start()
                elif line:
                    tail[:] = (tail + [line])[-6:]
        def _swap_engine():                           # (2.4.3) the updated engine starts behind the loading screen,
            from sgcore import appwindow                  # then the same window loads it - no closing and reopening
            appwindow.show_splash('Updating… starting the new version')
            time.sleep(0.6)                               # (the old engine lets go of its port)
            try:
                new_url = boot(lambda m: appwindow.show_splash(m))
                w = appwindow.WINDOW.get('win')
                if w is not None:
                    w.load_url(new_url)
            except Exception as e:                        # the new engine didn't start: say so, then restart fully
                appwindow.show_splash('Restarting Studio Lab… (%s)' % e)
                subprocess.Popen([sys.executable] + sys.argv, cwd=here, creationflags=0x08000000 if os.name == 'nt' else 0)
                _quit()
        threading.Thread(target=read, daemon=True).start()   # (keeps reading for good: a full pipe stalls the engine)
        while not found:
            if p.poll() is not None:
                time.sleep(0.3)
                if not found:
                    raise RuntimeError((' | '.join(tail) or 'the engine stopped while loading') + ' (details: ' + logp + ')')
            if time.time() - t0 > 120:
                raise RuntimeError('the engine is taking over 2 minutes to load - details are in ' + logp)
            time.sleep(0.1)
        url = found[0]

        return url
    return boot


def _window_setting():
    try:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')) as f:
            return json.load(f).get('window', 'app')
    except Exception:
        return 'app'


if __name__ == '__main__':
    _taskbar_identity()
    _check_python()
    _check_deps()
    if len(sys.argv) > 1 and sys.argv[1] in ('generate', 'gen', 'cli'):
        from sgcore.cli import main
        main(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == 'daisy':      # Daisy Bell (1892) sung by a creepy computer voice
        from sgcore import daisy
        voice = 'deep' if '--deep' in sys.argv else 'machine'          # python studiolab.py daisy [--deep] [folder]
        rest = [a for a in sys.argv[2:] if not a.startswith('--')]
        out = rest[0] if rest else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'songs')
        print(daisy.render(out, voice=voice)['files'])
    elif len(sys.argv) > 1 and sys.argv[1] in ('vsts', 'vst'):
        from sgcore.cli import vsts_main
        vsts_main(sys.argv[2:])
    else:
        port = int(os.environ.get('STUDIOLAB_PORT', '8765'))
        if '--serve' in sys.argv:                         # (2.2.3) the engine on its own, for the app window
            _serve(port)
        if '--browser' not in sys.argv and '--no-browser' not in sys.argv and _window_setting() != 'browser':
            from sgcore import appwindow                  # the window opens at once with a loading screen
            if appwindow.splash_window(_engine_boot(port), _quit):
                _quit()
        from sgcore.app import run
        run(port=port, open_browser='--no-browser' not in sys.argv,
            window='browser' if '--browser' in sys.argv else ('app' if '--app-window' in sys.argv else 'auto'))
