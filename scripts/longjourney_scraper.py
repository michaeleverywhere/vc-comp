#!/usr/bin/env python3
"""Long Journey Ventures portfolio scraper -> longjourney_companies.json
Source: https://www.longjourney.vc/portfolio — Squarespace logo/link grid;
name from domain, website from anchor.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://www.longjourney.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "longjourney_companies.json")
PRIMARY = "Long Journey Ventures"
TAG_OVERRIDES = {}
# Well-known domain -> display name
DOMAIN_NAMES = {
    "spacex": "SpaceX", "deepmind": "DeepMind", "anduril": "Anduril",
    "postmates": "Postmates", "thumbtack": "Thumbtack", "affirm": "Affirm",
    "notion": "Notion", "uber": "Uber", "carta": "Carta", "crusoe": "Crusoe",
}


def name_from_url(url):
    host = urlparse(url).netloc.lower().replace("www.", "")
    base = host.split(".")[0]
    if base in DOMAIN_NAMES:
        return DOMAIN_NAMES[base]
    return base.replace("-", " ").title() if base else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href^=http]"):
        href = a["href"]
        if "longjourney" in href or is_social(href):
            continue
        img = a.find("img")
        if not img:
            continue
        name = name_from_url(href)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(href),
            "everywhere_tags": tags_for(name, None),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
