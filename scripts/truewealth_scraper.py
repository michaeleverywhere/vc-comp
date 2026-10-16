#!/usr/bin/env python3
"""True Wealth Ventures portfolio scraper -> truewealth_companies.json
Source: https://truewealthvc.com/portfolio/ — portfolio feature blocks: company name,
description, website, founders and headquarters."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://truewealthvc.com/portfolio/"
PRIMARY = "True Wealth Ventures"


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
    for it in s.select("div.featured-content"):
        nm = txt(it.select_one("h3.entry-title"))
        if not nm:
            continue
        top = it.select(".top p")
        web = next((site(a) for a in it.select(".top a[href^=http]") if site(a) and "truewealthvc.com" not in a["href"]), None)
        desc = next((txt(p) for p in top if txt(p)), None)
        bt = it.select_one(".bottom")
        bts = bt.get_text("\n", strip=True) if bt else ""
        f = re.search(r"Founders?:\s*\n?([^\n]+)", bts)
        hq = re.search(r"Headquarters:\s*\n?([^\n]+)", bts)
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at, founders=clean(f.group(1)) if f else None,
                       headquarters=clean(hq.group(1)) if hq else None))
    finish(out, "truewealth", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
