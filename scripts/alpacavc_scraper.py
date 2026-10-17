#!/usr/bin/env python3
"""Alpaca VC portfolio scraper -> alpacavc_companies.json
Source: https://alpaca.vc/portfolio — portfolio page: company name (site-authored
link aria-label 'Open X website' / logo alt), website and thesis section
(Energy Abundance, Foundational Industries, ..., Notable Exits)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://alpaca.vc/portfolio"
PRIMARY = "Alpaca VC"


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
    for a in s.select("a[href^='http']"):
        if "alpaca.vc" in a["href"]:
            continue
        m = re.match(r"^Open (.+) website$", a.get("aria-label") or "")
        img = a.find("img", alt=True)
        nm = clean(m.group(1)) if m else (clean(img.get("alt")) if img else None)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        h = a.find_previous("h2")
        sec = txt(h)
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, thesis=None if sec == "Notable Exits" else sec,
                       status="exited" if sec == "Notable Exits" else None))
    finish(out, "alpacavc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
