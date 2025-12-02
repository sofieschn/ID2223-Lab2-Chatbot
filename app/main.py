from __future__ import annotations

from typing import List, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Allow importing chatbot.py from the project root
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from chatbot import LLM_model  # type: ignore

app = FastAPI(title="ID2223 Local LLaMA Chatbot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: List[HistoryItem] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    history: List[HistoryItem]


# Single shared model instance (keeps its own history_str)
llm = LLM_model(
    model_path="models/Llama-3.2-1B-Instruct-Q4_1.gguf",
    lora_path="models/lora_adapter_q8_0.gguf",
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # Let the LLaMA model handle conversational history via its internal history_str
    answer = llm.chat_fn(request.message)

    updated_history = request.history + [
        HistoryItem(role="user", content=request.message),
        HistoryItem(role="assistant", content=answer),
    ]

    return ChatResponse(answer=answer, history=updated_history)

