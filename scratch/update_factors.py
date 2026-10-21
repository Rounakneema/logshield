import re

# 1. Update varname_factor.py
with open("sidecar/logmask/factors/varname_factor.py", "r", encoding="utf-8") as f:
    text = f.read()

target = '"retry", "attempt", "iteration",'
replacement = '"retry", "attempt", "iteration",\n        "pod", "pod_name", "node", "pid", "thread", "namespace",'
if target in text and '"pod"' not in text[text.find(target):text.find(target)+200]:
    text = text.replace(target, replacement, 1)
    with open("sidecar/logmask/factors/varname_factor.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated varname_factor.py successfully")
else:
    print("varname_factor.py already updated or target not found")
