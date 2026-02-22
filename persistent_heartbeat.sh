#!/usr/bin/env bash
# Diesel-Goose Persistent Heartbeat Launcher
# Uses GNU screen to survive terminal closures

SESSION_NAME="dieselgoose"
LOG_DIR="/Users/dieselgoose/.openclaw/logs"
WORKSPACE="/Users/dieselgoose/.openclaw/workspace"

start_heartbeat() {
    # Kill existing session if running
    screen -S "$SESSION_NAME" -X quit 2>/dev/null
    
    echo "🚀 Starting persistent heartbeat in screen session: $SESSION_NAME"
    
    # Create new detached screen session
    screen -dmS "$SESSION_NAME" -c /dev/null
    
    # Send commands to the session
    screen -S "$SESSION_NAME" -X stuff "cd $WORKSPACE && ./self_monitor.sh start$(printf \\r)"
    
    echo "✅ Heartbeat running persistently"
    echo ""
    echo "Commands:"
    echo "  screen -r $SESSION_NAME          # View live monitor"
    echo "  Ctrl+A then D                     # Detach (keeps running)"
    echo "  screen -S $SESSION_NAME -X quit   # Stop completely"
    echo ""
    echo "Logs: tail -f $LOG_DIR/monitor.log"
}

stop_heartbeat() {
    screen -S "$SESSION_NAME" -X quit 2>/dev/null
    echo "🛑 Heartbeat stopped"
}

status() {
    if screen -list | grep -q "$SESSION_NAME"; then
        echo "✅ Heartbeat session active: $SESSION_NAME"
        screen -list | grep "$SESSION_NAME"
        echo ""
        echo "Recent activity:"
        tail -5 "$LOG_DIR/monitor.log" 2>/dev/null || echo "No log yet"
    else
        echo "❌ Heartbeat session not running"
        echo "Start with: ./persistent_heartbeat.sh start"
    fi
}

attach() {
    if screen -list | grep -q "$SESSION_NAME"; then
        echo "Attaching to heartbeat session..."
        echo "Press Ctrl+A then D to detach (keeps running)"
        sleep 2
        screen -r "$SESSION_NAME"
    else
        echo "No session to attach to. Start with: ./persistent_heartbeat.sh start"
    fi
}

case "${1:-}" in
    start)
        start_heartbeat
        ;;
    stop)
        stop_heartbeat
        ;;
    status)
        status
        ;;
    attach)
        attach
        ;;
    restart)
        stop_heartbeat
        sleep 1
        start_heartbeat
        ;;
    *)
        echo "Diesel-Goose Persistent Heartbeat"
        echo "Usage: $0 {start|stop|status|attach|restart}"
        echo ""
        echo "This runs the heartbeat in a screen session so it survives"
        echo "terminal closures and runs 24/7."
        ;;
esac
