#!/bin/bash
echo "============================================================"
echo "          Stopping all LogShield Native Services...         "
echo "============================================================"
echo ""

echo "Freeing ports 3000, 8000, 8001..."
lsof -ti:3000,8000,8001 | xargs kill -9 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "main.py" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true

echo "All local LogShield native services stopped."
echo "============================================================"
