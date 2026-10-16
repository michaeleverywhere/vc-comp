#!/usr/bin/env python3
"""Elevate Ventures portfolio scraper -> elevatevent_companies.json
Source: https://elevateventures.com/portfolio/ — portfolio table (`div.port-row`):
company name, website, stage, sector and status."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://elevateventures.com/portfolio/"
PRIMARY = "Elevate Ventures"


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
    for r in s.select("div.port-row"):
        a = r.select_one("h2.port-title a")
        nm = txt(a)
        if not nm:
            continue
        col = lambda c: txt(r.select_one(f".{c} .text"))
        st = col("port-col4")
        sec = col("port-col3")
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [], stage=col("port-col2"),
                       portfolio_status=st, status="acquired" if st and "acqui" in st.lower() else
                       ("exited" if st and st.lower() in ("exited", "exit") else
                       ("closed" if st and st.lower() in ("closed", "inactive", "defunct") else None))))
    finish(out, "elevatevent", ("company_url", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
