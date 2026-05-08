# Where the Water Will Come From

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-water/).

## Quickstart

```bash
pip install -r requirements.txt
python build_figures.py
```

Figures are written to `figures/`.

## Figures

| Figure | File | Description |
|--------|------|-------------|
| 1 | `hays_water_demand.png` | Hays County water demand, historical and projected, by category |
| 2 | `hays_aquifer_split.png` | Hays cities arrayed east–west by source aquifer (schematic) |
| 3 | `hays_arwa_ramp.png` | ARWA imported supply, phase ramp-up |

## Data Sources

- Texas Water Development Board, Historical Water Use Estimates (county-level, by category)
- Region L 2026 South Central Texas Regional Water Plan (county-level demand projections)
- Alliance Regional Water Authority (project phasing, nameplate capacities)
- City of Kyle, City of San Marcos, City of Buda annual financial reports (water-utility long-term debt)

## Notes

Numerical values in `build_figures.py` marked `# VERIFY` are author best estimates pending replacement with the cited public sources. The aquifer-split figure is a schematic and should not be used as a substitute for parcel-level service-area mapping.
