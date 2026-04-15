"""Pydantic request/response models — single source of truth for API I/O."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class PriceResponse(BaseModel):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

    model_config = {"from_attributes": True}


class MetricResponse(BaseModel):
    ticker: str
    date: date
    log_return: float | None = None
    rolling_vol: float | None = None
    sharpe_ratio: float | None = None

    model_config = {"from_attributes": True}


class BetaResponse(BaseModel):
    ticker: str
    computed_at: datetime
    window: int
    market_beta: float
    smb_beta: float | None = None
    hml_beta: float | None = None
    r_squared: float

    model_config = {"from_attributes": True}


class VolatilityPoint(BaseModel):
    date: date
    rolling_vol: float | None = None


class VolatilityResponse(BaseModel):
    ticker: str
    window: int
    series: list[VolatilityPoint]
