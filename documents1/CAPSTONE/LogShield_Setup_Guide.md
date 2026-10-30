# LogShield — Setup & Usage Guide

> **A Context-Aware, Pre-Ingestion Secret Protection Framework for Kubernetes**

This guide covers everything from a fresh machine to a fully running LogShield deployment with the Enterprise Dashboard.

---

## Prerequisites

Install the following before starting. Verify each one with the check commands.

| Tool | Minimum Version | Check Command |
|---|---|---|
| Docker Desktop | 24+ | `docker --version` |
| Minikube | 1.33+ | `minikube version` |
| kubectl | 1.29+ | `kubectl version --client` |
| Node.js | 18+ | `node --version` |
| Python | 3.11+ | `python --version` |

---

## Step 1 — Clone / Copy the Project

Copy the project folder to your machine. The essential folders are:

```
LOGSHEILD/
├── sidecar/          ← The detection engine (Python)
├── dashboard/        ← The Enterprise Dashboard (Next.js)
├── target-app/       ← The test application that leaks secrets
├── k8s/              ← Kubernetes manifests
├── requirements.txt  ← Python dependencies
└── sidecar/Dockerfile
```

> **Do NOT copy:** `.venv/`, `dashboard/node_modules/`, `dashboard/.next/`  
> These are rebuilt automatically on the new machine.

---

## Step 2 — Start Minikube

```bash
minikube start
```

**CRITICAL — Point Docker at Minikube's registry.**  
All `docker build` commands must run AFTER this step, so images land inside Minikube and are accessible to Kubernetes.

```bash
# Windows PowerShell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# macOS / Linux
eval $(minikube docker-env)
```

Verify it worked:
```bash
# This should show Minikube's internal images, not your local Docker Desktop ones
docker images
```

---

## Step 3 — Build the Three Docker Images

Run all three commands from the root of the `LOGSHEILD/` folder.

```bash
# 1. The LogShield detection engine (sidecar)
docker build -t logshield-sidecar:latest -f sidecar/Dockerfile .

# 2. The intentionally leaky test application
docker build -t logshield-protected-app:latest -f target-app/Dockerfile .

# 3. The Enterprise Dashboard (Next.js)
docker build -t logshield-dashboard:latest -f dashboard/Dockerfile dashboard/
```

Check all three images were built:
```bash
docker images | grep logshield
```
Expected output:
```
logshield-dashboard         latest    ...
logshield-sidecar           latest    ...
logshield-protected-app     latest    ...
```

---

## Step 4 — Deploy to Kubernetes

Apply the manifests in order. The RBAC file creates the namespace first, so it must go before the deployment.

```bash
# Creates: Namespace, ServiceAccount, Role, RoleBinding
kubectl apply -f k8s/rbac.yaml

# Creates: 3-container Pod (target-app + sidecar + dashboard) + Service
kubectl apply -f k8s/deployment.yaml
```

Wait for the pod to become ready (this takes ~30–60 seconds on first run):
```bash
kubectl get pods -n logshield-protected -w
```

Wait until you see:
```
NAME                                   READY   STATUS    RESTARTS
logshield-protected-xxx                3/3     Running   0
```

> `3/3` means all three containers (target-app, sidecar, dashboard) are healthy.

---

## Step 5 — Expose Ports Locally

Open a **new, dedicated terminal** and run this command. **Keep it running** for the entire session.

```bash
kubectl port-forward svc/logshield-protected -n logshield-protected 3000:3000 8000:8000
```

This makes the following available on your machine:

| URL | What it is |
|---|---|
| `http://localhost:3000` | LogShield Enterprise Dashboard |
| `http://localhost:8000` | Target App (the leaky application) |

---

## Step 6 — Access the Dashboard

Open your browser and navigate to:

### **`http://localhost:3000`**

You will be immediately redirected to the login screen.

---

### 🔐 Authentication

LogShield uses **two-tier authentication** to protect sensitive data.

#### Tier 1 — Global Dashboard Access

| Field | Value |
|---|---|
| **URL** | `http://localhost:3000/login` |
| **Password** | `admin123` |

Enter the password and click **Authenticate**. You will be redirected to the main dashboard.

#### Tier 2 — Vault Access (SecureReveal)

Navigating to the **SecureReveal Vault** page (`/vault`) requires a second, independent PIN even after you are logged into the dashboard.

| Field | Value |
|---|---|
| **Vault PIN** | `vault789` |

---

## Step 7 — Generate Live Data (Trigger Secret Leaks)

The dashboard will show live telemetry only after the target app generates logs. Open another terminal and run these `curl` commands to simulate real-world secret leaks.

```bash
# Trigger an AWS Key + JWT secret leak
curl http://localhost:8000/health

# Trigger a Stripe API key leak
curl http://localhost:8000/process-payment

# Trigger a database URL with password leak
curl "http://localhost:8000/auth?token=Bearer%20eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# Trigger a GitHub token leak
curl http://localhost:8000/debug
```

Repeat any command multiple times to generate more data.

---

## Step 8 — Verify Interception in Real-Time

In a separate terminal, watch the LogShield sidecar's live output to see secrets being masked as they happen:

```bash
kubectl logs -n logshield-protected \
  -l app=logshield-protected \
  -c logshield-sidecar \
  -f
```

**Expected output:**
```
[REDACTED:SEC-A1B2:SCS=99] - Stripe key masked
INFO: Connecting to DB: postgres://admin:[REDACTED:SEC-C3D4:SCS=97]@prod:5432/app
[FLAGGED:SEC-E5F6:SCS=62]  - Low confidence flag, not redacted
```

Raw secret values from the target app **never appear** in this output.

---

## Dashboard Pages

| Page | URL | What it shows |
|---|---|---|
| **Overview** | `/` | Live scan volume, secrets masked count, detection chart |
| **SecureReveal Vault** | `/vault` | Encrypted vault entries, SCS scores, reference IDs *(requires Vault PIN)* |
| **Audit Logs** | `/audit` | Immutable record of every sidecar action (vault store, flag events) |
| **Sprawl Lineage** | `/sprawl` | HMAC fingerprint tracking — shows if a secret leaked across multiple pods |

---

## Teardown

When you're done, clean up everything with:

```bash
# Stop port-forwarding: Ctrl+C in that terminal

# Delete all LogShield resources from the cluster
kubectl delete namespace logshield-protected

# Stop Minikube (optional)
minikube stop
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `ErrImagePull` or `ImagePullBackOff` | Docker build ran before `minikube docker-env` | Re-run `eval $(minikube docker-env)` then rebuild all 3 images |
| Dashboard shows "Loading..." forever | Port-forward is not running | Re-run the `kubectl port-forward` command in Step 5 |
| Pod stuck in `0/3 Pending` | Minikube is not started | Run `minikube start` |
| Vault page shows empty table | No secrets generated yet | Run the `curl` commands in Step 7 |
| Login redirect loop | Cookie not being set | Try in a private/incognito window |
