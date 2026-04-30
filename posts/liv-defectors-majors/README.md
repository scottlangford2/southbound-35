# LIV Defectors at the Majors — Replication

Companion code and data for [Did LIV Golfers Get Worse After They
Defected?](https://scottlangford2.github.io/scott_langford/posts/2026/04/liv-defectors-majors/).

## What it does

`liv_did.py` is a single end-to-end script that:

1. Scrapes every round of every men's major from 2018 through the 2026
   Masters from Wikipedia (31 tournaments, ~17,500 player-rounds).
2. Scrapes Wikipedia infobox birthdates for ~500 players (cached locally).
3. Builds a player × major × round panel.
4. Runs the difference-in-differences regressions reported in the post:
   strokes-vs-field with player FE + (major×round) FE, age control,
   matched controls, heterogeneity by player type, formal event study,
   round-specific effects, made-cut probability, and Lee-style bounds.
5. Generates the seven figures used in the post.

## Run it

```bash
pip install -r requirements.txt
python liv_did.py
```

First run takes ~10 minutes (Wikipedia scraping). Subsequent runs are fast
because results are cached to:

- `liv_majors_rounds_raw.csv` — raw scraped leaderboards
- `liv_majors_rounds_panel.csv` — analysis panel with treatment, age, event-time
- `player_birthdates.csv` — Wikipedia birthdate cache
- `figures/` — the 7 PNG charts

Cached files are checked into this folder so you can re-run the analysis
without scraping. Delete them to force a fresh scrape.

## Files

| File | Purpose |
|---|---|
| `liv_did.py` | All scraping, regressions, and plotting |
| `requirements.txt` | Python dependencies |
| `liv_majors_rounds_panel.csv` | Cached analysis panel |
| `player_birthdates.csv` | Cached Wikipedia birthdates |
| `figures/` | The 7 charts in the post |
