#!/usr/bin/env python3
"""E14 Fund portfolio scraper -> e14_companies.json
Source: https://www.e14.vc/companies — Webflow CMS `.card-company` cards (MIT Media Lab
spin-out fund): company name, tagline, status label (e.g. Acquired) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.e14.vc/companies"
PRIMARY = "E14 Fund"


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
    for it in s.select(".card-company"):
        nm = txt(it.select_one(".companies_title"))
        if not nm:
            continue
        lab = txt(it.select_one(".card-company_label-wrapper"))
        web = next((site(a) for a in it.select("a.card-company_link") if "Website" in a.get_text()), None)
        out.append(rec(nm, txt(it.select_one(".companies_subtitle")), web, PRIMARY, SOURCE_URL, scraped_at,
                       portfolio_status=lab, status="acquired" if lab and "acquired" in lab.lower() else
                       ("public" if lab and "ipo" in lab.lower() else None)))
    finish(out, "e14", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
