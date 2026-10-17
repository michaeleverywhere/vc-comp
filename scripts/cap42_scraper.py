#!/usr/bin/env python3
"""42CAP portfolio scraper -> cap42_companies.json
Source: https://42cap.com/portfolio — Portfolio table: company name, what they do, year
partnered, country, layer and status."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://42cap.com/portfolio"
PRIMARY = "42CAP"


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
    for tr in s.select("tr"):
        a = tr.select_one("td.c-name a")
        nm = txt(tr.select_one("td.c-name"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        fl = tr.select_one("td.c-country img[alt]")
        st = txt(tr.select_one("td.c-status"))
        lay = txt(tr.select_one("td.c-layer"))
        out.append(rec(nm, txt(tr.select_one("td.c-tag")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       partnered_year=txt(tr.select_one("td.c-year")), location=fl.get("alt") if fl else None,
                       sectors=[lay] if lay else [], portfolio_status=st, status="exited" if st and re.search(r"exit|acqui", st, re.I) else None))
    finish(out, "cap42", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
