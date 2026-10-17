#!/usr/bin/env python3
"""Motivate Ventures portfolio scraper -> motivate_companies.json
Source: https://motivate.vc/portfolio/ — portfolio grid (name, one-line description,
location) plus each /portfolio/<slug>/ page for the company website (and the name
from the page title where the logo has no alt text)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://motivate.vc/portfolio/"
PRIMARY = "Motivate Ventures"


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
    items = []
    for it in s.select("div.portfolio-item"):
        img = it.select_one(".portfolio-item-logo img")
        nm = clean(img.get("alt")) if img else None
        a = it.find("a")
        if a:
            items.append((nm, txt(it.select_one(".portfolio-item-excerpt")), txt(it.select_one(".portfolio-item-location")), a["href"]))
    pages = fetch_many([u for *_, u in items])
    for nm, d, loc, u in items:
        p = BeautifulSoup(pages.get(u) or "", "html.parser")
        if not nm and p.title:
            nm = clean(re.sub(r"\s*-\s*Motivate Venture Capital\s*$", "", p.title.get_text()))
        if not nm:
            continue
        out.append(rec(nm, d, site(p.select_one("a.btn-url")), PRIMARY, SOURCE_URL, scraped_at, location=loc, detail_url=u))
    finish(out, "motivate", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
