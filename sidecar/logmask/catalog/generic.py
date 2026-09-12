"""
Generic Detectors — Fallback Layer
====================================
Applied only when no Specific Detector claims the token.

Covers: High-Entropy Strings, Generic Password Assignment,
        Bearer Token, Basic Auth (clear & Base64),
        Username:Password Tuple, Generic Encryption Key,
        Generic Database Assignment, X-API-Key header,
        SMTP Credentials, JWT, WireGuard Key,
        Generic CLI Secrets, ConvertTo-SecureString,
        Curl Username:Password, Generic Terraform Variable.
"""

import re

# fmt: off
GENERIC_DETECTORS = [

    # ════════════════════════════════════════════════════════════════════
    # JWT — JSON Web Token
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
     "JSON Web Token", "None", "other", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Bearer Token
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:Authorization|auth):\s*Bearer\s+[A-Za-z0-9_\-\.]{20,}",
                re.IGNORECASE),
     "Bearer Token", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Basic Auth (clear text header)
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:Authorization|auth):\s*Basic\s+[A-Za-z0-9+/]{10,}={0,2}",
                re.IGNORECASE),
     "Base64 Basic Authentication", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Basic Auth String (URL-embedded)
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"https?://[^:\s@/]{3,}:[^@\s/]{6,}@"),
     "Basic Auth String", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Username:Password Tuple
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:username|user|login)\s*[=:]\s*[^\s;,\"']{3,}[\s;,]+"
                r"(?:password|passwd|pass|pwd)\s*[=:]\s*[^\s;,\"']{6,}",
                re.IGNORECASE),
     "Username Password", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Generic Password Assignment
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:password|passwd|pwd|pass)\s*[=:]\s*[\"']?[^\s\"']{8,}",
                re.IGNORECASE),
     "Generic Password", "None", "other", 0.70),

    # ════════════════════════════════════════════════════════════════════
    # Generic Database Assignment
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:db[_\-]?(?:pass|password|secret|key)|database[_\-]?(?:pass|password|uri))\s*[=:]\s*\S{6,}",
                re.IGNORECASE),
     "Generic Database Assignment", "None", "data_storage", 0.70),

    # ════════════════════════════════════════════════════════════════════
    # Generic Encryption Key
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:encryption[_\-]?key|cipher[_\-]?key|aes[_\-]?key|secret[_\-]?key)\s*[=:]\s*[A-Za-z0-9+/=]{16,}",
                re.IGNORECASE),
     "Generic Encryption Key", "None", "other", 0.70),

    # ════════════════════════════════════════════════════════════════════
    # X-API-Key Header
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"[Xx]-[Aa][Pp][Ii]-[Kk]ey\s*:\s*[A-Za-z0-9_\-]{16,}"),
     "X-API-Key Secret", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # SMTP Credentials
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"smtp://[^:\s]+:[^@\s]+@[^/\s]+(?::\d+)?"),
     "SMTP Credentials URI", "None", "other", 0.85),

    (re.compile(r"(?:SMTP_PASSWORD|MAIL_PASSWORD|EMAIL_PASSWORD)\s*[=:]\s*\S{6,}",
                re.IGNORECASE),
     "SMTP Password Env Var", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Generic High-Entropy Secret (long random alphanumeric)
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"),
     "Generic High Entropy Secret", "None", "other", 0.70),

    # ════════════════════════════════════════════════════════════════════
    # Authentication Tuple (key=val pair with auth keywords)
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:api[_\-]?key|apikey|api[_\-]?secret|auth[_\-]?token|access[_\-]?token)\s*[=:]\s*[A-Za-z0-9_\-]{16,}",
                re.IGNORECASE),
     "Authentication Tuple", "None", "other", 0.70),

    # ════════════════════════════════════════════════════════════════════
    # ConvertTo-SecureString (PowerShell)
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"ConvertTo-SecureString\s+[\"'][^\"']+[\"']"),
     "ConvertTo-SecureString Password", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Curl Username:Password
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"curl\s+(?:-u|--user)\s+[A-Za-z0-9_@.]{3,}:[^\s]{6,}"),
     "Curl Username Password", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Generic CLI Secret
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:--(?:token|secret|password|api[_\-]?key)|--auth)\s+[A-Za-z0-9_\-]{16,}"),
     "Generic CLI Secret", "None", "other", 0.70),

    # ════════════════════════════════════════════════════════════════════
    # Generic Terraform Variable Secret
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"variable\s+\"[^\"]*(?:secret|password|key|token)[^\"]*\"\s*\{[^}]*sensitive\s*=\s*true",
                re.IGNORECASE | re.DOTALL),
     "Generic Terraform Variable Secret", "Terraform", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # WireGuard Private Key
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"PrivateKey\s*=\s*[A-Za-z0-9+/]{43}="),
     "WireGuard Private Key", "None", "private_key", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Company Email + Password pair
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}:[^\s]{8,}"),
     "Company Email Password", "None", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # ServiceNow Generic Password
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:SN_PASSWORD|SERVICENOW_PASSWORD|servicenow[_\-]?password)\s*[=:]\s*\S{8,}",
                re.IGNORECASE),
     "ServiceNow Generic Password", "ServiceNow", "other", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Base64 High-Entropy Secret
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})"),
     "Base64 Generic High Entropy Secret", "None", "other", 0.70),
]
# fmt: on
