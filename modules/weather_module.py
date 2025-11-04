import re, requests

def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=j1"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        temp = data["current_condition"][0]["temp_C"]
        return f"In {city}, it's {desc.lower()} and around {temp}°C."
    except Exception:
        return f"Couldn't get weather info for {city}."

def handle_weather_intent(user_text):
    m = re.search(r"in\s+([A-Za-z\s]+)", user_text)
    city = m.group(1).strip() if m else "Delhi"
    report = get_weather(city)
    if re.search(r"\b(add|create)\b", user_text, re.I) and re.search(r"\bif\b", user_text, re.I):
        # Example: "add jogging if it doesn't rain tomorrow"
        if "rain" not in report.lower():
            return f"It doesn’t seem rainy — you can go ahead with your plan. ({report})"
        else:
            return f"It might rain — maybe reschedule. ({report})"
    return report
