#!/usr/bin/env python3
"""Character portfolio scraper -> character_companies.json
Source: https://www.character.vc/ — homepage portfolio name+website links.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://www.character.vc/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "character_companies.json")
PRIMARY = "Character"
TAG_OVERRIDES = {}
SKIP = {"get in touch", "subscribe to weekly updates", "lenny’s podcast", "lenny's podcast",
        "our feature in upstarts", "our backstory", "contact", "updates"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href^=http]"):
        href = a["href"]
        if "character.vc" in href or is_social(href) or "lenny" in href or "johnzeratsky" in href or "upstartsmedia" in href:
            continue
        name = clean(a.get_text(" "))
        if not name or len(name) > 40 or name.lower() in SKIP:
            continue
        if name.lower() in seen:
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
