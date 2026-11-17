@echo off
cd /d "%~dp0"
set PY=
where py >nul 2>nul && set PY=py
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY goto nopython
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>nul || goto oldpython
%PY% -c "import numpy, scipy" 2>nul || %PY% -m pip install --user -r requirements.txt
rem Start with no console window (pythonw); Studio Lab opens in its own app window.
where pyw >nul 2>nul && (start "" pyw studiolab.py & exit /b)
where pythonw >nul 2>nul && (start "" pythonw studiolab.py & exit /b)
%PY% studiolab.py
pause
exit /b

:nopython
echo.
echo  Studio Lab needs Python 3.9 or newer, and Python was not found.
echo  Download it from https://www.python.org/downloads/
echo  (tick "Add python.exe to PATH" in the installer), then run this again.
echo.
pause
exit /b 1

:oldpython
echo.
echo  Studio Lab needs Python 3.9 or newer. This computer has:
%PY% --version
echo  Download a newer one from https://www.python.org/downloads/ and run this again.
echo.
pause
exit /b 1
