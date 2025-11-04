import re
from core.utils import call_gemini
from modules.todoist_module import handle_todo_intent
from modules.weather_module import handle_weather_intent

def detect_intent(text: str):
    """Classify the user's intent."""
    if re.search(r"\b(add|create|delete|remove|list|show|task|todo)\b", text, re.I):
        return "todo"
    if re.search(r"\b(weather|rain|temperature|forecast|sunny|cloudy)\b", text, re.I):
        return "weather"
    return "chat"

def route_intent(intent, user_text):
    """Route user input to appropriate handler."""
    if intent == "todo":
        return handle_todo_intent(user_text)
    elif intent == "weather":
        return handle_weather_intent(user_text)
    else:
        # General conversation
        return call_gemini("You are a friendly, conversational assistant.", user_text)
