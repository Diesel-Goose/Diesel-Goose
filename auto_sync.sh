#!/bin/bash
# Auto-sync local changes to GitHub
# Run this every 5 minutes via cron: */5 * * * * /Users/dieselgoose/.openclaw/workspace/auto_sync.sh

cd /Users/dieselgoose/.openclaw/workspace

# Pull first (get any GitHub changes)
git fetch origin
git reset --hard origin/main 2>/dev/null || git pull --ff-only

# Check for local changes
if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "Auto-sync $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "✅ Synced at $(date)"
else
    echo "ℹ️ No changes at $(date)"
fi
