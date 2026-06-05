# Pillar-3 topic candidates: sports + Texas country music

*Topic backlog for econometric / statistical analysis posts that use sports or Texas country music as their empirical setting. Each candidate is fundamentally a methods post — the sport or the music is the data source, not the subject. Same lane as the legacy LIV defectors and Golf Clutch posts.*

*Last updated: 2026-06-05.*

---

## How to read this list

Each entry has:

- **Method** — the statistical / econometric technique the post illustrates
- **Setting** — the sport or event that supplies the data
- **Texas hook** — corridor/state relevance (★ = strong, ☆ = weak, — = none)
- **Window** — when the post is timely (driven by the sport's calendar)
- **Data path** — where the data realistically comes from
- **Notes** — anything that makes the post easier or harder

The strongest candidates are starred at the end of each section.

---

## PGA Tour (Jan – Aug + FedEx Cup playoffs)

### 1. Strokes-gained methodology, explained ★
- **Method:** decomposition of a noisy outcome into orthogonal components
- **Setting:** PGA Tour strokes-gained data (Data Golf, ShotLink summaries)
- **Texas hook:** ★ — Valero Texas Open (San Antonio, April) and Charles Schwab Challenge (Fort Worth, May) as the in-text examples
- **Window:** mid-April (Valero) or mid-May (Schwab) for max relevance
- **Data path:** Data Golf public CSVs; PGA Tour stat pages
- **Notes:** Pedagogical, very high reuse value. The follow-on to Golf Clutch.

### 2. The cut line as a regression discontinuity
- **Method:** RDD around the made-cut / missed-cut threshold
- **Setting:** every PGA Tour event, ~40 cuts per year
- **Texas hook:** ☆
- **Window:** anytime; reference any major-week
- **Data path:** Data Golf player-tournament results
- **Notes:** Classic RDD setup; ask whether barely-making-cut affects next-week field selection or career trajectory.

### 3. The Masters: how predictable are repeat contenders?
- **Method:** Bayesian updating of pre-tournament priors
- **Setting:** Masters field, 1990–2026
- **Texas hook:** —
- **Window:** Masters week (early April)
- **Data path:** Augusta historical leaderboards (scraped)
- **Notes:** Time-sensitive; only a few weeks per year.

### 4. LIV / PGA field-strength rebalance
- **Method:** synthetic control of PGA Tour field strength post-LIV
- **Setting:** OWGR scores by tournament, 2019–2026
- **Texas hook:** —
- **Window:** post-major-season (August), when the reunification narrative is loudest
- **Data path:** OWGR public ranking points; Data Golf field-strength
- **Notes:** This is the follow-up to the legacy LIV defectors post. The reunification (if it happens) gives a clean treatment date.

### 5. Putting under pressure, revisited
- **Method:** hierarchical model of putt-make probability with pressure covariates
- **Setting:** ShotLink putting data
- **Texas hook:** —
- **Window:** anytime mid-season
- **Data path:** ShotLink summaries; Data Golf
- **Notes:** A more rigorous follow-up to Golf Clutch.

### 6. Scheffler one-year-later (without theology this time) ★
- **Method:** individual-level trajectory model
- **Setting:** Scheffler's 2024–2026 round data
- **Texas hook:** ★ — Dallas-area resident; SMU; Texas roots
- **Window:** April 2027 (Masters anniversary)
- **Data path:** Data Golf player profile
- **Notes:** Bookend to the Ecclesiastes post but rebuilt as a pure trajectory-analysis piece. No theology.

**Strongest PGA candidates:** #1 (strokes-gained explained), #6 (Scheffler trajectory), #4 (LIV/PGA synthesis).

---

## NBA (Oct 2026 – Jun 2027)

### 1. Tank threshold as RDD ★
- **Method:** RDD around the play-in / lottery seed line
- **Setting:** end-of-season standings, multiple years
- **Texas hook:** ★ — Mavs, Spurs, Rockets all relevant
- **Window:** late April (regular season end) or June (lottery)
- **Data path:** Basketball-Reference standings tables
- **Notes:** Does the team that misses the play-in by one game actually do better in the lottery long-run? Clean RDD setup.

### 2. The Wemby effect on the Spurs
- **Method:** synthetic control with multiple donor-pool teams
- **Setting:** Spurs win % pre/post Wembanyama
- **Texas hook:** ★★ — San Antonio anchor
- **Window:** end of season (April–May 2027) when the third Wemby year is in the books
- **Data path:** Basketball-Reference team-game logs
- **Notes:** A textbook synthetic control case. Strong corridor relevance.

### 3. Mid-season coaching change: does it actually matter?
- **Method:** event study around the firing date
- **Setting:** NBA coaching changes, 2010–2026
- **Texas hook:** ☆ — depends on which year
- **Window:** anytime
- **Data path:** Basketball-Reference; news for date stamps
- **Notes:** Well-trodden methodologically but worth a Texas-readable version.

### 4. Trade-deadline effects on team performance
- **Method:** pre-post comparison with team fixed effects
- **Setting:** NBA trade deadline (early February)
- **Texas hook:** ★ — Mavs/Spurs/Rockets often active
- **Window:** late February
- **Data path:** Basketball-Reference; ESPN trade tracker
- **Notes:** Identification is tricky (selection); good post for "here's why this is hard."

### 5. Load management: what does the data actually say?
- **Method:** instrumental variables around star DNPs
- **Setting:** star-player DNP data, 2018–2026
- **Texas hook:** —
- **Window:** mid-season
- **Data path:** Basketball-Reference player game logs
- **Notes:** Charged topic; framing must be careful (the post is about IV, not about whether load management is good).

### 6. The Luka trade anniversary ★
- **Method:** synthetic control of Mavs trajectory
- **Setting:** Mavs game logs pre/post trade
- **Texas hook:** ★★ — Dallas anchor
- **Window:** February 2027 (one-year anniversary)
- **Data path:** Basketball-Reference; trade-date is public
- **Notes:** High-interest topic, clean treatment date, big Texas audience.

**Strongest NBA candidates:** #2 (Wemby effect), #6 (Luka trade anniversary), #1 (tank RDD).

---

## College football (Aug 2026 – Jan 2027)

### 1. 12-team CFP, year two retrospective ★
- **Method:** descriptive + simple counterfactual ("what would the 4-team field have looked like?")
- **Setting:** 2024-25 (first 12-team) + 2025-26 (year two)
- **Texas hook:** ★ — Texas, A&M, TCU, Baylor, Tech all SEC/Big-12 stakes
- **Window:** mid-December 2026 (post-conference championships)
- **Data path:** CFP rankings public; ESPN historical rankings
- **Notes:** Annual evaluation slot. High reader interest.

### 2. Conference realignment as DID: Texas's first SEC year (was 2024-25) ★
- **Method:** difference-in-differences on win %, recruiting, attendance
- **Setting:** Texas + OU joining SEC; treated vs. matched non-treated programs
- **Texas hook:** ★★
- **Window:** end of 2026 season
- **Data path:** Sports-Reference, 247Sports recruiting composite
- **Notes:** Third-year DID estimate possible. Identification is genuinely interesting because both treated programs were elite pre-treatment.

### 3. NIL effects on competitive balance
- **Method:** within-conference dispersion of win % over time
- **Setting:** P5 conferences, 2018–2026
- **Texas hook:** ★ — Texas, A&M among NIL leaders
- **Window:** January 2027 (post-bowl season)
- **Data path:** Sports-Reference; NIL valuation aggregators (with caveats)
- **Notes:** NIL data is messy; honest post would explore measurement.

### 4. Recruiting class quality → conference success
- **Method:** lead-lag regression with team fixed effects
- **Setting:** 247Sports composite rankings, 2010–2026
- **Texas hook:** ★ — Texas/A&M consistently top-10 recruiting
- **Window:** February (after signing day)
- **Data path:** 247Sports composite (public); Sports-Reference team records
- **Notes:** A staple of CFB analytics; do it well.

### 5. Home-field advantage with neutral-site games
- **Method:** RDD-like comparison around neutral-vs-home designations
- **Setting:** AT&T Stadium Arlington games (Cowboys Classic, Big 12 Championship)
- **Texas hook:** ★★ — Arlington venue, Texas teams frequent
- **Window:** September (Cowboys Classic week)
- **Data path:** Sports-Reference; ESPN game logs
- **Notes:** Direct corridor angle (Arlington isn't I-35 corridor but is DFW metroplex).

### 6. Texas State and the FBS pyramid
- **Method:** mobility analysis (G5 → P5 program transitions)
- **Setting:** FBS realignment, 2010–2026
- **Texas hook:** ★★★ — TXST itself, plus the broader Sun Belt → P5 question
- **Window:** anytime
- **Data path:** Sports-Reference; NCAA realignment news
- **Notes:** TXST-specific. Likely high engagement with the home audience.

**Strongest CFB candidates:** #6 (Texas State / G5 → P5), #2 (UT/OU SEC DID), #1 (CFP retrospective annual slot).

---

## College basketball (Nov 2026 – Apr 2027)

### 1. March Madness: how predictable is the bracket? ★
- **Method:** Brier score / log-loss of several prediction models
- **Setting:** NCAA tournament 2014–2026
- **Texas hook:** ☆
- **Window:** week before the tournament (early March)
- **Data path:** kenpom.com (subscription); 538-style brackets archive
- **Notes:** Annual slot; high traffic; pedagogically rich.

### 2. Cinderella runs as outlier events
- **Method:** extreme-value modeling
- **Setting:** historical Cinderella runs (Florida Gulf Coast, Loyola, etc.)
- **Texas hook:** —
- **Window:** mid-tournament (third weekend)
- **Data path:** Sports-Reference tournament logs
- **Notes:** Niche but distinctive method.

### 3. Transfer portal effects on competitive balance
- **Method:** within-team year-over-year retention vs. team-strength delta
- **Setting:** D-I men's basketball, 2018–2026
- **Texas hook:** ★ — UT, A&M, Houston, Texas Tech are transfer-heavy
- **Window:** mid-season; or post-tournament
- **Data path:** kenpom; Verbal Commits / 247Sports transfer logs
- **Notes:** Houston as a case study would be powerful.

### 4. Houston Cougars: a synthetic control of program ascent ★
- **Method:** synthetic control of Houston basketball trajectory
- **Setting:** Houston basketball, 2014–2026
- **Texas hook:** ★★
- **Window:** mid-tournament
- **Data path:** kenpom historical
- **Notes:** Houston went from middling AAC to legitimate national contender. Clean synthetic-control case.

### 5. The Big 12 → SEC migration in basketball (Texas)
- **Method:** DID on schedule strength and NET ranking
- **Setting:** Texas men's basketball, 2022–2026
- **Texas hook:** ★★
- **Window:** post-tournament (April)
- **Data path:** kenpom; NET rankings public
- **Notes:** Companion to the CFB version.

**Strongest CBB candidates:** #4 (Houston ascent), #1 (March Madness bracket), #5 (UT to SEC).

---

## Texas country music

The data here is harder to access cleanly than sports, but the topics are genuinely distinctive — almost no academic blog covers this space.

### 1. The Texas country crossover wave: Cody Johnson, Parker McCollum, Koe Wetzel, Turnpike, Randy Rogers ★
- **Method:** event study of streaming numbers around crossover-event dates (first Billboard chart entry, first major-label deal)
- **Setting:** Spotify monthly listener data, 2018–2026
- **Texas hook:** ★★★ — entire post is Texas country
- **Window:** anytime; spring or early fall for festival adjacency
- **Data path:** Spotify Charts (public weekly); Billboard country charts archive
- **Notes:** Probably the strongest pillar-3 candidate in this whole document. A genuine data analysis question with cultural relevance to the corridor.

### 2. Two Step Inn and the corridor's festival economy ★
- **Method:** descriptive economic-impact analysis using HOT receipts
- **Setting:** Two Step Inn festival, Georgetown TX, 2023–2026
- **Texas hook:** ★★★ — Georgetown is Williamson County, on the corridor
- **Window:** April (festival weekend) or May (post-festival)
- **Data path:** Williamson County HOT receipts (public); city of Georgetown sales tax data
- **Notes:** Bridges pillar 3 and pillar 4 (program-evaluation overlap). Could go in either pillar but the methodological angle is what makes it pillar-3. Strong corridor relevance.

### 3. Geographic concentration of TX country artists
- **Method:** spatial clustering / point-pattern analysis
- **Setting:** birthplaces and current-base of TX country artists, n ≈ 50
- **Texas hook:** ★★★
- **Window:** anytime
- **Data path:** Manual collation from artist Wikipedia pages
- **Notes:** Stephenville (Tarleton), Lubbock (Texas Tech), Austin clearly cluster. A pretty map.

### 4. Streaming-era concentration of Texas country charts
- **Method:** Herfindahl index of TX Country chart over time
- **Setting:** Texas Country Music Chart (or equivalent regional chart), 2010–2026
- **Texas hook:** ★★
- **Window:** anytime
- **Data path:** Texas Regional Radio Report (TRRR) weekly charts
- **Notes:** Is the genre actually getting more or less concentrated? Empirical question with multiple priors.

### 5. Algorithmic gatekeeping: who gets onto Spotify's "Texas Country" playlist?
- **Method:** logistic regression of playlist inclusion on observable artist features
- **Setting:** Spotify "Texas Country" official playlist, 2020–2026
- **Texas hook:** ★★★
- **Window:** anytime; could be quarterly with playlist refreshes
- **Data path:** Spotify API; manual snapshot scraping
- **Notes:** Methodologically modest, but politically interesting. The gatekeeper question for an independent-leaning genre.

### 6. Texas dance hall preservation as an economic-geography puzzle
- **Method:** descriptive + spatial regression of dance-hall survival on county-level covariates
- **Setting:** Gruene Hall, Floore's, Luckenbach, plus the ~80 historic dance halls catalogued by Texas Dance Hall Preservation Inc.
- **Texas hook:** ★★★ — central Texas / corridor-adjacent
- **Window:** anytime
- **Data path:** TDHP catalog (public); county-level demographics
- **Notes:** This one bridges into Pillar 2 economic-development territory. Could be co-billed.

**Strongest TX country candidates:** #2 (Two Step Inn — corridor + festival economy), #1 (crossover wave event study), #6 (dance hall preservation as econ geography).

---

## Top picks across the whole list

If only six topics from this list make it into the calendar over the next three years, the case for these six is the strongest:

1. **Two Step Inn and the corridor's festival economy** — only candidate that lives squarely inside the corridor identity while using music data. Bridges pillar-3 and pillar-4.
2. **Texas country crossover wave (event study)** — distinctive, no other blog does it well, methodologically clean.
3. **Houston Cougars ascent (synthetic control)** — strong Texas relevance, textbook method.
4. **Texas State G5 → P5 (mobility analysis)** — TXST audience hook is unique to this blog.
5. **Strokes-gained explained** — high pedagogical reuse value; sets up future golf posts.
6. **The Wemby effect on the Spurs** — clean treatment, big San Antonio audience.

These six fit naturally into the existing 16-slot pillar-3 backlog in `build_calendar.py`. If you want, I can edit the generator to swap these into specific weeks of the calendar — they would replace some of the more generic methodological slots like "DID with continuous treatment" or "Bayesian small-area estimates."

---

## What I did NOT include

- Posts that are *about* the sport rather than the method (off-scope under the four-pillar rule)
- Posts that require non-public data without a clear path to it (e.g., SportVU NBA tracking data)
- Texas country topics that are pure cultural commentary without an empirical hook
- College football / basketball topics that don't have a Texas angle and a methods angle simultaneously
