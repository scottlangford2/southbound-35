#!/usr/bin/env python3
"""Send a Southbound 35 post to the subscriber list, one personal email each.

By default it pulls the *published* post HTML from the live site (so the email
matches what readers see), strips the article body, rewrites relative links to
absolute, and wraps it in a clean email template with a per-subscriber
unsubscribe link. Sends individually (not BCC) over the existing SMTP creds.

Usage:
    python3 -m mailer.send_post <slug | permalink-path | url | file.md> [options]

Options:
    --test EMAIL     Send only to EMAIL (a real render); does not mark as sent.
    --dry-run        Render to a preview .html file and exit; send nothing.
    --resend         Send even if this post is already in the sent log.
    --subject "..."  Override the subject line (default: the post title).
    --local          Render from the local markdown file instead of live HTML
                     (use for drafts not yet published).
    --limit N        Send to at most N subscribers (testing).

Examples:
    python3 -m mailer.send_post hays-county-governance --dry-run
    python3 -m mailer.send_post hays-county-governance --test you@example.com
    python3 -m mailer.send_post hays-county-governance
"""

from __future__ import annotations

import argparse
import csv
import html as html_lib
import json
import re
import smtplib
import sys
import time
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from . import config

HOST = "https://scottlangford2.github.io"  # for rewriting root-relative URLs
STRIP_SELECTORS = [
    "script", "style", ".series-spine", ".page__share", ".page__comments",
    ".page__related", ".pagination", "nav", ".page__taxonomy",
]


# --------------------------------------------------------------------------- #
# Post resolution
# --------------------------------------------------------------------------- #
def find_local_post(arg: str) -> Path | None:
    p = Path(arg).expanduser()
    if p.is_file():
        return p
    # treat as slug: match against _posts filenames
    matches = sorted(config.POSTS_DIR.glob(f"*{arg}*.md"))
    return matches[-1] if matches else None


def parse_front_matter(md_text: str) -> tuple[dict, str]:
    if not md_text.startswith("---"):
        return {}, md_text
    end = md_text.find("\n---", 3)
    if end == -1:
        return {}, md_text
    fm_block = md_text[3:end]
    body = md_text[end + 4:].lstrip("\n")
    fm: dict[str, str] = {}
    for line in fm_block.splitlines():
        m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip("'\"")
    return fm, body


def resolve_post(arg: str):
    """Return (title, date_str, url, slug, local_path_or_None)."""
    if arg.startswith("http"):
        url = arg
        slug = url.rstrip("/").split("/")[-1]
        return None, None, url, slug, None

    local = find_local_post(arg)
    if local is None:
        raise SystemExit(f"No post found matching {arg!r} in {config.POSTS_DIR}")

    fm, _ = parse_front_matter(local.read_text(encoding="utf-8"))
    permalink = fm.get("permalink", "")
    title = fm.get("title", local.stem)
    date_str = fm.get("date", "")
    slug = local.stem.split("-", 3)[-1]  # strip YYYY-MM-DD-
    if permalink:
        url = config.SITE_BASE + "/" + permalink.strip("/") + "/"
    else:
        url = config.SITE_BASE  # fallback; live fetch will still work if given
    return title, date_str, url, slug, local


# --------------------------------------------------------------------------- #
# Content rendering
# --------------------------------------------------------------------------- #
def rewrite_relative_urls(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(["a", "img"]):
        for attr in ("href", "src"):
            v = tag.get(attr)
            if v and v.startswith("/"):
                tag[attr] = HOST + v


def content_from_live(url: str) -> tuple[str, str, str]:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = ""
    og = soup.select_one('meta[property="og:title"]')
    if og:
        title = og.get("content", "")
    if not title:
        h1 = soup.select_one("h1.page__title")
        title = h1.get_text(strip=True) if h1 else ""

    date_str = ""
    t = soup.select_one('meta[property="article:published_time"]')
    if t:
        date_str = t.get("content", "")[:10]

    nodes = soup.select(".page__content")
    if not nodes:
        raise SystemExit(f"Could not find .page__content in {url}")
    content = max(nodes, key=lambda n: len(n.get_text()))
    for sel in STRIP_SELECTORS:
        for el in content.select(sel):
            el.decompose()
    rewrite_relative_urls(content)
    inner = content.decode_contents()
    return title, date_str, inner


def content_from_local(local: Path) -> str:
    import markdown
    fm, body = parse_front_matter(local.read_text(encoding="utf-8"))
    # Drop Liquid tags python-markdown can't handle.
    body = re.sub(r"\{%.*?%\}", "", body)
    body = re.sub(r"\{\{.*?\}\}", "", body)
    inner = markdown.markdown(body, extensions=["extra", "sane_lists", "smarty"])
    soup = BeautifulSoup(inner, "html.parser")
    rewrite_relative_urls(soup)
    return str(soup)


def pretty_date(date_str: str) -> str:
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).strftime("%B %-d, %Y")
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%B %-d, %Y")
    except ValueError:
        return date_str


def build_html(title: str, date_str: str, content_html: str, url: str, unsub_url: str) -> str:
    nice_date = pretty_date(date_str) if date_str else ""
    return f"""\
<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f4f2;">
<div style="max-width:640px;margin:0 auto;padding:24px 20px;background:#ffffff;
            font-family:Georgia,'Times New Roman',serif;color:#1a1a1a;line-height:1.6;">
  <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;font-size:12px;
              letter-spacing:.08em;text-transform:uppercase;color:#006BA2;">
    Southbound 35
  </div>
  <h1 style="font-size:24px;line-height:1.25;margin:8px 0 4px;">{html_lib.escape(title)}</h1>
  <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;font-size:13px;
              color:#777;margin-bottom:6px;">{nice_date}</div>
  <p style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;font-size:13px;margin:0 0 18px;">
    <a href="{url}" style="color:#006BA2;">Read this online</a>
  </p>
  <hr style="border:0;border-top:1px solid #e2e2e0;margin:0 0 22px;">
  <div style="font-size:17px;">
    {content_html}
  </div>
  <hr style="border:0;border-top:1px solid #e2e2e0;margin:28px 0 14px;">
  <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;font-size:12px;color:#888;">
    <p style="margin:0 0 8px;">You're receiving this because you subscribed to Southbound 35,
    a newsletter on public finance and economic development along the Texas I-35 corridor.</p>
    <p style="margin:0;"><a href="{unsub_url}" style="color:#888;">Unsubscribe</a>
    &nbsp;·&nbsp; Just reply to reach me directly.</p>
  </div>
</div>
</body></html>"""


def build_text(title: str, url: str, unsub_url: str) -> str:
    return (
        f"Southbound 35 — {title}\n\n"
        f"Read this post online:\n{url}\n\n"
        f"(This email's HTML version has the full text. If you only see this, "
        f"open the link above.)\n\n"
        f"---\nYou subscribed to Southbound 35. Unsubscribe: {unsub_url}\n"
        f"Or just reply to reach me directly.\n"
    )


# --------------------------------------------------------------------------- #
# Subscribers + sent log
# --------------------------------------------------------------------------- #
def load_subscribers() -> list[dict]:
    if not config.SUBSCRIBERS_CSV.exists():
        raise SystemExit(
            f"No subscriber list at {config.SUBSCRIBERS_CSV}. "
            f"Run: python3 -m mailer.sync_subscribers"
        )
    with config.SUBSCRIBERS_CSV.open(encoding="utf-8") as fh:
        return [row for row in csv.DictReader(fh) if row.get("email")]


def load_sent() -> dict:
    if config.SENT_LOG.exists():
        return json.loads(config.SENT_LOG.read_text())
    return {}


def save_sent(log: dict) -> None:
    config.SENT_LOG.write_text(json.dumps(log, indent=2))


# --------------------------------------------------------------------------- #
# Sending
# --------------------------------------------------------------------------- #
def make_message(to_email: str, subject: str, html_body: str, text_body: str, unsub_url: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr((config.FROM_NAME, config.FROM_EMAIL))
    msg["To"] = to_email
    msg["Reply-To"] = config.REPLY_TO
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    # One-click unsubscribe for Gmail/Apple Mail.
    msg["List-Unsubscribe"] = f"<{unsub_url}>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    return msg


def main() -> int:
    ap = argparse.ArgumentParser(description="Send a Southbound 35 post to subscribers.")
    ap.add_argument("post", help="slug, permalink path, full URL, or local .md path")
    ap.add_argument("--test", metavar="EMAIL", help="send only to this address; don't mark sent")
    ap.add_argument("--dry-run", action="store_true", help="render preview and exit")
    ap.add_argument("--resend", action="store_true", help="send even if already sent")
    ap.add_argument("--subject", help="override subject line")
    ap.add_argument("--local", action="store_true", help="render from local markdown")
    ap.add_argument("--limit", type=int, help="cap number of recipients")
    args = ap.parse_args()

    title, date_str, url, slug, local = resolve_post(args.post)

    if args.local:
        if local is None:
            raise SystemExit("--local needs a local post (give a slug or .md path).")
        content_html = content_from_local(local)
    else:
        live_title, live_date, content_html = content_from_live(url)
        title = title or live_title
        date_str = date_str or live_date

    subject = args.subject or title

    # --- dry run: render with a placeholder unsubscribe link and stop ---
    if args.dry_run:
        preview_unsub = config.unsubscribe_url("PREVIEW-TOKEN") if config.WORKER_BASE_URL else "#unsubscribe"
        html_body = build_html(title, date_str, content_html, url, preview_unsub)
        out = config.PREVIEW_DIR / f"{slug}.html"
        out.write_text(html_body, encoding="utf-8")
        subs = []
        try:
            subs = load_subscribers()
        except SystemExit:
            pass
        print(f"DRY RUN — wrote preview: {out}")
        print(f"Subject: {subject}")
        print(f"Would send to {len(subs)} subscriber(s).")
        return 0

    config.require_smtp()

    # --- recipients ---
    if args.test:
        recipients = [{"email": args.test, "token": "TEST-TOKEN"}]
    else:
        sent = load_sent()
        if slug in sent and not args.resend:
            raise SystemExit(
                f"Post {slug!r} already sent on {sent[slug].get('sent_at')}. "
                f"Use --resend to send again."
            )
        recipients = load_subscribers()
        if args.limit:
            recipients = recipients[: args.limit]
        if not recipients:
            raise SystemExit("No subscribers to send to.")

    print(f"Sending {subject!r} to {len(recipients)} recipient(s)...")
    sent_count = 0
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as s:
        s.starttls()
        s.login(config.SMTP_USER, config.SMTP_PASS)
        for i, sub in enumerate(recipients, 1):
            email = sub["email"]
            unsub = config.unsubscribe_url(sub.get("token", "")) if config.WORKER_BASE_URL else "#"
            html_body = build_html(title, date_str, content_html, url, unsub)
            text_body = build_text(title, url, unsub)
            msg = make_message(email, subject, html_body, text_body, unsub)
            try:
                s.send_message(msg)
                sent_count += 1
                print(f"  [{i}/{len(recipients)}] sent -> {email}")
            except Exception as e:  # noqa: BLE001
                print(f"  [{i}/{len(recipients)}] FAILED -> {email}: {e}")
            if i < len(recipients):
                time.sleep(config.SEND_THROTTLE_SEC)

    if not args.test:
        sent = load_sent()
        sent[slug] = {
            "title": title,
            "url": url,
            "sent_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "count": sent_count,
        }
        save_sent(sent)

    print(f"Done. Sent {sent_count}/{len(recipients)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
