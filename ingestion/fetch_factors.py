"""Fetch Fama-French 3-factor daily data and upsert into PostgreSQL.

Downloads directly from the Ken French Data Library via HTTPS, bypassing
pandas-datareader which is broken on Python 3.12 (distutils removal).
"""

from __future__ import annotations

import argparse
import io
import logging
import zipfile
from datetime import date, timedelta

import pandas as pd
import requests
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.session import SessionLocal, init_db

logger = logging.getLogger(__name__)

FF3_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Research_Data_Factors_daily_CSV.zip"
)


def _download_ff3() -> pd.DataFrame:
    """Download and parse the FF3 daily CSV from the Ken French Data Library.

    Returns a DataFrame with columns: Mkt-RF, SMB, HML, RF (as decimals).
    Index is a DatetimeIndex.
    """
    resp = requests.get(FF3_URL, timeout=30)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        csv_name = next(n for n in zf.namelist() if n.endswith(".CSV") or n.endswith(".csv"))
        with zf.open(csv_name) as f:
            raw = f.read().decode("utf-8", errors="replace")

    lines = raw.splitlines()

    # Find the header line (contains "Mkt-RF")
    header_idx = next(i for i, line in enumerate(lines) if "Mkt-RF" in line)
    # Find the end of the daily data (blank line or non-date line after header)
    data_lines = []
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped:
            break
        # Annual summary section starts with a 4-digit year only — stop there
        first_token = stripped.split(",")[0].strip()
        if len(first_token) == 4 and first_token.isdigit():
            break
        data_lines.append(stripped)

    csv_block = "Date,Mkt-RF,SMB,HML,RF\n" + "\n".join(data_lines)
    df = pd.read_csv(io.StringIO(csv_block), index_col=0)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df / 100.0  # values are in percent — convert to decimal
    return df


def _most_recent_factor_date(db: Session) -> date | None:
    """Return the latest date in the factors table, or None if empty."""
    return db.execute(text("SELECT MAX(date) FROM factors")).scalar()


def fetch_and_store(force: bool = False) -> int:
    """Download FF3 daily factors and upsert into the factors table.

    If *force* is False and the most recent stored date is within the last
    7 days, the download is skipped (factors update infrequently).

    Returns the number of rows inserted.
    """
    db: Session = SessionLocal()
    try:
        if not force:
            latest = _most_recent_factor_date(db)
            if latest and (date.today() - latest) < timedelta(days=7):
                logger.info("Factor data is fresh (last: %s) — skipping.", latest)
                return 0

        logger.info("Downloading FF3 daily factors from Ken French Data Library…")
        df = _download_ff3()

        rows_inserted = 0
        for dt, row in df.iterrows():
            result = db.execute(
                text("""
                    INSERT INTO factors (date, mkt_rf, smb, hml, rf)
                    VALUES (:date, :mkt_rf, :smb, :hml, :rf)
                    ON CONFLICT (date) DO NOTHING
                """),
                {
                    "date": dt.date(),
                    "mkt_rf": float(row["Mkt-RF"]),
                    "smb": float(row["SMB"]),
                    "hml": float(row["HML"]),
                    "rf": float(row["RF"]),
                },
            )
            rows_inserted += result.rowcount

        db.commit()
        logger.info("Inserted %d factor rows.", rows_inserted)
        return rows_inserted
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Fetch Fama-French 3-factor data")
    parser.add_argument("--force", action="store_true", help="Bypass recency check")
    args = parser.parse_args()

    init_db()
    count = fetch_and_store(force=args.force)
    print(f"Done — {count} factor rows inserted.")
