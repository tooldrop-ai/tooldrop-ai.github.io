#!/usr/bin/env python3
"""Generate every static page, sitemap.xml, feed.xml, robots.txt and sw.js from tools.json.
Run: python3 scripts/build.py   (stdlib only; logos come from scripts/fetch_logos.py)"""
import json, re, html, datetime, pathlib, hashlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://tooldrop-ai.github.io/"
BASE = "/"
REPO = "https://github.com/tooldrop-ai/tooldrop-ai.github.io"
NEW_DAYS = 7
e = html.escape
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
tools = sorted(json.loads((ROOT/"tools.json").read_text()), key=lambda t: t["name"].lower())
_aff_file = ROOT/"affiliates.json"
AFF = {k: v.strip() for k, v in (json.loads(_aff_file.read_text()) if _aff_file.exists() else {}).items() if not k.startswith("_") and isinstance(v, str) and v.strip().startswith("https://")}
for t in tools:
    t["slug"] = slug(t["name"])
    t["out"] = AFF.get(t["slug"]) or (t.get("affiliate_url") or "").strip() or t["url"]
    t["aff"] = t["out"] != t["url"]
    t["logo"] = (ROOT/f"assets/logos/{t['slug']}.png").exists()
    t["hue"] = int(hashlib.md5(t["name"].encode()).hexdigest()[:4], 16) % 360
cats = sorted({t["category"] for t in tools})
newest = sorted(tools, key=lambda t: (t["date_added"], t["name"]), reverse=True)
latest = newest[0]["date_added"]
cutoff = (datetime.date.fromisoformat(latest) - datetime.timedelta(days=NEW_DAYS - 1)).isoformat()
for t in tools: t["new"] = t["date_added"] >= cutoff
SUBMIT = f"{REPO}/issues/new?template=submit-tool.yml"
SPONSOR = f"{REPO}/issues/new?template=sponsor-inquiry.yml"
VER = hashlib.md5(((ROOT/"style.css").read_bytes() + (ROOT/"app.js").read_bytes() + (ROOT/"tools.json").read_bytes())).hexdigest()[:8]
fmt_date = lambda d: datetime.date.fromisoformat(d).strftime("%b %-d, %Y")

LOGO = '''<svg class="mark" viewBox="0 0 32 32" aria-hidden="true" width="28" height="28"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8b7cff"/><stop offset=".55" stop-color="#e46fd1"/><stop offset="1" stop-color="#ffb36b"/></linearGradient></defs><path d="M16 2.5c5.2 6.4 10 11.4 10 17a10 10 0 0 1-20 0c0-5.6 4.8-10.6 10-17Z" fill="url(#lg)"/><path d="M11.5 17h9M16 17v8" stroke="#0b0b12" stroke-width="2.6" stroke-linecap="round"/></svg>'''
ICON = {
 "search": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m20 20-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 "sun": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" class="i-sun"><circle cx="12" cy="12" r="4.5" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></g></svg><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" class="i-moon"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" fill="currentColor"/></svg>',
 "star": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9Z" fill="var(--star-fill,none)" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
 "ext": '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "dice": '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="4" fill="none" stroke="currentColor" stroke-width="2"/><g fill="currentColor"><circle cx="8.5" cy="8.5" r="1.5"/><circle cx="15.5" cy="15.5" r="1.5"/><circle cx="12" cy="12" r="1.5"/></g></svg>',
 "up": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

def rel(t):
    return "sponsored noopener" if t["aff"] else "noopener"

def logo(t, size=44):
    if t["logo"]:
        return f'<span class="logo-tile" style="--s:{size}px"><img src="{BASE}assets/logos/{t["slug"]}.png" alt="" width="{size-16}" height="{size-16}" loading="lazy" decoding="async"></span>'
    return f'<span class="logo-tile mono" style="--s:{size}px;--h:{t["hue"]}" aria-hidden="true">{e(t["name"][0])}</span>'

def card(t):
    return (f'<article class="card reveal" data-slug="{t["slug"]}" data-cat="{e(t["category"])}" data-price="{t["pricing"]}" data-date="{t["date_added"]}" data-name="{e(t["name"].lower())}">'
            f'<div class="card-top">{logo(t)}<div class="card-title"><h3><a class="stretch" href="{BASE}tool/{t["slug"]}.html">{e(t["name"])}</a></h3>'
            f'<span class="sub">{e(t["category"])}</span></div>'
            f'<button type="button" class="fav" data-fav="{t["slug"]}" aria-pressed="false" aria-label="Save {e(t["name"])} to My stack">{ICON["star"]}</button></div>'
            f'<p>{e(t["description"])}</p><div class="meta"><span class="pill {t["pricing"]}">{t["pricing"].capitalize()}</span>'
            f'{"<span class=pill-new>New</span>" if t["new"] else ""}'
            f'<a class="visit" href="{e(t["out"])}" target="_blank" rel="{rel(t)}" aria-label="Visit {e(t["name"])} official site (opens in new tab){", affiliate link" if t["aff"] else ""}">Visit {ICON["ext"]}</a></div></article>')

def layout(title, desc, path, body, lds=(), og_type="website", noindex=False):
    url = SITE + path
    site_ld = {"@context":"https://schema.org","@type":"WebSite","name":"ToolDrop","url":SITE,
               "potentialAction":{"@type":"SearchAction","target":SITE+"?q={search_term_string}","query-input":"required name=search_term_string"}}
    ldtxt = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in [site_ld, *lds])
    foot_cats = "".join(f'<li><a href="{BASE}category/{slug(c)}.html">{e(c)}</a></li>' for c in cats)
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">{'<meta name="robots" content="noindex">' if noindex else ''}
<script>(function(){{try{{var t=localStorage.getItem("td-theme")||(matchMedia("(prefers-color-scheme: light)").matches?"light":"dark");document.documentElement.dataset.theme=t;document.documentElement.classList.add("js")}}catch(e){{}}}})()</script>
<meta name="theme-color" content="#0b0b12" media="(prefers-color-scheme: dark)"><meta name="theme-color" content="#f7f6fb" media="(prefers-color-scheme: light)"><meta name="color-scheme" content="dark light">
<link rel="preload" href="{BASE}assets/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" href="{BASE}assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="{BASE}assets/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="{BASE}assets/apple-touch-icon.png"><link rel="manifest" href="{BASE}manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="ToolDrop – new AI tools" href="{SITE}feed.xml">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="ToolDrop"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="ToolDrop – a curated directory of AI tools">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{SITE}assets/og.png">
<link rel="stylesheet" href="{BASE}style.css?v={VER}">{ldtxt}</head><body>
<a class="skip" href="#main">Skip to content</a><div class="bg" aria-hidden="true"></div>
<header class="top"><div class="wrap bar"><a class="brand" href="{BASE}" aria-label="ToolDrop home">{LOGO}<span>Tool<b>Drop</b></span></a>
<nav aria-label="Main"><ul class="nav"><li><a href="{BASE}#tools">Tools</a></li><li><a href="{BASE}#submit">Submit</a></li><li><a href="{BASE}advertise.html">Advertise</a></li></ul></nav>
<div class="actions"><button type="button" class="kbtn" data-palette aria-label="Search tools (Ctrl+K)">{ICON["search"]}<span class="kl">Search</span><kbd>⌘K</kbd></button>
<button type="button" class="icon-btn" id="theme" aria-label="Toggle light/dark theme">{ICON["sun"]}</button></div></div></header>
<main id="main">{body}</main>
<footer class="foot"><div class="wrap"><div class="foot-grid"><div><a class="brand" href="{BASE}">{LOGO}<span>Tool<b>Drop</b></span></a><p class="muted">A curated, independent directory of AI tools. Listings link to each tool's official site. Sponsored placements are always labeled.</p></div>
<nav aria-label="Categories"><h2 class="fh">Categories</h2><ul>{foot_cats}</ul></nav>
<nav aria-label="Site"><h2 class="fh">ToolDrop</h2><ul><li><a href="{BASE}#tools">All tools</a></li><li><a href="{BASE}best/free-ai-tools.html">Free AI tools</a></li><li><a href="{BASE}?view=stack#tools">My stack</a></li><li><a href="{SUBMIT}" rel="noopener">Submit a tool</a></li><li><a href="{BASE}advertise.html">Advertise</a></li><li><a href="{SITE}feed.xml">RSS feed</a></li><li><a href="{BASE}disclosure.html">Disclosure</a></li><li><a href="{REPO}" rel="noopener">GitHub</a></li></ul></nav></div>
<p class="muted small disc">Some links on ToolDrop may be affiliate links: if you buy through them, ToolDrop may earn a commission at no extra cost to you. It never affects which tools are listed or how they're described. <a href="{BASE}disclosure.html">Disclosure</a></p>
<p class="muted small">© {datetime.date.today().year} ToolDrop · Updated {fmt_date(latest)}</p></div></footer>
<button type="button" class="icon-btn totop" id="totop" aria-label="Back to top">{ICON["up"]}</button>
<dialog id="palette" aria-label="Search tools"><div class="pal"><div class="pal-in">{ICON["search"]}<input id="pal-q" type="search" placeholder="Search tools, categories…" autocomplete="off" aria-label="Search tools" aria-controls="pal-list"><kbd>Esc</kbd></div><ul id="pal-list" role="listbox"></ul><p class="pal-hint muted small">↑ ↓ to navigate · Enter to open</p></div></dialog>
<script src="{BASE}app.js?v={VER}" defer></script></body></html>
'''

def itemlist(ts, name):
    return {"@context":"https://schema.org","@type":"ItemList","name":name,"numberOfItems":len(ts),
            "itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":f"{SITE}tool/{t['slug']}.html"} for i,t in enumerate(ts)]}
def crumbs(*pairs):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":u} for i,(n,u) in enumerate(pairs)]}
def crumb_html(*pairs):
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(f'<li><a href="{u}">{e(n)}</a></li>' if u else f'<li aria-current="page">{e(n)}</li>' for n,u in pairs) + '</ol></nav>'

sponsor = f'''<aside class="sponsor reveal" aria-label="Sponsored placement"><div class="sp-glow" aria-hidden="true"></div><div class="sp-body"><span class="eyebrow">Featured · Sponsored</span>
<h2>Your tool here - sponsor ToolDrop</h2><p>Get your AI tool in front of people actively searching for one. One clearly labeled spot, top of every page.</p></div>
<a class="btn ghost" href="{BASE}advertise.html">Sponsor this spot →</a></aside>'''

# ---- home
new_week = [t for t in newest if t["new"]][:8]
chips = '<button type="button" class="chip" data-c="" aria-pressed="true">All</button>' + "".join(f'<button type="button" class="chip" data-c="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in cats)
stats = f'''<dl class="stats reveal"><div><dt>Tools</dt><dd>{len(tools)}</dd></div><div><dt>Categories</dt><dd>{len(cats)}</dd></div><div><dt>Free or freemium</dt><dd>{sum(t["pricing"]!="paid" for t in tools)}</dd></div><div><dt>Last updated</dt><dd><time datetime="{latest}">{fmt_date(latest)}</time></dd></div></dl>'''
home = f'''<section class="hero wrap"><p class="eyebrow reveal">Curated AI tool directory</p><h1 class="reveal">Find the right <span class="grad">AI tool</span>,<br>without the noise.</h1>
<p class="lede reveal">{len(tools)} hand-picked tools across {len(cats)} categories — each linked to its official site, labeled by pricing, and searchable in a keystroke.</p>
<div class="hero-cta reveal"><button type="button" class="btn" data-palette>{ICON["search"]} Search tools <kbd>Ctrl K</kbd></button><button type="button" class="btn ghost" id="random">{ICON["dice"]} Random tool</button></div>{stats}</section>
<div class="wrap">{sponsor}
<section class="block" aria-labelledby="new-h"><div class="sec-head"><h2 id="new-h">New this week</h2><a class="muted" href="{SITE}feed.xml">RSS feed →</a></div><div class="grid">{"".join(card(t) for t in new_week)}</div></section>
<section id="tools" class="block" aria-labelledby="all-h"><div class="sec-head"><h2 id="all-h">All tools</h2><p class="muted" id="count" aria-live="polite">{len(tools)} tools</p></div>
<div class="toolbar"><div class="search"><label class="sr" for="q">Filter tools</label>{ICON["search"]}<input id="q" type="search" placeholder="Filter {len(tools)} tools…" autocomplete="off"></div>
<label class="sr" for="price">Pricing</label><select id="price"><option value="">Any pricing</option><option value="free">Free</option><option value="freemium">Freemium</option><option value="paid">Paid</option></select>
<label class="sr" for="sort">Sort</label><select id="sort"><option value="az">A–Z</option><option value="new">Newest</option></select>
<button type="button" class="btn ghost sm" id="stack" aria-pressed="false">{ICON["star"]} My stack <span id="stack-n" class="n">0</span></button></div>
<div class="chips" id="cats" role="group" aria-label="Filter by category">{chips}</div>
<div class="grid" id="grid">{"".join(card(t) for t in tools)}</div><p class="empty" id="empty" hidden>No tools match. <button type="button" class="link" id="reset">Clear filters</button></p></section>
<section id="submit" class="block" aria-labelledby="sub-h"><div class="panel split reveal"><div><span class="eyebrow">Open submissions</span><h2 id="sub-h">Submit a tool</h2><p class="muted">Know a great AI tool that's missing? Fill this in and you'll continue to a pre-filled GitHub issue (free GitHub account required). Nothing is sent until you submit it there. Listings are free and never paid for.</p></div>
<form id="submit-form" action="{REPO}/issues/new" method="get" target="_blank" rel="noopener"><input type="hidden" name="template" value="submit-tool.yml"><input type="hidden" name="title" value="[Tool] ">
<div class="f2"><div><label for="f-name">Tool name</label><input id="f-name" name="tool-name" required></div><div><label for="f-url">Official URL</label><input id="f-url" name="tool-url" type="url" placeholder="https://" required></div></div>
<label for="f-desc">One-line description</label><input id="f-desc" name="description" maxlength="140">
<div class="f2"><div><label for="f-cat">Category</label><select id="f-cat" name="category">{"".join(f"<option>{e(c)}</option>" for c in cats)}<option>Other</option></select></div><div><label for="f-price">Pricing</label><select id="f-price" name="pricing"><option>free</option><option>freemium</option><option>paid</option></select></div></div>
<button class="btn" type="submit">Continue on GitHub →</button></form></div></section></div>'''
pages = {"index.html": layout("ToolDrop — Curated Directory of the Best AI Tools", f"Browse {len(tools)} hand-picked AI tools for chat, coding, images, video, audio, writing and productivity. Search instantly and filter by category and pricing.", "", home, [itemlist(tools, "AI tools")])}

# ---- categories
for c in cats:
    ts = [t for t in tools if t["category"] == c]; cu = f"{SITE}category/{slug(c)}.html"
    others = "".join(f'<a class="chip" href="{BASE}category/{slug(o)}.html">{e(o)}</a>' for o in cats if o != c)
    body = f'''<section class="hero sm wrap">{crumb_html(("Home", BASE), (c, None))}<h1 class="reveal">Best AI tools for <span class="grad">{e(c)}</span></h1>
<p class="lede reveal">{len(ts)} {e(c)} tools — {sum(t["pricing"]=="free" for t in ts)} free, {sum(t["pricing"]=="freemium" for t in ts)} freemium, {sum(t["pricing"]=="paid" for t in ts)} paid.</p></section>
<div class="wrap">{sponsor}<div class="grid block">{"".join(card(t) for t in ts)}</div>{f'<p class="block"><a class="btn ghost sm" href="{BASE}best/free-{slug(c)}-ai-tools.html">Only free {e(c)} tools →</a></p>' if sum(1 for x in ts if x["pricing"] != "paid") >= 3 else ''}<section class="block"><h2>Other categories</h2><div class="chips">{others}</div></section></div>'''
    pages[f"category/{slug(c)}.html"] = layout(f"Best {c} AI Tools ({len(ts)}) — ToolDrop", f"{len(ts)} {c} AI tools compared by pricing: " + ", ".join(t["name"] for t in ts[:6]) + ".", f"category/{slug(c)}.html", body, [crumbs(("Home", SITE), (c, cu)), itemlist(ts, f"{c} AI tools")])

# ---- tool pages
for t in tools:
    alts = [a for a in tools if a["category"] == t["category"] and a is not t]
    alts = sorted(alts, key=lambda a: (a["pricing"] != t["pricing"], a["name"].lower()))[:6]
    tu = f"{SITE}tool/{t['slug']}.html"; cu = f"{SITE}category/{slug(t['category'])}.html"
    app = {"@context":"https://schema.org","@type":"SoftwareApplication","name":t["name"],"url":t["url"],"description":t["description"],
           "applicationCategory":f"{t['category']} AI tool","operatingSystem":"Web"}
    if t["pricing"] == "free": app["offers"] = {"@type":"Offer","price":"0","priceCurrency":"USD"}
    pricing_note = {"free":"free to use","freemium":"free to start, with paid plans","paid":"a paid product"}[t["pricing"]]
    body = f'''<section class="hero sm wrap">{crumb_html(("Home", BASE), (t["category"], f"{BASE}category/{slug(t['category'])}.html"), (t["name"], None))}
<div class="tool-head reveal">{logo(t, 72)}<div><h1>{e(t["name"])}</h1><p class="lede">{e(t["description"])}</p>
<div class="meta"><a class="pill cat" href="{BASE}category/{slug(t['category'])}.html">{e(t["category"])}</a><span class="pill {t["pricing"]}">{t["pricing"].capitalize()}</span>{"<span class=pill-new>New</span>" if t["new"] else ""}</div></div></div>
<div class="hero-cta reveal"><a class="btn" href="{e(t["out"])}" target="_blank" rel="{rel(t)}">Visit {e(t["name"])} {ICON["ext"]}</a><button type="button" class="btn ghost fav fav-lg" data-fav="{t["slug"]}" aria-pressed="false">{ICON["star"]} <span class="fl">Save to My stack</span></button></div></section>
<div class="wrap"><section class="panel reveal block"><h2>At a glance</h2><dl class="facts"><div><dt>Category</dt><dd><a href="{BASE}category/{slug(t['category'])}.html">{e(t["category"])}</a></dd></div><div><dt>Pricing</dt><dd>{t["pricing"].capitalize()} — {pricing_note}</dd></div><div><dt>Official site</dt><dd><a href="{e(t["out"])}" target="_blank" rel="{rel(t)}">{e(re.sub(r"^https?://(www\.)?", "", t["url"]).rstrip("/"))}</a></dd></div><div><dt>Listed on ToolDrop</dt><dd><time datetime="{t["date_added"]}">{fmt_date(t["date_added"])}</time></dd></div></dl>
<p class="muted small">Pricing labels are a quick guide; check the official site for current plans.{' The Visit link is an affiliate link: ToolDrop may earn a commission at no extra cost to you. <a href="/disclosure.html">Disclosure</a>.' if t["aff"] else ''}</p></section>
{sponsor}{f'<section class="block"><h2>Alternatives to {e(t["name"])}</h2><div class="grid">{"".join(card(a) for a in alts)}</div>{f'<p><a class="btn ghost sm" href="{BASE}alternatives/{t["slug"]}.html">Compare all {sum(1 for x in tools if x["category"] == t["category"]) - 1} alternatives →</a></p>' if sum(1 for x in tools if x["category"] == t["category"]) - 1 >= 3 else ''}</section>' if alts else ''}</div>'''
    pages[f"tool/{t['slug']}.html"] = layout(f"{t['name']} — {t['category']} AI Tool, Pricing & Alternatives | ToolDrop", f"{t['name']}: {t['description']} {t['pricing'].capitalize()}. See alternatives like " + ", ".join(a["name"] for a in alts[:3]) + ".", f"tool/{t['slug']}.html", body, [crumbs(("Home", SITE), (t["category"], cu), (t["name"], tu)), app])

# ---- advertise / 404 / offline
adv = f'''<section class="hero sm wrap"><p class="eyebrow reveal">Advertise</p><h1 class="reveal">Put your tool where people <span class="grad">pick tools</span>.</h1><p class="lede reveal">ToolDrop visitors arrive looking for an AI tool to use. One sponsor spot, clearly labeled, at the top of every page.</p></section>
<div class="wrap"><section class="block"><div class="grid three">
<div class="panel reveal"><h2>Featured slot</h2><p class="muted">The highlighted banner at the top of the homepage, all {len(cats)} category pages and all {len(tools)} tool pages.</p></div>
<div class="panel reveal"><h2>Clearly labeled</h2><p class="muted">Sponsored placements are always marked "Sponsored". Regular listings are free, curated and never sold — that's what makes the slot worth having.</p></div>
<div class="panel reveal"><h2>Your message</h2><p class="muted">Tool name, a one-line pitch and a link to your official site. No tracking scripts or third-party ad code.</p></div></div></section>
<section class="block"><h2>Preview</h2>{sponsor}</section>
<section class="panel split reveal block"><div><span class="eyebrow">Get in touch</span><h2>Sponsorship inquiry</h2><p class="muted">Open an inquiry on GitHub (free account required). Inquiries are public issues, so please don't include anything confidential. Pricing and availability are shared on request.</p></div>
<div class="center"><a class="btn" href="{SPONSOR}" target="_blank" rel="noopener">Open a sponsor inquiry →</a></div></section></div>'''
pages["advertise.html"] = layout("Advertise on ToolDrop — Sponsor the Featured AI Tool Slot", "Sponsor the featured slot on ToolDrop, a curated directory of AI tools. One clearly labeled placement on every page.", "advertise.html", adv)
pages["404.html"] = layout("Page not found — ToolDrop", "This page doesn't exist.", "404.html", f'<section class="hero wrap"><p class="eyebrow">404</p><h1>This page <span class="grad">dropped off</span>.</h1><p class="lede">Try searching instead, or head back to all tools.</p><div class="hero-cta"><button type="button" class="btn" data-palette>{ICON["search"]} Search tools</button><a class="btn ghost" href="{BASE}">All tools</a></div></section>', noindex=True)
pages["offline.html"] = layout("Offline — ToolDrop", "You're offline.", "offline.html", f'<section class="hero wrap"><h1>You’re <span class="grad">offline</span>.</h1><p class="lede">Pages you’ve visited are still available. Reconnect to browse everything.</p><div class="hero-cta"><a class="btn" href="{BASE}">Home</a></div></section>', noindex=True)

# ---- disclosure
disc = f"""<section class="hero sm wrap"><p class="eyebrow reveal">Transparency</p><h1 class="reveal">Affiliate &amp; advertising <span class="grad">disclosure</span></h1><p class="lede reveal">Last updated <time datetime="{latest}">{fmt_date(latest)}</time>.</p></section>
<div class="wrap prose"><section class="panel reveal block">
<h2>Affiliate links</h2><p>Some "Visit" links on ToolDrop are affiliate links. If you click one and later buy a paid plan, ToolDrop may earn a commission from the tool's maker. You pay the same price — affiliate links never cost you extra.</p>
<p>Affiliate links are marked in the page code with <code>rel="sponsored"</code>, and tool pages that use one say so next to the Visit button.</p>
<h2>What affiliate links don't change</h2><ul><li>Which tools are listed: tools are added because they're useful and real, whether or not they have an affiliate program. Most listings have no affiliate link.</li><li>How tools are described, ordered or labeled. Lists are alphabetical or by date added; pricing labels are our best reading of each tool's official site.</li><li>Listings are free. Nobody can pay to be listed or to get a better description.</li></ul>
<h2>Sponsored placements</h2><p>The "Featured · Sponsored" slot is paid advertising when it is filled, and it is always labeled as sponsored. It is clearly separate from the regular listings.</p>
<h2>Privacy</h2><p>ToolDrop itself uses no analytics, ad trackers or cookies. Your theme choice and "My stack" favorites are stored only in your own browser (localStorage) and never sent anywhere. When you follow a link to another site, including an affiliate link, that site's own privacy and cookie policy applies; affiliate tracking happens on their side.</p>
<h2>Questions or corrections</h2><p>Spotted something wrong or outdated? <a href="{REPO}/issues/new" rel="noopener">Open an issue on GitHub</a>.</p>
</section></div>"""
pages["disclosure.html"] = layout("Affiliate & Advertising Disclosure — ToolDrop", "How ToolDrop uses affiliate links and sponsored placements, and what they never change.", "disclosure.html", disc)

# ---- alternatives pages (comparison tables, distinct search intent from tool pages)
def table(ts):
    rows = "".join(f'<tr><th scope="row"><a href="{BASE}tool/{t["slug"]}.html">{e(t["name"])}</a></th><td><span class="pill {t["pricing"]}">{t["pricing"].capitalize()}</span></td><td>{e(t["description"])}</td><td><a class="visit" href="{e(t["out"])}" target="_blank" rel="{rel(t)}">Visit {ICON["ext"]}</a></td></tr>' for t in ts)
    return f'<div class="tbl-wrap reveal"><table class="tbl"><thead><tr><th scope="col">Tool</th><th scope="col">Pricing</th><th scope="col">What it does</th><th scope="col"><span class="sr">Link</span></th></tr></thead><tbody>{rows}</tbody></table></div>'
ALT_MIN = 3
alt_pages = []
for t in tools:
    alts = sorted([a for a in tools if a["category"] == t["category"] and a is not t], key=lambda a: (a["pricing"] != "free", a["name"].lower()))
    if len(alts) < ALT_MIN: continue
    alt_pages.append(t["slug"]); au = f"{SITE}alternatives/{t['slug']}.html"
    freeish = [a["name"] for a in alts if a["pricing"] != "paid"]
    body = f"""<section class="hero sm wrap">{crumb_html(("Home", BASE), (t["category"], f"{BASE}category/{slug(t['category'])}.html"), (f"{t['name']} alternatives", None))}
<h1 class="reveal">{len(alts)} <span class="grad">{e(t["name"])}</span> alternatives</h1>
<p class="lede reveal">Looking for an alternative to {e(t["name"])}? Here are the other {e(t["category"])} tools on ToolDrop{f", {len(freeish)} of them free or with a free tier" if freeish else ""}.</p></section>
<div class="wrap"><section class="block">{table(alts)}</section>
<section class="panel reveal block"><h2>About {e(t["name"])}</h2><p class="muted">{e(t["description"])} Pricing: {t["pricing"]}.</p><p><a class="btn ghost sm" href="{BASE}tool/{t["slug"]}.html">{e(t["name"])} details</a></p></section>{sponsor}</div>"""
    pages[f"alternatives/{t['slug']}.html"] = layout(f"{len(alts)} Best {t['name']} Alternatives — {t['category']} AI Tools | ToolDrop", f"Alternatives to {t['name']}: " + ", ".join(a["name"] for a in alts[:5]) + f" and more. Compare {t['category']} AI tools by pricing.", f"alternatives/{t['slug']}.html", body, [crumbs(("Home", SITE), (t["category"], f"{SITE}category/{slug(t['category'])}.html"), (f"{t['name']} alternatives", au)), itemlist(alts, f"{t['name']} alternatives")])

# ---- best free pages
best_pages = []
def best_page(path, h1, title, desc, ts, intro):
    best_pages.append(path)
    body = f"""<section class="hero sm wrap">{crumb_html(("Home", BASE), (h1, None))}<h1 class="reveal">{h1}</h1><p class="lede reveal">{intro}</p></section>
<div class="wrap"><section class="block">{table(ts)}</section>{sponsor}</div>"""
    pages[path] = layout(title, desc, path, body, [crumbs(("Home", SITE), (h1, SITE + path)), itemlist(ts, h1)])
free_all = [t for t in tools if t["pricing"] != "paid"]
best_page("best/free-ai-tools.html", "Free AI tools", f"{len(free_all)} Free AI Tools (Free & Free-Tier) — ToolDrop", f"{len(free_all)} AI tools you can use for free or start on a free tier, across {len(cats)} categories.", sorted(free_all, key=lambda t: (t["pricing"] != "free", t["category"], t["name"].lower())), f"{sum(t['pricing']=='free' for t in tools)} completely free tools and {sum(t['pricing']=='freemium' for t in tools)} with a free tier. Free tiers usually have usage limits — check each official site.")
BEST_FREE = {}
for c in cats:
    ts = [t for t in tools if t["category"] == c and t["pricing"] != "paid"]
    if len(ts) >= 3:
        pth = f"best/free-{slug(c)}-ai-tools.html"; BEST_FREE[c] = pth
        best_page(pth, f"Free {c} AI tools", f"{len(ts)} Free {c} AI Tools — ToolDrop", f"{len(ts)} free or free-tier {c} AI tools: " + ", ".join(t["name"] for t in ts[:5]) + ".", sorted(ts, key=lambda t: (t["pricing"] != "free", t["name"].lower())), f"{len(ts)} {e(c)} tools you can start using without paying.")

import shutil
for d in ("tool", "alternatives", "best"): shutil.rmtree(ROOT/d, ignore_errors=True)
for p, s in pages.items():
    f = ROOT/p; f.parent.mkdir(exist_ok=True); f.write_text(s)

# ---- sitemap, robots, feed, manifest, service worker
urls = [("", latest, "1.0"), ("advertise.html", latest, "0.4"), ("disclosure.html", latest, "0.2")] + [(p, latest, "0.7") for p in best_pages] + [(f"alternatives/{s_}.html", latest, "0.6") for s_ in alt_pages] + [(f"category/{slug(c)}.html", latest, "0.8") for c in cats] + [(f"tool/{t['slug']}.html", t["date_added"], "0.6") for t in tools]
(ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod><priority>{p}</priority></url>\n" for u,d,p in urls) + "</urlset>\n")
(ROOT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /offline.html\nSitemap: {SITE}sitemap.xml\n")
rfc = lambda d: datetime.datetime.fromisoformat(d).strftime("%a, %d %b %Y 00:00:00 +0000")
items = "".join(f"<item><title>{e(t['name'])} — {e(t['category'])}</title><link>{SITE}tool/{t['slug']}.html</link><guid isPermaLink=\"true\">{SITE}tool/{t['slug']}.html</guid><pubDate>{rfc(t['date_added'])}</pubDate><category>{e(t['category'])}</category><description>{e(t['description'])} ({t['pricing']})</description></item>\n" for t in newest[:50])
(ROOT/"feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>ToolDrop — New AI tools</title><link>{SITE}</link><description>Newly added AI tools on ToolDrop.</description><language>en</language><lastBuildDate>{rfc(latest)}</lastBuildDate><atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>\n{items}</channel></rss>\n')
(ROOT/"manifest.webmanifest").write_text(json.dumps({"name":"ToolDrop — AI tools directory","short_name":"ToolDrop","description":"A curated directory of AI tools.","start_url":BASE,"scope":BASE,"display":"standalone","background_color":"#0b0b12","theme_color":"#0b0b12",
  "icons":[{"src":f"{BASE}assets/icon-192.png","sizes":"192x192","type":"image/png"},{"src":f"{BASE}assets/icon-512.png","sizes":"512x512","type":"image/png"},{"src":f"{BASE}assets/icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}, indent=2))
core = [BASE, f"{BASE}offline.html", f"{BASE}style.css?v={VER}", f"{BASE}app.js?v={VER}", f"{BASE}tools.json", f"{BASE}assets/fonts/inter.woff2", f"{BASE}assets/favicon.svg"]
(ROOT/"sw.js").write_text(f'''// Generated by scripts/build.py — network-first for pages, cache-first for assets.
const V="td-{VER}",CORE={json.dumps(core)};
self.addEventListener("install",e=>{{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))}});
self.addEventListener("activate",e=>{{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))}});
self.addEventListener("fetch",e=>{{const r=e.request;if(r.method!=="GET"||new URL(r.url).origin!==location.origin)return;
if(r.mode==="navigate"||r.url.endsWith("tools.json")){{e.respondWith(fetch(r).then(res=>{{const c=res.clone();caches.open(V).then(x=>x.put(r,c));return res}}).catch(()=>caches.match(r).then(m=>m||caches.match("{BASE}offline.html"))));return}}
e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{{if(res.ok){{const c=res.clone();caches.open(V).then(x=>x.put(r,c))}}return res}})))}});
''')
print(f"Affiliate links active: {sum(t['aff'] for t in tools)}")
print(f"Built {len(pages)} pages ({len(tools)} tool pages), {len(cats)} categories, {len(new_week)} new this week, v{VER}")
