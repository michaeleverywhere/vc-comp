#!/usr/bin/env python3
"""OTB Ventures portfolio scraper -> otb_companies.json
Source: https://otb.vc/portfolio/ — Portfolio accordion: company name, tagline, about
text, investment year, founders and OTB investors."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://otb.vc/portfolio/"
PRIMARY = "OTB Ventures"


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
    for it in s.select("li.p-a__item"):
        nm = txt(it.select_one(".p-a__heading"))
        if not nm:
            continue
        meta = {}
        for m in it.select(".p-a__meta-item"):
            d = m.find_all("div", recursive=False)
            if len(d) >= 2:
                meta[(txt(d[0]) or "").rstrip(":")] = ", ".join(x.strip() for x in d[1].stripped_strings)
        web = next((site(a) for a in it.select("a[href^=http]") if site(a) and "otb.vc" not in a["href"] and "linkedin" not in a["href"]), None)
        out.append(rec(nm, txt(it.select_one(".p-a__tagline")), web, PRIMARY, SOURCE_URL, scraped_at,
                       about=txt(it.select_one(".p-a__about")), invested_year=meta.get("Invested"), founders=meta.get("Founders"),
                       otb_investors=meta.get("Investors")))
    finish(out, "otb", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
