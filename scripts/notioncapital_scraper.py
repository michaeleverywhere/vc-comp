#!/usr/bin/env python3
"""Notion Capital portfolio scraper -> notioncapital_companies.json
Source: https://www.notion.vc/portfolio (Webflow company cards).
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

PORTFOLIO_URL = "https://www.notion.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "notioncapital_companies.json")
PRIMARY = "Notion Capital"


def parse_card(it):
    name_el = it.select_one("h4")
    name = clean(name_el.get_text()) if name_el else None
    if not name:
        return None
    desc = None
    hover = it.select_one(".card-hover-text")
    if hover:
        desc = clean(hover.get_text())
    text = it.get_text("\n", strip=True)
    status = "Exited" if ("\nExited\n" in f"\n{text}\n" or "\nExited" in text) else "Active"
    location = None
    for line in text.split("\n"):
        line = clean(line)
        if not line:
            continue
        if line in ("UK", "US", "USA", "EU", "Europe", "Germany", "France", "Spain", "Ireland", "Netherlands", "Nordics"):
            location = line
            break
    a = it.select_one("a[href*='/portfolio/']")
    profile = urljoin(PORTFOLIO_URL, a["href"]) if a else PORTFOLIO_URL
    logo = None
    img = it.select_one("img.company-card-logo")
    if img and img.get("src"):
        logo = clean(img["src"])
    return {
        "company_name": name,
        "description": desc,
        "company_url": None,
        "logo_url": logo,
        "location": location,
        "status": status,
        "stage": None,
        "everywhere_tags": classify(name, desc)[:4],
        "primary_investor": PRIMARY,
        "source_url": profile,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    cards = soup.select(".company-filter-results > .w-dyn-item, .company-card-wrapper.w-dyn-item")
    for it in cards:
        rec = parse_card(it)
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
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged")


if __name__ == "__main__":
    main()
