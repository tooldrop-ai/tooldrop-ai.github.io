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

## Add a tool (daily update)
```bash
python3 scripts/add_tool.py "Name" "https://official.url/" "One-line description." "Coding" freemium
git add -A && git commit -m "Add Name" && git push
```
Checks the URL, rejects duplicates, sets `date_added` to today, fetches the logo, rebuilds everything.
Or edit `tools.json` by hand, then `python3 scripts/fetch_logos.py && python3 scripts/build.py`.
Pricing: `free` | `freemium` | `paid`. Tools added within 7 days of the newest entry get a "New" badge.

## Files
- `tools.json` — source of truth · `style.css`, `app.js` — hand-written
- `scripts/build.py` — generates `index.html`, `category/`, `tool/`, `advertise.html`, `404.html`, `offline.html`, `sitemap.xml`, `feed.xml`, `robots.txt`, `manifest.webmanifest`, `sw.js` (don't edit those by hand)
- `scripts/fetch_logos.py` — downloads favicons once into `assets/logos/` (monogram fallback; `--force` to refresh)
- `.github/ISSUE_TEMPLATE/` — tool submissions and sponsor inquiries (the site's forms open pre-filled issues)

## Local preview
`python3 -m http.server 8000` → http://localhost:8000/ (paths are root-absolute).

## Deploy
Push to `main`; Pages serves `main` / root (`.nojekyll` included). Asset URLs are cache-busted automatically.
For another domain/repo, edit `SITE`, `BASE`, `REPO` at the top of `scripts/build.py`.
