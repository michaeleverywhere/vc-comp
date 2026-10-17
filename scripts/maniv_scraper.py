#!/usr/bin/env python3
"""Maniv Mobility portfolio scraper -> maniv_companies.json
Source: https://www.maniv.com/portfolio — Webflow portfolio popups: company name, sectors,
tagline, description, region and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.maniv.com/portfolio"
PRIMARY = "Maniv Mobility"


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
    for c in s.select("div.c-popup_content"):
        nm = txt(c.select_one("[item-name]"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        a = c.select_one("a.c-link[href^=http]")
        fl = c.select_one("div.c-flow div.c-flow")
        tx = [txt(x) for x in fl.select(".c-text")] if fl else []
        reg = None
        for col in c.select(".c-col"):
            t = [txt(x) for x in col.select(".c-text")]
            if len(t) >= 2 and t[0] == "Region":
                reg = t[1]
        out.append(rec(nm, tx[1] if len(tx) > 1 else (tx[0] if tx else None), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       tagline=tx[0] if len(tx) > 1 else None, location=reg,
                       sectors=[txt(x) for x in c.select("[b-indexed=sectors]") if txt(x)]))
    finish(out, "maniv", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
