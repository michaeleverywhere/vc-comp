#!/usr/bin/env python3
"""Incisive Ventures portfolio scraper -> incisive_companies.json
Source: https://incisive.vc/investments — investment cards: company name, vehicle
(Fund 1 / Access Fund / Syndicate / Opportunity Fund), description, memo and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://incisive.vc/investments"
PRIMARY = "Incisive Ventures"


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
    for c in s.select("div.investment-card"):
        nm = txt(c.find("h2"))
        if not nm:
            continue
        web = next((a for a in c.select("a[href]") if "Website" in (txt(a) or "")), None)
        memo = next((a for a in c.select("a[href]") if "memo" in (txt(a) or "").lower()), None)
        out.append(rec(nm, txt(c.select_one("p.mt-4")), site(web), PRIMARY, SOURCE_URL, scraped_at,
                       fund=txt(c.select_one("p.mt-0\\.5")), memo_url=urljoin(SOURCE_URL, memo["href"]) if memo else None))
    finish(out, "incisive", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
