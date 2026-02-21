import json
from typing import List, Dict

PRIVATE_PATH = "memory_store/private.json"
PUBLIC_PATH = "memory_store/public.json"

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(path, data: Dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def add_memory(entry: Dict, public=False):
    path = PUBLIC_PATH if public else PRIVATE_PATH
    mem = load_json(path)
    mem.update(entry)
    save_json(path, mem)
