This file explains the structure of the project and its codebase. 

ID2223-Lab2-Chatbot/
│
├── README.md
├── requirements.txt
│
├── app/                          # Python backend
│   ├── __init__.py
│   ├── api.py                    # FastAPI backend (POST /chat)
│   ├── models.py                 # Load finetuned LLM model
│   ├── orchestrator.py           # chat_with_debug + prompting pipeline
│   ├── intent.py                 # detect tickers and user intent
│   ├── context_builder.py        # build prompt with system message + data
│   │
│   ├── mcp_tools/                # Tool layer (Yahoo Finance API)
│   │   ├── __init__.py
│   │   └── stocks_tools.py       # get_stock_snapshot(), compare_two_stocks(), ...
│
          


# ID2223 Lab 2 – Educational Stock Chatbot

This project is my lab 2 chatbot for ID2223. It uses a finetuned Llama-based model
and an MCP-style tool layer to fetch stock market data and provide educational
explanations about stocks and basic investing concepts. It **does not** give
personal financial advice.

## Structure

- `app/models.py` – loads the finetuned model from Hugging Face.
- `app/intent.py` – detects tickers and user intent (compare, snapshot, etc.).
- `app/mcp_tools/stocks_tools.py` – "tool" layer using Yahoo Finance (`yfinance`).
- `app/context_builder.py` – builds the prompt with system message, disclaimers,
  external context and chat history.
- `app/orchestrator.py` – main chat pipeline (intent → tools → prompt → model).
- `app/main.py` – Gradio UI entrypoint.

## Running locally

```bash
pip install -r requirements.txt
python -m app.main
