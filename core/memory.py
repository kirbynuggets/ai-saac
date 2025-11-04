import json, os
from datetime import datetime

MEMORY_FILE = "assistant_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"conversation": []}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"conversation": []}

def save_memory(memory):
    memory["last_saved"] = datetime.now().isoformat()
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)
