#!/usr/bin/env python3
"""Scrub Capital portfolio scraper -> scrub_companies.json
Source: https://www.scrubcapital.com/ — homepage portfolio cards: company name, investment
date, round, syndicate, description, fund and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.scrubcapital.com/"
PRIMARY = "Scrub Capital"


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
    for a in s.select("a.group"):
        nm = txt(a.find("h3"))
        if not nm or not any((txt(r) or "").startswith("Date:") for r in a.select("div.flex.justify-between")):
            continue
        f = {}
        for row in a.select("div.flex.justify-between"):
            sp = row.find_all("span")
            if len(sp) >= 2:
                f[txt(sp[0]).rstrip(":")] = txt(sp[1])
        syn = None
        for b in a.select("div.border-t"):
            ps = b.find_all("p")
            if len(ps) >= 2 and (txt(ps[0]) or "").startswith("Syndicate"):
                syn = txt(ps[1])
        desc = [txt(b.find("p")) for b in a.select("div.border-t") if len(b.find_all("p")) == 1]
        fund = txt(a.select_one("div.mt-auto p"))
        out.append(rec(nm, desc[0] if desc else None, site(a), PRIMARY, SOURCE_URL, scraped_at, investment_date=f.get("Date"),
                       year=year_of(f.get("Date")), round=f.get("Round"), syndicate=syn, fund=fund))
    finish(out, "scrub", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
