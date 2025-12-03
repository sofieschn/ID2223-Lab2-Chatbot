from __future__ import annotations

from typing import List, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import os
import sys

# Allow importing chatbot.py / chatbot-hf.py from the project root
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)


def create_llm():
    """
    Factory for the LLM model.

    Use env var LLM_BACKEND to switch:
      - "local" (default)  -> chatbot.LLM_model (lokala .gguf-filer)
      - "hf"               -> chatbot-hf.LLM_model (laddar från Hugging Face)
    """
    backend = os.getenv("LLM_BACKEND", "local").lower()
    if backend == "hf":
        from chatbot_hf import LLM_model as HFModel  # type: ignore

        return HFModel()
    else:
        from chatbot import LLM_model as LocalModel  # type: ignore

        return LocalModel()


app = FastAPI(title="ID2223 LLaMA Chatbot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # Allow all origins for this course project so both local and KTH Cloud frontends work
    allow_origins=["*"],
    allow_credentials=False,
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
llm = create_llm()


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


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
