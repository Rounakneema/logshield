#!/bin/bash
echo "============================================================"
echo "          Stopping LogShield Kubernetes Cluster             "
echo "============================================================"
echo ""

echo "[1/2] Terminating any active kubectl port-forward tunnels..."
pkill -f "kubectl port-forward" 2>/dev/null || true

echo "[2/2] Stopping Minikube cluster..."
minikube stop

echo ""
echo "LogShield Kubernetes cluster stopped successfully."
echo "============================================================"
