#!/usr/bin/env python3
"""Download each tool's favicon once into assets/logos/<slug>.png (self-hosted; visitors never hit a third party).
Uses Google's public favicon service at build time only. Missing logos fall back to a monogram. --force re-downloads."""
import json, re, sys, pathlib, urllib.request, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
out = ROOT/"assets/logos"; out.mkdir(parents=True, exist_ok=True)
force = "--force" in sys.argv
for t in json.loads((ROOT/"tools.json").read_text()):
    f = out/f"{slug(t['name'])}.png"
    if f.exists() and not force: continue
    host = urllib.parse.urlparse(t["url"]).netloc
    try:
        r = urllib.request.urlopen(urllib.request.Request(f"https://www.google.com/s2/favicons?domain={host}&sz=128", headers={"User-Agent": "Mozilla/5.0"}), timeout=15)
        data = r.read()
        if len(data) > 200:
            f.write_bytes(data)
            try:  # normalise: drop tiny icons (monogram looks better), cap at 64px
                from PIL import Image
                im = Image.open(f).convert("RGBA")
                if im.size[0] < 32: f.unlink(); print("tiny", t["name"]); continue
                if im.size[0] > 64: im = im.resize((64, 64), Image.LANCZOS)
                im.save(f, optimize=True)
            except ImportError: pass
            print("ok  ", t["name"])
    except Exception as e:
        print("miss", t["name"], e)
