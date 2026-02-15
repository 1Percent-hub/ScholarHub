@echo off
title Academic Arsenal with AI
cd /d "%~dp0"

echo.
echo ===== Academic Arsenal with AI =====
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
  where py >nul 2>&1
  if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python and add it to PATH.
    echo Then run this file again.
    pause
    exit /b 1
  )
  set PYCMD=py
) else (
  set PYCMD=python
)

set "BACKEND_DIR=%~dp0..\chatbot\backend"
pushd "%BACKEND_DIR%" 2>nul
if %errorlevel% neq 0 (
  echo ERROR: Folder not found: %BACKEND_DIR%
  echo Make sure the "chatbot" folder is next to "calculator-with-ai".
  pause
  exit /b 1
)
set "BACKEND_DIR=%CD%"
popd

echo Starting AI server (a "Josiah Server" window will open)...
echo.
start "Josiah Server" /D "%BACKEND_DIR%" cmd /k "%PYCMD% app.py"

echo Waiting 7 seconds for the server to start...
timeout /t 7 /nobreak >nul

start "" "http://localhost:5000/app/"

echo.
echo Done. Your browser should open to Academic Arsenal with the AI widget.
echo.
echo If you see "This site can't be reached" or "connection refused":
echo   1. Look at the "Josiah Server" window - is it still open? Any red error text?
echo   2. If that window closed or shows an error, Python or the server failed to start.
echo   3. Try running manually: open Command Prompt, run: cd "%BACKEND_DIR%" then %PYCMD% app.py
echo.
echo Keep the "Josiah Server" window OPEN while you use the AI.
echo.
pause
