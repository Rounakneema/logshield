"""
LogShield Systematic Evasion Resistance Benchmark
================================================
Evaluates detection robustness on a labeled benchmark corpus (2,400 samples)
comparing:
  1. Baseline Regex/Heuristic Detector (No Token Fusion / No Normalization)
  2. LogShield Adaptive Pipeline (Token Window Fusion + Hex Normalization + Base64 Unnesting)

Evasion Categories Tested:
  - Delimiter Split (Whitespace, Hyphens, Slashes across token boundaries)
  - Hex-Escaped Sequences (\\x41\\x4b... byte encoding)
  - Base64 Wrapped Authorization Envelopes (Nested Basic/Bearer schemes)
  - URL Percent Encoding (Query/Path encoding)
  - Raw / Unobfuscated Control Secrets
  - Benign Controls (UUIDs, Git commit SHAs, hex logs, normal microservice traffic)

Metrics Reported:
  - Precision, Recall, F1-Score, False Positive Rate, Evasion Bypass Rate
  - Per-technique breakdown
  - Latency distribution (mean, p95, p99)
"""

import os
import sys
import time
import json
import random
import base64
import urllib.parse
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sidecar.logmask.scorer import SCSEngine
from sidecar.logmask.catalog import ALL_SPECIFIC_DETECTORS


class BaselineDetector:
    """
    Standard industry baseline detector (e.g. Trufflehog / Gitleaks / naive regex engine):
    Uses standard regex catalog matching over raw whitespace/key-value tokens.
    Lacks sliding-window token fusion, hex unescaping, and nested auth decoding.
    """
    def __init__(self):
        import re
        self.patterns = []
        for det in ALL_SPECIFIC_DETECTORS:
            name = det[1]
            regex_str = det[3]
            try:
                self.patterns.append((name, re.compile(regex_str)))
            except Exception:
                pass

    def detect(self, line: str) -> bool:
        # Standard regex matching against the line or simple space-split tokens
        for name, pat in self.patterns:
            if pat.search(line):
                return True
        return False


def generate_labeled_evasion_corpus(num_samples_per_class: int = 200) -> List[Dict]:
    """
    Generates a balanced, labeled adversarial evaluation dataset (2,400 rows total):
      - 1,200 Positive Secret Samples (across 5 representation classes)
      - 1,200 Negative Benign Controls (across 6 benign classes)
    """
    random.seed(42)

    raw_secret_seeds = [
        # AWS Access Keys
        ("AKIAIOSFODNN7EXAMPLE", "AWS Access Key", "access_key"),
        ("AKIAI44QH8DHBEXAMPLE", "AWS Access Key", "aws_key"),
        ("AKIA2E4V37F6ZEXAMPLE", "AWS Access Key", "access_key_id"),
        ("AKIAJ76DFG76FEXAMPLE", "AWS Access Key", "aws_access_key"),
        # GitHub Tokens
        ("gh" + "p_A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8", "GitHub Personal Access Token", "github_token"),
        ("gh" + "p_99NovelSecEvidenceToken2026ValidXyz", "GitHub Personal Access Token", "gh_token"),
        ("github" + "_pat_11AAAAAA0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "GitHub Fine-Grained Token", "token"),
        # Stripe API Keys
        ("sk_" + "live_51Mz99ExplicitKeyForLineageTesting1234", "Stripe Secret Key", "stripe_api_key"),
        ("sk_" + "live_4eC39HqLyjWDarjtT1zdp7dc", "Stripe Secret Key", "api_key"),
        ("sk_test_51Mz99ExplicitExemptionKey9876543210", "Stripe Secret Key", "stripe_test_key"),
        # Slack Tokens
        ("xo" + "xb-123456789012-1234567890123-AbCdEfGhIjKlMnOpQrStUvWx", "Slack Bot Token", "slack_bot_token"),
        ("xo" + "xp-123456789012-1234567890123-AbCdEfGhIjKlMnOpQrStUvWx", "Slack User Token", "slack_token"),
        # Database URIs
        ("postgres://admin:SuperSecr3tP@ss2026@db-prod.internal:5432/core_db", "Database URI", "db_uri"),
        ("mysql://root:RootDatabasePassw0rd99@mysql.internal:3306/app", "Database URI", "database_url"),
        ("mongodb://dbuser:MongoSecretPass7788@mongo.internal:27017/prod", "Database URI", "mongo_uri"),
        # JWT
        ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFkbWluIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c", "JWT Bearer Token", "jwt")
    ]

    services = ["auth-service", "payment-service", "inventory-service", "user-service", "ingress-controller"]
    log_levels = ["INFO", "WARN", "DEBUG", "ERROR"]

    dataset = []
    line_id = 1000

    # 1. CLASS A: Delimiter-Split Secrets
    for _ in range(num_samples_per_class):
        sec, sec_type, key_name = random.choice(raw_secret_seeds)
        svc = random.choice(services)
        lvl = random.choice(log_levels)

        # Apply whitespace or hyphen or slash split
        split_pos = random.randint(4, min(10, len(sec) - 4))
        delimiter = random.choice([" ", "  ", " - ", " / "])
        split_val = sec[:split_pos] + delimiter + sec[split_pos:]

        log_text = f"2026-10-21T12:00:00.000Z [{lvl}] {svc}: {key_name} = {split_val} request_id={random.randint(10000, 99999)}"
        dataset.append({
            "line_id": line_id,
            "label": 1,
            "category": "delimiter_split",
            "secret_type": sec_type,
            "secret_value": sec,
            "log_text": log_text
        })
        line_id += 1

    # 2. CLASS B: Hex-Escaped Secrets
    for _ in range(num_samples_per_class):
        sec, sec_type, key_name = random.choice(raw_secret_seeds)
        svc = random.choice(services)
        lvl = random.choice(log_levels)

        # Hex-escape bytes: \x41\x4b...
        hex_encoded = "".join(f"\\x{ord(c):02x}" for c in sec[:24])  # escape first 24 chars
        if len(sec) > 24:
            hex_encoded += sec[24:]

        log_text = f"2026-10-21T12:00:00.000Z [{lvl}] {svc}: credential {key_name}={hex_encoded} client_ip=10.0.4.12"
        dataset.append({
            "line_id": line_id,
            "label": 1,
            "category": "hex_escaped",
            "secret_type": sec_type,
            "secret_value": sec,
            "log_text": log_text
        })
        line_id += 1

    # 3. CLASS C: Base64-Wrapped Authentication Headers
    for _ in range(num_samples_per_class):
        sec, sec_type, key_name = random.choice(raw_secret_seeds)
        svc = random.choice(services)
        lvl = random.choice(log_levels)

        b64_val = base64.b64encode(sec.encode("utf-8")).decode("utf-8")
        scheme = random.choice(["Basic", "Bearer", "Token"])
        log_text = f"2026-10-21T12:00:00.000Z [{lvl}] {svc}: Authorization: {scheme} {b64_val} session_id=sess_{random.randint(1000, 9999)}"
        dataset.append({
            "line_id": line_id,
            "label": 1,
            "category": "base64_wrapped",
            "secret_type": sec_type,
            "secret_value": sec,
            "log_text": log_text
        })
        line_id += 1

    # 4. CLASS D: URL-Encoded Secrets
    for _ in range(num_samples_per_class):
        sec, sec_type, key_name = random.choice(raw_secret_seeds)
        svc = random.choice(services)
        lvl = random.choice(log_levels)

        url_val = urllib.parse.quote(sec)
        log_text = f"2026-10-21T12:00:00.000Z [{lvl}] {svc}: HTTP GET /api/v1/auth?token={url_val}&client=mobile status=401"
        dataset.append({
            "line_id": line_id,
            "label": 1,
            "category": "url_encoded",
            "secret_type": sec_type,
            "secret_value": sec,
            "log_text": log_text
        })
        line_id += 1

    # 5. CLASS E: Raw Unobfuscated Control Secrets
    for _ in range(num_samples_per_class):
        sec, sec_type, key_name = random.choice(raw_secret_seeds)
        svc = random.choice(services)
        lvl = random.choice(log_levels)

        log_text = f"2026-10-21T12:00:00.000Z [{lvl}] {svc}: connected with {key_name}={sec} node=node-{random.randint(1, 20)}"
        dataset.append({
            "line_id": line_id,
            "label": 1,
            "category": "raw_unobfuscated",
            "secret_type": sec_type,
            "secret_value": sec,
            "log_text": log_text
        })
        line_id += 1

    # Extra class for combination multi-evasion (delimiter split in URL)
    for _ in range(num_samples_per_class):
        sec, sec_type, key_name = random.choice(raw_secret_seeds)
        svc = random.choice(services)
        lvl = random.choice(log_levels)
        split_pos = random.randint(4, 10)
        split_val = sec[:split_pos] + " " + sec[split_pos:]
        log_text = f"2026-10-21T12:00:00.000Z [{lvl}] {svc}: config={key_name}={split_val} env=staging"
        dataset.append({
            "line_id": line_id,
            "label": 1,
            "category": "delimiter_split",
            "secret_type": sec_type,
            "secret_value": sec,
            "log_text": log_text
        })
        line_id += 1

    # 6. BENIGN CONTROLS (Negative Samples, Label = 0)
    benign_templates = [
        # Normal microservice logs
        "2026-10-21T12:00:00.000Z [INFO] {svc}: Heartbeat received from cluster node={node} cpu_usage=24.5% memory_mb=512",
        "2026-10-21T12:00:00.000Z [DEBUG] {svc}: HTTP 200 OK for GET /healthz duration_ms=4.12 client_ip=10.0.1.5",
        "2026-10-21T12:00:00.000Z [WARN] {svc}: Cache miss on key user_session_{num} re-fetching from redis cluster",
        # UUIDs (High entropy but non-secret)
        "2026-10-21T12:00:00.000Z [INFO] {svc}: Transaction completed tx_id=550e8400-e29b-41d4-a716-{uuid_tail} amount=$124.50",
        "2026-10-21T12:00:00.000Z [DEBUG] {svc}: Correlation ID c0a80101-1234-5678-9abc-{uuid_tail} assigned to request",
        # Git Commit SHA hashes (Hex strings but non-secret)
        "2026-10-21T12:00:00.000Z [INFO] {svc}: Deployment initialized git_commit=4b825dc642cb6eb9a060e54bf8d69288fbee{hex_tail} tag=v2.1.0",
        "2026-10-21T12:00:00.000Z [DEBUG] {svc}: Build artifact sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 verified",
        # Base64 Non-secret payloads
        "2026-10-21T12:00:00.000Z [INFO] {svc}: Received webhook payload data=eyJldmVudCI6ICJ1c2VyX2xvZ2luIiwgInN0YXR1cyI6ICJzdWNjZXNzIn0= processed=true",
        # Delimiter split numbers/version (benign split)
        "2026-10-21T12:00:00.000Z [WARN] {svc}: Service version mismatch found: v = 8 . 18 . 25 vs v = 8 . 18 . 26",
        # Hex-escaped non-secret text
        "2026-10-21T12:00:00.000Z [DEBUG] {svc}: Parsing binary frame header=\\x00\\x01\\x02\\x03 status=\\x4f\\x4b length=64"
    ]

    total_benign_needed = len(dataset)  # Exactly match the number of secret samples
    for i in range(total_benign_needed):
        tmpl = random.choice(benign_templates)
        svc = random.choice(services)
        log_text = tmpl.format(
            svc=svc,
            node=f"node-{random.randint(1, 50)}",
            num=random.randint(1000, 9999),
            uuid_tail=f"{random.randint(100000000000, 999999999999):x}"[:12],
            hex_tail=f"{random.randint(1000, 9999):x}"
        )
        dataset.append({
            "line_id": line_id,
            "label": 0,
            "category": "benign_control",
            "secret_type": "NONE",
            "secret_value": "",
            "log_text": log_text
        })
        line_id += 1

    random.shuffle(dataset)
    return dataset


def evaluate_detector(detector_name: str, detector_func, corpus: List[Dict]) -> Dict:
    """Evaluates a detector function against the labeled corpus and computes metrics."""
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    per_category = {}
    latencies = []

    for item in corpus:
        label = item["label"]
        cat = item["category"]
        text = item["log_text"]

        if cat not in per_category:
            per_category[cat] = {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "total": 0}
        per_category[cat]["total"] += 1

        t0 = time.perf_counter()
        pred = detector_func(text)
        lat_us = (time.perf_counter() - t0) * 1_000_000
        latencies.append(lat_us)

        if label == 1 and pred:
            tp += 1
            per_category[cat]["tp"] += 1
        elif label == 0 and pred:
            fp += 1
            per_category[cat]["fp"] += 1
        elif label == 0 and not pred:
            tn += 1
            per_category[cat]["tn"] += 1
        elif label == 1 and not pred:
            fn += 1
            per_category[cat]["fn"] += 1

    total = len(corpus)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    # Calculate evasion bypass rate on obfuscated categories
    evasion_cats = ["delimiter_split", "hex_escaped", "base64_wrapped", "url_encoded"]
    evasion_total = sum(per_category[c]["total"] for c in evasion_cats if c in per_category)
    evasion_fn = sum(per_category[c]["fn"] for c in evasion_cats if c in per_category)
    evasion_tp = sum(per_category[c]["tp"] for c in evasion_cats if c in per_category)
    evasion_bypass_rate = evasion_fn / evasion_total if evasion_total > 0 else 0.0
    evasion_recall = evasion_tp / evasion_total if evasion_total > 0 else 0.0

    latencies.sort()
    mean_lat = sum(latencies) / len(latencies)
    p95_lat = latencies[int(len(latencies) * 0.95)]
    p99_lat = latencies[int(len(latencies) * 0.99)]

    # Compute category-level recalls
    breakdown = {}
    for c, stats in per_category.items():
        if stats["tp"] + stats["fn"] > 0:
            cat_rec = stats["tp"] / (stats["tp"] + stats["fn"])
        else:
            cat_rec = 0.0
        breakdown[c] = {
            "total": stats["total"],
            "tp": stats["tp"],
            "fp": stats["fp"],
            "tn": stats["tn"],
            "fn": stats["fn"],
            "recall": round(cat_rec * 100, 2)
        }

    return {
        "detector": detector_name,
        "total_samples": total,
        "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr * 100, 2),
        "evasion_recall": round(evasion_recall * 100, 2),
        "evasion_bypass_rate": round(evasion_bypass_rate * 100, 2),
        "latency_us": {
            "mean": round(mean_lat, 2),
            "p95": round(p95_lat, 2),
            "p99": round(p99_lat, 2)
        },
        "breakdown": breakdown
    }


def main():
    print("="*80)
    print("LOGSHIELD ADVERSARIAL EVASION BENCHMARK (LABELED CORPUS EVALUATION)")
    print("="*80)

    print("\n[+] Generating 2,400-sample balanced evasion evaluation corpus...")
    corpus = generate_labeled_evasion_corpus(num_samples_per_class=200)
    print(f"    Total Corpus Size: {len(corpus)} rows")
    num_secrets = sum(1 for c in corpus if c["label"] == 1)
    num_benign = sum(1 for c in corpus if c["label"] == 0)
    print(f"    - Labeled Secrets: {num_secrets} rows")
    print(f"    - Benign Controls: {num_benign} rows")

    # Save corpus to CSV
    corpus_csv_path = PROJECT_ROOT / "research" / "datasets" / "evasion_benchmark_corpus.csv"
    corpus_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(corpus_csv_path, "w", encoding="utf-8") as f:
        f.write("LINE_ID,LABEL,CATEGORY,SECRET_TYPE,LOG_TEXT\n")
        for item in corpus:
            safe_text = item["log_text"].replace('"', '""')
            f.write(f"{item['line_id']},{item['label']},{item['category']},{item['secret_type']},\"{safe_text}\"\n")
    print(f"    Saved evaluation corpus: {corpus_csv_path.name}")

    # 1. Evaluate Baseline Detector
    print("\n[+] Evaluating Baseline Detector (Standard Regex Matching without Fusion)...")
    baseline = BaselineDetector()
    res_baseline = evaluate_detector("Baseline Regex Detector", baseline.detect, corpus)

    # 2. Evaluate LogShield Adaptive Pipeline
    print("\n[+] Evaluating LogShield Adaptive Pipeline (Token Window Fusion + Normalization)...")
    engine = SCSEngine()
    def logshield_detect(line: str) -> bool:
        results = engine.extract_and_score(line)
        return any(r.decision in ("MASK", "FLAG") for r in results)

    res_logshield = evaluate_detector("LogShield Adaptive Pipeline", logshield_detect, corpus)

    # 3. Print Comparison Table
    print("\n" + "="*80)
    print("EMPIRICAL BENCHMARK RESULTS SUMMARY (N = 2,400)")
    print("="*80)
    print(f"{'Metric':<32} | {'Baseline (No Fusion)':<20} | {'LogShield Adaptive':<20} | {'Delta':<10}")
    print("-" * 88)

    metrics_to_show = [
        ("Overall Recall (%)", res_baseline["recall"], res_logshield["recall"], f"+{res_logshield['recall'] - res_baseline['recall']:.2f}%"),
        ("Evasion Recall (%)", res_baseline["evasion_recall"], res_logshield["evasion_recall"], f"+{res_logshield['evasion_recall'] - res_baseline['evasion_recall']:.2f}%"),
        ("Evasion Bypass Rate (%)", res_baseline["evasion_bypass_rate"], res_logshield["evasion_bypass_rate"], f"{res_logshield['evasion_bypass_rate'] - res_baseline['evasion_bypass_rate']:.2f}%"),
        ("Precision (%)", res_baseline["precision"], res_logshield["precision"], f"{res_logshield['precision'] - res_baseline['precision']:.2f}%"),
        ("F1-Score", res_baseline["f1_score"], res_logshield["f1_score"], f"+{res_logshield['f1_score'] - res_baseline['f1_score']:.4f}"),
        ("False Positive Rate (%)", res_baseline["false_positive_rate"], res_logshield["false_positive_rate"], f"{res_logshield['false_positive_rate'] - res_baseline['false_positive_rate']:.2f}%"),
        ("Mean Latency (us)", res_baseline["latency_us"]["mean"], res_logshield["latency_us"]["mean"], f"+{res_logshield['latency_us']['mean'] - res_baseline['latency_us']['mean']:.1f} us"),
        ("P95 Latency (us)", res_baseline["latency_us"]["p95"], res_logshield["latency_us"]["p95"], f"+{res_logshield['latency_us']['p95'] - res_baseline['latency_us']['p95']:.1f} us")
    ]

    for m_name, val_b, val_l, delta in metrics_to_show:
        print(f"{m_name:<32} | {str(val_b):<20} | {str(val_l):<20} | {delta:<10}")

    print("-" * 88)
    print("\nPER-CATEGORY RECALL BREAKDOWN:")
    print(f"{'Evasion Category':<25} | {'Samples':<8} | {'Baseline Recall':<17} | {'LogShield Recall':<17}")
    print("-" * 75)
    for cat in ["raw_unobfuscated", "delimiter_split", "hex_escaped", "base64_wrapped", "url_encoded", "benign_control"]:
        b_rec = res_baseline["breakdown"].get(cat, {}).get("recall", 0.0)
        l_rec = res_logshield["breakdown"].get(cat, {}).get("recall", 0.0)
        cnt = res_baseline["breakdown"].get(cat, {}).get("total", 0)
        if cat == "benign_control":
            b_fp = res_baseline["breakdown"].get(cat, {}).get("fp", 0)
            l_fp = res_logshield["breakdown"].get(cat, {}).get("fp", 0)
            print(f"{cat:<25} | {cnt:<8} | FP: {b_fp} ({b_fp/cnt*100:.1f}%)        | FP: {l_fp} ({l_fp/cnt*100:.1f}%)")
        else:
            print(f"{cat:<25} | {cnt:<8} | {b_rec:<17}% | {l_rec:<17}%")

    # Save results to JSON
    output_json = {
        "benchmark_timestamp": int(time.time()),
        "corpus_size": len(corpus),
        "baseline_detector": res_baseline,
        "logshield_adaptive": res_logshield,
        "summary": {
            "evasion_bypass_reduction_pct": round(res_baseline["evasion_bypass_rate"] - res_logshield["evasion_bypass_rate"], 2),
            "evasion_recall_gain_pct": round(res_logshield["evasion_recall"] - res_baseline["evasion_recall"], 2),
            "f1_improvement": round(res_logshield["f1_score"] - res_baseline["f1_score"], 4)
        }
    }

    out_path = PROJECT_ROOT / "research" / "results" / "evasion_corpus_benchmark_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2)
    print(f"\n[+] Saved detailed evaluation metrics to: {out_path}")


if __name__ == "__main__":
    main()
