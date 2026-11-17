"""Run helper programs (ffmpeg, the plugin worker, git, Defender ...) without flashing a console window on Windows.

Pass **NOWIN to subprocess.run / Popen. On macOS and Linux it is empty."""
import subprocess
import sys

if sys.platform == 'win32':
    _si = subprocess.STARTUPINFO()
    _si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    _si.wShowWindow = 0                                    # SW_HIDE
    NOWIN = dict(creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000), startupinfo=_si)
else:
    NOWIN = {}
