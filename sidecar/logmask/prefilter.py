try:
    import ahocorasick
    HAS_AHOCORASICK = True
except ImportError:
    import warnings
    warnings.warn("[LogShield] pyahocorasick not installed — prefilter running in slow fallback mode. Run: pip install pyahocorasick", RuntimeWarning)
    HAS_AHOCORASICK = False

import json
from pathlib import Path
from .catalog import ALL_SPECIFIC_DETECTORS

_SECRETBENCH_PATH = Path(__file__).parent / "catalog" / "secretbench_761.json"

class CandidateFinder:
    """
    Stage 2: Candidate Finder (Aho-Corasick Pre-filter)
    Runs an O(n) check on log lines to see if they contain any vendor name
    or known sensitive keyword. If not, the line is bypassed entirely, saving CPU.
    """
    def __init__(self):
        self.keywords = set()
        self._build_keywords()
        if HAS_AHOCORASICK:
            self.A = ahocorasick.Automaton()
            for kw in self.keywords:
                self.A.add_word(kw, kw)
            self.A.make_automaton()

    def _build_keywords(self):
        # 1. Core sensitive fields & vendor keywords
        base_keywords = {
            'password', 'passwd', 'secret', 'api_key', 'apikey', 'access_token',
            'auth_token', 'private_key', 'database_password', 'client_secret',
            'token', 'credential', 'jwt', 'bearer', 'authorization',
            'sk_live', 'akia', 'ghp_', 'xoxb', 'eyj', 'begin', 'rsa', 'pem',
            'private', 'cert', 'certificate', 'aws', 'stripe', 'github', 'slack',
            'gitlab', 'openai', 'anthropic', 'gemini', 'postgres', 'mongo', 'redis',
            'mysql', 'snowflake', 'twilio', 'sendgrid', 'datadog', 'sentry', 'azure',
            'gcp', 'vault', 'doppler', 'heroku', 'mailgun', 'paypal', 'razorpay'
        }
        self.keywords.update(base_keywords)

        _name_extraction_stop_words = {
            'key', 'token', 'secret', 'password', 'api', 'with', 'access', 'account',
            'active', 'agent', 'test', 'uuid', 'classic', 'legacy', 'raw', 'info',
            'data', 'host', 'file', 'path', 'user', 'node', 'code', 'link', 'name',
            'type', 'time', 'read', 'write', 'block', 'candidate', 'pattern',
            'generic', 'public', 'system', 'server', 'client', 'service'
        }

        # 2. Extract from Specific Detectors
        for entry in ALL_SPECIFIC_DETECTORS:
            name, company = entry[1], entry[2]
            if company and company.lower() not in {'unknown', 'none'}:
                self.keywords.add(company.lower())
            
            for word in name.lower().split():
                clean_w = ''.join(c for c in word if c.isalnum())
                if len(clean_w) > 3 and clean_w not in _name_extraction_stop_words:
                    self.keywords.add(clean_w)

        # 3. Extract from SecretBench
        if _SECRETBENCH_PATH.exists():
            data = json.loads(_SECRETBENCH_PATH.read_text())
            for p in data.get('patterns', []):
                name = p.get('name', '').lower()
                for word in name.split():
                    clean_w = ''.join(c for c in word if c.isalnum())
                    if len(clean_w) > 3 and clean_w not in _name_extraction_stop_words:
                        self.keywords.add(clean_w)

    def is_candidate(self, line: str) -> bool:
        """
        Runs the pre-filter check over the lowercase line.
        """
        line_lower = line.lower()
        if HAS_AHOCORASICK:
            for _, _ in self.A.iter(line_lower):
                return True
            return False
        else:
            return any(kw in line_lower for kw in self.keywords)
