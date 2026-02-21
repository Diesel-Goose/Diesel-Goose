import json
import os
import uuid
from datetime import datetime
from typing import Dict, List

PRIVATE_PATH = "memory_store/private.json"
PUBLIC_PATH = "memory_store/public.json"


def _ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"memories": []}, f)


def load_memories(path: str) -> List[Dict]:
    _ensure_file(path)
    with open(path, "r") as f:
        return json.load(f)["memories"]


def save_memories(path: str, memories: List[Dict]):
    with open(path, "w") as f:
        json.dump({"memories": memories}, f, indent=2)


def add_memory(content: str, confidence: float = 0.9, public: bool = False):
    """
    Add a structured memory entry.
    Only saves if confidence > 0.8
    """
    if confidence < 0.8:
        return False

    path = PUBLIC_PATH if public else PRIVATE_PATH
    memories = load_memories(path)

    # Deduplication check
    for m in memories:
        if m["content"].lower() == content.lower():
            return False

    new_memory = {
        "id": str(uuid.uuid4()),
        "content": content,
        "confidence": confidence,
        "privacy": "public" if public else "private",
        "timestamp": datetime.utcnow().isoformat()
    }

    memories.append(new_memory)
    save_memories(path, memories)

    return True
