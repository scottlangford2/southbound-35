"""
Download raw data for "The Hays Discount, Five Years Later".

Sources:
  1. Zillow Home Value Index (ZHVI), all homes, middle tier, smoothed and
     seasonally adjusted, monthly, county level. Public CSV, no API key.
  2. Freddie Mac Primary Mortgage Market Survey (PMMS), 30-year fixed
     rate, weekly. Pulled from FRED (series MORTGAGE30US).

Outputs (written to data/, git-ignored):
  - data/zhvi_counties.csv   — long-format, one row per (county, month)
  - data/mortgage_rates.csv  — weekly 30Y fixed rate

Usage:
    pip install -r requirements.txt
    python fetch_data.py
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)

ZHVI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)

FRED_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
)

COUNTIES = ["Travis County", "Williamson County", "Hays County"]


def fetch_zhvi() -> pd.DataFrame:
    """Download Zillow ZHVI, filter to Travis/Williamson/Hays, melt to long."""
    print("Downloading Zillow ZHVI county panel…")
    df = pd.read_csv(ZHVI_URL)

    mask = (df["StateName"] == "TX") & (df["RegionName"].isin(COUNTIES))
    sub = df.loc[mask].copy()
    if len(sub) != len(COUNTIES):
        found = sub["RegionName"].tolist()
        raise RuntimeError(
            f"Expected {len(COUNTIES)} Texas counties, found {len(sub)}: {found}"
        )

    id_cols = ["RegionName", "StateName"]
    date_cols = [c for c in sub.columns if c[:4].isdigit() and "-" in c]
    long = sub.melt(
        id_vars=id_cols,
        value_vars=date_cols,
        var_name="date",
        value_name="zhvi",
    )
    long["date"] = pd.to_datetime(long["date"])
    long = long.dropna(subset=["zhvi"])
    long = long.sort_values(["RegionName", "date"]).reset_index(drop=True)

    out = DATA / "zhvi_counties.csv"
    long.to_csv(out, index=False)
    print(f"  saved → {out} ({len(long):,} rows, "
          f"{long['date'].min().date()} → {long['date'].max().date()})")
    return long


def fetch_mortgage_rates() -> pd.DataFrame:
    """Download Freddie Mac 30-year fixed rate from FRED (no API key)."""
    print("Downloading Freddie Mac 30Y fixed rate (FRED: MORTGAGE30US)…")
    df = pd.read_csv(FRED_URL)
    df.columns = ["date", "rate"]
    df["date"] = pd.to_datetime(df["date"])
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    df = df.dropna(subset=["rate"]).reset_index(drop=True)

    out = DATA / "mortgage_rates.csv"
    df.to_csv(out, index=False)
    print(f"  saved → {out} ({len(df):,} weekly obs, "
          f"{df['date'].min().date()} → {df['date'].max().date()})")
    return df


if __name__ == "__main__":
    fetch_zhvi()
    fetch_mortgage_rates()
    print("Done.")
