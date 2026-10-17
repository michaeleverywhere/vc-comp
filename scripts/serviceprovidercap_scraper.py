#!/usr/bin/env python3
"""Service Provider Capital portfolio scraper -> serviceprovidercap_companies.json
Source: https://www.serviceprovidercapital.com/portfolio — portfolio buttons: company name (button label)
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.serviceprovidercapital.com/portfolio"
PRIMARY = "Service Provider Capital"


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
    for a in s.select("a[aria-label][href^='http']"):
        if "serviceprovidercapital" in a["href"] or a.get("target") != "_blank":
            continue
        nm = clean(a.get("aria-label"))
        if not nm or nm.lower() in seen or len(nm.split()) > 6 or re.search(r"(?i)linkedin|twitter|instagram|facebook|view all", nm):
            continue
        seen.add(nm.lower())
        out.append(rec(nm, None, a["href"].strip(), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "serviceprovidercap", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
