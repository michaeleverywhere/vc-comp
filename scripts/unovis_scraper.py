#!/usr/bin/env python3
"""Unovis Asset Management portfolio scraper -> unovis_companies.json
Source: https://unovis.vc/portfolio/ — portfolio module items (`div.module__item`):
company name (site-authored logo alt, before ' - '), description, location,
website, founders, initial investment stage, category and geography."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://unovis.vc/portfolio/"
PRIMARY = "Unovis Asset Management"


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
    for it in s.select("div.module__item"):
        img = it.select_one(".item-logo img[alt]")
        nm = clean((img.get("alt") or "").split(" - ")[0]) if img else None
        if not nm or nm.lower() in seen or len(nm) > 40:
            continue
        seen.add(nm.lower())
        t = txt(it.select_one(".item-excerpt p")) or ""
        def fld(k, nxt):
            m = re.search(k + r":\s*(.+?)\s*(?:" + nxt + r"):", t + " END:")
            return clean(m.group(1)) if m else None
        d = re.split(r"\s+LOCATION:", t)[0].strip() or None
        loc = fld("LOCATION", "WEBSITE|FOUNDERS?|INITIAL INVESTMENT|END")
        web = fld("WEBSITE", "FOUNDERS?|INITIAL INVESTMENT|END")
        fd = fld("FOUNDERS?", "INITIAL INVESTMENT|END")
        stage = fld("INITIAL INVESTMENT", "END")
        out.append(rec(nm, d, web if web and web.startswith("http") else None, PRIMARY, SOURCE_URL, scraped_at,
                       location=loc, founders=fd, initial_stage=stage, category=clean(it.get("data-category")) or None,
                       geography=clean(it.get("data-geography")) or None))
    finish(out, "unovis", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
