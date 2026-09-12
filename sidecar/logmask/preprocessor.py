import json
import urllib.parse
import base64
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class ExtractedToken:
    value: str
    source_key: Optional[str] = None

@dataclass
class PreprocessedLine:
    raw: str
    tokens: List[ExtractedToken] = field(default_factory=list)
    decoded_values: Dict[str, str] = field(default_factory=dict)
    is_json: bool = False
    json_fields: Dict[str, str] = field(default_factory=dict)


class LogPreprocessor:
    """
    Stage 1: Preprocessor
    - JSON field extraction
    - URL decoding
    - Base64 decoding
    - Multi-line block assembly (deferred to Phase 3, currently limits line length)
    """
    
    # 64KB line limit
    MAX_LINE_LENGTH = 65536
    
    def __init__(self):
        self.kv_pattern = re.compile(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*[=:]\s*([^\s,;{}\[\]\"'\\]{8,})"
        )

    def _flatten_json(self, y, parent_key=''):
        """Flattens nested JSON into a single level dict with dot notation."""
        items = {}
        if isinstance(y, dict):
            for k, v in y.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                items.update(self._flatten_json(v, new_key))
        elif isinstance(y, list):
            for i, v in enumerate(y):
                new_key = f"{parent_key}[{i}]"
                items.update(self._flatten_json(v, new_key))
        else:
            items[parent_key] = y
        return items

    def process(self, raw_line: str) -> PreprocessedLine:
        # Line length guard
        if len(raw_line) > self.MAX_LINE_LENGTH:
            raw_line = raw_line[:self.MAX_LINE_LENGTH]

        result = PreprocessedLine(raw=raw_line)
        seen_values = set()

        # 1. Try JSON Parse
        try:
            obj = json.loads(raw_line)
            if isinstance(obj, dict):
                result.is_json = True
                flat_json = self._flatten_json(obj)
                for k, v in flat_json.items():
                    if isinstance(v, str) and len(v) >= 6:
                        result.json_fields[k] = v
                        if v not in seen_values:
                            result.tokens.append(ExtractedToken(value=v, source_key=k))
                            seen_values.add(v)
        except json.JSONDecodeError:
            pass

        # 2. Regular KV Extraction (Fallback/Addition)
        bearer_match = re.search(r"Bearer\s+([A-Za-z0-9_\-\.]{10,})", raw_line, re.IGNORECASE)
        if bearer_match:
            b_val = bearer_match.group(1).strip()
            if b_val not in seen_values:
                result.tokens.append(ExtractedToken(value=b_val, source_key="Bearer"))
                seen_values.add(b_val)

        for match in self.kv_pattern.finditer(raw_line):
            key = match.group(1).strip()
            value = match.group(2).strip()
            if value and len(value) >= 6 and value not in seen_values:
                result.tokens.append(ExtractedToken(value=value, source_key=key))
                seen_values.add(value)

        # 3. Decode URL Encoded Values
        for token in result.tokens:
            decoded_url = urllib.parse.unquote(token.value)
            if decoded_url != token.value and len(decoded_url) >= 6:
                result.decoded_values[token.value] = decoded_url

        # 4. Decode Base64 Encoded Values
        # (Only try decoding if it looks like base64, minimal validation to prevent overhead)
        for token in result.tokens:
            val = token.value
            if len(val) >= 12 and re.match(r"^[A-Za-z0-9+/]+={0,2}$", val):
                try:
                    # Pad to multiple of 4
                    padding_needed = len(val) % 4
                    padded_val = val
                    if padding_needed:
                        padded_val += '=' * (4 - padding_needed)
                    
                    decoded_b64 = base64.b64decode(padded_val).decode('utf-8', errors='strict')
                    # Only accept if it's printable and not the same
                    if len(decoded_b64) >= 6 and decoded_b64 != val and decoded_b64.isprintable():
                        result.decoded_values[token.value] = decoded_b64
                except Exception:
                    pass

        return result
