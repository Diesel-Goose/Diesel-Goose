"""
XRPL Production Client
Real WebSocket connection with automatic signing
"""

import json
import asyncio
from typing import Dict, Optional, Any, List
from decimal import Decimal
import logging

# xrpl-py for production
try:
    from xrpl.clients import WebsocketClient
    from xrpl.wallet import Wallet
    from xrpl.models.requests import BookOffers, AccountInfo, AccountOffers
    from xrpl.models.transactions import OfferCreate, OfferCancel, Payment
    from xrpl.models.amounts import IssuedCurrencyAmount
    from xrpl.utils import xrp_to_drops, drops_to_xrp
    XRPL_AVAILABLE = True
except ImportError:
    XRPL_AVAILABLE = False
    logging.warning("xrpl-py not installed. Run: pip install xrpl-py")


class XRPLProductionClient:
    """Production XRPL client with hot wallet signing."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('XRPLProduction')
        
        # Wallet setup
        self.address = config['wallet']['address']
        self.secret = config['wallet']['secret']
        self.vault_address = config['wallet'].get('vault_address', '')
        
        # Trading pair
        self.base = config['trading']['base']  # XRP
        self.quote = config['trading']['quote']  # RLUSD
        self.quote_issuer = config['trading']['quote_issuer']
        
        # XRPL connection
        self.ws_url = config['xrpl']['websocket_url']
        self.client = None
        self.wallet = None
        
        if XRPL_AVAILABLE and self.secret:
            try:
                self.wallet = Wallet.from_seed(self.secret)
                if self.wallet.classic_address != self.address:
                    self.logger.error("Secret does not match provided address!")
                    self.wallet = None
                else:
                    self.logger.info(f"Wallet loaded: {self.address}")
            except Exception as e:
                self.logger.error(f"Failed to load wallet: {e}")
    
    async def connect(self) -> bool:
        """Establish WebSocket connection to XRPL."""
        if not XRPL_AVAILABLE:
            self.logger.error("xrpl-py not available")
            return False
        
        try:
            self.client = WebsocketClient(self.ws_url)
            await self.client.open()
            self.logger.info(f"Connected to {self.ws_url}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close WebSocket connection."""
        if self.client:
            await self.client.close()
            self.logger.info("Disconnected from XRPL")
    
    async def get_balance(self) -> Dict[str, float]:
        """Get wallet balances (XRP + RLUSD)."""
        if not self.client:
            return {'xrp': 0.0, 'rlusd': 0.0}
        
        try:
            # Get XRP balance
            account_info = await self.client.request(AccountInfo(
                account=self.address
            ))
            xrp_balance = drops_to_xrp(account_info.result['account_data']['Balance'])
            
            # Get RLUSD balance from account lines
            # (simplified - would use AccountLines in full implementation)
            rlusd_balance = 0.0  # Placeholder - fetch from trust lines
            
            return {
                'xrp': float(xrp_balance),
                'rlusd': rlusd_balance
            }
        except Exception as e:
            self.logger.error(f"Balance fetch failed: {e}")
            return {'xrp': 0.0, 'rlusd': 0.0}
    
    async def get_orderbook(self, limit: int = 20) -> Dict:
        """Get XRP/RLUSD orderbook."""
        if not self.client:
            return {'bids': [], 'asks': [], 'mid': 0.0}
        
        try:
            # Get bids (people buying XRP with RLUSD)
            bids_request = BookOffers(
                taker_gets={
                    'currency': self.quote,
                    'issuer': self.quote_issuer
                },
                taker_pays='0',
                limit=limit
            )
            bids_response = await self.client.request(bids_request)
            
            # Get asks (people selling XRP for RLUSD)
            asks_request = BookOffers(
                taker_gets='0',
                taker_pays={
                    'currency': self.quote,
                    'issuer': self.quote_issuer
                },
                limit=limit
            )
            asks_response = await self.client.request(asks_request)
            
            # Parse into usable format
            bids = self._parse_offers(bids_response.result.get('offers', []), 'bid')
            asks = self._parse_offers(asks_response.result.get('offers', []), 'ask')
            
            # Calculate mid price
            mid = 0.0
            if bids and asks:
                mid = (bids[0]['price'] + asks[0]['price']) / 2
            
            return {
                'bids': bids,
                'asks': asks,
                'mid': mid,
                'spread': asks[0]['price'] - bids[0]['price'] if bids and asks else 0
            }
        except Exception as e:
            self.logger.error(f"Orderbook fetch failed: {e}")
            return {'bids': [], 'asks': [], 'mid': 0.0, 'spread': 0}
    
    def _parse_offers(self, offers: List, side: str) -> List[Dict]:
        """Parse XRPL offers into standardized format."""
        parsed = []
        for offer in offers:
            try:
                # XRPL offers are TakerPays/TakerGets
                # For bids: TakerGets = RLUSD, TakerPays = XRP
                # For asks: TakerGets = XRP, TakerPays = RLUSD
                
                taker_gets = offer.get('TakerGets', {})
                taker_pays = offer.get('TakerPays', {})
                
                if side == 'bid':
                    # Bid: Someone buying XRP, paying RLUSD
                    xrp_amount = float(taker_pays) / 1_000_000  # drops to XRP
                    rlusd_amount = float(taker_gets.get('value', 0))
                    price = rlusd_amount / xrp_amount if xrp_amount > 0 else 0
                else:
                    # Ask: Someone selling XRP, getting RLUSD
                    xrp_amount = float(taker_gets) / 1_000_000
                    rlusd_amount = float(taker_pays.get('value', 0))
                    price = rlusd_amount / xrp_amount if xrp_amount > 0 else 0
                
                parsed.append({
                    'price': price,
                    'amount': xrp_amount,
                    'total': rlusd_amount,
                    'account': offer.get('Account', ''),
                    'sequence': offer.get('Sequence', 0)
                })
            except Exception as e:
                self.logger.warning(f"Failed to parse offer: {e}")
        
        # Sort: bids descending (highest first), asks ascending (lowest first)
        parsed.sort(key=lambda x: x['price'], reverse=(side == 'bid'))
        return parsed
    
    async def create_offer(self, side: str, amount: float, price: float) -> Dict:
        """
        Create a DEX offer (hot wallet auto-signs).
        
        side: 'buy' (bid) or 'sell' (ask)
        amount: XRP amount
        price: Price in RLUSD per XRP
        """
        if not self.client or not self.wallet:
            return {'error': 'Not connected or wallet not loaded'}
        
        try:
            drops = xrp_to_drops(amount)
            rlusd_value = str(Decimal(amount) * Decimal(price))
            
            if side == 'buy':
                # Buy XRP: TakerGets = RLUSD, TakerPays = XRP (drops)
                taker_gets = IssuedCurrencyAmount(
                    currency=self.quote,
                    issuer=self.quote_issuer,
                    value=rlusd_value
                )
                taker_pays = str(int(drops))
            else:
                # Sell XRP: TakerGets = XRP (drops), TakerPays = RLUSD
                taker_gets = str(int(drops))
                taker_pays = IssuedCurrencyAmount(
                    currency=self.quote,
                    issuer=self.quote_issuer,
                    value=rlusd_value
                )
            
            offer_tx = OfferCreate(
                account=self.address,
                taker_gets=taker_gets,
                taker_pays=taker_pays
            )
            
            # Sign and submit
            from xrpl.transaction import sign_and_submit
            response = await sign_and_submit(offer_tx, self.client, self.wallet)
            
            result = response.result
            if result.get('engine_result') == 'tesSUCCESS':
                return {
                    'success': True,
                    'tx_hash': result.get('tx_json', {}).get('hash'),
                    'sequence': result.get('tx_json', {}).get('Sequence'),
                    'side': side,
                    'amount': amount,
                    'price': price
                }
            else:
                return {
                    'success': False,
                    'error': result.get('engine_result_message', 'Unknown error'),
                    'code': result.get('engine_result')
                }
        
        except Exception as e:
            self.logger.error(f"Offer creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cancel_offer(self, sequence: int) -> Dict:
        """Cancel an existing offer by sequence number."""
        if not self.client or not self.wallet:
            return {'error': 'Not connected or wallet not loaded'}
        
        try:
            cancel_tx = OfferCancel(
                account=self.address,
                offer_sequence=sequence
            )
            
            from xrpl.transaction import sign_and_submit
            response = await sign_and_submit(cancel_tx, self.client, self.wallet)
            
            result = response.result
            return {
                'success': result.get('engine_result') == 'tesSUCCESS',
                'tx_hash': result.get('tx_json', {}).get('hash'),
                'sequence': sequence
            }
        except Exception as e:
            self.logger.error(f"Cancel failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_open_offers(self) -> List[Dict]:
        """Get all open offers for this account."""
        if not self.client:
            return []
        
        try:
            response = await self.client.request(AccountOffers(
                account=self.address
            ))
            
            offers = []
            for offer in response.result.get('offers', []):
                offers.append({
                    'sequence': offer.get('seq'),
                    'taker_gets': offer.get('taker_gets'),
                    'taker_pays': offer.get('taker_pays')
                })
            
            return offers
        except Exception as e:
            self.logger.error(f"Failed to get open offers: {e}")
            return []
    
    async def send_payment(self, to_address: str, amount: float, currency: str = 'XRP') -> Dict:
        """Send XRP or RLUSD to vault address."""
        if not self.client or not self.wallet:
            return {'error': 'Not connected or wallet not loaded'}
        
        try:
            if currency == 'XRP':
                payment_amount = str(int(xrp_to_drops(amount)))
            else:
                payment_amount = IssuedCurrencyAmount(
                    currency=self.quote,
                    issuer=self.quote_issuer,
                    value=str(amount)
                )
            
            payment_tx = Payment(
                account=self.address,
                destination=to_address,
                amount=payment_amount
            )
            
            from xrpl.transaction import sign_and_submit
            response = await sign_and_submit(payment_tx, self.client, self.wallet)
            
            result = response.result
            return {
                'success': result.get('engine_result') == 'tesSUCCESS',
                'tx_hash': result.get('tx_json', {}).get('hash'),
                'to': to_address,
                'amount': amount,
                'currency': currency
            }
        except Exception as e:
            self.logger.error(f"Payment failed: {e}")
            return {'success': False, 'error': str(e)}
