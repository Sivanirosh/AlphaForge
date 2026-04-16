# AlphaForge

An automated quantitative finance data pipeline that ingests daily equity prices and
Fama-French factor data, computes CFA-aligned metrics, serves them through a
production-ready REST API, and visualises everything in a React dashboard. Built to
demonstrate data engineering, financial modelling, and full-stack software craftsmanship
in a single deployable system.

---

## What It Does

1. **Ingests** daily OHLCV price data from the Alpaca Markets API and Fama-French
   3-factor data from the Ken French Data Library.
2. **Computes** log returns, rolling annualised volatility, Sharpe ratios, and
   Fama-French beta decompositions (market, size, value) via OLS regression.
3. **Persists** all data idempotently into PostgreSQL — safe to re-run at any time.
4. **Serves** all metrics through a FastAPI REST API with full Pydantic schema
   validation and auto-generated OpenAPI docs.
5. **Visualises** prices, volatility, and FF3 beta decompositions in a React + Recharts
   dashboard with a dark-themed, responsive UI.
6. **Schedules** daily ingestion automatically at market close using APScheduler —
   no manual intervention required.
7. **Tests** every numerical invariant with property-based tests (Hypothesis) and
   every endpoint with HTTP-level integration tests (httpx).
8. **Ships** as a fully containerised application via Docker Compose (API, frontend,
   scheduler, and PostgreSQL as four coordinated services).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data ingestion | Alpaca Markets API (`alpaca-py`), Ken French Data Library |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Metrics | pandas, NumPy, statsmodels (OLS) |
| API | FastAPI + Uvicorn |
| Validation | Pydantic v2 + pydantic-settings |
| Frontend | React 18 + TypeScript + Vite + Recharts |
| Data fetching | TanStack React Query + Axios |
| Scheduling | APScheduler 3.x (blocking, cron-based) |
| Containerisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Testing | pytest + Hypothesis (property-based) + httpx |
| Dependencies | uv + pyproject.toml (Python), npm (Node) |
| Linting | Ruff |

---

## Financial Concepts Implemented

This project implements the following **CFA Level 1 Quantitative Methods** concepts
directly in production code:

| CFA Concept | Implementation |
|---|---|
| Continuously compounded returns | `ingestion/compute_metrics.py:log_returns()` |
| Annualised volatility (√252 convention) | `ingestion/compute_metrics.py:rolling_volatility()` |
| Sharpe ratio | `ingestion/compute_metrics.py:sharpe_ratio()` |
| Realised variance | `ingestion/compute_metrics.py:realised_variance()` |
| CAPM market beta | `models/beta.py:compute_capm_beta()` |
| Fama-French 3-factor model | `models/beta.py:compute_ff3_beta()` |
| EWMA volatility | `models/volatility.py:rolling_ewma_vol()` |

All return calculations use **log returns only** — `pd.DataFrame.pct_change()` and
simple returns are explicitly prohibited throughout the codebase.

---

## API Endpoints

Once running, interactive docs are available at `http://localhost:8000/docs`
(or `GET /` which redirects there automatically).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `GET` | `/tickers` | List of all tickers with price data |
| `GET` | `/prices/{ticker}` | Full OHLCV price history |
| `GET` | `/metrics/{ticker}` | Latest log return, rolling vol, Sharpe ratio |
| `GET` | `/metrics/{ticker}/beta` | Fama-French 3-factor beta decomposition |
| `GET` | `/metrics/{ticker}/volatility` | Full rolling volatility time series |

---

## Architecture

![](imgs/Architecture_dgm_nanoBananaMade.png)

---

## Project Structure

```
AlphaForge/
├── config.py                    # Pydantic BaseSettings (reads .env)
├── pyproject.toml               # Python dependencies + tool config
├── Dockerfile                   # API / scheduler image
├── docker-compose.yml           # db, api, scheduler, frontend
│
├── ingestion/
│   ├── fetch_prices.py          # Alpaca → PostgreSQL + compute metrics
│   ├── fetch_factors.py         # Ken French FF3 → PostgreSQL
│   ├── compute_metrics.py       # Pure financial metric functions
│   ├── compute_betas.py         # FF3 beta regression → beta_decompositions
│   ├── scheduler.py             # APScheduler: daily prices/betas, weekly factors
│   ├── constants.py             # TRADING_DAYS_PER_YEAR = 252
│   └── utils.py                 # Retry decorator, rate limiter
│
├── db/
│   ├── models.py                # SQLAlchemy ORM (Price, Factor, Metric, Beta)
│   ├── session.py               # Engine + session factory + FastAPI dependency
│   ├── schema.sql               # Reference DDL
│   └── migrations/              # Numbered SQL migration files
│
├── models/
│   ├── beta.py                  # CAPM + FF3 OLS via statsmodels
│   └── volatility.py            # EWMA rolling volatility
│
├── api/
│   ├── main.py                  # FastAPI app + CORS + lifespan
│   ├── schemas.py               # Pydantic I/O models
│   ├── services.py              # Business logic layer
│   ├── dependencies.py          # DB session injection
│   └── routers/
│       ├── health.py
│       ├── metrics.py
│       └── prices.py            # /prices + /tickers endpoints
│
├── frontend/
│   ├── Dockerfile               # node:20 build → nginx:alpine serve
│   ├── nginx.conf               # Proxies /api/ to the FastAPI service
│   ├── vite.config.ts           # Dev proxy: /api → localhost:8000
│   ├── index.html
│   └── src/
│       ├── main.tsx             # React Query provider entry point
│       ├── App.tsx              # Root layout + ticker state
│       ├── api/client.ts        # Axios instance (baseURL: /api)
│       ├── hooks/useApi.ts      # React Query hooks for all endpoints
│       ├── types/index.ts       # TypeScript interfaces ↔ Pydantic schemas
│       └── components/
│           ├── Layout.tsx       # Header shell
│           ├── TickerSelector.tsx
│           ├── PriceChart.tsx   # Closing price area chart
│           ├── VolatilityChart.tsx
│           ├── MetricsTable.tsx # Log return / Sharpe table
│           └── BetaPanel.tsx    # FF3 beta bar chart + R² badge
│
└── tests/
    ├── conftest.py              # SQLite fixtures, sample data, TestClient
    ├── test_metrics.py          # Hypothesis property-based tests
    └── test_api.py              # HTTP endpoint integration tests
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- A free [Alpaca Markets](https://app.alpaca.markets/signup) paper trading account
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Setup

```bash
git clone https://github.com/your-username/AlphaForge.git
cd AlphaForge

cp .env.example .env
# Edit .env and fill in your ALPACA_API_KEY and ALPACA_SECRET_KEY

uv sync --all-extras
```

### Run everything with Docker Compose

```bash
docker compose up -d
```

This starts four services:

| Service | URL | Description |
|---|---|---|
| `db` | — | PostgreSQL 16 |
| `api` | http://localhost:8000 | FastAPI + auto-redirect `/` → `/docs` |
| `frontend` | http://localhost:3000 | React dashboard (nginx) |
| `scheduler` | — | APScheduler (daily prices + betas, weekly factors) |

### Run locally (development)

```bash
# 1. Start PostgreSQL only
docker compose up -d db

# 2. Seed initial data
uv run python -m ingestion.fetch_factors          # FF3 factors (~10 seconds)
uv run python -m ingestion.fetch_prices           # Prices + compute metrics

# 3. Compute betas (requires factors + prices to be present)
uv run python -m ingestion.compute_betas

# 4. Start the API
uv run uvicorn api.main:app --reload              # http://localhost:8000

# 5. Start the frontend dev server (separate terminal)
cd frontend && npm run dev                        # http://localhost:5173
```

The Vite dev server proxies all `/api/*` requests to `localhost:8000`, so no
CORS configuration is needed during development.

### Automated scheduling

```bash
# Run the scheduler in the foreground (blocks, runs jobs on cron schedule)
uv run python -m ingestion.scheduler
```

Jobs run in US/Eastern time:
- **Mon–Fri 17:00** — fetch prices and recompute metrics
- **Mon–Fri 17:30** — recompute FF3 betas
- **Sunday 18:00** — sync Fama-French factor data

### Run tests

```bash
uv run pytest tests/ -v
uv run pytest tests/ -v --hypothesis-seed=0   # Deterministic property tests
```

### Lint

```bash
uv run ruff check .
```

---

## Design Decisions

**Log returns, not simple returns.** All calculations use `np.log(P_t / P_{t-1})`.
This is consistent with CFA convention and makes multi-period returns additive.

**Idempotent ingestion.** Every `INSERT` uses `ON CONFLICT DO NOTHING`. Scripts can be
re-run at any time without data corruption.

**No logic in route handlers.** Every handler is a one-liner that calls a service
function. Business logic lives in `api/services.py` and `ingestion/compute_metrics.py`.

**Metrics computed at ingestion time.** `fetch_prices.py` calls `compute_and_store_metrics()`
immediately after committing price rows, so the `metrics` table is always fresh without
a separate manual step.

**Frontend proxied through nginx.** In production (Docker), nginx serves the built React
SPA and forwards `/api/*` requests to the FastAPI container — no CORS headers required
in production. In development, Vite's built-in proxy handles the same forwarding.

**Property-based testing.** Numerical invariants (log return additivity, non-negative
variance, Sharpe NaN on zero-volatility input) are tested with Hypothesis — generating
thousands of random inputs rather than fixed examples.

**Lazy database engine.** The SQLAlchemy engine is created on first use, not at import
time. This allows tests to inject a SQLite engine before any database connection is made.

**Free, stable data sources only.** Alpaca provides a documented, free paper-trading
API. The Ken French Data Library provides free factor data directly — no API key
required.

---

## CI/CD

GitHub Actions runs on every push to `main` and every pull request:

1. Installs dependencies via `uv sync`
2. Runs `ruff check .` (linting)
3. Runs `pytest tests/ -v` (22 tests)

---

## Roadmap

- [x] Automated ingestion scheduling (APScheduler — daily prices/betas, weekly factors)
- [x] React + Recharts frontend dashboard (prices, volatility, beta decomposition)
- [x] `/prices/{ticker}` and `/tickers` REST endpoints
- [ ] GARCH(1,1) volatility model (`models/volatility.py:garch_stub()`)
- [ ] Prometheus metrics endpoint for observability
- [ ] Portfolio-level Sharpe ratio and correlation matrix endpoint
- [ ] Date-range query parameter on `/prices/{ticker}` and `/metrics/{ticker}`
