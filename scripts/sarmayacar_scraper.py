#!/usr/bin/env python3
"""Sarmayacar portfolio scraper -> sarmayacar_companies.json
Source: https://www.sarmayacar.com/portfolio — Webflow portfolio modals: company name,
website, CEO, founded and partnered dates, description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.sarmayacar.com/portfolio"
PRIMARY = "Sarmayacar"


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
    for it in s.select(".logowrapper"):
        nm = txt(it.select_one(".mid-boi"))
        if not nm:
            continue
        f = {}
        for blk in it.select(".modal-info-wrapper > .w-layout-vflex"):
            ks = [txt(x) for x in blk.select(".body-black") if txt(x)]
            if len(ks) >= 2:
                f[ks[0]] = ks[1]
        web = next((a for a in it.select(".modalslinks a[href^='http']") if site(a)), None)
        out.append(rec(nm, txt(it.select_one(".body-black.w-richtext")), site(web), PRIMARY, SOURCE_URL, scraped_at,
                       ceo=f.get("CEO"), founded=f.get("Founded"), partnered=f.get("Partnered")))
    finish(out, "sarmayacar", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
