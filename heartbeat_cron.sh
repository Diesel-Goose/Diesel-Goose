#!/usr/bin/env bash
# Diesel-Goose Heartbeat - Simple Cron Version
# No persistent daemon - just sends heartbeat and exits

HEARTBEAT_PY="/Users/dieselgoose/Honk-Node/Duck-Pond/System/telegram_heartbeat.py"
LOG_FILE="/Users/dieselgoose/.openclaw/logs/heartbeat_cron.log"

# Send heartbeat
if /opt/homebrew/bin/python3 "$HEARTBEAT_PY" >> "$LOG_FILE" 2>&1; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ✅ Heartbeat sent" >> "$LOG_FILE"
    
    # Sync to GitHub
    cd /Users/dieselgoose/.openclaw/workspace
    git add HEARTBEAT.md
    git commit -m "Heartbeat $(date -u +%Y%m%d_%H%M) | Auto" --quiet
    git push origin main --quiet
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ✅ Synced to GitHub" >> "$LOG_FILE"
else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ❌ Heartbeat failed" >> "$LOG_FILE"
fi
