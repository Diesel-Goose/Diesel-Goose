"""
Telegram Alerts for Chris Dunn Production
Real-time notifications on trades, profits, errors
"""

import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import Optional


class TelegramAlerts:
    """Send alerts to Telegram for important events."""
    
    def __init__(self, config: dict):
        self.config = config.get('telegram', {})
        self.logger = logging.getLogger('TelegramAlerts')
        
        self.bot_token = self.config.get('bot_token', '')
        self.chat_id = self.config.get('group_chat_id', '')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        # Alert settings
        self.alert_on_trade = self.config.get('alert_on_trade', True)
        self.alert_on_profit = self.config.get('alert_on_profit_sweep', True)
        self.alert_on_error = self.config.get('alert_on_error', True)
        
    async def send_alert(self, message: str, priority: str = 'normal'):
        """Send message to Telegram."""
        if not self.enabled:
            return
        
        # Add priority emoji
        emoji = {'high': '🚨', 'normal': 'ℹ️', 'profit': '💰', 'error': '❌'}.get(priority, 'ℹ️')
        full_message = f"{emoji} {message}"
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': full_message,
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        self.logger.debug(f"Alert sent: {message[:50]}...")
                    else:
                        self.logger.warning(f"Alert failed: {resp.status}")
        
        except Exception as e:
            self.logger.error(f"Telegram send failed: {e}")
    
    async def send_trade_alert(self, trade: dict):
        """Alert on executed trade."""
        if not self.alert_on_trade:
            return
        
        side = trade.get('side', 'unknown').upper()
        amount = trade.get('amount', 0)
        price = trade.get('price', 0)
        
        emoji = '🟢' if side == 'BUY' else '🔴'
        msg = f"{emoji} <b>Trade Executed</b>\n"
        msg += f"Side: {side}\n"
        msg += f"Amount: {amount:.2f} XRP\n"
        msg += f"Price: {price:.6f} RLUSD\n"
        msg += f"Total: {amount * price:.2f} RLUSD"
        
        await self.send_alert(msg, priority='normal')
    
    async def send_session_summary(self, stats: dict):
        """Send session summary."""
        runtime = stats.get('runtime_minutes', 0)
        trades = stats.get('total_trades', 0)
        pnl = stats.get('session_pnl', 0)
        
        msg = f"🦆 <b>Chris Dunn Session Summary</b>\n\n"
        msg += f"⏱ Runtime: {runtime:.0f} minutes\n"
        msg += f"📊 Trades: {trades}\n"
        msg += f"💰 P&L: {pnl:.4f} XRP\n"
        msg += f"🔥 Status: {'Profitable' if pnl > 0 else 'Building'}"
        
        await self.send_alert(msg, priority='profit' if pnl > 0 else 'normal')
    
    async def send_error_alert(self, error: str):
        """Alert on critical error."""
        if not self.alert_on_error:
            return
        
        msg = f"<b>Error:</b> {error[:200]}"
        await self.send_alert(msg, priority='error')
    
    async def send_startup_message(self, wallet: str, pair: str):
        """Send startup notification."""
        msg = f"🚀 <b>Chris Dunn v2.0 PRODUCTION</b>\n\n"
        msg += f"💼 Wallet: {wallet[:10]}...\n"
        msg += f"📈 Pair: {pair}\n"
        msg += f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}\n"
        msg += f"🎯 Strategy: Market Maker\n"
        msg += f"🔒 Profits → Vault"
        
        await self.send_alert(msg, priority='high')
