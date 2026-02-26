"""
15-Minute Momentum Trader - Greenhead Labs Employee
Swing trading XRP on 15-minute candles
"""

import asyncio
import yaml
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import deque

sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.xrpl_production import XRPLProductionClient
    from core.trade_logger import TradeLogger
    from utils.telegram_alerts import TelegramAlerts
    XRPL_AVAILABLE = True
except ImportError as e:
    logging.error(f"Import error: {e}")
    XRPL_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler('logs/momentum_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MomentumTrader')


class MomentumTrader:
    """
    15-Minute Timeframe Momentum Trader
    
    Strategy:
    - Analyze 15m price action
    - Enter on breakouts with volume
    - 2% stop loss, 4% take profit
    - Max 2 concurrent positions
    """
    
    def __init__(self, config_path: str = 'config/momentum_config.yaml'):
        self.config = self._load_config(config_path)
        self.running = False
        
        # Price history (15-min candles)
        self.price_history = deque(maxlen=20)  # 5 hours of data
        self.volume_history = deque(maxlen=20)
        
        # Position tracking
        self.positions = []  # Active trades
        self.max_positions = 2
        
        # Performance
        self.wins = 0
        self.losses = 0
        self.total_pnl = 0.0
        
        # Components
        self.xrpl = None
        self.telegram = None
        self.trade_logger = None
        
    def _load_config(self, path: str) -> Dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    async def initialize(self):
        """Initialize all components."""
        logger.info("=" * 60)
        logger.info("🚀 15-MIN MOMENTUM TRADER INITIALIZING")
        logger.info("=" * 60)
        
        self.telegram = TelegramAlerts(self.config)
        self.xrpl = XRPLProductionClient(self.config)
        
        if not self.xrpl.wallet:
            logger.error("❌ Wallet failed to load")
            return False
        
        if not await self.xrpl.connect():
            logger.error("❌ Failed to connect to XRPL")
            return False
        
        balance = await self.xrpl.get_balance()
        logger.info(f"💰 Balance: {balance['xrp']:.2f} XRP, {balance['rlusd']:.2f} RLUSD")
        
        self.trade_logger = TradeLogger(self.config)
        
        await self.telegram.send_alert(
            "🚀 15-Min Momentum Trader Activated\n"
            f"Strategy: Breakout trading\n"
            f"Timeframe: 15 minutes\n"
            f"Risk: 2% stop / 4% target",
            priority='high'
        )
        
        logger.info("✅ Momentum trader ready")
        return True
    
    async def fetch_candle_data(self) -> Dict:
        """Fetch current price and build 15m candle."""
        try:
            orderbook = await self.xrpl.get_orderbook()
            mid = orderbook['mid']
            spread = orderbook.get('spread', 0)
            
            # Get recent trades for volume estimation
            volume = 10  # Default volume estimate
            
            return {
                'timestamp': datetime.now(),
                'open': mid,
                'high': mid + spread/2,
                'low': mid - spread/2,
                'close': mid,
                'volume': volume
            }
        except Exception as e:
            logger.error(f"Failed to fetch candle: {e}")
            return None
    
    def analyze_momentum(self) -> str:
        """
        Analyze price action for signals.
        
        Returns: 'buy', 'sell', or 'hold'
        """
        if len(self.price_history) < 5:
            return 'hold'  # Not enough data
        
        prices = list(self.price_history)
        current = prices[-1]['close']
        
        # Calculate indicators
        # 1. Price vs 3-candle average (short term trend)
        short_ma = sum(p['close'] for p in prices[-3:]) / 3
        
        # 2. Price vs 10-candle average (medium trend)
        medium_ma = sum(p['close'] for p in prices[-10:]) / 3 if len(prices) >= 10 else short_ma
        
        # 3. Recent high/low breakout
        recent_high = max(p['high'] for p in prices[-5:])
        recent_low = min(p['low'] for p in prices[-5:])
        
        # 4. Momentum (price change over last 3 candles)
        momentum = (prices[-1]['close'] - prices[-3]['close']) / prices[-3]['close'] * 100
        
        # Signal logic
        signal = 'hold'
        
        # Buy signal: Break above recent high + positive momentum + above MA
        if current > recent_high * 0.998 and momentum > 0.5 and current > short_ma:
            signal = 'buy'
            logger.info(f"🟢 BUY SIGNAL: Breakout @ ${current:.4f}, momentum {momentum:.2f}%")
        
        # Sell signal: Break below recent low + negative momentum + below MA
        elif current < recent_low * 1.002 and momentum < -0.5 and current < short_ma:
            signal = 'sell'
            logger.info(f"🔴 SELL SIGNAL: Breakdown @ ${current:.4f}, momentum {momentum:.2f}%")
        
        return signal
    
    async def enter_position(self, side: str, price: float):
        """Enter a new position."""
        if len(self.positions) >= self.max_positions:
            logger.info(f"Max positions ({self.max_positions}) reached")
            return
        
        # Position size: 10% of available XRP
        balance = await self.xrpl.get_balance()
        position_size = min(balance['xrp'] * 0.1, 5.0)  # Max 5 XRP per trade
        
        if position_size < 1:
            logger.warning("Insufficient balance for trade")
            return
        
        # Set stop loss and take profit
        if side == 'buy':
            stop_loss = price * 0.98  # 2% below
            take_profit = price * 1.04  # 4% above
        else:  # sell (short)
            stop_loss = price * 1.02  # 2% above
            take_profit = price * 0.96  # 4% below
        
        position = {
            'id': len(self.positions) + 1,
            'side': side,
            'entry_price': price,
            'size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': datetime.now(),
            'status': 'open'
        }
        
        self.positions.append(position)
        
        msg = (f"📈 POSITION OPENED\n"
               f"Side: {side.upper()}\n"
               f"Size: {position_size:.2f} XRP\n"
               f"Entry: ${price:.4f}\n"
               f"Stop: ${stop_loss:.4f}\n"
               f"Target: ${take_profit:.4f}")
        
        logger.info(msg)
        await self.telegram.send_alert(msg, priority='high')
    
    async def check_positions(self, current_price: float):
        """Check and manage open positions."""
        for pos in self.positions[:]:
            if pos['status'] != 'open':
                continue
            
            side = pos['side']
            entry = pos['entry_price']
            stop = pos['stop_loss']
            target = pos['take_profit']
            
            exit_trade = False
            exit_price = current_price
            pnl_pct = 0
            
            if side == 'buy':
                if current_price <= stop:  # Stop loss hit
                    exit_trade = True
                    pnl_pct = (current_price - entry) / entry * 100
                    self.losses += 1
                elif current_price >= target:  # Take profit hit
                    exit_trade = True
                    pnl_pct = (current_price - entry) / entry * 100
                    self.wins += 1
            else:  # sell
                if current_price >= stop:  # Stop loss hit
                    exit_trade = True
                    pnl_pct = (entry - current_price) / entry * 100
                    self.losses += 1
                elif current_price <= target:  # Take profit hit
                    exit_trade = True
                    pnl_pct = (entry - current_price) / entry * 100
                    self.wins += 1
            
            if exit_trade:
                pos['status'] = 'closed'
                pos['exit_price'] = exit_price
                pos['pnl_pct'] = pnl_pct
                self.total_pnl += pnl_pct
                
                emoji = "✅" if pnl_pct > 0 else "❌"
                msg = (f"{emoji} POSITION CLOSED\n"
                       f"Side: {side.upper()}\n"
                       f"P&L: {pnl_pct:.2f}%\n"
                       f"Exit: ${exit_price:.4f}")
                
                logger.info(msg)
                await self.telegram.send_alert(msg, priority='high')
                
                # Remove from active positions
                self.positions.remove(pos)
    
    async def run(self):
        """Main trading loop - 15 minute candles."""
        if not await self.initialize():
            return
        
        self.running = True
        cycle = 0
        
        logger.info("🟢 MOMENTUM TRADER RUNNING - 15m candles")
        
        while self.running:
            try:
                cycle += 1
                logger.info(f"\n📊 Candle #{cycle}")
                
                # Fetch price data
                candle = await self.fetch_candle_data()
                if candle:
                    self.price_history.append(candle)
                    current_price = candle['close']
                    
                    # Check existing positions
                    await self.check_positions(current_price)
                    
                    # Analyze for new signals
                    signal = self.analyze_momentum()
                    
                    if signal in ['buy', 'sell'] and len(self.positions) < self.max_positions:
                        await self.enter_position(signal, current_price)
                    
                    # Log status
                    logger.info(f"Price: ${current_price:.4f} | "
                              f"Positions: {len(self.positions)} | "
                              f"Win/Loss: {self.wins}/{self.losses}")
                
                # Wait for next 15-minute candle
                await asyncio.sleep(900)  # 15 minutes = 900 seconds
                
            except Exception as e:
                logger.error(f"Trading cycle error: {e}")
                await asyncio.sleep(60)


if __name__ == "__main__":
    Path('logs').mkdir(exist_ok=True)
    
    trader = MomentumTrader()
    try:
        asyncio.run(trader.run())
    except KeyboardInterrupt:
        logger.info("Shutdown complete.")
