#!/usr/bin/env python3
"""Tenacity Venture Capital portfolio scraper -> tenacity_companies.json
Source: https://tenacity.vc/portfolio — Webflow portfolio list: company name,
description, sector, stage / year and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://tenacity.vc/portfolio"
PRIMARY = "Tenacity Venture Capital"


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
    for it in s.select(".w-dyn-item"):
        nm = txt(it.select_one(".text-block.company"))
        if not nm:
            continue
        ex = bool(re.search(r"\(\s*exited\s*\)", nm, re.I))
        nm = clean(re.sub(r"\(\s*exited\s*\)", "", nm, flags=re.I))
        sec = txt(it.select_one(".c1"))
        extra = [txt(x) for x in it.select(".mob-hide") if txt(x)]
        a = it.select_one("a[href]")
        yr = next((year_of(x) for x in extra if year_of(x)), None)
        out.append(rec(nm, txt(it.select_one(".desc")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                       details=extra, year=yr, status="exited" if ex else None, detail_url=urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else None))
    finish(out, "tenacity", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
