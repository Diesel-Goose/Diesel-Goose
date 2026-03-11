#!/bin/bash
# Polymarket XRP Trading Bot Launcher
# Greenhead Labs - Woody Pintail

cd "$(dirname "$0")"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Check for required packages
echo "Checking dependencies..."
pip3 list | grep -q aiohttp || pip3 install aiohttp websockets

echo "Starting Polymarket XRP Trading Bot..."
echo "Logs: xrp_predictions.jsonl"
echo "Trades: xrp_trades.jsonl"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the trader
python3 polymarket_xrp_trader.py
