#!/usr/bin/env python3
"""K3 Ventures portfolio scraper -> k3ventures_companies.json
Source: https://www.k3.co/portfolio — Webflow portfolio tabs: company name, one-line
description, website and sector (tab)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.k3.co/portfolio"
PRIMARY = "K3 Ventures"


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
    secs = {}
    for pane in s.select(".w-tab-pane"):
        sec = clean(pane.get("data-w-tab"))
        if not sec or sec.lower() == "all":
            continue
        for h in pane.select("h2.logos"):
            secs.setdefault(txt(h), []).append(sec.title() if sec.isupper() else sec)
    for it in s.select(".collection-item-3"):
        nm = txt(it.select_one("h2.logos"))
        if not nm:
            continue
        a = it.select_one("a[href]")
        out.append(rec(nm, txt(it.select_one(".body")), site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=secs.get(nm, [])))
    finish(out, "k3ventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
