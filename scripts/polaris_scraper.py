#!/usr/bin/env python3
"""Polaris Partners portfolio scraper -> polaris_companies.json
Source: WP REST /wp-json/wp/v2/company-api with rich ACF (description, website,
location, healthcare/technology, exit_info, CEO).
"""
import os, re, sys, html as htmlmod
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, html_text
from _d20_common import write_out

SOURCE_URL = "https://www.polarispartners.com/companies/"
REST = "https://www.polarispartners.com/wp-json/wp/v2/company-api?per_page=100&page={}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "polaris_companies.json")
PRIMARY = "Polaris Partners"
SECTOR_MAP = {"healthcare": ["Health"], "technology": []}
TAG_OVERRIDES = {}


def norm_url(u):
    u = clean(u)
    if not u:
        return None
    if not u.startswith("http"):
        u = "https://" + u
    return clean_url(u)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts, page = [], 1
    while True:
        batch = fetch(REST.format(page), as_json=True)
        if not batch:
            break
        posts += batch
        if len(batch) < 100:
            break
        page += 1
    out, seen = [], set()
    for p in posts:
        name = clean(htmlmod.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        acf = p.get("acf") or {}
        desc = html_text(acf.get("text") or "")
        website = norm_url(acf.get("website"))
        location = clean(acf.get("location"))
        sectors = [s.title() for s in (acf.get("healthcare_or_technology") or []) if s]
        exit_info = clean(acf.get("exit_info"))
        status = None
        acquirer = None
        if exit_info:
            status = "acquired" if re.search(r"(?i)acquir", exit_info) else "public" if re.search(r"(?i)ipo|nasdaq|nyse", exit_info) else "acquired"
            m = re.search(r"(?i)acquir(?:ed)?\s+by\s+(.+)", exit_info)
            if m:
                acquirer = clean(m.group(1))
        founders = []
        for i in ("", "_2", "_3"):
            cn = clean(acf.get(f"ceo_name{i}"))
            if cn:
                founders.append(cn)
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "location": location,
            "sectors": sectors,
            "status": status,
            "acquirer": acquirer,
            "exit_info": exit_info,
            "founders": founders,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "location", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
