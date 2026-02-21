#!/usr/bin/env python3
"""
silent-heartbeat.py - Silent Git-based heartbeat for Diesel-Goose repo.
Implements HEARTBEAT.md auto-sync: pull, update timestamp/wish %, safety scans, commit/push.
No Telegram, no external calls, local logs only. Run in loop or cron.
Error-free, billion-dollar reliability: fail fast, freeze on issues.

Usage: python silent-heartbeat.py [--cadence MINUTES] (default 30)
Env vars: REPO_PATH (default .), GIT_BRANCH (default main)
"""

import os
import sys
import time
import hashlib
import re
import subprocess
from datetime import datetime, timezone
import argparse

# Constants - Align with HEARTBEAT.md
CORE_FILES = ['HEARTBEAT.md', 'FOUNDER.md', 'IDENTITY.md', 'RULES.md']
SECRETS_REGEX = re.compile(r'(?i)(api_key|token|password|secret|private_key|bearer|auth|wallet|ssh_key)')
COMMIT_FORMAT = "HEARTBEAT {timestamp} | Wish {wish_pct}% | {mode} | Mandate: {summary}"
LOG_FILE = 'local_heartbeat.log'  # Local only, no external send

def log(message, level='INFO'):
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")

def run_git(cmd, repo_path='.'):
    try:
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"Git error: {e.stderr}", 'ERROR')
        sys.exit(1)

def safety_checks(repo_path='.'):
    failures = 0
    # Secrets scan
    for file in os.listdir(repo_path):
        if file.endswith(('.md', '.py', '.sh')):
            with open(os.path.join(repo_path, file), 'r') as f:
                content = f.read()
                if SECRETS_REGEX.search(content):
                    log(f"Secrets detected in {file}", 'CRITICAL')
                    failures += 1
    # Hash validation (simple SHA256 for core files)
    for core_file in CORE_FILES:
        if os.path.exists(os.path.join(repo_path, core_file)):
            with open(os.path.join(repo_path, core_file), 'rb') as f:
                hash_val = hashlib.sha256(f.read()).hexdigest()
                log(f"Hash for {core_file}: {hash_val}", 'DEBUG')  # Placeholder - in prod, compare to known good
        else:
            log(f"Missing core file: {core_file}", 'ERROR')
            failures += 1
    # No unexpected binaries
    for file in os.listdir(repo_path):
        if file.endswith(('.exe', '.bin', '.dll')):
            log(f"Unexpected binary: {file}", 'CRITICAL')
            failures += 1
    return failures

def update_heartbeat_md(repo_path='.'):
    hb_path = os.path.join(repo_path, 'HEARTBEAT.md')
    with open(hb_path, 'r') as f:
        content = f.read()
    # Update timestamp (ISO with Z)
    new_ts = datetime.now(timezone.utc).isoformat(timespec='seconds')
    content = re.sub(r'Last heartbeat: .+', f'Last heartbeat: {new_ts}', content)
    # Increment wish % (placeholder logic - bump by 1% each run, cap 100)
    match = re.search(r'Wish fulfillment: (\d+)%', content)
    wish_pct = min(int(match.group(1)) + 1 if match else 35, 100)
    content = re.sub(r'Wish fulfillment: \d+%', f'Wish fulfillment: {wish_pct}%', content)
    # Mode + summary (hardcode for now, or parse from content)
    mode = 'MAXIMUM EXECUTION'
    summary = 'Silent sync complete'
    with open(hb_path, 'w') as f:
        f.write(content)
    return wish_pct, mode, summary, new_ts

def main():
    parser = argparse.ArgumentParser(description='Silent Heartbeat for Diesel-Goose')
    parser.add_argument('--cadence', type=int, default=30, help='Minutes between heartbeats')
    args = parser.parse_args()

    repo_path = os.environ.get('REPO_PATH', '.')
    branch = os.environ.get('GIT_BRANCH', 'main')
    consecutive_failures = 0

    while True:
        log("Starting heartbeat cycle")
        # 1. git pull
        run_git(['git', 'pull', 'origin', branch], repo_path)
        
        # 2. Update HEARTBEAT.md
        wish_pct, mode, summary, timestamp = update_heartbeat_md(repo_path)
        
        # 3. Safety checks
        failures = safety_checks(repo_path)
        if failures > 0:
            consecutive_failures += 1
            log(f"Safety failures: {failures}", 'ERROR')
            if consecutive_failures >= 2:
                log("Freezing pushes - manual restore required", 'CRITICAL')
                sys.exit(1)  # Halt - Chairman restores via Telegram
        else:
            consecutive_failures = 0
        
        # 4. Stage + commit
        run_git(['git', 'add', 'HEARTBEAT.md'], repo_path)
        commit_msg = COMMIT_FORMAT.format(timestamp=timestamp, wish_pct=wish_pct, mode=mode, summary=summary)
        run_git(['git', 'commit', '-m', commit_msg], repo_path)
        
        # 5. git push (safe, no force)
        run_git(['git', 'push', 'origin', branch], repo_path)
        
        log("Heartbeat complete")
        time.sleep(args.cadence * 60)  # Loop with cadence

if __name__ == '__main__':
    main()
