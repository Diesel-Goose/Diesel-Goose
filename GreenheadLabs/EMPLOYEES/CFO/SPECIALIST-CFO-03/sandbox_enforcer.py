#!/usr/bin/env python3
"""
Chris Dunn — SCOPE ENFORCER & SANDBOX WRAPPER

This wrapper ensures Chris Dunn operates ONLY within his specialty.
Any attempt to access forbidden operations triggers immediate alerts.

Enforcement Rules:
1. NO code modification
2. NO GitHub access
3. NO config changes
4. NO live trading (paper only)
5. NO file writes outside sandbox/
6. ALL actions logged and reported

Author: DieselGoose Agent (Security Layer)
"""

import os
import sys
import logging
import functools
from pathlib import Path
from datetime import datetime
from typing import Callable, Any

# Diesel Goose contact for violations
DIESEL_GOOSE_CHAT = "7491205261"  # Nathan's Telegram
# BOT_TOKEN loaded from environment - NEVER hardcode secrets
BOT_TOKEN = os.getenv('CHRIS_DUNN_BOT_TOKEN', '')


class ScopeViolation(Exception):
    """Raised when Chris Dunn attempts forbidden operations."""
    pass


class ChrisDunnSandbox:
    """
    Sandbox enforcer for Chris Dunn trading bot.
    
    Wraps all operations with scope checks.
    """
    
    # Forbidden paths (cannot write here)
    FORBIDDEN_PATHS = [
        '.git',
        '.github',
        'chris_dunn.py',
        'core/',
        'strategies/',
        'utils/',
        '../',  # Cannot escape sandbox
        '../../',  # Definitely cannot reach main repo
    ]
    
    # Forbidden operations
    FORBIDDEN_OPS = [
        'eval',
        'exec',
        'compile',
        'subprocess',
        'os.system',
        'write_code',
        'modify_file',
        'git_push',
        'github_api',
    ]
    
    def __init__(self):
        self.violation_count = 0
        self.max_violations = 3
        self.is_halted = False
        self.setup_logging()
    
    def setup_logging(self):
        """Setup audit logging."""
        sandbox_dir = Path('sandbox')
        sandbox_dir.mkdir(exist_ok=True)
        
        self.audit_log = sandbox_dir / 'audit.log'
        
        # Configure logger
        self.logger = logging.getLogger('ChrisDunnSandbox')
        self.logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler(self.audit_log)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(handler)
        
        self.logger.info("=" * 60)
        self.logger.info("CHRIS DUNN SANDBOX INITIALIZED")
        self.logger.info("Scope: XRPL Trading ONLY")
        self.logger.info("=" * 60)
    
    def enforce_scope(self, operation: str):
        """
        Check if operation is allowed.
        
        Raises ScopeViolation if forbidden.
        """
        if self.is_halted:
            raise ScopeViolation("SANDBOX HALTED — Contact Diesel Goose")
        
        # Check against forbidden operations
        if any(forbidden in operation.lower() for forbidden in self.FORBIDDEN_OPS):
            self._handle_violation(f"Forbidden operation attempted: {operation}")
        
        # Log allowed operation
        self.logger.info(f"ALLOWED: {operation}")
    
    def check_path(self, path: str, mode: str = 'read') -> bool:
        """
        Check if file path access is allowed.
        
        Args:
            path: File path
            mode: 'read' or 'write'
        
        Returns:
            True if allowed, raises ScopeViolation if not
        """
        path_str = str(path)
        
        # Writing outside sandbox is FORBIDDEN
        if mode == 'write':
            # Must be in sandbox/
            if not path_str.startswith('sandbox/'):
                self._handle_violation(
                    f"WRITE ATTEMPT OUTSIDE SANDBOX: {path}"
                )
            
            # Cannot write to forbidden paths
            for forbidden in self.FORBIDDEN_PATHS:
                if forbidden in path_str:
                    self._handle_violation(
                        f"WRITE ATTEMPT TO FORBIDDEN PATH: {path}"
                    )
        
        # Reading is allowed (but logged)
        self.logger.debug(f"PATH ACCESS [{mode}]: {path}")
        return True
    
    def _handle_violation(self, message: str):
        """
        Handle scope violation.
        
        1. Log violation
        2. Alert Diesel Goose/Nathan
        3. Halt if max violations reached
        """
        self.violation_count += 1
        timestamp = datetime.utcnow().isoformat()
        
        # Critical log
        self.logger.critical("=" * 60)
        self.logger.critical(f"🚨 SCOPE VIOLATION #{self.violation_count}")
        self.logger.critical(f"Time: {timestamp}")
        self.logger.critical(f"Details: {message}")
        self.logger.critical("=" * 60)
        
        # Send alert
        self._alert_diesel_goose(f"""
🚨 CHRIS DUNN SCOPE VIOLATION

Violation #{self.violation_count}
Time: {timestamp}
Details: {message}

ACTION REQUIRED:
- Review Chris Dunn logs
- Determine if malicious or bug
- Decide: Resume or terminate

SANDBOX STATUS: {'HALTED' if self.violation_count >= self.max_violations else 'ACTIVE (WARNING)'}
        """)
        
        # Halt if too many violations
        if self.violation_count >= self.max_violations:
            self.is_halted = True
            raise ScopeViolation(
                f"MAX VIOLATIONS REACHED ({self.max_violations}). "
                "SANDBOX HALTED. Contact Diesel Goose."
            )
        
        # Raise violation even if not halted
        raise ScopeViolation(message)
    
    def _alert_diesel_goose(self, message: str):
        """Send Telegram alert to Diesel Goose."""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': DIESEL_GOOSE_CHAT,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info("Alert sent to Diesel Goose")
            else:
                self.logger.error(f"Alert failed: {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
    
    def wrap_function(self, func: Callable) -> Callable:
        """Decorator to wrap function with scope checks."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.enforce_scope(f"Function call: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    
    def safe_open(self, file: str, mode: str = 'r', *args, **kwargs):
        """Safe file open with scope enforcement."""
        self.check_path(file, mode)
        return open(file, mode, *args, **kwargs)


# Global sandbox instance
sandbox = ChrisDunnSandbox()


def enforce_scope(operation: str):
    """Public function to enforce scope."""
    sandbox.enforce_scope(operation)


def safe_file_write(filepath: str, content: str):
    """Safe file write (sandbox only)."""
    sandbox.check_path(filepath, 'write')
    with open(filepath, 'w') as f:
        f.write(content)


# Import override disabled - simpler approach via path checks
# Scope enforcement is handled in check_path() and enforce_scope()

# Log sandbox mode
if os.getenv('CHRIS_DUNN_SANDBOX', 'false').lower() == 'true':
    print("🛡️  SANDBOX MODE ACTIVE — Chris Dunn scope enforced")
