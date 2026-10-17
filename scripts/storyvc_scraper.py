#!/usr/bin/env python3
"""Story Ventures portfolio scraper -> storyvc_companies.json
Source: https://www.storyventures.vc/portfolio — Webflow portfolio table: company name,
description, category, leaders and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.storyventures.vc/portfolio"
PRIMARY = "Story Ventures"


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
    for it in s.select(".portfolio_table-list > .w-dyn-item"):
        nm = txt(it.select_one(".hightlights_title"))
        if not nm:
            continue
        cats = [txt(x) for x in it.select("[fs-cmsfilter-field='category']") if txt(x)]
        leaders = [txt(x.find("div")) for x in it.select("a.leader_title") if txt(x.find("div"))]
        d = txt(it.select_one(".highlights_details-container p"))
        out.append(rec(nm, f"{nm} {d}" if d and d[:1].islower() else d, site(it.select_one("a.portolio_logo-link")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=cats, founders=leaders))
    finish(out, "storyvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
