from core.agent import detect_intent, route_intent
from core.memory import load_memory, save_memory

def main():
    print("Hey, how may I help you?")
    memory = load_memory()
    while True:
        user_text = input("\nYou: ").strip()
        if user_text.lower() in ["exit", "quit", "bye"]:
            print("Assistant: Goodbye! Take care.")
            break

        intent = detect_intent(user_text)
        response = route_intent(intent, user_text)

        print(f"Assistant: {response}")
        memory["conversation"].append({"user": user_text, "assistant": response})
        save_memory(memory)

if __name__ == "__main__":
    main()
