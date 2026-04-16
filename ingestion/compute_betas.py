"""Compute Fama-French 3-factor betas for all tickers and store results.

Pulls prices and factors from PostgreSQL, runs OLS regression via
``models.beta.compute_ff3_beta``, and writes ``BetaDecomposition`` rows.

Safe to re-run — each invocation appends a new snapshot so historical
beta estimates are preserved.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import settings
from db.session import SessionLocal, init_db
from ingestion.compute_metrics import log_returns
from models.beta import compute_ff3_beta

logger = logging.getLogger(__name__)


def _load_prices(db: Session, ticker: str) -> pd.Series:
    """Load closing prices for *ticker* as a DatetimeIndex Series."""
    rows = db.execute(
        text("SELECT date, close FROM prices WHERE ticker = :t ORDER BY date"),
        {"t": ticker.upper()},
    ).fetchall()
    if not rows:
        return pd.Series(dtype=float)
    return pd.Series(
        [float(r[1]) for r in rows],
        index=pd.DatetimeIndex([r[0] for r in rows]),
        name="close",
    )


def _load_factors(db: Session) -> pd.DataFrame:
    """Load factor data as a DataFrame with Mkt-RF, SMB, HML, RF columns."""
    rows = db.execute(
        text("SELECT date, mkt_rf, smb, hml, rf FROM factors ORDER BY date"),
    ).fetchall()
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(
        [(r[1], r[2], r[3], r[4]) for r in rows],
        index=pd.DatetimeIndex([r[0] for r in rows]),
        columns=["Mkt-RF", "SMB", "HML", "RF"],
    )


def compute_and_store_betas(
    db: Session | None = None,
    tickers: list[str] | None = None,
) -> int:
    """Compute FF3 betas for each ticker and insert into beta_decompositions.

    Returns the total number of rows inserted.
    """
    own_session = db is None
    if own_session:
        db = SessionLocal()

    tickers = tickers or settings.ticker_list
    rows_inserted = 0

    try:
        factors_df = _load_factors(db)
        if factors_df.empty:
            logger.warning("No factor data — run fetch_factors first.")
            return 0

        for ticker in tickers:
            prices = _load_prices(db, ticker)
            if len(prices) < 30:
                logger.warning("Not enough price data for %s (%d rows)", ticker, len(prices))
                continue

            lr = log_returns(prices).dropna()
            aligned = pd.concat([lr.rename("ret"), factors_df["RF"]], axis=1, sort=False).dropna()
            if aligned.empty:
                logger.warning("No overlapping dates for %s and factor data", ticker)
                continue

            excess = aligned["ret"] - aligned["RF"]
            result = compute_ff3_beta(excess, factors_df)

            if np.isnan(result.market_beta):
                logger.warning("Beta regression failed for %s", ticker)
                continue

            db.execute(
                text("""
                    INSERT INTO beta_decompositions
                        (ticker, computed_at, "window", market_beta, smb_beta, hml_beta, r_squared)
                    VALUES
                        (:ticker, :computed_at, :window, :market_beta, :smb_beta, :hml_beta, :r_squared)
                """),
                {
                    "ticker": ticker.upper(),
                    "computed_at": datetime.now(UTC),
                    "window": result.rolling_window or len(excess),
                    "market_beta": result.market_beta,
                    "smb_beta": result.smb_beta,
                    "hml_beta": result.hml_beta,
                    "r_squared": result.r_squared,
                },
            )
            rows_inserted += 1
            logger.info(
                "%s β_mkt=%.3f β_smb=%.3f β_hml=%.3f R²=%.3f",
                ticker,
                result.market_beta,
                result.smb_beta or 0,
                result.hml_beta or 0,
                result.r_squared,
            )

        db.commit()
    finally:
        if own_session:
            db.close()

    return rows_inserted


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    count = compute_and_store_betas()
    print(f"Done — {count} beta rows inserted.")
