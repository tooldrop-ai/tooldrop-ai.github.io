#!/usr/bin/env python3
"""Notify IndexNow (Bing, Yandex, Seznam, Naver, Yep…) about site URLs. Free, no account.
The key lives in config.json and build.py publishes it as /<key>.txt.
Usage: python3 scripts/ping_indexnow.py            # all URLs in sitemap.xml
       python3 scripts/ping_indexnow.py --changed  # only URLs whose files changed in the last commit
Run AFTER pushing and after GitHub Pages has deployed (the key file must be live)."""
import json, sys, pathlib, subprocess, urllib.request, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parent.parent; SITE = "https://tooldrop-ai.github.io/"
key = json.loads((ROOT/"config.json").read_text())["indexnow_key"]
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = [u.find("s:loc", ns).text for u in ET.parse(ROOT/"sitemap.xml").getroot().findall("s:url", ns)]
if "--changed" in sys.argv:
    files = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", "HEAD~1", "HEAD"], capture_output=True, text=True).stdout.split()
    paths = {("" if f == "index.html" else f.replace("index.html", "")) for f in files if f.endswith(".html")}
    urls = [u for u in urls if u.replace(SITE, "") in paths] or [SITE]
try:
    live = urllib.request.urlopen(f"{SITE}{key}.txt", timeout=20).read().decode().strip() == key
except Exception: live = False
if not live: sys.exit(f"Key file {SITE}{key}.txt isn't live yet; push and wait for Pages to deploy.")
body = json.dumps({"host": "tooldrop-ai.github.io", "key": key, "keyLocation": f"{SITE}{key}.txt", "urlList": urls[:10000]}).encode()
for ep in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]:
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try: code = urllib.request.urlopen(req, timeout=30).status
    except urllib.error.HTTPError as err: code = f"{err.code} {err.read()[:200]!r}"
    except Exception as err: code = f"failed: {err}"
    print(f"{ep}: {code} ({len(urls)} URLs)")
print("200/202 = accepted. 403 = key not found/valid. 422 = URLs don't match host. 429 = too many requests.")
