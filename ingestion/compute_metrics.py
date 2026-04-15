"""Pure computational functions for financial metrics.

Every function is stateless (no DB, no I/O). Inputs are pandas Series /
DataFrames; outputs are plain Python scalars or pandas objects.

Convention: all returns are *log returns* — simple returns are never used.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ingestion.constants import TRADING_DAYS_PER_YEAR


def log_returns(prices: pd.Series) -> pd.Series:
    """Compute continuously compounded (log) returns.

    Formula: r_t = ln(P_t / P_{t-1})

    CFA reference: Holding-period return (log form).
    """
    return np.log(prices / prices.shift(1))


def rolling_volatility(log_rets: pd.Series, window: int = 60) -> pd.Series:
    """Annualised rolling volatility of log returns.

    Formula: σ_ann = σ_window × √252

    CFA reference: Annualised standard deviation of returns.
    """
    return log_rets.rolling(window=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)


def sharpe_ratio(log_rets: pd.Series, rf: float = 0.0) -> float:
    """Annualised Sharpe ratio from a series of daily log returns.

    Formula: SR = (μ_excess × 252) / (σ × √252)
               = (μ_excess × √252) / σ

    where μ_excess = mean(r) - rf_daily

    CFA reference: Sharpe ratio — excess return per unit of total risk.
    """
    daily_mean_excess = log_rets.mean() - rf
    daily_std = log_rets.std()
    if daily_std < 1e-12 or np.isnan(daily_std):
        return float("nan")
    return float(daily_mean_excess * np.sqrt(TRADING_DAYS_PER_YEAR) / daily_std)


def realised_variance(log_rets: pd.Series) -> float:
    """Sum of squared log returns (realised variance estimator).

    Formula: RV = Σ r_t²
    """
    clean = log_rets.dropna()
    return float((clean**2).sum())
