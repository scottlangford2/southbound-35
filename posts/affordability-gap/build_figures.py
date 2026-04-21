"""
Replication code for "The Hays Discount, Five Years Later".

Loads the raw data written by fetch_data.py, computes four derived series,
and writes four figures.

Derived series (monthly, 2020-01 through latest available):
  - Price levels   : Travis, Williamson, Hays ZHVI
  - Absolute gap   : Travis − Hays, Williamson − Hays (thousands of dollars)
  - Relative gap   : (Travis / Hays − 1) × 100, same for Williamson
  - Payment gap    : monthly principal & interest on the absolute gap,
                     30-year fixed, using the month-end Freddie Mac rate

Usage:
    pip install -r requirements.txt
    python fetch_data.py
    python build_figures.py
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd

# ── Styling (matches other posts) ────────────────────────────────────────────
RED    = "#DC3520"
BLUE   = "#1F77B4"
ORANGE = "#FF7F0E"
GRAY   = "#999999"
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
DATA = HERE / "data"
OUT  = HERE / "figures"
OUT.mkdir(exist_ok=True)

START = pd.Timestamp("2020-01-01")

COLORS = {
    "Travis County":     GRAY,
    "Williamson County": ORANGE,
    "Hays County":       BLUE,
}


# ── Analysis ─────────────────────────────────────────────────────────────────
def load_prices() -> pd.DataFrame:
    """Return wide (date × county) DataFrame of ZHVI in thousands, from 2020."""
    raw = pd.read_csv(DATA / "zhvi_counties.csv", parse_dates=["date"])
    wide = (raw.pivot(index="date", columns="RegionName", values="zhvi")
               .loc[START:]
               .div(1000.0))
    for c in COLORS:
        if c not in wide.columns:
            raise RuntimeError(f"Missing county in ZHVI panel: {c}")
    return wide[list(COLORS.keys())]


def load_rates() -> pd.Series:
    """Return a monthly 30Y fixed-rate series (last obs in month), from 2020."""
    raw = pd.read_csv(DATA / "mortgage_rates.csv", parse_dates=["date"])
    s = raw.set_index("date")["rate"].loc[START:]
    # Align weekly rates to month-end for merging with monthly ZHVI.
    return s.resample("ME").last()


def monthly_payment(principal_k: pd.Series, apr_pct: pd.Series,
                    term_months: int = 360) -> pd.Series:
    """Standard amortization P&I on a loan of `principal_k` (thousands)."""
    # ZHVI index is month-start; rates are month-end. Snap to nearest.
    apr = apr_pct.reindex(principal_k.index.to_period("M").to_timestamp("M"),
                          method="nearest")
    apr.index = principal_k.index
    r = (apr / 100.0) / 12.0
    return 1000.0 * principal_k * r * (1 + r) ** term_months \
           / ((1 + r) ** term_months - 1)


def build_analysis() -> dict:
    """Compute all derived series and summary numbers."""
    prices = load_prices()
    rates  = load_rates()

    abs_gap = pd.DataFrame({
        "Travis − Hays":     prices["Travis County"]     - prices["Hays County"],
        "Williamson − Hays": prices["Williamson County"] - prices["Hays County"],
    })

    rel_gap = pd.DataFrame({
        "Travis / Hays":     (prices["Travis County"]     / prices["Hays County"] - 1) * 100,
        "Williamson / Hays": (prices["Williamson County"] / prices["Hays County"] - 1) * 100,
    })

    pay_gap = pd.DataFrame({
        "Travis − Hays":     monthly_payment(abs_gap["Travis − Hays"], rates),
        "Williamson − Hays": monthly_payment(abs_gap["Williamson − Hays"], rates),
    })

    # Summary snapshots referenced in the post.
    summary = {
        "start":        prices.index.min(),
        "latest":       prices.index.max(),
        "levels_latest":   prices.iloc[-1].round(0).to_dict(),
        "abs_gap_latest":  abs_gap.iloc[-1].round(0).to_dict(),
        "abs_gap_peak":    abs_gap.max().round(0).to_dict(),
        "abs_gap_peak_dt": abs_gap.idxmax().to_dict(),
        "rel_gap_latest":  rel_gap.iloc[-1].round(1).to_dict(),
        "rel_gap_mean":    rel_gap.mean().round(1).to_dict(),
        "rel_gap_std":     rel_gap.std().round(1).to_dict(),
        "pay_gap_start":   pay_gap.iloc[0].round(0).to_dict(),
        "pay_gap_latest":  pay_gap.iloc[-1].round(0).to_dict(),
        "rate_start":      float(rates.iloc[0]),
        "rate_latest":     float(rates.iloc[-1]),
    }
    return dict(prices=prices, abs_gap=abs_gap, rel_gap=rel_gap,
                pay_gap=pay_gap, rates=rates, summary=summary)


# ── Figures ──────────────────────────────────────────────────────────────────
def _source_line(ax, text):
    ax.text(0, -0.12, text, transform=ax.transAxes, fontsize=7, color=GRAY)


def fig_levels(a: dict) -> None:
    """Figure 1: Three-county ZHVI, Jan 2020 → latest."""
    prices = a["prices"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for county, color in COLORS.items():
        ax.plot(prices.index, prices[county], color=color, lw=2.2,
                label=county.replace(" County", ""))
        ax.annotate(f"${prices[county].iloc[-1]:.0f}K",
                    (prices.index[-1], prices[county].iloc[-1]),
                    textcoords="offset points", xytext=(6, 0),
                    va="center", fontsize=9, fontweight="bold", color=color)

    ax.set_ylabel("Median home value ($K, ZHVI)")
    ax.set_title("Central Texas Home Values, 2020 → 2026")
    ax.legend(loc="lower right")
    _source_line(ax, "Source: Zillow Home Value Index (all homes, mid-tier, SA, smoothed), county level.")
    fig.savefig(OUT / "gap_levels.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'gap_levels.png'}")


def fig_absolute(a: dict) -> None:
    """Figure 2: Absolute dollar gap over time."""
    g = a["abs_gap"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(g.index, g["Travis − Hays"],     color=RED,    lw=2.2, label="Travis − Hays")
    ax.plot(g.index, g["Williamson − Hays"], color=ORANGE, lw=2.0, label="Williamson − Hays")

    peak_dt  = g["Travis − Hays"].idxmax()
    peak_val = g["Travis − Hays"].max()
    ax.scatter([peak_dt], [peak_val], color=RED, zorder=5, s=45)
    ax.annotate(f"Peak gap: ${peak_val:.0f}K\n({peak_dt:%b %Y})",
                (peak_dt, peak_val), textcoords="offset points",
                xytext=(10, -4), fontsize=8.5, color=RED, fontweight="bold")

    latest_dt  = g.index[-1]
    latest_val = g["Travis − Hays"].iloc[-1]
    ax.annotate(f"${latest_val:.0f}K\n({latest_dt:%b %Y})",
                (latest_dt, latest_val), textcoords="offset points",
                xytext=(8, 0), va="center", fontsize=8.5, color=RED, fontweight="bold")

    ax.axhline(0, color=GRAY, lw=0.6)
    ax.set_ylabel("Price gap over Hays ($K)")
    ax.set_title("The Dollar Gap Over Hays, 2020 → 2026")
    ax.legend(loc="upper left")
    _source_line(ax, "Source: Zillow ZHVI, author's calculations.")
    fig.savefig(OUT / "gap_absolute.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'gap_absolute.png'}")


def fig_relative(a: dict) -> None:
    """Figure 3: Relative premium over Hays."""
    g = a["rel_gap"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(g.index, g["Travis / Hays"],     color=RED,    lw=2.2, label="Travis premium")
    ax.plot(g.index, g["Williamson / Hays"], color=ORANGE, lw=2.0, label="Williamson premium")

    mean_t = g["Travis / Hays"].mean()
    ax.axhline(mean_t, color=RED, lw=0.8, ls="--", alpha=0.5)
    ax.text(g.index[2], mean_t + 0.8,
            f"Travis mean: {mean_t:.1f}%", color=RED, fontsize=8.5)

    mean_w = g["Williamson / Hays"].mean()
    ax.axhline(mean_w, color=ORANGE, lw=0.8, ls="--", alpha=0.5)
    ax.text(g.index[2], mean_w + 0.8,
            f"Williamson mean: {mean_w:.1f}%", color=ORANGE, fontsize=8.5)

    ax.set_ylabel("Premium over Hays median (%)")
    ax.set_title("The Percentage Premium Over Hays Has Barely Moved")
    ax.legend(loc="upper right")
    _source_line(ax, "Source: Zillow ZHVI, author's calculations.")
    fig.savefig(OUT / "gap_relative.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'gap_relative.png'}")


def fig_payment(a: dict) -> None:
    """Figure 4: Monthly P&I on the Travis−Hays gap, with contemporaneous rate."""
    pay  = a["pay_gap"]["Travis − Hays"]
    rate = a["rates"].reindex(pay.index, method="nearest")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.5, 5.5), sharex=True,
                                    gridspec_kw={"height_ratios": [2, 1]})

    ax1.plot(pay.index, pay, color=BLUE, lw=2.2)
    ax1.fill_between(pay.index, 0, pay, color=BLUE, alpha=0.10)
    for dt in [pay.index[0], pay.idxmax(), pay.index[-1]]:
        ax1.scatter([dt], [pay.loc[dt]], color=BLUE, s=40, zorder=5)
        ax1.annotate(f"${pay.loc[dt]:,.0f}/mo\n({dt:%b %Y})",
                     (dt, pay.loc[dt]), textcoords="offset points",
                     xytext=(8, -4), fontsize=8.5, color=BLUE, fontweight="bold")
    ax1.set_ylabel("Monthly P&I on the gap")
    ax1.set_title("What the Gap Costs Each Month (30-yr fixed, P&I only)")
    ax1.set_ylim(bottom=0)

    ax2.plot(rate.index, rate, color=RED, lw=2.0)
    ax2.set_ylabel("30Y fixed (%)")
    ax2.set_xlabel("")

    _source_line(ax2,
                 "Sources: Zillow ZHVI; Freddie Mac PMMS 30-year fixed (FRED: MORTGAGE30US).")
    fig.savefig(OUT / "gap_payment.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'gap_payment.png'}")


# ── Driver ───────────────────────────────────────────────────────────────────
def main():
    a = build_analysis()
    s = a["summary"]
    print("\nAnalysis summary")
    print(f"  window          : {s['start']:%Y-%m} → {s['latest']:%Y-%m}")
    print(f"  latest levels   : {s['levels_latest']}")
    print(f"  abs gap latest  : {s['abs_gap_latest']}")
    print(f"  abs gap peak    : {s['abs_gap_peak']}  at  {s['abs_gap_peak_dt']}")
    print(f"  rel gap latest  : {s['rel_gap_latest']}")
    print(f"  rel gap mean    : {s['rel_gap_mean']} (sd {s['rel_gap_std']})")
    print(f"  pay gap start   : {s['pay_gap_start']}  (rate {s['rate_start']:.2f}%)")
    print(f"  pay gap latest  : {s['pay_gap_latest']}  (rate {s['rate_latest']:.2f}%)")
    print()

    fig_levels(a)
    fig_absolute(a)
    fig_relative(a)
    fig_payment(a)
    print("Done.")


if __name__ == "__main__":
    main()
