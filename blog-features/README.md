# Blog Features — Drafts

Drafts for two features to add to the blog at
[`scottlangford2/scott_langford`](https://github.com/scottlangford2/scott_langford):

1. **Page-view counter** (GoatCounter, cookieless, privacy-friendly)
2. **Comments section** (giscus, powered by GitHub Discussions)

They're staged here in `southbound-35` because my GitHub tools don't
currently have write access to the blog repo — the files in this folder
mirror the paths they should land at in the blog repo.

## What's in here

```
blog-features/
├── _config.additions.yml                      → merge into scott_langford/_config.yml
├── _includes/
│   ├── analytics-providers/custom.html        → scott_langford/_includes/analytics-providers/custom.html
│   ├── comments-providers/custom.html         → scott_langford/_includes/comments-providers/custom.html
│   └── view-count.html                        → scott_langford/_includes/view-count.html
└── _layouts/
    └── single.html.patch                      → instructions only; apply to scott_langford/_layouts/single.html
```

All four new files slot into the theme's existing provider architecture
(academicpages / minimal-mistakes). No upstream theme files are modified;
only `_config.yml` and (optionally, for the per-page view badge)
`_layouts/single.html`.

## One-time setup on the blog repo

### 1. giscus (comments)

1. **Enable Discussions** on `scottlangford2/scott_langford`:
   *Settings → General → Features → check "Discussions".*
2. **Install the giscus app** on the repo: <https://github.com/apps/giscus>.
   (The app is open-source and stores nothing — the Discussions themselves
   are the data.)
3. **Create a discussion category** to hold blog comments — e.g.
   `Blog Comments`, announcement-only so random users can't start threads
   without a post.
4. **Get config values**: visit <https://giscus.app>, paste in your repo,
   pick the category and mapping (`pathname` is standard), and copy the
   `data-repo-id` and `data-category-id` values it prints.
5. Paste those into `giscus:` in `_config.yml` (see `_config.additions.yml`).

### 2. GoatCounter (view counter)

1. Register at <https://www.goatcounter.com> and create a site. Pick a
   short code like `southbound35` — your dashboard lives at
   `https://southbound35.goatcounter.com`.
2. Paste that code into `goatcounter.code` in `_config.yml`.
3. **Only if you want the inline per-page view badge** (from
   `view-count.html`): in GoatCounter → Site settings, enable
   *"Allow public access to site statistics"*. The tracking itself works
   either way; this just unlocks the read-side JSON endpoint the badge
   needs.

## Files

### `_includes/analytics-providers/custom.html`
The theme already routes `analytics.provider: custom` to this path. The
file emits the GoatCounter tracking `<script>`. Hits are recorded the
moment this ships.

### `_includes/comments-providers/custom.html`
The theme already routes `comments.provider: custom` to this path. The
file emits the giscus client `<script>` with config values read from
`_config.yml`. giscus handles the rest — new posts get a new Discussion
on first comment.

### `_includes/view-count.html`
Inline `<span>` that fetches the current page's hit count from
GoatCounter's JSON counter API and renders it as a small badge. Hides
itself silently if the API is unreachable (e.g. public stats not yet
enabled) so pages don't show a broken `…`.

Include it from whichever layout block should display the count — the
patch file suggests next to the read-time include in
`_layouts/single.html`.

### `_layouts/single.html.patch`
Context-only instructions for where to inject `view-count.html`. Not a
real `git apply` patch — the surrounding lines will vary by theme
version, so the file describes what to search for and what to add.

### `_config.additions.yml`
YAML snippet to merge into the blog's `_config.yml`. It overwrites the
existing `comments: false` / `analytics: false` keys with provider
`custom` and adds the `giscus:` and `goatcounter:` blocks. Placeholder
values are marked `REPLACE_ME`.

## What this does NOT do

- **No backfill of historical views.** GoatCounter starts counting the
  moment the tracking script ships. There's no way to retroactively
  populate pre-launch numbers.
- **No migration of old comments.** If there were prior comments on
  another platform (Disqus, Staticman), they stay there — giscus starts
  fresh.
- **No automatic handling of the first visit to each post.** giscus
  creates a Discussion on the first comment, not on the first page view.
  That's the standard behavior.

## Open questions

- Is `preferred_color_scheme` the right giscus theme? Academicpages
  currently doesn't expose a dark mode, so `light` would be a safer
  fixed choice. Happy to change — it's one line in `_config.yml`.
- Should comments render on all pages, or only on blog posts (not on
  Teaching / Research / CV collections)? The theme's `page.comments`
  front-matter flag already handles per-page opt-out; I'd suggest
  setting `comments: true` in `_config.yml`'s `defaults:` only for
  `type: posts`, and leaving other collections alone. Let me know and
  I'll add that block.
