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
    import importlib.util
    for m in ('numpy', 'scipy'):                 # (2.13.3) only look for them - importing scipy here held up the window
        try:
            if importlib.util.find_spec(m) is None:
                missing.append(m)
        except Exception:
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
                elif line.startswith('STUDIOLAB_RESTART'):    # an update was installed: (2.9.7) restart the whole app -
                    _restart_app()                            # a fresh window (the same-window swap could hang)
                elif line:
                    tail[:] = (tail + [line])[-6:]
        def _restart_app():
            try:
                from sgcore import appwindow
                appwindow.say_splash('Updated - restarting Studio Lab…')
            except Exception:
                pass
            flags = (0x00000008 | 0x00000200) if os.name == 'nt' else 0     # DETACHED_PROCESS | NEW_PROCESS_GROUP
            try:
                from sgcore import appwindow as _aw
                _aw.clear_heartbeat()
            except Exception:
                pass
            env2 = dict(os.environ, STUDIOLAB_WAIT_PID=str(os.getpid()))   # (2.13.3) the new app waits for this one
            env2.pop('STUDIOLAB_CHILD', None)
            env2.pop('STUDIOLAB_PARENT', None)
            try:
                subprocess.Popen([sys.executable] + sys.argv, cwd=here, creationflags=flags, close_fds=True, env=env2,
                                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            finally:
                _quit()
        threading.Thread(target=read, daemon=True).start()   # (keeps reading for good: a full pipe stalls the engine)
        while not found:
            if p.poll() is not None:
                time.sleep(0.3)
                if not found:
                    raise RuntimeError((' | '.join(tail) or 'the engine stopped while loading') + ' (details: ' + logp + ')')
            if time.time() - t0 > 300:                     # (after an update the first start compiles everything
                raise RuntimeError('the engine is taking over 5 minutes to load - details are in ' + logp)   # anew)
            time.sleep(0.1)
        url = found[0]
        try:
            from sgcore import updater as _up              # (2.16) the new version started: update confirmed
            _up.update_started_ok()
        except Exception:
            pass
        return url

    def safe_boot(say):                                # (2.16) a just-installed update that can't start is rolled back
        try:                                           # and the previous version started instead
            return boot(say)
        except Exception as e:
            try:
                from sgcore import updater as _up
                if not _up.update_pending():
                    raise
                rb = _up.roll_back()
            except Exception:
                raise e
            say(f"The update to {rb.get('bad')} didn't start - going back to {rb.get('back_to')}…")
            try:
                for c in _CHILD:
                    c.kill()
            except Exception:
                pass
            return boot(say)
    return safe_boot


def _wait_for_old_app(port):
    """(2.13.3) After an update the old app starts the new one and then closes. Starting the new window while the old
    one (its web view helpers, its engine on the port) is still going away made the restart hang or come up blank -
    so wait until the old process has really gone, the port is free and the web view has let go."""
    import socket
    import time
    pid = int(os.environ.pop('STUDIOLAB_WAIT_PID', '0') or 0)
    if not pid:
        return
    t0 = time.time()
    if os.name == 'nt':
        try:
            import ctypes
            k = ctypes.windll.kernel32
            h = k.OpenProcess(0x00100000, False, pid)              # SYNCHRONIZE
            if h:
                k.WaitForSingleObject(h, 20000)
                k.CloseHandle(h)
        except Exception:
            pass
    else:
        while time.time() - t0 < 20:
            try:
                os.kill(pid, 0)
            except OSError:
                break
            time.sleep(0.2)
    while time.time() - t0 < 30:                                     # the old engine's port
        try:
            with socket.socket() as sk:
                sk.bind(('127.0.0.1', port))
            break
        except OSError:
            time.sleep(0.3)
    time.sleep(1.5)                                                  # the old web view's helper processes


def _guard_instance():
    """(2.14.2) Two Studio Lab windows share one web view profile, and a frozen earlier copy (a window that hung or
    never closed properly) makes the next start freeze too. So: if an earlier copy is still answering, bring it to the
    front instead of opening a second one; if it has stopped answering, close it (and its engine) first."""
    if os.name != 'nt':
        return
    import json
    import subprocess
    import time
    from sgcore import appwindow
    try:
        with open(appwindow.INSTANCE) as f:
            old = json.load(f)
    except Exception:
        old = None
    if old and old.get('pid') and old['pid'] != os.getpid() and old.get('ctime') and \
            appwindow.proc_ctime(old['pid']) == old['ctime']:             # the very same process is still running
        age = time.time() - float(old.get('t') or 0)
        if age < 25:                                                   # it is alive and answering: show it
            try:
                import ctypes
                u = ctypes.windll.user32
                h = u.FindWindowW(None, 'Studio Lab')
                if h:
                    u.ShowWindow(h, 9)                                 # SW_RESTORE
                    u.SetForegroundWindow(h)
                    os._exit(0)
            except Exception:
                pass
        else:                                                          # frozen: close it and everything it started
            subprocess.run(['taskkill', '/PID', str(old['pid']), '/T', '/F'], capture_output=True,
                           creationflags=0x08000000)
            time.sleep(2.0)                                            # (its web view helpers let go of the profile)
    appwindow.heartbeat(first=True)


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
    elif len(sys.argv) > 1 and sys.argv[1] == 'shortcuts':  # (2.9.3) Windows: (re)make the Start menu + desktop shortcuts
        from sgcore.winshortcut import make_shortcuts
        print('\n'.join(make_shortcuts(os.path.dirname(os.path.abspath(__file__)), force=True)) or 'Windows only')
    elif len(sys.argv) > 1 and sys.argv[1] in ('vsts', 'vst'):
        from sgcore.cli import vsts_main
        vsts_main(sys.argv[2:])
    else:
        port = int(os.environ.get('STUDIOLAB_PORT', '8765'))
        if '--serve' in sys.argv:                         # (2.2.3) the engine on its own, for the app window
            _serve(port)
        _wait_for_old_app(port)
        try:                                              # (2.9.3) Windows: Start menu + desktop shortcuts with the icon,
            from sgcore.winshortcut import ensure_shortcuts   # pinnable to the taskbar (once, in the background)
            ensure_shortcuts(os.path.dirname(os.path.abspath(__file__)))
        except Exception:
            pass
        if '--browser' not in sys.argv and '--no-browser' not in sys.argv and _window_setting() != 'browser':
            _guard_instance()                             # (2.14.2) never two windows / never behind a frozen one
            from sgcore import appwindow                  # the window opens at once with a loading screen
            if appwindow.splash_window(_engine_boot(port), _quit):
                appwindow.clear_heartbeat()
                _quit()
        from sgcore.app import run
        run(port=port, open_browser='--no-browser' not in sys.argv,
            window='browser' if '--browser' in sys.argv else ('app' if '--app-window' in sys.argv else 'auto'))
