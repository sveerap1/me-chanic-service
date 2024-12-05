from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.llms.base import LLM
# from langchain_ollama import OllamaLLM
import requests
import os

llama3_api_url = os.environ.get('LLAMA3_API_URL')

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    context: list

user_contexts = {}

class Llama3LLM(LLM):
    def _call(self, prompt: str, stop=None) -> str:
        try:
            # llama3_api_url = "http://localhost:11434/api/generate"
            payload = {"prompt": prompt, "model": "llama3", "stream": False}
            response = requests.post(llama3_api_url, json=payload)
            response.raise_for_status()
            response_data = response.json()
            return response_data.get("response", "No response from model")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to connect to Llama3 API: {e}")

    @property
    def _identifying_params(self):
        return {}

    @property
    def _llm_type(self) -> str:
        return "llama3"

llm = Llama3LLM()
# llm = OllamaLLM(model="llama3")

prompt_template = ChatPromptTemplate.from_template("""
You are a helpful personal assistant for store employees. 
Here is the context of the conversation so far:
{context}

User: {message}
Assistant:""")

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_id = request.user_id
    message = request.message

    if user_id not in user_contexts:
        user_contexts[user_id] = ConversationBufferMemory(return_messages=True)

    memory = user_contexts[user_id]

    chain = prompt_template | llm

    try:
        context = memory.load_memory_variables({}).get("history", "")

        response_text = chain.invoke({"context": context, "message": message})

        memory.chat_memory.add_user_message(message)
        memory.chat_memory.add_ai_message(response_text)

        updated_context = memory.load_memory_variables({}).get("history", [])

        return ChatResponse(response=response_text, context=updated_context)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
