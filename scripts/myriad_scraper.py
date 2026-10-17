#!/usr/bin/env python3
"""Myriad Venture Partners portfolio scraper -> myriad_companies.json
Source: https://www.myriadventures.com/portfolio — Webflow/Finsweet accordion rows (all
paginated pages): company name, website, sector, stage, status, domain and description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.myriadventures.com/portfolio"
PRIMARY = "Myriad Venture Partners"


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
    url, seen = SOURCE_URL, set()
    while url and url not in seen:
        seen.add(url)
        s = soup_of(url)
        for it in s.select(".portfolio-item.w-dyn-item"):
            a = it.select_one("a.style-h6")
            nm = txt(a)
            if not nm:
                continue
            cols = it.select(".portfolio-row > .text-size-medium")
            sec = txt(cols[0]) if cols and not cols[0].get("fs-cmsfilter-field") else None
            st = txt(it.select_one("[fs-cmsfilter-field='status']"))
            out.append(rec(nm, txt(it.select_one(".portfolio-body-text")), site(a), PRIMARY, SOURCE_URL, scraped_at,
                           sectors=[sec] if sec else [], stage=txt(it.select_one("[fs-cmsfilter-field='stage']")), portfolio_status=st,
                           status="exited" if st and ("exit" in st.lower() or "acqui" in st.lower()) else None,
                           domain=txt(it.select_one("[fs-cmsfilter-field='domain']"))))
        nxt = s.select_one("a.w-pagination-next[href]")
        url = urljoin(SOURCE_URL, nxt["href"]) if nxt else None
    finish(out, "myriad", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
