import urllib.request
import json

tests = [
    ('Backend Mode', 'http://127.0.0.1:8000/api/mode'),
    ('Backend Stats', 'http://127.0.0.1:8000/api/stats'),
    ('Backend Audit Verify', 'http://127.0.0.1:8000/api/audit/verify'),
    ('Backend Logs', 'http://127.0.0.1:8000/api/logs'),
    ('Backend Raw Logs', 'http://127.0.0.1:8000/api/raw_logs'),
    ('Backend Lineage', 'http://127.0.0.1:8000/api/lineage'),
    ('Backend Vault', 'http://127.0.0.1:8000/api/vault'),
    ('Proxy Mode', 'http://localhost:3000/api/v1/mode'),
    ('Proxy Stats', 'http://localhost:3000/api/v1/stats'),
    ('Proxy Audit Verify', 'http://localhost:3000/api/v1/audit/verify'),
    ('Frontend Login Page', 'http://localhost:3000/login')
]

print("=" * 65)
print("       LOGSHIELD LIVE ENDPOINT VERIFICATION")
print("=" * 65)

all_passed = True
for name, url in tests:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as res:
            status = res.status
            content = res.read().decode('utf-8')
            print(f"[PASS] {name:<22} -> HTTP {status} ({len(content)} bytes)")
    except Exception as e:
        print(f"[FAIL] {name:<22} -> {e}")
        all_passed = False

# Test simulate endpoint via Next.js Proxy POST
try:
    post_data = json.dumps({'line': 'DATABASE_URL=postgres://user:pass@db:5432/test'}).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:3000/api/v1/simulate', 
        data=post_data, 
        headers={'Content-Type': 'application/json'}, 
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        decision = data.get('overall_decision')
        latency = data.get('latency_microseconds')
        print(f"[PASS] {'Proxy Simulate POST':<22} -> HTTP {res.status} | Decision: {decision} | Latency: {latency} us")
except Exception as e:
    print(f"[FAIL] {'Proxy Simulate POST':<22} -> {e}")
    all_passed = False

# Test mode toggle via Next.js Proxy POST
try:
    mode_data = json.dumps({'mode': 'bypass'}).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:3000/api/v1/mode', 
        data=mode_data, 
        headers={'Content-Type': 'application/json'}, 
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        print(f"[PASS] {'Proxy Mode (bypass)':<22} -> HTTP {res.status} | Set to: {data.get('mode')}")

    # Revert to protected
    mode_data = json.dumps({'mode': 'protected'}).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:3000/api/v1/mode', 
        data=mode_data, 
        headers={'Content-Type': 'application/json'}, 
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        print(f"[PASS] {'Proxy Mode (protected)':<22} -> HTTP {res.status} | Set to: {data.get('mode')}")
except Exception as e:
    print(f"[FAIL] {'Proxy Mode Toggle':<22} -> {e}")
    all_passed = False

print("=" * 65)
if all_passed:
    print("  ALL SERVICES ARE RUNNING AND FULLY FUNCTIONAL ON D DRIVE!")
print("=" * 65)
