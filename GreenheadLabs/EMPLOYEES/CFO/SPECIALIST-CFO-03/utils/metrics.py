"""
Metrics Tracker — P&L and performance analytics
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class MetricsTracker:
    """
    Tracks trading performance metrics:
    - P&L (Profit & Loss)
    - Win rate
    - Sharpe ratio
    - Drawdown
    """
    
    def __init__(self, config: Dict):
        self.config = config.get('metrics', {})
        self.enabled = self.config.get('enabled', True)
        
        # Storage
        self.metrics_file = Path('logs/metrics.json')
        self.trades = []
        self.daily_stats = {}
    
    async def update(self):
        """Update metrics from latest data."""
        if not self.enabled:
            return
        
        # Load existing metrics
        self._load_metrics()
        
        # Calculate current stats
        today = datetime.utcnow().date()
        
        if str(today) not in self.daily_stats:
            self.daily_stats[str(today)] = {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'pnl': 0.0,
                'volume': 0.0
            }
        
        # Save metrics
        self._save_metrics()
    
    async def record_paper_trade(self, strategy: str, signal: Dict):
        """Record paper trade for simulation."""
        trade = {
            'timestamp': datetime.utcnow().isoformat(),
            'mode': 'paper',
            'strategy': strategy,
            'signal': signal,
            'filled_price': signal.get('price', 0),
            'status': 'filled'
        }
        self.trades.append(trade)
    
    async def record_live_trade(self, strategy: str, signal: Dict, result: Dict):
        """Record live trade with actual result."""
        trade = {
            'timestamp': datetime.utcnow().isoformat(),
            'mode': 'live',
            'strategy': strategy,
            'signal': signal,
            'result': result,
            'status': result.get('status', 'unknown')
        }
        self.trades.append(trade)
    
    async def get_pnl(self) -> Dict[str, float]:
        """Calculate current P&L."""
        total_pnl = 0.0
        daily_pnl = 0.0
        unrealized = 0.0
        
        today = datetime.utcnow().date()
        
        for trade in self.trades:
            # Calculate P&L
            pnl = trade.get('pnl', 0)
            total_pnl += pnl
            
            # Check if today
            trade_date = datetime.fromisoformat(trade['timestamp']).date()
            if trade_date == today:
                daily_pnl += pnl
        
        return {
            'total_pnl': round(total_pnl, 4),
            'daily_pnl': round(daily_pnl, 4),
            'unrealized_pnl': round(unrealized, 4),
            'total_trades': len(self.trades)
        }
    
    def get_win_rate(self) -> float:
        """Calculate win rate percentage."""
        if not self.trades:
            return 0.0
        
        wins = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        return (wins / len(self.trades)) * 100
    
    def _load_metrics(self):
        """Load metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.daily_stats = data.get('daily', {})
                    self.trades = data.get('trades', [])
            except:
                pass
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            self.metrics_file.parent.mkdir(exist_ok=True)
            with open(self.metrics_file, 'w') as f:
                json.dump({
                    'daily': self.daily_stats,
                    'trades': self.trades[-1000:]  # Keep last 1000
                }, f, indent=2)
        except Exception as e:
            print(f"Failed to save metrics: {e}")
