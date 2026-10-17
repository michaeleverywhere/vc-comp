#!/usr/bin/env python3
"""Abstraction Capital portfolio scraper -> abstraction_companies.json
Source: https://abstraction.vc/portfolio/ — portfolio table: company name, description,
investment date, acquired flag and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://abstraction.vc/portfolio/"
PRIMARY = "Abstraction Capital"


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
    for tr in s.select("tr"):
        n = tr.select_one(".company-name")
        nm = txt(n)
        if not nm:
            continue
        acq = tr.select_one(".acquired")
        nm = clean(nm.replace(txt(acq) or "\0", "")) if acq else nm
        if not nm or nm.lower() == "stealth":
            continue
        t = tr.select_one("time")
        out.append(rec(nm, txt(tr.select_one("td.company-description")), site(n.find("a")), PRIMARY, SOURCE_URL, scraped_at,
                       investment_date=(t.get("datetime") if t else None) or txt(tr.select_one("td.date")), investment_year=year_of(t.get("datetime") if t else txt(tr.select_one("td.date"))),
                       exit_note=txt(acq), status="acquired" if acq else None))
    finish(out, "abstraction", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
