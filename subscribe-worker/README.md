# Southbound 35 — subscribe Worker

A tiny Cloudflare Worker that captures newsletter signups into a D1 database.
It **does not send any email**. All mail goes out from the operator's machine
over SMTP (see `../mailer/`). The Worker's only jobs:

| Route             | Method | Purpose                                              |
|-------------------|--------|------------------------------------------------------|
| `/subscribe`      | POST   | Capture a signup (honeypot + optional Turnstile)     |
| `/unsubscribe`    | GET    | One-click unsubscribe via tokenised link in emails   |
| `/export`         | GET    | Dump the active list as JSON (admin-key protected)   |
| `/` `/health`     | GET    | Health check                                         |

## Deployed instance

- URL: `https://southbound35-subscribe.southbound35.workers.dev`
- D1 database: `southbound35-subscribers`
- Account: scottlangford2@gmail.com

## One-time deploy (already done; for reference / re-deploy)

From this directory:

```bash
npm install                       # installs wrangler locally
npx wrangler login                # opens browser, authenticate to Cloudflare

# 1. Create the D1 database, then paste the printed database_id into wrangler.toml
npx wrangler d1 create southbound35-subscribers

# 2. Create the table (remote)
npm run schema

# 3. Set the admin key the mailer uses to pull the list.
npx wrangler secret put ADMIN_KEY

# 4. Deploy
npm run deploy
```

The Worker URL is wired into two places:

- the signup form on the blog (`scott_langford/_pages/subscribe.md`, `WORKER_URL`)
- the mailer's `.env` (`WORKER_BASE_URL`) at `~/lookout_local/southbound35/.env`

## Optional: Turnstile (bot protection)

The form works without it (honeypot only). To add Cloudflare's free CAPTCHA:

1. Cloudflare dashboard → Turnstile → add a widget for `scottlangford2.github.io`.
2. Put the **site key** into `subscribe.md` (`TURNSTILE_SITEKEY`) and uncomment
   the widget `<div>` + script.
3. Set the **secret key** on the Worker: `npx wrangler secret put TURNSTILE_SECRET`.

When `TURNSTILE_SECRET` is set, `/subscribe` verifies every token server-side.

## Quick checks

```bash
WORKER=https://southbound35-subscribe.southbound35.workers.dev
curl "$WORKER/"                                            # health
curl -X POST "$WORKER/subscribe" -H 'Content-Type: application/json' \
  -d '{"email":"you+test@example.com"}'                    # a test signup
curl "$WORKER/export?key=YOUR_ADMIN_KEY"                   # read the list back
```

## Inspecting / editing the list directly

```bash
npx wrangler d1 execute southbound35-subscribers --remote \
  --command "SELECT email,status,created_at FROM subscribers ORDER BY created_at"
```

Subscriber emails live only in D1 (Cloudflare) and in the off-repo CSV the
mailer syncs to `~/lookout_local/southbound35/`. They are never committed to
this public repo.
