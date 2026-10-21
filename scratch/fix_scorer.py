with open("sidecar/logmask/scorer.py", "r", encoding="utf-8") as f:
    text = f.read()

SCORING_LOGIC = '''            # Exact-format specific detector override
            if classification.is_specific and not classification.is_context_gated:
                if classification.confidence >= 1.0:
                    score = max(score, 80)
                elif classification.confidence >= 0.85 and (factors["varname"] > 0 or factors["context"] > 0):
                    score = max(score, 60)'''

import re
text = re.sub(
    r'            # Exact-format specific detector override.*?score = max\(score, 60\)',
    SCORING_LOGIC.strip(),
    text,
    flags=re.DOTALL
)

with open("sidecar/logmask/scorer.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed scorer.py successfully!")
