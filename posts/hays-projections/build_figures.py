"""
Replication code for "Where Is All of This Going?"
Hays County population projections post.

Generates two figures:
  1. Historical + projected population through 2060
  2. What 612K looks like — comparison to other Texas counties

Usage:
    pip install -r requirements.txt
    python build_figures.py
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path

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

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)


def fig_projection():
    """Figure 1: Historical growth + TDC projections through 2060."""
    hist_years = [1990, 2000, 2010, 2020, 2025]
    hist_pop   = [65.6, 97.6, 157.1, 241.1, 302.0]

    proj_years = [2025, 2030, 2040, 2050, 2060]
    proj_pop   = [302.0, 360.0, 470.0, 550.0, 612.0]

    fig, ax = plt.subplots(figsize=(7.0, 4.5))

    ax.plot(hist_years, hist_pop, color=BLUE, marker="o", lw=2.5, ms=7,
            zorder=5, label="Census / ACS (actual)")
    ax.plot(proj_years, proj_pop, color=ORANGE, marker="s", lw=2, ms=6,
            ls="--", zorder=5, label="Texas Demographic Center (projected)")

    ax.axvspan(2025, 2062, alpha=0.06, color=ORANGE)

    for yr, p in [(2020, 241.1), (2025, 302.0)]:
        ax.annotate(f"{p:.0f}K", (yr, p), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=8.5,
                    fontweight="bold", color="#333")

    ax.annotate("~612K", (2060, 612), textcoords="offset points",
                xytext=(0, 12), ha="center", fontsize=9,
                fontweight="bold", color=ORANGE)
    ax.annotate("~470K", (2040, 470), textcoords="offset points",
                xytext=(0, 12), ha="center", fontsize=8.5,
                fontweight="bold", color=ORANGE)

    ax.set_ylabel("Population (thousands)")
    ax.set_title("Hays County: Historical Growth and Projected Future")
    ax.set_xlim(1988, 2063)
    ax.set_ylim(0, 700)
    ax.legend(loc="upper left")
    ax.text(0, -0.10,
            "Sources: U.S. Census Bureau (1990–2020), ACS 2023, "
            "Texas Demographic Center Vintage 2024 (0.5 migration scenario).",
            transform=ax.transAxes, fontsize=7, color=GRAY)

    fig.savefig(OUT / "hays_projection.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_projection.png'}")


def fig_comparison():
    """Figure 2: What 612K looks like in context."""
    counties = ["El Paso\n(today)", "Hays\n(2060)", "Hays\n(today)", "Williamson\n(2010)"]
    pops     = [865, 612, 302, 422]
    colors   = [GRAY, ORANGE, BLUE, GRAY]

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    bars = ax.bar(counties, pops, color=colors, alpha=[0.5, 0.8, 0.8, 0.5],
                  width=0.55, edgecolor="white", linewidth=0.5)

    for bar, val in zip(bars, pops):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f"{val}K", ha="center", fontsize=10, fontweight="bold", color="#333")

    ax.set_ylabel("Population (thousands)")
    ax.set_title("What 612,000 Looks Like: Hays County in Context")
    ax.set_ylim(0, 1000)
    ax.text(0, -0.10,
            "Hays County at projected 2060 population would be roughly the size of "
            "Williamson County today.\nSources: Census Bureau, Texas Demographic Center.",
            transform=ax.transAxes, fontsize=7, color=GRAY)

    fig.savefig(OUT / "hays_comparison.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_comparison.png'}")


if __name__ == "__main__":
    print("Building figures for 'Where Is All of This Going?'…")
    fig_projection()
    fig_comparison()
    print("Done.")
