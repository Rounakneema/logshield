SCORING_LOGIC = '''            # Token-specific varname evaluation
            varname_score = 0.0
            if source_key:
                if source_key in self.f_varname.HIGH_RISK_VARNAMES:
                    varname_score = 1.0
                elif source_key in self.f_varname.LOW_RISK_VARNAMES:
                    varname_score = 0.0
            else:
                varname_score = self.f_varname.evaluate(line)

            # ── Stage 5: Confidence Model (SCS) ──────────────────────────────
            factors = {
                "regex":        classification.confidence,
                "varname":      varname_score,
                "entropy":      self.f_entropy.evaluate(token),
                "token_struct": self.f_token_struct.evaluate(token, line),
                "context":      context_score,
                "encoding":     self.f_encoding.evaluate(token),
            }

            raw = sum(factors[f] * self.WEIGHTS[f] for f in factors)
            score = int(min(100, raw))

            # Skip benign infrastructure metadata
            if source_key in INFRA_KEYS and not (classification.is_specific and classification.confidence >= 0.85):
                continue

            # Exact-format specific detector override
            if classification.is_specific and not classification.is_context_gated:
                if classification.confidence >= 0.85:
                    score = max(score, 80)
                elif classification.confidence >= 0.7 and (factors["varname"] > 0 or factors["context"] > 0):
                    score = max(score, 60)
            elif classification.confidence == 0.0 and factors["varname"] == 0.0 and context_score < 0.8:
                # Require high confidence before flagging unidentified tokens
                score = min(score, 45)
'''

with open("sidecar/logmask/scorer.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
# Find from '# Token-specific varname evaluation' to '# ── Stage 6: Decision Gate'
p = re.compile(r'            # Token-specific varname evaluation.*?(?=            # ── Stage 6: Decision Gate)', re.DOTALL)
if p.search(text):
    text = p.sub(SCORING_LOGIC, text)
    with open("sidecar/logmask/scorer.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Re-updated scorer.py successfully!")
else:
    print("Pattern not found")
