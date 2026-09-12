"""
Factor 1: Regex Patterns for Known Credential Formats
=======================================================
Weight: 20%

This factor loads all patterns from the unified detector catalog.
It implements a TWO-TIER priority system:

  Tier 1 — Specific Detector (confidence 1.0 or 0.85):
    Vendor-known credential formats (AWS keys, Stripe keys, etc.)
    Returns the detector's own confidence score.

  Tier 2 — Generic Detector (confidence 0.70):
    Fallback heuristic patterns (high entropy, bearer tokens, etc.)
    Returns 0.70 only if no specific detector claimed the token.

The tier system ensures that a Stripe key always wins over a generic
"high entropy" match and carries proper vendor attribution.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from ..catalog import ALL_SPECIFIC_DETECTORS, ALL_GENERIC_DETECTORS

_SECRETBENCH_PATH = Path(__file__).parent.parent / "catalog" / "secretbench_761.json"

# ─────────────────────────────────────────────────────────────────────────────
# Detector Entry type alias for readability
# Each entry: (compiled_pattern, name, company, category, confidence)
# ─────────────────────────────────────────────────────────────────────────────
DetectorEntry = Tuple[re.Pattern, str, str, str, float]


@dataclass
class DetectorMatch:
    """Carries the result of a regex detector hit, including vendor metadata."""
    name:       str
    company:    str
    category:   str
    confidence: float
    is_specific: bool = True   # False for generic detectors


class RegexFactor:
    """
    Evaluates candidate tokens against the full 600+ detector catalog.

    evaluate() returns a (score, metadata) tuple:
      - score: float 0.0–1.0 to be multiplied by this factor's weight (20)
      - metadata: DetectorMatch | None — carries vendor info for SCSResult
    """

    # ── Load catalog at class definition time (compiled once, zero startup cost)
    SPECIFIC_DETECTORS: List[DetectorEntry] = ALL_SPECIFIC_DETECTORS
    GENERIC_DETECTORS:  List[DetectorEntry] = ALL_GENERIC_DETECTORS
    SECRETBENCH_PATTERNS: List[Tuple[str, re.Pattern]] = []
    HIGH_FP_PATTERNS: List[Tuple[str, re.Pattern]] = []

    # ── Keep REGEX_PATTERNS alias for backward compat (scorer Pass 2 loop)
    REGEX_PATTERNS: List[Tuple[re.Pattern, str]] = [
        (pat, name)
        for pat, name, *_ in ALL_SPECIFIC_DETECTORS + ALL_GENERIC_DETECTORS
    ]

    def __init__(self):
        self._load_secretbench()

    @classmethod
    def _load_secretbench(cls):
        if not cls.SECRETBENCH_PATTERNS and not cls.HIGH_FP_PATTERNS and _SECRETBENCH_PATH.exists():
            data = json.loads(_SECRETBENCH_PATH.read_text())
            import warnings
            for p in data['patterns']:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("error", FutureWarning)
                        compiled = re.compile(p['regex'])
                    if p['fp_risk'] == 'HIGH':
                        cls.HIGH_FP_PATTERNS.append((p['name'], compiled))
                    else:
                        cls.SECRETBENCH_PATTERNS.append((p['name'], compiled))
                except (re.error, FutureWarning):
                    pass

    def evaluate(self, token: str, line: str) -> Tuple[float, Optional[DetectorMatch]]:
        """
        Returns (score, DetectorMatch | None).

        Priority:
          1. Check specific detectors first — if hit, return immediately.
          2. Fall back to generic detectors — return with lower confidence.
          3. No match → return (0.0, None).
        """
        # ── Tier 1: Specific detectors ─────────────────────────────────────
        for pat, name, company, category, confidence in self.SPECIFIC_DETECTORS:
            if confidence == 0.0:
                continue  # suppression entry (e.g. AWS example key)
            m = pat.search(line)
            if pat.search(token) or (m and token in m.group(0)):
                return confidence, DetectorMatch(
                    name=name,
                    company=company,
                    category=category,
                    confidence=confidence,
                    is_specific=True,
                )

        # ── Tier 2: SecretBench 761 validated patterns ──────────────────────
        for name, pattern in self.SECRETBENCH_PATTERNS:
            if pattern.search(token):
                return 0.9, DetectorMatch(
                    name=f"SecretBench:{name}",
                    company="Unknown",
                    category="SecretBench",
                    confidence=0.9,
                    is_specific=True,
                )

        # ── Tier 3: High-FP patterns (only if context allows, checking later) ─
        # Note: In a full multi-stage pipeline, context_score is passed here.
        # For now, we only match if there's no context, so we skip them here 
        # unless we add context_score to evaluate().
        # We will add context_score in the full Stage 4 update.

        # ── Tier 4: Generic detectors (only if specific missed) ────────────
        for pat, name, company, category, confidence in self.GENERIC_DETECTORS:
            m = pat.search(line)
            if pat.search(token) or (m and token in m.group(0)):
                return confidence, DetectorMatch(
                    name=name,
                    company=company,
                    category=category,
                    confidence=confidence,
                    is_specific=False,
                )

        return 0.0, None

    def evaluate_line_direct(self, line: str) -> List[Tuple[str, DetectorMatch]]:
        """
        Scan an entire log line against all specific detectors.
        Returns a list of (matched_token, DetectorMatch) pairs.

        Used by scorer's Pass 2 (direct pattern sweep).
        Specific-only — generic detectors are not applied directly to full lines
        to avoid massive false positives on long strings.
        """
        results: List[Tuple[str, DetectorMatch]] = []
        seen: set = set()

        for pat, name, company, category, confidence in self.SPECIFIC_DETECTORS:
            if confidence == 0.0:
                continue
            for m in pat.finditer(line):
                token = m.group(0)
                if token not in seen and len(token) >= 6:
                    seen.add(token)
                    results.append((
                        token,
                        DetectorMatch(
                            name=name,
                            company=company,
                            category=category,
                            confidence=confidence,
                            is_specific=True,
                        )
                    ))

        return results
