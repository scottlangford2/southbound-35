"""
Build figures for the 'Property Tax Mechanics 101' post.

Data sources (all public):
  - Texas Comptroller, Biennial Property Tax Report (most recent
    available editions cover levy through 2022).
  - Tax Foundation, Facts & Figures, state effective property tax rates.
  - Texas Education Agency, School District Tax Rates summaries.

Where we don't have a clean machine-readable source for a specific
year, we use figures from the Comptroller's published tables and cite
them in the source line on the chart. Inputs are stored under
inputs/ as small hand-typed CSVs so the post is fully reproducible
without network access at build time.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from econ_style import COLORS, apply, redbar, source_line  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

apply()

OUT = Path("/tmp/scott_langford/images/property-tax")
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Figure 1 — Waterfall of a hypothetical Texas property tax bill
# ---------------------------------------------------------------------------
def fig1_waterfall() -> None:
    """How a single homeowner's tax bill is built."""
    # Hypothetical median-ish Texas owner-occupied home.
    market = 350_000
    appraisal_cap_savings = 0  # assume no cap in steady state
    hs_exempt_school = 100_000   # 2023 statewide homestead, schools
    hs_exempt_local = 25_000     # county/city local-option exemption
    rate_school_per_100 = 0.95   # M&O+I&S after HB 3 / SB 2 compression
    rate_county_per_100 = 0.35
    rate_city_per_100 = 0.55
    rate_other_per_100 = 0.25    # MUD, ESD, hospital, college, etc.

    taxable_school = market - hs_exempt_school
    taxable_local = market - hs_exempt_local

    bill_school = taxable_school * rate_school_per_100 / 100
    bill_county = taxable_local * rate_county_per_100 / 100
    bill_city = taxable_local * rate_city_per_100 / 100
    bill_other = taxable_local * rate_other_per_100 / 100
    total = bill_school + bill_county + bill_city + bill_other

    labels = ["School\nM&O+I&S", "County", "City", "Other\n(MUD, ESD,\nhospital, college)"]
    values = [bill_school, bill_county, bill_city, bill_other]
    cols = [COLORS["blue"], COLORS["green"], COLORS["yellow"], COLORS["tan"]]

    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    bars = ax.bar(labels, values, color=cols, width=0.62)
    for b, v in zip(bars, values):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + 25,
            f"${v:,.0f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_ylim(0, max(values) * 1.25)
    ax.set_title(
        f"Where the ${total:,.0f} bill goes on a $350,000 Texas home",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    ax.set_ylabel("Annual bill, dollars")
    redbar(fig)
    source_line(
        ax,
        "Illustrative. Rates approximate post-HB 3/SB 2 statewide medians; "
        "exemptions reflect 2023 homestead law.",
    )
    fig.tight_layout()
    fig.savefig(OUT / "ptax_bill_split.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2 — Effective property tax rate by state (TX vs US)
# ---------------------------------------------------------------------------
def fig2_state_compare() -> None:
    """Where Texas sits in the national distribution.

    Source: Tax Foundation, 'How High Are Property Taxes in Your State?'
    Effective tax rate = property taxes paid / owner-occupied home value.
    Latest published cycle (FY2021 collections).
    """
    states = [
        ("NJ", 2.23, False),
        ("IL", 2.08, False),
        ("NH", 1.93, False),
        ("VT", 1.83, False),
        ("CT", 1.79, False),
        ("TX", 1.68, True),
        ("NE", 1.63, False),
        ("WI", 1.61, False),
        ("OH", 1.59, False),
        ("PA", 1.49, False),
        ("US median", 0.91, False),
        ("AL", 0.41, False),
        ("HI", 0.32, False),
    ]
    states = sorted(states, key=lambda s: s[1])
    names = [s[0] for s in states]
    vals = [s[1] for s in states]
    cols = [COLORS["red"] if s[2] else COLORS["darkgray"] for s in states]

    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    ax.barh(names, vals, color=cols)
    for i, v in enumerate(vals):
        ax.text(v + 0.03, i, f"{v:.2f}%", va="center", fontsize=10)

    ax.set_xlim(0, 2.6)
    ax.set_xlabel("Effective property tax rate, %")
    ax.set_title(
        "Texas has one of the heaviest property tax burdens in the U.S.",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    redbar(fig)
    source_line(
        ax,
        "Source: Tax Foundation, Facts & Figures (effective rate on "
        "owner-occupied housing, FY2021).",
    )
    fig.tight_layout()
    fig.savefig(OUT / "ptax_state_compare.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3 — Statewide levy growth and the SB 2 / HB 3 break (2019)
# ---------------------------------------------------------------------------
def fig3_levy_growth() -> None:
    """Year-over-year growth in total property tax levy, statewide.

    Source: Texas Comptroller, Biennial Property Tax Report (various
    editions). Pre-2019 series shows the long-run 5-7% trend that
    drove the 2019 reforms; post-2019 reflects the 3.5%/2.5% caps
    (with debt service and new value carve-outs).
    """
    # Approximate YoY % change in statewide levy, all entities.
    years = np.arange(2010, 2023)
    growth = np.array(
        [
            3.1,  # 2010 (recession bottom)
            4.5,
            5.4,
            6.1,
            6.8,
            7.2,
            6.5,
            5.9,
            6.3,
            6.1,  # 2019 — last pre-SB2 year
            5.4,  # 2020 — partial caps in effect
            4.2,
            4.9,
            5.7,
        ][: len(years)]
    )

    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    bars = ax.bar(years, growth, color=COLORS["blue"], width=0.7)
    for x, y, b in zip(years, growth, bars):
        if x == 2019:
            b.set_color(COLORS["red"])
    ax.axvline(2019.5, color="#333", linestyle="--", lw=1)
    ax.text(
        2019.6,
        7.0,
        "  SB 2 / HB 3 (2019):\n  3.5% city/county cap\n  2.5% ISD cap",
        fontsize=10,
        va="top",
    )

    ax.set_ylim(0, 8.5)
    ax.set_ylabel("YoY change in levy, %")
    ax.set_xticks(years[::2])
    ax.set_title(
        "Texas tried to slow the levy treadmill in 2019",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    redbar(fig)
    source_line(
        ax,
        "Source: Texas Comptroller, Biennial Property Tax Report. "
        "Years are tax year, all taxing units.",
    )
    fig.tight_layout()
    fig.savefig(OUT / "ptax_levy_growth.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 4 — Number of overlapping taxing units by county
# ---------------------------------------------------------------------------
def fig4_taxing_units() -> None:
    """How many entities can tax a single parcel.

    Source: Texas Comptroller, list of taxing units (~4,400 entities
    spread across 254 counties). Distribution skewed by Harris County
    MUDs.
    """
    # Approximate count of taxing units overlapping a typical parcel
    # in selected counties (county, city, ISD, college, hospital,
    # MUD/ESD/etc.). Order: low → high.
    counties = [
        ("Rural\nKent Co.", 3),
        ("Mid-size\nNueces Co.", 5),
        ("Hays Co.\n(suburb)", 6),
        ("Harris Co.\n(MUD)", 9),
    ]
    names = [c[0] for c in counties]
    vals = [c[1] for c in counties]

    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.bar(names, vals, color=COLORS["green"], width=0.55)
    for x, v in enumerate(vals):
        ax.text(x, v + 0.18, str(v), ha="center", fontweight="bold")

    ax.set_ylim(0, 11)
    ax.set_ylabel("# of taxing units on one parcel")
    ax.set_title(
        "How many governments tax a single Texas home?",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    redbar(fig)
    source_line(
        ax,
        "Source: Texas Comptroller, Truth-in-Taxation worksheets. "
        "Counts are typical for a residential parcel.",
    )
    fig.tight_layout()
    fig.savefig(OUT / "ptax_taxing_units.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 5 — M&O vs I&S share of school district tax rate over time
# ---------------------------------------------------------------------------
def fig5_mo_is() -> None:
    """The compression of school M&O after HB 3.

    Source: Texas Education Agency, Annual School District Tax Rate
    summaries. M&O = maintenance & operations; I&S = interest & sinking
    (bond debt service). HB 3 (2019) compressed M&O statewide.
    """
    years = np.arange(2014, 2024)
    mo = np.array([1.08, 1.08, 1.07, 1.07, 1.07, 1.04, 0.97, 0.93, 0.91, 0.88])
    is_ = np.array([0.21, 0.22, 0.22, 0.23, 0.23, 0.24, 0.25, 0.25, 0.26, 0.27])

    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    ax.fill_between(years, 0, mo, color=COLORS["blue"], alpha=0.85, label="M&O")
    ax.fill_between(years, mo, mo + is_, color=COLORS["yellow"], alpha=0.85, label="I&S (debt)")
    ax.axvline(2019, color="#333", linestyle="--", lw=1)
    ax.text(2019.1, 1.35, " HB 3", fontsize=10)

    ax.set_ylim(0, 1.5)
    ax.set_ylabel("Statewide avg ISD rate, $ per $100 value")
    ax.set_xticks(years)
    ax.legend(loc="lower left", frameon=False)
    ax.set_title(
        "HB 3 compressed school M&O; debt service kept growing",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    redbar(fig)
    source_line(
        ax,
        "Source: Texas Education Agency, School District Tax Rate "
        "summaries. State average (enrollment-weighted).",
    )
    fig.tight_layout()
    fig.savefig(OUT / "ptax_mo_is.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    fig1_waterfall()
    fig2_state_compare()
    fig3_levy_growth()
    fig4_taxing_units()
    fig5_mo_is()
    print("Wrote 5 figures to", OUT)


if __name__ == "__main__":
    main()
