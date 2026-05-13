# How Do You Pay for the Schools?

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/05/hays-county-schools/) on Hays CISD's split 2025 votes.

## Quickstart

```bash
pip install -r requirements.txt
python build_figures.py
```

Figures are written to `figures/`.

## Figures

| Figure | File | Description |
|--------|------|-------------|
| 1 | `hays_schools_squeeze.png` | HCISD enrollment, taxable value, and per-student M&O revenue indexed to 2020 |
| 2 | `hays_schools_split_vote.png` | May 2025 bond Prop A vs. November 2025 M&O TRE |

## Data Sources

- Hays Consolidated Independent School District budget documents (2024–25, 2025–26)
- Hays Central Appraisal District tax base estimates
- Hays County Elections (May 3, 2025; November 4, 2025)
- Texas Education Agency, Foundation School Program rules
- Community Impact News and KUT coverage of the 2025 votes
