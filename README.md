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
- `POST /chat` – expects `{ "message": \"...\", \"history\": [...] }` and returns the assistant answer plus updated history, powered by the local LLaMA model defined in `chatbot.py`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Access the UI at the URL printed by Vite (default http://localhost:5173). The chat box will forward user prompts to the FastAPI backend running on port `8000`, which in turn talks to the local model.
