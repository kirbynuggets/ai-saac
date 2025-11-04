import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY, temperature=0.3
)

def call_gemini(system_prompt: str, user_message: str):
    """Send a message to Gemini and get a string response."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": user_message})