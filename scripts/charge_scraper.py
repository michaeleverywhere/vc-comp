#!/usr/bin/env python3
"""Charge VC portfolio scraper -> charge_companies.json
Source: https://charge.vc/portfolio — Framer portfolio cards: company name, one-line description
and detail page ./portfolio/<slug>."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://charge.vc/portfolio"
PRIMARY = "Charge VC"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for a in s.select("a[href*='portfolio/']"):
        ps = [txt(p) for p in a.select("p.framer-text") if txt(p)]
        if len(ps) < 2:
            continue
        desc, nm = ps[0], ps[-1]
        out.append(rec(nm, desc, None, PRIMARY, SOURCE_URL, scraped_at,
                       detail_url=urljoin("https://charge.vc/", a["href"].lstrip("./"))))
    finish(out, "charge", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
