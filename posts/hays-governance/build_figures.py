"""
Replication code for "Who Governs Hays County?" — the closing post in
the Hays County series on overlapping jurisdictions.
https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-governance/

Generates two figures:
  1. Property-tax composition across three typical Hays County addresses
  2. Count of governing/taxing entities by typical address

Usage:
    pip install -r requirements.txt
    python build_figures.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import numpy as np

from econ_style import apply as apply_econ_style, COLORS, redbar, source_line

apply_econ_style()

RED      = COLORS["red"]
BLUE     = COLORS["blue"]
GREEN    = COLORS["green"]
YELLOW   = COLORS["yellow"]
PURPLE   = COLORS["purple"]
CYAN     = COLORS["cyan"]
GRAY     = COLORS["darkgray"]
TAN      = COLORS["tan"]
OLIVE    = COLORS["olive"]
DPI      = 150

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)


def fig_tax_stack():
    """Figure 1: Stacked tax rates for three typical Hays County addresses."""

    # 2025 effective rates per $100 of taxable value.
    # Layers ordered bottom-to-top: County, School district, City (or 0),
    # ESD, MUD/WCID (or 0). Sources: Hays CAD, BPTP summary,
    # district websites.
    archetypes = [
        "Kyle\n(in-city)",
        "Buda\n(in-city)",
        "Unincorporated\n(MUD-served)",
    ]

    county   = [0.3999, 0.3999, 0.3999]
    school   = [1.1546, 1.1546, 1.1546]  # HCISD for all three archetypes
    city     = [0.5957, 0.3576, 0.0000]
    esd      = [0.1000, 0.1000, 0.1000]
    mud_wcid = [0.0000, 0.0000, 0.6500]  # typical MUD/WCID supplemental

    layers = [
        ("Hays County",            county,   GRAY),
        ("Hays CISD",              school,   BLUE),
        ("City (Kyle or Buda)",    city,     RED),
        ("Emergency Services Dist.", esd,    YELLOW),
        ("MUD or WCID",            mud_wcid, GREEN),
    ]

    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    redbar(fig)

    x = np.arange(len(archetypes))
    width = 0.55
    bottom = np.zeros(len(archetypes))

    for name, vals, color in layers:
        ax.bar(x, vals, width, bottom=bottom, color=color, label=name,
               edgecolor="white", linewidth=0.6)
        bottom = bottom + np.array(vals)

    # Total label at top of each bar
    for i, total in enumerate(bottom):
        ax.text(i, total + 0.04, f"${total:.2f}",
                ha="center", fontsize=11, fontweight="bold", color="#1A1A1A")

    ax.set_xticks(x)
    ax.set_xticklabels(archetypes, fontsize=10)
    ax.set_ylabel("Property tax rate per $100 valuation")
    ax.set_title("How Many Layers Tax a Hays County Homeowner")
    ax.set_ylim(0, 3.0)
    ax.legend(loc="upper left", fontsize=8)
    source_line(ax,
                "Sources: Hays Central Appraisal District (2025 tax rates); Hays County; HCISD; "
                "city budgets; ESD and MUD rate filings.\nMUD/WCID rate shown is a typical 65¢ "
                r"supplemental rate; actual rates range from ~\$0.20 to over \$1.00.",
                y=-0.18)

    fig.savefig(OUT / "hays_governance_tax_stack.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_governance_tax_stack.png'}")


def fig_entity_count():
    """Figure 2: Count of distinct governing/taxing entities by address type."""

    archetypes = [
        "Inside a city\n(e.g., Kyle, Buda)",
        "Unincorporated\nin a MUD",
        "Rural / outside\nany district",
    ]

    # Count of distinct entities that tax, regulate, or provide services
    # to a typical address in each archetype. Counts include both elected
    # bodies (e.g., city council, ESD board) and quasi-governmental
    # entities (HOAs, river authorities) the homeowner interacts with.
    entities = {
        "Federal / state":         [2, 2, 2],   # USA, State of Texas
        "County government":       [1, 1, 1],   # Hays County
        "School district":         [1, 1, 1],   # HCISD or SMCISD
        "Appraisal district":      [1, 1, 1],   # Hays CAD (1 board, shared)
        "City government":         [1, 0, 0],
        "Emergency Services Dist.": [1, 1, 1],   # at least one
        "MUD / WCID / PID":        [0, 1, 0],
        "Groundwater conservation": [1, 1, 1],   # Hays Trinity or EAA
        "River authority (GBRA/LCRA)": [1, 1, 1],
        "HOA / property owners assn.": [1, 1, 0],
    }

    x = np.arange(len(archetypes))
    width = 0.55
    bottom = np.zeros(len(archetypes))

    palette = [
        GRAY, GRAY, BLUE, GRAY, RED, YELLOW, GREEN, CYAN, PURPLE, TAN
    ]

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    redbar(fig)

    for (name, vals), color in zip(entities.items(), palette):
        ax.bar(x, vals, width, bottom=bottom, color=color, label=name,
               edgecolor="white", linewidth=0.6)
        bottom = bottom + np.array(vals)

    # Total label at top
    for i, total in enumerate(bottom):
        ax.text(i, total + 0.12, f"{int(total)} entities",
                ha="center", fontsize=11, fontweight="bold", color="#1A1A1A")

    ax.set_xticks(x)
    ax.set_xticklabels(archetypes, fontsize=10)
    ax.set_ylabel("Number of governing entities")
    ax.set_title("Who Governs a Hays County Address")
    ax.set_ylim(0, 12.5)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8,
              frameon=False)
    source_line(ax,
                "Sources: Hays County government structure; District Directory; Hays CAD.\n"
                "Counts include federal and state governments plus all local entities with "
                "taxing, regulatory, or service-delivery authority.",
                y=-0.18)

    fig.savefig(OUT / "hays_governance_entity_count.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_governance_entity_count.png'}")


if __name__ == "__main__":
    print("Building figures for 'Who Governs Hays County?'…")
    fig_tax_stack()
    fig_entity_count()
    print("Done.")
