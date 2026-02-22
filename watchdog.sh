#!/usr/bin/env bash
# Diesel Goose Watchdog — Autonomous Sync & Monitor
# Runs every 10 minutes via cron
# Watches all Greenhead Labs systems and keeps repos in sync

set -euo pipefail

WORKSPACE="/Users/dieselgoose/.openclaw/workspace"
BACKUP="/Users/dieselgoose/Honk-Node/Hunters/Diesel-Goose"
LOG_DIR="/Users/dieselgoose/.openclaw/logs"
ALERT_TOKEN="8350022484:AAE93G6trBzE6fhahPtdCKWZke6ZubGTaGQ"
ALERT_CHAT="7491205261"

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1" >> "$LOG_DIR/watchdog.log"
}

alert() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot${ALERT_TOKEN}/sendMessage" \
        -d "chat_id=${ALERT_CHAT}" \
        -d "text=🛡️ Diesel Goose Watchdog\n\n${message}" \
        > /dev/null 2>&1 || true
}

# ==================== REPO SYNC ====================
sync_repos() {
    log "Starting repo sync cycle"
    
    cd "$WORKSPACE"
    
    # Check if there are uncommitted changes
    if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
        log "Uncommitted changes detected — auto-committing"
        git add -A
        git commit -m "Auto-sync: $(date -u +%Y%m%d_%H%M%S)" || true
    fi
    
    # Pull from GitHub (get any remote changes)
    if git pull origin main --quiet 2>/dev/null; then
        log "GitHub pull successful"
    else
        log "GitHub pull failed or no changes"
    fi
    
    # Push to GitHub (send local changes)
    if git push origin main --quiet 2>/dev/null; then
        log "GitHub push successful"
    else
        log "GitHub push failed or nothing to push"
    fi
    
    # Sync backup location
    if [[ -d "$BACKUP" ]]; then
        cd "$BACKUP"
        if git pull origin main --quiet 2>/dev/null; then
            log "Backup location synced"
        else
            log "Backup sync failed"
            alert "⚠️ Backup sync failed — Check Hunters/Diesel-Goose"
        fi
    fi
    
    log "Repo sync complete"
}

# ==================== SYSTEM HEALTH ====================
check_health() {
    log "Running health checks"
    
    # Check disk space
    local disk_usage=$(df -h "$WORKSPACE" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        alert "🚨 DISK CRITICAL: ${disk_usage}% full"
    elif [[ $disk_usage -gt 80 ]]; then
        log "WARNING: Disk ${disk_usage}% full"
    fi
    
    # Check if Chris Dunn is running (if should be)
    if pgrep -f "chris_dunn.py" > /dev/null; then
        log "Chris Dunn is running"
    else
        log "Chris Dunn not running (may be expected)"
    fi
    
    # Check heartbeat monitor
    if screen -list | grep -q "dieselgoose"; then
        log "Heartbeat monitor active"
    else
        log "WARNING: Heartbeat monitor down"
        # Auto-restart
        cd "$WORKSPACE"
        ./persistent_heartbeat.sh start 2>/dev/null || true
        alert "⚠️ Heartbeat monitor restarted"
    fi
}

# ==================== SECURITY SCAN ====================
security_scan() {
    log "Running security scan"
    
    # Check for secrets in code (exclude docs, venv, and audit files)
    local secrets_found=$(grep -r "ghp_[a-zA-Z0-9]\{36\}\|sk-[a-zA-Z0-9]\{48\}" \
        --include="*.py" --include="*.yaml" "$WORKSPACE" 2>/dev/null | \
        grep -v ".venv\|__pycache__\|SECURITY_AUDIT\|example\|\.md" | wc -l)
    
    if [[ $secrets_found -gt 0 ]]; then
        alert "🚨 SECURITY ALERT: $secrets_found potential secrets found in code!"
        log "CRITICAL: Secrets detected in repository"
    else
        log "Security scan clean"
    fi
}

# ==================== MAIN ====================
main() {
    log "=== Watchdog Cycle Started ==="
    
    sync_repos
    check_health
    security_scan
    
    log "=== Watchdog Cycle Complete ==="
}

main "$@"
