#!/usr/bin/env python3
"""
Pear VC portfolio scraper -> pear_companies.json

Source: server-rendered HTML on https://pear.vc/company/
(`.companies-all-box` cards — name, sector tag, one-line description, Pear
investment + current stage chips, external website via stretched-link).
WP REST `/wp-json/wp/v2/companies` exists but content.rendered is empty for
most records, so HTML is the source of truth.

usage:
    python3 scripts/pear_scraper.py [--limit N]
"""
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://pear.vc/company/"
SOURCE_URL = PORTFOLIO_URL
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "pear_companies.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

SECTOR_TAG_MAP = {
    "AI Applications": [],
    "AI Infrastructure": ["Dev Tools / Cloud"],
    "B2B": [],
    "Biotech": ["BioTech"],
    "Consumer": ["Consumer"],
    "Deep Tech": ["Deeptech / Robotics / AR/VR"],
    "FinTech": ["FinTech / Insurance"],
    "Healthcare": ["Health"],
    "Enterprise": [],
    "SaaS": [],
}

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify as _classify  # noqa: E402


def fetch(url):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            last = e
            time.sleep(1.5 * attempt)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


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


def parse_card(box):
    name_el = box.select_one(".left-area h5")
    name = clean(name_el.get_text()) if name_el else None
    if not name:
        return None
    sectors = []
    for a in box.select(".tags-area a"):
        t = clean(a.get_text())
        if t and t not in sectors:
            sectors.append(t)
    desc_el = box.select_one(".center-area p")
    description = clean(desc_el.get_text()) if desc_el else None
    stages = []
    pear_investment = None
    current_stage = None
    stage_links = box.select(".stages-area a")
    # Convention on Pear: first chip (often green) = Pear investment stage;
    # subsequent white chips = current stage / exit.
    for i, a in enumerate(stage_links):
        t = clean(a.get_text())
        if not t:
            continue
        if i == 0:
            pear_investment = t
        else:
            if t not in stages:
                stages.append(t)
        if current_stage is None and i > 0:
            current_stage = t
    if not stages and pear_investment:
        stages = [pear_investment]
    company_url = None
    a = box.select_one("a.stretched-link[href], a[href^='http']")
    if a and a.get("href", "").startswith("http"):
        href = a["href"].replace("#new_tab", "").rstrip("#")
        if "pear.vc" not in href:
            company_url = clean(href)
    return {
        "company_name": name,
        "description": description,
        "company_url": company_url,
        "sectors": sectors,
        "stage": stages,
        "pear_investment": pear_investment,
        "everywhere_tags": everywhere_tags(name, description, sectors),
        "source_url": SOURCE_URL,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    soup = BeautifulSoup(html, "html.parser")
    boxes = soup.select(".companies-all-box")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for box in boxes:
        rec = parse_card(box)
        if not rec:
            continue
        key = rec["company_name"].lower()
        if key in seen:
            continue
        seen.add(key)
        rec["scraped_at"] = scraped_at
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "pear_investment"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    print(f"  sectors: {sum(1 for r in out if r['sectors'])}/{n}")
    print(f"  stage: {sum(1 for r in out if r['stage'])}/{n}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
