"""
Replication code for "Where the Water Will Come From"
https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-water/

All numerical values come from CSV inputs in `inputs/`. To update a
figure, update the corresponding CSV and re-run this script. No values
are hardcoded in this file.

Inputs:
    inputs/twdb_water_use_hays.csv     # historical + projected demand
    inputs/aquifer_assignments.csv     # cities by source aquifer
    inputs/arwa_phases.csv             # ARWA imported-supply ramp

Outputs (PNG):
    figures/hays_water_demand.png
    figures/hays_aquifer_split.png
    figures/hays_arwa_ramp.png

Usage:
    pip install -r requirements.txt
    python build_figures.py
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
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

ROOT   = Path(__file__).parent
INPUT  = ROOT / "inputs"
OUT    = ROOT / "figures"
OUT.mkdir(exist_ok=True)


def _read_csv(name):
    """Read a CSV from inputs/, treating # lines as comments."""
    path = INPUT / name
    return pd.read_csv(path, comment="#")


def fig_demand():
    """Hays County water demand, historical and projected, by category."""
    df = _read_csv("twdb_water_use_hays.csv").sort_values("year")

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.stackplot(
        df["year"],
        df["municipal"], df["irrigation"], df["mining"], df["manufacturing"],
        labels=["Municipal", "Irrigation", "Mining", "Manufacturing"],
        colors=[BLUE, GREEN, ORANGE, GRAY], alpha=0.85,
    )

    # Mark the historical/projection boundary at the last historical
    # year present in the CSV. We treat anything <= 2025 as historical.
    historical = df[df["year"] <= 2025]
    if not historical.empty:
        boundary = historical["year"].max()
        ax.axvline(boundary, color="#555", lw=1, ls="--", alpha=0.6)
        ax.text(boundary + 0.5, ax.get_ylim()[1] * 0.92, "projected →",
                fontsize=8.5, color="#555", style="italic")

    ax.set_xlabel("Year")
    ax.set_ylabel("Demand (thousand acre-feet/yr)")
    ax.set_title("Hays County Water Demand: Historical and Projected")
    ax.set_xlim(df["year"].min(), df["year"].max())
    ax.legend(loc="upper left")
    ax.text(0, -0.12,
            "Sources: TWDB Historical Water Use Estimates; "
            "TWDB 2026 RWP Board-Adopted Demand Projections.",
            transform=ax.transAxes, fontsize=7, color=GRAY)

    fig.savefig(OUT / "hays_water_demand.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_water_demand.png'}")


def fig_aquifer_split():
    """Hays cities arrayed east–west by source aquifer (schematic)."""
    df = _read_csv("aquifer_assignments.csv")
    color_map = {"Trinity": ORANGE, "Edwards": BLUE}

    fig, ax = plt.subplots(figsize=(7.0, 3.6))

    # Stylized recharge-zone band: the Edwards recharge zone is a thin
    # diagonal along I-35; here we draw it between the easternmost
    # Trinity city and the westernmost Edwards city for legibility.
    trinity = df[df["aquifer"] == "Trinity"]["schematic_longitude"]
    edwards = df[df["aquifer"] == "Edwards"]["schematic_longitude"]
    if not trinity.empty and not edwards.empty:
        band_left = trinity.max() + 0.01
        band_right = edwards.min() - 0.01
        ax.axvspan(band_left, band_right, color="#FFE4B5", alpha=0.7,
                   label="Edwards recharge zone (schematic)")

    for _, row in df.iterrows():
        color = color_map.get(row["aquifer"], GRAY)
        ax.scatter(row["schematic_longitude"], 1, s=160, color=color,
                   zorder=5, edgecolor="white", linewidth=1.2)
        ax.annotate(row["city"].replace(" ", "\n", 1) if " " in row["city"]
                    and len(row["city"]) > 9 else row["city"],
                    (row["schematic_longitude"], 1), xytext=(0, 14),
                    textcoords="offset points", ha="center",
                    fontsize=9, fontweight="bold")
        ax.annotate(row["aquifer"], (row["schematic_longitude"], 1),
                    xytext=(0, -22), textcoords="offset points",
                    ha="center", fontsize=8, color=color, style="italic")

    pad = 0.06
    ax.set_xlim(df["schematic_longitude"].min() - pad,
                df["schematic_longitude"].max() + pad)
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
    """ARWA imported supply by phase, MGD, across partner cities."""
    df = _read_csv("arwa_phases.csv").sort_values("year_online")

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.step(df["year_online"], df["cumulative_mgd"],
            where="post", color=BLUE, lw=2.5, zorder=3)
    ax.fill_between(df["year_online"], 0, df["cumulative_mgd"],
                    step="post", color=BLUE, alpha=0.18)

    for _, row in df.iterrows():
        if row["cumulative_mgd"] > 0:
            ax.scatter(row["year_online"], row["cumulative_mgd"],
                       color=BLUE, s=60, zorder=5,
                       edgecolor="white", linewidth=1.2)
            ax.annotate(f"{row['phase']}\n{row['cumulative_mgd']:.0f} MGD",
                        (row["year_online"], row["cumulative_mgd"]),
                        xytext=(6, 8), textcoords="offset points",
                        fontsize=8.5, fontweight="bold")

    # "today" line at 2025 (boundary between completed and planned)
    today = 2025
    ax.axvline(today, color="#555", lw=1, ls="--", alpha=0.6)
    ax.text(today + 0.5, ax.get_ylim()[1] * 0.05, "today",
            fontsize=8.5, color="#555", style="italic")

    ax.set_xlabel("Year online")
    ax.set_ylabel("Cumulative imported supply (MGD)")
    ax.set_title("ARWA Imported Supply: Phase Ramp-Up")
    ax.set_xlim(df["year_online"].min() - 2, df["year_online"].max() + 5)
    ax.set_ylim(0, df["cumulative_mgd"].max() * 1.25)
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
    print("Reminder: input CSVs in `inputs/` contain placeholder values.")
    print("Update them with TWDB / ARWA published figures, then re-run.")
