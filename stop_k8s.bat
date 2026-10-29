@echo off
title Stopping LogShield Kubernetes Cluster
echo ============================================================
echo          Stopping LogShield Kubernetes Cluster
echo ============================================================
echo.

echo [1/2] Terminating any active kubectl port-forward processes...
taskkill /F /IM kubectl.exe >nul 2>&1

echo [2/2] Stopping Minikube cluster...
minikube stop

echo.
echo LogShield Kubernetes cluster stopped successfully.
echo ============================================================
pause
