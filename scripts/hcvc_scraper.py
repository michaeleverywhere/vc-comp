#!/usr/bin/env python3
"""HCVC portfolio scraper -> hcvc_companies.json
Source: https://www.hcvc.co/pages/portfolio — Portfolio table: company name, website, country,
year, stage and status."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.hcvc.co/pages/portfolio"
PRIMARY = "HCVC"


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
    for tr in s.select("tr"):
        tds = tr.find_all("td")
        nmel = tr.select_one(".company")
        nm = txt(nmel)
        if not nm or len(tds) < 5 or nm.lower().startswith("stealth"):
            continue
        a = nmel.select_one("a[href]")
        st = txt(tds[4])
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, location=txt(tds[1]),
                       invested_year=txt(tds[2]), stage=txt(tds[3]), portfolio_status=st,
                       status="exited" if st and re.search(r"exit|acqui", st, re.I) else None))
    finish(out, "hcvc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
