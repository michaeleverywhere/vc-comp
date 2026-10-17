#!/usr/bin/env python3
"""Kearny Jackson portfolio scraper -> kearnyjackson_companies.json
Source: https://www.kearnyjackson.com/ — Webflow CMS portfolio cards (paginated via
the list's ?<id>_page=N "next" link): company name, industry filter tag (Consumer /
Robotics / AI/SaaS / Infrastructure / Fintech) and one-line description. Cards carry
no website links."""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.kearnyjackson.com/"
PRIMARY = "Kearny Jackson"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "robotics": ["Deeptech / Robotics / AR/VR"],
              "infrastructure": ["Dev Tools / Cloud"], "consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, url, seen = [], SOURCE_URL, set()
    while url and url not in seen and len(seen) < 30:
        seen.add(url)
        s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
        for e in s.select(".w-condition-invisible"):
            e.decompose()
        for it in s.select(".portfolio_card-item"):
            top = it.select_one(".portfolio_card-content-top > div")
            name = clean(top.get_text(" ", strip=True)) if top else None
            if not name:
                continue
            inds = [clean(x.get_text(" ", strip=True)) for x in it.select('[fs-cmsfilter-field="industry"]')]
            inds = [x for x in inds if x and x != "All"]
            d = it.select_one(".portfolio_card-description-ph")
            a = it.select_one("a[href]")
            href = (a.get("href") or "") if a else ""
            out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None,
                           href if href.startswith("http") else None, PRIMARY, SOURCE_URL, scraped_at,
                           sectors=inds, sector_map=SECTOR_MAP, status="active"))
        nxt = s.select_one("a.w-pagination-next[href]")
        url = urljoin(url, nxt["href"]) if nxt else None
    finish(out, "kearnyjackson", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
