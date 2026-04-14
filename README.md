# Southbound 35 — Replication Packages

Replication code and data for [Southbound 35](https://scottlangford2.github.io/scott_langford/year-archive/), a blog on public finance and economic development on the Texas corridor.

Each post with figures or data analysis has its own folder under `posts/`. Every folder is self-contained: install dependencies, run the script, get the figures.

## Posts

| Date | Post | Replication |
|------|------|-------------|
| 2026-04-06 | [The Hays County Growth Story](https://scottlangford2.github.io/scott_langford/posts/2026/04/hays-county-growth/) | [`posts/hays-growth/`](posts/hays-growth/) |
| 2026-04-08 | [How Dangerous Is Spring Break, Really?](https://scottlangford2.github.io/scott_langford/posts/2026/04/spring-break-mortality/) | [`posts/spring-break-mortality/`](posts/spring-break-mortality/) |
| 2026-04-10 | [Hevel on the Back Nine](https://scottlangford2.github.io/scott_langford/posts/2026/04/scheffler-ecclesiastes/) | *(essay — no replication code)* |
| 2026-04-13 | Where Is All of This Going? | [`posts/hays-projections/`](posts/hays-projections/) |

## Quickstart

```bash
git clone https://github.com/scottlangford2/southbound-35.git
cd southbound-35/posts/hays-growth
pip install -r requirements.txt
python build_figures.py
```

Figures are written to `figures/` within each post folder.

## Author

W. Scott Langford, PhD — Assistant Professor, Texas State University
