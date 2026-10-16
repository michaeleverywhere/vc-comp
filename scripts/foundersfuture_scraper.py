#!/usr/bin/env python3
"""Founders Future portfolio scraper -> foundersfuture_companies.json
Source: https://www.foundersfuture.com/en/portfolio — Webflow CMS list
(paginated) of `.founders-collection2_item` cards: company name, description,
visible "Exit" tag, Sector, Stage and year (the site's "founded" field), plus
the company detail page link.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.foundersfuture.com/en/portfolio"
PRIMARY = "Founders Future"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "healthtech": ["Health"], "climate tech": ["Climate / Sustainability"],
              "consumer": ["Consumer"], "future of work": ["Future of Work"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".founders-collection2_item.w-dyn-item"):
            t = it.select_one(".founders-content_title .text-size-xlarge")
            if not t:
                continue
            tag = it.select_one(".founders-content_tag")
            exited = bool(tag) and "w-condition-invisible" not in (tag.get("class") or [])
            p = it.select_one(".founders-content_header p")
            secs = [clean(x.get_text(" ", strip=True)) for x in it.select("[fs-list-field=sectors]")]
            stages = [clean(x.get_text(" ", strip=True)) for x in it.select("[fs-list-field=stade]")]
            yr = it.select_one("[fs-cmsfilter-field=founded]")
            a = it.select_one("a.founders-collection2_link[href]")
            out.append(rec(t.get_text(" ", strip=True), p.get_text(" ", strip=True) if p else None, None, PRIMARY,
                           SOURCE_URL, scraped_at, sectors=[s for s in secs if s], sector_map=SECTOR_MAP,
                           stage=", ".join(s for s in stages if s) or None,
                           founded_year=year_of(yr.get_text() if yr else ""),
                           status="exited" if exited else None, detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "foundersfuture", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
