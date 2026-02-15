@echo off
title Josiah Chatbot Launcher
cd /d "%~dp0backend"

echo.
echo ===== Josiah Chatbot =====
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

echo Starting server (keep the "Josiah Server" window open)...
echo.
start "Josiah Server" cmd /k "%PYCMD% app.py"

echo Waiting 5 seconds for server to start...
timeout /t 5 /nobreak >nul

start "" "http://localhost:5000"

echo.
echo Done. Your browser should open to the chat.
echo - If you see "Can't reach the server", check the "Josiah Server" window for errors.
echo - That window must stay OPEN while you chat.
echo.
pause
