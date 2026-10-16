#!/usr/bin/env python3
"""Human Ventures portfolio scraper -> humanventures_companies.json
Source: https://human.vc/portfolio/ — featured company cards (name, description,
founders, website) plus the full company list (name, tagline from the
data-company-field attribute, website). Distinct from Human Capital."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_response, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://human.vc/portfolio/"
PRIMARY = "Human Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # the server omits a charset header, so decode the UTF-8 bytes explicitly
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for a in s.select("a.featured"):
        nm = txt(a.select_one(".featured__name"))
        if nm:
            out.append(rec(nm, txt(a.select_one(".featured__description")), site(a), PRIMARY, SOURCE_URL, scraped_at,
                           founders=", ".join(txt(d) for d in a.select(".featured__founders dd")) or None))
    for li in s.select("li.company"):
        nm = txt(li.select_one(".company__name"))
        if not nm:
            continue
        f = li.select_one("[data-company-field]")
        out.append(rec(nm, clean(f["data-company-field"]) if f else None, site(li.find("a", href=True)), PRIMARY,
                       SOURCE_URL, scraped_at))
    finish(out, "humanventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
