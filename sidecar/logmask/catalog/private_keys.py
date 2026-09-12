"""
Private Key Detectors — Highest Priority
==========================================
PEM/SSH/PGP/cryptographic key headers are unambiguous.
These are checked first before all other detectors.
"""

import re

# fmt: off
PRIVATE_KEY_DETECTORS = [
    # ── Test Key ────────────────────────────────────────────────────────────
    (re.compile(r"-----BEGIN TEST PRIVATE KEY-----"),
     "Test Private Key", "None", "private_key", 1.0),

    # ── RSA ─────────────────────────────────────────────────────────────────
    (re.compile(r"-----BEGIN RSA PRIVATE KEY-----"),
     "RSA Private Key", "None", "private_key", 1.0),

    # ── OpenSSH ──────────────────────────────────────────────────────────────
    (re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----"),
     "OpenSSH Private Key", "None", "private_key", 1.0),

    # ── EC (Elliptic Curve) ──────────────────────────────────────────────────
    (re.compile(r"-----BEGIN EC PRIVATE KEY-----"),
     "EC Private Key", "None", "private_key", 1.0),

    # ── DSA ──────────────────────────────────────────────────────────────────
    (re.compile(r"-----BEGIN DSA PRIVATE KEY-----"),
     "DSA Private Key", "None", "private_key", 1.0),

    # ── PKCS8 / Generic ──────────────────────────────────────────────────────
    (re.compile(r"-----BEGIN PRIVATE KEY-----"),
     "Generic Private Key", "None", "private_key", 1.0),

    # ── Encrypted PKCS8 ──────────────────────────────────────────────────────
    (re.compile(r"-----BEGIN ENCRYPTED PRIVATE KEY-----"),
     "Encrypted Private Key", "None", "private_key", 1.0),

    # ── PGP ──────────────────────────────────────────────────────────────────
    (re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----"),
     "PGP Private Key", "None", "private_key", 1.0),

    # ── PuTTY ────────────────────────────────────────────────────────────────
    (re.compile(r"PuTTY-User-Key-File-\d+:\s*(?:ssh-rsa|ssh-dss|ecdsa|ssh-ed25519)"),
     "PuTTY Private Key", "None", "private_key", 1.0),

    # ── Fernet (Python cryptography lib) ─────────────────────────────────────
    (re.compile(r"[A-Za-z0-9_\-]{43}="),  # 32 bytes -> 44 base64url chars with one padding
     "Fernet Key", "None", "private_key", 0.85),

    # ── Django SECRET_KEY (50-char mixed) ────────────────────────────────────
    (re.compile(r"(?:SECRET_KEY\s*=\s*['\"]?)([A-Za-z0-9!@#$%^&*()_+\-=]{40,60})"),
     "Django Secret Key", "None", "private_key", 0.85),

    # ── Laravel APP_KEY (base64:...) ─────────────────────────────────────────
    (re.compile(r"base64:[A-Za-z0-9+/]{43}="),
     "Laravel APP_KEY", "None", "private_key", 1.0),

    # ── Rails SECRET_KEY_BASE (128 hex chars) ────────────────────────────────
    (re.compile(r"(?:secret_key_base\s*[:=]\s*)[0-9a-f]{128}"),
     "Rails Secret Key Base", "None", "private_key", 1.0),

    # ── Rails master.key (32 hex chars) ──────────────────────────────────────
    (re.compile(r"\b[0-9a-f]{32}\b"),
     "Rails Master Key (candidate)", "None", "private_key", 0.85),

    # ── ASP.NET machineKey (decryptionKey / validationKey) ───────────────────
    (re.compile(r'(?:decryptionKey|validationKey)\s*=\s*"[0-9A-F]{48,128}"'),
     "ASP.NET Machine Key", "Microsoft", "private_key", 1.0),

    # ── AES Cipher Key (raw 128/192/256-bit hex) ──────────────────────────────
    (re.compile(r"\b[0-9a-fA-F]{32}(?:[0-9a-fA-F]{16}|[0-9a-fA-F]{32})?\b"),
     "AES Cipher Key (candidate)", "None", "private_key", 0.85),
]
# fmt: on
