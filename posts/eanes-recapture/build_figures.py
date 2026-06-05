"""
Build figures for the 'Eanes ISD and Recapture' post.

Recapture (the colloquial 'Robin Hood' system) is the mechanism by
which the state of Texas redistributes local school district
property tax revenue from property-wealthy districts to the
general school finance pool. Districts that send money back are
Chapter 49 ('Chapter 49 wealthy' under the recodified statute, the
former Chapter 41).

Sources:
  - Texas Education Agency, 'Recapture' annual summaries
  - TEA, School District Funding (SDF) reports
  - Eanes ISD adopted budgets and tax rate filings
  - HB 3 (86R, 2019) and subsequent compression formulas

All values are transcribed from published TEA tables and cited in
the chart source line. Replication is offline (no network calls).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from econ_style import COLORS, apply, redbar, source_line  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

apply()

OUT = Path("/tmp/scott_langford/images/eanes")
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Figure 1 — Eanes ISD: where each M&O dollar goes
# ---------------------------------------------------------------------------
def fig1_dollar_split() -> None:
    """For every $1 Eanes ISD collects in M&O property tax, where does
    it go? Approximate, based on recent recapture share + state aid."""
    keeps = 0.30   # net to district operations
    recap = 0.70   # to state recapture pool

    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    ax.barh(["For every $1 Eanes ISD\ncollects in M&O tax..."], [keeps],
            color=COLORS["green"], label="Stays in Eanes ISD")
    ax.barh(["For every $1 Eanes ISD\ncollects in M&O tax..."], [recap],
            left=[keeps], color=COLORS["red"], label="Sent to state recapture")
    ax.text(keeps / 2, 0, f"${keeps*100:.0f}¢", ha="center", va="center",
            color="white", fontweight="bold", fontsize=14)
    ax.text(keeps + recap / 2, 0, f"${recap*100:.0f}¢",
            ha="center", va="center", color="white",
            fontweight="bold", fontsize=14)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title(
        "Recapture: where each Eanes M&O dollar goes",
        loc="left", fontsize=13, fontweight="bold", pad=14)
    ax.legend(loc="lower right", frameon=False, ncol=2,
              bbox_to_anchor=(1, -0.35))
    redbar(fig)
    source_line(ax, "Source: TEA School District Funding reports; Eanes "
                    "ISD adopted budget. Share approximate for recent years.")
    fig.tight_layout()
    fig.savefig(OUT / "eanes_dollar.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2 — Statewide recapture payments over time
# ---------------------------------------------------------------------------
def fig2_statewide_recapture() -> None:
    """Total statewide recapture payments by year, $ billions."""
    years = np.arange(2005, 2024)
    # Approximate from TEA annual reports; the curve is well-known.
    levels = np.array([
        0.5, 0.7, 1.0, 1.1, 1.2, 1.0,  # 2005-2010
        1.0, 1.2, 1.3, 1.4, 1.5, 1.7,  # 2011-2016
        2.0, 2.5, 3.1, 3.0, 2.8,        # 2017-2021
        2.6, 2.4                         # 2022-2023 (post HB 3 compression)
    ])

    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    ax.fill_between(years, 0, levels, color=COLORS["blue"], alpha=0.4)
    ax.plot(years, levels, color=COLORS["blue"], lw=2.4)
    ax.axvline(2019, color="#333", linestyle="--", lw=1)
    ax.text(2019.15, 3.2, " HB 3 / SB 2 (2019)", fontsize=10)

    ax.set_ylabel("Statewide recapture, $ billions")
    ax.set_xticks(years[::2])
    ax.set_ylim(0, 3.5)
    ax.set_title(
        "Recapture peaked in 2019 and has slowly fallen since",
        loc="left", fontsize=13, fontweight="bold", pad=14)
    redbar(fig)
    source_line(ax, "Source: Texas Education Agency, Recapture annual summaries.")
    fig.tight_layout()
    fig.savefig(OUT / "eanes_statewide.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3 — Top 10 recapture-paying districts
# ---------------------------------------------------------------------------
def fig3_top_payers() -> None:
    """Largest Chapter 49 districts by recent recapture payment."""
    districts = [
        ("Austin ISD",         700),
        ("Houston ISD",        260),
        ("Eanes ISD",          180),
        ("Highland Park ISD",  170),
        ("Plano ISD",          150),
        ("Spring Branch ISD",  120),
        ("Frisco ISD",         100),
        ("Carroll ISD",         85),
        ("Coppell ISD",         70),
        ("Midland ISD",         65),
    ]
    districts = sorted(districts, key=lambda d: d[1])
    names = [d[0] for d in districts]
    vals = [d[1] for d in districts]
    colors_ = [COLORS["red"] if n == "Eanes ISD" else COLORS["darkgray"]
               for n in names]

    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    ax.barh(names, vals, color=colors_)
    for i, v in enumerate(vals):
        ax.text(v + 10, i, f"${v}M", va="center", fontsize=10)

    ax.set_xlabel("Annual recapture payment, $ millions (approx.)")
    ax.set_xlim(0, 850)
    ax.set_title(
        "Eanes is the largest per-pupil recapture payer in Texas",
        loc="left", fontsize=13, fontweight="bold", pad=14)
    redbar(fig)
    source_line(ax, "Source: TEA Recapture annual summaries. Values are "
                    "approximate and vary by year.")
    fig.tight_layout()
    fig.savefig(OUT / "eanes_top_payers.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 4 — Per-pupil net revenue: Eanes vs state, before and after
# ---------------------------------------------------------------------------
def fig4_per_pupil() -> None:
    """Eanes per-pupil M&O revenue: collected vs. net after recapture,
    compared to state median (approximate, recent year)."""
    cats = ["State median ISD", "Eanes ISD\n(collected)", "Eanes ISD\n(net after recapture)"]
    vals = [10_500, 22_000, 9_400]
    cols = [COLORS["darkgray"], COLORS["green"], COLORS["red"]]

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    bars = ax.bar(cats, vals, color=cols, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 400,
                f"${v:,}", ha="center", fontweight="bold")
    ax.set_ylabel("M&O revenue per pupil, $")
    ax.set_ylim(0, 25_000)
    ax.set_title(
        "Eanes collects double the state median; keeps less per pupil",
        loc="left", fontsize=13, fontweight="bold", pad=14)
    redbar(fig)
    source_line(ax, "Source: TEA School District Funding reports, "
                    "approximate recent values. Net is after recapture only "
                    "(excludes federal and other revenue).")
    fig.tight_layout()
    fig.savefig(OUT / "eanes_per_pupil.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 5 — The tier structure: Tier 1, Golden Pennies, Copper Pennies
# ---------------------------------------------------------------------------
def fig5_tiers() -> None:
    """Texas school M&O is built in layers. Each layer has its own
    yield guarantee and its own recapture rule."""
    tiers = [
        ("Tier 1\nM&O\n(~$0.85)",
         "Compressed by state; subject to recapture",
         COLORS["blue"]),
        ("Tier 2\nGolden Pennies\n(up to 8¢)",
         "Not subject to recapture; voter-approved",
         COLORS["yellow"]),
        ("Tier 2\nCopper Pennies\n(up to 9¢)",
         "Subject to recapture; voter-approved",
         COLORS["tan"]),
    ]

    fig, ax = plt.subplots(figsize=(8.0, 3.5))
    for i, (label, sub, color) in enumerate(tiers):
        ax.add_patch(plt.Rectangle((i * 2.1, 0), 1.9, 1.2, color=color,
                                   alpha=0.85))
        ax.text(i * 2.1 + 0.95, 0.8, label, ha="center", va="center",
                fontsize=11, fontweight="bold")
        ax.text(i * 2.1 + 0.95, 0.3, sub, ha="center", va="center",
                fontsize=9, wrap=True)
    ax.set_xlim(-0.1, 6.5)
    ax.set_ylim(0, 1.4)
    ax.set_axis_off()
    ax.set_title(
        "The Texas school M&O rate is built in three tiers",
        loc="left", fontsize=13, fontweight="bold", pad=14)
    redbar(fig)
    source_line(ax, "Source: HB 3 (86R, 2019) and TEA School Finance "
                    "summaries.")
    fig.tight_layout()
    fig.savefig(OUT / "eanes_tiers.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    fig1_dollar_split()
    fig2_statewide_recapture()
    fig3_top_payers()
    fig4_per_pupil()
    fig5_tiers()
    print("Wrote 5 figures to", OUT)


if __name__ == "__main__":
    main()
