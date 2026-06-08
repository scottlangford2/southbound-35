"""
Southbound 35 — Self-hosted mailer

Sends a blog-post notification email to each subscriber listed in
`subscribers.csv`, one at a time, via SMTP (Gmail by default). Each
recipient gets a personalized "Hi {name}" greeting, an excerpt of the
post, and a link to the live URL.

This is a hand-managed mailing list — no third party between you and
your subscribers. The list lives in a local CSV file. Subscribers and
unsubscribes are processed by hand. Suitable up to a few hundred
addresses; beyond that, switch to a hosted service.

Usage:
    # First time: copy the env template
    cp .env.example .env
    # Edit .env to add SMTP_USER and SMTP_APP_PASSWORD (Gmail app password)

    # Send the latest post
    python send_post.py --post 2026-05-25-hays-county-governance

    # Or pass the post slug from the _posts filename
    python send_post.py --post 2026-05-18-hays-county-schools --dry-run

    # Send to a single test address before the real run
    python send_post.py --post 2026-05-25-hays-county-governance \\
        --only test@example.com

CSV format (subscribers.csv, comma-separated):
    email,name,status,subscribed_on
    jane@example.com,Jane Doe,active,2026-05-01
    john@example.com,,active,2026-05-03

`status` should be `active` or `unsubscribed`. The script skips any
row whose status is not `active`. `name` is optional; if missing the
greeting reads "Hi there,".

Authentication: this uses SMTP with an app password, not OAuth. Create
a Gmail app password at https://myaccount.google.com/apppasswords and
put it in `.env` as SMTP_APP_PASSWORD. The script never touches your
real account password.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    import yaml  # PyYAML, used to parse Jekyll front matter
except ImportError:
    print("Missing dependency. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


# ── Configuration ─────────────────────────────────────────────────────────────

REPO_ROOT       = Path(__file__).resolve().parents[1]
SUBSCRIBERS_CSV = Path(__file__).resolve().parent / "subscribers.csv"
POSTS_DIR       = Path(os.environ.get("POSTS_DIR",
                                       Path.home() / "scott_langford" / "_posts"))
SITE_BASE_URL   = os.environ.get("SITE_BASE_URL",
                                  "https://scottlangford2.github.io/scott_langford")

SMTP_HOST       = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT       = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER       = os.environ.get("SMTP_USER")           # e.g. you@gmail.com
SMTP_APP_PW     = os.environ.get("SMTP_APP_PASSWORD")
FROM_NAME       = os.environ.get("FROM_NAME", "Scott Langford")
REPLY_TO        = os.environ.get("REPLY_TO", SMTP_USER)
THROTTLE_SECONDS = float(os.environ.get("THROTTLE_SECONDS", "2.0"))


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_env(env_path: Path = Path(__file__).resolve().parent / ".env") -> None:
    """Minimal .env loader. No external dependency."""
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip("'\""))


def parse_post(post_slug: str) -> dict:
    """Locate a post by slug (e.g. '2026-05-25-hays-county-governance'),
    parse the YAML front matter, and return a dict with title, url,
    permalink, excerpt, and full body markdown."""
    path = POSTS_DIR / f"{post_slug}.md"
    if not path.exists():
        # fall back: look for any file matching the slug
        matches = list(POSTS_DIR.glob(f"*{post_slug}*.md"))
        if len(matches) == 1:
            path = matches[0]
        else:
            raise FileNotFoundError(
                f"No post found for slug {post_slug!r} in {POSTS_DIR}")

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"Post {path.name} has no YAML front matter")

    _, fm_block, body = text.split("---", 2)
    front = yaml.safe_load(fm_block)
    body = body.strip()

    # First non-empty paragraph as the excerpt
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    excerpt_md = paragraphs[0] if paragraphs else ""

    permalink = front.get("permalink", f"/{path.stem}/")
    url = SITE_BASE_URL.rstrip("/") + permalink

    return {
        "title":    front.get("title", "(untitled)"),
        "url":      url,
        "permalink": permalink,
        "date":     front.get("date"),
        "excerpt":  excerpt_md,
        "body":     body,
        "path":     path,
    }


def load_subscribers(csv_path: Path) -> list[dict]:
    """Load active subscribers.

    Preference order:
      1) If SB35_WORKER_URL and SB35_ADMIN_TOKEN are set in the
         environment, pull confirmed subscribers from the Cloudflare
         Worker. This is the production path.
      2) Otherwise fall back to reading the local subscribers.csv
         (legacy / offline mode).
    """
    worker_url = os.environ.get("SB35_WORKER_URL")
    admin_token = os.environ.get("SB35_ADMIN_TOKEN")

    if worker_url and admin_token:
        return _load_from_worker(worker_url, admin_token)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Subscribers file not found at {csv_path}, and no "
            f"SB35_WORKER_URL / SB35_ADMIN_TOKEN set in the environment "
            f"to pull from the Cloudflare Worker. Either set those, or "
            f"copy subscribers.csv.example and add real entries.")
    subs: list[dict] = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row.get("status") or "active").strip().lower() == "active":
                subs.append({
                    "email": row["email"].strip(),
                    "name":  (row.get("name") or "").strip(),
                })
    return subs


def _load_from_worker(worker_url: str, admin_token: str) -> list[dict]:
    """Pull confirmed subscribers from the Cloudflare Worker /subscribers
    endpoint. Returns the list in the same shape the CSV loader returns."""
    import urllib.request
    import urllib.error
    url = worker_url.rstrip("/") + "/subscribers"
    req = urllib.request.Request(url, headers={"X-Admin-Token": admin_token})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"Worker returned HTTP {e.code} when listing subscribers. "
            f"Check SB35_WORKER_URL and SB35_ADMIN_TOKEN.")
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Could not reach Worker at {url}: {e.reason}")

    subs: list[dict] = []
    for rec in payload.get("subscribers", []):
        if rec.get("status") != "confirmed":
            continue
        subs.append({
            "email": rec.get("email", "").strip(),
            "name":  (rec.get("name") or "").strip(),
        })
    return subs


def render_email(post: dict, name: str) -> tuple[str, str]:
    """Return (plain_text, html) bodies for one subscriber."""
    greeting = f"Hi {name.split()[0]}," if name else "Hi there,"

    plain = (
        f"{greeting}\n\n"
        f"New post on Southbound 35:\n\n"
        f"    {post['title']}\n"
        f"    {post['url']}\n\n"
        f"{post['excerpt']}\n\n"
        f"Read the full post:\n  {post['url']}\n\n"
        f"— Scott\n\n"
        f"---\n"
        f"You're receiving this because you subscribed to Southbound 35.\n"
        f"To unsubscribe, reply with 'unsubscribe' and I'll remove you the same day."
    )

    html = f"""\
<html><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.55; color: #1a1a1a; max-width: 620px; margin: 24px auto; padding: 0 16px;">
  <p>{greeting}</p>
  <p>New post on <em>Southbound 35</em>:</p>
  <h2 style="margin-top: 0.5em;"><a href="{post['url']}" style="color: #006BA2; text-decoration: none;">{post['title']}</a></h2>
  <p style="color: #333;">{post['excerpt']}</p>
  <p><a href="{post['url']}" style="display: inline-block; background: #006BA2; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none;">Read the full post →</a></p>
  <p style="margin-top: 2em;">— Scott</p>
  <hr style="border: none; border-top: 1px solid #ddd; margin: 2em 0 1em;">
  <p style="font-size: 0.85em; color: #888;">
    You're receiving this because you subscribed to <em>Southbound 35</em>.
    To unsubscribe, reply with "unsubscribe" and I'll remove you the same day.
  </p>
</body></html>
"""
    return plain, html


def send_one(server: smtplib.SMTP, to_email: str, to_name: str,
             post: dict, dry_run: bool = False) -> None:
    """Send the post email to a single subscriber."""
    plain, html = render_email(post, to_name)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = post["title"]
    msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
    msg["To"]      = f"{to_name} <{to_email}>" if to_name else to_email
    msg["Reply-To"] = REPLY_TO
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    if dry_run:
        print(f"  [dry-run] would send to {to_email}")
        return

    server.sendmail(SMTP_USER, [to_email], msg.as_string())
    print(f"  sent → {to_email}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    load_env()

    ap = argparse.ArgumentParser(description="Send a Southbound 35 post to subscribers.")
    ap.add_argument("--post", required=True,
                    help="Post slug (filename without .md), e.g. "
                         "2026-05-25-hays-county-governance")
    ap.add_argument("--only", help="Send only to this single email address (testing)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Render and log without sending")
    args = ap.parse_args()

    if not args.dry_run and not (SMTP_USER and SMTP_APP_PW):
        print("ERROR: SMTP_USER and SMTP_APP_PASSWORD must be set in .env "
              "(or pass --dry-run).", file=sys.stderr)
        sys.exit(1)

    post = parse_post(args.post)
    print(f"\nPost: {post['title']}")
    print(f"URL:  {post['url']}\n")

    subs = load_subscribers(SUBSCRIBERS_CSV)
    if args.only:
        subs = [s for s in subs if s["email"] == args.only]
        if not subs:
            # Allow ad-hoc test send to an address not in the list
            subs = [{"email": args.only, "name": ""}]
            print(f"(Test send to {args.only} — not in subscribers.csv)")

    print(f"Sending to {len(subs)} subscriber(s) "
          f"{'(dry run)' if args.dry_run else 'live'}.\n")

    server = None
    if not args.dry_run:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_APP_PW)

    try:
        for i, s in enumerate(subs, 1):
            send_one(server, s["email"], s["name"], post, dry_run=args.dry_run)
            if not args.dry_run and i < len(subs):
                time.sleep(THROTTLE_SECONDS)
    finally:
        if server is not None:
            server.quit()

    print(f"\nDone. {len(subs)} email(s) {'simulated' if args.dry_run else 'sent'}.")


if __name__ == "__main__":
    main()
