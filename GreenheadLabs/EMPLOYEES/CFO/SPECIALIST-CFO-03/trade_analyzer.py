#!/usr/bin/env python3
"""
Chris Dunn — Live Trade Analyzer
Reads real trades from audit.log and calculates actual performance
"""

import json
import re
from datetime import datetime
from pathlib import Path

def analyze_trades(log_file='sandbox/audit.log'):
    """Analyze real trades from audit log."""
    trades = []
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if 'TRADE' in line and 'filled' in line:
                    try:
                        # Parse trade from log line
                        match = re.search(r"'signal': '(\w+)'.*'amount': ([\d.]+).*'price': ([\d.]+)", line)
                        if match:
                            signal = match.group(1)
                            amount = float(match.group(2))
                            price = float(match.group(3))
                            
                            trades.append({
                                'signal': signal,
                                'amount': amount,
                                'price': price,
                                'value': amount * price
                            })
                    except:
                        pass
    except FileNotFoundError:
        return None
    
    if not trades:
        return None
    
    # Calculate real metrics
    total_trades = len(trades)
    buys = [t for t in trades if t['signal'] == 'buy']
    sells = [t for t in trades if t['signal'] == 'sell']
    
    # Calculate P&L (simplified market maker logic)
    # Profit = sum of sells - sum of buys
    total_bought = sum(t['value'] for t in buys)
    total_sold = sum(t['value'] for t in sells)
    
    # For market maker, profit is the spread captured
    pnl_usd = total_sold - total_bought
    
    # Calculate win rate (trades that added value)
    profitable_trades = sum(1 for t in trades if t['signal'] == 'sell' and t['price'] > 0.50)
    win_rate = (profitable_trades / total_sold * 100) if sells else 0
    
    # Estimate XRP P&L (assuming average position)
    avg_position = sum(t['amount'] for t in trades) / len(trades) if trades else 0
    pnl_pct = (pnl_usd / total_bought * 100) if total_bought else 0
    pnl_xrp = pnl_usd / 0.50  # Assuming $0.50/XRP
    
    total_volume = sum(t['value'] for t in trades)
    
    return {
        'total_trades': total_trades,
        'buys': len(buys),
        'sells': len(sells),
        'pnl_usd': pnl_usd,
        'pnl_xrp': pnl_xrp,
        'pnl_pct': pnl_pct,
        'win_rate': win_rate,
        'total_volume': total_volume
    }

if __name__ == "__main__":
    stats = analyze_trades()
    if stats:
        print(json.dumps(stats, indent=2))
    else:
        print("No trades found")
