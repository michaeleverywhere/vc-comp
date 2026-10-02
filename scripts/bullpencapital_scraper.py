#!/usr/bin/env python3
"""Bullpen Capital portfolio scraper -> bullpencapital_companies.json
Source: https://bullpencap.com/companies — Webflow CMS collection.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://bullpencap.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "bullpencapital_companies.json")
PRIMARY = "Bullpen Capital"


def field_value(item, label):
    for block in item.select(".companies_content_list_item"):
        if "w-condition-invisible" in (block.get("class") or []):
            continue
        title = block.select_one(".companies_content_list_item_title")
        val = block.select_one(".companies_content_list_item_title_content")
        if title and clean(title.get_text()) == label and val:
            return clean(val.get_text())
    return None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    wrap = soup.select_one(".companies_collection_list_wrapper") or soup
    out, seen = [], set()
    for it in wrap.select(".companies_collection_ltem, .w-dyn-item"):
        name_el = it.select_one("h3.c-title, h3")
        name = clean(name_el.get_text()) if name_el else None
        if not name or name.lower() in seen:
            continue
        # skip filter chips
        if name.lower() in {"all", "consumer", "enterprise", "gaming", "fintech"}:
            continue
        seen.add(name.lower())
        desc_el = it.select_one(".companies_short_description")
        desc = clean(desc_el.get_text()) if desc_el else None
        website = None
        for a in it.select("a.companies_btn[href], a[href^='http']"):
            href = a.get("href") or ""
            if href.startswith("http") and "bullpen" not in href and "webflow" not in href:
                website = clean(href)
                break
        model = field_value(it, "Model")
        category = field_value(it, "Category")
        status_raw = field_value(it, "Status")
        invested = field_value(it, "Invested in")
        status = "Active"
        if status_raw:
            sl = status_raw.lower()
            if any(x in sl for x in ("exit", "acquired", "ipo", "public")):
                status = "Exited"
        sectors = [s for s in (category, model) if s]
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "sectors": sectors or None,
            "investment_year": invested,
            "everywhere_tags": classify(name, desc, sectors)[:4],
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
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
