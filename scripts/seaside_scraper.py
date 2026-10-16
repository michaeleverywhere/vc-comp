#!/usr/bin/env python3
"""Seaside Ventures portfolio scraper -> seaside_companies.json
Source: https://www.seasideventures.com/portfolio — Webflow CMS portfolio cards: company
name, category, description, stage, year and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.seasideventures.com/portfolio"
PRIMARY = "Seaside Ventures"


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
    for a in s.select("a.card.portfolio-row-card"):
        h = a.find("h2")
        nm = txt(h)
        if not nm:
            continue
        cat = txt(h.find_previous_sibling("div")) if h else None
        out.append(rec(nm, txt(a.find("p")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [],
                       stage=txt(a.select_one("[class*='stage-']")), year=year_of(txt(a.select_one(".year"))),
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a.get("href") else None))
    finish(out, "seaside", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
