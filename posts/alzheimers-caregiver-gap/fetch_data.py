"""
Fetch live data from public sources and rebuild the input CSVs.

This replaces the URL-catalog stub. Run with:

    pip install -r requirements.txt
    python fetch_data.py            # idempotent; skips cached raw files
    python fetch_data.py --refresh  # re-downloads everything

Raw downloads are cached under inputs/raw/. The script then parses
them and writes the canonical inputs/*.csv files that build_figures.py
consumes. Re-running is a no-op when raw files are cached.

Sources that this script fetches programmatically:

    BLS OEWS national wages (May 2024)            → wages_real.csv
    BLS OEWS Texas state wages (May 2024)         → texas_zoom.csv
    BLS Employment Projections 2023-2033          → direct_care_workforce.csv
    BLS CPI-U annual averages (BLS public API)    → wages_real.csv (deflator)
    Census NP2023 main series                     → pop_projections.csv
    Census ACS 1-year state 65+ population        → state_medicaid_workforce.csv
    IDEA Section 618 child counts SY2022-23       → disabled_children.csv
    CMS Chronic Conditions Warehouse (dementia)   → alz_prevalence.csv (lower bound)

Sources that remain manual (publisher does not offer a stable
machine-readable feed):

    Alzheimer's Association Facts & Figures (PDF tables)
        → alz_prevalence.csv (upper-bound scenario)
        → unpaid_caregiver_hours.csv
    AARP / National Alliance for Caregiving "Caregiving in the U.S."
        → unpaid_caregiver_hours.csv (relationship shares)
    KFF state HCBS spending (HTML; download URL changes per release)
        → state_medicaid_workforce.csv (HCBS spending column)
    ANCOR State of America's Direct Support Workforce Crisis (PDF)
        → texas_zoom.csv (DSP row)

For manual sources, the script reports the canonical hub URL and the
table reference needed, but does not modify the existing CSV values.
That preserves the audit trail in the file headers.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT = Path(__file__).parent
RAW = ROOT / "inputs" / "raw"
INPUTS = ROOT / "inputs"
RAW.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (compatible; southbound-35-fetch/1.0; "
      "research; +https://github.com/scottlangford2/southbound-35)")

CPI_U_ANNUAL = {
    2014: 236.736, 2015: 237.017, 2016: 240.007, 2017: 245.120,
    2018: 251.107, 2019: 255.657, 2020: 258.811, 2021: 270.970,
    2022: 292.655, 2023: 304.702, 2024: 313.689,
}

SOC_HHA      = "31-1121"
SOC_PCA      = "31-1122"
SOC_CNA      = "31-1131"
SOC_HHA_PCA  = "31-1120"
SOC_ALL      = "00-0000"
SOC_WAREHOUSE = "53-7065"
SOC_RETAIL    = "41-2031"
SOC_FASTFOOD  = "35-3023"
SOC_PSYCH_AIDE = "31-1133"

TX_FIPS = "48"


# -------------------------------------------------------------------- #
# HTTP plumbing                                                        #
# -------------------------------------------------------------------- #

def _get(url: str, timeout: int = 60, retries: int = 3,
         backoff: float = 2.0) -> bytes:
    """GET with User-Agent and exponential backoff retry."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(backoff ** attempt)
    raise RuntimeError(f"GET failed after {retries} attempts: {url}") from last_exc


def _post_json(url: str, body: dict, timeout: int = 60) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"User-Agent": UA, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _cache_path(name: str) -> Path:
    return RAW / name


def _fetch_to_cache(url: str, name: str, refresh: bool = False) -> Path:
    """Download `url` to inputs/raw/`name`, caching unless refresh=True.

    Returns the local path. Raises on download failure (caller decides
    whether to fall back to a manual source).
    """
    out = _cache_path(name)
    if out.exists() and not refresh:
        return out
    print(f"  fetch  → {url}")
    data = _get(url)
    out.write_bytes(data)
    print(f"  cached → inputs/raw/{name} ({len(data):,} bytes)")
    return out


# -------------------------------------------------------------------- #
# Source fetchers                                                      #
# -------------------------------------------------------------------- #

def fetch_bls_cpi_u(refresh: bool = False) -> dict[int, float]:
    """Annual-average CPI-U All Urban Consumers (series CUUR0000SA0),
    2014-2024. Hits the BLS public API and writes the cached JSON.

    Returns a year → index dict. Falls back to the hard-coded table
    above if the API is unreachable, so build_figures.py remains
    runnable offline.
    """
    out = _cache_path("bls_cpi_u.json")
    if out.exists() and not refresh:
        payload = json.loads(out.read_text())
    else:
        print("[BLS CPI-U]")
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        body = {
            "seriesid": ["CUUR0000SA0"],
            "startyear": "2014",
            "endyear": "2024",
            "annualaverage": True,
        }
        try:
            payload = _post_json(url, body)
            out.write_text(json.dumps(payload, indent=2))
            print(f"  cached → inputs/raw/{out.name}")
        except Exception as exc:
            print(f"  WARN: BLS API unreachable ({exc}); using "
                  f"hard-coded fallback CPI-U table.", file=sys.stderr)
            return dict(CPI_U_ANNUAL)

    rows = payload["Results"]["series"][0]["data"]
    result = {}
    for r in rows:
        if r.get("period") == "M13":  # annual average
            result[int(r["year"])] = float(r["value"])
    return result if result else dict(CPI_U_ANNUAL)


def fetch_bls_oews_national(refresh: bool = False) -> pd.DataFrame:
    """National May 2024 OEWS wage table.

    Returns DataFrame with OCC_CODE, OCC_TITLE, TOT_EMP (employment),
    H_MEDIAN (hourly median wage, USD/hr).
    """
    print("[BLS OEWS national May 2024]")
    url = "https://www.bls.gov/oes/special-requests/oesm24nat.zip"
    zip_path = _fetch_to_cache(url, "oesm24nat.zip", refresh=refresh)
    with zipfile.ZipFile(zip_path) as zf:
        member = next((n for n in zf.namelist()
                       if n.lower().endswith(".xlsx")), None)
        if member is None:
            raise RuntimeError(f"No xlsx inside {zip_path.name}")
        with zf.open(member) as f:
            df = pd.read_excel(f, dtype=str, engine="openpyxl")
    df.columns = [c.upper() for c in df.columns]
    df["TOT_EMP"] = pd.to_numeric(df["TOT_EMP"], errors="coerce")
    df["H_MEDIAN"] = pd.to_numeric(df["H_MEDIAN"], errors="coerce")
    return df[["OCC_CODE", "OCC_TITLE", "TOT_EMP", "H_MEDIAN"]]


def fetch_bls_oews_state(year: int = 2024, refresh: bool = False) -> pd.DataFrame:
    """All-state May 2024 OEWS file. Returns DataFrame keyed on AREA
    (state FIPS) and OCC_CODE.
    """
    print(f"[BLS OEWS state May {year}]")
    url = f"https://www.bls.gov/oes/special-requests/oesm{year - 2000:02d}st.zip"
    zip_path = _fetch_to_cache(url, f"oesm{year - 2000:02d}st.zip", refresh=refresh)
    frames = []
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.namelist():
            if not member.lower().endswith(".xlsx"):
                continue
            with zf.open(member) as f:
                df = pd.read_excel(f, dtype=str, engine="openpyxl")
            frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out.columns = [c.upper() for c in out.columns]
    out["TOT_EMP"] = pd.to_numeric(out["TOT_EMP"], errors="coerce")
    out["H_MEDIAN"] = pd.to_numeric(out["H_MEDIAN"], errors="coerce")
    keep = ["AREA", "AREA_TITLE", "OCC_CODE", "OCC_TITLE",
            "TOT_EMP", "H_MEDIAN"]
    return out[[c for c in keep if c in out.columns]]


def fetch_bls_ep(refresh: bool = False) -> pd.DataFrame:
    """BLS Employment Projections 2023-2033 occupation table.

    Returns DataFrame with SOC_CODE, OCC_TITLE, EMP_2023 (thousands),
    EMP_2033 (thousands), PCT_CHANGE_2023_33.
    """
    print("[BLS Employment Projections 2023-2033]")
    candidate_urls = [
        "https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.xlsx",
        "https://www.bls.gov/emp/data/occupational-data.xlsx",
        "https://www.bls.gov/emp/tables/Occupational_Projections.xlsx",
    ]
    path = None
    last_err = None
    for url in candidate_urls:
        try:
            path = _fetch_to_cache(url, "bls_ep_2023_33.xlsx", refresh=refresh)
            break
        except Exception as exc:
            last_err = exc
    if path is None:
        raise RuntimeError(
            "BLS Employment Projections XLSX not found at known URLs. "
            "Hub: https://www.bls.gov/emp/tables/"
            "occupational-projections-and-characteristics.htm . "
            f"Last error: {last_err}"
        )

    df = pd.read_excel(path, header=None, engine="openpyxl")
    header_row = None
    for i in range(min(20, len(df))):
        row = df.iloc[i].astype(str).str.lower().tolist()
        if any("occupation code" in c or "soc code" in c for c in row):
            header_row = i
            break
    if header_row is None:
        raise RuntimeError("Could not locate header row in BLS EP table.")
    df = pd.read_excel(path, header=header_row, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    def _col(*aliases: str) -> str:
        lower = {c.lower(): c for c in df.columns}
        for a in aliases:
            for k, v in lower.items():
                if a in k:
                    return v
        raise KeyError(f"None of {aliases} in {list(df.columns)}")

    soc_col   = _col("soc code", "occupation code")
    title_col = _col("occupation title", "occupation")
    emp_2023  = _col("employment, 2023", "2023 employment", "2023")
    emp_2033  = _col("employment, 2033", "2033 employment", "2033")

    out = pd.DataFrame({
        "SOC_CODE": df[soc_col].astype(str).str.strip(),
        "OCC_TITLE": df[title_col].astype(str).str.strip(),
        "EMP_2023": pd.to_numeric(df[emp_2023], errors="coerce"),
        "EMP_2033": pd.to_numeric(df[emp_2033], errors="coerce"),
    })
    out["PCT_CHANGE_2023_33"] = (out["EMP_2033"] / out["EMP_2023"] - 1.0) * 100.0
    return out


def fetch_census_np2023(refresh: bool = False) -> pd.DataFrame:
    """Census 2023 National Population Projections, main series,
    single-year-of-age detail.
    """
    print("[Census 2023 National Population Projections]")
    url = ("https://www2.census.gov/programs-surveys/popproj/datasets/"
           "2023/2023-summary-tables/np2023-d1.csv")
    path = _fetch_to_cache(url, "census_np2023_d1.csv", refresh=refresh)
    df = pd.read_csv(path)
    df.columns = [c.upper() for c in df.columns]
    if "SEX" in df.columns:
        df = df[(df["SEX"] == 0) & (df.get("ORIGIN", 0) == 0)
                & (df.get("RACE", 0) == 0)]
    return df


def fetch_census_acs_state_65p(year: int = 2023,
                               refresh: bool = False) -> pd.DataFrame:
    """Census ACS 1-year state 65+ population.

    Uses the Census public API. No key required for limited use.
    Returns DataFrame with state (USPS), pop_65p (millions).
    """
    print(f"[Census ACS 1-year {year} state 65+]")
    out = _cache_path(f"census_acs_{year}_state_65p.json")
    if out.exists() and not refresh:
        payload = json.loads(out.read_text())
    else:
        male_65p   = ["B01001_020E", "B01001_021E", "B01001_022E",
                      "B01001_023E", "B01001_024E", "B01001_025E"]
        female_65p = ["B01001_044E", "B01001_045E", "B01001_046E",
                      "B01001_047E", "B01001_048E", "B01001_049E"]
        all_vars = ",".join(["NAME"] + male_65p + female_65p)
        url = (f"https://api.census.gov/data/{year}/acs/acs1"
               f"?get={all_vars}&for=state:*")
        payload = json.loads(_get(url).decode("utf-8"))
        out.write_text(json.dumps(payload))
        print(f"  cached → inputs/raw/{out.name}")

    header, *rows = payload
    df = pd.DataFrame(rows, columns=header)
    num_cols = [c for c in df.columns if c.startswith("B01001_")]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["pop_65p"] = df[num_cols].sum(axis=1)

    name_to_usps = _state_name_to_usps()
    df["state"] = df["NAME"].map(name_to_usps)
    df = df.dropna(subset=["state"])
    return df[["state", "pop_65p"]]


def fetch_idea_section_618(refresh: bool = False) -> pd.DataFrame:
    """IDEA Section 618 child counts by disability category, ages 3-21,
    school year 2022-23. Returns DataFrame with category and count
    (children, not millions).
    """
    print("[IDEA Section 618 SY2022-23]")
    candidate_urls = [
        "https://sites.ed.gov/idea/files/bdpartbchildcountandedenvironment2022-23.xlsx",
        "https://sites.ed.gov/idea/files/2022-2023/bdpartbchildcountandedenvironment2022-23.xlsx",
    ]
    path = None
    last_err = None
    for url in candidate_urls:
        try:
            path = _fetch_to_cache(url, "idea_section_618_2022_23.xlsx",
                                   refresh=refresh)
            break
        except Exception as exc:
            last_err = exc
    if path is None:
        raise RuntimeError(
            "IDEA Section 618 XLSX not found at known URLs. "
            "Hub: https://sites.ed.gov/idea/data/ . "
            f"Last error: {last_err}"
        )

    sheets = pd.read_excel(path, sheet_name=None, header=None,
                           engine="openpyxl")
    target = None
    for name, df in sheets.items():
        if df.astype(str).apply(lambda s: s.str.contains(
                "Disability Category", case=False, na=False)).any().any():
            target = (name, df)
            break
    if target is None:
        raise RuntimeError("Could not locate disability-category sheet.")
    name, df = target
    header_idx = df.apply(lambda r: r.astype(str).str.contains(
        "Disability Category", case=False, na=False).any(), axis=1).idxmax()
    df = pd.read_excel(path, sheet_name=name, header=int(header_idx),
                       engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    cat_col = next(c for c in df.columns
                   if "disability category" in c.lower())
    count_col = next(c for c in df.columns
                     if "students" in c.lower() or "children" in c.lower())
    df = df[[cat_col, count_col]].rename(
        columns={cat_col: "category", count_col: "count"}
    )
    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    df = df.dropna()
    df["category"] = df["category"].astype(str).str.strip()
    return df


def fetch_cms_ccw_dementia(refresh: bool = False) -> pd.DataFrame:
    """CMS Chronic Conditions Warehouse: Alzheimer's & related
    disorders prevalence among Medicare FFS beneficiaries 65+.

    Returns DataFrame with year, beneficiaries_with_adrd, share_with_adrd.
    """
    print("[CMS Chronic Conditions Warehouse: ADRD prevalence]")
    candidate_urls = [
        ("https://data.cms.gov/sites/default/files/2024-06/"
         "Medicare_Chronic_Conditions_Prevalence_National.csv"),
        ("https://www2.ccwdata.org/documents/10280/19002232/"
         "cms-chronic-conditions-prevalence-national.csv"),
    ]
    path = None
    last_err = None
    for url in candidate_urls:
        try:
            path = _fetch_to_cache(url, "cms_ccw_national.csv",
                                   refresh=refresh)
            break
        except Exception as exc:
            last_err = exc
    if path is None:
        raise RuntimeError(
            "CMS CCW national prevalence file not found at known URLs. "
            "Hub: https://www2.ccwdata.org/web/guest/medicare-charts . "
            f"Last error: {last_err}"
        )

    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    cond_col = next((c for c in df.columns
                     if "condition" in c or "chronic" in c), None)
    if cond_col is None:
        raise RuntimeError(f"No condition column in {path.name}")
    mask = df[cond_col].astype(str).str.contains(
        "alzheimer", case=False, na=False)
    return df[mask].copy()


# -------------------------------------------------------------------- #
# Helpers                                                              #
# -------------------------------------------------------------------- #

def _state_name_to_usps() -> dict[str, str]:
    return {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT",
        "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL",
        "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
        "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
        "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
        "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
        "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
        "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
        "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
        "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY",
    }


_IDEA_KEY_FROM_CATEGORY = {
    "specific learning disabilities": "sld",
    "speech or language impairments": "sli",
    "speech/language impairments":    "sli",
    "other health impairments":       "ohi",
    "autism":                         "aut",
    "developmental delay":            "dd",
    "intellectual disabilities":      "id",
    "emotional disturbance":          "ed",
}

_IDEA_LABEL = {
    "sld": "Specific learning disabilities",
    "sli": "Speech/language impairments",
    "ohi": "Other health impairments (incl. ADHD)",
    "aut": "Autism",
    "dd":  "Developmental delay",
    "id":  "Intellectual disabilities",
    "ed":  "Emotional disturbance",
    "oth": "Multiple, hearing, visual, orthopedic, TBI, other",
}


# -------------------------------------------------------------------- #
# Builders: produce the canonical inputs/*.csv files                   #
# -------------------------------------------------------------------- #

def build_wages_real_csv(oews_national: pd.DataFrame,
                         cpi: dict[int, float]) -> None:
    """The 2024 OEWS gives one point; historical years require either
    the May-of-year OEWS releases or the BLS time series. To keep the
    pipeline minimal here, this writes the 2024 point and preserves
    the historical rows already in the committed CSV. A future
    extension can pull May 2014/2016/2018/2020/2022 archives from
    https://www.bls.gov/oes/tables.htm .
    """
    print("[build wages_real.csv]")
    occ_to_soc = {
        "hha":     SOC_HHA,
        "pca":     SOC_PCA,
        "cna":     SOC_CNA,
        "all_occ": SOC_ALL,
    }
    deflator_2024 = cpi.get(2024, CPI_U_ANNUAL[2024])

    existing = pd.read_csv(INPUTS / "wages_real.csv", comment="#")
    historic = existing[existing["year"] < 2024].copy()

    rows_2024 = []
    for occ, soc in occ_to_soc.items():
        row = oews_national[oews_national["OCC_CODE"] == soc]
        if row.empty:
            print(f"  WARN: SOC {soc} ({occ}) not found in OEWS national")
            continue
        nominal = float(row["H_MEDIAN"].iloc[0])
        # 2024 nominal already in 2024 dollars; CPI factor = 1
        real = nominal * (deflator_2024 / cpi.get(2024, deflator_2024))
        rows_2024.append({"year": 2024, "occupation": occ,
                          "median_wage_real_2024": round(real, 2)})

    new = pd.concat([historic, pd.DataFrame(rows_2024)],
                    ignore_index=True)
    new = new.sort_values(["year", "occupation"]).reset_index(drop=True)
    _write_with_header(INPUTS / "wages_real.csv", new,
                       INPUTS / "wages_real.csv")


def build_pop_projections_csv(np2023: pd.DataFrame) -> None:
    """Aggregate single-year-of-age detail to 65-74, 75-84, 85+ bands
    for the years used in pop_projections.csv (2020, 2025, 2030, 2035, 2040).
    """
    print("[build pop_projections.csv]")
    years = [2020, 2025, 2030, 2035, 2040]
    bands = [
        ("age_65_74", 65, 74),
        ("age_75_84", 75, 84),
        ("age_85plus", 85, 100),
    ]
    out_rows = []
    for y in years:
        col = f"POP_{y}"
        if col not in np2023.columns:
            print(f"  WARN: {col} not in NP2023 frame; skipping {y}")
            continue
        np2023[col] = pd.to_numeric(np2023[col], errors="coerce")
        row: dict[str, float | int] = {"year": y}
        for band_name, lo, hi in bands:
            mask = (np2023["AGE"].between(lo, hi)
                    if "AGE" in np2023.columns else None)
            if mask is None:
                continue
            row[band_name] = round(np2023.loc[mask, col].sum() / 1e6, 1)
        out_rows.append(row)
    new = pd.DataFrame(out_rows)
    _write_with_header(INPUTS / "pop_projections.csv", new,
                       INPUTS / "pop_projections.csv")


def build_direct_care_workforce_csv(oews_national: pd.DataFrame,
                                    ep: pd.DataFrame) -> None:
    """Use 2024 OEWS employment for the current point, BLS EP for 2033,
    and the same 2023-2033 CAGR extrapolation for 2040.
    """
    print("[build direct_care_workforce.csv]")
    existing = pd.read_csv(INPUTS / "direct_care_workforce.csv",
                           comment="#")
    historic = existing[existing["year"] < 2024].copy()

    def _ep_lookup(soc: str) -> tuple[float, float] | None:
        row = ep[ep["SOC_CODE"].astype(str).str.startswith(soc)]
        if row.empty:
            return None
        return float(row["EMP_2023"].iloc[0]), float(row["EMP_2033"].iloc[0])

    hha_pca_emp_2024 = oews_national.loc[
        oews_national["OCC_CODE"].isin([SOC_HHA, SOC_PCA]),
        "TOT_EMP",
    ].sum() / 1000.0
    cna_emp_2024 = oews_national.loc[
        oews_national["OCC_CODE"] == SOC_CNA, "TOT_EMP",
    ].sum() / 1000.0

    rows = [
        {"year": 2024, "occupation": "hha_pca", "employment_thousands": round(hha_pca_emp_2024)},
        {"year": 2024, "occupation": "cna",     "employment_thousands": round(cna_emp_2024)},
    ]

    for soc_key, occ_key in [(SOC_HHA_PCA, "hha_pca"), (SOC_CNA, "cna")]:
        ep_pair = _ep_lookup(soc_key)
        if ep_pair is None:
            print(f"  WARN: EP missing for {soc_key}")
            continue
        emp_2023, emp_2033 = ep_pair
        cagr = (emp_2033 / emp_2023) ** (1 / 10) - 1
        rows.append({"year": 2025, "occupation": occ_key,
                     "employment_thousands": round(emp_2023 * (1 + cagr) ** 2)})
        rows.append({"year": 2030, "occupation": occ_key,
                     "employment_thousands": round(emp_2023 * (1 + cagr) ** 7)})
        rows.append({"year": 2033, "occupation": occ_key,
                     "employment_thousands": round(emp_2033)})
        rows.append({"year": 2040, "occupation": occ_key,
                     "employment_thousands": round(emp_2033 * (1 + cagr) ** 7)})

    new = pd.concat([historic, pd.DataFrame(rows)], ignore_index=True)
    new = new.sort_values(["occupation", "year"]).reset_index(drop=True)
    _write_with_header(INPUTS / "direct_care_workforce.csv", new,
                       INPUTS / "direct_care_workforce.csv")


def build_disabled_children_csv(idea: pd.DataFrame) -> None:
    """Map IDEA's published category labels into the canonical keys."""
    print("[build disabled_children.csv]")
    idea = idea.copy()
    idea["lower"] = idea["category"].str.lower().str.strip()
    rows = []
    used = set()
    for _, r in idea.iterrows():
        key = next(
            (v for k, v in _IDEA_KEY_FROM_CATEGORY.items() if k in r["lower"]),
            None,
        )
        if key is None or key in used:
            continue
        used.add(key)
        rows.append({"panel": "idea_categories", "key": key,
                     "label": _IDEA_LABEL[key],
                     "value": round(float(r["count"]) / 1e6, 2)})

    other = 0.0
    for _, r in idea.iterrows():
        key = next(
            (v for k, v in _IDEA_KEY_FROM_CATEGORY.items() if k in r["lower"]),
            None,
        )
        if key is None:
            other += float(r["count"])
    if other > 0:
        rows.append({"panel": "idea_categories", "key": "oth",
                     "label": _IDEA_LABEL["oth"],
                     "value": round(other / 1e6, 2)})

    existing = pd.read_csv(INPUTS / "disabled_children.csv", comment="#")
    lfpr_rows = existing[existing["panel"] == "mothers_lfpr"]
    new = pd.concat([pd.DataFrame(rows), lfpr_rows], ignore_index=True)
    _write_with_header(INPUTS / "disabled_children.csv", new,
                       INPUTS / "disabled_children.csv")


def build_state_medicaid_workforce_csv(oews_state: pd.DataFrame,
                                       acs_65p: pd.DataFrame) -> None:
    """Compute direct-care workers per 1,000 elderly from BLS OEWS state
    employment + ACS 65+. The HCBS per-capita column is NOT refreshed
    here — KFF does not expose a stable machine-readable feed, and the
    existing CSV preserves the audit trail for that column.
    """
    print("[build state_medicaid_workforce.csv]")
    state_fips_to_usps = _state_fips_to_usps()

    care = oews_state[oews_state["OCC_CODE"].isin(
        [SOC_HHA, SOC_PCA, SOC_CNA, SOC_HHA_PCA])
    ].copy()
    care["TOT_EMP"] = pd.to_numeric(care["TOT_EMP"], errors="coerce")
    by_state = care.groupby("AREA")["TOT_EMP"].sum().reset_index()
    by_state["state"] = by_state["AREA"].map(state_fips_to_usps)
    by_state = by_state.dropna(subset=["state"])

    merged = by_state.merge(acs_65p, on="state", how="inner")
    merged["direct_care_per_1k_65p"] = (
        merged["TOT_EMP"] / (merged["pop_65p"] / 1000.0)
    ).round(0)

    existing = pd.read_csv(INPUTS / "state_medicaid_workforce.csv",
                           comment="#")
    keep = ["state", "hcbs_per_capita_usd"]
    refreshed = existing[keep].merge(
        merged[["state", "direct_care_per_1k_65p"]],
        on="state", how="left",
    )
    # Preserve old values only if the refreshed value is missing.
    refreshed["direct_care_per_1k_65p"] = refreshed["direct_care_per_1k_65p"].fillna(
        existing.set_index("state")["direct_care_per_1k_65p"]
    )
    _write_with_header(INPUTS / "state_medicaid_workforce.csv", refreshed,
                       INPUTS / "state_medicaid_workforce.csv")
    print("  note: HCBS spending column retained from manual entry; "
          "KFF does not offer a stable machine-readable feed. Hub: "
          "https://www.kff.org/medicaid/state-indicator/total-medicaid-hcbs-spending/")


def build_texas_zoom_csv(oews_state: pd.DataFrame) -> None:
    """Refresh Texas state wages for the four care SOCs and the
    comparable competitor SOCs.
    """
    print("[build texas_zoom.csv]")
    tx = oews_state[oews_state["AREA"] == TX_FIPS].copy()
    tx["H_MEDIAN"] = pd.to_numeric(tx["H_MEDIAN"], errors="coerce")

    def _med(soc: str) -> float | None:
        row = tx[tx["OCC_CODE"] == soc]
        if row.empty or pd.isna(row["H_MEDIAN"].iloc[0]):
            return None
        return float(row["H_MEDIAN"].iloc[0])

    refreshed = {
        ("hha", "care"):      _med(SOC_HHA),
        ("pca", "care"):      _med(SOC_PCA),
        ("cna", "care"):      _med(SOC_CNA),
        ("warehouse", "competitor"): _med(SOC_WAREHOUSE),
        ("retail",    "competitor"): _med(SOC_RETAIL),
        ("fastfood",  "competitor"): _med(SOC_FASTFOOD),
    }

    existing = pd.read_csv(INPUTS / "texas_zoom.csv", comment="#")
    out_rows = []
    for _, r in existing.iterrows():
        key = (r["occupation"], r["group"])
        refreshed_val = refreshed.get(key)
        if refreshed_val is not None:
            out_rows.append({"occupation": r["occupation"],
                             "group": r["group"],
                             "median_wage_2024": round(refreshed_val, 2)})
        else:
            out_rows.append({"occupation": r["occupation"],
                             "group": r["group"],
                             "median_wage_2024": float(r["median_wage_2024"])})
    new = pd.DataFrame(out_rows)
    _write_with_header(INPUTS / "texas_zoom.csv", new, INPUTS / "texas_zoom.csv")
    print("  note: DSP and Amazon FC rows retained from manual entry; "
          "BLS has no clean SOC for DSPs and Amazon FC wages come "
          "from company-posted listings.")


def build_alz_prevalence_csv_cms(cms: pd.DataFrame) -> None:
    """Refresh the cms_medicare_ffs scenario rows of alz_prevalence.csv.

    Conservative: requires year + prevalence count in the CMS file.
    If parsing fails, leaves the file unchanged.
    """
    print("[build alz_prevalence.csv: CMS scenario rows]")
    # CMS CCW file structure varies; we accept either 'year' + a
    # 'beneficiaries' or 'prevalence' column. If we can't find them,
    # we punt rather than corrupt the file.
    if cms.empty:
        print("  no CMS rows after filter; leaving CSV unchanged.")
        return
    year_col = next((c for c in cms.columns
                     if "year" in c.lower()), None)
    benf_col = next((c for c in cms.columns
                     if "beneficiaries" in c.lower()
                     or "count" in c.lower()), None)
    if year_col is None or benf_col is None:
        print("  CMS columns unrecognized; leaving CSV unchanged.")
        return
    cms_clean = cms[[year_col, benf_col]].copy()
    cms_clean[year_col] = pd.to_numeric(cms_clean[year_col], errors="coerce")
    cms_clean[benf_col] = pd.to_numeric(cms_clean[benf_col], errors="coerce")
    cms_clean = cms_clean.dropna()
    cms_clean["cases_millions"] = (cms_clean[benf_col] / 1e6).round(2)

    existing = pd.read_csv(INPUTS / "alz_prevalence.csv", comment="#")
    keep_assoc = existing[existing["scenario"] == "alz_assoc"]
    new_ffs_rows = pd.DataFrame({
        "year": cms_clean[year_col].astype(int),
        "scenario": "cms_medicare_ffs",
        "cases_millions": cms_clean["cases_millions"],
    })
    new = pd.concat([keep_assoc, new_ffs_rows], ignore_index=True)
    _write_with_header(INPUTS / "alz_prevalence.csv", new,
                       INPUTS / "alz_prevalence.csv")


# -------------------------------------------------------------------- #
# Output utilities                                                     #
# -------------------------------------------------------------------- #

def _state_fips_to_usps() -> dict[str, str]:
    fips = {
        "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA",
        "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
        "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN",
        "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
        "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS",
        "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
        "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
        "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
        "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
        "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
        "56": "WY",
    }
    return fips


def _read_header_comment(path: Path) -> str:
    """Read the leading comment block (lines starting with '#') of a CSV
    file. Returns the block as a single string including newlines.
    """
    if not path.exists():
        return ""
    lines = []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            lines.append(line)
        else:
            break
    return "\n".join(lines) + ("\n" if lines else "")


def _write_with_header(out: Path, df: pd.DataFrame,
                       header_source: Path) -> None:
    """Write `df` as CSV preceded by the existing file's header comment
    block (so audit trail is preserved across refreshes).
    """
    header = _read_header_comment(header_source)
    body = df.to_csv(index=False)
    out.write_text(header + body)
    print(f"  wrote   → inputs/{out.name} ({len(df)} rows)")


# -------------------------------------------------------------------- #
# Manual sources                                                       #
# -------------------------------------------------------------------- #

MANUAL_SOURCES = [
    ("Alzheimer's Association 2024 Facts & Figures",
     "https://www.alz.org/alzheimers-dementia/facts-figures",
     [
         "alz_prevalence.csv (alz_assoc scenario)",
         "unpaid_caregiver_hours.csv (hours, imputed value)",
     ],
     "Cite Tables 1 (prevalence projections) and the unpaid-caregiving "
     "tables. Publisher does not offer a machine-readable feed."),
    ("AARP & National Alliance for Caregiving, 'Caregiving in the U.S. 2020'",
     "https://www.aarp.org/caregiving/research/caregiving-in-the-united-states.html",
     ["unpaid_caregiver_hours.csv (relationship shares)"],
     "Survey-based; download the report PDF and transcribe relationship-share "
     "table values into the existing CSV."),
    ("KFF state Medicaid HCBS spending",
     "https://www.kff.org/medicaid/state-indicator/total-medicaid-hcbs-spending/",
     ["state_medicaid_workforce.csv (hcbs_per_capita_usd column)"],
     "KFF does not expose a stable download URL. Use the dashboard "
     "Export-to-CSV button on the indicator page, then update the "
     "hcbs_per_capita_usd column in state_medicaid_workforce.csv."),
    ("ANCOR State of America's Direct Support Workforce Crisis",
     "https://www.ancor.org/resources/state-of-direct-support-workforce-survey/",
     ["texas_zoom.csv (DSP row)"],
     "Survey report; download the PDF and update the DSP row in texas_zoom.csv."),
]


def report_manual_sources() -> None:
    print()
    print("Manual sources (publisher offers no stable machine-readable feed):")
    print()
    for name, hub, feeds, note in MANUAL_SOURCES:
        print(f"[{name}]")
        print(f"  hub:   {hub}")
        for feed in feeds:
            print(f"  feeds: inputs/{feed}")
        print(f"  note:  {note}")
        print()


# -------------------------------------------------------------------- #
# Orchestration                                                        #
# -------------------------------------------------------------------- #

def main(refresh: bool = False) -> int:
    print("Fetching live data for 'alzheimers-caregiver-gap'…")
    print()

    failures: list[tuple[str, Exception]] = []

    def _try(label: str, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            print(f"  FAILED [{label}]: {exc}", file=sys.stderr)
            failures.append((label, exc))
            return None

    cpi             = _try("BLS CPI-U",       fetch_bls_cpi_u, refresh=refresh) or dict(CPI_U_ANNUAL)
    oews_national   = _try("BLS OEWS nat.",   fetch_bls_oews_national, refresh=refresh)
    oews_state      = _try("BLS OEWS state",  fetch_bls_oews_state, refresh=refresh)
    ep              = _try("BLS EP 2023-33",  fetch_bls_ep, refresh=refresh)
    np2023          = _try("Census NP2023",   fetch_census_np2023, refresh=refresh)
    acs_65p         = _try("Census ACS 65+",  fetch_census_acs_state_65p, refresh=refresh)
    idea            = _try("IDEA Section 618", fetch_idea_section_618, refresh=refresh)
    cms             = _try("CMS CCW ADRD",    fetch_cms_ccw_dementia, refresh=refresh)

    print()
    print("Rebuilding canonical input CSVs…")
    print()
    if oews_national is not None:
        _try("wages_real.csv",          build_wages_real_csv, oews_national, cpi)
    if oews_national is not None and ep is not None:
        _try("direct_care_workforce.csv", build_direct_care_workforce_csv,
             oews_national, ep)
    if np2023 is not None:
        _try("pop_projections.csv",     build_pop_projections_csv, np2023)
    if idea is not None:
        _try("disabled_children.csv",   build_disabled_children_csv, idea)
    if oews_state is not None and acs_65p is not None:
        _try("state_medicaid_workforce.csv",
             build_state_medicaid_workforce_csv, oews_state, acs_65p)
    if oews_state is not None:
        _try("texas_zoom.csv",          build_texas_zoom_csv, oews_state)
    if cms is not None:
        _try("alz_prevalence.csv (CMS scenario)",
             build_alz_prevalence_csv_cms, cms)

    report_manual_sources()

    if failures:
        print(f"Completed with {len(failures)} failure(s):")
        for label, exc in failures:
            print(f"  - {label}: {exc}")
        print()
        print("Failed sources leave their target CSVs unchanged, so the "
              "package remains buildable from the committed inputs.")
        return 1
    print("Done. All live-fetchable inputs refreshed.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true",
                        help="Re-download even if raw files are cached.")
    args = parser.parse_args()
    sys.exit(main(refresh=args.refresh))
