#!/usr/bin/env python3
"""Set (or clear) an affiliate link for a tool, then rebuild.
Usage: python3 scripts/set_affiliate.py <slug> <https://your-affiliate-link>   |   python3 scripts/set_affiliate.py <slug> --clear
Slug = the tool page name, e.g. tool/elevenlabs.html -> elevenlabs. Run with no args to list slugs."""
import json, sys, re, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
slugs = {re.sub(r"[^a-z0-9]+", "-", t["name"].lower()).strip("-"): t["name"] for t in json.loads((ROOT/"tools.json").read_text())}
if len(sys.argv) < 3: sys.exit("Slugs:\n" + "\n".join(sorted(slugs)))
slug, url = sys.argv[1], sys.argv[2]
if slug not in slugs: sys.exit(f"Unknown slug '{slug}'. Run without args to list slugs.")
f = ROOT/"affiliates.json"; data = json.loads(f.read_text()) if f.exists() else {}
if url == "--clear": data[slug] = ""
elif not url.startswith("https://"): sys.exit("Link must start with https://")
else: data[slug] = url
f.write_text(json.dumps(data, indent=2) + "\n")
subprocess.run([sys.executable, str(ROOT/"scripts/build.py")], check=True)
print(f"{slugs[slug]}: {'cleared' if url == '--clear' else 'affiliate link set'}. Now: git add -A && git commit -m 'Affiliate: {slug}' && git push")
