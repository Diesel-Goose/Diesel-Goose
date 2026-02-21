#!/usr/bin/env python3
"""
heartbeat_generator.py – Founder / Chairman Pulse Generator
Appends formatted entries to HEARTBEAT.md in the exact Telegram-optimized format.
Safe for repeated calls, cron, or integration with founder_orchestrator.py.

Usage:
    from heartbeat_generator import append_heartbeat
    append_heartbeat(health=92, budget=87, mission=95, status="MAX", wish_summary="Launch XRPL liquidity monitor v2")

Or run standalone:
    python heartbeat_generator.py 92 87 95 MAX "Refine ethical veto layer"
"""

import os
import datetime
import sys
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG – Adjust only if repo structure changes
# ──────────────────────────────────────────────────────────────────────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Diesel-Goose root
HEARTBEAT_PATH = os.path.join(REPO_ROOT, "HEARTBEAT.md")
VERSION = "v1.8.0"  # Bump on major feature adds
LOG_SECTION_MARKER = "## LOG ENTRIES (Append-only – scripts add below this line)"

HEALTH_BAR_BLOCKS = 8
BLOCK_FULL = "█"
BLOCK_EMPTY = "░"
BLOCK_WIDTH = 100 // HEALTH_BAR_BLOCKS  # 12.5% per block


def generate_health_bar(percentage: int) -> str:
    """Generate visual bar: [███████░] style – 8 blocks = 100%"""
    if not 0 <= percentage <= 100:
        percentage = max(0, min(100, percentage))  # clamp
    filled = int(percentage / BLOCK_WIDTH)
    return f"[{BLOCK_FULL * filled}{BLOCK_EMPTY * (HEALTH_BAR_BLOCKS - filled)}]"


def append_heartbeat(
    health: int,
    budget: int,
    mission: int,
    status: str,
    wish_summary: str,
    version: Optional[str] = None,
    dry_run: bool = False
) -> str:
    """
    Append a new heartbeat entry to HEARTBEAT.md in Founder-locked format.
    Returns the exact string written (for logging / Telegram preview).
    """
    now = datetime.datetime.now()
    ts = now.strftime("%Y-%m-%d • %I:%M %p CST").lstrip("0")  # clean leading zero on day/hour
    ver = version or VERSION

    health_bar = generate_health_bar(health)

    # Core 3-line Telegram payload
    line1 = "🦆 DIESELGOOSE | Founder — Greenhead Labs"
    line2 = f"⚡️ {health}% | 💰 {budget}% | 💡 {mission}% | 🔥 {status}"
    line3 = f"🎯 Active: {wish_summary.strip()}"

    # Full log block (includes visual bar for markdown readability)
    entry = f"""
📅 {ts} • {ver}
{health_bar} {health}% — Health
{line2}
{line3}

"""

    entry = entry.strip()

    # Safety: Ensure file exists and has the LOG_ENTRIES section
    if not os.path.isfile(HEARTBEAT_PATH):
        print(f"ERROR: HEARTBEAT.md not found at {HEARTBEAT_PATH}", file=sys.stderr)
        return ""

    with open(HEARTBEAT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if LOG_SECTION_MARKER not in content:
        print(f"WARNING: LOG_ENTRIES marker missing – appending anyway", file=sys.stderr)

    # Append only – never overwrite
    if not dry_run:
        with open(HEARTBEAT_PATH, "a", encoding="utf-8") as f:
            f.write("\n" + entry + "\n")

    # Return payload for Telegram / logging
    telegram_payload = f"{line1}\n{line2}\n{line3}"
    print("Heartbeat generated (Telegram-ready):\n" + telegram_payload)
    return telegram_payload


if __name__ == "__main__":
    # CLI mode – python heartbeat_generator.py <health> <budget> <mission> <status> "wish summary"
    if len(sys.argv) >= 6:
        try:
            health = int(sys.argv[1])
            budget = int(sys.argv[2])
            mission = int(sys.argv[3])
            status = sys.argv[4].upper()
            wish = " ".join(sys.argv[5:])
            append_heartbeat(health, budget, mission, status, wish)
        except ValueError:
            print("Usage: python heartbeat_generator.py 92 87 95 MAX \"Launch XRPL v2 monitor\"", file=sys.stderr)
            sys.exit(1)
    else:
        # Example invocation
        append_heartbeat(
            health=94,
            budget=89,
            mission=96,
            status="MAX",
            wish_summary="Integrate real-time XRPL signal alerts + Catholic ethics filter v2"
        )
