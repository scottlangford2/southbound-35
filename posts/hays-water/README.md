# Where the Water Will Come From

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-water/).

All numerical values come from CSVs in `inputs/`. Map polygons come from public shapefiles fetched by `fetch_shapefiles.py` and cached under `inputs/shapefiles/`. The build script is purely a renderer.

## Quickstart

```bash
pip install -r requirements.txt
python fetch_shapefiles.py    # one-time, idempotent (~20 MB)
python build_figures.py
```

Figures are written to `figures/` (gitignored — regenerate from code).

## Files

```
posts/hays-water/
├── README.md
├── requirements.txt
├── fetch_shapefiles.py       # downloads TWDB + TIGER shapefiles
├── build_figures.py          # reads inputs/, writes figures/
├── inputs/
│   ├── twdb_water_use_hays.csv      # demand by year × category
│   ├── arwa_phases.csv              # ARWA imported supply, MGD
│   ├── city_locations.csv           # map markers (lat/lon)
│   └── shapefiles/                  # gitignored; populated on fetch
└── figures/                  # build output (gitignored)
```

## Figures

| # | File | Description |
|---|------|-------------|
| 1 | `hays_aquifer_map.png` | Hays County aquifer coverage (Edwards, Trinity) clipped to county boundary |
| 2 | `hays_water_demand.png` | County water demand, historical and projected, by category |
| 3 | `hays_gcd_map.png` | Groundwater conservation district boundaries within Hays |
| 4 | `hays_arwa_ramp.png` | ARWA imported supply, cumulative MGD by phase |

## Data sources

### `inputs/twdb_water_use_hays.csv`
Hays County water demand, kAF/yr, by category, by year.

- **Historical (2000–2020):** TWDB Historical Water Use Estimates by County. Tool: <https://www3.twdb.texas.gov/apps/reports/WU_REP/SumFinal_CountyReportWithReuse>. Filter County = Hays; export to Excel; sum across reuse and non-reuse rows by category.
- **Projected (2030–2070):** TWDB 2026 RWP Board-Adopted Demand Projections. Municipal: <https://www.twdb.texas.gov/waterplanning/data/projections/2027/municipal.asp>. Non-municipal: <https://www.twdb.texas.gov/waterplanning/data/projections/2027/projections.asp>. Filter Region = L (South Central Texas), County = Hays.

### `inputs/arwa_phases.csv`
ARWA cumulative imported supply across partner cities (Kyle, San Marcos, Buda, Canyon Regional Water Authority).

- Source: ARWA project documents and partner-city ACFR debt disclosures. Hub: <https://allianceregionalwater.com/>.

### `inputs/city_locations.csv`
City lat/lon for map markers. Coordinates are decimal degrees, WGS84.

### Map polygons (fetched by `fetch_shapefiles.py`)

| Layer | Source | URL |
|---|---|---|
| Major aquifers | TWDB | https://www.twdb.texas.gov/mapping/gisdata/doc/major_aquifers.zip |
| GCD boundaries | TWDB | https://www.twdb.texas.gov/mapping/gisdata/doc/GCD_Shapefiles.zip |
| County boundary | Census TIGER 2023 | https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_5m.zip |

All three are public-domain or open-data. The fetch script is idempotent and skips downloads when files are already cached.

## Schemas

### `twdb_water_use_hays.csv`
```
year, municipal, irrigation, mining, manufacturing
```
Units: thousand acre-feet per year. One row per year (historical or projection).

### `arwa_phases.csv`
```
phase, year_online, cumulative_mgd, status
```
`cumulative_mgd` is total nameplate capacity from ARWA across all partners as of `year_online`. `status` ∈ {`completed`, `in_construction`, `planned`}.

### `city_locations.csv`
```
city, lat, lon, aquifer
```
`aquifer` is informational; the map polygons come from the TWDB shapefile, not this column.

## Notes

CSV files in `inputs/` (other than the shapefiles directory) are committed so the package builds out of the box. Numerical values currently reflect order-of-magnitude placeholders pending the author's update from the cited public sources.
