#!/usr/bin/env python3
"""
Chris Dunn — Group Message Test
Quick test to verify bot can post to Greenhead Labs group.
"""

import os
import asyncio
import requests
from datetime import datetime

# Configuration
BOT_TOKEN = "8350022484:AAE93G6trBzE6fhahPtdCKWZke6ZubGTaGQ"
GROUP_CHAT_ID = "-1003885436287"

def test_bot_connection():
    """Test if bot is working."""
    print("🦆 Testing Chris Dunn Bot Connection...")
    print("=" * 50)
    
    # Test 1: Get bot info
    print("\n1. Testing bot authentication...")
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getMe",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"   ✅ Bot connected!")
                print(f"   Name: {bot_info.get('first_name')}")
                print(f"   Username: @{bot_info.get('username')}")
            else:
                print(f"   ❌ Bot error: {data}")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test 2: Send message to group
    print("\n2. Testing group message...")
    try:
        now = datetime.utcnow().strftime('%H:%M:%S')
        
        message = f"""🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs
⚡️ 0 Trades/Min | 💰 0.0% Profit | 💡 0% Win | 🔥 TEST
🎯 Active: Connection Test — Can you see me?
📅 {now} UTC • Test Message"""
        
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                'chat_id': GROUP_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"   ✅ Message sent to group!")
                print(f"   Message ID: {data['result'].get('message_id')}")
                return True
            else:
                print(f"   ❌ Telegram error: {data}")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Send failed: {e}")
        return False

if __name__ == "__main__":
    success = test_bot_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Chris Dunn can message the group!")
        print("\nNext steps:")
        print("  1. Check Greenhead Labs group for the test message")
        print("  2. If message appears, Chris Dunn is ready")
        print("  3. Start trading: python3 sandbox_runner.py")
    else:
        print("❌ Test failed — check errors above")
        print("\nPossible issues:")
        print("  • Bot not added to group")
        print("  • Wrong group chat ID")
        print("  • Bot doesn't have message permissions")
        print("  • Token incorrect")
