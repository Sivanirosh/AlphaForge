"""Service functions that encapsulate business logic for API handlers.

Route handlers call these — no business logic lives in the handlers themselves.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import settings
from db.models import BetaDecomposition, Metric, Price
from ingestion.compute_metrics import log_returns, rolling_volatility


def get_latest_metrics(db: Session, ticker: str) -> list[Metric]:
    """Return stored metrics for *ticker*, ordered by date descending."""
    return (
        db.query(Metric)
        .filter(Metric.ticker == ticker.upper())
        .order_by(Metric.date.desc())
        .limit(100)
        .all()
    )


def get_latest_beta(db: Session, ticker: str) -> BetaDecomposition | None:
    """Return the most recent beta decomposition for *ticker*."""
    return (
        db.query(BetaDecomposition)
        .filter(BetaDecomposition.ticker == ticker.upper())
        .order_by(BetaDecomposition.computed_at.desc())
        .first()
    )


def get_volatility_series(
    db: Session, ticker: str, window: int | None = None
) -> list[Metric]:
    """Return rolling volatility series for *ticker*."""
    window = window or settings.rolling_window
    return (
        db.query(Metric)
        .filter(Metric.ticker == ticker.upper(), Metric.rolling_vol.isnot(None))
        .order_by(Metric.date.asc())
        .all()
    )


def compute_and_store_metrics(db: Session, ticker: str) -> int:
    """Compute metrics from stored prices and persist them.

    Returns the number of metric rows upserted.
    """
    prices = (
        db.query(Price)
        .filter(Price.ticker == ticker.upper())
        .order_by(Price.date.asc())
        .all()
    )
    if not prices:
        return 0

    close_series = pd.Series(
        [p.close for p in prices],
        index=pd.DatetimeIndex([p.date for p in prices]),
        name="close",
    )

    log_rets = log_returns(close_series)
    roll_vol = rolling_volatility(log_rets, window=settings.rolling_window)

    rows_inserted = 0
    for i, price in enumerate(prices):
        lr = float(log_rets.iloc[i]) if not np.isnan(log_rets.iloc[i]) else None
        rv = float(roll_vol.iloc[i]) if not np.isnan(roll_vol.iloc[i]) else None

        result = db.execute(
            text("""
                INSERT INTO metrics (ticker, date, log_return, rolling_vol)
                VALUES (:ticker, :date, :log_return, :rolling_vol)
                ON CONFLICT (ticker, date) DO NOTHING
            """),
            {
                "ticker": ticker.upper(),
                "date": price.date,
                "log_return": lr,
                "rolling_vol": rv,
            },
        )
        rows_inserted += result.rowcount

    db.commit()
    return rows_inserted


def ticker_exists(db: Session, ticker: str) -> bool:
    """Check whether any price data exists for the given ticker."""
    return (
        db.query(Price).filter(Price.ticker == ticker.upper()).first() is not None
    )


def get_prices(db: Session, ticker: str) -> list[Price]:
    """Return OHLCV price history for *ticker*, oldest first."""
    return (
        db.query(Price)
        .filter(Price.ticker == ticker.upper())
        .order_by(Price.date.asc())
        .all()
    )


def list_tickers(db: Session) -> list[str]:
    """Return distinct tickers that have price data."""
    rows = db.execute(text("SELECT DISTINCT ticker FROM prices ORDER BY ticker")).fetchall()
    return [r[0] for r in rows]
