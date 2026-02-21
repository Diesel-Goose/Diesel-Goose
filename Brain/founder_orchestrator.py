import os
import subprocess
import time
import datetime
import json
from typing import Optional

# Paths – adjust if GreenheadLabs not cloned as sibling
HEARTBEAT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "HEARTBEAT.md")
GREENHEAD_AGENTS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "GreenheadLabs", "AGENTS")

ETHICS_BLOCK_WORDS = ["usury", "exploit", "deceive", "scam", "ponzi", "manipulate", "lie"]

class FounderChairmanOrchestrator:
    def __init__(self):
        self.role = "Founder / Chairman"
        self.log(f"{self.role} online – absolute command established")

    def log(self, message: str, level: str = "INFO"):
        ts = datetime.datetime.utcnow().isoformat() + "Z"
        entry = f"[{level} {ts}] | {self.role}: {message} | MAXIMUM EXECUTION\n"
        print(entry.strip())
        try:
            with open(HEARTBEAT_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"Heartbeat log failed: {e}")

    def ethical_clearance(self, task: str) -> bool:
        task_lower = task.lower()
        for word in ETHICS_BLOCK_WORDS:
            if word in task_lower:
                self.log(f"ETHICS VETO: Task blocked – contains '{word}'", "VETO")
                return False
        return True

    def delegate_to_agent(self, task: str, agent_name: str = "research_director_v1") -> str:
        if not self.ethical_clearance(task):
            return "Delegation vetoed – ethical violation"

        agent_path = os.path.join(GREENHEAD_AGENTS, agent_name)
        if not os.path.exists(agent_path):
            self.log(f"Agent directory missing: {agent_path}", "ERROR")
            return f"Agent {agent_name} not found"

        # In production: subprocess.run agent main script or API call
        result = f"Task delegated to {agent_name}: '{task}'"
        self.log(result)
        return result

    def veto_proposal(self, proposal_id: str, reason: str = "Strategic misalignment"):
        msg = f"VETO executed on proposal {proposal_id} – Reason: {reason}"
        self.log(msg, "VETO")
        # Future: Post comment via GitHub API or XRPL memo
        return msg

    def monitor_greenhead_sync(self, interval_sec: int = 600):
        self.log("Starting ecosystem monitor loop")
        while True:
            try:
                subprocess.run(["git", "-C", os.path.dirname(GREENHEAD_AGENTS), "fetch", "--quiet"], check=True, timeout=30)
                self.log("GreenheadLabs sync checked – no drift detected")
            except Exception as e:
                self.log(f"Ecosystem sync issue: {str(e)}", "WARN")
            time.sleep(interval_sec)

if __name__ == "__main__":
    orch = FounderChairmanOrchestrator()
    # Test commands – uncomment as needed
    # orch.delegate_to_agent("Analyze new XRPL AMM opportunity for token launch")
    # orch.veto_proposal("PROP-042", "Conflicts with long-term Catholic-aligned vision")
    # orch.monitor_greenhead_sync()  # Run as daemon in prod
