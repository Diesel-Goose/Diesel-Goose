"""
Kraken Multi-Pair Trading Bot - Greenhead Labs Employee #3
Trades any crypto pair on Kraken exchange
Momentum-based strategy with risk management
"""

import asyncio
import yaml
import logging
import sys
import time
import hmac
import hashlib
import base64
import urllib.request
import urllib.parse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque

sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.trade_logger import TradeLogger
    from utils.telegram_alerts import TelegramAlerts
    KRAKEN_AVAILABLE = True
except ImportError as e:
    logging.error(f"Import error: {e}")
    KRAKEN_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler('logs/kraken_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('KrakenBot')


class KrakenAPI:
    """Kraken API client for trading."""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_url = 'https://api.kraken.com'
        
    def _sign(self, urlpath: str, data: dict) -> str:
        """Sign API request."""
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        signature = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        return base64.b64encode(signature.digest()).decode()
    
    def _query(self, urlpath: str, data: dict = None, private: bool = False) -> dict:
        """Make API request."""
        if data is None:
            data = {}
        
        url = self.api_url + urlpath
        
        if private:
            data['nonce'] = int(1000 * time.time())
            headers = {
                'API-Key': self.api_key,
                'API-Sign': self._sign(urlpath, data)
            }
        else:
            headers = {}
        
        try:
            postdata = urllib.parse.urlencode(data).encode()
            request = urllib.request.Request(url, postdata, headers)
            response = urllib.request.urlopen(request)
            return json.loads(response.read())
        except Exception as e:
            logger.error(f"API error: {e}")
            return {'error': str(e)}
    
    def get_balance(self) -> dict:
        """Get account balance."""
        result = self._query('/0/private/Balance', {}, private=True)
        return result.get('result', {})
    
    def get_ticker(self, pairs: List[str]) -> dict:
        """Get ticker info for pairs."""
        pair_str = ','.join(pairs)
        result = self._query('/0/public/Ticker', {'pair': pair_str})
        return result.get('result', {})
    
    def get_ohlc(self, pair: str, interval: int = 15) -> List[list]:
        """Get OHLC data. interval in minutes."""
        result = self._query('/0/public/OHLC', {'pair': pair, 'interval': interval})
        return result.get('result', {}).get(pair, [])
    
    def place_order(self, pair: str, side: str, ordertype: str, volume: str, price: str = None) -> dict:
        """Place an order."""
        data = {
            'pair': pair,
            'type': side,  # buy or sell
            'ordertype': ordertype,  # market or limit
            'volume': volume
        }
        if price and ordertype == 'limit':
            data['price'] = price
        
        result = self._query('/0/private/AddOrder', data, private=True)
        return result
    
    def get_open_orders(self) -> dict:
        """Get open orders."""
        return self._query('/0/private/OpenOrders', {}, private=True)


class KrakenTradingBot:
    """
    Multi-Pair Momentum Trader for Kraken
    
    Strategy:
    - Monitor 8+ trading pairs
    - Enter on 15m momentum breakouts
    - 2% stop, 4% target
    - Max 3 concurrent positions
    """
    
    def __init__(self, config_path: str = 'config/kraken_config.yaml'):
        self.config = self._load_config(config_path)
        self.running = False
        
        # Initialize Kraken API
        kraken_cfg = self.config['kraken']
        self.kraken = KrakenAPI(kraken_cfg['api_key'], kraken_cfg['api_secret'])
        
        # Trading pairs
        self.pairs = self.config['trading_pairs']
        self.pair_data = {}  # Store OHLC data per pair
        
        # Positions
        self.positions = {}  # pair -> position dict
        self.max_positions = self.config['strategy']['max_concurrent_positions']
        
        # Performance
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.wins = 0
        self.losses = 0
        
        # Components
        self.telegram = None
        self.trade_logger = None
        
    def _load_config(self, path: str) -> Dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    async def initialize(self):
        """Initialize bot."""
        logger.info("=" * 60)
        logger.info("🚀 KRAKEN MULTI-PAIR BOT INITIALIZING")
        logger.info("=" * 60)
        
        self.telegram = TelegramAlerts(self.config)
        self.trade_logger = TradeLogger(self.config)
        
        # Check balance
        balance = self.kraken.get_balance()
        logger.info(f"💰 Kraken Balance: {len(balance)} assets")
        for asset, amount in list(balance.items())[:5]:
            logger.info(f"   {asset}: {amount}")
        
        await self.telegram.send_alert(
            "🚀 Kraken Multi-Pair Bot Activated\n"
            f"Pairs: {', '.join(self.pairs)}\n"
            f"Strategy: 15m Momentum\n"
            f"Risk: 2% stop / 4% target",
            priority='high'
        )
        
        logger.info("✅ Kraken bot ready")
        return True
    
    def analyze_pair(self, pair: str) -> str:
        """
        Analyze a trading pair for signals.
        
        Returns: 'buy', 'sell', or 'hold'
        """
        try:
            # Get 15m OHLC data
            ohlc = self.kraken.get_ohlc(pair, interval=15)
            
            if len(ohlc) < 10:
                return 'hold'  # Not enough data
            
            # Parse recent candles
            closes = [float(c[4]) for c in ohlc[-20:]]  # Close prices
            highs = [float(c[2]) for c in ohlc[-10:]]   # Recent highs
            lows = [float(c[3]) for c in ohlc[-10:]]    # Recent lows
            volumes = [float(c[6]) for c in ohlc[-5:]]  # Recent volume
            
            current = closes[-1]
            prev_close = closes[-2]
            
            # Calculate indicators
            short_ma = sum(closes[-5:]) / 5
            medium_ma = sum(closes[-10:]) / 10
            
            recent_high = max(highs)
            recent_low = min(lows)
            avg_volume = sum(volumes) / len(volumes)
            current_volume = volumes[-1]
            
            # Momentum
            momentum = (current - closes[-3]) / closes[-3] * 100
            
            # Volume spike
            volume_spike = current_volume > avg_volume * 1.5
            
            signal = 'hold'
            
            # Buy: Break above recent high + momentum + volume
            if current > recent_high * 0.998 and momentum > 0.8 and volume_spike:
                if current > short_ma and short_ma > medium_ma:
                    signal = 'buy'
                    logger.info(f"🟢 {pair} BUY: Breakout @ ${current:.4f}, mom {momentum:.2f}%")
            
            # Sell: Break below recent low + negative momentum
            elif current < recent_low * 1.002 and momentum < -0.8 and volume_spike:
                if current < short_ma and short_ma < medium_ma:
                    signal = 'sell'
                    logger.info(f"🔴 {pair} SELL: Breakdown @ ${current:.4f}, mom {momentum:.2f}%")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing {pair}: {e}")
            return 'hold'
    
    async def enter_position(self, pair: str, side: str, price: float):
        """Enter a new position."""
        if len(self.positions) >= self.max_positions:
            logger.info(f"Max positions ({self.max_positions}) reached")
            return
        
        if pair in self.positions:
            logger.info(f"Already in position for {pair}")
            return
        
        # Get position size (10% of USD balance)
        balance = self.kraken.get_balance()
        usd_balance = float(balance.get('ZUSD', 0))
        
        if usd_balance < 10:
            logger.warning("Insufficient USD balance")
            return
        
        position_usd = min(usd_balance * 0.1, 100)  # Max $100 per trade
        volume = str(round(position_usd / price, 6))
        
        # Place market order
        result = self.kraken.place_order(pair, side, 'market', volume)
        
        if 'error' in result and result['error']:
            logger.error(f"Order failed: {result['error']}")
            return
        
        # Set stops
        if side == 'buy':
            stop = price * 0.98
            target = price * 1.04
        else:
            stop = price * 1.02
            target = price * 0.96
        
        self.positions[pair] = {
            'side': side,
            'entry': price,
            'volume': volume,
            'stop': stop,
            'target': target,
            'entry_time': datetime.now()
        }
        
        self.daily_trades += 1
        
        msg = (f"📈 KRAKEN POSITION\n"
               f"Pair: {pair}\n"
               f"Side: {side.upper()}\n"
               f"Size: ${position_usd:.2f}\n"
               f"Entry: ${price:.4f}")
        
        logger.info(msg)
        await self.telegram.send_alert(msg, priority='high')
        
        # Log trade
        if self.trade_logger:
            await self.trade_logger.log_trade(
                {'tx_hash': result.get('result', {}).get('txid', ''), 'side': side, 
                 'amount': float(volume), 'price': price},
                {'xrp': 0, 'rlusd': usd_balance - position_usd}
            )
    
    async def check_positions(self):
        """Check and manage open positions."""
        ticker = self.kraken.get_ticker(list(self.positions.keys()))
        
        for pair, pos in list(self.positions.items()):
            if pair not in ticker:
                continue
            
            current_price = float(ticker[pair]['c'][0])  # Last trade close
            side = pos['side']
            entry = pos['entry']
            stop = pos['stop']
            target = pos['target']
            
            exit_trade = False
            pnl_pct = 0
            
            if side == 'buy':
                if current_price <= stop:
                    exit_trade = True
                    pnl_pct = (current_price - entry) / entry * 100
                    self.losses += 1
                elif current_price >= target:
                    exit_trade = True
                    pnl_pct = (current_price - entry) / entry * 100
                    self.wins += 1
            else:  # sell
                if current_price >= stop:
                    exit_trade = True
                    pnl_pct = (entry - current_price) / entry * 100
                    self.losses += 1
                elif current_price <= target:
                    exit_trade = True
                    pnl_pct = (entry - current_price) / entry * 100
                    self.wins += 1
            
            if exit_trade:
                # Close position
                close_side = 'sell' if side == 'buy' else 'buy'
                self.kraken.place_order(pair, close_side, 'market', pos['volume'])
                
                self.daily_pnl += pnl_pct
                del self.positions[pair]
                
                emoji = "✅" if pnl_pct > 0 else "❌"
                msg = (f"{emoji} KRAKEN CLOSE\n"
                       f"Pair: {pair}\n"
                       f"P&L: {pnl_pct:.2f}%")
                
                logger.info(msg)
                await self.telegram.send_alert(msg, priority='high')
    
    async def run(self):
        """Main trading loop."""
        if not await self.initialize():
            return
        
        self.running = True
        cycle = 0
        
        logger.info("🟢 KRAKEN BOT RUNNING - Multi-Pair Momentum")
        
        while self.running:
            try:
                cycle += 1
                logger.info(f"\n📊 Scan Cycle #{cycle} | Positions: {len(self.positions)}")
                
                # Check existing positions
                if self.positions:
                    await self.check_positions()
                
                # Scan for new opportunities
                if len(self.positions) < self.max_positions:
                    for pair in self.pairs:
                        if pair in self.positions:
                            continue
                        
                        signal = self.analyze_pair(pair)
                        
                        if signal in ['buy', 'sell']:
                            # Get current price
                            ticker = self.kraken.get_ticker([pair])
                            if pair in ticker:
                                price = float(ticker[pair]['c'][0])
                                await self.enter_position(pair, signal, price)
                                break  # One trade per cycle
                
                # Log status
                logger.info(f"Active: {len(self.positions)} | Win/Loss: {self.wins}/{self.losses} | Daily P&L: {self.daily_pnl:.2f}%")
                
                # Wait for next cycle (5 minutes between scans)
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Trading cycle error: {e}")
                await asyncio.sleep(60)


if __name__ == "__main__":
    Path('logs').mkdir(exist_ok=True)
    
    bot = KrakenTradingBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Shutdown complete.")
