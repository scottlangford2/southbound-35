#!/usr/bin/env python3
"""Email the operator when new subscribers appear.

Polls the Worker's /export, diffs the active list against a local record of
addresses already announced (notified.json), and emails a summary of any new
ones over the existing SMTP. Designed to run on a schedule (launchd).

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


def load_notified() -> set | None:
    if config.NOTIFIED_JSON.exists():
        return set(json.loads(config.NOTIFIED_JSON.read_text()))
    return None  # signals first run


def save_notified(emails: set) -> None:
    config.NOTIFIED_JSON.write_text(json.dumps(sorted(emails), indent=2))


def render_body(new: list[dict], total: int) -> str:
    lines = []
    for s in new:
        joined = (s.get("created_at", "") or "")[:19].replace("T", " ")
        lines.append(f"  • {s['email']}   (joined {joined} UTC)")
    return (
        f"{len(new)} new Southbound 35 subscriber"
        f"{'s' if len(new) != 1 else ''}:\n\n"
        + "\n".join(lines)
        + f"\n\nActive subscribers now: {total}\n"
    )


def send_notification(new: list[dict], total: int) -> None:
    msg = MIMEText(render_body(new, total), "plain", "utf-8")
    n = len(new)
    msg["Subject"] = f"📬 New Southbound 35 subscriber{'s' if n != 1 else ''}: {n}"
    msg["From"] = formataddr((config.FROM_NAME, config.FROM_EMAIL))
    msg["To"] = config.NOTIFY_TO
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as s:
        s.starttls()
        s.login(config.SMTP_USER, config.SMTP_PASS)
        s.send_message(msg)


def main() -> int:
    ap = argparse.ArgumentParser(description="Notify operator of new subscribers.")
    ap.add_argument("--include-existing", action="store_true",
                    help="on first run, email about the current list instead of seeding silently")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be sent; don't email or update state")
    args = ap.parse_args()

    config.require_worker()
    subs = fetch_subscribers()
    current_emails = {s["email"] for s in subs}
    notified = load_notified()

    if notified is None and not args.include_existing:
        if not args.dry_run:
            save_notified(current_emails)
        print(f"Baseline established with {len(current_emails)} existing "
              f"subscriber(s); no email sent.")
        return 0

    seen = notified or set()
    new = [s for s in subs if s["email"] not in seen]

    if not new:
        print("No new subscribers.")
        return 0

    if args.dry_run:
        print(f"DRY RUN — would email {config.NOTIFY_TO}:\n")
        print(render_body(new, len(current_emails)))
        return 0

    config.require_smtp()
    send_notification(new, len(current_emails))
    save_notified(seen | current_emails)
    print(f"Notified {config.NOTIFY_TO} of {len(new)} new subscriber(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
