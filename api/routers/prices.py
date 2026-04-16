"""Price and ticker-list endpoints for the frontend dashboard."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import PriceResponse, TickerListResponse
from api.services import get_prices, list_tickers, ticker_exists

router = APIRouter(tags=["prices"])


@router.get("/tickers", response_model=TickerListResponse)
def read_tickers(db: Session = Depends(get_db)):
    """Return the list of tickers that have price data."""
    return TickerListResponse(tickers=list_tickers(db))


@router.get("/prices/{ticker}", response_model=list[PriceResponse])
def read_prices(ticker: str, db: Session = Depends(get_db)) -> list:
    """Return OHLCV price history for a ticker."""
    if not ticker_exists(db, ticker):
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    return get_prices(db, ticker)
