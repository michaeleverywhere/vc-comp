#!/usr/bin/env python3
"""
Balderton Capital portfolio scraper -> balderton_companies.json

Source: https://www.balderton.com/companies/ — WordPress + FacetWP load-more
(~205 companies, 24/page). The FacetWP refresh endpoint returns empty to plain
HTTP clients from this host, so pagination is driven via headless Chrome
(scripts/_balderton_chrome.js + puppeteer-core + system google-chrome) calling
FWP.refresh() with is_load_more=true.

Each card exposes: name, one-line description, location, stage ("Seed in 2015"),
status (live/exited via CSS class), sector (CSS class), external website, logo.

usage:
    python3 scripts/balderton_scraper.py [--limit N]
    BALDERTON_DUMP=/path/to/raw.json python3 scripts/balderton_scraper.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "balderton_companies.json")
SOURCE_URL = "https://www.balderton.com/companies/"
CHROME = "/usr/bin/google-chrome"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROME_JS = os.path.join(SCRIPT_DIR, "_balderton_chrome.js")
NODE_DIR = "/tmp/vc-balderton-scrape"

SECTOR_TAG_MAP = {
    "ai-machine-learning": [],
    "consumer": ["Consumer"],
    "cyber-security": ["Cybersecurity"],
    "digital-health": ["Health"],
    "enterprise": [],
    "fintech": ["FinTech / Insurance"],
    "marketplace": ["Consumer"],
    "mobility": ["Transportation / Mobility"],
    "sustainability": ["Climate / Sustainability"],
}

sys.path.insert(0, os.path.join(SCRIPT_DIR, os.pardir, "automation"))
from tags import classify as _classify  # noqa: E402


def ensure_puppeteer():
    os.makedirs(NODE_DIR, exist_ok=True)
    mod = os.path.join(NODE_DIR, "node_modules", "puppeteer-core")
    if not os.path.isdir(mod):
        # Prefer shared /tmp/vc-recon install if present
        shared = "/tmp/vc-recon/node_modules/puppeteer-core"
        if os.path.isdir(shared):
            return shared
        subprocess.check_call(
            ["npm", "install", "--prefix", NODE_DIR, "puppeteer-core@22"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    return mod


def fetch_via_chrome():
    if not os.path.isfile(CHROME):
        raise SystemExit("FATAL: google-chrome not found; required for Balderton FacetWP pagination")
    pup = ensure_puppeteer()
    out_json = os.path.join(NODE_DIR, "raw.json")
    os.makedirs(NODE_DIR, exist_ok=True)
    env = os.environ.copy()
    env["PUPPETEER_PATH"] = pup
    env["CHROME_PATH"] = CHROME
    subprocess.check_call(["node", CHROME_JS, out_json], env=env, timeout=180)
    with open(out_json) as fh:
        return json.load(fh)


def clean(s):
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
    return s or None


def everywhere_tags(name, description, sectors):
    tags = []
    for sec in sectors or []:
        for mapped in SECTOR_TAG_MAP.get(sec, []):
            if mapped not in tags:
                tags.append(mapped)
    for t in _classify(name, description, sectors):
        if t not in tags:
            tags.append(t)
    return tags[:4]


def build_record(raw, scraped_at):
    name = clean(raw.get("name"))
    if not name:
        return None
    classes = raw.get("classes") or []
    sectors = []
    status = None
    for c in classes:
        if c.startswith("sector-"):
            sec = c[len("sector-"):]
            if sec and sec not in sectors:
                sectors.append(sec)
        if c.startswith("status-") and c != "status-publish":
            status = c[len("status-"):]
            if status == "live":
                status = "Live"
            elif status == "exited":
                status = "Exited"
    description = clean(raw.get("description"))
    stage = clean(raw.get("stage"))
    return {
        "company_name": name,
        "description": description,
        "company_url": clean(raw.get("company_url")) or None,
        "logo_url": clean(raw.get("logo_url")) or None,
        "location": clean(raw.get("location")) or None,
        "sectors": sectors,
        "stage": stage,
        "status": status,
        "everywhere_tags": everywhere_tags(name, description, sectors),
        "source_url": SOURCE_URL,
        "scraped_at": scraped_at,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    dump = os.environ.get("BALDERTON_DUMP")
    if dump and os.path.isfile(dump):
        with open(dump) as fh:
            raw = json.load(fh)
    else:
        print("fetching via headless Chrome (FacetWP load-more)...")
        raw = fetch_via_chrome()
    if limit:
        raw = raw[:limit]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for r in raw:
        rec = build_record(r, scraped_at)
        if not rec or rec["company_name"] in seen:
            continue
        seen.add(rec["company_name"])
        out.append(rec)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "logo_url", "location", "stage", "status"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    print(f"  sectors: {sum(1 for r in out if r['sectors'])}/{n}")
    print(f"  status dist: {Counter(r.get('status') for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
