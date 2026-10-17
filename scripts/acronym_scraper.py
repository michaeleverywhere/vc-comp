#!/usr/bin/env python3
"""Acronym VC portfolio scraper -> acronym_companies.json
Source: https://www.acronym.vc/portfolio — Squarespace accordion per company: name and
description (first item), Acronym role and post-investment note (following items). Website links are
laid out apart from the accordions, so they are not paired."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.acronym.vc/portfolio"
PRIMARY = "Acronym VC"


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
    for box in s.select(".accordion-items-container"):
        items = box.select("li.accordion-item")
        if not items:
            continue
        def pair(it):
            dd = it.select_one(".accordion-item__description")
            return txt(it.select_one(".accordion-item__title")), (txt(dd.find("p")) or txt(dd)) if dd else None
        nm, desc = pair(items[0])
        if not nm:
            continue
        more = dict(pair(it) for it in items[1:])
        out.append(rec(nm, desc, None, PRIMARY, SOURCE_URL, scraped_at,
                       acronym_role=more.get("Acronym Role"), after_acronym=more.get("After Acronym")))
    finish(out, "acronym", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
