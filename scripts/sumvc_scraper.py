#!/usr/bin/env python3
"""SUM Ventures portfolio scraper -> sumvc_companies.json
Source: https://sum.vc/portfolio — portfolio cards: company name, fund, sector tag
and description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://sum.vc/portfolio"
PRIMARY = "SUM Ventures"


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
    for it in s.select("div.group.relative"):
        nm = txt(it.select_one("h3"))
        if not nm:
            continue
        fund = txt(it.select_one(".top-5.left-5 span")) or txt(it.select_one("span.uppercase"))
        tags = [txt(x) for x in it.select(".top-4.right-5 span") if txt(x)]
        a = it.find_parent("a") or it.select_one("a[href]")
        href = a.get("href") if a else None
        out.append(rec(nm, txt(it.select_one("p")), href if href and href.startswith("http") else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=tags, fund=fund))
    finish(out, "sumvc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
