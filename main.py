from dotenv import load_dotenv
from langchain.messages import HumanMessage, AIMessage
from langchain.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic_core.core_schema import model_field

import os
load_dotenv()

todoist_api_key = os.getenv("TODOIST_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.5-flash',
    google_api_key = gemini_api_key,
    temperature = 0.3
)

system_prompt = "You are helpful assisstant. You will help the user add tasks."
#user_input = "What day is it today?"
prompt = ChatPromptTemplate([
    ("system", system_prompt),
    ("user", user_input)
])

chain =prompt | llm | StrOutputParser()
print(chain)

#chain.invoke("input": user_input)