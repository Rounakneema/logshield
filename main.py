"""
LogShield Root Main Entry Point
================================
Wrapper for sidecar/main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sidecar.main import LogShieldInterceptor

if __name__ == "__main__":
    interceptor = LogShieldInterceptor()
    interceptor.run()
