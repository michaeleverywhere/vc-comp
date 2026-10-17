#!/usr/bin/env python3
"""Avaana Capital portfolio scraper -> avaana_companies.json
Source: https://avaanacapital.com/ — homepage portfolio slider: company name
(site-authored logo alt), one-line description and profile page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://avaanacapital.com/"
PRIMARY = "Avaana Capital"


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
    for img in s.select("div.slide-image img[alt]"):
        nm = clean(img.get("alt"))
        box = img.find_parent("div", class_="slide-image")
        if not nm or nm.lower() in seen or nm.lower() == "avaana capital":
            continue
        seen.add(nm.lower())
        a = box.find_parent("a") or box.select_one("a[href]")
        d = " ".join(box.stripped_strings) or None
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, detail_url=urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else None))
    finish(out, "avaana", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
