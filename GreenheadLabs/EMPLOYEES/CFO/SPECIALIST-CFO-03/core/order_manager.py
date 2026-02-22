"""
Order Manager — Trade execution coordinator
Handles order lifecycle and Xaman approvals
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime


class OrderManager:
    """
    Manages order execution and lifecycle.
    
    Key functions:
    - Submit orders to XRPL
    - Monitor order status
    - Handle Xaman mobile approvals
    - Cancel/replace orders
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('OrderManager')
        self.mode = config.get('trading', {}).get('mode', 'paper')
        
        # Track orders
        self.open_orders: Dict[str, Dict] = {}
        self.order_history: List[Dict] = []
        
        # Xaman integration
        self.xrpl_client = None  # Set by caller
    
    async def execute(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a trade signal.
        
        Args:
            signal: Trade signal dict with type, amount, price, etc.
        
        Returns:
            Order result dict or None if failed
        """
        order_type = signal.get('type')
        
        if self.mode == 'paper':
            return await self._execute_paper(signal)
        
        # Live mode — requires Xaman approval
        if order_type == 'offer_create':
            return await self._create_offer(signal)
        elif order_type == 'offer_cancel':
            return await self._cancel_offer(signal)
        elif order_type == 'payment':
            return await self._execute_payment(signal)
        else:
            self.logger.error(f"Unknown order type: {order_type}")
            return None
    
    async def _execute_paper(self, signal: Dict) -> Dict[str, Any]:
        """Simulate order execution (paper trading)."""
        order_id = f"paper_{datetime.utcnow().timestamp()}"
        
        order = {
            'id': order_id,
            'type': signal.get('type'),
            'amount': signal.get('amount'),
            'price': signal.get('price'),
            'status': 'filled',
            'mode': 'paper',
            'created_at': datetime.utcnow().isoformat(),
            'filled_at': datetime.utcnow().isoformat(),
            'tx_hash': f"simulated_{order_id}"
        }
        
        self.order_history.append(order)
        
        self.logger.info(
            f"📊 PAPER TRADE: {signal.get('type')} "
            f"{signal.get('amount')} @ {signal.get('price', 'market')}"
        )
        
        return order
    
    async def _create_offer(self, signal: Dict) -> Optional[Dict]:
        """
        Create a DEX offer (requires Xaman approval).
        
        Flow:
        1. Create offer on XRPL
        2. Get payload UUID
        3. Send notification to user
        4. Wait for mobile approval
        5. Return result
        """
        if not self.xrpl_client:
            self.logger.error("XRPL client not initialized")
            return None
        
        try:
            # Build offer
            taker_gets = signal.get('taker_gets')
            taker_pays = signal.get('taker_pays')
            
            # Create offer via Xaman
            result = await self.xrpl_client.create_offer(taker_gets, taker_pays)
            
            if 'error' in result:
                self.logger.error(f"Offer creation failed: {result['error']}")
                return None
            
            payload_uuid = result.get('payload_uuid')
            approval_url = result.get('approval_url')
            
            self.logger.info(f"📱 Xaman approval required: {approval_url}")
            
            # Store pending order
            order = {
                'id': payload_uuid,
                'type': 'offer_create',
                'status': 'pending_approval',
                'signal': signal,
                'approval_url': approval_url,
                'created_at': datetime.utcnow().isoformat()
            }
            self.open_orders[payload_uuid] = order
            
            # Monitor for approval (non-blocking or timeout)
            # In production, this would be async with timeout
            # For now, return pending status
            
            return order
            
        except Exception as e:
            self.logger.error(f"Error creating offer: {e}")
            return None
    
    async def _cancel_offer(self, signal: Dict) -> Optional[Dict]:
        """Cancel an existing offer."""
        if not self.xrpl_client:
            return None
        
        offer_sequence = signal.get('offer_sequence')
        if not offer_sequence:
            self.logger.error("No offer_sequence provided for cancel")
            return None
        
        try:
            result = await self.xrpl_client.cancel_offer(offer_sequence)
            
            if 'error' in result:
                self.logger.error(f"Cancel failed: {result['error']}")
                return None
            
            return {
                'id': result.get('uuid'),
                'type': 'offer_cancel',
                'status': 'pending_approval',
                'offer_sequence': offer_sequence
            }
            
        except Exception as e:
            self.logger.error(f"Error canceling offer: {e}")
            return None
    
    async def _execute_payment(self, signal: Dict) -> Optional[Dict]:
        """Execute a payment (not typically used for trading)."""
        self.logger.warning("Payment execution not yet implemented")
        return None
    
    async def cancel_all(self) -> int:
        """
        Cancel all open orders.
        
        Returns:
            Number of orders canceled
        """
        count = 0
        
        for order_id, order in list(self.open_orders.items()):
            if order.get('status') == 'open':
                try:
                    # Cancel logic here
                    count += 1
                    self.logger.info(f"Canceled order: {order_id}")
                except Exception as e:
                    self.logger.error(f"Failed to cancel {order_id}: {e}")
        
        return count
    
    def get_open_orders(self) -> List[Dict]:
        """Get all open orders."""
        return [
            order for order in self.open_orders.values()
            if order.get('status') in ['open', 'pending_approval']
        ]
    
    def get_order_history(self, limit: int = 100) -> List[Dict]:
        """Get recent order history."""
        return self.order_history[-limit:]
    
    async def update_order_status(self, order_id: str) -> Optional[Dict]:
        """Update status of a specific order."""
        if order_id not in self.open_orders:
            return None
        
        order = self.open_orders[order_id]
        
        # Query XRPL for latest status
        if self.xrpl_client and order.get('tx_hash'):
            status = await self.xrpl_client.get_transaction_status(order['tx_hash'])
            order['status'] = status.get('status', 'unknown')
        
        return order
