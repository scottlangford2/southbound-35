"""
Replication code for "Who Will Care for Them?
America's Coming Alzheimer's Caregiver Shortage".

All numerical values come from CSV inputs under `inputs/`. The script
is purely a renderer.

Usage:
    pip install -r requirements.txt
    python build_figures.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from econ_style import apply as apply_econ_style, COLORS, redbar, source_line, BG

apply_econ_style()

DPI = 150
ROOT = Path(__file__).parent
INPUT = ROOT / "inputs"
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)


def _read_csv(name):
    """Read a CSV from inputs/, treating # lines as comments."""
    return pd.read_csv(INPUT / name, comment="#")


def fig_prevalence_vs_workforce():
    """Alzheimer's cases vs. direct-care workforce, 2020-2040.

    Two demand scenarios (Alz Assoc all-ages clinical, CMS Medicare FFS
    diagnosed) drawn as a shaded band against the projected paid
    direct-care workforce. The 2033 dividing line marks where the BLS
    Employment Projections horizon ends; the post-2033 segment is the
    2023-2033 CAGR extrapolated forward.
    """
    prev = _read_csv("alz_prevalence.csv")
    work = _read_csv("direct_care_workforce.csv")

    upper = prev[prev["scenario"] == "alz_assoc"].sort_values("year")
    lower = prev[prev["scenario"] == "cms_medicare_ffs"].sort_values("year")

    workforce = (work.groupby("year")["employment_thousands"].sum() / 1000.0
                 ).reset_index().sort_values("year")
    workforce = workforce.rename(columns={"employment_thousands": "millions"})

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    redbar(fig)

    common_lower = lower["year"].max()
    upper_in_range = upper[upper["year"] <= 2040]
    lower_in_range = lower[lower["year"] <= common_lower]
    band_years = upper_in_range["year"].values
    band_top = upper_in_range["cases_millions"].values
    band_bottom = np.interp(band_years, lower_in_range["year"],
                            lower_in_range["cases_millions"])
    ax.fill_between(band_years, band_bottom, band_top,
                    color=COLORS["red"], alpha=0.16,
                    label="Alzheimer's cases (range across data sources)")
    ax.plot(upper_in_range["year"], upper_in_range["cases_millions"],
            color=COLORS["red"], lw=2.0)
    ax.plot(lower_in_range["year"], lower_in_range["cases_millions"],
            color=COLORS["red"], lw=2.0, alpha=0.55)

    history = workforce[workforce["year"] <= 2033]
    future = workforce[workforce["year"] >= 2033]
    ax.plot(history["year"], history["millions"],
            color=COLORS["blue"], lw=2.4,
            label="Direct-care workforce (HHA, PCA, CNA)")
    ax.plot(future["year"], future["millions"],
            color=COLORS["blue"], lw=2.4, ls="--",
            label="Workforce (CAGR extrapolation, 2034-2040)")

    ax.axvline(2024, color=COLORS["darkgray"], lw=0.8, ls=":", alpha=0.7)
    ax.text(2024.2, ax.get_ylim()[1] * 0.94, "today",
            fontsize=8.5, color=COLORS["darkgray"], style="italic")
    ax.axvline(2033, color=COLORS["darkgray"], lw=0.8, ls=":", alpha=0.7)
    ax.text(2033.2, ax.get_ylim()[1] * 0.94, "BLS projection horizon",
            fontsize=8.5, color=COLORS["darkgray"], style="italic")

    ax.set_xlabel("Year")
    ax.set_ylabel("People (millions)")
    ax.set_title("Demand is climbing faster than supply")
    ax.set_xlim(2020, 2040)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", fontsize=8.5)
    source_line(ax,
                "Sources: Alzheimer's Association 2024 Facts & Figures; "
                "CMS Chronic Conditions Warehouse; "
                "BLS Employment Projections 2023-2033.")

    fig.savefig(OUT / "prevalence_vs_workforce.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'prevalence_vs_workforce.png'}")


def fig_caregiver_wages_real():
    """Real median hourly wage, 2014-2024, in 2024 dollars."""
    df = _read_csv("wages_real.csv")

    series = {
        "all_occ": ("All occupations", COLORS["darkgray"], 2.2, "-"),
        "cna":     ("Nursing assistants", COLORS["green"], 2.0, "-"),
        "hha":     ("Home health aides", COLORS["blue"], 2.0, "-"),
        "pca":     ("Personal care aides", COLORS["red"], 2.0, "-"),
    }

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    redbar(fig)

    for occ, (label, color, lw, ls) in series.items():
        sub = df[df["occupation"] == occ].sort_values("year")
        ax.plot(sub["year"], sub["median_wage_real_2024"],
                color=color, lw=lw, ls=ls, label=label, marker="o",
                markersize=4, markeredgecolor=BG, markeredgewidth=0.8)

    ax.set_xlabel("Year")
    ax.set_ylabel("Median hourly wage (2024 USD)")
    ax.set_title("Caregiver pay has barely moved in real terms")
    ax.set_xlim(2013.5, 2024.5)
    ax.set_ylim(10, 26)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=9)
    source_line(ax,
                "Sources: BLS Occupational Employment and Wage Statistics, "
                "May national estimates; deflated by CPI-U All Urban "
                "Consumers (annual, 2024 = 313.7).")

    fig.savefig(OUT / "caregiver_wages_real.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'caregiver_wages_real.png'}")


def fig_aging_pyramid_shift():
    """Paired horizontal bars: U.S. population by age band, 2020 vs. 2040."""
    pop = _read_csv("pop_projections.csv")
    snapshots = pop[pop["year"].isin([2020, 2040])].set_index("year")

    bands = [("85+", "age_85plus"),
             ("75-84", "age_75_84"),
             ("65-74", "age_65_74")]

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    redbar(fig)

    y = np.arange(len(bands))
    height = 0.36
    vals_2020 = [snapshots.loc[2020, col] for _, col in bands]
    vals_2040 = [snapshots.loc[2040, col] for _, col in bands]

    ax.barh(y + height / 2, vals_2020, height=height,
            color=COLORS["darkgray"], label="2020")
    ax.barh(y - height / 2, vals_2040, height=height,
            color=COLORS["red"], label="2040")

    for i, (v20, v40) in enumerate(zip(vals_2020, vals_2040)):
        ax.text(v20 + 0.4, i + height / 2, f"{v20:.1f}",
                va="center", fontsize=8.5, color=COLORS["darkgray"])
        ax.text(v40 + 0.4, i - height / 2, f"{v40:.1f}",
                va="center", fontsize=8.5, color=COLORS["red"],
                fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([b[0] for b in bands])
    ax.set_xlabel("Population (millions)")
    ax.set_title("The 85+ population doubles by 2040")
    ax.set_xlim(0, max(vals_2020 + vals_2040) * 1.18)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    source_line(ax,
                "Source: Census Bureau 2023 National Population Projections "
                "(main series, NP2023_D1).")

    fig.savefig(OUT / "aging_pyramid_shift.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'aging_pyramid_shift.png'}")


def fig_unpaid_family_burden():
    """Unpaid family dementia caregiving: hours, value, and incidence.

    Dual-axis charts confuse `constrained_layout`, so this figure
    disables it for the local figure and uses an explicit two-panel
    layout: time series on the left, single stacked relationship bar
    on the right.
    """
    df = _read_csv("unpaid_caregiver_hours.csv").sort_values("year")

    fig = plt.figure(figsize=(8.2, 4.6))
    fig.set_constrained_layout(False)
    gs = fig.add_gridspec(2, 2, width_ratios=[2.4, 1.0],
                          height_ratios=[6, 1], hspace=0.55, wspace=0.35,
                          left=0.08, right=0.92, top=0.86, bottom=0.18)
    ax_l = fig.add_subplot(gs[0, 0])
    ax_r = fig.add_subplot(gs[0, 1])
    redbar(fig)

    ax_l.bar(df["year"], df["hours_billions"],
             width=0.7, color=COLORS["blue"], alpha=0.85,
             label="Unpaid hours (billions/yr)")
    ax_l.set_ylabel("Hours (billions/yr)", color=COLORS["blue"])
    ax_l.tick_params(axis="y", colors=COLORS["blue"])
    ax_l.set_ylim(0, df["hours_billions"].max() * 1.25)
    ax_l.set_xlim(df["year"].min() - 0.7, df["year"].max() + 0.7)

    ax_l_r = ax_l.twinx()
    ax_l_r.plot(df["year"], df["imputed_value_billions_usd_2024"],
                color=COLORS["red"], lw=2.4, marker="o", markersize=5,
                markeredgecolor=BG, markeredgewidth=0.8,
                label="Imputed value ($B, 2024 USD)")
    ax_l_r.set_ylabel("Imputed value ($B, 2024 USD)", color=COLORS["red"])
    ax_l_r.tick_params(axis="y", colors=COLORS["red"])
    ax_l_r.set_ylim(0, df["imputed_value_billions_usd_2024"].max() * 1.18)
    ax_l_r.spines["right"].set_visible(True)
    ax_l_r.spines["right"].set_color(COLORS["red"])
    ax_l_r.grid(False)

    ax_l.set_xlabel("Year")
    ax_l.set_title("Hours and imputed value", fontsize=11)

    latest = df.iloc[-1]
    segments = [("Adult children", latest["share_adult_child"], COLORS["blue"]),
                ("Spouses",        latest["share_spouse"],      COLORS["red"]),
                ("Other",          latest["share_other"],       COLORS["darkgray"])]

    left = 0.0
    for name, share, color in segments:
        ax_r.barh([0], [share], left=left, height=0.55, color=color)
        ax_r.text(left + share / 2, 0,
                  f"{name}\n{int(round(share * 100))}%",
                  ha="center", va="center",
                  color="white", fontsize=9, fontweight="bold")
        left += share

    ax_r.set_xlim(0, 1.0)
    ax_r.set_ylim(-0.6, 0.6)
    ax_r.set_xticks([])
    ax_r.set_yticks([])
    ax_r.set_title(f"Who provides it ({int(latest['year'])})", fontsize=11)
    ax_r.grid(False)
    ax_r.spines["bottom"].set_visible(False)

    fig.suptitle("Unpaid dementia caregiving keeps growing",
                 fontsize=14, fontweight="bold", x=0.08, ha="left")

    fig.text(0.08, 0.04,
             "Sources: Alzheimer's Association Facts & Figures (unpaid "
             "caregiving tables); relationship shares from AARP / NAC "
             "'Caregiving in the U.S.' survey.\nHours valued at the Alz "
             "Assoc opportunity-cost wage (~$16.59/hr), restated in 2024 USD.",
             fontsize=7.5, color=COLORS["darkgray"], ha="left", va="top")

    fig.savefig(OUT / "unpaid_family_burden.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'unpaid_family_burden.png'}")


def fig_disabled_children_burden():
    """Children with disabilities: population (IDEA categories) and the
    parental labor-supply gap.

    Left panel: U.S. children ages 3-21 served under IDEA, by primary
    disability category, school year 2022-23, in millions.
    Right panel: Labor force participation rate of mothers, by
    disability status of youngest child under 18.
    """
    df = _read_csv("disabled_children.csv")
    cats = df[df["panel"] == "idea_categories"].copy()
    cats["value"] = cats["value"].astype(float)
    cats = cats.sort_values("value")
    lfpr = df[df["panel"] == "mothers_lfpr"].copy()
    lfpr["value"] = lfpr["value"].astype(float)

    fig = plt.figure(figsize=(8.6, 4.8))
    fig.set_constrained_layout(False)
    gs = fig.add_gridspec(1, 2, width_ratios=[2.2, 1.0], wspace=0.32,
                          left=0.27, right=0.97, top=0.84, bottom=0.18)
    ax_l = fig.add_subplot(gs[0, 0])
    ax_r = fig.add_subplot(gs[0, 1])
    redbar(fig)

    accent_keys = {"aut", "id", "dd", "oth"}
    bar_colors = [COLORS["red"] if k in accent_keys else COLORS["blue"]
                  for k in cats["key"]]
    y = np.arange(len(cats))
    ax_l.barh(y, cats["value"], color=bar_colors, height=0.7)
    for i, (val, label) in enumerate(zip(cats["value"], cats["label"])):
        ax_l.text(val + 0.03, i, f"{val:.2f}",
                  va="center", fontsize=8.5, fontweight="bold",
                  color=COLORS["darkgray"])
    ax_l.set_yticks(y)
    ax_l.set_yticklabels(cats["label"], fontsize=9)
    ax_l.set_xlabel("Children served (millions)")
    ax_l.set_xlim(0, cats["value"].max() * 1.22)
    ax_l.set_title("Children served under IDEA, 2022-23", fontsize=11)
    ax_l.grid(axis="x")
    ax_l.grid(axis="y", visible=False)

    bars_x = np.arange(len(lfpr))
    bar_colors_r = [COLORS["darkgray"], COLORS["red"]]
    ax_r.bar(bars_x, lfpr["value"], width=0.55, color=bar_colors_r)
    for i, v in enumerate(lfpr["value"]):
        ax_r.text(i, v + 0.012, f"{int(round(v * 100))}%",
                  ha="center", fontsize=10, fontweight="bold")
    ax_r.set_xticks(bars_x)
    ax_r.set_xticklabels(["Healthy child", "Disabled child"], fontsize=9)
    ax_r.set_ylim(0, max(lfpr["value"]) * 1.18)
    ax_r.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax_r.set_yticklabels(["20%", "40%", "60%", "80%"])
    ax_r.set_title("Mother's labor force\nparticipation rate", fontsize=11)

    gap = (lfpr.set_index("key").loc["no_disability", "value"]
           - lfpr.set_index("key").loc["with_disability", "value"])
    ax_r.annotate(f"{gap * 100:.1f} pp gap",
                  xy=(1, lfpr["value"].iloc[1]),
                  xytext=(1.05, max(lfpr["value"]) * 1.05),
                  fontsize=8.5, color=COLORS["red"], fontweight="bold",
                  ha="left")

    fig.suptitle("It's not only the elderly: lifelong care for disabled children",
                 fontsize=14, fontweight="bold", x=0.04, ha="left")

    fig.text(0.04, 0.04,
             "Sources: U.S. Department of Education, IDEA Section 618, "
             "school year 2022-23; mothers' LFPR from Census CPS ASEC "
             "tabulations summarized in the disability-economics literature.",
             fontsize=7.5, color=COLORS["darkgray"], ha="left", va="top")

    fig.savefig(OUT / "disabled_children_burden.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'disabled_children_burden.png'}")


def fig_state_medicaid_scatter():
    """State scatter: Medicaid HCBS spending per capita vs. direct-care
    workers per 1,000 elderly, with OLS line, 95% bootstrap confidence
    band, and an annotation reporting the formal regression
    diagnostics (HC1 robust SE, bootstrap CI, R², Spearman rank
    correlation). Texas highlighted as the natural Southbound 35 case.
    """
    from regression import (
        fit_state_scatter,
        confidence_band,
    )

    df = _read_csv("state_medicaid_workforce.csv")
    res = fit_state_scatter(df)

    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    redbar(fig)

    x = df["hcbs_per_capita_usd"].to_numpy(dtype=float)
    y = df["direct_care_per_1k_65p"].to_numpy(dtype=float)
    xs = np.linspace(x.min() * 0.95, x.max() * 1.02, 200)
    band_lo, band_hi = confidence_band(x, y, xs, n_boot=2000, seed=0)
    fit_line = res.intercept + res.slope * xs

    ax.fill_between(xs, band_lo, band_hi,
                    color=COLORS["darkgray"], alpha=0.18,
                    label="95% bootstrap CI (n=2,000)", zorder=1)
    ax.plot(xs, fit_line,
            color=COLORS["darkgray"], lw=1.6, ls="--",
            alpha=0.9, zorder=2, label="OLS fit")

    is_tx = df["state"].values == "TX"
    other = ~is_tx
    ax.scatter(x[other], y[other], s=46, color=COLORS["blue"],
               alpha=0.78, edgecolor=BG, linewidth=0.8, zorder=3)
    ax.scatter(x[is_tx], y[is_tx], s=130, color=COLORS["red"],
               edgecolor=BG, linewidth=1.4, zorder=5, label="Texas")

    highlight = {"TX", "MS", "FL", "NY", "MN", "CA", "OR", "MA", "AL"}
    for sx, sy, s in zip(x, y, df["state"]):
        if s in highlight:
            dx, dy = (8, 6) if s != "TX" else (12, -10)
            ax.annotate(s, (sx, sy),
                        xytext=(dx, dy), textcoords="offset points",
                        fontsize=9,
                        fontweight=("bold" if s == "TX" else "normal"),
                        color=(COLORS["red"] if s == "TX" else "#222"))

    ax.set_xlabel("State Medicaid HCBS spending per capita ($/yr)")
    ax.set_ylabel("Direct-care workers per 1,000 residents 65+")
    ax.set_title("States that pay more get more workers")
    ax.set_xlim(0, max(x) * 1.08)
    ax.set_ylim(0, max(y) * 1.18)

    annotation = res.annotate()
    ax.text(0.02, 0.97, annotation,
            transform=ax.transAxes, ha="left", va="top",
            fontsize=8.5, color="#222",
            family="monospace",
            bbox=dict(facecolor=BG, edgecolor="none", alpha=0.85, pad=4))

    ax.legend(loc="lower right", fontsize=9)
    source_line(ax,
                "Sources: KFF state HCBS programs reports (FY2022); BLS OEWS state "
                "estimates (May 2024); Census ACS 1-year state 65+ population. "
                "Univariate OLS; HC1 robust SE; pairs bootstrap CI.")

    fig.savefig(OUT / "state_medicaid_scatter.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'state_medicaid_scatter.png'}")


def fig_texas_wages_competitors():
    """Texas zoom: direct-care wages vs. competing low-credential jobs."""
    df = _read_csv("texas_zoom.csv").copy()
    label_map = {
        "hha":       "Home health aides",
        "pca":       "Personal care aides",
        "cna":       "Nursing assistants",
        "dsp":       "DSPs (IDD)",
        "warehouse": "Warehouse stockers",
        "retail":    "Retail salespersons",
        "fastfood":  "Fast food workers",
        "amazon":    "Amazon FC (start)",
    }
    df["display"] = df["occupation"].map(label_map)
    df = df.sort_values(["group", "median_wage_2024"])
    df_care = df[df["group"] == "care"]
    df_comp = df[df["group"] == "competitor"]

    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    redbar(fig)

    import matplotlib.patches as mpatches
    care_y = np.arange(len(df_care))
    comp_y = np.arange(len(df_comp)) + len(df_care) + 1
    ax.barh(care_y, df_care["median_wage_2024"], height=0.7,
            color=COLORS["red"])
    ax.barh(comp_y, df_comp["median_wage_2024"], height=0.7,
            color=COLORS["blue"])
    legend_handles = [
        mpatches.Patch(color=COLORS["red"], label="Direct care"),
        mpatches.Patch(color=COLORS["blue"], label="Competing low-credential jobs"),
    ]

    for yy, val in zip(care_y, df_care["median_wage_2024"]):
        ax.text(val + 0.15, yy, f"${val:.2f}",
                va="center", fontsize=9, fontweight="bold",
                color=COLORS["red"])
    for yy, val in zip(comp_y, df_comp["median_wage_2024"]):
        ax.text(val + 0.15, yy, f"${val:.2f}",
                va="center", fontsize=9, fontweight="bold",
                color=COLORS["blue"])

    ax.set_yticks(np.concatenate([care_y, comp_y]))
    ax.set_yticklabels(
        list(df_care["display"]) + list(df_comp["display"]),
        fontsize=9,
    )
    care_median = df_care["median_wage_2024"].median()
    gap_y = len(df_care) + 0.0
    ax.axvline(care_median, color=COLORS["darkgray"], lw=0.8, ls=":", alpha=0.7)
    ax.text(care_median + 0.2, gap_y, f"care median ${care_median:.2f}",
            fontsize=8.5, color=COLORS["darkgray"], style="italic",
            ha="left", va="center")

    ax.set_xlabel("Median hourly wage (nominal USD), Texas, May 2024")
    ax.set_title("Texas direct-care wages trail competing jobs")
    ax.set_xlim(0, df["median_wage_2024"].max() * 1.22)
    ax.set_ylim(-0.7, len(df) + 0.6)
    gap_label_y = len(df_care) + 0.55
    ax.text(0.5, gap_label_y, "Direct care",
            ha="left", va="center", fontsize=9, fontweight="bold",
            color=COLORS["red"])
    ax.text(7.0, gap_label_y, "Competing low-credential jobs",
            ha="left", va="center", fontsize=9, fontweight="bold",
            color=COLORS["blue"])
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    source_line(ax,
                "Sources: BLS OEWS Texas state estimates, May 2024; ANCOR State of "
                "America's Direct Support Workforce Crisis (DSPs); company-posted "
                "starting wages (Amazon FC).")

    fig.savefig(OUT / "texas_wages_competitors.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'texas_wages_competitors.png'}")


def fig_combined_populations():
    """The unified care demand picture: populations served by the same
    Medicaid-funded direct-care + DSP workforce. Paid workforce shown
    as a dashed reference line for scale.
    """
    df = _read_csv("combined_populations.csv")
    demand = df[df["population"] != "paid_workforce"].copy()
    supply = df[df["population"] == "paid_workforce"]
    demand = demand.sort_values("millions")

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    redbar(fig)

    palette = {
        "alz_dementia":  COLORS["red"],
        "elderly_adl":   COLORS["yellow"],
        "idd_adults":    COLORS["blue"],
        "disabled_kids": COLORS["green"],
    }
    colors = [palette[k] for k in demand["population"]]
    y = np.arange(len(demand))
    ax.barh(y, demand["millions"], height=0.62, color=colors)
    for yy, val in zip(y, demand["millions"]):
        ax.text(val + 0.12, yy, f"{val:.1f}M",
                va="center", fontsize=9, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(demand["label"], fontsize=9)

    total = demand["millions"].sum()
    workforce = float(supply["millions"].iloc[0])
    ax.axvline(workforce, color=COLORS["darkgray"], lw=1.4, ls="--",
               alpha=0.85)
    top_y = len(demand) - 0.4
    ax.text(workforce + 0.15, top_y,
            f"paid workforce  {workforce:.1f}M",
            fontsize=8.5, color=COLORS["darkgray"], style="italic",
            ha="left", va="top")

    ax.set_xlabel("People needing intensive ongoing care (millions)")
    ax.set_title("One labor market, four populations")
    ax.set_xlim(0, max(demand["millions"].max(), workforce) * 1.30)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)

    ax.text(0.98, 0.05,
            f"total demand: {total:.1f}M\n"
            f"ratio of care recipients per paid worker: "
            f"{total / workforce:.1f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8.5, color=COLORS["darkgray"], fontweight="bold")

    source_line(ax,
                "Sources: Alz Assoc 2024 F&F; Census ACS / HRS; CDC NHIS; Larson "
                "et al. (2023, U Minn); BLS OEWS 2024 + ANCOR.")

    fig.savefig(OUT / "combined_populations.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'combined_populations.png'}")


if __name__ == "__main__":
    print("Building figures for 'Who Will Care for Them?'…")
    fig_prevalence_vs_workforce()
    fig_caregiver_wages_real()
    fig_aging_pyramid_shift()
    fig_unpaid_family_burden()
    fig_disabled_children_burden()
    fig_state_medicaid_scatter()
    fig_texas_wages_competitors()
    fig_combined_populations()
    print("Done.")
    print()
    print("Reminder: input CSVs in `inputs/` contain placeholder values")
    print("transcribed from the cited public sources. Refresh from the")
    print("latest BLS, Census, CMS, and Alz Assoc releases before press.")
