#!/usr/bin/env bash
# Diesel-Goose Heartbeat - Simple Cron Version
# No persistent daemon - just sends heartbeat and exits

WORKSPACE="/Users/dieselgoose/.openclaw/workspace"
HEARTBEAT_PY="$WORKSPACE/BRAIN/heartbeat_generator.py"
LOG_FILE="/Users/dieselgoose/.openclaw/logs/heartbeat_cron.log"

# Send heartbeat using Python generator
cd "$WORKSPACE"
if /opt/homebrew/bin/python3 "$HEARTBEAT_PY" 100 96 99 "MAX" "Auto-heartbeat cycle" >> "$LOG_FILE" 2>&1; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ✅ Heartbeat sent" >> "$LOG_FILE"
    
    # Sync to GitHub
    git add HEARTBEAT.md
    git commit -m "Heartbeat $(date -u +%Y%m%d_%H%M) | Auto" --quiet
    git push origin main --quiet
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ✅ Synced to GitHub" >> "$LOG_FILE"
else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ❌ Heartbeat failed" >> "$LOG_FILE"
fi
