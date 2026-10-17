#!/usr/bin/env python3
"""BlueTree Venture Fund portfolio scraper -> bluetreevc_companies.json
Source: https://bluetreevc.com/portfolio — portfolio page: current BTVC Fund I logo
wall (site-authored logo alt, website, acquisition note) plus the 'From earlier
BlueTree funds' ticker (`span.ticker-item`, exited flag)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://bluetreevc.com/portfolio"
PRIMARY = "BlueTree Venture Fund"


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
        img = a.find("img", alt=True)
        if not img or "bluetreevc" in a["href"]:
            continue
        nm = clean(img.get("alt"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        acq = txt(a.select_one(".acquired"))
        out.append(rec(nm, None, None if acq else site(a), PRIMARY, SOURCE_URL, scraped_at, status="exited" if acq else None,
                       exit_note=acq, fund="BTVC Fund I"))
    for sp in s.select("span.ticker-item"):
        im = sp.find("img", alt=True)
        nm = clean(im.get("alt")) if im else clean(sp.get_text(" ", strip=True))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, fund="Earlier BlueTree funds",
                       status="exited" if "exited" in (sp.get("class") or []) else None))
    finish(out, "bluetreevc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
