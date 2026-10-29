#!/bin/bash
set -e

echo "============================================================"
echo "      LogShield: Starting Complete Kubernetes Cluster       "
echo "============================================================"
echo ""

# 1. Start Minikube if not running
if ! minikube status | grep -q "Running"; then
    echo "[1/4] Starting Minikube cluster (4 CPUs, Docker driver)..."
    minikube start --cpus=4 --driver=docker
else
    echo "[1/4] Minikube is already running."
fi

# 2. Clean up any stale Released PVs or Pending PVCs to prevent storage deadlock
echo "[2/4] Ensuring clean persistent storage bindings..."
kubectl delete pvc logshield-data-pvc -n logshield-protected --ignore-not-found=true 2>/dev/null || true
kubectl delete pv logshield-pv --ignore-not-found=true 2>/dev/null || true

# 3. Apply RBAC and deploy all microservices
echo "[3/4] Applying RBAC and deploying 5 Microservices + Dashboard + Traffic Generator..."
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/microservices.yaml

# 4. Wait for deployments to roll out
echo "[4/4] Waiting for all services to become Ready..."
kubectl rollout status deployment/logshield-dashboard -n logshield-protected --timeout=90s || true
kubectl rollout status deployment/auth-service -n logshield-protected --timeout=90s || true
kubectl rollout status deployment/payment-service -n logshield-protected --timeout=90s || true
kubectl rollout status deployment/inventory-service -n logshield-protected --timeout=90s || true
kubectl rollout status deployment/user-service -n logshield-protected --timeout=90s || true
kubectl rollout status deployment/notification-service -n logshield-protected --timeout=90s || true
kubectl rollout status deployment/traffic-generator -n logshield-protected --timeout=90s || true

echo ""
echo "============================================================"
echo " Cluster is LIVE! Pod Statuses:"
kubectl get pods -n logshield-protected
echo "============================================================"
echo ""
echo "Opening Dashboard at http://localhost:3000 (Password: admin123)..."
echo "Press Ctrl+C to stop the port-forward tunnel."
echo ""
kubectl port-forward svc/logshield-dashboard 3000:3000 -n logshield-protected
