#!/usr/bin/env bash
# Install Diesel Goose Watchdog as cron job
# Runs every 10 minutes

WATCHDOG_SCRIPT="/Users/dieselgoose/.openclaw/workspace/watchdog.sh"
LOG_DIR="/Users/dieselgoose/.openclaw/logs"

# Make watchdog executable
chmod +x "$WATCHDOG_SCRIPT"

# Create log directory
mkdir -p "$LOG_DIR"

# Install cron job
(crontab -l 2>/dev/null || echo "") | grep -v "watchdog" > /tmp/cron_temp
echo "*/10 * * * * $WATCHDOG_SCRIPT >> $LOG_DIR/watchdog_cron.log 2>&1" >> /tmp/cron_temp

if crontab /tmp/cron_temp 2>/dev/null; then
    echo "✅ Watchdog cron job installed"
    echo "   Runs every 10 minutes"
    echo "   Logs: $LOG_DIR/watchdog.log"
    echo ""
    echo "Next run in: 10 minutes"
else
    echo "❌ Failed to install cron job"
    echo "   (macOS may restrict cron — use launchd instead)"
    echo ""
    echo "Manual alternative:"
    echo "   while true; do $WATCHDOG_SCRIPT; sleep 600; done"
fi

rm -f /tmp/cron_temp
