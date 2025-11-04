import os, re, requests
from dotenv import load_dotenv
from core.utils import call_gemini
from modules.weather_module import get_weather

load_dotenv()
TODOIST_TOKEN = os.getenv("TODOIST_API_KEY")
TODOIST_BASE = "https://api.todoist.com/rest/v2"

def handle_todo_intent(user_text: str):
    """Recognize sub-intents and act accordingly."""
    if not TODOIST_TOKEN:
        return "Todoist not configured. Please add your TODOIST_API_KEY in .env."

    if re.search(r"\b(add|create)\b", user_text, re.I):
        return add_task(user_text)
    elif re.search(r"\b(list|show)\b", user_text, re.I):
        return list_tasks()
    elif re.search(r"\b(delete|remove|clear)\b", user_text, re.I):
        return delete_task(user_text)
    else:
        return "Could you specify what you'd like to do with your tasks?"

def add_task(text):
    # Check for conditional weather clause
    if re.search(r"\bif\b.*\b(rain|sunny|clear|storm|weather)\b", text, re.I):
        m_city = re.search(r"in\s+([A-Za-z\s]+)", text)
        city = m_city.group(1).strip() if m_city else "Delhi"
        weather_report = get_weather(city)

        # Extract main action before 'if'
        base_task_match = re.search(r"(?:add|create|remind(?: me)? to)\s+(.*?)\s*(?:if|when|unless|provided|only if)", text, re.I)
        content = base_task_match.group(1).strip() if base_task_match else None

        if not content:
            return "Couldn't identify the actual task from your request."

        # Check weather condition
        if "rain" in weather_report.lower():
            return f"It looks rainy in {city}. I'll skip adding that task for now. ({weather_report})"
        else:
            headers = {"Authorization": f"Bearer {TODOIST_TOKEN}", "Content-Type": "application/json"}
            resp = requests.post(f"{TODOIST_BASE}/tasks", json={"content": content}, headers=headers)
            if resp.status_code not in (200, 201):
                return f"Failed to add task: {resp.text}"
            return f"Weather looks fine in {city}. Task '{content}' added successfully!"

    # Regular task creation (no condition)
    m = re.search(r"(?:add|create|remind(?: me)? to)\s+(.*)", text, re.I)
    content = m.group(1).strip() if m else None
    if not content:
        return "What task would you like to add?"
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}", "Content-Type": "application/json"}
    resp = requests.post(f"{TODOIST_BASE}/tasks", json={"content": content}, headers=headers)
    if resp.status_code not in (200, 201):
        return f"Failed to add task: {resp.text}"
    return f"Task '{content}' added successfully!"



def list_tasks():
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    resp = requests.get(f"{TODOIST_BASE}/tasks", headers=headers)
    if resp.status_code != 200:
        return f"Could not list tasks: {resp.text}"
    tasks = resp.json()
    if not tasks:
        return "You have no active tasks."
    lines = [f"{i+1}. {t['content']}" for i, t in enumerate(tasks)]
    return "\n".join(lines)

def delete_task(text):
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    resp = requests.get(f"{TODOIST_BASE}/tasks", headers=headers)
    if resp.status_code != 200:
        return "Could not fetch tasks for deletion."
    tasks = resp.json()
    if not tasks:
        return "No tasks to delete."

    # Handle 'delete all' intent
    if re.search(r"\b(all|everything|entire|clear (all)? list)\b", text, re.I):
        count = 0
        for t in tasks:
            del_resp = requests.delete(f"{TODOIST_BASE}/tasks/{t['id']}", headers=headers)
            if del_resp.status_code == 204:
                count += 1
        return f"Deleted all {count} tasks."

    # Handle single task deletion
    phrase = re.sub(r"\b(delete|remove|task|the|list)\b", "", text, flags=re.I).strip().lower()
    best = None
    for t in tasks:
        if phrase in t["content"].lower():
            best = t
            break
    if not best:
        return f"Couldn't find a task matching '{phrase}'."
    del_resp = requests.delete(f"{TODOIST_BASE}/tasks/{best['id']}", headers=headers)
    if del_resp.status_code == 204:
        return f"Deleted task '{best['content']}'."
    return "Delete failed."