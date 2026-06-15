# The 3.5% Squeeze: SB 2 vs. a Doubling Tax Base in Hays-Area Cities

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/05/sb2-squeeze/) (Southbound 35, 2026-05-25).

All numerical values come from CSVs in `inputs/`. Those CSVs currently contain **synthetic placeholder rows** so the build runs on an empty checkout. The real values are written by Scott's `mf_scraper` ACFR pipeline (Census ASLGF + Texas COG + 50-state ACFR via Playwright) before the post goes live. See the Schemas section below for the exact columns the pipeline must produce.

## Quickstart

```bash
pip install -r requirements.txt
python build_figures.py
```

Figures are written to `figures/` (gitignored except for `.gitkeep`; regenerate from code).

## Files

```
posts/sb2-squeeze/
├── README.md
├── requirements.txt
├── build_figures.py          # reads inputs/, writes figures/
├── inputs/
│   ├── sb2_levy_vs_cap.csv          # M&O levy, NNR rate, voter-approval rate by city/year
│   ├── city_acfr_metrics.csv        # ACFR fiscal metrics: levy, certified value, population
│   └── voter_approval_elections.csv # SB 2 tax-rate elections since 2020
└── figures/                  # build output (gitignored)
    └── .gitkeep
```

## Figures

| # | Output file | Description |
|---|-------------|-------------|
| 1 | `sb2_mo_rates.png` | 2×2 panel: adopted M&O rate, NNR rate, voter-approval rate by fiscal year for Kyle, Buda, San Marcos, Dripping Springs |
| 2 | `sb2_tax_base_composition.png` | 2×2 stacked bar: certified value of existing property vs. new construction by city/year |
| 3 | `sb2_debt_service_share.png` | Line chart: I&S debt-service levy as % of total levy, four cities, with ARWA partnership inflection marked |

## Data sources

### `inputs/sb2_levy_vs_cap.csv`

M&O levy and rate data by city and fiscal year.

- **Source:** Scott's `mf_scraper` pipeline reading Texas Comptroller Truth-in-Taxation worksheet archives and city-filed rate certification worksheets (Form 50-856 or equivalent).
- **Public counterpart:** [Texas Comptroller Truth-in-Taxation](https://comptroller.texas.gov/taxes/property-tax/truth-in-taxation/).
- **Legal basis:** Texas Tax Code [Chapter 26](https://statutes.capitol.texas.gov/Docs/TX/htm/TX.26.htm), §26.04(c) (no-new-revenue and voter-approval rates post-SB 2).

### `inputs/city_acfr_metrics.csv`

City-level fiscal metrics from Annual Comprehensive Financial Reports.

- **Source:** Scott's `mf_scraper` pipeline pulling from Census ASLGF, Texas COG, and direct ACFR Playwright scraper.
- **Certified values:** Hays Central Appraisal District ([hayscad.com](https://hayscad.com/)) certified-roll summaries filed annually after ARB review.
- **Levy data:** City-filed Truth-in-Taxation worksheets and ACFR governmental-activities schedules.

### `inputs/voter_approval_elections.csv`

Voter-approval tax-rate elections held by Hays-area cities since SB 2 took effect (FY2020 onward).

- **Source:** Scott's `mf_scraper` pipeline reading Texas Secretary of State election results and Texas Tribune election database.
- **Note:** If no elections have been held, the mf_scraper should write an empty file (header only). The build script does not currently render a figure from this CSV; it is included for provenance and for future analysis.

## Schemas

### `sb2_levy_vs_cap.csv`

```
year                  integer   fiscal year (Oct–Sep for Texas cities)
city                  string    Kyle | Buda | San Marcos | Dripping Springs
prior_year_mo_levy    float     M&O levy collected in prior fiscal year ($thousands)
this_year_mo_levy     float     M&O levy adopted for this fiscal year ($thousands)
no_new_revenue_rate   float     no-new-revenue M&O rate ($/100 AV)
voter_approval_rate   float     voter-approval M&O rate = NNR × 1.035 ($/100 AV)
actual_rate           float     adopted M&O rate ($/100 AV)
```

### `city_acfr_metrics.csv`

```
year                             integer   fiscal year
city                             string    Kyle | Buda | San Marcos | Dripping Springs
total_levy                       float     total property tax levy adopted ($thousands)
mo_levy                          float     M&O levy ($thousands)
debt_service_levy                float     I&S (interest-and-sinking) levy ($thousands)
certified_value_existing         float     certified appraised value, existing property ($millions)
certified_value_new_construction float     certified appraised value, new construction ($millions)
population                       integer   city population estimate (persons)
```

### `voter_approval_elections.csv`

```
election_date     string   YYYY-MM-DD
city              string   Kyle | Buda | San Marcos | Dripping Springs
election_type     string   tax_rate_election | general_obligation_bond
proposition       string   short ballot text
outcome           string   approved | failed
vote_for_pct      float    % of votes cast in favor (0–100)
vote_against_pct  float    % of votes cast against (0–100)
```

## Notes

- Input CSVs in `inputs/` are committed with synthetic placeholder values so the package builds out of the box. Comments at the top of each file document the schema and sourcing.
- `figures/` is gitignored (root `.gitignore` covers `posts/*/figures/*.png`). Run `python build_figures.py` to regenerate after updating the CSVs.
- The build imports `econ_style` from the repo root via `sys.path.insert(0, str(Path(__file__).resolve().parents[2]))`. The repo must be cloned in full; the script will not run from a detached `posts/sb2-squeeze/` directory.
- `voter_approval_elections.csv` is not currently used by `build_figures.py` but is committed for provenance and future analysis.
