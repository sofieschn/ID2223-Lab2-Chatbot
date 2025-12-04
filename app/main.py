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
        # Local GGUF backend using chatbot.LLM_model.
        # We explicitly disable history here (save_hist=False) to match the
        # fast, stateless behavior used in Test.ipynb.
        from chatbot import LLM_model as LocalModel  # type: ignore

        model_path = os.path.join(ROOT_DIR, "models", "Llama-3.2-1B-Instruct-Q4_1.gguf")
        lora_path = os.path.join(ROOT_DIR, "models", "lora_adapter_q8_0.gguf")

        return LocalModel(model_path=model_path, lora_path=lora_path, save_hist=False)


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


def _build_last_turn_prompt(system_prompt: str, history: List[HistoryItem], message: str) -> str:
    """
    Build a minimal prompt that only includes the *last* user/assistant pair
    plus the latest user message.

    This keeps some conversational context without letting the prompt grow
    unbounded and become very slow.
    """
    prompt = system_prompt

    # history sent from the frontend already includes the latest user message,
    # so we look at everything *before* that for previous turns
    prior = history[:-1] if history else []

    # Find last assistant and the user immediately before it (if any)
    last_assistant_idx = None
    for i in range(len(prior) - 1, -1, -1):
        if prior[i].role == "assistant":
            last_assistant_idx = i
            break

    if last_assistant_idx is not None:
        # Find the closest preceding user message
        last_user_idx = None
        for j in range(last_assistant_idx - 1, -1, -1):
            if prior[j].role == "user":
                last_user_idx = j
                break

        if last_user_idx is not None:
            prompt += f"User: {prior[last_user_idx].content}\n"
        prompt += f"Assistant: {prior[last_assistant_idx].content}\n"

    # Always append the latest user message (the one from the current request)
    prompt += f"User: {message}\nAssistant: "
    return prompt


# Single shared model instance
llm = create_llm()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    backend = os.getenv("LLM_BACKEND", "local").lower()

    # For the HF backend we keep prompts short by only including the last
    # user/assistant pair plus the latest user message, and we bypass any
    # internal history the model wrapper might keep.
    if backend == "hf" and hasattr(llm, "llm"):
        # Import here to avoid circular imports at module load time
        from chatbot_hf import LLM_model as HFModel  # type: ignore

        if isinstance(llm, HFModel):
            system_prompt = llm._system_prompt  # type: ignore[attr-defined]
            prompt = _build_last_turn_prompt(system_prompt, request.history, request.message)
            output = llm.llm(  # type: ignore[attr-defined]
                prompt,
                max_tokens=64,
                temperature=0.7,
                stop=["User:", "Assistant:"],
            )
            answer = output["choices"][0]["text"].strip()
        else:
            # Fallback if types don't match for some reason
            answer = llm.chat_fn(request.message)
    else:
        # Local backend or any other implementation: let the model handle history
        answer = llm.chat_fn(request.message)

    updated_history = request.history + [
        HistoryItem(role="user", content=request.message),
        HistoryItem(role="assistant", content=answer),
    ]

    return ChatResponse(answer=answer, history=updated_history)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
