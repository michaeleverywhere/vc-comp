#!/usr/bin/env python3
"""Eximius Ventures portfolio scraper -> eximiusvc_companies.json
Source: https://eximiusvc.com/portfolio-all/ — portfolio grid: company name (heading) and one-
line description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://eximiusvc.com/portfolio-all/"
PRIMARY = "Eximius Ventures"


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
    for sec in s.select("section.elementor-inner-section"):
        hs = sec.select("h2.elementor-heading-title")
        if len(hs) != 1:
            continue
        nm = txt(hs[0])
        col = sec.find_parent(class_="elementor-widget-wrap")
        ss = [clean(x) for x in col.stripped_strings] if col else []
        if not nm or nm.lower() in seen or len(nm.split()) > 5 or len(ss) < 2 or len(ss) > 4:
            continue
        seen.add(nm.lower())
        d = next((x for x in ss if x != nm), None)
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "eximiusvc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
