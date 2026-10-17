#!/usr/bin/env python3
"""UpHonest Capital portfolio scraper -> uphonest_companies.json
Source: https://www.uphonestcapital.com/portfolios — Webflow portfolio: featured company cards (name,
category) and accordion list (name, description, category, founder, year invested, website)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.uphonestcapital.com/portfolios"
PRIMARY = "UpHonest Capital"


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
    seen = {}
    for it in s.select("div.fpl-accordion.w-dyn-item"):
        nm = txt(it.select_one(".fpl-title"))
        if not nm or nm.lower() in seen:
            continue
        info = {txt(b.select_one(".fpl-info-title")): txt(b.select_one(".fpl-info-content")) for b in it.select(".fpl-info-block, .fpl-info-block-long")}
        a = next((x for x in it.select("a.icon-link[href^=http]") if x.select_one("img[alt='Website Link']")), None)
        cats = [txt(x) for x in it.select("[fs-cmsfilter-field=categories]") if txt(x)]
        seen[nm.lower()] = 1
        out.append(rec(nm, txt(it.select_one(".fpl-short-description")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=cats, founders=info.get("Founder"), invested_year=info.get("Invested in")))
    for it in s.select("div.upl-collection-item.w-dyn-item"):
        p = [clean(x) for x in it.stripped_strings if clean(x) and "browser" not in x and x != "●"]
        if len(p) < 2:
            continue
        nm = p[1]
        if nm.lower() in seen:
            continue
        seen[nm.lower()] = 1
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[p[0]]))
    finish(out, "uphonest", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
