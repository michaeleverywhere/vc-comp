#!/usr/bin/env python3
"""Galaxy Ventures portfolio scraper -> galaxyventures_companies.json
Source: https://ventures.galaxy.com/portfolio — portfolio modal entries: company name (logo alt),
description, website and category."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://ventures.galaxy.com/portfolio"
PRIMARY = "Galaxy Ventures"


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
    for m in s.select(".portfolio-filter__modal-info"):
        img = m.find("img")
        nm = clean(img.get("alt")) if img else None
        if not nm:
            continue
        w = next((a for a in m.select(".portfolio-filter__modal-links a") if txt(a) == "Website"), None)
        cat = txt(m.select_one(".portfolio-filter__modal-type"))
        out.append(rec(nm, txt(m.select_one(".portfolio-filter__modal-description")), site(w), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cat] if cat else []))
    finish(out, "galaxyventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
