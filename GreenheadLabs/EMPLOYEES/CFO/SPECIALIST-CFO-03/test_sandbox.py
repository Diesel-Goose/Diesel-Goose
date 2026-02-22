#!/usr/bin/env python3
"""
Chris Dunn — SCOPE VIOLATION TEST SUITE

Tests to verify sandbox enforcement works correctly.
These tests confirm Chris Dunn CANNOT:
1. Modify code
2. Access GitHub
3. Write outside sandbox
4. Change config
5. Access forbidden modules
"""

import os
import sys
import pytest
from pathlib import Path

# Enable sandbox mode
os.environ['CHRIS_DUNN_SANDBOX'] = 'true'

from sandbox_enforcer import sandbox, ScopeViolation


class TestSandboxEnforcement:
    """Test suite for scope enforcement."""
    
    def test_write_outside_sandbox_blocked(self):
        """Test that writing outside sandbox/ is blocked."""
        with pytest.raises(ScopeViolation):
            sandbox.check_path('../chris_dunn.py', 'write')
    
    def test_write_to_git_blocked(self):
        """Test that writing to .git is blocked."""
        with pytest.raises(ScopeViolation):
            sandbox.check_path('sandbox/.git/config', 'write')
    
    def test_sandbox_write_allowed(self):
        """Test that writing inside sandbox is allowed."""
        assert sandbox.check_path('sandbox/test.txt', 'write') == True
    
    def test_read_anywhere_allowed(self):
        """Test that reading is allowed (but logged)."""
        assert sandbox.check_path('../chris_dunn.py', 'read') == True
    
    def test_forbidden_operation_blocked(self):
        """Test that forbidden operations raise violations."""
        with pytest.raises(ScopeViolation):
            sandbox.enforce_scope("Attempting to use subprocess.call")
    
    def test_allowed_operation_passes(self):
        """Test that allowed operations don't raise."""
        # Should not raise
        sandbox.enforce_scope("Analyzing market data")
    
    def test_violation_count_tracking(self):
        """Test that violations are counted."""
        initial_count = sandbox.violation_count
        
        try:
            sandbox._handle_violation("Test violation")
        except ScopeViolation:
            pass
        
        assert sandbox.violation_count == initial_count + 1


class TestChrisDunnScope:
    """Test Chris Dunn's specific scope limitations."""
    
    def test_cannot_modify_strategy_code(self):
        """Verify Chris Dunn cannot modify strategy files."""
        forbidden_paths = [
            'strategies/market_maker.py',
            'core/xrpl_client.py',
            'chris_dunn.py',
            '../chris_dunn.py',
        ]
        
        for path in forbidden_paths:
            with pytest.raises(ScopeViolation):
                sandbox.check_path(path, 'write')
    
    def test_cannot_access_github(self):
        """Verify GitHub operations are blocked."""
        with pytest.raises(ScopeViolation):
            sandbox.enforce_scope("Calling github_api to push changes")
    
    def test_cannot_execute_shell(self):
        """Verify shell execution is blocked."""
        with pytest.raises(ScopeViolation):
            sandbox.enforce_scope("Using os.system to run command")
    
    def test_can_read_market_data(self):
        """Verify reading market data is allowed."""
        # Should not raise
        sandbox.enforce_scope("Reading XRPL orderbook")
        sandbox.enforce_scope("Fetching price data")
    
    def test_can_log_trades(self):
        """Verify logging trades is allowed."""
        # Should not raise
        sandbox.enforce_scope("Logging trade to CSV")


def run_tests():
    """Run all sandbox tests."""
    print("=" * 60)
    print("🧪 CHRIS DUNN SCOPE ENFORCEMENT TESTS")
    print("=" * 60)
    print()
    
    # Create test sandbox directory
    Path('sandbox').mkdir(exist_ok=True)
    
    # Run tests
    test_classes = [
        TestSandboxEnforcement(),
        TestChrisDunnScope()
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n📦 {test_class.__class__.__name__}")
        print("-" * 40)
        
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                try:
                    method = getattr(test_class, method_name)
                    method()
                    print(f"  ✅ {method_name}")
                    passed += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {e}")
                    failed += 1
    
    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All scope enforcement tests passed!")
        print("Chris Dunn is properly contained.")
    else:
        print("⚠️  Some tests failed — review sandbox_enforcer.py")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
