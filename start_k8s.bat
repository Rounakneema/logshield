@echo off
title Starting LogShield Kubernetes Cluster
echo ============================================================
echo       LogShield: Starting Complete Kubernetes Cluster
echo ============================================================
echo.

echo [1/4] Checking and starting Minikube...
minikube status | findstr /i "Running" >nul
if %errorlevel% neq 0 (
    minikube start --cpus=4 --driver=docker
) else (
    echo Minikube is already running.
)

echo [2/4] Ensuring clean persistent storage bindings...
kubectl delete pvc logshield-data-pvc -n logshield-protected --ignore-not-found=true >nul 2>&1
kubectl delete pv logshield-pv --ignore-not-found=true >nul 2>&1

echo [3/4] Applying RBAC and deploying 5 Microservices + Dashboard + Traffic Generator...
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/microservices.yaml

echo [4/4] Waiting for all services to become Ready...
kubectl rollout status deployment/logshield-dashboard -n logshield-protected --timeout=90s
kubectl rollout status deployment/auth-service -n logshield-protected --timeout=90s
kubectl rollout status deployment/payment-service -n logshield-protected --timeout=90s
kubectl rollout status deployment/inventory-service -n logshield-protected --timeout=90s
kubectl rollout status deployment/user-service -n logshield-protected --timeout=90s
kubectl rollout status deployment/notification-service -n logshield-protected --timeout=90s
kubectl rollout status deployment/traffic-generator -n logshield-protected --timeout=90s

echo.
echo ============================================================
echo  Cluster is LIVE! Pod Statuses:
kubectl get pods -n logshield-protected
echo ============================================================
echo.
echo Forwarding Dashboard to http://localhost:3000 (Password: admin123)...
echo Press Ctrl+C to stop the port-forward tunnel.
echo.
kubectl port-forward svc/logshield-dashboard 3000:3000 -n logshield-protected
