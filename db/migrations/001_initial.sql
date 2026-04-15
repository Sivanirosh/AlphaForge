-- Migration 001: Initial table creation
-- Applied automatically by SQLAlchemy ORM on first run.
-- This file exists as a reference for manual / CI-based migration flows.

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

CREATE TABLE IF NOT EXISTS factors (
    id      SERIAL PRIMARY KEY,
    date    DATE             NOT NULL UNIQUE,
    mkt_rf  DOUBLE PRECISION NOT NULL,
    smb     DOUBLE PRECISION NOT NULL,
    hml     DOUBLE PRECISION NOT NULL,
    rf      DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
    id           SERIAL PRIMARY KEY,
    ticker       VARCHAR(10)  NOT NULL,
    date         DATE         NOT NULL,
    log_return   DOUBLE PRECISION,
    rolling_vol  DOUBLE PRECISION,
    sharpe_ratio DOUBLE PRECISION,
    UNIQUE (ticker, date)
);

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
