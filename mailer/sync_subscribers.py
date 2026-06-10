#!/usr/bin/env python3
"""Pull the active subscriber list from the Cloudflare Worker into a local CSV.

The CSV (~/lookout_local/southbound35/subscribers.csv) is what the sender reads,
so it works offline once synced. Run this before sending, or on a schedule.

Usage:
    python3 -m mailer.sync_subscribers
"""

from __future__ import annotations

import csv
import sys

import requests

from . import config


def fetch_subscribers() -> list[dict]:
    config.require_worker()
    url = f"{config.WORKER_BASE_URL}/export"
    resp = requests.get(url, params={"key": config.ADMIN_KEY}, timeout=30)
    if resp.status_code == 401:
        raise SystemExit("Worker rejected ADMIN_KEY (401). Check it matches the Worker secret.")
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise SystemExit(f"Worker returned an error: {data}")
    return data.get("subscribers", [])


def write_csv(subscribers: list[dict]) -> None:
    with config.SUBSCRIBERS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["email", "token", "created_at"])
        writer.writeheader()
        for s in subscribers:
            writer.writerow({
                "email": s.get("email", ""),
                "token": s.get("token", ""),
                "created_at": s.get("created_at", ""),
            })


def main() -> int:
    subs = fetch_subscribers()
    write_csv(subs)
    print(f"Synced {len(subs)} active subscriber(s) -> {config.SUBSCRIBERS_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
