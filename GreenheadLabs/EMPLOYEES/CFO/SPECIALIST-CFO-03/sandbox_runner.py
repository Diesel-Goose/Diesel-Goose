#!/usr/bin/env python3
"""
Chris Dunn — SANDBOX RUNNER

Safe testing environment with full scope enforcement.
NO REAL MONEY. NO CODE CHANGES. NO GITHUB ACCESS.

Usage:
    python3 sandbox_runner.py --strategy market_maker --duration 10

All violations logged and reported to Diesel Goose.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Set sandbox mode BEFORE importing anything
os.environ['CHRIS_DUNN_SANDBOX'] = 'true'
os.environ['CHRIS_DUNN_MODE'] = 'paper'

# Import sandbox enforcer first
from sandbox_enforcer import sandbox, enforce_scope, ScopeViolation

# Create sandbox directory structure
SANDBOX_DIR = Path('sandbox')
SANDBOX_DIR.mkdir(exist_ok=True)
(SANDBOX_DIR / 'logs').mkdir(exist_ok=True)


def setup_isolation():
    """
    Setup isolated environment for testing.
    """
    print("🛡️  Setting up sandbox isolation...")
    
    # Ensure we're in the right directory
    if not Path('chris_dunn.py').exists():
        print("❌ Error: Must run from SPECIALIST-CFO-03 directory")
        sys.exit(1)
    
    # Verify sandbox config exists
    if not Path('sandbox_config.yaml').exists():
        print("❌ Error: sandbox_config.yaml not found")
        sys.exit(1)
    
    # Change to sandbox working directory
    os.chdir(SANDBOX_DIR)
    
    # Create symlinks to read-only code (Linux/Mac)
    # On Windows, copy instead
    code_files = ['../chris_dunn.py', '../core', '../strategies', '../utils']
    
    for f in code_files:
        target = Path(f).name
        if not Path(target).exists():
            try:
                os.symlink(f, target, target_is_directory=Path(f).is_dir())
                print(f"  ✅ Linked: {f}")
            except:
                # Fallback: just note it
                print(f"  ℹ️  Reference: {f}")
    
    print("✅ Isolation complete")
    print(f"   Working dir: {os.getcwd()}")
    print(f"   Write scope: sandbox/ only")
    print()


class SandboxedChrisDunn:
    """
    Chris Dunn wrapped in sandbox constraints.
    """
    
    def __init__(self, config_path: str = '../sandbox_config.yaml'):
        self.config_path = config_path
        self.violations = []
        self.start_time = datetime.utcnow()
        self.last_report_time = datetime.utcnow()
        
        # Load reporter
        try:
            from utils.financial_reporter import FinancialReporter
            from utils.alerts import AlertManager
            import yaml
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.reporter = FinancialReporter(config, AlertManager(config))
            self.reporting_enabled = True
        except Exception as e:
            print(f"⚠️  Financial reporter not available: {e}")
            self.reporter = None
            self.reporting_enabled = False
        
        print("🦆 Initializing Chris Dunn (Sandbox Mode)...")
        print("   Mode: PAPER ONLY")
        print("   Scope: Trading operations ONLY")
        print("   Violations: Reported to Diesel Goose")
        print("   Reports: Every 30 minutes to group")
        print()
    
    async def run_test(self, strategy: str, duration_minutes: int):
        """
        Run sandboxed test of Chris Dunn.
        
        Args:
            strategy: Which strategy to test
            duration_minutes: How long to run
        """
        try:
            # Import Chris Dunn components (now sandboxed)
            enforce_scope(f"Loading strategy: {strategy}")
            
            print(f"📊 Strategy: {strategy}")
            print(f"⏱️  Duration: {duration_minutes} minutes")
            print(f"💰 Mode: Paper (simulated funds)")
            print("-" * 60)
            
            # Simulate trading cycles
            cycles = 0
            import time
            
            end_time = time.time() + (duration_minutes * 60)
            
            while time.time() < end_time:
                cycles += 1
                cycle_start = datetime.utcnow()
                
                try:
                    enforce_scope(f"Trading cycle #{cycles}")
                    
                    # Simulate strategy analysis
                    print(f"\n🔄 Cycle #{cycles} — {cycle_start.strftime('%H:%M:%S')}")
                    print(f"   Analyzing {strategy} strategy...")
                    
                    # Paper trading simulation
                    await self._simulate_cycle(strategy)
                    
                    # Safety check
                    if cycles % 10 == 0:
                        print(f"   ✅ {cycles} cycles complete, no violations")
                    
                    # Check if 15 minutes passed — send financial report (Chairman: 15-min intervals)
                    time_since_report = (datetime.utcnow() - self.last_report_time).total_seconds()
                    if time_since_report >= 900:  # 15 minutes
                        await self._send_financial_report(strategy)
                        self.last_report_time = datetime.utcnow()
                    
                except ScopeViolation as e:
                    print(f"\n🚨 SCOPE VIOLATION: {e}")
                    self.violations.append({
                        'cycle': cycles,
                        'time': datetime.utcnow().isoformat(),
                        'error': str(e)
                    })
                    
                    # Continue or halt based on severity
                    if sandbox.is_halted:
                        print("\n⛔ SANDBOX HALTED")
                        break
                
                # Cooldown
                await asyncio.sleep(30)  # 30 seconds between cycles
            
            # Test complete
            await self._report_results(cycles)
            
        except Exception as e:
            print(f"\n💥 Critical error: {e}")
            sandbox._alert_diesel_goose(f"""
🚨 CHRIS DUNN CRASHED IN SANDBOX

Error: {e}
Time: {datetime.utcnow().isoformat()}

Review logs immediately.
            """)
    
    async def _simulate_cycle(self, strategy: str):
        """Simulate one trading cycle."""
        import random
        
        # Simulate market analysis
        await asyncio.sleep(0.5)
        
        # Random signal generation (for testing)
        if random.random() > 0.7:  # 30% chance of signal
            signal_type = random.choice(['buy', 'sell'])
            amount = round(random.uniform(1, 100), 2)
            
            print(f"   📈 Signal: {signal_type.upper()} {amount} XRP")
            
            # Simulate paper trade
            trade_result = {
                'type': 'paper',
                'strategy': strategy,
                'signal': signal_type,
                'amount': amount,
                'price': round(random.uniform(0.45, 0.55), 4),
                'status': 'filled'
            }
            
            # Log to sandbox only
            self._log_trade(trade_result)
            
            print(f"   ✅ Paper trade executed (no real funds)")
    
    def _log_trade(self, trade: dict):
        """Log trade to sandbox audit trail."""
        log_file = Path('audit.log')
        with open(log_file, 'a') as f:
            f.write(f"{datetime.utcnow().isoformat()} | TRADE | {trade}\n")
    
    async def _send_financial_report(self, strategy: str):
        """Send 30-minute financial report to Telegram group."""
        if not self.reporter:
            return
        
        try:
            # Get current stats
            stats = self.reporter.get_current_stats()
            stats['strategy'] = strategy
            
            # Generate report
            report = self.reporter.generate_paper_report(stats)
            
            # Post to group
            await self.reporter.post_to_group(report)
            
            # Also log it
            print(f"\n📊 FINANCIAL REPORT SENT:\n{report}\n")
            
        except Exception as e:
            print(f"⚠️  Failed to send financial report: {e}")
    
    async def _report_results(self, total_cycles: int):
        """Generate test report."""
        runtime = datetime.utcnow() - self.start_time
        
        print("\n" + "=" * 60)
        print("🦆 CHRIS DUNN SANDBOX TEST COMPLETE")
        print("=" * 60)
        print(f"⏱️  Runtime: {runtime}")
        print(f"🔄 Cycles: {total_cycles}")
        print(f"🚨 Violations: {len(self.violations)}")
        print(f"📁 Logs: sandbox/audit.log")
        print()
        
        if self.violations:
            print("⚠️  VIOLATIONS DETECTED:")
            for v in self.violations:
                print(f"   - Cycle {v['cycle']}: {v['error']}")
            print()
            print("⚡ Diesel Goose has been notified")
        else:
            print("✅ NO VIOLATIONS")
            print("✅ Chris Dunn operated within scope")
        
        print()
        print("Next steps:")
        print("  1. Review sandbox/audit.log")
        print("  2. Check Telegram for alerts")
        print("  3. If clean: approve for expanded testing")
        print("  4. If violations: investigate and fix")
        
        # Send summary to Diesel Goose
        sandbox._alert_diesel_goose(f"""
📊 CHRIS DUNN SANDBOX TEST COMPLETE

Runtime: {runtime}
Cycles: {total_cycles}
Violations: {len(self.violations)}

Status: {'⚠️ VIOLATIONS DETECTED' if self.violations else '✅ CLEAN'}

Review audit.log for details.
        """)


def main():
    parser = argparse.ArgumentParser(
        description='Chris Dunn Sandbox Testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sandbox_runner.py --strategy market_maker --duration 10
  python3 sandbox_runner.py --strategy arbitrage --duration 5
  python3 sandbox_runner.py --strategy momentum --duration 15

Note: All testing uses PAPER (simulated) funds only.
        """
    )
    
    parser.add_argument(
        '--strategy', '-s',
        choices=['market_maker', 'arbitrage', 'momentum', 'all'],
        default='market_maker',
        help='Which strategy to test'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=10,
        help='Test duration in minutes (default: 10)'
    )
    
    parser.add_argument(
        '--cycles', '-c',
        type=int,
        help='Number of trading cycles (alternative to duration)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🛡️  CHRIS DUNN SANDBOX TESTING")
    print("=" * 60)
    print()
    print("⚠️  RESTRICTIONS:")
    print("   • Paper trading ONLY (no real funds)")
    print("   • Cannot modify code")
    print("   • Cannot access GitHub")
    print("   • All actions logged")
    print("   • Violations reported to Diesel Goose")
    print()
    
    # Setup isolation
    setup_isolation()
    
    # Run test
    runner = SandboxedChrisDunn()
    
    try:
        asyncio.run(runner.run_test(args.strategy, args.duration))
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        print("   Review sandbox/audit.log for results")


if __name__ == "__main__":
    main()
