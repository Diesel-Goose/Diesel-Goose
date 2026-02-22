#!/bin/bash
# Chris Dunn Persistent Runner
# Starts Chris Dunn in sandbox mode and keeps it running
# Reports every 15 minutes to Telegram group

SANDBOX_DIR="/Users/dieselgoose/.openclaw/workspace/GreenheadLabs/EMPLOYEES/CFO/SPECIALIST-CFO-03"
LOG_FILE="$SANDBOX_DIR/logs/chris_dunn_service.log"
PID_FILE="$SANDBOX_DIR/logs/chris_dunn.pid"

# Ensure log directory exists
mkdir -p "$SANDBOX_DIR/logs"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log "✅ Chris Dunn already running (PID: $PID)"
            return 0
        else
            log "⚠️ Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Start Chris Dunn
start() {
    if check_running; then
        echo "Chris Dunn is already running"
        return 0
    fi

    log "🦆 Starting Chris Dunn (Sandbox Mode)..."
    log "📊 Strategy: momentum (with rotation)"
    log "⏱️  Report interval: 15 minutes"
    log "💰 Mode: PAPER ONLY"
    
    cd "$SANDBOX_DIR" || exit 1
    
    # Activate virtual environment if exists
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # Start the daemon in background
    nohup python3 chris_daemon.py >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    log "✅ Chris Dunn started (PID: $!)"
    log "📱 Reports will post to Greenhead Lab group every 15 minutes"
    
    # Send startup message to group
    python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from utils.financial_reporter import FinancialReporter
from utils.alerts import AlertManager
import yaml

async def send_startup():
    with open('sandbox_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    reporter = FinancialReporter(config, AlertManager(config))
    
    message = '''🦆 Chris Dunn | Lead XRPL Analyst — Greenhead Labs
⚡️ 0 Trades/Min | 💰 0.0% Profit | 💡 0% Win | 🔥 MAX
🎯 Active: Starting up... Paper Trading XRP via Sandbox
📅 $(date '+%H:%M') CST • System Startup • 15-min reports enabled'''
    
    await reporter.post_to_group(message)

asyncio.run(send_startup())
" 2>/dev/null &
}

# Stop Chris Dunn
stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        log "🛑 Stopping Chris Dunn (PID: $PID)..."
        kill "$PID" 2>/dev/null
        rm -f "$PID_FILE"
        log "✅ Chris Dunn stopped"
    else
        log "⚠️ Chris Dunn not running"
    fi
}

# Check status
status() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        RUNTIME=$(ps -o etime= -p "$PID" | tr -d ' ')
        log "📊 Status: RUNNING"
        log "   PID: $PID"
        log "   Uptime: $RUNTIME"
        
        # Show recent trades
        if [ -f "$SANDBOX_DIR/sandbox/audit.log" ]; then
            TRADES=$(tail -20 "$SANDBOX_DIR/sandbox/audit.log" | grep -c "TRADE" || echo "0")
            log "   Recent trades: $TRADES"
        fi
        return 0
    else
        log "📊 Status: STOPPED"
        return 1
    fi
}

# Restart
restart() {
    stop
    sleep 2
    start
}

# Show recent logs
logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -50 "$LOG_FILE"
    else
        echo "No log file found"
    fi
}

# Command handling
case "${1:-start}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
