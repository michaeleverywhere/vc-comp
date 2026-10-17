#!/usr/bin/env python3
"""Beyond Capital Ventures portfolio scraper -> beyondcapital_companies.json
Source: https://www.beyondcapitalventures.com/portfolio — Squarespace accordion:
company name, location (italic line), description and LEARN MORE website link."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.beyondcapitalventures.com/portfolio"
PRIMARY = "Beyond Capital Ventures"


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
    for it in s.select("li.accordion-item"):
        nm = txt(it.select_one(".accordion-item__title"))
        if not nm:
            continue
        ps = it.select(".accordion-item__description p")
        loc = next((txt(p) for p in ps if p.find("em") and txt(p)), None)
        desc = next((txt(p) for p in ps if txt(p) and not p.find("em") and (txt(p) or "").upper() != "LEARN MORE"), None)
        web = next((a for a in it.select("a[href^='http']") if site(a)), None)
        out.append(rec(nm, desc, site(web), PRIMARY, SOURCE_URL, scraped_at, location=loc))
    finish(out, "beyondcapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
