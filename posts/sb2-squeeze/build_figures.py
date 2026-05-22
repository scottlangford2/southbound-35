"""
Replication code for "The 3.5% Squeeze: SB 2 vs. a Doubling Tax Base
in Hays-Area Cities"
https://scottlangford2.github.io/scott_langford/posts/2026/05/sb2-squeeze/

All numerical values come from CSV inputs in `inputs/`. The CSVs contain
synthetic placeholder rows so the build runs on an empty checkout. Scott's
mf_scraper ACFR pipeline writes real values to those files before the post
goes live.

Usage:
    pip install -r requirements.txt
    python build_figures.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from econ_style import apply as apply_econ_style, COLORS, redbar, source_line, BG

apply_econ_style()

ROOT  = Path(__file__).parent
INPUT = ROOT / "inputs"
OUT   = ROOT / "figures"
OUT.mkdir(exist_ok=True)

CITIES = ["Kyle", "Buda", "San Marcos", "Dripping Springs"]

CITY_COLORS = {
    "Kyle":             COLORS["blue"],
    "Buda":             COLORS["green"],
    "San Marcos":       COLORS["yellow"],
    "Dripping Springs": COLORS["red"],
}

# Approximate fiscal year when ARWA infrastructure debt first appears
# in partner-city ACFR debt disclosures.
ARWA_START_YEAR = 2020


def _read_csv(name: str) -> pd.DataFrame:
    """Read a CSV from inputs/, treating lines starting with # as comments."""
    return pd.read_csv(INPUT / name, comment="#")


def fig_mo_rates() -> None:
    """
    Figure 1: 2x2 panel grid showing the adopted M&O rate, no-new-revenue
    rate, and voter-approval rate by fiscal year for each of the four
    Hays-area cities.

    The voter-approval rate (NNR x 1.035) acts as the legal ceiling for M&O
    revenue growth from existing property without triggering an automatic
    election under Texas Tax Code §26.04(c) (post-SB 2, 86th Legislature).
    """
    df = _read_csv("sb2_levy_vs_cap.csv").sort_values(["city", "year"])

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    axes_flat = axes.flatten()
    redbar(fig)

    for i, city in enumerate(CITIES):
        ax = axes_flat[i]
        cdf = df[df["city"] == city].copy()

        ax.set_title(city, fontsize=11, fontweight="bold", loc="left", pad=6)
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("Rate ($/100 AV)")
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.3f"))

        if cdf.empty:
            continue

        ax.plot(cdf["year"], cdf["no_new_revenue_rate"],
                color=COLORS["darkgray"], lw=1.6, ls="--",
                label="No-new-revenue rate")
        ax.plot(cdf["year"], cdf["voter_approval_rate"],
                color=COLORS["cyan"], lw=1.6, ls=":",
                label="Voter-approval rate (NNR +3.5%)")
        ax.plot(cdf["year"], cdf["actual_rate"],
                color=CITY_COLORS[city], lw=2.2, marker="o", ms=4,
                label="Adopted rate")

        if i == 0:
            ax.legend(fontsize=8, loc="upper right")

    fig.suptitle(
        "M&O Tax Rate vs. No-New-Revenue and Voter-Approval Rates\n"
        "Hays-Area Cities, Fiscal Years 2019-2024",
        fontsize=12, fontweight="bold", x=0.02, ha="left", y=1.01,
    )
    source_line(
        axes_flat[-1],
        "Sources: Texas Comptroller Truth-in-Taxation notices; city ACFRs "
        "(Scott's mf_scraper pipeline). Placeholder values; update from pipeline.",
        y=-0.20,
    )

    out_path = OUT / "sb2_mo_rates.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {out_path}")


def fig_tax_base_composition() -> None:
    """
    Figure 2: 2x2 stacked bar panel showing annual certified appraised value
    split between existing property and new construction for each city.

    New construction is excluded from the SB 2 voter-approval rate
    calculation; it is the primary escape valve for fast-growing cities
    whose existing-property revenue is capped at NNR x 1.035.
    """
    df = _read_csv("city_acfr_metrics.csv").sort_values(["city", "year"])

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    axes_flat = axes.flatten()
    redbar(fig)

    for i, city in enumerate(CITIES):
        ax = axes_flat[i]
        cdf = df[df["city"] == city].copy()

        ax.set_title(city, fontsize=11, fontweight="bold", loc="left", pad=6)
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("Certified value ($M)")
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"${v:,.0f}M")
        )

        if cdf.empty:
            continue

        years = cdf["year"].values
        existing = cdf["certified_value_existing"].values
        new_const = cdf["certified_value_new_construction"].values
        x = np.arange(len(years))
        width = 0.60

        ax.bar(x, existing, width,
               color=CITY_COLORS[city], alpha=0.85, label="Existing property")
        ax.bar(x, new_const, width, bottom=existing,
               color=COLORS["darkgray"], alpha=0.60, label="New construction")

        ax.set_xticks(x)
        ax.set_xticklabels(years, fontsize=8)

        if i == 0:
            ax.legend(fontsize=8, loc="upper left")

    fig.suptitle(
        "Certified Tax Base: Existing Property vs. New Construction\n"
        "Hays-Area Cities, Fiscal Years 2019-2024",
        fontsize=12, fontweight="bold", x=0.02, ha="left", y=1.01,
    )
    source_line(
        axes_flat[-1],
        "Sources: Hays Central Appraisal District certified rolls; city ACFRs "
        "(Scott's mf_scraper pipeline). Placeholder values; update from pipeline.",
        y=-0.20,
    )

    out_path = OUT / "sb2_tax_base_composition.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {out_path}")


def fig_debt_service_share() -> None:
    """
    Figure 3: Line chart showing the interest-and-sinking (I&S) debt service
    levy as a share of the total property tax levy for each city over time.

    A vertical reference line marks the approximate year ARWA infrastructure
    debt begins appearing in partner-city ACFR disclosures. Debt service is
    not subject to the SB 2 M&O cap but competes for the same levy capacity.
    """
    df = _read_csv("city_acfr_metrics.csv").sort_values(["city", "year"])

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    redbar(fig)

    for city in CITIES:
        cdf = df[df["city"] == city].copy()
        if cdf.empty:
            continue
        cdf["ds_share"] = cdf["debt_service_levy"] / cdf["total_levy"] * 100
        ax.plot(
            cdf["year"], cdf["ds_share"],
            color=CITY_COLORS[city], lw=2.0, marker="o", ms=5,
            label=city,
        )

    # ARWA annotation: only draw if the reference year is within the data window.
    all_years = df["year"].unique()
    if len(all_years) > 0:
        x_min, x_max = all_years.min(), all_years.max()
        if x_min <= ARWA_START_YEAR <= x_max:
            ax.axvline(ARWA_START_YEAR, color=COLORS["darkgray"],
                       lw=0.9, ls="--", alpha=0.8)
            y_top = ax.get_ylim()[1]
            ax.text(
                ARWA_START_YEAR + 0.2, y_top * 0.96,
                "ARWA\npartnership\nbegins",
                fontsize=7.5, color=COLORS["darkgray"],
                style="italic", va="top",
            )
        else:
            # Reference line is outside the displayed window; add a note instead.
            ax.text(
                0.02, 0.97,
                f"ARWA partnership began ~{ARWA_START_YEAR} (before displayed window)",
                transform=ax.transAxes,
                fontsize=7.5, color=COLORS["darkgray"],
                style="italic", va="top",
            )

    ax.set_xlabel("Fiscal year")
    ax.set_ylabel("I&S levy as % of total levy")
    ax.set_title(
        "Debt-Service Share of Total Property Tax Levy\n"
        "Hays-Area Cities, Fiscal Years 2019-2024"
    )
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.legend(fontsize=9, loc="upper left")
    source_line(
        ax,
        "Sources: City ACFRs (Scott's mf_scraper pipeline); ARWA partnership documents. "
        "Placeholder values; update from pipeline.",
    )

    out_path = OUT / "sb2_debt_service_share.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {out_path}")


if __name__ == "__main__":
    print("Building figures for 'The 3.5% Squeeze'...")
    fig_mo_rates()
    fig_tax_base_composition()
    fig_debt_service_share()
    print("Done.")
    print()
    print("Reminder: input CSVs contain SYNTHETIC PLACEHOLDER values.")
    print("Update inputs/ from Scott's mf_scraper ACFR pipeline, then re-run.")
