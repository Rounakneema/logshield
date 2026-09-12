import re

PII_DETECTORS = [
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
     "Email Address", "None", "pii", 1.0),
    (re.compile(r"\+[1-9]\d{0,2}-\d{3}-\d{7,}"),
     "Phone Number", "None", "pii", 1.0),
]
