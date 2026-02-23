#!/usr/bin/env python3
"""
Chris Dunn — REAL-TIME Reporter Daemon
Reads actual trade data from logs and sends accurate reports.
"""

import time
import json
import requests
from datetime import datetime
from pathlib import Path
import os

# Telegram config
BOT_TOKEN = "8350022484:AAE93G6trBzE6fhahPtdCKWZke6ZubGTaGQ"
GROUP_CHAT_ID = "-1003885436287"

# Paths
LOG_DIR = Path(__file__).parent / "logs"
TRADES_LOG = LOG_DIR / "trades.log"
CONTINUOUS_LOG = LOG_DIR / "continuous_trades.log"


def get_xrp_price():
    """Fetch current XRP price from CoinGecko API (free, no key required)."""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd",
            timeout=5,
            headers={"Accept": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            price = data.get('ripple', {}).get('usd', 1.35)
            return float(price)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Price fetch failed: {e}")
    return 1.35  # Fallback price


def analyze_real_trades():
    """Read and analyze actual trade data from logs."""
    all_trades = []
    
    # Read main trades log (has real P&L data)
    if TRADES_LOG.exists():
        with open(TRADES_LOG, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 6:
                    try:
                        all_trades.append({
                            'timestamp': parts[0],
                            'strategy': parts[1],
                            'side': parts[2],
                            'amount': float(parts[3]),
                            'price': float(parts[4]),
                            'pnl': float(parts[5])
                        })
                    except (ValueError, IndexError):
                        continue
    
    # Read continuous trades log (for additional trade count only, no PNL)
    continuous_count = 0
    if CONTINUOUS_LOG.exists():
        with open(CONTINUOUS_LOG, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    try:
                        # Only count if not already in trades log (approximate)
                        continuous_count += 1
                    except (ValueError, IndexError):
                        continue
    
    if not all_trades:
        return None
    
    # Calculate stats
    total_trades = len(all_trades)
    winning_trades = len([t for t in all_trades if t.get('pnl', 0) > 0])
    losing_trades = len([t for t in all_trades if t.get('pnl', 0) < 0])
    total_pnl = sum(t.get('pnl', 0) for t in all_trades)
    total_volume = sum(t.get('amount', 0) * t.get('price', 0) for t in all_trades)
    
    # Use only trades with P&L for win rate calculation
    pnl_trades = [t for t in all_trades if t.get('pnl', 0) != 0 or 'pnl' in t]
    winning_trades = len([t for t in pnl_trades if t.get('pnl', 0) > 0])
    losing_trades = len([t for t in pnl_trades if t.get('pnl', 0) < 0])
    total_pnl = sum(t.get('pnl', 0) for t in pnl_trades)
    
    win_rate = (winning_trades / len(pnl_trades) * 100) if pnl_trades else 0
    
    # Get latest strategy
    latest_strategy = all_trades[-1].get('strategy', 'market_maker') if all_trades else 'market_maker'
    
    # Get live XRP price
    xrp_price = get_xrp_price()
    
    # Calculate trades per hour (including continuous)
    total_all_trades = len(all_trades) + continuous_count
    if len(all_trades) >= 2:
        try:
            first_time = datetime.fromisoformat(all_trades[0]['timestamp'].replace('Z', '+00:00'))
            last_time = datetime.fromisoformat(all_trades[-1]['timestamp'].replace('Z', '+00:00'))
            runtime_hours = (last_time - first_time).total_seconds() / 3600
            trades_per_hour = total_all_trades / runtime_hours if runtime_hours > 0 else 0
        except:
            trades_per_hour = total_all_trades / 24
    else:
        trades_per_hour = 0
    
    return {
        'total_trades': len(all_trades),
        'total_trades_with_continuous': total_all_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'total_pnl_xrp': total_pnl,
        'total_pnl_usd': total_pnl * xrp_price,
        'total_volume_usd': total_volume,
        'trades_per_hour': round(trades_per_hour, 1),
        'latest_strategy': latest_strategy,
        'last_trade_time': all_trades[-1]['timestamp'] if all_trades else None,
        'xrp_price': xrp_price,
        'continuous_trades': continuous_count
    }


def get_strategy_emoji(strategy):
    """Get emoji for strategy."""
    emojis = {
        'market_maker': '🏦',
        'arbitrage': '⚡',
        'momentum': '📈',
        'momentum_trader': '📈'
    }
    return emojis.get(strategy.lower(), '🎯')


def get_status_indicator(win_rate, pnl):
    """Get status based on performance."""
    if win_rate >= 70 and pnl > 0:
        return "🔥 MAX"
    elif win_rate >= 55 and pnl > 0:
        return "⚡️ HIGH"
    elif win_rate >= 40:
        return "💤 MOD"
    else:
        return "🚨 LOW"


def format_large_number(num):
    """Format large numbers with K/M suffix."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return f"{num:.1f}"


def send_report():
    """Send comprehensive trading report to Telegram."""
    stats = analyze_real_trades()
    
    if not stats:
        message = """🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs
⚠️ No trading data available
🎯 Status: Waiting for trades...
📅 {} CST • Auto-Report""".format(datetime.now().strftime('%H:%M'))
    else:
        strategy_emoji = get_strategy_emoji(stats['latest_strategy'])
        status = get_status_indicator(stats['win_rate'], stats['total_pnl_xrp'])
        
        message = f"""🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs
{strategy_emoji} Strategy: {stats['latest_strategy'].replace('_', ' ').title()}

📊 SESSION STATS
├─ Total Trades: {stats['total_trades']}
├─ Win Rate: {stats['win_rate']:.1f}% ({stats['winning_trades']}W/{stats['losing_trades']}L)
└─ Trade Rate: {stats['trades_per_hour']}/hr

💰 PROFIT & LOSS (XRP @ ${stats['xrp_price']:.2f})
├─ XRP Profit: {stats['total_pnl_xrp']:+.2f} XRP
├─ USD Value: ${stats['total_pnl_usd']:+.2f}
└─ Total Volume: ${format_large_number(stats['total_volume_usd'])}

{status} | 🎯 Paper Trading via Sandbox
📅 {datetime.now().strftime('%H:%M')} CST • Auto-Report"""
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(
            url,
            json={'chat_id': GROUP_CHAT_ID, 'text': message, 'parse_mode': 'HTML'},
            timeout=10
        )
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Report sent with real data")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {e}")
        return False


def main():
    """Send real trade reports every 5 minutes."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Chris Dunn REAL-TIME Reporter Started")
    print("Reading actual trade data from logs...")
    
    # Send initial report
    send_report()
    
    while True:
        time.sleep(300)  # 5 minutes
        send_report()


if __name__ == "__main__":
    main()
