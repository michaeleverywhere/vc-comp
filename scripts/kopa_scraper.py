#!/usr/bin/env python3
"""Kopa Ventures portfolio scraper -> kopa_companies.json
Source: https://www.kopa.vc/portfolio — Wix portfolio repeater: company name (h5),
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.kopa.vc/portfolio"
PRIMARY = "Kopa Ventures"


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
    for h in s.select("h5.font_5"):
        nm = txt(h)
        if not nm or nm.lower() == "title":
            continue
        box = h
        for _ in range(8):
            box = box.parent
            if box is None or box.select_one("p.font_8"):
                break
        p = box.select_one("p.font_8") if box is not None else None
        a = h.find("a") or (box.select_one("a[href^='http']") if box is not None else None)
        out.append(rec(nm, txt(p), site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "kopa", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
