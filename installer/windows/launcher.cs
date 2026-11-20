// StudioLab.exe - the program you pin to the taskbar. It starts Studio Lab with the private Python that the installer
// put next to it (runtime\python\pythonw.exe, no console window), passes on any arguments, and exits. The app window
// uses the same taskbar identity (AppUserModelID "StudioLab.App") as the Start menu / desktop shortcuts, so the
// pinned icon and the running window are one taskbar button. Built by .github/workflows/installers.yml with the C#
// compiler that ships with Windows (.NET Framework 4).
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;

[assembly: System.Reflection.AssemblyTitle("Studio Lab")]
[assembly: System.Reflection.AssemblyProduct("Studio Lab")]

static class Launcher
{
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    static extern int MessageBoxW(IntPtr h, string text, string caption, uint type);

    [STAThread]
    static int Main(string[] args)
    {
        string dir = AppDomain.CurrentDomain.BaseDirectory;
        string py = Path.Combine(dir, "runtime", "python", "pythonw.exe");
        string script = Path.Combine(dir, "studiolab.py");
        if (!File.Exists(py) || !File.Exists(script))
        {
            MessageBoxW(IntPtr.Zero, "Studio Lab's files are missing next to StudioLab.exe.\nPlease reinstall Studio Lab.",
                        "Studio Lab", 0x10);
            return 1;
        }
        string rest = "";
        foreach (string a in args)
            rest += " \"" + a.Replace("\"", "\\\"") + "\"";
        var psi = new ProcessStartInfo(py, "\"" + script + "\"" + rest);
        psi.WorkingDirectory = dir;
        psi.UseShellExecute = false;
        psi.EnvironmentVariables["STUDIOLAB_LAUNCHER"] = "1";
        Process.Start(psi);
        return 0;
    }
}
