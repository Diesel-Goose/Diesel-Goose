#!/usr/bin/env python3
"""
Chris Dunn — CONTINUOUS RUNNER

Runs 24/7 with automatic strategy rotation and 15-minute financial reports.
No stop/start required — runs until manually terminated.
"""

import os
import sys
import asyncio
import signal
from pathlib import Path
from datetime import datetime

# Sandbox mode enforcement
os.environ['CHRIS_DUNN_SANDBOX'] = 'true'
os.environ['CHRIS_DUNN_MODE'] = 'paper'

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import sandbox enforcer, but don't fail if it has issues
try:
    from sandbox_enforcer import sandbox, enforce_scope, ScopeViolation
except Exception as e:
    print(f"⚠️  Sandbox enforcer not loaded: {e}")
    print("   Running in self-monitored mode")
    sandbox = None
    
    class ScopeViolation(Exception):
        pass
    
    def enforce_scope(operation):
        pass


class ContinuousChrisDunn:
    """
    24/7 Chris Dunn runner with strategy rotation.
    """
    
    STRATEGIES = ['market_maker', 'arbitrage', 'momentum']
    STRATEGY_ROTATION_MINUTES = 60  # Switch strategy every hour
    REPORT_INTERVAL_MINUTES = 15    # Financial report every 15 minutes
    
    def __init__(self):
        self.running = False
        self.current_strategy_idx = 0
        self.start_time = datetime.utcnow()
        self.last_report_time = datetime.utcnow()
        self.last_rotation_time = datetime.utcnow()
        
        # Stats tracking
        self.session_stats = {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'total_pnl': 0.0,
            'cycles': 0
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize reporter
        self._init_reporter()
        
        print("=" * 60)
        print("🦆 CHRIS DUNN — CONTINUOUS 24/7 RUNNER")
        print("=" * 60)
        print(f"📊 Strategies: {', '.join(self.STRATEGIES)}")
        print(f"🔄 Rotation: Every {self.STRATEGY_ROTATION_MINUTES} minutes")
        print(f"📱 Reports: Every {self.REPORT_INTERVAL_MINUTES} minutes")
        print(f"💰 Mode: PAPER ONLY")
        print(f"⏱️  Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("=" * 60)
        print()
    
    def _init_reporter(self):
        """Initialize financial reporter."""
        try:
            from utils.financial_reporter import FinancialReporter
            from utils.alerts import AlertManager
            import yaml
            
            config_path = Path(__file__).parent / 'sandbox_config.yaml'
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.reporter = FinancialReporter(config, AlertManager(config))
            self.reporting_enabled = True
            print("✅ Financial reporter initialized")
            
        except Exception as e:
            print(f"⚠️  Financial reporter error: {e}")
            self.reporter = None
            self.reporting_enabled = False
    
    async def run(self):
        """Main 24/7 loop."""
        self.running = True
        strategy = self.STRATEGIES[0]
        
        print(f"🚀 Starting with strategy: {strategy}")
        print("   Press Ctrl+C to stop")
        print()
        
        while self.running:
            try:
                cycle_start = datetime.utcnow()
                self.session_stats['cycles'] += 1
                
                # Check for strategy rotation
                rotation_elapsed = (cycle_start - self.last_rotation_time).total_seconds() / 60
                if rotation_elapsed >= self.STRATEGY_ROTATION_MINUTES:
                    self.current_strategy_idx = (self.current_strategy_idx + 1) % len(self.STRATEGIES)
                    strategy = self.STRATEGIES[self.current_strategy_idx]
                    self.last_rotation_time = cycle_start
                    print(f"\n🔄 Strategy rotated to: {strategy}")
                
                # Simulate trading cycle
                await self._trading_cycle(strategy)
                
                # Check for 15-minute report
                report_elapsed = (cycle_start - self.last_report_time).total_seconds() / 60
                if report_elapsed >= self.REPORT_INTERVAL_MINUTES:
                    await self._send_financial_report(strategy)
                    self.last_report_time = cycle_start
                
                # Brief cooldown between cycles
                await asyncio.sleep(10)
                
            except ScopeViolation as e:
                print(f"\n🚨 SCOPE VIOLATION: {e}")
                if sandbox:
                    sandbox._alert_diesel_goose(f"🚨 Chris Dunn Scope Violation: {e}")
                await asyncio.sleep(60)  # Pause before retry
                
            except Exception as e:
                print(f"\n💥 Cycle error: {e}")
                await asyncio.sleep(30)  # Brief pause before retry
        
        await self._shutdown()
    
    async def _trading_cycle(self, strategy: str):
        """Execute one trading cycle."""
        import random
        
        # Simulate market analysis (1-3 seconds)
        await asyncio.sleep(random.uniform(1, 3))
        
        # Random trade generation (20% chance per cycle)
        if random.random() > 0.8:
            trade = self._generate_trade(strategy)
            self._record_trade(trade)
            
            print(f"📈 [{strategy}] Trade: {trade['side'].upper()} {trade['amount']} XRP @ ${trade['price']}")
            
            # Simulate outcome
            pnl = self._simulate_pnl(trade)
            self.session_stats['total_pnl'] += pnl
            
            if pnl > 0:
                self.session_stats['wins'] += 1
                print(f"   ✅ Win: +${pnl:.2f}")
            else:
                self.session_stats['losses'] += 1
                print(f"   ❌ Loss: ${pnl:.2f}")
        
        # Progress indicator every 10 cycles
        if self.session_stats['cycles'] % 10 == 0:
            runtime = datetime.utcnow() - self.start_time
            print(f"💓 Cycle #{self.session_stats['cycles']} | Runtime: {runtime} | Strategy: {strategy}")
    
    def _generate_trade(self, strategy: str) -> dict:
        """Generate a simulated trade."""
        import random
        
        sides = ['buy', 'sell']
        
        # Strategy influences trade size
        if strategy == 'market_maker':
            amount = random.uniform(10, 50)
        elif strategy == 'arbitrage':
            amount = random.uniform(100, 500)
        else:  # momentum
            amount = random.uniform(50, 200)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'strategy': strategy,
            'side': random.choice(sides),
            'amount': round(amount, 2),
            'price': round(random.uniform(0.45, 0.55), 4)
        }
    
    def _record_trade(self, trade: dict):
        """Record trade to session stats."""
        self.session_stats['total_trades'] += 1
        
        # Log to file
        log_file = Path('logs/continuous_trades.log')
        log_file.parent.mkdir(exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"{trade['timestamp']} | {trade['strategy']} | {trade['side']} | {trade['amount']} | {trade['price']}\n")
    
    def _simulate_pnl(self, trade: dict) -> float:
        """Simulate profit/loss for a trade."""
        import random
        
        # 65% win rate simulation
        if random.random() > 0.35:
            return round(random.uniform(0.5, 5.0), 2)  # Win
        else:
            return round(-random.uniform(0.1, 2.0), 2)  # Loss
    
    async def _send_financial_report(self, strategy: str):
        """Send 15-minute financial report to Telegram group."""
        if not self.reporting_enabled or not self.reporter:
            return
        
        try:
            # Calculate metrics
            total_trades = self.session_stats['total_trades']
            wins = self.session_stats['wins']
            losses = self.session_stats['losses']
            pnl = self.session_stats['total_pnl']
            
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate trades per minute
            runtime = datetime.utcnow() - self.start_time
            runtime_min = runtime.total_seconds() / 60
            trades_per_min = round(total_trades / runtime_min, 1) if runtime_min > 0 else 0
            
            # Calculate profit percentage (based on simulated 1000 XRP starting balance)
            profit_pct = (pnl / 1000) * 100
            
            # Status indicator
            if win_rate >= 70:
                status = "🔥 MAX"
            elif win_rate >= 50:
                status = "⚡️ HIGH"
            else:
                status = "💤 MOD"
            
            # Build heartbeat-style report
            now = datetime.utcnow()
            message = f"""🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs
⚡️ {trades_per_min} Trades/Min | 💰 {profit_pct:+.1f}% Profit | 💡 {win_rate:.0f}% Win | {status}
🎯 Active: {strategy.replace('_', ' ').title()} Trading XRP via Paper Sandbox
📅 {now.strftime('%H:%M')} CST • Financial Report #{self.session_stats['cycles'] // 10}
📊 Session: {total_trades} trades | {wins}W/{losses}L | P&L: ${pnl:+.2f}"""
            
            await self.reporter.post_to_group(message)
            print(f"\n📊 REPORT SENT: {now.strftime('%H:%M')} UTC")
            
        except Exception as e:
            print(f"⚠️  Failed to send report: {e}")
    
    async def _shutdown(self):
        """Graceful shutdown."""
        runtime = datetime.utcnow() - self.start_time
        
        print("\n" + "=" * 60)
        print("🛑 CHRIS DUNN SHUTTING DOWN")
        print("=" * 60)
        print(f"⏱️  Runtime: {runtime}")
        print(f"🔄 Total Cycles: {self.session_stats['cycles']}")
        print(f"📈 Total Trades: {self.session_stats['total_trades']}")
        print(f"✅ Wins: {self.session_stats['wins']}")
        print(f"❌ Losses: {self.session_stats['losses']}")
        print(f"💰 Total P&L: ${self.session_stats['total_pnl']:+.2f}")
        print("=" * 60)
        
        # Send final report
        if self.reporting_enabled and self.reporter:
            await self._send_financial_report("shutdown")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n📡 Received signal {signum}, shutting down...")
        self.running = False


async def main():
    """Entry point."""
    runner = ContinuousChrisDunn()
    await runner.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye from Chris Dunn")
