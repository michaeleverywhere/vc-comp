#!/usr/bin/env python3
"""Sapphire Ventures portfolio scraper -> sapphire_companies.json
Source: https://sapphireventures.com/companies/ — server-rendered list items.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://sapphireventures.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "sapphire_companies.json")
PRIMARY = "Sapphire Ventures"

SECTOR_FROM_FILTER = {
    "filter__consumer": "Consumer",
    "filter__data-ai": "Data & AI",
    "filter__devops-security": "DevOps & Security",
    "filter__enterprise": "Enterprise",
    "filter__infra": "Infrastructure",
    "filter__business-apps": "Business Apps",
    "filter__vertical-saas": "Vertical SaaS",
    "filter__other": "Other",
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for li in soup.select("li[class*=filter__]"):
        title = li.select_one(".companies-v2-list-items-title h3, .companies-v2-list-items-title")
        if not title:
            continue
        name = clean(title.get_text())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        text_el = li.select_one(".companies-v2-list-items-text")
        desc = clean(text_el.get_text()) if text_el else None
        website = None
        a = li.select_one("a[href^='http']")
        if a:
            website = clean(a.get("href"))
        classes = li.get("class") or []
        status = "Active"
        exit_detail = None
        if "filter__ma" in classes:
            status = "Acquired"
            if desc and desc.lower().startswith("acquired"):
                exit_detail = desc
        elif "filter__ipo" in classes:
            status = "Public"
        sectors = [SECTOR_FROM_FILTER[c] for c in classes if c in SECTOR_FROM_FILTER]
        region = None
        if "filter__u-s" in classes:
            region = "US"
        elif "filter__europe" in classes:
            region = "Europe"
        elif "filter__israel" in classes:
            region = "Israel"
        # Don't use exit blurb as description for tagging when that's all there is
        tag_desc = desc
        if status in ("Acquired", "Public") and desc and desc.lower().startswith(("acquired", "ipo", "public")):
            tag_desc = None
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "exit_detail": exit_detail,
            "stage": None,
            "sectors": sectors,
            "region": region,
            "everywhere_tags": classify(name, tag_desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
