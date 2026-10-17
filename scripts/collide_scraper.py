#!/usr/bin/env python3
"""Collide Capital portfolio scraper -> collide_companies.json
Source: https://www.collidecap.com/portfolio — Webflow CMS list (Finsweet filters),
paginated via the list's ?<id>_page=N "next" link: company name, website (card link),
CEO name, thesis tag (Fintech / Supply Chain / Future of Work …), entry year (first
invested), description, location, business model (B2B/B2C), sector tag and the
"Acquired" flag."""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.collidecap.com/portfolio"
PRIMARY = "Collide Capital"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "supply chain": ["Logistics / Supply Chain"],
              "future of work": ["Future of Work"]}


def field(it, f):
    el = it.select_one(f'[fs-cmsfilter-field="{f}"]')
    if not el or "w-dyn-bind-empty" in (el.get("class") or []):
        return None
    return clean(el.get_text(" ", strip=True))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, url, seen_pages = [], SOURCE_URL, set()
    while url and url not in seen_pages and len(seen_pages) < 40:
        seen_pages.add(url)
        s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
        for it in s.select(".portfolio-cms2 .w-dyn-item"):
            name = field(it, "name")
            if not name:
                continue
            a = it.select_one("a[href]")
            href = (a.get("href") or "").strip() if a else ""
            acq = (field(it, "Acquired") or "").lower().startswith("true")
            yr = field(it, "year")
            thesis, tag = field(it, "tag"), field(it, "tags")
            ceo = it.select_one('[fs-cmsfilter-field="ceo"]')
            out.append(rec(name, field(it, "description"), href if href.startswith("http") and not is_social(href) else None,
                           PRIMARY, SOURCE_URL, scraped_at, sectors=[x for x in (thesis, tag) if x], sector_map=SECTOR_MAP,
                           thesis=thesis, location=field(it, "location"), business_model=field(it, "bm"),
                           ceo=clean(ceo.get_text(" ", strip=True)) if ceo else None,
                           first_invested=int(yr) if yr and yr.isdigit() else None,
                           status="acquired" if acq else "active"))
        nxt = s.select_one("a.w-pagination-next[href]")
        url = urljoin(SOURCE_URL, nxt["href"]) if nxt else None
    finish(out, "collide", ("description", "company_url", "location", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
