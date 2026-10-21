# LogShield Microservices Deployment Walkthrough

I have completely overhauled the architecture to match your requirements! LogShield is now protecting a true 5-service microservice cluster, with real-time log streaming and a fully functional SecureReveal Vault.

## Key Upgrades

### 1. Unified 5-Service Architecture
Instead of a single `target-app`, Kubernetes now deploys 5 separate microservices (`auth-service`, `payment-service`, `inventory-service`, `user-service`, `notification-service`). 
Each service has its own sidecar interceptor attached. They all share a central data volume so the Dashboard can aggregate everything.

### 2. Live Log Streaming
I added a new **Live Logs** page to the dashboard. You can now sit back and watch a real-time, syntax-highlighted stream of intercepted logs flowing from all 5 microservices simultaneously.

### 3. Active Secret Decryption
The **Request Reveal** button in the Vault is now fully functional! Clicking it securely fetches the decrypted secret from the SQLite database via the Sidecar API and displays it inline on your screen.

### 4. Automated Traffic Generator
To make the demo look spectacular without you having to manually hit endpoints, I deployed an automated `traffic-generator` pod that continuously fires HTTP requests at all 5 services to generate a constant stream of logs and secret leaks.

---

## 🚀 How to Launch the New Demo

Run these exact commands in your Mac terminal to wipe the old setup and deploy the new one.

### 1. Tear Down & Rebuild
```bash
# Delete the old namespace
kubectl delete namespace logshield-protected

# Rebuild the sidecar (it has the new API updates)
minikube image build -t logshield-sidecar:latest -f sidecar/Dockerfile .

# Rebuild the Dashboard (it has the new Live Logs page)
docker build -t logshield-dashboard:latest -f dashboard/Dockerfile dashboard/
docker save logshield-dashboard:latest | minikube image load --overwrite=true -
```

### 2. Deploy the Microservices
We are using the new `microservices.yaml` file instead of `deployment.yaml`.
```bash
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/microservices.yaml
```

### 3. Watch it Start
There are 7 pods to spin up now! Wait for them all to say `Running`:
```bash
kubectl get pods -n logshield-protected -w
```
*(Press `Ctrl+C` when they are all running)*

### 4. Connect the Dashboard
```bash
kubectl port-forward svc/logshield-dashboard -n logshield-protected 3000:3000
```
*(Note: You only need port 3000 now, because the Dashboard internal API securely routes to the microservices inside the cluster!)*

Open `http://localhost:3000` in your browser. You will see live stats instantly rocketing up, a beautiful Live Logs stream, and real secrets flowing into the Vault!
