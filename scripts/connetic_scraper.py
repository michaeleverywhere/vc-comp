#!/usr/bin/env python3
"""Connetic Ventures portfolio scraper -> connetic_companies.json
Source: https://www.conneticventures.com/portfolio — portfolio cards: company name,
website, theme, description, location and year."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.conneticventures.com/portfolio"
PRIMARY = "Connetic Ventures"


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
    for a in s.select("a[href^=http]:has(h3)"):
        nm = txt(a.find("h3"))
        if not nm:
            continue
        th = txt(a.select_one("span.rounded-full"))
        meta = [txt(x) for x in a.select("div.border-t span") if txt(x)]
        yr = next((year_of(x) for x in meta if year_of(x) and re.fullmatch(r"\d{4}", x)), None)
        loc = next((x for x in meta if not re.fullmatch(r"\d{4}", x)), None)
        out.append(rec(nm, txt(a.find("p")), site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[th] if th else [], location=loc, year=yr))
    finish(out, "connetic", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
