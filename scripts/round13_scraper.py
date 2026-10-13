#!/usr/bin/env python3
"""Round13 Capital portfolio scraper -> round13_companies.json
Source: https://round13.com/portfolio/ — Elementor grid; names from detail slug;
detail pages for description + website.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, first_external_link,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://round13.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "round13_companies.json")
PRIMARY = "Round13 Capital"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".eael-grid-post"):
        a = it.select_one("a[href*='/portfolio/']")
        detail = urljoin(SOURCE_URL, a["href"]) if a else None
        if not detail or detail.rstrip("/") == SOURCE_URL.rstrip("/"):
            continue
        slug = detail.rstrip("/").split("/")[-1]
        name = clean(slug.replace("-", " ").title())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
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
    pages = fetch_many([r["detail_url"] for r in out if r.get("detail_url")], workers=5, pause=0.15)
    for r in out:
        detail = r.pop("detail_url", None)
        html = pages.get(detail)
        if not html:
            r["everywhere_tags"] = tags_for(r["company_name"], None)
            continue
        ds = BeautifulSoup(html, "html.parser")
        # prefer on-page H1 as canonical name
        h1 = ds.select_one("h1")
        if h1 and clean(h1.get_text(" ")):
            r["company_name"] = clean(h1.get_text(" "))
        for p in ds.select(".elementor-widget-theme-post-content p, .elementor-widget-text-editor p, article p, p"):
            t = clean(p.get_text(" "))
            if t and len(t) > 50 and "Round13" not in t:
                r["description"] = t
                break
        url = first_external_link(ds, ("round13.com",))
        r["company_url"] = clean_url(url) if url else None
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
