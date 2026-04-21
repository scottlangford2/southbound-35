# The Hays Discount, Five Years Later

Replication code for [`The Hays Discount, Five Years Later`](https://scottlangford2.github.io/scott_langford/)
(forthcoming). Revisits the Travis / Williamson / Hays median-home-price
gap from the April 2026 growth post and tracks it monthly from January
2020 through the latest Zillow release.

## Quickstart

```bash
pip install -r requirements.txt
python fetch_data.py     # downloads Zillow ZHVI + Freddie Mac 30Y rate
python build_figures.py  # computes gaps and writes figures/
```

All raw CSVs land in `data/` (git-ignored); all plots in `figures/`
(git-ignored).

## Data Sources

- **Zillow Home Value Index (ZHVI)** — `County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv`,
  all homes, middle tier, smoothed and seasonally adjusted, monthly,
  county level. No API key.
- **Freddie Mac Primary Mortgage Market Survey (PMMS)** — 30-year fixed
  rate, weekly, pulled from FRED series `MORTGAGE30US`. No API key.

## Figures

| Figure | File | Description |
|--------|------|-------------|
| 1 | `gap_levels.png`   | Travis / Williamson / Hays ZHVI, 2020 → latest |
| 2 | `gap_absolute.png` | Absolute dollar gap over Hays, with 2022 peak |
| 3 | `gap_relative.png` | Percentage premium over Hays, with long-run mean |
| 4 | `gap_payment.png`  | Monthly P&I on the gap at the prevailing 30Y rate |

## Files

- `fetch_data.py` — downloads raw ZHVI and mortgage-rate CSVs into `data/`.
- `build_figures.py` — loads the CSVs, computes the four derived series
  (price levels, absolute gap, relative premium, payment gap), prints an
  analysis summary, and writes the four figures into `figures/`.
- `requirements.txt` — `matplotlib`, `numpy`, `pandas`.
