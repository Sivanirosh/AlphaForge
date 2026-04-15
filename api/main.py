"""FastAPI application factory with lifespan-managed DB initialisation."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routers import health, metrics
from db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialise DB tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="AlphaForge",
    description="Equity metrics pipeline: log returns, volatility, Fama-French beta",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(metrics.router)
