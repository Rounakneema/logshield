import sys, os, time
sys.path.insert(0, '.')
from sidecar.logmask.scorer import SCSEngine

truth = {}
with open('ground_truth.txt', 'r', encoding='utf-8') as f:
    next(f)
    for i, line in enumerate(f, 1):
        if i > 5000: break
        parts = line.strip().split('|')
        truth[int(parts[0])] = parts[1]

engine = SCSEngine()

SENSITIVE_KEYS = {
    'password', 'passwd', 'secret', 'api_key', 'apikey', 'token',
    'access_token', 'private_key', 'credential', 'auth_token', 'jwt',
    'bearer', 'client_secret', 'database_password', 'db_password',
    'aws_secret_access_key', 'stripe_secret_key'
}

tp, fp, tn, fn = 0, 0, 0, 0
start = time.time()
with open('logs.txt', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if i > 5000: break
        results = engine.extract_and_score(line.strip())
        
        # Filter results with our proposed rule:
        filtered_results = []
        for r in results:
            # Check if token had regex match or sensitive key
            has_regex = (r.factors.get('regex', 0.0) >= 0.7)
            # Find if token in line was preceded by sensitive key
            line_str = line.strip().lower()
            token_lower = r.token.lower()
            has_sensitive_key = any(f"{sk}=" in line_str or f"{sk}:" in line_str for sk in SENSITIVE_KEYS)
            
            if has_regex or (has_sensitive_key and r.factors.get('entropy', 0.0) >= 0.7):
                filtered_results.append(r)
                
        action = 'ALLOW'
        if filtered_results:
            top = max(filtered_results, key=lambda r: r.score)
            if top.decision in ['MASK', 'FLAG']:
                action = 'REDACT'
                
        expected = truth.get(i, 'NORMAL')
        is_secret = expected in ['SECRET', 'PII']
        did_redact = (action == 'REDACT')
        if is_secret and did_redact: tp += 1
        elif is_secret and not did_redact: fn += 1
        elif not is_secret and did_redact: fp += 1
        else: tn += 1

prec = tp / (tp + fp) if (tp + fp) else 0.0
rec = tp / (tp + fn) if (tp + fn) else 0.0
f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
print(f'Evaluated {tp+fp+tn+fn} lines in {time.time()-start:.2f}s')
print(f'TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}')
print(f'Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1:.4f}')
