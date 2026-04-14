"""
Replication code for "Where Is All of This Going?"
Hays County population projections post.

Generates two figures:
  1. Multi-method projection comparison (TDC scenarios, CAMPO, statistical fits)
  2. What 612K looks like — comparison to other Texas counties

Historical data: Census Bureau annual population estimates (PEP) 2000–2023,
retrieved from FRED (series TXHAYS9POP). Falls back to hardcoded values if
FRED is unavailable.

Projection methods:
  - TDC 0.0 (low migration), TDC 0.5 (mid), TDC 1.0 (high)
  - CAMPO 2045 RTP estimate
  - Exponential fit to annual Census estimates
  - Linear fit to annual Census estimates
  - Logistic growth model (carrying capacity estimated via NLS)

Usage:
    pip install -r requirements.txt
    python build_figures.py
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from scipy.optimize import curve_fit
from pathlib import Path
import json
import urllib.request

RED    = "#DC3520"
BLUE   = "#1F77B4"
ORANGE = "#FF7F0E"
GRAY   = "#999999"
GREEN  = "#2CA02C"
PURPLE = "#9467BD"
BROWN  = "#8C564B"
DPI    = 150

mpl.rcParams.update({
    "figure.dpi": DPI, "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y",
    "grid.color": "#E5E5E5", "grid.linewidth": 0.8,
    "font.family": "sans-serif", "font.size": 11,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.fontsize": 8, "legend.frameon": False,
    "figure.constrained_layout.use": True,
})

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

# ── Projection years ─────────────────────────────────────────────────────────
PROJ_YEARS = np.array([2025, 2030, 2040, 2050, 2060])


def fetch_historical_data():
    """
    Fetch annual Hays County population estimates from FRED (Census PEP).
    Series: TXHAYS9POP (Resident Population in Hays County, TX).
    Returns (years, pop_thousands) arrays.
    Falls back to hardcoded values if FRED is unavailable.
    """
    # Census Bureau Population Estimates Program (PEP), via Neilsberg / texas-demographics.com
    # 2000–2023: annual intercensal / postcensal estimates
    # 2024–2025: author estimates based on ACS and growth rate
    FALLBACK_YEARS = np.array([
        2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
        2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
        2020, 2021, 2022, 2023, 2024, 2025,
    ])
    FALLBACK_POP = np.array([
        99.4, 105.4, 112.5, 117.2, 121.2, 127.5, 134.6, 143.2, 150.6,
        156.8, 158.1, 163.2, 168.4, 175.9, 184.8, 194.6, 204.6, 214.9,
        222.9, 230.4, 244.0, 256.0, 269.1, 280.5, 292.0, 302.0,
    ])

    try:
        url = ("https://api.stlouisfed.org/fred/series/observations"
               "?series_id=TXHAYS9POP&api_key=DEMO_KEY"
               "&file_type=json&observation_start=2000-01-01")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        years, pops = [], []
        for obs in data.get("observations", []):
            if obs["value"] == ".":
                continue
            yr = int(obs["date"][:4])
            pop = float(obs["value"]) / 1000  # FRED reports actual; convert to K
            years.append(yr)
            pops.append(pop)

        if len(years) >= 10:
            # Add 2025 estimate if not in FRED yet
            years_arr = np.array(years)
            pops_arr = np.array(pops)
            if 2025 not in years_arr:
                years_arr = np.append(years_arr, 2025)
                pops_arr = np.append(pops_arr, 302.0)
            print(f"  Loaded {len(years_arr)} observations from FRED (2000–{years_arr[-1]:.0f})")
            return years_arr, pops_arr

    except Exception as e:
        print(f"  FRED unavailable ({e}), using hardcoded estimates.")

    print(f"  Using {len(FALLBACK_YEARS)} hardcoded annual estimates (2000–2025)")
    return FALLBACK_YEARS, FALLBACK_POP


def fig_projection():
    """Figure 1: Multi-method projection comparison."""

    hist_years, hist_pop = fetch_historical_data()
    n_obs = len(hist_years)

    # --- TDC scenarios (Texas Demographic Center Vintage 2024) ---
    tdc_low  = np.array([302.0, 330.0, 390.0, 430.0, 460.0])
    tdc_mid  = np.array([302.0, 360.0, 470.0, 550.0, 612.0])
    tdc_high = np.array([302.0, 395.0, 570.0, 720.0, 870.0])

    # --- CAMPO 2045 RTP estimate ---
    campo_years = np.array([2025, 2040, 2060])
    campo_pop   = np.array([302.0, 628.0, 850.0])
    campo_interp = np.interp(PROJ_YEARS, campo_years, campo_pop)

    # --- Statistical fits from annual Census estimates ---
    t_hist = hist_years - hist_years[0]  # normalize to t=0 at first year
    t_proj = PROJ_YEARS - hist_years[0]

    # Exponential: P(t) = a * exp(b * t)
    def exp_func(t, a, b):
        return a * np.exp(b * t)

    popt_exp, _ = curve_fit(exp_func, t_hist, hist_pop, p0=[hist_pop[0], 0.04])
    exp_proj = exp_func(t_proj, *popt_exp)
    exp_fitted = exp_func(t_hist, *popt_exp)

    # Linear: P(t) = a + b*t
    coeffs_lin = np.polyfit(hist_years, hist_pop, 1)
    lin_proj = np.polyval(coeffs_lin, PROJ_YEARS)
    lin_fitted = np.polyval(coeffs_lin, hist_years)

    # Logistic: P(t) = K / (1 + exp(-r*(t - t0)))
    def logistic(t, K, r, t0):
        return K / (1 + np.exp(-r * (t - t0)))

    popt_log, _ = curve_fit(logistic, t_hist, hist_pop,
                            p0=[600, 0.06, 20], maxfev=50000,
                            bounds=([400, 0.01, 5], [2000, 0.20, 60]))
    log_proj = logistic(t_proj, *popt_log)
    log_fitted = logistic(t_hist, *popt_log)

    # --- R² for each fit ---
    ss_tot = np.sum((hist_pop - np.mean(hist_pop))**2)
    r2_exp = 1 - np.sum((hist_pop - exp_fitted)**2) / ss_tot
    r2_lin = 1 - np.sum((hist_pop - lin_fitted)**2) / ss_tot
    r2_log = 1 - np.sum((hist_pop - log_fitted)**2) / ss_tot

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(10, 6.5))

    import matplotlib.lines as mlines
    import matplotlib.patches as mpatches

    # Historical (line only)
    h_hist = ax.plot(hist_years, hist_pop, color=BLUE, lw=2.5, zorder=10)[0]

    # TDC band
    h_band = ax.fill_between(PROJ_YEARS, tdc_low, tdc_high,
                              color=ORANGE, alpha=0.12)
    h_tdc = ax.plot(PROJ_YEARS, tdc_mid, color=ORANGE, lw=2, ls="--", marker="s", ms=5,
                    zorder=6)[0]

    # CAMPO
    h_campo = ax.plot(PROJ_YEARS, campo_interp, color=RED, lw=1.8, ls="-.", marker="^", ms=5,
                      zorder=6)[0]

    # Statistical fits — show fitted line through historical + projection
    all_years = np.concatenate([hist_years, PROJ_YEARS[1:]])
    all_t = all_years - hist_years[0]

    h_exp = ax.plot(all_years, exp_func(all_t, *popt_exp), color=GREEN, lw=1.5, ls=":",
                    zorder=5)[0]
    h_lin = ax.plot(all_years, np.polyval(coeffs_lin, all_years), color=PURPLE, lw=1.5,
                    ls=":", zorder=5)[0]
    h_log = ax.plot(all_years, logistic(all_t, *popt_log), color=BROWN, lw=1.5, ls=":",
                    zorder=5)[0]

    # Build legend with section headers
    blank = mlines.Line2D([], [], color="none")
    ax.legend(
        [h_hist, blank,
         h_band, h_tdc, h_campo, blank,
         h_exp, h_lin, h_log],
        [f"Census / ACS annual estimates (n={n_obs})",
         r"$\bf{Published\ projections\ (plotted\ as\ reported):}$",
         "TDC range (low–high migration)",
         "TDC mid (0.5 migration)",
         "CAMPO 2045 RTP",
         r"$\bf{Estimated\ from\ Census\ data:}$",
         f"Exponential (r={popt_exp[1]:.3f}/yr, R²={r2_exp:.3f})",
         f"Linear (+{coeffs_lin[0]:.1f}K/yr, R²={r2_lin:.3f})",
         f"Logistic (K={popt_log[0]:.0f}K, R²={r2_log:.3f})"],
        loc="upper left", fontsize=8.5,
    )

    # Shade projection region
    ax.axvspan(2025, 2062, alpha=0.03, color=GRAY)
    ax.axvline(2025, color=GRAY, lw=0.8, ls="-", alpha=0.4)

    # Labels at 2060
    labels_2060 = [
        ("TDC mid", tdc_mid[-1], ORANGE),
        ("CAMPO", campo_interp[-1], RED),
        ("Exponential", exp_proj[-1], GREEN),
        ("Linear", lin_proj[-1], PURPLE),
        ("Logistic", log_proj[-1], BROWN),
    ]
    for name, val, color in labels_2060:
        ax.annotate(f"{val:.0f}K", (2060, val), textcoords="offset points",
                    xytext=(8, 0), ha="left", fontsize=7.5, color=color,
                    fontweight="bold")

    ax.set_ylabel("Population (thousands)")
    ax.set_title("Hays County: Six Projection Strategies Compared")
    ax.set_xlim(1998, 2068)
    ax.set_ylim(0, max(tdc_high[-1], exp_proj[-1], campo_interp[-1]) * 1.1)
    ax.text(0, -0.12,
            "TDC: Texas Demographic Center Vintage 2024. CAMPO: 2045 Regional Transportation Plan.\n"
            f"Statistical fits estimated from {n_obs} annual Census/ACS estimates (2000–2025). "
            "Logistic K estimated via NLS.",
            transform=ax.transAxes, fontsize=6.5, color=GRAY)

    fig.savefig(OUT / "hays_projection.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_projection.png'}")

    # Print summary
    print(f"\n  Fit summary ({n_obs} annual observations):")
    print(f"    Exponential:  r={popt_exp[1]:.4f}/yr, R²={r2_exp:.4f}, 2060={exp_proj[-1]:.0f}K")
    print(f"    Linear:       +{coeffs_lin[0]:.2f}K/yr, R²={r2_lin:.4f}, 2060={lin_proj[-1]:.0f}K")
    print(f"    Logistic:     K={popt_log[0]:.0f}K, r={popt_log[1]:.4f}, R²={r2_log:.4f}, 2060={log_proj[-1]:.0f}K")
    print(f"\n  Official projections at 2060:")
    print(f"    TDC low:  {tdc_low[-1]:.0f}K | mid: {tdc_mid[-1]:.0f}K | high: {tdc_high[-1]:.0f}K")
    print(f"    CAMPO:    {campo_interp[-1]:.0f}K")


def fig_comparison():
    """Figure 2: What 612K looks like in context."""
    counties = ["El Paso\n(today)", "Hays\n(2060)", "Hays\n(today)", "Williamson\n(2010)"]
    pops     = [865, 612, 302, 422]
    colors   = [GRAY, ORANGE, BLUE, GRAY]

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    alphas = [0.5, 0.8, 0.8, 0.5]
    bars = ax.bar(counties, pops, color=colors, width=0.55,
                  edgecolor="white", linewidth=0.5)
    for bar, a in zip(bars, alphas):
        bar.set_alpha(a)

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
