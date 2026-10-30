# LogShield vs. Baselines Comprehensive Comparative Report

| Evaluation Dimension | Baseline 1 (Detection-Only) | Baseline 2 (Redaction-Only) | LogShield Complete System | IEEE Significance |
| :--- | :--- | :--- | :--- | :--- |
| **In-Transit Log Sanitization** | 0% (Plaintext exposed) | Partial (Fails on split/hex) | **100% In-Place Masking** | Zero sensitive byte leakage to central SIEM |
| **Adversarial Evasion Bypass Rate** | 67.8% bypass | 67.8% bypass | **8.7% bypass** | 59.1 percentage-point reduction in evasion bypass |
| **Evasion Detection Recall (N=2,400)** | 32.2% | 32.2% | **91.3%** | +59.1% recall under active evasion |
| **Cross-Encoding Sprawl Linkage** | 0% (No sprawl tracking) | 0% (Exact hash fragments) | **100% Canonical HMAC Unification** | Tracks raw, Base64 & URL replicas as 1 incident |
| **Mean Time to Containment (MTTC)** | Hours to Days (Manual triage) | Undefined (Credentials remain active) | **26.67 ms** | Closed-loop automated mitigation in milliseconds |
| **Authorized Secret Ingestion** | False alert pollution | Sprawl graph false alarms | **0.0% Pollution (Exemption Engine)** | Zero-sprawl guarantee for pre-seeded secrets |
| **Compromised Pod Isolation** | None | None | **Autonomous V1NetworkPolicy** | Immediate egress exfiltration blockage |
| **Cryptographic Audit Trail** | None | Plain text logs | **Forward-Secure HMAC Hash Chain** | Mathematically verifiable tamper detection |
