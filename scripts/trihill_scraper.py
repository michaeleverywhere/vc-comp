#!/usr/bin/env python3
"""Trihill Capital portfolio scraper -> trihill_companies.json
Source: https://trihillcapital.com/portfolio/ — Elementor portfolio cards: company
name, sector tags, description and profile page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://trihillcapital.com/portfolio/"
PRIMARY = "Trihill Capital"


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
    seen = set()
    for a in s.select("a.elementor-element-ad19884"):
        nm = txt(a.select_one(".elementor-heading-title"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        tags = [txt(x) for x in a.find_all("span") if txt(x) and not x.find_parent(class_="elementor-heading-title")]
        d = txt(a.select_one(".elementor-element-0d2144e"))
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, sectors=tags, detail_url=a.get("href")))
    finish(out, "trihill", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
