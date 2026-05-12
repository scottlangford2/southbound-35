# Who Will Care for Them? America's Coming Caregiver Shortage

Replication code for the [blog post](https://scottlangford2.github.io/scott_langford/posts/2026/05/alzheimers-caregiver-gap/).

All numerical values come from CSVs in `inputs/`. The build script is purely a renderer; `fetch_data.py` documents the public source URL behind each CSV and refreshes cached raw downloads when possible.

## The problem in one sentence

The number of Americans living with Alzheimer's is on track to roughly double by 2050, and roughly four million U.S. children live with a disability that demands ongoing parental care — yet the paid workforce that supports both populations is growing slowly and at wages that already trail competing low-credential jobs, so an even larger share of care will fall on unpaid family.

## The demographic wave

The driver is age, not lifestyle. Roughly one in three Americans over 85 has Alzheimer's; under 65 the share is well below one percent. So the relevant question is not "is the disease getting more common per person" — it is "how many 85-year-olds are we about to have."

A lot more, it turns out. The Census Bureau's 2023 projections put the 85+ population at about 6.7 million today and 13.7 million by 2040 — a doubling in two decades. The 75–84 cohort grows almost as fast. The 65–74 cohort, by contrast, is flat: the leading edge of the boomers has already moved into the older bands.

![Aging pyramid shift](figures/aging_pyramid_shift.png)

Translating those age curves into disease prevalence gives the headline number that gets quoted in every Alzheimer's Association report: ~6.9 million Americans with Alzheimer's dementia today, ~11 million by 2040, ~13.8 million by 2050.

## A workforce that isn't keeping up

The paid workforce that does the day-to-day work of dementia care — bathing, dressing, transferring, feeding, medication reminders — is concentrated in three Bureau of Labor Statistics occupations: home health aides (HHA), personal care aides (PCA), and certified nursing assistants (CNA). Roughly 5 million workers all in. BLS's Employment Projections expect that workforce to grow about 22% for HHA/PCA and barely 1% for CNAs between 2023 and 2033.

That sounds fast, until you put it next to the demand curve.

![Demand and supply](figures/prevalence_vs_workforce.png)

The shaded red band is the range across data sources for the number of Americans with Alzheimer's: the upper edge is the Alzheimer's Association's all-ages clinical estimate, the lower edge is CMS's count of Medicare fee-for-service beneficiaries with a billed dementia diagnosis. (CMS misses Medicare Advantage enrollees and the undiagnosed, so it is genuinely a lower bound.) The blue line is the paid direct-care workforce, dashed past 2033 where it is the 2023–2033 CAGR extrapolated forward.

The important fact is not whether the lines cross. The paid workforce serves all elderly Americans needing personal-care help, not just those with dementia, so the absolute totals are not directly comparable. The important fact is the *slope*. Demand is compounding at roughly 3% a year. Supply is compounding at roughly 2%. Over twenty years that's a 22% gap in workers-per-patient that has to be filled by something — wages, hours, or unpaid family.

## Why the labor isn't there: wages

The standard story about shortages is that they reflect a market that hasn't cleared: demand has gone up, but wages haven't, so workers haven't been pulled in. Direct care fits that story well.

![Caregiver wages, real](figures/caregiver_wages_real.png)

Adjusting for inflation, the median home health aide earned about $13.60 an hour in 2014 and about $14.50 in 2024 — call it 65 cents an hour of real wage growth over a decade, while the national median for all occupations also barely moved. Personal care aides and nursing assistants did slightly better, but all three sit several dollars below the all-occupations median and a few dollars below what big-box retail and warehouse work currently pay. For a worker choosing between a CNA shift and a fulfillment-center shift at $19/hr with predictable scheduling, the math is straightforward.

The labor-economics framing here is more interesting than the wage gap alone. Direct-care employment is highly concentrated on the buyer side — Medicaid is the single largest payer and sets reimbursement rates that effectively cap wages. That looks a lot like a monopsony, and the empirical literature on Medicaid rate increases finds modest but real employment responses. The implication is that closing the workforce gap is at least partly a public-spending choice, not just a labor-market mystery.

## The invisible workforce

The slack in the system is unpaid family caregiving, and it is enormous.

![Unpaid family caregiving](figures/unpaid_family_burden.png)

In 2024, about 19 billion hours of unpaid care went to people with Alzheimer's and other dementias — the Alzheimer's Association values that at roughly $413 billion at an opportunity-cost wage. For context, total U.S. nursing-home revenue is on the order of $200 billion. The free, mostly-female labor of family caregivers is already larger than the entire paid nursing-home industry.

The incidence is also concentrated. About 46% of dementia caregivers are adult children (mostly daughters); about 30% are spouses; the remaining quarter are other relatives and friends. Adult-child caregivers are usually still in the labor force themselves, and a substantial literature documents the wage and retirement-savings hit they take. The "shortage" of paid caregivers is, in part, just a redistribution: hours that would have been paid at $15 are instead unpaid at $0, drawn from a household's own earnings capacity.

## It's not only the elderly: lifelong care for disabled children

Aging is the most visible driver of the care shortage, but it isn't the only one. In school year 2022–23, U.S. public schools served 7.3 million children ages 3–21 under the Individuals with Disabilities Education Act — about 15 percent of K–12 enrollment. Within that population, roughly 2.3 million children have conditions that typically require significant lifelong care: autism (0.9M), developmental delay (0.5M), intellectual disability (0.4M), and the combined orthopedic / multiple / hearing / visual / TBI categories (0.5M).

![Disabled children burden](figures/disabled_children_burden.png)

The care arc for these populations differs from Alzheimer's in one important way: it doesn't end. Dementia care is intense but usually runs four to eight years from diagnosis. A child diagnosed with severe autism at age three will, in many cases, need substantial daily support for sixty years or more. The lifetime hours add up to something on the order of magnitude of the unpaid dementia caregiving total — and the bulk of those hours fall on parents, overwhelmingly mothers.

The labor-market signature is sharp. Mothers of children without disabilities participate in the labor force at about 73%. Mothers of children with disabilities participate at about 65% — an eight percentage point gap that has been roughly stable for two decades. Translated into headcount, that gap represents around 300,000 mothers who would otherwise be working, with all the cumulative wage, tenure, and retirement consequences that come with leaving or scaling back. As with the Alzheimer's story, the "shortage" of paid caregivers shows up downstream as unpaid family labor and forgone earnings.

The paid workforce for this population — Direct Support Professionals (DSPs) who staff group homes, day programs, and in-home services for people with intellectual and developmental disabilities — has its own shortage of the same character. About 1.4 million DSPs nationally, a median wage around $14–15/hr, and annual turnover above 40 percent. Medicaid sets the rates here too, which means the same monopsony-style wage suppression applies. When the workforce thins, families absorb the difference.

## One labor market, four populations

The most useful way to think about this is as a single care labor market with four populations on the demand side and one workforce on the supply side.

![Combined populations](figures/combined_populations.png)

About 6.9 million Americans with Alzheimer's. About 6.1 million other elderly with at least one activity-of-daily-living limitation who aren't captured in the dementia figure. About 6.5 million adults with intellectual or developmental disabilities. About 3.5 million children with significant disabilities affecting daily care. Twenty-three million people who need substantial ongoing help with basic functioning.

On the supply side, all four populations are served by essentially the same labor pool — home health aides, personal care aides, certified nursing assistants, and direct support professionals. About 6.5 million paid workers in total. The math is uncomfortable: roughly three-and-a-half care recipients for every paid worker. The slack has to come from somewhere, and the somewhere is overwhelmingly unpaid family labor.

Treating elderly care and disability care as separate problems with separate budgets, separate workforces, and separate policy levers obscures a structural reality. The wages compete in the same local labor market against warehouse and retail. The reimbursement comes from the same Medicaid line. The training pipelines overlap. A wage floor that lifts CNAs out of the lowest tier also lifts DSPs. A Medicaid rate freeze that pushes home health aides out of the field also pushes DSPs out. It is one market.

## States that pay more get more workers

If the workforce problem really is a wage problem, then states that pay more — through higher Medicaid HCBS reimbursement rates — should have more direct-care workers per elderly resident. They do.

![State Medicaid scatter](figures/state_medicaid_scatter.png)

The cross-state correlation is striking. Across the 50 states plus DC, Medicaid HCBS spending per capita explains the bulk of the variation in how many direct-care workers a state has relative to its 65-plus population. New York spends roughly $1,240 per resident and has 128 direct-care workers per 1,000 elderly. Mississippi spends $250 and has 38. Texas, which is the natural Southbound 35 case, sits in the low-spend, low-workforce corner: $310 in HCBS spending per capita, 46 workers per 1,000 elderly. About a third of New York's intensity, on both axes.

A causal interpretation needs care. States that spend more on HCBS tend to have higher costs of living, higher taxes, and different demographics. But the correlation is what we would expect from a labor market where the marginal worker chooses between care and competing low-wage employers, and where the wage in care is set by Medicaid. The cleaner causal evidence — Matsudaira's nurse-staffing identification, Ruffini's minimum-wage natural experiments, Hackmann's Medicaid-reform estimates — points the same direction.

The implication is concrete: states that want more caregivers can have them, at a price. The price shows up in state and federal Medicaid budgets, and the elasticity is real but not infinite.

## A Texas zoom

The cross-state pattern is most useful when it forces a comparison with the local case. Texas direct-care wages, in the May 2024 BLS Texas state estimates, run several dollars below the competing low-credential jobs that draw from the same labor pool.

![Texas wages vs competitors](figures/texas_wages_competitors.png)

A home health aide in Texas earns about $13.20/hr at the median. A Texas DSP earns about $13.60. A personal care aide, about $13.95. A CNA, about $15.80 — the highest of the four, and still below retail. Meanwhile a stocker at a Texas warehouse earns $17.40. An Amazon fulfillment-center associate starts around $19.50 with benefits and a predictable schedule. Retail salespersons clear $14.85 with less physical and emotional toll. Even Texas fast-food work, at $11.95, lands within a dollar or two of the lower end of direct care.

The math for an individual Texas worker choosing between, say, an HHA position at a home health agency and a starting role at an Amazon FC is not subtle. There is roughly a $6/hr gap, before counting benefits, schedule predictability, and the difference in physical and emotional labor. Multiply that across the 380,000 direct-care workers Texas employs and the gap is on the order of $5 billion per year in foregone wages relative to comparable jobs — money that, under a different Medicaid rate structure, could be the difference between the workforce growing or shrinking. Texas is the case where the state-rate scatter sits at its lower extreme, and the local wage comparison shows the mechanism.

## After COVID: a temporary spike, then the snap-back

One thing the 2014–2024 real-wage figure obscures by smoothing is what happened during and after the pandemic. Direct-care wages actually spiked sharply in 2020 and 2021, in both nominal and real terms, as employers competed for scarce workers, signing bonuses appeared in classifieds, and federal emergency funding flowed to Medicaid HCBS programs through the American Rescue Plan Act. For a brief window, home health aide median wages rose faster than the all-occupations median for the first time in a decade.

Then inflation caught up. Real wages for caregivers in 2024 are back near where they were in 2020 — the nominal gains were almost entirely eroded by 2022-2023 inflation. Federal ARPA HCBS funding has wound down. The wage gap with warehouse and retail has reopened. The pandemic was a natural experiment in what wages it would take to attract caregivers in a tight labor market; the result was about $2–3/hr in real wages for a few years, which gives a rough revealed-preference measure of the elasticity the labor market is operating at.

The other lasting post-COVID change is on the supply side. Immigration of care workers — historically a major source of growth in the U.S. direct-care workforce, particularly in personal care and DSP roles — has been disrupted by visa backlogs and policy uncertainty since 2020. About a quarter of the U.S. direct-care workforce is foreign-born, and the share is higher in HCBS-rich states like California and New York. If immigration policy remains restrictive, the elasticity that closes the workforce gap is lower than the pre-2020 literature assumes, and the wage required to attract domestic workers in sufficient numbers is correspondingly higher.

## What it would take to close the gap

Two rough calibrations are useful for thinking about the size of the policy lever.

First, the demand side. If the dementia population grows from ~6.9 million today to ~11 million by 2040 (a 60% increase) and the workers-per-patient ratio stays constant, the paid direct-care workforce needs to grow at the same 60% — to roughly 8 million workers. BLS's current trajectory gets to about 7.4 million by 2040 on the dashed extrapolation. That is a 600,000-worker shortfall on conservative assumptions; doubling the prevalence growth or assuming higher dementia-specific staffing ratios pushes it past a million.

Second, the wage side. Estimates of labor-supply elasticity in low-credential service occupations cluster around 1–2 — meaning a 10% real wage increase pulls in 10–20% more workers. Closing a 15% workforce gap, at a midpoint elasticity, takes something like a 10% real wage increase across the three occupations. At today's wage levels and headcounts, that is on the order of $15–20 billion a year in additional compensation — which, given Medicaid's payer share, lands largely on federal and state budgets.

Neither of those calibrations is a forecast. They are bounds. The point is that the order of magnitude is tractable, and the policy levers (Medicaid rate floors, training subsidies, immigration of care workers) are well-known. The labor problem is real, and it is also solvable in the same boring way most labor problems are solvable: pay enough to attract the workers.

The same arithmetic applies, with a few adjustments, to the Direct Support Professional workforce that serves people with intellectual and developmental disabilities. The workforce is smaller, the wage gap relative to retail and warehouse work is wider, and the turnover rate is dramatically higher — but the policy levers are the same Medicaid rate floors. A combined approach is more efficient than treating elderly care and disability care as separate problems with separate solutions: they draw from the same labor pool, are paid by the same payer, and lose workers to the same competing low-credential jobs.

## Data and methods

Real wages are deflated using the BLS CPI-U All Urban Consumers annual average, base year 2024. Workforce projections beyond 2033 use the 2023–2033 BLS Employment Projections compound annual growth rate, applied through 2040. Alzheimer's prevalence is shown as a range across two reasonable definitions (Alzheimer's Association clinical, CMS diagnosed in Medicare FFS) rather than picking one. Unpaid caregiving hours are valued at the Alzheimer's Association opportunity-cost wage, restated in 2024 USD.

## Quickstart

```bash
pip install -r requirements.txt
python fetch_data.py        # optional; documents sources and caches raw downloads
python build_figures.py
```

Figures are written to `figures/` (gitignored — regenerate from code).

## Files

```
posts/alzheimers-caregiver-gap/
├── README.md
├── requirements.txt
├── fetch_data.py                  # source URLs + optional raw cache
├── build_figures.py               # reads inputs/, writes figures/
├── inputs/
│   ├── alz_prevalence.csv         # year × scenario → cases (millions)
│   ├── direct_care_workforce.csv  # year × occupation → employment (thousands)
│   ├── wages_real.csv             # year × occupation → median wage (2024 USD/hr)
│   ├── pop_projections.csv        # year → 65-74 / 75-84 / 85+ (millions)
│   ├── unpaid_caregiver_hours.csv  # year → hours, imputed value, relationship shares
│   ├── disabled_children.csv       # IDEA categories + mothers' LFPR by child disability
│   ├── combined_populations.csv    # populations needing intensive care + paid workforce
│   ├── state_medicaid_workforce.csv# state HCBS spend × direct-care workers per 1k 65+
│   └── texas_zoom.csv              # Texas wages: direct care vs. competing jobs
└── figures/                        # build output (gitignored)
```

## Figures

| # | File | Description |
|---|------|-------------|
| 1 | `prevalence_vs_workforce.png` | Alzheimer's prevalence range vs. direct-care workforce, 2020–2040 |
| 2 | `caregiver_wages_real.png` | Real median hourly wage by occupation, 2014–2024, in 2024 USD |
| 3 | `aging_pyramid_shift.png` | U.S. population by age band, 2020 vs. 2040 |
| 4 | `unpaid_family_burden.png` | Unpaid dementia-caregiving hours and imputed value, with caregiver-relationship breakdown |
| 5 | `disabled_children_burden.png` | Children served under IDEA by category; mothers' labor force participation gap |
| 6 | `combined_populations.png` | Four populations needing intensive ongoing care, with the paid workforce as a reference line |
| 7 | `state_medicaid_scatter.png` | State Medicaid HCBS spending per capita vs. direct-care workers per 1,000 elderly |
| 8 | `texas_wages_competitors.png` | Texas direct-care wages vs. competing low-credential jobs, May 2024 |

## Data sources

### `inputs/alz_prevalence.csv`
U.S. Alzheimer's prevalence, millions of people, by year and scenario.

- **`alz_assoc`:** Alzheimer's Association *2024 Facts & Figures*, Table 1 (prevalence projections). Hub: <https://www.alz.org/alzheimers-dementia/facts-figures>. Numerical tables are factual and transcribed by hand into this CSV.
- **`cms_medicare_ffs`:** CMS Chronic Conditions Warehouse, "Alzheimer's Disease and Related Disorders" prevalence among Medicare FFS beneficiaries 65+. Tool: <https://www.cms.gov/data-research/statistics-trends-and-reports/chronic-conditions>.

### `inputs/direct_care_workforce.csv`
U.S. employment (thousands) for home health & personal care aides (SOC 31-1120) and nursing assistants (SOC 31-1131).

- **Historical:** BLS OEWS May national estimates. <https://www.bls.gov/oes/tables.htm>.
- **Projected:** BLS Employment Projections 2023–2033 occupation table. <https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm>. Values past 2033 are linearly extrapolated at the 2023–2033 CAGR.

### `inputs/wages_real.csv`
Median hourly wages by occupation, deflated to 2024 USD using BLS CPI-U All Urban Consumers (annual avg, 2024 = 313.7).

- **Nominal wages:** BLS OEWS May national estimates for SOC 31-1011 / 31-1120 (home health aides), 31-1021 / 31-1122 (personal care aides), 31-1014 / 31-1131 (nursing assistants), and the all-occupations national median.
- **CPI-U:** <https://www.bls.gov/cpi/data.htm>, series CUUR0000SA0, annual averages.

### `inputs/pop_projections.csv`
Census Bureau 2023 National Population Projections, main series (NP2023_D1), aggregated to 65–74, 75–84, and 85+ bands. <https://www.census.gov/data/datasets/2023/demo/popproj/2023-popproj.html>.

### `inputs/unpaid_caregiver_hours.csv`
Unpaid family caregiving for people with Alzheimer's and other dementias.

- **Hours and imputed value:** Alzheimer's Association *Facts & Figures* (annual editions), unpaid caregiving tables; opportunity-cost wage assumption restated in 2024 USD.
- **Caregiver-relationship shares:** AARP / National Alliance for Caregiving, *Caregiving in the U.S.* surveys. <https://www.aarp.org/caregiving/research/caregiving-in-the-united-states.html>.

### `inputs/disabled_children.csv`
Two related panels: U.S. children served under IDEA by primary disability category (school year 2022–23) and labor force participation of mothers by disability status of youngest child.

- **IDEA categories:** U.S. Department of Education, EDFacts / IDEA Section 618 state-reported data. <https://sites.ed.gov/idea/data/>.
- **Mothers' LFPR:** Census Bureau CPS ASEC tabulations summarized in the disability-economics literature (e.g., Powers 2003, *J. Health Economics*; Stabile & Allin 2012, *Future of Children*); updated using recent BLS CPS unpublished tabulations.

### `inputs/combined_populations.csv`
Four U.S. populations needing intensive ongoing care (2024) plus the paid direct-care + DSP workforce serving them, in millions of people.

- **Alzheimer's & other dementias (65+):** Alzheimer's Association *2024 Facts & Figures*.
- **Other elderly with ADL limitations:** Census ACS and Health and Retirement Study (HRS) estimates of 65+ Americans with at least one ADL limitation, net of those already counted under dementia.
- **Adults with IDD:** CDC NHIS combined with Larson et al. (2023), *Status and Trends Through 2022*, U Minn Research and Training Center on Community Living.
- **Children with significant disabilities:** CDC NHIS and Census ACS combined estimate of children under 18 with a disability affecting daily functioning.
- **Paid workforce:** BLS OEWS 2024 plus ANCOR State of America's Direct Support Workforce Crisis (for the DSP component).

### `inputs/state_medicaid_workforce.csv`
State-level cross-section, 50 states plus DC. Two columns: Medicaid HCBS spending per capita (FY2022) and direct-care workers per 1,000 residents age 65+ (2024).

- **HCBS spending:** Kaiser Family Foundation state HCBS programs reports, FY2022. <https://www.kff.org/medicaid/state-indicator/total-medicaid-hcbs-spending/>.
- **Workforce per 1,000 elderly:** BLS OEWS state estimates (HHA + PCA + CNA, 2024) divided by Census ACS 1-year state 65+ population estimates.

### `inputs/texas_zoom.csv`
Texas state median hourly wages, May 2024, for direct-care occupations and competing low-credential jobs.

- **Direct care (HHA, PCA, CNA):** BLS OEWS Texas state estimates. <https://www.bls.gov/oes/current/oes_tx.htm>.
- **DSP:** ANCOR *State of America's Direct Support Workforce Crisis* annual report, Texas state cut.
- **Competitors:** BLS OEWS Texas state estimates for stockers (SOC 53-7065), retail salespersons (SOC 41-2031), and fast food workers (SOC 35-3023); Amazon FC starting wage from company-posted Texas-metro job listings.

## Schemas

### `alz_prevalence.csv`
```
year, scenario, cases_millions
```
`scenario` ∈ {`alz_assoc`, `cms_medicare_ffs`}.

### `direct_care_workforce.csv`
```
year, occupation, employment_thousands
```
`occupation` ∈ {`hha_pca`, `cna`}.

### `wages_real.csv`
```
year, occupation, median_wage_real_2024
```
`occupation` ∈ {`hha`, `pca`, `cna`, `all_occ`}. Wage column is in 2024 USD per hour.

### `pop_projections.csv`
```
year, age_65_74, age_75_84, age_85plus
```
Units: millions of people.

### `unpaid_caregiver_hours.csv`
```
year, hours_billions, imputed_value_billions_usd_2024,
share_spouse, share_adult_child, share_other
```
Shares are proportions summing to 1.0 within rounding.

### `disabled_children.csv`
```
panel, key, label, value
```
`panel` ∈ {`idea_categories`, `mothers_lfpr`}. For `idea_categories`, `value` is millions of children. For `mothers_lfpr`, `value` is a proportion (0–1).

### `combined_populations.csv`
```
population, label, millions
```
`population` ∈ {`alz_dementia`, `elderly_adl`, `idd_adults`, `disabled_kids`, `paid_workforce`}.

### `state_medicaid_workforce.csv`
```
state, hcbs_per_capita_usd, direct_care_per_1k_65p
```
`state` is USPS abbreviation (50 states + DC).

### `texas_zoom.csv`
```
occupation, group, median_wage_2024
```
`group` ∈ {`care`, `competitor`}.

## Notes

CSV files in `inputs/` are committed so the package builds out of the box. Numerical values reflect the most recent public releases at the time of writing and should be refreshed from the cited BLS, Census, CMS, and Alzheimer's Association sources before press. The post-2033 segment of Figure 1 is a CAGR extrapolation, not a BLS forecast, and is rendered as a dashed line for that reason.
