#!/usr/bin/env python3
"""Moderne Ventures portfolio scraper -> moderne_companies.json
Source: https://www.moderneventures.com/portfolio — Webflow/Finsweet portfolio cards: company
name, tagline, description, website, programme type and exit tag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.moderneventures.com/portfolio"
PRIMARY = "Moderne Ventures"


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
    for it in s.select("div.portfolio-item"):
        nm = txt(it.select_one(".text-block-27"))
        if not nm:
            continue
        tag = txt(it.select_one(".portfolio-tag"))
        a = it.select_one("a.portfolio-link")
        out.append(rec(nm, txt(it.select_one(".portoflio-description")) or txt(it.select_one(".text-block-29")), site(it.select_one("a.portfolio-card-link")), PRIMARY, SOURCE_URL, scraped_at,
                       tagline=txt(it.select_one(".text-block-29")), programme=txt(it.select_one(".portfolio-card-type")),
                       status="exited" if tag and "exit" in tag.lower() else None, detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "moderne", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
