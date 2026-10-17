#!/usr/bin/env python3
"""JME Ventures portfolio scraper -> jme_companies.json
Source: https://www.jme.vc/ — Webflow companies list: company name, investment
date, status, fund and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.jme.vc/"
PRIMARY = "JME Ventures"


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
    for it in s.select("div.companies_item.w-dyn-item"):
        nm = txt(it.select_one("[fs-list-field=name]"))
        if not nm:
            continue
        st = txt(it.select_one("[fs-list-field=status]"))
        a = it.select_one("a.companies_link[href]")
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, invested_date=txt(it.select_one("[fs-list-field=date]")),
                       portfolio_status=st, fund=txt(it.select_one("[fs-list-field=fund]")),
                       status="exited" if st and "exit" in st.lower() else None))
    finish(out, "jme", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
