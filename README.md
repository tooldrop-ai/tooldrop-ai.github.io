# ToolDrop

A fast, static, installable directory of AI tools — plain HTML/CSS/JS, hosted free on GitHub Pages.
Live: https://tooldrop-ai.github.io/

## Features
- Pre-rendered home, 10 category pages and one page per tool (`tool/<slug>.html`) with alternatives — all crawlable without JS
- Instant filter, category chips, pricing filter, sort (A–Z / newest), shareable URLs (`?q=&cat=&price=&sort=&view=stack`)
- `Ctrl/⌘ K` (or `/`) command-palette search, Random tool, favorites ("My stack", saved in localStorage)
- Dark/light theme (remembers choice, respects `prefers-color-scheme`), scroll reveals, `prefers-reduced-motion` respected
- Self-hosted Inter font (OFL) and tool logos — no third-party requests from visitors
- SEO: canonical, Open Graph/Twitter cards, JSON-LD (WebSite, ItemList, BreadcrumbList, SoftwareApplication), sitemap, RSS
- PWA: manifest + service worker (offline page, cached pages/assets)

## Daily update (5 minutes)
```bash
python3 scripts/add_tool.py "Name" "https://official.url/" "One-line description." "Coding" freemium   # repeat per tool
# optional: add the tool to a guide in content/guides.json, bump "guides_updated" in config.json when you revise guides
python3 scripts/build.py && python3 scripts/audit.py
git add -A && git commit -m "Add Name" && git push
# wait ~1 minute for Pages to deploy, then tell search engines:
python3 scripts/ping_indexnow.py --changed      # or without --changed to resubmit every URL (fine weekly)
```
`add_tool.py` checks the URL, rejects duplicates, sets `date_added` to today, fetches the logo and rebuilds:
the home page, tool/category/alternatives/free pages, the weekly Drop archive, sitemap (with lastmod) and RSS all refresh.
`audit.py` fails on titles over 60 chars, missing/duplicate h1, broken internal links, invalid JSON-LD or sitemap gaps.
Pricing: `free` | `freemium` | `paid`. Tools added within 7 days of the newest entry get a "New" badge.

## Guides
`content/guides.json` holds hand-written buying guides (picks with "best for", "why", "keep in mind", how-to-choose tips, FAQs).
They render to `guides/<slug>.html` with Article, ItemList, FAQPage and BreadcrumbList schema. Keep them honest:
only list tools that are on ToolDrop, describe real features, and update the date only when you actually review a guide.

## Search engines
- `config.json`: `google_site_verification` / `bing_site_verification` → paste the token, run `build.py`, push. The meta tag appears on every page.
- `indexnow_key` → published as `/<key>.txt`; `scripts/ping_indexnow.py` notifies Bing, Yandex and others.

## Affiliate links
Paste approved links with `python3 scripts/set_affiliate.py <slug> <url>` (or edit `affiliates.json`, then build).
A tool can also carry `"affiliate_url"` in `tools.json`. When set, Visit buttons use it with `rel="sponsored noopener"`;
otherwise the official URL is used. The disclosure (footer + `/disclosure.html`) is always on. See `AFFILIATES.md`.

## Files
- `tools.json` — source of truth · `style.css`, `app.js` — hand-written
- `scripts/build.py` — generates `index.html`, `category/`, `tool/`, `alternatives/`, `best/`, `guides/`, `drops/`, `badge.html`, `advertise.html`, `disclosure.html`, `404.html`, `offline.html`, `sitemap.xml`, `feed.xml`, `robots.txt`, `manifest.webmanifest`, `sw.js` (don't edit those by hand)
- `scripts/fetch_logos.py` — downloads favicons once into `assets/logos/` (monogram fallback; `--force` to refresh)
- `.github/ISSUE_TEMPLATE/` — tool submissions and sponsor inquiries (the site's forms open pre-filled issues)

## Local preview
`python3 -m http.server 8000` → http://localhost:8000/ (paths are root-absolute).

## Deploy
Push to `main`; Pages serves `main` / root (`.nojekyll` included). Asset URLs are cache-busted automatically.
For another domain/repo, edit `SITE`, `BASE`, `REPO` at the top of `scripts/build.py`.
