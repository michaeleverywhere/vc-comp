#!/usr/bin/env python3
"""Precursor Ventures portfolio scraper -> precursor_companies.json
Source: https://precursorvc.com/portfolio/ — Vite/React single-page site; the
portfolio is not in the HTML but ships as data arrays inside the site's own JS
bundle (/assets/index-*.js, the file the page loads): the "Companies" grid
(name, website, Precursor sector label) and the "Founders" grid (founder name ->
company), merged here so each company carries its founders."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://precursorvc.com/portfolio/"
PRIMARY = "Precursor Ventures"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"], "digital health": ["Health"],
              "legaltech": ["RegTech/Gov/Legal"], "hardware": ["Deeptech / Robotics / AR/VR"], "consumer": ["Consumer"],
              "edtech": ["Future of Work"]}


def js_array(src, first_keys):
    """JSON-decode the first `const X=[{...}]` literal whose first object starts with first_keys."""
    m = re.search(r"=\[\{" + first_keys, src)
    if not m:
        return []
    i = m.start() + 1
    depth, j, q = 0, i, False
    while j < len(src):
        c = src[j]
        if q:
            if c == "\\":
                j += 2; continue
            if c == '"':
                q = False
        elif c == '"':
            q = True
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    lit = src[i:j + 1]
    lit = re.sub(r'([{,])([A-Za-z_]\w*):', r'\1"\2":', lit)
    lit = re.sub(r'!0\b', 'true', re.sub(r'!1\b', 'false', lit))
    return json.loads(lit)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    page = fetch(SOURCE_URL)
    m = re.search(r'src="(/assets/index-[^"]+\.js)"', page)
    if not m:
        raise SystemExit("FATAL: bundle not found on portfolio page")
    src = fetch(urljoin(SOURCE_URL, m.group(1)))
    companies = js_array(src, r'name:"[^"]*",logoUrl:')
    founders = js_array(src, r'name:"[^"]*",company:')
    by_co = {}
    for f in founders:
        by_co.setdefault((f.get("company") or "").strip().lower(), []).append(clean(f.get("name")))
    out, seen = [], set()
    for c in companies:
        name = clean(c.get("name"))
        if not name:
            continue
        seen.add(name.lower())
        sec = clean(c.get("sector"))
        out.append(rec(name, None, c.get("websiteUrl"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sec] if sec else [], sector_map=SECTOR_MAP, sector_label=sec,
                       founders=[x for x in by_co.get(name.lower(), []) if x]))
    for key, names in by_co.items():  # founder-grid companies missing from the company grid
        f0 = next(f for f in founders if (f.get("company") or "").strip().lower() == key)
        nm = clean(f0.get("company"))
        if nm and nm.lower() not in seen:
            seen.add(nm.lower())
            sec = clean(f0.get("sector"))
            out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                           sector_map=SECTOR_MAP, sector_label=sec, founders=[x for x in names if x]))
    if len(out) < 100:
        raise SystemExit(f"FATAL: only {len(out)} Precursor companies parsed")
    finish(out, "precursor", ("company_url", "sector_label", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
