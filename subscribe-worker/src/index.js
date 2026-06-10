/**
 * Southbound 35 — subscribe Worker
 *
 * Captures newsletter signups and stores them in a D1 database. It does NOT
 * send any email — all mail goes out from the operator's machine over SMTP.
 * The Worker only:
 *   POST /subscribe       capture a signup (with honeypot + optional Turnstile)
 *   GET  /unsubscribe     one-click unsubscribe via tokenised link
 *   GET  /export          dump the active list (admin-key protected) for the mailer
 *   GET  /                health check
 *
 * Bindings (see wrangler.toml):
 *   DB                D1 database
 * Vars:
 *   ALLOW_ORIGIN      e.g. https://scottlangford2.github.io
 * Secrets (wrangler secret put ...):
 *   ADMIN_KEY         required; gate for /export
 *   TURNSTILE_SECRET  optional; if set, /subscribe verifies the Turnstile token
 */

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function cors(env) {
  return {
    "Access-Control-Allow-Origin": env.ALLOW_ORIGIN || "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

function json(body, status, env) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...cors(env) },
  });
}

function html(body, status) {
  return new Response(body, {
    status,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}

async function readEmailAndHoneypot(request) {
  const ct = request.headers.get("content-type") || "";
  let email = "";
  let honeypot = "";
  let turnstile = "";
  if (ct.includes("application/json")) {
    const b = await request.json().catch(() => ({}));
    email = (b.email || "").toString();
    honeypot = (b.website || "").toString();
    turnstile = (b["cf-turnstile-response"] || b.turnstile || "").toString();
  } else {
    const f = await request.formData().catch(() => null);
    if (f) {
      email = (f.get("email") || "").toString();
      honeypot = (f.get("website") || "").toString();
      turnstile = (f.get("cf-turnstile-response") || "").toString();
    }
  }
  return { email: email.trim().toLowerCase(), honeypot, turnstile };
}

async function verifyTurnstile(secret, token, ip) {
  const form = new FormData();
  form.append("secret", secret);
  form.append("response", token || "");
  if (ip) form.append("remoteip", ip);
  const res = await fetch(
    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
    { method: "POST", body: form }
  );
  const data = await res.json().catch(() => ({ success: false }));
  return !!data.success;
}

async function handleSubscribe(request, env) {
  const { email, honeypot, turnstile } = await readEmailAndHoneypot(request);

  // Honeypot: a bot filled the hidden field. Pretend success, store nothing.
  if (honeypot) return json({ ok: true }, 200, env);

  if (!EMAIL_RE.test(email) || email.length > 254) {
    return json({ ok: false, error: "Please enter a valid email address." }, 400, env);
  }

  if (env.TURNSTILE_SECRET) {
    const ok = await verifyTurnstile(
      env.TURNSTILE_SECRET,
      turnstile,
      request.headers.get("CF-Connecting-IP")
    );
    if (!ok) {
      return json({ ok: false, error: "Verification failed. Please try again." }, 400, env);
    }
  }

  const now = new Date().toISOString();
  const token = crypto.randomUUID();

  // Insert, or reactivate a previously-unsubscribed address. An existing
  // active row is left untouched (idempotent re-signup).
  await env.DB.prepare(
    `INSERT INTO subscribers (email, status, token, source, created_at, updated_at)
     VALUES (?, 'active', ?, 'web', ?, ?)
     ON CONFLICT(email) DO UPDATE SET
       status     = 'active',
       updated_at = excluded.updated_at
     WHERE subscribers.status = 'unsubscribed'`
  )
    .bind(email, token, now, now)
    .run();

  return json({ ok: true }, 200, env);
}

async function handleUnsubscribe(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token") || "";
  const page = (msg) => html(
    `<!doctype html><html><head><meta charset="utf-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
     <title>Southbound 35</title>
     <style>body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:34em;
     margin:14vh auto;padding:0 1.2em;color:#222;line-height:1.5}
     h1{font-size:1.3em}a{color:#006BA2}</style></head>
     <body><h1>Southbound 35</h1><p>${msg}</p>
     <p><a href="https://scottlangford2.github.io/scott_langford/">Back to the site</a></p>
     </body></html>`,
    200
  );

  if (!token) return page("That unsubscribe link is missing its token.");

  const r = await env.DB.prepare(
    `UPDATE subscribers SET status='unsubscribed', updated_at=?
     WHERE token=? AND status='active'`
  )
    .bind(new Date().toISOString(), token)
    .run();

  if (r.meta && r.meta.changes > 0) {
    return page("You've been unsubscribed. You won't receive any more emails. Sorry to see you go.");
  }
  return page("You're already unsubscribed (or that link has expired). No further action needed.");
}

async function handleExport(request, env) {
  const url = new URL(request.url);
  const key = url.searchParams.get("key") || request.headers.get("X-Admin-Key") || "";
  if (!env.ADMIN_KEY || key !== env.ADMIN_KEY) {
    return json({ ok: false, error: "unauthorized" }, 401, env);
  }
  const { results } = await env.DB.prepare(
    `SELECT email, token, created_at FROM subscribers
     WHERE status='active' ORDER BY created_at ASC`
  ).all();
  return json({ ok: true, count: results.length, subscribers: results }, 200, env);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const { pathname } = url;

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(env) });
    }

    if (pathname === "/subscribe" && request.method === "POST") {
      return handleSubscribe(request, env);
    }
    if (pathname === "/unsubscribe" && request.method === "GET") {
      return handleUnsubscribe(request, env);
    }
    if (pathname === "/export" && request.method === "GET") {
      return handleExport(request, env);
    }
    if (pathname === "/" || pathname === "/health") {
      return new Response("Southbound 35 subscribe worker: ok\n", {
        status: 200,
        headers: { "Content-Type": "text/plain" },
      });
    }
    return new Response("Not found\n", { status: 404 });
  },
};
