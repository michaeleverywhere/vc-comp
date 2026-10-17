#!/usr/bin/env python3
"""CSC Upshot Ventures portfolio scraper -> upshot_companies.json
Source: https://csc-upshot.vc/portfolio/ — portfolio tiles (paginated): company name,
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://csc-upshot.vc/portfolio/"
PRIMARY = "CSC Upshot Ventures"


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
        for it in s.select(".one_fourth"):
            nm = txt(it.select_one("h3"))
            if not nm:
                continue
            a = next((x for x in it.select("a[href^='http']") if site(x)), None)
            out.append(rec(nm, txt(it.select_one(".overlay-content-holder p")) or txt(it.select_one("p")), site(a), PRIMARY, SOURCE_URL, scraped_at))
        nx = s.select_one("a.next[href], .pagination a[href*='/page/']:-soup-contains('Next'), a.nextpostslink[href]")
        url = urljoin(url, nx["href"]) if nx else None
    finish(out, "upshot", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
