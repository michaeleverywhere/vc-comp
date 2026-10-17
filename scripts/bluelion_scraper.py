#!/usr/bin/env python3
"""Blue Lion Global portfolio scraper -> bluelion_companies.json
Source: https://www.bluelion.co/ — Webflow/Finsweet portfolio grid: company
name (logo alt), investment status (Current/Prior), industry and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.bluelion.co/"
PRIMARY = "Blue Lion Global"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for a in s.select("a.portfolio_item-gsap-blue"):
        img = a.find("img")
        nm = clean(re.sub(r"(?i)\s*logo$", "", img.get("alt") or "")) if img else None
        if not nm:
            continue
        st = txt(a.select_one("[fs-cmsfilter-field='investment-status']"))
        ind = txt(a.select_one("[fs-cmsfilter-field='investment-industry']"))
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[ind] if ind else [], portfolio_status=st,
                       status="active" if st == "Current" else ("prior" if st == "Prior" else None)))
    finish(out, "bluelion", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
