#!/usr/bin/env python3
"""Tidal Ventures portfolio scraper -> tidal_companies.json
Source: https://www.tidalvc.com/portfolio — Webflow companies accordion: company name, tagline,
initial partnership stage, current milestone, location, investment manager and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.tidalvc.com/portfolio"
PRIMARY = "Tidal Ventures"


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
    for d in s.select("details.accordion-component"):
        nm = txt(d.select_one(".companies_title"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        info = {txt(i.select_one(".card-info_label")): txt(i.select_one(".card-info_value")) for i in d.select(".card-info_item")}
        a = d.select_one("a.portfolio_card-url[href]")
        out.append(rec(nm, txt(d.select_one(".companies_tagline")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       stage=info.get("Initial Partnership"), current_milestone=info.get("Current Milestone"),
                       location=info.get("Location"), investment_manager=info.get("Investment Manager")))
    finish(out, "tidal", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
