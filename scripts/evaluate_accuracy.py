#!/usr/bin/env python3

import os
import sys
import time

# Ensure we can import sidecar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sidecar.logmask.scorer import SCSEngine

def main():
    log_file = "logs.txt"
    truth_file = "ground_truth.txt"

    if not os.path.exists(log_file) or not os.path.exists(truth_file):
        print(f"Error: Need both {log_file} and {truth_file}")
        sys.exit(1)

    print("Loading ground truth...")
    truth_labels = {} # line_number -> label
    with open(truth_file, "r", encoding="utf-8") as f:
        next(f) # skip header
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 2:
                truth_labels[int(parts[0])] = parts[1]

    engine = SCSEngine()
    
    # Metrics
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    
    print("Evaluating LogShield against dataset...")
    start_time = time.time()
    
    with open(log_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            results = engine.extract_and_score(line)
            
            # Decide action: if any token is MASK, action is REDACT
            action = "ALLOW"
            if results:
                top_score = max(r.score for r in results)
                top_decision = max(results, key=lambda r: r.score).decision
                if top_decision in ["MASK", "FLAG"]:
                    action = "REDACT"
            
            expected = truth_labels.get(i, "NORMAL")
            
            is_secret = expected in ["SECRET", "PII"] # Secrets should be REDACTed
            did_redact = (action == "REDACT")
            
            if is_secret and did_redact:
                tp += 1
            elif is_secret and not did_redact:
                fn += 1
                if fn <= 100:
                    with open("fn.log", "a", encoding="utf-8") as f_fn:
                        f_fn.write(f"Line {i}: {line}\n")
            elif not is_secret and did_redact:
                fp += 1
                if fp <= 100:
                    with open("fp.log", "a", encoding="utf-8") as f_fp:
                        f_fp.write(f"Line {i}: {line}\n")
            elif not is_secret and not did_redact:
                tn += 1
                
            if i % 1000 == 0:
                print(f"Processed {i} lines...")

    elapsed = time.time() - start_time
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    print("\n========================================================")
    print(" LOGSHIELD ACCURACY REPORT")
    print("========================================================")
    print(f" Total Lines Evaluated : {tp+fp+tn+fn:,}")
    print(f" Total Time            : {elapsed:.2f} seconds ({((tp+fp+tn+fn)/elapsed):.0f} lines/sec)")
    print("--------------------------------------------------------")
    print(f" True Positives (TP)   : {tp:,}")
    print(f" False Positives (FP)  : {fp:,}")
    print(f" True Negatives (TN)   : {tn:,}")
    print(f" False Negatives (FN)  : {fn:,}")
    print("--------------------------------------------------------")
    print(f" Precision             : {precision:.4f}")
    print(f" Recall                : {recall:.4f}")
    print(f" F1-Score              : {f1:.4f}")
    print("========================================================")

if __name__ == "__main__":
    main()
