"""
Replication figures for "The Hays Discount, Five Years Later".

All compute lives in analysis.py; this module is just plotting.

Figures
-------
  1. gap_levels.png          ZHVI levels, three counties, 2020-present
  2. gap_absolute.png        Absolute dollar gap (Travis/Williamson − Hays)
  3. gap_triangulation.png   Same premium measured three ways (ZHVI / FHFA / Realtor)
  4. gap_real_nominal.png    Real vs. nominal absolute gap (CPI deflated)
  5. gap_piti.png            PITI decomposition of the monthly gap (P&I, tax, ins, MUD)
  6. gap_relative_stats.png  Premium time series + mean, 95% CI, Quandt sup-F overlay
  7. gap_tiers.png           Premium across ZHVI tiers (bottom / mid / top)
  8. gap_out_of_metro.png    Austin (Travis/Hays) vs. DFW (Denton/Collin) premium
  9. migration_response.png  Hays in-migration vs. lagged Travis→Hays gap

Usage
-----
    pip install -r requirements.txt
    python fetch_data.py
    python build_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import analysis as A

# ── Styling (matches other posts) ──────────────────────────────────────────
RED    = "#DC3520"
BLUE   = "#1F77B4"
ORANGE = "#FF7F0E"
GRAY   = "#999999"
GREEN  = "#2CA02C"
PURPLE = "#9467BD"
BROWN  = "#8C564B"
DPI    = 150

mpl.rcParams.update({
    "figure.dpi": DPI, "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y",
    "grid.color": "#E5E5E5", "grid.linewidth": 0.8,
    "font.family": "sans-serif", "font.size": 11,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.fontsize": 9, "legend.frameon": False,
    "figure.constrained_layout.use": True,
})

HERE = Path(__file__).parent
OUT  = HERE / "figures"
OUT.mkdir(exist_ok=True)

COUNTY_COLOR = {
    "Travis County":     GRAY,
    "Williamson County": ORANGE,
    "Hays County":       BLUE,
}

# ── Small helpers ──────────────────────────────────────────────────────────
def _source(ax, text):
    ax.text(0, -0.15, text, transform=ax.transAxes, fontsize=7, color=GRAY)

def _save(fig, name):
    p = OUT / name
    fig.savefig(p, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {p}")

# ── 1. Levels ──────────────────────────────────────────────────────────────
def fig_levels(r: A.AnalysisResult):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for c, color in COUNTY_COLOR.items():
        if c not in r.levels.columns: continue
        ax.plot(r.levels.index, r.levels[c], color=color, lw=2.2,
                label=c.replace(" County", ""))
        ax.annotate(f"${r.levels[c].iloc[-1]:.0f}K",
                    (r.levels.index[-1], r.levels[c].iloc[-1]),
                    textcoords="offset points", xytext=(6, 0),
                    va="center", fontsize=9, fontweight="bold", color=color)
    ax.set_ylabel("Median home value ($K, ZHVI mid tier)")
    ax.set_title("Central Texas Home Values, 2020 → present")
    ax.legend(loc="lower right")
    _source(ax, "Source: Zillow ZHVI (all homes, mid tier, SA, smoothed), county level.")
    _save(fig, "gap_levels.png")

# ── 2. Absolute gap ────────────────────────────────────────────────────────
def fig_absolute(r: A.AnalysisResult):
    g = r.abs_gap
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(g.index, g["Travis − Hays"],     color=RED,    lw=2.2, label="Travis − Hays")
    ax.plot(g.index, g["Williamson − Hays"], color=ORANGE, lw=2.0, label="Williamson − Hays")

    pk = g["Travis − Hays"].idxmax(); pv = g["Travis − Hays"].max()
    ax.scatter([pk], [pv], color=RED, zorder=5, s=45)
    ax.annotate(f"Peak: ${pv:.0f}K\n({pk:%b %Y})",
                (pk, pv), textcoords="offset points",
                xytext=(10, -4), fontsize=8.5, color=RED, fontweight="bold")

    ld = g.index[-1]; lv = g["Travis − Hays"].iloc[-1]
    ax.annotate(f"${lv:.0f}K\n({ld:%b %Y})",
                (ld, lv), textcoords="offset points", xytext=(8, 0),
                va="center", fontsize=8.5, color=RED, fontweight="bold")

    ax.axhline(0, color=GRAY, lw=0.6)
    ax.set_ylabel("Price gap over Hays ($K)")
    ax.set_title("The Dollar Gap Over Hays, 2020 → present")
    ax.legend(loc="upper left")
    _source(ax, "Source: Zillow ZHVI, author's calculations.")
    _save(fig, "gap_absolute.png")

# ── 3. Triangulation ───────────────────────────────────────────────────────
def fig_triangulation(r: A.AnalysisResult):
    t = r.triangulation
    if t.empty:
        print("  (skipped triangulation — no series)")
        return
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    palette = [RED, BLUE, GREEN, PURPLE, BROWN]
    for (name, color) in zip(t.columns, palette):
        ax.plot(t.index, t[name], lw=2.0, color=color, label=name)
    ax.set_ylabel("Travis-over-Hays premium (%)")
    ax.set_title("Three Data Sources, One Invariant")
    ax.legend(loc="lower left", ncol=1)
    _source(ax,
            "Sources: Zillow ZHVI mid tier; FHFA HPI (rebased to 2020-Q1); "
            "Realtor.com median listing (FRED).")
    _save(fig, "gap_triangulation.png")

# ── 4. Real vs. nominal ────────────────────────────────────────────────────
def fig_real_nominal(r: A.AnalysisResult):
    rn = r.real_nominal
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(rn.index, rn["nominal"], color=RED, lw=2.2, label="Nominal gap")
    ax.plot(rn.index, rn["real_2020_01"], color=BLUE, lw=2.0, ls="--",
            label="Real gap (in Jan-2020 dollars)")
    for col, color in [("nominal", RED), ("real_2020_01", BLUE)]:
        lv = rn[col].iloc[-1]
        ax.annotate(f"${lv:.0f}K", (rn.index[-1], lv),
                    textcoords="offset points", xytext=(6, 0),
                    va="center", fontsize=9, fontweight="bold", color=color)
    ax.set_ylabel("Gap over Hays ($K)")
    ax.set_title("Deflating the Gap — Real vs. Nominal")
    ax.legend(loc="upper left")
    _source(ax, "Sources: Zillow ZHVI; BLS CPI-U All items, SA (FRED: CPIAUCSL).")
    _save(fig, "gap_real_nominal.png")

# ── 5. PITI decomposition ──────────────────────────────────────────────────
def fig_piti(r: A.AnalysisResult):
    p = r.piti.copy()
    comps = ["P&I", "Taxes", "Insurance", "MUD/PID"]
    totals = p["Total PITI"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.8, 6.2), sharex=True,
                                    gridspec_kw={"height_ratios": [2, 1]})

    colors = {"P&I": BLUE, "Taxes": RED, "Insurance": ORANGE, "MUD/PID": GRAY}

    # Stacked area with positives and negatives handled separately.
    pos = p[comps].clip(lower=0)
    neg = p[comps].clip(upper=0)
    ax1.stackplot(p.index,
                  [pos[c] for c in comps],
                  labels=comps, colors=[colors[c] for c in comps], alpha=0.85)
    ax1.stackplot(p.index,
                  [neg[c] for c in comps],
                  colors=[colors[c] for c in comps], alpha=0.85)
    ax1.plot(p.index, totals, color="black", lw=1.8, label="Total PITI gap")
    ax1.axhline(0, color="black", lw=0.6)

    start_v = totals.iloc[0]; end_v = totals.iloc[-1]
    ax1.annotate(f"${start_v:,.0f}/mo\n({p.index[0]:%b %Y})",
                 (p.index[0], start_v), textcoords="offset points",
                 xytext=(6, 8), fontsize=8.5, fontweight="bold", color="black")
    ax1.annotate(f"${end_v:,.0f}/mo\n({p.index[-1]:%b %Y})",
                 (p.index[-1], end_v), textcoords="offset points",
                 xytext=(-10, 8), ha="right", fontsize=8.5,
                 fontweight="bold", color="black")

    ax1.set_ylabel("Monthly gap (USD)")
    ax1.set_title("PITI Gap: Travis − Hays (monthly, not just P&I)")
    ax1.legend(loc="upper left", ncol=3, fontsize=8)

    ax2.plot(r.rates.index, r.rates.values, color=RED, lw=2.0)
    ax2.set_ylabel("30Y fixed (%)")
    ax2.set_xlabel("")
    _source(ax2,
            "Sources: Zillow ZHVI; Freddie Mac 30Y fixed (FRED: MORTGAGE30US); "
            "property tax & insurance per county per analysis.py notes.")
    _save(fig, "gap_piti.png")

# ── 6. Premium statistics ──────────────────────────────────────────────────
def fig_relative_stats(r: A.AnalysisResult):
    ps = r.prem_stats
    prem = ps["series"]
    mu = ps["mean"]; ci_lo, ci_hi = ps["ci95"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.8, 6.2), sharex=True,
                                    gridspec_kw={"height_ratios": [2, 1]})

    ax1.plot(prem.index, prem.values, color=RED, lw=2.2, label="Travis/Hays premium")
    ax1.axhline(mu, color=BLUE, lw=1.0, ls="--",
                label=f"Mean {mu:.1f}%")
    ax1.fill_between(prem.index, ci_lo, ci_hi, color=BLUE, alpha=0.08,
                      label=f"95% HAC CI [{ci_lo:.1f}, {ci_hi:.1f}]")
    ax1.axvline(ps["break_date"], color=GRAY, lw=0.8, ls=":",
                label=f"Quandt sup-F = {ps['sup_F']:.1f} @ {ps['break_date']:%Y-%m}")
    ax1.set_ylabel("Premium (%)")
    ax1.set_title("Is the Premium Constant? Stats on the Ratio")
    ax1.legend(loc="lower right", fontsize=8)

    ax2.plot(ps["F_series"].index, ps["F_series"].values, color=PURPLE, lw=1.8)
    ax2.set_ylabel("F (unknown break)")
    ax2.set_xlabel("")
    ax2.axhline(3.84, color=GRAY, lw=0.8, ls=":", label="5% crit ≈ 3.84 (1 df)")
    ax2.legend(loc="upper right", fontsize=8)
    _source(ax2, "Source: Zillow ZHVI; tests computed in analysis.py.")
    _save(fig, "gap_relative_stats.png")

# ── 7. Tier robustness ─────────────────────────────────────────────────────
def fig_tiers(r: A.AnalysisResult):
    t = r.tier_prems
    if t.empty:
        print("  (skipped tiers — no data)")
        return
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    colors = {"bottom": BLUE, "mid": RED, "top": GRAY}
    labels = {"bottom": "Bottom tier (0.00–0.33)",
              "mid":    "Mid tier (0.33–0.67)",
              "top":    "Top tier (0.67–1.00)"}
    for tier in ("bottom", "mid", "top"):
        if tier not in t.columns: continue
        ax.plot(t.index, t[tier], color=colors[tier], lw=2.0,
                label=labels[tier])
    ax.set_ylabel("Travis-over-Hays premium (%)")
    ax.set_title("Does the Story Survive at the Bottom of the Market?")
    ax.legend(loc="upper left")
    _source(ax, "Source: Zillow ZHVI tiered series (0.0–0.33, 0.33–0.67, 0.67–1.0).")
    _save(fig, "gap_tiers.png")

# ── 8. Out-of-metro ────────────────────────────────────────────────────────
def fig_out_of_metro(r: A.AnalysisResult):
    df = r.out_of_metro
    if df is None:
        print("  (skipped out-of-metro — Denton/Collin missing)")
        return
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(df.index, df["Austin: Travis/Hays"], color=RED,  lw=2.2,
            label="Austin — Travis over Hays")
    ax.plot(df.index, df["DFW: Denton/Collin"],  color=BLUE, lw=2.0,
            label="DFW — Denton over Collin")
    ax.set_ylabel("Premium (%)")
    ax.set_title("Is the 38 % Premium an Austin Thing?")
    ax.legend(loc="lower right")
    _source(ax, "Source: Zillow ZHVI mid tier, county level.")
    _save(fig, "gap_out_of_metro.png")

# ── 9. Migration response ──────────────────────────────────────────────────
def fig_migration(r: A.AnalysisResult):
    mig = r.migration
    if mig is None:
        print("  (skipped migration — IRS SOI panel unavailable)")
        return
    df = mig["frame"]

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    sc = ax.scatter(df["gap_k_lag1"], df["inflow_exemptions"],
                    s=80, c=df["year"], cmap="viridis", zorder=5,
                    edgecolor="white")
    for _, row in df.iterrows():
        ax.annotate(f"  {int(row['year'])}",
                    (row["gap_k_lag1"], row["inflow_exemptions"]),
                    fontsize=8.5, va="center")
    # Fit line using the regression beta for gap_k_lag1.
    xs = np.linspace(df["gap_k_lag1"].min(), df["gap_k_lag1"].max(), 50)
    beta = mig["beta"]
    # Evaluate at the mean contemporaneous gap so the line is a 2D slice.
    mean_gap = df["gap_k"].mean()
    ys = beta[0] + beta[1] * mean_gap + beta[2] * xs
    ax.plot(xs, ys, color=RED, lw=1.6, ls="--",
            label=f"slope β = {beta[2]:.0f} exemptions / $K gap (SE {mig['se'][2]:.0f})")

    ax.set_xlabel("Travis − Hays gap, prior year mean ($K)")
    ax.set_ylabel("Hays in-migration (exemptions / year)")
    ax.set_title("Do Inflows Follow the Gap? IRS SOI, n small")
    ax.legend(loc="lower right")
    cbar = fig.colorbar(sc, ax=ax, shrink=0.7)
    cbar.set_label("Tax year", fontsize=8)
    _source(ax,
            "Sources: IRS Statistics of Income county-to-county migration "
            "inflows; Zillow ZHVI. n = %d years." % len(df))
    _save(fig, "migration_response.png")

# ── Driver ─────────────────────────────────────────────────────────────────
def main():
    print("Loading analysis…")
    r = A.run()
    s = r.summary
    print(f"  window {s['window'][0]:%Y-%m} → {s['window'][1]:%Y-%m}")
    print(f"  premium mean {s['prem_mean_ci'][0]:.2f}%  "
          f"CI95 [{s['prem_mean_ci'][1][0]:.2f}, {s['prem_mean_ci'][1][1]:.2f}]  "
          f"SD {s['prem_sd']:.2f}")
    print(f"  AR(1) rho {s['ar1_rho']:+.3f}  (SE {s['ar1_rho_se']:.3f})")
    print(f"  Quandt sup-F {s['sup_F']:.2f} at {s['break_date']:%Y-%m}")
    print(f"  PITI (monthly USD): {s['piti_latest']}")
    pi_v, tot_v = s['piti_pi_vs_total']
    print(f"  P&I alone ${pi_v:,.0f}; after tax/ins/MUD offsets ${tot_v:,.0f}")
    print(f"  rate: {s['rate_start']:.2f}% → {s['rate_latest']:.2f}%")
    print()
    print("Building figures…")
    fig_levels(r)
    fig_absolute(r)
    fig_triangulation(r)
    fig_real_nominal(r)
    fig_piti(r)
    fig_relative_stats(r)
    fig_tiers(r)
    fig_out_of_metro(r)
    fig_migration(r)
    print("Done.")


if __name__ == "__main__":
    main()
