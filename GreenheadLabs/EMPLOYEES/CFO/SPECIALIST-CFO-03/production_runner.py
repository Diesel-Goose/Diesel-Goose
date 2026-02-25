#!/usr/bin/env python3
"""
Chris Dunn v2.0 - PRODUCTION RUNNER
XRP/RLUSD Market Maker with Auto Profit Sweep

Usage:
    python production_runner.py
    
Requirements:
    - config/production.yaml configured with wallet credentials
    - xrpl-py installed (pip install xrpl-py)
    - Funded wallet with XRP and RLUSD
"""

import asyncio
import yaml
import logging
import signal
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler('logs/production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ProductionRunner')

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

# Import our modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.xrpl_production import XRPLProductionClient
    from strategies.production_mm import ProductionMarketMaker
    from core.profit_sweeper import ProfitSweeper
    from core.trade_logger import TradeLogger
    from utils.telegram_alerts import TelegramAlerts
    XRPL_AVAILABLE = True
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Run: pip install xrpl-py aiohttp pyyaml")
    XRPL_AVAILABLE = False


class ChrisDunnProduction:
    """Main production trading orchestrator."""
    
    def __init__(self, config_path: str = 'config/production.yaml'):
        self.config = self._load_config(config_path)
        self.running = False
        self.start_time = None
        
        # Statistics
        self.total_trades = 0
        self.session_pnl = 0.0
        self.errors = 0
        
        # Components
        self.xrpl = None
        self.market_maker = None
        self.sweeper = None
        self.telegram = None
        self.trade_logger = None
        
    def _load_config(self, path: str) -> Dict:
        """Load configuration from YAML."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            raise
    
    async def initialize(self):
        """Initialize all components."""
        logger.info("=" * 60)
        logger.info("🚀 Chris Dunn v2.0 PRODUCTION INITIALIZING")
        logger.info("=" * 60)
        
        # Initialize Telegram
        self.telegram = TelegramAlerts(self.config)
        
        # Initialize XRPL client
        self.xrpl = XRPLProductionClient(self.config)
        
        if not self.xrpl.wallet:
            logger.error("❌ Wallet failed to load. Check your secret in config.")
            return False
        
        # Connect to XRPL
        if not await self.xrpl.connect():
            logger.error("❌ Failed to connect to XRPL")
            return False
        
        # Check balance
        balance = await self.xrpl.get_balance()
        logger.info(f"💰 Wallet Balance: {balance['xrp']:.2f} XRP, {balance['rlusd']:.2f} RLUSD")
        
        if balance['xrp'] < 5:
            logger.error("❌ Insufficient XRP. Need at least 5 XRP for reserves.")
            return False
        
        # Initialize market maker
        self.market_maker = ProductionMarketMaker(
            config=self.config,
            xrpl_client=self.xrpl,
            risk_manager=None  # Add risk manager if needed
        )
        
        # Initialize profit sweeper
        self.sweeper = ProfitSweeper(
            config=self.config,
            xrpl_client=self.xrpl,
            telegram_alerts=self.telegram
        )
        
        # Initialize trade logger for tax records
        self.trade_logger = TradeLogger(self.config)
        logger.info(f"📊 Trade logging enabled: {self.trade_logger.log_file}")
        
        # Send startup message
        await self.telegram.send_startup_message(
            wallet=self.xrpl.address,
            pair=self.config['trading']['pair']
        )
        
        logger.info("✅ All components initialized")
        logger.info(f"   Trading Pair: {self.config['trading']['pair']}")
        logger.info(f"   Vault: {self.config['wallet'].get('vault_address', 'Not set')[:15]}...")
        logger.info("=" * 60)
        
        return True
    
    async def trading_loop(self):
        """Main trading loop."""
        cycle = 0
        
        while self.running:
            try:
                cycle += 1
                logger.info(f"\n📊 Trading Cycle #{cycle}")
                
                # Run market maker cycle
                trades = await self.market_maker.analyze_and_trade()
                
                if trades:
                    self.total_trades += len(trades)
                    # Get current balance for trade logging
                    current_balance = await self.xrpl.get_balance()
                    for trade in trades:
                        await self.telegram.send_trade_alert(trade)
                        # Log trade for tax records
                        if self.trade_logger:
                            await self.trade_logger.log_trade(trade, current_balance)
                
                # Every 10 cycles, check profit sweep and log daily summary
                if cycle % 10 == 0:
                    await self.sweeper.check_and_sweep()
                    # Log daily summary every ~5 minutes (10 cycles * 30 seconds)
                    if self.trade_logger and cycle % 120 == 0:  # Every hour
                        await self.trade_logger.log_daily_summary(self.telegram)
                
                # Log status every cycle
                status = self.market_maker.get_status()
                logger.info(f"   Open Orders: {status['open_bids']} bids, {status['open_asks']} asks")
                logger.info(f"   Inventory: {status['inventory_ratio']:.1%} XRP")
                
                # Sleep between cycles
                await asyncio.sleep(30)  # 30 second cycles
                
            except Exception as e:
                logger.error(f"Trading cycle error: {e}", exc_info=True)
                self.errors += 1
                await self.telegram.send_error_alert(str(e))
                await asyncio.sleep(30)  # Continue after error
    
    async def run(self):
        """Run the production bot."""
        if not XRPL_AVAILABLE:
            logger.error("xrpl-py not available. Install with: pip install xrpl-py")
            return
        
        # Initialize
        if not await self.initialize():
            logger.error("Initialization failed. Exiting.")
            return
        
        # Set up signal handlers
        self.running = True
        self.start_time = datetime.now()
        
        def shutdown_handler(sig, frame):
            logger.info("\n🛑 Shutdown signal received. Stopping gracefully...")
            self.running = False
        
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)
        
        # Start profit sweeper in background
        sweeper_task = asyncio.create_task(self.sweeper.run_sweep_loop())
        
        logger.info("🟢 PRODUCTION RUNNING - Press Ctrl+C to stop")
        
        try:
            await self.trading_loop()
        except asyncio.CancelledError:
            pass
        finally:
            # Cleanup
            sweeper_task.cancel()
            try:
                await sweeper_task
            except asyncio.CancelledError:
                pass
            
            await self.xrpl.disconnect()
            
            # Send summary
            runtime = (datetime.now() - self.start_time).total_seconds() / 60
            await self.telegram.send_session_summary({
                'runtime_minutes': runtime,
                'total_trades': self.total_trades,
                'session_pnl': self.session_pnl
            })
            
            logger.info("=" * 60)
            logger.info("🏁 SESSION COMPLETE")
            logger.info(f"   Runtime: {runtime:.1f} minutes")
            logger.info(f"   Total Trades: {self.total_trades}")
            logger.info(f"   Errors: {self.errors}")
            logger.info("=" * 60)


if __name__ == "__main__":
    # Check config exists
    config_file = Path('config/production.yaml')
    if not config_file.exists():
        logger.error(f"Config not found: {config_file}")
        logger.error("Copy config/production.yaml.template to config/production.yaml and fill in your wallet details")
        sys.exit(1)
    
    # Run
    bot = ChrisDunnProduction()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Shutdown complete.")
