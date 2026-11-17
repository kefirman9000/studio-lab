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


def _check_deps():
    missing = []
    for m in ('numpy', 'scipy'):
        try:
            __import__(m)
        except ImportError:
            missing.append(m)
    if missing:
        _fail('Studio Lab needs: ' + ' '.join(missing) + '\n'
              'Install them with:   python -m pip install ' + ' '.join(missing))


if __name__ == '__main__':
    _check_python()
    _check_deps()
    if len(sys.argv) > 1 and sys.argv[1] in ('generate', 'gen', 'cli'):
        from sgcore.cli import main
        main(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] in ('vsts', 'vst'):
        from sgcore.cli import vsts_main
        vsts_main(sys.argv[2:])
    else:
        from sgcore.app import run
        port = int(os.environ.get('STUDIOLAB_PORT', '8765'))
        run(port=port, open_browser='--no-browser' not in sys.argv,
            window='browser' if '--browser' in sys.argv else ('app' if '--app-window' in sys.argv else 'auto'))
