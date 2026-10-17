#!/usr/bin/env python3
"""Tectonic Ventures portfolio scraper -> tectonic_companies.json
Source: https://www.tectonicventures.com/ — homepage company directory (Webflow):
company name, descriptor and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.tectonicventures.com/"
PRIMARY = "Tectonic Ventures"


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
    for it in s.select("div.directory_item-content"):
        nm = txt(it.select_one(".directory_text.is-name"))
        if not nm or nm == "Company":
            continue
        web = next((site(a) for a in it.select("a.directory_link") if site(a)), None)
        out.append(rec(nm, txt(it.select_one(".directory_descriptor .directory_text")), web, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "tectonic", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
