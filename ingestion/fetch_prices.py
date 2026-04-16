"""Fetch daily OHLCV bars from Alpaca and upsert into PostgreSQL."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import settings
from db.session import SessionLocal, init_db

logger = logging.getLogger(__name__)


def _build_client() -> StockHistoricalDataClient:
    return StockHistoricalDataClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
    )


def fetch_and_store(
    tickers: list[str] | None = None,
    lookback_days: int = 365,
) -> int:
    """Fetch daily bars for *tickers* and insert into the prices table.

    Uses the IEX feed, which is available on Alpaca's free tier.
    Returns the number of rows inserted.
    """
    tickers = tickers or settings.ticker_list
    client = _build_client()

    end = datetime.now()
    start = end - timedelta(days=lookback_days)

    request = StockBarsRequest(
        symbol_or_symbols=tickers,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed.IEX,
    )

    bars = client.get_stock_bars(request)
    rows_inserted = 0

    db: Session = SessionLocal()
    try:
        for symbol in tickers:
            symbol_bars = bars[symbol]
            for bar in symbol_bars:
                result = db.execute(
                    text("""
                        INSERT INTO prices (ticker, date, open, high, low, close, volume)
                        VALUES (:ticker, :date, :open, :high, :low, :close, :volume)
                        ON CONFLICT (ticker, date) DO NOTHING
                    """),
                    {
                        "ticker": symbol,
                        "date": bar.timestamp.date(),
                        "open": float(bar.open),
                        "high": float(bar.high),
                        "low": float(bar.low),
                        "close": float(bar.close),
                        "volume": int(bar.volume),
                    },
                )
                rows_inserted += result.rowcount
        db.commit()
        logger.info("Inserted %d price rows for %s", rows_inserted, tickers)

        from api.services import compute_and_store_metrics

        for symbol in tickers:
            metric_count = compute_and_store_metrics(db, symbol)
            logger.info("Computed %d metric rows for %s", metric_count, symbol)
    finally:
        db.close()

    return rows_inserted


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    count = fetch_and_store()
    print(f"Done — {count} rows inserted.")
