// Cloudflare Worker — Southbound 35 subscribe endpoint.
//
// Routes:
//   POST /subscribe        — accept new subscription (sends confirmation
//                            email; notifies admin)
//   GET  /confirm?t=TOKEN  — confirm subscription (sets status=confirmed)
//   GET  /unsubscribe?t=T  — unsubscribe (sets status=unsubscribed)
//   GET  /subscribers      — admin-only list of confirmed subscribers
//                            (requires X-Admin-Token header)
//   GET  /health           — liveness check
//
// Storage: Cloudflare KV namespace SUBSCRIBERS.
//   key   = lowercased email address
//   value = JSON {token, status, subscribed_at, confirmed_at?, source?, name?}
//
// Email: Resend HTTP API. Notification + confirmation + unsubscribed.

export interface Env {
  SUBSCRIBERS: KVNamespace;
  RESEND_API_KEY: string;       // Secret
  NOTIFY_EMAIL: string;         // Secret  (e.g. scottlangford@txstate.edu)
  FROM_EMAIL: string;           // Var     (e.g. southbound35@resend.dev)
  ALLOWED_ORIGIN: string;       // Var     (e.g. https://scottlangford2.github.io)
  ADMIN_TOKEN: string;          // Secret  (random string; used to call /subscribers)
  WORKER_URL: string;           // Var     (https://subscribe.workers.dev)
}

interface SubscriberRecord {
  email: string;
  name?: string;
  token: string;
  status: 'pending' | 'confirmed' | 'unsubscribed';
  subscribed_at: string;        // ISO timestamp
  confirmed_at?: string;
  unsubscribed_at?: string;
  source?: string;              // e.g. 'subscribe-page', 'inline-cta'
  ip?: string;                  // first-seen IP, for rate-limit/abuse only
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '');  // strip trailing slash

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(env) });
    }

    try {
      if (request.method === 'POST' && path === '/subscribe') {
        return await handleSubscribe(request, env);
      }
      if (request.method === 'GET' && path === '/confirm') {
        return await handleConfirm(url, env);
      }
      if (request.method === 'GET' && path === '/unsubscribe') {
        return await handleUnsubscribe(url, env);
      }
      if (request.method === 'GET' && path === '/subscribers') {
        return await handleListSubscribers(request, env);
      }
      if (request.method === 'GET' && path === '/health') {
        return json({ ok: true }, env);
      }
      return new Response('Not found', { status: 404, headers: corsHeaders(env) });
    } catch (e) {
      console.error('worker error:', e);
      return json({ error: 'internal_error' }, env, 500);
    }
  },
} satisfies ExportedHandler<Env>;

// ---------- handlers ----------

async function handleSubscribe(request: Request, env: Env): Promise<Response> {
  let body: any;
  const ctype = request.headers.get('content-type') || '';
  if (ctype.includes('application/json')) {
    body = await request.json().catch(() => ({}));
  } else if (ctype.includes('application/x-www-form-urlencoded')) {
    const form = await request.formData();
    body = Object.fromEntries(form.entries());
  } else {
    return json({ error: 'unsupported_content_type' }, env, 400);
  }

  // Honeypot (form has a hidden 'website' input; bots fill it)
  if (body.website) {
    return json({ ok: true }, env);  // pretend success, drop quietly
  }

  const email = String(body.email || '').trim().toLowerCase();
  const name  = body.name ? String(body.name).trim().slice(0, 100) : undefined;
  const source = body.source ? String(body.source).slice(0, 50) : 'subscribe-page';

  if (!isValidEmail(email)) {
    return json({ error: 'invalid_email' }, env, 400);
  }

  const ip = request.headers.get('CF-Connecting-IP') || undefined;

  // Lookup existing
  const existingRaw = await env.SUBSCRIBERS.get(email);
  const existing: SubscriberRecord | null = existingRaw ? JSON.parse(existingRaw) : null;

  // Already confirmed: idempotent success, no second confirmation email
  if (existing && existing.status === 'confirmed') {
    return json({ ok: true, already_confirmed: true }, env);
  }

  // Already pending: resend the confirmation email (don't re-notify admin)
  if (existing && existing.status === 'pending') {
    await sendConfirmationEmail(env, existing);
    return json({ ok: true, resent: true }, env);
  }

  // Previously unsubscribed: revive as pending (require re-confirmation)
  // OR brand new: create
  const token = generateToken();
  const record: SubscriberRecord = {
    email,
    name,
    token,
    status: 'pending',
    subscribed_at: new Date().toISOString(),
    source,
    ip,
  };
  await env.SUBSCRIBERS.put(email, JSON.stringify(record));

  await Promise.all([
    sendConfirmationEmail(env, record),
    sendAdminNotification(env, record, 'new'),
  ]);

  return json({ ok: true, pending: true }, env);
}

async function handleConfirm(url: URL, env: Env): Promise<Response> {
  const token = url.searchParams.get('t');
  const email = url.searchParams.get('e');
  if (!token || !email) return htmlPage('Missing token', 'The confirmation link is incomplete.', env);

  const raw = await env.SUBSCRIBERS.get(email.toLowerCase());
  if (!raw) return htmlPage('Not found', 'No pending subscription was found for that address.', env);

  const record: SubscriberRecord = JSON.parse(raw);
  if (record.token !== token) {
    return htmlPage('Invalid token', 'That confirmation link is not valid.', env);
  }
  if (record.status === 'confirmed') {
    return htmlPage('Already confirmed', 'Your subscription was already confirmed. Thanks for reading.', env);
  }
  record.status = 'confirmed';
  record.confirmed_at = new Date().toISOString();
  await env.SUBSCRIBERS.put(email.toLowerCase(), JSON.stringify(record));

  await sendAdminNotification(env, record, 'confirmed');

  return htmlPage(
    'Subscription confirmed',
    'You are now on the Southbound 35 list. New posts go out Monday mornings at 5 AM Central. To unsubscribe at any time, reply to any post email with the word "unsubscribe".',
    env,
  );
}

async function handleUnsubscribe(url: URL, env: Env): Promise<Response> {
  const token = url.searchParams.get('t');
  const email = url.searchParams.get('e');
  if (!token || !email) return htmlPage('Missing token', 'The unsubscribe link is incomplete.', env);

  const raw = await env.SUBSCRIBERS.get(email.toLowerCase());
  if (!raw) return htmlPage('Not found', 'No subscription was found for that address.', env);

  const record: SubscriberRecord = JSON.parse(raw);
  if (record.token !== token) {
    return htmlPage('Invalid token', 'That unsubscribe link is not valid.', env);
  }
  record.status = 'unsubscribed';
  record.unsubscribed_at = new Date().toISOString();
  await env.SUBSCRIBERS.put(email.toLowerCase(), JSON.stringify(record));

  await sendAdminNotification(env, record, 'unsubscribed');
  return htmlPage('Unsubscribed', 'You have been removed from the Southbound 35 list. No further emails will be sent.', env);
}

async function handleListSubscribers(request: Request, env: Env): Promise<Response> {
  const auth = request.headers.get('X-Admin-Token');
  if (!auth || auth !== env.ADMIN_TOKEN) {
    return json({ error: 'unauthorized' }, env, 401);
  }
  // Stream all keys (KV list returns up to 1000 per call; paginate if needed)
  const subs: SubscriberRecord[] = [];
  let cursor: string | undefined;
  do {
    const page = await env.SUBSCRIBERS.list({ cursor });
    for (const key of page.keys) {
      const raw = await env.SUBSCRIBERS.get(key.name);
      if (raw) {
        const rec: SubscriberRecord = JSON.parse(raw);
        if (rec.status === 'confirmed') subs.push(rec);
      }
    }
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);

  return json({ count: subs.length, subscribers: subs }, env);
}

// ---------- email senders ----------

async function sendConfirmationEmail(env: Env, rec: SubscriberRecord): Promise<void> {
  const confirmUrl = `${env.WORKER_URL}/confirm?t=${rec.token}&e=${encodeURIComponent(rec.email)}`;
  const html = `
    <p>Thanks for subscribing to Southbound 35.</p>
    <p>To confirm your subscription, click the link below:</p>
    <p><a href="${confirmUrl}">Confirm my subscription</a></p>
    <p>If you did not request this, no action is needed and you can ignore the email.</p>
    <p>— Scott</p>
  `;
  const text = `Thanks for subscribing to Southbound 35.

To confirm your subscription, open this link in your browser:
${confirmUrl}

If you did not request this, no action is needed.
— Scott`;

  await resendSend(env, {
    to: rec.email,
    subject: 'Confirm your Southbound 35 subscription',
    html,
    text,
  });
}

async function sendAdminNotification(
  env: Env,
  rec: SubscriberRecord,
  kind: 'new' | 'confirmed' | 'unsubscribed',
): Promise<void> {
  const subjectMap = {
    new: `[Southbound 35] new pending: ${rec.email}`,
    confirmed: `[Southbound 35] confirmed: ${rec.email}`,
    unsubscribed: `[Southbound 35] unsubscribed: ${rec.email}`,
  };
  const lines = [
    `email: ${rec.email}`,
    rec.name ? `name: ${rec.name}` : '',
    `status: ${rec.status}`,
    `subscribed_at: ${rec.subscribed_at}`,
    rec.confirmed_at ? `confirmed_at: ${rec.confirmed_at}` : '',
    rec.unsubscribed_at ? `unsubscribed_at: ${rec.unsubscribed_at}` : '',
    rec.source ? `source: ${rec.source}` : '',
    rec.ip ? `ip: ${rec.ip}` : '',
  ].filter(Boolean);

  await resendSend(env, {
    to: env.NOTIFY_EMAIL,
    subject: subjectMap[kind],
    text: lines.join('\n'),
    html: `<pre style="font-family: monospace">${lines.join('\n')}</pre>`,
  });
}

interface ResendMsg { to: string; subject: string; text: string; html: string; }

async function resendSend(env: Env, msg: ResendMsg): Promise<void> {
  const resp = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: env.FROM_EMAIL,
      to: msg.to,
      subject: msg.subject,
      html: msg.html,
      text: msg.text,
    }),
  });
  if (!resp.ok) {
    const body = await resp.text();
    console.error('resend send failed', resp.status, body);
    throw new Error(`resend ${resp.status}: ${body}`);
  }
}

// ---------- helpers ----------

function corsHeaders(env: Env): HeadersInit {
  return {
    'Access-Control-Allow-Origin': env.ALLOWED_ORIGIN,
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Admin-Token',
    'Access-Control-Max-Age': '86400',
  };
}

function json(body: unknown, env: Env, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(env),
    },
  });
}

function htmlPage(title: string, body: string, env: Env): Response {
  const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title} — Southbound 35</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;700&family=DM+Sans:wght@500;600&display=swap">
  <style>
    body { font-family: 'Spectral', Georgia, serif; background: #faf8f5; color: #1a1a1a;
           max-width: 560px; margin: 6rem auto; padding: 0 1.5rem; line-height: 1.6; }
    h1 { font-family: 'Spectral', Georgia, serif; font-weight: 700; font-size: 1.8rem;
         border-top: 1px solid #d6d6d2; padding-top: 1rem; }
    h1::before { content: ""; display: inline-block; width: 8px; height: 8px;
                 background: #D7BD8A; border-radius: 50%; margin-right: 0.6rem;
                 vertical-align: middle; }
    a { color: #501214; }
    .brand { font-family: 'DM Sans', sans-serif; font-size: 0.78rem;
             text-transform: uppercase; letter-spacing: 0.14em; color: #555; }
  </style>
</head>
<body>
  <p class="brand">Southbound 35</p>
  <h1>${title}</h1>
  <p>${body}</p>
  <p><a href="${env.ALLOWED_ORIGIN}/scott_langford/">← back to the site</a></p>
</body>
</html>`;
  return new Response(html, {
    status: 200,
    headers: { 'Content-Type': 'text/html; charset=utf-8' },
  });
}

function isValidEmail(email: string): boolean {
  if (!email || email.length > 254) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function generateToken(): string {
  const bytes = new Uint8Array(24);
  crypto.getRandomValues(bytes);
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}
