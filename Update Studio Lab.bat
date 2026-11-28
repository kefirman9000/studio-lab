@echo off
rem Update Studio Lab - works even when Studio Lab itself won't open.
rem Put this file in your Studio Lab folder (where StudioLab.exe / studiolab.py are) and double-click it.
rem It downloads the latest Studio Lab from GitHub and copies the program files over this folder.
rem Your songs, presets, settings, sounds, plugins and the bundled Python are never touched, and nothing is deleted.
title Update Studio Lab
cd /d "%~dp0"
if not exist "studiolab.py" (
  echo This file has to be in your Studio Lab folder - the one with studiolab.py and StudioLab.exe in it.
  echo.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue';" ^
 "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;" ^
 "$here=(Get-Location).Path; $repo='kefirman9000/studio-lab';" ^
 "try { $u=Get-Content (Join-Path $here 'update.json') -Raw | ConvertFrom-Json; if($u.repo){$repo=$u.repo} } catch {}" ^
 "$old='?'; if(Test-Path (Join-Path $here 'VERSION')){ $old=(Get-Content (Join-Path $here 'VERSION') -Raw).Trim() }" ^
 "Write-Host ('Studio Lab ' + $old + ' - closing it if it is open...');" ^
 "Get-Process pythonw,python -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($here) } | Stop-Process -Force -ErrorAction SilentlyContinue;" ^
 "Start-Sleep -Seconds 1;" ^
 "$tmp=Join-Path $env:TEMP ('studiolab-update-' + [guid]::NewGuid()); New-Item -ItemType Directory $tmp | Out-Null;" ^
 "try {" ^
 "  Write-Host ('Downloading the latest version from github.com/' + $repo + ' ...');" ^
 "  Invoke-WebRequest ('https://github.com/' + $repo + '/archive/refs/heads/main.zip') -OutFile (Join-Path $tmp 'sl.zip') -UseBasicParsing -Headers @{'User-Agent'='studio-lab-updater'};" ^
 "  Write-Host 'Unpacking...'; Expand-Archive (Join-Path $tmp 'sl.zip') (Join-Path $tmp 'x') -Force;" ^
 "  $src=Get-ChildItem (Join-Path $tmp 'x') -Directory | Select-Object -First 1;" ^
 "  $keep=@('runtime','songs','presets','settings.json','update.json','user_sounds','ratings.json','ab_picks.jsonl','plugins','vst_sounds','sound_library','recent_instruments.json','.git');" ^
 "  Write-Host 'Installing...';" ^
 "  Get-ChildItem $src.FullName -Force | Where-Object { $keep -notcontains $_.Name } | ForEach-Object { Copy-Item $_.FullName -Destination $here -Recurse -Force };" ^
 "  $py=Join-Path $here 'runtime\python\python.exe'; if(Test-Path $py){ Write-Host 'Preparing it for a quick start...'; & $py -m compileall -q -j 0 --invalidation-mode checked-hash (Join-Path $here 'sgcore') (Join-Path $here 'studiolab.py') | Out-Null };" ^
 "  $new=(Get-Content (Join-Path $here 'VERSION') -Raw).Trim();" ^
 "  Write-Host ''; Write-Host ('Done - Studio Lab is now version ' + $new + '.') -ForegroundColor Green;" ^
 "} catch { Write-Host ''; Write-Host ('The update did not work: ' + $_.Exception.Message) -ForegroundColor Red; Write-Host 'Nothing in your folder was removed. Check your internet connection and try again.'; exit 1 }" ^
 "finally { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }"
set ERR=%ERRORLEVEL%
echo.
if %ERR%==0 (
  choice /c YN /m "Start Studio Lab now"
  if not errorlevel 2 (
    if exist "StudioLab.exe" ( start "" "StudioLab.exe" ) else ( start "" "Start Studio Lab (Windows).bat" )
  )
) else (
  pause
)
