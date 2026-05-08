"""
Download and cache public shapefiles used by build_figures.py.

Run once before build_figures.py. Idempotent: skips downloads when
the target file already exists in inputs/shapefiles/.

Sources:
    TWDB Major Aquifers — https://www.twdb.texas.gov/mapping/gisdata.asp
    TWDB Groundwater Conservation Districts — same page
    Census TIGER cartographic county boundaries (2023, 1:5M)

All three are public-domain or open-data.
"""

import shutil
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).parent
SHAPES = ROOT / "inputs" / "shapefiles"
SHAPES.mkdir(parents=True, exist_ok=True)

DOWNLOADS = [
    {
        "url":      "https://www.twdb.texas.gov/mapping/gisdata/doc/major_aquifers.zip",
        "subdir":   "major_aquifers",
        "marker":   "NEW_major_aquifers_dd.shp",
    },
    {
        "url":      "https://www.twdb.texas.gov/mapping/gisdata/doc/GCD_Shapefiles.zip",
        "subdir":   "gcd",
        "marker":   "TWDB_GCD_NOV2019.shp",
    },
    {
        "url":      "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_5m.zip",
        "subdir":   "county",
        "marker":   "cb_2023_us_county_5m.shp",
    },
]


def fetch(item):
    target_dir = SHAPES / item["subdir"]
    marker = target_dir / item["marker"]
    if marker.exists():
        print(f"  cached  → {target_dir.relative_to(ROOT)}")
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    zip_path = target_dir.parent / f"{item['subdir']}.zip"
    print(f"  fetch   → {item['url']}")
    urlretrieve(item["url"], zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(target_dir)
    zip_path.unlink()
    print(f"  unzipped→ {target_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    print("Fetching shapefiles for hays-water replication…")
    for item in DOWNLOADS:
        fetch(item)
    print("Done.")
