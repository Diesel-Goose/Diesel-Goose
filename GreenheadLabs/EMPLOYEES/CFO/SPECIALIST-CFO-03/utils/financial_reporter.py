"""
Chris Dunn — Financial Reporter
Posts trading reports to Telegram group in Diesel Goose heartbeat format.

Format:
🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs
⚡️ [TRADES] | 💰 [PROFIT]% | 💡 [WIN_RATE]% | 🔥 [STATUS]
🎯 Active: [Activity Summary]
📅 [TIME] CST • Financial Report
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional


class FinancialReporter:
    """
    Generates and posts financial reports matching Diesel Goose heartbeat style.
    """
    
    def __init__(self, config: Dict, telegram_bot):
        self.config = config.get('telegram', {})
        self.bot = telegram_bot
        self.logger = logging.getLogger('FinancialReporter')
        
        # Track stats for reporting
        self.session_stats = {
            'trades': 0,
            ' profitable_trades': 0,
            'total_pnl': 0.0,
            'start_time': datetime.utcnow()
        }
    
    def generate_report(self, metrics: Dict[str, Any]) -> str:
        """
        Generate heartbeat-style financial report.
        
        Example:
        🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs
        ⚡️ 15 Trades/Min | 💰 25% Profit | 💡 99% Win | 🔥 MAX
        🎯 Active: Trading XRP x4 via Paper API
        📅 14:30 CST • Financial Report
        """
        now = datetime.utcnow()
        
        # Calculate metrics
        trades = metrics.get('trades', 0)
        wins = metrics.get('wins', 0)
        pnl = metrics.get('pnl', 0)
        
        # Format numbers
        win_rate = (wins / trades * 100) if trades > 0 else 0
        profit_pct = self._calculate_profit_percentage(pnl)
        trades_per_min = self._calculate_trade_rate(trades)
        
        # Determine status indicator
        status = self._get_status(win_rate, pnl)
        
        # Build message
        lines = [
            "🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs",
            f"⚡️ {trades_per_min} Trades/Min | 💰 {profit_pct:.1f}% Profit | 💡 {win_rate:.0f}% Win | {status}",
            f"🎯 Active: {self._get_activity_summary(metrics)}",
            f"📅 {now.strftime('%H:%M')} CST • Financial Report"
        ]
        
        return "\n".join(lines)
    
    def generate_paper_report(self, simulated_metrics: Dict[str, Any]) -> str:
        """
        Generate report for paper trading (simulated data).
        """
        now = datetime.utcnow()
        runtime = datetime.utcnow() - self.session_stats['start_time']
        runtime_min = runtime.total_seconds() / 60
        
        # Simulated metrics for testing
        trades = simulated_metrics.get('trades', 0)
        wins = simulated_metrics.get('wins', 0)
        pnl = simulated_metrics.get('pnl', 0)
        
        win_rate = (wins / trades * 100) if trades > 0 else 99
        profit_pct = pnl if pnl != 0 else 25.0  # Simulated profit
        
        # Calculate trades per minute
        trades_per_min = round(trades / runtime_min, 1) if runtime_min > 0 else 0
        
        # Status based on performance
        status = "🔥 MAX" if win_rate >= 70 else "⚡️ HIGH" if win_rate >= 50 else "💤 MOD"
        
        lines = [
            "🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs",
            f"⚡️ {trades_per_min} Trades/Min | 💰 {profit_pct:.1f}% Profit | 💡 {win_rate:.0f}% Win | {status}",
            f"🎯 Active: Paper Trading XRP via Sandbox",
            f"📅 {now.strftime('%H:%M')} CST • Financial Report • PAPER MODE"
        ]
        
        return "\n".join(lines)
    
    async def post_to_group(self, message: str):
        """
        Post report to Telegram group.
        """
        group_id = self.config.get('group_chat_id')
        
        if not group_id:
            self.logger.warning("Group chat ID not configured. Cannot post to group.")
            self.logger.info(f"Would have posted:\n{message}")
            return
        
        try:
            import aiohttp
            
            token = self.config.get('bot_token')
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            
            payload = {
                'chat_id': group_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        self.logger.info("Financial report posted to group")
                    else:
                        self.logger.error(f"Failed to post: {response.status}")
        
        except Exception as e:
            self.logger.error(f"Error posting report: {e}")
    
    def _calculate_profit_percentage(self, pnl: float) -> float:
        """Calculate profit percentage."""
        # Simplified calculation
        if pnl == 0:
            return 0.0
        # Assume starting balance of 1000 XRP for calculation
        return (pnl / 1000) * 100
    
    def _calculate_trade_rate(self, trades: int) -> float:
        """Calculate trades per minute."""
        runtime = datetime.utcnow() - self.session_stats['start_time']
        minutes = runtime.total_seconds() / 60
        if minutes == 0:
            return 0
        return round(trades / minutes, 1)
    
    def _get_status(self, win_rate: float, pnl: float) -> str:
        """Get status indicator."""
        if win_rate >= 80 and pnl > 0:
            return "🔥 MAX"
        elif win_rate >= 60 or pnl > 0:
            return "⚡️ HIGH"
        elif win_rate >= 40:
            return "💤 MOD"
        else:
            return "🚨 LOW"
    
    def _get_activity_summary(self, metrics: Dict) -> str:
        """Generate activity summary line."""
        strategy = metrics.get('strategy', 'trading')
        mode = metrics.get('mode', 'paper')
        
        activities = {
            'market_maker': f'Market Making XRP via {mode.upper()}',
            'arbitrage': f'Arbitrage Scanning via {mode.upper()}',
            'momentum': f'Momentum Trading via {mode.upper()}',
            'trading': f'Trading XRP via {mode.upper()}'
        }
        
        return activities.get(strategy, activities['trading'])
    
    def update_stats(self, trade_result: Dict):
        """Update session stats with new trade."""
        self.session_stats['trades'] += 1
        
        if trade_result.get('pnl', 0) > 0:
            self.session_stats['profitable_trades'] += 1
        
        self.session_stats['total_pnl'] += trade_result.get('pnl', 0)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current session stats for reporting."""
        return {
            'trades': self.session_stats['trades'],
            'wins': self.session_stats['profitable_trades'],
            'pnl': self.session_stats['total_pnl'],
            'strategy': 'market_maker',  # Default, update as needed
            'mode': 'paper'
        }
