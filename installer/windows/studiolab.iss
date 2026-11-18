; Studio Lab - Windows installer (Inno Setup 6).
; Built by .github/workflows/installers.yml:  ISCC /DAppVer=1.2.3 /DSrc=<staged app folder> studiolab.iss
; The staged folder holds the program plus runtime\python (a private Python with numpy, scipy, pedalboard,
; soundfile and lameenc already installed), so nothing else has to be downloaded or installed.

#ifndef AppVer
  #define AppVer "0.0.0"
#endif
#ifndef Src
  #define Src "..\..\build\win\app"
#endif

[Setup]
AppId={{6C1B7E52-3F0D-4E9A-9B57-5D2A8C41F0A7}
AppName=Studio Lab
AppVersion={#AppVer}
AppVerName=Studio Lab {#AppVer}
AppPublisher=Studio Lab
AppPublisherURL=https://github.com/kefirman9000/studio-lab
; per-user install: no admin password, and the app can update itself in place
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\Studio Lab
DisableProgramGroupPage=yes
DisableDirPage=auto
UsePreviousAppDir=yes
OutputDir=..\..\dist
OutputBaseFilename=StudioLab-Setup-{#AppVer}
SetupIconFile=studio-lab.ico
UninstallDisplayIcon={app}\studio-lab.ico
UninstallDisplayName=Studio Lab
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "Put a Studio Lab icon on the desktop"; GroupDescription: "Shortcuts:"

[Files]
Source: "{#Src}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "studio-lab.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Studio Lab"; Filename: "{app}\runtime\python\pythonw.exe"; Parameters: """{app}\studiolab.py"""; WorkingDir: "{app}"; IconFilename: "{app}\studio-lab.ico"; Comment: "Make music with Studio Lab"
Name: "{autodesktop}\Studio Lab"; Filename: "{app}\runtime\python\pythonw.exe"; Parameters: """{app}\studiolab.py"""; WorkingDir: "{app}"; IconFilename: "{app}\studio-lab.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\runtime\python\pythonw.exe"; Parameters: """{app}\studiolab.py"""; WorkingDir: "{app}"; Description: "Open Studio Lab now"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
; program files (including ones added by in-app updates). Your songs, presets, settings and sounds are left alone.
Type: filesandordirs; Name: "{app}\runtime"
Type: filesandordirs; Name: "{app}\sgcore"
Type: filesandordirs; Name: "{app}\tests"
Type: filesandordirs; Name: "{app}\tools"
Type: filesandordirs; Name: "{app}\docs"
Type: filesandordirs; Name: "{app}\installer"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\.appwindow"
Type: filesandordirs; Name: "{app}\.backup"
