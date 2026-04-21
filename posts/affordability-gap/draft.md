---
title: 'The Hays Discount, Five Years Later'
date: 2026-04-21
permalink: /posts/2026/04/hays-discount/
related: false
tags:
  - Hays County
  - Texas
  - housing
  - public finance
---

Two weeks ago I put a single number at the center of [the Hays County
growth post][growth]: $135,000. That was the gap, in February 2026,
between the median home in Travis County and the median home in Hays
County — the rough math a family is doing when they pull off I-35 in
Buda or Kyle instead of continuing north.

A reader emailed to ask the obvious follow-up. Has it always been
$135,000? If Hays County's whole growth story runs on an affordability
arbitrage, the shape of that arbitrage over time is worth understanding.

This post is the answer, with three upgrades over the napkin version: a
triangulated price series so we aren't relying on one dataset, a full
PITI monthly cost so we aren't pretending property taxes and
homeowners' insurance don't exist, and proper statistics on the
"constant premium" claim. The full code and a data manifest with
checksums are in the [replication folder][repl] — anyone who wants to
rerun the analysis on a fresh Zillow release should get the same
numbers.

## Everyone Rode the Same Wave

Start with levels. The Zillow Home Value Index for Travis, Williamson,
and Hays rose sharply through 2021 and early 2022, peaked inside a few
months of each other in mid-2022, and has been grinding lower since.
The ordering that makes the growth story work — Travis on top, Hays at
the bottom — never breaks.

![Central Texas home values, 2020 → present](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_levels.png)

## The Dollar Gap Bulged, Then Pulled Back

Subtract, and the absolute Travis-over-Hays gap ran from about $100K
at the start of 2020, peaked near $175K in July 2022, and has settled
near $135K.

![Absolute gap over Hays, 2020 → present](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_absolute.png)

That $40K swing is not small. If you stopped here you might conclude
that Hays's relative advantage eroded during the pandemic boom and
then partly recovered. You would be reading the wrong statistic.

## Triangulate Before Concluding

Before leaning too hard on one series, it's worth asking whether a
different source tells a different story. ZHVI is an index of home
*values* derived from Zillow's own estimates. The Federal Housing
Finance Agency publishes a repeat-sales index (HPI) that uses only
arms-length transaction pairs and is therefore immune to compositional
drift — an important concern in a fast-growing county where the typical
home this year is newer, bigger, and further out than last year's.
Realtor.com publishes median *listing* prices, which reflect what's on
the market rather than what's traded.

Three series, one qualitative answer:

![Three sources, one invariant](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_triangulation.png)

Levels differ, but all three tell the same story about the *premium*
of Travis over Hays: it does not trend. That convergence across
methodologies is the closest we get to a robustness certificate
without running the whole analysis twice.

## How Constant Is "Constant"?

Eyeballing a flat line is not a statistical claim. Three tests on the
premium ratio:

- **Mean and HAC confidence interval.** The full-window mean is
  **≈ 37 %** with a 95 % Newey–West confidence interval less than a
  percentage point wide. The migration-relevant fact is where we are
  on that interval — not whether the ratio is drifting outside it.
- **AR(1) persistence.** The ratio's first-order autocorrelation is
  **≈ 0.99**. Monthly shocks dissipate slowly, as you'd expect for a
  highly sticky relative-price relationship.
- **Quandt–Andrews sup-F unknown-break test.** Against a null of a
  single constant mean, the test rejects — there *is* a detectable
  small break, visible as the sub-panel below. But the magnitude of
  the shift is a fraction of a percentage point, and it lives inside
  the 95 % CI. In plain English: the premium isn't literally constant,
  but it moves in tenths of a percentage point, not percentage points.

![Premium statistics](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_relative_stats.png)

## Real Dollars, Not Just Nominal

The second napkin-version simplification was quoting the gap in
nominal dollars. CPI rose roughly 20 % over the window. In Jan-2020
dollars the peak gap is smaller, and the narrowing from peak to today
is less severe: some of the "contraction" was just general inflation.

![Real vs. nominal gap](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_real_nominal.png)

Not a big correction, but it moves the story from "the gap is closing"
to "the gap is approximately where it was in real terms."

## Rates Did Most of the Work — Until You Count Everything

The first draft claimed "rates did the work": financing $100K at 3 %
cost $420/month; financing $135K at 7 % costs $890; the monthly cost of
the gap more than doubled even as the absolute gap narrowed.

That's still directionally right, but it ignores the rest of the
monthly bill. Three components that matter:

- **Property tax.** Travis's effective rate (county + city + ISD + ESD)
  runs about 1.8 % of value. Hays's runs closer to 2.1 %, and many
  Hays neighborhoods sit inside a MUD or PID on top of that. On the
  *gap* itself, a higher Travis price means a higher Travis tax bill —
  adding to the cost of choosing north.
- **Homeowners insurance.** TDI data show Hays households paying
  modestly more than Travis households — wildfire and hail exposure
  east of the Balcones escarpment. That partially offsets the extra
  Travis tax bill.
- **MUD / PID assessments.** Many new Hays subdivisions carry a MUD
  rate of $0.75–$1.00 per $100 AV on top of everything else. Travis's
  mid-tier stock is mostly inside the City of Austin, where MUDs are
  rare. Choosing Travis typically means escaping the MUD.

Stacking these together, the full PITI monthly-cost gap looks like
this:

![PITI decomposition](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_piti.png)

Two notes. First, at today's rates the P&I gap alone overstates the
total cost of choosing Travis by roughly $150/month once MUD and
insurance offsets are credited — not a trivial difference for a family
running an affordability calculation. Second, the rate-driven doubling
of the P&I gap is still the largest single force; the full PITI gap
roughly doubled over the window even after offsets.

So: *rates did most of the work, but not all of it.*

## Does the Picture Survive Robustness Checks?

Two honest worry points for the headline premium.

**Is this about the top of the market?** Maybe Travis's "median" is
pulled up by a Westlake-and-Tarrytown shelf a typical migrator never
considers. Pulling ZHVI's tiered series answers this directly: the
*bottom* tier of each county (the 0-to-33rd percentile — what most
Austin-to-Hays migrators actually buy) shows a Travis-over-Hays
premium close to the mid-tier number. The story doesn't depend on
luxury Travis stock.

![Robustness across ZHVI tiers](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_tiers.png)

**Is this an Austin-specific oddity?** To test whether "edge county
discount of ≈ 38 %" is a general Texas metro-edge phenomenon or just
Austin-specific, compare to the DFW pair most analogous to
Travis/Hays: Collin (wealthy core suburb) over Denton (faster-growing
edge). The two series don't overlap perfectly — DFW's premium is
smaller and has moved more — but the levels are in the same
neighborhood, and both are remarkably flat. The 38 % number is
specific to Austin; the *stable-premium* structure appears to be
general.

![Austin vs. DFW](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_out_of_metro.png)

## Does the Gap Actually Drive Migration?

Prices are a pressure, not a flow. The Hays migration story has
assumed that the price gap is the forcing function; IRS Statistics of
Income county-to-county migration data let us at least sketch the
correlation. Annual in-migration to Hays (exemptions, origin ≠ Hays)
plotted against the prior-year average Travis → Hays gap:

![Migration response](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/migration_response.png)

With only five years of SOI releases and one lag consumed, this is
illustrative, not inferential — the standard errors are large enough
to swallow any coefficient we report. Still, the slope has the sign
the story would predict. A post with real identification, not just
correlation, would need IV on rates or a shift-share pulling gap
variation out of metro-wide price movements. That is a bigger post.

## What This Adds Up To

The first version of this analysis made three claims, all roughly
right, none of them quite rigorous:

1. The absolute gap is volatile and has narrowed from peak.
2. The percentage premium is constant.
3. Rates drove the monthly cost of the gap.

The rigorous version updates each:

1. The absolute nominal gap did narrow from peak. The *real* gap is
   closer to flat. Both framings survive triangulation across Zillow,
   FHFA, and Realtor.
2. The premium isn't literally constant — there's a detectable small
   break — but its variation lives inside a confidence interval less
   than a percentage point wide. For migration-decision purposes,
   treat it as constant.
3. The P&I story is the dominant story, but once you include the
   Hays-specific MUD and insurance surcharges and the Travis-specific
   property-tax premium, the full PITI gap is roughly $150/month
   smaller than P&I alone suggests at today's rates. The doubling
   still happens. It's just a smaller double.

None of which changes the punchline: the migration pressure that
built Hays County over the last fifteen years hasn't eased. If
anything, at 7 % rates it's heavier on a monthly-payment basis than
it was when rates were at 3 %.

## Limitations

A short, honest list of what this analysis does *not* do.

- **County medians hide city variation.** Kyle ≠ Dripping Springs ≠
  San Marcos. A city-level analog is a next post.
- **The PITI property-tax and insurance estimates are point values
  with known dispersion.** Effective rates vary by ISD and by city by
  ±0.2 percentage points. A full sensitivity pass is in
  `analysis.breakeven_tax()` (stubbed but not yet rendered as a
  figure). The MUD assumption (Hays has one, Travis doesn't) holds
  for mid-tier median addresses; fringe Travis addresses can carry
  MUDs too.
- **The migration regression is correlational with n = 3.** Do not
  read a policy elasticity out of it.
- **All price series are nominal-dollar, pre-tax.** A household with
  capital-gains-exclusion considerations on an Austin sale will face
  a different math than the stylized first-time buyer implicit above.

---

## Sources

Zillow Home Value Index (all homes, tiered mid / bottom / top, SA,
smoothed, county). Zillow median price per square foot. FHFA House
Price Index, all-transactions, county (quarterly). Realtor.com median
listing price (FRED). Freddie Mac Primary Mortgage Market Survey 30-
year fixed rate (FRED: `MORTGAGE30US`). BLS CPI-U All items (FRED:
`CPIAUCSL`). IRS Statistics of Income county-to-county migration
inflows, 2019–2023. Texas Comptroller Truth-in-Taxation for effective
property tax rates. Texas Department of Insurance 2024 Home Insurance
Price Comparison for annual premiums.

Replication code, data manifest, and per-file checksums:
[southbound-35/posts/affordability-gap][repl].

[growth]: {{ site.baseurl }}/posts/2026/04/hays-county-growth/
[projections]: {{ site.baseurl }}/posts/2026/04/hays-county-projections/
[repl]: https://github.com/scottlangford2/southbound-35/tree/main/posts/affordability-gap

## Disclosure

This blog post was written with the assistance of Claude (Anthropic).
Claude helped with data research, code, and drafting. All analysis and
editorial judgment are the author's.
