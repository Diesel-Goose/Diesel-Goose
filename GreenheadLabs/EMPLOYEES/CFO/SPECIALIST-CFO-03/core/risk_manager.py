"""
Risk Manager — Capital preservation enforcer
Non-negotiable risk limits
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class RiskManager:
    """
    Enforces trading risk limits.
    
    Mission: Protect capital. Every trade must pass risk checks.
    """
    
    def __init__(self, config: Dict):
        self.config = config.get('risk', {})
        self.logger = logging.getLogger('RiskManager')
        
        # Track daily stats
        self.daily_stats = {
            'date': datetime.utcnow().date(),
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'pnl_xrp': 0.0,
            'consecutive_losses': 0
        }
        
        # Track positions
        self.open_positions = {}
        self.daily_loss_xrp = 0.0
    
    def validate_config(self) -> bool:
        """Validate risk configuration."""
        required = [
            'max_position_size_xrp',
            'max_daily_loss_xrp',
            'stop_loss_pct',
            'max_open_orders'
        ]
        
        for key in required:
            if key not in self.config:
                self.logger.error(f"Missing risk config: {key}")
                return False
        
        # Sanity checks
        if self.config['max_position_size_xrp'] <= 0:
            self.logger.error("max_position_size_xrp must be positive")
            return False
        
        if self.config['stop_loss_pct'] > 10:
            self.logger.warning("stop_loss_pct > 10% — Very risky!")
        
        return True
    
    def approve_trade(self, signal: Dict[str, Any]) -> bool:
        """
        Approve or reject a trade signal.
        
        Returns True if trade passes all risk checks.
        """
        self._reset_daily_stats_if_needed()
        
        trade_size = signal.get('amount', 0)
        trade_type = signal.get('type', 'unknown')
        
        # Check 1: Position size limit
        max_size = self.config.get('max_position_size_xrp', 1000)
        if trade_size > max_size:
            self.logger.warning(
                f"❌ REJECTED: Trade size {trade_size} > max {max_size}"
            )
            return False
        
        # Check 2: Minimum order size
        min_size = self.config.get('min_order_size_xrp', 10)
        if trade_size < min_size:
            self.logger.warning(
                f"❌ REJECTED: Trade size {trade_size} < min {min_size}"
            )
            return False
        
        # Check 3: Max open orders
        max_orders = self.config.get('max_open_orders', 10)
        current_orders = len(self.open_positions)
        if current_orders >= max_orders:
            self.logger.warning(
                f"❌ REJECTED: Max orders ({max_orders}) reached"
            )
            return False
        
        # Check 4: Daily loss limit
        max_daily_loss = self.config.get('max_daily_loss_xrp', 500)
        if self.daily_loss_xrp >= max_daily_loss:
            self.logger.error(
                f"🛑 HALT: Daily loss {self.daily_loss_xrp} >= limit {max_daily_loss}"
            )
            return False
        
        # Check 5: Consecutive losses
        max_consecutive = self.config.get('halt_after_consecutive_losses', 5)
        if self.daily_stats['consecutive_losses'] >= max_consecutive:
            self.logger.error(
                f"🛑 HALT: {self.daily_stats['consecutive_losses']} consecutive losses"
            )
            return False
        
        # Check 6: Max orders per hour
        # (Implementation would track hourly counts)
        
        self.logger.info(f"✅ APPROVED: {trade_type} {trade_size} XRP")
        return True
    
    def calculate_position_size(self, 
                                available_capital: float,
                                confidence: float = 0.5) -> float:
        """
        Calculate safe position size based on Kelly Criterion (conservative).
        
        Args:
            available_capital: Total XRP available
            confidence: Strategy confidence (0-1)
        
        Returns:
            Recommended position size in XRP
        """
        max_pct = self.config.get('max_position_pct', 5.0) / 100
        max_size = self.config.get('max_position_size_xrp', 1000)
        
        # Conservative Kelly: f* = (p*b - q) / b
        # Simplified: Use confidence-adjusted fixed fraction
        position_pct = max_pct * confidence
        position_size = available_capital * position_pct
        
        # Cap at max size
        return min(position_size, max_size)
    
    def check_stop_loss(self, 
                       entry_price: float,
                       current_price: float,
                       position_type: str) -> bool:
        """
        Check if stop loss should trigger.
        
        Returns True if stop loss hit.
        """
        stop_pct = self.config.get('stop_loss_pct', 2.0) / 100
        
        if position_type == 'long':
            loss_pct = (entry_price - current_price) / entry_price
        else:  # short
            loss_pct = (current_price - entry_price) / entry_price
        
        if loss_pct >= stop_pct:
            self.logger.warning(
                f"🛑 STOP LOSS: Loss {loss_pct:.2%} >= limit {stop_pct:.2%}"
            )
            return True
        
        return False
    
    def record_trade_result(self, pnl_xrp: float):
        """Record trade outcome for risk tracking."""
        self._reset_daily_stats_if_needed()
        
        self.daily_stats['trades'] += 1
        self.daily_stats['pnl_xrp'] += pnl_xrp
        
        if pnl_xrp > 0:
            self.daily_stats['wins'] += 1
            self.daily_stats['consecutive_losses'] = 0
        else:
            self.daily_stats['losses'] += 1
            self.daily_stats['consecutive_losses'] += 1
            self.daily_loss_xrp += abs(pnl_xrp)
    
    def daily_limit_reached(self) -> bool:
        """Check if daily loss limit hit."""
        max_loss = self.config.get('max_daily_loss_xrp', 500)
        return self.daily_loss_xrp >= max_loss
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get current daily trading stats."""
        self._reset_daily_stats_if_needed()
        
        trades = self.daily_stats['trades']
        wins = self.daily_stats['wins']
        
        return {
            'date': str(self.daily_stats['date']),
            'trades': trades,
            'wins': wins,
            'losses': self.daily_stats['losses'],
            'win_rate': wins / trades if trades > 0 else 0,
            'pnl_xrp': self.daily_stats['pnl_xrp'],
            'consecutive_losses': self.daily_stats['consecutive_losses'],
            'daily_loss_xrp': self.daily_loss_xrp,
            'limit_reached': self.daily_limit_reached()
        }
    
    def _reset_daily_stats_if_needed(self):
        """Reset stats if new day."""
        today = datetime.utcnow().date()
        if today != self.daily_stats['date']:
            self.daily_stats = {
                'date': today,
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'pnl_xrp': 0.0,
                'consecutive_losses': 0
            }
            self.daily_loss_xrp = 0.0
