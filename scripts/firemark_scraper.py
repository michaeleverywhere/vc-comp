#!/usr/bin/env python3
"""IAG Firemark Ventures portfolio scraper -> firemark_companies.json
Source: https://iagfiremarkventures.com/portfolio/ — Portfolio flip cards: company name, founded year,
founders, CEO, country, year invested, sector and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://iagfiremarkventures.com/portfolio/"
PRIMARY = "IAG Firemark Ventures"


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
    for c in s.select("div.oxilab-flip-box-back"):
        nm = txt(c.select_one(".oxilab-heading"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        info = c.select_one(".oxilab-info")
        t = info.get_text("\n", strip=True) if info else ""
        def f(k):
            m = re.search(k + r":\s*\n?([^\n]+)", t)
            return clean(m.group(1)) if m else None
        web = next((site(a) for a in c.select("a[href^=http]") if site(a)), None)
        sec = f("Sector")
        out.append(rec(nm, None, web, PRIMARY, SOURCE_URL, scraped_at, founded_year=f("Founded"), founders=f("Founders?"),
                       ceo=f("CEO"), location=f("Country"), invested_year=f("Invested"), sectors=[sec] if sec else []))
    finish(out, "firemark", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
