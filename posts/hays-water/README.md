# Where the Water Will Come From

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-water/).

All numerical values come from CSVs in `inputs/`. The build script is purely a renderer; to update a figure, update the corresponding CSV and re-run.

## Quickstart

```bash
pip install -r requirements.txt
python build_figures.py
```

Figures are written to `figures/` (gitignored — regenerate from code).

## Files

```
posts/hays-water/
├── README.md
├── requirements.txt
├── build_figures.py          # reads inputs/, writes figures/
├── inputs/
│   ├── twdb_water_use_hays.csv      # demand by category, kAF/yr
│   ├── aquifer_assignments.csv      # cities by source aquifer
│   └── arwa_phases.csv              # ARWA imported supply, MGD
└── figures/                  # build output (gitignored)
```

## Data sources

### `inputs/twdb_water_use_hays.csv`
Hays County water demand, kAF/yr, by category, by year.

- **Historical (2000–2020):** TWDB Historical Water Use Estimates by County.
  - Tool: <https://www3.twdb.texas.gov/apps/reports/WU_REP/SumFinal_CountyReportWithReuse>
  - Filter: County = Hays. Export to Excel; sum across reuse and non-reuse rows by category.
- **Projected (2030–2070):** TWDB 2026 RWP Board-Adopted Demand Projections.
  - Municipal: <https://www.twdb.texas.gov/waterplanning/data/projections/2027/municipal.asp>
  - Non-municipal: <https://www.twdb.texas.gov/waterplanning/data/projections/2027/projections.asp>
  - Filter: Region = L (South Central Texas), County = Hays.

### `inputs/arwa_phases.csv`
ARWA cumulative imported supply across partner cities (Kyle, San Marcos, Buda, Canyon Regional Water Authority).

- Source: ARWA project documents and partner-city ACFR debt disclosures.
- Hub: <https://allianceregionalwater.com/>

### `inputs/aquifer_assignments.csv`
Hays cities by primary source aquifer. Hand-curated; should be verified against city utility service-area maps and BSEACD/HTGCD boundary files.

- BSEACD: <https://bseacd.org/>
- HTGCD: <https://haysgroundwater.com/>

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
`cumulative_mgd` is total nameplate capacity from ARWA across all partners as of `year_online`. `status` is one of `completed`, `in_construction`, `planned`.

### `aquifer_assignments.csv`
```
city, aquifer, schematic_longitude, true_longitude, note
```
`schematic_longitude` is artificially spread for chart legibility. `true_longitude` is documentation only. `aquifer` ∈ {Trinity, Edwards}.

## Notes

CSV files in `inputs/` are committed (not gitignored) so the package builds out of the box. Values currently reflect order-of-magnitude placeholders pending Scott's update from the cited public sources.
