#!/usr/bin/env python3
"""Outward VC portfolio scraper -> outwardvc_companies.json
Source: https://outwardvc.com/companies/ — company tiles: name, one-line description,
category tags, exited flag and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://outwardvc.com/companies/"
PRIMARY = "Outward VC"


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
    for it in s.select(".tile--company"):
        nm = txt(it.select_one(".tile__heading .linkline")) or txt(it.select_one(".linkline"))
        if not nm:
            continue
        tags = [txt(x) for x in it.select(".tile__btns a.tag") if txt(x)]
        ex = it.select_one(".tile__heading__exited") is not None
        a = it.select_one("a.tile__link")
        out.append(rec(nm, txt(it.select_one(".tile__description")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=tags,
                       status="exited" if ex else None, detail_url=a["href"] if a else None))
    finish(out, "outwardvc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
