@echo off
title Starting LogShield Enterprise Suite
echo ============================================================
echo           LogShield: Autonomous Secret Sanitization
echo ============================================================
echo.

if not exist "D:\shared" mkdir "D:\shared"
if not exist "D:\data" mkdir "D:\data"

echo [1/3] Starting Target Demo Application (Port 8001)...
start "LogShield - Target App [Port 8001]" cmd /k "cd /d D:\LOGSHEILD && set LOG_OUTPUT_PATH=D:\shared\app.log && .venv\Scripts\python.exe -m uvicorn app:app --app-dir target-app --host 0.0.0.0 --port 8001"

echo [2/3] Starting LogShield Sidecar & Enterprise API (Port 8000)...
start "LogShield - Sidecar Interceptor & API [Port 8000]" cmd /k "cd /d D:\LOGSHEILD && set LOG_INPUT_PATH=D:\shared\app.log&& set STATS_OUTPUT_PATH=D:\data\stats.json&& set VAULT_DB_PATH=D:\data\vault.db&& set VAULT_KEY_PATH=D:\data\vault.key&& set LINEAGE_DB_PATH=D:\data\lineage.db&& set LINEAGE_KEY_PATH=D:\data\lineage.key&& set CONTAINMENT_DB_PATH=D:\data\containment.db&& set POD_NAME=local-sidecar&& set PORT=8000&& .venv\Scripts\python.exe main.py"

echo [3/3] Starting LogShield Web Dashboard (Port 3000)...
start "LogShield - Web Dashboard [Port 3000]" cmd /k "cd /d D:\LOGSHEILD\dashboard && npm run dev"

echo.
echo All services launched in separate windows!
echo - Web Dashboard:  http://localhost:3000
echo - Sidecar API:    http://localhost:8000/docs
echo - Target App:     http://localhost:8001/docs
echo ============================================================
pause
