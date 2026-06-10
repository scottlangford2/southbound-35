-- Southbound 35 subscriber list (Cloudflare D1 / SQLite)
CREATE TABLE IF NOT EXISTS subscribers (
  email      TEXT PRIMARY KEY,
  status     TEXT NOT NULL DEFAULT 'active',   -- 'active' | 'unsubscribed'
  token      TEXT NOT NULL,                    -- per-subscriber unsubscribe token
  source     TEXT,                             -- where the signup came from
  created_at TEXT NOT NULL,                    -- ISO-8601 UTC
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);
