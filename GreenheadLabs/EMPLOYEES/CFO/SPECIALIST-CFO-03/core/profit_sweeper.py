"""
Profit Sweeper
Automatically moves excess profits to secure vault
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict


class ProfitSweeper:
    """
    Watches trading wallet and sweeps excess to vault.
    Keeps minimum working capital, sends profits to cold storage.
    """
    
    def __init__(self, config, xrpl_client, telegram_alerts=None):
        self.config = config.get('sweep', {})
        self.logger = logging.getLogger('ProfitSweeper')
        
        self.xrpl = xrpl_client
        self.telegram = telegram_alerts
        
        # Thresholds
        self.enabled = self.config.get('enabled', True)
        self.threshold_xrp = self.config.get('threshold_xrp', 40)
        self.threshold_rlusd = self.config.get('threshold_rlusd', 100)
        self.interval_minutes = self.config.get('interval_minutes', 60)
        
        # Vault address
        self.vault_address = config.get('wallet', {}).get('vault_address', '')
        
        # Tracking
        self.last_sweep = None
        self.total_swept_xrp = 0.0
        self.total_swept_rlusd = 0.0
        
    async def check_and_sweep(self) -> Dict:
        """
        Check balance and sweep excess to vault.
        
        Returns:
            Dict with sweep results
        """
        if not self.enabled or not self.vault_address:
            return {'swept': False, 'reason': 'Disabled or no vault'}
        
        results = {
            'swept': False,
            'xrp_swept': 0.0,
            'rlusd_swept': 0.0,
            'tx_hashes': []
        }
        
        try:
            # Get current balance
            balance = await self.xrpl.get_balance()
            xrp = balance['xrp']
            rlusd = balance['rlusd']
            
            self.logger.info(f"Checking sweep: {xrp:.2f} XRP, {rlusd:.2f} RLUSD | Vault: {self.vault_address[:10]}...")
            
            # Sweep XRP excess
            if xrp > self.threshold_xrp:
                excess = xrp - self.threshold_xrp
                # Reserve 10 XRP for fees
                sweep_amount = excess - 10
                
                if sweep_amount > 1:  # Only sweep if > 1 XRP
                    self.logger.info(f"Sweeping {sweep_amount:.2f} XRP to vault")
                    
                    result = await self.xrpl.send_payment(
                        to_address=self.vault_address,
                        amount=sweep_amount,
                        currency='XRP'
                    )
                    
                    if result.get('success'):
                        results['xrp_swept'] = sweep_amount
                        results['tx_hashes'].append(result['tx_hash'])
                        self.total_swept_xrp += sweep_amount
                        results['swept'] = True
                        
                        msg = f"🧹 Profit Sweep: {sweep_amount:.2f} XRP → Vault"
                        self.logger.info(msg)
                        
                        if self.telegram:
                            await self.telegram.send_alert(msg)
                    else:
                        self.logger.error(f"XRP sweep failed: {result.get('error')}")
            
            # Sweep RLUSD excess
            if rlusd > self.threshold_rlusd:
                excess = rlusd - self.threshold_rlusd
                
                if excess > 1:  # Only sweep if > 1 RLUSD
                    self.logger.info(f"Sweeping {excess:.2f} RLUSD to vault")
                    
                    result = await self.xrpl.send_payment(
                        to_address=self.vault_address,
                        amount=excess,
                        currency='RLUSD'
                    )
                    
                    if result.get('success'):
                        results['rlusd_swept'] = excess
                        results['tx_hashes'].append(result['tx_hash'])
                        self.total_swept_rlusd += excess
                        results['swept'] = True
                        
                        msg = f"🧹 Profit Sweep: {excess:.2f} RLUSD → Vault"
                        self.logger.info(msg)
                        
                        if self.telegram:
                            await self.telegram.send_alert(msg)
                    else:
                        self.logger.error(f"RLUSD sweep failed: {result.get('error')}")
            
            if results['swept']:
                self.last_sweep = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Sweep error: {e}", exc_info=True)
        
        return results
    
    async def run_sweep_loop(self):
        """Background task to sweep every interval."""
        while True:
            try:
                await self.check_and_sweep()
                await asyncio.sleep(self.interval_minutes * 60)
            except Exception as e:
                self.logger.error(f"Sweep loop error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute on error
    
    def get_status(self) -> Dict:
        """Get sweeper status."""
        return {
            'enabled': self.enabled,
            'vault': self.vault_address[:15] + '...' if self.vault_address else 'Not set',
            'last_sweep': self.last_sweep.isoformat() if self.last_sweep else None,
            'total_swept_xrp': self.total_swept_xrp,
            'total_swept_rlusd': self.total_swept_rlusd,
            'threshold_xrp': self.threshold_xrp,
            'threshold_rlusd': self.threshold_rlusd
        }
