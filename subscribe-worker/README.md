# Southbound 35 — subscribe Cloudflare Worker

Self-hosted newsletter signup. Replaces the manual `mailto:` link on
`/subscribe/` with an automated double-opt-in form. Per-subscribe
notifications go to `NOTIFY_EMAIL`.

## Architecture

```
  ┌──────────────────┐    POST /subscribe        ┌──────────────────┐
  │  /subscribe/     │ ─────────────────────────▶│ Cloudflare       │
  │  page on the     │                            │ Worker           │
  │  Jekyll site     │ ◀───────────────────────── │ + KV namespace   │
  └──────────────────┘    JSON response           └──────────────────┘
                                                          │
                                ┌─────────────────────────┤
                                ▼                         ▼
                          ┌──────────┐              ┌──────────┐
                          │  Resend  │              │  Resend  │
                          │  to user │              │  to you  │
                          │  (confirm)│              │ (notify) │
                          └──────────┘              └──────────┘
```

Storage: Cloudflare KV. Key = lowercased email; value = JSON
`{token, status, subscribed_at, ...}`. Status is one of `pending`,
`confirmed`, or `unsubscribed`.

## Setup (one-time, ~30 minutes)

### 1. Cloudflare account

1. Create a free account at https://dash.cloudflare.com/sign-up
2. Install wrangler CLI:
   ```bash
   npm install -g wrangler
   wrangler login
   ```

### 2. Resend account

1. Sign up at https://resend.com (free tier: 3,000 emails/month, 100/day)
2. From the dashboard, copy your API key (starts with `re_...`)
3. For initial testing you can send from the sandbox address
   `onboarding@resend.dev`. For production you'll want a verified
   sending domain (see step 6).

### 3. Create the KV namespace

```bash
cd subscribe-worker
wrangler kv namespace create SUBSCRIBERS
```

This prints a namespace `id`. Paste it into `wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "SUBSCRIBERS"
id = "PASTE_HERE"
```

### 4. Set secrets

```bash
wrangler secret put RESEND_API_KEY    # paste your re_... key
wrangler secret put NOTIFY_EMAIL      # e.g. scottlangford@txstate.edu
wrangler secret put ADMIN_TOKEN       # any random string; the mailer
                                       # uses this to list subscribers
```

Generate a strong ADMIN_TOKEN:
```bash
openssl rand -hex 32
```

### 5. Deploy

```bash
wrangler deploy
```

Cloudflare prints the Worker URL, e.g.
`https://southbound-35-subscribe.YOUR-SUBDOMAIN.workers.dev`.

Take that URL and:

- Paste into `wrangler.toml` under `[vars] WORKER_URL`
- Paste into `_pages/subscribe.md` in the `window.SB35_WORKER_URL`
  line
- Redeploy: `wrangler deploy`

### 6. (Optional but recommended) Verify a custom sending domain in Resend

Sending from `onboarding@resend.dev` works for testing but most
mailbox providers will mark those messages as spam. To send from
your own address (e.g. `scott@scottlangford.com`):

1. In Resend → Domains → Add Domain
2. Add the DNS records Resend shows (SPF, DKIM, MX, return-path)
   to your domain registrar
3. Wait for verification (usually <1 hour)
4. Update `FROM_EMAIL` in `wrangler.toml` to use the verified
   address, and `wrangler deploy`

### 7. Sanity-check

```bash
# Should return {"ok": true}
curl https://southbound-35-subscribe.YOUR-SUBDOMAIN.workers.dev/health

# Test subscribe (use a real email; you'll get a confirmation link)
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"you@yourdomain.com"}' \
  https://southbound-35-subscribe.YOUR-SUBDOMAIN.workers.dev/subscribe
```

You should:
- Get `{"ok": true, "pending": true}` from the curl
- Receive a confirmation email at the address you subscribed
- Receive a notification email at `NOTIFY_EMAIL`

## API

| Method | Path | Body / params | Description |
|---|---|---|---|
| POST | `/subscribe` | `{email, name?, source?}` | Subscribe a new email. Sends confirmation. Notifies admin. |
| GET  | `/confirm` | `?t=TOKEN&e=EMAIL` | Confirm pending subscription. Returns HTML success page. |
| GET  | `/unsubscribe` | `?t=TOKEN&e=EMAIL` | Unsubscribe. Returns HTML page. |
| GET  | `/subscribers` | header `X-Admin-Token: ADMIN_TOKEN` | List confirmed subscribers (JSON). Used by the mailer. |
| GET  | `/health` | — | Liveness check. |

## Mailer integration

The existing Python mailer (`southbound-35/mailer/send_post.py`)
previously read subscribers from a flat file. Updated version pulls
from the Worker's `/subscribers` endpoint. See
`../mailer/README.md` for the changes.

Set env vars in the mailer's `.env`:
```
SB35_WORKER_URL=https://southbound-35-subscribe.YOUR-SUBDOMAIN.workers.dev
SB35_ADMIN_TOKEN=the-token-you-set-above
```

## Notes

- **Honeypot.** The form has a hidden `website` field. Bots fill
  it; humans don't. Submissions with `website` set are silently
  dropped (returns `ok` to avoid telling the bot it was caught).
- **Idempotency.** Submitting the same email twice while pending
  re-sends the confirmation; the admin notification only fires
  once (on first submission and on confirmation).
- **Rate limiting.** Cloudflare's default DDoS protection covers
  basic abuse. For heavier protection add a Cloudflare Rate
  Limiting rule on `/subscribe` (1 request per IP per minute is
  reasonable).
- **CORS.** The Worker only accepts POSTs from `ALLOWED_ORIGIN`
  (set to `https://scottlangford2.github.io`). Update if you move
  to a custom domain.
- **Per-view notifications.** Not handled here. Enable Plausible's
  weekly email reports from Plausible → Settings → Notifications.

## Files

- `src/worker.ts` — Worker source
- `wrangler.toml` — Cloudflare config (KV bindings, env vars)
- `package.json` — npm scripts (deploy, dev, tail logs, list subs)
- `tsconfig.json` — TypeScript config

## Cost

- Cloudflare Workers free tier: 100,000 requests/day, 30s CPU/day.
  Plenty for a subscribe form.
- Cloudflare KV free tier: 100,000 reads/day, 1,000 writes/day,
  1 GB storage. Plenty.
- Resend free tier: 3,000 emails/month, 100/day. Enough for the
  notification + confirmation flow on a small list; if the list
  grows to ~1,000+ active subscribers, upgrade to $20/mo for 50K
  emails.
