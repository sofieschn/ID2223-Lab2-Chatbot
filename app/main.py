from __future__ import annotations

import asyncio
import logging
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import StockRepository, StockSnapshot, init_db
from services.alphavantage import Quote, fetch_quote

Ticker = str
app = FastAPI(title="ID2223 Stock Assistant API", version="0.1.0")
logger = logging.getLogger("uvicorn.error")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TICKER_REGEX = re.compile(r"\b[A-Z]{1,5}\b")
repo = StockRepository()


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: List[HistoryItem] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    history: List[HistoryItem]
    tickers: List[Ticker]
    stocks: Dict[Ticker, Dict[str, Any]]


def extract_tickers(text: str) -> List[Ticker]:
    """Very small helper until we replace it with an LLM routine."""
    tickers = []
    for match in TICKER_REGEX.findall(text.upper()):
        if match not in tickers:
            tickers.append(match)
    return tickers


async def fetch_stock_snapshot(ticker: Ticker) -> StockSnapshot | None:
    """Retrieve a snapshot, returning None if the ticker cannot be resolved."""
    quote: Quote | None = await fetch_quote(ticker)
    if quote:
        return StockSnapshot(
            ticker=quote.ticker,
            name=None,
            price=quote.price,
            change_pct=quote.change_pct,
            updated_at=quote.as_of,
        )

    logger.warning("No quote data for %s; skipping snapshot.", ticker)
    return None


def build_answer(prompt: str, stock_data: Dict[Ticker, Dict[str, Any]]) -> str:
    if not stock_data:
        return (
            "I could not match any tickers yet, but feel free to ask about company "
            "symbols (e.g., AAPL, MSFT) and I will try to look them up."
        )

    lines = ["Here is what I found:"]
    for ticker, snapshot in stock_data.items():
        price = snapshot.get("price")
        change_pct = snapshot.get("change_pct")
        lines.append(f"- {ticker}: ${price} ({change_pct}% daily move)")

    lines.append(
        "\nThis is an auto-generated summary. Always double-check before trading."
    )
    return "\n".join(lines)



@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    tickers = extract_tickers(request.message)
    stocks: Dict[Ticker, Dict[str, Any]] = {}

    for ticker in tickers:
        snapshot = await repo.get(ticker)
        if snapshot is None or snapshot.is_stale():
            snapshot = await fetch_stock_snapshot(ticker)
            if snapshot:
                await repo.upsert(snapshot)
        if snapshot:
            stocks[ticker] = snapshot.model_dump()

    assistant_message = build_answer(request.message, stocks)

    updated_history = request.history + [
        HistoryItem(role="user", content=request.message),
        HistoryItem(role="assistant", content=assistant_message),
    ]

    return ChatResponse(
        answer=assistant_message,
        history=updated_history,
        tickers=tickers,
        stocks=stocks,
    )

