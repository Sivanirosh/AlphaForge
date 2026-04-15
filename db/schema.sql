-- Reference DDL for AlphaForge — DO NOT EDIT after initial setup.
-- Actual table creation is handled by SQLAlchemy ORM (db/models.py).
-- Subsequent changes go in db/migrations/ as numbered SQL files.

CREATE TABLE IF NOT EXISTS prices (
    id          SERIAL PRIMARY KEY,
    ticker      VARCHAR(10)  NOT NULL,
    date        DATE         NOT NULL,
    open        DOUBLE PRECISION NOT NULL,
    high        DOUBLE PRECISION NOT NULL,
    low         DOUBLE PRECISION NOT NULL,
    close       DOUBLE PRECISION NOT NULL,
    volume      INTEGER      NOT NULL,
    UNIQUE (ticker, date)
);

CREATE INDEX IF NOT EXISTS idx_prices_ticker ON prices (ticker);
CREATE INDEX IF NOT EXISTS idx_prices_date   ON prices (date);

CREATE TABLE IF NOT EXISTS factors (
    id      SERIAL PRIMARY KEY,
    date    DATE             NOT NULL UNIQUE,
    mkt_rf  DOUBLE PRECISION NOT NULL,
    smb     DOUBLE PRECISION NOT NULL,
    hml     DOUBLE PRECISION NOT NULL,
    rf      DOUBLE PRECISION NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_factors_date ON factors (date);

CREATE TABLE IF NOT EXISTS metrics (
    id           SERIAL PRIMARY KEY,
    ticker       VARCHAR(10)  NOT NULL,
    date         DATE         NOT NULL,
    log_return   DOUBLE PRECISION,
    rolling_vol  DOUBLE PRECISION,
    sharpe_ratio DOUBLE PRECISION,
    UNIQUE (ticker, date)
);

CREATE INDEX IF NOT EXISTS idx_metrics_ticker ON metrics (ticker);
CREATE INDEX IF NOT EXISTS idx_metrics_date   ON metrics (date);

CREATE TABLE IF NOT EXISTS beta_decompositions (
    id          SERIAL PRIMARY KEY,
    ticker      VARCHAR(10)      NOT NULL,
    computed_at TIMESTAMP        NOT NULL DEFAULT NOW(),
    window      INTEGER          NOT NULL,
    market_beta DOUBLE PRECISION NOT NULL,
    smb_beta    DOUBLE PRECISION,
    hml_beta    DOUBLE PRECISION,
    r_squared   DOUBLE PRECISION NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_beta_ticker ON beta_decompositions (ticker);
