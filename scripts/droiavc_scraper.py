#!/usr/bin/env python3
"""Droia Ventures portfolio scraper -> droiavc_companies.json
Source: https://droiaventures.com/ — homepage portfolio gallery: company name (site-
authored image alt), description caption and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://droiaventures.com/"
PRIMARY = "Droia Ventures"


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
    for a in s.select("a[href^='http']"):
        img = a.select_one(".masonry_gallery_image_holder img[alt]")
        nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen or len(nm.split()) > 6:
            continue
        seen.add(nm.lower())
        d = txt(a.select_one("h3"))
        d = clean(re.sub(r"\s+—\s+\S+$", "", d)) if d else None
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "droiavc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
