# Southbound 35 — mailer

Sends each published post to the subscriber list, one personal email per
recipient (not a BCC blast), from this machine over the existing
lookoutanalytics SMTP creds. Pairs with `../subscribe-worker/`, which captures
signups; this side pulls that list and does the sending.

## Layout

```
mailer/
├── config.py            paths, SMTP + Worker config (reads two .env files)
├── sync_subscribers.py  pull active list from the Worker  -> local CSV
└── send_post.py         render a post and send it to subscribers
```

Private runtime data (never in this public repo) lives in
`~/lookout_local/southbound35/`:

```
.env              Worker URL + admin key + From/Reply-To overrides
subscribers.csv   synced list (email, token, created_at)
sent.json         which post slugs have gone out
preview/          --dry-run output
logs/
```

## Setup (one time)

1. SMTP creds are already shared from `~/lookout_local/research_scraper/.env`
   (`SMTP_USER`, `SMTP_PASS`, etc.) — the same ones the digests use. Nothing to do.

2. `~/lookout_local/southbound35/.env` holds the Worker config:

   ```ini
   WORKER_BASE_URL=https://southbound35-subscribe.southbound35.workers.dev
   ADMIN_KEY=<the same long string set as the Worker secret>
   # optional overrides:
   # NEWSLETTER_FROM=you@yourdomain
   # NEWSLETTER_FROM_NAME=Scott Langford
   # NEWSLETTER_REPLY_TO=scottlangford@txstate.edu
   ```

3. Install deps (most are already present):

   ```bash
   pip3 install -r ~/southbound-35/mailer/requirements.txt
   ```

## Usage

Run from the repo root so the package imports resolve:

```bash
cd ~/southbound-35

# 1. Pull the latest list
python3 -m mailer.sync_subscribers

# 2. Preview an email without sending (writes preview/<slug>.html)
python3 -m mailer.send_post hays-county-governance --dry-run

# 3. Send a test only to yourself
python3 -m mailer.send_post hays-county-governance --test you@example.com

# 4. Send to everyone
python3 -m mailer.send_post hays-county-governance
```

`post` can be a slug (`hays-county-governance`), a permalink path, a full URL,
or a local `.md` path. By default the email body is pulled from the **published**
live page so it matches the site; use `--local` to render an unpublished draft
from its markdown instead.

Re-sending the same post is blocked unless you pass `--resend` (guards against
double-sends). Sends are throttled (~1.5s apart) to stay under SMTP limits.

## Subscriber-change notifications

`notify_new_subscribers.py` emails you whenever someone joins **or leaves**. It
polls the Worker's `/export`, compares against a stored snapshot of the
last-seen active list (`subscriber_state.json`), and emails a summary of
additions (new subscribers) and departures (unsubscribes) over SMTP to
`NOTIFY_TO` (defaults to your address). First run seeds a silent baseline so an
existing list doesn't all arrive as "new".

```bash
python3 -m mailer.notify_new_subscribers --dry-run          # preview
python3 -m mailer.notify_new_subscribers --include-existing # email about current list too
```

It runs automatically every 15 minutes via launchd. To (re)install:

```bash
cp mailer/com.langfordlab.southbound35.subscriber-notify.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.langfordlab.southbound35.subscriber-notify.plist
```

Logs: `~/lookout_local/southbound35/logs/notify.{out,err}.log`.

## Typical Monday flow

```bash
cd ~/southbound-35
python3 -m mailer.sync_subscribers
python3 -m mailer.send_post <this-week-slug> --dry-run    # eyeball it
python3 -m mailer.send_post <this-week-slug> --test you@example.com
python3 -m mailer.send_post <this-week-slug>              # ship it
```
