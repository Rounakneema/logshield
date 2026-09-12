"""
Factor 6: Encoding Indicator (Decodable Base64)
Weight: 5%
"""

import base64


class EncodingFactor:
    """
    Evaluates whether token is valid, decodable Base64 of meaningful length.
    """

    def evaluate(self, token: str) -> float:
        if len(token) < 16:
            return 0.0
        padded = token + "=" * (4 - len(token) % 4) if len(token) % 4 else token
        try:
            decoded = base64.b64decode(padded, validate=True)
            if len(decoded) >= 12:
                return 0.8
        except Exception:
            pass
        return 0.0
