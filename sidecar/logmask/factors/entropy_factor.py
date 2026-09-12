"""
Factor 3: Shannon Entropy Calculation
Weight: 20%
"""

import math
import re


class EntropyFactor:
    """
    Calculates Shannon entropy in bits per character.
    Real keys/passwords tend to be > 3.5 bits/char.
    Plain English is around 1.5–2.5.
    UUIDs are ~3.3.
    """

    def evaluate(self, token: str) -> float:
        if len(token) < 8:
            return 0.0
            
        # Exclude standard UUIDs
        if len(token) == 36 and re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", token, re.IGNORECASE):
            return 0.0
            
        freq: dict = {}
        for c in token:
            freq[c] = freq.get(c, 0) + 1
        total = len(token)
        entropy = -sum((n / total) * math.log2(n / total) for n in freq.values())

        if entropy >= 3.5:
            return 1.0
        elif entropy >= 2.8:
            return 0.7
        elif entropy >= 2.0:
            return 0.3
        return 0.0
