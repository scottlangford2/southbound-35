"""
Replication code for "254 Counties, One Interstate: The Hays County Growth Story"
https://scottlangford2.github.io/scott_langford/posts/2026/04/hays-county-growth/

Generates three figures:
  1. Hays County population, 1990–2025
  2. Hays County cities: 2010 vs. 2025
  3. The growth engine: median home prices, 2025

Usage:
    pip install -r requirements.txt
    python build_figures.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import numpy as np

from econ_style import apply as apply_econ_style, COLORS, redbar, source_line, BG

apply_econ_style()

# Aliases so the existing figure code keeps reading.
RED    = COLORS["red"]
BLUE   = COLORS["blue"]
ORANGE = COLORS["yellow"]
GRAY   = COLORS["darkgray"]
DPI    = 150

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)


def fig_population():
    """Figure 1: Hays County population, 1990–2025."""
    years = [1990, 2000, 2010, 2020, 2025]
    pop   = [65_614, 97_589, 157_107, 241_067, 302_000]

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    redbar(fig)
    ax.plot(years, [p / 1000 for p in pop], color=BLUE, marker="o", lw=2.5, ms=8, zorder=5)

    for yr, p in zip(years, pop):
        label = f"~{p // 1000}K (est.)" if yr == 2025 else f"{p:,}"
        ax.annotate(label, (yr, p / 1000), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=8.5, fontweight="bold", color="#333")

    ax.axvspan(2000, 2020, alpha=0.20, color=ORANGE, label="20-year tripling (97K to 241K)")
    ax.set_ylabel("Population (thousands)")
    ax.set_title("Hays County Population, 1990–2025")
    ax.set_xlim(1988, 2027)
    ax.set_ylim(0, 350)
    ax.legend(loc="upper left")
    source_line(ax,
                "Sources: U.S. Census Bureau (1990–2020 decennial), ACS 2023, author estimate 2025.")

    fig.savefig(OUT / "hays_population.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_population.png'}")


def fig_cities():
    """Figure 2: Hays County cities, 2010 vs. 2025."""
    cities   = ["Kyle", "San Marcos", "Buda", "Dripping\nSprings", "Wimberley"]
    pop_2010 = [28.016, 44.894, 7.295, 1.788, 2.626]
    pop_now  = [70.0,   91.0,   16.0,  8.7,   2.9]

    x = np.arange(len(cities))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    redbar(fig)
    ax.bar(x - width/2, pop_2010, width, color=GRAY, alpha=0.6, label="2010 Census")
    ax.bar(x + width/2, pop_now, width, color=BLUE, alpha=0.80, label="2025 (est.)")

    pct_growth = [(n - o) / o * 100 for o, n in zip(pop_2010, pop_now)]
    bars2 = ax.patches[len(cities):]
    for bar, pct in zip(bars2, pct_growth):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                f"+{pct:.0f}%", ha="center", fontsize=8, fontweight="bold",
                color=RED if pct > 100 else "#333")

    ax.set_xticks(x)
    ax.set_xticklabels(cities)
    ax.set_ylabel("Population (thousands)")
    ax.set_title("Hays County Cities: 2010 vs. 2025")
    ax.legend()
    ax.set_ylim(0, 110)
    source_line(ax, "Sources: U.S. Census Bureau, city estimates, ACS 2023.",
                y=-0.16)

    fig.savefig(OUT / "hays_cities.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_cities.png'}")


def fig_affordability():
    """Figure 3: Median home prices — Travis vs. Williamson vs. Hays."""
    counties = ["Travis\nCounty", "Williamson\nCounty", "Hays\nCounty"]
    medians  = [490, 410, 355]
    colors   = [GRAY, ORANGE, BLUE]

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    redbar(fig)
    bars = ax.bar(counties, medians, color=colors, alpha=0.80, width=0.55)

    for bar, val in zip(bars, medians):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"${val}K", ha="center", fontsize=11, fontweight="bold", color="#333")

    ax.annotate("", xy=(2, 355), xytext=(0, 490),
                arrowprops=dict(arrowstyle="->", color=RED, lw=2.5,
                                connectionstyle="arc3,rad=0.2"))
    ax.text(1.35, 440, "$135K\ncheaper", fontsize=9, color=RED, fontweight="bold", ha="center")

    ax.set_ylabel("Median Home Price ($K)")
    ax.set_title("The Growth Engine: Median Home Prices, 2025")
    ax.set_ylim(0, 560)
    source_line(ax, "Sources: Redfin, ABoR/CBA Realtors, February 2026.",
                y=-0.18)

    fig.savefig(OUT / "hays_affordability.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_affordability.png'}")


if __name__ == "__main__":
    print("Building figures for 'The Hays County Growth Story'…")
    fig_population()
    fig_cities()
    fig_affordability()
    print("Done.")
