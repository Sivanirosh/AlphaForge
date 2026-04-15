"""Property-based and unit tests for financial metric computations."""

from __future__ import annotations

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from ingestion.compute_metrics import (
    log_returns,
    realised_variance,
    rolling_volatility,
    sharpe_ratio,
)
from models.beta import BetaResult, compute_capm_beta, compute_ff3_beta
from models.volatility import rolling_ewma_vol


class TestLogReturns:
    def test_constant_prices_yield_zero_returns(self) -> None:
        prices = pd.Series([100.0] * 10)
        rets = log_returns(prices)
        assert all(rets.dropna() == 0.0)

    def test_additivity(self, sample_prices: pd.DataFrame) -> None:
        """Sum of log returns equals the total log return."""
        close = sample_prices["close"]
        rets = log_returns(close)
        total_log_return = np.log(close.iloc[-1] / close.iloc[0])
        assert np.isclose(rets.sum(), total_log_return, rtol=1e-10)

    @given(
        prices=arrays(
            dtype=np.float64,
            shape=st.integers(min_value=2, max_value=500),
            elements=st.floats(min_value=1.0, max_value=1e6, allow_nan=False),
        )
    )
    @settings(max_examples=50)
    def test_log_returns_finite_for_positive_prices(self, prices: np.ndarray) -> None:
        series = pd.Series(prices)
        rets = log_returns(series).dropna()
        assert rets.apply(np.isfinite).all()


class TestRollingVolatility:
    def test_flat_series_zero_vol(self) -> None:
        rets = pd.Series([0.0] * 100)
        vol = rolling_volatility(rets, window=20)
        assert all(vol.dropna() == 0.0)

    def test_positive_for_non_constant(self, sample_prices: pd.DataFrame) -> None:
        close = sample_prices["close"]
        rets = log_returns(close)
        vol = rolling_volatility(rets, window=20)
        valid = vol.dropna()
        assert (valid > 0).all()

    @given(
        returns=arrays(
            dtype=np.float64,
            shape=st.integers(min_value=25, max_value=500),
            elements=st.floats(min_value=-0.1, max_value=0.1, allow_nan=False),
        )
    )
    @settings(max_examples=30)
    def test_vol_non_negative(self, returns: np.ndarray) -> None:
        series = pd.Series(returns)
        vol = rolling_volatility(series, window=20).dropna()
        assert (vol >= 0).all()


class TestSharpeRatio:
    def test_nan_for_zero_vol(self) -> None:
        rets = pd.Series([0.01] * 100)
        sr = sharpe_ratio(rets, rf=0.0)
        assert np.isnan(sr)

    def test_finite_for_valid_series(self, sample_prices: pd.DataFrame) -> None:
        close = sample_prices["close"]
        rets = log_returns(close).dropna()
        sr = sharpe_ratio(rets, rf=0.0)
        assert np.isfinite(sr)


class TestRealisedVariance:
    def test_zero_for_flat(self) -> None:
        rets = pd.Series([0.0] * 50)
        assert realised_variance(rets) == 0.0

    @given(
        returns=arrays(
            dtype=np.float64,
            shape=st.integers(min_value=2, max_value=200),
            elements=st.floats(min_value=-0.1, max_value=0.1, allow_nan=False),
        )
    )
    @settings(max_examples=30)
    def test_non_negative(self, returns: np.ndarray) -> None:
        assert realised_variance(pd.Series(returns)) >= 0.0


class TestCAPMBeta:
    def test_beta_one_for_same_series(self) -> None:
        np.random.seed(0)
        market = pd.Series(np.random.normal(0, 0.02, 200))
        result = compute_capm_beta(market, market)
        assert np.isclose(result.market_beta, 1.0, atol=1e-6)

    def test_result_type(self) -> None:
        np.random.seed(1)
        x = pd.Series(np.random.normal(0, 0.02, 100))
        y = pd.Series(np.random.normal(0, 0.02, 100))
        result = compute_capm_beta(x, y)
        assert isinstance(result, BetaResult)
        assert np.isfinite(result.r_squared)


class TestFF3Beta:
    def test_finite_output(self) -> None:
        np.random.seed(2)
        n = 200
        excess = pd.Series(np.random.normal(0, 0.02, n), name="y")
        factors = pd.DataFrame(
            {
                "Mkt-RF": np.random.normal(0, 0.01, n),
                "SMB": np.random.normal(0, 0.005, n),
                "HML": np.random.normal(0, 0.005, n),
            }
        )
        result = compute_ff3_beta(excess, factors)
        assert np.isfinite(result.market_beta)
        assert np.isfinite(result.smb_beta)
        assert np.isfinite(result.hml_beta)
        assert np.isfinite(result.r_squared)

    def test_insufficient_data_returns_nan(self) -> None:
        excess = pd.Series([0.01, 0.02])
        factors = pd.DataFrame(
            {"Mkt-RF": [0.01, 0.02], "SMB": [0.001, 0.002], "HML": [0.003, 0.004]}
        )
        result = compute_ff3_beta(excess, factors)
        assert np.isnan(result.market_beta)


class TestEWMAVol:
    def test_ewma_positive(self) -> None:
        np.random.seed(3)
        rets = pd.Series(np.random.normal(0, 0.02, 100))
        vol = rolling_ewma_vol(rets, span=30)
        valid = vol.dropna()
        assert (valid > 0).all()
