"""
LogMask — Secret Confidence Score (SCS) Engine
===============================================
Stage 5 & 6: Engine Pipeline Orchestrator
"""

from dataclasses import dataclass
from typing import List, Optional
import os
import json

from .preprocessor import LogPreprocessor
from .prefilter import CandidateFinder
from .classifier import SecretClassifier
from .factors import (
    EntropyFactor,
    VarnameFactor,
    TokenStructFactor,
    EncodingFactor,
)
from .factors.context_factor import ContextEngine

@dataclass
class SCSResult:
    """Full scoring result for a single extracted token."""
    token:         str
    score:         int
    factors:       dict
    decision:      str           # 'MASK' | 'FLAG' | 'PASS'
    # ── Vendor attribution fields ─────────────────────────────────────────
    detector_name: str  = "Unknown"    # e.g. "Stripe Live Secret Key"
    vendor:        str  = "Unknown"    # e.g. "Stripe"
    category:      str  = "other"      # e.g. "payment"
    detector_type: str  = "generic"    # 'specific' | 'generic' | 'heuristic'


class SCSEngine:
    """
    Stage 5 & 6: Orchestrates the multi-stage detection pipeline.
    """
    
    # ── Temporary Hardcoded Weights (Will be replaced by ML model) ──────
    WEIGHTS = {
        "varname": 0,
        "regex": 35,
        "entropy": 14,
        "token_struct": 9,
        "context": 42,
        "encoding": 0,
    }

    def __init__(self):
        # Initialize pipeline stages
        self.preprocessor    = LogPreprocessor()
        self.candidate_finder = CandidateFinder()
        self.context_engine  = ContextEngine()
        self.classifier      = SecretClassifier()
        
        # Remaining factors for Stage 5 features
        self.f_entropy       = EntropyFactor()
        self.f_varname       = VarnameFactor()
        self.f_token_struct  = TokenStructFactor()
        self.f_encoding      = EncodingFactor()

        # Load ML optimized weights if available
        weight_path = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "optimal_weights.json")
        if os.path.exists(weight_path):
            try:
                with open(weight_path, "r") as f:
                    ml_weights = json.load(f)
                    # Verify all required keys exist
                    if all(k in ml_weights for k in self.WEIGHTS.keys()):
                        self.WEIGHTS = ml_weights
            except Exception:
                pass

    def extract_and_score(self, line: str) -> List[SCSResult]:
        """
        Executes the 6-stage pipeline.
        """
        results: List[SCSResult] = []

        # ── Stage 1: Preprocessor ──────────────────────────────────────────
        preprocessed = self.preprocessor.process(line)
        if not preprocessed.tokens:
            return results

        # ── Stage 2: Candidate Finder (Early Exit) ─────────────────────────
        if not self.candidate_finder.is_candidate(line):
            return results

        # Evaluate candidates
        for token_obj in preprocessed.tokens:
            token = token_obj.value
            source_key = token_obj.source_key or ""
            
            # ── Stage 3: Context Engine ──────────────────────────────────────
            # Create a character window (±100 chars) around the token
            idx = line.find(token)
            if idx != -1:
                start = max(0, idx - 100)
                end = min(len(line), idx + len(token) + 100)
                window = line[start:end]
            else:
                window = line
            surrounding = f"{source_key} {window}"
            # Extract log level simply if present
            import re
            m_log = re.match(r'^\s*(DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|CRITICAL)\b', line, re.IGNORECASE)
            log_level = m_log.group(1).lower() if m_log else ''
            
            context_score = self.context_engine.score(token, surrounding, log_level)

            # ── Stage 4: Secret Classifier ───────────────────────────────────
            classification = self.classifier.classify(token, line, context_score)
            
            # ── Stage 5: Confidence Model (SCS) ──────────────────────────────
            factors = {
                "regex":        classification.confidence,
                "varname":      self.f_varname.evaluate(line),
                "entropy":      self.f_entropy.evaluate(token),
                "token_struct": self.f_token_struct.evaluate(token, line),
                "context":      context_score,
                "encoding":     self.f_encoding.evaluate(token),
            }

            raw = sum(factors[f] * self.WEIGHTS[f] for f in factors)
            score = int(min(100, raw))

            # Exact-format specific detector override
            if classification.is_specific and not classification.is_context_gated:
                if classification.confidence >= 1.0:
                    score = max(score, 80)
                elif classification.confidence >= 0.85 and (factors["varname"] > 0 or factors["context"] > 0):
                    score = max(score, 60)

            # ── Stage 6: Decision Gate ───────────────────────────────────────
            if score >= 80:
                decision = "MASK"
            elif score >= 50:
                decision = "FLAG"
            else:
                decision = "PASS"

            # Skip PASS results to save memory
            if decision == "PASS":
                continue

            results.append(SCSResult(
                token=token,
                score=score,
                factors=factors,
                decision=decision,
                detector_name=classification.regex_matched,
                vendor="Unknown", # To be mapped properly later if needed
                category=classification.secret_type,
                detector_type="specific" if classification.is_specific else "generic"
            ))

        return results
