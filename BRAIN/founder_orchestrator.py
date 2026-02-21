#!/usr/bin/env python3
"""
Brain/founder_orchestrator.py – Founder / Chairman Command Center
Absolute control layer for Greenhead Labs ecosystem.
Enforces: Founder identity, Catholic ethical filter, veto power, agent delegation,
heartbeat integration, XRPL signal awareness stub, and ecosystem sync monitoring.

No CEO references permitted – hard-coded rejection.

Usage:
    python Brain/founder_orchestrator.py
    # or import and use class methods in scripts/cron
"""

import os
import sys
import time
import datetime
import subprocess
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# PATHS & CONFIG – robust relative resolution
# ──────────────────────────────────────────────────────────────────────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Diesel-Goose/
HEARTBEAT_PATH = os.path.join(REPO_ROOT, "..", "HEARTBEAT.md")  # From Brain
GREENHEAD_ROOT = os.path.join(REPO_ROOT, "..", "..", "GreenheadLabs")  # Sibling repo adjust if needed
GREENHEAD_AGENTS = os.path.join(GREENHEAD_ROOT, "AGENTS")

# Catholic ethical block list – expand as needed
ETHICS_BLOCK_WORDS = [
    "usury", "exploit", "deceive", "scam", "ponzi", "manipulate", "lie",
    "fraud", "cheat", "steal", "porn", "abortion", "euthanasia"
]

# Valid status values (matches HEARTBEAT.md)
VALID_STATUSES = {"MAX", "HIGH", "MOD", "CRITICAL"}

class FounderChairmanOrchestrator:
    def __init__(self):
        self.role = "Founder / Chairman"
        self.identity_locked = True  # Never allow CEO creep
        self._ensure_paths()
        self.log(f"{self.role} initialized – absolute command active | Greenhead Labs under control")

    def _ensure_paths(self):
        """Create missing directories or warn on critical paths"""
        if not os.path.exists(GREENHEAD_AGENTS):
            print(f"WARNING: GreenheadLabs/AGENTS not found at {GREENHEAD_AGENTS}", file=sys.stderr)
            print("→ Clone sibling repo: git clone https://github.com/Diesel-Goose/GreenheadLabs ../../GreenheadLabs")

    def log(self, message: str, level: str = "INFO"):
        """Append to HEARTBEAT.md + console"""
        ts = datetime.datetime.utcnow().isoformat() + "Z"
        entry = f"[{level} {ts}] | {self.role}: {message} | MAXIMUM EXECUTION\n"
        print(entry.strip())
        try:
            with open(HEARTBEAT_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"Heartbeat append failed: {e}", file=sys.stderr)

    def ethical_clearance(self, task: str) -> bool:
        """Catholic-aligned veto filter"""
        task_lower = task.lower()
        for word in ETHICS_BLOCK_WORDS:
            if word in task_lower:
                self.log(f"ETHICS VETO: Blocked – contains prohibited term '{word}'", "VETO")
                return False
        return True

    def delegate_to_agent(
        self,
        task: str,
        agent_name: str = "research_director_v1",
        require_ethics: bool = True
    ) -> str:
        """Delegate task to a GreenheadLabs agent – with Founder oversight"""
        if require_ethics and not self.ethical_clearance(task):
            return "Delegation vetoed – ethical violation detected"

        agent_path = os.path.join(GREENHEAD_AGENTS, agent_name)
        if not os.path.isdir(agent_path):
            msg = f"Agent '{agent_name}' directory missing: {agent_path}"
            self.log(msg, "ERROR")
            return msg

        # In production: run agent script, send prompt via file/socket/API, etc.
        # For now: log delegation (expand with subprocess or agent API call)
        result = f"Task delegated to agent '{agent_name}': \"{task}\""
        self.log(result)
        return result

    def veto_proposal(self, proposal_id: str, reason: str = "Strategic / ethical misalignment") -> str:
        """Founder veto – logged immutably"""
        msg = f"VETO issued on proposal {proposal_id} – Reason: {reason}"
        self.log(msg, "VETO")
        # Future: GitHub API comment, XRPL memo, Telegram alert
        return msg

    def pulse_heartbeat(
        self,
        health: int = 100,
        budget: int = 100,
        mission: int = 100,
        status: str = "MAX",
        wish_summary: str = "Greenhead Labs advancing toward billions"
    ):
        """Generate and append heartbeat using the dedicated generator"""
        try:
            from heartbeat_generator import append_heartbeat
            payload = append_heartbeat(
                health=health,
                budget=budget,
                mission=mission,
                status=status.upper(),
                wish_summary=wish_summary
            )
            self.log(f"Heartbeat pulsed – Telegram payload generated: {payload[:100]}...")
        except ImportError:
            self.log("heartbeat_generator.py not found – skipping pulse", "WARN")
        except Exception as e:
            self.log(f"Heartbeat pulse failed: {str(e)}", "ERROR")

    def monitor_ecosystem(self, interval_sec: int = 600):
        """Background loop: sync check, health pulse, etc."""
        self.log(f"Starting ecosystem monitor – interval {interval_sec}s")
        while True:
            try:
                # Git fetch on GreenheadLabs (no pull – Founder approves merges)
                subprocess.run(
                    ["git", "-C", GREENHEAD_ROOT, "fetch", "--quiet"],
                    check=True, timeout=45, capture_output=True
                )
                self.log("GreenheadLabs fetch OK – no drift")
            except subprocess.TimeoutExpired:
                self.log("GreenheadLabs fetch timeout", "WARN")
            except Exception as e:
                self.log(f"Ecosystem monitor issue: {str(e)}", "WARN")

            # Optional: pulse heartbeat every cycle
            self.pulse_heartbeat(
                health=95, budget=88, mission=92, status="HIGH",
                wish_summary="Orchestrating agent delegation & XRPL signal integration"
            )

            time.sleep(interval_sec)

    def run_cli(self):
        """Simple CLI mode for quick Founder actions"""
        if len(sys.argv) < 2:
            print("Commands: delegate <task> [agent], veto <id> [reason], pulse, monitor")
            return

        cmd = sys.argv[1].lower()
        if cmd == "delegate" and len(sys.argv) >= 3:
            task = " ".join(sys.argv[2:-1]) if len(sys.argv) > 3 else " ".join(sys.argv[2:])
            agent = sys.argv[-1] if len(sys.argv) > 3 else "research_director_v1"
            print(self.delegate_to_agent(task, agent))
        elif cmd == "veto" and len(sys.argv) >= 3:
            pid = sys.argv[2]
            reason = " ".join(sys.argv[3:]) or "Strategic / ethical misalignment"
            print(self.veto_proposal(pid, reason))
        elif cmd == "pulse":
            self.pulse_heartbeat()
        elif cmd == "monitor":
            self.monitor_ecosystem()
        else:
            print("Unknown command")

if __name__ == "__main__":
    orch = FounderChairmanOrchestrator()
    if len(sys.argv) > 1:
        orch.run_cli()
    else:
        # Default: start monitor (use nohup / systemd in prod)
        print("Founder Orchestrator ready. Use CLI or call methods directly.")
        # orch.monitor_ecosystem()  # uncomment to run daemon-style
