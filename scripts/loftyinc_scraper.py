#!/usr/bin/env python3
"""LoftyInc Capital portfolio scraper -> loftyinc_companies.json
Source: https://loftyinc.vc/portfolio/ — portfolio gallery captions: company name
(h2), industry, country, status, investment year and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://loftyinc.vc/portfolio/"
PRIMARY = "LoftyInc Capital"


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
    for cap in s.select("div.gallery-item-caption-over"):
        nm = txt(cap.select_one("h2.fg-item-title"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        f = {}
        for p in cap.select(".fg-item-content p"):
            m = re.match(r"^\s*([A-Za-z ]+):\s*(.+)$", p.get_text(" ", strip=True))
            if m:
                f[m.group(1).strip().lower()] = clean(m.group(2))
        a = cap.select_one(".fg-item-content a[href^='http']")
        st = f.get("status")
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, industry=f.get("industry"),
                       country=f.get("country"), holding=st, status="exited" if st and re.search(r"exit|acquir", st, re.I) else None,
                       year=year_of(f.get("investment year") or "")))
    finish(out, "loftyinc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
