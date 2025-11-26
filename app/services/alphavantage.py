from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY") or os.getenv("ALPAVANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"


@dataclass
class Quote:
    ticker: str
    price: float
    change_pct: float
    as_of: datetime
    name: Optional[str] = None


@dataclass
class Mover:
    ticker: str
    price: float
    change_pct: float
    as_of: datetime
    name: Optional[str] = None


async def _fetch_global_quote(symbol: str) -> Optional[dict]:
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    logger.info("Requesting Alpha Vantage global quote for %s", symbol)
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
    logger.debug("Alpha Vantage raw response for %s: %s", symbol, data)

    if "Note" in data:
        logger.warning("Alpha Vantage note for %s: %s", symbol, data["Note"])
        return None

    if "Error Message" in data:
        logger.warning(
            "Alpha Vantage error for %s: %s | Raw: %s", symbol, data["Error Message"], data
        )
        return None

    return data


def _parse_quote(symbol: str, payload: dict) -> Optional[Quote]:
    quoted = payload.get("Global Quote")
    if not quoted:
        return None

    try:
        price = float(quoted["05. price"])
    except (KeyError, ValueError):
        return None

    change_pct_str = quoted.get("10. change percent", "0%").replace("%", "")
    try:
        change_pct = float(change_pct_str)
    except ValueError:
        change_pct = 0.0

    as_of = datetime.utcnow()

    return Quote(
        ticker=symbol.upper(),
        price=round(price, 2),
        change_pct=round(change_pct, 2),
        as_of=as_of,
    )


async def fetch_quote(symbol: str) -> Optional[Quote]:
    if not ALPHAVANTAGE_API_KEY:
        logger.warning("ALPHAVANTAGE_API_KEY missing; falling back to mocked data.")
        return None

    try:
        payload = await _fetch_global_quote(symbol)
    except httpx.HTTPError as exc:
        logger.error("Network error when contacting Alpha Vantage: %s", exc)
        return None

    if not payload:
        return None

    return _parse_quote(symbol, payload)


async def fetch_top_movers(limit: int = 500) -> List[Mover]:
    if not ALPHAVANTAGE_API_KEY:
        logger.warning("ALPHAVANTAGE_API_KEY missing; cannot fetch top movers.")
        return []

    params = {"function": "TOP_GAINERS_LOSERS", "apikey": ALPHAVANTAGE_API_KEY}
    logger.info("Requesting Alpha Vantage TOP_GAINERS_LOSERS")
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
    logger.debug("Alpha Vantage TOP_GAINERS_LOSERS raw response: %s", data)

    if "Note" in data:
        logger.warning("Alpha Vantage note: %s", data["Note"])
        return []

    gainers = data.get("top_gainers", [])
    losers = data.get("top_losers", [])
    combined = gainers + losers

    movers: List[Mover] = []
    seen: set[str] = set()

    for entry in combined:
        ticker = entry.get("ticker")
        if not ticker or ticker in seen:
            continue
        seen.add(ticker)

        try:
            price = float(entry.get("price", 0))
        except ValueError:
            continue

        change_pct_str = entry.get("change_percentage", "0%").replace("%", "")
        try:
            change_pct = float(change_pct_str)
        except ValueError:
            change_pct = 0.0

        movers.append(
            Mover(
                ticker=ticker.upper(),
                price=round(price, 2),
                change_pct=round(change_pct, 2),
                name=entry.get("ticker_name"),
                as_of=datetime.utcnow(),
            )
        )

        if len(movers) >= limit:
            break

    return movers

