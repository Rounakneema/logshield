#!/bin/bash

echo "============================================================"
echo "          LogShield: Autonomous Secret Sanitization         "
echo "============================================================"
echo ""

mkdir -p /tmp/shared /tmp/data

echo "[1/3] Starting Target Demo Application (Port 8001)..."
python3 -m uvicorn app:app --app-dir target-app --host 0.0.0.0 --port 8001 &
APP_PID=$!

echo "[2/3] Starting LogShield Sidecar & Enterprise API (Port 8000)..."
LOG_INPUT_PATH=/tmp/shared/app.log \
STATS_OUTPUT_PATH=/tmp/data/stats.json \
VAULT_DB_PATH=/tmp/data/vault.db \
VAULT_KEY_PATH=/tmp/data/vault.key \
LINEAGE_DB_PATH=/tmp/data/lineage.db \
LINEAGE_KEY_PATH=/tmp/data/lineage.key \
CONTAINMENT_DB_PATH=/tmp/data/containment.db \
POD_NAME=local-sidecar \
PORT=8000 \
python3 main.py &
SIDECAR_PID=$!

echo "[3/3] Starting LogShield Web Dashboard (Port 3000)..."
(cd dashboard && npm run dev) &
DASH_PID=$!

echo ""
echo "All services launched in background!"
echo "- Web Dashboard:  http://localhost:3000"
echo "- Sidecar API:    http://localhost:8000/docs"
echo "- Target App:     http://localhost:8001/docs"
echo "============================================================"
echo "Press Ctrl+C to terminate all services."

trap "kill $APP_PID $SIDECAR_PID $DASH_PID 2>/dev/null" EXIT
wait
