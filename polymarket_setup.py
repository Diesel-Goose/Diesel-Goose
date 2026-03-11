#!/usr/bin/env python3
"""
Polymarket Real Trading Setup Guide
Greenhead Labs - Woody Pintail

This script checks prerequisites and generates setup instructions
"""

import os
import sys

def check_prerequisites():
    """Check if prerequisites are met"""
    print("=" * 70)
    print("POLYMARKET REAL TRADING SETUP")
    print("Greenhead Labs - Woody Pintail")
    print("=" * 70)
    print()
    
    # Check for existing credentials
    api_key = os.getenv('POLYMARKET_API_KEY')
    private_key = os.getenv('POLYMARKET_PRIVATE_KEY')
    
    if api_key and private_key:
        print("✅ API credentials found in environment")
    else:
        print("❌ API credentials NOT found")
        print()
        print("=" * 70)
        print("SETUP REQUIRED")
        print("=" * 70)
        print()
        print("Step 1: Create Polymarket Account")
        print("  → Go to: https://polymarket.com")
        print("  → Sign up with email or wallet")
        print("  → Complete KYC verification")
        print()
        print("Step 2: Connect Wallet")
        print("  → Recommended: MetaMask or Rainbow")
        print("  → Fund with USDC on Polygon network")
        print("  → Minimum: $50-100 for testing")
        print()
        print("Step 3: Get API Credentials")
        print("  → Go to: https://polymarket.com/account")
        print("  → Navigate to 'API Keys' section")
        print("  → Generate new API key")
        print("  → Copy API Key and Secret")
        print()
        print("Step 4: Export Credentials")
        print("  export POLYMARKET_API_KEY='your_api_key_here'")
        print("  export POLYMARKET_API_SECRET='your_secret_here'")
        print("  export POLYMARKET_PRIVATE_KEY='your_wallet_private_key'")
        print()
        print("Step 5: Fund Your Account")
        print("  → Deposit USDC to your Polymarket wallet")
        print("  → Start with $50-100 for testing")
        print("  → Use Polygon network for lowest fees")
        print()
        return False
        
    print()
    print("=" * 70)
    print("FUNDING OPTIONS")
    print("=" * 70)
    print()
    print("Option 1: Direct USDC Deposit")
    print("  → Send USDC to your Polymarket wallet address")
    print("  → Network: Polygon (recommended) or Ethereum")
    print("  → Min deposit: $5")
    print()
    print("Option 2: Buy with Card")
    print("  → Use MoonPay or Transak on Polymarket")
    print("  → Higher fees (~3-5%)")
    print("  → Instant")
    print()
    print("Option 3: Transfer from Exchange")
    print("  → Buy USDC on Coinbase, Binance, etc.")
    print("  → Withdraw to your wallet")
    print("  → Then deposit to Polymarket")
    print()
    print("=" * 70)
    print("RECOMMENDED SETUP")
    print("=" * 70)
    print()
    print("For XRP 5-Minute Trading:")
    print("  • Starting capital: $100-500")
    print("  • Position size: $5-20 per trade")
    print("  • Max 3 concurrent positions")
    print("  • Expected: 10-30 trades/day")
    print("  • Fees: 2% per trade")
    print()
    print("Risk Management:")
    print("  • Stop if balance drops 20%")
    print("  • Daily loss limit: $50")
    print("  • Take profit at +50%")
    print()
    
    return True

def generate_trading_script():
    """Generate the real trading script"""
    script = '''#!/usr/bin/env python3
"""
Polymarket XRP Real Trading Bot
Greenhead Labs - Woody Pintail

REQUIRES:
  export POLYMARKET_API_KEY='your_key'
  export POLYMARKET_API_SECRET='your_secret'
  export POLYMARKET_PRIVATE_KEY='your_wallet_pk'
"""

import os
import json
import time
import logging
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xrp_real_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('polymarket_real')

class PolymarketAPI:
    """Real Polymarket API interface"""
    
    BASE_URL = "https://clob.polymarket.com"
    
    def __init__(self):
        self.api_key = os.getenv('POLYMARKET_API_KEY')
        self.api_secret = os.getenv('POLYMARKET_API_SECRET')
        self.private_key = os.getenv('POLYMARKET_PRIVATE_KEY')
        
        if not all([self.api_key, self.api_secret, self.private_key]):
            raise ValueError("Missing API credentials. Set env vars.")
            
        self.balance = 0.0
        
    def get_balance(self) -> float:
        """Get USDC balance"""
        try:
            req = urllib.request.Request(
                f"{self.BASE_URL}/balance",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                self.balance = float(data.get('balance', 0))
                return self.balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return 0.0
            
    def place_order(self, market_id: str, side: str, size: float, price: float) -> Dict:
        """Place an order"""
        try:
            payload = {
                'market_id': market_id,
                'side': side,  # 'buy' or 'sell'
                'size': size,
                'price': price,
                'type': 'limit'
            }
            
            req = urllib.request.Request(
                f"{self.BASE_URL}/orders",
                data=json.dumps(payload).encode(),
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {'error': str(e)}
            
    def get_market(self, market_id: str) -> Dict:
        """Get market data"""
        try:
            req = urllib.request.Request(
                f"{self.BASE_URL}/markets/{market_id}",
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.error(f"Error fetching market: {e}")
            return {}


class RealXRPTrader:
    """Real trading implementation"""
    
    def __init__(self):
        self.api = PolymarketAPI()
        self.market_id = "xrp-updown-5m-1773199800"  # Current 5-min market
        
    def run(self):
        """Main trading loop"""
        logger.info("=" * 70)
        logger.info("REAL POLYMARKET TRADING")
        logger.info("=" * 70)
        
        # Check balance
        balance = self.api.get_balance()
        logger.info(f"USDC Balance: ${balance:.2f}")
        
        if balance < 10.0:
            logger.error("Insufficient balance. Need at least $10 USDC.")
            return
            
        # Get market data
        market = self.api.get_market(self.market_id)
        logger.info(f"Market: {market.get('question', 'Unknown')}")
        
        logger.info("Ready to trade!")
        logger.info("WARNING: This will use REAL MONEY")
        

if __name__ == "__main__":
    try:
        trader = RealXRPTrader()
        trader.run()
    except ValueError as e:
        print(f"Setup Error: {e}")
        print("Run: python3 polymarket_setup.py")
'''
    
    with open('polymarket_real_trader.py', 'w') as f:
        f.write(script)
        
    print("Generated: polymarket_real_trader.py")

if __name__ == "__main__":
    check_prerequisites()
    generate_trading_script()
