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

### 7. UNC football: the Belichick era
- **Method:** synthetic control of program trajectory under a
  first-time college coaching hire from the NFL
- **Setting:** UNC football, 2024–2026
- **Texas hook:** — (PhD-alma-mater affiliation)
- **Window:** post-season (January)
- **Data path:** Sports-Reference; recruiting class data from 247
- **Notes:** Personal-affiliation topic. The Belichick hire is a
  legitimately novel natural experiment in college coaching;
  Texas-relevant only by the broader question of NFL coaches in
  college football.

### 8. UNCW football — never had it
- **Method:** N/A (UNCW has no football program)
- **Notes:** Included only to flag the absence; if a football post
  ever references UNCW it would be by negation.

**Strongest CFB candidates:** #6 (Texas State / G5 → P5), #2 (UT/OU SEC DID), #1 (CFP retrospective annual slot). Personal-affiliation candidate #7 (UNC under Belichick) flagged separately — distinctive natural experiment, but outside the corridor identity.

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

### 6. UNC basketball: the post-Roy Williams transition
- **Method:** descriptive trajectory + matched comparison with peer
  blue-blood programs through coaching transitions (Coach K → Scheyer
  at Duke, Boeheim → Autry at Syracuse, Roy → Hubert at UNC)
- **Setting:** UNC men's basketball 2018–2026
- **Texas hook:** — (PhD-alma-mater affiliation note in the byline)
- **Window:** mid-tournament (March) or post-tournament (April)
- **Data path:** kenpom historical; Sports-Reference
- **Notes:** Personal-affiliation topic. The Hubert Davis era is
  legitimately interesting empirically — a national title game
  appearance, a missed tournament, and inconsistency thereafter.

### 7. UNCW Seahawks and the CAA bid path
- **Method:** survival analysis of mid-major NCAA tournament
  appearances; or descriptive of how the CAA's bid pattern
  shapes mid-major program trajectories
- **Setting:** UNCW basketball + CAA, 2000–2026
- **Texas hook:** — (personal affiliation)
- **Window:** mid-tournament if UNCW is in the bracket; otherwise
  anytime
- **Data path:** kenpom; Sports-Reference; NCAA tournament archive
- **Notes:** Personal-affiliation topic. UNCW has 4-5 tournament
  appearances since 2000 — enough sample for a small-N case study
  of a mid-major program riding the CAA's autobid.

### 8. Texas State basketball: a mid-major in the Sun Belt
- **Method:** comparative analysis of Sun Belt program trajectories,
  with TXST as the case
- **Setting:** TXST men's basketball + Sun Belt, 2015–2026
- **Texas hook:** ★★ — TXST itself, plus the broader Sun Belt
  question
- **Window:** mid-season or post-tournament
- **Data path:** kenpom; Sun Belt records
- **Notes:** TXST-specific. Companion to the CFB G5→P5 piece.
  Likely high engagement with the home audience.

**Strongest CBB candidates:** #4 (Houston ascent), #1 (March Madness
bracket), #5 (UT to SEC), #8 (TXST mid-major analysis). Personal-
affiliation candidates (#6 UNC, #7 UNCW) flagged separately —
out-of-scope for the Texas corridor identity, but available when a
specific question or moment makes them relevant.

---

## Women's sports

Women's sports get covered the same way men's sports do — when the
data supports a clean empirical question. Coverage is not
afterthought-style or "and also for women" tacked-on; it's parallel
treatment with its own candidate topics. The blog should not look
like it covers men's sports six times and women's sports once.

### Women's college basketball

#### 1. The South Carolina dynasty as synthetic control ★
- **Method:** synthetic control of SC women's basketball under
  Dawn Staley vs. matched donor pool of peer programs
- **Setting:** SC WBB 2008–2026 (Staley arrival → present)
- **Texas hook:** —
- **Window:** post-tournament (April)
- **Data path:** Her Hoop Stats; Sports-Reference; kenpom WBB
- **Notes:** Textbook synthetic-control case. Multiple national
  titles, sustained #1 KenPom-equivalent ranking, clear coaching
  treatment date.

#### 2. The Caitlin Clark viewership shock
- **Method:** event study of WBB regular-season and tournament
  viewership around Clark's arrival, career, and post-Iowa
  professional move
- **Setting:** WBB viewership data, 2021–2026
- **Texas hook:** —
- **Window:** anytime
- **Data path:** Nielsen WBB ratings (where publicly summarized);
  ESPN public-facing viewership reports
- **Notes:** A genuine viewership inflection point. Methodologically
  clean treatment date; data availability is the constraint.

#### 3. UNC women's basketball under Banghart
- **Method:** descriptive trajectory + matched-program comparison
  through coaching transitions in the ACC women's basketball era
- **Setting:** UNC WBB 2019–2026 (Banghart arrival → present)
- **Texas hook:** — (personal affiliation)
- **Window:** mid- or post-tournament
- **Data path:** Her Hoop Stats; Sports-Reference
- **Notes:** Personal-affiliation topic. Banghart inherited a
  program with a recent rough stretch; the rebuild is a credible
  analytical case.

#### 4. UNCW women's basketball and the CAA
- **Method:** mid-major program analysis; CAA bid economics for
  women's tournament
- **Setting:** UNCW WBB + CAA, 2010–2026
- **Texas hook:** — (personal affiliation)
- **Window:** mid-tournament or off-season
- **Data path:** Her Hoop Stats; CAA records
- **Notes:** Personal-affiliation topic. Mid-major WBB programs
  are a thin slice of analytical coverage; this is a place where
  Southbound 35 could be one of very few outlets doing the work.

#### 5. Texas State women's basketball in the Sun Belt
- **Method:** comparative analysis of Sun Belt women's programs,
  with TXST as the case
- **Setting:** TXST WBB + Sun Belt, 2015–2026
- **Texas hook:** ★★
- **Window:** mid-season or post-tournament
- **Data path:** Her Hoop Stats; Sun Belt records
- **Notes:** Companion to the men's TXST CBB analysis.

#### 6. Transfer portal effects in women's basketball
- **Method:** within-team year-over-year retention vs. team-strength
  delta, women's edition
- **Setting:** D-I women's basketball, 2018–2026
- **Texas hook:** ★ — Baylor, UT, A&M, TCU all active in the WBB
  transfer portal
- **Window:** mid-season or post-tournament
- **Data path:** Verbal Commits WBB / Her Hoop Stats
- **Notes:** WBB portal dynamics differ meaningfully from men's;
  the post can illustrate the gendered patterns directly.

### LPGA

#### 1. Strokes-gained for the LPGA: a partial reconstruction
- **Method:** strokes-gained decomposition using publicly available
  LPGA stats (less granular than PGA ShotLink, but workable)
- **Setting:** LPGA Tour 2019–2026
- **Texas hook:** ★ — events at Pelican (FL), but check current
  TX-area events on the LPGA schedule
- **Window:** mid-season
- **Data path:** LPGA stats pages; Data Golf LPGA where available
- **Notes:** Less data than PGA, but the gap is itself interesting.
  Companion to the PGA strokes-gained explainer.

#### 2. LPGA Hall of Fame points: a unique formula
- **Method:** descriptive + counterfactual analysis of the points-
  based HOF formula
- **Setting:** LPGA HOF data, full archive
- **Texas hook:** —
- **Window:** anytime
- **Data path:** LPGA HOF criteria; player career histories
- **Notes:** The LPGA HOF formula is genuinely unusual (formal
  points-based admission, not voted). Pedagogically rich; clean
  data; distinctive subject.

#### 3. Solheim Cup performance vs individual tournament
- **Method:** within-player comparison of stroke-play averages vs.
  match-play performance
- **Setting:** Solheim Cup history + individual LPGA tournament data
- **Texas hook:** —
- **Window:** Solheim Cup year (every 2 years)
- **Data path:** LPGA stats; Solheim Cup historical
- **Notes:** Format-effect question that the LPGA setting answers
  more cleanly than the PGA Ryder Cup analog (smaller fields,
  more crossover).

### WNBA

#### 1. The Caitlin Clark / Paige Bueckers viewership economics ★
- **Method:** event study of WNBA viewership around college-to-pro
  transitions of marquee players
- **Setting:** WNBA viewership data 2022–2026
- **Texas hook:** ★ — Dallas Wings are the corridor's WNBA
  representative
- **Window:** mid-season or post-Finals
- **Data path:** Nielsen WNBA ratings; ESPN viewership summaries
- **Notes:** Sustained, real viewership inflection. Clean treatment
  dates. High reader interest.

#### 2. WNBA expansion economics
- **Method:** descriptive + counterfactual analysis of expansion-
  team viability using past expansion data (Atlanta, Las Vegas)
- **Setting:** WNBA, 2008–2026
- **Texas hook:** —
- **Window:** anytime
- **Data path:** WNBA financials (where public); attendance and
  ratings data
- **Notes:** With multiple expansion teams announced (Golden State
  Valkyries, Toronto, Portland), the historical record is
  instructive. Public-finance-adjacent: many WNBA arenas involve
  public subsidies.

#### 3. WNBA salary cap and labor economics
- **Method:** comparative analysis of WNBA vs. NBA salary structures
  and the resulting offshore-playing dynamics
- **Setting:** WNBA + international leagues, 2010–2026
- **Texas hook:** —
- **Window:** off-season (winter)
- **Data path:** WNBA CBA documents; international league salary
  reports (less reliable)
- **Notes:** Labor-economics topic with a sports setting.
  Methodologically more like a public-finance piece than a sports-
  analytics piece — fits pillar-3 well.

#### 4. Dallas Wings and the corridor's WNBA team ★
- **Method:** descriptive economic-impact analysis; attendance vs.
  team performance; venue economics
- **Setting:** Dallas Wings (Arlington), 2016–2026
- **Texas hook:** ★★ — DFW corridor team
- **Window:** mid-season or off-season
- **Data path:** Wings public financials; Arlington venue records
- **Notes:** The corridor angle. Wings have moved arenas; the
  economics of that decision are publicly accessible.

**Strongest women's-sports candidates:** #1 South Carolina dynasty,
#2 Caitlin Clark WBB viewership shock, WNBA #1 Clark/Bueckers
viewership, WNBA #4 Dallas Wings, LPGA #1 strokes-gained partial
reconstruction.

---

## Olympic sports

Quadrennial events with their own distinctive statistical questions.
Coverage is event-cycle: most posts cluster in the year before and
the year after each Summer/Winter Games.

#### 1. Olympic medal-table prediction models
- **Method:** comparative evaluation of GDP/population/host-status
  models vs. naive prior cycles; Brier scores on multiple models
- **Setting:** Olympic medal tables, 1996–2026 (or longer)
- **Texas hook:** —
- **Window:** week before opening ceremonies
- **Data path:** Olympedia medal table archive
- **Notes:** Annual-cycle slot (or rather, quadrennial). High
  traffic during the Games. Pedagogically rich.

#### 2. The host-nation medal bump
- **Method:** event study of medal counts around host-status
- **Setting:** Olympic medal tables, all hosts 1980–2024
- **Texas hook:** ★ — LA 2028 is the relevant near-term anchor
- **Window:** any Games year; especially relevant for LA 2028
- **Data path:** Olympedia archive
- **Notes:** Cleanest natural experiment in sports. The host bump
  is well-documented; the question is whether 2028 LA shows it.

#### 3. Sport additions and removals: viewership and participation
- **Method:** event-study analysis of sports added (sport climbing,
  surfing, breakdancing) and the effects on national-level participation
- **Setting:** Olympic sport program 2020–2028
- **Texas hook:** —
- **Window:** post-Games (fall after Olympics)
- **Data path:** IOC sport program; participation registries
- **Notes:** Quadrennial slot. Genuinely interesting policy
  question — does Olympic status drive grassroots adoption?

#### 4. Texas Olympic athletes: the corridor's contribution ★
- **Method:** descriptive analysis of Texas-trained Olympic athletes
  by sport and county
- **Setting:** US Olympic team rosters with training-location data
- **Texas hook:** ★★★ — corridor athletes specifically
- **Window:** during Games
- **Data path:** USOC roster data; training-center locations
- **Notes:** Direct corridor angle. Texas State, UT, A&M, Rice all
  produce Olympians; the per-county distribution is empirically
  interesting and locally relevant.

#### 5. NCAA-Olympic pipeline economics
- **Method:** comparative analysis of NCAA sports that are major
  Olympic feeders (swimming, track, gymnastics) vs. those that are
  not, in terms of program funding and Title IX compliance
- **Setting:** NCAA D-I sports + Olympic team composition
- **Texas hook:** ★ — UT swimming, A&M track
- **Window:** anytime
- **Data path:** NCAA financial reports; USOC roster history
- **Notes:** Bridges pillar-3 (statistical analysis) and pillar-4
  (program evaluation — Title IX as the program). Substantive
  policy question with a sports empirical setting.

**Strongest Olympic candidates:** #4 (Texas Olympic athletes
corridor analysis), #1 (medal-table prediction models), #5
(NCAA-Olympic pipeline) — all credible with currently-public data.

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
