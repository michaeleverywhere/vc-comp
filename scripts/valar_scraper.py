#!/usr/bin/env python3
"""Valar Ventures portfolio scraper -> valar_companies.json
Source: https://www.valar.com/ — Next.js homepage portfolio cards: company name, long
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.valar.com/"
PRIMARY = "Valar Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select("div.company"):
        card = it.select_one(".card")
        nm = txt(card.select_one(".name")) if card else None
        if not nm:
            continue
        out.append(rec(nm, txt(card.select_one(".desc")), site(card.select_one("a.url")), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "valar", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
