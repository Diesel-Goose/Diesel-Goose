#!/usr/bin/env bash
set -euo pipefail
# sync.sh - One-shot silent git pull for repo sync.
# No push, no output clutter. For manual/cron use.
# Env: REPO_PATH (default .)

REPO_PATH="${REPO_PATH:-.}"
LOG_FILE="local_sync.log"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1" >> "$LOG_FILE"
}

log "Starting one-shot sync"
cd "$REPO_PATH" || { log "ERROR: Invalid REPO_PATH"; exit 1; }
git pull origin main --quiet || log "Pull failed - check conflicts"
log "One-shot sync complete"
