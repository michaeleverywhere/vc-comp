#!/usr/bin/env python3
"""Chengwei Capital portfolio scraper -> chengwei_companies.json
Source: https://chengwei.com/ — homepage portfolio wall: company name (site-
authored logo alt; hover-state ' w' duplicates collapsed) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://chengwei.com/"
PRIMARY = "Chengwei Capital"


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
        if 'chengwei.com' in a["href"]:
            continue
        img = a.find("img", alt=True)
        nm = clean(re.sub(r"(?i)\s*(logo)?\s*$", "", img.get("alt") or "")) if img else None
        if not nm or re.search(r"\.(png|jpe?g|svg|webp|gif)$", nm, re.I) or nm.lower() in {'chengwei capital', 'chengwei'}:
            continue
        nm = clean(re.sub(r"(?i)\s+w$", "", nm))
        if not nm or len(nm.split()) > 5:
            continue
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        d = clean(a.get_text(" ", strip=True)) or None
        if d and (d.lower() == nm.lower() or len(d) < 4):
            d = None
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "chengwei", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
