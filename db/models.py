"""SQLAlchemy ORM table definitions for AlphaForge."""

from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("ticker", "date", name="uq_price_ticker_date"),)

    def __repr__(self) -> str:
        return f"<Price {self.ticker} {self.date}>"


class Factor(Base):
    __tablename__ = "factors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    mkt_rf = Column(Float, nullable=False)
    smb = Column(Float, nullable=False)
    hml = Column(Float, nullable=False)
    rf = Column(Float, nullable=False)

    def __repr__(self) -> str:
        return f"<Factor {self.date}>"


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    log_return = Column(Float)
    rolling_vol = Column(Float)
    sharpe_ratio = Column(Float)

    __table_args__ = (UniqueConstraint("ticker", "date", name="uq_metric_ticker_date"),)

    def __repr__(self) -> str:
        return f"<Metric {self.ticker} {self.date}>"


class BetaDecomposition(Base):
    __tablename__ = "beta_decompositions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    computed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    window = Column(Integer, nullable=False)
    market_beta = Column(Float, nullable=False)
    smb_beta = Column(Float)
    hml_beta = Column(Float)
    r_squared = Column(Float, nullable=False)

    def __repr__(self) -> str:
        return f"<BetaDecomposition {self.ticker} window={self.window}>"
