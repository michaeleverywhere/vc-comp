#!/usr/bin/env python3
"""M25 portfolio scraper -> m25_companies.json
Source: https://www.m25vc.com/portfolio — Webflow CMS logo grid (Midwest seed fund): company name from
the Finsweet `fs-cmsfilter-element` attribute, description from the logo alt
text, status field and detail page. 'Unannounced ...' placeholders are skipped."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.m25vc.com/portfolio"
PRIMARY = "M25"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select(".logo-item.w-dyn-item"):
        nm = clean(it.get("fs-cmsfilter-element"))
        if not nm or nm.lower().startswith("unannounced"):
            continue
        img = it.find("img")
        alt = clean(img.get("alt")) if img else None
        st = txt(it.select_one("[fs-cmsfilter-field='status']"))
        a = it.select_one("a[href]")
        out.append(rec(nm, alt if alt and alt != nm else None, None, PRIMARY, SOURCE_URL, scraped_at, portfolio_status=st,
                       status={"active": "active", "exited": "exited", "acquired": "acquired"}.get((st or "").lower()),
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "m25", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
