import csv
import random
import uuid
import os
import sys

# Ensure sidecar is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sidecar.logmask.scorer import SCSEngine

def generate_positive_lines(count=250):
    templates = [
        "DEBUG Connecting to database: postgres://admin:MyP@ssw0rd123!@db-host:5432/prod",
        "INFO  Session started with token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        "ERROR Failed to authenticate. AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLEwJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "DEBUG Payment intent failed. STRIPE_SECRET_KEY=sk_test_51J9xXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "INFO  [Config] Github Token configured: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "DUMP  Environment dump: slack_token=x0xb-123456789012-1234567890123-xxxxxxxxxxxxxxxxxxxxxxxx",
        "DEBUG User login request. password={password}",
        "WARN  Invalid API key provided: api_key={api_key}",
    ]
    
    passwords = [
        "Tr0ub4dor&3", "correcthorsebatterystaple", "P@ssw0rd123!", "Sup3rS3cr3t#99"
    ]
    api_keys = [
        "aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5z",
        "1234567890abcdef1234567890abcdef"
    ]
    
    lines = []
    for _ in range(count):
        tmpl = random.choice(templates)
        if "{password}" in tmpl:
            line = tmpl.format(password=random.choice(passwords) + str(random.randint(100, 999)))
        elif "{api_key}" in tmpl:
            line = tmpl.format(api_key=random.choice(api_keys))
        else:
            line = tmpl
        lines.append(line)
    return lines

def generate_negative_lines(count=250):
    templates = [
        "INFO  Request processed successfully. trace_id={uuid}",
        "DEBUG HTTP GET /api/v1/users/123 - 200 OK duration=45ms",
        "WARN  Cache miss for key=user_profile_12345",
        "INFO  Connection established to host=192.168.1.5 port=8080",
        "DEBUG File downloaded. ETag: {md5}",
        "INFO  Startup complete. Mode=Production Version=1.4.2",
        "ERROR Timeout waiting for service dependency_id={uuid}",
        "DEBUG Payload size: {size} bytes",
        "INFO  Image uploaded: data:image/png;base64,{base64}",
        "DEBUG Session generated hash={md5}",
        "WARN  Invalid input received id={uuid}",
        "INFO  Client connected. session_id={high_entropy}"
    ]
    
    lines = []
    for _ in range(count):
        tmpl = random.choice(templates)
        if "{uuid}" in tmpl:
            line = tmpl.format(uuid=str(uuid.uuid4()))
        elif "{md5}" in tmpl:
            # Generate a 32 char hex string
            line = tmpl.format(md5="".join(random.choices("0123456789abcdef", k=32)))
        elif "{size}" in tmpl:
            line = tmpl.format(size=random.randint(100, 100000))
        elif "{base64}" in tmpl:
            import base64
            line = tmpl.format(base64=base64.b64encode(os.urandom(64)).decode('utf-8'))
        elif "{high_entropy}" in tmpl:
            line = tmpl.format(high_entropy="".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*", k=24)))
        else:
            line = tmpl
        lines.append(line)
    return lines

def generate_dataset(output_path, total_samples=500):
    pos_lines = generate_positive_lines(total_samples // 2)
    neg_lines = generate_negative_lines(total_samples // 2)
    
    all_lines = [(line, 1) for line in pos_lines] + [(line, 0) for line in neg_lines]
    random.shuffle(all_lines)
    
    engine = SCSEngine()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["line", "token", "varname_score", "regex_score", "entropy_score", "token_struct_score", "context_score", "encoding_score", "label"])
        
        extracted_count = 0
        for line, label in all_lines:
            # We want to extract features. 
            # SCSEngine.extract_and_score drops PASS decisions in Stage 6, 
            # which means negative samples won't be returned.
            # We need to bypass Stage 6 decision dropping for dataset generation.
            
            preprocessed = engine.preprocessor.process(line)
            if not preprocessed.tokens:
                # If it's a negative sample, maybe it didn't even have a KV pair.
                continue
                
            for token_obj in preprocessed.tokens:
                token = token_obj.value
                source_key = token_obj.source_key or ""
                surrounding = f"{source_key} {line}"
                log_level = 'debug' if 'debug' in line.lower() else '' 
                if 'error' in line.lower(): log_level = 'error'
                
                context_score = engine.context_engine.score(token, surrounding, log_level)
                classification = engine.classifier.classify(token, line, context_score)
                
                varname_score = engine.f_varname.evaluate(line)
                entropy_score = engine.f_entropy.evaluate(token)
                token_struct_score = engine.f_token_struct.evaluate(token, line)
                encoding_score = engine.f_encoding.evaluate(token)
                
                writer.writerow([
                    line, token, 
                    varname_score, classification.confidence, entropy_score, 
                    token_struct_score, context_score, encoding_score, label
                ])
                extracted_count += 1
                
    print(f"Generated {extracted_count} feature rows to {output_path}")

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(__file__), "..", "data", "training_dataset.csv")
    generate_dataset(out_file)
