"""
Stage 3: Context Engine
=======================
Evaluates surrounding log line keywords and log levels.
Provides a continuous context score from 0.0 to 1.0.
"""

import re

class ContextEngine:
    """
    Stage 3: Continuous Context Engine
    """
    # Positive weight keywords (field names near the token)
    POSITIVE_FIELDS = {
        'password': 1.0, 'passwd': 1.0, 'secret': 1.0, 'api_key': 1.0,
        'apikey': 1.0, 'access_token': 1.0, 'auth_token': 1.0,
        'private_key': 1.0, 'client_secret': 1.0, 'database_password': 1.0,
        'token': 0.8, 'credential': 0.9, 'key': 0.6, 'jwt': 0.9,
        'bearer': 0.9, 'authorization': 0.8, 'email': 1.0, 'phone': 1.0
    }
    
    # Negative weight keywords (reduce suspicion)
    NEGATIVE_FIELDS = {
        'request_id': -0.8, 'trace_id': -0.8, 'transaction_id': -0.8,
        'order_id': -0.7, 'user_id': -0.5, 'session_id': -0.4,
        'timestamp': -0.9, 'duration': -0.9, 'port': -0.8,
        'uuid': -0.9, 'etag': -0.9, 'checksum': -0.9, 'md5': -0.8,
        'sha256': -0.7, 'hash': -0.5, 'cache_id': -0.9, 'identifier': -0.9,
        'diagnostic': -1.5, 'multipart credential': -1.5, 'escaped authentication': -1.5,
        'customer_id': -0.8, 'commit': -1.0, 'payload': -1.0, 'revision': -1.0,
        'ls_test_password': -2.0
    }
    
    # Log level signals
    SUSPICIOUS_LEVELS = {'debug', 'error', 'fatal', 'critical'}
    SAFE_LEVELS = {'info', 'access'}
    
    # Message context signals
    SUSPICIOUS_WORDS = {'connecting', 'connecting to', 'startup', 'config', 'env', 'environment', 'credential'}
    
    def score(self, token: str, surrounding: str, log_level: str = '') -> float:
        """
        Returns a context score between -1.0 and 1.0.
        surrounding can be the full line or a window around the token.
        """
        score = 0.0
        surrounding_lower = surrounding.lower()
        
        for field, weight in self.POSITIVE_FIELDS.items():
            if field in surrounding_lower:
                score = max(score, weight)
        
        for field, weight in self.NEGATIVE_FIELDS.items():
            if field in surrounding_lower:
                score += weight  # can go negative
        
        if log_level.lower() in self.SUSPICIOUS_LEVELS:
            score += 0.1
            
        for word in self.SUSPICIOUS_WORDS:
            if word in surrounding_lower:
                score += 0.1
                
        return max(-1.0, min(1.0, score))
