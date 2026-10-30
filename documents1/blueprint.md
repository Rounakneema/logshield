# LogShield Architecture Blueprint

## 1. Vision & Goal
LogShield is a zero-config, Kubernetes-native security engine that automatically detects and masks sensitive secrets (API keys, passwords, PII) in application logs before they are written to disk or shipped to log aggregators.

> **Goal:** A developer installs LogShield once, labels the Kubernetes namespace/workload, and LogShield automatically protects the logs without modifying application code.

## 2. Core Components (Data Plane)

### 2.1 LogMask (SCS Engine)
The Secret Confidence Score (SCS) engine is a multi-layered detection pipeline:
- **Preprocessor:** Parses JSON, decodes URLs and Base64.
- **CandidateFinder:** High-speed Aho-Corasick automaton to filter out non-sensitive lines.
- **ContextEngine:** Analyzes surrounding text for positive (e.g., `password=`) or negative (e.g., `trace_id=`) proximity fields.
- **SecretClassifier (Regex):** 600+ patterns across specific, generic, and SecretBench tiers.
- **Scorer:** Uses a trained Machine Learning model to weigh factors (Varname, Regex, Entropy, Token Structure, Context, Encoding) and produce a final confidence score (0-100).
- **Gate:** Makes decisions (`MASK` for >=80, `FLAG` for >=50, `ALLOW` for <50).

### 2.2 SecureReveal (Vault)
- Safely encrypts and stores the original secret locally (SQLite).
- Leaves behind a safe reference in the log: `[REDACTED:SEC-1234:SCS=94]`.
- Provides an audit trail for when authorized actors request to reveal the secret during incident investigations.

### 2.3 SecretLineage
- Generates a keyed HMAC fingerprint of the secret.
- Tracks secret sprawl across different microservices and pods without exposing the actual secret value.

## 3. Kubernetes Integration (Control Plane)

### 3.1 Mutating Admission Webhook
- A control plane server that intercepts Kubernetes `Pod` creation requests.
- **Automatic Injection:** If a namespace is labeled with `logshield.io/enabled=true`, the webhook dynamically injects the LogShield Sidecar container and required shared volumes (`shared-logs`, `sidecar-data`) into the Pod specification.

### 3.2 Helm Chart & Policies
- **Deployment:** LogShield is deployed cluster-wide via a Helm chart.
- **TLS:** The chart handles dynamic, self-signed TLS certificate generation for the webhook, ensuring zero external dependencies (like `cert-manager`).
- **LogShieldPolicy CRD:** Custom Resource Definition allowing cluster administrators to define detection thresholds and active features per namespace.

## 4. Developer Experience

### 4.1 LogShield CLI
A command-line tool `logshield` that simplifies interaction:
- `logshield install`: Installs the Helm chart.
- `logshield status`: Verifies the health of the Control Plane, Webhook, and protected namespaces.
- `logshield test`: Runs synthetic local tests to validate the engine's accuracy.

## 5. Architectural Flow

```text
                  Kubernetes Cluster
                         │
                ┌────────▼────────┐
                │ LogShield       │
                │ Controller      │
                │ (Webhook)       │
                └────────┬────────┘
                         │ (injects sidecar)
                         ▼
          ┌──────────────▼──────────────┐
          │           Pod               │
          │  ┌────────────┐             │
          │  │ Application│             │
          │  └─────┬──────┘             │
          │        │ writes logs        │
          │        ▼ /shared/app.log    │
          │  ┌────────────┐             │
          │  │ LogShield  │             │
          │  │ Sidecar    │             │
          │  │ (LogMask)  │             │
          │  └─────┬──────┘             │
          └────────┼────────────────────┘
                   │ emits sanitized logs
                   ▼
              Fluent Bit / Loki
```
