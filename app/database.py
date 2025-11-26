from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Iterable, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

DATABASE_URL = "sqlite:///./stocks.db"
engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)

FRESHNESS_WINDOW = timedelta(hours=6)


class StockSnapshot(SQLModel, table=True):
    ticker: str = Field(primary_key=True, index=True)
    name: Optional[str] = None
    price: float
    change_pct: float
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def is_stale(self) -> bool:
        return datetime.utcnow() - self.updated_at > FRESHNESS_WINDOW


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


class StockRepository:
    """Simple repository around SQLModel for stock snapshots."""

    def __init__(self) -> None:
        self._engine = engine

    def _session(self) -> Session:
        return Session(self._engine)

    def _get_sync(self, ticker: str) -> Optional[StockSnapshot]:
        with self._session() as session:
            return session.get(StockSnapshot, ticker)

    def _upsert_sync(self, snapshot: StockSnapshot) -> None:
        with self._session() as session:
            session.merge(snapshot)
            session.commit()

    def _bulk_upsert_sync(self, snapshots: Iterable[StockSnapshot]) -> None:
        with self._session() as session:
            for snapshot in snapshots:
                session.merge(snapshot)
            session.commit()

    def _all_sync(self) -> Dict[str, StockSnapshot]:
        with self._session() as session:
            results = session.exec(select(StockSnapshot)).all()
        return {item.ticker: item for item in results}

    async def get(self, ticker: str) -> Optional[StockSnapshot]:
        return await asyncio.to_thread(self._get_sync, ticker)

    async def upsert(self, snapshot: StockSnapshot) -> None:
        await asyncio.to_thread(self._upsert_sync, snapshot)

    async def bulk_upsert(self, snapshots: Iterable[StockSnapshot]) -> None:
        await asyncio.to_thread(self._bulk_upsert_sync, list(snapshots))

    async def dump_cache(self) -> Dict[str, StockSnapshot]:
        return await asyncio.to_thread(self._all_sync)

