#!/usr/bin/env python3
"""Asylum Ventures portfolio scraper -> asylum_companies.json
Source: https://www.asylum.vc/companies — company grid sentences ('<founder> building
<company>: <description>'): company name and website, description, exit note
and Asylum's stage."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.asylum.vc/companies"
PRIMARY = "Asylum Ventures"


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
    for it in s.select(".companies-grid-item"):
        p = it.select_one(".companies-grid-text-p")
        if not p:
            continue
        links = [a for a in p.select("a[href]") if site(a)]
        if not links:
            continue
        a = links[0]
        nm = txt(a)
        full = p.get_text(" ", strip=True)
        d = clean(full.split(":", 1)[1]) if ":" in full else None
        ex = txt(it.select_one(".companies-grid-when-exited"))
        ex = clean(ex.lstrip("*")) if ex else None
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at, exit_note=ex,
                       status="acquired" if ex and "acquired" in ex.lower() else None,
                       asylum_stage=txt(it.select_one(".companies-grid-when-txt"))))
    finish(out, "asylum", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
