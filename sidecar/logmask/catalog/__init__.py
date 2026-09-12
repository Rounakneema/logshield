"""
LogShield Detector Catalog
===========================
Aggregates all specific and generic detector patterns into unified lists.

Each detector entry is a 5-tuple:
  (compiled_pattern, detector_name, company, category, confidence)

  confidence:
    1.0  — Exact vendor format (known prefix + enforced length)
    0.85 — Structural/partial pattern (heuristic match)
    0.70 — Generic fallback pattern
"""

from .cloud       import CLOUD_DETECTORS
from .ai          import AI_DETECTORS
from .vcs_cicd    import VCS_CICD_DETECTORS
from .database    import DATABASE_DETECTORS
from .messaging   import MESSAGING_DETECTORS
from .payment     import PAYMENT_DETECTORS
from .private_keys import PRIVATE_KEY_DETECTORS
from .generic     import GENERIC_DETECTORS
from .generated_specifics import GENERATED_SPECIFIC_DETECTORS
from .pii         import PII_DETECTORS

# All specific detectors — ordered from highest to lowest confidence
ALL_SPECIFIC_DETECTORS = (
    PRIVATE_KEY_DETECTORS   # PEM headers are unambiguous — highest priority
    + CLOUD_DETECTORS
    + AI_DETECTORS
    + VCS_CICD_DETECTORS
    + DATABASE_DETECTORS
    + MESSAGING_DETECTORS
    + PAYMENT_DETECTORS
    + PII_DETECTORS
    + GENERATED_SPECIFIC_DETECTORS
)

# Generic detectors — applied only when no specific detector matches
ALL_GENERIC_DETECTORS = GENERIC_DETECTORS

__all__ = [
    "ALL_SPECIFIC_DETECTORS",
    "ALL_GENERIC_DETECTORS",
]
