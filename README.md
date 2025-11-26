# ID2223-Lab2-Chatbot

Simple stock-education chatbot with a React frontend and FastAPI backend.

## Getting Started

### Backend

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Set the Alpha Vantage API key before starting the server (e.g. in `.env` or your shell):

```bash
export ALPHAVANTAGE_API_KEY=your_key_here
```

The API exposes:
- `GET /health` – quick status check.
- `POST /chat` – expects `{ "message": "...", "history": [...] }` and returns the assistant answer plus extracted tickers and mocked stock data.

> A local SQLite file (`stocks.db`) is created automatically the first time the app starts. It currently stores cached ticker snapshots so repeated queries reuse the same data instead of hitting the external API every time. You can inspect it with any SQLite viewer if needed.

#### Seeding popular tickers

To pre-populate the cache with the current top gainers/losers from Alpha Vantage:

```bash
cd app
python -m jobs.seed_top_movers
```

This script calls the `TOP_GAINERS_LOSERS` endpoint, then upserts the returned tickers into `stocks.db`. Run it manually whenever you want to refresh the trending universe (later it can be scheduled via cron/GitHub Actions).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Access the UI at the URL printed by Vite (default http://localhost:5173). The chat box will forward user prompts to the FastAPI backend running on port `8000`.
