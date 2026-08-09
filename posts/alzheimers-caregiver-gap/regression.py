"""
Cross-state regression of direct-care workforce density on Medicaid
HCBS spending per capita.

This module is the analytical backbone of Figure 7 and the regression
table in the README. It uses only numpy (no statsmodels dependency).

Outputs (also embedded in the figure annotation):
    - OLS slope and intercept
    - Heteroskedasticity-robust (HC1) standard error on the slope
    - Univariate R-squared
    - Pearson and Spearman correlation
    - Nonparametric bootstrap 95% confidence intervals on the slope
    - Sensitivity: leave-one-out range, drop-DC, drop top-3 leverage

Methodology note: this is a univariate cross-state regression on a
single year of state-level public data. The slope identifies a
correlation between Medicaid HCBS rates and workforce density that
is consistent with the monopsony framing, but the cross-section
cannot rule out reverse causality (states with more available
caregivers may be able to support more HCBS programming) or omitted
state-level confounders (cost of living, demographic composition,
share urban, union density). The cleaner causal identifications in
the literature (Matsudaira 2014; Hackmann 2019; Ruffini 2022) point
in the same direction.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class RegressionResult:
    n: int
    slope: float
    intercept: float
    slope_se_hc1: float
    slope_ci_lo: float
    slope_ci_hi: float
    r2: float
    r_pearson: float
    r_spearman: float
    loo_slope_min: float
    loo_slope_max: float
    slope_drop_dc: float
    slope_drop_top3: float

    def annotate(self) -> str:
        """Compact multi-line annotation for the figure."""
        return (
            f"OLS: workers/1k = {self.intercept:.1f} + "
            f"{self.slope * 1000:.2f} per $1,000 HCBS\n"
            f"HC1 SE = {self.slope_se_hc1 * 1000:.3f}; "
            f"95% boot. CI = [{self.slope_ci_lo * 1000:.2f}, "
            f"{self.slope_ci_hi * 1000:.2f}]\n"
            f"r = {self.r_pearson:.2f} (Pearson); "
            f"{self.r_spearman:.2f} (Spearman); "
            f"R² = {self.r2:.2f}; n = {self.n}"
        )


def _ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Plain OLS slope and intercept (univariate)."""
    coef = np.polyfit(x, y, 1)
    return float(coef[0]), float(coef[1])


def _hc1_slope_se(x: np.ndarray, y: np.ndarray) -> float:
    """Heteroskedasticity-robust (HC1) SE for the OLS slope in a
    univariate regression with constant. Uses the standard
    sandwich formula:
        var_hat(beta_hat) = (X'X)^-1 X' diag(e_i^2) X (X'X)^-1
    with the HC1 small-sample correction n/(n-k).
    """
    n = len(x)
    X = np.column_stack([np.ones(n), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    meat = X.T @ np.diag(resid ** 2) @ X
    var_beta = XtX_inv @ meat @ XtX_inv
    k = X.shape[1]
    hc1 = var_beta * (n / (n - k))
    return float(np.sqrt(hc1[1, 1]))


def _bootstrap_slope_ci(
    x: np.ndarray, y: np.ndarray, n_boot: int = 5000,
    alpha: float = 0.05, seed: int = 0,
) -> tuple[float, float]:
    """Nonparametric pairs bootstrap CI on the OLS slope."""
    rng = np.random.default_rng(seed)
    n = len(x)
    slopes = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        slopes[i] = _ols(x[idx], y[idx])[0]
    lo, hi = np.quantile(slopes, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx = pd.Series(x).rank().to_numpy()
    ry = pd.Series(y).rank().to_numpy()
    return float(np.corrcoef(rx, ry)[0, 1])


def fit_state_scatter(df: pd.DataFrame) -> RegressionResult:
    """Fit the cross-state regression and return all diagnostics.

    Expects a DataFrame with columns:
        - state                  (USPS abbrev)
        - hcbs_per_capita_usd
        - direct_care_per_1k_65p
    """
    x = df["hcbs_per_capita_usd"].to_numpy(dtype=float)
    y = df["direct_care_per_1k_65p"].to_numpy(dtype=float)
    states = df["state"].to_numpy()

    slope, intercept = _ols(x, y)
    se = _hc1_slope_se(x, y)
    ci_lo, ci_hi = _bootstrap_slope_ci(x, y)
    r_pearson = float(np.corrcoef(x, y)[0, 1])
    r_spearman = _spearman(x, y)
    yhat = intercept + slope * x
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot

    loo_slopes = []
    for i in range(len(x)):
        mask = np.ones(len(x), dtype=bool)
        mask[i] = False
        loo_slopes.append(_ols(x[mask], y[mask])[0])
    loo_slopes_arr = np.array(loo_slopes)

    if "DC" in states:
        dc_mask = states != "DC"
        slope_drop_dc, _ = _ols(x[dc_mask], y[dc_mask])
    else:
        slope_drop_dc = slope

    leverage = (x - x.mean()) ** 2
    top3_idx = np.argsort(leverage)[-3:]
    top3_mask = np.ones(len(x), dtype=bool)
    top3_mask[top3_idx] = False
    slope_drop_top3, _ = _ols(x[top3_mask], y[top3_mask])

    return RegressionResult(
        n=len(x),
        slope=slope,
        intercept=intercept,
        slope_se_hc1=se,
        slope_ci_lo=ci_lo,
        slope_ci_hi=ci_hi,
        r2=r2,
        r_pearson=r_pearson,
        r_spearman=r_spearman,
        loo_slope_min=float(loo_slopes_arr.min()),
        loo_slope_max=float(loo_slopes_arr.max()),
        slope_drop_dc=slope_drop_dc,
        slope_drop_top3=slope_drop_top3,
    )


def confidence_band(
    x: np.ndarray, y: np.ndarray, x_grid: np.ndarray,
    n_boot: int = 1000, alpha: float = 0.05, seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Pointwise bootstrap CI for the OLS regression line."""
    rng = np.random.default_rng(seed)
    n = len(x)
    preds = np.empty((n_boot, len(x_grid)))
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        slope, intercept = _ols(x[idx], y[idx])
        preds[i] = intercept + slope * x_grid
    lo = np.quantile(preds, alpha / 2, axis=0)
    hi = np.quantile(preds, 1 - alpha / 2, axis=0)
    return lo, hi


if __name__ == "__main__":
    here = Path(__file__).parent
    df = pd.read_csv(here / "inputs" / "state_medicaid_workforce.csv",
                     comment="#")
    res = fit_state_scatter(df)
    print(res.annotate())
    print()
    print(f"Sensitivity:")
    print(f"  Leave-one-out slope range (× 1000): "
          f"[{res.loo_slope_min * 1000:.2f}, {res.loo_slope_max * 1000:.2f}]")
    print(f"  Slope dropping DC (× 1000): {res.slope_drop_dc * 1000:.2f}")
    print(f"  Slope dropping top-3 leverage (× 1000): "
          f"{res.slope_drop_top3 * 1000:.2f}")
