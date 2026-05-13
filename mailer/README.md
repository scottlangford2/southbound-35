# Southbound 35 — Mailer

Self-hosted, hand-managed mailing list for the Southbound 35 blog. Sends each post as an **individual email** to every active subscriber — no third-party newsletter service between you and your readers.

## What it does

- Reads `subscribers.csv` (kept locally, never committed)
- Parses the latest Jekyll post by slug
- Sends one personalized email per subscriber via SMTP
- Throttles between sends to stay under SMTP rate limits

Suitable up to a few hundred subscribers. Past that, migrate to a hosted service.

## One-time setup (on the machine that will actually send)

The recommended setup is your desktop — the machine you use for blog work. Once configured, sending a post is one command.

### Quick setup

```bash
# Clone the repo (if you don't already have it)
git clone https://github.com/scottlangford2/southbound-35.git
cd southbound-35/mailer

# Run the setup script — creates a virtualenv, installs deps,
# and copies the .env and subscribers.csv templates.
bash setup.sh
```

The script prints next-step instructions at the end.

### Manual setup (if you skip setup.sh)

1. **Install dependencies**
   ```bash
   cd mailer
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create a Gmail App Password** at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords). You need 2-step verification enabled on the account.

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env — fill in SMTP_USER and SMTP_APP_PASSWORD
   ```

4. **Create the subscribers list**
   ```bash
   cp subscribers.csv.example subscribers.csv
   # Edit subscribers.csv — replace example entries with real ones
   ```

`.env` and `subscribers.csv` are both in `.gitignore` and will never be committed.

## Sending a post

```bash
# Dry run — prints what would happen without sending
python send_post.py --post 2026-05-25-hays-county-governance --dry-run

# Real send to all active subscribers
python send_post.py --post 2026-05-25-hays-county-governance

# Test send to one address (yourself)
python send_post.py --post 2026-05-25-hays-county-governance \
    --only you@example.com
```

The `--post` argument is the Jekyll post slug — typically the `_posts/` filename without `.md`. The script will also accept a partial slug if it uniquely matches one post.

## Managing the list

- **New subscriber**: open `subscribers.csv` and add a row.
- **Unsubscribe**: change the row's `status` from `active` to `unsubscribed`. Don't delete — keeping the row prevents accidental re-adds and provides an audit trail.
- The CSV is human-editable. Sort it however you like.

## Email format

Each subscriber gets:
- A personalized greeting (`Hi {first-name},`)
- The post title as the subject line
- The first paragraph as the email body excerpt
- A "Read the full post →" button linking to the live URL
- A clear unsubscribe instruction at the bottom

Both plain-text and HTML versions are generated; the recipient's mail client picks whichever it prefers.

## Sending limits and deliverability

- **Gmail SMTP**: hard limit of ~500 outbound messages per 24 hours for personal accounts, ~2,000 for Workspace. The script throttles by default at 2 seconds between sends; adjust `THROTTLE_SECONDS` in `.env`.
- **Deliverability**: sending from a Gmail account using a real human's identity is reasonably reliable for small lists. If recipients start reporting messages going to spam, set up [SPF/DKIM for your domain](https://support.google.com/a/answer/33786) and send from a custom address.
- **Per-recipient send**: the script uses `server.sendmail()` with a single recipient per call. Each subscriber receives an email addressed only to them — no BCC, no list disclosure.

## Files

| File | Description |
|------|-------------|
| `send_post.py` | The mailer script |
| `requirements.txt` | Python dependencies (just PyYAML) |
| `.env.example` | Template for SMTP credentials and paths |
| `subscribers.csv.example` | Template for the list |
| `.env` | (not committed) Real SMTP credentials |
| `subscribers.csv` | (not committed) Real subscriber list |

## Why hand-managed

For a blog at this size, a hosted service costs $9/mo and adds a vendor between you and your readers. A self-managed list costs nothing, exposes the subscriber's email to no third party, and forces you to know who your readers are. Migrate when the list outgrows the workflow — not before.
