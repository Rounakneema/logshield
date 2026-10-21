with open("sidecar/logmask/factors/context_factor.py", "r", encoding="utf-8") as f:
    text = f.read()

target = "        'customer_id': -0.8, 'commit': -1.0, 'payload': -1.0, 'revision': -1.0,\n        'pod': -1.0, 'node': -1.0, 'pid': -1.0, 'thread': -1.0, 'namespace': -0.8\n    }"
replacement = "        'customer_id': -0.8, 'commit': -1.0, 'payload': -1.0, 'revision': -1.0\n    }"

if target in text:
    text = text.replace(target, replacement, 1)
    with open("sidecar/logmask/factors/context_factor.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Cleaned context_factor.py successfully")
else:
    print("Target not found in context_factor.py")
