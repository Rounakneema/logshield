"""
Factor 4: Token Structural Shapes
Weight: 15%
"""

import re


class TokenStructFactor:
    """
    Evaluates token structure for key shapes like bcrypt hashes, long hex blobs, or complex passwords.
    """

    def evaluate(self, token: str, line: str = "") -> float:
        # bcrypt hash
        if re.match(r"^\$2[aby]\$\d{2}\$.{53}$", token):
            return 1.0
        # Long hex string (32+ hex chars)
        if re.match(r"^[a-fA-F0-9]{32,}$", token):
            if len(token) == 32:
                # ETag / MD5 exemption
                line_lower = line.lower()
                if any(kw in line_lower for kw in ['etag', 'content-md5', 'checksum']):
                    return 0.0
                if not any(kw in line_lower for kw in ['password', 'secret', 'key', 'token']):
                    return 0.5
            return 1.0
        # Complex password shape (mixed uppercase, lowercase, digits, special chars)
        has_upper = bool(re.search(r"[A-Z]", token))
        has_lower = bool(re.search(r"[a-z]", token))
        has_digit = bool(re.search(r"[0-9]", token))
        has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", token))
        if len(token) >= 14 and (has_upper + has_lower + has_digit + has_special) >= 3:
            return 1.0
        # Long alphanumeric with special chars
        if len(token) >= 16 and re.match(r"^[A-Za-z0-9+/=_\-]+$", token):
            return 0.7
        return 0.0
