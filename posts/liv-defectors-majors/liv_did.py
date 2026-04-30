"""
Did LIV golfers improve or worsen after defecting?

Design: difference-in-differences on major-championship performance.
- Unit of observation: player x major x round  (up to 4 rows per player-major)
- Treated: golfers who defected to LIV; Control: golfers who stayed on PGA Tour
- Pre/Post: relative to the player's individual defection date
- Outcomes: strokes-vs-round-field-average; made-cut indicator (player x major)
- Identification: player FE + (major x round) FE. Within a single round of
  a single major, every golfer faced the same course/wind/pins, so the
  estimate is a defector's within-round shift relative to stayers' shift
  in the same rounds.

Cut selection: rounds 3-4 are only observed for cut-makers. Main spec uses
R1+R2 only (everyone plays both); R3+R4 reported separately as a check.

Why majors: defectors and stayers play the SAME course in the SAME field,
which removes the field-strength confound that kills cross-tour comparisons.

Data: scraped from Wikipedia leaderboards (free, public). Wikipedia tables
are imperfect — name variants and DQ/WD/CUT rows need cleaning.

Run:
    pip install pandas numpy lxml html5lib requests statsmodels linearmodels
    python liv_did.py
"""

from __future__ import annotations

import io
import re
import sys
import time
from dataclasses import dataclass

import os
import numpy as np
import pandas as pd
import requests
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Defectors and their (approximate) first LIV event dates.
# Sources: public reporting at the time of each move.
# Dates are the player's debut LIV event; we treat any major on/after this
# date as "post" for that player.
# ---------------------------------------------------------------------------
LIV_DEFECTORS: dict[str, str] = {
    "Phil Mickelson": "2022-06-09",
    "Dustin Johnson": "2022-06-09",
    "Sergio Garcia": "2022-06-09",
    "Louis Oosthuizen": "2022-06-09",
    "Charl Schwartzel": "2022-06-09",
    "Kevin Na": "2022-06-09",
    "Talor Gooch": "2022-06-09",
    "Branden Grace": "2022-06-09",
    "Ian Poulter": "2022-06-09",
    "Lee Westwood": "2022-06-09",
    "Graeme McDowell": "2022-06-09",
    "Martin Kaymer": "2022-06-09",
    "Patrick Reed": "2022-06-30",
    "Bryson DeChambeau": "2022-06-30",
    "Brooks Koepka": "2022-06-30",
    "Pat Perez": "2022-06-30",
    "Matthew Wolff": "2022-06-30",
    "Bubba Watson": "2022-07-29",
    "Cameron Smith": "2022-09-02",
    "Joaquin Niemann": "2022-09-02",
    "Marc Leishman": "2022-09-02",
    "Harold Varner III": "2022-12-01",
    "Thomas Pieters": "2022-12-01",
    "Mito Pereira": "2023-02-01",
    "Sebastian Munoz": "2023-02-01",
    "Brendan Steele": "2023-02-01",
    "Dean Burmester": "2023-04-01",
    "Jon Rahm": "2023-12-07",
    "Tyrrell Hatton": "2024-02-01",
    "Adrian Meronk": "2024-02-01",
}

# Name aliases that appear on Wikipedia leaderboards
NAME_ALIASES: dict[str, str] = {
    "Cam Smith": "Cameron Smith",
    "Joaquín Niemann": "Joaquin Niemann",
    "Sebastián Muñoz": "Sebastian Munoz",
    "Sergio García": "Sergio Garcia",
    "Joaquin Niemann*": "Joaquin Niemann",
}


# Hardcoded birthdates for LIV defectors (so we always have age data on them).
# Format: ISO date string. Sources: Wikipedia / public records.
DEFECTOR_BIRTHDATES: dict[str, str] = {
    "Phil Mickelson":     "1970-06-16",
    "Dustin Johnson":     "1984-06-22",
    "Sergio Garcia":      "1980-01-09",
    "Louis Oosthuizen":   "1982-10-19",
    "Charl Schwartzel":   "1984-08-31",
    "Kevin Na":           "1983-09-15",
    "Talor Gooch":        "1991-11-08",
    "Branden Grace":      "1988-05-20",
    "Ian Poulter":        "1976-01-10",
    "Lee Westwood":       "1973-04-24",
    "Graeme McDowell":    "1979-07-30",
    "Martin Kaymer":      "1984-12-28",
    "Patrick Reed":       "1990-08-05",
    "Bryson DeChambeau":  "1993-09-16",
    "Brooks Koepka":      "1990-05-03",
    "Pat Perez":          "1976-03-01",
    "Matthew Wolff":      "1999-04-14",
    "Bubba Watson":       "1978-11-05",
    "Cameron Smith":      "1993-08-18",
    "Joaquin Niemann":    "1998-11-07",
    "Marc Leishman":      "1983-10-24",
    "Harold Varner III":  "1990-08-15",
    "Thomas Pieters":     "1992-01-22",
    "Mito Pereira":       "1995-03-31",
    "Sebastian Munoz":    "1992-12-29",
    "Brendan Steele":     "1983-02-04",
    "Dean Burmester":     "1989-06-30",
    "Jon Rahm":           "1994-11-10",
    "Tyrrell Hatton":     "1991-10-14",
    "Adrian Meronk":      "1993-05-18",
}


# ---------------------------------------------------------------------------
# Wikipedia URLs for each major, 2018-2024 (skipping 2020 Open, cancelled).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Major:
    year: int
    name: str            # short name: Masters / PGA / USOpen / Open
    date: str            # final-round date, ISO
    url: str             # Wikipedia leaderboard page

MAJORS: list[Major] = [
    Major(2018, "Masters", "2018-04-08", "https://en.wikipedia.org/wiki/2018_Masters_Tournament"),
    Major(2018, "PGA",     "2018-08-12", "https://en.wikipedia.org/wiki/2018_PGA_Championship"),
    Major(2018, "USOpen",  "2018-06-17", "https://en.wikipedia.org/wiki/2018_U.S._Open_(golf)"),
    Major(2018, "Open",    "2018-07-22", "https://en.wikipedia.org/wiki/2018_Open_Championship"),
    Major(2019, "Masters", "2019-04-14", "https://en.wikipedia.org/wiki/2019_Masters_Tournament"),
    Major(2019, "PGA",     "2019-05-19", "https://en.wikipedia.org/wiki/2019_PGA_Championship"),
    Major(2019, "USOpen",  "2019-06-16", "https://en.wikipedia.org/wiki/2019_U.S._Open_(golf)"),
    Major(2019, "Open",    "2019-07-21", "https://en.wikipedia.org/wiki/2019_Open_Championship"),
    Major(2020, "Masters", "2020-11-15", "https://en.wikipedia.org/wiki/2020_Masters_Tournament"),
    Major(2020, "PGA",     "2020-08-09", "https://en.wikipedia.org/wiki/2020_PGA_Championship"),
    Major(2020, "USOpen",  "2020-09-20", "https://en.wikipedia.org/wiki/2020_U.S._Open_(golf)"),
    Major(2021, "Masters", "2021-04-11", "https://en.wikipedia.org/wiki/2021_Masters_Tournament"),
    Major(2021, "PGA",     "2021-05-23", "https://en.wikipedia.org/wiki/2021_PGA_Championship"),
    Major(2021, "USOpen",  "2021-06-20", "https://en.wikipedia.org/wiki/2021_U.S._Open_(golf)"),
    Major(2021, "Open",    "2021-07-18", "https://en.wikipedia.org/wiki/2021_Open_Championship"),
    Major(2022, "Masters", "2022-04-10", "https://en.wikipedia.org/wiki/2022_Masters_Tournament"),
    Major(2022, "PGA",     "2022-05-22", "https://en.wikipedia.org/wiki/2022_PGA_Championship"),
    Major(2022, "USOpen",  "2022-06-19", "https://en.wikipedia.org/wiki/2022_U.S._Open_(golf)"),
    Major(2022, "Open",    "2022-07-17", "https://en.wikipedia.org/wiki/2022_Open_Championship"),
    Major(2023, "Masters", "2023-04-09", "https://en.wikipedia.org/wiki/2023_Masters_Tournament"),
    Major(2023, "PGA",     "2023-05-21", "https://en.wikipedia.org/wiki/2023_PGA_Championship"),
    Major(2023, "USOpen",  "2023-06-18", "https://en.wikipedia.org/wiki/2023_U.S._Open_(golf)"),
    Major(2023, "Open",    "2023-07-23", "https://en.wikipedia.org/wiki/2023_Open_Championship"),
    Major(2024, "Masters", "2024-04-14", "https://en.wikipedia.org/wiki/2024_Masters_Tournament"),
    Major(2024, "PGA",     "2024-05-19", "https://en.wikipedia.org/wiki/2024_PGA_Championship"),
    Major(2024, "USOpen",  "2024-06-16", "https://en.wikipedia.org/wiki/2024_U.S._Open_(golf)"),
    Major(2024, "Open",    "2024-07-21", "https://en.wikipedia.org/wiki/2024_Open_Championship"),
    Major(2025, "Masters", "2025-04-13", "https://en.wikipedia.org/wiki/2025_Masters_Tournament"),
    Major(2025, "PGA",     "2025-05-18", "https://en.wikipedia.org/wiki/2025_PGA_Championship"),
    Major(2025, "USOpen",  "2025-06-15", "https://en.wikipedia.org/wiki/2025_U.S._Open_(golf)"),
    Major(2025, "Open",    "2025-07-20", "https://en.wikipedia.org/wiki/2025_Open_Championship"),
    Major(2026, "Masters", "2026-04-12", "https://en.wikipedia.org/wiki/2026_Masters_Tournament"),
]


# ---------------------------------------------------------------------------
# Scraping helpers
# ---------------------------------------------------------------------------
HEADERS = {"User-Agent": "Mozilla/5.0 (research; contact: scottlangford2@gmail.com)"}

def fetch_page(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def _flatten_cols(t: pd.DataFrame) -> pd.DataFrame:
    t = t.copy()
    t.columns = [c[-1] if isinstance(c, tuple) else c for c in t.columns]
    return t


def find_leaderboard(html: str) -> pd.DataFrame | None:
    """Find Wikipedia leaderboard tables (top 10 + below) and concat.

    A leaderboard table has Player + Score columns AND a Score column
    where most entries contain '=' (round-by-round breakdown like
    '70-72-71-69=282' or '76-70=146' for missed-cut). That filter rules
    out the round-leader sub-tables, which only show single-round scores.
    """
    tables = pd.read_html(io.StringIO(html))
    keep = []
    for t in tables:
        t = _flatten_cols(t)
        cols_lower = [str(c).lower() for c in t.columns]
        has_player = any("player" in c for c in cols_lower)
        score_col = next((c for c in t.columns if str(c).lower() in ("score", "scores")), None)
        if not (has_player and score_col is not None):
            continue
        # require that >= 50% of non-null score entries contain "=" (breakdown)
        s = t[score_col].dropna().astype(str)
        if len(s) == 0:
            continue
        if (s.str.contains("=").mean() < 0.5):
            continue
        keep.append(t)
    if not keep:
        return None
    return pd.concat(keep, ignore_index=True)


SCORE_RE = re.compile(r"^\s*(\d{3,4})\s*$")
def parse_score(x) -> float | None:
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s.upper() in ("CUT", "MC", "WD", "DQ", "DNS", "—", "-"):
        return None
    m = SCORE_RE.match(s)
    if m:
        return float(m.group(1))
    # sometimes the score column contains "70-72-71-69=282"
    m2 = re.search(r"=\s*(\d{3,4})", s)
    if m2:
        return float(m2.group(1))
    try:
        return float(s)
    except ValueError:
        return None


ROUND_RE = re.compile(r"(\d{2,3})")
def parse_rounds(x) -> list[float]:
    """Extract individual round scores from a 'Score' cell.

    Wikipedia formats: '70-72-71-69=282', '70–72–71–69=282', '70, 72, 71, 69',
    or sometimes just a total. Returns a list of up to 4 round scores;
    missing rounds (cut, WD) become NaN.
    """
    if pd.isna(x):
        return [np.nan] * 4
    s = str(x).strip()
    if s.upper() in ("CUT", "MC", "WD", "DQ", "DNS", "—", "-", ""):
        return [np.nan] * 4
    # strip the '=total' tail if present
    s = re.split(r"=", s)[0]
    nums = [int(n) for n in ROUND_RE.findall(s) if 55 <= int(n) <= 99]
    nums = (nums + [np.nan] * 4)[:4]
    return [float(n) if not (isinstance(n, float) and np.isnan(n)) else np.nan
            for n in nums]


def parse_position(x) -> int | None:
    if pd.isna(x):
        return None
    s = str(x).strip().upper().replace("T", "")
    if s in ("CUT", "MC", "WD", "DQ", "DNS"):
        return None
    try:
        return int(s)
    except ValueError:
        return None


def clean_name(x: str) -> str:
    s = re.sub(r"\(.*?\)", "", str(x)).strip()         # drop (a) for amateurs
    s = re.sub(r"\s+", " ", s)
    s = s.replace("*", "").strip()
    return NAME_ALIASES.get(s, s)


def normalize_leaderboard(df: pd.DataFrame, m: Major) -> pd.DataFrame:
    """Return a long-format frame: one row per player x round (R1..R4)."""
    df = df.copy()
    df.columns = [str(c) for c in df.columns]
    col_player = next((c for c in df.columns if "player" in c.lower()), None)
    col_score  = next((c for c in df.columns if c.lower() in ("score", "scores")), None)
    col_total  = next((c for c in df.columns if c.lower() in ("total",)), None) or col_score
    col_place  = next((c for c in df.columns if c.lower() in ("place", "pos", "position", "finish")), None)
    # explicit per-round columns when Wikipedia provides them
    round_cols = [next((c for c in df.columns if c.strip().upper() in (f"R{i}", f"ROUND {i}")), None)
                  for i in (1, 2, 3, 4)]

    if col_player is None or (col_score is None and not any(round_cols)):
        return pd.DataFrame()

    rows = []
    for _, row in df.iterrows():
        name = clean_name(row[col_player])
        if len(name) <= 1:
            continue
        if all(round_cols):
            rounds = [parse_score(row[c]) for c in round_cols]
        else:
            rounds = parse_rounds(row[col_score])
        total = parse_score(row[col_total]) if col_total else None
        if total is None:
            valid = [r for r in rounds if r is not None and not np.isnan(r)]
            total = sum(valid) if len(valid) == 4 else np.nan
        place = parse_position(row[col_place]) if col_place else np.nan
        for i, sc in enumerate(rounds, start=1):
            rows.append({
                "player": name,
                "round":  i,
                "score":  sc,
                "total":  total,
                "place":  place,
                "year":   m.year,
                "major":  m.name,
                "date":   pd.Timestamp(m.date),
                "major_id": f"{m.year}-{m.name}",
                "major_round": f"{m.year}-{m.name}-R{i}",
            })
    out = pd.DataFrame(rows)
    # Made cut = had a non-null R3 (cut comes after R2)
    cut_made = (out[out["round"] == 3]
                .groupby("player")["score"].apply(lambda s: s.notna().any()))
    out["made_cut"] = out["player"].map(cut_made).fillna(False).astype(int)
    return out


def build_dataset() -> pd.DataFrame:
    frames = []
    for m in MAJORS:
        try:
            html = fetch_page(m.url)
        except Exception as e:
            print(f"  ! fetch failed {m.url}: {e}", file=sys.stderr)
            continue
        lb = find_leaderboard(html)
        if lb is None:
            print(f"  ! no leaderboard table found for {m.year} {m.name}", file=sys.stderr)
            continue
        rows = normalize_leaderboard(lb, m)
        # Wikipedia includes round-2 and round-3 leader tables that also have
        # breakdowns ("68-65=133"); the same player's R1/R2 scores end up in
        # multiple tables. Dedupe (player, major, round) keeping the row with
        # the most info (non-null score wins; ties broken by completing total).
        rows = (rows
                .sort_values(["player", "round", "score", "total"],
                             na_position="last")
                .drop_duplicates(["player", "major_id", "round"], keep="first"))
        print(f"  {m.year} {m.name}: {len(rows)} rows")
        frames.append(rows)
        time.sleep(0.5)
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Birthdates (hardcoded for defectors, scraped + cached for everyone else)
# ---------------------------------------------------------------------------
BDAY_CACHE = "player_birthdates.csv"

WIKI_BDAY_RE = re.compile(
    r'class="bday"[^>]*>(\d{4}-\d{2}-\d{2})<', re.IGNORECASE)


def _wiki_url_for(name: str) -> str:
    base = name.replace(" ", "_")
    return f"https://en.wikipedia.org/wiki/{base}"


def _scrape_birthdate(name: str) -> str | None:
    """Try a couple of URL variants for the player; pull bday from infobox."""
    candidates = [
        _wiki_url_for(name),
        _wiki_url_for(name) + "_(golfer)",
    ]
    for url in candidates:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                continue
            m = WIKI_BDAY_RE.search(r.text)
            if m:
                return m.group(1)
        except Exception:
            continue
    return None


def get_birthdates(players: list[str]) -> dict[str, str]:
    """Return {player: ISO birthdate}. Uses on-disk cache."""
    cache: dict[str, str] = {}
    if os.path.exists(BDAY_CACHE):
        c = pd.read_csv(BDAY_CACHE)
        cache = dict(zip(c["player"], c["birthdate"]))
    # seed with hardcoded defectors
    for p, d in DEFECTOR_BIRTHDATES.items():
        cache.setdefault(p, d)
    missing = [p for p in players if p not in cache]
    if missing:
        print(f"  scraping birthdates for {len(missing)} players ...")
        for i, p in enumerate(missing):
            bd = _scrape_birthdate(p)
            cache[p] = bd if bd else ""
            if (i + 1) % 25 == 0:
                print(f"    {i+1}/{len(missing)} ({p}: {bd})")
            time.sleep(0.3)
        # persist
        pd.DataFrame([{"player": k, "birthdate": v} for k, v in cache.items()]) \
          .to_csv(BDAY_CACHE, index=False)
    return cache


def add_age(df: pd.DataFrame) -> pd.DataFrame:
    """Add age (in years) at time of each major. Players with no birthdate
    or implausible birthdate (born before 1940 or after 2010) get NaN."""
    players = sorted(df["player"].unique())
    bdays = get_birthdates(players)
    def _coerce(s):
        try:
            t = pd.to_datetime(s, errors="coerce")
            if pd.isna(t) or t.year < 1940 or t.year > 2010:
                return pd.NaT
            return t
        except Exception:
            return pd.NaT
    bd_series = pd.Series({k: _coerce(v) for k, v in bdays.items()})
    df = df.copy()
    df["birthdate"] = pd.to_datetime(df["player"].map(bd_series), errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["age"] = (df["date"] - df["birthdate"]).dt.days / 365.25
    return df


# ---------------------------------------------------------------------------
# Outcomes and treatment indicators
# ---------------------------------------------------------------------------
def add_treatment(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["liv"] = df["player"].isin(LIV_DEFECTORS).astype(int)
    defect_dates = pd.Series(LIV_DEFECTORS).map(pd.Timestamp)
    df["defect_date"] = df["player"].map(defect_dates)
    df["post"] = ((df["liv"] == 1) & (df["date"] >= df["defect_date"])).astype(int)
    return df


def add_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """Round-level strokes vs the round's field average.

    Field = every player who posted a score for that round. R1 and R2 fields
    are full; R3 and R4 fields are restricted to cut-makers.
    """
    df = df.copy()
    df["sv_field"] = df["score"] - df.groupby("major_round")["score"].transform("mean")
    return df


# ---------------------------------------------------------------------------
# DiD estimation
# ---------------------------------------------------------------------------
def _restrict_sample(df: pd.DataFrame, min_obs: int) -> pd.DataFrame:
    counts = df.groupby("player").size()
    keep_controls = counts[counts >= min_obs].index
    return df[df["liv"].eq(1) | df["player"].isin(keep_controls)].copy()


def did_strokes_vs_field(df: pd.DataFrame,
                         rounds: tuple[int, ...] = (1, 2),
                         control_age: bool = False,
                         restrict_to: pd.Index | None = None,
                         extra_terms: str = ""):
    """outcome ~ post + (age + age^2 if control_age) + player FE + (major x round) FE.
    Default sample: R1+R2 only (full field, no cut selection).
    SE clustered at the player level.
    """
    sample = df[(df["sv_field"].notna()) & (df["round"].isin(rounds))].copy()
    if restrict_to is not None:
        sample = sample[sample["player"].isin(restrict_to) | sample["liv"].eq(1)]
    sample = _restrict_sample(sample, min_obs=8)
    if control_age:
        sample = sample[sample["age"].notna()].copy()
    rhs = "post"
    if control_age:
        rhs += " + age + I(age**2)"
    if extra_terms:
        rhs += " + " + extra_terms
    rhs += " + C(player) + C(major_round)"
    model = smf.ols(f"sv_field ~ {rhs}", data=sample).fit(
        cov_type="cluster", cov_kwds={"groups": sample["player"]})
    return model, sample


def did_made_cut(df: pd.DataFrame, control_age: bool = False,
                 restrict_to: pd.Index | None = None):
    """Cut is per-major, so collapse rounds first."""
    by_major = (df.groupby(["player", "major_id", "date", "liv", "post"],
                           as_index=False)["made_cut"].max())
    if control_age:
        # bring age in (use age at the major's date)
        ages = df.groupby(["player", "major_id"])["age"].first().reset_index()
        by_major = by_major.merge(ages, on=["player", "major_id"], how="left")
        by_major = by_major[by_major["age"].notna()].copy()
    if restrict_to is not None:
        by_major = by_major[by_major["player"].isin(restrict_to) | by_major["liv"].eq(1)]
    sample = _restrict_sample(by_major, min_obs=4)
    rhs = "post" + (" + age + I(age**2)" if control_age else "")
    rhs += " + C(player) + C(major_id)"
    model = smf.ols(f"made_cut ~ {rhs}", data=sample).fit(
        cov_type="cluster", cov_kwds={"groups": sample["player"]})
    return model, sample


# ---------------------------------------------------------------------------
# Event time and event-study (formal: separate coefficient at each lead/lag)
# ---------------------------------------------------------------------------
def assign_event_time(df: pd.DataFrame) -> pd.DataFrame:
    """For each defector, number their majors as ..., -2, -1, 0, +1, +2, ...
    where 0 is their first major as a LIV member. Non-defectors get NaN.
    """
    df = df.copy()
    df["event_time"] = np.nan
    for player, sub in df[df["liv"] == 1].groupby("player"):
        majors = sub.drop_duplicates("major_id").sort_values("date")
        pre  = majors[majors["post"] == 0]
        post = majors[majors["post"] == 1]
        # most-recent pre = -1, going back: -2, -3, ...
        pre_et  = pd.Series(-np.arange(len(pre), 0, -1), index=pre["major_id"].values)
        post_et = pd.Series( np.arange(len(post)),       index=post["major_id"].values)
        et_map = pd.concat([pre_et, post_et])
        mask = (df["player"] == player)
        df.loc[mask, "event_time"] = df.loc[mask, "major_id"].map(et_map)
    return df


def event_study_strokes(df: pd.DataFrame, rounds=(1, 2),
                        leads: tuple[int, int] = (-8, 8),
                        omit: int = -1, control_age: bool = True):
    """outcome ~ sum_k 1{event_time=k} + age + player FE + major_round FE.
    Omit one period (default -1) as the reference. Returns model + sample
    + the table of {k, beta, se}.
    """
    d = df[(df["sv_field"].notna()) & (df["round"].isin(rounds))].copy()
    d = d[d["age"].notna()] if control_age else d
    # build dummies on the defector subsample only; non-defectors are control
    d["et"] = d["event_time"]
    lo, hi = leads
    d["et"] = d["et"].clip(lower=lo, upper=hi)  # bin endpoints
    # build dummy columns
    et_vals = sorted(d["et"].dropna().unique())
    et_vals = [int(k) for k in et_vals if int(k) != omit]
    rhs_terms = []
    for k in et_vals:
        col = f"et_{'m' if k<0 else 'p'}{abs(int(k))}"
        d[col] = (d["et"] == k).astype(int)
        rhs_terms.append(col)
    rhs = " + ".join(rhs_terms)
    if control_age:
        rhs += " + age + I(age**2)"
    rhs += " + C(player) + C(major_round)"
    model = smf.ols(f"sv_field ~ {rhs}", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["player"]})
    # extract event-time coefficients
    rows = []
    for k in et_vals:
        col = f"et_{'m' if k<0 else 'p'}{abs(int(k))}"
        if col in model.params.index:
            rows.append({"event_time": k,
                         "beta": model.params[col],
                         "se":   model.bse[col]})
    rows.append({"event_time": omit, "beta": 0.0, "se": 0.0})
    table = pd.DataFrame(rows).sort_values("event_time").reset_index(drop=True)
    return model, d, table


# ---------------------------------------------------------------------------
# Matched control group: pick one PGA stayer per defector, matched on
# pre-period skill (avg sv_field in pre-LIV majors), age at defection,
# and pre-period major appearance count.
# ---------------------------------------------------------------------------
def build_matched_controls(df: pd.DataFrame, k: int = 3) -> list[str]:
    """For each defector, find k nearest-neighbour stayers by Mahalanobis
    distance on (pre_sv_field, age_at_defection, n_pre_majors). Return the
    union of matched controls."""
    # pre-period summary stats
    pre = df[(df["round"].isin([1, 2])) & (df["sv_field"].notna())]
    # use only pre-2022-06 data so "pre" is symmetric for everyone
    pre_cutoff = pd.Timestamp("2022-06-01")
    pre = pre[pre["date"] < pre_cutoff]
    summ = (pre.groupby("player")
              .agg(pre_sv_field=("sv_field", "mean"),
                   n_pre=("major_id", "nunique"),
                   age_at_cutoff=("age", "max"))
              .dropna())
    # restrict to players with enough pre data
    summ = summ[summ["n_pre"] >= 4]

    defectors = [p for p in LIV_DEFECTORS if p in summ.index]
    stayers   = [p for p in summ.index if p not in LIV_DEFECTORS]
    if not defectors or not stayers:
        return []

    X = summ.loc[stayers + defectors].values
    cov = np.cov(X, rowvar=False)
    inv = np.linalg.pinv(cov)

    matched = set()
    for d_player in defectors:
        d_vec = summ.loc[d_player].values
        # distance to each stayer
        dists = []
        for s in stayers:
            diff = d_vec - summ.loc[s].values
            dists.append((s, float(diff @ inv @ diff)))
        dists.sort(key=lambda x: x[1])
        for s, _ in dists[:k]:
            matched.add(s)
    return sorted(matched)


# ---------------------------------------------------------------------------
# Pretty summary
# ---------------------------------------------------------------------------
def classify_defectors(df: pd.DataFrame) -> pd.Series:
    """Tag each defector as 'star', 'older', or 'journeyman'.

    star      = pre-period strokes-vs-field (R1+R2) <= -1.5 (truly elite)
    older     = age at defection >= 38
    journeyman = neither
    Players can only be in one bucket; star wins over older.
    """
    pre = df[(df["liv"] == 1) & (df["round"].isin([1, 2]))
             & (df["sv_field"].notna()) & (df["post"] == 0)]
    avg_pre = pre.groupby("player")["sv_field"].mean()
    age_at_def = (df[df["liv"] == 1]
                    .groupby("player")
                    .apply(lambda g: (g["defect_date"].iloc[0] - g["birthdate"].iloc[0]).days / 365.25
                           if pd.notna(g["birthdate"].iloc[0]) else np.nan))
    out = {}
    for p in LIV_DEFECTORS:
        sv = avg_pre.get(p, np.nan)
        ag = age_at_def.get(p, np.nan)
        if pd.notna(sv) and sv <= -1.5:
            out[p] = "star"
        elif pd.notna(ag) and ag >= 38:
            out[p] = "older"
        else:
            out[p] = "journeyman"
    return pd.Series(out)


def did_round_specific(df: pd.DataFrame, control_age: bool = True):
    """Estimate post effect separately for each round (R1..R4).
    Run as four separate regressions to keep the FE clean."""
    rows = []
    for r in [1, 2, 3, 4]:
        m, s = did_strokes_vs_field(df, rounds=(r,), control_age=control_age)
        rows.append({"round": r,
                     "beta": m.params.get("post", np.nan),
                     "se":   m.bse.get("post", np.nan),
                     "n":    len(s)})
    return pd.DataFrame(rows)


def did_by_subgroup(df: pd.DataFrame, groups: pd.Series,
                    control_age: bool = True):
    """Run the strokes DiD for each subgroup of defectors separately,
    using all stayers as the comparison group in each."""
    rows = []
    for g in sorted(groups.dropna().unique()):
        members = set(groups[groups == g].index)
        sub = df.copy()
        # null-out treatment for defectors NOT in this subgroup so they get
        # absorbed as untreated controls
        not_in = (sub["liv"] == 1) & ~sub["player"].isin(members)
        sub.loc[not_in, "post"] = 0
        sub.loc[not_in, "liv"]  = 0
        m, s = did_strokes_vs_field(sub, rounds=(1, 2), control_age=control_age)
        n_def = sub.loc[(sub["liv"] == 1) & (sub["post"] == 1), "player"].nunique()
        rows.append({"group": g, "beta": m.params.get("post", np.nan),
                     "se": m.bse.get("post", np.nan),
                     "n_defectors": n_def, "n_rounds": len(s)})
    return pd.DataFrame(rows)


def lee_bounds_made_cut(df: pd.DataFrame) -> dict:
    """Lee (2009) bounds on the made-cut effect, accounting for the fact
    that defectors with low post-period appearance counts are positively
    selected on quality. Treat 'appearance in post period' as the selection
    indicator and trim accordingly.

    Simple version: among defectors, calculate the share of players who
    appeared post (vs pre). If selection rate < 1, trim the worst (or best)
    pre-period observations to match.
    """
    by_major = (df.groupby(["player", "major_id", "date", "liv", "post"],
                           as_index=False)["made_cut"].max())
    pre  = by_major[(by_major["liv"] == 1) & (by_major["post"] == 0)]
    post = by_major[(by_major["liv"] == 1) & (by_major["post"] == 1)]
    # appearance rate: assume each defector "should" play 4 majors/year
    # post-period length per defector
    def_dates = pd.Series(LIV_DEFECTORS).map(pd.Timestamp)
    last_major = by_major["date"].max()
    expected_post = ((last_major - def_dates).dt.days / (365.25 / 4)).round()
    actual_post = post.groupby("player").size().reindex(LIV_DEFECTORS, fill_value=0)
    sel_rate = (actual_post / expected_post).clip(0, 1).mean()
    p_post = post["made_cut"].mean()
    p_pre  = pre["made_cut"].mean()
    # if selection rate < 1, the post-mean is biased upward (positively
    # selected entrants); upper-bound = observed; lower-bound = trim
    # the top (1 - sel_rate) share of post observations and recompute.
    trim_share = 1 - sel_rate
    sorted_post = post["made_cut"].sort_values(ascending=False)
    trim_n = int(round(trim_share * len(sorted_post)))
    p_post_trim = sorted_post.iloc[trim_n:].mean() if trim_n < len(sorted_post) else np.nan
    return {
        "p_pre": p_pre, "p_post_naive": p_post,
        "p_post_trimmed": p_post_trim, "selection_rate": sel_rate,
        "delta_naive": p_post - p_pre,
        "delta_lower": p_post_trim - p_pre if not np.isnan(p_post_trim) else np.nan,
    }


def summarize(df: pd.DataFrame):
    print("\n=== sample sizes ===")
    print(f"player-round rows: {len(df):,}")
    print(f"  with score:      {df['score'].notna().sum():,}")
    print(f"unique players:    {df['player'].nunique():,}")
    print(f"with birthdate:    {df['birthdate'].notna().sum():,}")
    print(f"defectors found:   {df.loc[df['liv']==1,'player'].nunique()} / {len(LIV_DEFECTORS)}")

    print("\n=== defector pre/post means (strokes vs round-field, R1+R2) ===")
    d = df[(df["liv"] == 1) & df["sv_field"].notna() & df["round"].isin([1, 2])].copy()
    g = d.groupby(["player", "post"])["sv_field"].mean().unstack("post")
    g.columns = ["pre", "post"] if list(g.columns) == [0, 1] else g.columns
    g["delta"] = g.get("post") - g.get("pre")
    print(g.dropna().sort_values("delta").to_string(float_format=lambda x: f"{x:+.2f}"))

    print("\n=== DiD strokes vs round-field, all stayers as control ===")
    for label, kwargs in [
        ("R1+R2 (no age control)", dict(rounds=(1, 2), control_age=False)),
        ("R1+R2 + age + age^2",    dict(rounds=(1, 2), control_age=True)),
        ("All rounds + age",       dict(rounds=(1, 2, 3, 4), control_age=True)),
        ("R3+R4 only + age",       dict(rounds=(3, 4), control_age=True)),
    ]:
        m, s = did_strokes_vs_field(df, **kwargs)
        c = m.params.get("post", np.nan); se = m.bse.get("post", np.nan)
        n_def = s.loc[s["liv"] == 1, "player"].nunique()
        print(f"  {label:30s}: post = {c:+.3f}  (SE {se:.3f})  N={len(s):,}, defectors={n_def}")

    # matched controls
    matched = build_matched_controls(df, k=3)
    print(f"\n=== matched-control spec ({len(matched)} stayers matched) ===")
    print(f"  matched stayers: {matched[:10]}{' ...' if len(matched)>10 else ''}")
    m, s = did_strokes_vs_field(df, rounds=(1, 2), control_age=True,
                                restrict_to=pd.Index(matched))
    c = m.params.get("post", np.nan); se = m.bse.get("post", np.nan)
    print(f"  R1+R2 + age, matched: post = {c:+.3f}  (SE {se:.3f})  N={len(s):,}")

    # heterogeneity
    print("\n=== heterogeneity by defector type ===")
    groups = classify_defectors(df)
    print("  defector type counts:", groups.value_counts().to_dict())
    het = did_by_subgroup(df, groups, control_age=True)
    print(het.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))

    # round-specific
    print("\n=== round-specific effects (age-controlled) ===")
    rs = did_round_specific(df, control_age=True)
    print(rs.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))

    # event study with leads (parallel-trends test)
    print("\n=== event study (R1+R2, age-controlled, omit t=-1) ===")
    _, _, table = event_study_strokes(df, rounds=(1, 2), control_age=True)
    print(table.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))
    pre_leads = table[(table["event_time"] < 0) & (table["event_time"] != -1)]
    f_test_pre = (pre_leads["beta"] / pre_leads["se"]).abs().max()
    print(f"  max |t-stat| on pre-period leads: {f_test_pre:.2f}  "
          f"({'pass' if f_test_pre < 1.96 else 'FAIL'} parallel-trends eyeball test)")

    # Lee bounds on cuts
    print("\n=== Lee-style bounds: made-cut effect ===")
    bounds = lee_bounds_made_cut(df)
    for k, v in bounds.items():
        print(f"  {k:20s} = {v:+.3f}" if isinstance(v, float) else f"  {k:20s} = {v}")

    print("\n=== defector pre/post cut rate (per major) ===")
    by_major = (df.groupby(["player", "major_id", "liv", "post"], as_index=False)
                  ["made_cut"].max())
    dc = by_major[by_major["liv"] == 1]
    gc = dc.groupby(["player", "post"])["made_cut"].mean().unstack("post")
    gc.columns = ["pre", "post"] if list(gc.columns) == [0, 1] else gc.columns
    gc["delta"] = gc.get("post") - gc.get("pre")
    gc["n_pre"]  = dc[dc["post"] == 0].groupby("player").size()
    gc["n_post"] = dc[dc["post"] == 1].groupby("player").size()
    print(gc.dropna(subset=["pre", "post"]).sort_values("delta")
            .to_string(float_format=lambda x: f"{x:+.2f}"))

    print("\n=== DiD: made-cut probability (per major) ===")
    m2, s2 = did_made_cut(df)
    coef = m2.params.get("post", np.nan)
    se   = m2.bse.get("post", np.nan)
    print(f"  post = {coef:+.3f}  (SE {se:.3f})   N major-appearances={len(s2):,}")
    print("  → negative means defectors started missing more cuts after moving")


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
FIG_DIR = "figures"
plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 160,
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "-",
})

WORSE_COLOR = "#C0392B"   # red
BETTER_COLOR = "#1E8449"  # green
NEUTRAL = "#7F8C8D"


def _per_defector_deltas(df: pd.DataFrame) -> pd.DataFrame:
    d = df[(df["liv"] == 1) & df["sv_field"].notna() & df["round"].isin([1, 2])]
    g = d.groupby(["player", "post"])["sv_field"].mean().unstack("post")
    g.columns = ["pre", "post"] if list(g.columns) == [0, 1] else g.columns
    g = g.dropna(subset=["pre", "post"]).copy()
    g["delta"] = g["post"] - g["pre"]
    g["n_post"] = (d[d["post"] == 1].groupby("player").size()
                   .reindex(g.index).fillna(0).astype(int))
    return g.sort_values("delta")


def _per_defector_cut_deltas(df: pd.DataFrame) -> pd.DataFrame:
    by_major = (df.groupby(["player", "major_id", "liv", "post"], as_index=False)
                  ["made_cut"].max())
    dc = by_major[by_major["liv"] == 1]
    g = dc.groupby(["player", "post"])["made_cut"].mean().unstack("post")
    g.columns = ["pre", "post"] if list(g.columns) == [0, 1] else g.columns
    g = g.dropna(subset=["pre", "post"]).copy()
    g["delta"] = g["post"] - g["pre"]
    g["n_post"] = (dc[dc["post"] == 1].groupby("player").size()
                   .reindex(g.index).fillna(0).astype(int))
    return g


def chart_player_deltas(df: pd.DataFrame, path: str):
    g = _per_defector_deltas(df)
    fig, ax = plt.subplots(figsize=(8, 9))
    colors = [WORSE_COLOR if d > 0 else BETTER_COLOR for d in g["delta"]]
    ax.barh(g.index, g["delta"], color=colors, edgecolor="white")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Change in strokes vs. field (R1+R2), post − pre")
    ax.set_title("LIV defectors: per-round scoring change at majors\n"
                 "(positive = got worse relative to the same field)",
                 loc="left", fontsize=12)
    # annotate with n_post
    for i, (player, row) in enumerate(g.iterrows()):
        x = row["delta"]
        ax.text(x + (0.08 if x >= 0 else -0.08), i, f"n={int(row['n_post'])}",
                va="center", ha="left" if x >= 0 else "right",
                fontsize=8, color=NEUTRAL)
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def chart_cut_rates(df: pd.DataFrame, path: str):
    g = _per_defector_cut_deltas(df)
    fig, ax = plt.subplots(figsize=(7, 7))
    sizes = 30 + 8 * g["n_post"]
    colors = [WORSE_COLOR if d < 0 else BETTER_COLOR if d > 0 else NEUTRAL
              for d in g["delta"]]
    ax.scatter(g["pre"], g["post"], s=sizes, c=colors, alpha=0.75,
               edgecolor="white", linewidth=0.7)
    lim = (-0.05, 1.05)
    ax.plot(lim, lim, color="black", lw=0.8, ls="--", alpha=0.6)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("Cut rate at majors, before LIV")
    ax.set_ylabel("Cut rate at majors, after LIV")
    ax.set_title("Cut rates at majors, pre vs. post defection\n"
                 "(below the dashed line = made fewer cuts after moving)",
                 loc="left", fontsize=12)
    # label a few notable players
    label_players = ["Jon Rahm", "Bryson DeChambeau", "Brooks Koepka",
                     "Cameron Smith", "Phil Mickelson", "Bubba Watson",
                     "Patrick Reed", "Dustin Johnson"]
    for p in label_players:
        if p in g.index:
            ax.annotate(p, (g.loc[p, "pre"], g.loc[p, "post"]),
                        xytext=(5, 5), textcoords="offset points",
                        fontsize=8, color="#34495E")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)




def chart_event_study(df: pd.DataFrame, path: str):
    """Formal event study: regression coefficients with leads and lags.
    Each point is the strokes-vs-field difference at event time k, relative
    to t=-1 (omitted), conditional on player FE, major-round FE, and age
    polynomial. Bars are 95% CIs.
    """
    _, _, table = event_study_strokes(df, rounds=(1, 2), control_age=True)
    table = table[(table["event_time"] >= -10) & (table["event_time"] <= 8)]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    pre = table[table["event_time"] < 0]
    post = table[table["event_time"] >= 0]
    for chunk, color, label in [(pre, "#34495E", "pre-defection"),
                                (post, WORSE_COLOR, "post-defection")]:
        ax.errorbar(chunk["event_time"], chunk["beta"],
                    yerr=1.96 * chunk["se"], fmt="o-", color=color,
                    label=label, capsize=3, lw=1.5,
                    markersize=6 if label == "post-defection" else 5)
    ax.axvline(-0.5, color="black", lw=0.8, ls="--", alpha=0.6)
    ax.axhline(0, color=NEUTRAL, lw=0.6)
    ax.set_xlabel("Major number relative to defection (0 = first major as LIV member)")
    ax.set_ylabel("Coefficient (strokes vs. field, R1+R2)")
    ax.set_title("Event-study regression: strokes vs. field by event time\n"
                 "(controls: player FE, major×round FE, age + age²; t=−1 omitted)",
                 loc="left", fontsize=11)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def chart_heterogeneity(df: pd.DataFrame, path: str):
    groups = classify_defectors(df)
    het = did_by_subgroup(df, groups, control_age=True)
    counts = groups.value_counts().to_dict()
    members = {g: sorted(groups[groups == g].index.tolist())
               for g in groups.unique()}
    short_label = {
        "star":       f"Stars\n(n={counts.get('star',0)})",
        "older":      f"Older (≥38)\n(n={counts.get('older',0)})",
        "journeyman": f"Journeymen\n(n={counts.get('journeyman',0)})",
    }
    order = ["star", "older", "journeyman"]
    het = het.set_index("group").reindex(order).reset_index()
    fig, ax = plt.subplots(figsize=(10, 4.8))
    y = np.arange(len(het))
    colors = [WORSE_COLOR if b > 0 else BETTER_COLOR for b in het["beta"]]
    ax.barh(y, het["beta"], xerr=1.96 * het["se"], color=colors,
            edgecolor="white", capsize=4, alpha=0.85, height=0.55)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([short_label[g] for g in het["group"]], fontsize=10)
    ax.invert_yaxis()
    # member names off to the right of zero, in small grey text
    for i, g in enumerate(het["group"]):
        names = members.get(g, [])
        text = ", ".join(names[:6]) + (" ..." if len(names) > 6 else "")
        # put text outside the visible bars to avoid overlap
        ax.text(0.02, i - 0.30, text, transform=ax.get_yaxis_transform(),
                fontsize=8, color="#6C7A89", va="center")
    ax.set_xlabel("Estimated effect on strokes vs. field (R1+R2, age-controlled)")
    ax.set_title("LIV's effect varies sharply by player type\n"
                 "(positive = worse after defecting; bars are 95% CI)",
                 loc="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def chart_spec_comparison(df: pd.DataFrame, path: str):
    """Forest plot: the post coefficient under different specifications."""
    matched = build_matched_controls(df, k=3)
    specs = []
    for label, kwargs in [
        ("R1+R2 only",                dict(rounds=(1, 2), control_age=False)),
        ("R1+R2  + age",              dict(rounds=(1, 2), control_age=True)),
        ("All rounds  + age",         dict(rounds=(1, 2, 3, 4), control_age=True)),
        ("R3+R4 only  + age",         dict(rounds=(3, 4), control_age=True)),
        ("R1+R2 + age, matched controls", dict(rounds=(1, 2), control_age=True,
                                               restrict_to=pd.Index(matched))),
    ]:
        m, s = did_strokes_vs_field(df, **kwargs)
        specs.append({"label": label,
                      "beta": m.params.get("post", np.nan),
                      "se":   m.bse.get("post", np.nan),
                      "n":    len(s)})
    sp = pd.DataFrame(specs)
    fig, ax = plt.subplots(figsize=(8, 4))
    y = np.arange(len(sp))[::-1]
    colors = [WORSE_COLOR if b > 0 else BETTER_COLOR for b in sp["beta"]]
    ax.errorbar(sp["beta"], y, xerr=1.96 * sp["se"], fmt="o", color="#34495E",
                ecolor=NEUTRAL, capsize=4, markersize=8)
    for i, (_, row) in enumerate(sp.iterrows()):
        ax.scatter(row["beta"], y[i], color=colors[i], s=80, zorder=3)
    ax.axvline(0, color="black", lw=0.8, ls="--", alpha=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(sp["label"], fontsize=10)
    ax.set_xlabel("Post-defection effect on strokes vs. field")
    ax.set_title("Effect estimate is robust across specifications\n"
                 "(positive = defectors worse; bars are 95% CI)",
                 loc="left", fontsize=12)
    # annotate sample sizes
    xmax = (sp["beta"] + 1.96 * sp["se"]).max() + 0.15
    for i, (_, row) in enumerate(sp.iterrows()):
        ax.text(xmax, y[i], f"N={row['n']:,}", va="center",
                fontsize=8, color=NEUTRAL)
    ax.set_xlim(left=min(0, (sp["beta"] - 1.96 * sp["se"]).min() - 0.1),
                right=xmax + 0.4)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def chart_dechambeau(df: pd.DataFrame, path: str):
    """Per-major time series for DeChambeau, with field comparison."""
    d = df[(df["player"] == "Bryson DeChambeau") & df["sv_field"].notna()
           & df["round"].isin([1, 2])]
    by_major = (d.groupby(["major_id", "date", "post"])["sv_field"]
                  .mean().reset_index().sort_values("date"))
    fig, ax = plt.subplots(figsize=(10, 4.5))
    pre = by_major[by_major["post"] == 0]
    post = by_major[by_major["post"] == 1]
    ax.scatter(pre["date"], pre["sv_field"], color="#34495E",
               label="pre-LIV", s=60, zorder=3)
    ax.scatter(post["date"], post["sv_field"], color=BETTER_COLOR,
               label="post-LIV", s=80, zorder=3, edgecolor="black", linewidth=0.5)
    ax.plot(by_major["date"], by_major["sv_field"], color=NEUTRAL,
            lw=0.8, alpha=0.5)
    ax.axhline(0, color=NEUTRAL, lw=0.6)
    # mark defection date
    defect = pd.Timestamp(DEFECTOR_BIRTHDATES.get("Bryson DeChambeau", "1993-09-16"))
    defect_actual = pd.Timestamp("2022-06-30")
    ax.axvline(defect_actual, color="black", ls="--", alpha=0.5)
    ax.text(defect_actual, ax.get_ylim()[1] * 0.95, "  signs with LIV",
            fontsize=9, va="top")
    ax.invert_yaxis()  # lower scores = better, so flip so up = better
    ax.set_ylabel("Strokes vs. field (R1+R2)\n← worse   |   better →", fontsize=10)
    ax.set_xlabel("Major date")
    ax.set_title("Bryson DeChambeau: the headline counterexample\n"
                 "(each dot = his average R1+R2 score relative to the field)",
                 loc="left", fontsize=12)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def chart_distribution(df: pd.DataFrame, path: str):
    d = df[(df["liv"] == 1) & df["sv_field"].notna() & df["round"].isin([1, 2])]
    pre = d.loc[d["post"] == 0, "sv_field"]
    post = d.loc[d["post"] == 1, "sv_field"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bins = np.arange(-12, 14, 1)
    ax.hist(pre, bins=bins, density=True, alpha=0.55, color="#34495E",
            label=f"pre-LIV  (n={len(pre):,} rounds, mean {pre.mean():+.2f})")
    ax.hist(post, bins=bins, density=True, alpha=0.55, color=WORSE_COLOR,
            label=f"post-LIV (n={len(post):,} rounds, mean {post.mean():+.2f})")
    ax.axvline(pre.mean(), color="#34495E", lw=1.2, ls="--")
    ax.axvline(post.mean(), color=WORSE_COLOR, lw=1.2, ls="--")
    ax.set_xlabel("Strokes vs. field (R1+R2)  —  lower is better")
    ax.set_ylabel("density")
    ax.set_title("Distribution of defectors' major rounds, pre vs. post LIV",
                 loc="left", fontsize=12)
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def make_plots(df: pd.DataFrame):
    os.makedirs(FIG_DIR, exist_ok=True)
    chart_cut_rates(df,         f"{FIG_DIR}/cut_rates.png")
    chart_heterogeneity(df,     f"{FIG_DIR}/heterogeneity.png")
    chart_spec_comparison(df,   f"{FIG_DIR}/spec_comparison.png")
    chart_player_deltas(df,     f"{FIG_DIR}/player_deltas.png")
    chart_event_study(df,       f"{FIG_DIR}/event_study.png")
    chart_dechambeau(df,        f"{FIG_DIR}/dechambeau.png")
    chart_distribution(df,      f"{FIG_DIR}/distribution.png")
    print(f"saved 7 charts to {FIG_DIR}/")


def main():
    print("scraping Wikipedia leaderboards ...")
    raw = build_dataset()
    raw.to_csv("liv_majors_rounds_raw.csv", index=False)
    print(f"\nsaved raw scrape to liv_majors_rounds_raw.csv ({len(raw):,} rows)")

    df = add_treatment(raw)
    df = add_outcomes(df)
    df = add_age(df)
    df = assign_event_time(df)
    df.to_csv("liv_majors_rounds_panel.csv", index=False)
    print("saved analysis panel to liv_majors_rounds_panel.csv")

    summarize(df)
    make_plots(df)


if __name__ == "__main__":
    main()
