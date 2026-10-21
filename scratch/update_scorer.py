INFRA_BLOCK = '''        INFRA_KEYS = {
            'pod', 'node', 'thread', 'pid', 'namespace', 'service', 'level',
            'status', 'code', 'version', 'host', 'port', 'method', 'path',
            'ip', 'client_ip', 'user_agent'
        }

        # Evaluate candidates
        for token_obj in preprocessed.tokens:
            token = token_obj.value
            source_key = (token_obj.source_key or "").lower().strip()
'''

SCORING_LOGIC = '''            # Token-specific varname evaluation if source_key is known
            varname_score = self.f_varname.evaluate(line)
            if source_key:
                if source_key in self.f_varname.HIGH_RISK_VARNAMES:
                    varname_score = 1.0
                elif source_key in self.f_varname.LOW_RISK_VARNAMES:
                    varname_score = 0.0

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
            elif factors["varname"] >= 1.0 and (factors["entropy"] >= 0.7 or factors["token_struct"] >= 0.7):
                score = max(score, 80)
            elif classification.confidence == 0.0 and factors["varname"] == 0.0 and context_score < 0.8:
                # Require high confidence before flagging unidentified tokens
                score = min(score, 45)
'''

with open("sidecar/logmask/scorer.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace candidates loop header
target1 = '''        # Evaluate candidates
        for token_obj in preprocessed.tokens:
            token = token_obj.value
            source_key = token_obj.source_key or ""'''

if target1 in text:
    text = text.replace(target1, INFRA_BLOCK.rstrip(), 1)
else:
    print("Warning: target1 not found")

# Replace factors and overrides
target2 = '''            # ── Stage 5: Confidence Model (SCS) ──────────────────────────────
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
                    score = max(score, 60)'''

if target2 in text:
    text = text.replace(target2, SCORING_LOGIC.rstrip(), 1)
    with open("sidecar/logmask/scorer.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated scorer.py successfully!")
else:
    print("Warning: target2 not found")
