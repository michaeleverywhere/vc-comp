#!/usr/bin/env python3
"""Vine Ventures portfolio scraper -> vine_companies.json
Source: https://vineventures.com/ — homepage portfolio sidebar panels: company name,
sectors, location, website, description and founders."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://vineventures.com/"
PRIMARY = "Vine Ventures"


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
    for p in s.select("div.home-section-portfolio-list-sidebar-hold"):
        nm = clean((txt(p.select_one(".hsplist-sidebar-title")) or "").rstrip("*"))
        if not nm:
            continue
        tx = p.select(".hsplist-sidebar-text")
        sec, loc = [], None
        if tx and tx[0].find("p"):
            parts = [clean(x) for x in tx[0].find("p").stripped_strings if clean(x)]
            for x in parts:
                if x.lower().startswith("in "):
                    loc = clean(x[3:])
                else:
                    sec += [clean(y) for y in x.split(",") if clean(y)]
        fnd = [txt(x) for x in p.select(".hsplist-sidebar-founder span") if txt(x)]
        out.append(rec(nm, txt(tx[1]) if len(tx) > 1 else None, site(p.select_one("a.link-white-arrow")), PRIMARY, SOURCE_URL,
                       scraped_at, sectors=sec, location=loc, founders=", ".join(fnd) or None))
    finish(out, "vine", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
