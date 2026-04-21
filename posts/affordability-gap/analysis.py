"""
Analysis module for "The Hays Discount, Five Years Later".

Keeps the compute separate from the plotting. `build_figures.py` imports
from here; this module imports nothing from matplotlib.

Responsibilities
----------------
1. Load raw CSVs written by `fetch_data.py`.
2. Triangulate a price panel across three independent series:
     - Zillow ZHVI (mid tier)
     - FHFA HPI all-transactions  (rebased to a common anchor so levels
       are comparable in index form)
     - Realtor.com median listing price
3. Deflate with CPI to produce real-dollar equivalents.
4. Compute full PITI monthly cost of the Travis → Hays gap, using:
     - contemporaneous 30-yr fixed mortgage rate
     - effective property-tax rate per county (published Truth-in-Taxation)
     - estimated annual homeowners insurance
     - estimated MUD / PID assessment where applicable
5. Statistical tests on the constancy-of-premium claim:
     - mean premium + 95% CI (HAC)
     - AR(1) coefficient
     - Quandt–Andrews sup-F unknown-break test
6. Migration response: county-level regression of annual net inflows
   (IRS SOI) on the lagged price gap.

Everything returns plain DataFrames / dicts — the figure layer does the
rendering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data"

MAIN = ["Travis County", "Williamson County", "Hays County"]
ROBUSTNESS_PAIR = ("Denton County", "Collin County")  # (higher, lower)

# ── Fiscal parameters ──────────────────────────────────────────────────────
#
# Effective property-tax rates: county + city + school + special districts,
# 2025 adopted rates (Truth-in-Taxation, Texas Comptroller). Point estimates
# at a typical within-county address; real-world dispersion across ISDs can
# be ±0.2 pp. Treated as constant across the 2020–present window for the
# headline PITI calculation; a sensitivity pass in analysis.breakeven_tax()
# moves them.
#
# Homeowners-insurance annual premium: TDI 2024 "Texas Home Insurance Price
# Comparison" averages for HO-B single-family, scaled linearly to 2026 with
# the TDI statewide 6.5 % average rate change. Hays premium is modestly
# higher than Travis (hail + wildfire exposure east of the Balcones
# escarpment; TDI Region 2).
#
# MUD / PID monthly assessment: typical new Hays subdivision MUD rate is
# $0.75–1.00 per $100 of assessed value; we use $0.85 as a point estimate.
# Travis is assumed to carry none (median home in this tier is in COA,
# inside MUD-rare zones).
FISCAL = pd.DataFrame({
    "eff_tax_rate":     [0.0180, 0.0195, 0.0210],  # fraction of AV, annual
    "annual_insurance": [2800.0, 3000.0, 3050.0],  # USD, HO-B single family
    "mud_rate":         [0.0,    0.0,    0.0085],  # additional ad valorem
}, index=MAIN)


# ── Loaders ────────────────────────────────────────────────────────────────
def _require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} missing. Run `python fetch_data.py` first.")
    return path

def load_zhvi(tier: str = "mid") -> pd.DataFrame:
    df = pd.read_csv(_require(DATA / f"zhvi_{tier}.csv"), parse_dates=["date"])
    wide = df.pivot(index="date", columns="RegionName", values="zhvi").div(1000.0)
    return wide.sort_index()

def load_zhvi_ppsf() -> pd.DataFrame:
    df = pd.read_csv(_require(DATA / "zhvi_ppsf.csv"), parse_dates=["date"])
    return df.pivot(index="date", columns="RegionName", values="ppsf").sort_index()

def load_fhfa() -> pd.DataFrame:
    df = pd.read_csv(_require(DATA / "fhfa_hpi.csv"), parse_dates=["date"])
    return (df.pivot_table(index="date", columns="county", values="hpi_all",
                           aggfunc="last")
              .sort_index())

def load_realtor_list_price() -> pd.DataFrame:
    df = pd.read_csv(_require(DATA / "realtor_list_price.csv"),
                     parse_dates=["date"])
    return (df.pivot_table(index="date", columns="RegionName",
                           values="list_price", aggfunc="last")
              .div(1000.0).sort_index())

def load_mortgage_rates() -> pd.Series:
    df = pd.read_csv(_require(DATA / "mortgage30.csv"), parse_dates=["date"])
    return df.set_index("date")["value"].resample("ME").last()

def load_cpi(which: str = "cpi_us") -> pd.Series:
    df = pd.read_csv(_require(DATA / f"{which}.csv"), parse_dates=["date"])
    return df.set_index("date")["value"]

def load_irs_soi_hays() -> Optional[pd.DataFrame]:
    p = DATA / "irs_soi_hays_inflows.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["year"] = df["year"].astype(int)
    return df

# ── Windowing ───────────────────────────────────────────────────────────────
START = pd.Timestamp("2020-01-01")

def _restrict(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[df.index >= START]

# ── 1. Triangulation ────────────────────────────────────────────────────────
def triangulated_gap() -> pd.DataFrame:
    """
    Return a DataFrame indexed by date with one column per source, each
    showing the Travis-over-Hays premium expressed as a percentage. Three
    independent series should agree on the qualitative claim (flat premium)
    even though their levels differ.
    """
    out = pd.DataFrame()

    zhvi = _restrict(load_zhvi("mid"))
    out["ZHVI (Zillow, mid tier)"] = (
        zhvi["Travis County"] / zhvi["Hays County"] - 1) * 100

    try:
        fhfa = _restrict(load_fhfa())
        # FHFA is an index, not a price; ratios still meaningful if we
        # rebase to each county's 2020-Q1 value. In index form, a gap
        # means "Travis prices have risen X% more than Hays since base".
        fhfa_reb = fhfa.div(fhfa.iloc[0])
        out["FHFA HPI (rebased)"] = (
            fhfa_reb["Travis County"] / fhfa_reb["Hays County"] - 1) * 100
    except Exception:
        pass

    try:
        rr = _restrict(load_realtor_list_price())
        out["Realtor.com median listing"] = (
            rr["Travis County"] / rr["Hays County"] - 1) * 100
    except Exception:
        pass

    return out.dropna(how="all")

# ── 2. Real vs. nominal ─────────────────────────────────────────────────────
def real_vs_nominal_gap() -> pd.DataFrame:
    zhvi = _restrict(load_zhvi("mid"))
    cpi = load_cpi("cpi_us")
    cpi_m = cpi.resample("ME").last()
    base = cpi_m.loc[cpi_m.index >= START].iloc[0]
    deflator = cpi_m / base

    nominal = zhvi["Travis County"] - zhvi["Hays County"]
    # Align deflator to ZHVI index (ZHVI is MS, CPI resampled to ME).
    defl = deflator.reindex(nominal.index, method="nearest")
    real = nominal / defl
    return pd.DataFrame({"nominal": nominal, "real_2020_01": real})

# ── 3. PITI ────────────────────────────────────────────────────────────────
def _pi_monthly(principal_k: pd.Series, apr_pct: pd.Series,
                term_months: int = 360) -> pd.Series:
    apr = apr_pct.reindex(principal_k.index.to_period("M").to_timestamp("M"),
                          method="nearest")
    apr.index = principal_k.index
    r = (apr / 100.0) / 12.0
    return 1000.0 * principal_k * r * (1 + r) ** term_months \
           / ((1 + r) ** term_months - 1)

def piti_gap() -> pd.DataFrame:
    """
    Incremental monthly cost of choosing Travis over Hays, decomposed into
    P&I, property tax, insurance, and MUD/PID. Tax and insurance depend on
    the *level* of each county's price, not just the gap — a dearer Travis
    home carries a higher tax bill even at the same effective rate.
    """
    zhvi = _restrict(load_zhvi("mid"))
    rates = load_mortgage_rates()

    principal_gap = zhvi["Travis County"] - zhvi["Hays County"]     # $K
    pi = _pi_monthly(principal_gap, rates)

    # Tax on the full price, not the gap — monthly.
    tax_travis = zhvi["Travis County"] * 1000 * FISCAL.loc["Travis County", "eff_tax_rate"] / 12
    tax_hays   = zhvi["Hays County"]   * 1000 * FISCAL.loc["Hays County",   "eff_tax_rate"] / 12
    tax_gap    = tax_travis - tax_hays

    # MUD (Hays only, on Hays price).
    mud_hays = zhvi["Hays County"] * 1000 * FISCAL.loc["Hays County", "mud_rate"] / 12
    mud_gap  = -mud_hays   # Travis pays nothing; so choosing Travis *saves* this.

    # Insurance (constant monthly delta — Hays > Travis → choosing Travis saves).
    ins_gap = (FISCAL.loc["Travis County", "annual_insurance"]
               - FISCAL.loc["Hays County",   "annual_insurance"]) / 12
    ins_gap = pd.Series(ins_gap, index=pi.index)

    total = pi + tax_gap + ins_gap + mud_gap
    return pd.DataFrame({
        "P&I":        pi,
        "Taxes":      tax_gap,
        "Insurance":  ins_gap,
        "MUD/PID":    mud_gap,
        "Total PITI": total,
    })

# ── 4. Statistical tests on the premium ────────────────────────────────────
def _newey_west_se(x: pd.Series, lags: int = 6) -> float:
    """HAC (Newey–West) standard error of the sample mean."""
    x = x.dropna().values
    n = len(x)
    mu = x.mean()
    e = x - mu
    gamma0 = (e @ e) / n
    s = gamma0
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        gL = (e[L:] @ e[:-L]) / n
        s += 2 * w * gL
    return float(np.sqrt(max(s, 0) / n))

def _ar1(x: pd.Series) -> tuple[float, float, int]:
    """OLS AR(1) on demeaned series; return (rho, se, n)."""
    x = x.dropna()
    y = x.iloc[1:].values
    x0 = x.iloc[:-1].values
    x0 = x0 - x0.mean()
    y  = y  - y.mean()
    beta = (x0 @ y) / (x0 @ x0)
    resid = y - beta * x0
    sig2 = (resid @ resid) / (len(y) - 1)
    se = float(np.sqrt(sig2 / (x0 @ x0)))
    return float(beta), se, len(y)

def _quandt_sup_f(x: pd.Series, trim: float = 0.15) -> dict:
    """
    Quandt–Andrews sup-F test for an unknown break in the mean of a
    stationary series. Grid-search the middle (1 - 2·trim) fraction of
    sample for the break date with the largest F statistic against a
    constant-mean null.
    """
    y = x.dropna().values
    n = len(y)
    lo, hi = int(trim * n), int((1 - trim) * n)
    F = np.zeros(hi - lo)
    sst = ((y - y.mean()) ** 2).sum()
    for i, k in enumerate(range(lo, hi)):
        y1, y2 = y[:k], y[k:]
        rss = ((y1 - y1.mean()) ** 2).sum() + ((y2 - y2.mean()) ** 2).sum()
        # F = ((SST - RSS) / q) / (RSS / (n - 2q)); q = 1 for mean shift.
        F[i] = ((sst - rss) / 1) / (rss / (n - 2))
    j = int(np.argmax(F))
    return {
        "sup_F":    float(F[j]),
        "break_idx": lo + j,
        "break_date": x.dropna().index[lo + j],
        "F_series": pd.Series(F, index=x.dropna().index[lo:hi]),
    }

def premium_statistics() -> dict:
    zhvi = _restrict(load_zhvi("mid"))
    prem = (zhvi["Travis County"] / zhvi["Hays County"] - 1) * 100
    mu = prem.mean()
    se = _newey_west_se(prem, lags=6)
    rho, rho_se, _ = _ar1(prem)
    qa = _quandt_sup_f(prem)
    return {
        "mean":        float(mu),
        "se":          float(se),
        "ci95":        (float(mu - 1.96 * se), float(mu + 1.96 * se)),
        "sd":          float(prem.std()),
        "ar1_rho":     rho,
        "ar1_rho_se":  rho_se,
        "sup_F":       qa["sup_F"],
        "break_date":  qa["break_date"],
        "F_series":    qa["F_series"],
        "series":      prem,
    }

# ── 5. Migration regression ────────────────────────────────────────────────
def migration_response() -> Optional[dict]:
    """
    Annual net in-migration to Hays County (returns * exemptions) regressed
    on the mean Travis→Hays gap over the same tax year, with one-year lag.
    Small n (5 years of SOI); presented as illustrative, not inferential.
    """
    soi = load_irs_soi_hays()
    if soi is None:
        return None

    # Inflows: total returns & exemptions entering Hays each year
    # (origin != Hays). IRS codes "Same County" rows with origin_fips ==
    # dest_fips — drop those.
    inflow = soi[soi["origin_fips"] != "48209"].groupby("year").agg(
        inflow_returns=("n1", "sum"),
        inflow_exemptions=("n2", "sum"),
    ).reset_index()

    zhvi = _restrict(load_zhvi("mid"))
    gap = (zhvi["Travis County"] - zhvi["Hays County"])  # $K
    annual_gap = gap.resample("YE").mean()
    annual_gap.index = annual_gap.index.year

    df = inflow.merge(
        annual_gap.rename("gap_k").reset_index().rename(columns={"date": "year"}),
        on="year", how="inner")
    if len(df) < 3:
        return None

    # Contemporaneous + lagged gap
    df["gap_k_lag1"] = df["gap_k"].shift(1)
    df = df.dropna()

    # OLS by hand to avoid statsmodels dependency for one tiny model.
    X = np.column_stack([np.ones(len(df)), df["gap_k"].values, df["gap_k_lag1"].values])
    y = df["inflow_exemptions"].values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    sig2 = (resid @ resid) / max(len(y) - X.shape[1], 1)
    cov = sig2 * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    return {
        "frame": df,
        "beta":  beta,
        "se":    se,
        "names": ["intercept", "gap_k", "gap_k_lag1"],
    }

# ── 6. Robustness: tier and out-of-metro ────────────────────────────────────
def tier_premiums() -> pd.DataFrame:
    """Premium of Travis over Hays for each ZHVI tier."""
    out = {}
    for tier in ("bottom", "mid", "top"):
        try:
            z = _restrict(load_zhvi(tier))
            out[tier] = (z["Travis County"] / z["Hays County"] - 1) * 100
        except FileNotFoundError:
            continue
    return pd.DataFrame(out)

def out_of_metro_gap() -> Optional[pd.DataFrame]:
    """
    Travis-over-Hays vs. Denton-over-Collin premium over time. If 38% is
    an Austin-specific constant, the DFW pair should differ; if it's a
    general metro-edge regularity, both should be stable at similar levels.
    """
    try:
        z = _restrict(load_zhvi("mid"))
    except FileNotFoundError:
        return None
    needed = list(MAIN) + list(ROBUSTNESS_PAIR)
    if not all(c in z.columns for c in needed):
        return None
    austin = (z["Travis County"] / z["Hays County"] - 1) * 100
    dfw    = (z["Denton County"] / z["Collin County"] - 1) * 100
    return pd.DataFrame({"Austin: Travis/Hays": austin,
                          "DFW: Denton/Collin":  dfw})

# ── 7. Summary record ──────────────────────────────────────────────────────
@dataclass
class AnalysisResult:
    triangulation:    pd.DataFrame
    real_nominal:     pd.DataFrame
    piti:             pd.DataFrame
    prem_stats:       dict
    migration:        Optional[dict]
    tier_prems:       pd.DataFrame
    out_of_metro:     Optional[pd.DataFrame]
    rates:            pd.Series
    levels:           pd.DataFrame          # mid-tier ZHVI, main counties
    abs_gap:          pd.DataFrame
    summary:          dict = field(default_factory=dict)

def run() -> AnalysisResult:
    zhvi = _restrict(load_zhvi("mid"))
    rates = load_mortgage_rates().loc[lambda s: s.index >= START]

    abs_gap = pd.DataFrame({
        "Travis − Hays":     zhvi["Travis County"]     - zhvi["Hays County"],
        "Williamson − Hays": zhvi["Williamson County"] - zhvi["Hays County"],
    })

    tri  = triangulated_gap()
    rn   = real_vs_nominal_gap()
    piti = piti_gap()
    ps   = premium_statistics()
    mig  = migration_response()
    tp   = tier_premiums()
    oom  = out_of_metro_gap()

    summary = {
        "window":                (zhvi.index.min(), zhvi.index.max()),
        "levels_latest":         zhvi.iloc[-1].round(0).to_dict(),
        "abs_gap_latest":        abs_gap.iloc[-1].round(0).to_dict(),
        "abs_gap_peak":          abs_gap.max().round(0).to_dict(),
        "abs_gap_peak_dt":       abs_gap.idxmax().to_dict(),
        "prem_mean_ci":          (ps["mean"], ps["ci95"]),
        "prem_sd":               ps["sd"],
        "ar1_rho":               ps["ar1_rho"],
        "ar1_rho_se":            ps["ar1_rho_se"],
        "sup_F":                 ps["sup_F"],
        "break_date":            ps["break_date"],
        "piti_latest":           piti.iloc[-1].round(0).to_dict(),
        "piti_pi_vs_total":      (float(piti["P&I"].iloc[-1]),
                                   float(piti["Total PITI"].iloc[-1])),
        "rate_start":            float(rates.iloc[0]),
        "rate_latest":           float(rates.iloc[-1]),
        "migration_n":           (0 if mig is None else len(mig["frame"])),
    }
    return AnalysisResult(
        triangulation=tri, real_nominal=rn, piti=piti, prem_stats=ps,
        migration=mig, tier_prems=tp, out_of_metro=oom,
        rates=rates, levels=zhvi, abs_gap=abs_gap, summary=summary,
    )

# ── CLI: print the summary for manual spot-check ───────────────────────────
if __name__ == "__main__":
    r = run()
    s = r.summary
    print("─" * 72)
    print(f"Window: {s['window'][0]:%Y-%m} → {s['window'][1]:%Y-%m}")
    print(f"Latest levels (K$):   {s['levels_latest']}")
    print(f"Absolute gap latest:  {s['abs_gap_latest']}")
    print(f"Absolute gap peak:    {s['abs_gap_peak']}  at  {s['abs_gap_peak_dt']}")
    print()
    print(f"Premium (Travis/Hays, %):")
    print(f"  mean                {s['prem_mean_ci'][0]:5.2f}")
    print(f"  95% HAC CI         [{s['prem_mean_ci'][1][0]:5.2f}, {s['prem_mean_ci'][1][1]:5.2f}]")
    print(f"  SD                  {s['prem_sd']:.2f}")
    print(f"  AR(1) rho           {s['ar1_rho']:+.3f}  (SE {s['ar1_rho_se']:.3f})")
    print(f"  Quandt sup-F        {s['sup_F']:.2f}  at  {s['break_date']:%Y-%m}")
    print()
    print(f"PITI latest (monthly gap, USD):")
    for k, v in s['piti_latest'].items():
        print(f"  {k:<12}  {v:+8.0f}")
    pi_v, tot_v = s['piti_pi_vs_total']
    print(f"  (P&I alone: ${pi_v:,.0f}; after tax/ins/MUD offsets: ${tot_v:,.0f})")
    print()
    print(f"Mortgage rate: {s['rate_start']:.2f}%  →  {s['rate_latest']:.2f}%")
    print(f"IRS SOI migration panel: n = {s['migration_n']} years")
    print("─" * 72)
