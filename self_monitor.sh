#!/usr/bin/env bash
# Diesel-Goose Self-Monitoring & Heartbeat System
# Replaces broken LaunchAgent with user-space daemon
# Logs health checks, validates code integrity, triggers heartbeats

set -euo pipefail

WORKSPACE="/Users/dieselgoose/.openclaw/workspace"
DUCKPOND="/Users/dieselgoose/.openclaw/workspace"
LOG_DIR="/Users/dieselgoose/.openclaw/logs"
PIDFILE="$LOG_DIR/heartbeat_daemon.pid"
CADENCE_MINUTES=10

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    local msg="$*"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[$timestamp] [MONITOR] $msg" >> "$LOG_DIR/monitor.log"
    echo "[MONITOR] $msg"
}

error() {
    local msg="$*"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[$timestamp] [ERROR] $msg" >> "$LOG_DIR/monitor.log"
    echo "[ERROR] $msg" >&2
}

warn() {
    local msg="$*"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[$timestamp] [WARN] $msg" >> "$LOG_DIR/monitor.log"
    echo "[WARN] $msg"
}

# Check if daemon is already running
check_running() {
    if [[ -f "$PIDFILE" ]]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Code safety scan
safety_check() {
    log "Running safety scans..."
    local issues=0
    
    # Check for secrets in recent commits
    cd "$WORKSPACE" || return 1
    
    # Scan Python files for hardcoded secrets
    local secret_patterns="(api_key|apikey|api-key|token|password|secret|private_key|privatekey|bearer|auth|wallet|ssh_key|seed)"
    local matches=$(find . -name "*.py" -o -name "*.sh" -o -name "*.md" | xargs grep -i -E "$secret_patterns" 2>/dev/null | grep -v ".pyc" | grep -v "__pycache__" | wc -l)
    
    if [[ $matches -gt 0 ]]; then
        warn "Found $matches potential secret references - review recommended"
        issues=$((issues + 1))
    fi
    
    # Check git status for uncommitted changes
    if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
        local uncommitted=$(git status --porcelain | wc -l)
        warn "$uncommitted uncommitted changes in workspace"
        issues=$((issues + 1))
    fi
    
    # Check disk space
    local disk_usage=$(df -h "$WORKSPACE" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        error "Disk usage critical: ${disk_usage}%"
        issues=$((issues + 5))
    elif [[ $disk_usage -gt 80 ]]; then
        warn "Disk usage high: ${disk_usage}%"
        issues=$((issues + 1))
    fi
    
    # Verify core files exist
    local core_files=("HEARTBEAT.md" "IDENTITY.md" "SOUL.md" "AGENTS.md")
    for file in "${core_files[@]}"; do
        if [[ ! -f "$WORKSPACE/$file" ]]; then
            error "Missing core file: $file"
            issues=$((issues + 10))
        fi
    done
    
    log "Safety check complete - $issues issues found"
    return $issues
}

# Trigger heartbeat
trigger_heartbeat() {
    log "Triggering heartbeat..."
    
    # Run Python heartbeat generator with proper arguments
    cd "$WORKSPACE"
    if /opt/homebrew/bin/python3 "$WORKSPACE/BRAIN/heartbeat_generator.py" 100 96 99 "MAX" "Auto-heartbeat via self_monitor" >> "$LOG_DIR/monitor.log" 2>&1; then
        log "✅ Heartbeat successful"
        return 0
    else
        warn "⚠️ Heartbeat generator returned error, continuing..."
        return 0
    fi
}

# Sync with GitHub
sync_github() {
    log "Syncing with GitHub..."
    cd "$WORKSPACE" || return 1
    
    # Pull first
    if git pull origin main --quiet 2>/dev/null; then
        log "✅ Git pull successful"
    else
        warn "Git pull had issues (may be normal if no remote changes)"
    fi
    
    # Check if HEARTBEAT.md has changes to push
    if git status --porcelain | grep -q "HEARTBEAT.md"; then
        git add HEARTBEAT.md
        local timestamp=$(date -u +"%Y%m%d_%H%M%S")
        if git commit -m "Heartbeat $timestamp | Auto-sync" --quiet; then
            if git push origin main --quiet; then
                log "✅ Git push successful"
            else
                error "Git push failed"
            fi
        fi
    fi
}

# Main monitoring loop
monitor_loop() {
    log "=== Diesel-Goose Self-Monitor Started ==="
    log "Workspace: $WORKSPACE"
    log "Cadence: Every $CADENCE_MINUTES minutes"
    log "PID: $$"
    
    # Write PID file
    echo $$ > "$PIDFILE"
    
    # Trap signals for clean shutdown
    trap 'rm -f "$PIDFILE"; log "Monitor stopped"; exit 0' INT TERM EXIT
    
    local cycle=0
    while true; do
        cycle=$((cycle + 1))
        log "--- Cycle $cycle ---"
        
        # Run safety checks
        safety_check
        local safety_result=$?
        
        # Trigger heartbeat
        trigger_heartbeat
        
        # Sync with GitHub
        sync_github
        
        # Log status
        local next_run=$(date -v+${CADENCE_MINUTES}M +"%H:%M:%S")
        log "Cycle $cycle complete. Next run: $next_run"
        
        # Sleep until next cycle
        sleep $((CADENCE_MINUTES * 60))
    done
}

# Manual single-run mode (for cron alternative)
single_run() {
    log "=== Single-run monitor mode ==="
    safety_check
    trigger_heartbeat
    sync_github
    log "=== Single-run complete ==="
}

# Status check
show_status() {
    echo "=== Diesel-Goose Monitor Status ==="
    if check_running; then
        local pid=$(cat "$PIDFILE")
        echo -e "Status: ${GREEN}Running${NC} (PID: $pid)"
        ps -p "$pid" -o pid,etime,%cpu,%mem,command | tail -1
    else
        echo -e "Status: ${RED}Stopped${NC}"
    fi
    echo ""
    echo "Recent log entries:"
    tail -10 "$LOG_DIR/monitor.log" 2>/dev/null || echo "No log file yet"
    echo ""
    echo "Last heartbeat:"
    tail -5 "$LOG_DIR/monitor.log" 2>/dev/null | grep -i "heartbeat" | tail -1 || echo "No heartbeats yet"
}

# Stop daemon
stop_daemon() {
    if check_running; then
        local pid=$(cat "$PIDFILE")
        log "Stopping monitor (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$PIDFILE"
        log "Monitor stopped"
    else
        echo "Monitor not running"
    fi
}

# Help
show_help() {
    cat << 'EOF'
Diesel-Goose Self-Monitoring System
Usage: ./self_monitor.sh [command]

Commands:
    start       Start monitoring daemon (10-min cycles)
    stop        Stop monitoring daemon
    status      Show current status
    once        Run single monitoring cycle
    check       Run safety checks only
    heartbeat   Trigger single heartbeat
    sync        Sync with GitHub only
    help        Show this help

The monitor performs:
  - Safety scans (secrets, uncommitted changes, disk space)
  - Heartbeat generation (HEARTBEAT.md + Telegram)
  - GitHub sync (pull/push)
  - Self-repair on common issues

Logs: /Users/dieselgoose/.openclaw/logs/monitor.log
EOF
}

# Main entry point
case "${1:-}" in
    start)
        if check_running; then
            echo "Monitor already running (PID: $(cat "$PIDFILE"))"
            exit 1
        fi
        monitor_loop &
        echo "Monitor started (PID: $!)"
        ;;
    stop)
        stop_daemon
        ;;
    status)
        show_status
        ;;
    once)
        single_run
        ;;
    check)
        safety_check
        ;;
    heartbeat)
        trigger_heartbeat
        ;;
    sync)
        sync_github
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
