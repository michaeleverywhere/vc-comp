#!/usr/bin/env python3
"""Chiratae Ventures portfolio scraper -> chiratae_companies.json
Source: https://chiratae.com/companies/ — Elementor company cards (h2 name,
external website, year in paragraph).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social, year_of
from _d20_common import write_out

SOURCE_URL = "https://chiratae.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "chiratae_companies.json")
PRIMARY = "Chiratae Ventures"
TAG_OVERRIDES = {}
SKIP = {"chiratae sonic deeptech program application is now open!", "chiratae sonic deeptech program applicat"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for h in soup.find_all("h2"):
        name = clean(h.get_text(" "))
        if not name or name.lower() in SKIP or len(name) > 80:
            continue
        if "chiratae" in name.lower() and len(name) > 20:
            continue
        if name.lower() in seen:
            continue
        parent = h.find_parent(["div", "article", "section"])
        website = desc = None
        year = None
        if parent:
            for a in parent.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and "chiratae" not in href and not is_social(href):
                    website = clean_url(href)
                    break
            for p in parent.find_all("p"):
                t = clean(p.get_text(" "))
                if not t:
                    continue
                if re.fullmatch(r"(19|20)\d{2}", t):
                    year = int(t)
                elif len(t) > 40 and not desc:
                    desc = t
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "first_invested": year,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
