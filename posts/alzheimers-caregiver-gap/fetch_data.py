"""
Document the public download URLs that back the committed input CSVs.

The CSVs under `inputs/` are committed so the package builds without
network access. This script exists to make the provenance reproducible:
re-running it prints the canonical source URL for each input, and (where
the publisher offers a direct download with a stable URL) refreshes a
cached copy under `inputs/raw/`. Hand-curated tables transcribed from
the Alzheimer's Association Facts & Figures PDF are listed but not
fetched, since the publisher does not offer a machine-readable feed.

Usage:
    python fetch_data.py

Re-running is a no-op for already-cached files.
"""

from __future__ import annotations

import sys
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).parent
RAW = ROOT / "inputs" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


@dataclass
class Source:
    name: str
    url: str
    target: str = ""
    note: str = ""
    fetchable: bool = True
    feeds: list[str] = field(default_factory=list)


SOURCES: list[Source] = [
    Source(
        name="BLS OEWS May 2024 national wages (xlsx)",
        url="https://www.bls.gov/oes/special-requests/oesm24nat.zip",
        target="bls_oews_2024_national.zip",
        feeds=["wages_real.csv"],
        note="Median hourly wage by SOC; filter to 31-1120, 31-1122, 31-1131.",
    ),
    Source(
        name="BLS Employment Projections 2023-2033 occupation table",
        url="https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm",
        target="bls_ep_2023_2033.xlsx",
        feeds=["direct_care_workforce.csv"],
        note="Download 'Occupational projections and worker characteristics' xlsx.",
    ),
    Source(
        name="BLS CPI-U All Urban Consumers, annual",
        url="https://download.bls.gov/pub/time.series/cu/cu.data.0.Current",
        target="bls_cpi_u.txt",
        feeds=["wages_real.csv"],
        note="Series CUUR0000SA0; annual averages used for real-wage deflation.",
    ),
    Source(
        name="Census 2023 National Population Projections (NP2023_D1)",
        url="https://www2.census.gov/programs-surveys/popproj/datasets/2023/2023-summary-tables/np2023_d1.csv",
        target="census_np2023_d1.csv",
        feeds=["pop_projections.csv"],
        note="Single-year-of-age detail; aggregated to 65-74, 75-84, 85+.",
    ),
    Source(
        name="CMS Chronic Conditions among Medicare FFS Beneficiaries",
        url="https://www.cms.gov/data-research/statistics-trends-and-reports/chronic-conditions",
        target="cms_chronic_conditions.csv",
        feeds=["alz_prevalence.csv (cms_medicare_ffs scenario)"],
        note="National prevalence table; filter to 'Alzheimer's Disease and Related Disorders'.",
    ),
    Source(
        name="Alzheimer's Association 2024 Facts & Figures (PDF, copyrighted)",
        url="https://www.alz.org/alzheimers-dementia/facts-figures",
        feeds=[
            "alz_prevalence.csv (alz_assoc scenario)",
            "unpaid_caregiver_hours.csv",
        ],
        note="Numerical tables are factual and transcribed by hand into the CSVs above. "
             "Cite Tables 1 (prevalence projections), 4 (unpaid hours), "
             "and 6 (relationship of caregivers).",
        fetchable=False,
    ),
]


def fetch(src: Source) -> None:
    if not src.fetchable:
        print(f"  manual  → {src.name}")
        print(f"            {src.url}")
        return
    out = RAW / src.target
    if out.exists():
        print(f"  cached  → inputs/raw/{out.name}")
        return
    print(f"  fetch   → {src.url}")
    try:
        urlretrieve(src.url, out)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"  FAILED  → {exc}", file=sys.stderr)
        print(f"            Skipping; the committed CSV under inputs/ is "
              f"the canonical input for build_figures.py.", file=sys.stderr)
        return
    print(f"  saved   → inputs/raw/{out.name}")


def main() -> None:
    print("Refreshing raw inputs for 'alzheimers-caregiver-gap'…")
    print()
    for src in SOURCES:
        print(f"[{src.name}]")
        for feed in src.feeds:
            print(f"  feeds   → inputs/{feed}")
        if src.note:
            print(f"  note    → {src.note}")
        fetch(src)
        print()
    print("Done. Committed CSVs in inputs/ remain the build inputs of record.")


if __name__ == "__main__":
    main()
