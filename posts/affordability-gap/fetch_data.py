"""
Download raw data for "The Hays Discount, Five Years Later" (rigorous version).

All sources are public, no API keys required. Each fetched file is
checksummed and a manifest (data/MANIFEST.json) is written alongside so
downstream analysis can confirm it's running on the expected vintage.

Sources
-------
1. Zillow Home Value Index (ZHVI), monthly, county-level, three tiers:
     - bottom_third  (0.00 → 0.33)  — "what a migrator actually buys"
     - middle        (0.33 → 0.67)  — headline series
     - top_third     (0.67 → 1.00)  — Westlake-effect control
   Also pulled: ZHVI price-per-square-foot (county, mid-tier).

2. Zillow ZORI (Observed Rent Index), county-level, monthly, single-family
   + multifamily — sanity check on the affordability mechanism.

3. FHFA House Price Index, county, quarterly, all-transactions —
   repeat-sales, compositionally immune.

4. FRED / Realtor.com Market Hotness:
     - MEDLISPRI<FIPS>        Median listing price
     - MEDLISPRIPERSQUFEE<FIPS> Median listing price per sqft

5. FRED:
     - MORTGAGE30US           Freddie Mac 30-year fixed, weekly
     - CPIAUCSL               CPI-U All items, SA, monthly (deflator)
     - CUURS37BSA0            Dallas–Fort Worth–Arlington CPI-U, monthly

6. IRS SOI county-to-county migration inflows (2019–2023 releases).
   ZIP files per year, parsed to a single Hays-County inflow panel.

7. Denton (48121) and Collin (48085) counties — same Zillow panel,
   pulled automatically with the rest so (out-of-metro) robustness
   checks reuse one fetch.

County FIPS used throughout
---------------------------
    48453  Travis
    48491  Williamson
    48209  Hays
    48121  Denton     (robustness)
    48085  Collin     (robustness)

Usage
-----
    pip install -r requirements.txt
    python fetch_data.py              # full refresh
    python fetch_data.py --offline    # skip network; use cached data/ only
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ── Paths ───────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

MANIFEST_PATH = DATA / "MANIFEST.json"

# ── County registry ─────────────────────────────────────────────────────────
COUNTIES = {
    "Travis County":     {"fips": "48453", "role": "main"},
    "Williamson County": {"fips": "48491", "role": "main"},
    "Hays County":       {"fips": "48209", "role": "main"},
    "Denton County":     {"fips": "48121", "role": "robustness"},
    "Collin County":     {"fips": "48085", "role": "robustness"},
}

MAIN_COUNTIES = [c for c, m in COUNTIES.items() if m["role"] == "main"]

# ── Source URLs ─────────────────────────────────────────────────────────────
ZHVI_URLS = {
    "mid":    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
              "County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "bottom": "https://files.zillowstatic.com/research/public_csvs/zhvi/"
              "County_zhvi_uc_sfrcondo_tier_0.0_0.33_sm_sa_month.csv",
    "top":    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
              "County_zhvi_uc_sfrcondo_tier_0.67_1.0_sm_sa_month.csv",
}
ZHVI_PPSF_URL = ("https://files.zillowstatic.com/research/public_csvs/zhvi/"
                 "County_median_price_per_sqft_uc_sfrcondo_sm_sa_month.csv")
ZORI_URL = ("https://files.zillowstatic.com/research/public_csvs/zori/"
            "County_zori_uc_sfrcondomfr_sm_month.csv")

FHFA_URL = ("https://www.fhfa.gov/hpi/download/quarterly_datasets/"
            "hpi_at_bdl_county.csv")

FRED_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"

# Realtor.com panels on FRED — series IDs suffix the county FIPS.
REALTOR_SERIES = {
    "list_price":     "MEDLISPRI",
    "list_price_psf": "MEDLISPRIPERSQUFEE",
}

# Other FRED series (flat, no FIPS).
FRED_FLAT = {
    "mortgage30": "MORTGAGE30US",
    "cpi_us":     "CPIAUCSL",
    "cpi_dfw":    "CUURS37BSA0",
}

# IRS SOI migration inflows — yearly ZIPs.
IRS_SOI_YEARS = list(range(2019, 2024))  # 2019–2023 inflow releases

def irs_soi_url(yr: int) -> str:
    yy = str(yr)[-2:]
    yy_next = str(yr + 1)[-2:]
    return (f"https://www.irs.gov/pub/irs-soi/"
            f"county{yy}{yy_next}.zip")

# ── HTTP helpers ────────────────────────────────────────────────────────────
def _http_get(url: str, timeout: int = 60) -> bytes:
    """GET with a real User-Agent (Zillow/FRED 403 default urllib)."""
    from urllib.request import Request, urlopen
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (research fetch)"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()

def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

# ── Manifest ────────────────────────────────────────────────────────────────
def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {"created": datetime.now(timezone.utc).isoformat(), "sources": {}}

def _write_manifest(m: dict) -> None:
    m["updated"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.write_text(json.dumps(m, indent=2, sort_keys=True))

def _record(m: dict, key: str, url: str, blob: bytes, out: Path, notes: str = ""):
    m["sources"][key] = {
        "url":      url,
        "sha256":   _sha256(blob),
        "bytes":    len(blob),
        "fetched":  datetime.now(timezone.utc).isoformat(),
        "output":   str(out.relative_to(DATA.parent)),
        "notes":    notes,
    }

# ── Zillow fetchers ─────────────────────────────────────────────────────────
def _melt_zillow_wide(df: pd.DataFrame, fips_set: set[str],
                     value_name: str) -> pd.DataFrame:
    """Zillow ship wide CSVs; melt to long (county, date, value)."""
    fips_col = "StateCodeFIPS" if "StateCodeFIPS" in df.columns else None
    muni_col = "MunicipalCodeFIPS" if "MunicipalCodeFIPS" in df.columns else None
    if fips_col and muni_col:
        df = df.copy()
        df["fips"] = (df[fips_col].astype(str).str.zfill(2)
                      + df[muni_col].astype(str).str.zfill(3))
        sub = df[df["fips"].isin(fips_set)].copy()
    else:
        # fall back to StateName + RegionName lookup
        sub = df[(df["StateName"] == "TX")
                 & df["RegionName"].isin(COUNTIES.keys())].copy()
        sub["fips"] = sub["RegionName"].map(lambda n: COUNTIES[n]["fips"])

    id_cols = ["RegionName", "fips"]
    date_cols = [c for c in sub.columns
                 if len(c) >= 7 and c[:4].isdigit() and c[4] == "-"]
    long = sub.melt(id_vars=id_cols, value_vars=date_cols,
                    var_name="date", value_name=value_name)
    long["date"] = pd.to_datetime(long["date"])
    return long.dropna(subset=[value_name]).sort_values(id_cols + ["date"])

def fetch_zillow(manifest: dict, offline: bool) -> None:
    fips_set = {m["fips"] for m in COUNTIES.values()}

    # ZHVI tiers
    for tier, url in ZHVI_URLS.items():
        key = f"zhvi_{tier}"
        out = DATA / f"zhvi_{tier}.csv"
        if offline and out.exists():
            print(f"[offline] {key} — using cached {out.name}")
            continue
        print(f"→ {key} …")
        blob = _http_get(url)
        df = pd.read_csv(io.BytesIO(blob))
        long = _melt_zillow_wide(df, fips_set, value_name="zhvi")
        long["tier"] = tier
        long.to_csv(out, index=False)
        _record(manifest, key, url, blob, out,
                notes=f"{len(long):,} rows, "
                      f"{long['date'].min().date()} → "
                      f"{long['date'].max().date()}")

    # Price per sqft (mid)
    key, out, url = "zhvi_ppsf", DATA / "zhvi_ppsf.csv", ZHVI_PPSF_URL
    if not (offline and out.exists()):
        print(f"→ {key} …")
        blob = _http_get(url)
        df = pd.read_csv(io.BytesIO(blob))
        long = _melt_zillow_wide(df, fips_set, value_name="ppsf")
        long.to_csv(out, index=False)
        _record(manifest, key, url, blob, out)

    # ZORI rent index
    key, out, url = "zori", DATA / "zori.csv", ZORI_URL
    if not (offline and out.exists()):
        print(f"→ {key} …")
        try:
            blob = _http_get(url)
            df = pd.read_csv(io.BytesIO(blob))
            long = _melt_zillow_wide(df, fips_set, value_name="zori")
            long.to_csv(out, index=False)
            _record(manifest, key, url, blob, out)
        except Exception as e:
            # ZORI county-level coverage is thinner; survive gracefully.
            print(f"  skipped {key}: {e}")

# ── FHFA ────────────────────────────────────────────────────────────────────
def fetch_fhfa(manifest: dict, offline: bool) -> None:
    key, out, url = "fhfa_hpi", DATA / "fhfa_hpi.csv", FHFA_URL
    if offline and out.exists():
        print(f"[offline] {key} — using cached {out.name}")
        return
    print(f"→ {key} …")
    blob = _http_get(url)
    df = pd.read_csv(io.BytesIO(blob), dtype={"FIPS code": str})
    # Column name is "FIPS code" (with space) in FHFA's CSV. Normalize.
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # Keep our counties, annual quarter, HPI (all-transactions).
    fips_set = {m["fips"] for m in COUNTIES.values()}
    fips_col = "fips_code" if "fips_code" in df.columns else "fips"
    sub = df[df[fips_col].isin(fips_set)].copy()
    # FHFA file has columns: FIPS code, State, County, Year, Quarter, Annual Change (%), HPI, ...
    sub = sub.rename(columns={"hpi": "hpi_all",
                              "annual_change_(%)": "hpi_yoy"})
    sub["date"] = pd.PeriodIndex(
        year=sub["year"].astype(int),
        quarter=sub["quarter"].astype(int),
        freq="Q",
    ).to_timestamp(how="start")
    sub.to_csv(out, index=False)
    _record(manifest, key, url, blob, out,
            notes=f"{len(sub):,} rows; {sub['date'].min().date()} → "
                  f"{sub['date'].max().date()}")

# ── FRED ───────────────────────────────────────────────────────────────────
def _fetch_fred_csv(series: str) -> pd.DataFrame:
    url = FRED_BASE.format(series=series)
    blob = _http_get(url)
    df = pd.read_csv(io.BytesIO(blob))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna(subset=["value"]), url, blob

def fetch_fred(manifest: dict, offline: bool) -> None:
    # Flat series
    for key, series in FRED_FLAT.items():
        out = DATA / f"{key}.csv"
        if offline and out.exists():
            print(f"[offline] {key} — using cached {out.name}")
            continue
        print(f"→ FRED {series} ({key}) …")
        df, url, blob = _fetch_fred_csv(series)
        df.to_csv(out, index=False)
        _record(manifest, key, url, blob, out,
                notes=f"{len(df):,} obs; {df['date'].min().date()} → "
                      f"{df['date'].max().date()}")

    # Realtor per-county panels
    frames = {k: [] for k in REALTOR_SERIES}
    for name, prefix in REALTOR_SERIES.items():
        for county, meta in COUNTIES.items():
            series = f"{prefix}{meta['fips']}"
            try:
                print(f"→ FRED {series} ({name}, {county}) …")
                df, url, blob = _fetch_fred_csv(series)
                df["RegionName"] = county
                df["fips"] = meta["fips"]
                df = df.rename(columns={"value": name})
                frames[name].append(df)
                _record(manifest, f"realtor_{name}_{meta['fips']}",
                        url, blob, DATA / f"realtor_{name}.csv")
            except Exception as e:
                print(f"  skipped {series}: {e}")

        if frames[name]:
            pd.concat(frames[name], ignore_index=True).to_csv(
                DATA / f"realtor_{name}.csv", index=False)

# ── IRS SOI county-to-county migration ──────────────────────────────────────
def fetch_irs_soi(manifest: dict, offline: bool) -> None:
    """Hays-County inflow panel: origin county, year, returns, exemptions, AGI."""
    out = DATA / "irs_soi_hays_inflows.csv"
    if offline and out.exists():
        print(f"[offline] irs_soi_hays_inflows — using cached {out.name}")
        return

    rows = []
    for yr in IRS_SOI_YEARS:
        url = irs_soi_url(yr)
        try:
            print(f"→ IRS SOI migration inflows {yr} …")
            blob = _http_get(url, timeout=120)
        except Exception as e:
            print(f"  skipped {yr}: {e}")
            continue

        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            # File naming: countyinflow{yy}{yy+1}.csv (lowercased on some vintages).
            names = [n for n in zf.namelist() if "inflow" in n.lower()
                     and n.lower().endswith(".csv")]
            if not names:
                print(f"  no inflow CSV in {yr} archive")
                continue
            with zf.open(names[0]) as fh:
                df = pd.read_csv(fh, dtype=str, encoding="latin-1",
                                 on_bad_lines="skip")

        # IRS SOI columns: y2_statefips, y2_countyfips, y1_statefips, y1_countyfips,
        #                  y1_state, y1_countyname, n1 (returns), n2 (exemptions), AGI
        df.columns = [c.lower().strip() for c in df.columns]
        dest_fips = (df["y2_statefips"].astype(str).str.zfill(2)
                     + df["y2_countyfips"].astype(str).str.zfill(3))
        hays = df[dest_fips == "48209"].copy()
        hays["year"] = yr
        hays["origin_fips"] = (hays["y1_statefips"].astype(str).str.zfill(2)
                               + hays["y1_countyfips"].astype(str).str.zfill(3))
        for col in ("n1", "n2", "agi"):
            if col in hays.columns:
                hays[col] = pd.to_numeric(hays[col], errors="coerce")
        rows.append(hays)
        _record(manifest, f"irs_soi_{yr}", url, blob, out,
                notes=f"year {yr}, {len(hays):,} origin rows into Hays")

    if rows:
        panel = pd.concat(rows, ignore_index=True)
        panel.to_csv(out, index=False)
        print(f"  → {out.name} ({len(panel):,} rows)")

# ── Driver ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="Use cached data/ only; skip any network calls.")
    args = ap.parse_args()

    manifest = _load_manifest()

    if not args.offline:
        try:
            fetch_zillow(manifest,  offline=False)
            fetch_fhfa(manifest,    offline=False)
            fetch_fred(manifest,    offline=False)
            fetch_irs_soi(manifest, offline=False)
        except Exception as e:
            print(f"\nFetch aborted: {e}\n"
                  f"You can still run analysis on cached data/ with "
                  f"`python fetch_data.py --offline` followed by "
                  f"`python build_figures.py`.", file=sys.stderr)
            _write_manifest(manifest)
            raise
    else:
        print("Offline mode — no network calls.")

    _write_manifest(manifest)
    print(f"\nManifest: {MANIFEST_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
