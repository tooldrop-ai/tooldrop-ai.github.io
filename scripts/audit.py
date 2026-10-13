#!/usr/bin/env python3
"""SEO/tech audit of the built site: titles, descriptions, h1, alt text, JSON-LD validity, internal links, sitemap. Exit 1 on errors."""
import re, json, pathlib, html, sys, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parent.parent; SITE = "https://tooldrop-ai.github.io/"
errs, warns, n = [], [], 0
files = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "node_modules" not in p.parts]
for f in files:
    rp = f.relative_to(ROOT).as_posix(); s = f.read_text(); n += 1
    t = re.search(r"<title>(.*?)</title>", s); title = html.unescape(t.group(1)) if t else ""
    d = re.search(r'<meta name="description" content="(.*?)">', s); desc = html.unescape(d.group(1)) if d else ""
    noindex = 'name="robots" content="noindex"' in s
    if not title: errs.append(f"{rp}: no title")
    elif len(title) > 60: errs.append(f"{rp}: title {len(title)} chars: {title}")
    if not noindex and not (50 <= len(desc) <= 160): warns.append(f"{rp}: description {len(desc)} chars")
    if len(re.findall(r"<h1[\s>]", s)) != 1: errs.append(f"{rp}: {len(re.findall(r'<h1[\s>]', s))} h1")
    if not re.search(r'<link rel="canonical" href="https://tooldrop-ai\.github\.io/', s): errs.append(f"{rp}: canonical")
    for img in re.findall(r"<img\b[^>]*>", s):
        if " alt=" not in img: errs.append(f"{rp}: img without alt")
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            j = json.loads(m); assert j.get("@context") == "https://schema.org" and j.get("@type")
            if j["@type"] == "FAQPage": assert all(q["acceptedAnswer"]["text"] for q in j["mainEntity"])
            if j["@type"] == "BreadcrumbList": assert all("item" in i for i in j["itemListElement"])
        except Exception as ex: errs.append(f"{rp}: bad JSON-LD {ex}")
    for href in re.findall(r'href="(/[^"#?]*)', s):
        tgt = ROOT / href.lstrip("/")
        if href.endswith("/"): tgt = tgt / "index.html"
        if not tgt.exists(): errs.append(f"{rp}: broken link {href}")
sm = ET.parse(ROOT/"sitemap.xml").getroot(); ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = [u.find("s:loc", ns).text for u in sm.findall("s:url", ns)]
for l in locs:
    p = ROOT / l.replace(SITE, ""); p = p / "index.html" if l.endswith("/") else p
    if not p.exists(): errs.append(f"sitemap: missing {l}")
print(f"Audited {n} pages, {len(locs)} sitemap URLs: {len(errs)} errors, {len(warns)} warnings")
for x in errs[:40]: print("ERROR", x)
for x in warns[:40]: print("warn ", x)
sys.exit(1 if errs else 0)
