# Who Governs Hays County?

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-governance/) on overlapping jurisdictions in Hays County.

## Quickstart

```bash
pip install -r requirements.txt
python build_figures.py
```

Figures are written to `figures/`.

## Figures

| Figure | File | Description |
|--------|------|-------------|
| 1 | `hays_governance_tax_stack.png` | Property tax rate composition for three typical Hays County addresses |
| 2 | `hays_governance_entity_count.png` | Number of governing entities by address type |

## Data Sources

- Hays Central Appraisal District (2025 tax rates by entity)
- Hays County government (ESD list, county budget)
- District Directory (MUDs and special districts)
- City budgets (Kyle, Buda, San Marcos)
- Texas Commission on Environmental Quality (water districts)
- BPTP property tax summary (rate compilation)
