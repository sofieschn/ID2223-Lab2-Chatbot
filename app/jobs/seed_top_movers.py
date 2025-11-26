from __future__ import annotations

import asyncio
from typing import List

from database import StockRepository, StockSnapshot, init_db
from services.alphavantage import Mover, fetch_top_movers


async def seed_top_movers(limit: int = 500) -> None:
    init_db()
    repo = StockRepository()
    movers: List[Mover] = await fetch_top_movers(limit=limit)
    if not movers:
        print("No movers returned from Alpha Vantage.")
        return

    snapshots = [
        StockSnapshot(
            ticker=mover.ticker,
            name=mover.name,
            price=mover.price,
            change_pct=mover.change_pct,
            updated_at=mover.as_of,
        )
        for mover in movers
    ]

    await repo.bulk_upsert(snapshots)
    print(f"Upserted {len(snapshots)} tickers from Alpha Vantage top movers.")


def main() -> None:
    asyncio.run(seed_top_movers())


if __name__ == "__main__":
    main()

