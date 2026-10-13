#!/usr/bin/env python3
"""Generate all static pages, sitemap.xml and feed.xml from tools.json. Run: python3 scripts/build.py"""
import json, re, html, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://tooldrop-ai.github.io/"
BASE = "/"
REPO = "https://github.com/tooldrop-ai/tooldrop-ai.github.io"
e = html.escape
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
tools = sorted(json.loads((ROOT/"tools.json").read_text()), key=lambda t: t["name"].lower())
cats = sorted({t["category"] for t in tools})
today = datetime.date.today()
SUBMIT = f"{REPO}/issues/new?template=submit-tool.yml"
SPONSOR = f"{REPO}/issues/new?template=sponsor-inquiry.yml"

def card(t):
    return (f'<article class="card" data-cat="{e(t["category"])}"><h3><a href="{e(t["url"])}" target="_blank" rel="noopener">{e(t["name"])}<span aria-hidden="true"> ↗</span></a></h3>'
            f'<p>{e(t["description"])}</p><div class="meta"><a class="badge" href="{BASE}category/{slug(t["category"])}.html">{e(t["category"])}</a>'
            f'<span class="badge {e(t["pricing"])}">{e(t["pricing"])}</span></div></article>')

def layout(title, desc, path, body, extra_ld=None, script=False):
    url = SITE + path
    ld = {"@context":"https://schema.org","@type":"WebSite","name":"ToolDrop","url":SITE,
          "potentialAction":{"@type":"SearchAction","target":SITE+"?q={search_term_string}","query-input":"required name=search_term_string"}}
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in [ld]+([extra_ld] if extra_ld else []))
    nav = "".join(f'<li><a href="{BASE}category/{slug(c)}.html">{e(c)}</a></li>' for c in cats)
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta name="theme-color" content="#0b0d12"><link rel="icon" href="{BASE}assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="{BASE}assets/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="{BASE}assets/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="ToolDrop – new AI tools" href="{SITE}feed.xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="ToolDrop"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="ToolDrop – directory of AI tools">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{SITE}assets/og.png">
<link rel="stylesheet" href="{BASE}style.css">{lds}</head><body>
<a class="skip" href="#main">Skip to content</a>
<header><div class="wrap"><nav aria-label="Main"><a class="logo" href="{BASE}">Tool<span>Drop</span></a><ul><li><a href="{BASE}#tools">Tools</a></li><li><a href="{BASE}#submit">Submit</a></li><li><a href="{BASE}advertise.html">Advertise</a></li></ul></nav></div></header>
<main id="main" class="wrap">{body}</main>
<footer><div class="wrap"><nav aria-label="Categories"><ul class="foot">{nav}</ul></nav><p>© {today.year} ToolDrop · Listings link to official sites · <a href="{BASE}advertise.html">Advertise</a> · <a href="{SITE}feed.xml">RSS</a> · <a href="{REPO}">GitHub</a></p></div></footer>
{f'<script src="{BASE}app.js" defer></script>' if script else ''}</body></html>
'''

def itemlist(ts, name):
    return {"@context":"https://schema.org","@type":"ItemList","name":name,"numberOfItems":len(ts),
            "itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":t["url"]} for i,t in enumerate(ts)]}

sponsor = f'''<aside class="sponsor" aria-label="Sponsored"><span class="badge">Featured / Sponsored</span><h2>Your tool here - sponsor ToolDrop</h2><p class="muted">Reach people actively looking for AI tools. <a href="{BASE}advertise.html">Learn about sponsor spots →</a></p></aside>'''
newest = sorted(tools, key=lambda t: t["date_added"], reverse=True)
latest = newest[0]["date_added"] if tools else today.isoformat()
cutoff = (datetime.date.fromisoformat(latest) - datetime.timedelta(days=6)).isoformat()
new_week = [t for t in newest if t["date_added"] >= cutoff][:12]
chips = '<button type="button" class="chip on" data-c="All" aria-pressed="true">All</button>' + "".join(f'<button type="button" class="chip" data-c="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in cats)
home = f'''<div class="hero"><h1>Discover the best AI tools</h1><p>{len(tools)} hand-picked AI tools for work and creativity — searchable by category and pricing.</p></div>
{sponsor}
<section aria-labelledby="new-h"><h2 id="new-h">New this week</h2><p class="muted">Tools added since {cutoff}.</p><div class="grid">{"".join(card(t) for t in new_week)}</div></section>
<section id="tools" aria-labelledby="all-h"><h2 id="all-h">All tools</h2><div class="controls"><label class="sr" for="q">Search tools</label><input id="q" type="search" placeholder="Search {len(tools)} tools…" autocomplete="off">
<div class="row"><div class="chips" id="cats" role="group" aria-label="Filter by category">{chips}</div><label class="sr" for="price">Pricing</label><select id="price"><option value="">Any pricing</option><option>free</option><option>freemium</option><option>paid</option></select></div>
<p class="muted" id="count" aria-live="polite">{len(tools)} of {len(tools)} tools</p></div><div class="grid" id="grid">{"".join(card(t) for t in tools)}</div></section>
<section id="submit" aria-labelledby="sub-h"><div class="panel"><h2 id="sub-h">Submit a tool</h2><p class="muted">Know a great AI tool that's missing? Fill this in and you'll be taken to a pre-filled GitHub issue (free GitHub account required). Nothing is sent until you submit it there.</p>
<form id="submit-form" action="{REPO}/issues/new" method="get" target="_blank"><input type="hidden" name="template" value="submit-tool.yml">
<label for="f-name">Tool name</label><input id="f-name" name="tool-name" required><label for="f-url">Official URL</label><input id="f-url" name="tool-url" type="url" placeholder="https://" required>
<label for="f-desc">One-line description</label><input id="f-desc" name="description" maxlength="140"><label for="f-cat">Category</label><select id="f-cat" name="category">{"".join(f"<option>{e(c)}</option>" for c in cats)}<option>Other</option></select>
<label for="f-price">Pricing</label><select id="f-price" name="pricing"><option>free</option><option>freemium</option><option>paid</option></select><button class="btn" type="submit">Continue on GitHub →</button></form></div></section>'''
out = {"index.html": layout("ToolDrop — Directory of the Best AI Tools", f"Browse {len(tools)} hand-picked AI tools for chat, coding, images, video, audio, writing and productivity. Search, filter by category and pricing.", "", home, itemlist(tools,"AI tools"), True)}

for c in cats:
    ts = [t for t in tools if t["category"] == c]
    body = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{BASE}">Home</a> / {e(c)}</nav><div class="hero"><h1>Best AI tools for {e(c)}</h1><p>{len(ts)} {e(c).lower()} AI tools, with pricing.</p></div>{sponsor}<div class="grid">{"".join(card(t) for t in ts)}</div><p><a class="btn" href="{BASE}#tools">Browse all {len(tools)} tools</a></p>'
    bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":SITE},{"@type":"ListItem","position":2,"name":c,"item":f"{SITE}category/{slug(c)}.html"}]}
    out[f"category/{slug(c)}.html"] = layout(f"Best {c} AI Tools ({len(ts)}) — ToolDrop", f"{len(ts)} {c} AI tools: " + ", ".join(t["name"] for t in ts[:6]) + ". Compare free, freemium and paid options.", f"category/{slug(c)}.html", body, itemlist(ts, f"{c} AI tools")).replace('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "ItemList"', f'<script type="application/ld+json">{json.dumps(bc)}</script><script type="application/ld+json">{{"@context": "https://schema.org", "@type": "ItemList"',1)

adv = f'''<div class="hero"><h1>Advertise on ToolDrop</h1><p>Put your AI tool in front of people actively searching for one.</p></div>
<section class="panel"><h2>Sponsor spots</h2><ul><li><strong>Featured / Sponsored slot</strong> — the highlighted banner at the top of the homepage and every category page.</li>
<li><strong>Clearly labeled</strong> — sponsored placements are always marked "Sponsored" so visitors can trust the directory. Regular listings are never paid.</li>
<li><strong>Your content</strong> — tool name, one-line pitch and a link to your official site.</li></ul><p class="muted">Pricing and availability are shared on request.</p></section>
<section class="panel"><h2>Get in touch</h2><p>Open a sponsorship inquiry on GitHub (free account required). Inquiries are public issues, so don't include anything confidential.</p><p><a class="btn" href="{SPONSOR}" target="_blank" rel="noopener">Open a sponsor inquiry →</a></p></section>'''
out["advertise.html"] = layout("Advertise on ToolDrop — Sponsor an AI Tool Listing", "Sponsor the featured slot on ToolDrop, a directory of AI tools. Clearly labeled placements in front of people looking for AI tools.", "advertise.html", adv)
out["404.html"] = layout("Page not found — ToolDrop", "This page doesn't exist.", "404.html", f'<div class="hero"><h1>404 — page not found</h1><p>That page dropped off. <a href="{BASE}">Back to all AI tools</a>.</p></div>').replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"')

for p, s in out.items():
    f = ROOT/p; f.parent.mkdir(exist_ok=True); f.write_text(s)

urls = ["", "advertise.html"] + [f"category/{slug(c)}.html" for c in cats]
(ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{latest}</lastmod></url>\n" for u in urls) + "</urlset>\n")
(ROOT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
rfc = lambda d: datetime.datetime.fromisoformat(d).strftime("%a, %d %b %Y 00:00:00 +0000")
items = "".join(f"<item><title>{e(t['name'])}</title><link>{e(t['url'])}</link><guid isPermaLink=\"false\">tooldrop-{slug(t['name'])}</guid><pubDate>{rfc(t['date_added'])}</pubDate><category>{e(t['category'])}</category><description>{e(t['description'])} ({t['pricing']})</description></item>\n" for t in newest[:50])
(ROOT/"feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>ToolDrop — New AI tools</title><link>{SITE}</link><description>Newly added AI tools on ToolDrop.</description><language>en</language><lastBuildDate>{rfc(latest)}</lastBuildDate><atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>\n{items}</channel></rss>\n')
print(f"Built {len(out)} pages, {len(tools)} tools, {len(cats)} categories, {len(new_week)} new this week")
