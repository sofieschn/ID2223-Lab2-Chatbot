# ID2223-Lab2-Chatbot

Local LLaMA chatbot with a React frontend and FastAPI backend.

## Getting Started

### Backend

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API exposes:
- `GET /health` – quick status check.
- `POST /chat` – expects `{ "message": \"...\", \"history\": [...] }` and returns the assistant answer plus updated history, powered by the LLaMA model.

#### Choosing model backend

The FastAPI backend can use either:

- A **local GGUF model** from the `models/` folder (`chatbot.py`), or
- A **Hugging Face–hosted model** from `SofieSchn/kth-llama-lora` (`chatbot-hf.py`).

This is controlled via the `LLM_BACKEND` environment variable:

```bash
# Local GGUF (default)
export LLM_BACKEND=local

# Hugging Face (requires a valid token if the repo is private (this one is public tho))
export LLM_BACKEND=hf
export HUGGINGFACE_HUB_TOKEN=hf_...your_token...
```

Then start the backend as usual:

```bash
cd app
source .venv/bin/activate
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Access the UI at the URL printed by Vite (default http://localhost:5173). The chat box will forward user prompts to the FastAPI backend running on port `8000`, which in turn talks to the local model.
