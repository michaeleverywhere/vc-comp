#!/usr/bin/env python3
"""Hypersphere portfolio scraper -> hypersphere_companies.json
Source: https://www.hypersphere.capital/portfolio — Investment cards: company name, round, date invested
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.hypersphere.capital/portfolio"
PRIMARY = "Hypersphere"


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
    for li in s.select("li.investment-card"):
        nm = txt(li.select_one("span.investment-card__meta__name"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in li.stripped_strings if clean(x)]
        rnd = p[p.index("Round") + 1] if "Round" in p[:-1] else None
        dt = p[p.index("Date Invested") + 1] if "Date Invested" in p[:-1] else None
        a = li.select_one("a[href^=http]")
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, round=rnd, date_invested=dt))
    finish(out, "hypersphere", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
