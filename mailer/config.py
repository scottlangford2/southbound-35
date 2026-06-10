"""Configuration for the Southbound 35 newsletter mailer.

Email is sent from THIS machine over the existing lookoutanalytics SMTP creds
(same ones the weekly/team digests use). Subscriber data lives off-repo in
~/lookout_local/southbound35/ so it never lands in the public GitHub repo.

Two env files are read (later one wins):
  1. ~/lookout_local/research_scraper/.env   -> SMTP_HOST/PORT/USER/PASS (shared)
  2. ~/lookout_local/southbound35/.env       -> Worker URL, admin key, From/Reply-To
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---- Env files -------------------------------------------------------------
SHARED_ENV = Path.home() / "lookout_local" / "research_scraper" / ".env"
DATA_DIR = Path.home() / "lookout_local" / "southbound35"
NEWSLETTER_ENV = DATA_DIR / ".env"

for env_path in (SHARED_ENV, NEWSLETTER_ENV):
    if env_path.exists():
        load_dotenv(env_path, override=True)

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR = DATA_DIR / "logs"
PREVIEW_DIR = DATA_DIR / "preview"
for d in (LOGS_DIR, PREVIEW_DIR):
    d.mkdir(exist_ok=True)

# ---- Runtime data ----------------------------------------------------------
SUBSCRIBERS_CSV = DATA_DIR / "subscribers.csv"
SENT_LOG = DATA_DIR / "sent.json"   # records which post slugs have been sent
NOTIFY_STATE = DATA_DIR / "subscriber_state.json"  # snapshot of last-seen active emails

# ---- Blog source -----------------------------------------------------------
SITE_BASE = os.environ.get(
    "SITE_BASE", "https://scottlangford2.github.io/scott_langford"
).rstrip("/")
POSTS_DIR = Path(os.environ.get("POSTS_DIR", str(Path.home() / "scott_langford" / "_posts")))

# ---- Worker (list source) --------------------------------------------------
WORKER_BASE_URL = os.environ.get("WORKER_BASE_URL", "").rstrip("/")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")

# ---- SMTP (shared with the digests) ---------------------------------------
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

# ---- Newsletter identity ---------------------------------------------------
FROM_NAME = os.environ.get("NEWSLETTER_FROM_NAME", "Scott Langford")
FROM_EMAIL = os.environ.get("NEWSLETTER_FROM", SMTP_USER)
REPLY_TO = os.environ.get("NEWSLETTER_REPLY_TO", "scottlangford@txstate.edu")

# Where new-subscriber notifications go (defaults to the operator's address).
NOTIFY_TO = (
    os.environ.get("NEWSLETTER_NOTIFY_TO")
    or os.environ.get("EMAIL_TO")
    or "scottlangford2@gmail.com"
)

# Seconds to pause between individual sends, to stay under SMTP rate limits.
SEND_THROTTLE_SEC = float(os.environ.get("NEWSLETTER_THROTTLE", "1.5"))


def unsubscribe_url(token: str) -> str:
    return f"{WORKER_BASE_URL}/unsubscribe?token={token}"


def require_smtp() -> None:
    missing = [k for k, v in {"SMTP_USER": SMTP_USER, "SMTP_PASS": SMTP_PASS}.items() if not v]
    if missing:
        raise SystemExit(
            f"Missing SMTP creds ({', '.join(missing)}). Expected in {SHARED_ENV}."
        )


def require_worker() -> None:
    missing = [k for k, v in {"WORKER_BASE_URL": WORKER_BASE_URL, "ADMIN_KEY": ADMIN_KEY}.items() if not v]
    if missing:
        raise SystemExit(
            f"Missing Worker config ({', '.join(missing)}). Set them in {NEWSLETTER_ENV}."
        )
