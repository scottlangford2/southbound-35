"""
Replication code for the Hays CISD schools post.
https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-schools/

Generates two figures:
  1. The squeeze: enrollment, property tax base, and per-student revenue
     indexed to 2020 = 100
  2. The split vote: HCISD bond (May 2025) vs M&O Tax Rate Election
     (November 2025)

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

RED    = COLORS["red"]
BLUE   = COLORS["blue"]
GREEN  = COLORS["green"]
YELLOW = COLORS["yellow"]
GRAY   = COLORS["darkgray"]
DPI    = 150

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)


def fig_squeeze():
    """Figure 1: enrollment vs. tax base vs. per-student revenue (indexed)."""
    years = np.array([2020, 2021, 2022, 2023, 2024, 2025])

    # Hays CISD enrollment (estimated): ~21K → 25.6K over 6 years.
    enrollment = np.array([21_000, 22_000, 22_800, 23_500, 24_400, 25_590])

    # Hays CISD taxable property value (rough composite from HCAD and
    # district budget documents, indexed). The Hill Country market boom
    # of 2022 drove the steep midpoint; 2024 added ~8.83 % and 2026
    # estimates were +9.7 % county-wide.
    tax_base = np.array([100, 108, 134, 145, 158, 173])  # index = 100 in 2020

    # M&O revenue per student. Texas's $6,160 basic allotment has been
    # essentially flat since 2019, and the state compresses the local
    # M&O rate as values rise. We index per-student M&O at roughly
    # +1 to +2 percent per year — a small real decline in inflation-
    # adjusted terms.
    rev_per_student = np.array([100, 101, 102, 103, 104, 105])

    enr_idx = enrollment / enrollment[0] * 100

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    redbar(fig)

    ax.plot(years, tax_base, color=YELLOW, lw=2.5, marker="s", ms=6,
            label="Taxable property value")
    ax.plot(years, enr_idx, color=BLUE, lw=2.5, marker="o", ms=6,
            label="Enrollment")
    ax.plot(years, rev_per_student, color=GRAY, lw=2.5, marker="D", ms=5,
            label="M&O revenue per student")

    # End-of-line labels
    ax.annotate(f"+{tax_base[-1]-100:.0f}%", (years[-1], tax_base[-1]),
                xytext=(8, 0), textcoords="offset points",
                fontsize=9, fontweight="bold", color=YELLOW, va="center")
    ax.annotate(f"+{enr_idx[-1]-100:.0f}%", (years[-1], enr_idx[-1]),
                xytext=(8, 0), textcoords="offset points",
                fontsize=9, fontweight="bold", color=BLUE, va="center")
    ax.annotate(f"+{rev_per_student[-1]-100:.0f}%", (years[-1], rev_per_student[-1]),
                xytext=(8, 0), textcoords="offset points",
                fontsize=9, fontweight="bold", color=GRAY, va="center")

    ax.axhline(100, color="black", lw=0.8, alpha=0.4)

    ax.set_ylabel("Index, 2020 = 100")
    ax.set_title("The Squeeze: Tax Base Up, Enrollment Up, Revenue Flat")
    ax.set_xlim(2019.5, 2026.5)
    ax.set_ylim(90, 200)
    ax.legend(loc="upper left")
    source_line(ax,
                "Sources: Hays CISD budget documents; Hays Central Appraisal District; "
                "Texas Education Agency basic-allotment rules. Tax base and revenue indexed "
                "from author calculations.",
                y=-0.16)

    fig.savefig(OUT / "hays_schools_squeeze.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_schools_squeeze.png'}")


def fig_split_vote():
    """Figure 2: May 2025 bond vs. November 2025 M&O TRE."""
    labels = ["May 2025 bond\n(Prop A)\nSchool construction",
              "November 2025 TRE\n(+12¢ M&O)\nOperating budget"]
    yes_pct = [60.0, 40.3]
    no_pct  = [40.0, 59.8]

    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    redbar(fig)

    bars_yes = ax.bar(x - width/2, yes_pct, width,
                       color=[GREEN, GRAY], label="Yes")
    bars_no  = ax.bar(x + width/2, no_pct, width,
                       color=[GRAY, RED], label="No")

    for b, v in zip(bars_yes, yes_pct):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5,
                f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold", color="#333")
    for b, v in zip(bars_no, no_pct):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5,
                f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold", color="#333")

    ax.axhline(50, color="black", lw=0.8, ls="--", alpha=0.5)
    ax.text(0.5, 51.5, "50% threshold", fontsize=8, color="#555",
            ha="center", style="italic")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Percent of votes")
    ax.set_title("Six Months Apart, Opposite Answers")
    ax.set_ylim(0, 80)
    ax.legend(loc="upper right")
    source_line(ax,
                "Sources: Hays County Elections, May 3 and November 4, 2025. "
                "Bond Proposition A funded school construction and expansion; "
                "the TRE would have raised the maintenance & operations tax rate.",
                y=-0.22)

    fig.savefig(OUT / "hays_schools_split_vote.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_schools_split_vote.png'}")


if __name__ == "__main__":
    print("Building figures for the Hays CISD schools post…")
    fig_squeeze()
    fig_split_vote()
    print("Done.")
