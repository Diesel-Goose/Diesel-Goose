#!/usr/bin/env bash
set -euo pipefail  # Fail fast on errors/unset vars
# auto_sync.sh - Silent git pull loop for local repo sync.
# No push, no Telegram, local logs only. Aligns with HEARTBEAT.md silence.
# Usage: ./auto_sync.sh [CADENCE_MINUTES] (default 30)
# Env: REPO_PATH (default .)

REPO_PATH="${REPO_PATH:-.}"
CADENCE="${1:-30}"
LOG_FILE="local_sync.log"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1" >> "$LOG_FILE"
}

while true; do
  log "Starting sync cycle"
  cd "$REPO_PATH" || { log "ERROR: Invalid REPO_PATH"; exit 1; }
  git pull origin main --quiet || log "Pull failed - check conflicts"
  log "Sync complete"
  sleep $((CADENCE * 60))
done
