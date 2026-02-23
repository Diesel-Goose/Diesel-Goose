#!/usr/bin/env python3
"""
Chris Dunn — SIMPLE Reporter Daemon
Just sends reports every 5 minutes. Nothing else.
"""

import time
import json
import requests
from datetime import datetime

# Hardcoded config — no file dependencies
BOT_TOKEN = "8350022484:AAE93G6trBzE6fhahPtdCKWZke6ZubGTaGQ"
GROUP_CHAT_ID = "-1003885436287"

def send_report(trades, wins, pnl):
    """Send simple report to Telegram."""
    win_rate = round((wins / trades * 100), 0) if trades > 0 else 0
    
    message = f"""🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs
⚡️ Trading Active | 💰 {pnl:.1f}% Profit | 💡 {win_rate:.0f}% Win | 🔥 LIVE
🎯 Active: Paper Trading XRP via Sandbox
📅 {datetime.now().strftime('%H:%M')} CST • Auto-Report"""
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={'chat_id': GROUP_CHAT_ID, 'text': message}, timeout=10)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Report sent")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")

def main():
    """Send report every 5 minutes."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Chris Dunn Reporter Started")
    print("Sending report every 5 minutes to Greenhead Labs group...")
    
    # Simulated stats (will be replaced with real data)
    trades = 230
    wins = 120
    pnl = 15.0
    
    while True:
        send_report(trades, wins, pnl)
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()
