"""Volatility models: EWMA and GARCH stub."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ingestion.constants import TRADING_DAYS_PER_YEAR


def rolling_ewma_vol(log_rets: pd.Series, span: int = 60) -> pd.Series:
    """Annualised exponentially weighted moving average volatility.

    EWMA gives more weight to recent observations, making the estimate
    more responsive to volatility clustering than a simple rolling window.

    Formula: σ_ewma = EWM_std(r, span) × √252
    """
    return log_rets.ewm(span=span).std() * np.sqrt(TRADING_DAYS_PER_YEAR)


def garch_stub() -> None:
    """Placeholder for a future GARCH(1,1) volatility model.

    Will use ``arch`` package when implemented.
    """
    raise NotImplementedError("GARCH model not yet implemented — future work.")
