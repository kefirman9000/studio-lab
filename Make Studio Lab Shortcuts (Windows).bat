@echo off
rem Puts Studio Lab in the Start menu and on the desktop, with its icon. Then right-click either one
rem (or the open Studio Lab window on the taskbar) and choose "Pin to taskbar".
cd /d "%~dp0"
set PY=
if exist "runtime\python\python.exe" set PY=runtime\python\python.exe
if not defined PY where py >nul 2>nul && set PY=py
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo Python was not found - run "Start Studio Lab (Windows).bat" first.
  pause
  exit /b 1
)
%PY% studiolab.py shortcuts
echo.
echo Done. Studio Lab is in your Start menu and on your desktop.
echo Right-click it ^(or the open Studio Lab window on the taskbar^) and choose "Pin to taskbar".
pause
