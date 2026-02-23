"""
Alert Manager — Telegram notifications
"""

import os
import logging
from typing import Optional


class AlertManager:
    """
    Sends alerts via Telegram for important events.
    
    Events:
    - Trade executed
    - Error occurred
    - Daily summary
    - Stop loss triggered
    """
    
    # Default tokens - DieselGoose Bot
    DEFAULT_BOT_TOKEN = "8476304097:AAFOPOzPlJ7uG8rWjAQuJsL8adfj1c7kMO8"
    DEFAULT_CHAT_ID = "7491205261"
    
    def __init__(self, config: Dict):
        self.config = config.get('alerts', {})
        self.enabled = self.config.get('enabled', True)  # Enable by default
        
        # Use config values or fall back to defaults
        self.bot_token = self._get_config('telegram', 'bot_token') or self.DEFAULT_BOT_TOKEN
        self.chat_id = self._get_config('telegram', 'chat_id') or self.DEFAULT_CHAT_ID
        
        self.logger = logging.getLogger('AlertManager')
        
        if self.enabled and (not self.bot_token or not self.chat_id):
            self.logger.warning("Alerts enabled but Telegram not configured")
            self.enabled = False
    
    def _get_config(self, section: str, key: str) -> Optional[str]:
        """Get config value, checking environment variables."""
        # Check config
        value = self.config.get(section, {}).get(key, '')
        
        # Check environment (for ${VAR} syntax)
        if value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            value = os.getenv(env_var, '')
        
        return value
    
    async def send(self, message: str):
        """Send alert message."""
        if not self.enabled:
            return
        
        try:
            import aiohttp
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': f"🦆 Chris Dunn Alert\n\n{message}",
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        self.logger.debug(f"Alert sent: {message[:50]}...")
                    else:
                        self.logger.error(f"Alert failed: {response.status}")
        
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
    
    async def send_trade(self, trade: Dict):
        """Send trade notification."""
        if not self.config.get('on_trade', True):
            return
        
        message = (
            f"<b>Trade Executed</b>\n"
            f"Strategy: {trade.get('strategy')}\n"
            f"Type: {trade.get('type')}\n"
            f"Amount: {trade.get('amount')} XRP\n"
            f"Price: ${trade.get('price', 'N/A')}"
        )
        
        await self.send(message)
    
    async def send_error(self, error: str):
        """Send error notification."""
        if not self.config.get('on_error', True):
            return
        
        await self.send(f"<b>❌ ERROR</b>\n{error}")
    
    async def send_daily_summary(self, stats: Dict):
        """Send daily performance summary."""
        if not self.config.get('on_daily_summary', True):
            return
        
        message = (
            f"<b>📊 Daily Summary</b>\n"
            f"Trades: {stats.get('trades', 0)}\n"
            f"P&L: {stats.get('pnl', 0):.4f} XRP\n"
            f"Win Rate: {stats.get('win_rate', 0):.1f}%"
        )
        
        await self.send(message)
