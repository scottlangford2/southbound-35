"""
Replication code for "Where the Water Will Come From"
https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-water/

Generates three figures:
  1. Hays County water demand, historical + projected
  2. The aquifer split: Hays cities by source aquifer
  3. ARWA imported supply, phase ramp-up

Numbers marked `# VERIFY` are author best estimates and should be
replaced with the cited public source before publication.

Usage:
    pip install -r requirements.txt
    python build_figures.py
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path

# Same palette as hays-growth / hays-projections for visual continuity
RED    = "#DC3520"
BLUE   = "#1F77B4"
ORANGE = "#FF7F0E"
GREEN  = "#2CA02C"
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


def fig_demand():
    """Figure 1: Hays County water demand, historical + projected.

    Source: TWDB Water Use Survey (historical) + Region L 2026 Regional
    Water Plan (projections). Acre-feet per year by category.

    # VERIFY: numbers below are placeholder estimates aligned with the
    # general magnitude of TWDB Hays County reporting. Replace with
    # exact values from the TWDB Historical Water Use Estimates tool
    # and the Region L 2026 plan tables before publication.
    """
    years      = [2000, 2005, 2010, 2015, 2020, 2030, 2040, 2050, 2060, 2070]
    municipal  = [16.0, 22.0, 30.0, 40.0, 55.0, 78.0, 100.0, 120.0, 138.0, 152.0]  # VERIFY
    irrigation = [ 5.5,  5.0,  4.5,  4.0,  4.0,  3.8,   3.5,   3.3,   3.0,   2.8]  # VERIFY
    mining     = [ 0.4,  0.6,  0.9,  1.2,  1.4,  1.4,   1.3,   1.2,   1.1,   1.0]  # VERIFY
    manuf      = [ 0.2,  0.3,  0.4,  0.5,  0.6,  0.7,   0.8,   0.8,   0.9,   0.9]  # VERIFY

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.stackplot(years, municipal, irrigation, mining, manuf,
                 labels=["Municipal", "Irrigation", "Mining", "Manufacturing"],
                 colors=[BLUE, GREEN, ORANGE, GRAY], alpha=0.85)

    ax.axvline(2025, color="#555", lw=1, ls="--", alpha=0.6)
    ax.text(2025.5, ax.get_ylim()[1] * 0.92, "projected →",
            fontsize=8.5, color="#555", style="italic")

    ax.set_xlabel("Year")
    ax.set_ylabel("Demand (thousand acre-feet/yr)")
    ax.set_title("Hays County Water Demand: Historical and Projected")
    ax.set_xlim(2000, 2070)
    ax.legend(loc="upper left")
    ax.text(0, -0.12,
            "Sources: TWDB Historical Water Use Estimates; Region L 2026 Regional Water Plan.",
            transform=ax.transAxes, fontsize=7, color=GRAY)

    fig.savefig(OUT / "hays_water_demand.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_water_demand.png'}")


def fig_aquifer_split():
    """Figure 2: Hays cities arrayed east–west by approximate longitude,
    colored by source aquifer. Schematic; no external data.

    # VERIFY: aquifer assignments are simplifications. Eastern San
    # Marcos draws Edwards (Authority side); Buda straddles BSEACD
    # boundary; Wimberley is squarely Trinity. Confirm exact
    # service-area boundaries with city utility staff or HCAD before
    # using in policy contexts.
    """
    # Approximate longitudes, spread for legibility (schematic).
    # True longitudes for Wimberley and Dripping Springs are ~0.02
    # apart, which collides at this scale; cities are pushed apart
    # along x to keep labels readable.
    cities = [
        ("Wimberley",         -98.16, "Trinity"),
        ("Dripping\nSprings", -98.04, "Trinity"),
        ("San Marcos",        -97.93, "Edwards"),
        ("Kyle",              -97.87, "Edwards"),
        ("Buda",              -97.81, "Edwards"),
        ("Niederwald",        -97.72, "Edwards"),
    ]
    color_map = {"Trinity": ORANGE, "Edwards": BLUE}

    fig, ax = plt.subplots(figsize=(7.0, 3.6))

    # Stylized recharge-zone band: the Edwards recharge zone runs in a
    # narrow diagonal along I-35; here we draw it as a vertical band
    # just east of the city cluster to keep the schematic readable.
    band_left, band_right = -97.99, -97.95
    ax.axvspan(band_left, band_right, color="#FFE4B5", alpha=0.7,
               label="Edwards recharge zone (schematic)")

    for label, lon, aquifer in cities:
        ax.scatter(lon, 1, s=160, color=color_map[aquifer], zorder=5,
                   edgecolor="white", linewidth=1.2)
        ax.annotate(label, (lon, 1), xytext=(0, 14),
                    textcoords="offset points", ha="center",
                    fontsize=9, fontweight="bold")
        ax.annotate(aquifer, (lon, 1), xytext=(0, -22),
                    textcoords="offset points", ha="center",
                    fontsize=8, color=color_map[aquifer], style="italic")

    ax.set_xlim(-98.22, -97.66)
    ax.set_ylim(0.6, 1.5)
    ax.set_yticks([])
    ax.set_xlabel("Longitude (West)")
    ax.set_title("The Aquifer Split: Hays Cities by Source")
    ax.legend(loc="upper right", frameon=False)
    ax.spines["left"].set_visible(False)
    ax.grid(False)
    ax.text(0, -0.18,
            "Schematic. Aquifer assignments based on city utility "
            "service areas, not parcel-level mapping.",
            transform=ax.transAxes, fontsize=7, color=GRAY)

    fig.savefig(OUT / "hays_aquifer_split.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_aquifer_split.png'}")


def fig_arwa_ramp():
    """Figure 3: ARWA imported supply by phase, in MGD, across partner
    cities. Stepped to reflect when each phase came / will come online.

    Source: Alliance Regional Water Authority project documents and
    partner-city annual financial reports.

    # VERIFY: phase capacities and online dates are approximate. Phase
    # 1 nominal nameplate is in the tens of MGD across all four
    # partners; later phases scale up. Replace with ARWA's published
    # figures before publication.
    """
    # Phase, year online, cumulative MGD across all partners
    phases = [
        ("Pre-ARWA",  2010,  0),    # baseline
        ("Phase 1A",  2020, 10.0),  # VERIFY
        ("Phase 1B",  2024, 16.0),  # VERIFY
        ("Phase 2",   2030, 28.0),  # VERIFY: planned
        ("Phase 3",   2040, 42.0),  # VERIFY: long-range
    ]

    years = [p[1] for p in phases]
    mgd   = [p[2] for p in phases]
    labels = [p[0] for p in phases]

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.step(years, mgd, where="post", color=BLUE, lw=2.5, zorder=3)
    ax.fill_between(years, 0, mgd, step="post", color=BLUE, alpha=0.18)

    for yr, m, lab in zip(years, mgd, labels):
        if m > 0:
            ax.scatter(yr, m, color=BLUE, s=60, zorder=5,
                       edgecolor="white", linewidth=1.2)
            ax.annotate(f"{lab}\n{m:.0f} MGD", (yr, m),
                        xytext=(6, 8), textcoords="offset points",
                        fontsize=8.5, fontweight="bold")

    ax.axvline(2025, color="#555", lw=1, ls="--", alpha=0.6)
    ax.text(2025.5, ax.get_ylim()[1] * 0.05, "today",
            fontsize=8.5, color="#555", style="italic")

    ax.set_xlabel("Year online")
    ax.set_ylabel("Cumulative imported supply (MGD)")
    ax.set_title("ARWA Imported Supply: Phase Ramp-Up")
    ax.set_xlim(2008, 2045)
    ax.set_ylim(0, max(mgd) * 1.25)
    ax.text(0, -0.13,
            "Sources: Alliance Regional Water Authority; partner-city ACFRs.",
            transform=ax.transAxes, fontsize=7, color=GRAY)

    fig.savefig(OUT / "hays_arwa_ramp.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_arwa_ramp.png'}")


if __name__ == "__main__":
    print("Building figures for 'Where the Water Will Come From'…")
    fig_demand()
    fig_aquifer_split()
    fig_arwa_ramp()
    print("Done.")
    print()
    print("REMINDER: values marked `# VERIFY` are placeholders.")
    print("Replace with TWDB / Region L / ARWA published figures before")
    print("the post goes live.")
