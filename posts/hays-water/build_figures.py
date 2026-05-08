"""
Replication code for "Where the Water Will Come From"
https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-water/

All numerical values come from CSV inputs in `inputs/`. Map polygons
come from public shapefiles fetched by `fetch_shapefiles.py` and
cached under `inputs/shapefiles/`. The script is purely a renderer.

Usage:
    pip install -r requirements.txt
    python fetch_shapefiles.py    # one-time, idempotent
    python build_figures.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import pandas as pd

from econ_style import apply as apply_econ_style, COLORS, redbar, source_line, BG

apply_econ_style()

# Convenience aliases for legacy code that referenced specific colors
BLUE   = COLORS["blue"]
ORANGE = COLORS["yellow"]   # used as a warm secondary in maps
GREEN  = COLORS["green"]
RED    = COLORS["red"]
GRAY   = COLORS["darkgray"]
DPI    = 150

# Texas projected CRS for accurate area / shape rendering. EPSG:3083
# is the NAD83 Texas Centric Albers Equal Area projection.
TEXAS_CRS = "EPSG:3083"

ROOT   = Path(__file__).parent
INPUT  = ROOT / "inputs"
SHAPES = INPUT / "shapefiles"
OUT    = ROOT / "figures"
OUT.mkdir(exist_ok=True)


def _read_csv(name):
    """Read a CSV from inputs/, treating # lines as comments."""
    return pd.read_csv(INPUT / name, comment="#")


def _hays_polygon():
    """Return Hays County polygon, projected to Texas CRS."""
    counties = gpd.read_file(SHAPES / "county" / "cb_2023_us_county_5m.shp")
    hays = counties[(counties["STATEFP"] == "48") &
                    (counties["NAME"] == "Hays")]
    return hays.to_crs(TEXAS_CRS)


def _city_points():
    """Return city locations as a GeoDataFrame in the Texas CRS."""
    cities = _read_csv("city_locations.csv")
    gdf = gpd.GeoDataFrame(
        cities,
        geometry=gpd.points_from_xy(cities["lon"], cities["lat"]),
        crs="EPSG:4326",
    )
    return gdf.to_crs(TEXAS_CRS)


def _label_cities(ax, cities_gdf, fontsize=8, dy=8):
    """Add city labels next to point markers on a projected map."""
    for _, row in cities_gdf.iterrows():
        ax.annotate(
            row["city"],
            xy=(row.geometry.x, row.geometry.y),
            xytext=(0, dy), textcoords="offset points",
            ha="center", fontsize=fontsize, fontweight="bold",
            color="#222",
        )


def fig_demand():
    """Hays County water demand, historical and projected, by category."""
    df = _read_csv("twdb_water_use_hays.csv").sort_values("year")

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    redbar(fig)

    ax.stackplot(
        df["year"],
        df["municipal"], df["irrigation"], df["mining"], df["manufacturing"],
        labels=["Municipal", "Irrigation", "Mining", "Manufacturing"],
        colors=[COLORS["blue"], COLORS["green"], COLORS["yellow"],
                COLORS["darkgray"]],
    )

    historical = df[df["year"] <= 2025]
    if not historical.empty:
        boundary = historical["year"].max()
        ax.axvline(boundary, color=COLORS["darkgray"], lw=0.8, ls="--",
                   alpha=0.7)
        ax.text(boundary + 0.5, ax.get_ylim()[1] * 0.92, "projected",
                fontsize=8.5, color=COLORS["darkgray"], style="italic")

    ax.set_xlabel("Year")
    ax.set_ylabel("Demand (thousand acre-feet/yr)")
    ax.set_title("Hays County Water Demand: Historical and Projected")
    ax.set_xlim(df["year"].min(), df["year"].max())
    ax.legend(loc="upper left")
    source_line(ax,
                "Sources: TWDB Historical Water Use Estimates; "
                "TWDB 2026 RWP Board-Adopted Demand Projections.")

    fig.savefig(OUT / "hays_water_demand.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_water_demand.png'}")


def fig_aquifer_map():
    """Hays County aquifer map: Edwards and Trinity polygons clipped to
    the county boundary, with cities as labeled points.

    Trinity covers most of Hays. The Edwards Balcones Fault Zone
    aquifer overlies Trinity along the eastern edge near I-35 and is
    drawn on top so the recharge zone is visible.
    """
    hays = _hays_polygon()
    cities = _city_points()

    aquifers = gpd.read_file(SHAPES / "major_aquifers" /
                             "NEW_major_aquifers_dd.shp").to_crs(TEXAS_CRS)
    in_hays = gpd.overlay(aquifers, hays[["geometry"]], how="intersection")

    # Distinct, full-opacity fills so the layers read clearly.
    colors = {"TRINITY": COLORS["yellow"], "EDWARDS": COLORS["blue"]}

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    redbar(fig)
    hays.plot(ax=ax, color=BG, edgecolor=COLORS["darkgray"],
              linewidth=1.2, zorder=1)

    # Trinity first (covers most of the county), then Edwards drawn on
    # top so the eastern recharge band is visible.
    for name in ("TRINITY", "EDWARDS"):
        slab = in_hays[in_hays["AQ_NAME"] == name]
        if slab.empty:
            continue
        slab.plot(ax=ax, color=colors[name],
                  edgecolor="white", linewidth=0.4, zorder=2)

    cities.plot(ax=ax, color="black", markersize=22, zorder=5)
    _label_cities(ax, cities)

    ax.set_axis_off()
    ax.set_title("Hays County: Aquifer Coverage")
    handles = [mpatches.Patch(color=colors["TRINITY"], label="Trinity aquifer"),
               mpatches.Patch(color=colors["EDWARDS"], label="Edwards aquifer")]
    ax.legend(handles=handles, loc="lower left",
              frameon=True, framealpha=0.95, fontsize=9,
              facecolor=BG, edgecolor="none")
    source_line(ax,
                "Sources: TWDB Major Aquifers; Census TIGER 2023 county boundary.",
                y=-0.02)

    fig.savefig(OUT / "hays_aquifer_map.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_aquifer_map.png'}")


def fig_gcd_map():
    """Hays County groundwater conservation district boundaries.

    BSEACD (eastern Edwards), HTGCD (most of the county, Trinity), and
    EAA (southern Edwards corridor). The unshaded sliver near central
    Hays reflects the gap between EAA's northern boundary and BSEACD's
    southern extent.
    """
    hays = _hays_polygon()
    cities = _city_points()
    gcd_all = gpd.read_file(SHAPES / "gcd" / "TWDB_GCD_NOV2019.shp").to_crs(TEXAS_CRS)

    targets = [
        ("HAYS TRINITY GROUNDWATER CONSERVATION DISTRICT",     "HTGCD",  COLORS["yellow"]),
        ("BARTON SPRINGS/EDWARDS AQUIFER CONSERVATION DISTRICT", "BSEACD", COLORS["blue"]),
        ("EDWARDS AQUIFER AUTHORITY",                          "EAA",    COLORS["green"]),
    ]

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    redbar(fig)
    hays.plot(ax=ax, color=BG, edgecolor=COLORS["darkgray"],
              linewidth=1.2, zorder=1)

    legend_handles = []
    for full_name, short, color in targets:
        sel = gcd_all[gcd_all["DISTNAME"] == full_name]
        if sel.empty:
            continue
        clipped = gpd.overlay(sel, hays[["geometry"]], how="intersection")
        clipped.plot(ax=ax, color=color,
                     edgecolor="white", linewidth=0.5, zorder=2)
        legend_handles.append(mpatches.Patch(color=color, label=short))

    cities.plot(ax=ax, color="black", markersize=22, zorder=5)
    _label_cities(ax, cities)

    ax.set_axis_off()
    ax.set_title("Hays County: Groundwater Conservation Districts")
    ax.legend(handles=legend_handles, loc="lower left",
              frameon=True, framealpha=0.95, fontsize=9,
              facecolor=BG, edgecolor="none")
    source_line(ax,
                "Sources: TWDB GCD Boundaries (Nov 2019); Census TIGER 2023.",
                y=-0.02)

    fig.savefig(OUT / "hays_gcd_map.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_gcd_map.png'}")


def fig_arwa_ramp():
    """ARWA imported supply by phase, MGD, across partner cities."""
    df = _read_csv("arwa_phases.csv").sort_values("year_online")

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    redbar(fig)

    ax.step(df["year_online"], df["cumulative_mgd"],
            where="post", color=COLORS["blue"], lw=2.5, zorder=3)
    ax.fill_between(df["year_online"], 0, df["cumulative_mgd"],
                    step="post", color=COLORS["blue"], alpha=0.18)

    for _, row in df.iterrows():
        if row["cumulative_mgd"] > 0:
            ax.scatter(row["year_online"], row["cumulative_mgd"],
                       color=COLORS["blue"], s=60, zorder=5,
                       edgecolor=BG, linewidth=1.2)
            ax.annotate(f"{row['phase']}\n{row['cumulative_mgd']:.0f} MGD",
                        (row["year_online"], row["cumulative_mgd"]),
                        xytext=(6, 8), textcoords="offset points",
                        fontsize=8.5, fontweight="bold")

    today = 2025
    ax.axvline(today, color=COLORS["darkgray"], lw=0.8, ls="--", alpha=0.7)
    ax.text(today + 0.5, ax.get_ylim()[1] * 0.05, "today",
            fontsize=8.5, color=COLORS["darkgray"], style="italic")

    ax.set_xlabel("Year online")
    ax.set_ylabel("Cumulative imported supply (MGD)")
    ax.set_title("ARWA Imported Supply: Phase Ramp-Up")
    ax.set_xlim(df["year_online"].min() - 2, df["year_online"].max() + 5)
    ax.set_ylim(0, df["cumulative_mgd"].max() * 1.25)
    source_line(ax,
                "Sources: Alliance Regional Water Authority; partner-city ACFRs.")

    fig.savefig(OUT / "hays_arwa_ramp.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {OUT / 'hays_arwa_ramp.png'}")


if __name__ == "__main__":
    print("Building figures for 'Where the Water Will Come From'…")
    if not (SHAPES / "county" / "cb_2023_us_county_5m.shp").exists():
        print("Shapefiles not cached. Run: python fetch_shapefiles.py")
        raise SystemExit(1)
    fig_demand()
    fig_aquifer_map()
    fig_gcd_map()
    fig_arwa_ramp()
    print("Done.")
    print()
    print("Reminder: input CSVs in `inputs/` contain placeholder values.")
    print("Update them with TWDB / ARWA published figures, then re-run.")
