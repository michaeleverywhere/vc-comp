#!/usr/bin/env python3
"""Endurance28 portfolio scraper -> endurance28_companies.json
Source: https://www.endurance28.com/portfolio/ — founder gallery: each tile links to a company
page giving the company name (page title), sector, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.endurance28.com/portfolio/"
PRIMARY = "Endurance28"


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
    tiles = []
    for a in s.select(".uael-grid-item-content a[href]"):
        cap = txt(a.select_one(".uael-grid-caption-text"))
        img = a.select_one("img")
        if cap:
            tiles.append((cap, a["href"], clean(img.get("alt")) if img else None))
    pages = fetch_many([u for _, u, _ in tiles])
    for cap, u, founder in tiles:
        nm, sec, desc, web = None, None, None, None
        h = pages.get(u)
        if h:
            d = BeautifulSoup(h, "html.parser")
            t = txt(d.title) or ""
            nm = clean(t.rsplit(" – ", 1)[0]) if " – " in t else None
            h4 = next((x for x in d.select("h4") if " — " in (txt(x) or "")), None)
            web = None
            if h4:
                sec = txt(h4)
                p = h4.find_next("p")
                desc = txt(p)
                web = site(p.select_one("a[href^='http']")) if p else None
        out.append(rec(nm or cap, desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=[x.strip() for x in sec.split(" — ")] if sec else [],
                       founders=[founder] if founder else [], detail_url=u))
    finish(out, "endurance28", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
