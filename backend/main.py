from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    user_input: str

@app.post("/chat")
def chat_with_agent(message: Message):
    reply = run_agent(message.user_input)
    return { "reply": reply }
