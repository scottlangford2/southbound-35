#!/usr/bin/env python3
"""Email the operator when subscribers join or leave.

Polls the Worker's /export (active subscribers only), compares against a stored
snapshot of the last-seen active list, and emails a summary of any additions
(new subscribers) and departures (unsubscribes) over the existing SMTP.
Designed to run on a schedule (launchd).

First run establishes a silent baseline (so a pre-existing list doesn't all
arrive as "new") unless --include-existing is passed.

Usage:
    python3 -m mailer.notify_new_subscribers [--include-existing] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import smtplib
import sys
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid

from . import config
from .sync_subscribers import fetch_subscribers


def load_state() -> set | None:
    if config.NOTIFY_STATE.exists():
        data = json.loads(config.NOTIFY_STATE.read_text())
        return set(data.get("active", []))
    return None  # signals first run


def save_state(active: set) -> None:
    config.NOTIFY_STATE.write_text(json.dumps({"active": sorted(active)}, indent=2))


def render_body(new: list[dict], gone: list[str], total: int) -> str:
    parts = []
    if new:
        lines = []
        for s in new:
            joined = (s.get("created_at", "") or "")[:19].replace("T", " ")
            lines.append(f"  • {s['email']}   (joined {joined} UTC)")
        parts.append(
            f"{len(new)} new subscriber{'s' if len(new) != 1 else ''}:\n" + "\n".join(lines)
        )
    if gone:
        lines = [f"  • {e}" for e in gone]
        parts.append(
            f"{len(gone)} unsubscribe{'s' if len(gone) != 1 else ''}:\n" + "\n".join(lines)
        )
    return "\n\n".join(parts) + f"\n\nActive subscribers now: {total}\n"


def subject_for(new: list[dict], gone: list[str]) -> str:
    bits = []
    if new:
        bits.append(f"{len(new)} new")
    if gone:
        bits.append(f"{len(gone)} unsubscribed")
    icon = "📬" if new and not gone else ("👋" if gone and not new else "📊")
    return f"{icon} Southbound 35: {', '.join(bits)}"


def send_notification(new: list[dict], gone: list[str], total: int) -> None:
    msg = MIMEText(render_body(new, gone, total), "plain", "utf-8")
    msg["Subject"] = subject_for(new, gone)
    msg["From"] = formataddr((config.FROM_NAME, config.FROM_EMAIL))
    msg["To"] = config.NOTIFY_TO
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as s:
        s.starttls()
        s.login(config.SMTP_USER, config.SMTP_PASS)
        s.send_message(msg)


def main() -> int:
    ap = argparse.ArgumentParser(description="Notify operator of subscriber changes.")
    ap.add_argument("--include-existing", action="store_true",
                    help="on first run, email about the current list instead of seeding silently")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be sent; don't email or update state")
    args = ap.parse_args()

    config.require_worker()
    subs = fetch_subscribers()
    current = {s["email"] for s in subs}
    prev = load_state()

    if prev is None and not args.include_existing:
        if not args.dry_run:
            save_state(current)
        print(f"Baseline established with {len(current)} existing "
              f"subscriber(s); no email sent.")
        return 0

    prev = prev or set()
    new = [s for s in subs if s["email"] not in prev]
    gone = sorted(prev - current)

    if not new and not gone:
        print("No subscriber changes.")
        return 0

    if args.dry_run:
        print(f"DRY RUN — would email {config.NOTIFY_TO}:\n")
        print(subject_for(new, gone))
        print()
        print(render_body(new, gone, len(current)))
        return 0

    config.require_smtp()
    send_notification(new, gone, len(current))
    save_state(current)
    print(f"Notified {config.NOTIFY_TO}: {len(new)} new, {len(gone)} unsubscribed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
