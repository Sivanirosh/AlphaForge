"""FastAPI application factory with lifespan-managed DB initialisation."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.routers import health, metrics, prices
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(prices.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
