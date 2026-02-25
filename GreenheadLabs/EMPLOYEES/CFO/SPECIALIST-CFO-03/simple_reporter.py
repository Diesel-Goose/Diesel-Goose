#!/usr/bin/env python3
"""
Chris Dunn — 30-Minute Reporter Daemon
Reads actual trade data from logs and sends formatted reports.
"""

import time
import json
import requests
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Telegram config
BOT_TOKEN = "8350022484:AAE93G6trBzE6fhahPtdCKWZke6ZubGTaGQ"
GROUP_CHAT_ID = "-1003885436287"

# Paths
LOG_DIR = Path(__file__).parent / "logs"
TRADES_LOG = LOG_DIR / "trades.log"
CONTINUOUS_LOG = LOG_DIR / "continuous_trades.log"
PRODUCTION_LOG = LOG_DIR / "production.log"

# Session tracking
SESSION_START_FILE = LOG_DIR / ".session_start"


def get_session_start():
    """Get or set session start time."""
    if SESSION_START_FILE.exists():
        try:
            with open(SESSION_START_FILE, 'r') as f:
                return datetime.fromisoformat(f.read().strip())
        except:
            pass
    # New session
    now = datetime.now()
    SESSION_START_FILE.write_text(now.isoformat())
    return now


def get_xrp_price():
    """Fetch current XRP price from CoinGecko API."""
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
    return 1.35  # Fallback


def analyze_trades():
    """Read and analyze trade data from all logs."""
    all_trades = []
    
    # Read main trades log
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
    
    # Count continuous trades (additional activity)
    continuous_count = 0
    if CONTINUOUS_LOG.exists():
        with open(CONTINUOUS_LOG, 'r') as f:
            continuous_count = sum(1 for line in f if '|' in line)
    
    if not all_trades and continuous_count == 0:
        return None
    
    # Calculate stats
    total_trades = len(all_trades)
    winning_trades = len([t for t in all_trades if t.get('pnl', 0) > 0])
    losing_trades = len([t for t in all_trades if t.get('pnl', 0) < 0])
    total_pnl = sum(t.get('pnl', 0) for t in all_trades)
    total_volume = sum(t.get('amount', 0) * t.get('price', 0) for t in all_trades)
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Get strategy from latest trade
    latest_strategy = all_trades[-1].get('strategy', 'market_maker') if all_trades else 'market_maker'
    
    # Get XRP price
    xrp_price = get_xrp_price()
    
    # Calculate runtime
    session_start = get_session_start()
    runtime = datetime.now() - session_start
    runtime_minutes = runtime.total_seconds() / 60
    
    return {
        'total_trades': total_trades,
        'continuous_trades': continuous_count,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'total_pnl_xrp': total_pnl,
        'total_pnl_usd': total_pnl * xrp_price,
        'total_volume_usd': total_volume,
        'latest_strategy': latest_strategy,
        'xrp_price': xrp_price,
        'runtime_minutes': runtime_minutes
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


def get_status_indicator(pnl):
    """Get status based on P&L."""
    if pnl > 0:
        return "🔥 Profitable"
    elif pnl < 0:
        return "📉 Recovering"
    else:
        return "🔥 Building"


def format_runtime(minutes):
    """Format runtime nicely."""
    if minutes < 60:
        return f"{minutes:.0f} minutes"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f} hours"
    days = hours / 24
    return f"{days:.1f} days"


def send_startup_report():
    """Send the v2.0 PRODUCTION startup message."""
    # Try to get wallet info from config
    wallet_addr = "rNWvQrBF4T..."  # Default
    config_path = Path(__file__).parent / "config" / "production.yaml"
    if config_path.exists():
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                addr = config.get('wallet', {}).get('address', '')
                if addr:
                    wallet_addr = addr[:13] + "..."
        except:
            pass
    
    message = f"""🚀 <b>Chris Dunn v2.0 PRODUCTION</b>

💼 Wallet: {wallet_addr}
📈 Pair: XRP/RLUSD
⏰ Started: {datetime.now().strftime('%H:%M:%S')}
🎯 Strategy: Market Maker
🔒 Profits → Vault"""
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(
            url,
            json={'chat_id': GROUP_CHAT_ID, 'text': message, 'parse_mode': 'HTML'},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Startup message failed: {e}")
        return False


def send_session_summary():
    """Send session summary with real data."""
    stats = analyze_trades()
    
    if not stats:
        # No data yet - send building status
        session_start = get_session_start()
        runtime = datetime.now() - session_start
        runtime_minutes = runtime.total_seconds() / 60
        
        message = f"""🦆 <b>Chris Dunn Session Summary</b>

⏱ Runtime: {format_runtime(runtime_minutes)}
📊 Trades: 0
💰 P&L: 0.0000 XRP
🔥 Status: Building"""
    else:
        strategy_emoji = get_strategy_emoji(stats['latest_strategy'])
        status = get_status_indicator(stats['total_pnl_xrp'])
        
        message = f"""🦆 <b>Chris Dunn Session Summary</b>

⏱ Runtime: {format_runtime(stats['runtime_minutes'])}
📊 Trades: {stats['total_trades']}
💰 P&L: {stats['total_pnl_xrp']:.4f} XRP (${stats['total_pnl_usd']:.2f})
{status}

{strategy_emoji} Strategy: {stats['latest_strategy'].replace('_', ' ').title()}
📈 Win Rate: {stats['win_rate']:.1f}% ({stats['winning_trades']}W/{stats['losing_trades']}L)
💵 Volume: ${stats['total_volume_usd']:.0f}
🪙 XRP @ ${stats['xrp_price']:.2f}

⏰ Updated: {datetime.now().strftime('%H:%M')} CST | 30-min Report"""
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(
            url,
            json={'chat_id': GROUP_CHAT_ID, 'text': message, 'parse_mode': 'HTML'},
            timeout=10
        )
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Session summary sent")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {e}")
        return False


def main():
    """Send reports every 30 minutes with real data."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Chris Dunn 30-Minute Reporter Started")
    print(f"Session start: {get_session_start().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Send initial startup message
    send_startup_report()
    time.sleep(2)
    
    # Send first summary
    send_session_summary()
    
    cycle = 0
    while True:
        # Sleep for 30 minutes
        time.sleep(1800)  # 30 minutes = 1800 seconds
        cycle += 1
        
        # Send updated summary
        send_session_summary()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Cycle {cycle} complete (30-min interval)")


if __name__ == "__main__":
    main()
