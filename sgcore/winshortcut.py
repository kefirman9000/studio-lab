"""(2.9.3) Windows: make Studio Lab a normal program - a Start menu and a desktop shortcut with the Studio Lab icon,
carrying the same taskbar identity (AppUserModelID 'StudioLab.App') as the app window, so you can pin it to the
taskbar and the pinned icon and the open window are ONE taskbar button with the Studio Lab icon (not 'Python').

The installer already makes these. This also covers a Studio Lab run from a downloaded folder (Start Studio Lab
(Windows).bat) or an older install that was only ever updated in place. It runs once, in the background, at start-up.
"""
import base64
import os
import subprocess
import sys
import threading

AUMID = 'StudioLab.App'
VERSION = '1'                           # bump to remake everyone's shortcuts

_CS = r'''
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
using System.Text;
[ComImport, Guid("00021401-0000-0000-C000-000000000046")] class SLCShellLink {}
[ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("000214F9-0000-0000-C000-000000000046")]
interface SLIShellLinkW {
  void GetPath([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder f, int c, IntPtr fd, uint fl);
  void GetIDList(out IntPtr p); void SetIDList(IntPtr p);
  void GetDescription([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder s, int c);
  void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string s);
  void GetWorkingDirectory([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder s, int c);
  void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string s);
  void GetArguments([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder s, int c);
  void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string s);
  void GetHotkey(out short h); void SetHotkey(short h);
  void GetShowCmd(out int c); void SetShowCmd(int c);
  void GetIconLocation([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder s, int c, out int i);
  void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string s, int i);
  void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string s, uint r);
  void Resolve(IntPtr h, uint f);
  void SetPath([MarshalAs(UnmanagedType.LPWStr)] string s);
}
[StructLayout(LayoutKind.Sequential, Pack = 4)] struct SLPropertyKey { public Guid fmtid; public uint pid; }
[StructLayout(LayoutKind.Explicit)] struct SLPropVariant { [FieldOffset(0)] public ushort vt; [FieldOffset(8)] public IntPtr p; }
[ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
interface SLIPropertyStore {
  void GetCount(out uint c); void GetAt(uint i, out SLPropertyKey k);
  void GetValue(ref SLPropertyKey k, out SLPropVariant v);
  void SetValue(ref SLPropertyKey k, ref SLPropVariant v); void Commit();
}
public static class StudioLabShortcut {
  public static void Make(string lnk, string target, string args, string dir, string icon, string aumid) {
    var link = (SLIShellLinkW)new SLCShellLink();
    link.SetPath(target); link.SetArguments(args); link.SetWorkingDirectory(dir);
    link.SetIconLocation(icon, 0); link.SetDescription("Make music with Studio Lab");
    var ps = (SLIPropertyStore)link;
    var key = new SLPropertyKey { fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"), pid = 5 };
    var pv = new SLPropVariant { vt = 31, p = Marshal.StringToCoTaskMemUni(aumid) };
    ps.SetValue(ref key, ref pv); ps.Commit();
    ((IPersistFile)link).Save(lnk, true);
    Marshal.FreeCoTaskMem(pv.p);
  }
}
'''


def _q(s):
    return "'" + str(s).replace("'", "''") + "'"


def _target(root):
    """What the shortcut starts: the installer's StudioLab.exe if there is one, else this Python's windowless
    pythonw.exe running studiolab.py."""
    exe = os.path.join(root, 'StudioLab.exe')
    if os.path.isfile(exe):
        return exe, ''
    d = os.path.dirname(sys.executable)
    pyw = os.path.join(d, 'pythonw.exe')
    return (pyw if os.path.isfile(pyw) else sys.executable), '"' + os.path.join(root, 'studiolab.py') + '"'


def _icon(root):
    for p in (os.path.join(root, 'studio-lab.ico'), os.path.join(root, 'installer', 'windows', 'studio-lab.ico')):
        if os.path.isfile(p):
            return p
    return _target(root)[0]


def _places():
    start = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Studio Lab.lnk')
    try:
        import ctypes
        from ctypes import wintypes
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buf)    # CSIDL_DESKTOPDIRECTORY (OneDrive-aware)
        desk = os.path.join(buf.value, 'Studio Lab.lnk')
    except Exception:                                                        # noqa: BLE001
        desk = os.path.join(os.path.expanduser('~'), 'Desktop', 'Studio Lab.lnk')
    return start, desk


def make_shortcuts(root, desktop=True, force=False):
    """Create / refresh the shortcuts. Returns the paths made (or raises)."""
    if os.name != 'nt':
        return []
    target, args = _target(root)
    icon = _icon(root)
    start, desk = _places()
    want = [start] + ([desk] if desktop else [])
    calls = '\n'.join(f'[StudioLabShortcut]::Make({_q(p)}, {_q(target)}, {_q(args)}, {_q(root)}, {_q(icon)}, {_q(AUMID)})'
                      for p in want)
    ps = "$ErrorActionPreference = 'Stop'\nAdd-Type -TypeDefinition @'\n" + _CS + "\n'@\n" + calls + '\n'
    enc = base64.b64encode(ps.encode('utf-16-le')).decode('ascii')
    subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden',
                    '-EncodedCommand', enc], check=True, timeout=120, capture_output=True,
                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    return want


def ensure_shortcuts(root):
    """Once per computer (per shortcut version): make the Start menu shortcut (and a desktop one the first time), in
    the background. An install made by the Studio Lab installer already has them and is left alone."""
    if os.name != 'nt' or os.environ.get('STUDIOLAB_NO_SHORTCUTS'):
        return
    marker = os.path.join(root, '.appwindow', 'shortcuts_v' + VERSION)
    start, desk = _places()
    if os.path.isfile(marker):
        return
    if os.path.isfile(os.path.join(root, 'StudioLab.exe')) and os.path.isfile(start):
        return                                                               # (the installer's own shortcuts)

    def work():
        try:
            first = not os.path.isfile(desk)
            make_shortcuts(root, desktop=first)
            os.makedirs(os.path.dirname(marker), exist_ok=True)
            with open(marker, 'w') as f:
                f.write('ok\n')
        except Exception:                                                    # noqa: BLE001 - never stop the app over this
            pass
    threading.Thread(target=work, daemon=True).start()
