#!/usr/bin/env python3
"""Abac Nest portfolio scraper -> abacnest_companies.json
Source: https://abacnest.abaccapital.com/es/ — homepage portfolio tiles (Spanish):
company name, description, exit marker ('Desinvertida') and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://abacnest.abaccapital.com/es/"
PRIMARY = "Abac Nest"


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
    for it in s.select("div.flexat4"):
        nm = txt(it.select_one("h2"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        st = txt(it.select_one("h4"))
        a = it.select_one("a[href^=http]")
        w = a["href"].split("#")[0] if a else None
        out.append(rec(nm, txt(it.select_one("h3")), w, PRIMARY, SOURCE_URL, scraped_at,
                       status="exited" if st and "desinvert" in st.lower() else None))
    finish(out, "abacnest", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
