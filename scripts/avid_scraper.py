#!/usr/bin/env python3
"""Avid Ventures portfolio scraper -> avid_companies.json
Source: https://avidventures.com/ — homepage Companies section (Framer): company name,
one-line description, website and Current/Exited group."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://avidventures.com/"
PRIMARY = "Avid Ventures"


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
    sec = s.find(id="companies")
    for a in (sec.select("a[href]") if sec else []):
        nm = txt(a.find("h6"))
        if not nm:
            continue
        grp = a.find_previous("p", string=re.compile(r"^\s*(Current|Exited)\s*$"))
        g = txt(grp)
        out.append(rec(nm, txt(a.select_one("p.framer-text")), site(a), PRIMARY, SOURCE_URL, scraped_at, portfolio_status=g,
                       status="exited" if g == "Exited" else None))
    finish(out, "avid", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
