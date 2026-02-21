#!/bin/bash
# Auto-sync every 5 minutes
# Add to crontab: */5 * * * * /Users/dieselgoose/.openclaw/workspace/sync.sh

cd /Users/dieselgoose/.openclaw/workspace

# Pull first
git fetch origin
git reset --hard origin/main 2>/dev/null

# Push if changes
if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "Sync $(date +%H:%M)"
    git push origin main
fi
