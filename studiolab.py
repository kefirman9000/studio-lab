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

    def watch_parent():                               # the window closed (or crashed): its end of the pipe closes
        try:
            while os.read(0, 1):
                pass
        except OSError:
            return                                    # (no pipe to watch: keep serving)
        os._exit(0)
    threading.Thread(target=watch_parent, daemon=True).start()
    _out('STUDIOLAB_SAY Loading the sound engine…')
    from sgcore import app
    _out('STUDIOLAB_SAY Starting the studio…')
    url = app.start_server(port)[1]
    _out('STUDIOLAB_URL ' + url)
    threading.Event().wait()


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
        env = dict(os.environ, STUDIOLAB_CHILD='1', PYTHONUNBUFFERED='1')
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), '--serve'], cwd=here, env=env,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             creationflags=0x08000000 if os.name == 'nt' else 0)
        _CHILD.append(p)
        url, tail = None, []
        for raw in iter(p.stdout.readline, b''):
            line = raw.decode('utf-8', 'replace').rstrip()
            if line.startswith('STUDIOLAB_SAY '):
                say(line[14:])
            elif line.startswith('STUDIOLAB_URL '):
                url = line[14:]
                break
            elif line:
                tail = (tail + [line])[-6:]
        if not url:
            raise RuntimeError(' | '.join(tail) or 'the engine stopped while loading')

        def drain():                                  # keep reading (a full pipe would stall the engine)
            for raw in iter(p.stdout.readline, b''):
                if raw.startswith(b'STUDIOLAB_RESTART'):  # an update was installed: start the whole app again
                    subprocess.Popen([sys.executable] + sys.argv, cwd=here,
                                     creationflags=0x08000000 if os.name == 'nt' else 0)
                    _quit()
        threading.Thread(target=drain, daemon=True).start()
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
