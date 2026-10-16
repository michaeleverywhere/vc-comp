#!/usr/bin/env python3
"""SKY VC (formerly JetBlue Ventures) portfolio scraper -> skyvc_companies.json
Source: https://www.sky-vc.com/portfolio — Webflow CMS `.portfolio_content`
items: name and summary (Finsweet fields), data-status (Acquired/...), a
hidden category field and a detail page /portfolio-companies/<slug>.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.sky-vc.com/portfolio"
PRIMARY = "SKY VC"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".portfolio_content[data-portfolio-item]"):
        nm = it.select_one("[fs-cmsfilter-field='name']")
        if not nm or not clean(nm.get_text()):
            continue
        sm = it.select_one("[fs-cmsfilter-field='summary']")
        cats = [clean(h.get_text(" ", strip=True)) for h in it.select(".hide[fs-cmsfilter-field]")]
        st = clean(it.get("data-status"))
        a = it.select_one("a[href]")
        out.append(rec(nm.get_text(" ", strip=True), sm.get_text(" ", strip=True) if sm else None, None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=[c for c in cats if c], portfolio_status=st,
                       status={"acquired": "acquired", "active": "active", "exited": "exited", "ipo": "public"}.get((st or "").lower()),
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "skyvc", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
