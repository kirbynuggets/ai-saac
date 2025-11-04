# Conversational AI Agent using LangChain and Gemini

A modular conversational assistant that combines large language models with real-world API integration for intelligent, context-aware dialogue.  
Built with **LangChain**, **Gemini**, and external APIs like **Todoist** and **Weather (wttr.in)**, the system demonstrates how NLP techniques such as intent recognition, dialogue management, and conditional reasoning converge into a functional AI agent.

---

## 🧭 Overview

This project implements a **multi-domain conversational system** capable of open-ended dialogue and task-oriented reasoning.  
It integrates a lightweight intent recognition mechanism with a modular action framework, enabling the agent to perform tasks such as managing to-do lists, checking weather, and handling conditional actions through natural language.

The architecture emphasizes the synergy between **rule-based NLP** and **LLM-driven semantic understanding**, showcasing practical applications of tokenization, embeddings, and context modeling in conversational AI.

---

## ⚙️ Key Features

- **Modular Architecture** – Decoupled design separating core intelligence from domain modules.  
- **Intent Recognition and Routing** – Dynamic input classification directing queries to task, weather, or chat modules.  
- **Conditional Reasoning** – Supports natural decision logic such as *"Add jogging if it doesn't rain tomorrow."*  
- **Memory Management** – Persistent conversational history enabling context retention.  
- **Extensibility** – Plug-and-play framework for new modules like news, dictionary, or calendar integrations.

---

## 🧠 System Architecture

```
main.py → core/agent.py → [modules/todoist_module | modules/weather_module]
                    ↓
            core/utils (Gemini LLM)
                    ↓
            core/memory (Context)
```

The assistant acts as a routing system where:
- `main.py` handles user interaction,  
- `core/` governs intent detection and decision-making,  
- and `modules/` executes domain-specific actions.

---

## 🔬 Technical Implementation

- **Intent Recognition:** Regex-based detection for task and weather intents with LLM fallback for open conversation.  
- **Dialogue Management:** Context persistence via structured JSON memory.  
- **LLM Integration:** Gemini 2.0 through LangChain for reasoning and prompt management.  
- **External APIs:** Todoist REST API for task operations; wttr.in for real-time weather without authentication.

---

## 🧩 Requirements

- Python ≥ 3.8  
- LangChain, LangChain Google GenAI, Requests, python-dotenv  

### Installation

```bash
pip install -r requirements.txt
```

### Environment Setup

```
GEMINI_API_KEY=your_gemini_api_key
TODOIST_API_KEY=your_todoist_api_key
```

### Run the Assistant

```bash
python main.py
```

---

## 🗂 Project Structure

```
ai-assistant/
├── main.py                 # Entry point: conversational interface
├── core/                   # Decision logic, LLM connection, memory
│   ├── agent.py
│   ├── utils.py
│   └── memory.py
├── modules/                # Domain-specific skills
│   ├── todoist_module.py
│   └── weather_module.py
├── assistant_memory.json   # Stored dialogue context
└── .env                    # API credentials
```

---

## 📚 Research Relevance

This project illustrates the integration of theoretical NLP principles with practical AI agent development.  
It bridges token-level processing, semantic embeddings, and prompt-based reasoning through LangChain's orchestration of Gemini's LLM.  
By combining deterministic routing with probabilistic reasoning, the system exemplifies hybrid NLP design suited for multi-domain conversational agents.

---

## 🚀 Future Enhancements

* Dynamic plugin system for new domains (news, calendar, dictionary)
* Advanced semantic memory using vector embeddings
* Voice I/O pipeline for speech-based interaction
* Temporal expression parsing for natural date handling
* Automated evaluation for intent and response accuracy

---

## 🏛 Acknowledgments

Developed as part of the NLP Course Project under the Department of Computer Science,  
Indian Institute of Information Technology Guwahati.  
Built with open APIs from LangChain, Gemini, and Todoist.

---

## ⚖️ License

Licensed under the MIT License for educational and research purposes.
