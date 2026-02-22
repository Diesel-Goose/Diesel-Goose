"""
Chris Dunn — Ultimate XRPL Trading Specialist
Main orchestrator for multi-strategy trading bot.

Author: DieselGoose Agent for Greenhead Labs
Role: Specialist-CFO-03
Strategies: Market Making, Arbitrage, Momentum
"""

import asyncio
import yaml
import logging
import sys
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from core.xrpl_client import XRPLClient
from core.risk_manager import RiskManager
from core.order_manager import OrderManager
from core.market_data import MarketData
from strategies.market_maker import MarketMaker
from strategies.arbitrage_scanner import ArbitrageScanner
from strategies.momentum_trader import MomentumTrader
from utils.logger import TradingLogger
from utils.metrics import MetricsTracker
from utils.alerts import AlertManager


class ChrisDunnTrader:
    """
    Ultimate XRPL Trading Specialist
    
    Chris Dunn executes three core strategies:
    1. Market Making - Capture bid-ask spreads
    2. Arbitrage - Exploit price discrepancies  
    3. Momentum - Ride trend waves
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.mode = self.config.get('trading', {}).get('mode', 'paper')
        
        # Core components
        self.xrpl = XRPLClient(self.config)
        self.risk = RiskManager(self.config)
        self.orders = OrderManager(self.config)
        self.market = MarketData(self.config)
        
        # Strategy modules
        self.strategies = {}
        self._init_strategies()
        
        # Utilities
        self.logger = TradingLogger(self.config)
        self.metrics = MetricsTracker(self.config)
        self.alerts = AlertManager(self.config)
        
        # State
        self.running = False
        self.cycle_count = 0
        self.start_time = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, path: str) -> Dict:
        """Load trading configuration."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {path}")
            print("   Copy config.yaml.example to config.yaml and edit")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML in config: {e}")
            sys.exit(1)
    
    def _init_strategies(self):
        """Initialize enabled strategies."""
        enabled = self.config.get('strategies', {}).get('enabled', [])
        
        if 'market_maker' in enabled:
            self.strategies['market_maker'] = MarketMaker(
                self.config, self.xrpl, self.risk, self.orders
            )
            self.logger.info("✅ Market Maker strategy initialized")
        
        if 'arbitrage' in enabled:
            self.strategies['arbitrage'] = ArbitrageScanner(
                self.config, self.xrpl, self.risk, self.market
            )
            self.logger.info("✅ Arbitrage Scanner initialized")
        
        if 'momentum' in enabled:
            self.strategies['momentum'] = MomentumTrader(
                self.config, self.xrpl, self.risk, self.market
            )
            self.logger.info("✅ Momentum Trader initialized")
        
        if not self.strategies:
            self.logger.warning("⚠️ No strategies enabled! Check config.yaml")
    
    async def start(self):
        """Start trading operations."""
        self.running = True
        self.start_time = datetime.utcnow()
        
        self.logger.info("=" * 60)
        self.logger.info("🦆 Chris Dunn — Ultimate XRPL Trader")
        self.logger.info(f"Mode: {self.mode.upper()}")
        self.logger.info(f"Strategies: {list(self.strategies.keys())}")
        self.logger.info("=" * 60)
        
        # Send startup alert
        await self.alerts.send(
            f"🚀 Chris Dunn started\n"
            f"Mode: {self.mode}\n"
            f"Strategies: {', '.join(self.strategies.keys())}"
        )
        
        # Pre-flight checks
        if not await self._preflight_checks():
            self.logger.error("❌ Pre-flight checks failed")
            return
        
        # Main trading loop
        try:
            await self._trading_loop()
        except Exception as e:
            self.logger.error(f"💥 Fatal error: {e}")
            await self.alerts.send(f"🚨 Chris Dunn crashed: {e}")
            raise
    
    async def _preflight_checks(self) -> bool:
        """Run pre-flight safety checks."""
        self.logger.info("🔍 Running pre-flight checks...")
        
        # Check XRPL connection
        if not await self.xrpl.ping():
            self.logger.error("❌ Cannot connect to XRPL")
            return False
        self.logger.info("✅ XRPL connection OK")
        
        # Check wallet balance
        balance = await self.xrpl.get_balance()
        if balance < self.config.get('risk', {}).get('min_balance_xrp', 100):
            self.logger.warning(f"⚠️ Low XRP balance: {balance} XRP")
        else:
            self.logger.info(f"✅ Balance: {balance} XRP")
        
        # Check risk limits
        if not self.risk.validate_config():
            self.logger.error("❌ Risk configuration invalid")
            return False
        self.logger.info("✅ Risk limits configured")
        
        # Paper mode warning
        if self.mode == 'paper':
            self.logger.info("📊 PAPER TRADING MODE — No real funds at risk")
        else:
            self.logger.warning("💰 LIVE TRADING MODE — Real funds at risk!")
            await self.alerts.send("⚠️ LIVE TRADING ACTIVE — Monitor closely")
        
        return True
    
    async def _trading_loop(self):
        """Main trading loop."""
        cooldown = self.config.get('trading', {}).get('cooldown_seconds', 60)
        
        while self.running:
            self.cycle_count += 1
            cycle_start = datetime.utcnow()
            
            self.logger.info(f"\n🔄 Cycle #{self.cycle_count} — {cycle_start}")
            
            try:
                # Update market data
                await self.market.update()
                
                # Run each strategy
                for name, strategy in self.strategies.items():
                    if not self.running:
                        break
                    
                    try:
                        signals = await strategy.analyze()
                        if signals:
                            self.logger.info(f"📈 {name} generated {len(signals)} signals")
                            await self._execute_signals(name, signals)
                    except Exception as e:
                        self.logger.error(f"❌ {name} error: {e}")
                
                # Update metrics
                await self.metrics.update()
                
                # Check daily limits
                if self.risk.daily_limit_reached():
                    self.logger.warning("🛑 Daily loss limit reached — Stopping")
                    await self.alerts.send("🛑 Daily loss limit hit — Trading halted")
                    break
                
                # Log cycle summary
                cycle_time = (datetime.utcnow() - cycle_start).total_seconds()
                self.logger.info(f"✅ Cycle complete in {cycle_time:.2f}s")
                
            except Exception as e:
                self.logger.error(f"💥 Cycle error: {e}")
            
            # Cooldown
            if self.running:
                await asyncio.sleep(cooldown)
    
    async def _execute_signals(self, strategy_name: str, signals: List[Dict]):
        """Execute trading signals."""
        for signal in signals:
            # Risk check
            if not self.risk.approve_trade(signal):
                self.logger.info(f"⛔ Risk manager blocked trade: {signal}")
                continue
            
            if self.mode == 'paper':
                # Paper trade — simulate execution
                self.logger.info(f"📊 PAPER TRADE: {strategy_name} — {signal}")
                await self.metrics.record_paper_trade(strategy_name, signal)
            else:
                # Live trade — requires approval
                self.logger.info(f"💰 LIVE TRADE: {strategy_name} — {signal}")
                result = await self.orders.execute(signal)
                if result:
                    await self.metrics.record_live_trade(strategy_name, signal, result)
                    await self.alerts.send(
                        f"✅ Trade executed\n"
                        f"Strategy: {strategy_name}\n"
                        f"Type: {signal.get('type')}\n"
                        f"Amount: {signal.get('amount')}"
                    )
    
    def stop(self):
        """Stop trading gracefully."""
        self.logger.info("🛑 Stopping Chris Dunn...")
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"\n📡 Received signal {signum}")
        self.stop()
    
    async def shutdown(self):
        """Cleanup and shutdown."""
        runtime = datetime.utcnow() - self.start_time if self.start_time else None
        
        self.logger.info("=" * 60)
        self.logger.info("🦆 Chris Dunn shutting down")
        self.logger.info(f"Cycles completed: {self.cycle_count}")
        if runtime:
            self.logger.info(f"Runtime: {runtime}")
        
        # Cancel open orders
        await self.orders.cancel_all()
        
        # Final metrics
        pnl = await self.metrics.get_pnl()
        self.logger.info(f"P&L: {pnl}")
        
        # Send shutdown alert
        await self.alerts.send(
            f"🛑 Chris Dunn stopped\n"
            f"Cycles: {self.cycle_count}\n"
            f"P&L: {pnl}"
        )
        
        self.logger.info("=" * 60)


async def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Chris Dunn — XRPL Trading Bot')
    parser.add_argument('--config', '-c', default='config.yaml', help='Config file path')
    parser.add_argument('--mode', '-m', choices=['paper', 'live'], help='Trading mode override')
    parser.add_argument('--strategy', '-s', help='Single strategy to run (market_maker/arbitrage/momentum)')
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with CLI args
    if args.mode:
        config['trading']['mode'] = args.mode
    if args.strategy:
        config['strategies']['enabled'] = [args.strategy]
    
    # Create and start trader
    trader = ChrisDunnTrader(args.config)
    
    try:
        await trader.start()
    finally:
        await trader.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
