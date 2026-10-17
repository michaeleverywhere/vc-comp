#!/usr/bin/env python3
"""Blossom Street Ventures portfolio scraper -> blossomstreet_companies.json
Source: https://www.blossomstreetventures.com/ — Webflow portfolio cards: company name (linked in the
write-up), description, date of investment, amount, fund, role and co-investors."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.blossomstreetventures.com/"
PRIMARY = "Blossom Street Ventures"


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
    for c in s.select("div.card-portfolio"):
        rt = c.select_one(".rich-text-portfolio")
        a = rt.select_one("a[href]") if rt else None
        nm = txt(a)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        info = {txt(t.select_one(".h4")): txt(t.select_one(".p3-body-copy")) for t in c.select(".tag")}
        out.append(rec(nm, txt(rt), site(a), PRIMARY, SOURCE_URL, scraped_at, invested_date=info.get("Date of Investment"),
                       amount=info.get("Amount"), fund=info.get("Fund"), role=info.get("Role"),
                       co_investors=info.get("Co-Investors") if info.get("Co-Investors") not in (None, "None") else None))
    finish(out, "blossomstreet", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
