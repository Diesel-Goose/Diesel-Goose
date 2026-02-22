"""
Market Data — Real-time price feeds
Aggregates data from multiple sources
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class MarketData:
    """
    Aggregates market data from XRPL DEX and external sources.
    """
    
    def __init__(self, config: Dict):
        self.config = config.get('market_data', {})
        self.logger = logging.getLogger('MarketData')
        
        # Price cache
        self.prices: Dict[str, Dict] = {}
        self.orderbooks: Dict[str, Dict] = {}
        self.last_update: Optional[datetime] = None
        
        # Data sources
        self.sources = self.config.get('sources', ['xrpl_dex'])
        self.update_interval = self.config.get('price_update_seconds', 10)
    
    async def update(self):
        """Update all market data."""
        try:
            # Update from XRPL DEX
            if 'xrpl_dex' in self.sources:
                await self._update_xrpl_dex()
            
            # Update from CoinMarketCap (if API key available)
            if 'coinmarketcap' in self.sources:
                await self._update_coinmarketcap()
            
            self.last_update = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Market data update failed: {e}")
    
    async def _update_xrpl_dex(self):
        """Update prices from XRPL DEX."""
        try:
            # In real implementation, fetch orderbook
            # and calculate mid price
            self.prices['XRP/USD'] = {
                'bid': 0.0,  # Placeholder
                'ask': 0.0,  # Placeholder
                'mid': 0.0,  # Placeholder
                'source': 'xrpl_dex',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"XRPL DEX update failed: {e}")
    
    async def _update_coinmarketcap(self):
        """Update prices from CoinMarketCap."""
        # Requires API key
        pass
    
    def get_price(self, pair: str = "XRP/USD") -> Optional[float]:
        """Get current price for trading pair."""
        if pair in self.prices:
            return self.prices[pair].get('mid')
        return None
    
    def get_orderbook(self, pair: str = "XRP/USD", depth: int = 10) -> Dict:
        """Get orderbook for pair."""
        return self.orderbooks.get(pair, {'bids': [], 'asks': []})
    
    def get_spread(self, pair: str = "XRP/USD") -> Optional[float]:
        """Get bid-ask spread as percentage."""
        if pair not in self.prices:
            return None
        
        price_data = self.prices[pair]
        bid = price_data.get('bid', 0)
        ask = price_data.get('ask', 0)
        mid = price_data.get('mid', 0)
        
        if mid == 0:
            return None
        
        return ((ask - bid) / mid) * 100
    
    def is_fresh(self, max_age_seconds: int = 60) -> bool:
        """Check if data is fresh."""
        if not self.last_update:
            return False
        
        age = (datetime.utcnow() - self.last_update).total_seconds()
        return age < max_age_seconds
