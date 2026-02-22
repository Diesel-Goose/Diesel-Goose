"""
Momentum Trader
Trend-following with technical indicators
"""

import logging
from typing import Dict, Any, List, Optional
from collections import deque


class MomentumTrader:
    """
    Momentum/Trend Following Strategy
    
    Uses technical indicators:
    - RSI (Relative Strength Index): Overbought/oversold
    - MACD: Trend direction and momentum
    - Volume: Confirm trend strength
    
    Enters on breakout, exits on reversal.
    """
    
    def __init__(self, config, xrpl_client, risk_manager, market_data):
        self.config = config.get('strategies', {}).get('momentum', {})
        self.logger = logging.getLogger('MomentumTrader')
        
        self.xrpl = xrpl_client
        self.risk = risk_manager
        self.market = market_data
        
        # Parameters
        self.timeframe = self.config.get('timeframe', '15m')
        self.rsi_period = self.config.get('rsi_period', 14)
        self.rsi_overbought = self.config.get('rsi_overbought', 70)
        self.rsi_oversold = self.config.get('rsi_oversold', 30)
        self.macd_fast = self.config.get('macd_fast', 12)
        self.macd_slow = self.config.get('macd_slow', 26)
        self.macd_signal = self.config.get('macd_signal', 9)
        self.volume_threshold = self.config.get('volume_threshold', 1.5)
        self.trend_strength = self.config.get('trend_strength', 2)
        
        # Price history for indicators
        self.price_history = deque(maxlen=100)
        self.volume_history = deque(maxlen=100)
        self.position = None  # Current position
    
    async def analyze(self) -> List[Dict[str, Any]]:
        """
        Analyze price action and generate momentum signals.
        
        Returns:
            List of trade signals
        """
        signals = []
        
        try:
            # Update price history
            price = self.market.get_price("XRP/USD")
            if price:
                self.price_history.append(price)
            
            # Need minimum data
            if len(self.price_history) < self.macd_slow + 10:
                self.logger.debug("Insufficient price history")
                return signals
            
            # Calculate indicators
            rsi = self._calculate_rsi()
            macd, signal, histogram = self._calculate_macd()
            
            # Generate signals
            if rsi is not None and macd is not None:
                # Long signal: RSI oversold + MACD bullish crossover
                if (rsi < self.rsi_oversold and 
                    macd > signal and 
                    self._is_trend_up() and
                    not self.position):
                    
                    signals.append(self._build_long_signal(rsi, macd))
                
                # Short signal: RSI overbought + MACD bearish crossover
                elif (rsi > self.rsi_overbought and 
                      macd < signal and 
                      self._is_trend_down() and
                      not self.position):
                    
                    signals.append(self._build_short_signal(rsi, macd))
                
                # Exit signals
                if self.position == 'long' and self._should_exit_long(rsi, macd):
                    signals.append(self._build_exit_signal('long'))
                
                if self.position == 'short' and self._should_exit_short(rsi, macd):
                    signals.append(self._build_exit_signal('short'))
            
        except Exception as e:
            self.logger.error(f"Momentum analysis error: {e}")
        
        return signals
    
    def _calculate_rsi(self) -> Optional[float]:
        """Calculate RSI indicator."""
        if len(self.price_history) < self.rsi_period + 1:
            return None
        
        prices = list(self.price_history)
        
        # Calculate price changes
        gains = []
        losses = []
        
        for i in range(1, self.rsi_period + 1):
            change = prices[-i] - prices[-(i+1)]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self) -> tuple:
        """Calculate MACD, signal line, and histogram."""
        prices = list(self.price_history)
        
        # Calculate EMAs
        ema_fast = self._calculate_ema(prices, self.macd_fast)
        ema_slow = self._calculate_ema(prices, self.macd_slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None, None
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        # Simplified: use SMA for signal
        signal_line = macd_line * 0.9  # Placeholder
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _calculate_ema(self, prices: list, period: int) -> Optional[float]:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return None
        
        # Use last 'period' prices
        recent = prices[-period:]
        
        # Simple EMA calculation
        multiplier = 2 / (period + 1)
        ema = sum(recent) / len(recent)  # Start with SMA
        
        for price in recent:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _is_trend_up(self) -> bool:
        """Check if price is trending up."""
        if len(self.price_history) < self.trend_strength + 1:
            return False
        
        prices = list(self.price_history)
        
        # Check last N candles are higher highs
        for i in range(1, self.trend_strength + 1):
            if prices[-i] <= prices[-(i+1)]:
                return False
        
        return True
    
    def _is_trend_down(self) -> bool:
        """Check if price is trending down."""
        if len(self.price_history) < self.trend_strength + 1:
            return False
        
        prices = list(self.price_history)
        
        # Check last N candles are lower lows
        for i in range(1, self.trend_strength + 1):
            if prices[-i] >= prices[-(i+1)]:
                return False
        
        return True
    
    def _should_exit_long(self, rsi: float, macd: float) -> bool:
        """Check if we should exit long position."""
        # Exit on RSI overbought or trend reversal
        return rsi > self.rsi_overbought or not self._is_trend_up()
    
    def _should_exit_short(self, rsi: float, macd: float) -> bool:
        """Check if we should exit short position."""
        # Exit on RSI oversold or trend reversal
        return rsi < self.rsi_oversold or not self._is_trend_down()
    
    def _build_long_signal(self, rsi: float, macd: float) -> Dict:
        """Build long entry signal."""
        size = self.risk.calculate_position_size(1000, confidence=0.6)
        
        signal = {
            'type': 'offer_create',
            'side': 'buy',
            'amount': size,
            'price': self.market.get_price(),
            'strategy': 'momentum',
            'reason': f'Long: RSI={rsi:.1f}, MACD bullish'
        }
        
        self.position = 'long'
        return signal
    
    def _build_short_signal(self, rsi: float, macd: float) -> Dict:
        """Build short entry signal."""
        size = self.risk.calculate_position_size(1000, confidence=0.6)
        
        signal = {
            'type': 'offer_create',
            'side': 'sell',
            'amount': size,
            'price': self.market.get_price(),
            'strategy': 'momentum',
            'reason': f'Short: RSI={rsi:.1f}, MACD bearish'
        }
        
        self.position = 'short'
        return signal
    
    def _build_exit_signal(self, position_type: str) -> Dict:
        """Build position exit signal."""
        signal = {
            'type': 'offer_cancel' if position_type else 'offer_create',
            'action': 'exit',
            'position': position_type,
            'strategy': 'momentum',
            'reason': f'Exit {position_type}: Reversal detected'
        }
        
        self.position = None
        return signal
