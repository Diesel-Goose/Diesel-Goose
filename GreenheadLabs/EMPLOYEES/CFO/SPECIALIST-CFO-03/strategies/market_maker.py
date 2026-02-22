"""
Market Maker Strategy
Capture bid-ask spread by providing liquidity
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal


class MarketMaker:
    """
    Market Making Strategy
    
    Places buy orders below market, sell orders above.
    Captures spread when both sides fill.
    
    Key Parameters:
    - spread_pct: Target distance from mid price
    - order_size: Amount per order
    - max_orders: Limit total exposure
    """
    
    def __init__(self, config, xrpl_client, risk_manager, order_manager):
        self.config = config.get('strategies', {}).get('market_maker', {})
        self.logger = logging.getLogger('MarketMaker')
        
        self.xrpl = xrpl_client
        self.risk = risk_manager
        self.orders = order_manager
        
        # Strategy parameters
        self.spread_pct = self.config.get('spread_pct', 0.5) / 100
        self.order_size = self.config.get('order_size_xrp', 100)
        self.max_orders_each_side = self.config.get('max_orders_each_side', 3)
        self.rebalance_threshold = self.config.get('rebalance_threshold_pct', 1.0) / 100
        self.target_inventory = self.config.get('target_inventory_pct', 50.0) / 100
        
        # State
        self.open_bids = []  # Buy orders
        self.open_asks = []  # Sell orders
        self.inventory_ratio = 0.5  # Current XRP ratio
    
    async def analyze(self) -> List[Dict[str, Any]]:
        """
        Analyze market and generate MM signals.
        
        Returns:
            List of trade signals
        """
        signals = []
        
        try:
            # Get current price
            price = await self._get_mid_price()
            if not price:
                self.logger.warning("No price data available")
                return signals
            
            # Check inventory balance
            self.inventory_ratio = await self._calculate_inventory()
            
            # Calculate order prices
            bid_price = price * (1 - self.spread_pct)
            ask_price = price * (1 + self.spread_pct)
            
            # Check if we need to place buy orders
            current_bids = len(self.open_bids)
            if current_bids < self.max_orders_each_side and self._should_buy():
                signals.append({
                    'type': 'offer_create',
                    'side': 'buy',
                    'amount': self.order_size,
                    'price': bid_price,
                    'taker_gets': {
                        'currency': 'USD',
                        'value': str(self.order_size * bid_price),
                        'issuer': 'rvYAfWj5gh67oV6fW32'  # Bitstamp USD
                    },
                    'taker_pays': str(self.order_size * 1_000_000),  # Drops
                    'strategy': 'market_maker',
                    'reason': f'Bid @ {bid_price:.4f}'
                })
            
            # Check if we need to place sell orders
            current_asks = len(self.open_asks)
            if current_asks < self.max_orders_each_side and self._should_sell():
                signals.append({
                    'type': 'offer_create',
                    'side': 'sell',
                    'amount': self.order_size,
                    'price': ask_price,
                    'taker_gets': str(self.order_size * 1_000_000),  # Drops
                    'taker_pays': {
                        'currency': 'USD',
                        'value': str(self.order_size * ask_price),
                        'issuer': 'rvYAfWj5gh67oV6fW32'
                    },
                    'strategy': 'market_maker',
                    'reason': f'Ask @ {ask_price:.4f}'
                })
            
            # Check for inventory rebalance
            rebalance_signals = await self._check_rebalance(price)
            signals.extend(rebalance_signals)
            
        except Exception as e:
            self.logger.error(f"Market maker analysis error: {e}")
        
        return signals
    
    async def _get_mid_price(self) -> Optional[float]:
        """Get current mid price."""
        # In real implementation, fetch from market data
        # Placeholder
        return 0.50  # Assume $0.50 XRP
    
    async def _calculate_inventory(self) -> float:
        """Calculate current XRP inventory ratio (0-1)."""
        try:
            # Get balances
            xrp_balance = await self.xrpl.get_balance()
            # Get USD value (simplified)
            usd_value = xrp_balance * 0.50  # Placeholder price
            
            total_value = xrp_balance + usd_value  # Simplified
            if total_value == 0:
                return 0.5
            
            return xrp_balance / total_value
        except:
            return 0.5
    
    def _should_buy(self) -> bool:
        """Determine if we should place buy orders."""
        # Buy more if inventory is below target
        return self.inventory_ratio < (self.target_inventory + self.rebalance_threshold)
    
    def _should_sell(self) -> bool:
        """Determine if we should place sell orders."""
        # Sell more if inventory is above target
        return self.inventory_ratio > (self.target_inventory - self.rebalance_threshold)
    
    async def _check_rebalance(self, current_price: float) -> List[Dict]:
        """Check if inventory needs rebalancing."""
        signals = []
        
        deviation = abs(self.inventory_ratio - self.target_inventory)
        if deviation > self.rebalance_threshold:
            if self.inventory_ratio > self.target_inventory:
                # Too much XRP, sell some
                rebalance_amount = self._calculate_rebalance_amount()
                if rebalance_amount > 0:
                    signals.append({
                        'type': 'offer_create',
                        'side': 'sell',
                        'amount': rebalance_amount,
                        'price': current_price,
                        'taker_gets': str(rebalance_amount * 1_000_000),
                        'taker_pays': {
                            'currency': 'USD',
                            'value': str(rebalance_amount * current_price),
                            'issuer': 'rvYAfWj5gh67oV6fW32'
                        },
                        'strategy': 'market_maker',
                        'reason': f'Rebalance: inventory {self.inventory_ratio:.1%} vs target {self.target_inventory:.1%}'
                    })
            else:
                # Too much USD, buy XRP
                rebalance_amount = self._calculate_rebalance_amount()
                if rebalance_amount > 0:
                    signals.append({
                        'type': 'offer_create',
                        'side': 'buy',
                        'amount': rebalance_amount,
                        'price': current_price,
                        'taker_gets': {
                            'currency': 'USD',
                            'value': str(rebalance_amount * current_price),
                            'issuer': 'rvYAfWj5gh67oV6fW32'
                        },
                        'taker_pays': str(rebalance_amount * 1_000_000),
                        'strategy': 'market_maker',
                        'reason': f'Rebalance: inventory {self.inventory_ratio:.1%} vs target {self.target_inventory:.1%}'
                    })
        
        return signals
    
    def _calculate_rebalance_amount(self) -> float:
        """Calculate amount to rebalance."""
        # Rebalance 10% of order size at a time
        return self.order_size * 0.1
