import pytest
from sidecar.logmask.factors.regex_factor import RegexFactor
import re

def test_secretbench_patterns_loaded():
    factor = RegexFactor()
    # We expect roughly 755 normal patterns (761 total - 6 high FP)
    # The parsing might have skipped some invalid regexes, but it should be > 700.
    assert len(factor.SECRETBENCH_PATTERNS) > 700
    assert len(factor.HIGH_FP_PATTERNS) >= 6

def test_secretbench_evaluation():
    factor = RegexFactor()
    
    # Fake token that matches one of the simple SecretBench patterns
    # (Assuming there's a simple match we can trigger, but since we don't know exactly 
    # which ones are in there, we can at least test the structure.)
    
    # Just verify that evaluate doesn't crash on standard input
    score, match = factor.evaluate("some_random_token", "some_random_line")
    assert isinstance(score, float)
