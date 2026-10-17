#!/usr/bin/env python3
"""137 Ventures portfolio scraper -> 137ventures_companies.json
Source: https://www.137ventures.com/portfolio — Webflow portfolio grid plus each
/portfolio/<slug> page: company name (h1), description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.137ventures.com/portfolio"
PRIMARY = "137 Ventures"


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
    links = []
    for a in s.select("a.portfolio-collection-list-item-link[href^='/portfolio/']"):
        u = urljoin(SOURCE_URL, a["href"])
        if u not in links:
            links.append(u)
    pages = fetch_many(links)
    for u in links:
        if not pages.get(u):
            continue
        d = BeautifulSoup(pages[u], "html.parser")
        nm = txt(d.select_one("h1.post-h3")) or txt(d.find("h1"))
        if not nm:
            continue
        w = next((a for a in d.select("a.link-with-icon") if txt(a) == "Website"), None)
        out.append(rec(nm, txt(d.select_one(".post-info-wrapper .w-richtext")), site(w), PRIMARY, SOURCE_URL, scraped_at, detail_url=u))
    finish(out, "137ventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
