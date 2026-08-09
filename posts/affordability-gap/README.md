# The Hays Discount, Five Years Later

Replication code for [the blog post](https://scottlangford2.github.io/scott_langford/posts/2026/04/hays-discount/).

Draft prose lives alongside the code in [`draft.md`](draft.md).

## Pipeline

```
fetch_data.py    →  data/*.csv + data/MANIFEST.json   (network, one run per vintage)
analysis.py      →  derived series + statistical tests (pure computation, no plotting)
build_figures.py →  figures/*.png                     (imports analysis)
```

`analysis.py` exposes `run()` returning an `AnalysisResult` dataclass
with the full derived panel, so the same numbers can be pulled into a
notebook or another script without re-running the figure step.

## Quickstart

```bash
pip install -r requirements.txt
python fetch_data.py            # ~30 s, writes data/ and MANIFEST.json
python analysis.py              # prints the summary block referenced by draft.md
python build_figures.py         # renders all nine figures
```

If Zillow or FRED is unreachable, run `python fetch_data.py --offline`
to skip the network and rerun against whatever's already cached in
`data/`.

## Sources

| Source | What we pull | Endpoint |
|---|---|---|
| Zillow ZHVI | Home value index, mid / bottom / top tiers, county | `files.zillowstatic.com/research/public_csvs/zhvi/…` |
| Zillow $/sqft | Median price per sqft, county | same |
| FHFA HPI | Repeat-sales house-price index, county, quarterly | `fhfa.gov/hpi/download/quarterly_datasets/hpi_at_bdl_county.csv` |
| Realtor.com | Median listing price by county | FRED series `MEDLISPRI{FIPS}` |
| Freddie Mac | 30-year fixed mortgage rate, weekly | FRED series `MORTGAGE30US` |
| BLS CPI-U | Deflator, all items + DFW | FRED series `CPIAUCSL`, `CUURS37BSA0` |
| IRS SOI | County-to-county migration inflows, annual | `irs.gov/pub/irs-soi/county{YY}{YY+1}.zip` |

All sources are public with no API keys. Counties: Travis (48453),
Williamson (48491), Hays (48209). Denton (48121) and Collin (48085)
are pulled for the out-of-metro robustness check.

## Reproducibility

`data/MANIFEST.json` records for each fetched file: source URL, SHA-256
checksum of the raw payload, byte count, fetch timestamp, and any
per-source notes. Rerunning `fetch_data.py` updates the manifest. A
reviewer who wants to confirm they're running on the same data vintage
as the published figures can diff the checksums.

Zillow releases ZHVI monthly and revises prior months. FHFA revises
quarterly. FRED series are effectively real-time. The post's headline
numbers will drift modestly between releases — that's the nature of
revised data, not a bug.

## Figures

| # | File | What it answers |
|---|---|---|
| 1 | `gap_levels.png` | How did all three counties' medians move together? |
| 2 | `gap_absolute.png` | How has the Travis−Hays and Williamson−Hays gap moved? |
| 3 | `gap_triangulation.png` | Do ZHVI, FHFA HPI, and Realtor listings agree on the premium? |
| 4 | `gap_real_nominal.png` | How much of the gap's narrowing is general inflation? |
| 5 | `gap_piti.png` | Decomposes the monthly gap into P&I, taxes, insurance, MUD |
| 6 | `gap_relative_stats.png` | Is the ≈38 % premium constant? Mean + HAC CI + Quandt sup-F |
| 7 | `gap_tiers.png` | Does the premium survive at the bottom / top ZHVI tiers? |
| 8 | `gap_out_of_metro.png` | Is the stable premium Austin-specific, or does DFW look similar? |
| 9 | `migration_response.png` | Do IRS SOI inflows to Hays follow the lagged Travis→Hays gap? |

## Fiscal parameters

The PITI decomposition uses point estimates documented in `analysis.py`
(see the `FISCAL` table):

| County | Effective tax rate | Annual insurance | MUD rate |
|---|---|---|---|
| Travis | 1.80 % | $2,800 | 0 |
| Williamson | 1.95 % | $3,000 | 0 |
| Hays | 2.10 % | $3,050 | 0.85 % |

These are representative of a typical mid-tier address within each
county and come from the Texas Comptroller's Truth-in-Taxation filings
and TDI's 2024 Home Insurance Price Comparison. Real-world dispersion
across ISDs and MUDs is ±0.2 percentage points on the tax rate and
roughly ±$500 on insurance.

## Known limitations

Documented in the `Limitations` section of `draft.md`:

- County medians hide within-county variation (Kyle vs. Dripping Springs vs. San Marcos).
- Effective tax and insurance are point estimates, not household-level.
- Migration regression is correlational with n = 3 (after consuming a lag).
- All series are nominal-dollar, pre-tax; no capital-gains adjustment.

## Files

- `fetch_data.py` — downloads raw CSVs, checksums them, writes `MANIFEST.json`.
- `analysis.py` — pure compute; loads raw CSVs, produces derived series and statistical tests.
- `build_figures.py` — plotting-only; imports `analysis` and writes the nine figures.
- `requirements.txt` — `matplotlib`, `numpy`, `pandas`, `scipy`, `statsmodels`.
- `draft.md` — blog-post prose with Jekyll frontmatter, ready to drop into the blog repo.
