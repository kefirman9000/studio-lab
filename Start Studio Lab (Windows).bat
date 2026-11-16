@echo off
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% -c "import numpy, scipy" 2>nul || %PY% -m pip install --user -r requirements.txt
rem Start with no console window (pythonw); Studio Lab opens in its own app window.
where pyw >nul 2>nul && (start "" pyw studiolab.py & exit /b)
where pythonw >nul 2>nul && (start "" pythonw studiolab.py & exit /b)
%PY% studiolab.py
pause
