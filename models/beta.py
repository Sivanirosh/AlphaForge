"""CAPM and Fama-French 3-factor beta estimation via OLS regression."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass
class BetaResult:
    """Container for OLS beta regression output."""

    market_beta: float
    smb_beta: float | None = None
    hml_beta: float | None = None
    r_squared: float = 0.0
    t_stats: dict[str, float] = field(default_factory=dict)
    rolling_window: int | None = None


def compute_capm_beta(
    excess_returns: pd.Series,
    market_returns: pd.Series,
) -> BetaResult:
    """Single-factor CAPM beta via OLS: R_i - R_f = α + β(R_m - R_f) + ε.

    Both inputs should already be excess returns (net of risk-free rate).

    CFA reference: Capital Asset Pricing Model — market beta.
    """
    aligned = pd.concat(
        [excess_returns.rename("y"), market_returns.rename("mkt")],
        axis=1,
    ).dropna()

    if len(aligned) < 3:
        return BetaResult(market_beta=float("nan"), r_squared=float("nan"))

    x = sm.add_constant(aligned["mkt"])
    model = sm.OLS(aligned["y"], x).fit()

    return BetaResult(
        market_beta=float(model.params.get("mkt", np.nan)),
        r_squared=float(model.rsquared),
        t_stats={"mkt": float(model.tvalues.get("mkt", np.nan))},
        rolling_window=len(aligned),
    )


def compute_ff3_beta(
    excess_returns: pd.Series,
    factors_df: pd.DataFrame,
) -> BetaResult:
    """Fama-French 3-factor beta via OLS.

    R_i - R_f = α + β_mkt(Mkt-RF) + β_smb(SMB) + β_hml(HML) + ε

    *factors_df* must have columns: ``Mkt-RF``, ``SMB``, ``HML``.
    *excess_returns* should already be net of the risk-free rate.

    CFA reference: Fama-French three-factor model.
    """
    factor_cols = ["Mkt-RF", "SMB", "HML"]

    aligned = pd.concat(
        [excess_returns.rename("y"), factors_df[factor_cols]],
        axis=1,
    ).dropna()

    if len(aligned) < 5:
        return BetaResult(market_beta=float("nan"), r_squared=float("nan"))

    x = sm.add_constant(aligned[factor_cols])
    model = sm.OLS(aligned["y"], x).fit()

    return BetaResult(
        market_beta=float(model.params.get("Mkt-RF", np.nan)),
        smb_beta=float(model.params.get("SMB", np.nan)),
        hml_beta=float(model.params.get("HML", np.nan)),
        r_squared=float(model.rsquared),
        t_stats={
            col: float(model.tvalues.get(col, np.nan)) for col in factor_cols
        },
        rolling_window=len(aligned),
    )
