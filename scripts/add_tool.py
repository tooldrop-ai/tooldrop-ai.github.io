#!/usr/bin/env python3
"""Add a tool and rebuild the site.
Usage: python3 scripts/add_tool.py "Name" "https://url/" "One-line description" "Category" free|freemium|paid [--date YYYY-MM-DD] [--no-check]
"""
import argparse, json, datetime, pathlib, subprocess, sys, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser(); p.add_argument("name"); p.add_argument("url"); p.add_argument("description"); p.add_argument("category")
p.add_argument("pricing", choices=["free","freemium","paid"]); p.add_argument("--date", default=datetime.date.today().isoformat()); p.add_argument("--no-check", action="store_true")
a = p.parse_args()
if not a.url.startswith("https://"): sys.exit("URL must start with https://")
tools = json.loads((ROOT/"tools.json").read_text())
if any(t["name"].lower()==a.name.lower() or t["url"].rstrip("/")==a.url.rstrip("/") for t in tools): sys.exit("Tool already listed.")
if not a.no_check:
    try:
        code = urllib.request.urlopen(urllib.request.Request(a.url, headers={"User-Agent":"Mozilla/5.0"}), timeout=15).status
    except urllib.error.HTTPError as err: code = err.code
    except Exception as err: sys.exit(f"URL check failed: {err} (use --no-check to skip)")
    if code >= 400 and code not in (401, 403): sys.exit(f"URL returned {code}")  # 403 = bot protection, usually fine
cats = sorted({t["category"] for t in tools})
if a.category not in cats: print(f"Note: new category '{a.category}' (existing: {', '.join(cats)})")
tools.append(dict(name=a.name, url=a.url, description=a.description, category=a.category, pricing=a.pricing, date_added=a.date))
(ROOT/"tools.json").write_text(json.dumps(tools, indent=2, ensure_ascii=False) + "\n")
subprocess.run([sys.executable, str(ROOT/"scripts/fetch_logos.py")])  # best effort; monogram fallback
subprocess.run([sys.executable, str(ROOT/"scripts/build.py")], check=True)
print(f"Added {a.name}. Now: git add -A && git commit -m 'Add {a.name}' && git push")
