import json
import os
from datetime import datetime

MEMORY_FILE = "assistant_memory.json"

def load_memory():
    """Load past conversation and tasks."""
    if not os.path.exists(MEMORY_FILE):
        return {"conversation": [], "tasks_added": []}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"conversation": [], "tasks_added": []}

def save_memory(memory):
    """Persist memory to disk."""
    memory["last_saved"] = datetime.now().isoformat()
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def remember_task(memory, task_text, task_id):
    """Remember each task the assistant created."""
    memory["tasks_added"].append(
        {"text": task_text, "id": task_id, "time": datetime.now().isoformat()}
    )
    save_memory(memory)

def clear_memory():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
