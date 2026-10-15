#!/usr/bin/env python3
"""VestedVC portfolio scraper -> vestedvc_companies.json
Source: https://www.vestedvc.com/portfolio — SSR cards with h3 name, status
(Active/Exit), and company website link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.vestedvc.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "vestedvc_companies.json")
PRIMARY = "VestedVC"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for h in soup.select("h3"):
        name = clean(h.get_text(" "))
        if not name or name.lower() in seen:
            continue
        # walk up to card container
        card = h
        for _ in range(6):
            if card.parent:
                card = card.parent
        text = card.get_text(" ", strip=True)
        status = None
        if "exit" in text.lower():
            status = "acquired"
        elif "active" in text.lower():
            status = "active"
        website = None
        for a in card.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http") and "vestedvc.com" not in href and not any(x in href for x in ("linkedin", "twitter", "facebook", "youtube")):
                website = clean_url(href)
                break
        # description: short blurb near name if present
        desc = None
        for el in card.select("p"):
            t = clean(el.get_text(" "))
            if t and len(t) > 30 and t.lower() not in ("active", "exit"):
                desc = t
                break
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "sectors": [],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
