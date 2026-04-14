# Where Is All of This Going?

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/04/hays-county-projections/).

## Quickstart

```bash
pip install -r requirements.txt
python build_figures.py
```

Figures are written to `figures/`.

## Figures

| Figure | File | Description |
|--------|------|-------------|
| 1 | `hays_projection.png` | Historical population + TDC projections through 2060 |
| 2 | `hays_comparison.png` | What 612K looks like — comparison to other Texas counties |

## Data Sources

- U.S. Census Bureau (decennial census 1990–2020, ACS 2023)
- Texas Demographic Center, Vintage 2024 population projections (0.5 migration scenario)
- CAMPO 2045 Regional Transportation Plan demographic forecast
