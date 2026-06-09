# Weekly check-in routine

*Spec for a scheduled agent that runs every Monday morning starting
2026-07-06. To be wired into the Claude `/schedule` system once
the remote scheduling service is available again.*

**Cadence:** Every Monday, 8:00 AM Central
(13:00 UTC during CDT, 14:00 UTC during CST)

**First effective run:** Monday, July 6, 2026

**Pause window:** June 8, 2026 → July 6, 2026 — no proactive work
during this window.

## What the agent does each Monday

1. **Overleaf paper check.** Re-check the four currently
   0-byte-evicted Overleaf paper folders on Scott's Dropbox:
   - Bank Deregulation and Carbon Emissions
   - Banking - Municipal Finance
   - Cost-Savings in Hazard Mitigation
   - Extreme Weather - Public Finance

   If any have synced down, parse for title / abstract / coauthors /
   status and surface as candidate /research/ updates.

2. **Other paper diffs.** For each accessible Overleaf paper
   folder (Moneys Together, Tempestates, Weather × Opioid, Weather
   × Minority Employment, Local Finance - Pollution, PPP Discontinuity,
   banking - political philosophy, Minority-Owned Bank Failures,
   Sports Gambling - Tax Revenue, spring-break-risk), diff the
   current content against what's live on /research/. Surface
   meaningful changes (title shifts, abstract revisions, new
   coauthors, status changes).

3. **Calendar check.** Read `~/southbound-35/plan/content-calendar.json`
   and report the next 3 calendar slots. For each, note: title,
   pillar, status (review/planned/drafted), and whether a draft
   PDF exists in `~/Dropbox/southbound-35-drafts/`.

4. **Live site spot-check.** Optional. Hit
   `https://scottlangford2.github.io/scott_langford/` and check
   for obvious breakage (homepage 404, blog landing broken, etc.).
   Skip if it slows the routine.

5. **Monday summary.** Produce a terse, ~10-bullet summary:
   - What changed in Overleaf this week
   - What's next in the blog calendar
   - What's currently in the review queue
   - Anything stuck (still-evicted papers, accounts not set up,
     Worker not deployed, etc.)
   - Open decisions waiting on Scott

## Standing rules

- **Never push live without Scott's review of a PDF.** Everything
  produced is surfaced for review, not auto-deployed.
- **Don't argue with chosen options.** Once Scott picks something,
  execute. No "I'd still recommend X" prefaces.
- **Only working papers go on the public /research/ page.**
  In-progress drafts, exploratory manuscripts, slides, business
  plans, and the like stay private even if they're in the Overleaf
  folder.
- **Four-pillar editorial scope.** Public finance, economic
  development, econometric and statistical analysis, program
  evaluation. Detour topics (sports/religion/off-topic politics)
  are out of scope for new posts; legacy detour posts remain live.

## Cron expression

```
0 13 * * 1   # every Monday at 13:00 UTC
              # = 8 AM CDT (summer) / 7 AM CST (winter)
              # acceptable drift; not worth two separate crons
```

## Files the agent will read

- `~/Dropbox/Apps/Overleaf/*` (paper sources)
- `~/southbound-35/plan/content-calendar.json` (calendar)
- `~/southbound-35/` repo (research page state, plan docs)
- `~/Dropbox/southbound-35-drafts/` (current review queue)
- `https://scottlangford2.github.io/scott_langford/` (live site,
  for spot-check)

## Files the agent does NOT modify

The agent reads-only. Any proposed changes go into a summary
email/note for Scott to review, not direct edits.

## To activate

```
/schedule    # then paste the spec above and pick the cron expression
```

If `/schedule` is unavailable, fallback is manual: Scott pings the
session each Monday and the same routine runs interactively.
