"""Metrics endpoints: returns, volatility, and beta decomposition."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import BetaResponse, MetricResponse, VolatilityPoint, VolatilityResponse
from api.services import get_latest_beta, get_latest_metrics, get_volatility_series, ticker_exists
from config import settings

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/{ticker}", response_model=list[MetricResponse])
def read_metrics(ticker: str, db: Session = Depends(get_db)) -> list:
    """Return the latest computed metrics for a ticker."""
    if not ticker_exists(db, ticker):
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return get_latest_metrics(db, ticker)


@router.get("/{ticker}/beta", response_model=BetaResponse)
def read_beta(ticker: str, db: Session = Depends(get_db)):
    """Return the most recent FF3 beta decomposition for a ticker."""
    if not ticker_exists(db, ticker):
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    beta = get_latest_beta(db, ticker)
    if beta is None:
        raise HTTPException(status_code=404, detail=f"No beta data for '{ticker}'")
    return beta


@router.get("/{ticker}/volatility", response_model=VolatilityResponse)
def read_volatility(ticker: str, db: Session = Depends(get_db)):
    """Return the rolling volatility series for a ticker."""
    if not ticker_exists(db, ticker):
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    rows = get_volatility_series(db, ticker)
    return VolatilityResponse(
        ticker=ticker.upper(),
        window=settings.rolling_window,
        series=[VolatilityPoint(date=m.date, rolling_vol=m.rolling_vol) for m in rows],
    )
