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
    raw_slice: Optional[str] = None
    evasion_type: Optional[str] = None

@dataclass
class PreprocessedLine:
    raw: str
    tokens: List[ExtractedToken] = field(default_factory=list)
    decoded_values: Dict[str, str] = field(default_factory=dict)
    is_json: bool = False
    json_fields: Dict[str, str] = field(default_factory=dict)


class LogPreprocessor:
    """
    Stage 1: Preprocessor & Adaptive Evasion Defense
    - JSON field extraction
    - URL decoding & de-obfuscation
    - Base64 normalization
    - Hex escape decoding (\x41\x42 -> AB)
    - Adaptive Sliding Window Token Fusion (defeating delimiter & whitespace splits)
    """
    
    # 64KB line limit
    MAX_LINE_LENGTH = 65536
    
    def __init__(self):
        self.kv_pattern = re.compile(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*[=:]\s*([^\s,;{}\[\]\"\'\\():=]{8,})"
        )
        self.split_kv_pattern = re.compile(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*[=:]\s*([^\s,;{}\[\]\"\'\\():=]{2,})\s+([^\s,;{}\[\]\"\'\\():=]{2,})(?:\s+([^\s,;{}\[\]\"\'\\():=]{2,}))?"
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
                            result.tokens.append(ExtractedToken(value=v, source_key=k, raw_slice=v))
                            seen_values.add(v)
        except json.JSONDecodeError:
            pass

        # 2. Regular KV Extraction (Fallback/Addition)
        bearer_match = re.search(r"Bearer\s+([A-Za-z0-9_\-\.]{10,})", raw_line, re.IGNORECASE)
        if bearer_match:
            b_val = bearer_match.group(1).strip()
            if b_val not in seen_values:
                result.tokens.append(ExtractedToken(value=b_val, source_key="Bearer", raw_slice=b_val))
                seen_values.add(b_val)

        for match in self.kv_pattern.finditer(raw_line):
            key = match.group(1).strip()
            value = match.group(2).strip()
            if value and len(value) >= 6 and value not in seen_values:
                result.tokens.append(ExtractedToken(value=value, source_key=key, raw_slice=value))
                seen_values.add(value)

        # 3. Adaptive Token Window Fusion (Defeating Delimiter & Whitespace Split Attacks)
        for match in self.split_kv_pattern.finditer(raw_line):
            key = match.group(1).strip()
            part1 = match.group(2).strip()
            part2 = match.group(3).strip()
            part3 = match.group(4).strip() if match.group(4) else ""
            
            # Handle Authorization header schemes (Bearer, Basic, Token)
            if part1.lower() in {"basic", "bearer", "token"}:
                if len(part2) >= 8 and part2 not in seen_values:
                    result.tokens.append(ExtractedToken(
                        value=part2,
                        source_key=key,
                        raw_slice=part2,
                        evasion_type=None
                    ))
                    seen_values.add(part2)
                continue

            # Bigram window (part1 + part2)
            raw_2 = f"{part1} {part2}"
            fused_2 = f"{part1}{part2}".strip()
            if len(fused_2) >= 12 and fused_2 not in seen_values:
                result.tokens.append(ExtractedToken(
                    value=fused_2,
                    source_key=key,
                    raw_slice=raw_2,
                    evasion_type="delimiter_split"
                ))
                seen_values.add(fused_2)

            # Trigram window (part1 + part2 + part3)
            if part3:
                raw_3 = f"{part1} {part2} {part3}"
                fused_3 = f"{part1}{part2}{part3}".strip()
                if len(fused_3) >= 16 and fused_3 not in seen_values:
                    result.tokens.append(ExtractedToken(
                        value=fused_3,
                        source_key=key,
                        raw_slice=raw_3,
                        evasion_type="delimiter_split"
                    ))
                    seen_values.add(fused_3)

        # 4. Hex Escape Normalization (\\x41\\x4b\\x49\\x41 -> AKIA)
        if "\\x" in raw_line:
            # 4a. Key-Value Hex escape: key=\x41\x4b...
            kv_hex = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*[=:]\s*([^\s,;{}\[\]\"'=]+)")
            for match in kv_hex.finditer(raw_line):
                key = match.group(1).strip()
                val = match.group(2).strip()
                if "\\x" in val:
                    try:
                        unescaped = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), val)
                        if len(unescaped) >= 8 and unescaped.isprintable() and unescaped not in seen_values:
                            result.tokens.append(ExtractedToken(
                                value=unescaped,
                                source_key=key,
                                raw_slice=val,
                                evasion_type="hex_escaped"
                            ))
                            seen_values.add(unescaped)
                    except Exception:
                        pass

            # 4b. Standalone contiguous hex-escaped sequence: (?:\x[0-9a-fA-F]{2}){4,}
            raw_hex = re.compile(r"(?:\\x[0-9a-fA-F]{2}){4,}")
            for match in raw_hex.finditer(raw_line):
                val = match.group(0)
                try:
                    unescaped = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), val)
                    if len(unescaped) >= 8 and unescaped.isprintable() and unescaped not in seen_values:
                        result.tokens.append(ExtractedToken(
                            value=unescaped,
                            source_key="",
                            raw_slice=val,
                            evasion_type="hex_escaped"
                        ))
                        seen_values.add(unescaped)
                except Exception:
                    pass

        # 4c. Free-Form & Specific Pattern Candidate Token Extraction
        # Captures credentials emitted without a 'key=' prefix (e.g. AWS access keys, Stripe keys, JWTs, URIs)
        SPECIFIC_STANDALONE = [
            (re.compile(r"(?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}"), "aws_access_key_id"),
            (re.compile(r"(?:sk|pk)_(?:live|test)_[0-9a-zA-Z]{24,}"), "stripe_api_key"),
            (re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}"), "github_pat"),
            (re.compile(r"github_pat_[A-Za-z0-9_]{82}"), "github_fine_grained_pat"),
            (re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}"), "slack_token"),
            (re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "jwt_token"),
            (re.compile(r"(?:postgres|postgresql|mysql|mongodb|redis)://[^\s,;\"\'<>]+"), "database_uri"),
        ]
        for pat, key_label in SPECIFIC_STANDALONE:
            for match in pat.finditer(raw_line):
                val = match.group(0).strip()
                if val and val not in seen_values:
                    result.tokens.append(ExtractedToken(value=val, source_key=key_label, raw_slice=val))
                    seen_values.add(val)

        # 4d. General high-entropy word boundary tokens
        general_word_pat = re.compile(r"(?:^|[\s,;{}\[\]\"\'()<>=|/])([A-Za-z0-9_\-\.]{14,})(?:$|[\s,;{}\[\]\"\'()<>=|/])")
        for match in general_word_pat.finditer(raw_line):
            val = match.group(1).strip()
            # Skip timestamps and numeric sequences
            if val and val not in seen_values and not re.match(r"^\d{4}-\d{2}-\d{2}", val) and not val.isdigit():
                start_pos = match.start(1)
                before = raw_line[:start_pos].strip()
                words = before.split()
                inferred = words[-1].strip(":=[](),\"'") if words else "standalone"
                result.tokens.append(ExtractedToken(value=val, source_key=inferred, raw_slice=val))
                seen_values.add(val)

        # 5. Decode URL Encoded Values
        for token in list(result.tokens):
            try:
                decoded_url = urllib.parse.unquote(token.value)
                if decoded_url != token.value and len(decoded_url) >= 6 and decoded_url not in seen_values:
                    result.decoded_values[token.value] = decoded_url
                    result.tokens.append(ExtractedToken(
                        value=decoded_url,
                        source_key=token.source_key,
                        raw_slice=token.raw_slice or token.value,
                        evasion_type="url_encoded"
                    ))
                    seen_values.add(decoded_url)
            except Exception:
                pass

        # 6. Decode Base64 Encoded Values
        for token in list(result.tokens):
            val = token.value
            if len(val) >= 12 and re.match(r"^[A-Za-z0-9+/]+={0,2}$", val):
                try:
                    padding_needed = len(val) % 4
                    padded_val = val + ('=' * (4 - padding_needed) if padding_needed else '')
                    decoded_b64 = base64.b64decode(padded_val).decode('utf-8', errors='strict')
                    if len(decoded_b64) >= 6 and decoded_b64 != val and decoded_b64.isprintable() and decoded_b64 not in seen_values:
                        result.decoded_values[token.value] = decoded_b64
                        result.tokens.append(ExtractedToken(
                            value=decoded_b64,
                            source_key=token.source_key,
                            raw_slice=token.raw_slice or token.value,
                            evasion_type="base64_encoded"
                        ))
                        seen_values.add(decoded_b64)
                except Exception:
                    pass

        return result
