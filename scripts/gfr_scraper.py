#!/usr/bin/env python3
"""GFR Fund portfolio scraper -> gfr_companies.json
Source: https://gfrfund.com/portfolio — portfolio grid: company name, description,
category (class) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://gfrfund.com/portfolio"
PRIMARY = "GFR Fund"


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
    for it in s.select(".room120_portfolio__item"):
        nm = txt(it.select_one(".room120_portfolio__title"))
        if not nm:
            continue
        cls = " ".join(c for c in (it.get("class") or []) if c != "room120_portfolio__item")
        ex = "exited" in cls.lower()
        cat = clean(re.sub(r"(?i)\bexited\b", "", cls))
        out.append(rec(nm, txt(it.select_one(".room120_portfolio__desc")), site(it.select_one("a[href]")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cat.title().replace("&", "&")] if cat else [], status="exited" if ex else None))
    finish(out, "gfr", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
