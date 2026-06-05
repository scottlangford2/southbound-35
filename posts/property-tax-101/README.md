# Property Tax Mechanics 101 — replication

Build script for the Southbound 35 post **"How a Texas Property Tax Bill is Built"** (June 2026).

## Run

```bash
pip install -r requirements.txt
python build_figures.py
```

Outputs five PNGs to `images/property-tax/` in the website repo.

## Sources

- Texas Comptroller of Public Accounts, *Biennial Property Tax Report*
- Tax Foundation, *Facts & Figures* (state effective tax rates)
- Texas Education Agency, *School District Tax Rate Summaries*
- Texas Comptroller, *Truth-in-Taxation worksheets* (taxing-unit counts)

Where a specific year lacks a clean machine-readable feed, values are
transcribed from the source's published tables and cited in the chart
source line. All figures are explicitly illustrative when constructed
(see chart annotations).
