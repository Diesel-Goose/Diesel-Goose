# Chris Dunn v2.0 - Production Quickstart

XRP/RLUSD Market Maker with Auto Profit Sweep

## Prerequisites

- Python 3.10+
- Funded XRPL wallet with:
  - 30+ XRP for reserves
  - RLUSD trust line established
  - RLUSD balance for trading
- Vault wallet address (Xaman secured)

## Install Dependencies

```bash
cd /Users/dieselgoose/.openclaw/workspace/GreenheadLabs/EMPLOYEES/CFO/SPECIALIST-CFO-03
pip install xrpl-py aiohttp pyyaml
```

## Configure Wallet

```bash
python setup_production.py
```

This will:
1. Convert your 12-word phrase to wallet credentials
2. Collect your vault address for profit sweeps
3. Generate secure config at `config/production.yaml`

## Start Trading

```bash
python production_runner.py
```

## What Happens

1. ✅ Connects to XRPL mainnet
2. ✅ Checks balances (XRP + RLUSD)
3. ✅ Places market maker orders (bid/ask around mid price)
4. ✅ Sweeps excess profits to vault hourly
5. ✅ Sends Telegram alerts on every trade

## Monitoring

- **Logs**: `tail -f logs/production.log`
- **Telegram**: Real-time trade/profit alerts
- **Status**: Logs show open orders, inventory ratio, mid price

## Stopping

Press `Ctrl+C` - bot will:
- Cancel open orders (best effort)
- Send session summary to Telegram
- Disconnect gracefully

## Files Created

```
├── config/
│   └── production.yaml          # Your wallet config (SECURE)
│   └── production.yaml.template # Template
├── core/
│   └── xrpl_production.py       # XRPL client with signing
│   └── profit_sweeper.py        # Auto profit sweep
├── strategies/
│   └── production_mm.py         # Market maker logic
├── utils/
│   └── telegram_alerts.py       # Telegram integration
├── production_runner.py         # Main entry point
├── setup_production.py          # Wallet setup helper
└── logs/
    └── production.log           # Runtime logs
```

## Conservative Defaults

Config starts conservative for safety:
- 25 XRP per order (small)
- 0.8% spread
- Max 2 orders each side
- Auto-sweep keeps 35 XRP, 50 RLUSD, sends rest to vault

Increase sizes after you're comfortable with the bot.

## Security

- Trading wallet: Limited funds only
- Vault wallet: Receives profits (your Xaman wallet)
- Config file: chmod 600 (owner read-only)
- Secret key: Never leaves your machine
