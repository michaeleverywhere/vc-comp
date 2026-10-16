#!/usr/bin/env python3
"""Ubiquity Ventures portfolio scraper -> ubiquity_companies.json
Source: https://www.ubiquity.vc/portfolio — portfolio cards: company name,
website, category, stage, city and description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.ubiquity.vc/portfolio"
PRIMARY = "Ubiquity Ventures"


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
    for c in s.select("div.flex.min-h-0"):
        h = c.select_one("h3")
        a = h.select_one("a") if h else None
        nm = clean(re.sub(r"\s*↗\s*$", "", h.get_text(" ", strip=True))) if h else None
        if not nm:
            continue
        cats = [txt(x) for x in c.select("a.chip-link[href*='category=']") if txt(x)]
        stg = next((txt(x) for x in c.select("a.chip-link[href*='stage=']")), None)
        out.append(rec(nm, txt(c.select_one("p.leading-relaxed")), site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=cats, stage=stg,
                       city=txt(c.select_one("p.text-xs span"))))
    finish(out, "ubiquity", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
