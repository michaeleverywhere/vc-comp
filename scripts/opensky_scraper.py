#!/usr/bin/env python3
"""OpenSky Ventures portfolio scraper -> opensky_companies.json
Source: https://www.opensky.vc — Wix homepage portfolio: company name
(linked, "Name >"), one-line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.opensky.vc"
PRIMARY = "OpenSky Ventures"


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
    for a in s.select("a[href^='http']"):
        t = a.get_text()
        if not re.search(r"\S\s*>\s*$", t):
            continue
        nm = clean(t.replace("\u200b", "").rstrip(" >"))
        if not nm:
            continue
        p = a.find_parent("p")
        d = None
        for q in (p.find_next_siblings("p") if p else []):
            d = clean(q.get_text().replace("\u200b", ""))
            if d:
                break
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "opensky", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
