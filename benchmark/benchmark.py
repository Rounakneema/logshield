"""
LogShield — Performance & Accuracy Benchmarking Suite
======================================================
Evaluates:
  1. Detection Performance (Precision, Recall, F1-Score, False Mask Rate)
     compared against single-factor baselines (Regex-only, Entropy-only).
  2. Latency Overhead (Avg, P95, P99 processing time per log line).

Directly supports claims from Phase I Presentation Slides 4, 12, and 17.
"""

import sys
import os
import time
import random
import string
from dataclasses import dataclass
from typing import List, Tuple

# Ensure sidecar import works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sidecar.logmask.scorer import SCSEngine


@dataclass
class BenchmarkItem:
    line: str
    contains_secret: bool
    description: str


class SingleFactorRegexBaseline:
    """Baseline 1: Standard Regex-Only Detector (e.g. Gitleaks static regex rules)"""
    def __init__(self):
        self.engine = SCSEngine()

    def is_secret(self, line: str) -> bool:
        rf = self.engine.classifier.regex_factor
        # Check specific detectors
        for pat, name, company, category, confidence in rf.SPECIFIC_DETECTORS:
            if pat.search(line):
                return True
        # Check SecretBench patterns
        for name, pattern in rf.SECRETBENCH_PATTERNS:
            if pattern.search(line):
                return True
        # Check Generic detectors
        for pat, name, company, category, confidence in rf.GENERIC_DETECTORS:
            if pat.search(line):
                return True
        return False


class SingleFactorEntropyBaseline:
    """Baseline 2: Pure Shannon Entropy Detector (Flags any token with entropy >= 3.5)"""
    def is_secret(self, line: str) -> bool:
        engine = SCSEngine()
        tokens = line.split()
        for t in tokens:
            if engine.f_entropy.evaluate(t) >= 0.7:
                return True
        return False


class BenchmarkSuite:
    def __init__(self):
        self.engine = SCSEngine()
        self.regex_baseline = SingleFactorRegexBaseline()
        self.entropy_baseline = SingleFactorEntropyBaseline()

    def generate_dataset(self) -> List[BenchmarkItem]:
        dataset = []

        # Positive Samples (True Secrets)
        dataset.append(BenchmarkItem(
            line="DEBUG DATABASE_PASSWORD=MyP@ssw0rd123 connected to db",
            contains_secret=True,
            description="DB Password in Debug Dump"
        ))
        dataset.append(BenchmarkItem(
            line="INFO Config loaded AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLEwJalrXUtnFEMI",
            contains_secret=True,
            description="AWS Access Key"
        ))
        dataset.append(BenchmarkItem(
            line="DEBUG Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            contains_secret=True,
            description="JWT Token"
        ))
        dataset.append(BenchmarkItem(
            line="ERROR Failed request stripe_secret=sk_test_abcdefghijklmnopqrstuvwxyz",
            contains_secret=True,
            description="Stripe Live API Key"
        ))
        dataset.append(BenchmarkItem(
            line="DEBUG Loaded private_key=-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----",
            contains_secret=True,
            description="PEM Private Key"
        ))
        dataset.append(BenchmarkItem(
            line="INFO User token updated api_key=ghp_1234567890abcdefghijklmnopqrstuvwxyz",
            contains_secret=True,
            description="GitHub PAT"
        ))

        # Negative Samples (Non-Secrets, UUIDs, IDs, English text)
        dataset.append(BenchmarkItem(
            line="INFO Processed request order_id=550e8400-e29b-41d4-a716-446655440000 status=success",
            contains_secret=False,
            description="UUID Order ID"
        ))
        dataset.append(BenchmarkItem(
            line="DEBUG trace_id=c0a80101-4096-11ec-81d3-0242ac130003 duration=45ms",
            contains_secret=False,
            description="Trace ID in Debug"
        ))
        dataset.append(BenchmarkItem(
            line="INFO GET /users/1024 HTTP/1.1 response status=200 duration=12ms",
            contains_secret=False,
            description="Standard HTTP Access Log"
        ))
        dataset.append(BenchmarkItem(
            line="ERROR Connection timeout to host db.prod.internal port=5432 retry=3 attempt=2",
            contains_secret=False,
            description="Database Timeout Error Log"
        ))
        dataset.append(BenchmarkItem(
            line="INFO Session initialized user_id=usr_99882211 correlation_id=corr_88776655",
            contains_secret=False,
            description="Session IDs"
        ))

        # Generate additional synthetic variations for benchmark scale (Total ~100 items)
        for i in range(40):
            # Synthetic clean log lines
            uid = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
            dataset.append(BenchmarkItem(
                line=f"INFO [worker-{i}] Task completed transaction_id=tx_{uid} duration={random.randint(5, 120)}ms",
                contains_secret=False,
                description="Synthetic Clean Task Log"
            ))
            # Synthetic secret lines
            sec = "".join(random.choices(string.ascii_letters + string.digits + "!@#$", k=16))
            dataset.append(BenchmarkItem(
                line=f"DEBUG [worker-{i}] Connecting with database_password={sec} to host=db-{i}.local",
                contains_secret=True,
                description="Synthetic Secret Log"
            ))

        return dataset

    def evaluate_detector(self, name: str, dataset: List[BenchmarkItem], predict_fn) -> dict:
        tp = fp = tn = fn = 0
        latencies = []

        for item in dataset:
            t0 = time.perf_counter()
            is_detected = predict_fn(item.line)
            t_ms = (time.perf_counter() - t0) * 1000
            latencies.append(t_ms)

            if item.contains_secret and is_detected:
                tp += 1
            elif not item.contains_secret and is_detected:
                fp += 1
            elif not item.contains_secret and not is_detected:
                tn += 1
            else:
                fn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        false_mask_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        latencies.sort()
        n = len(latencies)
        avg_lat = sum(latencies) / n
        p95_lat = latencies[int(n * 0.95) - 1]
        p99_lat = latencies[int(n * 0.99) - 1]

        return {
            "name": name,
            "total_lines": n,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "false_mask_rate": round(false_mask_rate, 4),
            "avg_latency_ms": round(avg_lat, 4),
            "p95_latency_ms": round(p95_lat, 4),
            "p99_latency_ms": round(p99_lat, 4),
        }

    def run_all(self):
        dataset = self.generate_dataset()
        print("=========================================================================")
        print("  LOGSHIELD BENCHMARKING SUITE — MULTI-FACTOR VS BASELINES")
        print("=========================================================================")
        print(f"Total benchmark log lines: {len(dataset)}\n")

        # 1. LogShield SCS Multi-Factor
        def logshield_predict(line: str) -> bool:
            results = self.engine.extract_and_score(line)
            return any(r.decision in ("MASK", "FLAG") for r in results)

        res_logshield = self.evaluate_detector("LogShield SCS (Multi-Factor)", dataset, logshield_predict)

        # 2. Baseline 1: Regex Only
        def regex_predict(line: str) -> bool:
            return self.regex_baseline.is_secret(line)

        res_regex = self.evaluate_detector("Baseline 1 (Regex-Only)", dataset, regex_predict)

        # 3. Baseline 2: Entropy Only
        def entropy_predict(line: str) -> bool:
            return self.entropy_baseline.is_secret(line)

        res_entropy = self.evaluate_detector("Baseline 2 (Entropy-Only)", dataset, entropy_predict)

        results = [res_logshield, res_regex, res_entropy]

        # Display Comparison Table
        print(f"{'Detector Model':<30} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'FMR':<6} | {'Avg (ms)':<8} | {'P95 (ms)':<8}")
        print("-" * 84)
        for r in results:
            print(f"{r['name']:<30} | {r['precision']:<6.4f} | {r['recall']:<6.4f} | {r['f1']:<6.4f} | {r['false_mask_rate']:<6.4f} | {r['avg_latency_ms']:<8.4f} | {r['p95_latency_ms']:<8.4f}")
        print("-" * 84)

        print("\nSUMMARY OF RESULTS:")
        print(f"  • LogShield SCS achieved F1 Score of {res_logshield['f1']:.4f} with {res_logshield['avg_latency_ms']:.4f} ms/line average latency.")
        print(f"  • Multi-factor scoring reduced False Mask Rate to {res_logshield['false_mask_rate']:.4f} compared to Entropy-only's {res_entropy['false_mask_rate']:.4f}.")
        print("=========================================================================\n")


if __name__ == "__main__":
    suite = BenchmarkSuite()
    suite.run_all()
