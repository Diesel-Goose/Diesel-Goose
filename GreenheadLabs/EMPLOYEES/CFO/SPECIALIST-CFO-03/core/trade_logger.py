"""
Trade Logger for Tax Records
Tracks all trades with cost basis, fees, and P&L for tax reporting
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import asyncio


class TradeLogger:
    """
    Records all trades for tax season reporting.
    
    Tracks:
    - Timestamp
    - Transaction hash
    - Side (buy/sell)
    - Amount (XRP)
    - Price (USD per XRP)
    - Value USD
    - Fees (XRP)
    - Realized P&L
    - Cost basis
    """
    
    def __init__(self, config: dict):
        self.config = config.get('trade_logging', {})
        self.logger = logging.getLogger('TradeLogger')
        
        self.enabled = self.config.get('enabled', True)
        self.log_file = Path(self.config.get('log_file', 'logs/trades.csv'))
        self.daily_summary = self.config.get('daily_summary', True)
        
        # Ensure directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cost basis tracking (FIFO)
        self.cost_basis_queue = []  # List of (amount, price) tuples for buys
        self.total_realized_pnl = 0.0
        self.total_fees = 0.0
        self.trade_count = 0
        
        # Initialize CSV with headers if new file
        self._init_csv()
        
    def _init_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.log_file.exists():
            headers = [
                'timestamp',
                'tx_hash',
                'side',
                'amount_xrp',
                'price_usd',
                'value_usd',
                'fee_xrp',
                'fee_usd',
                'realized_pnl',
                'cost_basis',
                'balance_xrp',
                'balance_usd',
                'notes'
            ]
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            self.logger.info(f"Created new trade log: {self.log_file}")
    
    async def log_trade(self, trade: dict, balance: dict):
        """
        Log a trade for tax records.
        
        Args:
            trade: Dict with 'tx_hash', 'side', 'amount', 'price'
            balance: Dict with 'xrp', 'rlusd' balances after trade
        """
        if not self.enabled:
            return
        
        try:
            timestamp = datetime.now().isoformat()
            tx_hash = trade.get('tx_hash', '')
            side = trade.get('side', '').upper()
            amount = float(trade.get('amount', 0))
            price = float(trade.get('price', 0))
            value_usd = amount * price
            
            # Estimate fee (typical XRPL transaction fee)
            fee_xrp = 0.000012  # 12 drops
            fee_usd = fee_xrp * price
            
            # Calculate realized P&L for sells
            realized_pnl = 0.0
            cost_basis = 0.0
            
            if side == 'SELL' and self.cost_basis_queue:
                # FIFO cost basis calculation
                remaining = amount
                total_cost = 0.0
                
                while remaining > 0 and self.cost_basis_queue:
                    cb_amount, cb_price = self.cost_basis_queue[0]
                    
                    if cb_amount <= remaining:
                        # Use entire cost basis lot
                        total_cost += cb_amount * cb_price
                        remaining -= cb_amount
                        self.cost_basis_queue.pop(0)
                    else:
                        # Use partial cost basis lot
                        total_cost += remaining * cb_price
                        self.cost_basis_queue[0] = (cb_amount - remaining, cb_price)
                        remaining = 0
                
                cost_basis = total_cost
                realized_pnl = value_usd - total_cost - fee_usd
                self.total_realized_pnl += realized_pnl
                
            elif side == 'BUY':
                # Add to cost basis queue
                self.cost_basis_queue.append((amount, price))
                cost_basis = amount * price
            
            self.total_fees += fee_usd
            self.trade_count += 1
            
            # Write to CSV
            row = [
                timestamp,
                tx_hash,
                side,
                f"{amount:.6f}",
                f"{price:.6f}",
                f"{value_usd:.6f}",
                f"{fee_xrp:.6f}",
                f"{fee_usd:.6f}",
                f"{realized_pnl:.6f}",
                f"{cost_basis:.6f}",
                f"{balance.get('xrp', 0):.6f}",
                f"{balance.get('rlusd', 0):.6f}",
                f"Trade #{self.trade_count}"
            ]
            
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            self.logger.info(
                f"Trade #{self.trade_count} logged: {side} {amount} XRP @ ${price:.4f} | "
                f"P&L: ${realized_pnl:.4f}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log trade: {e}")
    
    async def log_daily_summary(self, telegram=None):
        """Log daily summary of trading activity."""
        if not self.enabled or not self.daily_summary:
            return
        
        try:
            summary = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_trades': self.trade_count,
                'realized_pnl': self.total_realized_pnl,
                'total_fees': self.total_fees,
                'net_pnl': self.total_realized_pnl - self.total_fees
            }
            
            # Save summary to JSON
            summary_file = self.log_file.parent / f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            msg = (
                f"📊 Daily Trading Summary\n"
                f"Trades: {summary['total_trades']}\n"
                f"Realized P&L: ${summary['realized_pnl']:.2f}\n"
                f"Fees: ${summary['total_fees']:.4f}\n"
                f"Net P&L: ${summary['net_pnl']:.2f}"
            )
            
            self.logger.info(msg)
            
            if telegram:
                await telegram.send_alert(msg, priority='profit')
            
        except Exception as e:
            self.logger.error(f"Failed to log daily summary: {e}")
    
    def get_tax_report(self, year: int = 2026) -> dict:
        """Generate tax report for the year."""
        try:
            total_pnl = 0.0
            total_fees = 0.0
            trades = []
            
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        trade_year = int(row['timestamp'][:4])
                        if trade_year == year:
                            trades.append(row)
                            total_pnl += float(row.get('realized_pnl', 0))
                            total_fees += float(row.get('fee_usd', 0))
            
            return {
                'year': year,
                'total_trades': len(trades),
                'realized_pnl': total_pnl,
                'total_fees': total_fees,
                'net_profit': total_pnl - total_fees,
                'trades': trades
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate tax report: {e}")
            return {'error': str(e)}
