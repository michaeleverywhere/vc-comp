#!/usr/bin/env python3
"""Embark Ventures portfolio scraper -> embark_companies.json
Source: https://www.embark.vc/ — Wix portfolio gallery: company name, description
(with acquisition notes) and website (omitted when it points to an acquirer)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.embark.vc/"
PRIMARY = "Embark Ventures"


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
    for it in s.select("div.wixui-gallery__item"):
        p = [clean(x) for x in it.stripped_strings if clean(x)]
        if not p or p[0].lower() in seen:
            continue
        nm = p[0]
        seen.add(nm.lower())
        d = it.select_one("p")
        desc = clean(d.get_text(" ", strip=True)) if d else None
        acq = bool(desc and re.match(r"(acquired|ipo|nasdaq|nyse)", desc, re.I))
        a = it.select_one("a[href^=http]")
        out.append(rec(nm, desc, None if acq else (site(a) if a else None), PRIMARY, SOURCE_URL, scraped_at, status="exited" if acq else None))
    finish(out, "embark", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
