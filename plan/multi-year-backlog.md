# Southbound 35 — multi-year content backlog

*Companion to `content-calendar.json` and `build_calendar.py`. The JSON is the per-Monday schedule; this doc is the topic universe organized by series, with rough year-of-publication windows and dependency notes. When the rolling 52-week horizon shrinks, draw the next slot from here.*

*Last updated: 2026-06-05.*

---

## Year 1 (June 2026 – May 2027) — coverage status

The script already slots 52 weeks of high/medium-certainty content for Year 1. Pillar mix:

- **Pillar 2 (economic development / corridor case studies):** ~31 of 52 weeks. Hays follow-ons (4), full Comal series (5), full Caldwell series (5), full Guadalupe series (5), full Southern-Travis series (4), full Eastern-Blanco series (3), plus 5 of the I-35 framing posts.
- **Pillar 1 (public finance mechanics):** ~8 of 52 weeks. Property-tax mechanics finishes (TIT, appraisal districts, homestead/cap). Sales-tax mechanics series starts and finishes.
- **Pillar 3 (econometric/statistical):** ~5 of 52 weeks. Pacing one per ~10 weeks.
- **Pillar 4 (program evaluation):** ~5 of 52 weeks. Type A/B EDCs, HB 3, SB 2, plus 2 corridor-specific evaluations.
- **Annual anchors:** 3 fixed (bond preview, bond results, year-in-review).

Year 1 is fully populated and high-confidence. No backlog draws needed here unless a calendar entry is killed.

---

## Year 2 (June 2027 – May 2028) — coverage status

The script slots Year 2 from the same backlogs at medium / low certainty. By the end of Year 2:

- All Ring-2 corridor series finished (Williamson, Bexar Northside, Bastrop edge).
- Special-districts mechanics series finished.
- State-aid-formulas mechanics series finished.
- Bond mechanics series finished.
- ~9–10 more pillar-3 stats posts; ~9–10 more pillar-4 evaluations.
- 2027 legislative-session posts (Jan–May 2027) slotted as fixed anchors.

This is where backlog draws start mattering — the script will exhaust some queues mid-Year-2 and pull fillers from whatever is left.

---

## Year 3 (June 2028 – May 2029) — backlog needed

By Year 3, the original backlogs in `build_calendar.py` run out. The trailing ~37 slots are tagged `tbd / UNASSIGNED`. This is where the doc below comes in. The topics listed are not yet in the generator script but are credible Year-3 candidates.

---

## Series roadmap — what's in the existing backlog

### Pillar 2 — corridor case studies

| Series | Posts | Build ring | Approx window | Status |
|---|---|---|---|---|
| Hays follow-ons | 4 | 0 | Jul–Aug 2026 | in script |
| Comal | 5 | 1 | Aug–Oct 2026 | in script |
| Caldwell | 5 | 1 | Oct–Dec 2026 | in script |
| Guadalupe | 5 | 1 | Jan–Mar 2027 | in script |
| Southern Travis | 4 | 1 | Mar–May 2027 | in script |
| Eastern Blanco | 3 | 1 | May–Jun 2027 | in script |
| Williamson | 5 | 2 | Jul–Sep 2027 | in script |
| Bexar Northside | 5 | 2 | Oct–Dec 2027 | in script |
| Bastrop edge | 4 | 2 | Jan–Mar 2028 | in script |
| **I-35 framing (interleaved)** | 8 | — | Throughout | in script |

### Pillar 1 — public finance mechanics

| Series | Posts in backlog | Approx window |
|---|---|---|
| Property tax mechanics | 5 (3 in 20-week + 2 follow-ons) | Jun–Sep 2026 |
| Sales tax mechanics | 4 | Sep 2026 – Jan 2027 |
| Special districts | 4 | Feb–May 2027 |
| State aid formulas | 4 | Jun–Sep 2027 |
| Bond mechanics | 4 | Oct 2027 – Jan 2028 |

### Pillar 3 — econometric / statistical analysis

16 topics in the backlog; paced ~one per 10 weeks → fills through early 2029.

### Pillar 4 — program evaluation

16 topics in the backlog; paced ~one per 10 weeks → fills through early 2029.

---

## Year-3 backlog additions (not yet in script)

The 37 trailing `tbd` slots in the calendar should be populated from these candidates. Each is credibly publishable but flagged as "fill once the immediate-term series are done" rather than slotted today.

### Pillar 2 — second-pass corridor work

Posts that revisit counties already covered, with a different question:

1. Hays at five years (Nov 2026 → Nov 2031 trajectory check)
2. Comal at three years post-Edwards permit reform
3. Williamson after the Samsung Phase-2 commitment (assumes Phase 2 announced)
4. The Caldwell–Bastrop SH 130 development band
5. The eastern-Travis development pattern after the Tesla-area buildout
6. The Bexar Northside annexation reversal (if any city repeals)
7. Comparison: which corridor county had the best decade?
8. The corridor's lowest-growth county — and why
9. Cross-corridor: ESDs that work and ESDs that don't
10. Cross-corridor: MUDs at the moment of city annexation

### Pillar 1 — third pillar mechanics series

After bond mechanics, three further mechanics series:

1. **Annexation mechanics** (3 posts): the post-2017 limited annexation regime, ETJ rules, disannexation
2. **TIF / TIRZ mechanics** (3 posts): chapter 311 mechanics, how the increment is calculated, what cities have used it for
3. **Local economic development incentive mechanics** (3 posts): Chapter 380/381, Texas Enterprise Zones, hotel occupancy tax incentives

### Pillar 3 — second-pass stats

Topics that revisit methodology with a year of intervening practice:

1. The pitfalls of difference-in-differences with continuous treatment
2. Synthetic control with multiple treated units (Texas)
3. Spatial spillovers in county-level outcomes
4. Bayesian approaches to small-area Texas estimates
5. Machine learning for predicting bond-election outcomes
6. Causal forests applied to a Texas program

### Pillar 4 — second-pass evaluation

Programs that need re-evaluation as new years of data accrue:

1. Type A/B EDCs revisited (one year of new audits)
2. HB 3 compression at five years
3. SB 2 levy caps at five years
4. Tesla Austin at five years
5. Samsung Taylor at two years
6. The Chapter 313 successor program (if enacted in 2027 or 2029 lege)
7. The 2027 lege session's enacted property-tax reforms — evaluation

### Topical / event-driven (held in reserve)

Posts to write when triggered by external events, not on a fixed calendar:

- Major bond election results that warrant a follow-up post
- Court rulings on Texas school finance
- Major Comptroller revenue estimate revisions
- A significant special-district scandal or reform proposal
- Major water-supply decisions (e.g., new SAWS contract)
- TXST-specific finance news that matters for the corridor

---

## How to refresh the calendar from this backlog

1. Edit the relevant `*_BACKLOG` list in `build_calendar.py` to add the new topics (in series order).
2. Re-run `python build_calendar.py > content-calendar.json`.
3. The rotation pattern in `slot_pillar()` will continue paint-by-numbers; new topics flow into the previously-`tbd` slots.
4. Adjust the rotation pattern only if the pillar mix needs to change (e.g., more program evaluation, less mechanics).

To kill a calendar slot, set its certainty in the script to "high" and replace its title — don't edit `content-calendar.json` directly, because the next regeneration will overwrite it.

---

## Honest caveats

- The Year-3 tbd slots are real placeholders. The series enumerated above are best-current-guess topics, not promises. The blog's editorial direction in mid-2028 will reflect what's actually happening in Texas finance then — including the outputs of the 2027 lege session, the 2026/2028 election cycles, and unforeseeable events.
- Annual anchors (year-in-review, bond preview/results, lege session) are the most stable items in this calendar. They will almost certainly happen on the slots indicated.
- The Year-1 high-certainty slots are the operational plan. Year-2 medium-certainty is a strong working plan. Year-3 low-certainty is a credible reservation of slot time, not a commitment to specific topics.
