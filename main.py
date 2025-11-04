import os
import re
import requests
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from step3_memory import load_memory, save_memory, remember_task

# -------------------------------------------------------------------
# ENVIRONMENT SETUP
# -------------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TODOIST_TOKEN = os.getenv("TODOIST_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing in .env")

# -------------------------------------------------------------------
# TODOIST HELPERS
# -------------------------------------------------------------------
TODOIST_BASE = "https://api.todoist.com/rest/v2"

def todoist_create_task(content: str, due_string: str = None):
    """Create a task in Todoist."""
    if not TODOIST_TOKEN:
        raise RuntimeError("Todoist token not set")
    url = f"{TODOIST_BASE}/tasks"
    headers = {
        "Authorization": f"Bearer {TODOIST_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"content": content}
    if due_string:
        payload["due_string"] = due_string
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Todoist create failed: {resp.status_code} - {resp.text}")
    return resp.json()

def todoist_list_tasks():
    """List active tasks."""
    if not TODOIST_TOKEN:
        raise RuntimeError("Todoist token not set")
    url = f"{TODOIST_BASE}/tasks"
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"Todoist list failed: {resp.status_code} - {resp.text}")
    return resp.json()

def todoist_delete_task(task_id: int):
    """Delete a task by ID."""
    url = f"{TODOIST_BASE}/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    resp = requests.delete(url, headers=headers)
    return resp.status_code == 204

# -------------------------------------------------------------------
# INTENT DETECTION
# -------------------------------------------------------------------
ADD_RE = re.compile(r"\b(add|create|remind|remember|set)\b", re.I)
LIST_RE = re.compile(r"\b(list|show|what (are|is)|view)\b", re.I)
DEL_RE = re.compile(r"\b(delete|remove|clear)\b", re.I)
EXIT_RE = re.compile(r"\b(exit|quit|bye)\b", re.I)

def detect_intent(text: str):
    if EXIT_RE.search(text):
        return "exit"
    if ADD_RE.search(text):
        return "add"
    if LIST_RE.search(text):
        return "list"
    if DEL_RE.search(text):
        return "delete"
    return "none"

# -------------------------------------------------------------------
# GEMINI LLM
# -------------------------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY, temperature=0.2
)
system_prompt = (
    "You are a helpful assistant that manages a user's to-do tasks. "
    "Be concise, polite, and accurate."
)

# -------------------------------------------------------------------
# MEMORY INITIALIZATION
# -------------------------------------------------------------------
memory = load_memory()
conversation_history = memory.get(
    "conversation", [{"role": "system", "content": system_prompt}]
)

# -------------------------------------------------------------------
# GEMINI CALL WITH HISTORY
# -------------------------------------------------------------------
def call_gemini_with_history(user_message: str):
    """Send system + history + user message to Gemini and return short reply."""
    history_text = ""
    for msg in conversation_history:
        if msg["role"] in ("user", "assistant"):
            history_text += f"{msg['role'].capitalize()}: {msg['content']}\n"

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "{user_input}")]
    )
    chain = prompt | llm | StrOutputParser()
    full_input = {
        "user_input": f"{history_text}\nUser: {user_message}\nAssistant (short):"
    }
    try:
        reply = chain.invoke(full_input)
        return str(reply).strip()
    except Exception as e:
        return f"Sorry, something went wrong: {e}"

# -------------------------------------------------------------------
# MAIN LOOP
# -------------------------------------------------------------------
def main_loop():
    print("Simple Todoist-enabled assistant. Type 'exit' to quit.")
    while True:
        user_text = input("\nYou: ").strip()
        if not user_text:
            continue

        intent = detect_intent(user_text)
        if intent == "exit":
            print("Assistant: Goodbye — good luck with your tasks!")
            break

        conversation_history.append({"role": "user", "content": user_text})
        memory["conversation"] = conversation_history
        save_memory(memory)

        # -----------------------------------------------------------
        # ADD TASK
        # -----------------------------------------------------------
        if intent == "add":
            content, due = None, None
            quoted = re.findall(r"'([^']+)'|\"([^\"]+)\"", user_text)
            if quoted:
                content = next((q[0] or q[1]) for q in quoted)

            if not content:
                m = re.search(r"(?:add|create|remind(?: me)? to)\s+(.*)", user_text, re.I)
                if m:
                    content = m.group(1)
                    # Remove filler phrases like "to the list"
                    content = re.sub(
                        r"\b(to (the )?(list|todo(ist)?|task(s)?|my tasks?)|in (the )?(list|todo(ist)?))\b",
                        "",
                        content,
                        flags=re.I,
                    )
                    # Remove time expressions
                    content = re.sub(
                        r"\b(tomorrow|today|tonight|this (morning|evening)|on \S+|at \d{1,2}(:\d{2})?\s?(am|pm)?)\b",
                        "",
                        content,
                        flags=re.I,
                    )
                    content = content.strip(" .!?").strip()

            due_match = re.search(
                r"\b(tomorrow|today|next \w+|monday|tuesday|wednesday|thursday|friday|saturday|sunday|at \d{1,2}(?:[:.]\d{2})?(?:\s?(?:am|pm))?)\b",
                user_text,
                re.I,
            )
            if due_match:
                due = due_match.group(0)

            if not content:
                followup = call_gemini_with_history(
                    "The user said they want to add a task, but I couldn't detect what. Ask briefly what task to add."
                )
                print("Assistant:", followup)
                conversation_history.append({"role": "assistant", "content": followup})
                continue

            try:
                created = todoist_create_task(content=content, due_string=due)
                created_id = created.get("id")
                remember_task(memory, content, created_id)
                assistant_text = f"Added '{content}'" + (
                    f" (due {due})" if due else ""
                )
            except Exception as e:
                assistant_text = f"Task creation failed: {e}"

            conversation_history.append({"role": "assistant", "content": assistant_text})
            memory["conversation"] = conversation_history
            save_memory(memory)

            gemini_reply = call_gemini_with_history(
                "Provide a one-sentence confirmation for the task just added."
            )
            print("Assistant:", gemini_reply)
            conversation_history.append({"role": "assistant", "content": gemini_reply})
            continue

        # -----------------------------------------------------------
        # LIST TASKS
        # -----------------------------------------------------------
        if intent == "list":
            try:
                tasks = todoist_list_tasks()
                if not tasks:
                    assistant_text = "You have no active tasks."
                    print("Assistant:", assistant_text)
                else:
                    out_lines = []
                    for i, t in enumerate(tasks[:10], start=1):
                        due = (
                            t.get("due", {}).get("string") if t.get("due") else ""
                        )
                        out_lines.append(
                            f"{i}. {t.get('content')} {('('+due+')') if due else ''} [id:{t.get('id')}]"
                        )
                    listing = "\n".join(out_lines)
                    print("Assistant:\n" + listing)
                    assistant_text = "Listed your current tasks."
                conversation_history.append(
                    {"role": "assistant", "content": assistant_text}
                )
                memory["conversation"] = conversation_history
                save_memory(memory)
            except Exception as e:
                print("Assistant: Could not list tasks:", e)
            continue

        # -----------------------------------------------------------
        # DELETE TASKS (IMPROVED + DELETE-ALL)
        # -----------------------------------------------------------
        if intent == "delete":
            try:
                tasks = todoist_list_tasks()
                if not tasks:
                    print("Assistant: No tasks to delete.")
                    continue

                # Check for "delete all"
                if re.search(r"\b(all|everything|entire|clear (all)? list)\b", user_text, re.I):
                    confirm = input("Are you sure you want to delete ALL tasks? (y/n): ").strip().lower()
                    if confirm != "y":
                        print("Assistant: Cancelled delete-all operation.")
                        continue
                    count = 0
                    for t in tasks:
                        if todoist_delete_task(t["id"]):
                            count += 1
                    print(f"Assistant: Deleted all {count} tasks.")
                    memory["tasks_added"] = []
                    save_memory(memory)
                    continue

                # Otherwise, delete specific task
                target_phrase = re.sub(
                    r"\b(delete|remove|task|please|from|the|list|my)\b", "", user_text, flags=re.I
                ).strip()

                if not target_phrase:
                    print("Assistant: Please specify which task you want me to delete.")
                    continue

                best_match = None
                best_score = 0
                for t in tasks:
                    task_name = t["content"].lower()
                    common = len(set(task_name.split()) & set(target_phrase.lower().split()))
                    if common > best_score:
                        best_score = common
                        best_match = t

                if not best_match or best_score == 0:
                    print(f"Assistant: I couldn't find a task matching '{target_phrase}'.")
                    continue

                target_id = best_match["id"]
                if todoist_delete_task(target_id):
                    print(f"Assistant: Deleted task '{best_match['content']}'.")
                    memory["tasks_added"] = [
                        t for t in memory["tasks_added"] if t["id"] != target_id
                    ]
                    save_memory(memory)
                else:
                    print(f"Assistant: Could not delete '{best_match['content']}'.")
            except Exception as e:
                print("Assistant: Error deleting task:", e)
            continue

        # -----------------------------------------------------------
        # DEFAULT CHAT
        # -----------------------------------------------------------
        gemini_reply = call_gemini_with_history(user_text)
        print("Assistant:", gemini_reply)
        conversation_history.append({"role": "assistant", "content": gemini_reply})
        memory["conversation"] = conversation_history
        save_memory(memory)

if __name__ == "__main__":
    main_loop()
