#!/usr/bin/env python3
"""DOT Capital portfolio scraper -> dotcapital_companies.json
Source: https://dotcapital.com/ — Portfolio popups: company name (site logo alt),
summary and website (omitted when it links to a Dot Capital news post)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://dotcapital.com/"
PRIMARY = "DOT Capital"


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
    for p in s.select("div.portfolio-popup"):
        img = p.select_one(".popup-left img[alt]")
        nm = clean(re.sub(r"\s*logo$", "", img.get("alt") or "", flags=re.I)) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        d = p.select_one(".popup-left p")
        a = p.select_one(".popup-website a[href^=http]")
        web = site(a) if a and "dotcapital.com" not in a["href"] else None
        out.append(rec(nm, txt(d), web, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "dotcapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
