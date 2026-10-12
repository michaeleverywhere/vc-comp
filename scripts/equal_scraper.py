#!/usr/bin/env python3
"""Equal Ventures portfolio scraper -> equal_companies.json
Source: https://www.equal.vc/portfolio — Webflow; .portfolio-item cards with name
(img alt / link text) and detail pages carrying description + company website.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, first_external_link,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.equal.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "equal_companies.json")
PRIMARY = "Equal Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio-item"):
        a = it.select_one("a[href]")
        img = it.select_one("img[alt]")
        name = clean(img.get("alt") if img else None) or clean(it.get_text(" "))
        if not name or name.lower() in seen or name.startswith("(") or name == "No items found.":
            continue
        seen.add(name.lower())
        detail = urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else None
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "detail_url": detail,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    pages = fetch_many([r["detail_url"] for r in out if r.get("detail_url")], workers=6, pause=0.15)
    for r in out:
        html = pages.get(r.pop("detail_url", None))
        if not html:
            r["everywhere_tags"] = tags_for(r["company_name"], None)
            continue
        ds = BeautifulSoup(html, "html.parser")
        # description: first substantial paragraph on the page about the company
        for p in ds.select("p"):
            t = clean(p.get_text(" "))
            if t and len(t) > 40 and r["company_name"].split()[0].lower() in t.lower():
                r["description"] = t
                break
        if not r["description"]:
            for p in ds.select("p"):
                t = clean(p.get_text(" "))
                if t and len(t) > 60 and not t.lower().startswith(("equal", "portfolio", "careers")):
                    r["description"] = t
                    break
        r["company_url"] = clean_url(first_external_link(ds, ("equal.vc", "ashbyhq.com", "medium.com", "altalogy.com")))
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
