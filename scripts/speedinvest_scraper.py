#!/usr/bin/env python3
"""Speedinvest portfolio scraper -> speedinvest_companies.json
Source: https://www.speedinvest.com/portfolio (Webflow list + featured grid).
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

PORTFOLIO_URL = "https://www.speedinvest.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "speedinvest_companies.json")
PRIMARY = "Speedinvest"

SECTOR_MAP = {
    "AI & Infra": ["Dev Tools / Cloud", "Deeptech / Robotics / AR/VR"],
    "Fintech & DeFi": ["FinTech / Insurance", "Web3 / Crypto"],
    "Health & Bio": ["Health", "BioTech"],
    "Deep Tech": ["Deeptech / Robotics / AR/VR"],
    "Marketplaces & Consumer": ["Consumer"],
    "Climate Tech & Industrial Tech": ["Climate / Sustainability"],
    "Middle East, Africa & Beyond": [],
    "Exits": [],
}


def tags_for(name, desc, sectors):
    out = []
    for s in sectors or []:
        for t in SECTOR_MAP.get(s, []):
            if t not in out:
                out.append(t)
    for t in classify(name, desc, sectors):
        if t not in out:
            out.append(t)
    return out[:4]


def parse_list_item(it):
    name_el = it.select_one(".portfolio-list-title, h6")
    name = clean(name_el.get_text()) if name_el else None
    if not name:
        return None
    desc_el = it.select_one(".portfolio-list_short-descript p, [fs-list-field=descript]")
    desc = clean(desc_el.get_text()) if desc_el else None
    sectors = []
    for s in it.select("[fs-list-field=portfolio]"):
        t = clean(s.get_text())
        if t and t not in sectors:
            sectors.append(t)
    status = "Active"
    # exits section / label
    blob = it.get_text(" ", strip=True).lower()
    if "exit" in blob and "exits" in " ".join(sectors).lower():
        status = "Exited"
    a = it.select_one("a[href*='/portfolio/']")
    href = a["href"] if a else None
    profile = urljoin(PORTFOLIO_URL, href) if href else PORTFOLIO_URL
    return {
        "company_name": name,
        "description": desc,
        "company_url": None,
        "status": status,
        "stage": None,
        "sectors": sectors,
        "everywhere_tags": tags_for(name, desc, sectors),
        "primary_investor": PRIMARY,
        "source_url": profile,
    }


def parse_featured(it):
    name_el = it.select_one("h6, .heading-style-h6")
    name = clean(name_el.get_text()) if name_el else None
    if not name:
        return None
    desc = None
    for p in it.select("p"):
        t = clean(p.get_text())
        if t and len(t) >= 20:
            desc = t
            break
    a = it.select_one("a[href*='/portfolio/']")
    href = a["href"] if a else None
    profile = urljoin(PORTFOLIO_URL, href) if href else PORTFOLIO_URL
    return {
        "company_name": name,
        "description": desc,
        "company_url": None,
        "status": "Active",
        "stage": None,
        "sectors": [],
        "everywhere_tags": tags_for(name, desc, []),
        "primary_investor": PRIMARY,
        "source_url": profile,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for it in soup.select(".portfolio-list_list.w-dyn-items > .w-dyn-item"):
        rec = parse_list_item(it)
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

    if not limit or len(out) < limit:
        for it in soup.select(".portfolio.w-dyn-items > .w-dyn-item"):
            rec = parse_featured(it)
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

    # Mark exits from exits-wrapper if names match
    exit_names = set()
    for it in soup.select(".exits-wrapper .w-dyn-item"):
        t = clean(it.get_text(" ", strip=True))
        if t:
            exit_names.add(t.lower())
    for rec in out:
        if rec["company_name"].lower() in exit_names:
            rec["status"] = "Exited"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged")
    for tag, cnt in Counter(t for r in out for t in r["everywhere_tags"]).most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
