#!/usr/bin/env python3
"""DSG Consumer Partners portfolio scraper -> dsgconsumer_companies.json
Source: https://www.dsgcp.com/ — homepage brand cards: company name (site-authored
image alt)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.dsgcp.com/"
PRIMARY = "DSG Consumer Partners"


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
    for img in s.select(".home-hero-slider-img img[alt], a.home-brand-card img[alt]"):
        nm = clean(img.get("alt"))
        if not nm or nm.lower() in seen or len(nm.split()) > 5 or ":" in nm:
            continue
        seen.add(nm.lower())
        a = img.find_parent("a", href=re.compile(r"^https?://"))
        out.append(rec(nm, None, site(a) if a and "dsgcp" not in a["href"] else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "dsgconsumer", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
