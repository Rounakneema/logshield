"""
Stage 4: Secret Classifier
==========================
Uses regex patterns to determine the secret type and confidence.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import re

from .factors.regex_factor import RegexFactor, DetectorMatch

@dataclass
class SecretClassification:
    secret_type: str
    confidence: float
    regex_matched: str
    is_context_gated: bool
    is_specific: bool


class SecretClassifier:
    """
    Stage 4: Secret Classifier
    Evaluates candidate tokens against the regex catalog.
    """
    def __init__(self):
        self.regex_factor = RegexFactor()

    def classify(self, token: str, line: str, context_score: float) -> SecretClassification:
        """
        Executes Pass 1, 2, and 3 based on context_score.
        """
        # ── Pass 1: Specific detectors ─────────────────────────────────────
        for pat, name, company, category, confidence in self.regex_factor.SPECIFIC_DETECTORS:
            if confidence == 0.0:
                continue
            
            is_match = False
            if pat.search(token):
                is_match = True
            else:
                for m in pat.finditer(line):
                    if token in m.group(0):
                        is_match = True
                        break
                        
            if is_match:
                return SecretClassification(
                    secret_type=category,
                    confidence=confidence,
                    regex_matched=name,
                    is_context_gated=False,
                    is_specific=True
                )

        # ── Pass 2: SecretBench 755 validated patterns ──────────────────────
        for name, pattern in self.regex_factor.SECRETBENCH_PATTERNS:
            if pattern.search(token):
                return SecretClassification(
                    secret_type="SecretBench",
                    confidence=0.9,
                    regex_matched=f"SecretBench:{name}",
                    is_context_gated=False,
                    is_specific=True
                )

        # ── Pass 3: High-FP patterns (only if context > 0.5) ────────────────
        if context_score > 0.5:
            for name, pattern in self.regex_factor.HIGH_FP_PATTERNS:
                m = pattern.search(token)
                if m:
                    return SecretClassification(
                        secret_type="SecretBench_HighFP",
                        confidence=0.7,
                        regex_matched=f"ContextGated:{name}",
                        is_context_gated=True,
                        is_specific=True
                    )

        # ── Pass 4: Generic detectors ──────────────────────────────────────
        for pat, name, company, category, confidence in self.regex_factor.GENERIC_DETECTORS:
            is_match = False
            if pat.search(token):
                is_match = True
            else:
                for m in pat.finditer(line):
                    if token in m.group(0):
                        is_match = True
                        break
            
            if is_match:
                return SecretClassification(
                    secret_type=category,
                    confidence=confidence,
                    regex_matched=name,
                    is_context_gated=False,
                    is_specific=False
                )

        return SecretClassification(
            secret_type="Unknown",
            confidence=0.0,
            regex_matched="None",
            is_context_gated=False,
            is_specific=False
        )
