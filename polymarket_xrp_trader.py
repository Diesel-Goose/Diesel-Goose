#!/usr/bin/env python3
"""
Polymarket XRP 5-Minute Trading Bot - Simplified Version
Greenhead Labs - Woody Pintail

Uses only standard library - no external dependencies
"""

import json
import time
import logging
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('polymarket_xrp')

class XRPPredictor:
    """Predicts XRP 5-minute price direction"""
    
    def __init__(self):
        self.price_history = []
        self.max_history = 20
        self.trade_count = 0
        self.win_count = 0
        
    def add_price(self, price: float, timestamp: float):
        """Add new price point"""
        self.price_history.append({
            'price': price,
            'timestamp': timestamp
        })
        
        if len(self.price_history) > self.max_history:
            self.price_history.pop(0)
            
    def calculate_momentum(self) -> Dict[str, Any]:
        """Calculate momentum indicators"""
        if len(self.price_history) < 5:
            return {'momentum': 0, 'trend': 'neutral', 'confidence': 0}
            
        prices = [p['price'] for p in self.price_history]
        
        # Short-term momentum
        recent = prices[-3:]
        previous = prices[-6:-3] if len(prices) >= 6 else prices[:3]
        
        recent_avg = sum(recent) / len(recent)
        previous_avg = sum(previous) / len(previous)
        
        if previous_avg == 0:
            momentum = 0
        else:
            momentum = (recent_avg - previous_avg) / previous_avg * 100
        
        # Consistency
        up_moves = sum(1 for i in range(1, len(prices)) if prices[i] > prices[i-1])
        consistency = up_moves / (len(prices) - 1) if len(prices) > 1 else 0.5
        
        # Determine trend
        if momentum > 0.03 and consistency > 0.55:
            trend = 'up'
            confidence = min(abs(momentum) * 15, 0.80)
        elif momentum < -0.03 and consistency < 0.45:
            trend = 'down'
            confidence = min(abs(momentum) * 15, 0.80)
        else:
            trend = 'neutral'
            confidence = 0.35
            
        return {
            'momentum': momentum,
            'trend': trend,
            'confidence': confidence,
            'consistency': consistency,
            'current_price': prices[-1],
            'price_change_5m': ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] != 0 else 0
        }
        
    def predict(self) -> Dict[str, Any]:
        """Generate prediction"""
        analysis = self.calculate_momentum()
        
        # Only trade on sufficient confidence
        if analysis['confidence'] < 0.60:
            return {
                'direction': None,
                'confidence': analysis['confidence'],
                'reason': 'Insufficient confidence',
                'should_trade': False,
                'analysis': analysis
            }
            
        return {
            'direction': analysis['trend'],
            'confidence': analysis['confidence'],
            'reason': f"Momentum: {analysis['momentum']:.4f}% | Consistency: {analysis['consistency']:.2f}",
            'should_trade': True,
            'analysis': analysis
        }


class PolymarketTrader:
    """Polymarket trading interface"""
    
    def __init__(self, starting_balance: float = 100.0):
        self.predictor = XRPPredictor()
        self.active = False
        self.balance = starting_balance
        self.trades = []
        self.last_prediction = None
        
    def get_xrp_price(self) -> Optional[float]:
        """Get current XRP price"""
        try:
            # Using CoinGecko API
            req = urllib.request.Request(
                "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data.get('ripple', {}).get('usd')
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return None
            
    def simulate_trade(self, direction: str, amount: float, confidence: float):
        """Simulate a trade"""
        timestamp = datetime.now().isoformat()
        
        trade = {
            'timestamp': timestamp,
            'direction': direction,
            'amount': amount,
            'confidence': confidence,
            'entry_price': self.predictor.price_history[-1]['price'] if self.predictor.price_history else 0,
            'type': 'PAPER_TRADE'
        }
        
        self.trades.append(trade)
        self.balance -= amount  # Deduct from balance
        
        logger.info(f"🎯 PAPER TRADE: {direction.upper()} ${amount:.2f} (Confidence: {confidence:.2f})")
        
        # Save trade
        with open('xrp_trades.jsonl', 'a') as f:
            f.write(json.dumps(trade) + '\n')
            
    def run_once(self):
        """Run one prediction cycle"""
        price = self.get_xrp_price()
        if not price:
            logger.warning("Could not fetch price, skipping cycle")
            return
            
        self.predictor.add_price(price, time.time())
        prediction = self.predictor.predict()
        
        # Format output
        momentum = prediction['analysis'].get('momentum', 0)
        consistency = prediction['analysis'].get('consistency', 0)
        
        logger.info(f"💰 XRP: ${price:.4f} | Momentum: {momentum:+.4f}% | Consistency: {consistency:.2f}")
        
        if prediction['should_trade']:
            direction = prediction['direction']
            confidence = prediction['confidence']
            
            # Position sizing: 5% of balance per trade
            trade_amount = self.balance * 0.05
            
            if trade_amount >= 1.0:  # Minimum $1 trade
                self.simulate_trade(direction, trade_amount, confidence)
                self.last_prediction = prediction
        else:
            logger.info(f"⏸️  No trade: {prediction['reason']}")
            
        # Log to file
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'price': price,
            'prediction': prediction,
            'balance': self.balance
        }
        
        with open('xrp_predictions.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def run_continuous(self, interval: int = 10):
        """Run continuous prediction loop"""
        logger.info("=" * 60)
        logger.info("Polymarket XRP 5-Minute Trading Bot")
        logger.info("Greenhead Labs - Woody Pintail")
        logger.info("=" * 60)
        logger.info(f"Starting Balance: ${self.balance:.2f}")
        logger.info(f"Update Interval: {interval}s")
        logger.info(f"Trade Threshold: 60% confidence")
        logger.info(f"Position Size: 5% of balance per trade")
        logger.info("=" * 60)
        logger.info("")
        
        self.active = True
        
        try:
            while self.active:
                self.run_once()
                logger.info("")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("Shutting down...")
            self.print_summary()
            
    def print_summary(self):
        """Print trading summary"""
        logger.info("=" * 60)
        logger.info("TRADING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Trades: {len(self.trades)}")
        logger.info(f"Current Balance: ${self.balance:.2f}")
        logger.info(f"P&L: ${self.balance - 100.0:+.2f}")
        logger.info("=" * 60)


def main():
    """Main entry point"""
    import sys
    
    # Parse arguments
    starting_balance = 100.0
    interval = 10
    
    if len(sys.argv) > 1:
        try:
            starting_balance = float(sys.argv[1])
        except ValueError:
            pass
            
    if len(sys.argv) > 2:
        try:
            interval = int(sys.argv[2])
        except ValueError:
            pass
    
    trader = PolymarketTrader(starting_balance=starting_balance)
    trader.run_continuous(interval=interval)


if __name__ == "__main__":
    main()
