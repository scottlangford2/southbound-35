# How Dangerous Is Spring Break, Really?

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/04/spring-break-mortality/).

## Quickstart

```bash
pip install -r requirements.txt
python fetch_data.py   # downloads FARS, Google Trends, etc.
python main.py         # builds all 10 figures
```

Figures are written to `graphics/`.

## Data

`fetch_data.py` downloads FARS person-level data from NHTSA (2016–2023),
Google Trends data via `pytrends`, and creates comparison datasets. All
CSVs land in `data/` and are git-ignored.

## Figures

| Figure | File | Description |
|--------|------|-------------|
| 1a | `blog_deaths_trend.png` | Annual news-scraped death counts, 2016–2025 |
| 1b | `blog_monte_carlo.png` | Monte Carlo simulation of expected deaths |
| 2a | `blog_monthly_bars.png` | Seasonal deviation in 18–24 traffic deaths |
| 2b | `blog_did.png` | DiD: destination vs. other states |
| 3a | `blog_google_trends.png` | Google Trends search interest |
| 3b | `blog_concentration.png` | Deaths per county per week |
| CF1 | `blog_cf_weekends.png` | Spring break vs. other holiday weekends |
| CF3 | `blog_cf_gatherings.png` | Deaths per million attendees |
| CF4 | `blog_cf_substitution.png` | Risk substitution in non-destination states |
| CF5 | `blog_cf_causal.png` | Actual vs. counterfactual excess deaths |
