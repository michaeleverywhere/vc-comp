#!/usr/bin/env python3
"""Planet A Ventures portfolio scraper -> planeta_companies.json
Source: https://planet-a.com/portfolio/ — startup grid: company name (as
printed on the site, mostly upper-case), claim, sector pill, website and impact
assessment PDF."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://planet-a.com/portfolio/"
PRIMARY = "Planet A Ventures"


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
    for c in s.select("div.startup_column"):
        nm = txt(c.select_one(".startup_title h2"))
        if not nm or nm.upper() == "COMING SOON":
            continue
        sec = [txt(x) for x in c.select(".filter_terms .label_pill") if txt(x)]
        web = next((site(a) for a in c.select("a.button") if txt(a) == "Website"), None)
        ia = next((a.get("href") for a in c.select("a.button") if txt(a) == "Impact Assessment"), None)
        out.append(rec(nm, txt(c.select_one(".startup_column__overlay_claim")), web, PRIMARY, SOURCE_URL, scraped_at, sectors=sec,
                       impact_assessment_url=ia))
    finish(out, "planeta", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
