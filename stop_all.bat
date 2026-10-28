@echo off
title Stopping LogShield Enterprise Suite
echo ============================================================
echo           Stopping all LogShield Services...
echo ============================================================
echo.

echo Freeing ports 8000, 8001, 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %%a 2>nul

echo All LogShield services stopped.
echo ============================================================
pause
