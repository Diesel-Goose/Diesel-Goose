#!/usr/bin/env python3
"""
Polymarket XRP 5-Minute Trading Bot - Production Version
Greenhead Labs - Woody Pintail

Strategy: Momentum-based prediction for 5-minute binary options
Uses multiple price sources with fallback
"""

import json
import time
import logging
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xrp_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('polymarket_xrp')

class PriceFeed:
    """Multi-source price feed with fallback"""
    
    SOURCES = [
        {
            'name': 'CoinGecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd',
            'parser': lambda d: d.get('ripple', {}).get('usd')
        },
        {
            'name': 'CryptoCompare',
            'url': 'https://min-api.cryptocompare.com/data/price?fsym=XRP&tsyms=USD',
            'parser': lambda d: d.get('USD')
        },
        {
            'name': 'Binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT',
            'parser': lambda d: float(d.get('price', 0))
        }
    ]
    
    @classmethod
    def get_price(cls) -> Optional[float]:
        """Try each price source until one works"""
        for source in cls.SOURCES:
            try:
                req = urllib.request.Request(
                    source['url'],
                    headers={'User-Agent': 'Mozilla/5.0'},
                    method='GET'
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    data = json.loads(response.read().decode())
                    price = source['parser'](data)
                    if price and price > 0:
                        logger.debug(f"Price from {source['name']}: ${price}")
                        return float(price)
            except Exception as e:
                logger.debug(f"{source['name']} failed: {e}")
                continue
        
        logger.error("All price sources failed")
        return None


class XRPPredictor:
    """Predicts XRP 5-minute price direction using momentum analysis"""
    
    def __init__(self):
        self.price_history: List[Dict] = []
        self.max_history = 30  # 5 minutes of data at 10s intervals
        self.signals_generated = 0
        self.trades_taken = 0
        
    def add_price(self, price: float, timestamp: float):
        """Add new price point"""
        self.price_history.append({
            'price': price,
            'timestamp': timestamp
        })
        
        if len(self.price_history) > self.max_history:
            self.price_history.pop(0)
            
    def calculate_indicators(self) -> Dict[str, Any]:
        """Calculate technical indicators"""
        if len(self.price_history) < 10:
            return {
                'ready': False,
                'reason': f'Collecting data ({len(self.price_history)}/10 points)'
            }
            
        prices = [p['price'] for p in self.price_history]
        
        # Price changes
        changes = [(prices[i] - prices[i-1]) / prices[i-1] * 100 
                   for i in range(1, len(prices))]
        
        # Short-term momentum (last 5 points vs previous 5)
        recent_changes = changes[-5:]
        older_changes = changes[-10:-5] if len(changes) >= 10 else changes[:5]
        
        recent_momentum = sum(recent_changes)
        older_momentum = sum(older_changes)
        
        # Acceleration
        acceleration = recent_momentum - older_momentum
        
        # Trend consistency
        up_moves = sum(1 for c in changes[-10:] if c > 0)
        consistency = up_moves / min(len(changes[-10:]), 10)
        
        # Volatility
        volatility = sum(abs(c) for c in changes[-10:]) / min(len(changes[-10:]), 10)
        
        # Current price vs moving average
        ma_10 = sum(prices[-10:]) / min(len(prices), 10)
        price_vs_ma = (prices[-1] - ma_10) / ma_10 * 100
        
        return {
            'ready': True,
            'current_price': prices[-1],
            'momentum': recent_momentum,
            'acceleration': acceleration,
            'consistency': consistency,
            'volatility': volatility,
            'price_vs_ma': price_vs_ma,
            'changes': changes[-5:]
        }
        
    def generate_signal(self) -> Dict[str, Any]:
        """Generate trading signal"""
        ind = self.calculate_indicators()
        
        if not ind['ready']:
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': ind['reason'],
                'indicators': ind
            }
            
        self.signals_generated += 1
        
        momentum = ind['momentum']
        acceleration = ind['acceleration']
        consistency = ind['consistency']
        volatility = ind['volatility']
        
        # Skip high volatility periods
        if volatility > 0.5:  # >0.5% average change
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': f'High volatility ({volatility:.3f}%)',
                'indicators': ind
            }
            
        # UP signal criteria
        if momentum > 0.05 and acceleration > 0 and consistency > 0.6:
            confidence = min(0.5 + abs(momentum) * 5 + abs(acceleration) * 2, 0.85)
            return {
                'signal': 'UP',
                'confidence': confidence,
                'reason': f'Momentum {momentum:+.3f}%, Accel {acceleration:+.3f}%, Consistency {consistency:.2f}',
                'indicators': ind
            }
            
        # DOWN signal criteria
        if momentum < -0.05 and acceleration < 0 and consistency < 0.4:
            confidence = min(0.5 + abs(momentum) * 5 + abs(acceleration) * 2, 0.85)
            return {
                'signal': 'DOWN',
                'confidence': confidence,
                'reason': f'Momentum {momentum:+.3f}%, Accel {acceleration:+.3f}%, Consistency {consistency:.2f}',
                'indicators': ind
            }
            
        return {
            'signal': 'HOLD',
            'confidence': 0.35,
            'reason': f'No clear signal (Mom: {momentum:+.3f}%, Cons: {consistency:.2f})',
            'indicators': ind
        }


class TradingEngine:
    """Paper trading engine for Polymarket simulation"""
    
    def __init__(self, starting_capital: float = 100.0):
        self.capital = starting_capital
        self.initial_capital = starting_capital
        self.open_positions: List[Dict] = []
        self.closed_positions: List[Dict] = []
        self.trade_id = 0
        
    def calculate_position_size(self, confidence: float) -> float:
        """Kelly-inspired position sizing"""
        # Base 5% of capital
        base_size = self.capital * 0.05
        
        # Scale by confidence (0.6 to 0.85 range)
        confidence_scale = (confidence - 0.6) / 0.25  # Normalize to 0-1
        
        position = base_size * (0.5 + confidence_scale)
        
        # Max 10% per trade
        return min(position, self.capital * 0.10)
        
    def enter_position(self, signal: str, confidence: float, price: float, 
                       indicators: Dict) -> Optional[Dict]:
        """Enter a new paper position"""
        # Max 3 open positions
        if len(self.open_positions) >= 3:
            return None
            
        size = self.calculate_position_size(confidence)
        
        if size < 1.0 or size > self.capital:
            return None
            
        self.trade_id += 1
        
        position = {
            'id': self.trade_id,
            'signal': signal,  # UP or DOWN
            'entry_price': price,
            'size': size,
            'confidence': confidence,
            'entry_time': datetime.now().isoformat(),
            'indicators': indicators,
            'status': 'OPEN'
        }
        
        self.open_positions.append(position)
        self.capital -= size  # Reserve capital
        
        logger.info(f"🎯 ENTER {signal} | Size: ${size:.2f} | Confidence: {confidence:.2f} | Price: ${price:.4f}")
        
        return position
        
    def close_position(self, position_id: int, exit_price: float, result: str) -> Dict:
        """Close a position and calculate P&L"""
        position = None
        for p in self.open_positions:
            if p['id'] == position_id:
                position = p
                break
                
        if not position:
            return {}
            
        self.open_positions.remove(position)
        
        # Calculate P&L
        if position['signal'] == 'UP':
            pnl_pct = (exit_price - position['entry_price']) / position['entry_price'] * 100
        else:  # DOWN
            pnl_pct = (position['entry_price'] - exit_price) / position['entry_price'] * 100
            
        # Binary outcome: win = 95% payout (5% fee), lose = -100%
        if result == 'WIN':
            pnl_amount = position['size'] * 0.95
        else:
            pnl_amount = -position['size']
            
        position.update({
            'exit_price': exit_price,
            'exit_time': datetime.now().isoformat(),
            'result': result,
            'pnl_amount': pnl_amount,
            'pnl_pct': pnl_pct,
            'status': 'CLOSED'
        })
        
        self.capital += position['size'] + pnl_amount
        self.closed_positions.append(position)
        
        emoji = "✅" if result == 'WIN' else "❌"
        logger.info(f"{emoji} CLOSE #{position_id} | Result: {result} | P&L: ${pnl_amount:+.2f} | Balance: ${self.capital:.2f}")
        
        return position
        
    def get_stats(self) -> Dict:
        """Get trading statistics"""
        if not self.closed_positions:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'current_balance': self.capital
            }
            
        wins = sum(1 for p in self.closed_positions if p['result'] == 'WIN')
        total_pnl = sum(p['pnl_amount'] for p in self.closed_positions)
        
        return {
            'total_trades': len(self.closed_positions),
            'open_trades': len(self.open_positions),
            'wins': wins,
            'losses': len(self.closed_positions) - wins,
            'win_rate': wins / len(self.closed_positions) * 100,
            'total_pnl': total_pnl,
            'current_balance': self.capital,
            'roi': (self.capital - self.initial_capital) / self.initial_capital * 100
        }


class PolymarketXRPBot:
    """Main trading bot"""
    
    def __init__(self, capital: float = 100.0, interval: int = 10):
        self.predictor = XRPPredictor()
        self.trading = TradingEngine(starting_capital=capital)
        self.interval = interval
        self.active = False
        self.cycle_count = 0
        
    def print_header(self):
        """Print startup header"""
        logger.info("=" * 70)
        logger.info("POLYMARKET XRP 5-MINUTE TRADING BOT")
        logger.info("Greenhead Labs - Woody Pintail")
        logger.info("=" * 70)
        logger.info(f"Mode: PAPER TRADING (Simulated)")
        logger.info(f"Starting Capital: ${self.trading.initial_capital:.2f}")
        logger.info(f"Update Interval: {self.interval}s")
        logger.info(f"Min Confidence: 60%")
        logger.info(f"Max Position: 10% of capital")
        logger.info(f"Max Open Positions: 3")
        logger.info("=" * 70)
        logger.info("")
        
    def print_status(self):
        """Print current status"""
        stats = self.trading.get_stats()
        
        logger.info("-" * 70)
        logger.info(f"Cycle #{self.cycle_count} | Balance: ${stats['current_balance']:.2f} | ROI: {stats['roi']:+.2f}%")
        logger.info(f"Trades: {stats['total_trades']} (W: {stats['wins']} L: {stats['losses']}) | Win Rate: {stats['win_rate']:.1f}%")
        logger.info(f"Open Positions: {stats['open_trades']}")
        logger.info("-" * 70)
        
    def run_cycle(self):
        """Run one trading cycle"""
        self.cycle_count += 1
        
        # Get price
        price = PriceFeed.get_price()
        if not price:
            logger.warning("⚠️  Could not fetch price, skipping cycle")
            return
            
        # Update predictor
        self.predictor.add_price(price, time.time())
        
        # Generate signal
        signal = self.predictor.generate_signal()
        
        # Log status every 6 cycles (1 minute)
        if self.cycle_count % 6 == 0:
            self.print_status()
            
        # Execute trade if signal is strong
        if signal['signal'] in ['UP', 'DOWN'] and signal['confidence'] >= 0.60:
            position = self.trading.enter_position(
                signal=signal['signal'],
                confidence=signal['confidence'],
                price=price,
                indicators=signal['indicators']
            )
            
            if position:
                # Log trade
                self._log_trade(position, price, signal)
        else:
            logger.info(f"📊 XRP: ${price:.4f} | Signal: {signal['signal']} | {signal['reason']}")
            
    def _log_trade(self, position: Dict, price: float, signal: Dict):
        """Log trade to file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'TRADE',
            'position': position,
            'signal': signal,
            'balance': self.trading.capital
        }
        
        with open('xrp_trading.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def simulate_position_closes(self):
        """Simulate closing positions after 5 minutes (for paper trading)"""
        current_time = time.time()
        positions_to_close = []
        
        for pos in self.trading.open_positions:
            entry_time = datetime.fromisoformat(pos['entry_time']).timestamp()
            if current_time - entry_time > 300:  # 5 minutes
                positions_to_close.append(pos)
                
        for pos in positions_to_close:
            # Simulate result based on actual price movement
            current_price = PriceFeed.get_price()
            if not current_price:
                continue
                
            if pos['signal'] == 'UP':
                result = 'WIN' if current_price >= pos['entry_price'] else 'LOSE'
            else:
                result = 'WIN' if current_price <= pos['entry_price'] else 'LOSE'
                
            self.trading.close_position(pos['id'], current_price, result)
            
    def run(self):
        """Main loop"""
        self.print_header()
        self.active = True
        
        try:
            while self.active:
                self.run_cycle()
                self.simulate_position_closes()
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 70)
            logger.info("SHUTTING DOWN")
            logger.info("=" * 70)
            self.print_status()
            logger.info("Final positions will be marked at current price")
            
            # Close all open positions
            current_price = PriceFeed.get_price()
            if current_price:
                for pos in list(self.trading.open_positions):
                    result = 'WIN' if pos['signal'] == 'UP' else 'LOSE'
                    self.trading.close_position(pos['id'], current_price, result)
                    
            self.print_status()


def main():
    import sys
    
    capital = 100.0
    interval = 10
    
    if len(sys.argv) > 1:
        try:
            capital = float(sys.argv[1])
        except ValueError:
            pass
            
    if len(sys.argv) > 2:
        try:
            interval = int(sys.argv[2])
        except ValueError:
            pass
    
    bot = PolymarketXRPBot(capital=capital, interval=interval)
    bot.run()


if __name__ == "__main__":
    main()
