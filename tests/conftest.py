"""Shared test fixtures: in-memory SQLite DB, sample data, and HTTP client."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from db.models import Base, Metric, Price

SQLITE_URL = "sqlite://"


@pytest.fixture()
def db_engine():
    """Create a fresh in-memory SQLite engine shared across connections."""
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Generator[Session, Any, None]:
    """Provide a transactional DB session that rolls back after each test."""
    testing_session = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_engine) -> Generator[TestClient, Any, None]:
    """FastAPI TestClient with the DB dependency overridden to use SQLite."""
    import db.session as db_session_module

    original_engine = db_session_module._engine
    original_factory = db_session_module._session_factory

    testing_session_factory = sessionmaker(
        bind=db_engine, autocommit=False, autoflush=False
    )
    db_session_module._engine = db_engine
    db_session_module._session_factory = testing_session_factory

    from api.dependencies import get_db
    from api.main import app

    def _override_get_db() -> Generator[Session, Any, None]:
        session = testing_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

    db_session_module._engine = original_engine
    db_session_module._session_factory = original_factory


@pytest.fixture()
def sample_prices() -> pd.DataFrame:
    """Synthetic price DataFrame with 252 rows (one trading year)."""
    np.random.seed(42)
    n = 252
    dates = pd.bdate_range(start="2024-01-02", periods=n)
    base_price = 150.0
    daily_returns = np.random.normal(0.0005, 0.02, n)
    prices = base_price * np.exp(np.cumsum(daily_returns))

    return pd.DataFrame(
        {
            "date": dates,
            "open": prices * np.random.uniform(0.99, 1.01, n),
            "high": prices * np.random.uniform(1.00, 1.03, n),
            "low": prices * np.random.uniform(0.97, 1.00, n),
            "close": prices,
            "volume": np.random.randint(1_000_000, 10_000_000, n),
        }
    )


@pytest.fixture()
def seeded_db(db_engine, sample_prices: pd.DataFrame) -> Session:
    """DB session pre-loaded with sample price and metric data for AAPL."""
    import db.session as db_session_module

    db_session_module._engine = db_engine
    db_session_module._session_factory = sessionmaker(
        bind=db_engine, autocommit=False, autoflush=False
    )

    testing_session = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = testing_session()

    for _, row in sample_prices.iterrows():
        session.add(
            Price(
                ticker="AAPL",
                date=row["date"].date(),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=int(row["volume"]),
            )
        )
    session.commit()

    log_rets = np.log(sample_prices["close"] / sample_prices["close"].shift(1))
    for i, (_, row) in enumerate(sample_prices.iterrows()):
        lr = float(log_rets.iloc[i]) if not np.isnan(log_rets.iloc[i]) else None
        session.add(
            Metric(
                ticker="AAPL",
                date=row["date"].date(),
                log_return=lr,
            )
        )
    session.commit()
    return session
