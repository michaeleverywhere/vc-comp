#!/usr/bin/env python3
"""Flagship Pioneering portfolio scraper -> flagship_companies.json
Source: https://www.flagshippioneering.com/companies — grid of .companies__grid-link
with name (title/alt) and founding year; detail pages publish description.
Bio/health company builder — no funding round labels on the index.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, first_external_link,
                             year_of, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.flagshippioneering.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "flagship_companies.json")
PRIMARY = "Flagship Pioneering"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.companies__grid-link[href]"):
        name = clean(a.get("title") or a.get("alt"))
        if not name:
            img = a.select_one("img[alt]")
            name = clean(img.get("alt")) if img else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        year = year_of(a.get_text(" "))
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "first_invested": year,  # year shown is company launch year at Flagship
            "founded_year": year,
            "detail_url": a["href"] if a["href"].startswith("http") else "https://www.flagshippioneering.com" + a["href"],
            "everywhere_tags": ["BioTech", "Health"],  # Flagship is a bio company builder; refined below
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    pages = fetch_many([r["detail_url"] for r in out], workers=6, pause=0.15)
    for r in out:
        html = pages.get(r.pop("detail_url", None))
        if html:
            ds = BeautifulSoup(html, "html.parser")
            # meta description or first long p
            md = ds.select_one('meta[name="description"]')
            if md and md.get("content") and len(md["content"]) > 40:
                r["description"] = clean(md["content"])
            if not r["description"]:
                for p in ds.select("p"):
                    t = clean(p.get_text(" "))
                    if t and len(t) > 80:
                        r["description"] = t
                        break
            r["company_url"] = clean_url(first_external_link(ds, ("flagshippioneering.com",)))
        # retag from description; keep BioTech bias via sector map empty + keyword
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"), ["biotech", "health"], {
            "biotech": ["BioTech"], "health": ["Health"],
        })
        if not r["everywhere_tags"]:
            r["everywhere_tags"] = ["BioTech"]
    prune_substring_tags(out, {"biotech": ["BioTech"], "health": ["Health"]})
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "founded_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
