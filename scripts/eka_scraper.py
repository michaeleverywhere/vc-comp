#!/usr/bin/env python3
"""Eka Ventures portfolio scraper -> eka_companies.json
Source: https://www.ekavc.com/portfolio — Webflow portfolio modals: company name, tagline,
founders, first investment date, about, impact statement and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.ekavc.com/portfolio"
PRIMARY = "Eka Ventures"


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
    for h in s.select(".portfolio-modal-heading"):
        box = h.find_parent(class_="modal_content") or h.parent
        nm = txt(h.select_one(".heading-style-h5.is-portfolio-page:not(.is-hyphen)"))
        if not nm:
            continue
        f = [txt(x) for x in box.select(".founder-name-links a") if txt(x)]
        web = next((site(a) for a in box.select("a.button[href^=http]") if site(a)), None)
        out.append(rec(nm, txt(h.select_one(".is-grey")), web, PRIMARY, SOURCE_URL, scraped_at, founders=", ".join(f) or None,
                       first_investment=txt(box.select_one(".investment-date")), about=txt(box.select_one(".modal-about .is-modal")),
                       impact=txt(box.select_one(".modal-impact .is-modal"))))
    finish(out, "eka", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
